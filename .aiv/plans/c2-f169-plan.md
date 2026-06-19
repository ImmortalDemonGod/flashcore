# Plan: Fix F169 — correct elapsed_days for on-time FSRS reviews

**Finding:** CRITICAL — `flashcore/scheduler.py:212` sets `fsrs_card.last_review = fsrs_card.due`,
causing `elapsed_days=0` for any Review-state card reviewed on its due date, which pins FSRS
retrievability to R=1.0 and corrupts stability updates for the normal (on-time) case.

**Branch:** `feat/c2-pr-f169-fsrs-elapsed-days-b1` (off `origin/main`)  
**AIV change-id:** `f169-fsrs-elapsed-days`  
**Risk tier:** R1 (standard logic fix; no DB schema changes)

---

## Path Decision: Option A

**Chosen:** Option A — Add `last_review_date: Optional[date]` as a transient field to `Card` and populate it in `review_processor.py` before the scheduler call.

**One-sentence rationale:** Option A provides an exact fix (no approximation boundaries) while aligning with the hub-and-spoke architecture, requiring only transient model changes (no DB schema widening), and remaining R1-scoped.

**Why not Option B:** Stability-based approximation (`fsrs_card.due - timedelta(days=max(1, round(card.stability)))`) fails for post-lapse cards where stability resets to low values, re-introducing the bug for the most common failure mode and creating hard-to-debug approximation boundaries.

**Scope of Option A (this PR):**
- `last_review_date` is a transient Pydantic field (`exclude=True`) — NOT persisted to SQLite.
- DB migration for persistence deferred → stage-c2 DB migration PR.
- Processor fetches prior-review timestamp from existing `reviews` table (one indexed lookup).
- Scheduler uses `last_review_date` if set, else defaults to `due` (for Learning-state cards).

---

## Files touched

| File | Change |
|------|--------|
| `flashcore/models.py` | Add `last_review_date: Optional[date]` field (transient, `exclude=True`) |
| `flashcore/scheduler.py` | Replace line 212; use `card.last_review_date` if set, else skip `last_review` assignment |
| `flashcore/review_processor.py` | Before scheduler call: if `card.last_review_id` is set, fetch prior review's `ts`, assign `card.last_review_date = prior_ts.date()` |
| `tests/test_scheduler.py` | Add two new tests (acceptance gates) |

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
# If last_review_date is None, leave fsrs_card.last_review unset so the
# elapsed_days branch at line 218 falls through to elapsed_days=0 (Learning path).
```

Guard: this block is already inside `if card.state != CardState.New`, and the inner
`if card.next_due_date:` block. The new sub-condition `if card.last_review_date is not None:`
prevents any arithmetic on None stability.

Verify: `grep -n "last_review = fsrs_card.due" flashcore/scheduler.py` → no output.

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
Add two new tests after the existing 15.

**test_on_time_review_elapsed_days_positive**
```python
def test_on_time_review_elapsed_days_positive():
    """On-time Review-state review must produce elapsed_days > 0."""
    today = date.today()
    card = make_review_card(next_due_date=today, stability=10.0, difficulty=5.0)
    card.last_review_date = today - timedelta(days=10)
    scheduler = FSRS_Scheduler()
    review_ts = datetime.combine(today, time(12, 0, 0), tzinfo=timezone.utc)
    result = scheduler.compute_next_state(card, new_rating=3, review_ts=review_ts)
    assert result.elapsed_days > 0, (
        f"elapsed_days={result.elapsed_days}; expected >0 for on-time Review-state review"
    )
```

**test_on_time_vs_same_day_review_stability_distinct**
```python
def test_on_time_vs_same_day_review_stability_distinct():
    """On-time review (elapsed_days=10) must yield different stability than same-day re-review (elapsed_days=0)."""
    today = date.today()
    scheduler = FSRS_Scheduler()
    review_ts = datetime.combine(today, time(12, 0, 0), tzinfo=timezone.utc)

    # On-time: reviewed 10 days after last review, which was on due date
    on_time_card = make_review_card(next_due_date=today, stability=10.0, difficulty=5.0)
    on_time_card.last_review_date = today - timedelta(days=10)
    on_time_result = scheduler.compute_next_state(on_time_card, new_rating=3, review_ts=review_ts)

    # Same-day re-review: last_review_date == review date → elapsed_days=0
    same_day_card = make_review_card(next_due_date=today, stability=10.0, difficulty=5.0)
    same_day_card.last_review_date = today
    same_day_result = scheduler.compute_next_state(same_day_card, new_rating=3, review_ts=review_ts)

    assert on_time_result.stab != same_day_result.stab, (
        f"Stability should differ: on_time={on_time_result.stab}, same_day={same_day_result.stab}"
    )
```

Assumes a `make_review_card(next_due_date, stability, difficulty)` helper already
exists in the test file (or create one inline). The `timedelta` and `date` imports
should already be present; add `time` and `timezone` if missing.

---

## Test layers

| Layer | Command | Pass condition |
|-------|---------|----------------|
| New acceptance — elapsed_days | `pytest tests/test_scheduler.py::test_on_time_review_elapsed_days_positive -v` | 1 passed, elapsed_days=10 |
| New acceptance — stability | `pytest tests/test_scheduler.py::test_on_time_vs_same_day_review_stability_distinct -v` | 1 passed, stab values differ |
| Learning-state guard | `pytest tests/test_scheduler.py -k "new_card or learning or first_review" -v` | all pass, no TypeError |
| Regression — scheduler | `pytest tests/test_scheduler.py -q --tb=short` | 17 passed, 0 failed |
| Typecheck | `mypy flashcore/scheduler.py flashcore/models.py --ignore-missing-imports` | "Success" or only pre-existing |
| Full suite | `pytest tests/ -q --tb=short` | 480 passed, 1 skipped |
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
  -c "line 212 removed; fsrs_card.last_review now set from card.last_review_date when not None" \
  -c "grep for 'last_review = fsrs_card.due' returns no output after change" \
  -c "Learning-state cards (last_review_date=None) retain elapsed_days=0 via existing else branch" \
  -i "<SHA-pinned URL to task spec>" \
  --requirement "bug site scheduler.py:212 replaced; elapsed_days > 0 for on-time Review-state reviews" \
  -r "R1 — logic-only change, isolated to scheduler computation, no DB or API changes" \
  -s "replace due-date proxy with actual last_review_date for elapsed_days"

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

# Commit 4 — tests/test_scheduler.py
git add tests/test_scheduler.py
aiv commit tests/test_scheduler.py \
  -m "test(scheduler): add acceptance tests for on-time elapsed_days and stability correctness" \
  -t R1 \
  -c "test_on_time_review_elapsed_days_positive asserts elapsed_days > 0 for Review-state on-time review" \
  -c "test_on_time_vs_same_day_review_stability_distinct asserts stability differs between elapsed_days=10 and elapsed_days=0" \
  -c "all 15 prior scheduler tests still pass after addition" \
  -i "<SHA-pinned URL to task spec>" \
  --requirement "acceptance gates [1] and [2] from completion contract are covered by new tests" \
  -r "R1 — test-only addition; no production code changes" \
  -s "two new scheduler acceptance tests for F169 closure"

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
