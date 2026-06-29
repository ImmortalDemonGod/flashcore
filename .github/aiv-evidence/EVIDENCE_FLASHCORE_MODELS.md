# AIV Evidence File (v1.0)

**File:** `flashcore/models.py`
**Commit:** `fb1ae5a`
**Previous:** `6a9311f`
**Generated:** 2026-06-29T20:39:46Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "flashcore/models.py"
  classification_rationale: "R1 correctness-critical FSRS data model"
  classified_by: "Miguel Ingram"
  classified_at: "2026-06-29T20:39:46Z"
```

## Claim(s)

1. Card.next_due_date and last_review_date are typed datetime (not date) so sub-day FSRS spacing is representable
2. Card.step (Optional int) is added under extra=forbid for persisting the FSRS learning-step index
3. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/pull/58](https://github.com/ImmortalDemonGod/flashcore/pull/58)
- **Requirements Verified:** Live deck 2026-06-29: learning-step spacing requires datetime dues + a persisted step field

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`fb1ae5a`](https://github.com/ImmortalDemonGod/flashcore/tree/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965))

- [`flashcore/models.py#L11`](https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/flashcore/models.py#L11)
- [`flashcore/models.py#L61`](https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/flashcore/models.py#L61)
- [`flashcore/models.py#L64-L66`](https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/flashcore/models.py#L64-L66)
- [`flashcore/models.py#L69`](https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/flashcore/models.py#L69)
- [`flashcore/models.py#L71-L75`](https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/flashcore/models.py#L71-L75)
- [`flashcore/models.py#L88-L95`](https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/flashcore/models.py#L88-L95)
- [`flashcore/models.py#L252`](https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/flashcore/models.py#L252)
- [`flashcore/models.py#L254-L258`](https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/flashcore/models.py#L254-L258)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`Card`** (L11): PASS -- 77 test(s) call `Card` directly
  - `tests/test_review_manager.py::test_start_session_populates_queue`
  - `tests/test_review_manager.py::test_start_session_clears_existing_queue`
  - `tests/test_review_manager.py::test_get_next_card_returns_card_from_queue`
  - `tests/test_review_manager.py::test_submit_review_removes_card_from_active_queue`
  - `tests/test_review_manager.py::test_skip_card_removes_card_from_queue`
  - `tests/test_review_manager.py::test_e2e_session_flow`
  - `tests/test_review_manager.py::test_initialize_session_with_tags`
  - `tests/test_review_manager.py::test_record_session_analytics_failure`
  - `tests/test_review_manager.py::test_get_session_stats_with_analytics`
  - `tests/test_review_manager.py::test_get_session_stats_analytics_failure`
- **`Review`** (L61): PASS -- 35 test(s) call `Review` directly
  - `tests/test_review_manager.py::test_submit_review_successful_with_history`
  - `tests/test_review_manager.py::test_e2e_session_flow`
  - `tests/test_db.py::test_get_due_cards_logic`
  - `tests/test_db.py::test_add_review_success`
  - `tests/test_db.py::test_add_review_fk_violation`
  - `tests/test_db.py::test_add_review_check_constraint_violation`
  - `tests/test_db.py::test_add_reviews_individually`
  - `tests/test_db.py::test_add_review_transactionality`
  - `tests/test_db.py::test_get_reviews_for_card`
  - `tests/test_db.py::test_get_latest_review_for_card`

**Coverage summary:** 2/2 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | Card.next_due_date and last_review_date are typed datetime (... | symbol | 112 test(s) call `Review`, `Card` | PASS VERIFIED |
| 2 | Card.step (Optional int) is added under extra=forbid for per... | symbol | 77 test(s) call `Card` | PASS VERIFIED |
| 3 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 2 verified, 0 unverified, 1 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (2/2 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

datetime dues and step field on Card/Review
