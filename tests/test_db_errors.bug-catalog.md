# Bug Catalog for db_row_to_review error handling

## Overview
The function `db_row_to_review` in `flashcore/db/db_utils.py` constructs a `Review` model from a dict without catching `pydantic.ValidationError`. Callers expect a `MarshallingError` on malformed rows, but a raw `ValidationError` propagates, causing unexpected crashes.

## Bugs considered

| ID | Bug description | Blast radius | Plausibility | Test type(s) |
|----|-----------------|--------------|--------------|--------------|
| B1 | Missing `MarshallingError` wrapper for `ValidationError` in `db_row_to_review` leads to uncaught exception when a database row is missing required fields (e.g., `rating`). | High – crashes API endpoint, propagates to user‑facing error. | Pattern: other converters (`db_row_to_card`, `db_row_to_session`) correctly wrap; omission is likely accidental. | Captured bug / contract pin (unit test asserting raised `MarshallingError`). |

## Skipped bugs

- None: all plausible error‑handling bugs are covered as they directly affect stability.

## Test design
- **Test B1**: Call `db_row_to_review` with a row missing the `rating` column and assert that a `MarshallingError` is raised with a message mentioning `rating`.

## Evaluation (to be filled after test execution)
- Bugs caught:
- Bugs characterized:
- Bugs discovered during writing:
