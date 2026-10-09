import argparse
from hashlib import sha256
import json
from pathlib import Path

import numpy as np

from .contact import STATES, LIMIT_SECONDS, DEVELOPMENT_ALLOWANCE_SECONDS, contact_voltage, mesh_axes, verify_axes, verify_reference
from .domain import CURRENT_A, electrodes, homogeneous_voltage, noise_sigma, normalized_discrepancy
from .pilot import save_json, write_csv


def build_report(directory):
    if (directory / "raw-data-sha256.json").exists():
        checksums = json.loads((directory / "raw-data-sha256.json").read_text())
        for name, expected in checksums.items():
            if Path(name).name != name or sha256((directory / name).read_bytes()).hexdigest() != expected:
                raise ValueError("Raw artifact checksum differs from published record")
    config = json.loads((directory / "configuration.json").read_text())
    if (config["rms_threshold"], config["maximum_threshold"], config["worker_cap_seconds"], config["memory_cap_gib"]) != (.1, .25, LIMIT_SECONDS, 8):
        raise ValueError("Declared thresholds or caps differ from the approved scope")
    if set(path.name for path in directory.glob("worker-*.json")) - {f"worker-{label}.json" for label in "ABCD"}:
        raise ValueError("Worker labels exceed the approved scope")
    payload = (directory / "candidate-manifest.csv").read_bytes()
    if sha256(payload).hexdigest() != config["manifest_sha256"]:
        raise ValueError("Manifest checksum changed")
    # The declared hash is checked against the original published record as well.
    from .validation import frozen_inputs
    original, original_manifest = frozen_inputs()
    if config["manifest_sha256"] != original["manifest_sha256"]:
        raise ValueError("This is not the approved manifest")
    manifest = np.loadtxt(directory / "candidate-manifest.csv", delimiter=",", skiprows=1, dtype=int)
    np.testing.assert_array_equal(manifest, original_manifest)
    locations = np.array(config["electrodes_m"])
    np.testing.assert_array_equal(locations, electrodes())
    if config["current_a"] != CURRENT_A or config["states_ohm_m"] != {key: list(value) for key, value in STATES.items()}:
        raise ValueError("Declared current or material states changed")
    sigma = noise_sigma(homogeneous_voltage(locations, manifest), .01, 1e-6)
    np.testing.assert_array_equal(sigma, np.load(directory / "fixed-sigma-v.npy", allow_pickle=False))
    reference_checks = verify_reference(locations, manifest)
    axes = {label: tuple(np.load(directory / f"{label}-{name}-axis-m.npy", allow_pickle=False) for name in ("x", "y", "z")) for label in "ABCD"}
    verify_axes(axes)
    for label in axes:
        for actual, expected in zip(axes[label], mesh_axes(label)):
            np.testing.assert_array_equal(actual, expected)
    for state, (left, right) in STATES.items():
        np.testing.assert_array_equal(contact_voltage(locations, manifest, left, right), np.load(directory / f"{state}-reference-v.npy", allow_pickle=False))
    rows, voltages, workers = [], {}, []
    attempts = 0
    peak = 0
    for label in "ABCD":
        path = directory / f"worker-{label}.json"
        if not path.exists():
            rows.extend({"mesh": label, "state": state, "status": "not attempted", "rms": "", "maximum": "", "passed": False} for state in STATES)
            continue
        record = json.loads(path.read_text())
        workers.append(record)
        if record["mesh"] != label or set(record["states"]) - set(STATES):
            raise ValueError("Worker scope differs from approved states")
        peak = max(peak, record.get("resources", {}).get("peak_rss_bytes", 0), record.get("construction", {}).get("peak_rss_bytes", 0))
        geometry = record.get("geometry_checks", {})
        completed = any(entry["status"] == "completed" for entry in record["states"].values())
        if completed and (geometry.get("straddling_cells") != 0 or geometry.get("maximum_electrode_node_error_m") != 0):
            raise ValueError("Native geometry checks failed")
        for state in STATES:
            entry = record["states"].get(state, {"status": "not attempted"})
            status = entry["status"]
            if status in ("attempted", "completed"):
                attempts += 1
            if status != "completed":
                rows.append({"mesh": label, "state": state, "status": status, "rms": "", "maximum": "", "passed": False})
                continue
            if state != "H" and not record["states"]["H"]["check"]["passed"]:
                raise ValueError("Heterogeneous state ran without its homogeneous gate")
            voltage = np.load(directory / f"{label}-{state}-voltage-v.npy", allow_pickle=False)
            if voltage.shape != (4096,) or not np.all(np.isfinite(voltage)):
                raise ValueError("Invalid native voltage array")
            voltages[label, state] = voltage
            reference = np.load(directory / f"{state}-reference-v.npy", allow_pickle=False)
            check = normalized_discrepancy(voltage, reference, sigma)
            for key in ("rms", "maximum"):
                if not np.isclose(check[key], entry["check"][key], rtol=1e-12, atol=1e-12):
                    raise ValueError("Recorded metric differs from raw data")
            if check["passed"] != entry["check"]["passed"]:
                raise ValueError("Recorded acceptance decision differs from raw data")
            peak = max(peak, entry["resources"]["peak_rss_bytes"])
            rows.append({"mesh": label, "state": state, "status": status, **check})
            np.save(directory / f"{label}-{state}-normalized-residual.npy", (voltage - reference) / sigma, allow_pickle=False)
    if attempts > 12:
        raise ValueError("More than twelve native state solves attempted")
    comparisons = []
    for first, second, factor in (("A", "B", "core resolution"), ("C", "D", "core resolution"), ("A", "C", "extent"), ("B", "D", "extent")):
        for state in STATES:
            if (first, state) in voltages and (second, state) in voltages:
                comparisons.append({"first": first, "second": second, "factor": factor, "state": state,
                                    **normalized_discrepancy(voltages[first, state], voltages[second, state], sigma)})
    established = (all(any(row["mesh"] == label and row["state"] == state and row["passed"] for row in rows) for label in "BD" for state in STATES)
                   and all(any(row["first"] == "B" and row["second"] == "D" and row["state"] == state and row["passed"] for row in comparisons) for state in STATES))
    seconds = DEVELOPMENT_ALLOWANCE_SECONDS + json.loads((directory / "preparation.json").read_text())["wall_seconds"] + sum(record["worker_wall_seconds"] for record in workers)
    stopped = (directory / "resource-limit.json").exists()
    if stopped:
        peak = max(peak, json.loads((directory / "resource-limit.json").read_text())["peak_rss_bytes"])
    established = established and all(record["status"] == "completed" for record in workers) and not stopped and seconds <= LIMIT_SECONDS and peak <= 8 * 2**30
    summary = {"scientific_status": "contact accuracy established for declared survey" if established else "inconclusive",
               "native_state_solve_attempts": attempts, "completed_states": len(voltages),
               "accounted_worker_seconds": seconds, "development_allowance_seconds": DEVELOPMENT_ALLOWANCE_SECONDS,
               "worker_cap_seconds": LIMIT_SECONDS, "peak_rss_gib": peak / 2**30, "resource_stop": stopped,
               "reference_checks_passed": reference_checks["passed"], "state_errors": rows, "controlled_comparisons": comparisons,
               "sphere_accuracy": "unverified", "cross_library_agreement": "not tested"}
    save_json(directory / "summary.json", summary)
    write_csv(directory / "state-errors.csv", rows)
    write_csv(directory / "controlled-comparisons.csv", comparisons)
    lines = ["# Recomputed contact benchmark evidence", "", f"Scientific outcome: **{summary['scientific_status']}**.", "",
             "All errors use the original fixed homogeneous tolerance scale. RMS <= 0.1 and maximum <= 0.25 are required.", "",
             "| Mesh | State | Status | RMS | Maximum | Pass |", "| --- | --- | --- | ---: | ---: | --- |"]
    for row in rows:
        lines.append(f"| {row['mesh']} | {row['state']} | {row['status']} | {row['rms']} | {row['maximum']} | {row['passed']} |")
    lines += ["", "| First | Second | Changed factor | State | RMS | Maximum | Pass |", "| --- | --- | --- | --- | ---: | ---: | --- |"]
    for row in comparisons:
        lines.append(f"| {row['first']} | {row['second']} | {row['factor']} | {row['state']} | {row['rms']:.6g} | {row['maximum']:.6g} | {row['passed']} |")
    lines += ["", f"Native state solves attempted: {attempts}. Accounted worker time: {seconds:.3f} s, including {DEVELOPMENT_ALLOWANCE_SECONDS:.0f} s development allowance. Peak recorded process memory: {peak / 2**30:.3f} GiB.",
              "", "Single-run CPU resource observations describe this study. They do not establish a repeatable speedup or validate sphere responses.", ""]
    (directory / "TABLES.md").write_text("\n".join(lines), encoding="utf-8")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes_plot = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
    for ax, metric, limit in zip(axes_plot, ("rms", "maximum"), (.1, .25)):
        for state in ("C10", "C100"):
            data = [row for row in rows if row["state"] == state and row["status"] == "completed"]
            ax.plot([row["mesh"] for row in data], [row[metric] for row in data], "o-", label=state)
        ax.axhline(limit, color="red", linestyle="--", label="Threshold")
        ax.set_yscale("log")
        ax.set_ylabel(f"Normalized {metric}")
        ax.set_xlabel("Controlled mesh")
        ax.legend()
    fig.savefig(directory / "contact-errors.png", dpi=160)
    plt.close(fig)
    return summary


def main():
    parser = argparse.ArgumentParser(description="Recompute exact-contact benchmark evidence from saved data")
    parser.add_argument("directory", type=Path)
    result = build_report(parser.parse_args().directory)
    print(json.dumps({key: result[key] for key in ("scientific_status", "native_state_solve_attempts", "accounted_worker_seconds", "peak_rss_gib")}))


if __name__ == "__main__":
    main()
