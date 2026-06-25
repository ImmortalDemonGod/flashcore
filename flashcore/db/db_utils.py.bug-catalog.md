## Bug Catalog Entry

- **File:** `flashcore/db/db_utils.py`
- **Location:** Lines 152-158 (function `db_row_to_review`)
- **Issue:** Missing handling of `pydantic.ValidationError`, causing uncaught exception instead of `MarshallingError`.
- **Fix:** Added try/except block to catch `ValidationError` and raise `MarshallingError` with column information.
- **Verification:** Added unit test `tests/test_db_errors.py` asserting `MarshallingError` is raised with missing `rating` column.
- **References:** Audit entry [L150](https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L150).
