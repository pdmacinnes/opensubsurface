# Pilot dependencies

The pilot uses Python 3.12 and the pinned environment in [requirements-lock.txt](../requirements-lock.txt). No paid API or GPU backend is used.

| Dependency | Version | Purpose | Upstream license metadata |
| --- | --- | --- | --- |
| SimPEG | 0.25.2 | Primary DC resistivity framework | MIT |
| discretize | 0.12.0 | Existing finite-volume meshes and operators | MIT |
| pymatsolver | 0.4.0 | Existing sparse linear-solver adapters | MIT |
| pyGIMLi | 1.6.1 | Independent finite-element framework | Apache 2.0 |
| pgcore | 1.6.0 | pyGIMLi compiled core | Apache 2.0 |
| PyAMG | 5.3.0 | Standard algebraic-multigrid preconditioner | MIT |
| TetGen Python interface | 0.8.4 | Fitted tetrahedral meshes for numerical validation | Wrapper MIT; bundled TetGen has its own AGPLv3 notice |
| NumPy | 2.5.3 | Arrays and deterministic survey generation | Composite open-source notices in distribution metadata |
| SciPy | 1.18.1 | Sparse solves and Gaussian diagnostic | BSD-style license and bundled dependency notices |
| Matplotlib | 3.11.2 | Scientific figures | Matplotlib license |
| psutil | 7.2.2 | Worker resource measurements | BSD 3-Clause |
| pytest | 9.1.1 | Scientific unit and solver smoke checks | MIT |
| Ruff | 0.16.10 | Development-only static code checks | MIT |

This table records the installed distribution metadata. Dependencies and bundled components retain their own notices and licenses. Third-party binaries are not committed to this repository.

The tested pyGIMLi Python distribution reports version 1.6.1. Its Python-reported `__version__` is not a reliable compiled-build identifier in this installation: its version helper resolves the enclosing OpenSubsurface Git checkout. The [native source review](../research/native-solver-review.md) documents the correction. Historical environment JSON retains the values actually reported at execution.

The independent native-core string from `pg.core.versionStr()` is `libgimli-v1.6.0-4-g9076db0e`. The [review evidence](../research/native-solver-review-evidence.json) records installed Python hashes, the extension and bundled DLL hashes, and the corresponding upstream revision. Distribution versions, dynamic Python version strings, and native binary provenance are separate fields.

The original project code and generated research data are covered by the repository's Apache 2.0 license. That license does not relicense dependencies.

The validation follow-up uses the [TetGen array API](https://github.com/pyvista/tetgen) with pyGIMLi sphere geometry and pyGIMLi's existing PDE solver. This adds a meshing dependency, not a custom forward solver. Read the distribution's wrapper license and bundled `tetgen-license`, and the [upstream licensing statement](https://github.com/TetGen/TetGen/blob/main/README.md). The project does not redistribute a bundled executable or change third-party licenses.

PyVista and VTK were installed locally while diagnosing the older filename-based mesh bridge. The final array adapter does not require them; they are excluded from the reproducible dependency lock. No code or data from those diagnostic dependencies is copied into this repository.
