# Task ID: 6

**Title:** Develop CLI for flashcore-lib

**Status:** pending

**Dependencies:** 5

**Priority:** medium

**Description:** Create a new CLI using Typer that interfaces with the refactored library.

**Details:**

Reference HPE_ARCHIVE/flashcore/cli/ for command structure. Build flashcore/cli.py with Typer commands: review, ingest, stats. CRITICAL (PRD Section 3.3): CLI must accept --db flag for database path (no defaults). Example: 'flashcore review --db=/path/to/flash.db --deck=python'. The CLI is responsible for dependency injection - it receives paths from user and passes to library classes. Implement deduplication logic in ingest command (moved from Task 5).

**Test Strategy:**

Run 'flashcore review --db=/tmp/test.db --deck=test' - should work. Run 'flashcore review' without --db - should show error requiring db path.

## Subtasks

### 6.1. Scaffold CLI Application Structure

**Status:** pending  
**Dependencies:** None  

Create the base Typer CLI application in flashcore/cli.py.

**Details:**

Create flashcore/cli.py with Typer app initialization. Reference HPE_ARCHIVE/flashcore/cli/main.py for structure. Set up command groups and common options (--db flag required for all commands).

### 6.2. Implement Ingest Command with Deduplication

**Status:** pending  
**Dependencies:** 6.1  

Create ingest command that processes YAML files with stateless parser and DB-based deduplication.

**Details:**

Port logic from HPE_ARCHIVE/flashcore/cli/_ingest_logic.py. CRITICAL DEDUPLICATION LOGIC (from Task 5.3): (1) Call db.get_all_card_fronts_and_uuids() to get authoritative list of existing cards. (2) Process YAML files with YAMLProcessor (stateless). (3) Filter output cards against existing_fronts set. (4) Only insert cards not in existing_fronts. This makes DB the single source of truth.

### 6.3. Implement Review Command

**Status:** pending  
**Dependencies:** 6.1  

Create review command that orchestrates review sessions with dependency injection.

**Details:**

Port logic from HPE_ARCHIVE/flashcore/cli/_review_logic.py. Wire up: FlashcardDatabase(db_path=args.db), FSRS_Scheduler, ReviewSessionManager. Pass all paths explicitly - no config.settings references. Implement review UI flow.

### 6.4. Implement Stats Command

**Status:** pending  
**Dependencies:** 6.1  

Create stats command to display deck statistics.

**Details:**

Port logic from HPE_ARCHIVE/flashcore/cli/ stats functionality. Query database for card counts, review stats, due cards. Display with rich tables.

### 6.5. Add CLI to __main__.py Entry Point

**Status:** pending  
**Dependencies:** 6.2, 6.3, 6.4  

Wire CLI to package entry point for 'flashcore' command.

**Details:**

Update flashcore/__main__.py to import and run CLI app. Ensure setup.py entry_points references this. Test that 'flashcore' command is available after pip install.
