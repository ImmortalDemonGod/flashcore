# AIV Evidence File (v1.0)

**File:** `flashcore/review_manager.py`
**Commit:** `a233a9d`
**Previous:** `0aa4621`
**Generated:** 2026-06-25T22:14:35Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "flashcore/review_manager.py"
  classification_rationale: "high"
  classified_by: "Claude"
  classified_at: "2026-06-25T22:14:35Z"
```

## Claim(s)

1. ReviewManager now sorts due cards by next due date instead of modified_at
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L180](https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L180)
- **Requirements Verified:** Fix ordering bug

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`a233a9d`](https://github.com/ImmortalDemonGod/flashcore/tree/a233a9d81c0295a336d3d87a0461593065556ceb))

- [`flashcore/review_manager.py#L1`](https://github.com/ImmortalDemonGod/flashcore/blob/a233a9d81c0295a336d3d87a0461593065556ceb/flashcore/review_manager.py#L1)
- [`flashcore/review_manager.py#L5`](https://github.com/ImmortalDemonGod/flashcore/blob/a233a9d81c0295a336d3d87a0461593065556ceb/flashcore/review_manager.py#L5)
- [`flashcore/review_manager.py#L343-L347`](https://github.com/ImmortalDemonGod/flashcore/blob/a233a9d81c0295a336d3d87a0461593065556ceb/flashcore/review_manager.py#L343-L347)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`ReviewManager`** (L1): PASS -- 1 test(s) call `ReviewManager` directly
  - `tests/test_review_manager_order.py::test_review_manager_ordering_by_due_date`

**Coverage summary:** 1/1 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | ReviewManager now sorts due cards by next due date instead o... | symbol | 1 test(s) call `ReviewManager` | PASS VERIFIED |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 1 verified, 0 unverified, 1 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (1/1 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Sort due cards correctly
