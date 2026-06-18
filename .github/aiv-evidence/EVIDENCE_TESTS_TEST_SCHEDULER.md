# AIV Evidence File (v1.0)

**File:** `tests/test_scheduler.py`
**Commit:** `96a03dd`
**Generated:** 2026-06-18T19:58:32Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/test_scheduler.py"
  classification_rationale: "Test-only change, no runtime surface; bounded to the scheduler suite."
  classified_by: "Claude"
  classified_at: "2026-06-18T19:58:32Z"
```

## Claim(s)

1. compute_next_state, called with last_review_ts seven days before an on-time review_ts, returns SchedulerOutput.elapsed_days == 7 (exercised by the new scheduler test)
2. compute_next_state called with last_review_ts equal to review_ts returns elapsed_days == 0 with a stability distinct from the seven-day case (same-instant re-review invariant)
3. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/blob/b5e1c4b983b33602e8531340f382c72626a0fb59/flashcore/scheduler.py#L211](https://github.com/ImmortalDemonGod/flashcore/blob/b5e1c4b983b33602e8531340f382c72626a0fb59/flashcore/scheduler.py#L211)
- **Requirements Verified:** A regression test must lock the corrected contract so on-time elapsed-days can never silently revert (corpus C2)

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`96a03dd`](https://github.com/ImmortalDemonGod/flashcore/tree/96a03dd0ff7020cc76ed1be39158db966dac3a78))

- [`tests/test_scheduler.py#L521-L522`](https://github.com/ImmortalDemonGod/flashcore/blob/96a03dd0ff7020cc76ed1be39158db966dac3a78/tests/test_scheduler.py#L521-L522)
- [`tests/test_scheduler.py#L531`](https://github.com/ImmortalDemonGod/flashcore/blob/96a03dd0ff7020cc76ed1be39158db966dac3a78/tests/test_scheduler.py#L531)
- [`tests/test_scheduler.py#L697-L737`](https://github.com/ImmortalDemonGod/flashcore/blob/96a03dd0ff7020cc76ed1be39158db966dac3a78/tests/test_scheduler.py#L697-L737)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`test_review_processor_process_review_success`** (L521-L522): FAIL -- WARNING: No tests import or call `test_review_processor_process_review_success`
- **`test_on_time_review_uses_prior_review_ts_not_due_date`** (L531): FAIL -- WARNING: No tests import or call `test_on_time_review_uses_prior_review_ts_not_due_date`

**Coverage summary:** 0/2 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** 0 error(s)
- **mypy:** 

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | compute_next_state, called with last_review_ts seven days be... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | compute_next_state called with last_review_ts equal to revie... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 3 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 3 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (0/2 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Regression test pins the prior-review elapsed-days contract
