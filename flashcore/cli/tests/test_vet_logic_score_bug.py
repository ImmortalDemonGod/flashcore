import pytest
from flashcore.cli._vet_logic import _validate_and_normalize_card
from flashcore.models import Card
from pydantic import ValidationError

def test_score_field_not_stripped_causes_validation_error():
    """Bug B1: _validate_and_normalize_card now removes 's' score field, allowing Card creation."""
    card_data = {"q": "What?", "a": "Answer", "s": 2}
    deck_name = "test_deck"
    normalized = _validate_and_normalize_card(card_data, deck_name)
    # The fixed implementation returns dict without 's'
    assert "s" not in normalized
    # Card creation should succeed
    card = Card(**normalized, deck_name=deck_name)
    assert card.front == "What?"
    assert card.back == "Answer"
