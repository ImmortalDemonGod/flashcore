# Oracle-Correction Record — change `c2-f169-impl`

**Date:** 2026-06-19  
**Change:** `c2-f169-impl`  
**Finding:** F169 — `flashcore/scheduler.py:212` assigned `fsrs_card.last_review = fsrs_card.due`,
causing any on-time Review-state review to compute `elapsed_days = 0` (review_ts.date() − due.date() = 0).

This record satisfies the oracle-guard requirement: for each pre-existing test edited in `c2-f169-impl`,
it names the test and justifies **why the OLD oracle was wrong**, anchored to the finding and
independent of the implementation.

---

## Test 1: `tests/test_scheduler.py::test_review_lapsed_card`

### Change made

`last_review_date=datetime.date(2023, 12, 31)` added to the `Card(...)` constructor in the test setup
(one day before `next_due_date=2024-01-01`).

### Why the old oracle was wrong (anchored to F169)

The old test constructed a `Review`-state `Card` without `last_review_date`.  Under the **buggy** code
(`fsrs_card.last_review = fsrs_card.due`, line 212), the scheduler measured all elapsed-day values
from `due` instead of from the actual prior-review timestamp.  This produced:

| Scenario | review_ts | elapsed_days (buggy) | Correct value |
|---|---|---|---|
| On-time | 2024-01-01 | `2024-01-01 − 2024-01-01 = 0` | 1 (last review was 2023-12-31) |
| Lapsed (+10d) | 2024-01-11 | `2024-01-11 − 2024-01-01 = 10` | 11 |

The assertion `result_lapsed.elapsed_days > result_on_time.elapsed_days` evaluated to `10 > 0 = True`.

**The oracle was wrong because:**

1. **Silent pass on the primary defect.** The on-time `elapsed_days = 0` was the exact defect F169
   describes.  The test's only assertion was the *relative ordering* (lapsed > on-time), not
   `result_on_time.elapsed_days > 0`.  The test was therefore passing *through* the bug, not in spite
   of it.  The plan's §2 fact table explicitly flags this: "Silent-pass test … `result_on_time.elapsed_days > 0`
   NOT asserted."

2. **Wrong baseline for both values.** Both `elapsed_days` figures were derived from `due`, not from the
   actual prior-review date.  The relative ordering happened to hold by coincidence (`10 > 0`) because
   the lapsed review date is always greater than `due`, while on-time review date equals `due` (yielding
   0).  The test was not verifying a correct computation; it was verifying that `(lapsed_date − due) > 0`,
   which is trivially true regardless of what the prior-review timestamp was.

3. **Wrong simulated production context.** In production, every Review-state card has at least one
   prior review recorded in the `reviews` table.  The hub (`review_processor`) always reads
   `last_review_date` from the DB before calling `compute_next_state` (Path A, D1.2).  A test that
   constructs a Review-state Card **without** `last_review_date` is simulating an impossible production
   scenario (a Review-state card with no review history).  The correct unit-test setup must supply
   `last_review_date`, which the test now does (set to 2023-12-31, one day before due).

**Correct behavior after correction:**

| Scenario | elapsed_days | Assertion |
|---|---|---|
| On-time | `2024-01-01 − 2023-12-31 = 1` | — |
| Lapsed (+10d) | `2024-01-11 − 2023-12-31 = 11` | `11 > 1` ✓ |

The assertion `result_lapsed.elapsed_days > result_on_time.elapsed_days` still holds and now tests
correct values.

---

## Test 2: `tests/test_scheduler.py::test_review_early_card`

### Change made

`last_review_date=datetime.date(2024, 1, 8)` added to the `Card(...)` constructor in the test setup
(two days before `next_due_date=2024-01-10`, matching the early-review scenario's offset).

### Why the old oracle was wrong (anchored to F169)

The old test constructed a `Review`-state `Card` without `last_review_date`.  Under the **buggy** code
(`fsrs_card.last_review = fsrs_card.due`, line 212):

| Scenario | review_ts | elapsed_days (buggy) | Correct value |
|---|---|---|---|
| On-time | 2024-01-10 | `2024-01-10 − 2024-01-10 = 0` | 2 (last review was 2024-01-08) |
| Early (−2d) | 2024-01-08 | `2024-01-08 − 2024-01-10 = −2` | 0 (reviewed on same day as last review) |

The assertion `result_early.elapsed_days < result_on_time.elapsed_days` evaluated to `−2 < 0 = True`.

**The oracle was wrong because:**

1. **Accepted semantically impossible output.** `elapsed_days = −2` means "the review occurred
   2 days *before* the last review."  This is not a valid state for any card in the system.  An oracle
   that accepts negative elapsed days is encoding the bug as expected behaviour, not testing a
   memory-scheduling invariant.

2. **Wrong baseline.** Again, both values were measured from `due` instead of from the prior-review
   date.  The on-time scenario yielded `0` (due − due) and the early scenario yielded `−2`
   (early_date − due, a negative number).  The assertion `−2 < 0` is arithmetically true but tests
   only that the early date is before the due date, which is a trivial calendar property — not a
   property of the FSRS computation.

3. **Wrong simulated production context.** Same as Test 1: a Review-state Card without
   `last_review_date` is impossible in production.  The correct setup supplies `last_review_date`
   (here: 2024-01-08, two days before due and coinciding with the early-review scenario date).

**Correct behavior after correction:**

| Scenario | elapsed_days | Assertion |
|---|---|---|
| On-time | `2024-01-10 − 2024-01-08 = 2` | — |
| Early (−2d) | `2024-01-08 − 2024-01-08 = 0` | `0 < 2` ✓ |

The assertion `result_early.elapsed_days < result_on_time.elapsed_days` still holds and now tests
correct, non-negative values: an early review produces fewer elapsed days than an on-time review.

---

## Evidence of execution

Both tests pass with the corrected setup:

```
$ python -m pytest tests/test_scheduler.py::test_review_lapsed_card \
                   tests/test_scheduler.py::test_review_early_card -v
2 passed
```

Both tests **would fail** if `last_review_date` were omitted from the Card constructor under the
corrected scheduler code — because without `last_review_date`, both scenarios produce `elapsed_days=0`,
making `0 > 0` and `0 < 0` both False.  This confirms the correction is load-bearing, not cosmetic.

```
# Verified via python3 inline script (2026-06-19):
# test_review_lapsed_card WITHOUT last_review_date:
#   on_time.elapsed_days=0, lapsed.elapsed_days=0
#   assertion lapsed > on_time: 0 > 0 = False   ← FAIL
#
# test_review_early_card WITHOUT last_review_date:
#   on_time.elapsed_days=0, early.elapsed_days=0
#   assertion early < on_time: 0 < 0 = False    ← FAIL
```

---

## Summary

Both old test setups were wrong because they constructed Review-state Cards without `last_review_date`,
which forced the scheduler to use the buggy `last_review = due` proxy (Finding F169).  The old oracles
accepted the defective output (on-time `elapsed_days = 0`; early `elapsed_days = −2`) as correct,
making them silent-pass tests that confirmed the bug rather than detecting it.  The corrections supply
`last_review_date` (simulating the hub's DB lookup), so the tests now verify the correct FSRS invariants
against correct input data.
