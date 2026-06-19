# Bug Catalog — `flashcore/scheduler.py` (FSRS_Scheduler)

Generated for finding F169. Target: `tests/test_scheduler.py`.
Skill: design-tests. Path decision: **Path A** — add `last_review_date: Optional[date]`
to `Card` as a transient field, giving `compute_next_state` the actual prior-review date.
Rationale: Path A is exact (no approximation); Path B's stability-based approximation
yields wrong elapsed_days for post-lapse cards (low stability after reset) and cannot
cleanly represent a genuinely-zero-elapsed same-day re-review in unit tests.

---

## 1. Code Summary

### Public interface
`FSRS_Scheduler.compute_next_state(card: Card, new_rating: int, review_ts: datetime) → SchedulerOutput`
All FSRS scheduling state flows through this single method. Inputs: a Card carrying
cached FSRS fields (`state`, `stability`, `difficulty`, `next_due_date`); an integer
rating 1–4; a UTC review timestamp. Output: `SchedulerOutput` carrying the new
stability, difficulty, next_due date, scheduled_days, review_type, elapsed_days, and
new CardState.

### Load-bearing comments
- `scheduler.py:199` — "Initialize from cached card state (O(1) instead of O(N)
  history replay)": the architecture choice that removes direct access to prior-review
  history and makes `last_review_date` a required caller-supplied input.
- `scheduler.py:211` — "Set last_review to due date for elapsed_days calculation":
  this is the bug site; the comment describes the broken logic as if it were intentional.

### IO boundaries
None (pure function). No file I/O, DB, HTTP, or randomness. The only external call is
`self.fsrs_scheduler.review_card(...)` from `py-fsrs`. `review_ts` is the only
time-sensitive input, supplied by the caller.

### Branching points (pre-bug-catalog candidates)
1. `scheduler.py:200` — `if card.state != CardState.New` — skips field initialization
   for New cards; New cards have `last_review` unset → `elapsed_days = 0` (correct for
   new cards; this branch is correctly guarded).
2. `scheduler.py:205` — `if card.next_due_date` — only sets `fsrs_card.due` (and the
   buggy `last_review`) when `next_due_date` is present. Cards with no due date but
   non-New state are an edge case (reachable via data corruption; currently sets
   `last_review` to an unset attribute → skips to `elapsed_days = 0`).
3. `scheduler.py:218` — `if hasattr(fsrs_card, "last_review") and fsrs_card.last_review`
   — primary elapsed_days dispatch; the false branch (`elapsed_days = 0`) is correct
   for New cards but is incidentally reached by the bug for all on-time reviews.
4. `scheduler.py:229–238` — `try/except TypeError` fallback for older `py-fsrs` API
   (`now=` keyword not supported). Two different call signatures, tested.
5. `scheduler.py:247–255` — `try/except KeyError` for unknown FSRS state names. Guards
   against future py-fsrs state enum additions.
6. `REVIEW_TYPE_MAP` dispatch at `scheduler.py:113–118` — maps FSRS state name to
   flashcore review type string. A new FSRS state would fall through to the `.get`
   default `"review"`, silently wrong.

### Type definitions of magic-string contracts
- `CardState(IntEnum)` — `New=0, Learning=1, Review=2, Relearning=3` maps 1:1 to
  `FSRSState` enum values; the mapping at `scheduler.py:204` relies on value parity.
- `REVIEW_TYPE_MAP` at `scheduler.py:113` — maps `{"new": "learn", "learning": "learn",
  "review": "review", "relearning": "relearn"}`. Covered by the `.get` default but no
  dedicated contract test.
- Rating mapping `1=Again, 2=Hard, 3=Good, 4=Easy` validated at `scheduler.py:183`.

### Existing tests (audit)
15 tests in `tests/test_scheduler.py`. Notable gap: `test_review_lapsed_card`
(line 252) asserts `result_lapsed.elapsed_days > result_on_time.elapsed_days`
(10 > 0); this passes silently with the bug because on-time=0 satisfies the relative
comparison. The absolute assertion `result_on_time.elapsed_days > 0` is absent —
the bug is undetected by all 15 current tests.

---

## 2. Bug Catalog (ranked by blast radius × plausibility)

---

### Bug B1 — `last_review = fsrs_card.due` zeroes elapsed_days for all on-time reviews (F169, CRITICAL)

**The bug**: `compute_next_state` sets `fsrs_card.last_review = fsrs_card.due`
(line 212) so that for any Review-state card reviewed on its due date,
`elapsed_days = (review_ts.date() − due.date()).days = 0`.

**Blast radius**: The most common review path — reviewing a card on its scheduled date —
silently produces `elapsed_days = 0`, which pins FSRS retrievability to R=1.0. The
stability-update formula interprets this as perfect memory with zero elapsed time, yielding
a near-zero stability increase. Over many reviews, cards are never rescheduled correctly;
long-term retention degrades invisibly.

**Why it's plausible**: The code was written to reconstruct FSRS card state from cached
fields without access to review history. `fsrs_card.last_review` had to be set to
*something* when building the synthetic `FSRSCard`; setting it to `due` was the
convenient choice. The bug is latent: `test_review_lapsed_card` passes silently
because `on_time.elapsed_days = 0 < lapsed.elapsed_days = 10` satisfies the relative
assertion, masking the absolute wrong value.

**Test type**: Captured bug (F169) + contract pin.
**Tests that catch it**: `test_on_time_review_elapsed_days_positive` (B1-A),
`test_on_time_vs_same_day_review_stability_distinct` (B1-B).

---

### Bug B2 — Negative elapsed_days for early reviews (out-of-scope F169b)

**The bug**: For any Review-state card reviewed *before* its due date,
`elapsed_days = review_ts.date() - due.date() < 0`. Negative elapsed_days is
semantically invalid for FSRS; it is equivalent to a future last_review date.

**Blast radius**: Early reviews (common when users review ahead of schedule) pass a
negative `elapsed_days` to FSRS, which may compute a nonsensical retrievability.
`test_review_early_card` currently checks `result_early.elapsed_days < result_on_time.elapsed_days`
and `result_early.stab <= result_on_time.stab`; both pass with the bug because
`-2 < 0` and the stab ordering happens to hold.

**Why it's plausible**: Same root cause as B1 — `last_review = due`. The fix for B1
(Path A: use `card.last_review_date`) also resolves the early-review sign issue if
`last_review_date` is provided correctly.

**Why deferred**: Designated out-of-scope in the launch brief as F169b. The fix for B1
will set the foundation; F169b will be filed as a separate finding in the stage-c2
audit pass.

**Test type**: Would be a negative-path + contract-pin test.

---

### Bug B3 — `CardState`/`FSRSState` value-parity assumption breaks on py-fsrs update

**The bug**: `FSRSState(card.state.value)` at line 204 relies on `CardState.Review = 2`
mapping to `FSRSState(2) == FSRSState.Review`. If py-fsrs ever reorders its enum, the
mapping silently produces a wrong state without error.

**Blast radius**: All non-New cards would be scheduled with incorrect state-transition
logic; could cause Review cards to behave as Learning cards or vice versa.

**Why it's plausible**: The py-fsrs library is an external dependency; its enum is not
under flashcore's control. The existing `KeyError` guard (line 247) catches unknown
state *names* on output but does not guard the input mapping.

**Why deferred**: Low probability — py-fsrs enum values are stable; breaking change would
require a major version bump. Out of scope for this PR. Would require a decision table
test covering all four CardState values mapping to their FSRSState equivalents.

**Test type**: Decision table.

---

### Bug B4 — `REVIEW_TYPE_MAP` default silently returns `"review"` for unknown FSRS states

**The bug**: `self.REVIEW_TYPE_MAP.get(state_before_review.name.lower(), "review")` at
line 262 returns `"review"` for any state name not in the map (e.g., a future py-fsrs
`"Suspended"` state). This corrupts analytics that rely on `review_type`.

**Blast radius**: Low — `review_type` is metadata for the hub layer; scheduling is
unaffected. Corrupts review-type statistics.

**Why it's plausible**: Same py-fsrs upgrade scenario as B3. Trivial to miss.

**Why deferred**: Cosmetic impact. No test added here; would be a contract-pin test
for the map's key set.

**Test type**: Contract pin (decision table over the four map entries).

---

## 3. Skipped Bugs (explicit negative space)

| Bug | Reason skipped |
|---|---|
| B2 (negative elapsed_days for early reviews) | Out of scope for this PR per launch brief; designated F169b; deferred to stage-c2 audit |
| B3 (CardState/FSRSState value-parity) | Low probability; requires py-fsrs major-version break; deferred |
| B4 (REVIEW_TYPE_MAP silent default) | Cosmetic; analytics metadata only; deferred |
| None-stability arithmetic guard | Guarded by `if card.state != CardState.New` — New cards (stability=None) skip the `last_review` assignment; the existing `test_first_review_new_card` covers this branch |
| `_ensure_utc` naive-datetime handling | Covered by `test_ensure_utc_handles_naive_datetime` |
| Unknown FSRS state on output | Covered by `test_compute_next_state_with_unknown_fsrs_state` |
| Old py-fsrs API (no `now=` kwarg) | Covered by `test_compute_next_state_review_card_fallback_no_now_kw` |

---

## 4. Test Design: B1 — Bugs to Catch

### B1-A: `test_on_time_review_elapsed_days_positive`

**Target bug**: B1 — `last_review=due` produces `elapsed_days=0` for any on-time review.

**Test type**: Captured bug / contract pin. Unit test of `compute_next_state`.

**Self-critique**:
- Would fail if bug introduced? YES — `elapsed_days == 0` ≠ `> 0`.
- Would fail under behavior-preserving refactor? NO — asserts on output field.
- Tests observable behavior (not internals)? YES — `SchedulerOutput.elapsed_days`.
- Uses public interface? YES — `scheduler.compute_next_state(card, rating, ts)`.

**Setup**: Review-state card, `next_due_date = review_ts.date()`. Rating=3 (Good).
Caller explicitly supplies `stability`, `difficulty`, `next_due_date` (simulating hub).
`last_review_date` is NOT supplied in this test; it only tests that `elapsed_days > 0`
regardless of how the fix supplies the prior date.

**Expected RED state**: With bug, `elapsed_days = 0`; assertion `> 0` FAILS.

---

### B1-B: `test_on_time_vs_same_day_review_stability_distinct`

**Target bug**: B1 — because `elapsed_days=0` for on-time reviews (same as a genuine
same-day re-review), the stability update is identical to what a same-day re-review
would produce, corrupting the scheduled interval.

**Test type**: Differential + captured bug. Unit test of `compute_next_state`.
Explicitly sets `last_review_date` on Card (Path A input), simulating the hub caller
that sets this field after each persisted review.

**Self-critique**:
- Would fail if bug introduced? YES — Card raises `ValidationError` now (field absent);
  after fix, if scheduler ignores `last_review_date`, both cards yield same elapsed → same stab → assertion fails.
- Would fail under behavior-preserving refactor? NO — asserts on output values.
- Tests observable behavior? YES — stability and elapsed_days are output fields.
- Uses public interface? YES.

**Setup**: Two `Card` objects, identical base params (state=Review, stability=14,
difficulty=5.0, next_due_date=Mar15). They differ only in `last_review_date`:
- `card_on_time.last_review_date = Mar 1` (14 days before due → elapsed should = 14)
- `card_same_day.last_review_date = Mar 15` (same day → elapsed should = 0)
Both reviewed at `review_ts = Mar 15 10:00 UTC`, rating=3.

**Expected RED state**: `Card(..., last_review_date=...)` raises `pydantic.ValidationError`
(`extra="forbid"`) because `last_review_date` is not yet a field on `Card`. Test ERRORS.

---

## 5. Post-Writing Evaluation (to be filled after tests run)

| Test | First run outcome | Status |
|---|---|---|
| `test_on_time_review_elapsed_days_positive` | `AssertionError: elapsed_days=0, expected >0` | RED ✓ |
| `test_on_time_vs_same_day_review_stability_distinct` | `ValidationError: last_review_date extra inputs not permitted` | RED ✓ |

**Bugs caught** (test failed first run): B1 confirmed present in both dimensions —
(A) `elapsed_days=0` for on-time Review card, (B) `Card` rejects `last_review_date`
proving Path A model field absent.

**Bugs characterized**: 0 (intentional RED stage; no new test passed first run).

**Bugs discovered during writing**: None beyond the catalog above.
Existing 15 tests: all PASS (no regression introduced by adding new tests).

---

## 6. Investigation Pass — Suspect Findings

**No "pass + suspect" items**: both tests are designed to be RED; no green-but-suspect
results to investigate.

**Zero-bugs-caught check**: N/A — this catalog was built from a known CRITICAL finding
(F169), not from exploratory analysis. The bug is already confirmed at
`scheduler.py:211-212` via `grep -n "last_review = fsrs_card.due" flashcore/scheduler.py`.
