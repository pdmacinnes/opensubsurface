# Spec: ERT numerical validation follow-up

Status: approved on October 8, 2026 and completed with an inconclusive scientific outcome. The [published follow-up](../experiments/ert-numerical-validation/README.md) records the accepted scope and evidence. SimPEG's homogeneous gate still fails; four existing pyGIMLi inclusion geometries were checked only after that solver's own homogeneous gates passed. Independent inclusion accuracy remains unverified.

## Requirements & Goals

Resolve the homogeneous-reference failure before interpreting geometry responses.

Keep the original electrodes, 1 mA mathematical source, units, analytic half-space reference, and normalized error thresholds. Do not compensate voltages using an empirical correction or relax the thresholds to produce a passing result.

The fine development profile converged algebraically but remained inaccurate against the continuum reference. Its full-bank projection was approximately 13.4 hours. That does not identify the cause completely or establish an observability limit.

This next stage is numerical validation only. It runs no nuisance bank, adaptive policy, classifier, or hardware experiment.

Use existing SimPEG and pyGIMLi capabilities. Retain the 8 GiB process cap and add a four-hour total compute cap for this stage.

## Inputs, Outputs & Behavior

Use the frozen 4,096-configuration manifest from the [published record](../experiments/ert-observability-pilot/results/2026-10-08/configuration.json).

Compare the analytical homogeneous voltages with small, explicitly recorded numerical configurations:

1. Inspect electrode interpolation, source superposition, current conservation, and sign conventions.
2. Separate near-electrode refinement from remote-region grading. The previous inside-region refinement did not remove the discrepancy.
3. Compare an existing graded tensor-mesh formulation with the current octree formulation at compatible resource sizes.
4. Refine the intermediate and remote regions independently of the inclusion region.
5. Check padding separately from mesh grading.
6. Compare the homogeneous case with the independent pyGIMLi formulation.
7. Only after a homogeneous configuration passes, test at most four existing representative inclusion models for mesh and independent-solver agreement.

The mesh choices are experimental factors, not a predetermined root-cause diagnosis. Profile a homogeneous solve before expanding a configuration.

Publish raw voltages, residuals, interpolation and geometry settings, convergence comparisons, resources, and an explicit pass or inconclusive decision.

If a validated configuration is found, measure its representative inclusion cost. Present a separate revised catalog scope before running geometry classification or nuisance searches.

The original 810-state bank is not silently reduced. A future amendment may reduce it, but must identify what uncertainty is removed and what conclusions become narrower.

## Edge Cases & Error Handling

- Stop if the process exceeds 8 GiB or this validation stage exceeds four hours.
- Record failed or missing comparisons without imputing favorable outcomes.
- Treat agreement in the homogeneous singularity-removal case as a limited check, not proof of inclusion accuracy.
- Do not mix numerical error with assumed measurement noise.
- Do not call a failed numerical configuration evidence that the ground geometry is unobservable.
- Do not implement a custom PDE solver or accelerator if an existing-library approach fails.
- No change to the physical model, covariance, candidate manifest, or acceptance thresholds is authorized by this stage.
- If source or boundary assumptions need a substantive change, document the reason and propose a further amendment.

## Acceptance Criteria

- [x] Numerical configurations, units, electrode placement, and source conventions are recorded.
- [x] The frozen manifest and analytic reference match the published original.
- [x] A passing homogeneous configuration has normalized RMS at most 0.1 and maximum at most 0.25, or the stage reports inconclusive.
- [x] Algebraic residual and continuum-reference error are reported separately. pyGIMLi equation residuals are not exposed by this adapter and are labeled unavailable.
- [x] Padding and remote grading are tested independently rather than attributing every improvement to cell size.
- [x] Inclusion comparisons are attempted only after the applicable homogeneous gate passes.
- [x] No nuisance bank, adaptive acquisition, classification claim, or hardware work is included.
- [x] The four-hour and 8 GiB caps are monitored, accepted peaks are recorded, and checks run after native calls. The README describes the monitoring limitation.
- [x] Reproduction commands and raw data support the actual next decision.
- [x] Any future geometry-bank amendment is presented separately before execution. No bank amendment was executed.

Evidence is in the [results](../experiments/ert-numerical-validation/results/2026-10-08/RESULTS.md) and [raw-data tables](../experiments/ert-numerical-validation/results/2026-10-08/TABLES.md). A fitted-mesh dependency was added to avoid cell-center volume aliasing, using existing meshing and PDE libraries. The same four geometries and all original physical and statistical assumptions were retained.
