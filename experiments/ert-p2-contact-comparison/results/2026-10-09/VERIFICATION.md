# Verification checkpoints

The replacement test-first instructions arrived during this task, after `p2_contact.py` and `p2_report.py` had been written and while C-P2 was executing. Initial feature development therefore predates those instructions; no retrospective red-first claim is made.

## Checkpoint 1: real failing checks

The reporting-integrity test constructed invalid joint three-dimensional cell positions while retaining each coordinate column's sorted values. The unchanged implementation accepted those positions. The key failure was:

```text
Failed: DID NOT RAISE any of (ValueError, AssertionError)
```

An earlier fixture attempt merely permuted a valid Cartesian set and failed its own corruption assertion. That setup failure was understood and corrected before recording the reporting failure above. The rejection expectation was not changed.

The new lint gate found a pre-existing unused context binding:

```text
F841 Local variable `construction` is assigned to but never used
src/opensubsurface/pilot.py:61
```

A second reporting test proved that a failed worker could still produce a complete diagnostic decision. Its key failure was:

```text
AssertionError: assert 'not supported' == 'inconclusive: invalid run'
```

## Checkpoint 2: smallest fixes

The report now compares sorted complete coordinate tuples. The integrity test also verifies that the original six-state record is valid before corruption, and updates the fixture checksum so rejection must come from geometry validation rather than checksum mismatch.

The unused local binding was removed while retaining its resource-monitor context. No numerical method changed.

The report now requires completed, valid workers as well as valid resources before drawing a complete diagnostic conclusion. Failed-worker records remain inconclusive.

The six P2 tests pass. They cover real geometry construction and explicit material assignment, both resource-admission and resource-skip cases, separate diagnostic/accuracy decisions, failed-worker handling, published report reconstruction, and invalid-data rejection. Their geometry probes run no contact voltage calculation.

## Checkpoint 3: final gate

The PR body records the actual final summary lines for:

- the complete pytest suite;
- five repeated runs of the six new P2 tests;
- pinned Ruff code checks with zero lint diagnostics;
- Python package wheel construction;
- end-to-end recreation of all four published study reports and dependency consistency.

This is a Python research project with a CLI workflow. Report recreation is its end-to-end check; there is no browser product or UI test suite. Existing native unit tests emit two known library performance/efficiency warnings, which are recorded separately from lint diagnostics.

Ruff 0.16.10 is a development-only addition under the new standing instructions. The experiment's solver/runtime dependency set and six-solve limit remain unchanged. Native P2 cases were not repeated to satisfy software-test repetition.

Observed final summary lines:

```text
39 passed, 2 warnings in 11.95s
New P2 tests repeated five times: 6 passed each run
Ruff: All checks passed!
Successfully built opensubsurface
Four published report CLI commands completed successfully
No broken requirements found.
```
