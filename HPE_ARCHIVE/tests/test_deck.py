import pytest
from pydantic import ValidationError

from cultivation.scripts.flashcore.deck import Deck


def test_deck_creation_with_name():
    """Tests that a Deck can be created with just a name."""
    deck = Deck(name="Test Deck")
    assert deck.name == "Test Deck"
    assert deck.cards == []


def test_deck_creation_with_cards(new_card_factory):
    """Tests that a Deck can be created with a list of cards."""
    card1 = new_card_factory(deck_name="Test Deck", front="Q1", back="A1")
    card2 = new_card_factory(deck_name="Test Deck", front="Q2", back="A2")
    cards = [card1, card2]

    deck = Deck(name="Test Deck", cards=cards)
    assert deck.name == "Test Deck"
    assert len(deck.cards) == 2
    assert deck.cards[0].front == "Q1"
    assert deck.cards[1].front == "Q2"


def test_deck_creation_with_empty_cards_list():
    """Tests that a Deck can be created with an empty list of cards."""
    deck = Deck(name="Test Deck", cards=[])
    assert deck.name == "Test Deck"
    assert deck.cards == []


def test_deck_creation_missing_name():
    """Tests that creating a Deck without a name raises a ValidationError."""
    with pytest.raises(ValidationError) as excinfo:
        Deck()
    # Check that the error is about the 'name' field being required
    assert "name\n  Field required" in str(excinfo.value)
    assert "Field required" in str(excinfo.value)
