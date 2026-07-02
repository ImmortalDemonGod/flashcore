import pytest
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from flashcore.models import Card
from flashcore.review_manager import ReviewSessionManager
from flashcore.db.database import FlashcardDatabase
from flashcore.scheduler import FSRS_Scheduler


@pytest.fixture
def mock_db():
    db = MagicMock(spec=FlashcardDatabase)
    now = datetime.now(timezone.utc)
    # Three cards with due dates - all due today for simplicity
    today = now.date()
    card1 = Card(
        uuid=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        front="1",
        back="1",
        deck_name="Test Deck",
        next_due_date=today + timedelta(days=1),
        added_at=now,
        modified_at=now,
    )
    card2 = Card(
        uuid=uuid.UUID("22222222-2222-2222-2222-222222222222"),
        front="2",
        back="2",
        deck_name="Test Deck",
        next_due_date=today + timedelta(days=2),
        added_at=now,
        modified_at=now,
    )
    card3 = Card(
        uuid=uuid.UUID("33333333-3333-3333-3333-333333333333"),
        front="3",
        back="3",
        deck_name="Test Deck",
        next_due_date=today + timedelta(days=3),
        added_at=now,
        modified_at=now,
    )
    db.get_due_cards.return_value = [card1, card2, card3]
    return db


@pytest.fixture
def mock_scheduler():
    sched = MagicMock(spec=FSRS_Scheduler)
    return sched


def test_review_flow_maintains_due_date_order(mock_db, mock_scheduler):
    """Test that reviewing a card doesn't break due date ordering.

    After reviewing the first card, the next card should still be ordered
    by next_due_date, not by modified_at.
    """
    manager = ReviewSessionManager(
        db_manager=mock_db,
        scheduler=mock_scheduler,
        user_uuid=uuid.uuid4(),
        deck_name="Test Deck",
    )
    manager.initialize_session()
    # First card should be card1 (earliest due)
    first = manager.get_next_card()
    assert first.uuid == uuid.UUID("11111111-1111-1111-1111-111111111111")

    # Simulate reviewing it - card1 should be removed from queue
    manager._remove_card_from_queue(first.uuid)

    # Get next card, should be card2 (still earliest due), not card1 again
    second = manager.get_next_card()
    assert second.uuid == uuid.UUID(
        "22222222-2222-2222-2222-222222222222"
    ), f"Expected card2 next, got {second.uuid}"
