import pytest
from flashcore.cli._vet_logic import _validate_and_normalize_card
from flashcore.models import Card

def test_validate_and_normalize_card_removes_score_field():
    """B1: `_validate_and_normalize_card` should drop the `s` field to avoid ValidationError."""
    raw_card = {
        "q": "What is 2+2?",
        "a": "4",
        "s": 5,
    }
    result = _validate_and_normalize_card(raw_card, deck_name="Test Deck")
    assert "s" not in result, "Score field should be removed"
    # The function returns the original keys (q/a) with the new UUID
    assert "uuid" in result
    assert "q" in result
    assert "a" in result
    # Note: The function transforms q->front and a->back internally for Card validation,
    # but returns the original keys for YAML output.
