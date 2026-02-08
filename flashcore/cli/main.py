"""
CLI entry point for flashcard system (cultivation-flashcards).
"""

# Standard library imports
from pathlib import Path
from typing import List, Optional, Tuple

# Third-party imports
import typer
from rich.console import Console
from rich.table import Table

# Local application imports
from ..config import settings
from ..database import FlashcardDatabase
from ..exceptions import DatabaseError, DeckNotFoundError
from ..card import Card
from ._export_logic import export_to_markdown
from ._review_logic import review_logic
from ._review_all_logic import review_all_logic
from ..db_utils import backup_database, find_latest_backup
import shutil
from ._vet_logic import vet_logic
from ..yaml_processing.yaml_processor import (
    YAMLProcessorConfig,
    load_and_process_flashcard_yamls,
)


console = Console()

app = typer.Typer(
    name="tm-fc",
    help="Flashcore: The Cultivation Project's Spaced Repetition System.",
    add_completion=False,
    rich_markup_mode="markdown",
)


def _normalize_for_comparison(text: str) -> str:
    """Normalizes text for comparison by lowercasing and stripping whitespace."""
    return text.lower().strip()


@app.command()
def vet(
    check: bool = typer.Option(
        False,
        "--check",
        help="Run in check-only mode without modifying files. Exits with 1 if changes are needed.",
    ),
    files: Optional[List[Path]] = typer.Argument(  # noqa: B008
        None,
        help="Optional list of files to process. If not provided, vets all files in the source directory.",
    ),
):
    """Validate, format, and add UUIDs to flashcard YAML files."""
    changes_needed = vet_logic(check=check, files_to_process=files)
    if check and changes_needed:
        # vet_logic already prints a message.
        raise typer.Exit(code=1)


def _load_cards_from_source() -> List[Card]:
    """Loads flashcards from YAML files and handles errors."""
    config = YAMLProcessorConfig(
        source_directory=settings.yaml_source_dir,
        assets_root_directory=settings.assets_dir,
    )
    yaml_cards, errors = load_and_process_flashcard_yamls(config)

    if errors:
        console.print("[bold red]Errors encountered during YAML processing:[/bold red]")
        for error in errors:
            console.print(f"- {error}")

    if not yaml_cards:
        if errors:
            # Errors were found, and no cards were loaded. Exit with an error.
            raise typer.Exit(code=1)
        else:
            # No errors, but no cards found. Graceful exit.
            console.print("[yellow]No flashcards found to ingest. Exiting.[/yellow]")
            raise typer.Exit(code=0)

    return yaml_cards


def _filter_new_cards(
    db: FlashcardDatabase, all_cards: List[Card]
) -> Tuple[List[Card], int]:
    """
    Filters out cards that already exist in the database or are duplicates within the batch.
    """
    all_fronts_and_uuids = db.get_all_card_fronts_and_uuids()
    existing_card_fronts = {
        _normalize_for_comparison(front) for front in all_fronts_and_uuids
    }

    cards_to_upsert: List[Card] = []
    # Use a set to track fronts from the current YAML batch to handle in-file duplicates
    processed_fronts = set()
    duplicate_count = 0

    for card in all_cards:
        normalized_front = _normalize_for_comparison(card.front)
        # A card is a duplicate if it's already in the DB or we've seen it in this batch
        if (
            normalized_front in existing_card_fronts
            or normalized_front in processed_fronts
        ):
            duplicate_count += 1
        else:
            cards_to_upsert.append(card)
            processed_fronts.add(normalized_front)

    return cards_to_upsert, duplicate_count


def _execute_ingestion(db: FlashcardDatabase, cards_to_upsert: List[Card]) -> int:
    """Upserts cards into the database and returns the count."""
    if not cards_to_upsert:
        console.print(
            "[green]All cards already exist in the database. No new cards to add.[/green]"
        )
        return 0
    return db.upsert_cards_batch(cards_to_upsert)


def _report_ingestion_summary(
    upserted_count: int, duplicate_count: int, re_ingest: bool
):
    """Prints a summary of the ingestion process."""
    console.print("[bold green]Ingestion complete![/bold green]")
    console.print(
        f"- [green]{upserted_count}[/green] cards were successfully ingested or updated."
    )
    if not re_ingest:
        console.print(f"- [yellow]{duplicate_count}[/yellow] duplicate cards were skipped.")


def _perform_ingestion_logic(re_ingest: bool):
    """Handles the core logic of loading, filtering, and upserting cards."""
    all_cards = _load_cards_from_source()

    with FlashcardDatabase() as db:
        cards_to_upsert: List[Card]
        duplicate_count = 0

        if re_ingest:
            # When re-ingesting, we want to update all cards from the source.
            # The de-duplication logic is handled by the `upsert`.
            cards_to_upsert = all_cards
        else:
            cards_to_upsert, duplicate_count = _filter_new_cards(db, all_cards)

        upserted_count = _execute_ingestion(db, cards_to_upsert)
        if upserted_count > 0 or duplicate_count > 0:
            _report_ingestion_summary(upserted_count, duplicate_count, re_ingest)


@app.command()
def ingest(
    re_ingest: bool = typer.Option(  # noqa: B008
        False, "--re-ingest", help="Force re-ingestion of all flashcards."
    ),
):
    """Ingest flashcards from YAML files into the database, preserving review history."""
    console.print(f"Starting ingestion from [cyan]{settings.yaml_source_dir}[/cyan]...")
    if re_ingest:
        console.print(
            "[yellow]--re-ingest flag is noted. Existing cards will be updated.[/yellow]"
        )

    try:
        _perform_ingestion_logic(re_ingest)
    except typer.Exit:
        raise
    except DatabaseError as e:
        console.print(f"[bold red]Database Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred during ingestion:[/bold red] {e}")
        raise typer.Exit(code=1) from e


def _display_overall_stats(console: Console, stats_data: dict):
    """Displays the overall stats table."""
    overall_table = Table(title="Overall Database Stats", show_header=False)
    overall_table.add_column("Metric", style="cyan")
    overall_table.add_column("Value", style="magenta")
    overall_table.add_row("Total Cards", str(stats_data["total_cards"]))
    overall_table.add_row("Total Reviews", str(stats_data["total_reviews"]))
    console.print(overall_table)


def _display_deck_stats(console: Console, stats_data: dict):
    """Displays the deck stats table."""
    decks_table = Table(title="Decks")
    decks_table.add_column("Deck Name", style="cyan")
    decks_table.add_column("Card Count", style="magenta")
    decks_table.add_column("Due Count", style="yellow")

    for deck in stats_data["decks"]:
        decks_table.add_row(
            deck["deck_name"], str(deck["card_count"]), str(deck["due_count"])
        )
    console.print(decks_table)


def _display_state_stats(console: Console, stats_data: dict):
    """Displays the card state stats table."""
    states_table = Table(title="Card States")
    states_table.add_column("State", style="cyan")
    states_table.add_column("Count", style="magenta")
    card_states = stats_data["states"]
    if not card_states:
        states_table.add_row("N/A", str(stats_data["total_cards"]))
    else:
        for state, count in sorted(card_states.items()):
            states_table.add_row(state, str(count))
    console.print(states_table)


@app.command()
def stats():
    """Display statistics about the flashcard database."""
    try:
        with FlashcardDatabase() as db:
            stats_data = db.get_database_stats()

            _display_overall_stats(console, stats_data)

            if not stats_data["total_cards"]:
                console.print("[yellow]No cards found in the database.[/yellow]")
                return

            _display_deck_stats(console, stats_data)
            _display_state_stats(console, stats_data)

    except DatabaseError as e:
        console.print(f"[bold]A database error occurred: {e}[/bold]")
        raise typer.Exit(code=1) from e
    except Exception as e:
        console.print(
            f"[bold]An unexpected error occurred while fetching stats: {e}[/bold]"
        )
        raise typer.Exit(code=1) from e


@app.command()
def review(
    deck_name: str = typer.Argument(..., help="The name of the deck to review."),  # noqa: B008
    tags: Optional[List[str]] = typer.Option(None, "--tags", help="Filter cards by tags (comma-separated)"),  # noqa: B008
):
    """Starts a review session for the specified deck."""
    try:
        backup_path = backup_database(settings.db_path)
        if backup_path.exists() and "backups" in str(backup_path):
            console.print(f"Database successfully backed up to: [dim]{backup_path}[/dim]")

        if tags:
            console.print(f"Starting review for deck: [bold cyan]{deck_name}[/bold cyan] with tags: [bold yellow]{', '.join(tags)}[/bold yellow]")
        else:
            console.print(f"Starting review for deck: [bold cyan]{deck_name}[/bold cyan]")
        review_logic(deck_name=deck_name, tags=tags)
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
    limit: int = typer.Option(
        50, "--limit", "-l", help="Maximum number of cards to review across all decks."
    ),
):
    """Starts a review session for all due cards across all decks."""
    try:
        backup_path = backup_database(settings.db_path)
        if backup_path.exists() and "backups" in str(backup_path):
            console.print(f"Database successfully backed up to: [dim]{backup_path}[/dim]")

        console.print(
            "[bold cyan]Starting review session for all due cards...[/bold cyan]"
        )
        review_all_logic(limit=limit)
    except DatabaseError as e:
        console.print(f"[bold]A database error occurred: {e}[/bold]")
        raise typer.Exit(code=1) from e
    except Exception as e:
        console.print(f"[bold]An unexpected error occurred:[/bold] {e}")
        raise typer.Exit(code=1) from e


# Create a subcommand group for 'export'
export_app = typer.Typer(name="export", help="Export flashcards to different formats.")
app.add_typer(export_app)


@export_app.command("anki")
def export_anki():
    """Export flashcards to an Anki deck (Not implemented)."""
    console.print(
        "[yellow]Export to Anki is not yet implemented. This is a placeholder.[/yellow]"
    )


@export_app.command("md")
def export_md(
    output_dir: Optional[Path] = typer.Option(  # noqa: B008
        None,
        "--output-dir",
        help="Directory to save exported Markdown files. Defaults to settings.export_dir",
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True,
    ),
):
    """Export flashcards to Markdown files, one file per deck."""
    final_output_dir = output_dir or settings.export_dir
    console.print(f"Exporting flashcards to [cyan]{final_output_dir}[/cyan]...")
    try:
        with FlashcardDatabase() as db:
            export_to_markdown(db=db, output_dir=final_output_dir)
    except (DatabaseError, IOError) as e:
        console.print(f"[bold]An error occurred during export: {e}[/bold]")
        raise typer.Exit(code=1) from e


@app.command()
def restore(
    yes: bool = typer.Option(False, "--yes", "-y", help="Bypass confirmation prompt.")
):
    """
    Restores the database from the most recent backup.
    """
    console.print("[bold yellow]Attempting to restore database from backup...[/bold yellow]")

    latest_backup = find_latest_backup(settings.db_path)

    if not latest_backup:
        console.print("[bold red]Error: No backup files found.[/bold red]")
        raise typer.Exit(code=1)

    console.print(f"Found latest backup: [cyan]{latest_backup.name}[/cyan]")

    if not yes:
        confirmed = typer.confirm(
            "Are you sure you want to overwrite the current database with this backup?"
        )
        if not confirmed:
            console.print("Restore operation cancelled.")
            raise typer.Exit()

    try:
        shutil.copy2(latest_backup, settings.db_path)
        console.print(
            f"[bold green]✅ Database successfully restored from {latest_backup.name}[/bold green]"
        )
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred during restore: {e}[/bold red]")
        raise typer.Exit(code=1) from e


def main():
    try:
        app()
    except Exception as e:
        console.print(f"[bold red]UNEXPECTED ERROR: {e}[/bold red]")


if __name__ == "__main__":
    main()
