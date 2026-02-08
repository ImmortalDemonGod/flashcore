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
    """Normalizes text for comparison by lowercasing and stripping whitespace."""
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
    """Validate, format, and add UUIDs to flashcard YAML files."""
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
    """Loads flashcards from YAML files and handles errors."""
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
    Filters out cards that already exist in the database
    or are duplicates within the batch.
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
    """Upserts cards into the database and returns the count."""
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
    """Prints a summary of the ingestion process."""
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
    """Handles the core logic of loading, filtering, and upserting cards."""
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
    """Ingest flashcards from YAML files into the database."""
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
    """Displays the overall stats table."""
    overall_table = Table(title="Overall Database Stats", show_header=False)
    overall_table.add_column("Metric", style="cyan")
    overall_table.add_column("Value", style="magenta")
    overall_table.add_row("Total Cards", str(stats_data["total_cards"]))
    overall_table.add_row("Total Reviews", str(stats_data["total_reviews"]))
    cons.print(overall_table)


def _display_deck_stats(cons: Console, stats_data: dict):
    """Displays the deck stats table."""
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
    """Export flashcards to Markdown files, one file per deck."""
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
    try:
        app()
    except Exception as e:
        console.print(f"[bold red]UNEXPECTED ERROR: {e}[/bold red]")


if __name__ == "__main__":
    main()
