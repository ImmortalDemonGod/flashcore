# Bug catalog — `flashcore/scheduler.py` `compute_next_state` elapsed-days

Built before writing tests (per `design-tests`). Source finding: audit corpus C2 / F4,F87,F169,F255,F115.

## Ranked bugs

### B1 — on-time review computes `elapsed_days = 0` (the C2 critical) — **HIGH blast radius, certain**
- **Failure mode:** `scheduler.py:212` sets `fsrs_card.last_review = fsrs_card.due`, then
  `elapsed_days = (review_ts.date() - fsrs_card.last_review.date()).days`. For an on-time review
  (`review_ts == next_due_date`), this is `0`. py-fsrs then sees zero elapsed time → retrievability
  `R = 1.0` → the stability/difficulty update treats every on-time review like a same-day re-review.
- **Blast radius:** the *entire* spaced-repetition engine (the 3/3-grounded primary goal). Every
  card reviewed on or near its due date — the normal case — gets a corrupted stability update and a
  wrong next interval. Also corrupts the persisted `Review.elapsed_days_at_review` analytics column.
- **Why plausible:** confirmed in source against `origin/main` (b5e1c4b). The comment "Set
  last_review to due date for elapsed_days calculation" documents the wrong intent.
- **Test type:** captured-bug / contract-pin — pin the corrected contract (`elapsed_days` derives
  from the *prior review timestamp*, not the due date) so the regression can never silently return.

### B2 — `elapsed_days` differs between a real interval and a same-day re-review — **invariant**
- **Failure mode:** if last_review is mis-sourced, a card last reviewed 7 days ago and a card
  re-reviewed the same instant produce the *same* `elapsed_days`. They must not.
- **Test type:** invariant/differential — same card, two `last_review_ts` values (prior vs now) must
  yield different `elapsed_days` (7 vs 0) and different stability.

## Skipped (explicit negative space)
- **FSRS weight-vector / DEFAULT_PARAMETERS alignment** — that is a *separate* critical (corpus C3,
  `depends_on: C2`). Out of scope for this PR; queued as its own finding.
- **Exact stability magnitude** under correct elapsed time — FSRS-version-sensitive; we assert
  *direction/inequality* (real-interval ≠ same-day), not a hard-coded float, to avoid a test that
  breaks under a behavior-preserving py-fsrs bump (fails bar #2).
- **review_processor DB wiring** — covered by its own existing mocked tests; here we pin the pure
  scheduler contract via the public `compute_next_state` interface.
