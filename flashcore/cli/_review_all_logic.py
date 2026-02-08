"""
Logic for reviewing all due cards across all decks.
"""

from datetime import datetime, date
from typing import Dict, List, Optional
from rich.console import Console

from pathlib import Path

from flashcore.cli.review_ui import _display_card, _get_user_rating
from flashcore.db.database import FlashcardDatabase
from flashcore.db.db_utils import db_row_to_card
from flashcore.scheduler import FSRS_Scheduler
from flashcore.review_processor import ReviewProcessor
from flashcore.models import Card

console = Console()


def review_all_logic(db_path: Path, limit: int = 50):
    """
    Run a unified review session for all cards due on the local date, up to a specified limit.
    
    Opens the flashcard database, fetches due cards across all decks, presents a per-deck summary, iterates through each due card to collect a user rating, submits each review, and prints per-card and session-level results.
    
    Parameters:
        db_path (Path): Filesystem path to the flashcard database file.
        limit (int): Maximum number of due cards to include in this review session.
    """
    with FlashcardDatabase(db_path=db_path) as db_manager:
        db_manager.initialize_schema()

        scheduler = FSRS_Scheduler()

        # Get all due cards across all decks
        today = date.today()  # Use local date for user-friendly scheduling
        all_due_cards = _get_all_due_cards(db_manager, today, limit)

        if not all_due_cards:
            console.print(
                "[bold yellow]No cards are due for review across any deck.[/bold yellow]"
            )
            console.print("[bold cyan]Review session finished.[/bold cyan]")
            return

        # Group cards by deck for display purposes
        deck_counts: Dict[str, int] = {}
        for card in all_due_cards:
            deck_counts[card.deck_name] = (
                deck_counts.get(card.deck_name, 0) + 1
            )

        # Show summary
        console.print(
            f"[bold green]Found {len(all_due_cards)} due cards across {len(deck_counts)} decks:[/bold green]"
        )
        for deck_name, count in deck_counts.items():
            console.print(f"  • [cyan]{deck_name}[/cyan]: {count} cards")
        console.print()

        # Create a unified review session by manually handling reviews
        reviewed_count = 0
        for card in all_due_cards:
            reviewed_count += 1

            # Display progress with deck context
            console.rule(
                f"[bold]Card {reviewed_count} of {len(all_due_cards)} • [cyan]{card.deck_name}[/cyan][/bold]"
            )

            resp_ms = _display_card(card)
            rating, eval_ms = _get_user_rating()

            # Submit the review directly using database and scheduler
            try:
                updated_card = _submit_single_review(
                    db_manager=db_manager,
                    scheduler=scheduler,
                    card=card,
                    rating=rating,
                    resp_ms=resp_ms,
                    eval_ms=eval_ms,
                )

                if updated_card and updated_card.next_due_date:
                    days_until_due = (
                        updated_card.next_due_date - date.today()
                    ).days
                    due_date_str = updated_card.next_due_date.strftime(
                        "%Y-%m-%d"
                    )
                    console.print(
                        f"[green]Reviewed.[/green] Next due in [bold]{days_until_due} days[/bold] on {due_date_str}."
                    )
                else:
                    console.print(
                        "[bold red]Error submitting review. Card will be reviewed again later.[/bold red]"
                    )
            except Exception as e:
                console.print(
                    f"[bold red]Error reviewing card: {e}[/bold red]"
                )

            console.print("")  # Add spacing

        console.print(
            f"[bold green]Review session complete! Reviewed {reviewed_count} cards.[/bold green]"
        )


def _get_all_due_cards(
    db_manager: FlashcardDatabase, on_date: date, limit: int
) -> List[Card]:
    """
    Retrieve due flashcards across all decks up to the specified limit.
    
    Cards are prioritized with never-reviewed cards first, then by oldest next-due date, grouped by deck, and finally by the card's added time.
    
    Parameters:
        db_manager (FlashcardDatabase): Database manager providing a connection to fetch cards.
        on_date (date): Date to test card due status (cards with next_due_date on or before this date are due; NULL counts as due).
        limit (int): Maximum number of cards to return.
    
    Returns:
        List[Card]: A list of due Card objects ordered by priority. Returns an empty list if no cards match or if an error occurs while fetching.
    """
    conn = db_manager.get_connection()

    sql = """
    SELECT * FROM cards
    WHERE next_due_date <= $1 OR next_due_date IS NULL
    ORDER BY
        next_due_date ASC NULLS FIRST,  -- Cards never reviewed first, then oldest due
        deck_name ASC,                  -- Group by deck for better UX
        added_at ASC                    -- Oldest cards within deck first
    LIMIT $2
    """

    try:
        result = conn.execute(sql, [on_date, limit])
        if result.description is None:
            return []
        cols = [desc[0] for desc in result.description]
        rows = result.fetchall()
        if not rows:
            return []

        cards = []
        for row in rows:
            row_dict = dict(zip(cols, row))
            card = db_row_to_card(row_dict)
            cards.append(card)

        return cards
    except Exception as e:
        console.print(f"[bold red]Error fetching due cards: {e}[/bold red]")
        return []


def _submit_single_review(
    db_manager: FlashcardDatabase,
    scheduler: FSRS_Scheduler,
    card: Card,
    rating: int,
    resp_ms: int = 0,
    eval_ms: int = 0,
    reviewed_at: Optional[datetime] = None,
) -> Optional[Card]:
    """
    Process and submit a single card review using the shared ReviewProcessor.
    
    Parameters:
        card (Card): The card being reviewed.
        rating (int): User's rating where 1=Again, 2=Hard, 3=Good, 4=Easy.
        resp_ms (int): Time in milliseconds to reveal the answer.
        eval_ms (int): Time in milliseconds to provide the rating.
        reviewed_at (Optional[datetime]): Timestamp of the review; if omitted, the processor will use the current time.
    
    Returns:
        Optional[Card]: The updated Card on success, or `None` if an error occurred.
    """
    try:
        # Use the shared review processor for consistent logic
        review_processor = ReviewProcessor(db_manager, scheduler)

        updated_card = review_processor.process_review(
            card=card,
            rating=rating,
            resp_ms=resp_ms,
            eval_ms=eval_ms,
            reviewed_at=reviewed_at,
            session_uuid=None,  # No session for review-all workflow
        )

        return updated_card

    except Exception as e:
        console.print(f"[bold red]Error submitting review: {e}[/bold red]")
        return None