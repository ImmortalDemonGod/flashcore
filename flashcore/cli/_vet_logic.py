"""
Logic for the 'vet' subcommand, which validates and cleans flashcard YAML files.
"""
import uuid
import copy
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pydantic import ValidationError
from rich.console import Console
from ruamel.yaml import YAML

from cultivation.scripts.flashcore.card import Card
from cultivation.scripts.flashcore.config import settings


console = Console()
yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.preserve_quotes = True


def yaml_to_string(data: Dict[str, Any]) -> str:
    """Dumps YAML data to a string."""
    string_stream = StringIO()
    yaml.dump(data, string_stream)
    return string_stream.getvalue()


def _validate_and_normalize_card(
    raw_card_dict: Dict[str, Any], deck_name: str
) -> Dict[str, Any]:
    """
    Validates a single card, adds a UUID if missing, and normalizes its structure.
    Raises ValidationError or TypeError on failure.
    """
    # 1. Create a mutable copy and map front/back aliases
    mapped_card_dict = raw_card_dict.copy()
    if "q" in mapped_card_dict:
        mapped_card_dict["front"] = mapped_card_dict.pop("q")
    if "a" in mapped_card_dict:
        mapped_card_dict["back"] = mapped_card_dict.pop("a")

    # 2. Remove empty UUIDs so Pydantic can generate a new one
    if "uuid" in mapped_card_dict and not mapped_card_dict["uuid"]:
        mapped_card_dict.pop("uuid")

    # 2.5. Convert string UUID to UUID object if present
    if "uuid" in mapped_card_dict and isinstance(mapped_card_dict["uuid"], str):
        try:
            mapped_card_dict["uuid"] = uuid.UUID(mapped_card_dict["uuid"])
        except ValueError:
            # Invalid UUID format, remove it so Pydantic can generate a new one
            mapped_card_dict.pop("uuid")

    # 3. Validate with the Pydantic model
    card_obj = Card(**mapped_card_dict, deck_name=deck_name)

    # 4. Prepare the dictionary for writing back to YAML
    card_to_write_raw = raw_card_dict.copy()
    card_to_write_raw["uuid"] = str(card_obj.uuid)

    # 5. Sort keys for consistent output
    card_to_write_sorted = dict(
        sorted(
            {
                k: str(v) if isinstance(v, uuid.UUID) else v
                for k, v in card_to_write_raw.items()
            }.items()
        )
    )
    return card_to_write_sorted


def _validate_and_process_cards(
    raw_cards: List[Dict[str, Any]], deck_name: str, file_path: Path
) -> Tuple[List[Dict[str, Any]], bool]:
    """
    Validates and processes a list of cards, returning vetted cards and an error flag.
    """
    vetted_cards = []
    validation_error_found = False
    for i, raw_card_dict in enumerate(raw_cards):
        try:
            processed_card = _validate_and_normalize_card(raw_card_dict, deck_name)
            vetted_cards.append(processed_card)
        except (ValidationError, TypeError) as e:
            console.print(
                f"[bold red]Validation error in {file_path.name} at card index {i}:[/bold red]"
            )
            # Handle Pydantic's ValidationError structure
            if hasattr(e, "errors"):
                for error in e.errors():
                    loc = " -> ".join(map(str, error["loc"]))
                    console.print(f"  - Field `{loc}`: {error['msg']}")
            else:
                # Handle other errors like TypeError
                console.print(f"  - {e}")
            validation_error_found = True
    return vetted_cards, validation_error_found


def _sort_and_format_data(data: Dict[str, Any]) -> str:
    """Sorts cards and top-level keys, and returns the formatted YAML string."""
    def normalize_front(card: Dict[str, Any]) -> str:
        # Handle both 'q' and 'front' for robustness during sorting
        return " ".join(str(card.get("q", card.get("front", ""))).lower().split())

    if "cards" in data:
        data["cards"].sort(key=normalize_front)

    sorted_data = dict(sorted(data.items()))
    return yaml_to_string(sorted_data)


def _process_single_file(file_path: Path, check: bool) -> Tuple[bool, bool]:
    """
    Processes a single YAML file: validates, cleans, adds UUIDs, and sorts.
    Returns a tuple of (is_dirty, has_errors).
    """
    try:
        original_content = file_path.read_text(encoding="utf-8")
        data = yaml.load(original_content)

        if not isinstance(data, dict) or "cards" not in data:
            console.print(f"[yellow]Skipping {file_path.name}: Invalid format.[/yellow]")
            return False, False

        deck_name = data.get("deck", "Default Deck")

        vetted_cards, validation_error_found = _validate_and_process_cards(
            data.get("cards", []),
            deck_name,
            file_path
        )

        if validation_error_found:
            return False, True

        modified_data = copy.deepcopy(data)
        modified_data["cards"] = vetted_cards
        new_content = _sort_and_format_data(modified_data)

        made_change = original_content != new_content

        if made_change and not check:
            file_path.write_text(new_content, encoding="utf-8")


        return made_change, validation_error_found

    except Exception as e:
        console.print(f"[bold red]Error processing {file_path.name}: {e}[/bold red]")
        return False, True


def _report_vet_summary(any_dirty: bool, any_errors: bool, check: bool) -> None:
    """Prints a final summary message after vetting all files."""
    if any_errors:
        console.print(
            "[bold red]Vetting complete. Some files have validation errors.[/bold red]"
        )
        return

    if check:
        if any_dirty:
            console.print(
                "[bold yellow]Check failed: Some files need changes. Run without --check to fix.[/bold yellow]"
            )
        else:
            console.print(
                "[bold green]All files are clean. No changes needed.[/bold green]"
            )
    else:
        if any_dirty:
            console.print(
                "[bold yellow]✓ Vetting complete. Some files were modified.[/bold yellow]"
            )
        else:
            console.print(
                "[bold green]All files are clean. No changes needed.[/bold green]"
            )


def vet_logic(check: bool, files_to_process: Optional[List[Path]] = None) -> bool:
    """
    Main logic for the 'vet' command.
    Validates, formats, sorts, and adds UUIDs to flashcard YAML files.
    """
    if files_to_process is None:
        source_dir = Path(settings.yaml_source_dir)
        files = sorted(
            list(source_dir.glob("*.yml")) + list(source_dir.glob("*.yaml"))
        )
    else:
        files = [p for p in files_to_process if p.suffix in (".yaml", ".yml")]

    if not files:
        console.print("[bold yellow]No YAML files found to vet.[/bold yellow]")
        return False

    console.print(f"Vetting {len(files)} YAML file(s)...")

    any_dirty = False
    any_errors = False

    for file_path in files:
        is_dirty, has_errors = _process_single_file(file_path, check=check)
        if has_errors:
            any_errors = True
            continue
        if is_dirty:
            any_dirty = True
            if check:
                console.print(f"[yellow]! Dirty: {file_path.name}[/yellow]")
            else:
                console.print(f"[green]File formatted successfully: {file_path.name}[/green]")

    _report_vet_summary(any_dirty, any_errors, check)

    return any_dirty or any_errors
