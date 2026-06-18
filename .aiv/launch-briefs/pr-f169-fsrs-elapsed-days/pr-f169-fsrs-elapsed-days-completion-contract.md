===== PR-F169 COMPLETION CONTRACT - correct elapsed_days for on-time FSRS reviews =====

GOAL: Close finding F169 (CRITICAL). flashcore/scheduler.py:212 sets
fsrs_card.last_review = fsrs_card.due, causing elapsed_days=0 for any
Review-state card reviewed on its due date. This pins FSRS retrievability to
R=1.0 and corrupts the stability update for the normal review case. The fix
makes compute_next_state supply a last_review that reflects the actual prior
review date, not the due date. Verified when: (1) a new test confirms
elapsed_days > 0 for an on-time Review-state review, (2) a new test confirms
stability differs between on-time and same-day re-review, and (3) all 15
existing scheduler tests pass.

---

VERIFY (binary green/red):

[1] ON-TIME REVIEW PRODUCES elapsed_days > 0
    cmd: python -m pytest tests/test_scheduler.py::test_on_time_review_elapsed_days_positive -v
    pass: 1 passed, 0 failed; output shows elapsed_days > 0 for a Review-state card
          with next_due_date == review_ts.date()

[2] ON-TIME VS SAME-DAY STABILITY DISTINCT
    cmd: python -m pytest tests/test_scheduler.py::test_on_time_vs_same_day_review_stability_distinct -v
    pass: 1 passed, 0 failed; stability from on-time review != stability from same-day re-review
          at identical rating and card parameters

[3] PATH DECISION DOCUMENTED AND IMPLEMENTED (path-fork)
    Option A — last_review_date added to Card model:
    cmd: grep -n "last_review_date" flashcore/models.py flashcore/review_processor.py flashcore/scheduler.py
    Option A pass: last_review_date present in models.py AND populated in review_processor.py
                   AND consumed (not assigned from due) in scheduler.py:compute_next_state

    Option B — stability-based approximation in scheduler only:
    cmd: grep -n "timedelta.*stability\|stability.*timedelta\|max(1.*round\|round.*stability" flashcore/scheduler.py
    Option B pass: scheduler.py line ~212 replaced with a timedelta-from-stability expression;
                   models.py and review_processor.py show no diff

[4] LEARNING-STATE GUARD CORRECT
    cmd: python -m pytest tests/test_scheduler.py -k "new_card or learning or first_review" -v
    pass: all matching tests pass; no TypeError from None stability arithmetic

[5] NO REGRESSION — ALL EXISTING SCHEDULER TESTS PASS
    cmd: python -m pytest tests/test_scheduler.py -q --tb=short
    pass: 15 passed, 0 failed, 0 errors

[6] BUG SITE REPLACED
    cmd: grep -n "last_review = fsrs_card.due" flashcore/scheduler.py
    pass: no output (the offending assignment is gone)

[7] TYPECHECK CLEAN
    cmd: mypy flashcore/scheduler.py flashcore/models.py --ignore-missing-imports 2>&1 | tail -5
    pass: "Success: no issues found" or only pre-existing errors; zero new errors introduced

[8] PACKET VALIDATES
    cmd: aiv check .github/aiv-packets/PACKET_f169-fsrs-elapsed-days.md
    pass: exits 0, no blocking errors (E010 trigger words absent from claims; no bare Class E links)

[9] NO ATTRIBUTION — BRANCH SHAPE CORRECT
    cmd: git log feat/c2-pr-f169-fsrs-elapsed-days-b1 --format="%an | %s" | head -10
    pass: branch name matches feat/c2-pr-f169-fsrs-elapsed-days-b1 exactly;
          no commit author is an AI agent; Co-Authored-By tag present if pair-authored

[10] LOCAL CI PASSES
    cmd: python -m pytest tests/ -q --tb=short 2>&1 | tail -5
    pass: 480 passed, 1 skipped (baseline) or better; 0 failed

[11] PROGRESS-TRACKER CLOSURE
    check: .taskmaster/tasks/tasks.json or a task_NNN.md reflects F169 addressed.
           (review.coord_file not configured — coord-file slot dropped)
    cmd: grep -r "F169\|fsrs.*elapsed\|elapsed.*fsrs" .taskmaster/tasks/ --include="*.md" --include="*.json" | head -5
    pass: at least one entry references F169 as addressed or in-progress for this PR

[12] REVIEW QUIET WINDOW
    check: Reviewer has read the full diff and the code-review body.
           No blocking comments remain open.
    pass: operator confirms via AskUserQuestion before merge

[13] FINDING CLOSED
    check: Finding F169 marked resolved in audit artifacts.
    cmd: grep -r "F169" artifacts/ audit/ --include="*.md" --include="*.json" 2>/dev/null | head -5
    pass: at least one artifact references F169 as resolved/addressed,
          OR operator confirms an inline closing note in the PR description

---

PRE-MERGE:
- AskUserQuestion: "Has the full code-review diff been read and all blocking comments
  resolved?" → operator answers green before merge.
- AskUserQuestion: "Is the path decision (A or B) documented with a one-sentence
  rationale in the PR description?" → operator confirms.
- Confirm VERIFY [8]: `aiv check` exits 0 on the final packet. Do not merge with
  a blocking packet error.

---

POST-MERGE:
- Bookkeeping: Update `.taskmaster/tasks/tasks.json` to mark the F169 sub-item
  complete. Add a one-line note to the relevant `task_NNN.md` recording which path
  (A or B) was chosen and the commit SHA.
- Unblock: If Path A was taken, spin up the backfill follow-up PR
  (`feat/c2-pr-backfill-last-review-date`) and open a DB migration PR for
  stage-c2. If Path B, note the approximation boundary in the follow-up
  investigation ticket for F169b (early-review negative elapsed_days).
- Triggers: Run the full test suite one final time post-merge:
  `python -m pytest tests/ -q --tb=short`. Confirm 480 passed, 1 skipped.
- Retro-verify: After a real review session against a live DB, spot-check that
  `elapsed_days_at_review` values in the `reviews` table are > 0 for on-time
  reviews. N/A until integration testing is available post-merge.

---

OUT-OF-SCOPE REMINDERS:
- Backfill of historical last_review_date for existing DB cards
  → deferred to feat/c2-pr-backfill-last-review-date
- Persisting last_review_date as a SQLite column
  → deferred to stage-c2 DB migration PR (open before stage-c3 cutoff)
- Negative elapsed_days for early-review cards (test_review_early_card currently
  passes with elapsed_days=-2 for the early scenario, which is wrong)
  → deferred to new audit finding F169b; file in the stage-c2 audit pass
