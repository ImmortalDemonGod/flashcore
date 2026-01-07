import logging
from pathlib import Path
from typing import Dict, List, Tuple, Union

import yaml
from pydantic import ValidationError

from .models import Card
from .yaml_models import (
    YAMLProcessingError,
    YAMLProcessorConfig,
    _FileProcessingContext,
    _RawYAMLDeckFile,
)

logger = logging.getLogger(__name__)


class YAMLProcessor:
    def __init__(self, config: YAMLProcessorConfig):
        self.config = config

    def process_file(
        self,
        file_path: Path,
    ) -> Tuple[List[Card], List[YAMLProcessingError]]:
        try:
            content = file_path.read_text(encoding="utf-8")
            raw_yaml_content = yaml.safe_load(content)
        except FileNotFoundError:
            raise YAMLProcessingError(file_path, "File not found.") from None
        except IOError as e:
            raise YAMLProcessingError(
                file_path,
                f"Could not read file: {e}",
            ) from e
        except yaml.YAMLError as e:
            raise YAMLProcessingError(
                file_path,
                f"Invalid YAML syntax: {e}",
            ) from e

        if not isinstance(raw_yaml_content, dict):
            raise YAMLProcessingError(
                file_path,
                "Top level of YAML must be a dictionary (deck object).",
            )

        try:
            deck_data = _RawYAMLDeckFile.model_validate(raw_yaml_content)
            deck_name = deck_data.deck
            deck_tags = set(deck_data.tags) if deck_data.tags else set()
            cards_list = [
                card.model_dump(exclude_none=True) for card in deck_data.cards
            ]
        except ValidationError as e:
            error_details = e.errors()[0]
            field = ".".join(map(str, error_details["loc"]))
            msg = error_details["msg"]
            error_message = f"Validation error in field '{field}': {msg}"
            raise YAMLProcessingError(file_path, error_message) from e

        file_context = _FileProcessingContext(
            file_path=file_path,
            assets_root_directory=self.config.assets_root_directory,
            deck_name=deck_name,
            deck_tags=deck_tags,
            skip_media_validation=self.config.skip_media_validation,
            skip_secrets_detection=self.config.skip_secrets_detection,
        )

        return self._process_raw_cards(cards_list, file_context)

    def _process_raw_cards(
        self,
        cards_list: List[Dict],
        file_context: _FileProcessingContext,
    ) -> Tuple[List[Card], List[YAMLProcessingError]]:
        cards_in_file: List[Card] = []
        errors_in_file: List[YAMLProcessingError] = []

        for idx, card_dict in enumerate(cards_list):
            result = self._process_single_raw_card(
                card_dict,
                idx,
                file_context,
            )
            if isinstance(result, Card):
                cards_in_file.append(result)
            else:
                errors_in_file.append(result)

        return cards_in_file, errors_in_file

    def _prepare_card_data(
        self,
        card_dict: Dict,
        file_context: _FileProcessingContext,
    ) -> Dict:
        card_data = card_dict.copy()

        if "id" in card_data:
            card_data["uuid"] = card_data.pop("id")

        card_data.pop("s", None)

        card_data["front"] = card_data.pop("q")
        card_data["back"] = card_data.pop("a")
        card_data["deck_name"] = file_context.deck_name
        card_data["source_yaml_file"] = file_context.file_path

        card_tags = set(card_data.get("tags", []))
        card_data["tags"] = file_context.deck_tags.union(card_tags)

        if card_data.get("state") is None:
            card_data.pop("state", None)

        return card_data

    def _process_single_raw_card(
        self,
        card_dict: Dict,
        idx: int,
        file_context: _FileProcessingContext,
    ) -> Union[Card, YAMLProcessingError]:
        if not isinstance(card_dict, dict):
            return YAMLProcessingError(
                message=f"Card entry at index {idx} is not a dictionary.",
                file_path=file_context.file_path,
                card_index=idx,
            )

        try:
            card_data = self._prepare_card_data(card_dict, file_context)
            card = Card(**card_data)
            return card
        except Exception as e:
            return YAMLProcessingError(
                message=f"Card validation failed: {e}",
                file_path=file_context.file_path,
                card_index=idx,
                card_question_snippet=card_dict.get("q", "")[:50],
            )


def _process_file_wrapper(
    processor: YAMLProcessor,
    file_path: Path,
    config: YAMLProcessorConfig,
    all_cards: List[Card],
    all_errors: List[YAMLProcessingError],
) -> None:
    try:
        cards, errors = processor.process_file(file_path)
        all_cards.extend(cards)
        all_errors.extend(errors)
        if config.fail_fast and errors:
            raise errors[0]
    except YAMLProcessingError as e:
        if config.fail_fast:
            raise e
        all_errors.append(e)
    except Exception as e:
        err = YAMLProcessingError(
            file_path=file_path,
            message=(
                "An unexpected error occurred while processing "
                f"{file_path.name}: {e}"
            ),
        )
        if config.fail_fast:
            raise err from e
        all_errors.append(err)


def load_and_process_flashcard_yamls(
    config: YAMLProcessorConfig,
) -> Tuple[List[Card], List[YAMLProcessingError]]:
    processor = YAMLProcessor(config)

    if not config.source_directory.exists():
        return [], [
            YAMLProcessingError(
                file_path=config.source_directory,
                message=(
                    "Source directory does not exist: "
                    f"{config.source_directory}"
                ),
            )
        ]

    if (
        not config.skip_media_validation
        and not config.assets_root_directory.exists()
    ):
        return [], [
            YAMLProcessingError(
                file_path=config.assets_root_directory,
                message=(
                    "Assets root directory does not exist: "
                    f"{config.assets_root_directory}"
                ),
            )
        ]

    yaml_files = sorted(list(config.source_directory.rglob("*.yaml")))
    yaml_files += sorted(list(config.source_directory.rglob("*.yml")))

    logger.info(
        "Found %s YAML files to process in %s",
        len(yaml_files),
        config.source_directory,
    )

    all_cards: List[Card] = []
    all_errors: List[YAMLProcessingError] = []

    for file_path in yaml_files:
        _process_file_wrapper(
            processor,
            file_path,
            config,
            all_cards,
            all_errors,
        )

    logger.info(
        "Successfully processed %s cards from %s files with %s errors.",
        len(all_cards),
        len(yaml_files),
        len(all_errors),
    )

    return all_cards, all_errors
