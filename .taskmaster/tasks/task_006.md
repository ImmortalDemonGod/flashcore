# Task ID: 6

**Title:** Develop CLI for flashcore-lib

**Status:** pending

**Dependencies:** 5

**Priority:** medium

**Description:** Create a new CLI using Typer that interfaces with the refactored library.

**Details:**

Reference HPE_ARCHIVE/flashcore/cli/ for command structure. Build flashcore/cli.py with Typer commands: review, ingest, stats. CRITICAL (PRD Section 3.3): CLI must accept --db flag for database path (no defaults). Example: 'flashcore review --db=/path/to/flash.db --deck=python'. The CLI is responsible for dependency injection - it receives paths from user and passes to library classes. Implement deduplication logic in ingest command per Task 5.

**Test Strategy:**

Run 'flashcore review --db=/tmp/test.db --deck=test' - should work. Run 'flashcore review' without --db - should show error requiring db path.
