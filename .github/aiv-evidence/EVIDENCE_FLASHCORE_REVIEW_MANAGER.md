# AIV Evidence File (v1.0)

**File:** `flashcore/review_manager.py`
**Commit:** `1d25c22`
**Previous:** `1d25c22`
**Generated:** 2026-06-25T22:04:55Z
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
  classified_at: "2026-06-25T22:04:55Z"
```

## Claim(s)

1. Provides ReviewManager compatibility and sorts by next_due_date
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L180](https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L180)
- **Requirements Verified:** F170 ordering bug fix

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`1d25c22`](https://github.com/ImmortalDemonGod/flashcore/tree/1d25c2212d53adf446c4f7bcb11c1bed9c397f52))

- [`flashcore/review_manager.py#L43`](https://github.com/ImmortalDemonGod/flashcore/blob/1d25c2212d53adf446c4f7bcb11c1bed9c397f52/flashcore/review_manager.py#L43)
- [`flashcore/review_manager.py#L58`](https://github.com/ImmortalDemonGod/flashcore/blob/1d25c2212d53adf446c4f7bcb11c1bed9c397f52/flashcore/review_manager.py#L58)
- [`flashcore/review_manager.py#L65`](https://github.com/ImmortalDemonGod/flashcore/blob/1d25c2212d53adf446c4f7bcb11c1bed9c397f52/flashcore/review_manager.py#L65)
- [`flashcore/review_manager.py#L69`](https://github.com/ImmortalDemonGod/flashcore/blob/1d25c2212d53adf446c4f7bcb11c1bed9c397f52/flashcore/review_manager.py#L69)
- [`flashcore/review_manager.py#L71-L72`](https://github.com/ImmortalDemonGod/flashcore/blob/1d25c2212d53adf446c4f7bcb11c1bed9c397f52/flashcore/review_manager.py#L71-L72)
- [`flashcore/review_manager.py#L86`](https://github.com/ImmortalDemonGod/flashcore/blob/1d25c2212d53adf446c4f7bcb11c1bed9c397f52/flashcore/review_manager.py#L86)
- [`flashcore/review_manager.py#L104-L124`](https://github.com/ImmortalDemonGod/flashcore/blob/1d25c2212d53adf446c4f7bcb11c1bed9c397f52/flashcore/review_manager.py#L104-L124)
- [`flashcore/review_manager.py#L128-L129`](https://github.com/ImmortalDemonGod/flashcore/blob/1d25c2212d53adf446c4f7bcb11c1bed9c397f52/flashcore/review_manager.py#L128-L129)
- [`flashcore/review_manager.py#L132`](https://github.com/ImmortalDemonGod/flashcore/blob/1d25c2212d53adf446c4f7bcb11c1bed9c397f52/flashcore/review_manager.py#L132)
- [`flashcore/review_manager.py#L135`](https://github.com/ImmortalDemonGod/flashcore/blob/1d25c2212d53adf446c4f7bcb11c1bed9c397f52/flashcore/review_manager.py#L135)
- [`flashcore/review_manager.py#L141-L142`](https://github.com/ImmortalDemonGod/flashcore/blob/1d25c2212d53adf446c4f7bcb11c1bed9c397f52/flashcore/review_manager.py#L141-L142)
- [`flashcore/review_manager.py#L146-L151`](https://github.com/ImmortalDemonGod/flashcore/blob/1d25c2212d53adf446c4f7bcb11c1bed9c397f52/flashcore/review_manager.py#L146-L151)
- [`flashcore/review_manager.py#L174-L175`](https://github.com/ImmortalDemonGod/flashcore/blob/1d25c2212d53adf446c4f7bcb11c1bed9c397f52/flashcore/review_manager.py#L174-L175)
- [`flashcore/review_manager.py#L177-L178`](https://github.com/ImmortalDemonGod/flashcore/blob/1d25c2212d53adf446c4f7bcb11c1bed9c397f52/flashcore/review_manager.py#L177-L178)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`<parse-error>`** (L43): FAIL -- WARNING: No tests import or call `<parse-error>`

**Coverage summary:** 0/1 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** 9 error(s)
- **mypy:** Found 1 error in 1 file (errors prevented further checking)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | Provides ReviewManager compatibility and sorts by next_due_d... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (0/1 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Legacy shim and ordering
