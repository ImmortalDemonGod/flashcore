# PR-F169 - Correct elapsed_days for on-time FSRS reviews

> Config: no `.aiv-workflow.yml` found at repo root. All values below are skill defaults.
> Defaults applied:
> - `launch_brief.out_dir`: `.aiv/launch-briefs/`
> - `launch_brief.pr_classes`: default vocabulary
> - `branch.pattern`: `feat/{stage}-pr-{slug}-{brief}` → `feat/c2-pr-f169-fsrs-elapsed-days-b1`
> - `branch.base`: `origin/main`
> - `aiv.cli`: `aiv`, `aiv.check_cmd`: `aiv check`, `aiv.packets_dir`: `.github/aiv-packets`
> - `ci.test_cmd`: `python -m pytest tests/ -q --tb=short` (adapted from CLAUDE.md; `.venv` absent in this worktree)
> - `review.coord_file`: not configured — coord-file slot dropped
> - `review.spec_sections.progress_tracker`: adapted to `.taskmaster/tasks/`
> - `memory.dir`/`memory.index`: absent → skipped silently
> - `merge.strategy`: rebase, `merge.autonomous`: false

---

## Goal

Close finding F169 (CRITICAL). `flashcore/scheduler.py:212` assigns
`fsrs_card.last_review = fsrs_card.due`, so for any Review-state card reviewed
on its due date, `elapsed_days = (review_ts.date() - due.date()).days = 0`. Zero
elapsed_days pins FSRS retrievability to R=1.0 and corrupts the stability update
for the normal (on-time) review case — the single most common review path.

Acceptance: in `tests/test_scheduler.py`, a new `test_on_time_review_elapsed_days_positive`
test passes asserting `result.elapsed_days > 0` for a Review-state card reviewed
on its `next_due_date`; a new `test_on_time_vs_same_day_review_stability_distinct`
test passes asserting that stability output differs between an on-time review and
a same-day re-review; all 15 existing scheduler tests still pass.

---

## High-level facts (verify each yourself)

- **Bug site**: `flashcore/scheduler.py:212` — `fsrs_card.last_review = fsrs_card.due`.
  The due date is midnight UTC on `card.next_due_date`; reviewing at any hour on
  that same date yields `elapsed_days = 0`.
  `grep -n "last_review = fsrs_card.due" flashcore/scheduler.py`

- **elapsed_days computation path**: `scheduler.py:218-221` —
  `elapsed_days = (review_ts.date() - fsrs_card.last_review.date()).days`.
  The sign can go negative when reviewing early (a separate sub-issue; not in scope here).

- **Card model**: `flashcore/models.py:43-75` — fields on `Card` are
  `next_due_date`, `stability`, `difficulty`, `state`. There is **no `last_review_date`
  field**. The DB schema (`flashcore/db/schema.py:46-47`) stores
  `elapsed_days_at_review` and `scheduled_days_interval` in the `reviews` table —
  these could inform a backfill, but are not on the Card model.
  `grep -n "last_review_date\|scheduled_days_interval" flashcore/models.py flashcore/db/schema.py`

- **Existing test gap**: `tests/test_scheduler.py:252` — `test_review_lapsed_card`
  asserts `result_lapsed.elapsed_days > result_on_time.elapsed_days` (10 > 0 with
  the bug). This passes silently because on-time=0 satisfies the relative comparison.
  The assertion `result_on_time.elapsed_days > 0` is **absent** — the bug is undetected.
  `grep -n "elapsed_days" tests/test_scheduler.py`

- **Tests baseline**: 15 passed, 0 failed in `tests/test_scheduler.py`.
  `python -m pytest tests/test_scheduler.py -q --tb=short`

- **Same-day re-review semantics**: Learning-state cards with `stability=None` are
  correctly scheduled with `elapsed_days=0` (they represent intra-day learning steps).
  The fix must NOT change elapsed_days for these cards. Only Review-state cards with
  non-None stability should be affected.
  `grep -n "CardState.Learning\|state != CardState.New" flashcore/scheduler.py`

---

## You decide

- **Path A vs Path B (path-fork)** — the core design decision for this PR:
  - **Path A**: Add `last_review_date: Optional[date]` to `flashcore/models.py:Card`.
    Propagate: `review_processor.py` sets `card.last_review_date = review_ts.date()`
    after each processed review. `compute_next_state` uses `card.last_review_date`
    (not `due`) as `fsrs_card.last_review`. Exact fix, no approximation. Requires
    no new DB column if `last_review_date` is a transient model field only (populated
    at review time from `review_ts`). Widens scope to `review_processor.py`.
  - **Path B**: In `compute_next_state`, replace line 212 with
    `fsrs_card.last_review = fsrs_card.due - datetime.timedelta(days=max(1, round(card.stability)))`
    for Review-state cards with non-None stability; keep current behavior otherwise.
    Pure `scheduler.py` fix. Approximate: stability ≈ scheduled_days, but not exact
    after lapses or early reviews. No model or processor changes.

- **Guard for None stability (both paths)**: When `card.stability` is None (Learning
  or Relearning state), `elapsed_days=0` is semantically correct. Confirm the fix
  does not attempt arithmetic on None.

- **If Path A**: whether to also add `last_review_date` as a persisted SQLite column.
  This widens scope to a DB migration — recommend deferring; keep the field transient
  for this PR. Decide and document in the PR description.

- **If Path B**: whether to clamp to `max(1, round(stability))` or allow `round()`
  alone. A stability < 0.5 rounds to 0, re-introducing the bug. Clamping to 1 is
  safer.

---

## Worktree + branch

Run the start-PR ritual. It will:

1. Create worktree at `branch.worktree_pattern` (config default — the ritual resolves this).
2. Branch off `origin/main` onto `feat/c2-pr-f169-fsrs-elapsed-days-b1`.
3. Stage is `c2` (derived from current branch `feat/c2-fsrs-harness`).

After the ritual, all work for this PR lives in that worktree on that branch.
Never commit directly to `main`.

---

## Gates (binary)

Each bullet below has a corresponding VERIFY item in the completion contract.

- [ ] `tests/test_scheduler.py::test_on_time_review_elapsed_days_positive` added and green —
      Review-state card with `next_due_date = review_ts.date()` produces `elapsed_days > 0`
- [ ] `tests/test_scheduler.py::test_on_time_vs_same_day_review_stability_distinct` added and green —
      stability output for an on-time review != stability for a same-day re-review at identical rating
- [ ] All 15 existing `tests/test_scheduler.py` tests still pass (no regression)
- [ ] No `elapsed_days = 0` for any Review-state on-time review in the test suite
- [ ] Path decision documented (A or B) in PR description with one-sentence rationale
- [ ] `aiv check .github/aiv-packets/PACKET_f169-fsrs-elapsed-days.md` exits 0
- [ ] `mypy flashcore/scheduler.py flashcore/models.py --ignore-missing-imports` introduces no new errors
- [ ] Full test suite (`tests/`) passes at baseline or better

---

## Iter budget

2 live-fire cycles pre-authorized.

- Cycle 1: implement fix + add two new tests; run full scheduler suite.
- Cycle 2: edge cases — lapsed card, early card, Learning-state card; confirm no regression.
- Escalate via AskUserQuestion after cycle 2 if stability for on-time still matches same-day.

---

## When to AskUserQuestion

- Path choice (A or B) is unclear or the implementing agent wants operator sign-off
  before widening scope to `review_processor.py`.
- Path A is chosen and there is doubt whether `last_review_date` should also be
  persisted to SQLite (this widens scope beyond R1 — escalate before proceeding).
- Path B: if the stability-based approximation fails the acceptance test for any
  edge case (e.g., post-lapse card where stability was reset to a low value), ask
  whether to switch to Path A.
- Any existing test must be edited to pass after the fix — stop and confirm which
  side (test or code) is wrong before changing.

---

## Risk tier + scope estimate

**R1** — standard logic fix; no external API surface changes; no DB schema changes
(unless Path A with persistence, which requires escalation). Failure mode is local
to the scheduler computation and fully covered by the new tests.

**Size**: Small. 1 file modified (Path B: `scheduler.py` only) or 2-3 files
(Path A: `scheduler.py` + `models.py` + `review_processor.py`). 2 new test functions.
No dependency upgrades; no new imports beyond what already exists.

---

## Out-of-scope

- **Backfill of historical `last_review_date`** for cards already in the DB: the reviews
  table carries `elapsed_days_at_review` and `scheduled_days_interval` that could
  reconstruct last-review dates. Deferred → `feat/c2-pr-backfill-last-review-date`.
- **Persisting `last_review_date` as a SQLite column**: if Path A is chosen,
  `last_review_date` stays a transient model field this PR. DB migration deferred →
  stage-c2 DB migration PR (open as follow-up before stage-c3 cutoff).
- **Negative `elapsed_days` for early reviews**: `test_review_early_card` currently
  passes with `elapsed_days = -2` (on-time=0, early=-2), both wrong. The fix may
  correct the on-time value but leave the early-review negative case partially
  unaddressed depending on path. Deferred → open as new audit finding (F169b) in
  the stage-c2 audit pass before stage-c3 closes.

---

## Reading order before start-PR

1. `flashcore/scheduler.py:190-270` — full `compute_next_state` method; focus on
   lines 205-224 (the `last_review` assignment and `elapsed_days` calculation).
2. `tests/test_scheduler.py:252-320` — `test_review_lapsed_card` and
   `test_review_early_card`; note what is and is not asserted.
3. `flashcore/models.py:43-90` — `Card` model fields; confirm no `last_review_date` exists.
4. `flashcore/review_processor.py:100-140` — post-review `Card` update path (relevant
   if Path A is taken).

Universal principles (no memory store loaded — these travel with every brief):
- Never merge autonomously. The human is the merge gate.
- Run the local CI replica before every push; do not push knowing CI will fail.
- Read the code-review body, not just its status.
- Never edit a test to make it pass without first establishing which side is wrong.
- Every out-of-scope item points to a follow-up PR ID, stage, or issue #.
- The packet validates through `aiv check`; do not restate spec rules inline.

---

Now run the start-PR ritual.
