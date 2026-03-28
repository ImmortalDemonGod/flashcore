# Flashcore

[![CI](https://github.com/ImmortalDemonGod/flashcore/actions/workflows/main.yml/badge.svg)](https://github.com/ImmortalDemonGod/flashcore/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/ImmortalDemonGod/flashcore/branch/main/graph/badge.svg)](https://codecov.io/gh/ImmortalDemonGod/flashcore)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Flashcore** is a high-performance, local-first Spaced Repetition System (SRS)
engine built for developers. It combines the
**FSRS (Free Spaced Repetition Scheduler)** algorithm with a **DuckDB** backend
to give you a fast, dependency-light memory engine you can embed in any project
or drive from the command line.

---

## Quick Start

```bash
git clone https://github.com/ImmortalDemonGod/flashcore.git
cd flashcore
pip install -e .

# Point every command at your database
export FLASHCORE_DB=./study.db

# Validate a deck of YAML cards
flashcore vet --source-dir ./decks

# Sync cards into the database
flashcore ingest --source-dir ./decks

# Start a review session
flashcore review "My Deck"
```

---

## Key Features

- **O(1) scheduler** — next interval computed from cached card state; no full
  history replay regardless of how many reviews a card has.
- **Lightweight runtime** — no `torch`, no `transformers`, no `fsrs-optimizer`.
  The install footprint is ~10 packages.
- **Single-file DuckDB backend** — ACID-compliant, embeddable, zero server
  setup. Move your `.db` file like any other file.
- **YAML-first authoring** — write cards in plain YAML; the parser validates
  structure, sanitizes HTML, and detects accidentally embedded secrets (API
  keys, tokens) before they reach the database.
- **Dependency-injection architecture** — the library never assumes a path.
  Every operation receives its database path explicitly, making it safe to run
  multiple isolated instances side-by-side.
- **Safe ingestion** — re-ingesting a YAML file never overwrites existing
  review history; stability and difficulty are preserved on conflict.

---

## Installation

Flashcore requires Python 3.10 or higher.

```bash
git clone https://github.com/ImmortalDemonGod/flashcore.git
cd flashcore
pip install -e .
```

For development (tests, linting, formatting):

```bash
make install   # installs package + all dev deps
make test      # runs 480 tests
make fmt       # black + isort
make lint      # flake8 + black --check + mypy
```

---

## CLI Usage

Supply the database path via `--db` or the `FLASHCORE_DB` environment variable.

| Step | Command | Description |
| :--- | :--- | :--- |
| **1. Author** | `vim deck.yaml` | Write cards in YAML (see format below). |
| **2. Vet** | `flashcore vet --source-dir ./decks` | Validate structure, detect secrets, assign stable UUIDs. |
| **3. Ingest** | `flashcore ingest --source-dir ./decks` | Sync YAML cards to DuckDB without overwriting review history. |
| **4. Review** | `flashcore review "Deck Name"` | Interactive TUI session powered by FSRS. |
| **5. Review all** | `flashcore review-all` | Review all due cards across every deck. |
| **6. Export** | `flashcore export --out-dir ./export` | Export cards to Markdown. |
| **7. Audit** | `flashcore stats` | Retention metrics and deck health. |

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

## Programmatic Usage

```python
from datetime import date

from flashcore import Card, FlashcardDatabase
from flashcore.scheduler import FSRS_Scheduler
from flashcore.review_processor import ReviewProcessor

db = FlashcardDatabase(db_path="./my_study.db")

with db:
    # Create and persist a card
    card = Card(
        deck_name="Computer Science",
        front="What is the average complexity of a dict lookup?",
        back="O(1) on average.",
    )
    db.upsert_cards_batch([card])

    # Submit a review using the O(1) scheduler
    scheduler = FSRS_Scheduler()
    processor = ReviewProcessor(db_manager=db, scheduler=scheduler)
    processor.process_review(card=db.get_card_by_uuid(card.uuid), rating=3)

    # Query what is due today
    due = db.get_due_cards(deck_name="Computer Science", on_date=date.today())
    print(f"Due today: {len(due)}")
```

### YAML Pipeline

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

## Architecture: Hub-and-Spoke

Flashcore separates logic from configuration to avoid the "hardcoded path"
problem common in SRS tools.

**Spoke — `flashcore/`** (the library)
Pure logic: scheduling, DB marshalling, YAML parsing, models. No hardcoded
paths, no global config. Safe to import and use in any context.

**Hub — `flashcore/cli/`** (the interface)
Accepts paths and config from the user (flags or `FLASHCORE_DB`) and injects
them into the Spoke at runtime. Two different programs can use the Spoke
simultaneously against two different databases without interference.

**Scripts — `flashcore/scripts/`**
Standalone utility scripts (migration tooling). Not part of the installed
package; not importable from core code.

---

## AIV Case Study

Flashcore is a reference implementation for the
**AIV (Architect–Implementer–Verifier)** workflow: every PR carries a
structured verification packet with falsifiable claims, immutable intent links,
and CI-collected evidence.

| Layer | State |
|---|---|
| Mechanical (packet gate, immutable Class E links, anti-cheat) | implemented |
| Cognitive (SVP verifier protocol) | in progress |

### Evidence artifacts

- `artifacts/task_4_ci_verification_report.md` — O(N)→O(1) scheduler benchmark
- `docs/AIV_ENFORCEMENT_PLAN.md` — enforcement strategy
- `docs/AIV_ENFORCEMENT_AUDIT.md` — gap analysis
- `.github/aiv-packets/` — per-PR verification packets

### CI gates

- `.github/workflows/aiv-guard.yml` — rejects PRs without a valid packet
- `.github/workflows/main.yml` — lint, tests (6 platform/Python combinations),
  negative evidence checks, anti-cheat warning

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

Released into the public domain under the [Unlicense](LICENSE). No rights reserved.
