# Spec: standalone pyGIMLi reflection reproduction

Status: proposed on October 9, 2026. Awaiting approval for implementation and two bounded native state calculations. This spec introduces no executable code or new numerical results.

## Requirements & Goals

Prepare a small, independently runnable example for [pyGIMLi issue 979](https://github.com/gimli-org/pyGIMLi/issues/979). The example tests whether the published heterogeneous reflection discrepancy persists after extracting two measurement rows from the full survey pipeline.

The [saved P2 study](../experiments/ert-p2-contact-comparison/results/2026-10-09/RESULTS.md) already contains the two responses. A new standalone calculation is needed to establish that the smaller example reproduces them. That outcome is a hypothesis, not an established result.

Use one Python script, one frozen JSON input file, and a short README under `experiments/pygimli-reflection-reproduction/`. The script must run without installing OpenSubsurface, importing its modules, or reading other project files. Runtime dependencies are NumPy, pyGIMLi, and its pgcore distribution. Reuse Python 3.12, NumPy 2.5.3, pyGIMLi 1.6.1, and pgcore 1.6.0 for the local comparison. Do not change the existing environment or add packages.

Preserve the reported C mesh, all 64 sensors in their original order, material mapping, boundary labels, singularity removal, and direct native calculation path. Reducing the sensor list can change the native boundary center or source preparation. The example reduces measurement rows and project dependencies; it does not promise fewer source fields, lower mesh memory, or a speedup.

Exclude mesh sweeps, reduced sensor sets, changes to solver settings, operator instrumentation, exact-contact primary fields, corrections, hardware, and observability conclusions. Do not modify historical raw data or acceptance gates. Posting an issue comment or otherwise messaging maintainers is a separate action requiring Patrick's explicit authorization.

## Inputs, Outputs & Behavior

### Frozen inputs

Copy the published C x, y, and z axes numerically exactly into the input JSON. Record the original NumPy-file SHA-256 identifiers and the published source commit. Check these values against the existing raw-data registry before packaging. Copy the original 64 surface sensor coordinates without reordering. Include exactly these two ABMN rows, preserving their orientation and roles:

| Measurement | A | B | M | N | Original manifest index |
| --- | ---: | ---: | ---: | ---: | ---: |
| First | 26 | 36 | 52 | 62 | 3646 |
| Reflected | 29 | 35 | 51 | 57 | 3786 |

Their coordinates are:

| Electrode | First configuration, meters | Reflected configuration, meters |
| --- | --- | --- |
| A | `(-1.5,-4.5,0)` | `(-1.5,4.5,0)` |
| B | `(1.5,1.5,0)` | `(1.5,-1.5,0)` |
| M | `(7.5,1.5,0)` | `(7.5,-1.5,0)` |
| N | `(10.5,7.5,0)` | `(10.5,-7.5,0)` |

Use current 0.001 A, a flat surface at z=0, and the infinite contact at x=0. Run only H with 100 ohm m on both sides, followed by C100 with 100 ohm m on the left and 10,000 ohm m on the right. Retain all 64 valid sensors even though only two measurement rows are requested.

Frozen exact reference voltages are `-0.0006476359420855907 V` for both H rows and `-0.06000386265259415 V` for both C100 rows. Verify these against the existing analytical reference during development. Include the published C100 numerical responses `-0.05981245281773522 V` and `-0.059951241221804834 V` as historical comparison values, clearly separate from analytical truth and newly computed results.

### Calculation and local execution

1. Validate the input file before any native voltage calculation. Check finite, ordered axes, x and y reflection symmetry, the contact knot, all sensor locations, the full sensor order, valid distinct ABMN indices, and the stated reflection coordinates. Provide a validation-only command that performs no voltage calculation.
2. Build the original C linear grid with `pg.createGrid`, then call `createP2()` once. Verify 23,328 cells, 101,269 nodes, 20-node cells, unchanged cell geometry, no cell crossing x=0, and exact sensor nodes. Reapply outside boundary markers after `createNeighborInfos()`: -1 at the surface and -2 elsewhere. Verify 1,296 surface and 3,888 outer facets. Never rely on P2 inheriting material attributes.
3. Construct a two-row `DataContainerERT` with all 64 original sensors. Use a fresh `ERTModelling(sr=True)` operator per state. Assign resistivity after P2 construction, then follow the published sequence: `fop.data = scheme`, `setMesh(mesh, ignoreRegionManager=True)`, `mapERTModel(resistivity, 0)`, `calculate(DataMap)`, and direct `DataMap.data(scheme) * 0.001`. Verify native topology and material attributes. Do not enable reciprocal averaging or query the optional primary-mesh getter.
4. Run H first. Both absolute reference errors and the absolute reflected-pair difference must be <= `1e-12 V`. If H fails or returns invalid data, preserve the failure and skip C100.
5. If H passes, run C100 once. Record both signed voltages, exact-reference errors, and `V_reflected - V_first`. Compare each result with the corresponding published voltage using an absolute parity tolerance of `1e-9 V`. This is a declared reproduction tolerance, not a replacement accuracy gate.
6. Classify the published numerical discrepancy as reproduced only when H passes, both C100 rows match the published numerical values within `1e-9 V`, and the C100 pair difference exceeds `1e-6 V`. The historical difference is approximately 138.788 microvolt. If extraction changes a result beyond the parity tolerance, report that fact and leave the cause unresolved. Do not expand the script or rerun with the full 4,096 rows in this stage.

After approval, attempt at most two native state calculations, sequentially, within 30 minutes total accounted execution time and the existing 8 GiB monitored process limit. Count failed attempts. Reuse the existing resource monitor during local verification rather than building a new runner. The standalone script itself need not import that monitor. Keep its local stdout and output in an ignored directory while preparing the publication record. The monitor's sampled limit is not an operating-system memory guarantee.

The prior three-state C worker took about 93 seconds and peaked near 2.49 GiB in this environment. Those observations support the proposed budget but do not guarantee runtime or memory for the extracted example. Do not repeat native voltage calculations as part of unit-test repetition or routine CI.

### Outputs and interpretation

The standalone script prints the input identity, native build string, mesh and material checks, signed voltages, analytical references, pair differences, and reproduction decision. Save the same evidence to a requested fresh JSON output. Record distribution versions independently of `pygimli.__version__`, the script/input hashes, and installed binary hashes using distribution-relative names. Do not publish personal absolute paths or environment values containing credentials.

Publish the script, frozen inputs, README with exact commands, executed results, raw stdout, checksums, and a verification record. All required files must be usable after copying this directory outside the checkout into an environment with the stated runtime dependencies. Test that condition locally without depending on the checkout's current directory or Python import path.

A successful reproduction establishes a specific numerical self-consistency discrepancy on this setup. It does not identify a pyGIMLi bug or distinguish boundary assembly, primary construction, constraints, projection, and solver accuracy. A failed reproduction is also useful evidence and must be reported without changing tolerances or concealing values.

## Edge Cases & Error Handling

- Reject corrupt inputs, missing axes, reordered sensors, invalid indices, changed coordinates, or altered physical constants before solving. A checksum is provenance, not sufficient physical validation.
- Reject geometry, boundary, or material mismatches before the first native calculation. Structural checks may construct small native meshes but must not calculate voltages in routine tests.
- Reject nonfinite voltages or a result shape other than two rows. Preserve valid partial results and mark missing states explicitly.
- Refuse to overwrite an existing output file. A native exception, interruption, resource stop, or failed control cannot produce a successful reproduction decision.
- Label unsupported or unrecorded native diagnostics as unavailable. Do not interpret a successful solve or homogeneous control as heterogeneous continuum accuracy.
- If a maintainer requests another formulation, preserve this proposed scope and seek approval for the requested change before additional calculations.

## Acceptance Criteria

- [ ] The standalone directory contains one script, frozen inputs, and commands that work outside OpenSubsurface without project imports or dependencies on other result directories.
- [ ] Input provenance, all 64 sensors, both rows, references, axes, current, and states match the published record, with independent tests for literal coordinates and values.
- [ ] Native mesh, boundary, sensor-node, and explicit material checks pass before calculation, or a specific failure stops execution.
- [ ] No more than two sequential native state calculations are attempted. Failures, skips, execution time, and peak memory are recorded within the declared limits.
- [ ] H control and C100 parity/symmetry outcomes follow the declared rules. A non-reproduction is documented rather than turned into a success by changing inputs or tolerances.
- [ ] Machine-readable results, console output, build/binary provenance, and checksums agree with the actual executed artifacts. Published checksums account for Git text normalization.
- [ ] Development follows the standing test-first checkpoints. Record actual expected behavior failures before implementation. Include invalid-input, failed-control, nonfinite-output, incomplete-run, and positive-reproduction cases without native voltage reruns.
- [ ] Full pytest, zero-diagnostic Ruff checks including the standalone script, package build, and existing four CLI report recreations pass. Run validation-only standalone execution outside the checkout, and repeat cheap new tests five times.
- [ ] Update `FEATURE_MAP.md` when the capability is implemented. Commit relevant files and publish a human-review PR with auto-merge off.
- [ ] No hardware, new dependency, unapproved native variant, changed historical accuracy gate, or external message is introduced.
