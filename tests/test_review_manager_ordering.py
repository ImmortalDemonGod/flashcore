import pytest
import uuid
from datetime import date, datetime, timedelta, timezone
from unittest.mock import MagicMock
from flashcore.models import Card, CardState
from flashcore.review_manager import ReviewSessionManager
from flashcore.db.database import FlashcardDatabase
from flashcore.scheduler import FSRS_Scheduler


@pytest.fixture
def mock_db():
    db = MagicMock(spec=FlashcardDatabase)
    # Create three cards with different next_due_date
    # DB returns them ALREADY ORDERED by next_due_date ASC NULLS FIRST, added_at ASC
    now = datetime.now(timezone.utc)
    card1 = Card(
        uuid=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        front="Card 1",
        back="Back 1",
        deck_name="Test Deck",
        next_due_date=now.date() + timedelta(days=1),  # earliest due
        added_at=now,
        modified_at=now,
    )
    card2 = Card(
        uuid=uuid.UUID("22222222-2222-2222-2222-222222222222"),
        front="Card 2",
        back="Back 2",
        deck_name="Test Deck",
        next_due_date=now.date() + timedelta(days=2),  # middle due
        added_at=now,
        modified_at=now,
    )
    card3 = Card(
        uuid=uuid.UUID("33333333-3333-3333-3333-333333333333"),
        front="Card 3",
        back="Back 3",
        deck_name="Test Deck",
        next_due_date=now.date() + timedelta(days=3),  # latest due
        added_at=now,
        modified_at=now,
    )
    # DB returns them in the correct order (as the real DB would)
    db.get_due_cards.return_value = [card1, card2, card3]
    return db


def test_initialize_session_respects_due_date_order(mock_db):
    """Test that initialize_session preserves DB ordering by next_due_date.

    The DB returns cards ordered by next_due_date ASC NULLS FIRST, added_at ASC.
    The review queue should respect this ordering, not re-sort by modified_at.
    """
    scheduler = MagicMock(spec=FSRS_Scheduler)
    manager = ReviewSessionManager(
        db_manager=mock_db,
        scheduler=scheduler,
        user_uuid=uuid.uuid4(),
        deck_name="Test Deck",
    )
    manager.initialize_session()
    # After init, review_queue should preserve DB ordering (card1, card2, card3)
    ordered_uuids = [c.uuid for c in manager.review_queue]
    expected_uuids = [
        uuid.UUID("11111111-1111-1111-1111-111111111111"),
        uuid.UUID("22222222-2222-2222-2222-222222222222"),
        uuid.UUID("33333333-3333-3333-3333-333333333333"),
    ]
    assert (
        ordered_uuids == expected_uuids
    ), f"Queue order incorrect: {ordered_uuids}"
