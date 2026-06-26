# AIV Evidence File (v1.0)

**File:** `tests/test_review_manager_order.py`
**Commit:** `cbefb02`
**Previous:** `c503023`
**Generated:** 2026-06-26T00:16:48Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/test_review_manager_order.py"
  classification_rationale: "R2: integration test for bug fix"
  classified_by: "Claude"
  classified_at: "2026-06-26T00:16:48Z"
```

## Claim(s)

1. Test verifies that ReviewManager orders cards by next_due_date (earliest first) after initialize_session
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L180](https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L180)
- **Requirements Verified:** F170: add integration test for ordering

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`cbefb02`](https://github.com/ImmortalDemonGod/flashcore/tree/cbefb02428746c841c732c7772255ac6cb4749da))

- [`tests/test_review_manager_order.py#L2`](https://github.com/ImmortalDemonGod/flashcore/blob/cbefb02428746c841c732c7772255ac6cb4749da/tests/test_review_manager_order.py#L2)
- [`tests/test_review_manager_order.py#L4`](https://github.com/ImmortalDemonGod/flashcore/blob/cbefb02428746c841c732c7772255ac6cb4749da/tests/test_review_manager_order.py#L4)
- [`tests/test_review_manager_order.py#L6-L9`](https://github.com/ImmortalDemonGod/flashcore/blob/cbefb02428746c841c732c7772255ac6cb4749da/tests/test_review_manager_order.py#L6-L9)
- [`tests/test_review_manager_order.py#L13-L19`](https://github.com/ImmortalDemonGod/flashcore/blob/cbefb02428746c841c732c7772255ac6cb4749da/tests/test_review_manager_order.py#L13-L19)
- [`tests/test_review_manager_order.py#L21-L48`](https://github.com/ImmortalDemonGod/flashcore/blob/cbefb02428746c841c732c7772255ac6cb4749da/tests/test_review_manager_order.py#L21-L48)
- [`tests/test_review_manager_order.py#L51`](https://github.com/ImmortalDemonGod/flashcore/blob/cbefb02428746c841c732c7772255ac6cb4749da/tests/test_review_manager_order.py#L51)
- [`tests/test_review_manager_order.py#L53-L59`](https://github.com/ImmortalDemonGod/flashcore/blob/cbefb02428746c841c732c7772255ac6cb4749da/tests/test_review_manager_order.py#L53-L59)
- [`tests/test_review_manager_order.py#L61-L68`](https://github.com/ImmortalDemonGod/flashcore/blob/cbefb02428746c841c732c7772255ac6cb4749da/tests/test_review_manager_order.py#L61-L68)
- [`tests/test_review_manager_order.py#L70-L98`](https://github.com/ImmortalDemonGod/flashcore/blob/cbefb02428746c841c732c7772255ac6cb4749da/tests/test_review_manager_order.py#L70-L98)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`db_with_three_due_cards`** (L2): FAIL -- WARNING: No tests import or call `db_with_three_due_cards`
- **`test_review_manager_ordering_by_due_date`** (L4): FAIL -- WARNING: No tests import or call `test_review_manager_ordering_by_due_date`

**Coverage summary:** 0/2 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** 14 error(s)
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | Test verifies that ReviewManager orders cards by next_due_da... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (0/2 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Integration test for review queue ordering
