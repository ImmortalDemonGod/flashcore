"""
Shared review processing logic for flashcore.

This module consolidates the core review submission logic that was previously
duplicated between ReviewSessionManager and _review_all_logic.py.

The ReviewProcessor class encapsulates all the common steps:
1. Timestamp handling
2. Review history fetching
3. Scheduler computation
4. Review object creation
5. Database persistence
6. Error handling
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from .models import Card, Review
from .db.database import FlashcardDatabase
from .scheduler import FSRS_Scheduler, SchedulerOutput

# Initialize logger
logger = logging.getLogger(__name__)


class ReviewProcessor:
    """
    Processes review submissions with consistent logic across all review workflows.

    This class consolidates the core review processing logic that was previously
    duplicated between ReviewSessionManager.submit_review() and _submit_single_review().

    Benefits:
    - Single source of truth for review processing
    - Eliminates code duplication
    - Easier to maintain and extend
    - Consistent behavior across all review workflows
    - Foundation for future session analytics integration
    """

    def __init__(
        self, db_manager: FlashcardDatabase, scheduler: FSRS_Scheduler
    ):
        """
        Initialize the ReviewProcessor.

        Args:
            db_manager: Database manager instance for persistence
            scheduler: FSRS scheduler instance for computing next states
        """
        self.db_manager = db_manager
        self.scheduler = scheduler

    def process_review(
        self,
        card: Card,
        rating: int,
        resp_ms: int = 0,
        eval_ms: int = 0,
        reviewed_at: Optional[datetime] = None,
        session_uuid: Optional[UUID] = None,
    ) -> Card:
        """
        Process a review submission with consistent logic.

        This method encapsulates all the core review processing steps:
        1. Handle timestamp (use provided or current time)
        2. Compute next state using scheduler (O(1) with cached card state)
        3. Create Review object with all required fields
        4. Persist to database and update card state
        5. Return updated card

        Args:
            card: The card being reviewed
            rating: User's rating (1-4: Again, Hard, Good, Easy)
            resp_ms: Response time in milliseconds (time to reveal answer)
            eval_ms: Evaluation time in milliseconds (time to provide rating)
            reviewed_at: Review timestamp (defaults to current time)
            session_uuid: Optional session UUID for analytics (future use)

        Returns:
            Updated Card object with new state and scheduling information

        Raises:
            ValueError: If rating is invalid or card data is inconsistent
            CardOperationError: If database operation fails
        """
        # Step 1: Handle timestamp
        ts = reviewed_at or datetime.now(timezone.utc)

        logger.debug(
            f"Processing review for card {card.uuid} with rating {rating}"
        )

        try:
            # Step 2: Compute next state using scheduler (O(1) with cached card state)
            scheduler_output: SchedulerOutput = (
                self.scheduler.compute_next_state(
                    card=card, new_rating=rating, review_ts=ts
                )
            )

            # Step 3: Create Review object with all required fields
            new_review = Review(
                card_uuid=card.uuid,
                session_uuid=session_uuid,  # For future session analytics
                ts=ts,
                rating=rating,
                resp_ms=resp_ms,
                eval_ms=eval_ms,
                stab_before=card.stability,  # Card's stability before this review
                stab_after=scheduler_output.stab,
                diff=scheduler_output.diff,
                next_due=scheduler_output.next_due,
                elapsed_days_at_review=scheduler_output.elapsed_days,
                scheduled_days_interval=scheduler_output.scheduled_days,
                review_type=scheduler_output.review_type,
            )

            # Step 4: Persist to database and update card state
            updated_card = self.db_manager.add_review_and_update_card(
                review=new_review, new_card_state=scheduler_output.state
            )

            logger.debug(
                f"Review processed successfully for card {card.uuid}. "
                f"Next due: {updated_card.next_due_date}, State: {updated_card.state}"
            )

            # Step 5: Return updated card
            return updated_card

        except Exception:
            logger.exception(f"Failed to process review for card {card.uuid}")
            raise

    def process_review_by_uuid(
        self,
        card_uuid: UUID,
        rating: int,
        resp_ms: int = 0,
        eval_ms: int = 0,
        reviewed_at: Optional[datetime] = None,
        session_uuid: Optional[UUID] = None,
    ) -> Card:
        """
        Process a review submission by card UUID.

        This is a convenience method that fetches the card by UUID and then
        calls process_review(). Useful when you only have the card UUID.

        Args:
            card_uuid: UUID of the card being reviewed
            rating: User's rating (1-4: Again, Hard, Good, Easy)
            resp_ms: Response time in milliseconds
            eval_ms: Evaluation time in milliseconds
            reviewed_at: Review timestamp (defaults to current time)
            session_uuid: Optional session UUID for analytics

        Returns:
            Updated Card object

        Raises:
            ValueError: If card not found or rating invalid
            CardOperationError: If database operation fails
        """
        # Fetch the card first
        card = self.db_manager.get_card_by_uuid(card_uuid)
        if not card:
            raise ValueError(f"Card {card_uuid} not found in database")

        # Delegate to main process_review method
        return self.process_review(
            card=card,
            rating=rating,
            resp_ms=resp_ms,
            eval_ms=eval_ms,
            reviewed_at=reviewed_at,
            session_uuid=session_uuid,
        )
