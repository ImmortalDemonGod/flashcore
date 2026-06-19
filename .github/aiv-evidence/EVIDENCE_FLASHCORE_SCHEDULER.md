# AIV Evidence File (v1.0)

**File:** `flashcore/scheduler.py`
**Commit:** `e0f6519`
**Generated:** 2026-06-19T05:27:58Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "flashcore/scheduler.py"
  classification_rationale: "R1: logic change in core scheduler; covered by acceptance tests in subsequent commits"
  classified_by: "Claude"
  classified_at: "2026-06-19T05:27:58Z"
```

## Claim(s)

1. Line 212 assignment last_review=due removed; replaced with conditional on card.last_review_date
2. When last_review_date is None (hub not populated), last_review remains unset; elapsed_days=0 (correct for New/first-ever review)
3. Scheduler does not read DB directly; last_review_date populated by hub before this call
4. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/blob/27797f4/.taskmaster/tasks/task_008.md](https://github.com/ImmortalDemonGod/flashcore/blob/27797f4/.taskmaster/tasks/task_008.md)
- **Requirements Verified:** D1.3: offending assignment gone; ground-truth path only; hub-supplied last_review_date drives elapsed_days

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`e0f6519`](https://github.com/ImmortalDemonGod/flashcore/tree/e0f6519fcee02a20f88367ae8e2c2fba59da6357))

- [`flashcore/scheduler.py#L211-L217`](https://github.com/ImmortalDemonGod/flashcore/blob/e0f6519fcee02a20f88367ae8e2c2fba59da6357/flashcore/scheduler.py#L211-L217)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`FSRS_Scheduler`** (L211-L217): PASS -- 13 test(s) call `FSRS_Scheduler` directly
  - `tests/test_session_analytics_gaps.py::test_review_session_manager_now_creates_session_objects`
  - `tests/test_session_analytics_gaps.py::test_review_workflows_now_have_session_integration`
  - `tests/test_session_analytics_gaps.py::test_missing_session_lifecycle_management`
  - `tests/test_session_analytics_gaps.py::test_missing_session_performance_analytics`
  - `tests/test_session_analytics_gaps.py::test_missing_real_time_session_tracking`
  - `tests/test_review_manager.py::test_e2e_session_flow`
  - `tests/test_scheduler.py::test_mature_card_lapse`
  - `tests/test_scheduler.py::test_config_impact_on_scheduling`
  - `tests/test_rating_system_inconsistency.py::test_review_manager_uses_unified_rating_scale`
  - `tests/test_rating_system_inconsistency.py::test_review_all_logic_uses_unified_rating_scale`
- **`FSRS_Scheduler.compute_next_state`** (unknown): PASS -- 13 test(s) call `compute_next_state` directly
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

**Coverage summary:** 2/2 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** 0 error(s)
- **mypy:** Found 2 errors in 2 files (checked 1 source file)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | Line 212 assignment last_review=due removed; replaced with c... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | When last_review_date is None (hub not populated), last_revi... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 3 | Scheduler does not read DB directly; last_review_date popula... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 4 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 4 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (2/2 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Use card.last_review_date for last_review when set; no stability proxy; remove wrong due-date proxy
