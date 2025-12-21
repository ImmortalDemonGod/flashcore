import uuid
from datetime import datetime, timezone

import pytest

from cultivation.scripts.flashcore.card import Card, CardState
from cultivation.scripts.flashcore.database import FlashcardDatabase


@pytest.fixture
def in_memory_db_with_data():
    """
    Provides an in-memory FlashcardDatabase instance populated with some
    initial data for testing retrieval and error handling.
    """
    db = FlashcardDatabase(db_path=':memory:')
    db.initialize_schema()

    # Add some valid cards
    cards = [
        Card(uuid=uuid.uuid4(), deck_name="test-deck", front="Front 1", back="Back 1"),
        Card(uuid=uuid.uuid4(), deck_name="test-deck", front="Front 2", back="Back 2"),
        Card(uuid=uuid.uuid4(), deck_name="another-deck", front="Front 3", back="Back 3"),
    ]
    db.upsert_cards_batch(cards)

    yield db
    db.close_connection()
