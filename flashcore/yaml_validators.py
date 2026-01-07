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
    """
    Determine or generate a UUID for a raw card, validating any provided identifier.
    
    If the card supplies a `uuid` value it is preferred; otherwise an `id` value is used for
    backward compatibility. If neither is present a new UUID is generated. If a provided
    value cannot be parsed as a UUID a YAMLProcessingError is returned and populated with
    contextual metadata from `context`.
    
    Parameters:
        raw_card (_RawYAMLCardEntry): The parsed raw card entry containing `uuid` and/or `id`.
        context (_CardProcessingContext): Processing context used to populate error details
            (file path, card index, question preview).
    
    Returns:
        uuid.UUID if a valid or newly generated UUID is available, `YAMLProcessingError` if a
        provided identifier has an invalid UUID format.
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
    """
    Normalize and HTML-sanitize the card front and back text.
    
    Parameters:
        raw_card (_RawYAMLCardEntry): Raw card entry containing `q` (front) and `a` (back) text.
    
    Returns:
        Tuple[str, str]: (front_sanitized, back_sanitized) — the trimmed and HTML-sanitized front and back text.
    """
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
    """
    Detects potential secret patterns in the card front or back text.
    
    If secret detection is disabled via the provided context, no scan is performed.
    When a pattern matches, returns a YAMLProcessingError populated with the source
    file, card index, a question snippet, and which field (`q` or `a`) contained the match.
    
    Parameters:
        context (_CardProcessingContext): Provides the skip flag and metadata used to
            populate any returned YAMLProcessingError.
    
    Returns:
        YAMLProcessingError: Details about the detected secret and affected field, or
        `None` if no secret pattern was found or detection was skipped.
    """
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
    """
    Merge deck-level tags with optional card-level tags into a normalized tag set.
    
    Card-level tags are stripped of surrounding whitespace and lowercased before being added.
    Parameters:
        deck_tags (Set[str]): Base set of tags defined at the deck level.
        card_tags (Optional[List[str]]): Optional list of tags defined on the card.
    
    Returns:
        Set[str]: Combined set of tags including deck tags and normalized card tags.
    """
    final_tags = deck_tags.copy()
    if card_tags:
        final_tags.update(tag.strip().lower() for tag in card_tags)
    return final_tags


def _handle_skipped_media_validation(media_paths: List[str]) -> List[Path]:
    """
    Convert a list of media path strings to Path objects without performing validation.
    
    If `media_paths` is not a list, returns an empty list.
    
    Parameters:
        media_paths (List[str]): Iterable of media path strings.
    
    Returns:
        List[Path]: Converted Path objects for each entry in `media_paths`, or an empty list if input is not a list.
    """
    if not isinstance(media_paths, list):
        return []
    return [Path(p) for p in media_paths]


def _validate_media_path_list(
    media_paths: List[str],
    context: _CardProcessingContext,
) -> Union[List[Path], YAMLProcessingError]:
    """
    Validate a list of media path strings and convert them to Path objects.
    
    Parameters:
        media_paths (List[str]): Sequence of media path strings to validate and convert.
    
    Returns:
        Union[List[Path], YAMLProcessingError]: A list of validated Path objects, or a YAMLProcessingError describing the first validation failure.
    """
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
    """
    Validate and resolve a card's media path entries according to the provided processing context.
    
    Parameters:
        media_paths (List[str]): List of media path strings from the card; if media validation is skipped, entries are converted to Path objects without filesystem checks.
        context (_CardProcessingContext): Processing context that may enable skipping media validation and supplies file/card metadata used in generated YAMLProcessingError instances.
    
    Returns:
        Union[List[Path], YAMLProcessingError]: A list of resolved Path objects when validation succeeds, or a YAMLProcessingError describing the first validation failure.
    """
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
    """
    Validate a single media path string and ensure it resolves to an existing file inside the assets root.
    
    Parameters:
        media_item_str (str): Raw media path string from the card entry.
        context (_CardProcessingContext): Processing context containing source file path, card index, assets root directory, skip flag, and preview snippet used to construct error metadata.
    
    Returns:
        Path: Resolved file path (relative to the assets root) when the media path is valid.
        YAMLProcessingError: Error containing contextual details when the path is absolute, resolves outside the assets root, does not exist, is a directory, or another validation error occurs.
    """
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
    """
    Validate and normalize a single raw card and return its canonical components or a YAMLProcessingError.
    
    This runs end-to-end card validation: determine or generate the card UUID, sanitize front and back text, detect secrets (unless skipped by the context), merge deck-level and card-level tags, and validate media paths (unless media validation is skipped).
    
    Parameters:
        raw_card (_RawYAMLCardEntry): The parsed raw card entry to validate.
        context (_CardProcessingContext): Processing options and metadata that influence validation (for example, flags to skip secret or media validation and assets root paths).
        deck_tags (Set[str]): Deck-level tags to merge with any card-level tags.
    
    Returns:
        Tuple[uuid.UUID, str, str, Set[str], List[Path]] | YAMLProcessingError:
            On success, a tuple containing:
                - UUID: the validated or generated card UUID.
                - front (str): the sanitized front/question text.
                - back (str): the sanitized back/answer text.
                - tags (Set[str]): the merged set of lowercased tags.
                - media_paths (List[Path]): validated Paths for card media (empty list if none or validation skipped).
            On failure, a YAMLProcessingError describing the first validation error encountered.
    """
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
    """
    Verify the source directory exists and, unless media validation is skipped, verify the assets root exists.
    
    Parameters:
        source_directory (Path): Path expected to be an existing directory for the YAML source.
        assets_root_directory (Path): Path expected to be the assets root directory.
        skip_media_validation (bool): If True, skip checking existence of assets_root_directory.
    
    Returns:
        YAMLProcessingError: Error describing the invalid path when a required directory is missing.
        None: When all required directory checks pass.
    """
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
    """
    Validate and return the deck name from top-level YAML content.
    
    Parameters:
        raw_yaml_content (Dict): Parsed YAML mapping representing the deck file.
        file_path (Path): Path to the source YAML file (used for error context).
    
    Returns:
        str: Trimmed deck name.
    
    Raises:
        YAMLProcessingError: If the `deck` field is missing, not a string, or is empty/whitespace only.
    """
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
    """
    Return the set of deck-level tags normalized to lowercase and stripped of surrounding whitespace.
    
    Parameters:
        raw_yaml_content (Dict): Parsed top-level YAML mapping that may contain a "tags" key.
        file_path (Path): Path to the source YAML file used to produce error context.
    
    Returns:
        Set[str]: A set of unique tag strings from `raw_yaml_content["tags"]`, each stripped and lowercased.
    
    Raises:
        YAMLProcessingError: If the `tags` field is present but is not a list.
    """
    tags = raw_yaml_content.get("tags", [])
    if tags is not None and not isinstance(tags, list):
        raise YAMLProcessingError(
            file_path, "'tags' field must be a list if present."
        )

    if not tags:
        return set()

    return {t.strip().lower() for t in tags if isinstance(t, str)}


def extract_cards_list(raw_yaml_content: Dict, file_path: Path) -> List[Dict]:
    """
    Validate and return the top-level list of card entries from parsed YAML content.
    
    Parameters:
        raw_yaml_content (Dict): Parsed YAML document as a mapping.
        file_path (Path): Path to the source YAML file (used in error reporting).
    
    Returns:
        List[Dict]: The non-empty list of card dictionaries from the top-level 'cards' key.
    
    Raises:
        YAMLProcessingError: If the 'cards' key is missing, is not a list, or the list is empty.
    """
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
    """
    Validate top-level deck fields and return the deck's extracted metadata.
    
    Parameters:
        raw_yaml_content (Dict): Parsed YAML mapping for the deck file.
        file_path (Path): Path to the source YAML file used for contextual error messages.
    
    Returns:
        Tuple[str, Set[str], List[Dict]]: A tuple containing:
            - deck_name: The trimmed deck name.
            - deck_tags: A set of lowercased, stripped deck-level tags.
            - cards_list: The list of card dictionaries from the deck.
    
    Raises:
        YAMLProcessingError: If the deck name, tags, or cards list fail validation.
    """
    deck_name = extract_deck_name(raw_yaml_content, file_path)
    deck_tags = extract_deck_tags(raw_yaml_content, file_path)
    cards_list = extract_cards_list(raw_yaml_content, file_path)
    return deck_name, deck_tags, cards_list


def validate_raw_card_structure(
    card_dict: Dict, idx: int, file_path: Path
) -> Union[_RawYAMLCardEntry, YAMLProcessingError]:
    """
    Validate and normalize a single raw card dictionary and return either a validated card model or a YAMLProcessingError.
    
    Normalizes legacy keys ('front' -> 'q', 'back' -> 'a') when present, then validates the resulting mapping against the _RawYAMLCardEntry model. If the input is not a mapping or validation fails, returns a YAMLProcessingError that includes the source file path, card index, and a short snippet of the card question when available.
    
    Parameters:
        card_dict (Dict): The raw card entry parsed from YAML.
        idx (int): Zero-based index of the card within the source file, used for error reporting.
        file_path (Path): Path to the YAML file being processed, included in any returned error.
    
    Returns:
        Union[_RawYAMLCardEntry, YAMLProcessingError]: A validated _RawYAMLCardEntry on success, or a YAMLProcessingError describing why validation failed.
    """
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