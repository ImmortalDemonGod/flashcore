"""
Houses all validation-related functions for the YAML processing pipeline.
"""

import uuid
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

import bleach
from pydantic import ValidationError

from .yaml_models import (
    DEFAULT_ALLOWED_HTML_ATTRIBUTES,
    DEFAULT_ALLOWED_HTML_TAGS,
    DEFAULT_CSS_SANITIZER,
    DEFAULT_SECRET_PATTERNS,
    _CardProcessingContext,
    _RawYAMLCardEntry,
    YAMLProcessingError,
)


def validate_card_uuid(
    raw_card: _RawYAMLCardEntry, context: _CardProcessingContext
) -> Union[uuid.UUID, YAMLProcessingError]:
    """Validate the raw UUID.

    Returns a UUID object or a YAMLProcessingError.
    """
    # Check uuid field first (preferred), then fall back to id field
    # for backward compatibility.
    uuid_value = raw_card.uuid or raw_card.id
    field_name = "uuid" if raw_card.uuid is not None else "id"

    if uuid_value is None:
        return uuid.uuid4()  # Assign a new UUID if none is provided
    try:
        return uuid.UUID(uuid_value)
    except ValueError:
        return YAMLProcessingError(
            file_path=context.source_file_path,
            card_index=context.card_index,
            card_question_snippet=context.card_q_preview,
            field_name=field_name,
            message=(
                "Invalid UUID format for '{field_name}': '{uuid_value}'."
            ).format(field_name=field_name, uuid_value=uuid_value),
        )


def sanitize_card_text(raw_card: _RawYAMLCardEntry) -> Tuple[str, str]:
    """Normalizes and sanitizes card front and back text."""
    front_normalized = raw_card.q.strip()
    back_normalized = raw_card.a.strip()
    front_sanitized = bleach.clean(
        front_normalized,
        tags=DEFAULT_ALLOWED_HTML_TAGS,
        attributes=DEFAULT_ALLOWED_HTML_ATTRIBUTES,
        css_sanitizer=DEFAULT_CSS_SANITIZER,
        strip=True,
    )
    back_sanitized = bleach.clean(
        back_normalized,
        tags=DEFAULT_ALLOWED_HTML_TAGS,
        attributes=DEFAULT_ALLOWED_HTML_ATTRIBUTES,
        css_sanitizer=DEFAULT_CSS_SANITIZER,
        strip=True,
    )
    return front_sanitized, back_sanitized


def check_for_secrets(
    front: str, back: str, context: _CardProcessingContext
) -> Optional[YAMLProcessingError]:
    """Scans text for secrets, returning an error if a secret is found."""
    if context.skip_secrets_detection:
        return None

    for pattern in DEFAULT_SECRET_PATTERNS:
        if pattern.search(back):
            return YAMLProcessingError(
                file_path=context.source_file_path,
                card_index=context.card_index,
                card_question_snippet=context.card_q_preview,
                field_name="a",
                message=(
                    "Potential secret detected in card answer. "
                    f"Matched pattern: '{pattern.pattern[:50]}...'."
                ),
            )
        if pattern.search(front):
            return YAMLProcessingError(
                file_path=context.source_file_path,
                card_index=context.card_index,
                card_question_snippet=context.card_q_preview,
                field_name="q",
                message=(
                    "Potential secret detected in card question. "
                    f"Matched pattern: '{pattern.pattern[:50]}...'."
                ),
            )

    return None


def compile_card_tags(
    deck_tags: Set[str],
    card_tags: Optional[List[str]],
) -> Set[str]:
    """Combines deck-level and card-level tags into a single set."""
    final_tags = deck_tags.copy()
    if card_tags:
        final_tags.update(tag.strip().lower() for tag in card_tags)
    return final_tags


def _handle_skipped_media_validation(media_paths: List[str]) -> List[Path]:
    """Converts media paths to Path objects without validation."""
    if not isinstance(media_paths, list):
        return []
    return [Path(p) for p in media_paths]


def _validate_media_path_list(
    media_paths: List[str],
    context: _CardProcessingContext,
) -> Union[List[Path], YAMLProcessingError]:
    """Iterates through and validates a list of media path strings."""
    processed_media_paths = []
    for path_str in media_paths:
        result = validate_single_media_path(path_str, context)
        if isinstance(result, YAMLProcessingError):
            return result
        processed_media_paths.append(result)
    return processed_media_paths


def validate_media_paths(
    media_paths: List[str],
    context: _CardProcessingContext,
) -> Union[List[Path], YAMLProcessingError]:
    """Validates all media paths for a card."""
    if context.skip_media_validation:
        return _handle_skipped_media_validation(media_paths)

    if not isinstance(media_paths, list):
        return YAMLProcessingError(
            context.source_file_path,
            (
                "The 'media' field must be a list of strings, but got "
                f"{type(media_paths).__name__}."
            ),
            card_index=context.card_index,
            card_question_snippet=context.card_q_preview,
            field_name="media",
        )

    return _validate_media_path_list(media_paths, context)


def validate_single_media_path(
    media_item_str: str,
    context: _CardProcessingContext,
) -> Union[Path, YAMLProcessingError]:
    """Validates a single media path."""
    media_path = Path(media_item_str.strip())
    if media_path.is_absolute() or media_path.drive or media_path.root:
        return YAMLProcessingError(
            file_path=context.source_file_path,
            card_index=context.card_index,
            card_question_snippet=context.card_q_preview,
            field_name="media",
            message=("Media path must be relative: '{media_path}'.").format(
                media_path=media_path
            ),
        )

    if not context.skip_media_validation:
        try:
            candidate_path = context.assets_root_directory / media_path
            full_media_path = candidate_path.resolve(strict=False)
            abs_assets_root = context.assets_root_directory.resolve(
                strict=True
            )
            if not str(full_media_path).startswith(str(abs_assets_root)):
                return YAMLProcessingError(
                    file_path=context.source_file_path,
                    card_index=context.card_index,
                    card_question_snippet=context.card_q_preview,
                    field_name="media",
                    message=(
                        "Media path '{media_path}' resolves outside "
                        "the assets root directory."
                    ).format(media_path=media_path),
                )
            if not full_media_path.exists():
                return YAMLProcessingError(
                    file_path=context.source_file_path,
                    card_index=context.card_index,
                    card_question_snippet=context.card_q_preview,
                    field_name="media",
                    message=(
                        "Media file not found at expected path: "
                        f"'{full_media_path}'."
                    ),
                )
            if full_media_path.is_dir():
                return YAMLProcessingError(
                    file_path=context.source_file_path,
                    card_index=context.card_index,
                    card_question_snippet=context.card_q_preview,
                    field_name="media",
                    message=(
                        "Media path is a directory, not a file: "
                        f"'{media_path}'."
                    ),
                )
            return full_media_path
        except Exception as e:
            return YAMLProcessingError(
                file_path=context.source_file_path,
                card_index=context.card_index,
                card_question_snippet=context.card_q_preview,
                field_name="media",
                message=(
                    "Error validating media path '{media_path}': {e}."
                ).format(media_path=media_path, e=e),
            )

    return Path(media_path)


def run_card_validation_pipeline(
    raw_card: _RawYAMLCardEntry,
    context: _CardProcessingContext,
    deck_tags: Set[str],
) -> Union[
    Tuple[uuid.UUID, str, str, Set[str], List[Path]],
    YAMLProcessingError,
]:
    """Run the validation pipeline for a raw card."""
    uuid_or_error = validate_card_uuid(raw_card, context)
    if isinstance(uuid_or_error, YAMLProcessingError):
        return uuid_or_error

    front, back = sanitize_card_text(raw_card)

    secret_error = check_for_secrets(front, back, context)
    if secret_error:
        return secret_error

    final_tags = compile_card_tags(deck_tags, raw_card.tags)

    media_paths: List[Path] = []
    if raw_card.media:
        media_paths_or_error = validate_media_paths(raw_card.media, context)
        if isinstance(media_paths_or_error, YAMLProcessingError):
            return media_paths_or_error
        media_paths = media_paths_or_error

    return uuid_or_error, front, back, final_tags, media_paths


def validate_directories(
    source_directory: Path,
    assets_root_directory: Path,
    skip_media_validation: bool,
) -> Optional[YAMLProcessingError]:
    """Validates that the source and asset directories exist."""
    if not source_directory.is_dir():
        return YAMLProcessingError(
            source_directory,
            "Source directory does not exist or is not a directory.",
        )

    if not assets_root_directory.is_dir():
        if not skip_media_validation:
            return YAMLProcessingError(
                assets_root_directory,
                "Assets root directory does not exist or is not a directory.",
            )

    return None


def extract_deck_name(raw_yaml_content: Dict, file_path: Path) -> str:
    """Extracts and validates the deck name from the raw YAML content."""
    deck_value = raw_yaml_content.get("deck")
    if deck_value is None:
        raise YAMLProcessingError(
            file_path, "Missing 'deck' field at top level."
        )
    if not isinstance(deck_value, str):
        raise YAMLProcessingError(file_path, "'deck' field must be a string.")
    if not deck_value.strip():
        raise YAMLProcessingError(
            file_path,
            "'deck' field cannot be empty or just whitespace.",
        )
    return deck_value.strip()


def extract_deck_tags(raw_yaml_content: Dict, file_path: Path) -> Set[str]:
    """Extracts and validates deck-level tags from the raw YAML content."""
    tags = raw_yaml_content.get("tags", [])
    if tags is not None and not isinstance(tags, list):
        raise YAMLProcessingError(
            file_path, "'tags' field must be a list if present."
        )

    if not tags:
        return set()

    return {t.strip().lower() for t in tags if isinstance(t, str)}


def extract_cards_list(raw_yaml_content: Dict, file_path: Path) -> List[Dict]:
    """Extracts and validates the list of cards from the raw YAML content."""
    if "cards" not in raw_yaml_content or not isinstance(
        raw_yaml_content["cards"],
        list,
    ):
        raise YAMLProcessingError(
            file_path,
            "Missing or invalid 'cards' list at top level.",
        )

    cards_list = raw_yaml_content["cards"]
    if not cards_list:
        raise YAMLProcessingError(file_path, "No cards found in 'cards' list.")

    return cards_list


def validate_deck_and_extract_metadata(
    raw_yaml_content: Dict, file_path: Path
) -> Tuple[str, Set[str], List[Dict]]:
    """Validate deck structure and extract metadata."""
    deck_name = extract_deck_name(raw_yaml_content, file_path)
    deck_tags = extract_deck_tags(raw_yaml_content, file_path)
    cards_list = extract_cards_list(raw_yaml_content, file_path)
    return deck_name, deck_tags, cards_list


def validate_raw_card_structure(
    card_dict: Dict, idx: int, file_path: Path
) -> Union[_RawYAMLCardEntry, YAMLProcessingError]:
    """Validates the structure of a raw card dict using Pydantic."""
    if not isinstance(card_dict, dict):
        return YAMLProcessingError(
            file_path=file_path,
            message="Card entry is not a valid dictionary.",
            card_index=idx,
        )

    card_dict_copy = card_dict.copy()
    if "front" in card_dict_copy and "q" not in card_dict_copy:
        card_dict_copy["q"] = card_dict_copy.pop("front")
    if "back" in card_dict_copy and "a" not in card_dict_copy:
        card_dict_copy["a"] = card_dict_copy.pop("back")

    try:
        return _RawYAMLCardEntry.model_validate(card_dict_copy)
    except ValidationError as e:
        error_details = "; ".join(
            [
                f"{''.join(map(str, err['loc']))}: {err['msg']}"
                for err in e.errors()
            ]
        )
        q_preview = card_dict.get("q", "N/A")
        return YAMLProcessingError(
            file_path=file_path,
            message=f"Card validation failed. Details: {error_details}",
            card_index=idx,
            card_question_snippet=q_preview,
        )
