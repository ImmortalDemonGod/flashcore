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
    """
    Prepare a database row dictionary for constructing a Card model.

    Parameters:
        row_dict (Dict[str, Any]): Raw database row; may contain keys `media_paths`, `source_yaml_file`, `tags`, and `state`.  # noqa: E501

    Returns:
        Dict[str, Any]: A copy of the input row with canonicalized fields:
            - `media`: list of Path objects (empty list if no media_paths).
            - `source_yaml_file`: Path if present.
            - `tags`: set of tags (empty set if missing).
            - `state`: CardState enum value if `state` was provided.
    """
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
    """
    Convert a sequence of Card models into a list of tuples suitable for bulk database insertion.  # noqa: E501

    This function will ensure each card has complexity metrics (front_length, back_length, has_media, tag_count)  # noqa: E501
    by calling card.calculate_complexity_metrics() when any of those fields are missing; that call may mutate  # noqa: E501
    the input Card objects.

    Returns:
        List[Tuple]: A list of tuples, one per card, with fields in the following order:  # noqa: E501
        (uuid, deck_name, front, back, tags, added_at, modified_at, last_review_id, next_due_date,  # noqa: E501
        state_name, stability, difficulty, origin_task, media_paths, source_yaml_file, internal_note,  # noqa: E501
        front_length, back_length, has_media, tag_count).
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
    Create a Card model from a database row dictionary.

    Transforms database-native fields to model-compatible types and validates the result.  # noqa: E501

    Returns:
        Card: The constructed Card instance.

    Raises:
        MarshallingError: If the row cannot be validated into a Card (wraps the original ValidationError).  # noqa: E501
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
    """
    Convert a Review model into a tuple suitable for database insertion.

    Parameters:
        review (Review): Review instance to serialize.

    Returns:
        tuple: Ordered tuple with fields:
                (card_uuid, session_uuid, ts, rating, resp_ms, eval_ms,
                 stab_before, stab_after, diff, next_due,
                 elapsed_days_at_review, scheduled_days_interval, review_type)
    """
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
    """
    Serialize a Session model into a tuple suitable for database insertion.

    Parameters:
        session (Session): Session model to serialize.

    Returns:
        A tuple containing, in order:
        - `session_uuid`: session UUID
        - `user_id`: user identifier
        - `start_ts`: session start timestamp
        - `end_ts`: session end timestamp
        - `total_duration_ms`: total session duration in milliseconds
        - `cards_reviewed`: number of cards reviewed
        - `decks_accessed`: list of accessed deck names or `None` if empty
        - `deck_switches`: number of times the deck was switched
        - `interruptions`: count of interruptions
        - `device_type`: device type string
        - `platform`: platform string
    """
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
    """
    Create a Session model from a raw database row dictionary.

    Converts the 'decks_accessed' entry to a set (an empty set if missing) before constructing the model. Raises MarshallingError if Pydantic validation fails.  # noqa: E501

    Parameters:
        row_dict (Dict[str, Any]): Raw database row mapping column names to values.  # noqa: E501

    Returns:
        Session: Constructed Session instance.

    Raises:
        MarshallingError: If model validation fails while building the Session.
    """
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
    Locate the most recent backup file for the given database path.

    Parameters:
        db_path (Path): Path to the main database file; the function
            looks for backups in a "backups" subdirectory of
            db_path.parent.

    Returns:
        Path or None: Path to the latest backup file, or `None` if no
            backups are found.
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
