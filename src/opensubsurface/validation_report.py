import argparse
import json
from pathlib import Path

import numpy as np

from .domain import homogeneous_voltage, noise_sigma, normalized_discrepancy, primary_catalog
from .pilot import save_json, write_csv
from .validation import frozen_inputs, RETRY_RESERVE_SECONDS


def recorded_seconds(record):
    return record.get("worker_wall_seconds", record.get("resources", {}).get("wall_seconds", 0.)
                      + record.get("construction", {}).get("wall_seconds", 0.))


def build_report(directory):
    config, manifest = frozen_inputs()
    analytic = homogeneous_voltage(np.array(config["electrodes_m"]), manifest)
    sigma = noise_sigma(analytic, .01, 1e-6)
    records = []
    for path in sorted(directory.glob("*.json")):
        record = json.loads(path.read_text())
        if "label" in record:
            records.append(record)
    homogeneous = []
    volumes = []
    models, _ = primary_catalog()
    ids = set()
    peak = 0
    for record in records:
        label = record["label"]
        if "models" not in record:
            voltage = np.load(directory / f"{label}-voltages-v.npy", allow_pickle=False)
            if voltage.shape != (4096,) or not np.all(np.isfinite(voltage)):
                raise ValueError(f"Invalid raw voltage array: {label}")
            check = normalized_discrepancy(voltage, analytic, sigma)
            for key in ("rms", "maximum"):
                if not np.isclose(check[key], record["homogeneous_check"][key], rtol=1e-10, atol=1e-12):
                    raise ValueError(f"Recorded homogeneous metric differs from raw data: {label}")
            resource = record["resources"]
            peak = max(peak, resource["peak_rss_bytes"], record["construction"]["peak_rss_bytes"])
            homogeneous.append({"label": label, **check, "cells": resource["cells"],
                "peak_gib": resource["peak_rss_bytes"] / 2**30,
                "worker_seconds": recorded_seconds(record),
                "equation_residual": resource.get("maximum_relative_equation_residual", "not exposed by adapter")})
            np.save(directory / f"{label}-normalized-residual.npy", (voltage - analytic) / sigma, allow_pickle=False)
        for identifier, entry in record.get("models", {}).items():
            ids.add(identifier)
            if "resources" not in entry:
                continue
            resource = entry["resources"]
            peak = max(peak, resource["peak_rss_bytes"], entry.get("construction", {}).get("peak_rss_bytes", 0))
            nominal = len(models[identifier].centers) * 4 * np.pi * models[identifier].radius ** 3 / 3
            volume = resource["voxel_inclusion_volume_m3"]
            volumes.append({"label": label, "model": identifier, "nominal_m3": nominal,
                            "represented_m3": volume, "relative_error": volume / nominal - 1,
                            "cells": resource["cells"], "peak_gib": resource["peak_rss_bytes"] / 2**30})
            if not entry.get("homogeneous_check", record.get("homogeneous_check", {})).get("passed"):
                raise ValueError("Inclusion evaluated without its homogeneous gate")
            raw_homogeneous = directory / f"{label}-{identifier}-homogeneous-v.npy"
            if raw_homogeneous.exists():
                check = normalized_discrepancy(np.load(raw_homogeneous, allow_pickle=False), analytic, sigma)
                if not check["passed"]:
                    raise ValueError("Published fitted homogeneous data fail the gate")
    if len(ids) > 4:
        raise ValueError("Approved four-geometry scope exceeded")
    labels = {record["label"] for record in records}
    comparisons = []
    pairs = [("pygimli-inclusions-h075", "pygimli-inclusions-h075-core6"),
             ("pygimli-inclusions-h075-core6", "pygimli-inclusions-h05-core6"),
             ("fitted-s24-r12-v005", "fitted-s48-r24-v0025"),
             ("fitted-s48-r24-v0025", "fitted-s48-r24-v001"),
             ("fitted-s48-r24-v0025", "fitted-s64-r32-v0025")]
    for first, second in pairs:
        if first not in labels or second not in labels:
            continue
        for identifier in sorted(ids):
            a = np.load(directory / f"{first}-{identifier}-voltages-v.npy", allow_pickle=False)
            b = np.load(directory / f"{second}-{identifier}-voltages-v.npy", allow_pickle=False)
            if a.shape != (4096,) or b.shape != (4096,) or not np.all(np.isfinite(a + b)):
                raise ValueError("Invalid inclusion voltage array")
            comparisons.append({"first": first, "second": second, "model": identifier,
                                **normalized_discrepancy(a, b, sigma)})
    seconds = RETRY_RESERVE_SECONDS + sum(recorded_seconds(record) for record in records)
    extra = directory / "homogeneous-replay.json"
    if extra.exists():
        replay = json.loads(extra.read_text())
        seconds += replay["worker_wall_seconds"]
        peak = max(peak, replay["peak_rss_bytes"])
    summary = {"scientific_status": "inconclusive", "manifest_sha256": config["manifest_sha256"],
               "unique_geometries": sorted(ids), "accounted_compute_seconds": seconds,
               "development_retry_reserve_seconds": RETRY_RESERVE_SECONDS,
               "peak_rss_gib": peak / 2**30, "compute_cap_seconds": 14400, "memory_cap_gib": 8,
               "independent_inclusion_agreement": "not established; SimPEG homogeneous gate still fails",
               "homogeneous": homogeneous, "inclusion_comparisons": comparisons}
    if seconds > 14400 or peak > 8 * 2**30:
        raise ValueError("Published resource accounting exceeds the approved cap")
    save_json(directory / "summary.json", summary)
    write_csv(directory / "homogeneous-comparison.csv", homogeneous)
    write_csv(directory / "inclusion-mesh-comparison.csv", comparisons)
    write_csv(directory / "represented-volumes.csv", volumes)
    lines = ["# Recomputed numerical evidence", "", "Scientific outcome: **inconclusive**.", "",
             "These tables are generated from the published raw voltages and mesh metadata. "
             "All discrepancies use the original analytic-background noise scale. RMS <= 0.1 and maximum <= 0.25 are required.", "",
             "## Homogeneous reference", "", "| Configuration | RMS | Maximum | Cells | Peak GiB | Equation residual | Gate |",
             "| --- | ---: | ---: | ---: | ---: | --- | --- |"]
    for row in homogeneous:
        residual = row["equation_residual"]
        residual = f"{residual:.3g}" if isinstance(residual, float) else residual
        lines.append(f"| {row['label']} | {row['rms']:.6g} | {row['maximum']:.6g} | {row['cells']} | {row['peak_gib']:.3f} | {residual} | {row['passed']} |")
    lines += ["", "## Inclusion mesh changes", "", "These are numerical convergence comparisons, not geometry-discrimination scores. "
              "Agreement between two meshes does not alone prove accuracy.", "",
              "| First mesh | Second mesh | Existing geometry | RMS | Maximum | Gate |", "| --- | --- | --- | ---: | ---: | --- |"]
    for row in comparisons:
        lines.append(f"| {row['first']} | {row['second']} | {row['model']} | {row['rms']:.6g} | {row['maximum']:.6g} | {row['passed']} |")
    lines += ["", "## Represented body volumes", "", "| Mesh | Geometry | Nominal m3 | Represented m3 | Relative error |", "| --- | --- | ---: | ---: | ---: |"]
    for row in volumes:
        lines.append(f"| {row['label']} | {row['model']} | {row['nominal_m3']:.8g} | {row['represented_m3']:.8g} | {row['relative_error']:.3%} |")
    lines += ["", "## Resources", "", f"Accounted worker time including the retry reserve: {seconds:.2f} s. "
              f"Maximum recorded process peak: {peak / 2**30:.3f} GiB. "
              "The ledger sums overlapping probe times, so it is conservative. "
              "These are CPU runs; no GPU speedup is claimed.", ""]
    (directory / "TABLES.md").write_text("\n".join(lines), encoding="utf-8")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    simpeg = [row for row in homogeneous if not row["label"].startswith("independent")]
    fig, axes = plt.subplots(1, 2, figsize=(12, 6), layout="constrained")
    for ax, metric, threshold in zip(axes, ("rms", "maximum"), (.1, .25)):
        ax.barh([row["label"] for row in simpeg], [row[metric] for row in simpeg])
        ax.axvline(threshold, color="red", linestyle="--", label="Acceptance threshold")
        ax.set_xscale("log")
        ax.set_xlabel(f"Normalized {metric} discrepancy")
        ax.legend()
    fig.savefig(directory / "homogeneous-convergence.png", dpi=160)
    plt.close(fig)
    return summary


def main():
    parser = argparse.ArgumentParser(description="Recompute the published numerical-only ERT evidence")
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    summary = build_report(args.directory)
    print(json.dumps({key: summary[key] for key in ("scientific_status", "accounted_compute_seconds", "peak_rss_gib")}))


if __name__ == "__main__":
    main()
