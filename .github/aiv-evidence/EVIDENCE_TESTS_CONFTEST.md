# AIV Evidence File (v1.0)

**File:** `tests/conftest.py`
**Commit:** `e195ae7`
**Previous:** `e195ae7`
**Generated:** 2026-06-24T06:55:07Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/conftest.py"
  classification_rationale: "R1: test-fixture UUID generation change; no production logic, no schema, no DB, no CLI path touched"
  classified_by: "Miguel Ingram"
  classified_at: "2026-06-24T06:55:07Z"
```

## Claim(s)

1. import uuid added to conftest.py import block; three card fixture definitions updated to use str(uuid.uuid4()) for the uuid field — producing distinct UUIDs on every test run
2. conftest card fixtures produce distinct UUIDs across runs; no test outside test_db.py asserts against conftest card fixture UUID literals
3. full suite count not lower than baseline 480 collected 1 skipped with uuid4 card fixtures active
4. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L18](https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L18)
- **Requirements Verified:** conftest card fixtures produce distinct UUIDs across runs per finding GOAL clause 2

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`e195ae7`](https://github.com/ImmortalDemonGod/flashcore/tree/e195ae76a6f715855b520c8a160836dfec957932))

- [`tests/conftest.py#L2`](https://github.com/ImmortalDemonGod/flashcore/blob/e195ae76a6f715855b520c8a160836dfec957932/tests/conftest.py#L2)
- [`tests/conftest.py#L120`](https://github.com/ImmortalDemonGod/flashcore/blob/e195ae76a6f715855b520c8a160836dfec957932/tests/conftest.py#L120)
- [`tests/conftest.py#L139`](https://github.com/ImmortalDemonGod/flashcore/blob/e195ae76a6f715855b520c8a160836dfec957932/tests/conftest.py#L139)
- [`tests/conftest.py#L161`](https://github.com/ImmortalDemonGod/flashcore/blob/e195ae76a6f715855b520c8a160836dfec957932/tests/conftest.py#L161)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`sample_card1`** (L2): FAIL -- WARNING: No tests import or call `sample_card1`
- **`sample_card2`** (L120): FAIL -- WARNING: No tests import or call `sample_card2`
- **`sample_card3_deck_b`** (L139): FAIL -- WARNING: No tests import or call `sample_card3_deck_b`

**Coverage summary:** 0/3 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** 13 error(s)
- **mypy:** Found 3 errors in 1 file (checked 1 source file)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | import uuid added to conftest.py import block; three card fi... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | conftest card fixtures produce distinct UUIDs across runs; n... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 3 | full suite count not lower than baseline 480 collected 1 ski... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 4 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 4 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (0/3 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Switch conftest card fixtures from constant UUID literals to uuid4() to satisfy GOAL clause 2
