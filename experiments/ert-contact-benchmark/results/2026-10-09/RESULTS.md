# Exact-contact benchmark results

Study date: October 9, 2026, America/Denver. Status: approved experiment executed. These are synthetic CPU voltages, not field measurements.

**Scientific outcome: inconclusive.** All four meshes pass the homogeneous reference check. Every heterogeneous state fails the unchanged exact-reference thresholds. The fine-mesh extent comparison also fails. The declared configuration set therefore does not establish accurate contact responses, and it provides no validation of the original sphere responses.

The [recomputed evidence tables](TABLES.md), [summary](summary.json), and [reproduction instructions](../../README.md) support this decision. The study ran exactly the approved four meshes and three states, without adding variants after observing failure.

## Model, independent reference, and checks

The contact is the infinite vertical plane `x = 0` in an insulating flat-surface half-space. Left resistivity is 100 ohm m. Right resistivity is 100, 1,000, or 10,000 ohm m for states H, C10, and C100. The original 64 electrodes, 3 m spacing, 1 mA current, and 4,096 signed ABMN configurations remain frozen.

The manifest SHA-256 is `0b04f7711ccfb05c920d43e86f5c633d065eaba7e9fb089e6f90c6eca5a62b6a`. No empirical correction or analytical contact field was supplied to the native solver.

The [independent reference](../../../../research/contact-reference.md) restates the image solution in [Van Nostrand and Cook (1966)](https://pubs.usgs.gov/pp/0499/report.pdf), printed pages 52-53, equations 21-23. Literal pole and signed-dipole values pass the declared tolerances. Equal-conductivity reduction, reciprocity across all distinct electrodes, potential continuity, normal-current continuity, and surface insulation checks pass. The largest recorded scaled interface identity error is below `9e-15`.

The fixed scale is `hypot(0.01 * abs(V_original_homogeneous), 1e-6)` V in every state. Reference-error and mesh-difference gates require normalized RMS <= 0.1 and maximum <= 0.25. This is a numerical error budget; no measurement noise realization was added. Zero and near-zero background voltages remain included.

All input mesh cells lie wholly on one side of the contact. The interface coincides with faces, and every electrode is an exact mesh node. Published axis arrays verify that core refinement retains remote intervals and that extent extension retains all old knots. This separates the two experimental factors and removes curved-body volume aliasing from this diagnostic.

## Established numerical findings

| Mesh | Core spacing m | Extent m | C10 RMS | C10 maximum | C100 RMS | C100 maximum |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 1.5 | 64 | 52.288 | 2827.849 | 625.922 | 33878.188 |
| B | 0.75 | 64 | 10.450 | 553.945 | 125.035 | 6636.373 |
| C | 1.5 | 128 | 52.313 | 2827.905 | 626.196 | 33878.865 |
| D | 0.75 | 128 | 10.441 | 554.002 | 124.943 | 6637.052 |

Homogeneous normalized RMS values are below `8.1e-13`. As in the previous stage, native analytical singularity treatment makes this a limited control rather than evidence of heterogeneous accuracy.

Refining only the core reduces the contact errors substantially. Extending only the domain changes the overall errors much less, and it does not bring any heterogeneous configuration through the reference gate. These are accuracy changes, not runtime speedups.

For B versus D, the normalized extent-change RMS and maximum are approximately 0.994 and 11.251 for C10, and 11.526 and 129.829 for C100. Those comparisons also fail. The data do not justify treating outer-domain effects as negligible at the project's tolerance.

On mesh D, the worst C10 error is approximately 0.554 mV and the worst C100 error approximately 6.637 mV. Both occur at a configuration whose fixed background scale is 1 microvolt. Reporting only a typical percentage error or omitting low-background configurations would hide this failed requirement.

## Native formulation and diagnostics

The adapter uses the same public pyGIMLi ERT modelling operations as `ert.simulate(..., calcOnly=True, sr=True)`: mesh assignment, cell-resistivity mapping, native calculation, and signed DataMap voltages. It exposes the operator to record diagnostics rather than modifying the PDE. Sources remain mathematical surface points; boundaries remain the existing Neumann surface and mixed outer boundaries.

Input, operator, and exposed core mesh counts match for every recorded state. The native primary-potential matrix has 64 rows and one column per exposed mesh node. No increased internal mesh count was observed along this calculation path. The `primaryMesh` getter did not provide a usable mesh object, and that diagnostic is marked unavailable. Equation residuals are also unavailable from this adapter and are not imputed from reference agreement.

The inspected [upstream C++ implementation](https://github.com/gimli-org/pyGIMLi/blob/main/core/src/bert/dcfemmodelling.cpp) constructs an analytical primary field and scales it using source-local material attributes during the secondary solve. The reviewed source blob was `85c45fa7c16162a0df155a125c1850f97d69785c`. This source review describes the upstream convention; it is not proof that every detail matches the installed compiled build. Distribution and runtime identifiers are published in the environment record.

No exact contact field was used as native primary potential or boundary data. No contact-resistance, air-layer, source-size, covariance, or threshold changes were made. SimPEG was not rerun; its earlier failed homogeneous checks remain part of the project record.

## Resources and reproducibility

All twelve native state solves completed sequentially. Worker durations summed to approximately 50.321 s. Preparation added approximately 0.392 s. With the conservative 600 s development allowance, accounted time is 650.713 s, below the 7,200 s cap. Peak recorded process memory is 3.695 GiB, below 8 GiB. No worker approached the remaining time limit, and none was omitted for resources.

These are single-run observations on the recorded Windows/Python environment. No controlled performance comparison or GPU benchmark was run. The runtime numbers do not establish a repeatable speedup or a universal cost bound.

The code verifies the reference before native work, prevents worker overwrites, and blocks continuation after a resource stop. The [README](../../README.md) describes native-call monitoring limitations. Raw voltage and axis checksums, the frozen manifest, source hashes, and a report that recreates the metrics are published. Full logs and downloaded third-party source remain local.

## Hypotheses and next research decision

The declared hypothesis is falsified for this four-mesh configuration set: it fails the stipulated heterogeneous accuracy and extent-stability criteria despite fitting the resource budget. This does not show that the solver can never achieve those criteria.

The response to core refinement supports investigating discretization of the heterogeneous secondary field and the library's forward-mesh refinement path. Extent sensitivity remains another factor. Neither observation identifies a single cause, and no alternative element-order or primary-field variant was tested here.

The next recommendation is a focused review of native refinement and secondary-field assembly before proposing any further runs. A finite-contrast sphere reference still needs its own audited formulation and convergence bound. Contact failure is not evidence of a physical observability limit, and hardware purchases, geometry classification, and adaptive-acquisition claims remain unjustified by these results.
