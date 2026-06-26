from flashcore.cli._vet_logic import _validate_and_normalize_card

def test_score_field_not_stripped_causes_validation_error():
    """B1: _validate_and_normalize_card strips 's'; returned dict keeps YAML-format keys (q/a)."""
    card_data = {"q": "What?", "a": "Answer", "s": 2}
    deck_name = "test_deck"
    normalized = _validate_and_normalize_card(card_data, deck_name)
    assert "s" not in normalized, "Score field was not stripped"
    assert "q" in normalized and "a" in normalized and "uuid" in normalized
