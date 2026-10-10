# Numerical validation results

Study date: October 8, 2026, America/Denver. Some timestamps fall on October 9 in UTC. These are synthetic CPU simulations, not field measurements.

**Scientific outcome: inconclusive.** No tested SimPEG configuration passes the unchanged homogeneous accuracy gate. pyGIMLi passes its analytical homogeneous checks, but the same four inclusion geometries remain sensitive to mesh refinement. Independent inclusion agreement has not been established. The geometry bank, nuisance search, and adaptive acquisition experiment remain unrun.

The [generated tables](TABLES.md), [summary](summary.json), raw voltage arrays, and saved fitted meshes support this decision. The [reproduction guide](../../README.md) and [commands](commands.ps1) describe how to inspect and rerun the evidence.

## Frozen assumptions and acceptance criteria

The source current is 0.001 A, the background resistivity is 100 ohm m, and all 64 electrodes lie on a flat surface with the original 3 m spacing. The homogeneous reference is the analytical infinite half-space solution. Numerical meshes truncate the domain and use each library's documented outer-boundary treatment. Finite-domain errors remain an experimental factor.

The 4,096 configurations retain manifest SHA-256 `0b04f7711ccfb05c920d43e86f5c633d065eaba7e9fb089e6f90c6eca5a62b6a`. The mathematical point sources, geometry catalog, units, and assumed measurement covariance are unchanged. No empirical voltage correction is applied.

For each configuration, the fixed scale is `sigma_i = hypot(0.01 * abs(V_analytic_i), 1e-6)` volts. The normalized discrepancy is `(V_numeric - V_reference) / sigma_i`. Passing requires RMS <= 0.1 and maximum absolute discrepancy <= 0.25 over all configurations. Inclusion mesh comparisons use this same fixed background scale; they do not represent observed measurement noise or geometry-discrimination performance.

## Established findings from these runs

### Source handling passes the tested audits

The baseline tree mesh has zero coordinate-interpolation error and zero unit-source injection-sum error. Its maximum reciprocity discrepancy at 1 mA is approximately `1.49e-12` V. Eight directly simulated dipoles agree with pole-source superposition within `1.18e-12` V.

These measurements argue against an injection, unit, interpolation, or superposition defect in the tested configuration. The eight dipoles are a spot check, not an exhaustive test of every alternative discretization. Streamed source batches also reproduce the full-source solve in a real solver test.

All recorded SimPEG maximum relative equation residuals are below `1e-8`, approximately `4.9e-11` to `1.0e-10`. Those are residuals of the discretized equations. They do not measure agreement with the continuum reference. The pyGIMLi adapter does not expose an equivalent equation-residual diagnostic; it is reported as unavailable.

### Refinement helps but does not validate SimPEG

The default tree mesh has normalized RMS 2.083 and maximum 36.31. The graded tensor mesh at 0.5 m has RMS 1.112 and maximum 23.85. Halving its central cell size to 0.25 m reduces the maximum to 6.586, but still fails both thresholds.

Changing tensor padding from 64 to 128 m while retaining grading and central resolution does not improve this case. Changing grading from 1.5 to 1.2 improves RMS to 0.866 but leaves the maximum at 23.53. Expanding the fine core independently also leaves a large maximum discrepancy. Padding, grading, and local resolution cannot be treated as interchangeable.

Broad graded refinement around electrodes produces the best tested tree RMS, 0.2261, and maximum, 2.1664. Adding a finer innermost level changes them to 0.2262 and 2.1666. Both configurations fail. This plateau contradicts the premise that reducing the innermost source cell size alone will resolve the error. It does not isolate every remaining boundary, grading, or discretization contribution.

The electrode-role census and residual correlations are published. Canonicalization gives uneven role counts; those counts are not evidence that a particular electrode causes the error.

### Analytical singularity removal makes the homogeneous check limited

The independent pyGIMLi homogeneous RMS is approximately `2.6e-13`. pyGIMLi uses an analytical primary field with singularity removal in this setup. An exact homogeneous result therefore checks conventions and the primary field, while providing little evidence about accuracy of the heterogeneous secondary response. The [library documentation](https://www.pygimli.org/pygimliapi/_generated/pygimli.physics.ert/) describes this formulation.

This is an established numerical technique. [Li and Spitzer (2002)](https://doi.org/10.1046/j.1365-246X.2002.01819.x) compare finite-element and finite-difference DC modelling and discuss singularity treatment. [Rucker, Gunther, and Spitzer (2006)](https://doi.org/10.1111/j.1365-246X.2006.03010.x) describe three-dimensional DC modelling with topography. This project does not claim novelty for singularity removal, graded meshes, or fitted finite elements.

### Coarse geometry assignment changes the scientific question

Exactly four existing catalog geometries were evaluated with pyGIMLi, after each applicable homogeneous gate passed:

| Identifier | Geometry | Depth m | Resistivity contrast |
| --- | --- | ---: | ---: |
| `h1-ba32b0c77ef15679` | One sphere | 3 | 10 |
| `h1-f8fa2489359b0830` | One sphere | 7 | 100 |
| `h2-996eccf7a825f5aa` | Two spheres, 3 m center separation, orientation 0 | 3 | 100 |
| `h2-83c81c35bdbb7ddf` | Two spheres, 3 m center separation, orientation 0 | 7 | 10 |

Every geometry has nominal total volume 14.13717 m3. At 0.75 m grid spacing, cell-center assignment represents 13.5, 16.875, 6.75, and 10.125 m3 respectively. The shallow two-sphere case loses approximately 52% of its intended volume. At 0.5 m, the corresponding volumes become 17, 17, 14, and 14 m3. Comparing those responses as an equal-volume topology experiment would confound topology with discretized volume.

Changing only the horizontal fine-core extent passes the four response comparisons at 0.75 m. Changing cell size from 0.75 to 0.5 m fails all four. The largest normalized maximum discrepancy is 24.35.

### Fitted geometry improves volume agreement but response convergence still fails

The follow-up uses pyGIMLi sphere geometry, SciPy surface triangulation including exact electrode nodes, and TetGen's existing array mesher. pyGIMLi remains the PDE solver. This avoids an incompatible older filename bridge and free surface nodes that created invalid mesh intersections. Early failed mesh-construction attempts produced no accepted voltage results; the budget includes an explicit development allowance.

Sphere surfaces are faceted approximations. At 24 segments and 12 rings, represented volumes are approximately 13.7381 m3. At 48 segments and 24 rings they are approximately 14.0365 m3. Finer surfaces reduce volume error while retaining matched volumes across the one-sphere and two-sphere cases. The table records each value, including the 64-segment comparison.

The initial 24-to-48 comparison changes both facets and the target interior tetrahedron volume. Two subsequent comparisons separate these factors: 48 segments with target volume 0.025 versus 0.01 m3, and 48 versus 64 segments with target volume fixed at 0.025 m3. All four geometries fail the maximum-discrepancy threshold in both comparisons. Mesh agreement has not been demonstrated, even within one library. A smaller volume error is not proof of accurate voltages.

The cell counts in metadata describe the input mesh; pyGIMLi may internally refine the forward mesh. Fitted-mesh records inherit common adapter settings, but their active mesh controls are domain extent, sphere segments/rings, and regional tetrahedron-volume constraints. Tensor/tree and central-grid settings apply to the other adapters.

## Resource and provenance limits

The ledger, reproduced in `summary.json`, counts worker wall time, homogeneous replay, and a ten-minute allowance for uninstrumented development and failed early attempts. It remains below the four-hour limit. Two early probes overlapped; their times are counted separately. These records describe feasibility on this machine and are not repeatable performance benchmarks.

The largest accepted recorded process peak is 7.301 GiB. The finest fitted-mesh suite remains below 6 GiB. The [README](../../README.md) explains sampling and native-call limitations. A source-batch cache issue discovered during development was fixed by using fresh library simulation instances; real batch-versus-full tests verify the fix.

No GPU performance measurement is included. Python 3.12 and pinned distribution versions are recorded. Native meshing can differ across builds, so exact regenerated meshes are not guaranteed byte-for-byte identical. Saved meshes and raw arrays preserve the published evidence. The original manifest hash remains exact.

## Plausible hypotheses

The SimPEG plateau suggests that the spatial support and transition of refined source regions matter alongside innermost resolution. A formulation with analytical singularity treatment may be more efficient for these sources, but the homogeneous pyGIMLi result alone cannot establish that claim for inclusions.

The fitted-mesh discrepancies suggest that secondary-field resolution outside the bodies, boundary truncation, and surface representation deserve separate checks. The current experiment does not identify a single remaining cause. More local refinement without an independent reference would risk repeating the same premise.

## Speculation and next decision

It remains speculative that nuisance-aware adaptive acquisition will recover the intended one-body versus two-body distinction more cheaply. These runs provide no physical observability limit and no acquisition-efficiency result.

The recommended next research step is to identify a published heterogeneous DC benchmark with an independently reproducible reference. Then define a small amendment that separately checks secondary-field mesh resolution and outer boundaries against that reference. Establish accuracy before enlarging the geometry bank. Retain the frozen four-case results as failure evidence. No hardware purchase is justified by this stage.
