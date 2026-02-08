from cultivation.scripts.flashcore.cli.review_ui import start_review_flow
from typing import List, Optional

from cultivation.scripts.flashcore.config import settings
from cultivation.scripts.flashcore.database import FlashcardDatabase
from cultivation.scripts.flashcore.review_manager import ReviewSessionManager
from cultivation.scripts.flashcore.scheduler import FSRS_Scheduler

def review_logic(deck_name: str, tags: Optional[List[str]] = None):
    """
    Core logic for the review session.
    """
    # The database path is now handled automatically by the FlashcardDatabase class,
    # which reads from the centralized settings object.
    db_manager = FlashcardDatabase()
    db_manager.initialize_schema()

    scheduler = FSRS_Scheduler()

    manager = ReviewSessionManager(
        db_manager=db_manager,
        scheduler=scheduler,
        user_uuid=settings.user_uuid,
        deck_name=deck_name,
    )

    start_review_flow(manager, tags=tags)

