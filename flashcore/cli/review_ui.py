"""
Command-line interface for reviewing flashcards.
"""

import logging
import time
from datetime import date
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel

from flashcore.models import Card
from flashcore.review_manager import ReviewSessionManager

logger = logging.getLogger(__name__)
console = Console()


def _get_user_rating() -> tuple[int, int]:
    """
    Prompt the user to enter a review rating (1–4) and measure how long they took to provide it.

    Repeatedly prompts until a valid integer in the range 1 to 4 is entered. The elapsed time is measured from the first prompt until a valid response is received.

    Returns:
        tuple[int, int]: (rating, eval_ms) where `rating` is an integer 1–4 and `eval_ms` is the elapsed time in milliseconds between the first prompt and the accepted input.
    """
    start_time = time.time()
    while True:
        try:
            rating_str = console.input(
                "[bold]Rating (1:Again, 2:Hard, 3:Good, 4:Easy): [/bold]"
            )
            rating = int(rating_str)
            if 1 <= rating <= 4:
                end_time = time.time()
                eval_ms = int((end_time - start_time) * 1000)
                return rating, eval_ms
            else:
                console.print(
                    "[bold red]Invalid rating. Please enter a number between 1 and 4.[/bold red]"
                )
        except (ValueError, TypeError):
            console.print(
                "[bold red]Invalid input. Please enter a number.[/bold red]"
            )


def _display_card(card: Card) -> int:
    """
    Show a card's front, wait for the user to press Enter, then reveal the back.

    Parameters:
        card (Card): Card object with `front` and `back` attributes to display.

    Returns:
        response_time_ms (int): Milliseconds elapsed between showing the front and the user pressing Enter.
    """
    console.print(Panel(card.front, title="Front", border_style="green"))
    start_time = time.time()
    console.input("[italic]Press Enter to see the back...[/italic]")
    end_time = time.time()
    console.print(Panel(card.back, title="Back", border_style="blue"))
    return int((end_time - start_time) * 1000)


def start_review_flow(
    manager: ReviewSessionManager, tags: Optional[List[str]] = None
) -> None:
    """
    Manages the command-line review session flow.

    Args:
        manager: An instance of ReviewSessionManager.
        tags: Optional list of tags to filter cards by.
    """
    console.print("[bold cyan]Starting review session...[/bold cyan]")
    manager.initialize_session(tags=tags)

    due_cards_count = len(manager.review_queue)
    if due_cards_count == 0:
        console.print(
            "[bold yellow]No cards are due for review.[/bold yellow]"
        )
        console.print("[bold cyan]Review session finished.[/bold cyan]")
        return

    reviewed_count = 0
    while (card := manager.get_next_card()) is not None:
        reviewed_count += 1
        console.rule(
            f"[bold]Card {reviewed_count} of {due_cards_count}[/bold]"
        )

        resp_ms = _display_card(card)
        rating, eval_ms = _get_user_rating()

        try:
            updated_card = manager.submit_review(
                card_uuid=card.uuid,
                rating=rating,
                resp_ms=resp_ms,
                eval_ms=eval_ms,
            )
        except Exception as e:
            logger.error(f"Failed to submit review for {card.uuid}: {e}")
            console.print(
                "[bold red]Error submitting review. Card will be reviewed again later.[/bold red]"
            )
            continue

        if updated_card and updated_card.next_due_date:
            days_until_due = (updated_card.next_due_date - date.today()).days
            due_date_str = updated_card.next_due_date.strftime("%Y-%m-%d")
            console.print(
                f"[green]Reviewed.[/green] Next due in [bold]{days_until_due} days[/bold] on {due_date_str}."
            )
        elif updated_card:
            console.print("[green]Reviewed.[/green]")
        else:
            console.print(
                "[bold red]Error submitting review. Card will be reviewed again later.[/bold red]"
            )
        console.print("")  # Add a blank line for spacing

    console.print("[bold cyan]Review session finished. Well done![/bold cyan]")
