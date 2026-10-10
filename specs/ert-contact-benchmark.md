# Spec: exact heterogeneous contact benchmark

Status: proposed for approval. The literature and [mathematical reference](../research/contact-reference.md) have been reviewed. No benchmark software has been implemented or run. This is a new diagnostic physical model, explicitly separate from the original sphere pilot.

## Requirements & Goals

Determine whether the existing three-dimensional pyGIMLi DC solver can reproduce an independently defined heterogeneous reference at the project's original voltage-error thresholds. Separate central mesh resolution from finite-domain extent without changing the interface representation.

The [benchmark review](../research/heterogeneous-benchmark-review.md) recommends a vertical contact because its image solution is closed-form and its plane can coincide exactly with mesh faces. The reference removes both curved-body volume aliasing and numerical series truncation from this diagnostic.

Hypothesis: the declared solver and configuration set can achieve normalized RMS <= 0.1 and maximum absolute discrepancy <= 0.25, with stable padding comparisons, within two hours of accounted worker time and 8 GiB peak process memory. A resource stop or failure to satisfy the full conditions yields an inconclusive numerical-validation outcome and falsifies this bounded feasibility hypothesis.

This stage includes reference evaluation, an adapter for prescribed cell resistivities, four controlled meshes, and reproducible reporting. It uses existing libraries and CPU execution. No new dependency, custom PDE solver, fitted sphere, geometry bank, nuisance search, classifier, adaptive policy, GPU accelerator, hardware purchase, or paid API is included.

Passing this contact benchmark cannot certify either one-sphere or two-sphere accuracy. The original results and thresholds remain unchanged. A later sphere stage requires a separately reviewed reference and scope.

## Inputs, Outputs & Behavior

### Frozen survey and new physical inputs

Keep the original 64 electrodes, 3 m spacing, 0.001 A source current, signed voltage convention, and 4,096-row candidate manifest. Require manifest SHA-256 `0b04f7711ccfb05c920d43e86f5c633d065eaba7e9fb089e6f90c6eca5a62b6a`.

The ground is the infinite flat half-space `z < 0`. An ideal infinite vertical interface at `x = 0` divides two isotropic media. Use the following three states:

| State | Left resistivity ohm m | Right resistivity ohm m | Purpose |
| --- | ---: | ---: | --- |
| H | 100 | 100 | Homogeneous convention control |
| C10 | 100 | 1000 | Heterogeneous contact |
| C100 | 100 | 10000 | Larger heterogeneous contrast |

Electrodes lie on both sides and none lies on the contact. Evaluate each source using the conductivity of its own side; the frozen manifest already includes sources and receivers in both media. Do not turn this contact into a finite buried wall, give it contact resistance, or add an air-conductivity layer.

Compute the independent Green function defined in the reference note and superpose poles for the signed ABMN voltage. Keep the evaluation scale fixed for every state:

`sigma_i = hypot(0.01 * abs(V_original_homogeneous_i), 1e-6)` volts.

This scale is a numerical tolerance convention, not newly simulated measurement noise. Do not renormalize it to the contact signal or drop configurations with small reference voltage.

### Controlled meshes

Use pyGIMLi's existing grid and ERT forward formulation with its usual homogeneous singularity treatment and existing Neumann surface/mixed outer boundaries. Record the effective primary-field convention and all internal forward-mesh refinements that can be inspected. Where a diagnostic is inaccessible, label it unavailable rather than inventing a value.

The fine core spans `[-12,12]` m horizontally and `[-12,0]` m vertically. The contact must coincide exactly with cell faces at `x = 0`. Build and save axis arrays as explicit experimental inputs:

1. Construct the coarse core with spacing 1.5 m and exact electrode nodes. Freeze its remote knots using the current graded-axis convention, grading ratio 1.5 and extent 64 m.
2. Construct the fine core by inserting the 0.75 m core nodes. Retain every coarse core node, electrode, and remote knot. Change no remote interval for this refinement.
3. Extend the coarse domain to 128 m by retaining every 64 m axis knot and adding outer knots from the same geometric progression, including the exact new boundary. Do not remove the old 64 m knot.
4. Insert the same fine core nodes into that extended axis set. The two fine meshes must share all knots inside the original 64 m domain.

| Mesh | Core spacing m | Extent m | Controlled comparison |
| --- | ---: | ---: | --- |
| A | 1.5 | 64 | Baseline |
| B | 0.75 | 64 | A to B changes core resolution only |
| C | 1.5 | 128 | A to C changes extent only |
| D | 0.75 | 128 | C to D changes core resolution; B to D changes extent |

Publish the full axis vectors and checksums. Assign conductivity by side on these face-aligned meshes. Assert that no cell straddles the contact and that all electrode positions remain exact. This parameterization deliberately avoids the earlier graded-axis coupling between central spacing and remote widths.

### Execution and reporting

1. Verify the analytical reference against the literal values and identities in the reference note. Use relative tolerance `1e-12` and absolute voltage tolerance `1e-14` V for literal values and homogeneous reduction. Check scaled potential continuity and normal-current identities to `1e-10` for sources `(-3,0,0)` and `(3,0,0)` at contact points `(0,0,0)`, `(0,2,0)`, `(0,0,-2)`, and `(0,2,-2)` in each state. Check reciprocity at all distinct frozen electrode pairs and zero surface-normal derivative at `(-1,1,0)` and `(1,1,0)`. Publish the normalization conventions and stop before native solves if these checks fail.
2. Construct one mesh at a time. Record mesh counts, geometry checks, construction resources, and library versions. Do not execute workers concurrently.
3. Solve H first on each mesh. Run C10 and C100 only when that mesh's H gate passes. Report skipped states explicitly if it fails. A passing H case is a control, not heterogeneous certification.
4. Limit the study to four meshes and three states, at most twelve native state solves. Each solve retains all 4,096 configurations; the 64 pole fields or equivalent native survey evaluation remain the source of those observations.
5. Record signed raw voltages, analytical references, fixed-scale residuals, maximum-error configurations, state-specific gates, resources, and failures. Report algebraic residuals where exposed separately from continuum error.
6. Report A/B and C/D core-refinement changes, and A/C and B/D extent changes for all completed states. Do not attribute simultaneous changes to a single cause.
7. Mark contact accuracy established for this survey only if D passes H, C10, and C100, B passes those same reference gates, and B/D discrepancies pass the same RMS and maximum thresholds. Coarse meshes may fail; report their errors without requiring them to validate a finer mesh whose exact-reference error is independently checked.
8. Otherwise report inconclusive with the failed or missing criteria. Do not expand the sweep to force a pass.

Use a two-hour cumulative worker budget and an 8 GiB process cap. Include mesh construction, reference verification, native solves, failed attempts, and a conservative development allowance in the ledger. Use the existing monitoring behavior and document native-call limitations. If an earlier projection leaves insufficient budget for a worker, skip it with a recorded resource decision.

Publish one standalone result directory with a frozen configuration, references, axes, raw arrays, checksums, resources, a status record, and a report reproducible from saved arrays. Preserve original pilot data. Keep full third-party papers in ignored local research output; publish links and original notes.

## Edge Cases & Error Handling

- Reject nonfinite or nonpositive conductivity, unsupported source geometry, and source/receiver coincidence. Require the analytic branch selection to handle sources on either side correctly.
- Treat a receiver's contact value as a one-sided limit used in formula verification. Exclude a source on the contact. The native frozen electrodes require neither special case.
- Reject a mesh with misplaced electrodes, a cell spanning the contact, or changes to frozen inner/remote knots that invalidate the controlled comparison.
- Keep zero and near-zero signed voltages. Use the fixed absolute noise floor rather than relative-voltage divisions or apparent-resistivity conversion.
- Stop or record a failed worker for nonfinite output, a library error, exhausted time, or exceeded memory. Preserve partial records and prevent overwriting accepted worker labels.
- Do not supply the exact contact field as a native primary field or exact outer-boundary values. Do not correct numerical outputs using the reference, empirical scaling, or a fitted calibration.
- Do not replace mixed boundaries with a different physical condition in this stage. Record a failed extent check as evidence for a later amendment.
- Do not claim cross-library agreement. pyGIMLi is compared with an independent analytical solution; SimPEG's failed homogeneous profiles remain published and are not rerun in this bounded study.
- A passing contact test leaves sphere/image coupling, curved geometry, two-body interaction, and acquisition robustness unresolved. No automatic continuation into those problems is included.

## Acceptance Criteria

- [ ] The contact reference is traced to the inspected original equations and passes the literal and physical-identity checks before native execution.
- [ ] The frozen electrodes, current, manifest hash, signed convention, and fixed tolerance scale match the original record.
- [ ] Three physical states and four explicit nested mesh-axis sets are published; contact alignment and electrode placement checks pass.
- [ ] Core-resolution and extent comparisons change only their stated factors, with saved axis vectors supporting that claim.
- [ ] At most twelve native state solves are attempted, sequentially, with heterogeneous states gated by their own mesh's homogeneous control.
- [ ] Raw analytical and numerical voltages reproduce the reported gates and comparisons; failed, skipped, and unavailable diagnostics are explicit.
- [ ] Success requires the stated B/D exact-reference and extent-stability criteria for all three states; otherwise the report is inconclusive.
- [ ] The two-hour and 8 GiB limits are monitored and the ledger includes failed/development work and monitoring limitations.
- [ ] Existing pilot tests and report reproduction still pass, and new verification checks address literal values, both source sides, units, interface identities, mesh invariants, stop behavior, and report recreation.
- [ ] No sphere-validation, physical-observability, mapping-resolution, acquisition-efficiency, or novelty claim exceeds this contact benchmark's evidence.
- [ ] The implementation and result are committed to a review branch and pull request, with auto-merge off.
