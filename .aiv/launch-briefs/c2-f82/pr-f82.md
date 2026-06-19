# PR-F82 — Bound infinite retry loop in start_review_flow

> **Config note.** No `.aiv-workflow.yml` found at repo root. All values below use skill
> defaults. Effective settings:
> - `launch_brief.out_dir` → `.aiv/launch-briefs/` (default)
> - `branch.pattern` → `feat/{stage}-pr-{slug}-{brief}` (default; harness assigns final name)
> - `branch.base` → `origin/main` (default)
> - `aiv.cli` / `aiv.check_cmd` → `aiv` / `aiv check` (default)
> - `aiv.packets_dir` → `.github/aiv-packets` (default)
> - `ci.test_cmd` → `source .venv/bin/activate && pytest tests/ -q --tb=short` (per CLAUDE.md)
> - `ci.local_replica_cmd` → `source .venv/bin/activate && make lint && pytest tests/ -q --tb=short`
> - `review.coord_file` → not configured; coord-file slot dropped
> - `review.spec_sections.progress_tracker` → not configured; slot uses `.taskmaster/tasks/`
> - `memory.dir` / `memory.index` → no `MEMORY.md` found; lesson store skipped
>
> **PR class:** `dispatcher`
> **Modifier flags:** `path-fork`
> **Risk tier:** R1
> **Stage:** c2

---

## Goal

Close finding F82 (`audit/02-static-audit.md#L92`). In `start_review_flow()`
(`flashcore/cli/review_ui.py:100-111`), a `continue` in the exception handler after a failed
`submit_review()` call leaves the failed card at `review_queue[0]`.
`get_next_card()` (`review_manager.py:127`) always returns `review_queue[0]`, so the same card
is retried on every iteration — an unbounded infinite retry loop under any persistent error
(DB corruption, scheduler failure, etc.). The fix must advance past a failed card, bound the
loop, and when every review in the session fails, suppress "Well done" from output and signal
failure to the CLI layer.

---

## High-level facts (verify each yourself)

| # | Item | Status | Code anchor |
|---|------|--------|-------------|
| 1 | `start_review_flow()` while loop — exception handler at L106-111 calls `continue` without removing the card from the queue | BUG | `flashcore/cli/review_ui.py:100-111` |
| 2 | `get_next_card()` always returns `review_queue[0]`; never pops | root cause | `flashcore/review_manager.py:124-127` |
| 3 | `_remove_card_from_queue()` is private (`_`-prefixed); called by `submit_review` on success path only (L210), never on failure | root cause | `flashcore/review_manager.py:144-153, 210` |
| 4 | `submit_review()` failure path re-raises at L214-216 — queue is never mutated on exception | root cause | `flashcore/review_manager.py:214-216` |
| 5 | "Well done" is emitted unconditionally at end of while loop regardless of failure count | output to change | `flashcore/cli/review_ui.py:127` |
| 6 | Existing exception test mocks `get_next_card.side_effect = [card, None]` — masks infinite loop by making the mock terminate the loop naturally | GAP / masked test | `tests/cli/test_review_ui.py:125-145` |
| 7 | No test asserts "Well done" is absent when all `submit_review` calls fail | GAP | `tests/cli/test_review_ui.py` |
| 8 | `start_review_flow()` returns `None`; its only caller ignores the return value | design constraint | `flashcore/cli/_review_logic.py:43` |
| 9 | Project CLI exit pattern is `raise typer.Exit(code=1)` | exit convention | `flashcore/cli/main.py:58, 129, 171` |
| 10 | Test baseline: 480 tests, 1 skipped | baseline | `CLAUDE.md` |

**Verification commands:**

```bash
# Fact 2
grep -n "def get_next_card" flashcore/review_manager.py

# Fact 3+4
grep -n "_remove_card_from_queue\|def submit_review" flashcore/review_manager.py

# Fact 5
grep -n "Well done" flashcore/cli/review_ui.py

# Fact 7
grep -n "Well done" tests/cli/test_review_ui.py

# Fact 8+9
grep -n "start_review_flow\|typer.Exit" flashcore/cli/_review_logic.py flashcore/cli/main.py
```

---

## You decide

This PR has one principal path fork and three dependent decisions. Resolve all four via
AskUserQuestion before writing a single line of code.

### Path fork: advance mechanism

**Path A — skip-and-advance:** On exception in `start_review_flow`, remove the failed card
from the queue so the loop naturally advances to the next card. Track `failed_count`; compute
the outcome message from `success_count` vs `failed_count` vs `due_cards_count` at loop end.
Session runs to completion (other cards still reviewed).

- Sub-decision A1: Call the private `manager._remove_card_from_queue(card.uuid)` directly
  from `review_ui.py` (cross-layer reach into a private method), OR add a new public method
  `manager.skip_card(card_uuid: UUID) -> None` to `ReviewSessionManager` that wraps
  `_remove_card_from_queue`.

**Path B — bound-and-exit:** On exception, break out of the while loop immediately (or after
N retries). Session is truncated; remaining cards are not attempted.

*Operator confirmation required before implementation.*

### Decision 2: end-of-session message

Choose from three variants:
- All succeeded → `"Review session finished. Well done!"`
- Mixed (some failed, some succeeded) → neutral: `"Review session finished."` (no "Well done")
- All failed → `"Review session failed."` or similar; no "Well done"

*Is the mixed-outcome message acceptable, or must "Well done" appear whenever at least one
card succeeded?*

### Decision 3: failure signal mechanism

`start_review_flow()` currently returns `None`; `_review_logic.py:43` ignores the return.
Options:
- Return `bool` from `start_review_flow` (True = at least one success); update
  `_review_logic.py` to `raise typer.Exit(code=1)` on False.
- `start_review_flow` raises `typer.Exit(code=1)` directly when all fail (cross-layer
  coupling into typer from a non-CLI module).
- Emit structured failure via logging only; no process-exit signal (weakest option).

### Decision 4: test location

The finding goal names `tests/cli/test_review_all_logic.py` alongside `review_ui test`. The
natural location for tests of `start_review_flow` is `tests/cli/test_review_ui.py`. Add the
all-fail test to `test_review_ui.py` only, or duplicate into `test_review_all_logic.py` as
well?

---

## Worktree + branch

Agent creates the feature branch via the start-PR ritual using pattern
`feat/{stage}-pr-f82-{brief}` off `origin/main`. The harness assigns the final branch name;
do not hard-code it in any verification target. The agent must not commit directly to `main`.

---

## Gates (binary)

Every item below has a matching VERIFY slot in the completion contract.

1. `get_next_card()` is not called more times than `len(initial_review_queue)` when all
   `submit_review` calls raise — loop is bounded regardless of error persistence.
2. Session terminates in finite time (no hang) when every `submit_review` call raises.
3. Output omits "Well done" when all `submit_review` calls fail.
4. Output contains "Well done" (or the agreed success variant) when all reviews succeed
   (regression guard).
5. Failure signal (exit code or returned bool propagated to caller) is implemented and tested.
6. Advance mechanism decision (Path A private-access / public-method, or Path B) is recorded
   in the commit message — a reviewer can verify the design choice without reading the code.
7. `test_start_review_flow_submit_review_exception` (`test_review_ui.py:125-145`) is updated
   to assert the bounded-loop property; the mock no longer uses `[card, None]` to mask
   the infinite-loop path.
8. New test: all-fail scenario → "Well done" absent, failure signaled.
9. `pytest tests/ -q --tb=short` passes with 0 failures; at least 2 new tests collected.
10. `make lint` (mypy + black + flake8) exits 0 with no new errors.
11. `aiv check` passes on the generated packet with no blocking errors.
12. Finding F82 is referenced in the commit log and `audit/02-static-audit.md` entry status
    is updated.

---

## Iter budget

**2 live-fire cycles pre-authorized.** R1 correctness fix; pure Python logic change plus test
additions; no schema or DB changes. If the Path A sub-decision requires adding a public API
to `ReviewSessionManager`, that counts as one additional file in scope — still within R1.

Escalate to operator if: mypy surfaces new type errors from the chosen return-type change,
or if the all-fail test reveals a second bug site not in the original finding.

---

## When to AskUserQuestion

| Trigger | Question |
|---------|----------|
| Before any code | Path A (skip-and-advance) vs Path B (bound-and-exit)? |
| If Path A chosen | Private `_remove_card_from_queue` access vs new public `skip_card` method? |
| Before any code | End-of-session message for mixed outcome (some fail, some succeed)? |
| Before any code | Failure signal: return bool + caller raises `typer.Exit` vs `start_review_flow` raises directly vs log-only? |
| Before test writing | All-fail test in `test_review_ui.py` only, or also `test_review_all_logic.py`? |

---

## Risk tier + scope estimate

**R1 — standard correctness fix.** Pure Python logic and test changes; no SQL migrations, no
schema changes, no new dependencies.

Scope: `flashcore/cli/review_ui.py` (primary fix), `flashcore/review_manager.py` (if public
`skip_card` API added — Path A only), `flashcore/cli/_review_logic.py` (if failure-signal
wired through return value), `tests/cli/test_review_ui.py` (test updates + new test),
optionally `tests/cli/test_review_all_logic.py` (per Decision 4).

---

## Out-of-scope

- **Retry-with-backoff / per-card retry budget** — architectural policy decision; out of
  scope by design. Open a new issue if desired.
- **F83–F114** (all other audit findings) — each is a separate PR; not addressed here.
- **Making `ReviewSessionManager` a proper iterator** — refactor; out of scope by design.
- **F85 (`_review_logic.py` DB connection leak)** — separate finding; will be addressed in a
  dedicated PR for F85.
- **Changes to `flashcore/cli/_review_all_logic.py`** — separate code path; no overlap with
  the bug in `start_review_flow`.

---

## Reading order before start-PR

1. `audit/02-static-audit.md#L92` — the canonical finding; Class E intent anchor for all
   AIV packet claims on this PR
2. `flashcore/cli/review_ui.py:68-128` — the buggy function in full
3. `flashcore/review_manager.py:114-216` — `get_next_card`, `_remove_card_from_queue`,
   `submit_review` (the three methods whose interaction causes the bug)
4. `tests/cli/test_review_ui.py` — fixture patterns; the masked test at L125-145
5. `flashcore/cli/_review_logic.py` — the only caller; exit-signal convention
6. `flashcore/cli/main.py:48-60` — `raise typer.Exit(code=1)` pattern in context

**Universal principles (no memory store present — stated here explicitly):**
- Never merge autonomously. H2 (judge + merge) is the human's act; the agent's final act is
  `aiv close` + `gh pr create`.
- Run `make lint && pytest tests/ -q --tb=short` locally before every push.
- Read the code-review body, not just its CI status, before considering the PR mergeable.
- Never edit a test to make it pass without first establishing which side (test or code) is
  wrong.
- Every deferred item in Out-of-scope is a pinned intention, not abandonment.
- AIV packet verification is mechanical: run `aiv check`; do not manually decide it passes.
- Avoid "fix/fixed/fixes/resolve/resolved" in AIV claim text (E010 trap; rephrase to
  "corrects", "updates", "bounds", "suppresses", etc.).

Now run the start-PR ritual.
