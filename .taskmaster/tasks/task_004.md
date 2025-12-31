# Task ID: 4

**Title:** Optimize Scheduler Logic (O(1) Performance Fix)

**Status:** pending

**Dependencies:** 3

**Priority:** critical

**Description:** Eliminate the O(N) history replay bottleneck by using cached card state.

**Details:**

CRITICAL PERFORMANCE FIX (PRD Section 2 Finding 2): HPE_ARCHIVE/flashcore/scheduler.py lines 154-160 contain 'for review in history: fsrs_card, _ = self.fsrs_scheduler.review_card(...)' - this replays ENTIRE history on every review (O(N) complexity). For a card with 500 reviews, this loops 500 times. SOLUTION: Change compute_next_state signature from 'compute_next_state(history: List[Review], ...)' to 'compute_next_state(card: Card, new_rating: int, ...)'. Initialize FSRSCard from card.stability, card.difficulty, card.state (cached values) instead of replaying history. This makes scheduling O(1).

**Test Strategy:**

Create card with 100 reviews. Time compute_next_state - should be <10ms regardless of history length. Compare before/after: old implementation time should scale with history length, new should be constant.

## Subtasks

### 4.1. Copy scheduler.py and Update Imports

**Status:** pending  
**Dependencies:** None  

Transfer the scheduler module from HPE_ARCHIVE and update imports to use constants.py.

**Details:**

Execute: cp HPE_ARCHIVE/flashcore/scheduler.py flashcore/scheduler.py. This contains FSRS_Scheduler and BaseScheduler classes. CRITICAL: Update imports on lines 16-19 from 'from cultivation.scripts.flashcore.config import DEFAULT_PARAMETERS, DEFAULT_DESIRED_RETENTION' to 'from .constants import DEFAULT_PARAMETERS, DEFAULT_DESIRED_RETENTION'. This reflects the config.py → constants.py rename for clarity.

### 4.2. Change compute_next_state Signature

**Status:** pending  
**Dependencies:** 4.1  

Modify method to accept Card object instead of history list.

**Details:**

In scheduler.py line 147, change 'def compute_next_state(self, history: List[Review], new_rating: int, review_ts: datetime.datetime)' to 'def compute_next_state(self, card: Card, new_rating: int, review_ts: datetime.datetime)'. Update BaseScheduler abstract method signature too (line 53).

### 4.3. Copy review_processor.py to flashcore/review_processor.py

**Status:** pending  
**Dependencies:** 4.2  

Transfer the ReviewProcessor service module from HPE_ARCHIVE.

**Details:**

Execute: cp HPE_ARCHIVE/flashcore/review_processor.py flashcore/review_processor.py. Also port the dependent review/session services used by the CLI: cp HPE_ARCHIVE/flashcore/review_manager.py flashcore/review_manager.py; cp HPE_ARCHIVE/flashcore/session_manager.py flashcore/session_manager.py. CRITICAL: session_manager.py uses DuckDB fetch_df() (requires pandas). When porting, refactor session_manager.py to avoid fetch_df() and pandas usage, mirroring the DB-layer 'no pandas' constraint.

### 4.4. Remove History Replay Loop (O(N) -> O(1))

**Status:** pending  
**Dependencies:** 4.3  

Delete the for loop that replays entire review history.

**Details:**

Delete lines 154-160 in scheduler.py: 'fsrs_card = FSRSCard()' followed by 'for review in history: ...' loop. This is the performance bottleneck.

### 4.5. Initialize FSRSCard from Cached Card State

**Status:** pending  
**Dependencies:** 4.4  

Use card.stability, card.difficulty, card.state instead of replaying history.

**Details:**

Replace deleted loop with: 'fsrs_card = FSRSCard(); if card.state != CardState.New: fsrs_card.stability = card.stability; fsrs_card.difficulty = card.difficulty; fsrs_card.state = FSRSState(card.state.value); fsrs_card.due = card.next_due_date'. This initializes from cached state (O(1)).

### 4.6. Update review_processor.py to Pass Card Object

**Status:** pending  
**Dependencies:** 4.5  

Modify callers of compute_next_state to pass card instead of history.

**Details:**

In flashcore/review_processor.py (review_processor.py) line 103, change 'scheduler_output = self.scheduler.compute_next_state(history=review_history, ...)' to 'scheduler_output = self.scheduler.compute_next_state(card=card, ...)'. Remove history parameter.

### 4.7. Migrate Scheduler Tests with O(1) Benchmark (Incremental Verification)

**Status:** pending  
**Dependencies:** 4.6  

Copy and adapt test_scheduler.py to verify O(1) optimization works correctly.

**Details:**

Execute: cp HPE_ARCHIVE/tests/test_scheduler.py tests/test_scheduler.py. Update imports from 'cultivation.scripts.flashcore' to 'flashcore'. CRITICAL: Add new benchmark test 'test_compute_next_state_is_constant_time' that creates cards with 1, 10, 100, 500 reviews and times compute_next_state for each. Assert that time difference between 1 and 500 reviews is <50ms (proving O(1) not O(N)). This verifies the performance fix works.

### 4.8. Preserve FSRS Parameter Override Support

**Status:** pending  
**Dependencies:** 4.1  

Ensure FSRS_Scheduler can accept custom weight vectors at runtime (no forever-defaults trap).

**Details:**

HPE_ARCHIVE FSRS_Scheduler already supports injection via FSRSSchedulerConfig(parameters=..., desired_retention=...). When porting/optimizing, ensure this remains supported and is surfaced to the CLI (Task 6) so users can supply externally-optimized weights without fsrs-optimizer.
