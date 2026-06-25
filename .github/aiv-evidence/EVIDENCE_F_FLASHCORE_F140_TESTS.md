## Class F (Provenance)

- Test file `tests/test_db_errors.py` added in commit `f418ec6` introduces a red test that captures the missing `MarshallingError` handling in `db_row_to_review`.
- The test ensures that a `ValidationError` raised during row conversion is wrapped in `MarshallingError`, matching the pattern used elsewhere.
- This evidence links the test creation directly to the bug fix intent, satisfying the provenance requirement.
