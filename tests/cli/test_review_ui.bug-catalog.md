# Bug Catalog — `flashcore/cli/review_ui.py`

**Target**: `flashcore/cli/review_ui.py` — `start_review_flow()`
**Audit finding**: F82 (`audit/02-static-audit.md` L92)
**Date**: 2026-06-19

---

## Module Summary

**Public interface**:
- `start_review_flow(manager: ReviewSessionManager, tags: Optional[List[str]] = None) -> None` — drives the CLI review loop; calls `manager.initialize_session`, then iterates `manager.get_next_card()` / `manager.submit_review()` until the queue is empty.
- `_display_card(card: Card) -> int` — private helper; renders card front/back and returns elapsed ms.
- `_get_user_rating() -> tuple[int, int]` — private helper; prompts user for a 1–4 rating, returns `(rating, eval_ms)`.

**Load-bearing comments**: None. The control-flow decision in the `except` block at line 111 (`continue`) is undocumented but critical: it determines whether the failed card is retried or skipped.

**IO boundaries**: `console.input()` (blocking user input), `console.print()` (terminal); all DB and scheduler IO is delegated to the injected `manager`.

**Branching points**:
- `if due_cards_count == 0` (line 82): early return with "no due cards" message — no "Well done!".
- `while (card := manager.get_next_card()) is not None` (line 90): main loop, exits when queue is empty.
- `try/except Exception` (lines 99–111): submit exception handler — calls `continue`, returning to the `while` header without removing the card from the queue.
- `if updated_card and updated_card.next_due_date` (line 113): display-formatting branch.
- `elif updated_card` (line 119): display-formatting branch for no-due-date case.
- `else` (line 121): display error branch when `submit_review` returns `None`.
- Line 127: `console.print("...Well done!")` — executes unconditionally after the `while` loop exits, with no guard for whether any reviews actually succeeded.

**Type definitions**: `ReviewSessionManager.get_next_card()` returns `Optional[Card]`; returns `None` when `review_queue` is empty (`review_manager.py:124–127`). `submit_review()` calls `_remove_card_from_queue()` **only** on the success path (`review_manager.py:210`); on failure it re-raises (`review_manager.py:214–216`), so the queue is unchanged when an exception propagates back to `start_review_flow`.

**Existing tests**: `tests/cli/test_review_ui.py` has 5 tests. The submit-exception test (`test_start_review_flow_submit_review_exception`) uses `get_next_card.side_effect = [card, None]`, which masks the infinite-retry bug: after the failed submit, the mock returns `None` instead of the same card, so the loop exits after one iteration rather than looping forever.

---

## Bug Catalog

### B1 — Infinite retry loop on persistent `submit_review` failure

**The bug**: When `submit_review()` raises an exception, `start_review_flow()` unconditionally calls `continue`, which returns to the `while` header and calls `get_next_card()` again; because the failed card was never removed from the queue, `get_next_card()` returns the same card again, creating a loop that repeats until the process is killed.

**Blast radius**: The CLI hangs indefinitely on any persistent error (DB corruption, scheduler failure, network partition). The only recovery path is an external kill signal; a session in progress is entirely lost.

**Why it's plausible**: `_remove_card_from_queue()` at `review_manager.py:210` is inside the success `try` block, after `review_processor.process_review()`. An exception anywhere in that block (`process_review`, `session_manager.record_card_review`) causes the `except` at line 214 to re-raise, bypassing `_remove_card_from_queue()`. Back in `start_review_flow`, the `except` at line 106 catches the re-raised exception and calls `continue` (line 111). The `while` header then calls `get_next_card()`, which returns `review_queue[0]` — the same card, still in position 0.

**Test type**: Behavioral invariant — the invariant "each iteration of the review loop must advance to a different card or exit" is violated on failure.

---

### B2 — "Well done!" printed when all `submit_review` calls failed

**The bug**: Line 127 (`console.print("[bold cyan]Review session finished. Well done![/bold cyan]")`) executes unconditionally after the `while` loop exits, with no check of whether any reviews actually succeeded. A session where every submission failed still prints a success message.

**Blast radius**: The user is told "Well done!" after a session in which zero reviews were persisted. They may believe their study session was recorded when it was not — silent data loss from the user's perspective.

**Why it's plausible**: The function has a single exit point after the loop (line 127). The only branches that avoid it are the `due_cards_count == 0` early return (line 83–87) and an unhandled exception escaping `start_review_flow`. The exception handler at line 106 captures all exceptions and calls `continue`, guaranteeing the function survives to line 127 even after total failure.

**Test type**: Decision table / negative path — the output must differ between "all reviews succeeded" and "all reviews failed".

---

### B3 — No failure signal when all reviews fail

**The bug**: `start_review_flow()` always returns `None` regardless of whether any reviews were persisted; no exception is raised, no `sys.exit()` is called, no non-zero status is communicated.

**Blast radius**: The CLI entrypoint cannot propagate a failure exit code. Automated pipelines (CI, scheduled review scripts) see a zero-exit-code success even when the review session wrote nothing to the database.

**Why it's plausible**: The function signature is `-> None`; the only non-`None` exit is via an unhandled exception, but the broad `except Exception` at line 106 absorbs all failures.

**Test type**: Negative path — callers must be able to distinguish success from failure.

---

## Skipped

| Bug class | Reason skipped |
|---|---|
| Rating-prompt infinite loop (user keeps entering bad input to `_get_user_rating`) | Already covered in `test_start_review_flow_invalid_rating_input`; user-controllable, not a system bug. |
| `initialize_session()` failure | Out of scope: `initialize_session` is called before the loop; its failure mode is not part of the submit-retry invariant. Covered separately. |
| `_display_card` blocking behavior | Pure UI I/O; mocked in all tests; no logic under test. |

---

## Test Self-Critique

### Test T1: `test_all_submit_review_fail_output_omits_well_done_guards_against_false_success_message`

**Catches**: B1 (observable via "Well done!" after a total-failure session) and B2 (the unconditional success message).

**What specific catalog bug?** B2 — the success message is printed even when all submit_review calls raise.

**Would this pass for wrong-but-stable output?** No — the assertion checks specific text *absence*, not a snapshot of the entire output. If "Well done!" were replaced with another misleading success message, the test would need updating, but it would not silently pass.

**Would this fail under a non-behavior-changing refactor?** No — the assertion is on console output text only, with no coupling to internal call order or implementation structure.

---

### Test T2: `test_persistent_submit_failure_retries_same_card_guards_against_infinite_retry_loop`

**Catches**: B1 — the retry loop is directly observable as `submit_review.call_count > 1` for a single card.

**What specific catalog bug?** B1 — `submit_review` is called twice for the same card when it should be attempted at most once per card.

**Would this pass for wrong-but-stable output?** No — it counts method invocations, not output text. A wrong implementation that retries but produces the same terminal output would still be caught.

**Would this fail under a non-behavior-changing refactor?** No — `submit_review` is the public method on the injected `manager`; calling it is the observable unit of work. Asserting on call count is stable across refactors that preserve the "one submit per card" contract.

---

## Post-session Evaluation

*(To be filled after tests are written and run.)*

### Bugs caught (test failed first run, fix needed)

- T1: FAILED — current code prints "Well done!" when all submits fail.
- T2: FAILED — current code calls `submit_review` twice for the same card.

### Bugs characterized (test passed first run, behavior pinned)

- (none — both tests are RED as designed)

### Bugs discovered during writing not in original catalog

- The existing test `test_start_review_flow_submit_review_exception` masks the bug by using `get_next_card.side_effect = [card, None]`: after the first failed submit, the mock returns `None`, so the loop exits without ever simulating the real stuck-queue scenario.
