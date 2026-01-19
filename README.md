
 # Flashcore

 [![CI](https://github.com/ImmortalDemonGod/flashcore/actions/workflows/main.yml/badge.svg)](https://github.com/ImmortalDemonGod/flashcore/actions/workflows/main.yml)
 [![codecov](https://codecov.io/gh/ImmortalDemonGod/flashcore/branch/main/graph/badge.svg)](https://codecov.io/gh/ImmortalDemonGod/flashcore)
 [![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
 [![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

 **Flashcore** is a high-performance, local-first Spaced Repetition System (SRS) engine built for developers. It combines the state-of-the-art **FSRS (Free Spaced Repetition Scheduler)** algorithm with a **DuckDB** backend to provide a lightning-fast, dependency-light memory engine.

 Designed using a **Hub-and-Spoke** architecture, Flashcore is a path-agnostic logic library (the "Spoke") intended to be driven by a CLI (the "Hub"). It treats your knowledge base as source code.

 ---

 ## 🚀 Key Features

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

 ## ✅ Status

 - **Library**
   Usable today: `FlashcardDatabase`, `FSRS_Scheduler`, YAML parsing utilities.
 - **CLI**
   In progress. The `flashcore` console entrypoint is wired, but the full multi-command CLI workflow (`vet`, `ingest`, `review`, `stats`, etc.) is still being implemented.

 If you want to see what’s planned next, run:

 ```bash
 task-master list
 ```

 ---

 ## 📦 Installation

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

 ## 🛠️ Programmatic Usage (The Library)

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

 ## 🗂️ YAML Processing (Current Library Capability)

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

 ## 💻 CLI Usage (The Hub) — WIP

 The intended workflow cycle will look like this:

 | Step | Command | Description |
 | :--- | :--- | :--- |
 | **1. Author** | `vim deck.yaml` | Create cards in YAML (see format below). |
 | **2. Vet** | `flashcore vet` | Validate structure, check for secrets, and assign stable UUIDs. |
 | **3. Ingest** | `flashcore ingest` | Sync YAML cards to the DuckDB database without losing history. |
 | **4. Review** | `flashcore review` | Start an interactive TUI session powered by FSRS. |
 | **5. Audit** | `flashcore stats` | View retention metrics and deck health. |

 Environment-variable support (e.g., `FLASHCORE_DB`) is planned for the CLI so you can avoid repeating flags.

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

 ## 🏗️ Architecture: Hub-and-Spoke

 Flashcore solves the "Hardcoded Life" problem by separating logic from configuration:

 1. **The Spoke (`flashcore/`)**
    The core library. Contains scheduling logic, DB marshalling, and YAML parsing.
 2. **The Hub (`flashcore.cli`)**
    The interface layer (in progress). Accepts user input (flags/env) and injects paths/config into the Spoke.

 ---

 ## 🧪 Development

 ```bash
 make virtualenv
 make install
 make fmt
 make test
 ```

 See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow.

 ---

 ## 📄 License

 This project is released into the public domain under the [Unlicense](LICENSE). No rights reserved.
