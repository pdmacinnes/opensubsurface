import argparse
from dataclasses import asdict, replace
from hashlib import sha256
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
from time import perf_counter
import csv

import numpy as np

from .domain import (
    CURRENT_A, NOISE_SCENARIOS, SEED, candidate_manifest, electrodes,
    homogeneous_voltage, manifest_bytes, noise_sigma, normalized_discrepancy,
    primary_catalog, discrimination, nuisance_bank,
)
from .solvers import MeshSettings, PygimliForward, SimpegForward, ResourceSample


def save_json(path, record):
    path.write_text(json.dumps(record, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def setup_record(output):
    output.mkdir(parents=True, exist_ok=True)
    manifest = candidate_manifest()
    payload = manifest_bytes(manifest)
    path = output / "candidate-manifest.csv"
    if path.exists() and path.read_bytes() != payload:
        raise ValueError("Existing candidate manifest does not match the frozen configuration")
    path.write_bytes(payload)
    models, pairs = primary_catalog()
    save_json(output / "configuration.json", {
        "seed": SEED, "generator": "numpy.random.PCG64", "current_a": CURRENT_A,
        "electrodes_m": electrodes().tolist(), "manifest_sha256": sha256(payload).hexdigest(),
        "candidate_count": len(manifest), "hypothetical_sequential_commands": len(manifest),
        "unique_current_pairs": len({tuple(row[:2]) for row in manifest}),
        "models": {key: asdict(value) for key, value in models.items()}, "pairs": pairs,
        "noise_scenarios": [{"relative_error": eta, "floor_v": floor} for eta, floor in NOISE_SCENARIOS],
    })
    save_json(output / "environment.json", {
        "python": platform.python_version(), "platform": platform.system(), "machine": platform.machine(),
        "gpu_used": False, "versions": {name: version(name) for name in (
            "numpy", "scipy", "simpeg", "discretize", "pymatsolver", "pygimli", "pgcore", "psutil", "matplotlib")},
        "thread_limits": {name: os.environ.get(name) for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")},
        "pygimli_runtime_version": __import__("pygimli").__version__,
        "source_sha256": {name: sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                          for name in ("domain.py", "solvers.py", "pilot.py")},
    })
    np.save(output / "electrodes-m.npy", electrodes(), allow_pickle=False)
    np.save(output / "currents-a.npy", np.full(len(manifest), CURRENT_A), allow_pickle=False)
    return manifest, models


def profile(output, solver_name, settings):
    manifest, models = setup_record(output)
    start = perf_counter()
    constructor = SimpegForward if solver_name == "simpeg" else PygimliForward
    with ResourceSample():
        forward = constructor(settings, manifest)
    construction_seconds = perf_counter() - start
    analytic = homogeneous_voltage(electrodes(), manifest)
    sigma = noise_sigma(analytic, 0.01, 1e-6)
    voltages = {}
    records = {}
    selected = [None, next(model for model in models.values() if model.kind == "H1" and model.depth == 3 and model.contrast == 10),
                next(model for model in models.values() if model.kind == "H2" and model.depth == 7 and model.contrast == 100)]
    suffix = f"h{settings.cell_size:g}-e{settings.extent:g}-s{settings.electrode_cell_size or settings.cell_size:g}-{settings.linear_solver}"
    for model in selected:
        key = "homogeneous" if model is None else model.identifier
        voltage, record = forward.solve(model)
        voltages[key] = voltage
        records[key] = record
        np.save(output / f"{solver_name}-{key}-{suffix}.npy", voltage, allow_pickle=False)
        print(json.dumps({"model": key, **record}), flush=True)
    twin, twin_record = forward.solve(replace(selected[1]))
    twin_check = normalized_discrepancy(twin, voltages[selected[1].identifier], sigma)
    np.save(output / f"{solver_name}-material-twin-{suffix}.npy", twin, allow_pickle=False)
    error = normalized_discrepancy(voltages["homogeneous"], analytic, sigma)
    average = np.mean([record["wall_seconds"] for key, record in records.items() if key != "homogeneous"])
    # Uniform background-resistivity scaling reduces 810 bank states to 270 solves.
    projected_seconds = float(construction_seconds + average * 270)
    cap_passed = bool(projected_seconds <= 12 * 3600 and max(record["peak_rss_bytes"] for record in records.values()) <= 8 * 1024 ** 3)
    result = {"phase": "profile", "solver": solver_name, "mesh": asdict(settings), "records": records,
              "construction_seconds": construction_seconds, "homogeneous_check": error,
              "projected_full_bank_seconds": projected_seconds, "projection_basis": "mean of two inclusion solves times 270 distinct normalized-background models; excludes additional verification and plotting",
              "projection_run_count": 2, "resource_cap_passed": cap_passed,
              "material_twin_check": twin_check, "material_twin_resources": twin_record,
              "decision": "continue numerical verification" if cap_passed else "stop: resource-cap amendment required",
              "scientific_status": "not yet verified; no discrimination claim"}
    save_json(output / f"profile-{solver_name}-{suffix}.json", result)
    print(json.dumps({"homogeneous_check": error, "projected_full_bank_seconds": projected_seconds, "resource_cap_passed": cap_passed}), flush=True)
    return result


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def verify(output, settings):
    manifest, models = setup_record(output)
    reference = homogeneous_voltage(electrodes(), manifest)
    sigma = noise_sigma(reference, 0.01, 1e-6)
    constructors = {"simpeg": SimpegForward, "pygimli": PygimliForward}
    selected = [
        next(model for model in models.values() if model.kind == "H1" and model.depth == 3 and model.contrast == 10),
        next(model for model in models.values() if model.kind == "H1" and model.depth == 7 and model.contrast == 100),
        next(model for model in models.values() if model.kind == "H2" and model.depth == 3 and model.contrast == 100),
        next(model for model in models.values() if model.kind == "H2" and model.depth == 7 and model.contrast == 10),
    ]
    checks = []
    responses = {}
    for solver, constructor in constructors.items():
        configurations = {
            "base": settings,
            "refined": replace(settings, cell_size=settings.cell_size / 2,
                               electrode_cell_size=None if settings.electrode_cell_size is None else settings.electrode_cell_size / 2),
            "padded": replace(settings, extent=settings.extent * 2),
        }
        for mesh_name, mesh_settings in configurations.items():
            with ResourceSample():
                forward = constructor(mesh_settings, manifest)
            homogeneous, record = forward.solve()
            np.save(output / f"verify-{solver}-{mesh_name}-homogeneous.npy", homogeneous, allow_pickle=False)
            check = {"solver": solver, "mesh": mesh_name, "model": "homogeneous", "comparison": "analytic half-space",
                     **normalized_discrepancy(homogeneous, reference, sigma), "resources": record}
            checks.append(check)
            save_json(output / "verification.json", {"passed": False, "complete": False, "checks": checks})
            if not check["passed"]:
                result = {"passed": False, "complete": False, "checks": checks,
                          "stop_reason": "homogeneous accuracy gate", "scientific_status": "inconclusive"}
                save_json(output / "verification.json", result)
                return result
            for model in selected:
                voltage, record = forward.solve(model)
                key = (solver, mesh_name, model.identifier)
                responses[key] = voltage
                np.save(output / f"verify-{solver}-{mesh_name}-{model.identifier}.npy", voltage, allow_pickle=False)
                if mesh_name != "base":
                    checks.append({"solver": solver, "mesh": mesh_name, "model": model.identifier,
                                   "comparison": "base mesh", "resources": record,
                                   **normalized_discrepancy(voltage, responses[(solver, "base", model.identifier)], sigma)})
            del forward
    for model in selected:
        checks.append({"solver": "independent comparison", "mesh": "base", "model": model.identifier,
                       "comparison": "SimPEG versus pyGIMLi",
                       **normalized_discrepancy(responses[("simpeg", "base", model.identifier)],
                                                responses[("pygimli", "base", model.identifier)], sigma)})
    result = {"passed": all(check["passed"] for check in checks), "complete": True, "checks": checks}
    save_json(output / "verification.json", result)
    return result


def skipped_diagnostics(output, reason):
    _, pairs = primary_catalog()
    rows = [{**pair, "relative_error": eta, "floor_v": floor, "status": reason,
             "distance": "", "optimal_error": "", "verified": False}
            for pair in pairs for eta, floor in NOISE_SCENARIOS]
    write_csv(output / "pair-diagnostics.csv", rows)
    save_json(output / "bank-status.json", {"status": "not run", "reason": reason,
              "intended_material_states": 810, "intended_distinct_normalized_models": 270})


def summarize(output, status, reason, profile_result, verification=None):
    save_json(output / "run-status.json", {"scientific_status": status, "stop_reason": reason,
              "catalog_complete": False, "verification_complete": bool(verification and verification.get("complete")),
              "verification_passed": bool(verification and verification["passed"]), "profile": profile_result})
    report = ["# ERT observability pilot run", "", f"Scientific status: **{status}**.", "", reason, "",
              "The approved accuracy thresholds are RMS <= 0.1 and maximum <= 0.25 after normalization by the 1% relative-error and 1 microvolt noise scenario.", ""]
    if profile_result:
        check = profile_result["homogeneous_check"]
        report += [f"The primary homogeneous comparison has normalized RMS {check['rms']:.6g} and maximum {check['maximum']:.6g}.", "",
                   f"The resource projection is {profile_result['projected_full_bank_seconds'] / 3600:.3g} hours, based on two inclusion solves. It excludes additional verification and plotting and is not a measured full-study runtime.", ""]
    report += ["No adaptive acquisition, hardware validation, or field mapping result is established.", "",
               "Missing geometry diagnostics are recorded explicitly. A failed numerical gate is not evidence that the geometries are physically indistinguishable.", ""]
    (output / "REPORT.md").write_text("\n".join(report), encoding="utf-8")


def run_catalog(output, settings):
    manifest, primary = setup_record(output)
    profile_result = profile(output, "simpeg", settings)
    if not profile_result["resource_cap_passed"]:
        reason = "Projected compute or observed memory exceeds the approved resource cap. A scope amendment is required."
        skipped_diagnostics(output, "not computed: resource cap")
        summarize(output, "inconclusive", reason, profile_result)
        return False
    if not profile_result["homogeneous_check"]["passed"]:
        verification = {"passed": False, "complete": False, "checks": [{"solver": "simpeg", "comparison": "analytic half-space",
                        **profile_result["homogeneous_check"]}], "stop_reason": "homogeneous accuracy gate"}
        save_json(output / "verification.json", verification)
    else:
        verification = verify(output, settings)
    if not verification["passed"]:
        reason = "Numerical verification failed. The full geometry catalog and nuisance bank were not run."
        skipped_diagnostics(output, "not computed: numerical gate")
        summarize(output, "inconclusive", reason, profile_result, verification)
        return False
    with ResourceSample():
        forward = SimpegForward(settings, manifest)
    _, pairs = primary_catalog()
    bank = {variant.identifier: variant for model in primary.values() for variant in nuisance_bank(model)}
    normalized = {replace(model, background=100.).identifier: replace(model, background=100.) for model in bank.values()}
    predictions = {}
    records = {}
    started = perf_counter()
    raw = output / "raw"
    raw.mkdir(exist_ok=True)
    for number, (key, model) in enumerate(normalized.items(), 1):
        if perf_counter() - started > 12 * 3600:
            skipped_diagnostics(output, "not computed: elapsed resource cap")
            summarize(output, "inconclusive", "Catalog stopped at the elapsed compute cap.", profile_result, verification)
            save_json(output / "model-resources.json", records)
            return False
        predictions[key], records[key] = forward.solve(model)
        np.save(raw / f"{key}.npy", predictions[key], allow_pickle=False)
        save_json(output / "model-resources.json", records)
        print(json.dumps({"completed_models": number, "total_models": len(normalized)}), flush=True)
    for key, model in bank.items():
        base = replace(model, background=100.).identifier
        predictions[key] = predictions[base] * model.background / 100.
        np.save(raw / f"{key}.npy", predictions[key], allow_pickle=False)
    reference = homogeneous_voltage(electrodes(), manifest)
    rows, countermodels = [], []
    for pair in pairs:
        first, second = predictions[pair["h1"]], predictions[pair["h2"]]
        for eta, floor in NOISE_SCENARIOS:
            sigma = noise_sigma(reference, eta, floor)
            distance, error, contributions = discrimination(first, second, sigma)
            rows.append({**pair, "relative_error": eta, "floor_v": floor, "status": "computed",
                         "distance": distance, "optimal_error": error, "verified": True})
            np.save(raw / f"contributions-{pair['h2']}-{eta}-{floor}.npy", contributions, allow_pickle=False)
            for truth, opposite in ((pair["h1"], pair["h2"]), (pair["h2"], pair["h1"])):
                candidates = nuisance_bank(primary[opposite])
                distances = [discrimination(predictions[truth], predictions[model.identifier], sigma)[0] for model in candidates]
                closest = int(np.argmin(distances))
                countermodels.append({"truth": truth, "opposite": opposite, "relative_error": eta, "floor_v": floor,
                                      "closest_model": candidates[closest].identifier, "distance": distances[closest],
                                      "interpretation": "finite-bank diagnostic, not marginalized inference accuracy"})
    write_csv(output / "pair-diagnostics.csv", rows)
    write_csv(output / "countermodels.csv", countermodels)
    save_json(output / "bank-status.json", {"status": "computed", "states": len(bank), "forward_solves": len(normalized)})
    save_json(output / "run-status.json", {"scientific_status": "verified restricted-model diagnostics", "catalog_complete": True,
              "verification_complete": True, "verification_passed": True, "seconds": perf_counter() - started,
              "informative_pairs": {f"eta={eta},floor={floor}": sum(row["optimal_error"] <= 0.1 for row in rows
                    if row["relative_error"] == eta and row["floor_v"] == floor) for eta, floor in NOISE_SCENARIOS}})
    (output / "REPORT.md").write_text("# ERT observability pilot\n\nThe numerical checks passed for the specified configurations. All 24 paired models and six noise scenarios were evaluated.\n\nThese are optimistic known-model Gaussian diagnostics. Countermodels cover a finite nuisance bank and are not marginalized inference accuracy. No adaptive efficiency or hardware claim follows.\n\nRead pair-diagnostics.csv, countermodels.csv, verification.json, and run-status.json for the actual values and decision.\n", encoding="utf-8")
    return True


def main():
    parser = argparse.ArgumentParser(description="Run the approved ERT observability pilot")
    parser.add_argument("phase", choices=["profile", "verify", "run", "record-stop"])
    parser.add_argument("--profile-record", type=Path, help="Completed profile JSON for a stop record; no new simulation")
    parser.add_argument("--solver", choices=["simpeg", "pygimli"], default="simpeg")
    parser.add_argument("--cell-size", type=float, default=0.5)
    parser.add_argument("--extent", type=float, default=128.)
    parser.add_argument("--electrode-cell-size", type=float)
    parser.add_argument("--linear-solver", choices=["lu", "amg"], default="lu")
    parser.add_argument("--output", type=Path, default=Path("experiments/outputs/ert-observability-pilot"))
    args = parser.parse_args()
    if args.cell_size <= 0 or args.extent < 16:
        parser.error("Positive cell size and at least 16 m padding extent are required")
    if args.electrode_cell_size is not None and args.electrode_cell_size <= 0:
        parser.error("Electrode cell size must be positive")
    os.environ["OPENSUBSURFACE_OUTPUT"] = str(args.output)
    try:
        if args.phase == "record-stop":
            if args.profile_record is None:
                parser.error("record-stop requires --profile-record")
            result = json.loads(args.profile_record.read_text(encoding="utf-8"))
            if result["resource_cap_passed"] and result["homogeneous_check"]["passed"]:
                parser.error("A passing profile is not a stop condition")
            args.output.mkdir(parents=True, exist_ok=True)
            reasons = []
            if not result["homogeneous_check"]["passed"]:
                reasons.append("Numerical verification failed.")
            if not result["resource_cap_passed"]:
                reasons.append("The profiled configuration exceeds the projected compute or observed memory cap.")
            reason = " ".join(reasons)
            skipped_diagnostics(args.output, "not computed: failed profile gate")
            summarize(args.output, "inconclusive", reason, result)
            raise SystemExit(2)
        settings = MeshSettings(args.cell_size, args.extent, args.electrode_cell_size, args.linear_solver)
        if args.phase == "run":
            raise SystemExit(0 if run_catalog(args.output, settings) else 2)
        if args.phase == "verify":
            raise SystemExit(0 if verify(args.output, settings)["passed"] else 2)
        result = profile(args.output, args.solver, settings)
    except Exception as error:
        args.output.mkdir(parents=True, exist_ok=True)
        save_json(args.output / "failure.json", {"phase": args.phase, "solver": args.solver,
                  "exception_type": type(error).__name__, "message": str(error), "scientific_status": "inconclusive"})
        raise
    if not result["resource_cap_passed"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
