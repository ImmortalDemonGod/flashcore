# AIV Evidence File (v1.0)

**File:** `tests/test_review_manager_order.py`
**Commit:** `b2449c7`
**Previous:** `5942a36`
**Generated:** 2026-06-26T03:51:47Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/test_review_manager_order.py"
  classification_rationale: "R1: test-only change; strengthens oracle correctness without touching production code"
  classified_by: "Claude"
  classified_at: "2026-06-26T03:51:47Z"
```

## Claim(s)

1. Cards now have modified_at in reverse order of added_at; sorted(…,key=modified_at) yields [card3,card2,card1] while DB order yields [card1,card2,card3] — test now fails on the buggy implementation
2. All 496 tests pass at HEAD after the change
3. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L180](https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L180)
- **Requirements Verified:** Test must demonstrate failure on the buggy modified_at sort

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`b2449c7`](https://github.com/ImmortalDemonGod/flashcore/tree/b2449c74b1af43ea8b6036ef08a207df75e314a9))

- [`tests/test_review_manager_order.py#L23-L27`](https://github.com/ImmortalDemonGod/flashcore/blob/b2449c74b1af43ea8b6036ef08a207df75e314a9/tests/test_review_manager_order.py#L23-L27)
- [`tests/test_review_manager_order.py#L33-L34`](https://github.com/ImmortalDemonGod/flashcore/blob/b2449c74b1af43ea8b6036ef08a207df75e314a9/tests/test_review_manager_order.py#L33-L34)
- [`tests/test_review_manager_order.py#L41-L42`](https://github.com/ImmortalDemonGod/flashcore/blob/b2449c74b1af43ea8b6036ef08a207df75e314a9/tests/test_review_manager_order.py#L41-L42)
- [`tests/test_review_manager_order.py#L49-L50`](https://github.com/ImmortalDemonGod/flashcore/blob/b2449c74b1af43ea8b6036ef08a207df75e314a9/tests/test_review_manager_order.py#L49-L50)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`db_with_three_due_cards`** (L23-L27): FAIL -- WARNING: No tests import or call `db_with_three_due_cards`

**Coverage summary:** 0/1 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | Cards now have modified_at in reverse order of added_at; sor... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | All 496 tests pass at HEAD after the change | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 3 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 3 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (0/1 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Set reversed modified_at values in test fixture so oracle is not accidentally satisfied by the bug
