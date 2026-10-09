import argparse
from hashlib import sha256
import json
from pathlib import Path

import numpy as np

from .contact import STATES, LIMIT_SECONDS, DEVELOPMENT_ALLOWANCE_SECONDS, contact_voltage, verify_reference
from .domain import CURRENT_A, electrodes, homogeneous_voltage, noise_sigma, normalized_discrepancy
from .p2_contact import BASELINE, expected_nodes, resource_plan
from .pilot import save_json, write_csv


def decisions(rows, ratios, extent, resource_ok):
    complete = all(any(row["mesh"] == label and row["state"] == state and row["status"] == "completed" for row in rows) for label in "AC" for state in STATES)
    diagnostic = "inconclusive: incomplete states" if resource_ok else "inconclusive: invalid run"
    if complete and resource_ok:
        diagnostic = "supported" if len(ratios) == 4 and all(row["rms_ratio"] <= .25 and row["maximum_ratio"] <= .25 for row in ratios) else "not supported"
    accuracy = (complete and resource_ok and all(row["passed"] for row in rows)
                and len(extent) == 3 and all(row["passed"] for row in extent))
    return diagnostic, "contact accuracy established for declared survey" if accuracy else "inconclusive"


def build_report(directory):
    checksums_path = directory / "raw-data-sha256.json"
    if checksums_path.exists():
        for name, expected in json.loads(checksums_path.read_text()).items():
            if Path(name).name != name or sha256((directory / name).read_bytes()).hexdigest() != expected:
                raise ValueError("Published P2 raw checksum differs")
    config = json.loads((directory / "configuration.json").read_text())
    if (config["current_a"], config["rms_threshold"], config["maximum_threshold"], config["worker_cap_seconds"], config["memory_cap_gib"], config["maximum_state_solves"], config["diagnostic_ratio_threshold"]) != (CURRENT_A, .1, .25, LIMIT_SECONDS, 8, 6, .25):
        raise ValueError("P2 study constants differ from approved scope")
    if config["states_ohm_m"] != {key: list(value) for key, value in STATES.items()} or config["mesh_labels"] != ["A", "C"]:
        raise ValueError("P2 physical states or mesh labels changed")
    baseline_checksums = json.loads((BASELINE / "raw-data-sha256.json").read_text())
    if config["baseline_raw_data_sha256"] != baseline_checksums:
        raise ValueError("Baseline provenance differs")
    payload = (directory / "candidate-manifest.csv").read_bytes()
    if payload != (BASELINE / "candidate-manifest.csv").read_bytes() or sha256(payload).hexdigest() != config["manifest_sha256"]:
        raise ValueError("P2 manifest changed")
    manifest = np.loadtxt(directory / "candidate-manifest.csv", delimiter=",", skiprows=1, dtype=int)
    locations = np.array(config["electrodes_m"])
    np.testing.assert_array_equal(locations, electrodes())
    verify_reference(locations, manifest)
    sigma = noise_sigma(homogeneous_voltage(locations, manifest), .01, 1e-6)
    np.testing.assert_array_equal(sigma, np.load(directory / "fixed-sigma-v.npy", allow_pickle=False))
    for state, (left, right) in STATES.items():
        np.testing.assert_array_equal(np.load(directory / f"{state}-reference-v.npy", allow_pickle=False), contact_voltage(locations, manifest, left, right))
    if set(path.name for path in directory.glob("p2-worker-*.json")) - {f"p2-worker-{label}.json" for label in "AC"}:
        raise ValueError("Unapproved P2 worker")
    rows, ratios, order_changes, voltages, records = [], [], [], {}, {}
    attempts = 0
    peak = 0
    for label in "AC":
        axes = [np.load(directory / f"{label}-{name}-axis-m.npy", allow_pickle=False) for name in "xyz"]
        for name, axis in zip("xyz", axes):
            np.testing.assert_array_equal(axis, np.load(BASELINE / f"{label}-{name}-axis-m.npy", allow_pickle=False))
        path = directory / f"p2-worker-{label}.json"
        record = json.loads(path.read_text()) if path.exists() else {"mesh": label, "status": "not attempted", "states": {}, "worker_wall_seconds": 0.}
        records[label] = record
        if record["mesh"] != label or set(record["states"]) - set(STATES):
            raise ValueError("Worker scope changed")
        peak = max(peak, record.get("resources", {}).get("peak_rss_bytes", 0), record.get("construction", {}).get("peak_rss_bytes", 0))
        if "geometry" in record:
            geometry = record["geometry"]
            if not geometry["passed"] or geometry["p2_nodes"] != expected_nodes(axes) or not geometry["boundary_convention_verified"]:
                raise ValueError("P2 geometry validation failed")
            centers = np.load(directory / f"{label}-cell-centers-m.npy", allow_pickle=False)
            mapping = np.load(directory / f"{label}-cell-correspondence.npy", allow_pickle=False)
            lengths = [len(axis) - 1 for axis in axes]
            cell_count = int(np.prod(lengths))
            if sorted(mapping.tolist()) != list(range(cell_count)) or centers.shape != (cell_count, 3):
                raise ValueError("Invalid material correspondence")
            expected_centers = np.array(np.meshgrid(*[(axis[:-1] + axis[1:]) / 2 for axis in axes], indexing="ij")).reshape(3, -1).T
            actual_order = np.lexsort(centers.T[::-1])
            expected_order = np.lexsort(expected_centers.T[::-1])
            np.testing.assert_array_equal(centers[actual_order], expected_centers[expected_order])
        for state, (left, right) in STATES.items():
            linear_path = directory / f"linear-{label}-{state}-voltage-v.npy"
            linear = np.load(linear_path, allow_pickle=False)
            if sha256(linear_path.read_bytes()).hexdigest() != baseline_checksums[f"{label}-{state}-voltage-v.npy"]:
                raise ValueError("Frozen linear baseline changed")
            reference = np.load(directory / f"{state}-reference-v.npy", allow_pickle=False)
            linear_check = normalized_discrepancy(linear, reference, sigma)
            entry = record["states"].get(state, {"status": "not attempted"})
            if entry["status"] in ("attempted", "completed"):
                attempts += 1
            if entry["status"] != "completed":
                rows.append({"mesh": label, "state": state, "status": entry["status"], "rms": "", "maximum": "", "passed": False})
                continue
            if not record.get("geometry", {}).get("passed") or not entry["native_diagnostics"]["material_assignment_verified"]:
                raise ValueError("Completed state lacks geometry/material validation")
            if state != "H" and not record["states"]["H"]["check"]["passed"]:
                raise ValueError("P2 homogeneous gate was bypassed")
            resistivity = np.load(directory / f"{label}-{state}-resistivity-ohm-m.npy", allow_pickle=False)
            np.testing.assert_array_equal(resistivity, np.where(centers[:, 0] < 0, left, right))
            voltage = np.load(directory / f"p2-{label}-{state}-voltage-v.npy", allow_pickle=False)
            if voltage.shape != (4096,) or not np.all(np.isfinite(voltage)):
                raise ValueError("Invalid P2 voltage array")
            check = normalized_discrepancy(voltage, reference, sigma)
            for key in ("rms", "maximum", "passed"):
                if not np.isclose(check[key], entry["check"][key], rtol=1e-12, atol=1e-12):
                    raise ValueError("P2 metric differs from raw data")
            voltages[label, state] = voltage
            peak = max(peak, entry["resources"]["peak_rss_bytes"])
            rows.append({"mesh": label, "state": state, "status": "completed", **check})
            order_changes.append({"mesh": label, "state": state, **normalized_discrepancy(voltage, linear, sigma)})
            if state != "H":
                ratios.append({"mesh": label, "state": state, "linear_rms": linear_check["rms"], "p2_rms": check["rms"],
                    "rms_ratio": check["rms"] / linear_check["rms"], "linear_maximum": linear_check["maximum"],
                    "p2_maximum": check["maximum"], "maximum_ratio": check["maximum"] / linear_check["maximum"]})
            np.save(directory / f"p2-{label}-{state}-normalized-residual.npy", (voltage - reference) / sigma, allow_pickle=False)
    if attempts > 6:
        raise ValueError("P2 solve cap exceeded")
    extent = [{"state": state, **normalized_discrepancy(voltages["A", state], voltages["C", state], sigma)}
              for state in STATES if ("A", state) in voltages and ("C", state) in voltages]
    preparation = json.loads((directory / "preparation.json").read_text())["wall_seconds"]
    seconds = DEVELOPMENT_ALLOWANCE_SECONDS + preparation + sum(record["worker_wall_seconds"] for record in records.values())
    stop_path = directory / "resource-limit.json"
    if stop_path.exists():
        peak = max(peak, json.loads(stop_path.read_text())["peak_rss_bytes"])
    resource_ok = not stop_path.exists() and seconds <= LIMIT_SECONDS and peak <= 8 * 2**30
    if "resource_plan" in records["C"]:
        a = records["A"]
        expected = resource_plan(a["resources"]["peak_rss_bytes"], a["worker_wall_seconds"], a["geometry"]["p2_nodes"],
                                 expected_nodes([np.load(directory / f"C-{name}-axis-m.npy", allow_pickle=False) for name in "xyz"]),
                                 LIMIT_SECONDS - DEVELOPMENT_ALLOWANCE_SECONDS - preparation - a["worker_wall_seconds"])
        for key in ("factor", "projected_peak_bytes", "projected_worker_seconds", "remaining_seconds", "allowed"):
            if not np.isclose(expected[key], records["C"]["resource_plan"][key], rtol=1e-12, atol=1e-9):
                raise ValueError("Resource projection differs from recorded evidence")
        if not expected["allowed"] and any(entry["status"] in ("attempted", "completed") for entry in records["C"]["states"].values()):
            raise ValueError("C-P2 bypassed its resource planning gate")
    valid_workers = all(record["status"] == "completed" for record in records.values())
    diagnostic, accuracy = decisions(rows, ratios, extent, resource_ok and valid_workers)
    summary = {"diagnostic_hypothesis": diagnostic, "contact_accuracy": accuracy, "native_state_solve_attempts": attempts,
               "completed_states": len(voltages), "accounted_worker_seconds": seconds, "peak_rss_gib": peak / 2**30,
               "resource_ok": resource_ok, "valid_workers": valid_workers, "development_allowance_seconds": DEVELOPMENT_ALLOWANCE_SECONDS,
               "states": rows, "error_ratios": ratios, "order_changes": order_changes, "extent_changes": extent,
               "worker_statuses": {label: record["status"] for label, record in records.items()}, "sphere_accuracy": "unverified"}
    save_json(directory / "summary.json", summary)
    write_csv(directory / "state-errors.csv", rows)
    if ratios:
        write_csv(directory / "error-ratios.csv", ratios)
    if order_changes:
        write_csv(directory / "order-comparisons.csv", order_changes)
    if extent:
        write_csv(directory / "extent-comparisons.csv", extent)
    lines = ["# Recomputed P2 evidence", "", f"Diagnostic hypothesis: **{diagnostic}**. Contact accuracy: **{accuracy}**.", "",
             "| Mesh | State | Status | RMS | Maximum | Pass |", "| --- | --- | --- | ---: | ---: | --- |"]
    for row in rows:
        lines.append(f"| {row['mesh']} | {row['state']} | {row['status']} | {row['rms']} | {row['maximum']} | {row['passed']} |")
    lines += ["", "| Mesh | State | P2/linear RMS | P2/linear maximum |", "| --- | --- | ---: | ---: |"]
    for row in ratios:
        lines.append(f"| {row['mesh']} | {row['state']} | {row['rms_ratio']:.8g} | {row['maximum_ratio']:.8g} |")
    lines += ["", f"Attempted state solves: {attempts}. Accounted time: {seconds:.3f} s, including the 600 s allowance. Peak process memory: {peak / 2**30:.3f} GiB.", "",
              "Resource skips remain missing observations; they are not interpreted as favorable numerical results.", ""]
    (directory / "TABLES.md").write_text("\n".join(lines), encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser(description="Recompute approved P2 comparison from raw evidence")
    parser.add_argument("directory", type=Path)
    summary = build_report(parser.parse_args().directory)
    print(json.dumps({key: summary[key] for key in ("diagnostic_hypothesis", "contact_accuracy", "native_state_solve_attempts", "accounted_worker_seconds", "peak_rss_gib")}))


if __name__ == "__main__":
    main()
