# AIV Evidence — Class A (Behavioral/Direct) & Class B/F

**Change ID:** `flashcore-f83-adopt-6828dc7`
**Adopted commit:** `6828dc70bbc135d65e4daacb44c64d562ce36165`
**Baseline SHA (6828dc7^):** `151570d1085386c54ac9d3810417d7060764cb1f`
**HEAD SHA:** `22d8b6c42a7c46aff3d68bc44d59833023d03caf`
**Generated:** 2026-06-26T00:00:00Z

---

## Baseline run — 151570d (6828dc7^)

Command:
```
pytest tests/cli/test_vet_logic.py -v --tb=short
```
(via `git worktree add /tmp/baseline-6828dc7b 151570d`; shared project venv)

Result:
```
collected 10 items

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

10 passed in 0.11s
```

Notes:
- `tests/test_vet_logic_idempotent.py` did not exist at 151570d — not collected.
- `tests/test_vet_logic_score.py` had a pre-existing SyntaxError at this commit and was excluded.

---

## HEAD run — 22d8b6c

Command:
```
pytest tests/test_vet_logic_idempotent.py tests/cli/test_vet_logic.py tests/test_vet_logic_score.py -v --tb=short
```

Result:
```
collected 12 items

tests/test_vet_logic_idempotent.py::test_idempotent_normalization_keeps_uuid_and_no_error PASSED
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

12 passed in 0.12s
```

---

## Delta

| Metric | Baseline (151570d) | HEAD (22d8b6c) |
|--------|--------------------|-----------------|
| Collected | 10 | 12 |
| Passed | 10 | 12 |
| Failed | 0 | 0 |
| Regressions from 6828dc7 | — | **0** |

The +2 tests are `test_idempotent_normalization_keeps_uuid_and_no_error` (added by 6828dc7) and
`test_score_field_removed_allows_card_creation` (SyntaxError resolved by a later commit in the chain,
not by 6828dc7 itself). All 10 pre-existing `tests/cli/test_vet_logic.py` tests pass at HEAD.

---

## Class F — Provenance

- Commit `6828dc70bbc135d65e4daacb44c64d562ce36165` authored by
  `openrouter-driver (fix-pipeline) <noreply@openrouter.ai>`;
  message: `Add idempotence test for _validate_and_normalize_card`.
- Parent: `151570d1085386c54ac9d3810417d7060764cb1f` (`Add test for missing score field removal bug`).
- Child chain to HEAD: `6828dc7` → … → `22d8b6c` (33 commits, continuous, no gaps confirmed
  by `git log --oneline 6828dc7..HEAD`).
- `tests/test_vet_logic_idempotent.py` first appears in `6828dc7`; unmodified by any subsequent
  commit through HEAD (`git log --oneline 6828dc7..HEAD -- tests/test_vet_logic_idempotent.py`
  returns empty — the file has not been touched since it was added).
