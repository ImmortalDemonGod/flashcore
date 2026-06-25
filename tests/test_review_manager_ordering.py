import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from flashcore.models import Card
from flashcore.review_manager import ReviewSessionManager

@pytest.fixture
def mock_db():
    db = MagicMock()
    # create three cards with different next_due_date
    now = datetime.now(timezone.utc)
    card1 = Card(id=1, front='1', back='1', next_due_date=now + timedelta(days=1), added_at=now, modified_at=now)
    card2 = Card(id=2, front='2', back='2', next_due_date=now + timedelta(days=2), added_at=now, modified_at=now)
    card3 = Card(id=3, front='3', back='3', next_due_date=now + timedelta(days=3), added_at=now, modified_at=now)
    # DB returns them unsorted intentionally
    db.get_due_cards.return_value = [card3, card1, card2]
    return db

def test_initialize_session_respects_due_date_order(mock_db):
    manager = ReviewSessionManager(db=mock_db, scheduler=MagicMock())
    manager.initialize_session()
    # after init, review_queue should be ordered by next_due_date (card1, card2, card3)
    ordered_ids = [c.id for c in manager.review_queue]
    assert ordered_ids == [1, 2, 3], f"Queue order incorrect: {ordered_ids}"
