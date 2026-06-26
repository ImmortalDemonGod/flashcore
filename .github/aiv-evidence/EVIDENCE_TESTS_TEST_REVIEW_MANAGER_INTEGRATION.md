# AIV Evidence File (v1.0)

**File:** `tests/test_review_manager_integration.py`
**Commit:** `5942a36`
**Previous:** `8de67de`
**Generated:** 2026-06-26T00:17:27Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/test_review_manager_integration.py"
  classification_rationale: "R2: test fix"
  classified_by: "Claude"
  classified_at: "2026-06-26T00:17:27Z"
```

## Claim(s)

1. Test verifies that reviewing a card doesn't break due date ordering in the queue
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L180](https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L180)
- **Requirements Verified:** F170: fix integration test

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`5942a36`](https://github.com/ImmortalDemonGod/flashcore/tree/5942a363643e8e13a9b5e85f6e0ff64fb0e3e23a))

- [`tests/test_review_manager_integration.py#L2`](https://github.com/ImmortalDemonGod/flashcore/blob/5942a363643e8e13a9b5e85f6e0ff64fb0e3e23a/tests/test_review_manager_integration.py#L2)
- [`tests/test_review_manager_integration.py#L7-L9`](https://github.com/ImmortalDemonGod/flashcore/blob/5942a363643e8e13a9b5e85f6e0ff64fb0e3e23a/tests/test_review_manager_integration.py#L7-L9)
- [`tests/test_review_manager_integration.py#L13`](https://github.com/ImmortalDemonGod/flashcore/blob/5942a363643e8e13a9b5e85f6e0ff64fb0e3e23a/tests/test_review_manager_integration.py#L13)
- [`tests/test_review_manager_integration.py#L15-L43`](https://github.com/ImmortalDemonGod/flashcore/blob/5942a363643e8e13a9b5e85f6e0ff64fb0e3e23a/tests/test_review_manager_integration.py#L15-L43)
- [`tests/test_review_manager_integration.py#L47-L48`](https://github.com/ImmortalDemonGod/flashcore/blob/5942a363643e8e13a9b5e85f6e0ff64fb0e3e23a/tests/test_review_manager_integration.py#L47-L48)
- [`tests/test_review_manager_integration.py#L50`](https://github.com/ImmortalDemonGod/flashcore/blob/5942a363643e8e13a9b5e85f6e0ff64fb0e3e23a/tests/test_review_manager_integration.py#L50)
- [`tests/test_review_manager_integration.py#L53`](https://github.com/ImmortalDemonGod/flashcore/blob/5942a363643e8e13a9b5e85f6e0ff64fb0e3e23a/tests/test_review_manager_integration.py#L53)
- [`tests/test_review_manager_integration.py#L55-L65`](https://github.com/ImmortalDemonGod/flashcore/blob/5942a363643e8e13a9b5e85f6e0ff64fb0e3e23a/tests/test_review_manager_integration.py#L55-L65)
- [`tests/test_review_manager_integration.py#L67`](https://github.com/ImmortalDemonGod/flashcore/blob/5942a363643e8e13a9b5e85f6e0ff64fb0e3e23a/tests/test_review_manager_integration.py#L67)
- [`tests/test_review_manager_integration.py#L69-L74`](https://github.com/ImmortalDemonGod/flashcore/blob/5942a363643e8e13a9b5e85f6e0ff64fb0e3e23a/tests/test_review_manager_integration.py#L69-L74)
- [`tests/test_review_manager_integration.py#L76-L78`](https://github.com/ImmortalDemonGod/flashcore/blob/5942a363643e8e13a9b5e85f6e0ff64fb0e3e23a/tests/test_review_manager_integration.py#L76-L78)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`mock_db`** (L2): FAIL -- WARNING: No tests import or call `mock_db`
- **`mock_scheduler`** (L7-L9): FAIL -- WARNING: No tests import or call `mock_scheduler`
- **`test_review_flow_maintains_due_date_order`** (L13): FAIL -- WARNING: No tests import or call `test_review_flow_maintains_due_date_order`

**Coverage summary:** 0/3 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | Test verifies that reviewing a card doesn't break due date o... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (0/3 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Integration test for review flow
