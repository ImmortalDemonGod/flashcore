# AIV Verification Packet (v2.2)

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/ImmortalDemonGod/flashcore |
| **Change ID** | c2-fsrs-elapsed-days |
| **Commits** | `8c9fa36`, `96a03dd`, `f801290`, `413bc62` |
| **Head SHA** | `413bc62` |
| **Base SHA** | `b5e1c4b` |
| **Created** | 2026-06-18T19:58:55Z |

## Classification

```yaml
classification:
  risk_tier: R2
  sod_mode: S0
  critical_surfaces: []
  blast_radius: component
  classification_rationale: >
    Touches the core FSRS scheduling engine (compute_next_state) consumed by
    review_processor. The added parameter defaults to the prior behavior, but the
    production call path (review_processor) now supplies a real prior-review
    timestamp, so the scheduling output of every on-time review changes — a
    component-level behavioral change, not a local one. Per the spec's round-up
    rule the additive-default detail does not pull this below R2.
  sod_waiver: >
    R2 normally requires S1 (two distinct natural persons). This is a solo + AI
    workflow; per the aiv-protocol exception section and flashcore's established
    convention, we proceed S0 with the AI as Verifier and the directing human as
    the single independent final evidence judge (H2). Future maturity path: a CI
    gate requiring a second-human verifier_id. This waiver is a ratified policy
    decision for the Polymath Track, not a one-off.
  classified_by: "ImmortalDemonGod (Author) + Claude (Verifier)"
  classified_at: "2026-06-18T19:58:55Z"
```

## Claim(s)

1. compute_next_state accepts an optional last_review_ts; when provided, fsrs_card.last_review is set from it (UTC-normalized) rather than the due date
2. An on-time review (review_ts == next_due_date) with a prior-review timestamp 7 days earlier yields SchedulerOutput.elapsed_days == 7, not 0
3. When last_review_ts is None, behavior is unchanged (new cards and history-less callers fall back to the due-date approximation)
4. Exactly one existing test was modified: `test_review_processor_process_review_success` had its `assert_called_once_with` updated to expect the new `last_review_ts=None` argument for a new card; no other existing tests were modified or deleted. Full-suite baseline isolation: clean base (b5e1c4b) = 464 passed / 1 skipped / 16 pre-existing errors; this change = 465 passed / 1 skipped / 16 errors (same pre-existing errors in untouched files test_db.py/test_parser.py/test_yaml_validators.py — environmental, not change-caused, verified by stash-and-rerun). Net effect: +1 passing test, 0 regressions.
5. process_review fetches the latest review via db_manager.get_latest_review_for_card(card.uuid) and passes its ts as last_review_ts to compute_next_state
6. When the card has no prior review, last_review_ts is None and scheduler behavior is unchanged
7. The reviews-store lookup keeps the scheduler a pure spoke (no DB handle in scheduler), honoring the hub-and-spoke boundary
8. compute_next_state, called with last_review_ts seven days before an on-time review_ts, returns SchedulerOutput.elapsed_days == 7 (exercised by the new scheduler test)
9. compute_next_state called with last_review_ts equal to review_ts returns elapsed_days == 0 with a stability distinct from the seven-day case (same-instant re-review invariant)
10. tests/test_scheduler.bug-catalog.md records the ranked bug catalog (B1 on-time elapsed=0, B2 same-day invariant) and explicit skipped set

---

## Evidence

| # | Evidence File | Commit SHA | Classes |
|---|---------------|------------|---------|
| 1 | EVIDENCE_FLASHCORE_SCHEDULER.md | `8c9fa36` | A, B, C, E, F |
| 2 | EVIDENCE_FLASHCORE_REVIEW_PROCESSOR.md | `96a03dd` | A, B, C, E, F |
| 3 | EVIDENCE_TESTS_TEST_SCHEDULER.md | `f801290` | A, B, E |
| 4 | EVIDENCE_TESTS_TEST_SCHEDULER.BUG_CATALOG.MD.md | `413bc62` | A, B, E |

### Class A (Execution Evidence)

Test suite run on branch HEAD (`9d0b3129`), Python 3.11, Ubuntu:

- `test_on_time_review_uses_prior_review_ts_not_due_date` — PASS
- `test_review_processor_process_review_success` — PASS
- Full baseline: 465 passed / 1 skipped / 16 pre-existing errors (same 16 as clean base `b5e1c4b`, verified by stash-and-rerun)

---

### Class B (Referential Evidence)

**Scope Inventory** (from 9 file references across evidence files)

- `flashcore/scheduler.py#L191-L195`
- `flashcore/scheduler.py#L199-L211`
- `flashcore/scheduler.py#L228-L234`
- `flashcore/review_processor.py#L99-L104`
- `flashcore/review_processor.py#L107-L110`
- `tests/test_scheduler.py#L521-L522`
- `tests/test_scheduler.py#L531`
- `tests/test_scheduler.py#L697-L737`
- `tests/test_scheduler.bug-catalog.md#L1-L33`

---

### Class C (Negative Evidence)

Searched for and did not find:

- Any other call site that passes `last_review` to `compute_next_state` before this change: none found
- Any existing test deleted or `@pytest.mark.skip` added: none (only one `assert_called_once_with` updated for the new `last_review_ts=None` kwarg on a new-card call)
- The 16 pre-existing errors in `test_db.py`, `test_parser.py`, `test_yaml_validators.py` do NOT involve any file touched by this change — confirmed by stash-and-rerun on clean base

---

### Class D (Behavioral Evidence) — prove-it, diffed against cited baseline

Before/after on the on-time-review path, vs the exact ref the finding pins (`b5e1c4b`):

| State | on-time `elapsed_days` | resulting stability |
|---|--:|--:|
| BASE (b5e1c4b) | 0 | 5.1001 |
| FIX | 7 | 18.2399 |
| same-day re-review (FIX) | 0 | 5.1001 |

Artifacts (sha256 in `MANIFEST.sha256`): `.github/aiv-packets/evidence/C2_before.json`,
`C2_after.json`. The bug collapsed every on-time review to the zero-elapsed
stability (5.1001); the fix restores correct retrievability while still
distinguishing a genuine same-day re-review. Per-claim verdict: claims 1, 2, 3, 5,
6, 7, 8, 9 PASS; claim 4 PASS (baseline isolation recorded); claim 10 PASS. 0 UNVERIFIED.

---

### Class E (Intent Alignment)

The change is anchored to the audit finding's immutable evidence (corpus C2 / F4,
F87, F169, F255, F115), SHA-pinned to the cited baseline `b5e1c4b`:

- Intent — the defect line: <https://github.com/ImmortalDemonGod/flashcore/blob/b5e1c4b983b33602e8531340f382c72626a0fb59/flashcore/scheduler.py#L211-L212>
- Call site the hub repairs: <https://github.com/ImmortalDemonGod/flashcore/blob/b5e1c4b983b33602e8531340f382c72626a0fb59/flashcore/review_processor.py#L101>

**Requirement satisfied:** FSRS retrievability must derive from the real interval
since the prior review, not the due date. The audit recipe assumed a one-line edit;
grounding showed the prior-review timestamp is not in the scheduler's cached state,
so the intent is satisfied by plumbing it from the reviews store (hub) into the
scheduler (spoke) via a new optional parameter.

---

### Class F (Provenance Evidence)

Git chain-of-custody for the test change (collected by `aiv commit` per file; see
`EVIDENCE_TESTS_TEST_SCHEDULER.md` at commit `f801290`):

**Claim 4:** Exactly one existing test assertion was modified
(`test_review_processor_process_review_success`), and the full-suite baseline was
isolated by stash-and-rerun — clean base 464 passed / 16 pre-existing errors vs
465 passed / 16 errors with the change (net +1 test, 0 regressions).

**Justification:** The single existing-test edit is a contract update, not a
weakening: it changes an `assert_called_once_with` to expect the new
`last_review_ts=None` argument for a new card. No assertions were deleted, no
`@pytest.mark.skip` was added, and no test bodies were removed. The 16 errors are
pre-existing and environmental (untouched files `test_db.py`/`test_parser.py`/
`test_yaml_validators.py` in this fresh container), proven identical on the clean
base via `git stash`-and-rerun. The added regression test
`test_on_time_review_uses_prior_review_ts_not_due_date` is net-new coverage.

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence was collected by `aiv commit` during the change lifecycle.
Packet generated by `aiv close`.

---

## Known Limitations

- Evidence references point to Layer 1 evidence files at specific commit SHAs.
  Use `git show <sha>:.github/aiv-evidence/<file>` to retrieve.

---

## Summary

Change 'c2-fsrs-elapsed-days': 4 commit(s) across 4 file(s).
