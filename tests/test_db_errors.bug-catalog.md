# Bug Catalog for db_row_to_review error handling

## Overview
The function `db_row_to_review` in `flashcore/db/db_utils.py` constructs a `Review` model from a dictionary without catching `pydantic.ValidationError`. Other similar conversion functions wrap validation errors in `MarshallingError`. This omission causes uncaught `ValidationError` to propagate as raw errors, breaking callers expecting `MarshallingError`.

## Bugs

| ID | Bug description | Blast radius | Why plausible | Test type |
|----|-----------------|--------------|---------------|-----------|
| B1 | Missing `MarshallingError` wrapper for `ValidationError` in `db_row_to_review` leads to uncaught exception when required fields are missing. | High – callers raise `ReviewOperationError` only on `MarshallingError`; raw `ValidationError` crashes the service. | Pattern exists in `db_row_to_card` and `db_row_to_session`; omission is likely a copy‑paste error. | Captured bug / contract pin (unit test exercising error path). |

## Skipped

- **B2**: Validation of extra/unknown fields – `Review` model already discards unknown fields; no functional impact.
- **B3**: Performance overhead of try/except – negligible for error paths.

## Self‑critique
- The test for B1 will fail when the bug is present (current code) and pass after fixing (which we will not do here). It asserts on the raised exception type and its message, satisfying the four test criteria.
