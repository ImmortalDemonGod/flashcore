"""
Contains the business logic for exporting flashcards to various formats.
This logic is called by the CLI commands in main.py.
"""

import logging
from pathlib import Path
from collections import defaultdict

from flashcore.db.database import FlashcardDatabase

logger = logging.getLogger(__name__)


def export_to_markdown(db: FlashcardDatabase, output_dir: Path) -> None:
    """
    Export all flashcards from the database into Markdown files, one file per deck, saved under output_dir.
    
    Creates the output directory if missing (raises IOError on failure). For each deck a Markdown file named from a sanitized deck name is written containing a header with the deck name and entries for each card (cards are written sorted by front; tags, if present, are written sorted alphabetically). File write errors for individual decks are logged and do not stop the overall export.
    
    Parameters:
        db (FlashcardDatabase): Source database from which to retrieve flashcards.
        output_dir (Path): Destination directory for generated Markdown files.
    
    Raises:
        IOError: If the output directory cannot be created.
    """
    logger.info(f"Starting Markdown export to directory: {output_dir}")

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logger.error(f"Could not create output directory {output_dir}: {e}")
        raise IOError(f"Failed to create output directory: {e}") from e

    all_cards = db.get_all_cards()
    if not all_cards:
        logger.warning("No cards found in the database to export.")
        return

    decks = defaultdict(list)
    for card in all_cards:
        decks[card.deck_name].append(card)

    exported_files = 0
    for deck_name, cards in decks.items():
        # Sanitize deck name for use as a filename
        safe_deck_name = "".join(
            c for c in deck_name if c.isalnum() or c in (" ", "_")
        ).rstrip()
        if not safe_deck_name:
            safe_deck_name = "unnamed_deck"
        file_path = output_dir / f"{safe_deck_name}.md"

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"# Deck: {deck_name}\n\n")
                for card in sorted(cards, key=lambda c: c.front):
                    f.write(f"**Front:** {card.front}\n\n")
                    f.write(f"**Back:** {card.back}\n\n")
                    if card.tags:
                        tags_str = ", ".join(sorted(list(card.tags)))
                        f.write(f"**Tags:** `{tags_str}`\n\n")
                    f.write("---\n\n")
            logger.info(
                f"Successfully exported {len(cards)} cards to {file_path}"
            )
            exported_files += 1
        except IOError as e:
            logger.error(f"Could not write to file {file_path}: {e}")
            # Continue to next deck

    logger.info(
        f"Markdown export complete. Exported {len(decks)} deck(s) to {exported_files} file(s)."
    )