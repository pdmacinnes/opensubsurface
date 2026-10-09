# ERT numerical validation follow-up

This approved study investigates the numerical-reference failure in the original ERT observability pilot. It preserves the physical model, frozen survey, noise scale, and accuracy thresholds. Its scientific outcome is **inconclusive**.

Read the [results and interpretation](results/2026-10-08/RESULTS.md), [raw-data comparison tables](results/2026-10-08/TABLES.md), and [approved scope](../../specs/ert-numerical-validation.md).

## Recompute the published evidence

Use Python 3.12 and run these commands from the repository root. The tested platform is Windows x64. The dependency lock records that environment; compatibility with other platforms has not been demonstrated.

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-lock.txt
.venv/Scripts/python.exe -m pip install -e . --no-deps
$env:OMP_NUM_THREADS='2'
$env:OPENBLAS_NUM_THREADS='2'
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe -m opensubsurface.validation_report experiments/ert-numerical-validation/results/2026-10-08
```

The reporting command recomputes homogeneous errors, inclusion mesh differences, residual arrays, tables, and the figure from published voltage arrays. It checks the original manifest hash and resource totals. It does not rerun the native forward models or establish independent inclusion accuracy.

## Rerun native comparisons

The [published commands](results/2026-10-08/commands.ps1) reproduce the recorded mesh choices in a fresh output directory. They run only the same four existing inclusion geometries after each applicable homogeneous gate passes. Expect CPU work and several GiB of memory. There is no paid API or GPU backend.

Run each worker sequentially. Each invocation subtracts previous recorded worker times from the four-hour budget. A ten-minute allowance covers uninstrumented development, smoke checks, and early failed meshing attempts. The published ledger counts two initially overlapping probes twice. These times are not controlled performance benchmarks.

The monitor samples process memory and checks an absolute deadline. On Windows it also reads the OS peak working set. Compiled calls may defer Python monitoring until they return; a resource check then stops the process before accepting its output. This is a monitored stop mechanism, not an operating-system memory sandbox. Every accepted recorded peak is below 8 GiB.

## What is published

- JSON files record solver settings, gates, source audits, equation residuals where exposed, and resources.
- NPY files store synthetic voltages in volts and normalized residuals. Load them with `allow_pickle=False`.
- `fitted-meshes.zip` contains the generated pyGIMLi BMS meshes for inspection or homogeneous replay. It stores only mesh basenames. Extract them into the rerun output directory before calling `validation replay-homogeneous`.
- CSV files record electrode-role counts, mesh comparisons, and represented volumes.
- The original electrode locations, analytic background, and 4,096-row manifest remain in the [original record](../ert-observability-pilot/results/2026-10-08/).

Some early homogeneous-only profiles record solve and construction durations rather than a single complete worker duration. The resource accounting uses their sum and the development allowance. Homogeneous responses on early fitted meshes were replayed from the saved meshes to publish raw reference voltages; replay time is counted separately.

The comparison protocol is numerical validation only. No full geometry bank, nuisance search, classifier, adaptive acquisition policy, or hardware result is included.
