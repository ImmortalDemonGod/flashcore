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
    Core logic for the review session.

    Args:
        deck_name: Name of the deck to review.
        db_path: Path to the database file (DI, no defaults).
        user_uuid: UUID of the user conducting the review.
        tags: Optional list of tags to filter cards by.
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

