# AIV Evidence File (v1.0)

**File:** `flashcore/scheduler.py`
**Commit:** `dfd5d5f`
**Previous:** `1572e54`
**Generated:** 2026-06-29T20:41:07Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "flashcore/scheduler.py"
  classification_rationale: "R1 correctness-critical FSRS scheduling path"
  classified_by: "Miguel Ingram"
  classified_at: "2026-06-29T20:41:07Z"
```

## Claim(s)

1. FSRS_Scheduler.compute_next_state returns next_due as a datetime preserving sub-day learning-step spacing
2. FSRS_Scheduler.compute_next_state restores and emits the FSRS learning step so Learning cards progress across reviews
3. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/pull/58](https://github.com/ImmortalDemonGod/flashcore/pull/58)
- **Requirements Verified:** Learning steps must keep sub-day spacing and graduate; the prior .date() truncation broke both

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`dfd5d5f`](https://github.com/ImmortalDemonGod/flashcore/tree/dfd5d5fe2f621dc005433cc66fffe5d25ba7033a))

- [`flashcore/scheduler.py#L41-L43`](https://github.com/ImmortalDemonGod/flashcore/blob/dfd5d5fe2f621dc005433cc66fffe5d25ba7033a/flashcore/scheduler.py#L41-L43)
- [`flashcore/scheduler.py#L48`](https://github.com/ImmortalDemonGod/flashcore/blob/dfd5d5fe2f621dc005433cc66fffe5d25ba7033a/flashcore/scheduler.py#L48)
- [`flashcore/scheduler.py#L208-L212`](https://github.com/ImmortalDemonGod/flashcore/blob/dfd5d5fe2f621dc005433cc66fffe5d25ba7033a/flashcore/scheduler.py#L208-L212)
- [`flashcore/scheduler.py#L214-L216`](https://github.com/ImmortalDemonGod/flashcore/blob/dfd5d5fe2f621dc005433cc66fffe5d25ba7033a/flashcore/scheduler.py#L214-L216)
- [`flashcore/scheduler.py#L218`](https://github.com/ImmortalDemonGod/flashcore/blob/dfd5d5fe2f621dc005433cc66fffe5d25ba7033a/flashcore/scheduler.py#L218)
- [`flashcore/scheduler.py#L268-L270`](https://github.com/ImmortalDemonGod/flashcore/blob/dfd5d5fe2f621dc005433cc66fffe5d25ba7033a/flashcore/scheduler.py#L268-L270)
- [`flashcore/scheduler.py#L277`](https://github.com/ImmortalDemonGod/flashcore/blob/dfd5d5fe2f621dc005433cc66fffe5d25ba7033a/flashcore/scheduler.py#L277)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`SchedulerOutput`** (L41-L43): PASS -- 1 test(s) call `SchedulerOutput` directly
  - `tests/test_scheduler.py::test_review_processor_process_review_success`
- **`FSRS_Scheduler`** (L48): PASS -- 13 test(s) call `FSRS_Scheduler` directly
  - `tests/test_review_manager.py::test_e2e_session_flow`
  - `tests/test_review_logic_duplication.py::test_both_methods_have_identical_core_logic`
  - `tests/test_review_logic_duplication.py::test_maintenance_hazard_demonstration`
  - `tests/test_scheduler.py::test_mature_card_lapse`
  - `tests/test_scheduler.py::test_config_impact_on_scheduling`
  - `tests/test_rating_system_inconsistency.py::test_review_manager_uses_unified_rating_scale`
  - `tests/test_rating_system_inconsistency.py::test_review_all_logic_uses_unified_rating_scale`
  - `tests/test_rating_system_inconsistency.py::test_rating_consistency_after_fix`
  - `tests/test_session_analytics_gaps.py::test_review_session_manager_now_creates_session_objects`
  - `tests/test_session_analytics_gaps.py::test_review_workflows_now_have_session_integration`
- **`FSRS_Scheduler.compute_next_state`** (L208-L212): PASS -- 15 test(s) call `compute_next_state` directly
  - `tests/test_scheduler.py::test_first_review_new_card`
  - `tests/test_scheduler.py::test_invalid_rating_input`
  - `tests/test_scheduler.py::test_rating_impact_on_interval`
  - `tests/test_scheduler.py::test_multiple_reviews_stability_increase`
  - `tests/test_scheduler.py::test_review_lapsed_card`
  - `tests/test_scheduler.py::test_review_early_card`
  - `tests/test_scheduler.py::test_mature_card_lapse`
  - `tests/test_scheduler.py::test_compute_next_state_with_unknown_fsrs_state`
  - `tests/test_scheduler.py::test_compute_next_state_review_card_fallback_no_now_kw`
  - `tests/test_scheduler.py::test_config_impact_on_scheduling`

**Coverage summary:** 3/3 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | FSRS_Scheduler.compute_next_state returns next_due as a date... | symbol | 28 test(s) call `FSRS_Scheduler.compute_next_state`, `FSRS_Scheduler` | PASS VERIFIED |
| 2 | FSRS_Scheduler.compute_next_state restores and emits the FSR... | symbol | 28 test(s) call `FSRS_Scheduler.compute_next_state`, `FSRS_Scheduler` | PASS VERIFIED |
| 3 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 2 verified, 0 unverified, 1 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (3/3 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Full datetime due + step restore/persist in scheduler
