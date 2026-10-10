# Explicit P2 contact comparison

The user approved the [spec](../../specs/ert-p2-contact-comparison.md) on October 9, 2026. All six declared P2 state solves completed. The [results](results/2026-10-09/RESULTS.md) do not support the predefined fourfold-error-reduction hypothesis, and contact accuracy remains inconclusive.

P2 increases field approximation order on the original A/C material cells. The [native review](../../research/native-solver-review.md) explains the direct mesh path and why materials must be assigned explicitly after construction. This experiment changes no material geometry, physical source, boundary convention, or accuracy threshold.

## Recompute the published evidence

Use Python 3.12 from the repository root and the pinned environment:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-lock.txt
.venv/Scripts/python.exe -m pip install -e . --no-deps
$env:OMP_NUM_THREADS='2'
$env:OPENBLAS_NUM_THREADS='2'
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe -m ruff check src tests
.venv/Scripts/python.exe -m opensubsurface.p2_report experiments/ert-p2-contact-comparison/results/2026-10-09
```

The report verifies original input provenance, analytical identities, joint three-dimensional cell coordinates, materials, recorded errors, and resource planning. It recomputes the diagnostic and accuracy decisions from saved arrays. It performs no new contact voltage solve.

## Rerun the bounded experiment

Run the original twelve-state contact record verification first; the preparation command does this automatically. Use a fresh P2 output directory:

```powershell
$env:OMP_NUM_THREADS='2'
$env:OPENBLAS_NUM_THREADS='2'
$output = 'experiments/outputs/p2-contact-rerun'
.venv/Scripts/python.exe -m opensubsurface.p2_contact prepare --output $output
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
.venv/Scripts/python.exe -m opensubsurface.p2_contact worker --mesh A --output $output
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
.venv/Scripts/python.exe -m opensubsurface.p2_contact worker --mesh C --output $output
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
.venv/Scripts/python.exe -m opensubsurface.p2_report $output
```

Each worker runs H before C10/C100. C-P2 requires completed A-P2 and its passing H control. It also requires the approved memory/time projection to fit remaining resources. Skips are explicit observations, not successful cases. An attempted label cannot be overwritten.

The ledger includes preparation, complete worker time, and a ten-minute development allowance within the two-hour cap. The process memory limit is 8 GiB. The existing sampled monitor also checks after native calls and reads Windows peak working set. Compiled code may delay monitoring; this is not an operating-system hard memory sandbox. The planning heuristic is not a guaranteed memory/runtime bound.

## Published artifacts

- The original manifest, A/C axes, independent reference voltages, and fixed tolerance scale are frozen inputs.
- `linear-*-voltage-v.npy` are byte-identical copies of the published linear A/C baselines.
- `*-cell-correspondence.npy` and `*-cell-centers-m.npy` support material-cell correspondence.
- `*-resistivity-ohm-m.npy` records explicit per-state material assignment.
- `p2-*-voltage-v.npy` stores signed synthetic volts. Load arrays with `allow_pickle=False`.
- Worker JSON records geometry, boundaries, native counts, material checks, resources, and C admission planning.
- Fundamental-array checksums and the original baseline checksum registry preserve provenance. Residual arrays and report tables are derived.
- The environment separates distribution versions, Python-reported version, native build string, binary hashes, installed source hashes, and project execution-source hashes.

The original baseline axis checks were verified during preparation. P2 geometry checks are recorded separately in each worker. Local logs and package-build output are ignored and are not publication artifacts.

The [checkpoint record](results/2026-10-09/VERIFICATION.md) documents the updated testing instructions received during execution and the actual red-to-green reporting fix. Ruff was added as development-only tooling for those new gates. No solver/runtime dependency was added.
