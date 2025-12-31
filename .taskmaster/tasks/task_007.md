# Task ID: 7

**Title:** Migrate Integration and Architectural Regression Tests

**Status:** pending

**Dependencies:** 6

**Priority:** high

**Description:** Transfer integration tests and architectural regression tests to verify end-to-end functionality.

**Details:**

Since unit tests are now migrated incrementally (Tasks 2-5), this task focuses on: (1) CLI Integration Tests - copy HPE_ARCHIVE/tests/cli/ to tests/cli/ for end-to-end CLI command testing. (2) Architectural Regression Tests - copy test_rating_system_inconsistency.py, test_session_analytics_gaps.py, test_review_logic_duplication.py (PRD Section 4 Phase 2 Step 5 calls these 'high-value assets' documenting past flaws). (3) Service Layer Tests - copy test_review_processor.py, test_review_manager.py, test_session_manager.py. Update all imports from 'cultivation.scripts.flashcore' to 'flashcore'. Update fixtures to use explicit db_path.

**Test Strategy:**

Run 'pytest tests/ -v' - all tests pass including integration and regression tests. Verify test coverage >80% with 'pytest --cov=flashcore tests/'. Run CLI integration tests to verify end-to-end workflows.

## Subtasks

### 7.1. Migrate CLI Integration Tests

**Status:** pending  
**Dependencies:** None  

Copy CLI integration tests to verify end-to-end command functionality.

**Details:**

Execute: cp -r HPE_ARCHIVE/tests/cli/ tests/cli/. These tests verify the full CLI workflow (ingest, review, stats commands). Update imports and ensure tests use explicit --db flags (no config.settings).

### 7.2. Migrate Architectural Regression Tests

**Status:** pending  
**Dependencies:** None  

Copy tests that document and prevent past architectural flaws.

**Details:**

Copy: test_rating_system_inconsistency.py, test_session_analytics_gaps.py, test_review_logic_duplication.py. PRD emphasizes these are 'invaluable architectural regression tests' that validate fixes for past bugs. Update imports to 'flashcore'.

### 7.3. Migrate Service Layer Tests

**Status:** pending  
**Dependencies:** None  

Copy tests for ReviewProcessor, ReviewManager, SessionManager.

**Details:**

Copy: test_review_processor.py, test_review_manager.py, test_session_manager.py, test_session_model.py. These test the service orchestration layer. Update imports to the new module layout: flashcore.review_processor, flashcore.review_manager, flashcore.session_manager.

### 7.4. Copy conftest.py and Shared Fixtures

**Status:** pending  
**Dependencies:** 7.1, 7.2, 7.3  

Migrate shared test fixtures and configuration.

**Details:**

Copy HPE_ARCHIVE/tests/conftest.py to tests/conftest.py. Update fixtures to use explicit db_path (tmp_path / 'test.db') instead of config.settings. Ensure pytest configuration is correct.

### 7.5. Run Full Test Suite and Verify Coverage

**Status:** pending  
**Dependencies:** 7.4  

Execute complete test suite and verify coverage meets PRD requirements.

**Details:**

Run 'pytest tests/ -v' to execute all tests (unit + integration + regression). Run 'pytest --cov=flashcore tests/' to verify >80% coverage. All tests should pass, proving the refactoring is correct and safe.
