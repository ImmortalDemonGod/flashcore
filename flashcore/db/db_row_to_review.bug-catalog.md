# Bug Catalog for db_row_to_review error handling

## Overview
`db_row_to_review` converts a DB row dict into a `Review` model. It currently does not catch `pydantic.ValidationError` and therefore leaks this exception instead of wrapping it in `MarshallingError`. This leads to unexpected error types propagating to callers.

## Bugs

| ID | Bug Description | Blast Radius | Plausibility | Test Type |
|----|-----------------|--------------|--------------|-----------|
| B1 | Missing `except ValidationError` wrapper causes `ValidationError` to escape as raw error instead of `MarshallingError`. | High – callers expect `MarshallingError`; unhandled `ValidationError` can crash API endpoints. | Pattern: other similar functions (`db_row_to_card`, `db_row_to_session`) correctly wrap the error, indicating an intended invariant. | Captured bug / contract pin (unit test) |

## Skipped Bugs

- None – all plausible error‑handling bugs are captured.

---
### Evidence Classes

#### Class A – Behavioral/direct
N/A — No runtime behavior executed in this catalog file.

#### Class B – Referential
Reference to code at `flashcore/db/db_utils.py:156-158` where the bug resides.

#### Class C – Negative
Search for missing `except ValidationError` pattern yielded no existing handling in this function.

#### Class D – Static analysis
Static analysis shows the function lacks a try/except block for `ValidationError` while similar functions include it.

#### Class E – Intent alignment
Intent URL: https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L150

#### Class F – Provenance
N/A — No prior test provenance for this newly added catalog.
