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
        Create a ReviewSessionManager for a user's deck and prepare a new review session context.

        Parameters:
            db_manager (FlashcardDatabase): Database interface used to load and persist cards and session data.
            scheduler (FSRS): Scheduling engine used to compute card due dates and spacing.
            user_uuid (UUID): Identifier of the user who will perform the review session.
            deck_name (str): Name of the deck to review.

        Notes:
            Initializes session-specific state including `session_uuid`, `review_queue`, `current_session_card_uuids`,
            `session_start_time`, a shared `review_processor`, and a `session_manager` for analytics. The `_session_started`
            flag is initialized to False.
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
        Initialize a review session: start analytics (if not started), fetch due cards for today, and populate the session queue.

        Starts session analytics if not already active, then fetches due cards for the manager's deck (optionally filtered by `tags`) limited by `limit`, sorts them by `modified_at`, and stores them in `self.review_queue` and `self.current_session_card_uuids`.

        Parameters:
            limit (int): Maximum number of cards to include in the session.
            tags (Optional[List[str]]): Optional list of tags to filter which cards are fetched.
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
        Remove a card with the given UUID from the session's review queue.

        Parameters:
            card_uuid (UUID): UUID of the card to remove from the queue.
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
        Submit a review for a card in the current session and update the card's state and next scheduled review.

        Parameters:
            card_uuid (UUID): UUID of the card to review.
            rating (int): User's rating for the review (e.g., Again, Hard, Good, Easy).
            reviewed_at (Optional[datetime]): Timestamp when the review occurred; defaults to now when omitted.
            resp_ms (int): Time in milliseconds from showing the card to revealing the answer.
            eval_ms (int): Time in milliseconds taken to decide and submit the rating.

        Returns:
            Card: The updated Card object reflecting the processed review.

        Raises:
            ValueError: If the specified card is not part of the current review session.
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
        Provide aggregated statistics for the active review session.

        Returns:
            dict: Mapping containing session statistics:
                - "total_cards" (int): Number of cards that were initially in the session.
                - "reviewed_cards" (int): Number of cards reviewed so far.
                Additional keys may be present when session analytics are active; those metrics (e.g., performance or timing statistics) are merged into the returned dictionary.
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
        End the active review session and produce a structured summary with analytics-driven insights.

        If a session is active, ends analytics tracking, compiles a session summary (uuid, duration, reviewed cards, decks accessed, deck switches, interruptions) and an insights block containing performance metrics, recommendations, achievements, alerts, and comparisons. If no session is active or an error occurs, returns an error description.

        Returns:
            dict: On success, a dictionary with keys:
                - "session": dict with keys:
                    - "uuid" (str): Session UUID.
                    - "duration_ms" (int): Total session duration in milliseconds.
                    - "cards_reviewed" (int): Number of cards reviewed in the session.
                    - "decks_accessed" (List[str]): Deck names accessed during the session.
                    - "deck_switches" (int): Number of times the user switched decks.
                    - "interruptions" (int): Number of interruptions recorded.
                - "insights": dict containing:
                    - "performance": dict with keys:
                        - "cards_per_minute" (float)
                        - "average_response_time_ms" (float)
                        - "accuracy_percentage" (float)
                        - "focus_score" (float)
                    - "recommendations" (Any): Actionable suggestions.
                    - "achievements" (Any): Achievements earned during the session.
                    - "alerts" (Any): Notable alerts or warnings.
                    - "comparisons": dict with keys:
                        - "vs_last_session" (Any): Comparison data against the previous session.
                        - "trend_direction" (Any): High-level trend indicator.
            On failure or when no session is active, returns:
                dict: {"error": "<error message>"}
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
        Get the number of cards due for the manager's deck on today's date.

        Returns:
            The number of due cards for the manager's deck on today's date.
        """
        today = date.today()  # Use local date for user-friendly scheduling
        return self.db.get_due_card_count(
            deck_name=self.deck_name, on_date=today
        )
