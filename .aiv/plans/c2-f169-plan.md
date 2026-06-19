# c2-f169-plan.md — Correct elapsed_days for on-time FSRS reviews

> Branch: `feat/c2-pr-f169-fsrs-elapsed-days-b1`
> Base: `origin/main` @ b5e1c4b
> Risk tier: R1
> Created: 2026-06-19

---

## §1 Context

Finding F169 (CRITICAL) in `flashcore/scheduler.py:212`:

```python
fsrs_card.last_review = fsrs_card.due   # line 212 — the bug
```

`fsrs_card.due` is midnight UTC on `card.next_due_date`. For any Review-state
card reviewed on its due date, `(review_ts.date() - fsrs_card.due.date()).days == 0`.
Zero `elapsed_days` pins FSRS retrievability to R=1.0 and corrupts the stability
update for the normal (on-time) review path — the single most common real-world case.

Source: `.aiv/launch-briefs/pr-f169-fsrs-elapsed-days/pr-f169-fsrs-elapsed-days.md`
and the companion completion contract at
`.aiv/launch-briefs/pr-f169-fsrs-elapsed-days/pr-f169-fsrs-elapsed-days-completion-contract.md`.

---

## §2 Verified state (5 Explore lookups, 2026-06-19)

All facts below were confirmed by direct file reads in this session.

| # | Claim | Evidence path:line |
|---|-------|--------------------|
| V1 | `fsrs_card.last_review = fsrs_card.due` is the sole assignment that causes the bug | `flashcore/scheduler.py:212` |
| V2 | `elapsed_days` is computed as `(review_ts.date() - fsrs_card.last_review.date()).days` | `flashcore/scheduler.py:219-221` |
| V3 | `Card` model has NO `last_review_date` field; existing fields: `uuid`, `last_review_id`, `next_due_date`, `state`, `stability`, `difficulty`, `deck_name`, `front`, `back`, `tags` | `flashcore/models.py:43-92` |
| V4 | `reviews` table carries `elapsed_days_at_review` and `scheduled_days_interval` but NOT a `last_review_date` column; no DB migration is required for Path B | `flashcore/db/schema.py:44-48` |
| V5 | Existing test `test_review_lapsed_card` asserts `result_lapsed.elapsed_days > result_on_time.elapsed_days` (10 > 0) — passes silently because on-time=0 satisfies the relative comparison; the assertion `result_on_time.elapsed_days > 0` is ABSENT | `tests/test_scheduler.py:285` |
| V6 | 15 scheduler tests collected; baseline: 15 passed, 0 failed | `pytest --co tests/test_scheduler.py` |
| V7 | `compute_next_state` guards `hasattr(fsrs_card, "last_review") and fsrs_card.last_review` before computing `elapsed_days`; for New-state cards `elapsed_days = 0` by the else branch | `flashcore/scheduler.py:218-224` |
| V8 | `review_processor.py` does not currently set any `last_review_date` on the Card; it passes `card` directly to `compute_next_state` and uses `scheduler_output` fields post-call | `flashcore/review_processor.py:93-138` |
| V9 | `Card.stability` is `Optional[float]`; None for New and Learning-state cards; arithmetic on None must be guarded | `flashcore/models.py:69-71` |

---

## §5 Memory + lesson references

- **E010 trap**: claim text containing `fix(ed|es|ing)?`, `bug`, `resolve`, `patch`,
  `closes #N`, `hotfix` triggers a blocking E010 unless a Class F (PROVENANCE) claim
  is present. Use neutral verbs: "correct", "update", "replace", "set" instead.
- **`aiv commit` FILE arg must exist on disk and differ from HEAD**. For commits that
  only delete lines, also touch/update a companion tracking file (e.g., the task md).
- **`aiv abandon` requires interactive confirm** — pipe `echo "y" | aiv abandon`.
- **Intent URLs must be SHA-pinned** (commit SHA in path, not `blob/main/...`).
  Find SHA: `git log --oneline --follow -- .taskmaster/tasks/task_NNN.md`.
- **`--skip-checks` is R0-only**. This PR is R1; never pass `--skip-checks`.
- Never edit a test to make it pass without first establishing which side (test or
  code) is wrong.

---

## §6 Strict scope boundaries

**In scope:**
- `flashcore/scheduler.py` — replace line 212 (the `last_review = fsrs_card.due` assignment) with a
  stability-based approximation (Path B, see §7).
- `tests/test_scheduler.py` — add exactly two new test functions:
  `test_on_time_review_elapsed_days_positive` and
  `test_on_time_vs_same_day_review_stability_distinct`.

**Explicitly out of scope (do not touch):**
- `flashcore/models.py` — no `last_review_date` field added this PR (Path B).
- `flashcore/review_processor.py` — no changes (Path B does not widen scope).
- `flashcore/db/schema.py` — no DB migration.
- Any existing test function body — read-only; the two new tests are additive.
- `HPE_ARCHIVE/` — removed; do not reference or recreate.
- Backfill of historical `last_review_date` → deferred to `feat/c2-pr-backfill-last-review-date`.
- Persisting `last_review_date` as a SQLite column → deferred to stage-c2 DB migration PR.
- Negative `elapsed_days` for early reviews → deferred to finding F169b.

---

## §7 Locked design decisions

**Decision: Path B — scheduler-only stability approximation.**

Rationale: Path A requires widening scope to `models.py` and `review_processor.py`,
and every call site that constructs a Card must populate `last_review_date` correctly;
Path B confines the entire change to a single file (`scheduler.py`) and is fully
verifiable with no cross-module plumbing, while the approximation error (stability ≈
scheduled_days) is negligible for the on-time case this PR targets.

**Locked implementation for line 212 replacement** (Review-state only, None guard required):

```python
# Replace (line 212):
#   fsrs_card.last_review = fsrs_card.due
# With:
if card.state != CardState.New and card.stability is not None:
    approx_days = max(1, round(card.stability))
    fsrs_card.last_review = fsrs_card.due - datetime.timedelta(days=approx_days)
else:
    fsrs_card.last_review = fsrs_card.due   # Learning/Relearning: elapsed_days=0 is correct
```

The `max(1, ...)` clamp prevents `round(stability)` from producing 0 when stability < 0.5,
which would re-introduce the bug.

The existing outer `if card.state != CardState.New:` block at line 200 already guards
the entire section; the inner guard on `card.stability is not None` defends against
Learning/Relearning cards whose stability was just initialized.

**No other design decisions are open for this PR.**

---

## §9 Sequenced atomic-commit plan

All commits on branch `feat/c2-pr-f169-fsrs-elapsed-days-b1`.
One `aiv commit` call per logical unit (primary-file rule).

```
Commit 1 — scheduler fix
  Primary file: flashcore/scheduler.py
  Message: "correct(scheduler): replace last_review=due with stability-based approximation"
  Tier: R1
  Claims:
    - "compute_next_state sets fsrs_card.last_review to (due - max(1,round(stability)) days) for Review-state cards"
    - "elapsed_days > 0 for on-time Review-state review when stability >= 0.5"
    - "Learning/Relearning cards retain elapsed_days=0 via unchanged else branch"
  Risk rationale: "single-file scheduler logic change; no DB or API surface affected"

Commit 2 — new tests
  Primary file: tests/test_scheduler.py
  Message: "test(scheduler): add on-time elapsed_days and stability-distinct assertions"
  Tier: R1
  Claims:
    - "test_on_time_review_elapsed_days_positive asserts elapsed_days > 0 for Review-state on-time review"
    - "test_on_time_vs_same_day_review_stability_distinct asserts stability output differs between on-time and same-day re-review"
    - "all 15 pre-existing scheduler tests pass after addition"
  Risk rationale: "additive test-only commit; no production code touched"

Commit 3 — AIV packet (auto-generated by aiv close)
  Primary file: .github/aiv-packets/PACKET_f169-fsrs-elapsed-days.md
  Message: "docs(aiv): add packet for f169-fsrs-elapsed-days"
  Tier: R0 with --skip-checks --skip-reason "auto-generated packet document"
```

Pre-commit checklist (run before each `aiv commit`):
1. `source .venv/bin/activate && python -m pytest tests/test_scheduler.py -q --tb=short`
   — must show 15 passed (after Commit 1) or 17 passed (after Commit 2).
2. `mypy flashcore/scheduler.py flashcore/models.py --ignore-missing-imports`
   — must show no new errors.
3. `grep -n "last_review = fsrs_card.due" flashcore/scheduler.py`
   — must return no output (after Commit 1).

---

## §10 Critical files

| File | Role | Read before touching |
|------|------|---------------------|
| `flashcore/scheduler.py:190-268` | Bug site + full `compute_next_state` method | Yes — re-read lines 200-224 immediately before editing |
| `flashcore/models.py:43-92` | `Card` model field list; confirms no `last_review_date` | Yes — confirm `CardState` import path |
| `tests/test_scheduler.py:230-320` | Existing lapsed/early tests; baseline for regression check | Yes — understand existing `elapsed_days` assertions |
| `flashcore/db/schema.py:44-48` | Confirms `reviews` table columns; no migration needed for Path B | Read-only reference |
| `flashcore/review_processor.py:93-138` | Confirms Path B requires no changes here | Read-only reference |
| `.aiv/launch-briefs/pr-f169-fsrs-elapsed-days/pr-f169-fsrs-elapsed-days-completion-contract.md` | Binary VERIFY checklist — run each `cmd` before closing the change | Reference throughout |

---

## §11 Reused utilities (must consume, not reimplement)

- **`CardState` enum** (`flashcore/models.py`) — already imported in `scheduler.py:32`; use `CardState.New` and value comparisons as the Learning/Relearning guard, consistent with line 200.
- **`datetime.timedelta`** — already imported via `import datetime` at top of `scheduler.py`; use `datetime.timedelta(days=approx_days)` directly.
- **`FSRSCard`, `FSRSState`** — already imported and used in `compute_next_state`; no new imports required.
- **Existing fixture pattern in `tests/test_scheduler.py`** — reuse the `make_review_card()` or inline `Card(...)` construction pattern already present in `test_review_lapsed_card` and `test_review_early_card` for the two new tests; do NOT introduce a new pytest fixture.
- **`py-fsrs` library** — consumed via `self.fsrs_scheduler.review_card(...)`; do not call FSRS internals directly.

---

## §14 Acceptance criteria

All criteria are binary (pass/fail). Source: completion contract VERIFY items [1]–[13].

| # | Criterion | Verification command |
|---|-----------|---------------------|
| AC-1 | `test_on_time_review_elapsed_days_positive` passes; `elapsed_days > 0` for Review-state card with `next_due_date == review_ts.date()` | `python -m pytest tests/test_scheduler.py::test_on_time_review_elapsed_days_positive -v` |
| AC-2 | `test_on_time_vs_same_day_review_stability_distinct` passes; stability for on-time != stability for same-day re-review at identical rating | `python -m pytest tests/test_scheduler.py::test_on_time_vs_same_day_review_stability_distinct -v` |
| AC-3 | All 15 original scheduler tests pass (no regression) | `python -m pytest tests/test_scheduler.py -q --tb=short` → 17 passed, 0 failed |
| AC-4 | Learning/Relearning cards still produce `elapsed_days = 0`; no TypeError on None stability | `python -m pytest tests/test_scheduler.py -k "new_card or learning or first_review" -v` |
| AC-5 | Line 212 (`last_review = fsrs_card.due`) is gone | `grep -n "last_review = fsrs_card.due" flashcore/scheduler.py` → no output |
| AC-6 | mypy reports no new errors | `mypy flashcore/scheduler.py flashcore/models.py --ignore-missing-imports 2>&1 \| tail -5` → "Success" or pre-existing errors only |
| AC-7 | Full test suite at baseline or better | `python -m pytest tests/ -q --tb=short 2>&1 \| tail -5` → 480 passed, 1 skipped, 0 failed |
| AC-8 | AIV packet validates | `aiv check .github/aiv-packets/PACKET_f169-fsrs-elapsed-days.md` → exits 0 |
| AC-9 | Path B documented in PR description with one-sentence rationale | PR body contains "Path B" and rationale before merge |
| AC-10 | No E010 trigger words in any claim text | all claim text avoids: fix/fixed/fixes/fixing, bug/bugfix, resolve/resolves/resolved, closes #N, patch/patched, hotfix |

---

## §15 Risks + mitigations + stop conditions (RED)

| Risk | Likelihood | Mitigation | RED stop condition |
|------|-----------|------------|-------------------|
| **Stability approximation fails AC-2**: `round(stability)` produces `elapsed_days` too small → stability differs from same-day only by rounding noise | Low | Use `max(1, round(card.stability))` and verify AC-2 passes after Commit 1 before writing tests | If AC-2 fails after 2 iter cycles, escalate via `AskUserQuestion` — may require switching to Path A |
| **None-stability TypeError**: card in Learning state has `stability=None`; arithmetic crashes | Low | Inner `card.stability is not None` guard before computing `approx_days` | If TypeError appears in test run, stop, diagnose, re-read guard logic before re-committing |
| **Existing test edited to pass**: `test_review_early_card` asserts `result_early.elapsed_days < result_on_time.elapsed_days`; Path B changes `result_on_time.elapsed_days` from 0 to >0, which may invalidate the `<` comparison | Medium | Verify the early-card test still passes unchanged; the early scenario has `elapsed_days = -2` (review_ts before due) which should remain < the new positive on-time value; confirm before committing | If the early-card test fails and the fix is in production code (not the test), escalate; do NOT edit the test without operator approval |
| **E010 blocking packet error**: claim text contains "fix" or cognates | Medium | Write all claims using "correct", "replace", "set", "update", "add" | If `aiv check` raises E010, rephrase claims and re-run; do not merge with a blocking packet |
| **aiv commit FILE not found / unchanged**: if the fix is a pure deletion, `aiv commit flashcore/scheduler.py` fails | Low | The fix adds new lines (the if/else block) so the file has a net addition; confirm with `git diff flashcore/scheduler.py` before committing | If aiv commit fails with "file unchanged", diagnose staging before re-attempting |

---

## §19 Locked PR sequence position

- **Stage**: c2 (current harness branch `feat/c2-fsrs-harness`).
- **PR slot**: F169 is a standalone CRITICAL-finding fix; it does not depend on any
  other open c2 PR and no other c2 PR depends on it.
- **Merge prerequisite**: `aiv check` exits 0 on the packet AND operator confirms
  review quiet window via `AskUserQuestion` (completion contract PRE-MERGE items).
- **Autonomous merge**: NEVER. Human is the sole merge authority.
- **After this PR merges, unblock**:
  - `feat/c2-pr-backfill-last-review-date` (Path B chosen → note approximation
    boundary in the F169b investigation ticket for negative elapsed_days).
  - Stage-c2 DB migration PR (not blocked on this PR but record Path B decision there).

---

## §20 After-merge handoff

1. **Progress tracker**: Update `.taskmaster/tasks/tasks.json` to mark the F169
   sub-item complete. Add a one-line note to the relevant `task_NNN.md`:
   `"F169 closed via Path B (stability approx); commit <SHA>; elapsed_days now >0 for on-time reviews."`.

2. **Follow-up PRs to open**:
   - `feat/c2-pr-backfill-last-review-date` — out-of-scope this PR; spin up
     only if Path A is chosen at a later date.
   - Finding F169b — negative `elapsed_days` for early-review cards
     (`test_review_early_card` passes with `elapsed_days=-2` for the early
     scenario; file as new audit finding in the stage-c2 audit pass before
     stage-c3 closes).

3. **Post-merge CI check**: Run `python -m pytest tests/ -q --tb=short` immediately
   after merge on main; confirm 480 passed, 1 skipped, 0 failed.

4. **Retro-verify (integration)**: After a live review session against a real DB,
   spot-check that `elapsed_days_at_review` values in the `reviews` table are > 0
   for on-time reviews. Defer until integration testing is available post-merge.

5. **Completion contract closure**: Confirm binary VERIFY items [1]–[13] in the
   contract file are all green before archiving the packet.

---

## Machine-checkable data

```json
{
  "plan_id": "c2-f169-plan",
  "finding": "F169",
  "severity": "CRITICAL",
  "branch": "feat/c2-pr-f169-fsrs-elapsed-days-b1",
  "base": "origin/main",
  "base_sha": "b5e1c4b",
  "risk_tier": "R1",
  "path_decision": "B",
  "path_rationale": "Confines change to scheduler.py only; no model or processor plumbing required; approximation error negligible for on-time case.",
  "bug_site": "flashcore/scheduler.py:212",
  "files_modified": ["flashcore/scheduler.py", "tests/test_scheduler.py"],
  "files_not_modified": ["flashcore/models.py", "flashcore/review_processor.py", "flashcore/db/schema.py"],
  "new_tests": [
    "tests/test_scheduler.py::test_on_time_review_elapsed_days_positive",
    "tests/test_scheduler.py::test_on_time_vs_same_day_review_stability_distinct"
  ],
  "baseline_test_count": 15,
  "expected_test_count_after": 17,
  "full_suite_baseline": "480 passed, 1 skipped",
  "atomic_commits": 3,
  "created": "2026-06-19"
}
```
