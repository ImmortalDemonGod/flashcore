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
        self.db = db_manager
        self.scheduler = scheduler
        self.user_uuid = user_uuid
        self.deck_name = deck_name
        self.session_uuid = uuid4()
        self.review_queue: list[Card] = []
        self.current_session_card_uuids: Set[UUID] = set()
        self.session_start_time = datetime.now(timezone.utc)
        self.review_processor = ReviewProcessor(db_manager, scheduler)
        self.session_manager = SessionManager(db_manager, user_id=str(user_uuid))
        self._session_started = False
        self.skipped_card_count: int = 0

    def initialize_session(
        self, limit: int = 20, tags: Optional[List[str]] = None
    ) -> None:
        logger.info(
            f"Initializing review session {self.session_uuid} for user {self.user_uuid} and deck '{self.deck_name}'"
        )
        if tags:
            logger.info(f"Filtering cards by tags: {tags}")
        if not self._session_started:
            try:
                self.session_manager.start_session(
                    device_type="desktop",
                    platform="cli",
                    session_uuid=self.session_uuid,
                )
                self._session_started = True
            except Exception as e:
                logger.warning(f"Failed to start session analytics: {e}")
        today = date.today()
        due_cards = self.db.get_due_cards(
            self.deck_name, on_date=today, limit=limit, tags=tags
        )
        # Correct ordering by next_due_date (scheduler priority)
        self.review_queue = sorted(due_cards, key=lambda c: c.next_due_date)
        self.current_session_card_uuids = {card.uuid for card in self.review_queue}
        logger.info(f"Initialized session with {len(self.review_queue)} cards.")

    def get_next_card(self) -> Optional[Card]:
        if not self.review_queue:
            return None
        return self.review_queue[0]

    def _get_card_from_queue(self, card_uuid: UUID) -> Optional[Card]:
        for card in self.review_queue:
            if card.uuid == card_uuid:
                return card
        return None

    def _remove_card_from_queue(self, card_uuid: UUID) -> None:
        self.review_queue = [c for c in self.review_queue if c.uuid != card_uuid]

    def skip_card(self, card_uuid: UUID) -> None:
        before = len(self.review_queue)
        self._remove_card_from_queue(card_uuid)
        if len(self.review_queue) < before:
            self.skipped_card_count += 1

    def submit_review(
        self,
        card_uuid: UUID,
        rating: int,
        reviewed_at: Optional[datetime] = None,
        resp_ms: int = 0,
        eval_ms: int = 0,
    ) -> Card:
        card = self._get_card_from_queue(card_uuid)
        if not card:
            raise ValueError(f"Card {card_uuid} not found in the current review session.")
        updated_card = self.review_processor.process_review(
            card=card,
            rating=rating,
            resp_ms=resp_ms,
            eval_ms=eval_ms,
            reviewed_at=reviewed_at,
            session_uuid=self.session_uuid,
        )
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
        self._remove_card_from_queue(card_uuid)
        return updated_card

    def get_session_stats(self) -> Dict[str, int]:
        total_cards = len(self.current_session_card_uuids)
        reviewed_cards = total_cards - len(self.review_queue) - self.skipped_card_count
        stats = {"total_cards": total_cards, "reviewed_cards": reviewed_cards}
        if self._session_started:
            try:
                stats.update(self.session_manager.get_current_session_stats())
            except Exception as e:
                logger.warning(f"Failed to get session analytics: {e}")
        return stats

    def end_session_with_insights(self) -> Dict[str, Any]:
        if not self._session_started:
            return {"error": "No active session to end"}
        try:
            completed = self.session_manager.end_session()
            insights = self.session_manager.generate_session_insights(completed.session_uuid)
            self._session_started = False
            return {
                "session": {
                    "uuid": str(completed.session_uuid),
                    "duration_ms": completed.total_duration_ms,
                    "cards_reviewed": completed.cards_reviewed,
                    "decks_accessed": list(completed.decks_accessed),
                    "deck_switches": completed.deck_switches,
                    "interruptions": completed.interruptions,
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
        today = date.today()
        return self.db.get_due_card_count(deck_name=self.deck_name, on_date=today)

# Compatibility shim for legacy imports
+ReviewManager = ReviewSessionManager
