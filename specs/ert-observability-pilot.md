# Spec: ERT observability pilot

Status: proposed for approval. No implementation, simulation, or hardware purchase has begun.

This is a bounded feasibility study preceding the [broader adaptive acquisition experiment](../research/first-experiment.md). The [focused prior-art review](../research/prior-art-review.md) records why it does not claim a new design principle.

## Requirements & Goals

Determine whether one resistive sphere and two separated resistive spheres of equal total volume produce distinguishable surface ERT responses under a declared numerical model.

The pilot must separate the optimistic known-model case from ambiguity caused by nuisance uncertainty. It must expose numerical error before interpreting small signal differences.

The scientific outcome may be informative, ambiguous, or inconclusive. Completing the pilot is not the same as obtaining a positive result.

The pilot uses existing open-source solvers. SimPEG is the primary candidate and pyGIMLi is the independent check. Pin versions and record their licenses when implementation is approved.

No adaptive policy, learned reconstruction model, custom PDE solver, paid API, field measurement, or procurement is included. The twofold acquisition-efficiency hypothesis remains a later research target.

The normal implementation plan is:

1. Validate a homogeneous reference response and numerical convergence.
2. Produce a fixed candidate-measurement manifest.
3. Simulate the small matched geometry catalog.
4. Compute noise-scaled differences and optimistic discrimination diagnostics.
5. Search a declared finite nuisance bank for opposing explanations.
6. Check representative cases with an independent solver.
7. Publish observations, verification evidence, costs, and the next research decision.

## Inputs, Outputs & Behavior

### Coordinates and electrical properties

Use metres, amperes, volts, siemens per metre, and ohm metres. Cartesian z increases upward, the flat ground is z = 0, and depth d is positive downward.

The 64 electrodes have x and y coordinates in {-10.5, -7.5, -4.5, -1.5, 1.5, 4.5, 7.5, 10.5} m and z = 0. This is a 21 m surface aperture.

The primary background is homogeneous and isotropic, with resistivity 100 ohm metres. The resistive inclusion has resistivity K times the background, where K is 10 or 100.

Use point electrodes with a prescribed current of 1 mA for the initial normalized-current study. This is a mathematical source assumption, not demonstrated instrument capability. Point-source singularities cannot establish finite-electrode voltage compliance.

Treat the subsurface as an open half-space. Use appropriate numerical padding and air or surface boundary treatment for each solver. The 12 m depth of the region of interest is not a reflecting or insulating bottom boundary.

### Matched geometry catalog

H1 is a sphere with radius 1.5 m centered at (0, 0, -d).

H2 comprises two spheres with radius 1.5 divided by the cube root of 2, approximately 1.19055 m. Their centers are displaced by plus or minus s/2 from (0, 0, -d) along a horizontal direction theta.

This gives H1 and H2 the same total anomalous volume and the same resistivity contrast.

| Variable | Values |
| --- | --- |
| Center depth d | 3, 5, and 7 m |
| Contrast K | 10 and 100 |
| H2 center separation s | 3 and 5 m |
| H2 horizontal orientation theta | 0 and 90 degrees |

The catalog contains 24 matched pairs. H1 repeats across separation and orientation, so there are six distinct H1 models and 24 distinct H2 models. Reuse repeated calculations after verifying their identifiers.

The minimum H2 surface-to-surface separation is approximately 0.619 m. All models remain below ground and within the central survey footprint.

The task distinguishes this restricted family. It does not establish recovery of arbitrary connectivity, cavity identity, or general geology.

### Candidate survey manifest

Use 4,096 unique four-electrode configurations. All four electrode indices must differ.

Canonicalize current-pair ordering, potential-pair ordering, and reciprocal duplicates under the ideal linear reciprocal model. Preserve a documented sign convention.

Sample configurations without replacement using a fixed published seed of 20261008. Sort the selected canonical entries lexicographically. Record the generator, its pinned version, and the final manifest hash.

Fix the manifest before simulating targets. Do not select configurations using the hidden geometry.

Use the same manifest for every model. Include broad array directions through unbiased sampling, and report the actual direction and source-pair distribution.

Candidate configurations are not independent spatial measurements. Response reuse through superposition is established prior art. Noise and cost must reflect the actual measurement procedure rather than independent noise added to reused synthetic basis potentials.

For this first pilot, every listed voltage difference is one hypothetical sequential acquisition with independent receiver noise. This idealized model does not claim multichannel, shared-electrode, or correlated-field error realism. Report unique current pairs and the number of hypothetical commands.

A later repeat-acquisition or multichannel design requires a separate covariance and cost model.

### Noise scenarios

Let V_bg,i be the predicted homogeneous-background voltage for candidate i. For the optimistic paired-model diagnostic, use a common diagonal covariance with

sigma_i squared = (eta times abs(V_bg,i)) squared + u0 squared.

Use eta values of 0.01 and 0.03. Use u0 values of 1, 10, and 100 microvolts. This produces six declared noise scenarios.

The same covariance is used for both hypotheses in a given pair. This permits the Gaussian diagnostic below. These are assumed noise floors rather than measured specifications.

Retain signed voltages. Do not take logarithms of nonpositive values or normalize away the absolute noise floor.

The primary statistical assumption is independent zero-mean Gaussian receiver noise. Correlated gain, drift, failed electrodes, contact effects, and current compliance remain required later studies.

### Optimistic discrimination diagnostic

For a paired response difference delta and common covariance Sigma, compute

D squared = delta transposed times inverse(Sigma) times delta.

For two fully known Gaussian hypotheses with equal prior probability and common covariance, the optimal classification error is Phi(-D/2). The distance corresponding to 90% accuracy is approximately D = 2.563.

This is a derived diagnostic under stated assumptions, not evidence from the literature or a guarantee of practical classification.

Report D and the corresponding error for all 24 pairs and all six noise scenarios. Report single-configuration contributions as well as the complete-pool value.

The known-hypothesis result is optimistic. Unknown position, contrast, background, noise, and physical-model error may reduce useful discrimination.

For this fixed acquisition pool with at most one observation per configuration, poor complete-pool discrimination limits subset discrimination under the same assumptions. It does not rule out repeat measurements, new configurations, additional sensors, or other measurement physics.

### Finite nuisance search

After the matched-model calculation, consider opposing-hypothesis alternatives with:

- background resistivity in {80, 100, 125} ohm metres;
- horizontal x displacement in {-1.5, 0, 1.5} m;
- center-depth displacement in {-0.5, 0, 0.5} m.

Keep y unchanged and retain the catalog's radius, separation, orientation, and contrasts. This gives at most 27 alternatives per opposing catalog model. Deduplicate repeated physical models.

Use the primary pair's declared covariance when comparing an alternative with its reference truth. Publish this convention and the dependence on the reference noise scenario.

Report the closest opposite-hypothesis candidate and its noise-scaled distance in both truth directions.

A low-distance alternative is constructive evidence of ambiguity within the evaluated assumptions. A high minimum over this finite bank is not a lower bound over all possible ground models.

This is a diagnostic search, not marginalized Bayesian inference or a classifier using unknown nuisance parameters. Do not present its distances as achieved inference accuracy.

Layered or irregular ground is outside this first bank. Explicitly retain it as an outstanding robustness test.

### Numerical verification and cost controls

Use the analytic flat homogeneous half-space response with the documented sign convention to check the implementation.

For each solver, refine the mesh and enlarge the padded domain independently. Use representative shallow and deep models from both hypotheses and a high-contrast case.

Normalize numerical differences using the 1 microvolt, 1% covariance. Require root-mean-square normalized discrepancy at most 0.1 and maximum normalized discrepancy at most 0.25 on checked configurations.

Compare independent solvers on at least four representative distinct models covering H1, H2, shallow, deep, and high contrast. Use the same thresholds for matched physical assumptions.

Solver convergence or solver agreement must not be inferred from similar images. Publish per-configuration differences and mesh settings.

First profile a homogeneous solve and two distinct inclusion models. Stop if a projected complete study exceeds 12 hours of sequential compute or an 8 GiB peak-memory budget for one worker. This is a proposed resource cap, not a runtime forecast.

If the cap is exceeded, report the evidence and propose a smaller amended catalog for approval. Do not substitute convenient cases silently or introduce a custom accelerator.

Report solver time, assembly time, factorization or iterative-solve behavior where available, memory, numerical precision, source-response reuse, and hardware class. Do not claim GPU acceleration without using and measuring it.

### Intended outputs

An approved implementation would write an experiment record under experiments/ert-observability-pilot/ containing:

- the frozen configuration and candidate manifest;
- geometry identifiers, units, and generation seed;
- raw currents and predicted signed voltages;
- assumed covariance definitions;
- convergence and cross-solver comparisons;
- pair diagnostics and finite-bank countermodels;
- resource measurements;
- plots with depth, contrast, and noise labels;
- a Markdown report distinguishing numerical findings from future hypotheses;
- a pinned dependency environment and exact reproduction commands.

The record must state whether the full catalog and verification checks completed. No output file exists yet.

### Research decision

An informative pair has optimistic accuracy at least 90% in its declared noise scenario, after numerical checks pass. This definition applies only to the fully specified Gaussian pair.

Report the informative fraction separately for every noise scenario. Do not drop deep or low-signal cases from the denominator.

Proceed to designing the larger inference comparison only if at least one scenario contains verified informative pairs. Report how nuisance alternatives change that assessment.

If no pairs pass, consider different sensor geometry or target scales. The result concerns the evaluated catalog and noise scenarios, not all surface ERT.

Do not proceed to adaptive acquisition or hardware based on optimistic pair accuracy alone. A later proposal must specify inference with nuisance marginalization, strong Bayesian target-design baselines, calibration, and acquisition time.

## Edge Cases & Error Handling

- Reject overlapping H2 spheres, objects intersecting the surface, duplicate electrodes, invalid current signs, and nonpositive material resistivity.
- Treat zero or negative measured voltage as valid signed data when physically consistent. The absolute noise floor keeps the covariance positive.
- Fail numerical verification when solver tolerance, padding, or discretization cannot meet the declared thresholds.
- Resolve potential-reference choices consistently. Compare voltage differences rather than absolute potentials.
- Deduplicate symmetry-related physical models and reciprocal measurements without losing sign information.
- Retain absent or failed diagnostics as missing outcomes. Do not impute a successful result.
- Record finite-bank limitations. An apparent distinction does not prove global uniqueness.
- Include differently labeled material twins with identical conductivity fields. Their responses must agree within numerical tolerance; no material-label classifier is implemented.
- Keep independent-solver failures visible. A result without the independent check is inconclusive.
- If version or platform compatibility blocks a solver, record the blocker and use a supported open-source environment only after documenting the change.
- If runtime or memory exceeds the resource cap, stop and propose a scope amendment. Do not claim the pilot is complete.
- Never interpret the fixed-current assumption as physical instrument feasibility. A finite-electrode and compliance study must precede such a claim.

## Acceptance Criteria

- [ ] All 24 pair definitions and 30 distinct primary physical models match the specified geometry and units.
- [ ] The candidate manifest contains 4,096 valid canonical configurations, a published seed, and a reproducible hash.
- [ ] Signed voltages and all six covariance scenarios are preserved without noise-floor removal.
- [ ] The homogeneous reference, mesh-convergence, padding-convergence, and independent-solver checks meet the declared normalized thresholds.
- [ ] Every primary pair and noise scenario has a diagnostic result or an explicitly reported failure.
- [ ] Finite-bank alternatives are checked in both truth directions, with coverage and deduplication documented.
- [ ] Exact material twins agree within numerical tolerance.
- [ ] No claim of marginalized inference accuracy, global uniqueness, adaptive efficiency, hardware feasibility, or field mapping follows from this pilot.
- [ ] Runtime, memory, model reuse, and incomplete outcomes are reported against the resource cap.
- [ ] Original code and public artifacts have recorded provenance and suitable licenses.
- [ ] The report provides a continue, change-geometry, or inconclusive decision supported by the actual diagnostics.
- [ ] Reproduction commands regenerate the raw response tables and reported diagnostics from the frozen configuration.
