# Bug Catalog for `_vet_logic.py`

## Overview
The module provides functions to validate and normalize flashcard YAML files. A known issue is that `_validate_and_normalize_card` does not remove the `s` (score) field from the input card dictionary before constructing a `Card` model. The `Card` model (in `flashcore/models.py`) forbids extra fields (`extra='forbid'`). Consequently, any YAML card containing a valid `s` field triggers a `ValidationError` during vetting, causing the card to be rejected even though the `s` field is allowed in the source YAML (defined in `flashcore/yaml_models.py`).

## Bugs

| ID | Bug Description | Blast Radius | Plausibility | Test Type |
|----|-----------------|--------------|--------------|-----------|
| B1 | `s` (score) field is not stripped before `Card` validation, causing a `ValidationError` for valid cards containing `s`. | Corrupts entire deck import; valid cards are rejected, user sees false errors and loses data. | The function maps aliases and handles UUID but never removes `s`; other code paths (parser) do. | Captured bug / contract pin (unit test). |

## Skipped Bugs

- None – all plausible bugs related to this finding are captured.

## Test Plan

- Write a unit test that supplies a raw card dictionary containing `q`, `a`, and `s` fields. The test expects `_validate_and_normalize_card` to return a dictionary **without** the `s` key and to succeed without raising `ValidationError`.
- The test description will name bug **B1**.

## Evaluation (to be filled after test run)
- Bugs caught: 
- Bugs characterized: 
- New bugs discovered: 
