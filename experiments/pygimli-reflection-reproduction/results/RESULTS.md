# Standalone reflection reproduction results

Executed October 9, 2026. The two-row standalone example reproduces the published heterogeneous discrepancy. This establishes that the full 4,096-row extraction pipeline is not required to observe it on the declared setup. It does not establish the numerical cause, a native-library bug, or accurate heterogeneous subsurface mapping.

| State | First voltage, V | Reflected voltage, V | Reflected minus first, V | Maximum difference from historical numerical values, V |
| --- | ---: | ---: | ---: | ---: |
| H, 100/100 ohm m | -0.0006476359420855688 | -0.0006476359420855683 | 4.336808689942018e-19 | 0 |
| C100, 100/10,000 ohm m | -0.05981245281773522 | -0.05995124122180487 | -0.0001387884040696466 | 3.469446951953614e-17 |

The exact H reference is `-0.0006476359420855907 V` for both rows. Its maximum absolute error is approximately `2.23e-17 V`, passing the `1e-12 V` homogeneous control.

The exact C100 reference is `-0.06000386265259415 V` for both rows. Numerical reference errors are approximately 191.410 and 52.621 microvolts. The reflected-pair difference has magnitude **138.788404 microvolts**, despite exact-reference invariance. Both numerical voltages pass the declared `1e-9 V` historical parity check, so the reproduction decision is `reproduced`.

## Physical and numerical setup

The surface is z=0, the material contact is x=0, and current is 0.001 A. All 64 original sensors retain their coordinates and order. The only measurement rows are `[26,36,52,62]` and `[29,35,51,57]`, corresponding to original indices 3646 and 3786. They reflect y without exchanging source and receiver roles or reversing within-pair orientation.

The copied C axes retain 23,328 cells. Explicit `createP2()` gives 101,269 nodes and 20-node cells. Cell geometry, contact alignment, exact sensor nodes, and the 1,296 Neumann surface and 3,888 mixed outer facets were checked before solving. Each state's explicit material array is checked against the native mesh before `calculate()`.

The operator path remains `ERTModelling(sr=True)`, direct `setMesh(..., ignoreRegionManager=True)`, `mapERTModel`, `calculate(DataMap)`, and signed `DataMap.data(scheme) * 0.001`. There is no reciprocal averaging, changed solver setting, or exact-contact primary field.

## Execution and provenance

Exactly two native state calculations completed, with no native repeats. The successful copied-directory run took approximately 21.846 seconds, including construction and monitoring setup, and peaked at 2,366,668,800 bytes, about 2.204 GiB. These are observations of this run, not a performance comparison or scaling guarantee.

A preceding startup attempt failed before either native state calculation because the local isolation helper also removed the virtual environment's dependency path. Only the helper's path filtering changed. The standalone script and frozen input hashes stayed identical. The preserved startup record reports zero state attempts and an inconclusive decision. Its time is included in the combined 21.859593-second execution ledger, below the approved 30 minutes. Both attempts were below 8 GiB.

The successful run used a copied two-file example outside the checkout and excluded project source paths from its import search. Runtime dependencies stayed in the existing virtual environment. Validation-only testing additionally blocks native and project imports to prove those are unnecessary for input validation.

Native build: `libgimli-v1.6.0-4-g9076db0e`. Distribution versions, native binary hashes, exact script/input identities, and source provenance are in [results.json](results.json). The Python-reported version is labeled separately. Algebraic residuals and actual reference-constraint diagnostics remain unavailable.

See [console.txt](console.txt), [resources.json](resources.json), [execution-accounting.json](execution-accounting.json), [startup-failure.json](startup-failure.json), and [startup-failure-resources.json](startup-failure-resources.json). The console capture preserves output content with LF line endings and a single final newline. The startup traceback remains local because it contains personal absolute paths; its machine-readable failure evidence is public. [artifact-sha256.json](artifact-sha256.json) verifies published Git bytes, accounting for text normalization.

The next scientific step is formulation or diagnostic guidance from pyGIMLi maintainers. This stage adds no mesh sweep, hardware recommendation, correction, or observability claim. No follow-up message has been sent upstream.
