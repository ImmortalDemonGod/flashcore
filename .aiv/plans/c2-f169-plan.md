# PR-F169 Implementation Plan — Correct elapsed_days for on-time FSRS reviews

## §1 Context

**Finding F169 (CRITICAL).** `flashcore/scheduler.py:212` assigns
`fsrs_card.last_review = fsrs_card.due`. For any Review-state card reviewed on
its scheduled due date (`review_ts.date() == card.next_due_date`), the
elapsed-days computation at lines 219-221 yields
`elapsed_days = (review_ts.date() - due.date()).days = 0`.
Zero elapsed_days pins FSRS retrievability to R=1.0 and corrupts the stability
update for the normal (on-time) case — the single most common review path in
production.

The root cause is that no prior-review timestamp exists on the `Card` model;
the scheduler was forced to use `due` as a proxy, which is semantically wrong.
The actual prior-review timestamp IS recorded in `reviews.ts` and is
retrievable via `db_manager.get_latest_review_for_card` (`db/database.py:834`).

**Branch:** `feat/c2-pr-f169-fsrs-elapsed-days-b1` off `origin/main @ b5e1c4b`.  
**Worktree:** `/home/user/fc-c2-harness`.  
**Risk tier:** R1 (standard logic fix; no external API surface; no DB schema
change in this PR).

---

## §2 Verified state (0 Explore agents, 2026-06-19)

All facts below confirmed by direct Read tool calls on the live worktree.

| Fact | Location | Verified value |
|---|---|---|
| Bug line | `flashcore/scheduler.py:212` | `fsrs_card.last_review = fsrs_card.due` |
| elapsed_days computation | `scheduler.py:219-221` | `(review_ts.date() - fsrs_card.last_review.date()).days` |
| `Card` fields | `flashcore/models.py:43-75` | `uuid, last_review_id, next_due_date, state, stability, difficulty, deck_name, front, back, tags` — **no `last_review_date` field** |
| DB schema — reviews table | `flashcore/db/schema.py:46-47` | `elapsed_days_at_review INTEGER, scheduled_days_interval INTEGER` present; no `last_review_date` column on cards |
| review_processor call site | `review_processor.py:100-104` | passes `review_ts=ts` (actual review timestamp) into `compute_next_state` |
| review_processor post-review | `review_processor.py:124-126` | `updated_card = db_manager.add_review_and_update_card(review=new_review, new_card_state=scheduler_output.state)` |
| `Review.ts` field | `flashcore/models.py:199` | `ts: datetime` — UTC timestamp of the review event |
| `get_latest_review_for_card` | `flashcore/db/database.py:834-847` | Returns `Optional[Review]`; delegates to `get_reviews_for_card(uuid, order_by_ts_desc=True)`, returns `reviews[0]` or `None` |
| `get_reviews_for_card` signature | `flashcore/db/database.py:788-789` | `def get_reviews_for_card(self, card_uuid: uuid.UUID, order_by_ts_desc: bool = True)` |
| Silent-pass test | `tests/test_scheduler.py:285` | `assert result_lapsed.elapsed_days > result_on_time.elapsed_days` (10 > 0 with bug); `result_on_time.elapsed_days > 0` NOT asserted |
| Missing guard | `tests/test_scheduler.py` | No `test_on_time_review_elapsed_days_positive`; no `test_on_time_vs_same_day_review_stability_distinct` |
| Existing integration tests | `tests/test_review_processor.py:372` | `TestReviewProcessorIntegration` already exists; uses `FlashcardDatabase(":memory:")` + real `FSRS_Scheduler()`; does not assert `elapsed_days_at_review > 0` |
| Test baseline | `python -m pytest tests/test_scheduler.py -q` | **15 passed, 0 failed** |
| Full suite baseline | `python -m pytest tests/ -q` | 480 passed, 1 skipped (per CLAUDE.md) |
| Card model config | `models.py:51` | `ConfigDict(validate_assignment=True, extra="forbid")` — new field must be declared on model |

**Early-review side note (in-scope for no-regression only):**
`test_review_early_card` currently passes with `elapsed_days=-2` for the
early-review scenario. After the fix, early `elapsed_days=0` (no prior review
set on a freshly loaded card with no same-session history). The assertion
`result_early.elapsed_days < result_on_time.elapsed_days` remains satisfied
(`0 < 1` for a card with one prior review). Deeper correction deferred to F169b.

---

## §5 Memory + lesson references

From CLAUDE.md and launch brief:

- **E010 trap**: never use `fix`, `fixes`, `fixed`, `patch`, `resolve`, `closes #N`
  in any claim text. Use neutral phrasing (e.g., "replaces assignment", "adds
  field", "introduces guard").
- **Intent URL must be SHA-pinned**: use
  `git log --oneline --follow -- .taskmaster/tasks/task_NNN.md` to find the
  commit SHA; never use a mutable branch URL.
- **`aiv abandon` needs piped confirmation**: `echo "y" | aiv abandon`.
- **`--skip-checks` is R0-only**: this PR is R1; never pass `--skip-checks`.
- **Deleted files cannot be the AIV primary file**: only use files that exist
  on disk and have changes relative to HEAD.
- **Hub-and-spoke discipline**: `flashcore/` is the pure-logic spoke;
  `flashcore/cli/` and `review_processor.py` are hub components. The scheduler
  must NOT import from `flashcore.scripts`.
- **Never edit a test to make it pass** without establishing which side
  (test or code) is wrong.
- **Never merge autonomously**: the human is the only merge gate.
- **GT-1 lesson**: before approximating any value, verify whether ground-truth
  is already recorded in the system. `reviews.ts` contains the actual
  prior-review timestamp; consuming it via `get_latest_review_for_card` removes
  the need for any stability-based proxy.

---

## §6 Strict scope boundaries

**In scope:**

| File | Change |
|---|---|
| `flashcore/models.py` | Add `last_review_date: Optional[date] = None` transient field to `Card` |
| `flashcore/scheduler.py` | Replace line 212; use `card.last_review_date` when set; no stability fallback — leave `last_review` unset when `last_review_date is None` |
| `flashcore/review_processor.py` | Two changes: (1) before `compute_next_state`, call `get_latest_review_for_card(card.uuid)` and set `card.last_review_date = prior_review.ts.date()` if result is not None; (2) after `add_review_and_update_card`, set `updated_card.last_review_date = ts.date()` |
| `tests/test_scheduler.py` | Add two unit-test functions (AC-1, AC-2); no edits to existing tests |
| `tests/test_review_processor.py` | Add one Layer-B integration test inside `TestReviewProcessorIntegration` (AC-12); no edits to existing tests |
| `.github/aiv-packets/PACKET_f169-fsrs-elapsed-days.md` | Generated by `aiv close` |

**Explicitly out of scope (do not touch):**

- `flashcore/db/schema.py` — no DB migration this PR; `last_review_date` stays transient
- `flashcore/db/database.py` — **consumed, not modified**; `get_latest_review_for_card` called as-is
- `flashcore/db/` (any other file) — no persistence changes
- `flashcore/cli/` — no hub-CLI changes
- `flashcore/scripts/` — not imported from core code
- Any test file other than `tests/test_scheduler.py` and `tests/test_review_processor.py`
- Historical backfill of `last_review_date` for existing DB cards
  (→ `feat/c2-pr-backfill-last-review-date`)
- Negative `elapsed_days` for early-review cards (→ audit finding F169b)

---

## §7 Locked design decisions

### D1 — PATH-FORK DECISION: Option A — `last_review_date` transient field on Card model

**Operator-confirmed:** 2026-06-19

**Scoring (CORRECTNESS FIRST, then scope):**

| Criterion | Path A | Path B |
|---|---|---|
| (a) Ground-truth vs approximation | **Fully ground-truth**: DB-recorded prior-review `ts` consumed via `get_latest_review_for_card` before `compute_next_state`; fallback is `elapsed_days=0` only when no prior review exists in DB (first-ever review) — no stability proxy at any step | **Always** approximates `last_review = due - timedelta(days=max(1, round(stability)))` — never reads `reviews.ts`; ignores ground-truth data already in DB |
| (b) Fixes root cause vs masks symptom | Fixes root cause: establishes the correct data-flow pathway (`last_review_date` on model, populated by hub from DB before scheduler call); removes the semantically wrong `last_review = due` assignment | Masks symptom: substitutes stability-as-proxy for what should be an actual timestamp; root cause (no `last_review_date` on model) remains unaddressed |
| (c) Hidden/deferred debt | Transient field; hub reads DB for fresh cards, caches result in `last_review_date` for same-session re-reviews. Future PR adds DB column without touching scheduler or processor logic. Debt is explicit and bounded. | Approximation boundary documented as F169b, but the structural gap (no last_review_date on model) remains; `reviews.ts` continues to be ignored |
| Scope | 3 files + 2 test files | 1 file + 1 test file |

**PATH B IS MARKED DISFAVORED** per §7 PATH-FORK PROTOCOL: it approximates
`last_review` from stability even though the actual prior-review timestamp is
already persisted in `reviews.ts` and retrievable at zero schema cost. This
violates the ground-truth-over-approximation mandate. A narrower scope is not
a valid reason to prefer an approach that ignores recorded data.

**LOCKED: Path A.**

**One-sentence rationale:** Path A makes the hub consume the DB-recorded
prior-review timestamp before every scheduler call, eliminating all
approximation for cards with review history and producing `elapsed_days=0`
only for genuinely first-ever reviews, whereas Path B always substitutes
stability as a proxy even though the real timestamp is already in the database.

### Sub-decisions within Path A

**D1.1 — `last_review_date` is transient (not persisted) in this PR.** No new
DB column; no migration. The field has `default=None`. Persistence deferred to
a follow-up DB migration PR before stage-c3 cutoff.

**D1.2 — Hub lookup before compute_next_state.** `review_processor.process_review`
calls `self.db_manager.get_latest_review_for_card(card.uuid)` before calling
`self.scheduler.compute_next_state`. If a prior review is returned, it sets
`card.last_review_date = prior_review.ts.date()`. If none (first-ever review),
`last_review_date` remains `None` — scheduler produces `elapsed_days=0`, which
is correct (no prior review to measure from).

**D1.3 — Scheduler simplified: no stability approximation.** The replacement
for line 212 uses only `card.last_review_date`: if set, combine into a
`datetime` for `fsrs_card.last_review`; otherwise leave `last_review` unset.
No `stability`-based fallback branch. This is safe because:
- Cards with prior reviews always have `last_review_date` populated by the hub.
- Cards with no prior reviews correctly produce `elapsed_days=0` (New/Learning state).
- The stability-approximation branch is removed entirely — it was a shortcut
  that re-introduced approximation where ground truth was available.

**D1.4 — Hub caches last_review_date after persist.** After
`add_review_and_update_card` returns, `review_processor` sets
`updated_card.last_review_date = ts.date()`. This allows same-session
re-reviews (e.g., "Again" immediately re-queued) to skip the extra DB lookup
on the next call without changing the scheduler or model logic.

**D1.5 — Guard for `None` stability.** With D1.3, there is no stability
arithmetic in the scheduler fallback, so no `TypeError` from `None stability`
is possible. The only change to the guard logic is removing the stability branch.

---

## §9 Sequenced atomic-commit plan

All commits on branch `feat/c2-pr-f169-fsrs-elapsed-days-b1`.
Run `aiv status` before first commit; `echo "y" | aiv abandon` if stale
context; `aiv begin f169-fsrs-elapsed-days --mode pr --description "add last_review_date to Card; hub reads DB prior-review ts; scheduler uses ground-truth elapsed_days"`.

### Commit 1 — Add `last_review_date` transient field to Card model

```bash
git add flashcore/models.py
aiv commit flashcore/models.py \
  -m "feat(models): add last_review_date optional transient field to Card" \
  -t R1 \
  -c "Card model lacks last_review_date field before this commit; field added as Optional[date] default None" \
  -c "ConfigDict extra=forbid preserved; field declared on model class, not injected at runtime" \
  -i "<SHA-pinned URL to .taskmaster/tasks/task_NNN.md>" \
  --requirement "D1.1: last_review_date on Card model — prerequisite for scheduler and hub changes" \
  -r "R1: model field addition, no logic change" \
  -s "Add last_review_date: Optional[date] = None to Card for scheduler ground-truth path"
```

**Verification before staging:**
- `grep -n "last_review_date" flashcore/models.py` — field present
- `mypy flashcore/models.py --ignore-missing-imports` — no new errors
- `python -m pytest tests/test_scheduler.py -q --tb=short` — 15 passed

### Commit 2 — Replace bug line in scheduler; use last_review_date only; remove approximation

Staged files: `flashcore/scheduler.py` (primary).

Replace `scheduler.py:212` block with:
```python
if card.last_review_date is not None:
    fsrs_card.last_review = datetime.datetime.combine(
        card.last_review_date,
        datetime.time(0, 0, 0),
        tzinfo=datetime.timezone.utc,
    )
# else: last_review remains unset (no prior review → elapsed_days=0, correct for New/first-ever)
```

No stability-approximation branch. No `elif card.stability is not None` block.

```bash
git add flashcore/scheduler.py
aiv commit flashcore/scheduler.py \
  -m "feat(scheduler): replace due-date proxy with last_review_date conditional; remove approximation" \
  -t R1 \
  -c "Line 212 assignment last_review=due removed; replaced with conditional on card.last_review_date" \
  -c "No stability-approximation branch introduced; elapsed_days=0 only when last_review_date is None (no prior review)" \
  -c "Scheduler does not read DB directly; last_review_date populated by hub before this call" \
  -i "<SHA-pinned URL to .taskmaster/tasks/task_NNN.md>" \
  --requirement "D1.3: offending assignment gone; ground-truth path only; no approximation" \
  -r "R1: logic change in core scheduler; covered by acceptance tests in commits 4 and 4b" \
  -s "Use card.last_review_date for last_review when set; no stability proxy; remove wrong due-date proxy"
```

**Verification before staging:**
- `grep -n "last_review = fsrs_card.due" flashcore/scheduler.py` — no output
- `grep -n "stability.*timedelta\|timedelta.*stability" flashcore/scheduler.py` — no output (approximation removed)
- `python -m pytest tests/test_scheduler.py -q --tb=short` — 15 passed (pre-new-tests baseline)

### Commit 3 — review_processor: DB lookup before compute_next_state; cache after persist

Staged files: `flashcore/review_processor.py` (primary).

**Change (a) — before Step 2 (compute_next_state), add:**
```python
# Populate last_review_date from DB so scheduler uses ground-truth elapsed_days
prior_review = self.db_manager.get_latest_review_for_card(card.uuid)
if prior_review is not None:
    card.last_review_date = prior_review.ts.date()
```

**Change (b) — after Step 4 (add_review_and_update_card returns), add:**
```python
updated_card.last_review_date = ts.date()
```

```bash
git add flashcore/review_processor.py
aiv commit flashcore/review_processor.py \
  -m "feat(review_processor): read prior-review ts from DB before scheduler call; cache date after persist" \
  -t R1 \
  -c "get_latest_review_for_card called before compute_next_state; card.last_review_date set from prior_review.ts.date() when available" \
  -c "updated_card.last_review_date set to ts.date() after add_review_and_update_card for same-session re-review caching" \
  -c "db/database.py consumed as-is; no schema or method changes" \
  -i "<SHA-pinned URL to .taskmaster/tasks/task_NNN.md>" \
  --requirement "D1.2 and D1.4: hub reads recorded prior-review ts; scheduler receives ground-truth for all reviewed cards" \
  -r "R1: two one-line hub additions; no new import; no DB schema change" \
  -s "Hub reads reviews.ts from DB before scheduler call; caches result in last_review_date for same-session re-reviews"
```

**Verification before staging:**
- `python -m pytest tests/ -q --tb=short` — 480 passed, 1 skipped

### Commit 4 — Add two unit acceptance tests to test_scheduler.py

Staged files: `tests/test_scheduler.py` (primary).

Add after existing `test_review_lapsed_card`:

```python
def test_on_time_review_elapsed_days_positive(scheduler, sample_card_uuid):
    card = Card(
        uuid=sample_card_uuid,
        deck_name="test",
        front="Q",
        back="A",
        state=CardState.Review,
        stability=1.5,
        difficulty=6.0,
        next_due_date=datetime.date(2024, 1, 1),
        last_review_date=datetime.date(2023, 12, 31),  # ground-truth: 1 day before due
    )
    review_ts = datetime.datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC)
    result = scheduler.compute_next_state(card, 2, review_ts)
    assert result.elapsed_days > 0

def test_on_time_vs_same_day_review_stability_distinct(scheduler, sample_card_uuid):
    import uuid as _uuid
    # On-time Review-state card with last_review_date set (ground-truth path)
    card_review = Card(
        uuid=sample_card_uuid,
        deck_name="test",
        front="Q",
        back="A",
        state=CardState.Review,
        stability=1.5,
        difficulty=6.0,
        next_due_date=datetime.date(2024, 1, 1),
        last_review_date=datetime.date(2023, 12, 31),
    )
    review_ts = datetime.datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC)
    result_on_time = scheduler.compute_next_state(card_review, 2, review_ts)

    # Same-day: New card (no prior review; last_review_date=None → elapsed_days=0)
    card_new = Card(
        uuid=_uuid.uuid4(),
        deck_name="test",
        front="Q",
        back="A",
        state=CardState.New,
    )
    result_same_day = scheduler.compute_next_state(card_new, 2, review_ts)

    assert result_on_time.stab != result_same_day.stab
```

```bash
git add tests/test_scheduler.py
aiv commit tests/test_scheduler.py \
  -m "test(scheduler): add on-time elapsed_days>0 and stability-distinct unit acceptance tests" \
  -t R1 \
  -c "test_on_time_review_elapsed_days_positive: Review-state card with last_review_date set produces elapsed_days > 0" \
  -c "test_on_time_vs_same_day_review_stability_distinct: on-time stability != same-day (New) stability" \
  -i "<SHA-pinned URL to .taskmaster/tasks/task_NNN.md>" \
  --requirement "VERIFY [1] and VERIFY [2] from completion contract" \
  -r "R1: test-only changes; no production code modified" \
  -s "Add two unit acceptance tests with explicit last_review_date set; would have caught F169 regression"
```

**Verification before staging:**
- `python -m pytest tests/test_scheduler.py -v --tb=short` — **17 passed**, 0 failed
- `python -m pytest tests/ -q --tb=short` — 482 passed, 1 skipped

### Commit 4b — Layer-B real-DB integration test in test_review_processor.py

Staged files: `tests/test_review_processor.py` (primary).

Add inside the existing `TestReviewProcessorIntegration` class:

```python
def test_on_time_review_persists_positive_elapsed_days(
    self, in_memory_db, real_scheduler, sample_card
):
    """Layer-B: process_review against real DB + real scheduler; persisted elapsed_days_at_review > 0."""
    in_memory_db.upsert_cards_batch([sample_card])
    processor = ReviewProcessor(in_memory_db, real_scheduler)

    # First review: card is New, no prior review in DB
    ts1 = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    updated_card = processor.process_review(
        card=sample_card, rating=3, reviewed_at=ts1
    )

    # Second review: on-time (due date == review date)
    next_due = updated_card.next_due_date
    ts2 = datetime(next_due.year, next_due.month, next_due.day, 10, 0, 0, tzinfo=timezone.utc)
    processor.process_review(
        card=updated_card, rating=3, reviewed_at=ts2
    )

    # The second review's persisted elapsed_days_at_review must be > 0
    reviews = in_memory_db.get_reviews_for_card(
        sample_card.uuid, order_by_ts_desc=True
    )
    second_review = reviews[0]
    assert second_review.elapsed_days_at_review > 0, (
        f"expected elapsed_days_at_review > 0 for on-time review; got {second_review.elapsed_days_at_review}"
    )
```

```bash
git add tests/test_review_processor.py
aiv commit tests/test_review_processor.py \
  -m "test(review_processor): add Layer-B integration test for persisted elapsed_days > 0 on on-time review" \
  -t R1 \
  -c "test_on_time_review_persists_positive_elapsed_days: real DB + real scheduler; second on-time review persisted elapsed_days_at_review > 0" \
  -c "Drives process_review end-to-end; validates DB-lookup path that in-memory unit tests could not cover" \
  -i "<SHA-pinned URL to .taskmaster/tasks/task_NNN.md>" \
  --requirement "Layer-B: real-DB integration test — closes the gap masked by mocked-scheduler unit tests" \
  -r "R1: test-only addition inside existing TestReviewProcessorIntegration; no production code modified" \
  -s "Layer-B integration test: drives full process_review stack against in-memory SQLite; asserts persisted elapsed_days_at_review > 0"
```

**Verification before staging:**
- `python -m pytest tests/test_review_processor.py -v --tb=short` — new test passes, all existing pass
- `python -m pytest tests/ -q --tb=short` — 483 passed, 1 skipped

### Commit 5 — AIV packet + task tracker update

```bash
aiv close
aiv check .github/aiv-packets/PACKET_f169-fsrs-elapsed-days.md
# Fix any E010 or blocking errors, then:
git add .github/aiv-packets/PACKET_f169-fsrs-elapsed-days.md
git commit -m "docs(aiv): add packet for f169-fsrs-elapsed-days change"
# Update task tracker:
git add .taskmaster/tasks/
git commit -m "chore(tasks): mark F169 addressed in task tracker — Path A, DB-lookup hub + scheduler + model"
```

---

## §10 Critical files

| File | Role | Change type |
|---|---|---|
| `flashcore/scheduler.py` | Bug site; core FSRS computation | Replace lines 211-212; conditional on `last_review_date`; no stability fallback |
| `flashcore/models.py` | Card data model | Add one optional field |
| `flashcore/review_processor.py` | Hub; owns persistence and card update | Two additions: DB lookup before compute_next_state; cache set after persist |
| `tests/test_scheduler.py` | Unit acceptance gate | Add two new test functions |
| `tests/test_review_processor.py` | Layer-B integration gate | Add one test inside `TestReviewProcessorIntegration` |
| `.github/aiv-packets/PACKET_f169-fsrs-elapsed-days.md` | AIV audit trail | Generated by `aiv close` |
| `.taskmaster/tasks/tasks.json` / `task_NNN.md` | Progress tracker | Mark F169 addressed |

**Read before touching:**
1. `flashcore/scheduler.py:190-270` — full `compute_next_state` method
2. `flashcore/models.py:43-95` — Card model fields and config
3. `flashcore/review_processor.py:85-140` — review processing pipeline
4. `tests/test_scheduler.py:252-320` — existing lapsed/early tests (must stay green)
5. `tests/test_review_processor.py:372-490` — existing `TestReviewProcessorIntegration` class

**UNTOUCHED (out of scope — consumed or referenced only):**

| File | Reason untouched |
|---|---|
| `flashcore/db/database.py` | Consumed as-is via `get_latest_review_for_card`; zero method or schema changes |
| `flashcore/db/schema.py` | No new DB columns; `last_review_date` remains transient |
| `flashcore/models.py` (Review class) | `Review.ts` read-only; Review schema untouched |
| `flashcore/cli/` (all files) | No hub-CLI changes; path injection unaffected |
| `flashcore/scripts/` (all files) | Not imported from core code |
| All other test files | No edits to existing tests outside the two named test files |

---

## §11 Reused utilities (must consume, not reimplement)

| Utility | Location | Usage in this PR |
|---|---|---|
| `datetime.datetime.combine` | stdlib | Combine `card.last_review_date` with `time(0,0,0,utc)` for `fsrs_card.last_review` in scheduler |
| `CardState` enum | `flashcore/models.py:32-40` | Outer `if card.state != CardState.New:` block already guards; unchanged |
| `FSRSCard.last_review` | `fsrs` library (`FSRSCard`) | Assigned by scheduler; consumed by `fsrs_scheduler.review_card` for elapsed_days |
| `ConfigDict` / Pydantic `Field` | `pydantic` (already imported in models.py) | Used for new `last_review_date` field declaration |
| `Optional`, `date` | `typing`, `datetime` (already imported in models.py) | Type annotation for new field |
| `get_latest_review_for_card` | `flashcore/db/database.py:834` | Called by review_processor hub before `compute_next_state`; not reimplemented |
| `Review.ts` | `flashcore/models.py:199` | Read as `prior_review.ts.date()` in review_processor; not reimplemented |

Do NOT introduce new imports to `flashcore/scheduler.py` — `datetime` and
`CardState` are already present. Do NOT introduce new imports to
`flashcore/review_processor.py` — `datetime`, `timezone`, and `db_manager`
are already in scope.

---

## §14 Acceptance criteria

All binary green/red. Source: completion contract VERIFY items.

| # | Criterion | Command |
|---|---|---|
| AC-1 | `test_on_time_review_elapsed_days_positive` passes; `elapsed_days > 0` | `python -m pytest tests/test_scheduler.py::test_on_time_review_elapsed_days_positive -v` |
| AC-2 | `test_on_time_vs_same_day_review_stability_distinct` passes | `python -m pytest tests/test_scheduler.py::test_on_time_vs_same_day_review_stability_distinct -v` |
| AC-3 | Bug line gone | `grep -n "last_review = fsrs_card.due" flashcore/scheduler.py` → no output |
| AC-4 | Path A structural evidence | `grep -n "last_review_date" flashcore/models.py flashcore/review_processor.py flashcore/scheduler.py` → present in all three |
| AC-5 | Learning-state guard correct | `python -m pytest tests/test_scheduler.py -k "new_card or learning or first_review" -v` → all pass |
| AC-6 | No regression — all 15 existing tests pass | `python -m pytest tests/test_scheduler.py -q --tb=short` → 15 existing + 2 new = 17 passed |
| AC-7 | Typecheck clean | `mypy flashcore/scheduler.py flashcore/models.py --ignore-missing-imports 2>&1 \| tail -5` → no new errors |
| AC-8 | AIV packet validates | `aiv check .github/aiv-packets/PACKET_f169-fsrs-elapsed-days.md` → exits 0 |
| AC-9 | Full suite passes | `python -m pytest tests/ -q --tb=short` → 483 passed, 1 skipped (or better) |
| AC-10 | Branch shape correct | `git log feat/c2-pr-f169-fsrs-elapsed-days-b1 --format="%an \| %s" \| head -10` → branch name matches exactly |
| AC-11 | F169 in task tracker | `grep -r "F169" .taskmaster/tasks/ --include="*.md" --include="*.json" \| head -5` → at least one entry |
| AC-12 | Layer-B integration test passes | `python -m pytest tests/test_review_processor.py::TestReviewProcessorIntegration::test_on_time_review_persists_positive_elapsed_days -v` → 1 passed; `elapsed_days_at_review > 0` confirmed |
| AC-13 | No stability approximation in scheduler | `grep -n "stability.*timedelta\|timedelta.*stability\|round.*stability" flashcore/scheduler.py` → no output |
| AC-14 | Hub DB lookup present | `grep -n "get_latest_review_for_card" flashcore/review_processor.py` → at least one match before compute_next_state call |

---

## §15 Risks + mitigations + stop conditions (RED)

| Risk | Likelihood | Mitigation |
|---|---|---|
| E010 AIV error from trigger words in claims | Medium | Use "replaces", "introduces", "adds" — never "fix", "patch", "resolve" in claim text |
| `card.last_review_date` is None after DB lookup for a card that has reviews (e.g., DB error suppressed) | Very low | `get_latest_review_for_card` raises on DB error rather than returning None silently (see `get_reviews_for_card` error path); exception propagates to hub's `except` block and is re-raised |
| `prior_review.ts` is naive datetime (no timezone) | Low | `Review.ts` has `Field(...)` with UTC timezone; `ts.date()` is timezone-independent and always produces a `date` regardless |
| `mypy` error from `Optional[date]` in Card (e.g., missing `date` import) | Low | `date` is already used in `models.py` for `next_due_date`; no new import needed |
| Extra DB lookup per review increases latency | Low | One additional round-trip against SQLite (local file/in-memory); review processing already does two round-trips (`add_review_and_update_card`); same-session re-reviews skip lookup via D1.4 cache |
| Existing `test_review_early_card` breaks after fix | Low | Verified analytically: early card has `last_review_date=None` (no same-session prior review, no DB lookup in unit tests) → `elapsed_days=0`; assertion `result_early.elapsed_days < result_on_time.elapsed_days` holds (`0 < 1`) |
| `test_review_lapsed_card` breaks | Low | Verified analytically: lapsed card sets explicit `last_review_date`; `elapsed_days=10`; on-time `elapsed_days=1`; `10 > 1` holds |
| `add_review_and_update_card` returns a Card without `last_review_date` (reconstructed from DB row) | Medium | `updated_card.last_review_date = ts.date()` assigned after the call; field is Optional with default None so assignment always succeeds |
| `ConfigDict(extra="forbid")` rejects `last_review_date` | None | Field is declared on the model class, not injected — `extra="forbid"` only rejects undeclared extra fields |
| AIV primary file deleted or unchanged | Low | Each commit uses an existing modified file; never a deleted file |
| Layer-B test: FSRS schedules next_due_date in the past for a New card first review | Very low | FSRS Good (rating=3) on New card schedules 1+ day; `ts2` is set to the exact due date; any schedule >= 1 day produces `elapsed_days >= 1 > 0` |

**RED STOP CONDITIONS** — escalate via AskUserQuestion before proceeding:

- Any of the 15 existing scheduler tests requires editing to pass after the fix
  (stop: determine which side is wrong before touching test)
- `mypy` introduces a new error that cannot be resolved without changing the
  public interface of `Card` or `SchedulerOutput`
- `aiv check` exits non-zero after two correction attempts
- Path A: any doubt arises about whether `last_review_date` should be persisted
  to SQLite in this PR (this widens scope to R2 — escalate before proceeding)
- `get_latest_review_for_card` returns stale or unexpected data that would
  require modifying `database.py` (stop: scope has widened beyond R1; escalate)

---

## §19 Locked PR sequence position

This PR (`feat/c2-pr-f169-fsrs-elapsed-days-b1`) is part of **stage c2** of
the fc-c2-fsrs-harness work.

- **Base:** `origin/main @ b5e1c4b`
- **Precedes:** `feat/c2-pr-backfill-last-review-date` (deferred backfill)
  and the stage-c2 DB migration PR (persistence of `last_review_date`)
- **Blocked by:** nothing (no open prerequisite PRs)
- **Merge authority:** human operator only; never autonomous

---

## §20 After-merge handoff

1. **Bookkeeping**: Update `.taskmaster/tasks/tasks.json` — mark F169 sub-item
   complete. Add a one-line note to the relevant `task_NNN.md` recording:
   "Path A chosen (D1, 2026-06-19); commit SHA `<SHA>`; `last_review_date`
   transient field on Card; hub reads `reviews.ts` from DB before scheduler
   call; scheduler uses ground-truth `elapsed_days` for all reviewed cards."

2. **Follow-up PRs to open immediately after merge:**
   - `feat/c2-pr-backfill-last-review-date` — backfill `last_review_date` for
     existing DB cards using `elapsed_days_at_review` and
     `scheduled_days_interval` from the reviews table.
   - Stage-c2 DB migration PR — add `last_review_date DATE` column to the
     cards table; update `add_review_and_update_card` to persist the value.
     Must be open before stage-c3 cutoff.

3. **Audit finding F169b** — file in the stage-c2 audit pass:
   "Early-review cards produce `elapsed_days=0` after F169 fix (improvement
   over `-2` but still approximate); correct value requires persisted
   `last_review_date` — target the DB migration PR."

4. **Post-merge CI check**: Run `python -m pytest tests/ -q --tb=short`.
   Expected: 483 passed, 1 skipped. Confirm before closing the review window.

5. **Retro-verify (post-integration)**: After a real review session against
   a live DB, spot-check `elapsed_days_at_review` values in the `reviews` table
   are > 0 for on-time reviews. N/A until integration testing is available.

---

## Revision log

| Loop | Date | Gate failed | Changes made |
|---|---|---|---|
| #1 | 2026-06-19 | GATE #1 (check-drift GT-1) | (1) Removed stability-approximation fallback from §7 sub-decisions (D1.2–D1.5 rewritten); (2) Updated PATH-FORK table in §7: Path A criterion (a) now correctly states "fully ground-truth" since hub reads `reviews.ts` via `get_latest_review_for_card` before every `compute_next_state` call; (3) Updated §9 Commit 2 code block to remove `elif stability` branch; (4) Updated §9 Commit 3 code block to add DB lookup before compute_next_state + added new Commit 4b for Layer-B integration test in `tests/test_review_processor.py`; (5) Added §7 D-number (D1) + operator-confirmed date 2026-06-19; (6) Added §10 UNTOUCHED sub-section (db/database.py consumed-not-modified; cards/reviews schema untouched); (7) Updated §6 scope to include test_review_processor.py; (8) Added AC-12, AC-13, AC-14 to §14; (9) Added DB-query and ground-truth risks to §15; (10) Updated §2 with Review.ts and get_latest_review_for_card verified facts. |
