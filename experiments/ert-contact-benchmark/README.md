# Exact heterogeneous contact benchmark

The user approved the [spec](../../specs/ert-contact-benchmark.md) for implementation and execution on October 9, 2026. The [first result](results/2026-10-09/RESULTS.md) is **inconclusive**. All twelve declared state solves completed, with accurate homogeneous controls and failed heterogeneous reference gates.

This benchmark uses an independent image solution for an infinite vertical contact. The [reference note](../../research/contact-reference.md) documents the equations and literal checks. It is a separate diagnostic model; it does not certify sphere or two-body accuracy.

## Reproduce the saved evidence

Use Python 3.12 from the repository root. The pinned environment and tested platform are documented in [dependencies](../../docs/dependencies.md). No dependency was added for this study.

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-lock.txt
.venv/Scripts/python.exe -m pip install -e . --no-deps
$env:OMP_NUM_THREADS='2'
$env:OPENBLAS_NUM_THREADS='2'
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe -m opensubsurface.contact_report experiments/ert-contact-benchmark/results/2026-10-09
```

The report verifies the frozen survey and reference, mesh nesting, raw checksums, recorded gates, and scope. It recomputes the tables and figure from saved voltages. It runs no native contact solve.

## Rerun the approved twelve-state experiment

Use a fresh output directory. These commands verify the reference before native work and run one mesh at a time. The homogeneous gate controls whether that mesh's contact states execute.

```powershell
$env:OMP_NUM_THREADS='2'
$env:OPENBLAS_NUM_THREADS='2'
$output = 'experiments/outputs/ert-contact-rerun'
.venv/Scripts/python.exe -m opensubsurface.contact prepare --output $output
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
foreach ($meshLabel in 'A','B','C','D') {
    .venv/Scripts/python.exe -m opensubsurface.contact worker --mesh $meshLabel --output $output
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
.venv/Scripts/python.exe -m opensubsurface.contact_report $output
```

`prepare` refuses to overwrite an existing directory. Worker labels cannot be overwritten or repeated, and a resource stop blocks continuation. The two-hour ledger includes preparation, complete worker durations, and a ten-minute development allowance. A finite absolute deadline is set before each worker. The existing monitor checks peak process memory against 8 GiB during work and after native calls.

Compiled calls may defer the Python monitor. Windows peak working-set observations help capture transient use, but this is not an operating-system memory sandbox. The published twelve solves remained below the cap. Reruns on different machines are not guaranteed to fit the same budget or reproduce identical floating-point values.

## Artifact conventions

- `configuration.json` freezes materials, electrodes, units, thresholds, and resource caps. The manifest is copied with its original checksum.
- `*-axis-m.npy` records every mesh axis in meters; core-refinement and extent comparisons retain the prescribed old knots.
- `*-reference-v.npy`, `*-voltage-v.npy`, and `fixed-sigma-v.npy` store signed volts and the unchanged background tolerance scale.
- `worker-*.json` records attempts, gates, input/core/operator mesh counts, primary-field diagnostics, worst configurations, and resources.
- `reference-checks.json` records literal and physical-identity checks. `axis-checks.json` records controlled mesh invariants.
- `raw-data-sha256.json` checksums fundamental arrays, excluding derived residual arrays and figures.
- `TABLES.md`, the summary, comparison CSV files, residual arrays, and figure are derived artifacts.

Load NPY files with `allow_pickle=False`. The environment records the executed source hashes. Local logs and downloaded upstream source remain ignored; they are not public experiment artifacts.

Timings are single-run CPU feasibility observations. No GPU speedup, hardware sensing result, cross-library agreement, or acquisition-efficiency result is claimed.
