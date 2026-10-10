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
| Exact contact reference | `contact.green_and_gradient`, `contact_voltage` | Literal signed voltages, interface/current identities, reciprocity, and homogeneous reduction | Implemented; reference checks pass |
| Controlled contact meshes | `contact.mesh_axes`, `verify_axes` | Published axis arrays, retained-knot tests, native cell/electrode checks | Implemented; four meshes preserve independent factors |
| Bounded native contact study | `python -m opensubsurface.contact` | Twelve state records and raw voltages | Exercised; homogeneous controls pass, all heterogeneous gates fail |
| Contact report reproduction | `python -m opensubsurface.contact_report` | Recomputed references, raw checksums, state and factor comparisons | Exercised; scientific outcome inconclusive |
| Optional primary-field diagnostics | `contact.primary_field_diagnostics` | Regression check prohibits absent native-mesh getter call | Corrected; voltage calculation unchanged |
| Native refinement/provenance review | `research/native-solver-review.md` | Installed-source hashes, native build/binary identities, construction-only probe | Direct/managed path distinction verified; subsequent P2 accuracy checks fail |
| Explicit P2 contact calculation | `python -m opensubsurface.p2_contact` | Six raw state arrays; cell/material checks and C resource plan | Exercised; homogeneous gates pass, heterogeneous gates fail |
| P2 diagnostic/accuracy decisions | `python -m opensubsurface.p2_report` | Raw ratio recreation, joint-coordinate and failed-worker regression checks | Diagnostic target not supported; contact accuracy inconclusive |
| Development quality gate | Pinned Ruff, pytest, package build, CLI report recreation | Checkpoint record and CI workflow | Implemented; no added solver/runtime dependency |
| Standalone reflection reproduction | `experiments/pygimli-reflection-reproduction/reproduce.py` | Two-row H/C100 execution outside the checkout, frozen-input tests, and saved artifacts | Exercised; heterogeneous reflection discrepancy reproduced, cause unresolved |

See the [pilot README](experiments/ert-observability-pilot/README.md), [first results](experiments/ert-observability-pilot/results/2026-10-08/RESULTS.md), and [numerical follow-up](experiments/ert-numerical-validation/README.md).
