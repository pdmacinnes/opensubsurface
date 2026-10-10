# Reproducibility requirements

Status: research practice applied to the [first numerical pilot record](../experiments/ert-observability-pilot/results/2026-10-08/RESULTS.md). The environment and raw profiles are published; the full numerical study remains incomplete.

The [numerical validation follow-up](../experiments/ert-numerical-validation/README.md) publishes additional homogeneous voltages, four-geometry mesh comparisons, generated fitted meshes, and a reporting command. Its outcome also remains inconclusive. Successful software checks do not establish inclusion accuracy.

## Record each experiment

For an approved experiment, publish:

- the hypothesis, scope, acceptance criteria, and failure conditions;
- the protocol version and all deviations;
- model geometry, units, boundaries, and physical assumptions;
- raw observations and acquisition metadata;
- noise and nuisance models;
- software versions, dependency environment, and random seeds;
- baseline configurations and tuning procedures;
- the evaluation split and metrics;
- complete results, including failures and ambiguous cases;
- runtime, hardware class, and memory use.

Mark synthetic observations and physical measurements separately. Report source data and processing history for derived artifacts.

## Verify inference claims

Check the actual observations, forward predictions, numerical convergence, and held-out cases. A rendered image or successful optimizer exit is not sufficient verification.

Distinguish detection, localization, shape recovery, and material identification. Report the conditions under which each claim holds.

Label posterior uncertainty as conditional on its physical model and prior. Test model mismatch and prior sensitivity where relevant.

## Keep the public record independent

Publish only original project material and external content with suitable redistribution rights. Keep credentials, private information, internal documents, and proprietary datasets out of commits and releases.

Record provenance and license terms for each external dependency or dataset. Linking a paper does not grant permission to copy its text, figures, or data.

Use public no-reply addresses for commit metadata when appropriate. Review staged files rather than adding the entire workspace.

## Local output and public artifacts

The initial ignore rules exclude local output directories and common caches. These rules do not substitute for reviewing publications.

When data become too large for ordinary Git, choose an appropriate public artifact location and document persistent identifiers, checksums, and download instructions.

The Apache 2.0 license applies to original repository content. External datasets and dependencies retain their own terms.
