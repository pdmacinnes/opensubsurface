# ERT observability pilot

The approved pilot is implemented. The [first run is inconclusive](results/2026-10-08/RESULTS.md): numerical verification failed, and the finest tested configuration exceeded the projected compute cap. The full geometry catalog and nuisance bank were not run.

See the [approved specification](../../specs/ert-observability-pilot.md) and [proposed validation-only follow-up](../../specs/ert-numerical-validation.md).

## Environment

Use Python 3.12 in an isolated environment. The commands below use `python` for that interpreter. Activate the environment using your platform's normal procedure.

```text
python -m venv .venv
python -m pip install -r requirements-lock.txt
python -m pip install -e . --no-deps
python -m pytest -q
```

On Windows, the environment interpreter is `.venv/Scripts/python.exe`. On Linux, it is `.venv/bin/python`. A compatible Python 3.12 installation is required to create the environment.

The tested platform is Windows x86-64 with Python 3.12.14. Other platforms require their own compatibility checks. Solver distributions, Python packages, and their dependencies retain their upstream licenses.

## Commands

Run commands from the repository root.

```text
python -m opensubsurface.pilot profile --solver simpeg --cell-size 0.5 --extent 64
python -m opensubsurface.pilot profile --solver pygimli --cell-size 1.5 --extent 64
python -m opensubsurface.pilot verify --cell-size 0.5 --extent 64
python -m opensubsurface.pilot run --cell-size 0.5 --extent 64
```

The `profile` command evaluates a homogeneous background and two specified inclusion models. It also checks an identical-conductivity material twin. It records assumed source current, raw voltages, geometry volume, sampled memory, and solve times.

The `verify` command checks the homogeneous response first. Passing configurations proceed to mesh, padding, and independent-solver comparisons.

The `run` command proceeds to the catalog only after resource and numerical gates pass. Failed gates produce explicit missing-case records rather than geometry conclusions.

These commands are documented reproduction paths. Do not rerun the full catalog under the failed configuration without an approved scope change.

A development profile also tested:

```text
python -m opensubsurface.pilot profile --solver simpeg --cell-size 0.25 --electrode-cell-size 0.125 --extent 128 --linear-solver amg
```

That configuration failed the homogeneous gate and projected about 13.4 hours for the full bank. No full bank was attempted.

PyAMG supplies a standard algebraic-multigrid preconditioner for SciPy conjugate gradients. The SimPEG PDE and physical assumptions are unchanged. The primary and independent backends use different discretizations. Solver agreement is not assumed.

## Rebuild the published report without simulation

```text
python -m opensubsurface.report experiments/ert-observability-pilot/results/2026-10-08
```

This verifies the stored homogeneous errors against raw voltages and the manifest checksum. It regenerates the table, figure, and results report. It does not rerun a forward solver.

## Record an expected stop

```text
python -m opensubsurface.pilot record-stop --profile-record experiments/ert-observability-pilot/results/2026-10-08/profile-simpeg-h0.25-e128-s0.125-amg.json --output experiments/local/reproduced-stop
```

Exit code 2 means a scientific verification or resource gate stopped progression. Exit code 1 indicates an unexpected software exception. Exit code 0 means the requested phase completed; a completed profile may still show failed numerical checks.

A profile does not establish geometry discrimination. Inspect its recorded gate fields.

## Source and artifacts

- [domain.py](../../src/opensubsurface/domain.py): geometry, canonical survey generation, half-space reference, and Gaussian diagnostics.
- [solvers.py](../../src/opensubsurface/solvers.py): existing-library forward adapters and resource measurements.
- [pilot.py](../../src/opensubsurface/pilot.py): profiling, verification, gated catalog execution, and stop records.
- [report.py](../../src/opensubsurface/report.py): verification of saved records and scientific figures.
- [Tests](../../tests/): literal physical checks and failure accounting.
- [Published record](results/2026-10-08/): raw arrays, configuration, manifest, profile metadata, and explicit skipped cases.

Local runs default to ignored `experiments/outputs/`. Published results are added deliberately outside that directory.

The full successful-catalog path is implemented but has not been exercised by this pilot, because its numerical gate did not pass. No field data or hardware result exists.
