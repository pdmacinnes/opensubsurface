# Reproduce the review calculations

These recipes read the published P2 arrays and evaluate existing analytical formulas. They run no native forward solve and change no historical acceptance result. Execute the blocks in order in one Python process from the repository root, using the pinned Python 3.12 environment. Printed diagnostics are post-hoc review evidence, not replacement gates.

## Verify inputs and reproduce the error census

The formulas also produce the contents of [saved-data metrics](boundary-error-budget-review/2026-10-09/saved-data-metrics.csv) and the [role census](boundary-error-budget-review/2026-10-09/role-census.csv). Here the output is printed rather than written over published files.

```python
from pathlib import Path
from hashlib import sha256
import json
import numpy as np
from opensubsurface.contact import green_and_gradient
from opensubsurface.domain import canonical_configuration

root = Path("experiments/ert-p2-contact-comparison/results/2026-10-09")
for name, digest in json.loads((root / "raw-data-sha256.json").read_text()).items():
    assert sha256((root / name).read_bytes()).hexdigest() == digest
cfg = json.loads((root / "configuration.json").read_text())
positions = np.array(cfg["electrodes_m"])
manifest = np.loadtxt(root / "candidate-manifest.csv", delimiter=",", skiprows=1, dtype=int)
hom = np.load(root / "H-reference-v.npy", allow_pickle=False)
sigma = np.load(root / "fixed-sigma-v.npy", allow_pickle=False)
null = np.abs(hom) <= 1e-14
side = positions[:, 0] < 0
groups = []
for a, b, m, n in manifest:
    source = "LL" if side[a] and side[b] else "RR" if not side[a] and not side[b] else "LR"
    receiver = "LL" if side[m] and side[n] else "RR" if not side[m] and not side[n] else "LR"
    groups.append(source + "/" + receiver)
groups = np.array(groups)
print("background-null count", int(null.sum()))
for label in "AC":
    for state in ("C10", "C100"):
        ref = np.load(root / f"{state}-reference-v.npy", allow_pickle=False)
        model_scale = np.hypot(.01 * np.abs(ref), 1e-6)
        for method in ("linear", "p2"):
            value = np.load(root / f"{method}-{label}-{state}-voltage-v.npy", allow_pickle=False)
            error = value - ref
            weighted = error / sigma
            total = np.sum(weighted ** 2)
            worst = int(np.argmax(np.abs(weighted)))
            print(method, label, state, {
                "null_squared_error_share": float(np.sum(weighted[null] ** 2) / total),
                "relative_l2_error": float(np.linalg.norm(error) / np.linalg.norm(ref)),
                "max_absolute_error_v": float(np.max(np.abs(error))),
                "model_scale_rms_diagnostic": float(np.sqrt(np.mean((error / model_scale) ** 2))),
                "model_scale_max_diagnostic": float(np.max(np.abs(error / model_scale))),
                "worst_frozen_index": worst,
                "worst_model_to_frozen_scale_ratio": float(model_scale[worst] / sigma[worst]),
            })
            for group in ("LL/LL", "LL/LR", "LL/RR", "LR/LL", "LR/LR", "LR/RR", "RR/LL", "RR/LR", "RR/RR"):
                chosen = groups == group
                print(group, int(chosen.sum()), int(np.sum(chosen & null)),
                      float(np.sum(weighted[chosen] ** 2) / total))
```

## Evaluate the formal boundary analogue

This reconstructs outer-facet centers and areas directly from the saved regular axes. The native coefficient is sampled at those centers. The printed integrated absolute residual is a midpoint boundary-data diagnostic, not an exact weak residual or propagated voltage error.

The center `(0,0,0)` is inferred from the inspected source for the declared valid symmetric electrode set. The original runs did not independently record the runtime center. The homogeneous control must be below `1e-12`; the observed values are approximately `1e-16`.

```python
for label in "AC":
    axes = [np.load(root / f"{label}-{axis}-axis-m.npy", allow_pickle=False) for axis in "xyz"]
    mids = [(axis[:-1] + axis[1:]) / 2 for axis in axes]
    widths = [np.diff(axis) for axis in axes]
    points, normals, areas = [], [], []
    for axis, sign in ((0, -1), (0, 1), (1, -1), (1, 1), (2, -1)):
        other = [index for index in range(3) if index != axis]
        pair = np.array(np.meshgrid(mids[other[0]], mids[other[1]], indexing="ij")).reshape(2, -1).T
        p = np.zeros((len(pair), 3))
        p[:, axis] = axes[axis][0] if sign < 0 else axes[axis][-1]
        p[:, other] = pair
        n = np.zeros_like(p)
        n[:, axis] = sign
        points.append(p)
        normals.append(n)
        areas.append(np.outer(widths[other[0]], widths[other[1]]).ravel())
    p = np.vstack(points)
    n = np.vstack(normals)
    area = np.concatenate(areas)
    alpha = np.abs(np.sum(p * n, axis=1)) / np.sum(p * p, axis=1)
    assert np.all(p[:, 0] != 0)
    for state, (left, right) in cfg["states_ohm_m"].items():
        measures = []
        for source in positions:
            g, gradient = green_and_gradient(p, source, left, right)
            g0, gradient0 = green_and_gradient(p, source, 1., 1.)
            conductivity = np.where(p[:, 0] < 0, 1 / left, 1 / right)
            residual = conductivity * (np.sum(gradient * n, axis=1) + alpha * g)
            residual -= np.sum(gradient0 * n, axis=1) + alpha * g0
            measure = float(np.sum(np.abs(residual) * area))
            if state == "H":
                assert measure < 1e-12
            measures.append(measure)
        print(label, state, "facets", len(p), "median", np.median(measures), "maximum", max(measures))
```

## Find only symmetry pairs already in the manifest

This produces eight translation matches and three reflection matches. Within-pair sorting affects voltage orientation; source/receiver exchange additionally requires reciprocity. The latter flag is printed explicitly, and all three saved reflection matches have it false.

```python
lookup = {tuple(row): index for index, row in enumerate(manifest)}
matches = []
for i, row in enumerate(manifest):
    for shift in range(-7, 8):
        if shift == 0 or np.any((row % 8 + shift < 0) | (row % 8 + shift > 7)):
            continue
        j = lookup.get(tuple(row + shift))
        if j is not None and i < j:
            matches.append(("translation_y", i, j, 1, False))
    transformed = 8 * (row // 8) + (7 - row % 8)
    sign = (1 if transformed[0] < transformed[1] else -1) * (1 if transformed[2] < transformed[3] else -1)
    role_swap = sorted(transformed[:2]) > sorted(transformed[2:])
    j = lookup.get(canonical_configuration(transformed))
    if j is not None and i < j:
        matches.append(("reflection_y", i, j, sign, role_swap))
for kind in ("translation_y", "reflection_y"):
    selected = [match for match in matches if match[0] == kind]
    print(kind, "pairs", len(selected))
    for method in ("linear", "p2"):
        for label in "AC":
            for state in ("H", "C10", "C100"):
                ref = np.load(root / f"{state}-reference-v.npy", allow_pickle=False)
                value = np.load(root / f"{method}-{label}-{state}-voltage-v.npy", allow_pickle=False)
                differences = []
                for _, i, j, sign, role_swap in selected:
                    assert abs(sign * ref[j] - ref[i]) < 1e-12
                    differences.append(abs(float(sign * value[j] - value[i])))
                    if kind == "reflection_y":
                        print("reflection pair", i, j, "role swap", role_swap)
                print(method, label, state, "max absolute native difference", max(differences))
```

The [published pair data](boundary-error-budget-review/2026-10-09/saved-symmetry-pairs.csv) includes every match and state rather than only the largest differences. These are limited post-hoc diagnostics, not a replacement experimental protocol.
