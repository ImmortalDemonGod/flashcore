import pytest
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from flashcore.review_manager import ReviewManager
from flashcore.db.database import FlashcardDatabase
from flashcore.models import Card
from flashcore.scheduler import FSRS_Scheduler


@pytest.fixture
def db_with_three_due_cards():
    """Create an in-memory database with three cards having distinct due dates.

    All cards are due on the same date (today) but have different modified_at times
    to test that the queue ordering respects DB ordering by next_due_date, not modified_at.
    """
    db = FlashcardDatabase(db_path=":memory:")
    db.initialize_schema()
    now = datetime.now(timezone.utc)
    today = now.date()

    # Create three cards all due today, with different added_at times.
    # The DB orders by next_due_date ASC NULLS FIRST, added_at ASC → [card1, card2, card3].
    # modified_at is set in REVERSE order so that sorted(…, key=lambda c: c.modified_at)
    # would yield [card3, card2, card1] — the opposite of DB order.
    # This makes the test actually fail on the buggy implementation.
    card1 = Card(
        front="Card 1 - Added First",
        back="Back 1",
        deck_name="Test Deck",
        next_due_date=today,
        added_at=now - timedelta(hours=3),   # added first  → DB first
        modified_at=now - timedelta(minutes=1),  # most recent → bug puts LAST
    )
    card2 = Card(
        front="Card 2 - Added Second",
        back="Back 2",
        deck_name="Test Deck",
        next_due_date=today,
        added_at=now - timedelta(hours=2),   # added second → DB second
        modified_at=now - timedelta(hours=1),    # middle       → bug puts second
    )
    card3 = Card(
        front="Card 3 - Added Third",
        back="Back 3",
        deck_name="Test Deck",
        next_due_date=today,
        added_at=now - timedelta(hours=1),   # added third  → DB third
        modified_at=now - timedelta(hours=2),    # oldest       → bug puts FIRST
    )

    db.upsert_cards_batch([card1, card2, card3])
    return db


def test_review_manager_ordering_by_due_date(db_with_three_due_cards):
    """Test that ReviewManager orders cards by next_due_date (earliest first).

    This test verifies the fix for the bug where initialize_session()
    incorrectly sorted by modified_at instead of respecting DB ordering.

    The DB returns cards ordered by: next_due_date ASC NULLS FIRST, added_at ASC.
    The review queue should preserve this ordering.
    """
    db = db_with_three_due_cards
    scheduler = MagicMock(spec=FSRS_Scheduler)
    rm = ReviewManager(
        db_manager=db,
        scheduler=scheduler,
        user_uuid=uuid.uuid4(),
        deck_name="Test Deck",
    )
    rm.initialize_session()

    # All three cards should be in the queue
    assert (
        len(rm.review_queue) == 3
    ), f"Expected 3 cards, got {len(rm.review_queue)}"

    # The queue should be ordered by added_at (the secondary sort key in DB)
    # card1 was added first, then card2, then card3
    ordered_uuids = [c.uuid for c in rm.review_queue]

    # Verify the queue matches DB ordering
    db_cards = db.get_due_cards(
        "Test Deck", on_date=datetime.now(timezone.utc).date()
    )
    expected_uuids = [c.uuid for c in db_cards]

    assert ordered_uuids == expected_uuids, (
        f"Queue should match DB ordering. "
        f"Expected {expected_uuids}, got {ordered_uuids}"
    )
