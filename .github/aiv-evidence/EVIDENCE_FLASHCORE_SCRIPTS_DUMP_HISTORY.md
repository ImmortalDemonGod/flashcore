# AIV Evidence File (v1.0)

**File:** `flashcore/scripts/dump_history.py`
**Commit:** `4234480`
**Generated:** 2026-03-22T03:28:59Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "flashcore/scripts/dump_history.py"
  classification_rationale: "New utility scripts and documentation; no changes to core library logic"
  classified_by: "Miguel Ingram"
  classified_at: "2026-03-22T03:28:59Z"
```

## Claim(s)

1. dump_history.py exports cards, reviews, and sessions from legacy DuckDB to JSON without importing HPE_ARCHIVE
2. migrate.py import_from_json() initialises the canonical schema and bulk-inserts all rows from JSON files
3. validate_migration() detects orphaned reviews, stability-range violations, and schema-sanity failures
4. README updated: Status section reflects Tasks 1-8 complete; CLI usage block added; Migration Guide section added
5. pyproject.toml description fixed; flashcore.scripts excluded from package discovery
6. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/blob/27797f4/.taskmaster/tasks/task_008.md](https://github.com/ImmortalDemonGod/flashcore/blob/27797f4/.taskmaster/tasks/task_008.md)
- **Requirements Verified:** Task 8: Implement Data Safety Strategy — export script, import utility, and validation queries

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`4234480`](https://github.com/ImmortalDemonGod/flashcore/tree/423448045ef6389c9dc0a0da38e900db1a232b09))

- [`flashcore/scripts/dump_history.py#L1-L136`](https://github.com/ImmortalDemonGod/flashcore/blob/423448045ef6389c9dc0a0da38e900db1a232b09/flashcore/scripts/dump_history.py#L1-L136)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`_serialize`** (L1-L136): FAIL -- WARNING: No tests import or call `_serialize`
- **`_rows_to_json`** (unknown): FAIL -- WARNING: No tests import or call `_rows_to_json`
- **`dump_table`** (unknown): FAIL -- WARNING: No tests import or call `dump_table`
- **`dump_database`** (unknown): FAIL -- WARNING: No tests import or call `dump_database`
- **`main`** (unknown): PASS -- 1 test(s) call `main` directly
  - `tests/cli/test_main.py::test_main_handles_unexpected_exception`

**Coverage summary:** 1/5 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | dump_history.py exports cards, reviews, and sessions from le... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | migrate.py import_from_json() initialises the canonical sche... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 3 | validate_migration() detects orphaned reviews, stability-ran... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 4 | README updated: Status section reflects Tasks 1-8 complete; ... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 5 | pyproject.toml description fixed; flashcore.scripts excluded... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 6 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 6 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (1/5 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Add JSON-based export/import migration path and update README for GA readiness
