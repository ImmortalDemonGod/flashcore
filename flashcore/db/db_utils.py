"""
Utility functions for data marshalling between Pydantic models and database formats.  # noqa: E501
This module helps decouple the core database logic from the specifics of data conversion.  # noqa: E501
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple
from pydantic import ValidationError

from ..models import Card, Review, Session, CardState
from ..exceptions import MarshallingError
import shutil
from datetime import datetime


def transform_db_row_for_card(row_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Transforms raw DB data into a dictionary suitable for the Card model."""
    data = row_dict.copy()

    media_paths = data.pop("media_paths", None)
    data["media"] = (
        [Path(p) for p in media_paths] if media_paths is not None else []
    )

    if data.get("source_yaml_file"):
        data["source_yaml_file"] = Path(data["source_yaml_file"])

    tags_val = data.get("tags")
    data["tags"] = set(tags_val) if tags_val is not None else set()

    state_val = data.pop("state", None)
    if state_val:
        data["state"] = CardState[state_val]

    return data


def card_to_db_params_list(cards: Sequence[Card]) -> List[Tuple]:
    """Converts a sequence of Card models to a list of tuples for DB insertion.
    
    Note: This function may mutate input Card objects by computing complexity
    metrics (front_length, back_length, has_media, tag_count) if not already set.
    """
    result = []
    for card in cards:
        # Calculate complexity metrics if not already set
        if (
            card.front_length is None
            or card.back_length is None
            or card.has_media is None
            or card.tag_count is None
        ):
            card.calculate_complexity_metrics()

        result.append(
            (
                card.uuid,
                card.deck_name,
                card.front,
                card.back,
                list(card.tags) if card.tags else None,
                card.added_at,
                card.modified_at,
                card.last_review_id,
                card.next_due_date,
                card.state.name if card.state else None,
                card.stability,
                card.difficulty,
                card.origin_task,
                [str(p) for p in card.media] if card.media else None,
                str(card.source_yaml_file) if card.source_yaml_file else None,
                card.internal_note,
                card.front_length,
                card.back_length,
                card.has_media,
                card.tag_count,
            )
        )
    return result


def db_row_to_card(row_dict: Dict[str, Any]) -> Card:
    """
    Converts a database row dictionary to a Card Pydantic model.
    This method handles necessary type transformations from DB types to model types.  # noqa: E501
    """
    data = transform_db_row_for_card(row_dict)

    try:
        return Card(**data)
    except ValidationError as e:
        # Consider adding logger here if this module gets one
        raise MarshallingError(
            f"Failed to parse card from DB row: {row_dict}. Error: {e}",
            original_exception=e,
        ) from e


def review_to_db_params_tuple(review: Review) -> Tuple:
    """Converts a Review model to a tuple for DB insertion."""
    return (
        review.card_uuid,
        review.session_uuid,
        review.ts,
        review.rating,
        review.resp_ms,
        review.eval_ms,
        review.stab_before,
        review.stab_after,
        review.diff,
        review.next_due,
        review.elapsed_days_at_review,
        review.scheduled_days_interval,
        review.review_type,
    )


def db_row_to_review(row_dict: Dict[str, Any]) -> Review:
    """Converts a database row dictionary to a Review Pydantic model."""
    return Review(**row_dict)


def session_to_db_params_tuple(session: Session) -> Tuple:
    """Converts a Session model to a tuple for DB insertion."""
    return (
        session.session_uuid,
        session.user_id,
        session.start_ts,
        session.end_ts,
        session.total_duration_ms,
        session.cards_reviewed,
        list(session.decks_accessed) if session.decks_accessed else None,
        session.deck_switches,
        session.interruptions,
        session.device_type,
        session.platform,
    )


def db_row_to_session(row_dict: Dict[str, Any]) -> Session:
    """Convert database row to Session model."""
    data = row_dict.copy()
    decks_accessed = data.pop("decks_accessed", None)
    data["decks_accessed"] = (
        set(decks_accessed) if decks_accessed is not None else set()
    )
    try:
        return Session(**data)
    except ValidationError as e:
        # Consider adding logger here if this module gets one
        raise MarshallingError(
            f"Data validation failed for session: {e}", original_exception=e
        ) from e


def find_latest_backup(db_path: Path) -> Optional[Path]:
    """
    Finds the most recent backup file in the backups directory.

    Args:
        db_path: The path to the main database file (to locate the backups dir).  # noqa: E501

    Returns:
        The path to the latest backup file, or None if no backups are found.
    """
    backup_dir = db_path.parent / "backups"
    if not backup_dir.exists():
        return None

    backup_files = list(backup_dir.glob(f"{db_path.stem}-backup-*.db"))
    if not backup_files:
        return None

    # Sort files by name, which includes the timestamp, to find the latest
    latest_backup = max(backup_files, key=lambda p: p.name)
    return latest_backup


def backup_database(db_path: Path) -> Path:
    """
    Creates a timestamped backup of the database file.

    Args:
        db_path: The path to the database file.

    Returns:
        The path to the created backup file.
    """
    if not db_path.exists():
        # No database to back up, so we can just return the original path.
        return db_path

    backup_dir = db_path.parent / "backups"
    backup_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_filename = f"{db_path.stem}-backup-{timestamp}{db_path.suffix}"
    backup_path = backup_dir / backup_filename

    shutil.copy2(db_path, backup_path)
    return backup_path
