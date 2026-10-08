# Proposed first experiment

Status: **draft protocol for review**. This document is not a completed preregistration or approval to implement software. No experiments have been run and no hardware purchase is authorized by this protocol.

All numerical settings and thresholds below are proposed design choices. They are not measured instrument specifications or scientific results.

## Hypothesis

For a specified family of shallow three-dimensional resistivity structures and realistic acquisition errors, ambiguity-focused adaptive measurement selection can reach a defined accuracy at at most half the acquisition cost of the strongest evaluated standard or optimized design.

The [recommended-direction document](recommended-direction.md) defines the scientific claim boundary.

## Inputs, outputs, and behavior

The input is a sequence of electrode configurations, injected currents, measured voltage differences, acquisition metadata, and uncertainty assumptions.

The primary output is a probability distribution over two competing geometry hypotheses.

- **H1:** one connected resistive inclusion.
- **H2:** two separated resistive inclusions.

Additional outputs include position uncertainty, posterior predictive checks, acquisition cost, and an explicit unresolved result.

The policy sees acquired observations and publicly defined model families. It does not see the true geometry, test labels, noise realization, or observations reserved for independent checking.

The next measurement comes from a physically feasible candidate pool defined before the hidden target is generated.

## Geometry and target families

Start with a hypothetical 8 by 8 surface electrode grid with 3 m spacing and a 21 m aperture.

Use a central region of interest extending approximately 12 m down. Numerical boundaries must be sufficiently distant to pass a boundary-convergence check.

Proposed sweeps include:

- target-center depths of approximately 2, 4, 6, and 8 m;
- characteristic inclusion sizes of approximately 1-3 m;
- weak through strong electrical contrasts;
- varying orientation and separation;
- homogeneous, layered, and heterogeneous backgrounds;
- modest topography;
- surface-only acquisition throughout the primary comparison.

Reject configurations that intersect the ground surface or otherwise violate their intended geometry. Report minimum cover depth separately from center depth.

Match total anomalous volume and bulk contrast across selected H1/H2 pairs. Otherwise the comparison may be solved by anomaly strength instead of geometry.

Include homogeneous backgrounds and unrelated anomalies as negative or out-of-family controls. Some geometry pairs should be unresolvable.

## Pilot and confirmatory separation

Use a separate pilot to check physical plausibility, computational expense, numerical accuracy, and task difficulty.

The pilot may refine numerical settings and the sample count. Record each change and its reason before freezing the confirmatory protocol.

Freeze the confirmatory geometry distribution, candidate pool, policies, tuning budget, stopping criteria, and success thresholds before evaluating held-out cases.

An eligibility rule for the primary observable regime must come from the pilot and a published geometry-based definition. Do not select easy test cases after seeing which policy succeeds.

Retain difficult and unobservable strata in the released evaluation. Report them even when they are outside the primary comparison.

## Acquisition uncertainty

Use raw voltages and injected currents rather than apparent resistivity alone.

Proposed stress conditions include:

| Condition | Proposed sweep |
| --- | --- |
| Relative voltage error | 1%, 3%, and 5% |
| Absolute voltage noise floor | 1-100 microvolts |
| Electrode position error | Up to 5% of nominal spacing |
| Correlated acquisition error | Gain and drift cases |
| Electrode failures | Occasional unavailable electrodes |
| Physical electrode effects | Finite geometry and selected contact effects |
| Instrument limits | Current and voltage-compliance constraints |
| Model mismatch | Background heterogeneity and modest topography |

These are sensitivity studies. Later instrument measurements must establish actual ranges.

A noise floor must affect achievable information. Do not normalize weak voltages in a way that silently removes absolute noise or current-compliance limits.

Do not represent contact resistance as an arbitrary voltage offset. Four-electrode arrangements suppress some contact effects. Finite geometry, polarization, current compliance, and receiver behavior need appropriate treatment. The complete-electrode model is an established basis for finite geometry and contact effects. [Rücker and Günther, 2011](https://doi.org/10.1190/1.3581356)

Use simpler electrode models where validated. The study need not implement every nuisance model in its first pilot.

## Baselines and ablations

Compare at least:

1. Standard dipole-dipole and Wenner-Schlumberger surveys extended across the grid.
2. A static optimized design based on linearized resolution or uncertainty.
3. An adaptive design targeting resolution in the currently uncertain region.
4. The proposed design targeting H1/H2 discrimination.
5. A nuisance-unaware version of the proposed method.

Use comparable downstream inference across acquisition policies wherever possible. If inference differs, separate its contribution from the acquisition-policy effect.

Give baselines comparable tuning effort on development cases. Publish the configurations and tuning process.

The adaptive baseline must reflect established work, not a deliberately weak substitute. [Wilkinson et al., 2015](https://academic.oup.com/gji/article/203/1/755/586360)

## Acquisition cost

The primary budget represents acquisition time. Include:

- current injections and simultaneous receiver channels;
- repeated stacks;
- switching and settling;
- reciprocal observations and quality checks;
- calibration;
- failed or rejected observations.

Also report the number of configurations, instrument commands, modeled energy where meaningful, compute time, memory, and setup burden.

Fewer recorded voltage pairs do not necessarily mean less survey time. Freeze instrument-channel assumptions for every compared policy.

Keep electrode geometry fixed in the primary experiment. Moving sensors must not provide an uncounted advantage.

The cost model is simulated until physical validation. Label it accordingly and test whether the conclusion changes under plausible timing models.

## Independent numerical verification

Develop with one forward solver and check representative results with another. SimPEG and pyGIMLi are candidate foundations.

Use different meshes and refinement levels. Check current conservation, a homogeneous reference solution, mesh convergence, and outer-boundary convergence.

For matched-model comparisons, numerical disagreement must be below the intended measurement noise floor. If it is not, fix the numerical issue or use a clearly justified higher floor. Do not silently count solver error as measurement noise.

Assess intentional physical-model mismatch separately.

Do not generate and reconstruct observations using identical discretization and assumptions. This avoids the inverse crime, where a method succeeds because data generation and inversion share the same numerical simplifications.

No custom solver or GPU backend is part of the initial proposed scope unless profiling establishes a concrete need.

## Controls against unsupported inference

### Exact material ambiguity

Give differently labeled physical objects identical conductivity fields.

Their ideal DC observations must agree within numerical tolerance. The algorithm must report that material identity is unresolved.

This control tests interpretation discipline, not H1/H2 geometry accuracy.

### Near-indistinguishable geometry

Search for H1/H2 pairs whose feasible measurements differ by less than the noise and model-error scale.

Keep the construction procedure separate from policy evaluation. Use these cases to test unresolved behavior, not to inflate primary accuracy.

### Held-out geological families

Test irregular inclusion shapes and background structures outside the development family.

Label these as distribution-shift tests. Do not claim that calibration inside a restricted prior establishes robustness outside it.

### Held-out measurements

Reserve electrode configurations that the policy cannot acquire. Check whether inferred models predict their observations.

Define the reservation without using the hidden test geometry. Keep the held-out observations unavailable to tuning and stopping rules.

### Negative and out-of-family cases

Include ground without the target, unrelated conductive or resistive changes, failed electrodes, and model configurations outside H1/H2.

Define in advance what counts as a confident false detection and what triggers an unresolved result.

An “unknown” output alone does not guarantee open-set robustness. Measure its performance against these controls.

## Sample size and analysis

A starting plan is approximately 50 independent pilot geometries, at least 500 independent confirmatory geometries, and a dedicated ambiguity-control set.

Treat repeated noise realizations from the same geometry as grouped observations. Do not count them as independent geological evidence.

The pilot must support a sample-size and compute-budget assessment. Any revision happens before the confirmatory comparison and is documented.

Evaluate each policy at common cost budgets and estimate its cost-to-accuracy curve. A baseline that never reaches the target has a censored cost, not an invented finite value.

Use geometry-grouped uncertainty estimates. Report confidence intervals for the improvement, accuracy, false detections, and unresolved rate.

## Metrics

Report:

- unconditional balanced H1/H2 accuracy, counting abstentions as unsuccessful decisions;
- acquisition cost needed to reach the target accuracy;
- confident false detections on negative controls;
- unresolved rates on ambiguity controls;
- uncertainty calibration and interval width;
- localization and separation errors;
- held-out observation prediction errors;
- outcomes by depth, contrast, noise, geometry, and background family;
- runtime and peak memory.

A narrow interval is not useful if it misses the truth. A broad interval can be calibrated without resolving the geometry. Report both coverage and precision.

Selection probabilities and calibration statements are conditional on the declared model family. Test sensitivity to the prior and nuisance assumptions.

## Proposed acceptance criteria

- [ ] At least 90% balanced H1/H2 accuracy on the preregistered primary distribution.
- [ ] At most half the acquisition cost of the strongest evaluated baseline at the same accuracy.
- [ ] Confident false detections on negative controls no greater than 5%.
- [ ] At least 90% unresolved responses on designated indistinguishable controls.
- [ ] The advantage survives independent-solver checks.
- [ ] The advantage survives important nuisance conditions.
- [ ] The improvement has a statistical confidence interval excluding no benefit.
- [ ] Held-out measurement predictions support the inferred explanations.
- [ ] Baseline tuning and inference comparisons do not provide an unfair advantage.
- [ ] Runtime and memory fit a documented local workflow.
- [ ] Complete outcomes, failures, and protocol deviations are reproducible.

Thresholds are intentionally demanding and may change only during the documented pilot. Success in shallow high-contrast cases must be reported within that scope.

## Failure and stop conditions

Reject the proposed advance if it:

- fails to beat established optimized designs;
- loses its advantage under realistic electrode errors or heterogeneous ground;
- confidently separates physically indistinguishable examples;
- succeeds only under its assumed object shapes;
- reaches the cost target by relaxing accuracy or uncertainty requirements;
- fails independent forward-model checks.

If compute limits prevent the confirmatory study, report the study as incomplete. Do not replace the frozen test set with convenient cases.

A negative result may identify the need for additional acquisition geometry or measurement physics. Publish that finding without presenting it as an efficiency success.

## Meaning of a successful result

A successful simulation result would justify a physical test. It would not establish field mapping performance.

The next evidence would be a blinded physical experiment with known geometry, raw current and voltage records, instrument error characterization, and an independent rerun.

Borrow equipment or investigate collaboration before purchasing a survey system. A tank test must use appropriate boundaries and cannot by itself establish field performance.

## Review before implementation

Confirm the following before approving software work:

- the target geometry and model families are physically meaningful;
- the closest task-specific prior art has been checked;
- the acquisition cost and noise models are defensible;
- strong baselines are feasible;
- solver independence and numerical convergence can be verified;
- the pilot and confirmatory stages remain separate;
- the project scope and acceptance criteria are explicitly approved.
