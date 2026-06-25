import pytest
from datetime import datetime, timedelta, timezone
from flashcore.review_manager import ReviewManager
from flashcore.database import InMemoryDB

@pytest.fixture
def db_with_three_due_cards():
    db = InMemoryDB()
    now = datetime.now(timezone.utc)
    # create three cards with different next_due_date values
    card1 = db.create_card(due_date=now + timedelta(days=1))  # due later
    card2 = db.create_card(due_date=now + timedelta(hours=1))  # due sooner
    card3 = db.create_card(due_date=now + timedelta(days=2))  # due latest
    return db

def test_review_manager_ordering_by_due_date(db_with_three_due_cards):
    """Bug B1: ReviewManager incorrectly sorts by modified_at instead of next_due_date.
    The test expects the first queue element to be the earliest due card.
    """
    rm = ReviewManager(db=db_with_three_due_cards)
    rm.initialize_session()
    # The queue should be ordered by next_due_date ascending
    first_card = rm.review_queue[0]
    # find the card with the earliest due date from DB
    earliest = min(db_with_three_due_cards.cards, key=lambda c: c.next_due_date)
    assert first_card.id == earliest.id, "Queue not ordered by next due date"
