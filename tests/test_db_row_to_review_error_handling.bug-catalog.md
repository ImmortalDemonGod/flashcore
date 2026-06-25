# Bug Catalog for db_row_to_review error handling

## Bug 1: Missing ValidationError wrapper in db_row_to_review
- **Description**: `db_row_to_review` does not catch `pydantic.ValidationError` and wrap it in `MarshallingError`, causing unexpected exception propagation.
- **Blast radius**: Review fetching fails with uncaught ValidationError, breaking API callers and leading to 500 errors.
- **Plausibility**: Inconsistent error handling pattern compared to `db_row_to_card` and `db_row_to_session` which correctly wrap the error.
- **Test type**: Captured bug / contract pin (unit test that triggers ValidationError and expects MarshallingError).

## Skipped
- N/A

---

### Class E
Intent alignment evidence: https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L150