# Bug Catalog for _vet_logic.py

## Overview
The `_validate_and_normalize_card` function is responsible for mapping aliases, handling UUIDs, validating via the `Card` model, and preparing a dict for YAML output. It must **strip any fields not allowed by the `Card` model**, such as the legacy score field `s`.

## Bugs

### Bug 1: Score field `s` not stripped
- **Failure mode**: ValidationError is raised when a card dictionary contains the `s` field because the `Card` model has `extra='forbid'`. This prevents legitimate cards with a score from being vetted, causing false errors and dropping cards.
- **Blast radius**: Any YAML flashcard file that includes a score (`s`) fails vetting, leading to data loss and broken CLI usage for users importing existing decks with scores.
- **Why plausible**: The function maps `q`/`a` and handles UUIDs but never removes legacy fields. The parser module correctly pops `s` before validation, indicating this was an oversight.
- **Test type**: Captured bug / contract pin – a test that expects the function to *not* raise and to return a dict without `s` will fail now, exposing the bug.

## Skipped Bugs
- N/A — all identified plausible bugs are covered.
