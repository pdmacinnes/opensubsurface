from dataclasses import asdict, dataclass, replace
from hashlib import sha256
from itertools import product
import json

import numpy as np
from scipy.special import ndtr


CURRENT_A = 0.001
SEED = 20261008
RADIUS_M = 1.5
NOISE_SCENARIOS = tuple(product((0.01, 0.03), (1e-6, 10e-6, 100e-6)))


def electrodes():
    axis = np.arange(-10.5, 10.6, 3.0)
    return np.array([(x, y, 0.0) for x in axis for y in axis])


def canonical_configuration(indices):
    a, b, m, n = map(int, indices)
    if len({a, b, m, n}) != 4 or min(a, b, m, n) < 0:
        raise ValueError("A configuration requires four distinct nonnegative electrodes")
    source = tuple(sorted((a, b)))
    receiver = tuple(sorted((m, n)))
    source, receiver = sorted((source, receiver))
    return (*source, *receiver)


def candidate_manifest(count=4096, seed=SEED, electrode_count=64):
    maximum = electrode_count * (electrode_count - 1) * (electrode_count - 2) * (electrode_count - 3) // 8
    if electrode_count < 4 or not 1 <= count <= maximum:
        raise ValueError("Requested configuration count is outside the available pool")
    rng = np.random.Generator(np.random.PCG64(seed))
    configurations = set()
    while len(configurations) < count:
        configurations.add(canonical_configuration(rng.choice(electrode_count, 4, replace=False)))
    return np.array(sorted(configurations), dtype=np.int64)


def manifest_bytes(manifest):
    return ("a,b,m,n\n" + "".join(",".join(map(str, row)) + "\n" for row in manifest)).encode("ascii")


def homogeneous_voltage(locations, manifest, resistivity=100.0, current=CURRENT_A):
    if resistivity <= 0 or current <= 0:
        raise ValueError("Resistivity and injection current must be positive")
    a, b, m, n = locations[manifest].transpose(1, 0, 2)
    distances = [np.linalg.norm(x - y, axis=1) for x, y in ((a, m), (b, m), (a, n), (b, n))]
    if any(np.any(r == 0) for r in distances):
        raise ValueError("Point-source voltages cannot be measured at a current electrode")
    return resistivity * current / (2 * np.pi) * (1 / distances[0] - 1 / distances[1] - 1 / distances[2] + 1 / distances[3])


@dataclass(frozen=True)
class Geometry:
    kind: str
    depth: float
    contrast: float
    separation: float = 0.0
    orientation: float = 0.0
    background: float = 100.0
    shift_x: float = 0.0
    shift_depth: float = 0.0

    def __post_init__(self):
        if self.kind not in ("H1", "H2"):
            raise ValueError("Geometry must be H1 or H2")
        for key, value in asdict(self).items():
            if key != "kind":
                object.__setattr__(self, key, float(value))
        if not all(np.isfinite(value) for key, value in asdict(self).items() if key != "kind"):
            raise ValueError("Geometry parameters must be finite")
        if self.background <= 0 or self.contrast <= 0:
            raise ValueError("Material resistivity must be positive")
        if self.depth + self.shift_depth <= self.radius:
            raise ValueError("Inclusion intersects the ground surface")
        if self.kind == "H2" and self.separation <= 2 * self.radius:
            raise ValueError("H2 spheres must be separated")
        if self.kind == "H1" and (self.separation != 0 or self.orientation != 0):
            raise ValueError("H1 has no separation or orientation")

    @property
    def radius(self):
        return RADIUS_M if self.kind == "H1" else RADIUS_M / np.cbrt(2.0)

    @property
    def centers(self):
        center = np.array([self.shift_x, 0.0, -self.depth - self.shift_depth])
        if self.kind == "H1":
            return center[None, :]
        angle = np.deg2rad(self.orientation)
        offset = self.separation / 2 * np.array([np.cos(angle), np.sin(angle), 0.0])
        return np.array([center - offset, center + offset])

    @property
    def identifier(self):
        payload = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return self.kind.lower() + "-" + sha256(payload.encode()).hexdigest()[:16]

    def contains(self, points):
        return np.any(np.sum((points[:, None, :] - self.centers[None, :, :]) ** 2, axis=2) <= self.radius ** 2, axis=1)


def primary_catalog():
    models = {}
    pairs = []
    for depth, contrast, separation, orientation in product((3.0, 5.0, 7.0), (10.0, 100.0), (3.0, 5.0), (0.0, 90.0)):
        one = Geometry("H1", depth, contrast)
        two = Geometry("H2", depth, contrast, separation, orientation)
        models[one.identifier] = one
        models[two.identifier] = two
        pairs.append({"h1": one.identifier, "h2": two.identifier, "depth": depth, "contrast": contrast, "separation": separation, "orientation": orientation})
    return models, pairs


def nuisance_bank(model):
    return [replace(model, background=background, shift_x=dx, shift_depth=dd)
            for background, dx, dd in product((80.0, 100.0, 125.0), (-1.5, 0.0, 1.5), (-0.5, 0.0, 0.5))]


def noise_sigma(background_voltages, relative_error, floor_v):
    if relative_error < 0 or floor_v <= 0:
        raise ValueError("Noise requires a positive absolute floor and nonnegative relative error")
    return np.hypot(relative_error * np.abs(background_voltages), floor_v)


def discrimination(first, second, sigma):
    if first.shape != second.shape or first.shape != sigma.shape or np.any(sigma <= 0):
        raise ValueError("Responses and positive noise scales must have identical shapes")
    contributions = ((first - second) / sigma) ** 2
    distance = float(np.sqrt(np.sum(contributions)))
    return distance, float(ndtr(-distance / 2)), contributions


def normalized_discrepancy(first, second, sigma):
    normalized = np.abs((first - second) / sigma)
    return {"rms": float(np.sqrt(np.mean(normalized ** 2))), "maximum": float(normalized.max()),
            "passed": bool(np.sqrt(np.mean(normalized ** 2)) <= 0.1 and normalized.max() <= 0.25)}
