# Verification checkpoints

## Checkpoint 1: expected behavior failure

The changed-current test was written first. The initial loader checked sensor and measurement shapes but accepted a current of 1 A instead of the frozen 0.001 A. Running the targeted test produced:

```text
test_changed_current_is_rejected_before_any_calculation
Failed: DID NOT RAISE ValueError
1 failed in 3.04s
```

This was a missing input-validation behavior, not a missing module, fixture, or dependency. No native voltage calculation was used for the failing test.

## Checkpoint 2: implementation and controls

The loader now rejects an altered current, sensor order, axes, measurement indices, resistivity states, references, and historical contact values. Tests independently compare literal electrode coordinates, published axes and voltages, and the existing analytical contact reference.

After implementing the standalone script, 16 new checks passed in 0.70 seconds. The publication checksum test was temporarily skipped because executed artifacts had not yet been staged. It is required in the final gate and contains no skip marker.

Other checks exercise positive reproduction, non-reproduction, nonfinite and incorrectly shaped voltages, failed control skips, native exceptions, incomplete runs, and overwrite protection. They use test doubles and saved arrays. Validation-only execution copies the two files outside the checkout, blocks native and project imports, and confirms no result file appears. The import guard itself is checked before execution.

Exactly two real native state calculations then completed in the monitored, copied-directory execution. The preceding local-helper startup failure reached zero native calculations. Failed and successful evidence is preserved; the native calculations are not repeated for test repetition or CI.

## Checkpoint 3: final gate

The final gate covers the complete pytest suite, five repeated runs of the cheap new tests, zero-diagnostic Ruff checks including the standalone script, package wheel construction without new dependencies, all four historical report recreations, and published Git-byte checksums. The result-metric test independently recreates the executed decision from literal voltages and checks combined time and memory accounting.

There is no browser UI in this research workflow. Validation-only standalone execution and report reconstruction are its end-to-end checks. The full suite's existing SimPEG tests emit two native-library performance and sparse-format warnings. These are separate from lint diagnostics.

Observed final summary lines:

```text
58 passed, 2 warnings in 13.59s
New reproduction tests repeated five times: 18 passed each run
Ruff: All checks passed!
Successfully built opensubsurface
No broken requirements found.
Four historical report CLI commands completed successfully
Published Git-byte checksums and execution identities verified
```

Native provenance, resource observations, and reproduction status come from the executed artifacts, not test doubles. No solver/runtime dependency or development package was added.
