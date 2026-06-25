# Bug Catalog for db_row_to_review error handling

## Overview
`db_row_to_review` converts a DB row dict into a `Review` model. It currently does not catch `pydantic.ValidationError` and therefore leaks this exception instead of wrapping it in `MarshallingError`. This leads to unexpected error types propagating to callers.

## Bugs

| ID | Bug Description | Blast Radius | Plausibility | Test Type |
|----|-----------------|--------------|--------------|-----------|
| B1 | Missing `except ValidationError` wrapper causes `ValidationError` to escape as raw error instead of `MarshallingError`. | High – callers expect `MarshallingError`; unhandled `ValidationError` can crash API endpoints. | Pattern: other similar functions (`db_row_to_card`, `db_row_to_session`) correctly wrap the error, indicating an intended invariant. | Captured bug / contract pin (unit test) |

## Skipped Bugs

- None – all plausible error‑handling bugs are captured.
