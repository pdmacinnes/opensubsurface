import argparse
from hashlib import sha256
from importlib.metadata import distribution, version
import json
from pathlib import Path
import platform
import time

import numpy as np


REFERENCES = {"H": [-0.0006476359420855907] * 2, "C100": [-0.06000386265259415] * 2}
HISTORICAL_C100 = [-0.05981245281773522, -0.059951241221804834]
AXIS_HASHES = {"x": "f591859a43fa6ca2a41c9d45e4324e147cac2e04f3538ec36471d43fdbf85f69",
               "y": "f591859a43fa6ca2a41c9d45e4324e147cac2e04f3538ec36471d43fdbf85f69",
               "z": "237f2e44066821b3cb57c1049483cc006c1c161be89d103017dc211fc53a1fce"}


def load_inputs(path):
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    if config.get("current_a") != 0.001:
        raise ValueError("Frozen current must be 0.001 A")
    expected = np.array([(x, y, 0.) for x in np.arange(-10.5, 10.6, 3.) for y in np.arange(-10.5, 10.6, 3.)])
    if not np.array_equal(config.get("sensors_m"), expected):
        raise ValueError("All 64 original sensors must retain their coordinates and order")
    if not np.array_equal(config.get("abmn"), [[26,36,52,62], [29,35,51,57]]):
        raise ValueError("Frozen ABMN rows must retain distinct integer indices and orientation")
    if config.get("states_ohm_m") != {"H": [100.,100.], "C100": [100.,10000.]}:
        raise ValueError("Frozen resistivity states changed")
    if config.get("references_v") != REFERENCES or config.get("historical_v", {}).get("C100") != HISTORICAL_C100:
        raise ValueError("Frozen analytical or historical comparison values changed")
    historical_h = np.asarray(config["historical_v"].get("H"), dtype=float)
    if historical_h.shape != (2,) or not np.all(np.isfinite(historical_h)) or np.max(np.abs(historical_h - REFERENCES["H"])) > 1e-12:
        raise ValueError("Historical homogeneous values do not pass the control")
    for name in "xyz":
        axis = np.asarray(config.get("axes_m", {}).get(name, []), dtype="<f8")
        if axis.ndim != 1 or len(axis) != (19 if name == "z" else 37) or not np.all(np.isfinite(axis)) or not np.all(np.diff(axis) > 0):
            raise ValueError("Axes must be finite and strictly ordered")
        if sha256(axis.tobytes()).hexdigest() != AXIS_HASHES[name] or 0. not in axis:
            raise ValueError("Frozen mesh axis changed")
        if name != "z" and (not np.array_equal(axis, -axis[::-1]) or not np.all(np.isin(expected[:, "xy".index(name)], axis))):
            raise ValueError("Horizontal axes must retain reflection symmetry and sensor nodes")
    rows = np.asarray(config["abmn"], dtype=int)
    if not np.array_equal(expected[rows[1]], expected[rows[0]] * [1,-1,1]):
        raise ValueError("The two rows must be coordinate reflections without a role swap")
    return config


def measurement(values, reference, historical):
    values = np.asarray(values, dtype=float)
    if values.shape != (2,) or not np.all(np.isfinite(values)):
        raise ValueError("Native output must contain two finite voltages")
    error = values - np.asarray(reference)
    parity = values - np.asarray(historical)
    difference = float(values[1] - values[0])
    return {"status": "completed", "voltage_v": values.tolist(), "reference_v": list(reference),
            "reference_error_v": error.tolist(), "historical_v": list(historical), "historical_error_v": parity.tolist(),
            "pair_difference_v": difference,
            "homogeneous_control_passed": bool(np.max(np.abs(error)) <= 1e-12 and abs(difference) <= 1e-12),
            "historical_parity_passed": bool(np.max(np.abs(parity)) <= 1e-9)}


def decision(states, status):
    if status != "completed" or any(states.get(name, {}).get("status") != "completed" for name in ("H", "C100")):
        return "inconclusive"
    if not states["H"]["homogeneous_control_passed"]:
        return "inconclusive"
    return "reproduced" if states["C100"]["historical_parity_passed"] and abs(states["C100"]["pair_difference_v"]) > 1e-6 else "not reproduced"


def build_mesh(config):
    import pygimli as pg

    axes = config["axes_m"]
    linear = pg.createGrid(x=axes["x"], y=axes["y"], z=axes["z"])
    mesh = linear.createP2()
    if mesh.cellCount() != 23328 or mesh.nodeCount() != 101269:
        raise ValueError("P2 topology differs from the published C mesh")
    original = {tuple(cell.center()): cell for cell in linear.cells()}
    for cell in mesh.cells():
        old = original.get(tuple(cell.center()))
        if old is None or cell.nodeCount() != 20:
            raise ValueError("P2 cell correspondence or element order changed")
        xyz = np.array([list(node.pos()) for node in cell.nodes()])
        old_xyz = np.array([list(node.pos()) for node in old.nodes()])
        if not np.array_equal(xyz.min(axis=0), old_xyz.min(axis=0)) or not np.array_equal(xyz.max(axis=0), old_xyz.max(axis=0)):
            raise ValueError("P2 cell geometry changed")
        if xyz[:,0].min() < 0 < xyz[:,0].max():
            raise ValueError("A material cell crosses the contact")
    nodes = {tuple(node.pos()) for node in mesh.nodes()}
    if not all(tuple(sensor) in nodes for sensor in config["sensors_m"]):
        raise ValueError("A sensor is not an exact P2 node")
    mesh.createNeighborInfos()
    counts = {"-1": 0, "-2": 0}
    for boundary in mesh.boundaries():
        if boundary.outside():
            marker = -1 if abs(boundary.center().z()) < 1e-10 else -2
            boundary.setMarker(marker)
            if boundary.marker() != marker:
                raise ValueError("Boundary assignment failed")
            counts[str(marker)] += 1
    if counts != {"-1": 1296, "-2": 3888}:
        raise ValueError("Outside boundary topology changed")
    return mesh, {"cells": mesh.cellCount(), "nodes": mesh.nodeCount(), "nodes_per_cell": 20,
                  "cell_geometry_preserved": True, "exact_sensor_nodes": True, "straddling_cells": 0,
                  "boundary_counts": counts, "inherited_materials_trusted": False}


def solve_state(mesh, config, state):
    import pygimli as pg
    from pygimli.physics import ert

    scheme = pg.DataContainerERT()
    for sensor in config["sensors_m"]:
        scheme.createSensor(sensor)
    scheme.resize(2)
    for name, values in zip("abmn", np.asarray(config["abmn"]).T):
        scheme[name] = values
    scheme["valid"] = [1., 1.]
    left, right = config["states_ohm_m"][state]
    resistivity = np.where(np.array([cell.center().x() for cell in mesh.cells()]) < 0, left, right)
    mesh.setCellAttributes(resistivity)
    fop = ert.ERTModelling(sr=True, verbose=False)
    fop.data = scheme
    fop.setMesh(mesh, ignoreRegionManager=True)
    fop.mapERTModel(resistivity, 0)
    core_mesh = fop._core.mesh()
    if core_mesh.cellCount() != 23328 or core_mesh.nodeCount() != 101269 or not np.array_equal(core_mesh.cellAttributes(), resistivity):
        raise ValueError("Native topology or explicit material assignment changed")
    data = pg.core.DataMap()
    fop.calculate(data)
    return np.asarray(data.data(scheme)) * config["current_a"]


def environment():
    import pygimli as pg

    dist = distribution("pgcore")
    return {"python": platform.python_version(), "platform": platform.system(), "gpu_used": False,
            "versions": {name: version(name) for name in ("numpy", "pygimli", "pgcore")},
            "native_core_version": pg.core.versionStr(), "python_reported_version": pg.__version__,
            "python_reported_version_role": "separate identifier; may reflect an enclosing checkout",
            "native_binary_sha256": {str(file).replace("\\", "/"): sha256(dist.locate_file(file).read_bytes()).hexdigest()
                for file in dist.files if str(file).endswith((".pyd", ".dll")) or ".so" in Path(file).name},
            "equation_residual": "unavailable", "reference_constraints": "unavailable"}


def save(path, result):
    payload = json.dumps(result, indent=2, allow_nan=False) + "\n"
    path.write_text(payload, encoding="utf-8", newline="\n")
    print(payload, flush=True)


def run(config, output, identity):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8"):
        pass
    started = time.perf_counter()
    result = {"status": "started", "identity": identity, "states": {state: {"status": "skipped", "reason": "not reached"} for state in ("H", "C100")},
              "state_solve_attempts": 0, "decision": "inconclusive"}
    save(output, result)
    try:
        result["environment"] = environment()
        mesh, checks = build_mesh(config)
        result["geometry"] = checks
        for state in ("H", "C100"):
            if state == "C100" and not result["states"]["H"]["homogeneous_control_passed"]:
                result["states"][state] = {"status": "skipped", "reason": "homogeneous control failed"}
                break
            result["states"][state] = {"status": "attempted"}
            result["state_solve_attempts"] += 1
            save(output, result)
            state_started = time.perf_counter()
            values = solve_state(mesh, config, state)
            result["states"][state] = measurement(values, config["references_v"][state], config["historical_v"][state])
            result["states"][state]["wall_seconds"] = time.perf_counter() - state_started
            save(output, result)
        result["status"] = "completed"
    except BaseException as error:
        result.update(status="failed", exception_type=type(error).__name__)
        raise
    finally:
        result["wall_seconds"] = time.perf_counter() - started
        result["decision"] = decision(result["states"], result["status"])
        save(output, result)
    return result


def main():
    parser = argparse.ArgumentParser(description="Standalone reproduction of pyGIMLi issue 979")
    parser.add_argument("--inputs", type=Path, default=Path(__file__).with_name("inputs.json"))
    parser.add_argument("--output", type=Path, default=Path("results.json"))
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    config = load_inputs(args.inputs)
    identity = {"input_sha256": sha256(args.inputs.read_bytes()).hexdigest(), "script_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
                "source_provenance": config["provenance"]}
    if args.validate_only:
        print(json.dumps({"status": "inputs valid", "identity": identity, "sensor_count": 64, "measurement_count": 2}))
        return
    result = run(config, args.output, identity)
    if result["decision"] == "inconclusive":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
