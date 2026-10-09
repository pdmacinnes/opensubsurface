import argparse
import csv
from hashlib import sha256
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .domain import homogeneous_voltage, noise_sigma, normalized_discrepancy


def build_report(directory):
    status = json.loads((directory / "run-status.json").read_text())
    if status["scientific_status"] != "inconclusive":
        raise ValueError("This report summarizes an inconclusive numerical-profile run")
    config = json.loads((directory / "configuration.json").read_text())
    manifest_path = directory / "candidate-manifest.csv"
    if sha256(manifest_path.read_bytes()).hexdigest() != config["manifest_sha256"]:
        raise ValueError("Published manifest checksum does not match its configuration")
    manifest = np.loadtxt(manifest_path, delimiter=",", skiprows=1, dtype=int)
    locations = np.array(config["electrodes_m"])
    analytic = homogeneous_voltage(locations, manifest, current=config["current_a"])
    sigma = noise_sigma(analytic, 0.01, 1e-6)
    rows = []
    for path in sorted(directory.glob("profile-*.json")):
        profile = json.loads(path.read_text())
        solver = profile["solver"]
        suffix = path.stem[len("profile-") + len(solver) + 1:]
        numerical = np.load(directory / f"{solver}-homogeneous-{suffix}.npy", allow_pickle=False)
        check = normalized_discrepancy(numerical, analytic, sigma)
        np.testing.assert_allclose([check["rms"], check["maximum"]],
                                   [profile["homogeneous_check"]["rms"], profile["homogeneous_check"]["maximum"]],
                                   rtol=1e-9, atol=1e-10)
        settings = profile["mesh"]
        linear = settings.get("linear_solver", "lu") if solver == "simpeg" else "native SR"
        rows.append({"profile": path.name, "solver": solver, "linear_solver": linear,
                     "target_cell_m": settings["cell_size"],
                     "electrode_cell_m": settings.get("electrode_cell_size") or settings["cell_size"],
                     "extent_m": settings["extent"], "normalized_rms": check["rms"],
                     "normalized_maximum": check["maximum"], "homogeneous_passed": check["passed"],
                     "projected_bank_hours": profile["projected_full_bank_seconds"] / 3600,
                     "peak_gib": max(record["peak_rss_bytes"] for record in profile["records"].values()) / 1024 ** 3,
                     "resource_cap_passed": profile["resource_cap_passed"]})
    with (directory / "profile-summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), layout="constrained")
    labels = [f"{row['solver']} {row['linear_solver']}\nbody {row['target_cell_m']:g} m\nsource {row['electrode_cell_m']:g} m\nextent {row['extent_m']:g} m" for row in rows]
    for ax, metric, threshold, title in zip(axes, ("normalized_rms", "normalized_maximum"), (0.1, 0.25), ("RMS error", "Maximum error")):
        ax.scatter(np.arange(len(rows)), [row[metric] for row in rows], s=60, color=["#27746e" if row["homogeneous_passed"] else "#a74632" for row in rows])
        ax.axhline(threshold, color="#202020", linestyle="--", label=f"Acceptance: {threshold:g}")
        ax.set_yscale("log")
        ax.set_xticks(np.arange(len(rows)), labels, fontsize=7)
        ax.set_title(title)
        ax.set_ylabel("Error / assumed noise standard deviation")
        ax.legend(fontsize=8, loc="lower right")
    fig.suptitle("Exploratory homogeneous-reference checks\n1% relative error plus 1 microvolt absolute floor", fontsize=13)
    fig.savefig(directory / "numerical-verification.png", dpi=180)
    plt.close(fig)
    np.save(directory / "analytic-homogeneous-v.npy", analytic, allow_pickle=False)
    table = ["| Solver | Body cell (m) | Source cell (m) | Extent (m) | RMS | Maximum | Projected bank (h) | Peak (GiB) |",
             "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    table += [f"| {row['solver']} {row['linear_solver']} | {row['target_cell_m']:g} | {row['electrode_cell_m']:g} | {row['extent_m']:g} | {row['normalized_rms']:.6g} | {row['normalized_maximum']:.6g} | {row['projected_bank_hours']:.3g} | {row['peak_gib']:.3g} |" for row in rows]
    report = """# First pilot run: inconclusive

The numerical profiles did not establish verified geometry discrimination. The finest tested SimPEG configuration failed the homogeneous-reference accuracy gate and exceeded the projected 12-hour bank budget. The full catalog and nuisance bank were not run.

This is a failure of the tested numerical configuration, not evidence that surface ERT cannot distinguish these geometries.

## Measurements from the profiles

Errors below are normalized by the common 1% relative-error plus 1 microvolt covariance. Acceptance requires RMS at most 0.1 and maximum at most 0.25.

""" + "\n".join(table) + """

![Exploratory numerical verification](numerical-verification.png)

The finest SimPEG profile used 800,724 cells and 789,745 nodes. Its linear equation residuals were below 1e-10, while its continuum-reference errors remained much larger than the acceptance limits. An algebraically converged solve is not sufficient evidence of forward-model accuracy.

The pyGIMLi homogeneous check uses its analytical singularity-removal formulation. Passing that homogeneous case does not establish accurate sphere responses, convergence, or agreement with SimPEG. Four verified independent inclusion comparisons remain outstanding.

Coarse cell-center inclusion assignments also changed represented volume. The nominal sphere volume is about 14.137 cubic metres. The first 0.5 m SimPEG mesh represented 17 cubic metres. The fine source-refined mesh represented about 14.180 cubic metres for the profiled single sphere. Geometric volume agreement alone does not establish electrical accuracy.

## Scope of the record

These were exploratory numerical profiles during implementation, with one run per distinct profiled model. Timings are observations, not a speedup benchmark. The complete-bank estimate uses the mean of two inclusion solve times multiplied by 270 distinct normalized-background models. It excludes additional verification and plotting. That is a projection, not measured full-study runtime.

The observed fine-profile projection was approximately 13.4 hours, above the approved 12-hour cap. Its observed peak process memory remained below 8 GiB. Compute and numerical gates both prevent proceeding with that configuration.

All 144 planned pair/noise outcomes are recorded as not computed in pair-diagnostics.csv. Distances and classification errors are blank. The 810-state nuisance bank was not evaluated. There is no adaptive acquisition, material identification, hardware feasibility, or field mapping result.

The data-generation physics can be rerun using the published mesh flags and pinned dependencies. Exploratory records predate the final reporting and gate code. Exact runtimes and last-bit floating-point values are not promised across machines. The report generator checks the stored numerical metrics against the raw voltage arrays and frozen manifest.

## Verification and limitations

The scientific unit and solver smoke checks cover units, polarity, reciprocity, equal-volume geometry definitions, manifest uniqueness, background-resistivity scaling, and explicit failure accounting. Smoke-check tolerances do not replace the stricter pilot verification thresholds.

An electrode-node placement issue found in a coarse pyGIMLi smoke test was fixed by retaining all exact electrode coordinates in the independent grid. The published pyGIMLi profile used a 1.5 m grid that already contained those coordinates. No acceptance threshold was relaxed.

No fundamental observability conclusion follows from this stop. The cause of the remaining continuum-reference error has not been isolated completely. Discretization and remote-boundary grading need a separate validation study before interpreting small anomaly responses.

## Next decision

Pause the full bank. Review the proposed validation-only specification before more experiments. Keep the original physical assumptions and accuracy thresholds. Revisit the bank scope or its cost only after numerical validity is demonstrated.
"""
    (directory / "RESULTS.md").write_text(report, encoding="utf-8")
    return rows


def main():
    parser = argparse.ArgumentParser(description="Verify and summarize the published numerical profiles")
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    rows = build_report(args.directory)
    print(json.dumps({"profiles_verified_against_raw_data": len(rows), "scientific_status": "inconclusive"}))


if __name__ == "__main__":
    main()
