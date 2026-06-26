# Class A Evidence — adopt-cb5c6c3 Test Run

**Change:** cb5c6c3 ("Add bug catalog for vet_logic score field bug")
**Baseline (cb5c6c3^):** `0b8d853b7215d1b9a72febf371c8ab22559058ff`
**Head:** `27b61566d09f2c660a60008812683e8a5dbfb303`
**Captured:** 2026-06-26

## What cb5c6c3 changed

Files modified (both documentation only, no Python):
- `flashcore/cli/_vet_logic.bug-catalog.md` — reformatted Bug 1 entry into a table (Bug B1), updated Summary header, added Test Plan section
- `.github/aiv-evidence/EVIDENCE_FLASHCORE_CLI__VET_LOGIC.BUG_CATALOG.MD.md` — corresponding evidence wrapper updated

No production Python, no test files modified by cb5c6c3.

## Test results at branch HEAD

Command: `pytest flashcore/cli/tests/ -v --tb=short`

```
============================= test session starts ==============================
platform linux -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
collected 3 items

flashcore/cli/tests/test_vet_logic_missing_score_field.py::test_validate_and_normalize_card_preserves_score_field_without_error FAILED
flashcore/cli/tests/test_vet_logic_score_bug.py::test_score_field_not_stripped_causes_validation_error FAILED
flashcore/cli/tests/test_vet_logic_score_bug_red.py::test_score_field_not_stripped_causes_validation_error PASSED

2 failed, 1 passed in 0.26s
```

### Pre-existing failures (NOT caused by cb5c6c3)

| Test file | Failure reason | Introduced by |
|-----------|---------------|---------------|
| `test_vet_logic_score_bug.py` | Wrong key assertions (`front`/`back` expected; `q`/`a` returned) | `b6ed2eb` (impl-stage pipeline) |
| `test_vet_logic_missing_score_field.py` | Wrong key assertion (`front` expected; `q`/`a` returned) | `479f91c` (impl-stage pipeline) |

Both failures existed at `cb5c6c3^` and exist identically at branch HEAD. `cb5c6c3` touched only documentation; it introduced zero new test failures.

### Primary correctness test — PASSES

```
flashcore/cli/tests/test_vet_logic_score_bug_red.py::test_score_field_not_stripped_causes_validation_error PASSED
1 passed in 0.24s
```

## Live runtime probe

```python
from flashcore.cli._vet_logic import _validate_and_normalize_card
result = _validate_and_normalize_card({'q': 'What?', 'a': 'Answer', 's': 2}, 'test_deck')
# result: {'a': 'Answer', 'q': 'What?', 'uuid': '<generated>'}
# 's' absent from result — implementation fix at 9c50e27 is operative
```

`s` field is correctly absent. `Card(**result, deck_name='test_deck')` succeeds (no ValidationError).
