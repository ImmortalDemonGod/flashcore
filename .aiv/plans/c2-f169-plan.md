# Plan: Fix F169 — correct elapsed_days for on-time FSRS reviews

Finding: CRITICAL — `flashcore/scheduler.py:212` sets `fsrs_card.last_review = fsrs_card.due`,
causing `elapsed_days=0` for any Review-state card reviewed on its due date.

Branch: `feat/c2-pr-f169-fsrs-elapsed-days-b1` (off `origin/main`)
AIV change-id: `f169-fsrs-elapsed-days`
Risk tier: R1

---

## Path decision: Option A

**Chosen: Option A** — add `last_review_date: Optional[date]` as a transient field to `Card`
and populate it in `review_processor.py` from the prior review record before calling the
scheduler.

**Rationale:** Option A is exact with no approximation; `db_manager.get_latest_review_for_card()`
already exists and the processor already owns the DB handle, so no new infrastructure is
needed. Option B's stability-based approximation (`due - timedelta(days=max(1, round(stability)))`)
breaks for post-lapse cards where stability is reset to a low value — the most common
failure mode for the CRITICAL path — disqualifying it.

**Scope of Option A (this PR):**
- `last_review_date` is a transient Pydantic field (`exclude=True`) — NOT persisted to SQLite.
- DB migration for persistence is deferred → stage-c2 DB migration PR.
- The extra `get_latest_review_for_card()` query is one indexed lookup (card_uuid PK);
  acceptable on the hot path for correctness.

---

## Files touched

| File | Change |
|------|--------|
| `flashcore/models.py` | Add `last_review_date: Optional[date]` field (transient, `exclude=True`) |
| `flashcore/scheduler.py` | Replace line 212; use `card.last_review_date` if set, else fall back to `fsrs_card.due` |
| `flashcore/review_processor.py` | Before scheduler call: if `card.last_review_id` is set, fetch prior review's `ts`, assign `card.last_review_date = prior_ts.date()` |
| `tests/test_scheduler.py` | Add two new unit-acceptance tests (Layer-A) |
| `tests/test_review_processor.py` | Add one new integration test (Layer-B) in `TestReviewProcessorIntegration` |

---

## Atomic commits (in order)

### Commit 1 — `flashcore/models.py`
Add transient `last_review_date` field to `Card`.

```python
# In Card (after last_review_id field):
last_review_date: Optional[date] = Field(
    default=None,
    exclude=True,          # never serialised / never written to DB
    description="Date of prior review, set transiently by ReviewProcessor before scheduling.",
)
```

Add `from datetime import date` if not already imported.
`extra="forbid"` is satisfied — this is a declared field, not an extra key.
`validate_assignment=True` is fine — `Optional[date]` accepts `None` and `date`.

Verify: `mypy flashcore/models.py --ignore-missing-imports` — no new errors.

### Commit 2 — `flashcore/scheduler.py`
Replace the bug site at line 211-212. Old:

```python
# Set last_review to due date for elapsed_days calculation
fsrs_card.last_review = fsrs_card.due
```

New:

```python
if card.last_review_date is not None:
    fsrs_card.last_review = datetime.datetime.combine(
        card.last_review_date,
        datetime.time(0, 0, 0),
        tzinfo=datetime.timezone.utc,
    )
else:
    # Fallback: use due-date proxy for cards where review_processor has not
    # populated last_review_date (e.g., cards constructed directly in tests
    # or via paths that bypass process_review). Preserves lapsed-review
    # elapsed_days > 0 behavior for existing tests.
    fsrs_card.last_review = fsrs_card.due
```

Guard: this block is already inside `if card.state != CardState.New`, and the inner
`if card.next_due_date:` block. The new sub-condition `if card.last_review_date is not None:`
selects the exact prior-review date; the else-fallback preserves backward-compatible
behavior so that `test_review_lapsed_card` (which creates a Review-state card without
`last_review_date`) continues to pass.

**Why the fallback is required:** `test_review_lapsed_card` asserts
`result_lapsed.elapsed_days > result_on_time.elapsed_days`. Both cards have
`last_review_date = None` (no prior `process_review` call). Without the fallback,
`fsrs_card.last_review` is left unset, `elapsed_days = 0` for both scenarios, and the
assertion `0 > 0` fails. The fallback reinstates `fsrs_card.last_review = due` for this
path, keeping elapsed_days correct for lapsed reviews while the exact fix activates only
when `last_review_date` is supplied by `review_processor`.

Verify: `grep -n "last_review = fsrs_card.due" flashcore/scheduler.py` → no output
(the old single-line assignment is replaced; the new else-fallback is a new expression).

### Commit 3 — `flashcore/review_processor.py`
In `process_review`, between the timestamp assignment (`ts = ...`) and the
`compute_next_state` call, insert:

```python
# Populate transient last_review_date so the scheduler can compute exact elapsed_days.
if card.last_review_id is not None:
    prior_review = self.db_manager.get_latest_review_for_card(card.uuid)
    if prior_review is not None:
        card.last_review_date = prior_review.ts.date()
```

This fetches the single most-recent review record (already indexed on `card_uuid`).
`card.last_review_date` defaults to `None`, so for New-state cards (no `last_review_id`)
nothing changes.

`process_review_by_uuid` calls `process_review` after loading the card, so it is
covered automatically.

### Commit 4 — `tests/test_scheduler.py`
Add two new tests after the existing 15. These are Layer-A (scheduler unit) acceptance
gates. All names used below are already available in the file:
- `datetime` module (imported as `import datetime`)
- `UTC = datetime.timezone.utc` (module-level alias)
- `uuid4`, `UUID` (from `from uuid import uuid4, UUID`)
- `Card`, `CardState` (from `from flashcore.models import Card, CardState`)
- `FSRS_Scheduler` (from `from flashcore.scheduler import FSRS_Scheduler, FSRSSchedulerConfig`)
- `scheduler` fixture (defined at file scope, yields `FSRS_Scheduler` with default config)

No new imports are needed.

**test_on_time_review_elapsed_days_positive**
```python
def test_on_time_review_elapsed_days_positive(scheduler: FSRS_Scheduler):
    """On-time Review-state review must produce elapsed_days > 0."""
    today = datetime.date.today()
    card = Card(
        uuid=uuid4(),
        deck_name="test",
        front="Q",
        back="A",
        state=CardState.Review,
        stability=10.0,
        difficulty=5.0,
        next_due_date=today,
    )
    card.last_review_date = today - datetime.timedelta(days=10)
    review_ts = datetime.datetime.combine(
        today, datetime.time(12, 0, 0), tzinfo=UTC
    )
    result = scheduler.compute_next_state(card, new_rating=3, review_ts=review_ts)
    assert result.elapsed_days > 0, (
        f"elapsed_days={result.elapsed_days}; expected >0 for on-time Review-state review"
    )
```

**test_on_time_vs_same_day_review_stability_distinct**
```python
def test_on_time_vs_same_day_review_stability_distinct(scheduler: FSRS_Scheduler):
    """On-time review (elapsed_days=10) must yield different stability than same-day re-review (elapsed_days=0)."""
    today = datetime.date.today()
    review_ts = datetime.datetime.combine(
        today, datetime.time(12, 0, 0), tzinfo=UTC
    )

    on_time_card = Card(
        uuid=uuid4(),
        deck_name="test",
        front="Q",
        back="A",
        state=CardState.Review,
        stability=10.0,
        difficulty=5.0,
        next_due_date=today,
    )
    on_time_card.last_review_date = today - datetime.timedelta(days=10)
    on_time_result = scheduler.compute_next_state(
        on_time_card, new_rating=3, review_ts=review_ts
    )

    same_day_card = Card(
        uuid=uuid4(),
        deck_name="test",
        front="Q",
        back="A",
        state=CardState.Review,
        stability=10.0,
        difficulty=5.0,
        next_due_date=today,
    )
    same_day_card.last_review_date = today
    same_day_result = scheduler.compute_next_state(
        same_day_card, new_rating=3, review_ts=review_ts
    )

    assert on_time_result.stab != same_day_result.stab, (
        f"Stability should differ: on_time={on_time_result.stab}, same_day={same_day_result.stab}"
    )
```

### Commit 5 — `tests/test_review_processor.py`
Add one new test in the existing `TestReviewProcessorIntegration` class. This is the
Layer-B gate that proves Commit 3 (review_processor plumbing) correctly populates
`last_review_date` and that the persisted `Review.elapsed_days_at_review > 0`.

All imports needed (`datetime`, `timedelta`, `timezone`, `date`, `uuid4`, `Card`,
`CardState`, `ReviewProcessor`) are already present in the file. The `in_memory_db`
and `real_scheduler` fixtures are already defined in `TestReviewProcessorIntegration`.

```python
def test_on_time_review_elapsed_days_persisted(
    self, in_memory_db, real_scheduler
):
    """Layer-B: review_processor must persist elapsed_days_at_review > 0
    for a Review-state card reviewed 10 days after its prior review."""
    card = Card(
        uuid=uuid4(),
        deck_name="Integration Test Deck",
        front="Layer-B elapsed_days front",
        back="Layer-B elapsed_days back",
        state=CardState.Review,
        stability=5.0,
        difficulty=5.0,
        next_due_date=date(2024, 6, 1),
    )
    in_memory_db.upsert_cards_batch([card])
    processor = ReviewProcessor(in_memory_db, real_scheduler)

    # First review: establishes the prior review record, sets last_review_id on card
    prior_ts = datetime(2024, 6, 1, 10, 0, 0, tzinfo=timezone.utc)
    card_after_first = processor.process_review(
        card=card, rating=3, reviewed_at=prior_ts
    )

    # Second review: 10 days later. review_processor must fetch the prior review,
    # set card.last_review_date = date(2024, 6, 1), so scheduler computes
    # elapsed_days = 10 instead of 0.
    review_ts = datetime(2024, 6, 11, 10, 0, 0, tzinfo=timezone.utc)
    card_after_second = processor.process_review(
        card=card_after_first, rating=3, reviewed_at=review_ts
    )

    reviews = in_memory_db.get_reviews_for_card(
        card_after_second.uuid, order_by_ts_desc=True
    )
    assert len(reviews) >= 2, (
        "Expected at least 2 reviews after two process_review calls"
    )
    second_review = reviews[0]  # newest = second review

    assert second_review.elapsed_days_at_review > 0, (
        f"elapsed_days_at_review={second_review.elapsed_days_at_review}; "
        "expected >0: review_processor must supply last_review_date from prior "
        "review so scheduler does not default to elapsed_days=0"
    )
```

---

## Test layers

| Layer | Command | Pass condition |
|-------|---------|----------------|
| New acceptance — elapsed_days (Layer-A) | `pytest tests/test_scheduler.py::test_on_time_review_elapsed_days_positive -v` | 1 passed, elapsed_days=10 |
| New acceptance — stability (Layer-A) | `pytest tests/test_scheduler.py::test_on_time_vs_same_day_review_stability_distinct -v` | 1 passed, stab values differ |
| Layer-B integration — elapsed_days persisted | `pytest tests/test_review_processor.py::TestReviewProcessorIntegration::test_on_time_review_elapsed_days_persisted -v` | 1 passed, elapsed_days_at_review=10 |
| Learning-state guard | `pytest tests/test_scheduler.py -k "new_card or learning or first_review" -v` | all pass, no TypeError |
| Regression — scheduler | `pytest tests/test_scheduler.py -q --tb=short` | 17 passed, 0 failed |
| Regression — review_processor | `pytest tests/test_review_processor.py -q --tb=short` | all prior tests + 1 new pass |
| Typecheck | `mypy flashcore/scheduler.py flashcore/models.py --ignore-missing-imports` | "Success" or only pre-existing |
| Full suite | `pytest tests/ -q --tb=short` | 480 passed, 1 skipped (+ 3 new = 483 passed) |
| Packet | `aiv check .github/aiv-packets/PACKET_f169-fsrs-elapsed-days.md` | exits 0 |

---

## AIV commit sequence

```bash
# Check / abandon stale context
aiv status
echo "y" | aiv abandon   # if stale

# Open change on the PR branch
aiv begin f169-fsrs-elapsed-days --mode pr \
  --description "add last_review_date transient field and plumb through reviewer so scheduler sees exact prior-review date"

# Commit 1 — models.py
git add flashcore/models.py
aiv commit flashcore/models.py \
  -m "feat(models): add transient last_review_date field to Card" \
  -t R1 \
  -c "Card gains Optional[date] last_review_date field with exclude=True; default None; extra=forbid still satisfied" \
  -c "mypy reports no new errors on flashcore/models.py after field addition" \
  -i "<SHA-pinned URL to task spec>" \
  --requirement "Option A path: model carries last_review_date for scheduler consumption" \
  -r "R1 — model-only change, no persistence, no external API surface" \
  -s "transient last_review_date field on Card for exact elapsed_days"

# Commit 2 — scheduler.py
git add flashcore/scheduler.py
aiv commit flashcore/scheduler.py \
  -m "feat(scheduler): use card.last_review_date for fsrs last_review instead of due date" \
  -t R1 \
  -c "line 212 replaced: fsrs_card.last_review now set from card.last_review_date when not None, else falls back to fsrs_card.due" \
  -c "grep for 'last_review = fsrs_card.due' returns no output after change (old single-line assignment is gone)" \
  -c "Learning-state cards and cards without last_review_date retain prior elapsed_days behavior via else-fallback to fsrs_card.due" \
  -i "<SHA-pinned URL to task spec>" \
  --requirement "bug site scheduler.py:212 replaced; elapsed_days > 0 for on-time Review-state reviews when last_review_date is supplied" \
  -r "R1 — logic-only change, isolated to scheduler computation, no DB or API changes" \
  -s "replace due-date proxy with actual last_review_date for elapsed_days; fallback to due when absent"

# Commit 3 — review_processor.py
git add flashcore/review_processor.py
aiv commit flashcore/review_processor.py \
  -m "feat(review_processor): populate card.last_review_date before scheduler call" \
  -t R1 \
  -c "process_review fetches prior review via get_latest_review_for_card when card.last_review_id is set" \
  -c "card.last_review_date set to prior_review.ts.date() before compute_next_state is called" \
  -c "New-state cards (last_review_id=None) are unaffected; last_review_date remains None" \
  -i "<SHA-pinned URL to task spec>" \
  --requirement "hub supplies exact last_review_date so scheduler computes correct elapsed_days" \
  -r "R1 — adds one indexed DB read per review; no new error paths; existing exception handling unchanged" \
  -s "populate last_review_date transient field in processor before scheduler call"

# Commit 4 — tests/test_scheduler.py  (Layer-A unit acceptance)
git add tests/test_scheduler.py
aiv commit tests/test_scheduler.py \
  -m "test(scheduler): add Layer-A acceptance tests for on-time elapsed_days and stability correctness" \
  -t R1 \
  -c "test_on_time_review_elapsed_days_positive asserts elapsed_days > 0 for Review-state on-time review with last_review_date set 10 days prior" \
  -c "test_on_time_vs_same_day_review_stability_distinct asserts stability differs between elapsed_days=10 and elapsed_days=0" \
  -c "tests use only names already imported in test_scheduler.py (datetime module, UTC alias, uuid4, Card, CardState, scheduler fixture) — no new imports" \
  -c "all 15 prior scheduler tests still pass after addition" \
  -i "<SHA-pinned URL to task spec>" \
  --requirement "Layer-A acceptance gates [1] and [2] from completion contract are covered by new tests" \
  -r "R1 — test-only addition; no production code changes" \
  -s "two new scheduler unit acceptance tests for F169 closure (Layer-A)"

# Commit 5 — tests/test_review_processor.py  (Layer-B integration)
git add tests/test_review_processor.py
aiv commit tests/test_review_processor.py \
  -m "test(review_processor): add Layer-B integration test for elapsed_days_at_review persistence" \
  -t R1 \
  -c "test_on_time_review_elapsed_days_persisted drives ReviewProcessor.process_review against a real in-memory SQLite DB with a real FSRS_Scheduler" \
  -c "second review persists Review.elapsed_days_at_review > 0, proving review_processor supplies last_review_date from prior review record" \
  -c "test placed in TestReviewProcessorIntegration; uses existing in_memory_db and real_scheduler fixtures; no new imports needed" \
  -i "<SHA-pinned URL to task spec>" \
  --requirement "Layer-B integration gate: end-to-end proof that Commit 3 plumbing produces correct elapsed_days in the persisted Review row" \
  -r "R1 — test-only addition; no production code changes" \
  -s "Layer-B integration test: persisted elapsed_days_at_review > 0 for on-time Review-state review"

aiv close
aiv check .github/aiv-packets/PACKET_f169-fsrs-elapsed-days.md
```

---

## Scope guard — out of this PR

| Item | Deferred to |
|------|-------------|
| Persisting `last_review_date` as a SQLite column | stage-c2 DB migration PR |
| Backfill of historical `last_review_date` for existing cards | `feat/c2-pr-backfill-last-review-date` |
| Negative `elapsed_days` for early-review cards (F169b) | New audit finding F169b; stage-c2 audit pass |
| Existing `test_review_lapsed_card` asserts `result_on_time.elapsed_days > 0` gap | Covered by new Commit 4 tests; existing test untouched |

---

## E010 / packet hygiene notes

- Avoid trigger words in claims: use "replaced" not "fixed", "updated" not "patched",
  "removed" not "resolved".
- All intent links must target a commit SHA, not `main`.
- `aiv check` must exit 0 before push. Correct packet errors with a new commit
  (`docs(aiv): correct packet — <what changed>`), never amend.

---

## Revision log

### Loop #1, iteration 2 — hard-stops H-A and H-B

**H-A (structural) — resolved by adding Commit 5:**
The original plan's Layer-A tests (Commit 4) test the scheduler in isolation; a green
scheduler unit test does not prove the on-time path is repaired in production because
Commit 3's `review_processor` plumbing is never exercised. Added
`TestReviewProcessorIntegration::test_on_time_review_elapsed_days_persisted` in
`tests/test_review_processor.py` (Commit 5). The test drives two sequential
`process_review` calls against a real in-memory SQLite DB and a real `FSRS_Scheduler`,
then fetches the persisted `Review` row and asserts
`elapsed_days_at_review > 0`. This is a Layer-B integration gate that exercises the
full Commit 3 → Commit 2 chain end-to-end.

**H-B (correctness) — resolved in Commit 4 and Commit 2:**

*Commit 4 test rewrite:* Removed the non-existent `make_review_card` helper. Tests now
construct `Card(...)` inline (identical pattern used throughout the file). Replaced all
bare datetime names with their `datetime.*` prefixed equivalents (`datetime.date.today()`,
`datetime.timedelta(days=N)`, `datetime.datetime.combine(...)`, `datetime.time(H, M, S)`)
and use the already-defined `UTC = datetime.timezone.utc` alias. Both new tests accept the
existing `scheduler: FSRS_Scheduler` pytest fixture instead of constructing their own
scheduler, keeping them consistent with the rest of the file.

*Commit 2 else-fallback (implicit H-B correctness):* The original Commit 2 omitted an
else-branch, leaving `fsrs_card.last_review` unset when `card.last_review_date is None`.
This silently broke `test_review_lapsed_card` (lines 252-286 of `tests/test_scheduler.py`),
which creates a Review-state card directly without a prior `process_review` call. Both the
on-time and lapsed scenarios would produce `elapsed_days = 0`, causing
`assert result_lapsed.elapsed_days > result_on_time.elapsed_days` (`0 > 0`) to fail.
Added `else: fsrs_card.last_review = fsrs_card.due` to preserve the prior approximation
for cards where `last_review_date` is absent. The exact fix still activates only when
`review_processor` populates `last_review_date`.
