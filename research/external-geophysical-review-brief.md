# External geophysical review brief

This packet is ready for a reviewer selected by the project owner. It has not been sent to anyone. The accompanying [audit](error-budget-boundary-review.md) is assistant-prepared, not external peer review.

## Review objective

Decide whether our numerical validation protocol and finite-domain formulation are suitable foundations for a later shallow one-sphere/two-sphere discrimination study. We seek corrections before buying hardware or running a geometry/nuisance bank.

OpenSubsurface is an independent civilian open-source sensing project. Adaptive ERT and optimized survey design are established prior art. No new technology, accurate map, acquisition-efficiency gain, or physical observability limit is claimed.

## Evidence to inspect

- [Initial research and candidate approaches](initial-research-report.md).
- [Exact vertical-contact reference](contact-reference.md), traced to USGS Professional Paper 499, pages 52-53.
- [Twelve-state contact study](../experiments/ert-contact-benchmark/results/2026-10-09/RESULTS.md).
- [Six-state P2 comparison](../experiments/ert-p2-contact-comparison/results/2026-10-09/RESULTS.md), with raw voltages, materials, topology, checksums, and source/build metadata.
- [Native execution-path review](native-solver-review.md), including the distinction between direct mesh assignment and managed refinement.
- [Error-budget and boundary audit](error-budget-boundary-review.md), its role census, analytical probes, and matched symmetry pairs.

The tests verify software behavior and reproducible reporting. They do not certify heterogeneous accuracy. No new native solve was run for the final audit.

## Specific questions

1. Is the contact image reference and signed ABMN superposition correct under the stated point-electrode, flat-surface, isotropic assumptions?
2. Is the derived discrete relation `S * u_total = S1 * g_unit` an accurate description of the inspected singularity-removal path, including calibration and source-node handling? Which parts of its continuous boundary analogue are justified?
3. Does the shared-center, facetwise mixed-boundary coefficient impose a materially different finite problem from the infinite contact reference? How should a useful benchmark isolate truncation from volume/source discretization?
4. What could explain the heterogeneous y-reflection discrepancies on a symmetric material/grid/domain while the homogeneous matched pairs agree? Which source-load, assembly, projection, reciprocity, constraint, or solver diagnostics should be collected first?
5. Is a covariance based on the homogeneous response appropriate for the eventual discrimination task? What numerical budget should be required relative to validated target-response differences and realistic correlated acquisition errors?
6. Which independently reproducible finite-contrast sphere reference is suitable next, and how should sphere/image interactions and reference-series error be bounded?
7. Which established open-source formulation or benchmark should we reuse before developing new numerical machinery?

## Requested review output

Identify any incorrect assumptions, derivations, or comparisons. Distinguish a project-adapter defect, native-library approximation, benchmark/formulation mismatch, and an evaluation-budget choice. Recommend the smallest falsifiable next diagnostic with explicit uncertainty and resource limits.

No approval to alter measurements, thresholds, source physics, or public results is implied by this packet. Any proposed study requires a concrete reviewed scope. Public issue/PR discussion is welcome once the owner chooses how to request the review.
