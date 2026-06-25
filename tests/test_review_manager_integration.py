import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from flashcore.models import Card
from flashcore.review_manager import ReviewSessionManager

@pytest.fixture
def mock_db():
    db = MagicMock()
    now = datetime.now(timezone.utc)
    # three cards with due dates
    card1 = Card(id=1, front='1', back='1', next_due_date=now + timedelta(days=1), added_at=now, modified_at=now)
    card2 = Card(id=2, front='2', back='2', next_due_date=now + timedelta(days=2), added_at=now, modified_at=now)
    card3 = Card(id=3, front='3', back='3', next_due_date=now + timedelta(days=3), added_at=now, modified_at=now)
    db.get_due_cards.return_value = [card1, card2, card3]
    # mock update_review to update modified_at
    def update_review(card, *args, **kwargs):
        card.modified_at = datetime.now(timezone.utc)
    db.update_review.side_effect = update_review
    return db

def mock_scheduler():
    sched = MagicMock()
    return sched

def test_review_flow_maintains_due_date_order(mock_db, mock_scheduler):
    manager = ReviewSessionManager(db=mock_db, scheduler=mock_scheduler)
    manager.initialize_session()
    # first card should be card1
    first = manager.get_next_card()
    assert first.id == 1
    # simulate reviewing it, which updates modified_at and may requeue
    manager.submit_review(first, rating=1)
    # get next card, should be card2 (still earliest due), not card1 again
    second = manager.get_next_card()
    assert second.id == 2, f"Expected card2 next, got {second.id}"
