# P2 contact comparison results

Study date: October 9, 2026, America/Denver. These are approved synthetic CPU calculations, not field measurements.

**Diagnostic hypothesis: not supported. Contact accuracy: inconclusive.** P2 lowers the measured errors, but the RMS ratios fail the predefined `P2/linear <= 0.25` target at both extents. Every heterogeneous state still fails the original absolute accuracy gates, and the P2 extent comparison fails. All six declared native state solves completed; no additional variant was run after failure.

The [recomputed tables](TABLES.md), [summary](summary.json), and [reproduction guide](../../README.md) support these decisions.

## Frozen problem and controlled change

The original 64 surface electrodes, 0.001 A source, signed 4,096-row ABMN manifest, and exact vertical-contact reference are retained. The manifest SHA-256 remains `0b04f7711ccfb05c920d43e86f5c633d065eaba7e9fb089e6f90c6eca5a62b6a`. The tolerance scale remains `hypot(0.01 * abs(V_original_homogeneous), 1e-6)` V.

The material contact is `x = 0`. Left resistivity is 100 ohm m. Right resistivity is 100, 1,000, or 10,000 ohm m in H, C10, and C100. The independent [image solution](../../../../research/contact-reference.md) is evaluated for comparison, never supplied as the native contact primary field or boundary values.

Explicit `createP2()` changes each original 8-node hexahedral cell to a 20-node cell. Material cell count, centers, bounding extents, markers, interface alignment, and exact electrodes pass validation. The A/C axes and planar material geometry remain fixed. Resistivity is reassigned after refinement and verified on the native working mesh. The original Neumann surface and mixed outer-boundary labels are restored and checked.

| Extent | Material cells | Linear nodes | P2 nodes |
| --- | ---: | ---: | ---: |
| A, 64 m | 13,500 | 15,376 | 59,551 |
| C, 128 m | 23,328 | 26,011 | 101,269 |

Each state uses a fresh direct native operator. No managed H2 refinement, empirical correction, source-size change, material-interface displacement, covariance change, or threshold relaxation is included.

## Established numerical findings

Both homogeneous P2 controls pass, with normalized RMS below `3.7e-12` and maximum below `3.5e-11`. As in the earlier studies, this is a limited control because homogeneous secondary-field cancellation does not certify heterogeneous accuracy.

| Mesh | State | Linear RMS | P2 RMS | P2 maximum | RMS ratio | Maximum ratio |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| A | C10 | 52.2880 | 13.7223 | 703.5029 | 0.26243769 | 0.24877669 |
| A | C100 | 625.9220 | 164.6005 | 8471.2050 | 0.26297285 | 0.25004894 |
| C | C10 | 52.3130 | 13.6870 | 703.4465 | 0.26163740 | 0.24875180 |
| C | C100 | 626.1959 | 164.1968 | 8470.5316 | 0.26221322 | 0.25002407 |

The diagnostic requires both ratios <= 0.25 for both contact states at both extents. Every RMS ratio exceeds the limit. C100 maximum ratios also exceed it slightly. Rounding those values to 0.25 would incorrectly imply a pass. The criterion was fixed before the runs and remains unchanged.

The strict reference gates remain RMS <= 0.1 and maximum <= 0.25. Every contact state misses them by a large margin. An observed reduction is not accurate-voltage certification.

The [extent comparison CSV](extent-comparisons.csv) records the A-P2/C-P2 differences using the same fixed scale. Its contact cases fail the extent-stability gate. Increasing polynomial order therefore does not eliminate the remaining finite-domain sensitivity in this configuration set.

Native equation residuals remain unavailable from the adapter. The analytical checks, exact nodes, retained cells, and material-mapping checks pass; they do not identify or quantify every remaining source, integration, interpolation, and boundary approximation.

## Resource decision and limits

A-P2's observed peak was approximately 1.414 GiB. The approved squared-node-ratio rule projected C-P2 below the 8 GiB cap, so C was admitted. The recorded projection and its reconstruction are in `p2-worker-C.json` and the reporting code. It is a planning heuristic, not a proven bound.

The C worker took 92.689 s versus a 75.107 s projection. It still fit the remaining budget. This observation illustrates why the planning estimate cannot replace actual resource monitoring.

Peak accepted process memory was 2.492 GiB. Accounted preparation and worker time plus the 600 s development allowance totaled 715.357 s, below the 7,200 s cap. Every state completed without a resource stop. The [README](../../README.md) documents monitoring limitations.

These are single-run feasibility observations. No repeated performance experiment, GPU benchmark, or runtime speedup claim is made. Standard solver dependencies are unchanged. Development-only Ruff was added when replacement standing instructions introduced a lint gate during execution.

## Software verification and provenance

The new testing instructions arrived after the runner and reporter had been written and while C-P2 was executing. The [checkpoint record](VERIFICATION.md) distinguishes that chronology from the subsequent real test-first fix.

A corruption test showed that comparing cell-coordinate columns separately could accept duplicate/missing joint three-dimensional positions. The test failed with `DID NOT RAISE`, and the report now compares complete coordinate tuples. This strengthens evidence validation. It does not change the executed native voltages or the scientific acceptance thresholds.

Fundamental arrays have published checksums. Linear baseline arrays are copied byte-for-byte. The environment records native build and binary identities separately from Python-reported version strings, plus the executed project source hashes. Historical records retain their original metadata. No credentials, local logs, or downloaded third-party source are part of the publication.

## Hypotheses and next decision

The observed reduction supports field-discretization error as one contributor, but the specific fourfold-reduction hypothesis is not supported by this dataset. Neither the reduction nor the source review proves a complete root cause for the remaining discrepancy.

Contact accuracy remains unestablished, and sphere accuracy remains unverified. These results do not establish a physical observability limit or an acquisition-efficiency gain.

The next recommendation is an independent geophysical review of the error budget and secondary-field/boundary formulation before adding another benchmark sweep. The current evidence does not justify hardware purchases or expansion into the geometry and nuisance bank.
