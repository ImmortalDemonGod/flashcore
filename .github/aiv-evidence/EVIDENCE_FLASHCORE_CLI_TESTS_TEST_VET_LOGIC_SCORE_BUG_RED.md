# AIV Evidence File (v1.0)

**File:** `flashcore/cli/tests/test_vet_logic_score_bug_red.py`
**Commit:** `87047af`
**Previous:** `4f3ce12`
**Generated:** 2026-06-25T21:30:22Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "flashcore/cli/tests/test_vet_logic_score_bug_red.py"
  classification_rationale: "high"
  classified_by: "Claude"
  classified_at: "2026-06-25T21:30:22Z"
```

## Claim(s)

1. _validate_and_normalize_card fails to strip score field causing ValidationError
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L93](https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L93)
- **Requirements Verified:** test

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`87047af`](https://github.com/ImmortalDemonGod/flashcore/tree/87047af33a6b221efa06ba76b4e33aab883a73b4))

- [`flashcore/cli/tests/test_vet_logic_score_bug_red.py#L1`](https://github.com/ImmortalDemonGod/flashcore/blob/87047af33a6b221efa06ba76b4e33aab883a73b4/flashcore/cli/tests/test_vet_logic_score_bug_red.py#L1)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`<module>`** (L1): FAIL -- WARNING: No tests import or call `<module>`

**Coverage summary:** 0/1 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | _validate_and_normalize_card fails to strip score field caus... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (0/1 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Red test for score field bug
