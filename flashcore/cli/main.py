"""
CLI entry point for flashcore.
"""

# Standard library imports
import os
import shutil
from pathlib import Path
from typing import List, Optional, Tuple
from uuid import uuid4

# Third-party imports
import typer
from rich.console import Console
from rich.table import Table

# Local application imports
from flashcore.db.database import FlashcardDatabase
from flashcore.db.db_utils import backup_database, find_latest_backup
from flashcore.exceptions import DatabaseError, DeckNotFoundError
from flashcore.models import Card
from flashcore.parser import (
    YAMLProcessorConfig,
    load_and_process_flashcard_yamls,
)
from flashcore.cli._export_logic import export_to_markdown
from flashcore.cli._review_logic import review_logic
from flashcore.cli._review_all_logic import review_all_logic
from flashcore.cli._vet_logic import vet_logic


console = Console()

app = typer.Typer(
    name="flashcore",
    help="Flashcore: Lightweight Spaced Repetition System.",
    add_completion=False,
    rich_markup_mode="markdown",
)


# ---------------------------------------------------------------------------
# Helpers for resolving the --db path (DI: no defaults, FLASHCORE_DB envvar)
# ---------------------------------------------------------------------------


def _resolve_db_path(db: Optional[Path]) -> Path:
    """Resolve db path from CLI flag or FLASHCORE_DB envvar. Exits on missing."""
    if db is not None:
        return db
    env_val = os.environ.get("FLASHCORE_DB")
    if env_val:
        return Path(env_val)
    console.print(
        "[bold red]Error: --db is required "
        "(or set the FLASHCORE_DB environment variable).[/bold red]"
    )
    raise typer.Exit(code=1)


# Common typer options reused across commands
_db_option = typer.Option(  # noqa: B008
    None,
    "--db",
    help="Path to the DuckDB database file. "
    "Falls back to FLASHCORE_DB env var.",
    envvar="FLASHCORE_DB",
)

_source_dir_option = typer.Option(  # noqa: B008
    None,
    "--source-dir",
    help="Directory containing YAML flashcard files.",
)

_assets_root_option = typer.Option(  # noqa: B008
    None,
    "--assets-root",
    help="Root directory for media assets referenced in YAML files.",
)


def _normalize_for_comparison(text: str) -> str:
    """
    Normalize text for comparison by converting to lowercase and removing leading and trailing whitespace.

    Returns:
        normalized_text (str): The input text converted to lowercase with surrounding whitespace removed.
    """
    return text.lower().strip()


# ---------------------------------------------------------------------------
# Vet
# ---------------------------------------------------------------------------


@app.command()
def vet(
    check: bool = typer.Option(
        False,
        "--check",
        help="Run in check-only mode without modifying files. "
        "Exits with 1 if changes are needed.",
    ),
    source_dir: Optional[Path] = _source_dir_option,
    files: Optional[List[Path]] = typer.Argument(  # noqa: B008
        None,
        help="Optional list of files to process. "
        "If not provided, vets all files in --source-dir.",
    ),
):
    """
    Validate, format, and ensure each flashcard YAML file contains a UUID.

    Performs validation and formatting of flashcard YAML files and adds missing UUIDs. When `check` is True the function runs a dry run and does not modify files; it will cause the CLI to exit with code 1 if any changes would be required.

    Parameters:
        check: If True, perform a non-destructive check-only run (no file writes).
        source_dir: Optional path containing flashcard YAML files to process.
        files: Optional list of specific file paths to process. If omitted, all files under `source_dir` are processed.
    """
    changes_needed = vet_logic(
        check=check,
        files_to_process=files,
        source_dir=source_dir,
    )
    if check and changes_needed:
        raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# Ingest helpers
# ---------------------------------------------------------------------------


def _load_cards_from_source(
    source_dir: Path,
    assets_root: Optional[Path],
) -> List[Card]:
    """
    Load flashcards from YAML files in source_dir and return the resulting Card objects.

    Parameters:
        source_dir (Path): Directory containing flashcard YAML files to process.
        assets_root (Optional[Path]): Root directory for asset resolution; if None, source_dir is used.

    Behavior:
        - Prints any processing errors to the console.
        - If no cards are produced and there were processing errors, exits with code 1.
        - If no cards are produced and there were no errors, prints a notice and exits with code 0.

    Returns:
        List[Card]: Processed Card objects loaded from the YAML files.
    """
    config = YAMLProcessorConfig(
        source_directory=source_dir,
        assets_root_directory=assets_root or source_dir,
    )
    yaml_cards, errors = load_and_process_flashcard_yamls(config)

    if errors:
        console.print(
            "[bold red]Errors encountered during YAML processing:[/bold red]"
        )
        for error in errors:
            console.print(f"- {error}")

    if not yaml_cards:
        if errors:
            raise typer.Exit(code=1)
        else:
            console.print(
                "[yellow]No flashcards found to ingest. Exiting.[/yellow]"
            )
            raise typer.Exit(code=0)

    return yaml_cards


def _filter_new_cards(
    db: FlashcardDatabase, all_cards: List[Card]
) -> Tuple[List[Card], int]:
    """
    Selects cards that should be inserted or updated by removing any whose fronts duplicate an existing database card or an earlier card in the provided batch.

    Returns:
        tuple: (cards_to_upsert, duplicate_count) where `cards_to_upsert` is a list of Card objects kept for upsert and `duplicate_count` is the number of cards skipped because their front was a duplicate.
    """
    all_fronts_and_uuids = db.get_all_card_fronts_and_uuids()
    existing_card_fronts = {
        _normalize_for_comparison(front) for front in all_fronts_and_uuids
    }

    cards_to_upsert: List[Card] = []
    processed_fronts: set = set()
    duplicate_count = 0

    for card in all_cards:
        normalized_front = _normalize_for_comparison(card.front)
        if (
            normalized_front in existing_card_fronts
            or normalized_front in processed_fronts
        ):
            duplicate_count += 1
        else:
            cards_to_upsert.append(card)
            processed_fronts.add(normalized_front)

    return cards_to_upsert, duplicate_count


def _execute_ingestion(
    db: FlashcardDatabase, cards_to_upsert: List[Card]
) -> int:
    """
    Upsert a batch of cards into the provided flashcard database.

    If `cards_to_upsert` is empty, prints a notice and returns 0.

    Returns:
        int: Number of cards inserted or updated; `0` if no cards were provided.
    """
    if not cards_to_upsert:
        console.print(
            "[green]All cards already exist in the database. "
            "No new cards to add.[/green]"
        )
        return 0
    return db.upsert_cards_batch(cards_to_upsert)


def _report_ingestion_summary(
    upserted_count: int, duplicate_count: int, re_ingest: bool
):
    """
    Print a concise summary of ingestion results to the console.

    Parameters:
        upserted_count (int): Number of cards that were inserted or updated.
        duplicate_count (int): Number of cards skipped because they were detected as duplicates.
        re_ingest (bool): When True, indicates existing cards were intentionally re-ingested and duplicate_count is not reported.
    """
    console.print("[bold green]Ingestion complete![/bold green]")
    console.print(
        f"- [green]{upserted_count}[/green] cards were "
        "successfully ingested or updated."
    )
    if not re_ingest:
        console.print(
            f"- [yellow]{duplicate_count}[/yellow] "
            "duplicate cards were skipped."
        )


def _perform_ingestion_logic(
    db_path: Path,
    source_dir: Path,
    assets_root: Optional[Path],
    re_ingest: bool,
):
    """
    Orchestrates loading flashcards from the source directory, selecting which cards should be upserted, performing the upsert into the database, and reporting a summary.

    Parameters:
        db_path (Path): Path to the flashcard database file to open for upserting.
        source_dir (Path): Directory containing source YAML flashcard files to load.
        assets_root (Optional[Path]): Root directory to resolve asset references; if None, the source directory is used.
        re_ingest (bool): If True, force upserting all loaded cards (update existing cards). If False, only new or non-duplicate cards are upserted.

    Side effects:
        Opens and modifies the database, may print ingestion summary and error messages via the CLI output.
    """
    all_cards = _load_cards_from_source(source_dir, assets_root)

    with FlashcardDatabase(db_path=db_path) as db:
        cards_to_upsert: List[Card]
        duplicate_count = 0

        if re_ingest:
            cards_to_upsert = all_cards
        else:
            cards_to_upsert, duplicate_count = _filter_new_cards(db, all_cards)

        upserted_count = _execute_ingestion(db, cards_to_upsert)
        if upserted_count > 0 or duplicate_count > 0:
            _report_ingestion_summary(
                upserted_count, duplicate_count, re_ingest
            )


# ---------------------------------------------------------------------------
# Ingest command
# ---------------------------------------------------------------------------


@app.command()
def ingest(
    db: Optional[Path] = _db_option,
    source_dir: Optional[Path] = _source_dir_option,
    assets_root: Optional[Path] = _assets_root_option,
    re_ingest: bool = typer.Option(  # noqa: B008
        False,
        "--re-ingest",
        help="Force re-ingestion of all flashcards.",
    ),
):
    """
    Ingest flashcards defined in YAML files from a source directory into the configured database.

    Parameters:
        db (Optional[Path]): Path to the database file; resolved from the value or the FLASHCORE_DB environment variable.
        source_dir (Optional[Path]): Directory containing YAML flashcard files to ingest; required.
        assets_root (Optional[Path]): Root directory for card assets; defaults to `source_dir` when not provided.
        re_ingest (bool): If True, force re-ingestion and update existing cards.

    Raises:
        typer.Exit: Raised with a non-zero exit code when required inputs are missing or when an error occurs during ingestion.
    """
    db_path = _resolve_db_path(db)
    if source_dir is None:
        console.print(
            "[bold red]Error: --source-dir is required "
            "for ingestion.[/bold red]"
        )
        raise typer.Exit(code=1)

    console.print(f"Starting ingestion from [cyan]{source_dir}[/cyan]...")
    if re_ingest:
        console.print(
            "[yellow]--re-ingest flag is noted. "
            "Existing cards will be updated.[/yellow]"
        )

    try:
        _perform_ingestion_logic(db_path, source_dir, assets_root, re_ingest)
    except typer.Exit:
        raise
    except DatabaseError as e:
        console.print(f"[bold red]Database Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(
            "[bold red]An unexpected error occurred "
            f"during ingestion:[/bold red] {e}"
        )
        raise typer.Exit(code=1) from e


# ---------------------------------------------------------------------------
# Stats helpers & command
# ---------------------------------------------------------------------------


def _display_overall_stats(cons: Console, stats_data: dict):
    """
    Prints a two-row table summarizing the database's total cards and total reviews.

    Parameters:
        stats_data (dict): Mapping containing at least the keys
            `"total_cards"` and `"total_reviews"` with numeric values
            to display.
    """
    overall_table = Table(title="Overall Database Stats", show_header=False)
    overall_table.add_column("Metric", style="cyan")
    overall_table.add_column("Value", style="magenta")
    overall_table.add_row("Total Cards", str(stats_data["total_cards"]))
    overall_table.add_row("Total Reviews", str(stats_data["total_reviews"]))
    cons.print(overall_table)


def _display_deck_stats(cons: Console, stats_data: dict):
    """
    Render and print a table of per-deck statistics to the given console.

    Parameters:
        cons (Console): Rich Console used to print the table.
        stats_data (dict): Mapping containing a "decks" key with an iterable of deck records.
            Each deck record must provide "deck_name", "card_count", and "due_count".
    """
    decks_table = Table(title="Decks")
    decks_table.add_column("Deck Name", style="cyan")
    decks_table.add_column("Card Count", style="magenta")
    decks_table.add_column("Due Count", style="yellow")

    for deck in stats_data["decks"]:
        decks_table.add_row(
            deck["deck_name"],
            str(deck["card_count"]),
            str(deck["due_count"]),
        )
    cons.print(decks_table)


def _display_state_stats(cons: Console, stats_data: dict):
    """
    Render a table summarizing card counts grouped by state.

    Parameters:
        cons (Console): Rich Console used to print the table.
        stats_data (dict): Statistics mapping containing:
            - "states" (Mapping[str, int]): Mapping of state names to their counts.
            - "total_cards" (int): Total number of cards; used when "states" is empty.
    """
    states_table = Table(title="Card States")
    states_table.add_column("State", style="cyan")
    states_table.add_column("Count", style="magenta")
    card_states = stats_data["states"]
    if not card_states:
        states_table.add_row("N/A", str(stats_data["total_cards"]))
    else:
        for state, count in sorted(card_states.items()):
            states_table.add_row(state, str(count))
    cons.print(states_table)


@app.command()
def stats(
    db: Optional[Path] = _db_option,
):
    """Display statistics about the flashcard database."""
    db_path = _resolve_db_path(db)
    try:
        with FlashcardDatabase(db_path=db_path) as db_inst:
            stats_data = db_inst.get_database_stats()

            _display_overall_stats(console, stats_data)

            if not stats_data["total_cards"]:
                console.print(
                    "[yellow]No cards found in the database.[/yellow]"
                )
                return

            _display_deck_stats(console, stats_data)
            _display_state_stats(console, stats_data)

    except DatabaseError as e:
        console.print(f"[bold]A database error occurred: {e}[/bold]")
        raise typer.Exit(code=1) from e
    except Exception as e:
        console.print(
            "[bold]An unexpected error occurred "
            f"while fetching stats: {e}[/bold]"
        )
        raise typer.Exit(code=1) from e


# ---------------------------------------------------------------------------
# Review commands
# ---------------------------------------------------------------------------


@app.command()
def review(
    deck_name: str = typer.Argument(  # noqa: B008
        ..., help="The name of the deck to review."
    ),
    db: Optional[Path] = _db_option,
    tags: Optional[List[str]] = typer.Option(  # noqa: B008
        None,
        "--tags",
        help="Filter cards by tags (comma-separated)",
    ),
):
    """Starts a review session for the specified deck."""
    db_path = _resolve_db_path(db)
    try:
        backup_path = backup_database(db_path)
        if backup_path.exists() and "backups" in str(backup_path):
            console.print(f"Database backed up to: [dim]{backup_path}[/dim]")

        if tags:
            console.print(
                f"Starting review for deck: "
                f"[bold cyan]{deck_name}[/bold cyan] "
                f"with tags: [bold yellow]"
                f"{', '.join(tags)}[/bold yellow]"
            )
        else:
            console.print(
                f"Starting review for deck: "
                f"[bold cyan]{deck_name}[/bold cyan]"
            )
        review_logic(
            deck_name=deck_name,
            db_path=db_path,
            user_uuid=uuid4(),
            tags=tags,
        )
    except DeckNotFoundError as e:
        console.print(f"[bold]Error: {e}[/bold]")
        raise typer.Exit(code=1) from e
    except DatabaseError as e:
        console.print(f"[bold]A database error occurred: {e}[/bold]")
        raise typer.Exit(code=1) from e
    except Exception as e:
        console.print(f"[bold]An unexpected error occurred:[/bold] {e}")
        raise typer.Exit(code=1) from e


@app.command()
def review_all(
    db: Optional[Path] = _db_option,
    limit: int = typer.Option(
        50,
        "--limit",
        "-l",
        help="Maximum number of cards to review across all decks.",
    ),
):
    """Starts a review session for all due cards across all decks."""
    db_path = _resolve_db_path(db)
    try:
        backup_path = backup_database(db_path)
        if backup_path.exists() and "backups" in str(backup_path):
            console.print(f"Database backed up to: [dim]{backup_path}[/dim]")

        console.print(
            "[bold cyan]Starting review session "
            "for all due cards...[/bold cyan]"
        )
        review_all_logic(db_path=db_path, limit=limit)
    except DatabaseError as e:
        console.print(f"[bold]A database error occurred: {e}[/bold]")
        raise typer.Exit(code=1) from e
    except Exception as e:
        console.print(f"[bold]An unexpected error occurred:[/bold] {e}")
        raise typer.Exit(code=1) from e


# ---------------------------------------------------------------------------
# Export subcommand group
# ---------------------------------------------------------------------------

export_app = typer.Typer(
    name="export",
    help="Export flashcards to different formats.",
)
app.add_typer(export_app)


@export_app.command("anki")
def export_anki():
    """Export flashcards to an Anki deck (Not implemented)."""
    console.print(
        "[yellow]Export to Anki is not yet implemented. "
        "This is a placeholder.[/yellow]"
    )


@export_app.command("md")
def export_md(
    db: Optional[Path] = _db_option,
    output_dir: Optional[Path] = typer.Option(  # noqa: B008
        None,
        "--output-dir",
        help="Directory to save exported Markdown files.",
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True,
    ),
):
    """
    Export flashcards into Markdown files, creating one Markdown file per deck in the given directory.

    Parameters:
        output_dir (Path): Directory where per-deck Markdown
            files will be written; required.
    """
    db_path = _resolve_db_path(db)
    if output_dir is None:
        console.print(
            "[bold red]Error: --output-dir is required "
            "for Markdown export.[/bold red]"
        )
        raise typer.Exit(code=1)
    console.print(f"Exporting flashcards to [cyan]{output_dir}[/cyan]...")
    try:
        with FlashcardDatabase(db_path=db_path) as db_inst:
            export_to_markdown(db=db_inst, output_dir=output_dir)
    except (DatabaseError, IOError) as e:
        console.print(f"[bold]An error occurred during export: {e}[/bold]")
        raise typer.Exit(code=1) from e


# ---------------------------------------------------------------------------
# Restore command
# ---------------------------------------------------------------------------


@app.command()
def restore(
    db: Optional[Path] = _db_option,
    yes: bool = typer.Option(
        False, "--yes", "-y", help="Bypass confirmation prompt."
    ),
):
    """Restores the database from the most recent backup."""
    db_path = _resolve_db_path(db)
    console.print(
        "[bold yellow]Attempting to restore database "
        "from backup...[/bold yellow]"
    )

    latest_backup = find_latest_backup(db_path)

    if not latest_backup:
        console.print("[bold red]Error: No backup files found.[/bold red]")
        raise typer.Exit(code=1)

    console.print(f"Found latest backup: [cyan]{latest_backup.name}[/cyan]")

    if not yes:
        confirmed = typer.confirm(
            "Are you sure you want to overwrite the current "
            "database with this backup?"
        )
        if not confirmed:
            console.print("Restore operation cancelled.")
            raise typer.Exit()

    try:
        shutil.copy2(latest_backup, db_path)
        console.print(
            "[bold green]Database successfully restored "
            f"from {latest_backup.name}[/bold green]"
        )
    except Exception as e:
        console.print(
            "[bold red]An unexpected error occurred "
            f"during restore: {e}[/bold red]"
        )
        raise typer.Exit(code=1) from e


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    """
    Run the CLI application.

    If an unexpected exception occurs, print a bold red error message to the console and exit the process with status code 1.
    """
    try:
        app()
    except Exception as e:
        console.print(f"[bold red]UNEXPECTED ERROR: {e}[/bold red]")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
