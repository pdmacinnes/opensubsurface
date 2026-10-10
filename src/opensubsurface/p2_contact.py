import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import time

import numpy as np
from scipy.spatial import cKDTree

from .contact import STATES, LIMIT_SECONDS, DEVELOPMENT_ALLOWANCE_SECONDS, prepare as prepare_contact, primary_field_diagnostics
from .contact_report import build_report as verify_linear_record
from .domain import CURRENT_A, electrodes, normalized_discrepancy
from .pilot import save_json
from .solvers import MeshSettings, PygimliForward, ResourceSample


BASELINE = Path("experiments/ert-contact-benchmark/results/2026-10-09")


def expected_nodes(axes):
    x, y, z = map(len, axes)
    return x * y * z + (x - 1) * y * z + x * (y - 1) * z + x * y * (z - 1)


def resource_plan(peak_a_bytes, seconds_a, nodes_a, nodes_c, remaining_seconds):
    factor = 1.25 * (nodes_c / nodes_a) ** 2
    projected_bytes = factor * peak_a_bytes
    projected_seconds = factor * seconds_a
    return {"factor": factor, "nodes_A": nodes_a, "nodes_C": nodes_c,
            "projected_peak_bytes": projected_bytes, "projected_worker_seconds": projected_seconds,
            "remaining_seconds": remaining_seconds, "allowed": projected_bytes <= 8 * 2**30 and projected_seconds <= remaining_seconds,
            "method": "approved 1.25 times squared node ratio; planning heuristic, not a bound"}


def prepare(output):
    if output.exists():
        raise ValueError("Use a fresh P2 study directory")
    started = time.perf_counter()
    baseline_summary = verify_linear_record(BASELINE)
    prepare_contact(output)
    for label in "BD":
        for name in "xyz":
            (output / f"{label}-{name}-axis-m.npy").unlink()
    for label in "AC":
        for name in "xyz":
            source = BASELINE / f"{label}-{name}-axis-m.npy"
            np.testing.assert_array_equal(np.load(source, allow_pickle=False), np.load(output / source.name, allow_pickle=False))
        for state in STATES:
            shutil.copy2(BASELINE / f"{label}-{state}-voltage-v.npy", output / f"linear-{label}-{state}-voltage-v.npy")
        shutil.copy2(BASELINE / f"worker-{label}.json", output / f"linear-worker-{label}.json")
    config = json.loads((output / "configuration.json").read_text())
    config.update({"study": "explicit P2 comparison on frozen A/C cells", "mesh_labels": ["A", "C"],
                   "maximum_state_solves": 6, "diagnostic_ratio_threshold": .25,
                   "native_formulation": "explicit createP2 once; direct per-cell DCSR; no managed H2 refinement",
                   "baseline_raw_data_sha256": json.loads((BASELINE / "raw-data-sha256.json").read_text())})
    save_json(output / "configuration.json", config)
    save_json(output / "baseline-verification.json", {"passed": True, "scope": "all original raw checksums and metrics verified",
              "baseline_scientific_status": baseline_summary["scientific_status"]})
    environment = json.loads((output / "environment.json").read_text())
    environment["source_sha256"]["p2_contact.py"] = sha256(Path(__file__).read_bytes()).hexdigest()
    save_json(output / "environment.json", environment)
    save_json(output / "preparation.json", {"wall_seconds": time.perf_counter() - started})


def correspondence(linear, quadratic):
    if quadratic.cellCount() != linear.cellCount():
        raise ValueError("P2 changed the material cell count")
    old = np.array([list(cell.center()) for cell in linear.cells()])
    new = np.array([list(cell.center()) for cell in quadratic.cells()])
    distance, mapping = cKDTree(old).query(new)
    if np.max(distance) > 1e-12 or len(set(mapping)) != len(mapping):
        raise ValueError("P2 material cell correspondence failed")
    if any(cell.nodeCount() != 20 for cell in quadratic.cells()):
        raise ValueError("P2 cells do not have twenty nodes")
    for cell in quadratic.cells():
        coordinates = np.array([list(node.pos()) for node in cell.nodes()])
        original = np.array([list(node.pos()) for node in linear.cell(int(mapping[cell.id()])).nodes()])
        if not np.array_equal(coordinates.min(axis=0), original.min(axis=0)) or not np.array_equal(coordinates.max(axis=0), original.max(axis=0)):
            raise ValueError("P2 changed a cell's material extent")
        if coordinates[:, 0].min() < 0 < coordinates[:, 0].max():
            raise ValueError("A P2 cell spans the contact")
    np.testing.assert_array_equal(np.array(quadratic.cellMarkers()), np.array(linear.cellMarkers())[mapping])
    nodes = np.array([list(node.pos()) for node in quadratic.nodes()])
    if cKDTree(nodes).query(electrodes())[0].max() != 0:
        raise ValueError("Electrodes are not exact P2 nodes")
    return mapping, {"passed": True, "material_cells": linear.cellCount(), "linear_nodes": linear.nodeCount(),
                     "p2_nodes": quadratic.nodeCount(), "nodes_per_cell": 20,
                     "maximum_center_error_m": float(distance.max()), "straddling_cells": 0,
                     "cell_extents_preserved": True, "markers_preserved": True,
                     "exact_electrodes": True, "inherited_attributes_trusted": False}


def spent(output):
    return DEVELOPMENT_ALLOWANCE_SECONDS + json.loads((output / "preparation.json").read_text())["wall_seconds"] + sum(
        json.loads(path.read_text()).get("worker_wall_seconds", 0.) for path in output.glob("p2-worker-*.json"))


def worker(output, label):
    if label not in ("A", "C"):
        raise ValueError("Only A-P2 and C-P2 are approved")
    path = output / f"p2-worker-{label}.json"
    if path.exists():
        raise ValueError("An attempted or accepted P2 worker cannot be overwritten")
    record = {"mesh": label, "status": "started", "states": {}, "worker_wall_seconds": 0.}
    config = json.loads((output / "configuration.json").read_text())
    axes = [np.load(output / f"{label}-{name}-axis-m.npy", allow_pickle=False) for name in "xyz"]
    for name, axis in zip("xyz", axes):
        np.testing.assert_array_equal(axis, np.load(BASELINE / f"{label}-{name}-axis-m.npy", allow_pickle=False))
    payload = (output / "candidate-manifest.csv").read_bytes()
    if sha256(payload).hexdigest() != config["manifest_sha256"] or payload != (BASELINE / "candidate-manifest.csv").read_bytes():
        raise ValueError("Frozen manifest changed")
    sigma = np.load(output / "fixed-sigma-v.npy", allow_pickle=False)
    np.testing.assert_array_equal(sigma, np.load(BASELINE / "fixed-sigma-v.npy", allow_pickle=False))
    if not json.loads((output / "reference-checks.json").read_text())["passed"]:
        raise ValueError("Reference identities did not pass")
    reason = None
    if (output / "resource-limit.json").exists() or spent(output) >= LIMIT_SECONDS:
        reason = "resource stop or exhausted worker budget"
    if label == "C":
        a_path = output / "p2-worker-A.json"
        if not a_path.exists():
            raise ValueError("Profile A-P2 before C-P2")
        a_record = json.loads(a_path.read_text())
        if a_record["status"] != "completed" or not a_record["states"].get("H", {}).get("check", {}).get("passed"):
            reason = "A-P2 failed or its homogeneous gate did not pass"
        elif reason is None:
            plan = resource_plan(a_record["resources"]["peak_rss_bytes"], a_record["worker_wall_seconds"],
                                 a_record["geometry"]["p2_nodes"], expected_nodes(axes), LIMIT_SECONDS - spent(output))
            record["resource_plan"] = plan
            if not plan["allowed"]:
                reason = "approved memory/time projection exceeds remaining resources"
    if reason:
        record.update(status="skipped", reason=reason, states={state: {"status": "skipped", "reason": reason} for state in STATES})
        save_json(path, record)
        print(json.dumps({"mesh": label, "status": "skipped", "reason": reason, "resource_plan": record.get("resource_plan")}), flush=True)
        return
    manifest = np.loadtxt(output / "candidate-manifest.csv", delimiter=",", skiprows=1, dtype=int)
    os.environ["OPENSUBSURFACE_OUTPUT"] = str(output)
    os.environ["OPENSUBSURFACE_DEADLINE"] = str(time.time() + LIMIT_SECONDS - spent(output))
    started = time.perf_counter()
    save_json(path, record)
    try:
        import pygimli as pg
        from pygimli.physics import ert
        with ResourceSample() as whole_worker:
            with ResourceSample() as construction:
                linear = pg.createGrid(x=axes[0], y=axes[1], z=axes[2])
                mesh = linear.createP2()
                mapping, geometry = correspondence(linear, mesh)
                if mesh.nodeCount() != expected_nodes(axes):
                    raise ValueError("P2 node count differs from the declared topology")
                np.save(output / f"{label}-cell-correspondence.npy", mapping, allow_pickle=False)
                np.save(output / f"{label}-cell-centers-m.npy", np.array([list(cell.center()) for cell in mesh.cells()]), allow_pickle=False)
                adapter = PygimliForward.__new__(PygimliForward)
                adapter.attach_mesh(mesh, MeshSettings(1.5, 64 if label == "A" else 128), manifest)
                outside = [boundary for boundary in mesh.boundaries() if boundary.outside()]
                if any(boundary.marker() != (-1 if abs(boundary.center().z()) < 1e-10 else -2) for boundary in outside):
                    raise ValueError("P2 boundary labels do not match the baseline convention")
                geometry["boundary_counts"] = {str(marker): sum(boundary.marker() == marker for boundary in outside) for marker in (-1, -2)}
                geometry["boundary_convention_verified"] = True
            record.update(geometry=geometry, construction=construction.record())
            for state, (left, right) in STATES.items():
                if state != "H" and not record["states"]["H"]["check"]["passed"]:
                    record["states"][state] = {"status": "skipped", "reason": "P2 homogeneous gate failed"}
                    continue
                if time.time() >= float(os.environ["OPENSUBSURFACE_DEADLINE"]):
                    raise RuntimeError("Remaining P2 budget exhausted")
                record["states"][state] = {"status": "attempted"}
                record["worker_wall_seconds"] = time.perf_counter() - started
                save_json(path, record)
                resistivity = np.where(adapter.centers[:, 0] < 0, left, right)
                mesh.setCellAttributes(resistivity)
                np.save(output / f"{label}-{state}-resistivity-ohm-m.npy", resistivity, allow_pickle=False)
                with ResourceSample() as resources:
                    fop = ert.ERTModelling(sr=True, verbose=False)
                    fop.data = adapter.scheme
                    fop.setMesh(mesh, ignoreRegionManager=True)
                    fop.mapERTModel(resistivity, 0)
                    core_mesh = fop._core.mesh()
                    np.testing.assert_array_equal(np.array(core_mesh.cellAttributes()), resistivity)
                    if core_mesh.cellCount() != mesh.cellCount() or core_mesh.nodeCount() != mesh.nodeCount():
                        raise ValueError("The native path changed the verified P2 topology")
                    data_map = pg.core.DataMap()
                    fop.calculate(data_map)
                    voltage = np.array(data_map.data(adapter.scheme)) * CURRENT_A
                    diagnostics = {"core_cells": core_mesh.cellCount(), "core_nodes": core_mesh.nodeCount(),
                        "material_assignment_verified": True, "maximum_relative_equation_residual": "unavailable from this adapter",
                        **primary_field_diagnostics(fop._core)}
                if voltage.shape != (4096,) or not np.all(np.isfinite(voltage)):
                    raise ValueError("P2 returned invalid voltage data")
                np.save(output / f"p2-{label}-{state}-voltage-v.npy", voltage, allow_pickle=False)
                reference = np.load(output / f"{state}-reference-v.npy", allow_pickle=False)
                check = normalized_discrepancy(voltage, reference, sigma)
                record["states"][state] = {"status": "completed", "check": check, "resources": resources.record(),
                    "native_diagnostics": diagnostics, "worst_manifest_index": int(np.argmax(np.abs((voltage - reference) / sigma)))}
                record["worker_wall_seconds"] = time.perf_counter() - started
                save_json(path, record)
                print(json.dumps({"mesh": label, "state": state, **check}), flush=True)
            record["status"] = "completed"
        record["resources"] = whole_worker.record()
    except Exception as error:
        record.update(status="failed", exception_type=type(error).__name__)
        raise
    finally:
        record["worker_wall_seconds"] = time.perf_counter() - started
        save_json(path, record)


def main():
    parser = argparse.ArgumentParser(description="Approved explicit P2 comparison on frozen contact cells")
    parser.add_argument("phase", choices=("prepare", "worker"))
    parser.add_argument("--mesh", choices=("A", "C"))
    parser.add_argument("--output", type=Path, default=Path("experiments/outputs/p2-contact"))
    args = parser.parse_args()
    if args.phase == "prepare":
        prepare(args.output)
    elif args.mesh is None:
        parser.error("worker requires --mesh")
    else:
        worker(args.output, args.mesh)


if __name__ == "__main__":
    main()
