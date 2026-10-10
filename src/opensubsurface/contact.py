import argparse
from hashlib import sha256
from importlib.metadata import distribution, version
import json
import os
from pathlib import Path
import platform
import time

import numpy as np

from .domain import CURRENT_A, electrodes, homogeneous_voltage, noise_sigma, normalized_discrepancy
from .pilot import save_json
from .solvers import MeshSettings, PygimliForward, ResourceSample, graded_axis
from .validation import frozen_inputs


STATES = {"H": (100., 100.), "C10": (100., 1000.), "C100": (100., 10000.)}
LIMIT_SECONDS = 7200.
DEVELOPMENT_ALLOWANCE_SECONDS = 600.


def green_and_gradient(points, source, rho_left, rho_right, receiver_side=None):
    points = np.asarray(points, dtype=float)
    source = np.asarray(source, dtype=float)
    if points.ndim != 2 or points.shape[1] != 3 or source.shape != (3,):
        raise ValueError("Expected receiver coordinates (n,3) and one source (3,)")
    if not np.all(np.isfinite(points)) or not np.all(np.isfinite(source)) or np.any(points[:, 2] > 0):
        raise ValueError("Coordinates must be finite and receivers in the ground or surface")
    if source[2] != 0 or source[0] == 0:
        raise ValueError("Source must lie on the surface away from the contact")
    if any(not np.isfinite(rho) or rho <= 0 for rho in (rho_left, rho_right)):
        raise ValueError("Resistivities must be positive and finite")
    source_left = source[0] < 0
    sigma_source, sigma_other = (1 / rho_left, 1 / rho_right) if source_left else (1 / rho_right, 1 / rho_left)
    difference = points - source
    radius = np.linalg.norm(difference, axis=1)
    if np.any(radius == 0):
        raise ValueError("Receiver coincides with a point source")
    if receiver_side not in (None, "left", "right"):
        raise ValueError("Unknown contact limit side")
    receiver_left = points[:, 0] < 0
    if receiver_side is not None:
        receiver_left = np.where(points[:, 0] == 0, receiver_side == "left", receiver_left)
    same = receiver_left == source_left
    coefficient = 1 / (np.pi * (sigma_source + sigma_other))
    potential = coefficient / radius
    gradient = -coefficient * difference / radius[:, None] ** 3
    # Evaluate the image only in its virtual region; a real receiver can sit on it.
    image = source * np.array([-1., 1., 1.])
    image_difference = points[same] - image
    image_radius = np.linalg.norm(image_difference, axis=1)
    reflection = (sigma_source - sigma_other) / (sigma_source + sigma_other)
    scale = 1 / (2 * np.pi * sigma_source)
    potential[same] = scale * (1 / radius[same] + reflection / image_radius)
    gradient[same] = -scale * (difference[same] / radius[same, None] ** 3
                              + reflection * image_difference / image_radius[:, None] ** 3)
    return potential, gradient


def contact_voltage(locations, manifest, rho_left, rho_right, current=CURRENT_A):
    if not np.isfinite(current) or current <= 0:
        raise ValueError("Injection current must be positive and finite")
    voltage = np.zeros(len(manifest))
    for source_column, receiver_column, sign in ((0, 2, 1), (1, 2, -1), (0, 3, -1), (1, 3, 1)):
        for source_index in np.unique(manifest[:, source_column]):
            selected = manifest[:, source_column] == source_index
            values, _ = green_and_gradient(locations[manifest[selected, receiver_column]], locations[source_index], rho_left, rho_right)
            voltage[selected] += sign * current * values
    return voltage


def verify_reference(locations, manifest):
    a, b = np.array([-3., 0., 0.]), np.array([3., 0., 0.])
    receivers = np.array([[-1., 0., 0.], [1., 0., 0.]])
    literal = np.r_[green_and_gradient(receivers, a, 100., 1000.)[0],
                    green_and_gradient(receivers, b, 100., 1000.)[0]] * CURRENT_A
    expected = np.array([31 / 880, 1 / 44, 1 / 44, 13 / 88]) / np.pi
    np.testing.assert_allclose(literal, expected, rtol=1e-12, atol=1e-14)
    np.testing.assert_allclose(literal[0] - literal[2] - literal[1] + literal[3], 11 / (80 * np.pi), rtol=1e-12, atol=1e-14)
    contact = np.array([[0., 0., 0.], [0., 2., 0.], [0., 0., -2.], [0., 2., -2.]])
    reference = contact_voltage(locations, manifest, 100., 100.)
    np.testing.assert_allclose(reference, homogeneous_voltage(locations, manifest), rtol=1e-12, atol=1e-14)
    checks = {}
    for state, (left, right) in STATES.items():
        continuity, flux, surface, reciprocity = 0., 0., 0., 0.
        for source in (a, b):
            l, dl = green_and_gradient(contact, source, left, right, "left")
            r, dr = green_and_gradient(contact, source, left, right, "right")
            continuity = max(continuity, float(np.max(np.abs(l - r) / np.maximum(np.maximum(np.abs(l), np.abs(r)), 1e-30))))
            jl, jr = -dl[:, 0] / left, -dr[:, 0] / right
            flux = max(flux, float(np.max(np.abs(jl - jr) / np.maximum(np.maximum(np.abs(jl), np.abs(jr)), 1e-30))))
            _, derivative = green_and_gradient(np.array([[-1., 1., 0.], [1., 1., 0.]]), source, left, right)
            surface = max(surface, float(np.max(np.abs(derivative[:, 2]))))
        matrix = np.zeros((64, 64))
        for index, source in enumerate(locations):
            selected = np.arange(64) != index
            matrix[index, selected] = green_and_gradient(locations[selected], source, left, right)[0]
        reciprocity = float(np.max(np.abs(matrix - matrix.T) / np.maximum(np.maximum(np.abs(matrix), np.abs(matrix.T)), 1e-30)))
        if max(continuity, flux, surface, reciprocity) > 1e-10:
            raise ValueError("Analytical boundary or reciprocity identity failed")
        checks[state] = {"scaled_continuity": continuity, "scaled_normal_current": flux,
                         "surface_normal_derivative": surface, "scaled_reciprocity": reciprocity}
    left_limit = green_and_gradient(contact[:1], a, 100., 1000., "left")[0] * CURRENT_A
    np.testing.assert_allclose(left_limit, 1 / (33 * np.pi), rtol=1e-12, atol=1e-14)
    return {"passed": True, "literal_voltages_v": literal.tolist(), "literal_expected_v": expected.tolist(),
            "normalization": "identity difference divided by maximum magnitude of the two terms, with 1e-30 floor; surface derivative is absolute and exactly zero", "identities": checks}


def mesh_axes(label):
    if label not in ("A", "B", "C", "D"):
        raise ValueError("Only the four approved meshes are supported")
    xy = graded_axis(1.5, 64., 1.5)
    z = graded_axis(1.5, 64., 1.5, vertical=True)
    if label in ("C", "D"):
        xy = np.unique(np.r_[xy, graded_axis(1.5, 128., 1.5)])
        z = np.unique(np.r_[z, graded_axis(1.5, 128., 1.5, vertical=True)])
    if label in ("B", "D"):
        xy = np.unique(np.r_[xy, np.arange(-12., 12.001, .75)])
        z = np.unique(np.r_[z, np.arange(-12., .001, .75)])
    return xy, xy.copy(), z


def verify_axes(axes):
    for coarse, fine in (("A", "B"), ("C", "D")):
        for index, (a, b) in enumerate(zip(axes[coarse], axes[fine])):
            assert np.all(np.isin(a, b))
            outside_a = a[(a < -12) | (a > (0 if index == 2 else 12))]
            outside_b = b[(b < -12) | (b > (0 if index == 2 else 12))]
            np.testing.assert_array_equal(outside_a, outside_b)
    for inner, extended in (("A", "C"), ("B", "D")):
        for a, b in zip(axes[inner], axes[extended]):
            np.testing.assert_array_equal(a, b[(b >= a[0]) & (b <= a[-1])])
    for label, vectors in axes.items():
        extent = 128. if label in ("C", "D") else 64.
        for index, axis in enumerate(vectors):
            assert np.all(np.diff(axis) > 0) and axis[0] == -extent
            assert axis[-1] == (0 if index == 2 else extent) and 0 in axis
            if index < 2:
                assert np.all(np.isin(electrodes()[:, index], axis))
    return {"passed": True, "contact_on_faces": True, "coarse_nodes_retained": True,
            "remote_intervals_unchanged_by_core_refinement": True, "inner_intervals_retained_by_extension": True}


def prepare(output):
    if output.exists():
        raise ValueError("Use a fresh study directory; accepted data cannot be overwritten")
    output.mkdir(parents=True)
    started = time.perf_counter()
    config, manifest = frozen_inputs()
    locations = np.array(config["electrodes_m"])
    np.testing.assert_array_equal(locations, electrodes())
    if config["current_a"] != CURRENT_A:
        raise ValueError("Frozen source current differs")
    payload = Path("experiments/ert-observability-pilot/results/2026-10-08/candidate-manifest.csv").read_bytes()
    (output / "candidate-manifest.csv").write_bytes(payload)
    save_json(output / "reference-checks.json", verify_reference(locations, manifest))
    axes = {label: mesh_axes(label) for label in "ABCD"}
    save_json(output / "axis-checks.json", verify_axes(axes))
    for label, vectors in axes.items():
        for name, axis in zip(("x", "y", "z"), vectors):
            np.save(output / f"{label}-{name}-axis-m.npy", axis, allow_pickle=False)
    for state, (left, right) in STATES.items():
        np.save(output / f"{state}-reference-v.npy", contact_voltage(locations, manifest, left, right), allow_pickle=False)
    np.save(output / "fixed-sigma-v.npy", noise_sigma(homogeneous_voltage(locations, manifest), .01, 1e-6), allow_pickle=False)
    save_json(output / "configuration.json", {"states_ohm_m": STATES, "current_a": CURRENT_A,
              "electrodes_m": locations.tolist(), "manifest_sha256": sha256(payload).hexdigest(),
              "rms_threshold": .1, "maximum_threshold": .25, "worker_cap_seconds": LIMIT_SECONDS,
              "development_allowance_seconds": DEVELOPMENT_ALLOWANCE_SECONDS, "memory_cap_gib": 8,
              "model": "infinite vertical x=0 contact in flat z<0 half-space; no contact resistance",
              "native_formulation": "pyGIMLi DCSR, homogeneous analytical singularity treatment; standard mixed outer boundaries; exact contact field not supplied"})
    save_json(output / "environment.json", {"python": platform.python_version(), "platform": platform.system(),
              "machine": platform.machine(), "gpu_used": False,
              "versions": {name: version(name) for name in ("numpy", "scipy", "pygimli", "pgcore", "psutil")},
              "thread_limits": {key: os.environ.get(key) for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS")},
              "pygimli_runtime_version": __import__("pygimli").__version__,
              "pygimli_runtime_version_role": "Python-reported identifier; may derive from enclosing project Git history",
              "native_core_version": __import__("pygimli").core.versionStr(),
              "native_binary_sha256": {str(file): sha256(distribution("pgcore").locate_file(file).read_bytes()).hexdigest()
                                       for file in distribution("pgcore").files
                                       if str(file).endswith((".pyd", ".dll")) or ".so" in Path(file).name},
              "installed_python_source_sha256": {"pygimli/" + name:
                  sha256((Path(__import__("pygimli").__file__).parent / name).read_bytes()).hexdigest()
                  for name in ("physics/ert/ert.py", "physics/ert/ertModelling.py", "frameworks/modelling.py", "_version.py")},
              "source_sha256": {name: sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in ("contact.py", "solvers.py")}})
    save_json(output / "preparation.json", {"wall_seconds": time.perf_counter() - started})


def spent_seconds(output):
    preparation = json.loads((output / "preparation.json").read_text())["wall_seconds"]
    return DEVELOPMENT_ALLOWANCE_SECONDS + preparation + sum(json.loads(path.read_text()).get("worker_wall_seconds", 0.) for path in output.glob("worker-*.json"))


def primary_field_diagnostics(core):
    diagnostics = {"primaryMesh": {"status": "not queried",
        "reason": "optional native mesh is absent for the flat analytical primary; getter assumes a non-null pointer"}}
    try:
        potential = core.primaryPotential()
        diagnostics["primaryPotential"] = {"rows": potential.rows(), "columns": potential.cols()}
    except Exception as error:
        diagnostics["primaryPotential"] = {"status": "unavailable", "exception_type": type(error).__name__}
    return diagnostics


def worker(output, label):
    if label not in "ABCD" or len(label) != 1:
        raise ValueError("Unknown mesh label")
    path = output / f"worker-{label}.json"
    if path.exists():
        raise ValueError("Accepted or attempted workers cannot be overwritten")
    if (output / "resource-limit.json").exists() or spent_seconds(output) >= LIMIT_SECONDS:
        raise RuntimeError("The study has a resource stop or exhausted budget")
    config = json.loads((output / "configuration.json").read_text())
    payload = (output / "candidate-manifest.csv").read_bytes()
    if sha256(payload).hexdigest() != config["manifest_sha256"]:
        raise ValueError("Study manifest changed")
    if not json.loads((output / "reference-checks.json").read_text())["passed"]:
        raise ValueError("Reference gate did not pass")
    manifest = np.loadtxt(output / "candidate-manifest.csv", delimiter=",", skiprows=1, dtype=int)
    sigma = np.load(output / "fixed-sigma-v.npy", allow_pickle=False)
    axes = [np.load(output / f"{label}-{name}-axis-m.npy", allow_pickle=False) for name in ("x", "y", "z")]
    for actual, expected in zip(axes, mesh_axes(label)):
        np.testing.assert_array_equal(actual, expected)
    os.environ["OPENSUBSURFACE_OUTPUT"] = str(output)
    os.environ["OPENSUBSURFACE_DEADLINE"] = str(time.time() + LIMIT_SECONDS - spent_seconds(output))
    started = time.perf_counter()
    record = {"mesh": label, "states": {}, "status": "started", "worker_wall_seconds": 0.}
    save_json(path, record)
    try:
        import pygimli as pg
        from pygimli.physics import ert
        with ResourceSample() as whole_worker:
            with ResourceSample() as construction:
                mesh = pg.createGrid(x=axes[0], y=axes[1], z=axes[2])
                adapter = PygimliForward.__new__(PygimliForward)
                adapter.attach_mesh(mesh, MeshSettings(1.5 if label in "AC" else .75, 64 if label in "AB" else 128), manifest)
                straddling = sum(min(node.pos().x() for node in cell.nodes()) < 0 < max(node.pos().x() for node in cell.nodes()) for cell in mesh.cells())
                if straddling:
                    raise ValueError("A cell spans the contact")
                nodes = np.array([list(node.pos()) for node in mesh.nodes()])
                from scipy.spatial import cKDTree
                electrode_error = float(cKDTree(nodes).query(electrodes())[0].max())
                if electrode_error != 0:
                    raise ValueError("Electrodes are not exact mesh nodes")
            record["construction"] = construction.record()
            record["geometry_checks"] = {"straddling_cells": straddling, "maximum_electrode_node_error_m": electrode_error}
            for state, (left, right) in STATES.items():
                if state != "H" and not record["states"]["H"]["check"]["passed"]:
                    record["states"][state] = {"status": "skipped", "reason": "homogeneous gate failed"}
                    continue
                record["states"][state] = {"status": "attempted"}
                record["worker_wall_seconds"] = time.perf_counter() - started
                save_json(path, record)
                resistivity = np.where(adapter.centers[:, 0] < 0, left, right)
                with ResourceSample() as resources:
                    fop = ert.ERTModelling(sr=True, verbose=False)
                    fop.data = adapter.scheme
                    fop.setMesh(mesh, ignoreRegionManager=True)
                    fop.mapERTModel(resistivity, 0)
                    data_map = pg.core.DataMap()
                    fop.calculate(data_map)
                    voltage = np.array(data_map.data(adapter.scheme)) * CURRENT_A
                    diagnostics = {"input_cells": mesh.cellCount(), "input_nodes": mesh.nodeCount(),
                        "operator_cells": fop.mesh().cellCount(), "operator_nodes": fop.mesh().nodeCount(),
                        "core_cells": fop._core.mesh().cellCount(), "core_nodes": fop._core.mesh().nodeCount(),
                        "maximum_relative_equation_residual": "unavailable from this adapter"}
                    diagnostics.update(primary_field_diagnostics(fop._core))
                if voltage.shape != (4096,) or not np.all(np.isfinite(voltage)):
                    raise ValueError("Native voltage array is invalid")
                np.save(output / f"{label}-{state}-voltage-v.npy", voltage, allow_pickle=False)
                reference = np.load(output / f"{state}-reference-v.npy", allow_pickle=False)
                check = normalized_discrepancy(voltage, reference, sigma)
                worst = int(np.argmax(np.abs((voltage - reference) / sigma)))
                record["states"][state] = {"status": "completed", "check": check, "resources": resources.record(),
                    "native_diagnostics": diagnostics, "worst_manifest_index": worst,
                    "worst_configuration": manifest[worst].tolist()}
                record["worker_wall_seconds"] = time.perf_counter() - started
                save_json(path, record)
                print(json.dumps({"mesh": label, "state": state, **check}), flush=True)
            record["status"] = "completed"
        record["resources"] = whole_worker.record()
    except Exception as error:
        record["status"] = "failed"
        record["exception_type"] = type(error).__name__
        # Tracebacks stay in local logs; public error records contain no user paths.
        print(f"Worker failed: {type(error).__name__}", flush=True)
        raise
    finally:
        record["worker_wall_seconds"] = time.perf_counter() - started
        save_json(path, record)


def main():
    parser = argparse.ArgumentParser(description="Approved exact vertical-contact DC benchmark")
    parser.add_argument("phase", choices=("prepare", "worker"))
    parser.add_argument("--output", type=Path, default=Path("experiments/outputs/ert-contact-benchmark"))
    parser.add_argument("--mesh", choices=tuple("ABCD"))
    args = parser.parse_args()
    if args.phase == "prepare":
        prepare(args.output)
    elif args.mesh is None:
        parser.error("worker requires --mesh")
    else:
        worker(args.output, args.mesh)


if __name__ == "__main__":
    main()
