import pytest
from flashcore.cli._vet_logic import _validate_and_normalize_card
from flashcore.models import Card

def test_B1_score_field_stripped():
    """B1: Ensure 's' (score) field is removed before Card validation.
    A raw card dict with 'q', 'a', and 's' should be processed without raising ValidationError
    and the returned dict must not contain the 's' key.
    """
    raw = {
        "q": "What is 2+2?",
        "a": "4",
        "s": 5,
    }
    result = _validate_and_normalize_card(raw, deck_name="TestDeck")
    assert "s" not in result, "Score field was not stripped"
    assert "front" in result and "back" in result and "uuid" in result
    Card(**result, deck_name="TestDeck")
