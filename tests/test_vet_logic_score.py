import pytest
from flashcore.cli._vet_logic import _validate_and_normalize_card
from flashcore.models import Card

def test_score_field_not_removed_raises_validation_error():
    """Bug 1: Score field (`s`) not removed during validation should raise ValidationError."""
    raw = {"front": "Q?", "back": "A!", "s": 5}
    # Expect ValidationError because extra fields are forbidden
    with pytest.raises(Exception):  # ValidationError subclass of Exception
        _validate_and_normalize_card(raw, deck_name="TestDeck")
"