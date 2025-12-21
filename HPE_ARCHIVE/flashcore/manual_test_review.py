"""
Script for manually testing the CLI review flow.
"""

import os
import sys
from datetime import datetime, timezone, date
from typing import List, Optional, Dict
from uuid import UUID, uuid4

# Add the project root to the Python path for module resolution
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from cultivation.scripts.flashcore.card import Card, Review, CardState, Rating  # noqa: E402
from cultivation.scripts.flashcore.database import FlashcardDatabase  # noqa: E402
from cultivation.scripts.flashcore.exceptions import CardOperationError  # noqa: E402
from cultivation.scripts.flashcore.review_manager import ReviewSessionManager  # noqa: E402
from cultivation.scripts.flashcore.scheduler import FSRS_Scheduler  # noqa: E402
class MockDatabase(FlashcardDatabase):
    """An in-memory mock of the FlashcardDatabase for testing."""

    def __init__(self, cards: List[Card]):
        super().__init__(db_path=":memory:")
        self.cards = {c.uuid: c for c in cards}
        self.reviews: Dict[UUID, List[Review]] = {c.uuid: [] for c in cards}
        self._next_review_id = 1

    def get_due_cards(self, deck_name: str, on_date: date, limit: Optional[int] = 50) -> List[Card]:
        # For this test, all cards are new, so they are all due.
        # The mock can ignore deck_name for simplicity.
        limit = limit if limit is not None else 50
        return list(self.cards.values())[:limit]

    def get_card_by_uuid(self, card_uuid: UUID) -> Optional[Card]:
        return self.cards.get(card_uuid)

    def get_reviews_for_card(self, card_uuid: UUID, order_by_ts_desc: bool = True) -> List[Review]:
        reviews = self.reviews.get(card_uuid, [])
        # The mock doesn't need to implement sorting for this test, but it accepts the arg.
        return reviews

    def add_review_and_update_card(self, review: Review, new_card_state: CardState) -> Card:
        if self.read_only:
            raise CardOperationError("Mock is in read-only mode.")
        
        card_to_update = self.cards.get(review.card_uuid)
        if not card_to_update:
            raise CardOperationError(f"Card with UUID {review.card_uuid} not found.")

        # Simulate review ID generation and add review to history
        new_review_id = self._next_review_id
        self._next_review_id += 1
        self.reviews.setdefault(review.card_uuid, []).append(review)
        
        # Update card state using model_copy for immutability
        updated_card = card_to_update.model_copy(update={
            'last_review_id': new_review_id,
            'next_due_date': review.next_due,
            'modified_at': review.ts,
            'stability': review.stab_after,
            'difficulty': review.diff,
            'state': new_card_state
        })

        self.cards[updated_card.uuid] = updated_card
        print(f"  - MockDB: Added review for card {updated_card.uuid}, new state: {updated_card.state}")
        return updated_card

    def get_all_cards(self, deck_name_filter: Optional[str] = None) -> List[Card]:
        # Mock implementation can ignore the filter.
        return list(self.cards.values())


def main():
    """Sets up and runs an automated review session."""
    # 1. Create a sample deck with a few cards
    cards = [
        Card(
            uuid=uuid4(),
            deck_name="Geography",
            front="What is the capital of Japan?",
            back="Tokyo",
            tags={"capitals", "asia"},
            added_at=datetime.now(timezone.utc),
            modified_at=datetime.now(timezone.utc),
        ),
        Card(
            uuid=uuid4(),
            deck_name="Geography",
            front="What is the highest mountain in the world?",
            back="Mount Everest",
            tags={"mountains", "geography-facts"},
            added_at=datetime.now(timezone.utc),
            modified_at=datetime.now(timezone.utc),
        ),
        Card(
            uuid=uuid4(),
            deck_name="Geography",
            front="Which river is the longest in Africa?",
            back="The Nile",
            tags={"rivers", "africa"},
            added_at=datetime.now(timezone.utc),
            modified_at=datetime.now(timezone.utc),
        ),
    ]

    # 2. Initialize the mock database, scheduler, and manager
    mock_db = MockDatabase(cards=cards)
    scheduler = FSRS_Scheduler()
    manager = ReviewSessionManager(
        db_manager=mock_db,
        scheduler=scheduler,
        user_uuid=UUID("DEADBEEF-DEAD-BEEF-DEAD-BEEFDEADBEEF"),
        deck_name="mock_deck",
    )

    # 3. Start the automated review flow
    print("--- Starting Automated Review Test ---")
    manager.initialize_session()

    reviewed_cards_count = 0
    initial_card_count = len(manager.review_queue)
    
    while card := manager.get_next_card():
        print(f"Reviewing card: '{card.front}'")
        # We need to get the card from the DB to see the updated state
        card_before_review = mock_db.get_card_by_uuid(card.uuid)
        
        manager.submit_review(card.uuid, Rating.Good)
        reviewed_cards_count += 1
        
        card_after_review = mock_db.get_card_by_uuid(card.uuid)
        print(
            f"  -> Submitted 'Good' rating. "
            f"State: {card_before_review.state.value} -> {card_after_review.state.value}, "
            f"Next due: {card_after_review.next_due_date}"
        )

    print("\n--- Review Session Complete ---")
    print(f"Total cards reviewed: {reviewed_cards_count}")

    # 4. Verification
    assert reviewed_cards_count == initial_card_count, "Not all cards were reviewed"
    print("✅ Verification: All cards in the session were reviewed.")

    all_cards_after_review = mock_db.get_all_cards()
    for card in all_cards_after_review:
        assert card.state == CardState.Learning, f"Card '{card.front}' should be in LEARNING state, but is {card.state}"
        assert card.next_due_date >= datetime.now(timezone.utc).date(), f"Card '{card.front}' next due date is not in the future"
    
    print("✅ Verification: All cards are in the correct final state.")
    print("\n--- Automated test successful ---")


if __name__ == "__main__":
    main()
