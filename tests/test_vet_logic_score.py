import pytest
from flashcore.cli._vet_logic import _validate_and_normalize_card
from flashcore.models import Card

def test_score_field_removed_allows_card_creation():
    """Bug 1: Score field (`s`) should be removed during validation to avoid ValidationError."""
    raw = {"q": "Q?", "a": "A!", "s": 5}
    # Should NOT raise ValidationError because 's' is removed
    result = _validate_and_normalize_card(raw, deck_name="TestDeck")
    assert "s" not in result, "Score field should be removed"
    # The function returns the original keys (q/a) with the new UUID
    assert "uuid" in result
    assert "q" in result
    assert "a" in result
