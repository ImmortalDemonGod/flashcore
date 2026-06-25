import pytest
from flashcore.cli._vet_logic import _validate_and_normalize_card

def test_score_field_removed_bug_catch():
    """Bug 1: _validate_and_normalize_card should drop the 's' (score) field.
    The current implementation retains it, causing ValidationError downstream.
    This test expects the normalized dict to NOT contain 's'.
    """
    raw_card = {"q": "What is 2+2?", "a": "4", "s": 5}
    normalized = _validate_and_normalize_card(raw_card, deck_name="test_deck")
    assert "s" not in normalized, "The 's' field should be removed during validation"
