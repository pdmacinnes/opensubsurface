# Feature map

This file records implemented research capabilities and their verification state. Numerical validity is tracked separately from whether the software runs.

| Capability | Entry point | Evidence | Current state |
| --- | --- | --- | --- |
| Canonical fixed survey | `domain.candidate_manifest` | Manifest checksum and unit tests | Implemented; 4,096 configurations with seed 20261008 |
| Matched geometry definitions | `domain.primary_catalog` | Volume and catalog tests | 24 pairs, 30 distinct primary models |
| Half-space and Gaussian diagnostics | `domain` | Literal analytic and probability checks | Implemented; conditional on declared assumptions |
| SimPEG field adapter | `solvers.SimpegForward` | Raw numerical profiles and units/reciprocity tests | Runs; strict pilot continuum-reference gate failed |
| Independent pyGIMLi adapter | `solvers.PygimliForward` | Homogeneous profile and background-scaling tests | Runs; four inclusion mesh comparisons fail convergence gates |
| Resource and numerical gates | `pilot profile`, `pilot verify`, `pilot run` | Profile JSON and stop-accounting tests | Implemented; the first study stopped |
| Full catalog and nuisance analysis | `pilot run` | Source inspection and domain tests | Implemented continuation; native full path not exercised |
| Explicit incomplete outcomes | `pilot record-stop` | 144 skipped-case rows and CLI stop record | Exercised; no fabricated distances |
| Report reproduction | `python -m opensubsurface.report` | Recomputed metrics from five raw profiles | Exercised; first scientific outcome inconclusive |
| Source audits and streamed solves | `SimpegForward.audit`, `audit_dipoles` | Real batch/superposition tests and recorded current/interpolation audits | Implemented; tested audits pass, continuum accuracy still fails |
| Tensor and separately graded octree meshes | `validation worker` | Published homogeneous voltage comparisons | Exercised; every tested SimPEG configuration fails strict reference gate |
| Fitted sphere meshes | `PygimliConformingForward`, `validation conforming` | Exact electrode/region test, saved meshes, four-geometry refinement comparisons | Implemented; volume representation improves, response convergence unverified |
| Numerical follow-up report | `python -m opensubsurface.validation_report` | Recomputed raw-data tables and resource ledger | Exercised; scientific outcome inconclusive |

See the [pilot README](experiments/ert-observability-pilot/README.md), [first results](experiments/ert-observability-pilot/results/2026-10-08/RESULTS.md), and [numerical follow-up](experiments/ert-numerical-validation/README.md).
