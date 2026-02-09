from pathlib import Path
from typing import List, Optional
from uuid import UUID

from flashcore.cli.review_ui import start_review_flow
from flashcore.db.database import FlashcardDatabase
from flashcore.review_manager import ReviewSessionManager
from flashcore.scheduler import FSRS_Scheduler


def review_logic(
    deck_name: str,
    db_path: Path,
    user_uuid: UUID,
    tags: Optional[List[str]] = None,
):
    """
    Set up and start a review session for the specified deck.

    Initializes the flashcard database schema, creates a scheduler
    and review session manager for the given user and deck, and
    launches the interactive review flow.

    Parameters:
        deck_name (str): Name of the deck to review.
        db_path (Path): Path to the flashcard database file.
        user_uuid (UUID): UUID of the user conducting the review.
        tags (Optional[List[str]]): If provided, restricts the
            review to cards matching any of these tags.
    """
    db_manager = FlashcardDatabase(db_path=db_path)
    db_manager.initialize_schema()

    scheduler = FSRS_Scheduler()

    manager = ReviewSessionManager(
        db_manager=db_manager,
        scheduler=scheduler,
        user_uuid=user_uuid,
        deck_name=deck_name,
    )

    start_review_flow(manager, tags=tags)
