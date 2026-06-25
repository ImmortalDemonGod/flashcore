# Bug Catalog for `_vet_logic.py`

## Overview
The module `_vet_logic.py` contains the function `_validate_and_normalize_card` which maps the keys `q` → `front` and `a` → `back` for a flashcard. The function is supposed to drop the temporary `s` (score) field before constructing a `Card` model. However, it currently **does not** remove the `s` field, leading to a `ValidationError` because the `Card` model defines `extra='forbid'`.

## Bugs

| ID | Bug | Blast radius | Why plausible |
|----|-----|---------------|---------------|
| B1 | `_validate_and_normalize_card` leaves the `s` (score) field in the dict passed to `Card`, causing a `ValidationError` for any card that includes a score. | Prevents legitimate cards with a score from being vetted; they are silently dropped and never written back, breaking data pipelines. | The function mirrors `parser.py` which correctly does `card_data.pop("s", None)`. The omission is a typical copy‑paste error when handling temporary fields.
| B2 | Re‑vetting a valid card file twice results in a different UUID because the faulty handling of the `s` field triggers a re‑creation of the card object. | Idempotency is broken; scripts that run vet repeatedly will produce churn and may cause downstream sync issues. | The validation error forces the card to be re‑generated without the original UUID, changing its identity.

## Skipped Bugs

- None – all identified plausible bugs are covered by tests.

## Test Plan

| Test ID | Bug ID | Test type | Description |
|---------|--------|-----------|-------------|
| T1 | B1 | Unit (captured bug) | Verify that vetting a YAML card containing an `s` field raises a `ValidationError` (the bug is present). |
| T2 | B2 | Integration (idempotence) | Run `flashcore vet --source-dir <dir>` twice on a directory containing a valid card with an `s` field and assert that the second run reports no UUID changes. |

## Self‑critique
- Each test directly targets a cataloged bug.
- Tests assert on observable behaviour (exception raised, UUID stability) rather than internal implementation.
- Tests use the public CLI interface for the idempotence check and the internal function for the validation error, matching the public contract of `_validate_and_normalize_card`.
