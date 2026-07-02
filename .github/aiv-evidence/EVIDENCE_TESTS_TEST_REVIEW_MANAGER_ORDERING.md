# AIV Evidence File (v1.0)

**File:** `tests/test_review_manager_ordering.py`
**Commit:** `b2f8ba5`
**Previous:** `b15bcde`
**Generated:** 2026-06-26T00:16:08Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/test_review_manager_ordering.py"
  classification_rationale: "R2: test for bug fix"
  classified_by: "Claude"
  classified_at: "2026-06-26T00:16:08Z"
```

## Claim(s)

1. Test verifies that initialize_session preserves DB ordering by next_due_date instead of re-sorting by modified_at
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L180](https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L180)
- **Requirements Verified:** F170: add test for ordering fix

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`b2f8ba5`](https://github.com/ImmortalDemonGod/flashcore/tree/b2f8ba5f10b7b80cabcabb9fc39f3df8a906e584))

- [`tests/test_review_manager_ordering.py#L2-L3`](https://github.com/ImmortalDemonGod/flashcore/blob/b2f8ba5f10b7b80cabcabb9fc39f3df8a906e584/tests/test_review_manager_ordering.py#L2-L3)
- [`tests/test_review_manager_ordering.py#L5`](https://github.com/ImmortalDemonGod/flashcore/blob/b2f8ba5f10b7b80cabcabb9fc39f3df8a906e584/tests/test_review_manager_ordering.py#L5)
- [`tests/test_review_manager_ordering.py#L7-L9`](https://github.com/ImmortalDemonGod/flashcore/blob/b2f8ba5f10b7b80cabcabb9fc39f3df8a906e584/tests/test_review_manager_ordering.py#L7-L9)
- [`tests/test_review_manager_ordering.py#L13-L15`](https://github.com/ImmortalDemonGod/flashcore/blob/b2f8ba5f10b7b80cabcabb9fc39f3df8a906e584/tests/test_review_manager_ordering.py#L13-L15)
- [`tests/test_review_manager_ordering.py#L17-L45`](https://github.com/ImmortalDemonGod/flashcore/blob/b2f8ba5f10b7b80cabcabb9fc39f3df8a906e584/tests/test_review_manager_ordering.py#L17-L45)
- [`tests/test_review_manager_ordering.py#L48`](https://github.com/ImmortalDemonGod/flashcore/blob/b2f8ba5f10b7b80cabcabb9fc39f3df8a906e584/tests/test_review_manager_ordering.py#L48)
- [`tests/test_review_manager_ordering.py#L50-L61`](https://github.com/ImmortalDemonGod/flashcore/blob/b2f8ba5f10b7b80cabcabb9fc39f3df8a906e584/tests/test_review_manager_ordering.py#L50-L61)
- [`tests/test_review_manager_ordering.py#L63-L72`](https://github.com/ImmortalDemonGod/flashcore/blob/b2f8ba5f10b7b80cabcabb9fc39f3df8a906e584/tests/test_review_manager_ordering.py#L63-L72)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`mock_db`** (L2-L3): FAIL -- WARNING: No tests import or call `mock_db`
- **`test_initialize_session_respects_due_date_order`** (L5): FAIL -- WARNING: No tests import or call `test_initialize_session_respects_due_date_order`

**Coverage summary:** 0/2 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** 26 error(s)
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | Test verifies that initialize_session preserves DB ordering ... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (0/2 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Unit test for review queue ordering
