# Class A Evidence — Behavioral Test Run
## Change: flashcore-f83-adopt-f0730af

### Baseline (f0730af^: 6c6705b63070ac50cd0bb864b0d47437d5dfe9eb)

Baseline produced by: `git worktree add /tmp/baseline-f0730af f0730af^` with shared venv
(`source /root/flashcore-flashcore-f83/.venv/bin/activate`).

**`tests/cli/test_vet_logic.py`** — 10 tests collected, 10 passed, 0 failed:

```
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

10 passed in 0.19s
```

Note on f0730af itself: at that commit, `flashcore/cli/_vet_logic.py` stores diff-format
text in "*** Begin Patch" / "*** End Patch" format — not valid Python. Any import raises
`SyntaxError`. Commit `1d176b1` (the immediate successor after `2887b02`) reinstated
parseable Python; the score-field strip reached the live implementation in `9c50e27`.

---

### HEAD (d42840e4903e1fa8c5350ba6b0d3df18ef50cd81)

Command: `pytest tests/cli/test_vet_logic.py tests/test_vet_logic_score.py -v --tb=short`

**11 tests collected, 11 passed, 0 failed:**

```
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

11 passed in 0.21s
```

---

### Delta

| Metric | Baseline (f0730af^) | HEAD |
|--------|---------------------|------|
| `tests/cli/test_vet_logic.py` collected | 10 | 10 |
| `tests/cli/test_vet_logic.py` passed | 10 | 10 |
| `tests/test_vet_logic_score.py` | not collected (file absent at baseline) | 1 passed |
| Regressions | — | 0 |

- 0 pre-existing tests regressed.
- `tests/test_vet_logic_score.py::test_score_field_removed_allows_card_creation` passes at
  HEAD, directly verifying that a card carrying an `s` field is accepted without ValidationError.
