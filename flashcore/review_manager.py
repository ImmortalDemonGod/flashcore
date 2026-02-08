"""
This module defines the ReviewSessionManager class, which is responsible for
managing a flashcard review session. It interacts with the database to fetch
cards, uses a scheduler to determine review timings, and records review outcomes.
"""

import logging
from datetime import datetime, timezone, date
from typing import Dict, List, Optional, Set, Any
from uuid import UUID, uuid4

from .models import Card
from .db.database import FlashcardDatabase
from .scheduler import FSRS_Scheduler as FSRS
from .review_processor import ReviewProcessor
from .session_manager import SessionManager

# Initialize logger
logger = logging.getLogger(__name__)


class ReviewSessionManager:
    """
    Manages a review session for flashcards.

    This class is responsible for:
    - Initializing a review session with a specific set of cards.
    - Providing cards one by one for review.
    - Processing user reviews and updating card states.
    - Interacting with the database to persist changes.
    """

    def __init__(
        self,
        db_manager: FlashcardDatabase,
        scheduler: FSRS,
        user_uuid: UUID,
        deck_name: str,
    ):
        """
        Initializes the ReviewSessionManager.

        Args:
            db_manager: An instance of DatabaseManager to interact with the database.
            scheduler: An instance of a scheduling algorithm (e.g., FSRS).
            user_uuid: The UUID of the user conducting the review.
            deck_name: The name of the deck being reviewed.
        """
        self.db = db_manager
        self.scheduler = scheduler
        self.user_uuid = user_uuid
        self.deck_name = deck_name
        self.session_uuid = uuid4()
        self.review_queue: list[Card] = []
        self.current_session_card_uuids: Set[UUID] = set()
        self.session_start_time = datetime.now(timezone.utc)

        # Initialize the shared review processor
        self.review_processor = ReviewProcessor(db_manager, scheduler)

        # Initialize session manager for analytics
        self.session_manager = SessionManager(
            db_manager, user_id=str(user_uuid)
        )
        self._session_started = False

    def initialize_session(
        self, limit: int = 20, tags: Optional[List[str]] = None
    ) -> None:
        """
        Initializes the review session by fetching due cards from the database.

        Args:
            limit: The maximum number of cards to fetch for the session.
            tags: Optional list of tags to filter cards by.
        """
        logger.info(
            f"Initializing review session {self.session_uuid} for user {self.user_uuid} and deck '{self.deck_name}'"
        )
        if tags:
            logger.info(f"Filtering cards by tags: {tags}")

        # Start session analytics tracking
        if not self._session_started:
            try:
                self.session_manager.start_session(
                    device_type="desktop",  # Could be detected
                    platform="cli",
                    session_uuid=self.session_uuid,
                )
                self._session_started = True
                logger.debug(
                    f"Started session analytics for {self.session_uuid}"
                )
            except Exception as e:
                logger.warning(f"Failed to start session analytics: {e}")

        today = date.today()  # Use local date for user-friendly scheduling
        due_cards = self.db.get_due_cards(
            self.deck_name, on_date=today, limit=limit, tags=tags
        )
        self.review_queue = sorted(due_cards, key=lambda c: c.modified_at)
        self.current_session_card_uuids = {
            card.uuid for card in self.review_queue
        }
        logger.info(
            f"Initialized session with {len(self.review_queue)} cards."
        )

    def get_next_card(self) -> Optional[Card]:
        """
        Retrieves the next card to be reviewed.

        Returns:
            The next Card object to be reviewed, or None if the queue is empty.
        """
        if not self.review_queue:
            logger.info("Review queue is empty. Session may be complete.")
            return None
        return self.review_queue[0]

    def _get_card_from_queue(self, card_uuid: UUID) -> Optional[Card]:
        """
        Finds a card in the current review queue by its UUID.

        Args:
            card_uuid: The UUID of the card to find.

        Returns:
            The Card object if found, otherwise None.
        """
        for card in self.review_queue:
            if card.uuid == card_uuid:
                return card
        return None

    def _remove_card_from_queue(self, card_uuid: UUID) -> None:
        """
        Removes a card from the review queue.

        Args:
            card_uuid: The UUID of the card to remove.
        """
        self.review_queue = [
            card for card in self.review_queue if card.uuid != card_uuid
        ]

    def submit_review(
        self,
        card_uuid: UUID,
        rating: int,
        reviewed_at: Optional[datetime] = None,
        resp_ms: int = 0,
        eval_ms: int = 0,
    ) -> Card:
        """
        Submits a review for a card, updates its state, and schedules the next review.

        Args:
            card_uuid: The UUID of the card being reviewed.
            rating: The user's rating of the card (e.g., Again, Hard, Good, Easy).
            reviewed_at: The timestamp of the review. Defaults to now.
            resp_ms: The response time in milliseconds (time to reveal answer).
            eval_ms: The evaluation time in milliseconds (time to provide rating).

        Returns:
            The updated Card object.

        Raises:
            ValueError: If the card is not in the current session.
            CardOperationError: If there's an issue with the database update.
        """
        # Validate that the card is in the current session
        card = self._get_card_from_queue(card_uuid)
        if not card:
            raise ValueError(
                f"Card {card_uuid} not found in the current review session."
            )

        try:
            # Use the shared review processor for consistent logic
            updated_card = self.review_processor.process_review(
                card=card,
                rating=rating,
                resp_ms=resp_ms,
                eval_ms=eval_ms,
                reviewed_at=reviewed_at,
                session_uuid=self.session_uuid,  # Link review to this session
            )

            # Record analytics if session tracking is active
            if self._session_started:
                try:
                    self.session_manager.record_card_review(
                        card=card,
                        rating=rating,
                        response_time_ms=resp_ms,
                        evaluation_time_ms=eval_ms,
                    )
                except Exception as e:
                    logger.warning(f"Failed to record session analytics: {e}")

            # Remove card from session queue after successful review
            self._remove_card_from_queue(card_uuid)

            return updated_card

        except Exception as e:
            logger.error(f"Failed to submit review for card {card_uuid}: {e}")
            raise

    def get_session_stats(self) -> Dict[str, int]:
        """
        Returns statistics for the current review session.

        Returns:
            A dictionary with session statistics.
        """
        total_cards = len(self.current_session_card_uuids)
        reviewed_cards = total_cards - len(self.review_queue)

        # Include real-time analytics if available
        basic_stats = {
            "total_cards": total_cards,
            "reviewed_cards": reviewed_cards,
        }

        if self._session_started:
            try:
                analytics_stats = (
                    self.session_manager.get_current_session_stats()
                )
                basic_stats.update(analytics_stats)
            except Exception as e:
                logger.warning(f"Failed to get session analytics: {e}")

        return basic_stats

    def end_session_with_insights(self) -> Dict[str, Any]:
        """
        End the current session and generate comprehensive insights.

        Returns:
            Dictionary containing session summary and insights
        """
        if not self._session_started:
            return {"error": "No active session to end"}

        try:
            # End the session analytics
            completed_session = self.session_manager.end_session()

            # Generate insights
            insights = self.session_manager.generate_session_insights(
                completed_session.session_uuid
            )

            self._session_started = False

            return {
                "session": {
                    "uuid": str(completed_session.session_uuid),
                    "duration_ms": completed_session.total_duration_ms,
                    "cards_reviewed": completed_session.cards_reviewed,
                    "decks_accessed": list(completed_session.decks_accessed),
                    "deck_switches": completed_session.deck_switches,
                    "interruptions": completed_session.interruptions,
                },
                "insights": {
                    "performance": {
                        "cards_per_minute": insights.cards_per_minute,
                        "average_response_time_ms": insights.average_response_time_ms,
                        "accuracy_percentage": insights.accuracy_percentage,
                        "focus_score": insights.focus_score,
                    },
                    "recommendations": insights.recommendations,
                    "achievements": insights.achievements,
                    "alerts": insights.alerts,
                    "comparisons": {
                        "vs_last_session": insights.vs_last_session,
                        "trend_direction": insights.trend_direction,
                    },
                },
            }

        except Exception as e:
            logger.error(f"Failed to end session with insights: {e}")
            return {"error": f"Failed to generate insights: {e}"}

    def get_due_card_count(self) -> int:
        """
        Gets the total number of cards currently due for review using the efficient database count method.

        Returns:
            The count of due cards.
        """
        today = date.today()  # Use local date for user-friendly scheduling
        return self.db.get_due_card_count(
            deck_name=self.deck_name, on_date=today
        )
