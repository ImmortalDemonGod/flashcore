# AIV Evidence — Class A (Behavioral/Direct) & Class B/F

**Change ID:** `flashcore-f83-adopt-b438dbd`
**Adopted commit:** `b438dbd048fcd59781a1a5b23bcd6c0a93b3200f`
**Baseline SHA (b438dbd^):** `4f3ce12bdd49f2eb6b1fc66af7bc63bb2c843613`
**HEAD SHA:** `b05610c60c9a13e0707100ad5142e2079644d461`
**Generated:** 2026-06-26T00:00:00Z

---

## Nature of b438dbd

Commit `b438dbd` added two markdown documentation files only — no Python source code:

- `.github/aiv-claims/CLAIM_SCORE_FIELD_NOT_STRIPPED.md` (12 lines)
- `.github/aiv-evidence/EVIDENCE_.GITHUB_AIV_CLAIMS.md` (73 lines)

These files are not imported by any test or production module. There are no
directly exercisable behavioral tests for markdown claim documents. The Class A
evidence below therefore covers:
(a) The claim document's content against the established defect record, and
(b) The pre-existing vet_logic tests as regression guards at both baseline and HEAD.

---

## Baseline run — 4f3ce12 (b438dbd^)

Command (via `git worktree add /tmp/baseline-b438dbd 4f3ce12`; shared project venv):
```
pytest /tmp/baseline-b438dbd/tests/cli/test_vet_logic.py -v --tb=short
```

Result:
```
collected 10 items

tests/cli/test_vet_logic.py::test_vet_logic_no_yaml_files PASSED
tests/cli/test_vet_logic.py::test_vet_logic_clean_files_check_mode PASSED
tests/cli/test_vet_logic.py::test_vet_logic_clean_files_modify_mode PASSED
tests/cli/test_vet_logic.py::test_vet_logic_dirty_files_check_mode PASSED
tests/cli/test_vet_logic.py::test_vet_logic_dirty_files_modify_mode PASSED
tests/cli/test_vet_logic.py::test_vet_logic_ignores_invalid_yaml_structure PASSED
tests/cli/test_vet_logic.py::test_vet_logic_dirty_files_modify_mode PASSED
tests/cli/test_vet_logic.py::test_vet_card_with_invalid_uuid PASSED
tests/cli/test_vet_logic.py::test_vet_file_processing_exception PASSED
tests/cli/test_vet_logic.py::test_vet_source_dir_none PASSED
tests/cli/test_vet_logic.py::test_vet_non_validation_error PASSED

10 passed in 0.10s
```

Notes:
- `.github/aiv-claims/` did NOT exist at `4f3ce12` — confirmed by
  `ls /tmp/baseline-b438dbd/.github/aiv-claims/` → `No such file or directory`.
- `tests/test_vet_logic_score.py` had a pre-existing SyntaxError at `4f3ce12`; excluded.

---

## HEAD run — b05610c

Command:
```
pytest tests/cli/test_vet_logic.py tests/test_vet_logic_score.py tests/test_vet_logic_idempotent.py tests/test_vet_logic.py -v --tb=short
```

Result:
```
collected 13 items

tests/cli/test_vet_logic.py::test_vet_logic_no_yaml_files PASSED
tests/cli/test_vet_logic.py::test_vet_logic_clean_files_check_mode PASSED
tests/cli/test_vet_logic.py::test_vet_logic_clean_files_modify_mode PASSED
tests/cli/test_vet_logic.py::test_vet_logic_dirty_files_check_mode PASSED
tests/cli/test_vet_logic.py::test_vet_logic_dirty_files_modify_mode PASSED
tests/cli/test_vet_logic.py::test_vet_logic_ignores_invalid_yaml_structure PASSED
tests/cli/test_vet_logic.py::test_vet_card_with_invalid_uuid PASSED
tests/cli/test_vet_logic.py::test_vet_file_processing_exception PASSED
tests/cli/test_vet_logic.py::test_vet_source_dir_none PASSED
tests/cli/test_vet_logic.py::test_vet_non_validation_error PASSED
tests/test_vet_logic_score.py::test_score_field_removed_allows_card_creation PASSED
tests/test_vet_logic_idempotent.py::test_idempotent_normalization_keeps_uuid_and_no_error PASSED
tests/test_vet_logic.py::test_validate_and_normalize_card_removes_score_field PASSED

13 passed in 0.13s
```

Delta vs baseline: 0 regressions. The +3 tests reflect additions by later commits in the
chain (score removal test, idempotence test, normalize test). All 10 pre-existing
`tests/cli/test_vet_logic.py` tests PASS at HEAD.

---

## Claim content verification

CLAIM-001 in `CLAIM_SCORE_FIELD_NOT_STRIPPED.md` asserts:
> `_validate_and_normalize_card` **does not** have the `s` field removed

This claim describes the BUG as it existed at the time of the commit (early in the fix
chain, before the `pop("s", None)` fix was applied). The claim is corroborated by:

- The audit finding at `audit/02-static-audit.md#L93` (canonical intent URL).
- The primary fix commit `9c50e27` which added `mapped_card_dict.pop("s", None)` at
  `flashcore/cli/_vet_logic.py:67` — confirming the `s` field was NOT removed before.
- `tests/test_vet_logic_score.py::test_score_field_removed_allows_card_creation` passes
  GREEN at HEAD, confirming the fix is in place and the claim's described defect no
  longer exists in the codebase.

No fix-forward commit is required: `b438dbd` added documentation files that have no
behavioral impact; no tests were broken.
