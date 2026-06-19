===== PR-F82 COMPLETION CONTRACT — Bound infinite retry loop in start_review_flow =====

GOAL: Close finding F82 (audit/02-static-audit.md#L92). In start_review_flow()
(flashcore/cli/review_ui.py:100-111), a continue in the exception handler after submit_review()
raises leaves the failed card at review_queue[0]; get_next_card() (review_manager.py:127) always
returns review_queue[0], creating an unbounded infinite retry loop under persistent error.
The fix must advance past a failed card so the loop is bounded, suppress "Well done" when all
reviews in the session fail, and wire a failure signal to the CLI layer.

AI-DRIVEN TRACK: Commits are agent-authored. The human's only acts are H1 (the finding, already
done) and H2 (judge the evidence + merge). No "no-AI-author" pass-condition applies.

═══════════════════════════════════════════════════════════════════════════════
VERIFY (binary green/red):
═══════════════════════════════════════════════════════════════════════════════

── CLASS-BOUND SLOTS (dispatcher) ─────────────────────────────────────────────

[1] LOOP IS BOUNDED — FAILED CARD DOES NOT REPEAT

  Path A (skip-and-advance):
    cmd: pytest tests/cli/test_review_ui.py -q --tb=short -k "exception or all_fail"
    check: within the all-fail test, mock_manager.get_next_card.call_count <=
           len(initial_review_queue); card is removed from queue on exception path
    pass: test passes; call count assertion holds

  Path B (bound-and-exit):
    cmd: pytest tests/cli/test_review_ui.py -q --tb=short -k "exception or all_fail"
    check: while loop exits (break executed) after the first exception; no second call
           to get_next_card for the same card
    pass: test passes; loop terminates after first failure

[2] SESSION TERMINATES IN FINITE TIME — NO HANG

    cmd: pytest tests/cli/test_review_ui.py -q --tb=short -k "all_fail" --timeout=10
    pass: pytest completes within 10 s; no timeout error; test collected and passed

[3] "WELL DONE" ABSENT ON TOTAL FAILURE

    cmd: pytest tests/cli/test_review_ui.py -q --tb=short -k "all_fail"
    check: assert "Well done" not in captured.out
    pass: assertion holds; test passes

[4] "WELL DONE" PRESENT ON ALL-SUCCESS (ANTI-REGRESSION)

    cmd: pytest tests/cli/test_review_ui.py -q --tb=short -k "one_card or success"
    check: "Review session finished. Well done!" in captured.out
    pass: test(s) pass; output contains the success message

[5] FAILURE SIGNAL WIRED TO CLI LAYER

  Path A — return-bool variant:
    drill: grep -n "return False\|return True\|return.*success\|return.*failed" \
             flashcore/cli/review_ui.py flashcore/cli/_review_logic.py
    check: start_review_flow returns a bool; _review_logic.py raises typer.Exit(code=1)
           when return value indicates total failure
    pass: grep output is non-empty at the relevant sites; a test verifies the bool is
          returned and the caller acts on it

  Path B — raise-on-exit variant:
    drill: grep -n "typer.Exit\|raise.*Exit" flashcore/cli/review_ui.py
    check: start_review_flow raises typer.Exit(code=1) when all fail
    pass: grep output non-empty; a test asserts pytest.raises(typer.Exit) or SystemExit

[6] EXISTING EXCEPTION TEST STRENGTHENED

    cmd: pytest tests/cli/test_review_ui.py::test_start_review_flow_submit_review_exception \
           -v --tb=short
    check: test no longer uses get_next_card.side_effect=[card, None] as the only loop
           termination; asserts that call_count is bounded (Path A) or loop breaks (Path B)
    drill: grep -n "side_effect.*None\|call_count" tests/cli/test_review_ui.py
    pass: test passes with the strengthened assertion; the masked-loop pattern is removed

[7] ADVANCE MECHANISM DECISION RECORDED IN COMMIT LOG

    cmd: git log --oneline HEAD~5..HEAD
    check: at least one commit message names the chosen mechanism:
           Path A → "private _remove_card_from_queue" or "public skip_card method"
           Path B → "break on first failure" or "bound-and-exit"
    pass: mechanism identifiable from git log without reading the diff

── FLOOR SLOTS ────────────────────────────────────────────────────────────────

[8] TYPECHECK + LOCAL-CI PASSES

    cmd: source .venv/bin/activate && make lint && pytest tests/ -q --tb=short
    pass: exit 0; zero new mypy errors; zero new flake8/black violations; at least 482
          tests collected (baseline 480 + ≥2 new); 1 skipped acceptable; 0 failures

[9] AIV PACKET VALIDATES

    cmd: aiv check .github/aiv-packets/PACKET_c2-f82_*.md
    pass: exit 0; no blocking errors reported
    note: E010 trap — avoid "fix/fixed/resolve/resolved" in claim text; rephrase to
          "corrects", "bounds", "suppresses", "updates", etc.

[10] PROGRESS TRACKER CLOSURE

    drill: grep -rn "F82\|review_ui.*retry\|infinite.*retry" .taskmaster/tasks/ 2>/dev/null
    check: if a task entry for F82 exists, the relevant subtask is marked completed in
           the .taskmaster/tasks/task_NNN.md file and that change is committed
    pass: either grep returns no results (N/A — no taskmaster entry for this finding)
          OR the relevant subtask is marked done in a committed file

[11] REVIEW QUIET WINDOW

    check: read the full code-review body (not just the green-check status) before
           considering the PR mergeable; address or explicitly defer every BLOCKING finding
    pass: zero unresolved BLOCKING findings remain in the review body; non-blocking
          findings are acknowledged in a comment or a follow-up issue

[12] FINDING CLOSED

    cmd: git log --oneline --grep="F82" HEAD~10..HEAD
    check: at least one commit references F82 (e.g., "Close F82", "corrects F82",
           "addresses audit finding F82")
    pass: grep returns at least one commit

═══════════════════════════════════════════════════════════════════════════════
PRE-MERGE:
═══════════════════════════════════════════════════════════════════════════════

• AskUserQuestion gate: operator has confirmed Path A vs B, API exposure choice (A1),
  end-of-session message for mixed outcome, failure-signal mechanism, and test location
  — all four decisions resolved before first commit.

• Local-CI gate: `source .venv/bin/activate && make lint && pytest tests/ -q --tb=short`
  exits 0 on the agent's machine before each push; do not push knowing CI will fail.

• VERIFY [1]–[12] all green.

═══════════════════════════════════════════════════════════════════════════════
POST-MERGE:
═══════════════════════════════════════════════════════════════════════════════

• Bookkeeping: update `audit/02-static-audit.md` finding F82 status field to mark
  resolved (or note the commit SHA that lands the correction). If a taskmaster entry
  tracks F82, mark the subtask completed and commit the change.

• Unblock: none identified. F82 is an isolated correctness fix with no downstream
  PRs blocked on it.

• Triggers: if the failure-signal path was wired through a return-bool change to
  `start_review_flow`, verify no other callers silently broke:
    cmd: grep -rn "start_review_flow" flashcore/
    expected: only flashcore/cli/_review_logic.py:43 (single caller); confirm it
              handles the new return type correctly post-merge.
  If Path A added a public `skip_card` method to ReviewSessionManager, verify no
  other call site adopted it inadvertently:
    cmd: grep -rn "skip_card" flashcore/ tests/

• Retro-verify: run `pytest tests/cli/test_review_ui.py -q` on main after merge to
  confirm the CI gate did not regress; record pass/fail in the PR comment thread.

═══════════════════════════════════════════════════════════════════════════════
OUT-OF-SCOPE REMINDERS:
═══════════════════════════════════════════════════════════════════════════════

• Retry-with-backoff or per-card retry budget — architectural policy; open a new
  issue if desired. Not part of this PR.
• F83–F114 — each finding is a separate PR. No cross-finding scope creep.
• ReviewSessionManager iterator refactor — architectural; out of scope by design.
• F85 (DB connection leak in _review_logic.py) — separate PR for F85.
• Changes to _review_all_logic.py — separate code path; not in scope.

===== END CONTRACT =====
