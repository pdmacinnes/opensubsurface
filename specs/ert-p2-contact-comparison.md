# Spec: explicit P2 contact comparison

Status: proposed for approval. The [source and construction review](../research/native-solver-review.md) is complete. No P2 contact voltage solve has been implemented or executed.

## Requirements & Goals

Test whether increasing the field approximation order on fixed material cells reduces the heterogeneous error in the completed contact benchmark. Use pyGIMLi's existing `createP2()` and native DC calculation. Do not introduce a custom finite-element solver or silently select region-managed material mapping.

The installed direct path does not automatically create a refined forward mesh. Tiny structural probes confirm that P2 changes 8-node hexahedral cells into 20-node cells while retaining tested cell centers and markers. It does not retain cell attributes. Material assignment after construction is a required part of the experiment.

Diagnostic hypothesis: P2 reduces both normalized RMS and maximum reference error to at most one quarter of the corresponding published linear-element error for C10 and C100 on both A and C. This fourfold target is a project hypothesis, not a convergence theorem or a relaxed accuracy threshold.

Contact accuracy remains a separate claim. It requires the unchanged RMS <= 0.1 and maximum <= 0.25 gates for all states on both P2 meshes, plus their extent-difference gate. A successful reduction alone does not validate the solver for the declared survey.

Limit this stage to two P2 configurations and at most six native state solves, sequentially, under a two-hour accounted worker budget and 8 GiB process cap. No new dependency, additional mesh variant, H2 sweep, boundary change, exact-contact primary field, GPU backend, hardware, nuisance analysis, classifier, adaptive acquisition, or sphere work is included.

## Inputs, Outputs & Behavior

### Frozen physical and statistical inputs

Reuse the [published contact record](../experiments/ert-contact-benchmark/results/2026-10-09/RESULTS.md). Retain the 64 electrodes, 0.001 A current, signed measurement convention, and 4,096-row manifest with SHA-256 `0b04f7711ccfb05c920d43e86f5c633d065eaba7e9fb089e6f90c6eca5a62b6a`.

Reuse the exact vertical-contact reference and its literal/physical checks. Left resistivity remains 100 ohm m. Right resistivity is 100, 1,000, or 10,000 ohm m for H, C10, and C100. The fixed scale remains `hypot(0.01 * abs(V_original_homogeneous), 1e-6)` V.

Use the previously saved A axes at 64 m extent and C axes at 128 m extent. The linear baselines are their published raw voltages; do not rerun them or replace them with the B/D fine-core meshes.

### Controlled polynomial refinement

Construct the original linear grid from each frozen axis set and call its existing `createP2()` method once. Keep the original material cells and planar interface. Do not create additional subcells or enable automatic managed H2 refinement.

Before calculation, verify:

- The material cell count, cell centers, and contact faces agree with the corresponding original grid. Check cell correspondence explicitly rather than assuming an array order.
- Every cell has 20 nodes, and no cell spans `x = 0`.
- The source/receiver locations remain exact nodes and the surface remains flat at `z = 0`.
- Boundary labels are reassigned through the same existing surface Neumann/outer mixed convention after P2 construction.
- Resistivity is assigned explicitly after construction from the declared physical side. No inherited zero or stale attributes are accepted.

Record topology, node counts, centers, boundary labels, and material correspondence. For a regular grid, the expected P2 node count is the original vertex count plus the counts of edges in the three coordinate directions. For the saved axes this gives 59,551 nodes on A and 101,269 on C. Those are geometric counts, not memory or solve-time guarantees.

Keep the direct `setMesh(..., ignoreRegionManager=True)` calculation path. Create a fresh native operator per state. Keep homogeneous analytical singularity treatment, source-local scaling, and the existing boundary assembly. Do not supply the exact contact field or empirical corrections to the native solver.

### Gating and resource sequence

1. Verify all original raw checksums, survey constants, analytical identities, and baseline metrics before native work. Capture distribution versions, native build string, extension/library hashes, and installed Python source hashes. Label the Python-reported version separately.
2. Build A-P2 and verify its geometry/material correspondence. Run H first under resource monitoring. If H fails, stop this comparison and record the remaining cases as skipped.
3. If H passes and sufficient budget remains, run A-P2 C10 and C100. A failed heterogeneous accuracy gate does not authorize an extra mesh or a correction.
4. Before C-P2 native work, assess resources using A-P2 observations and the actual proposed node count. Use `1.25 * peak_A_bytes * (nodes_C / nodes_A)^2` as a conservative planning heuristic. If it exceeds 8 GiB, record C-P2 as skipped. This heuristic is not a mathematical memory bound; retain the process monitor.
5. Estimate the C-P2 worker duration with the same `1.25 * (nodes_C / nodes_A)^2` multiplier applied to completed A-P2 worker time. Skip it if the remaining budget cannot cover that estimate. Include construction and checks in the ledger.
6. If resource planning permits C-P2, construct it, check correspondence, and solve H before its two contact states. If its H gate fails, skip its contact states. Do not retry failed native cases with different solver settings or another mesh family.
7. Publish signed raw voltages, independent references, fixed-scale residuals, native diagnostics, failures/skips, and complete resource accounting. Record algebraic residuals where exposed; otherwise mark them unavailable. Avoid querying the absent optional primary-mesh pointer.

Use a ten-minute development allowance within the two-hour ledger and account for failed attempts. Capture worker records before native execution and preserve partial records. The existing monitored-cap limitations apply; no operating-system hard memory isolation is claimed.

### Evaluation and outputs

Recompute linear and P2 reference errors independently from saved arrays. Compare A to A-P2 and C to C-P2 as polynomial-order changes. Compare A-P2 to C-P2 as an extent change. Do not mix core resolution, domain extent, and polynomial refinement in a single attribution.

Report the diagnostic hypothesis as supported only if both RMS and maximum P2/linear error ratios are <= 0.25 for C10 and C100 at both extents, with complete valid runs. Missing cases yield inconclusive evidence rather than an imputed reduction.

Report contact accuracy established only if H, C10, and C100 pass the original exact-reference gates on both P2 meshes and their mutual extent differences also pass. Otherwise contact accuracy remains inconclusive, even if the diagnostic reduction target succeeds. State exactly which outcome failed or remains missing.

Publish a standalone result directory with frozen input provenance, P2 topology/material checks, raw voltages, reference values, checksums, version/build metadata, resources, and a report recreated from saved evidence. Preserve the original twelve-state results and their execution-source hashes.

## Edge Cases & Error Handling

- Reject any change to the original axes, source conventions, physical material values, manifest, reference, or fixed tolerance scale.
- Do not assume `createP2()` preserves cell attributes. Remap and check materials explicitly before solving.
- If cell correspondence, element type, boundary labels, exact electrodes, or interface alignment cannot be verified, stop before native calculation.
- If the installed native solver does not support the refined element path, report that failure. Do not switch to tetrahedra, a different PDE formulation, or a new library in this stage.
- Stop or skip on memory/time planning limits and actual resource stops. Do not overwrite or rerun accepted/attempted worker labels.
- Keep near-zero background configurations and use the original absolute floor. Never hide large maximum errors behind aggregate percentages.
- Treat optional missing diagnostics and unavailable equation residuals as unavailable, not favorable outcomes.
- A dynamic Python version derived from the project checkout is not native provenance. Record the independent core build identifier and binary hashes.
- A passing polynomial diagnostic or contact benchmark still leaves sphere geometry, sphere/image coupling, two-body interaction, and acquisition uncertainty unresolved.

## Acceptance Criteria

- [ ] Original raw data, baseline errors, manifest, electrode/current constants, reference identities, and tolerance scale verify before native work.
- [ ] Two P2 configurations are declared; every constructed mesh retains the original A/C material geometry and passes correspondence, boundary, electrode, and element checks. Skipped construction is explicit.
- [ ] Resistivities are explicitly mapped after refinement and verified; inherited attributes are never trusted.
- [ ] At most six state solves are attempted sequentially, with homogeneous gates and documented resource planning/stop decisions.
- [ ] Time and peak-memory records satisfy the two-hour and 8 GiB limits for accepted runs, including construction, failed work, and the development allowance.
- [ ] All numerical-error and P2/linear ratios recreate from raw arrays; missing or failed cases remain explicit.
- [ ] Diagnostic error reduction and strict contact accuracy have separate, unambiguous decisions under the stated criteria.
- [ ] Polynomial-order comparisons and extent comparisons preserve their declared independent factors.
- [ ] Native build/source/binary provenance is recorded separately from Python-reported version strings.
- [ ] No unsupported sphere, observability, performance-speedup, acquisition-efficiency, or novelty claim is made.
- [ ] Existing study tests/reports still reproduce, and new checks cover material correspondence, lost attributes, element counts, budget skips, and report decisions.
- [ ] The approved implementation and results are committed and published through a human-review PR with auto-merge off.
