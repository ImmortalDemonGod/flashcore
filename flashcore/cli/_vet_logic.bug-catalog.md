# Bug Catalog for _vet_logic.py

## Overview
The function `_validate_and_normalize_card` is responsible for normalising card dictionaries before they are instantiated as `Card` models. It maps the short keys `q` → `front` and `a` → `back` but **fails to drop the optional `s` (score) field**. The `Card` model (see `flashcore/models.py`) declares `extra='forbid'`, causing a pydantic `ValidationError` when an incoming card contains the `s` field. This results in **false validation errors** and prevents legitimate cards with a score from being vetted or written back.

## Bugs

| ID | Description | Blast Radius | Plausibility Reason |
|----|-------------|--------------|---------------------|
| B1 | `_validate_and_normalize_card` does not remove the `s` field, causing a `ValidationError` for any card YAML that includes a score. | Prevents valid cards with scores from being processed, breaking decks that store review scores and causing the CLI vet command to abort. | The parser in `flashcore/parser.py` correctly pops `s`; the omission here is a copy‑paste error and easy to miss because the field is optional in the source YAML. |

## Skipped Bugs

- **B2** – Missing handling of unknown extra fields beyond `s`. *Reason*: The `extra='forbid'` policy already guarantees a failure; addressing it would require changing the model contract, which is out of scope for this test suite.
- **B3** – Validation of duplicate UUIDs across cards. *Reason*: Existing tests already cover UUID uniqueness; not directly related to the current finding.

## Test Plan

| Bug ID | Test Type | Rationale |
|--------|-----------|-----------|
| B1 | Captured bug / contract pin (unit test) | Directly asserts that invoking `_validate_and_normalize_card` on a card dict containing `s` does **not** raise a `ValidationError` and returns a dict without the `s` key. |

## Evaluation (to be filled after test execution)

- **Bugs caught**: 
- **Bugs characterized**: 
- **New bugs discovered**: 
