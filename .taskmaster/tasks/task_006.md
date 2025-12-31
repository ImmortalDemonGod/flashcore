# Task ID: 6

**Title:** Develop CLI Package for flashcore

**Status:** pending

**Dependencies:** 5

**Priority:** medium

**Description:** Reconstruct the CLI as a modular package maintaining separation of concerns.

**Details:**

Port HPE_ARCHIVE/flashcore/cli/ as flashcore/cli/ PACKAGE (not single file). HPE_ARCHIVE has 6 modules totaling 960 lines: main.py (382 lines - entry point), review_ui.py (93 lines - UI), _review_logic.py (28 lines), _review_all_logic.py (172 lines), _vet_logic.py (222 lines - ingest), _export_logic.py (63 lines). Preserve this modular structure to avoid creating a 'God Object'. CRITICAL (PRD Section 3.3): CLI must accept --db flag for database path (no defaults). The CLI is responsible for dependency injection - it receives paths from user and passes to library classes.

**Test Strategy:**

Run 'flashcore review --db=/tmp/test.db --deck=test' - should work. Run 'flashcore review' without --db - should show error requiring db path.

## Subtasks

### 6.1. Create CLI Package Structure

**Status:** pending  
**Dependencies:** None  

Set up flashcore/cli/ as a package with modular architecture.

**Details:**

Create directory: mkdir -p flashcore/cli. Copy modular structure: cp HPE_ARCHIVE/flashcore/cli/main.py flashcore/cli/main.py (entry point); cp HPE_ARCHIVE/flashcore/cli/review_ui.py flashcore/cli/review_ui.py (UI layer); cp HPE_ARCHIVE/flashcore/cli/__init__.py flashcore/cli/__init__.py. This preserves separation of concerns - main.py handles CLI routing, separate modules handle business logic. Update imports from 'cultivation.scripts.flashcore' to 'flashcore'.

### 6.2. Extract and Refactor Ingestion Logic with Authoritative Deduplication

**Status:** pending  
**Dependencies:** 6.1  

Extract ingestion and upsert logic from legacy main.py and implement DB-based deduplication.

**Details:**

CRITICAL SOURCE CORRECTION: Ingestion logic is in HPE_ARCHIVE/flashcore/cli/main.py lines 65-161 (_load_cards_from_source, _filter_new_cards, _execute_ingestion, _perform_ingestion_logic). Create flashcore/cli/ingest.py module extracting these functions. REFACTOR DEDUPLICATION (from Task 5.3): Replace _filter_new_cards logic to call db.get_all_card_fronts_and_uuids() BEFORE YAMLProcessor, filter output against existing_fronts set, then upsert only new cards. NOTE: _vet_logic.py (222 lines) is for 'vet' command (validation/formatting), NOT ingestion - copy separately if vet command needed.

### 6.3. Port Review Logic Modules

**Status:** pending  
**Dependencies:** 6.1  

Copy review logic modules maintaining separation between orchestration and UI.

**Details:**

Execute: cp HPE_ARCHIVE/flashcore/cli/_review_logic.py flashcore/cli/_review_logic.py (28 lines - session orchestration); cp HPE_ARCHIVE/flashcore/cli/_review_all_logic.py flashcore/cli/_review_all_logic.py (172 lines - multi-deck logic). Update imports to 'flashcore'. Wire up: FlashcardDatabase(db_path=args.db), FSRS_Scheduler, ReviewSessionManager. Pass all paths explicitly - no config.settings references. Connect to review_ui.py for presentation layer.

### 6.4. Port Export, Vet, and Stats Functionality

**Status:** pending  
**Dependencies:** 6.1  

Copy remaining CLI modules for export, vet, and stats commands.

**Details:**

Execute: cp HPE_ARCHIVE/flashcore/cli/_export_logic.py flashcore/cli/_export_logic.py (63 lines - export functionality); cp HPE_ARCHIVE/flashcore/cli/_vet_logic.py flashcore/cli/_vet_logic.py (222 lines - YAML validation/formatting for 'vet' command, NOT ingestion). Add stats command logic to main.py (query database for card counts, review stats, due cards). Display with rich tables. Update all imports to 'flashcore'.

### 6.5. Add CLI to __main__.py Entry Point

**Status:** pending  
**Dependencies:** 6.2, 6.3, 6.4  

Wire CLI to package entry point for 'flashcore' command.

**Details:**

Update flashcore/__main__.py to import and run CLI app. Ensure setup.py entry_points references this. Test that 'flashcore' command is available after pip install.
