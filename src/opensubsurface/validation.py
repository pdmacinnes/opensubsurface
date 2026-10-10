import argparse
from dataclasses import asdict
from hashlib import sha256
import json
import os
from pathlib import Path
import time

import numpy as np

from .domain import homogeneous_voltage, noise_sigma, normalized_discrepancy, primary_catalog
from .pilot import save_json, write_csv
from .solvers import MeshSettings, SimpegForward, PygimliForward, PygimliConformingForward, ResourceSample


RECORD = Path("experiments/ert-observability-pilot/results/2026-10-08")
RETRY_RESERVE_SECONDS = 600.


def start_budget(output):
    output.mkdir(parents=True, exist_ok=True)
    if (output / "resource-limit.json").exists():
        raise RuntimeError("A resource-limit stop is already recorded; do not continue this study")
    records = [json.loads(path.read_text()) for path in output.glob("*.json")
               if path.name not in ("budget.json", "prior-residual-correlations.json", "resource-limit.json")]
    spent = RETRY_RESERVE_SECONDS + sum(record.get("worker_wall_seconds", record.get("resources", {}).get("wall_seconds", 0.)
                        + record.get("construction", {}).get("wall_seconds", 0.)) for record in records)
    remaining = 14400 - spent
    if remaining <= 0:
        raise RuntimeError("The approved four-hour compute budget is exhausted")
    os.environ["OPENSUBSURFACE_OUTPUT"] = str(output)
    os.environ["OPENSUBSURFACE_DEADLINE"] = str(time.time() + remaining)
    save_json(output / "budget.json", {"limit_seconds": 14400, "completed_compute_seconds": spent,
              "remaining_seconds": remaining, "development_retry_reserve_seconds": RETRY_RESERVE_SECONDS,
              "accounting": "sum of recorded worker wall times; overlapping probes count twice; ten-minute allowance for uninstrumented development, smoke checks, and early failed meshing attempts"})


def frozen_inputs():
    config = json.loads((RECORD / "configuration.json").read_text())
    content = (RECORD / "candidate-manifest.csv").read_bytes()
    if sha256(content).hexdigest() != config["manifest_sha256"]:
        raise ValueError("Original manifest hash changed")
    manifest = np.loadtxt(RECORD / "candidate-manifest.csv", delimiter=",", skiprows=1, dtype=int)
    return config, manifest


def census(output):
    output.mkdir(parents=True, exist_ok=True)
    config, manifest = frozen_inputs()
    locations = np.array(config["electrodes_m"])
    analytic = homogeneous_voltage(locations, manifest)
    sigma = noise_sigma(analytic, .01, 1e-6)
    files = sorted(RECORD.glob("simpeg-homogeneous-*.npy"))
    residuals = [(np.load(path, allow_pickle=False) - analytic) / sigma for path in files]
    rows = []
    residual = residuals[files.index(RECORD / "simpeg-homogeneous-h0.25-e128-s0.125-amg.npy")]
    for role, column in zip(("a", "b", "m", "n"), manifest.T):
        for index in range(64):
            selected = residual[column == index]
            rows.append({"role": role, "electrode": index, "count": len(selected),
                         "normalized_rms": float(np.sqrt(np.mean(selected ** 2))) if len(selected) else ""})
    write_csv(output / "electrode-role-census.csv", rows)
    save_json(output / "prior-residual-correlations.json", {"files": [path.name for path in files],
              "correlations": np.corrcoef(residuals).tolist(),
              "premise_under_test": "Local refinement alone controls the homogeneous response error",
              "warning": "Role counts differ under canonicalization; sparse role samples do not establish electrode causality"})


def worker(output, label, settings, solver="simpeg"):
    output.mkdir(parents=True, exist_ok=True)
    if (output / f"{label}.json").exists():
        raise ValueError("A recorded worker label cannot be overwritten")
    os.environ["OPENSUBSURFACE_OUTPUT"] = str(output)
    start_budget(output)
    started = time.perf_counter()
    config, manifest = frozen_inputs()
    analytic = homogeneous_voltage(np.array(config["electrodes_m"]), manifest)
    sigma = noise_sigma(analytic, .01, 1e-6)
    constructor = SimpegForward if solver == "simpeg" else PygimliForward
    with ResourceSample() as construction:
        forward = constructor(settings, manifest)
    voltage, resources = forward.solve()
    np.save(output / f"{label}-voltages-v.npy", voltage, allow_pickle=False)
    audits = forward.audit() if solver == "simpeg" else {"singularity_removal": True}
    if solver == "simpeg" and label == "baseline-tree":
        audits["direct_dipole_check"] = forward.audit_dipoles()
    record = {"label": label, "solver": solver, "settings": asdict(settings),
              "manifest_sha256": config["manifest_sha256"], "resources": resources,
              "construction": construction.record(),
              "homogeneous_check": normalized_discrepancy(voltage, analytic, sigma),
              "audit": audits, "worker_wall_seconds": time.perf_counter() - started,
              "scope": "homogeneous validation only", "recorded_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    save_json(output / f"{label}.json", record)
    print(json.dumps(record), flush=True)
    return record


def inclusion_checks(output, label, settings, solver):
    if (output / f"{label}.json").exists():
        raise ValueError("A recorded worker label cannot be overwritten")
    start_budget(output)
    started = time.perf_counter()
    config, manifest = frozen_inputs()
    analytic = homogeneous_voltage(np.array(config["electrodes_m"]), manifest)
    sigma = noise_sigma(analytic, .01, 1e-6)
    constructor = SimpegForward if solver == "simpeg" else PygimliForward
    with ResourceSample():
        forward = constructor(settings, manifest)
    homogeneous, resources = forward.solve()
    check = normalized_discrepancy(homogeneous, analytic, sigma)
    record = {"label": label, "solver": solver, "settings": asdict(settings), "homogeneous_check": check,
              "scope": "at most four existing representative inclusions; no classification or nuisance bank", "models": {}}
    if check["passed"]:
        models, _ = primary_catalog()
        selectors = [("H1", 3., 10.), ("H1", 7., 100.), ("H2", 3., 100.), ("H2", 7., 10.)]
        selected = [next(model for model in models.values() if (model.kind, model.depth, model.contrast) == selector) for selector in selectors]
        record["representative_ids"] = [model.identifier for model in selected]
        for model in selected:
            voltage, resources = forward.solve(model)
            np.save(output / f"{label}-{model.identifier}-voltages-v.npy", voltage, allow_pickle=False)
            record["models"][model.identifier] = {"geometry": asdict(model), "resources": resources,
                                                   "maximum_anomaly_v": float(np.max(np.abs(voltage - homogeneous)))}
            record["worker_wall_seconds"] = time.perf_counter() - started
            save_json(output / f"{label}.json", record)
            print(json.dumps({"completed_inclusions": len(record["models"]), "total_unique_inclusions": 4}), flush=True)
    record["worker_wall_seconds"] = time.perf_counter() - started
    save_json(output / f"{label}.json", record)
    print(json.dumps(record), flush=True)
    return record


def conforming_checks(output, label, settings, segments, rings, target_volume):
    if (output / f"{label}.json").exists():
        raise ValueError("A recorded worker label cannot be overwritten")
    start_budget(output)
    started = time.perf_counter()
    config, manifest = frozen_inputs()
    analytic = homogeneous_voltage(np.array(config["electrodes_m"]), manifest)
    sigma = noise_sigma(analytic, .01, 1e-6)
    models, _ = primary_catalog()
    selectors = [("H1", 3., 10.), ("H1", 7., 100.), ("H2", 3., 100.), ("H2", 7., 10.)]
    selected = [next(model for model in models.values() if (model.kind, model.depth, model.contrast) == selector) for selector in selectors]
    record = {"label": label, "solver": "pygimli", "settings": asdict(settings), "segments": segments,
              "rings": rings, "target_volume": target_volume, "scope": "same four representative geometries; fitted-mesh validation", "models": {}}
    for model in selected:
        with ResourceSample() as construction:
            forward = PygimliConformingForward(settings, manifest, model, segments, rings, target_volume)
        homogeneous, _ = forward.solve()
        np.save(output / f"{label}-{model.identifier}-homogeneous-v.npy", homogeneous, allow_pickle=False)
        check = normalized_discrepancy(homogeneous, analytic, sigma)
        if not check["passed"]:
            record["models"][model.identifier] = {"homogeneous_check": check, "status": "inclusion skipped"}
        else:
            voltage, resources = forward.solve(model)
            np.save(output / f"{label}-{model.identifier}-voltages-v.npy", voltage, allow_pickle=False)
            record["models"][model.identifier] = {"geometry": asdict(model), "resources": resources,
                   "construction": construction.record(), "homogeneous_check": check,
                   "maximum_anomaly_v": float(np.max(np.abs(voltage - homogeneous)))}
            forward.mesh.save(str(output / f"{label}-{model.identifier}.bms"))
        record["worker_wall_seconds"] = time.perf_counter() - started
        save_json(output / f"{label}.json", record)
        print(json.dumps({"completed_inclusions": len(record["models"]), "total_unique_inclusions": 4}), flush=True)
    return record


def replay_homogeneous(output):
    import pygimli as pg
    start_budget(output)
    started = time.perf_counter()
    config, manifest = frozen_inputs()
    analytic = homogeneous_voltage(np.array(config["electrodes_m"]), manifest)
    sigma = noise_sigma(analytic, .01, 1e-6)
    record = {"scope": "homogeneous replay of saved fitted meshes", "checks": {}, "peak_rss_bytes": 0}
    for path in sorted(output.glob("*.bms")):
        target = output / f"{path.stem}-homogeneous-v.npy"
        if target.exists():
            continue
        label = path.stem.rsplit("-h", 1)[0]
        settings = MeshSettings(**json.loads((output / f"{label}.json").read_text())["settings"])
        with ResourceSample() as construction:
            forward = PygimliForward.__new__(PygimliForward)
            forward.attach_mesh(pg.Mesh(str(path)), settings, manifest)
        voltage, resources = forward.solve()
        np.save(target, voltage, allow_pickle=False)
        record["checks"][path.stem] = normalized_discrepancy(voltage, analytic, sigma)
        record["peak_rss_bytes"] = max(record["peak_rss_bytes"], resources["peak_rss_bytes"], construction.peak_rss_bytes)
        record["worker_wall_seconds"] = time.perf_counter() - started
        save_json(output / "homogeneous-replay.json", record)
    return record


def main():
    parser = argparse.ArgumentParser(description="Approved numerical-only ERT validation")
    parser.add_argument("phase", choices=("census", "worker", "inclusions", "conforming", "replay-homogeneous"))
    parser.add_argument("--output", type=Path, default=Path("experiments/outputs/ert-numerical-validation"))
    parser.add_argument("--label", default="baseline")
    parser.add_argument("--mesh-type", choices=("tree", "tensor"), default="tree")
    parser.add_argument("--solver", choices=("simpeg", "pygimli"), default="simpeg")
    parser.add_argument("--cell-size", type=float, default=.5)
    parser.add_argument("--extent", type=float, default=64.)
    parser.add_argument("--grading", type=float, default=1.5)
    parser.add_argument("--intermediate-cell-size", type=float)
    parser.add_argument("--central-extent", type=float, default=12.)
    parser.add_argument("--source-batch-size", type=int, default=64)
    parser.add_argument("--source-ball-cell-size", type=float)
    parser.add_argument("--source-ball-radius-ratio", type=float, default=8.)
    parser.add_argument("--fem-core-extent", type=float, default=12.)
    parser.add_argument("--segments", type=int, default=24)
    parser.add_argument("--rings", type=int, default=12)
    parser.add_argument("--target-volume", type=float, default=.05)
    args = parser.parse_args()
    if args.phase == "replay-homogeneous":
        replay_homogeneous(args.output)
        return
    if args.phase == "census":
        census(args.output)
        return
    settings = MeshSettings(args.cell_size, args.extent, linear_solver="amg", mesh_type=args.mesh_type,
                            grading=args.grading, intermediate_cell_size=args.intermediate_cell_size,
                            central_extent=args.central_extent, source_batch_size=args.source_batch_size,
                            source_ball_cell_size=args.source_ball_cell_size,
                            source_ball_radius_ratio=args.source_ball_radius_ratio,
                            fem_core_extent=args.fem_core_extent)
    if args.phase == "conforming":
        conforming_checks(args.output, args.label, settings, args.segments, args.rings, args.target_volume)
    elif args.phase == "inclusions":
        inclusion_checks(args.output, args.label, settings, args.solver)
    else:
        worker(args.output, args.label, settings, args.solver)


if __name__ == "__main__":
    main()
