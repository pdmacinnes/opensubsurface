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
| NumPy | 2.5.3 | Arrays and deterministic survey generation | Composite open-source notices in distribution metadata |
| SciPy | 1.18.1 | Sparse solves and Gaussian diagnostic | BSD-style license and bundled dependency notices |
| Matplotlib | 3.11.2 | Scientific figures | Matplotlib license |
| psutil | 7.2.2 | Worker resource measurements | BSD 3-Clause |
| pytest | 9.1.1 | Scientific unit and solver smoke checks | MIT |

This table records the installed distribution metadata. Dependencies and bundled components retain their own notices and licenses. Third-party binaries are not committed to this repository.

The tested pyGIMLi Python distribution reports version 1.6.1 while its runtime version string is an untagged build identifier. The published environment records distribution versions. Pinning pgcore separately preserves the observed compiled-core version.

The original project code and generated research data are covered by the repository's Apache 2.0 license. That license does not relicense dependencies.
