# Flashcore

[![CI](https://github.com/ImmortalDemonGod/flashcore/actions/workflows/main.yml/badge.svg)](https://github.com/ImmortalDemonGod/flashcore/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/ImmortalDemonGod/flashcore/branch/main/graph/badge.svg)](https://codecov.io/gh/ImmortalDemonGod/flashcore)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Flashcore** is a high-performance, local-first Spaced Repetition System (SRS) engine built for developers. It combines the state-of-the-art **FSRS (Free Spaced Repetition Scheduler)** algorithm with a **DuckDB** backend to provide a lightning-fast, dependency-light memory engine.

Designed using a **Hub-and-Spoke** architecture, Flashcore is a path-agnostic logic library (the "Spoke") intended to be driven by a CLI (the "Hub"). It treats your knowledge base as source code.

---

## Key Features

- **O(1) scheduler performance**
  Flashcore computes the next interval from cached card state (no full history replay).
- **The "Nuclear Reactor" fix (lightweight deps)**
  Runtime dependency set is intentionally small (no `torch`, no `transformers`).
- **DuckDB backend**
  A single-file database with fast OLAP-style queries and minimal overhead.
- **YAML-first authoring (library support)**
  Parse cards from human-readable YAML into strongly validated Pydantic models.
- **Dependency-injection first**
  The library requires paths to be provided explicitly at runtime (e.g., database path).

---

## Status

- **Library** — complete
  `FlashcardDatabase`, `FSRS_Scheduler`, YAML parsing, review processing, session analytics.
- **CLI** — complete
  All commands (`vet`, `ingest`, `review`, `review-all`, `export`, `stats`) are implemented and tested.
- **Data migration tooling** — complete
  `flashcore/scripts/dump_history.py` and `flashcore/scripts/migrate.py` ship with the project.
- **AIV protocol**
  The mechanical enforcement layer (packet structure + immutable intent links) is implemented in CI. The cognitive layer (SVP) is still a work in progress.

Tasks 1–8 are complete. Task 9 (finalization) is in progress.

---

## AIV Case Study

Flashcore is being developed as a reference *case study* for the AIV (Architect–Implementer–Verifier) workflow: tight task decomposition, explicit claims, and artifact-backed verification.

This is intentionally honest about the current state:
- **AIV SOP (mechanical layer):** implemented
- **AIV SVP (cognitive layer):** not fully implemented yet
- **CLI “Hub” implementation:** in progress

### Evidence Index (real repo artifacts)

- **Task 4: Scheduler O(N) → O(1) audit trail**
  - `artifacts/task_4_ci_verification_report.md`
  - `artifacts/task_4_implementation_summary.md`
  - `artifacts/task_4_scheduler_optimization_audit.md`
- **AIV enforcement docs**
  - `docs/AIV_ENFORCEMENT_PLAN.md`
  - `docs/AIV_ENFORCEMENT_AUDIT.md`

### CI enforcement (what’s actually gated)

- **AIV packet validation (PR-body gate + immutable links)**
  - `.github/workflows/aiv-guard.yml`
- **CI + artifact production + negative evidence checks**
  - `.github/workflows/main.yml`

---

## Installation

Flashcore requires Python 3.10 or higher.

```bash
git clone https://github.com/ImmortalDemonGod/flashcore.git
cd flashcore
pip install -e .
```

For development (tests, linting, etc.):

```bash
make install
```

---

## Programmatic Usage (The Library)

This example shows the current working public APIs.

```python
from datetime import date

from flashcore import Card, FlashcardDatabase
from flashcore.scheduler import FSRS_Scheduler
from flashcore.review_processor import ReviewProcessor

db = FlashcardDatabase(db_path="./my_study.db")

with db:
    # 1) Create and upsert a card
    card = Card(
        deck_name="Computer Science",
        front="What is the average complexity of a dict lookup?",
        back="O(1) on average.",
    )
    db.upsert_cards_batch([card])

    # 2) Fetch it back from the DB
    persisted = db.get_card_by_uuid(card.uuid)
    assert persisted is not None

    # 3) Submit a review using the O(1) scheduler
    scheduler = FSRS_Scheduler()
    processor = ReviewProcessor(db_manager=db, scheduler=scheduler)
    updated = processor.process_review(card=persisted, rating=3)

    # 4) Ask what’s due
    due = db.get_due_cards(deck_name="Computer Science", on_date=date.today())
    print(f"Due today: {len(due)}")
```

---

## YAML Processing (Current Library Capability)

Flashcore includes a YAML parsing pipeline you can call directly.

```python
from pathlib import Path

from flashcore import YAMLProcessorConfig
from flashcore.parser import load_and_process_flashcard_yamls

config = YAMLProcessorConfig(
    source_directory=Path("./decks"),
    assets_root_directory=Path("./assets"),
)

cards, errors = load_and_process_flashcard_yamls(config)
print(f"Parsed {len(cards)} cards with {len(errors)} errors")
```

---

## CLI Usage (The Hub)

Supply the database path via `--db` flag or the `FLASHCORE_DB` environment variable.

```bash
export FLASHCORE_DB=./study.db

flashcore vet   --source-dir ./decks        # Validate YAMLs, detect secrets
flashcore ingest --source-dir ./decks       # Sync cards → DB (preserves history)
flashcore review "Deck Name"                # Interactive FSRS review session
flashcore review-all                        # Review all due cards across decks
flashcore stats                             # Retention metrics and deck health
flashcore export --out-dir ./export         # Export cards to Markdown
```

| Step | Command | Description |
| :--- | :--- | :--- |
| **1. Author** | `vim deck.yaml` | Create cards in YAML (see format below). |
| **2. Vet** | `flashcore vet` | Validate structure, check for secrets, assign stable UUIDs. |
| **3. Ingest** | `flashcore ingest` | Sync YAML cards to DuckDB without losing review history. |
| **4. Review** | `flashcore review` | Interactive TUI session powered by FSRS. |
| **5. Audit** | `flashcore stats` | View retention metrics and deck health. |

### YAML Card Format

```yaml
deck: Programming::Python
tags: [coding, backend]
cards:
  - q: What is the complexity of a dict lookup?
    a: O(1) on average.
  - q: How do you define a decorator?
    a: |
      A function that takes another function and extends its behavior:
      ```python
      @my_decorator
      def func(): pass
      ```
```

---

## Migrating from a Legacy Flashcore Database

If you have data in an older Flashcore DuckDB file (pre-pivot schema), use the
bundled scripts to export and re-import safely. **Do not copy the `.db` file
directly** — binary compatibility is not guaranteed across DuckDB versions.

```bash
# Step 1 — export legacy DB to JSON (read-only, non-destructive)
python flashcore/scripts/dump_history.py \
    --db ./old.db \
    --out-dir ./export/

# Step 2 — import into a new DB
python flashcore/scripts/migrate.py import \
    --cards   ./export/cards.json \
    --reviews ./export/reviews.json \
    --sessions ./export/sessions.json \
    --db ./new.db

# Step 3 — validate completeness and integrity
python flashcore/scripts/migrate.py validate \
    --old-db ./old.db \
    --new-db ./new.db
```

The validate step checks row-count parity, orphaned reviews, stability/difficulty
value ranges, and schema sanity. Exit code 0 means all checks passed.

---

## Architecture: Hub-and-Spoke

Flashcore solves the "Hardcoded Life" problem by separating logic from configuration:

1. **The Spoke (`flashcore/`)**
   The core library. Contains scheduling logic, DB marshalling, and YAML parsing.
2. **The Hub (`flashcore.cli`)**
   The interface layer (in progress). Accepts user input (flags/env) and injects paths/config into the Spoke.

---

## Development

```bash
make virtualenv
make install
make fmt
make test
```

 See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow.

---

## License

This project is released into the public domain under the [Unlicense](LICENSE). No rights reserved.
