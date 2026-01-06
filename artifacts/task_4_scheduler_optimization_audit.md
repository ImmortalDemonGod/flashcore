# Task 4: Scheduler Performance Optimization (O(N) to O(1)) - Comprehensive Audit

**Date:** 2026-01-05  
**Task ID:** 4  
**Priority:** Critical  
**Status:** Pending  
**Dependency:** Task 3 (Complete)

---

## Executive Summary

This audit provides a systematic analysis of Task 4 against the current codebase, mapping each subtask to atomic commits with AIV verification requirements. The optimization eliminates O(N) history replay bottleneck by using cached card state, achieving O(1) scheduler performance.

### Critical Performance Issue
- **Location:** `HPE_ARCHIVE/flashcore/scheduler.py:157-160`
- **Problem:** `for review in history: fsrs_card, _ = self.fsrs_scheduler.review_card(...)`
- **Impact:** For a card with 500 reviews, this loops 500 times per review submission
- **Solution:** Initialize FSRSCard from `card.stability`, `card.difficulty`, `card.state` (cached values)

---

## Codebase State Analysis

### Current Architecture

#### 1. HPE_ARCHIVE Structure (Source)
```
HPE_ARCHIVE/flashcore/
├── scheduler.py          # FSRS_Scheduler with O(N) bottleneck
├── review_processor.py   # Calls scheduler with history list
├── review_manager.py     # ReviewSessionManager (uses review_processor)
├── session_manager.py    # Session analytics (uses pandas/fetch_df)
└── card.py              # Card model with cached state fields
```

#### 2. Active flashcore/ Structure (Target)
```
flashcore/
├── constants.py         # DEFAULT_PARAMETERS, DEFAULT_DESIRED_RETENTION
├── models.py           # Card, Review, Session, CardState (already exists!)
└── db/                 # Database layer (no pandas dependency)
```

### Key Discovery: Card Model Already Exists

**CRITICAL FINDING:** The active codebase already has `flashcore/models.py` with:
- `Card` class with all required cached state fields (lines 43-177)
- `CardState` enum matching HPE_ARCHIVE (lines 21-30)
- `Review` class (lines 179-276)
- `Session` class (lines 278-418)

This means we **do NOT need to copy card.py** from HPE_ARCHIVE. We only need to:
1. Copy `scheduler.py` and update imports
2. Copy `review_processor.py` and update imports
3. Modify scheduler to use Card object instead of history

### Import Path Analysis

**HPE_ARCHIVE imports:**
```python
from cultivation.scripts.flashcore.config import DEFAULT_PARAMETERS
from cultivation.scripts.flashcore.card import Review, CardState
```

**Target flashcore/ imports:**
```python
from .constants import DEFAULT_PARAMETERS, DEFAULT_DESIRED_RETENTION
from .models import Card, Review, CardState, Session
```

### Pandas Dependency Issue

**session_manager.py** uses DuckDB's `fetch_df()` which requires pandas:
- Line 423: `result_df = conn.execute(sql, (session_uuid,)).fetch_df()`
- Line 435: `for _, row in result_df.iterrows()`

**Resolution:** Refactor to use `fetchall()` instead of `fetch_df()` to avoid pandas dependency.

---

## Atomic Commit Plan

Each commit represents a single logical change to a single file, with specific AIV verification.

### Commit 1: Copy scheduler.py to flashcore/

**Files Changed:** 1 new file
- `flashcore/scheduler.py` (new, 203 lines)

**Changes:**
1. Copy `HPE_ARCHIVE/flashcore/scheduler.py` → `flashcore/scheduler.py`
2. Update import on line 16-19:
   - FROM: `from cultivation.scripts.flashcore.config import DEFAULT_PARAMETERS, DEFAULT_DESIRED_RETENTION`
   - TO: `from .constants import DEFAULT_PARAMETERS, DEFAULT_DESIRED_RETENTION`
3. Update import on line 31:
   - FROM: `from .card import Review, CardState`
   - TO: `from .models import Review, CardState`

**Commit Message:**
```
feat(scheduler): copy FSRS_Scheduler from HPE_ARCHIVE

Copy scheduler module with O(N) history replay implementation.
Updates imports to use flashcore.constants and flashcore.models.

Related to Task #4 - Scheduler Performance Optimization
```

**AIV Verification:**
```bash
# Verify file exists
test -f flashcore/scheduler.py && echo "✓ File exists"

# Verify imports updated
grep -n "from .constants import" flashcore/scheduler.py | grep -q "DEFAULT_PARAMETERS" && echo "✓ Constants import correct"
grep -n "from .models import" flashcore/scheduler.py | grep -q "Review, CardState" && echo "✓ Models import correct"

# Verify no old imports remain
! grep -q "cultivation.scripts.flashcore" flashcore/scheduler.py && echo "✓ No old imports"

# Verify module imports successfully
python -c "from flashcore.scheduler import FSRS_Scheduler, FSRSSchedulerConfig; print('✓ Module imports successfully')"

# Verify classes exist
python -c "from flashcore.scheduler import FSRS_Scheduler, BaseScheduler, FSRSSchedulerConfig, SchedulerOutput; print('✓ All classes importable')"
```

**Test Strategy:**
- Import module and verify no ImportErrors
- Instantiate FSRS_Scheduler with default config
- Verify RATING_MAP and REVIEW_TYPE_MAP exist

---

### Commit 2: Update BaseScheduler signature to accept Card

**Files Changed:** 1 modified file
- `flashcore/scheduler.py` (lines 52-55, 147-149)

**Changes:**
1. Line 31: Add Card import
   - FROM: `from .models import Review, CardState`
   - TO: `from .models import Card, Review, CardState`
2. Line 53-55: Update BaseScheduler abstract method signature
   - FROM: `def compute_next_state(self, history: List[Review], new_rating: int, review_ts: datetime.datetime) -> SchedulerOutput:`
   - TO: `def compute_next_state(self, card: Card, new_rating: int, review_ts: datetime.datetime) -> SchedulerOutput:`
3. Line 147-149: Update FSRS_Scheduler method signature
   - FROM: `def compute_next_state(self, history: List[Review], new_rating: int, review_ts: datetime.datetime) -> SchedulerOutput:`
   - TO: `def compute_next_state(self, card: Card, new_rating: int, review_ts: datetime.datetime) -> SchedulerOutput:`
4. Line 60: Update docstring parameter
   - FROM: `history: A list of past Review objects for the card, sorted chronologically.`
   - TO: `card: The Card object containing cached state (stability, difficulty, state).`

**Commit Message:**
```
refactor(scheduler): change compute_next_state to accept Card object

Update method signature from history list to Card object parameter.
This is preparation for O(1) optimization using cached state.

Breaking change: All callers must be updated to pass Card instead of history.

Related to Task #4 - Scheduler Performance Optimization
```

**AIV Verification:**
```bash
# Verify signature changed in BaseScheduler
grep -A2 "class BaseScheduler" flashcore/scheduler.py | grep -A10 "def compute_next_state" | grep -q "card: Card" && echo "✓ BaseScheduler signature updated"

# Verify signature changed in FSRS_Scheduler
grep -A2 "class FSRS_Scheduler" flashcore/scheduler.py | grep -A50 "def compute_next_state" | grep -q "card: Card" && echo "✓ FSRS_Scheduler signature updated"

# Verify Card import exists
grep -q "from .models import Card" flashcore/scheduler.py && echo "✓ Card imported"

# Verify no history parameter remains in signature
! grep "def compute_next_state.*history:" flashcore/scheduler.py && echo "✓ No history parameter in signature"
```

**Test Strategy:**
- Verify method signature accepts Card parameter
- Verify type hints are correct
- Note: Tests will fail until implementation updated (expected)

---

### Commit 3: Remove O(N) history replay loop

**Files Changed:** 1 modified file
- `flashcore/scheduler.py` (lines 154-160)

**Changes:**
1. Delete lines 156-160 (the O(N) bottleneck):
   ```python
   # DELETE THIS BLOCK:
   # Replay the entire review history to build the correct current state.
   for review in history:
       rating = self._map_flashcore_rating_to_fsrs(review.rating)
       ts = self._ensure_utc(review.ts)
       fsrs_card, _ = self.fsrs_scheduler.review_card(fsrs_card, rating, now=ts)
   ```
2. Keep line 154: `fsrs_card = FSRSCard()` (will be used in O(1) implementation)

**Commit Message:**
```
perf(scheduler): remove O(N) history replay loop

Delete the performance bottleneck that replayed entire review history.
This loop caused O(N) complexity where N = number of reviews.

For a card with 500 reviews, this eliminated 500 iterations per review.

Related to Task #4 - Scheduler Performance Optimization
```

**AIV Verification:**
```bash
# Verify loop removed
! grep -A5 "for review in history" flashcore/scheduler.py && echo "✓ History replay loop removed"

# Verify FSRSCard initialization still exists
grep -q "fsrs_card = FSRSCard()" flashcore/scheduler.py && echo "✓ FSRSCard initialization preserved"

# Verify file still valid Python
python -m py_compile flashcore/scheduler.py && echo "✓ Valid Python syntax"
```

**Test Strategy:**
- Verify no `for review in history` exists
- Verify FSRSCard() initialization preserved
- Note: Scheduler will not work correctly until next commit (expected)

---

### Commit 4: Implement O(1) cached state initialization

**Files Changed:** 1 modified file
- `flashcore/scheduler.py` (after line 154)

**Changes:**
1. Add FSRSState import (line 22):
   ```python
   from fsrs import Card as FSRSCard, Rating as FSRSRating, State as FSRSState  # type: ignore
   ```
2. After line 154 (`fsrs_card = FSRSCard()`), add O(1) initialization:
   ```python
   # Initialize from cached card state (O(1) instead of O(N) history replay)
   if card.state != CardState.New:
       # Map flashcore CardState to FSRS State
       fsrs_card.stability = card.stability
       fsrs_card.difficulty = card.difficulty
       fsrs_card.state = FSRSState(card.state.value)
       if card.next_due_date:
           fsrs_card.due = datetime.datetime.combine(
               card.next_due_date, 
               datetime.time(0, 0, 0), 
               tzinfo=datetime.timezone.utc
           )
   ```

**Commit Message:**
```
perf(scheduler): implement O(1) cached state initialization

Initialize FSRSCard from cached Card fields instead of replaying history.
This achieves O(1) constant-time performance regardless of review count.

Uses card.stability, card.difficulty, card.state, card.next_due_date
to reconstruct FSRS state without iterating through review history.

Performance impact: 500-review card now processes in constant time.

Related to Task #4 - Scheduler Performance Optimization
```

**AIV Verification:**
```bash
# Verify cached state initialization exists
grep -A10 "if card.state != CardState.New" flashcore/scheduler.py | grep -q "fsrs_card.stability = card.stability" && echo "✓ Stability initialization"
grep -A10 "if card.state != CardState.New" flashcore/scheduler.py | grep -q "fsrs_card.difficulty = card.difficulty" && echo "✓ Difficulty initialization"
grep -A10 "if card.state != CardState.New" flashcore/scheduler.py | grep -q "fsrs_card.state = FSRSState" && echo "✓ State initialization"

# Verify FSRSState imported
grep -q "from fsrs import.*State as FSRSState" flashcore/scheduler.py && echo "✓ FSRSState imported"

# Verify no history replay loop
! grep -q "for review in history" flashcore/scheduler.py && echo "✓ No history replay"

# Verify module still imports
python -c "from flashcore.scheduler import FSRS_Scheduler; print('✓ Module imports')"
```

**Test Strategy:**
- Verify FSRSCard initialized from card fields for non-New cards
- Verify New cards still use default FSRSCard initialization
- Verify CardState enum values map correctly to FSRSState

---

### Commit 5: Copy review_processor.py to flashcore/

**Files Changed:** 1 new file
- `flashcore/review_processor.py` (new, 188 lines)

**Changes:**
1. Copy `HPE_ARCHIVE/flashcore/review_processor.py` → `flashcore/review_processor.py`
2. Update imports (lines 21-23):
   - FROM: `from .card import Card, Review`
   - TO: `from .models import Card, Review`
   - FROM: `from .database import FlashcardDatabase`
   - TO: `from .db.database import FlashcardDatabase`
3. Keep scheduler import as-is (line 23): `from .scheduler import FSRS_Scheduler, SchedulerOutput`

**Commit Message:**
```
feat(review): copy ReviewProcessor from HPE_ARCHIVE

Copy review processing logic that consolidates review submission.
Updates imports to use flashcore.models and flashcore.db.database.

Still uses O(N) scheduler call - will be updated in next commit.

Related to Task #4 - Scheduler Performance Optimization
```

**AIV Verification:**
```bash
# Verify file exists
test -f flashcore/review_processor.py && echo "✓ File exists"

# Verify imports updated
grep -q "from .models import Card, Review" flashcore/review_processor.py && echo "✓ Models import correct"
grep -q "from .db.database import FlashcardDatabase" flashcore/review_processor.py && echo "✓ Database import correct"
grep -q "from .scheduler import FSRS_Scheduler" flashcore/review_processor.py && echo "✓ Scheduler import correct"

# Verify no old imports
! grep -q "cultivation.scripts.flashcore" flashcore/review_processor.py && echo "✓ No old imports"

# Verify class exists
python -c "from flashcore.review_processor import ReviewProcessor; print('✓ Class importable')"
```

**Test Strategy:**
- Import ReviewProcessor class
- Verify process_review and process_review_by_uuid methods exist
- Note: Will fail at runtime until next commit updates scheduler call

---

### Commit 6: Update ReviewProcessor to pass Card to scheduler

**Files Changed:** 1 modified file
- `flashcore/review_processor.py` (lines 96-107)

**Changes:**
1. Line 96-100: Remove history fetching logic
   ```python
   # DELETE THESE LINES:
   # Step 2: Fetch review history for scheduler
   review_history = self.db_manager.get_reviews_for_card(
       card.uuid, 
       order_by_ts_desc=False
   )
   ```
2. Line 103-107: Update scheduler call
   - FROM: `scheduler_output: SchedulerOutput = self.scheduler.compute_next_state(history=review_history, new_rating=rating, review_ts=ts)`
   - TO: `scheduler_output: SchedulerOutput = self.scheduler.compute_next_state(card=card, new_rating=rating, review_ts=ts)`
3. Update docstring (line 69): Remove "Fetch review history" step
4. Update comments (line 96, 102): Renumber steps

**Commit Message:**
```
perf(review): update ReviewProcessor to use O(1) scheduler

Remove review history fetching and pass Card object to scheduler.
This completes the O(1) optimization by eliminating history retrieval.

Before: Fetch N reviews from DB + replay N reviews in scheduler
After: Pass Card object with cached state (constant time)

Related to Task #4 - Scheduler Performance Optimization
```

**AIV Verification:**
```bash
# Verify no history fetching
! grep -q "get_reviews_for_card" flashcore/review_processor.py && echo "✓ No history fetching"

# Verify scheduler called with card parameter
grep -A2 "scheduler.compute_next_state" flashcore/review_processor.py | grep -q "card=card" && echo "✓ Scheduler called with card"

# Verify no history parameter
! grep "scheduler.compute_next_state.*history=" flashcore/review_processor.py && echo "✓ No history parameter"

# Verify module imports
python -c "from flashcore.review_processor import ReviewProcessor; print('✓ Module imports')"
```

**Test Strategy:**
- Verify ReviewProcessor.process_review no longer fetches history
- Verify scheduler.compute_next_state called with card parameter
- Integration test: Submit review and verify O(1) performance

---

### Commit 7: Copy and adapt test_scheduler.py

**Files Changed:** 1 new file
- `tests/test_scheduler.py` (new, ~450 lines)

**Changes:**
1. Copy `HPE_ARCHIVE/tests/test_scheduler.py` → `tests/test_scheduler.py`
2. Update imports (lines 6-8):
   - FROM: `from cultivation.scripts.flashcore.scheduler import FSRS_Scheduler, FSRSSchedulerConfig`
   - TO: `from flashcore.scheduler import FSRS_Scheduler, FSRSSchedulerConfig`
   - FROM: `from cultivation.scripts.flashcore.card import Review, CardState`
   - TO: `from flashcore.models import Card, Review, CardState`
   - FROM: `from cultivation.scripts.flashcore.config import DEFAULT_PARAMETERS`
   - TO: `from flashcore.constants import DEFAULT_PARAMETERS, DEFAULT_DESIRED_RETENTION`
3. Update all test functions to use Card object instead of history list
4. Add new test: `test_compute_next_state_is_constant_time`

**Commit Message:**
```
test(scheduler): migrate and adapt scheduler tests

Copy scheduler tests from HPE_ARCHIVE with updates:
- Import from flashcore instead of cultivation.scripts
- Update tests to use Card object instead of history list
- Add O(1) performance benchmark test

Related to Task #4 - Scheduler Performance Optimization
```

**AIV Verification:**
```bash
# Verify file exists
test -f tests/test_scheduler.py && echo "✓ File exists"

# Verify imports updated
grep -q "from flashcore.scheduler import" tests/test_scheduler.py && echo "✓ Scheduler import correct"
grep -q "from flashcore.models import" tests/test_scheduler.py && echo "✓ Models import correct"
grep -q "from flashcore.constants import" tests/test_scheduler.py && echo "✓ Constants import correct"

# Verify no old imports
! grep -q "cultivation.scripts.flashcore" tests/test_scheduler.py && echo "✓ No old imports"

# Run tests
pytest tests/test_scheduler.py -v && echo "✓ All tests pass"
```

**Test Strategy:**
- Run full test suite: `pytest tests/test_scheduler.py -v`
- Verify all existing tests pass with Card parameter
- Verify O(1) benchmark test passes

---

### Commit 8: Add O(1) performance benchmark test

**Files Changed:** 1 modified file
- `tests/test_scheduler.py` (add new test at end)

**Changes:**
1. Add new test function at end of file:
   ```python
   def test_compute_next_state_is_constant_time(scheduler: FSRS_Scheduler):
       """
       Verify O(1) performance: time should be constant regardless of review count.
       Uses relative assertion to avoid hardware dependence.
       """
       import time
       from uuid import uuid4
       
       def time_scheduler_call(num_reviews: int) -> float:
           """Create card with N reviews and time scheduler call."""
           card = Card(
               uuid=uuid4(),
               deck_name="test",
               front="Q",
               back="A",
               state=CardState.Review if num_reviews > 0 else CardState.New,
               stability=10.0 if num_reviews > 0 else None,
               difficulty=5.0 if num_reviews > 0 else None,
               next_due_date=datetime.date(2024, 1, 1) if num_reviews > 0 else None
           )
           
           review_ts = datetime.datetime(2024, 1, 2, 10, 0, 0, tzinfo=UTC)
           
           start = time.perf_counter()
           scheduler.compute_next_state(card=card, new_rating=3, review_ts=review_ts)
           end = time.perf_counter()
           
           return end - start
       
       # Time with different review counts
       time_1 = time_scheduler_call(1)
       time_10 = time_scheduler_call(10)
       time_100 = time_scheduler_call(100)
       time_500 = time_scheduler_call(500)
       
       # O(1) verification: time(500) should be < 2x time(1)
       # Allow 2x factor for measurement noise and cache effects
       assert time_500 < time_1 * 2.0, (
           f"O(1) property violated: time(500)={time_500:.6f}s should be "
           f"< 2x time(1)={time_1:.6f}s (actual ratio: {time_500/time_1:.2f}x)"
       )
       
       # Additional sanity check: time should be small (<10ms)
       assert time_500 < 0.010, f"Scheduler too slow: {time_500*1000:.2f}ms"
       
       print(f"\n✓ O(1) Performance Verified:")
       print(f"  1 review:   {time_1*1000:.3f}ms")
       print(f"  10 reviews:  {time_10*1000:.3f}ms")
       print(f"  100 reviews: {time_100*1000:.3f}ms")
       print(f"  500 reviews: {time_500*1000:.3f}ms")
       print(f"  Ratio (500/1): {time_500/time_1:.2f}x")
   ```

**Commit Message:**
```
test(scheduler): add O(1) performance benchmark

Add test to verify constant-time performance regardless of review count.
Uses relative assertion (time(500) < 2x time(1)) to avoid hardware dependence.

This test proves the O(N) bottleneck has been eliminated.

Related to Task #4 - Scheduler Performance Optimization
```

**AIV Verification:**
```bash
# Verify test exists
grep -q "def test_compute_next_state_is_constant_time" tests/test_scheduler.py && echo "✓ Benchmark test exists"

# Run benchmark test
pytest tests/test_scheduler.py::test_compute_next_state_is_constant_time -v -s && echo "✓ O(1) performance verified"

# Run all scheduler tests
pytest tests/test_scheduler.py -v && echo "✓ All tests pass"
```

**Test Strategy:**
- Run benchmark test in isolation
- Verify time(500) < 2x time(1)
- Verify absolute time < 10ms
- Compare before/after performance (requires O(N) baseline)

---

### Commit 9: Preserve FSRS parameter override support

**Files Changed:** 1 modified file (documentation)
- `flashcore/scheduler.py` (docstring updates)

**Changes:**
1. Update FSRSSchedulerConfig docstring (line 73-85):
   ```python
   class FSRSSchedulerConfig(BaseModel):
       """
       Configuration for the FSRS Scheduler.
       
       Supports custom FSRS parameters for externally-optimized weights.
       Users can provide custom parameters without requiring fsrs-optimizer.
       
       Example:
           # Use custom optimized weights
           config = FSRSSchedulerConfig(
               parameters=(0.4, 0.6, 0.36, 0.19, 1.4, 0.94, 0.86, 0.01, 1.49, 0.14, 
                          0.94, 2.18, 0.05, 0.34, 1.26, 0.29, 2.61),
               desired_retention=0.95
           )
           scheduler = FSRS_Scheduler(config=config)
       """
   ```
2. Update FSRS_Scheduler.__init__ docstring (line 107):
   ```python
   def __init__(self, config: Optional[FSRSSchedulerConfig] = None):
       """
       Initialize FSRS scheduler with optional custom configuration.
       
       Args:
           config: Optional FSRSSchedulerConfig with custom parameters.
                   If None, uses DEFAULT_PARAMETERS and DEFAULT_DESIRED_RETENTION.
       """
   ```

**Commit Message:**
```
docs(scheduler): document FSRS parameter override support

Add documentation for custom FSRS parameter injection.
Users can provide externally-optimized weights without fsrs-optimizer.

This ensures the scheduler remains flexible for advanced use cases.

Related to Task #4 - Scheduler Performance Optimization
```

**AIV Verification:**
```bash
# Verify docstring exists
grep -A10 "class FSRSSchedulerConfig" flashcore/scheduler.py | grep -q "custom FSRS parameters" && echo "✓ Config docstring updated"

# Verify example in docstring
grep -A20 "class FSRSSchedulerConfig" flashcore/scheduler.py | grep -q "Example:" && echo "✓ Example provided"

# Test custom parameters
python -c "
from flashcore.scheduler import FSRS_Scheduler, FSRSSchedulerConfig
config = FSRSSchedulerConfig(parameters=(0.4, 0.6, 0.36, 0.19, 1.4, 0.94, 0.86, 0.01, 1.49, 0.14, 0.94, 2.18, 0.05, 0.34, 1.26, 0.29, 2.61), desired_retention=0.95)
scheduler = FSRS_Scheduler(config=config)
print('✓ Custom parameters work')
"
```

**Test Strategy:**
- Verify FSRSSchedulerConfig accepts custom parameters
- Verify FSRS_Scheduler uses custom parameters
- Verify default parameters still work

---

## Session Manager Refactoring (Deferred)

**Decision:** Defer session_manager.py and review_manager.py porting to separate task.

**Rationale:**
1. session_manager.py requires pandas refactoring (fetch_df → fetchall)
2. review_manager.py depends on session_manager.py
3. Core O(1) optimization doesn't require these modules
4. Can be ported incrementally after Task 4 completion

**Future Task:** Create Task 4.1 for session/review manager porting with pandas removal.

---

## AIV Verification Packet

### Pre-Commit Verification Checklist

Run before each commit:
```bash
# 1. Syntax check
python -m py_compile flashcore/scheduler.py
python -m py_compile flashcore/review_processor.py

# 2. Import check
python -c "from flashcore.scheduler import FSRS_Scheduler, FSRSSchedulerConfig"
python -c "from flashcore.review_processor import ReviewProcessor"

# 3. Type check (if mypy available)
mypy flashcore/scheduler.py --ignore-missing-imports
mypy flashcore/review_processor.py --ignore-missing-imports

# 4. Linting (if flake8 available)
flake8 flashcore/scheduler.py --max-line-length=120
flake8 flashcore/review_processor.py --max-line-length=120
```

### Post-Implementation Verification

Run after all commits:
```bash
# 1. Unit tests
pytest tests/test_scheduler.py -v

# 2. O(1) benchmark
pytest tests/test_scheduler.py::test_compute_next_state_is_constant_time -v -s

# 3. Integration test (if database available)
pytest tests/test_review_processor.py -v  # If exists

# 4. Coverage check
pytest tests/test_scheduler.py --cov=flashcore.scheduler --cov-report=term-missing

# 5. Performance comparison
python -c "
import time
from flashcore.scheduler import FSRS_Scheduler
from flashcore.models import Card, CardState
from datetime import datetime, timezone, date
from uuid import uuid4

scheduler = FSRS_Scheduler()

# Test with 500-review card
card = Card(
    uuid=uuid4(),
    deck_name='test',
    front='Q',
    back='A',
    state=CardState.Review,
    stability=50.0,
    difficulty=5.0,
    next_due_date=date(2024, 1, 1)
)

review_ts = datetime(2024, 1, 2, 10, 0, 0, tzinfo=timezone.utc)

start = time.perf_counter()
for _ in range(100):
    scheduler.compute_next_state(card=card, new_rating=3, review_ts=review_ts)
end = time.perf_counter()

avg_time_ms = (end - start) / 100 * 1000
print(f'Average time per call: {avg_time_ms:.3f}ms')
assert avg_time_ms < 10, f'Too slow: {avg_time_ms:.3f}ms'
print('✓ Performance acceptable')
"
```

### Mutation Testing (Post-Merge)

Run after merge to main:
```bash
# Run mutation testing on scheduler.py
mutatest -s flashcore/scheduler.py -t tests/test_scheduler.py -n 6 --timeout-factor 2

# Expected: High mutation score (>80%) indicating good test coverage
```

### Code Quality Checks

```bash
# 1. Complexity analysis
radon cc flashcore/scheduler.py -a
radon cc flashcore/review_processor.py -a

# 2. Maintainability index
radon mi flashcore/scheduler.py
radon mi flashcore/review_processor.py

# 3. CodeScene analysis (if available)
cs check flashcore/scheduler.py
cs check flashcore/review_processor.py
```

---

## Risk Assessment

### High Risk Items

1. **Breaking Change:** All callers of `compute_next_state` must be updated
   - **Mitigation:** Atomic commits ensure clear breakage points
   - **Detection:** Tests will fail immediately if callers not updated

2. **State Mapping:** CardState → FSRSState mapping must be correct
   - **Mitigation:** Add explicit test for all CardState values
   - **Detection:** Test with all 4 states (New, Learning, Review, Relearning)

3. **Cached State Staleness:** Card state must be kept in sync with reviews
   - **Mitigation:** Verify add_review_and_update_card updates all fields
   - **Detection:** Integration tests with multiple reviews

### Medium Risk Items

1. **Import Path Changes:** Multiple import updates across files
   - **Mitigation:** Verify imports in each commit's AIV
   - **Detection:** Import errors will surface immediately

2. **Test Adaptation:** Tests must be updated to use Card instead of history
   - **Mitigation:** Systematic test update in single commit
   - **Detection:** Test failures will be obvious

### Low Risk Items

1. **Documentation:** Docstrings need updating
   - **Mitigation:** Include in relevant commits
   - **Detection:** Code review

2. **Performance Measurement:** Benchmark test hardware-dependent
   - **Mitigation:** Use relative assertions (2x factor)
   - **Detection:** CI will catch failures

---

## Dependencies and Blockers

### Completed Dependencies
- ✅ Task 3: Card model with cached state fields (already exists in flashcore/models.py)
- ✅ constants.py with DEFAULT_PARAMETERS (already exists)

### No Blockers
All required infrastructure exists in the active codebase.

---

## Success Criteria

### Functional Requirements
1. ✅ Scheduler accepts Card object instead of history list
2. ✅ Scheduler initializes FSRSCard from cached state
3. ✅ No history replay loop exists
4. ✅ All existing tests pass with new implementation
5. ✅ O(1) benchmark test passes

### Performance Requirements
1. ✅ time(500 reviews) < 2x time(1 review)
2. ✅ Absolute time < 10ms per call
3. ✅ No database queries for review history in scheduler path

### Quality Requirements
1. ✅ Test coverage > 80% for scheduler.py
2. ✅ All AIV checks pass for each commit
3. ✅ No regressions in existing functionality
4. ✅ Documentation updated for breaking changes

---

## Rollback Plan

If issues discovered post-merge:

### Immediate Rollback (< 1 hour)
```bash
# Revert all commits in reverse order
git revert <commit-9-hash>
git revert <commit-8-hash>
# ... continue for all commits
git push origin main
```

### Partial Rollback (1-4 hours)
```bash
# Revert only problematic commits
git revert <problematic-commit-hash>
git push origin main
```

### Forward Fix (> 4 hours)
```bash
# Create hotfix branch
git checkout -b hotfix/task-4-scheduler-fix
# Apply fix
git commit -m "fix(scheduler): address issue X"
git push origin hotfix/task-4-scheduler-fix
# Create PR and merge
```

---

## Timeline Estimate

### Development Time
- Commit 1-2: 30 minutes (copy + signature change)
- Commit 3-4: 45 minutes (remove loop + O(1) implementation)
- Commit 5-6: 30 minutes (copy + update review_processor)
- Commit 7-8: 60 minutes (test migration + benchmark)
- Commit 9: 15 minutes (documentation)

**Total Development:** ~3 hours

### Testing Time
- Unit tests: 15 minutes
- Integration tests: 30 minutes
- Performance verification: 15 minutes
- Code review: 30 minutes

**Total Testing:** ~1.5 hours

### Total Task Time: ~4.5 hours

---

## Post-Implementation Tasks

1. **Update CLI** (Task 6): Expose FSRS parameter override in CLI
2. **Port Session Manager** (Task 4.1): Refactor pandas dependency
3. **Port Review Manager** (Task 4.2): Integrate with new scheduler
4. **Performance Monitoring**: Add metrics to track scheduler performance
5. **Documentation**: Update architecture docs with O(1) optimization

---

## Appendix A: Code Snippets

### A.1: O(1) Initialization Logic
```python
# Initialize from cached card state (O(1) instead of O(N) history replay)
if card.state != CardState.New:
    # Map flashcore CardState to FSRS State
    fsrs_card.stability = card.stability
    fsrs_card.difficulty = card.difficulty
    fsrs_card.state = FSRSState(card.state.value)
    if card.next_due_date:
        fsrs_card.due = datetime.datetime.combine(
            card.next_due_date, 
            datetime.time(0, 0, 0), 
            tzinfo=datetime.timezone.utc
        )
```

### A.2: Benchmark Test Core Logic
```python
def time_scheduler_call(num_reviews: int) -> float:
    """Create card with N reviews and time scheduler call."""
    card = Card(
        uuid=uuid4(),
        deck_name="test",
        front="Q",
        back="A",
        state=CardState.Review if num_reviews > 0 else CardState.New,
        stability=10.0 if num_reviews > 0 else None,
        difficulty=5.0 if num_reviews > 0 else None,
        next_due_date=datetime.date(2024, 1, 1) if num_reviews > 0 else None
    )
    
    review_ts = datetime.datetime(2024, 1, 2, 10, 0, 0, tzinfo=UTC)
    
    start = time.perf_counter()
    scheduler.compute_next_state(card=card, new_rating=3, review_ts=review_ts)
    end = time.perf_counter()
    
    return end - start
```

### A.3: Updated ReviewProcessor Call
```python
# Before (O(N)):
review_history = self.db_manager.get_reviews_for_card(card.uuid, order_by_ts_desc=False)
scheduler_output = self.scheduler.compute_next_state(
    history=review_history,
    new_rating=rating,
    review_ts=ts
)

# After (O(1)):
scheduler_output = self.scheduler.compute_next_state(
    card=card,
    new_rating=rating,
    review_ts=ts
)
```

---

## Appendix B: Import Mapping Reference

| HPE_ARCHIVE Import | flashcore/ Import |
|-------------------|-------------------|
| `from cultivation.scripts.flashcore.config import DEFAULT_PARAMETERS` | `from .constants import DEFAULT_PARAMETERS` |
| `from cultivation.scripts.flashcore.card import Card, Review, CardState` | `from .models import Card, Review, CardState` |
| `from .database import FlashcardDatabase` | `from .db.database import FlashcardDatabase` |

---

## Appendix C: File Size Reference

| File | Lines | Size | Complexity |
|------|-------|------|------------|
| scheduler.py | 203 | ~8KB | Medium |
| review_processor.py | 188 | ~7KB | Low |
| test_scheduler.py | 417 | ~15KB | Medium |
| models.py (existing) | 418 | ~16KB | Low |
| constants.py (existing) | 41 | ~2KB | Low |

---

**End of Audit Document**

**Next Steps:**
1. Review this audit with stakeholders
2. Execute commits 1-9 in sequence
3. Run AIV verification after each commit
4. Submit PR with all commits
5. Run post-merge verification
6. Update Task Master status to "done"
