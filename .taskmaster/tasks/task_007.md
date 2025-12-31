# Task ID: 7

**Title:** Migrate and Adapt Test Suite

**Status:** pending

**Dependencies:** 6

**Priority:** high

**Description:** Transfer and adapt the existing test suite to the new library structure.

**Details:**

Copy HPE_ARCHIVE/tests/ to tests/ directory. PRD Section 4 Phase 2 Step 5 emphasizes the test suite is a 'high-value asset' with architectural regression tests. Priority tests to migrate: test_database.py (includes TestIngestionBugReproduction), test_scheduler.py (verify O(1) optimization), test_yaml_processor.py (verify stateless behavior), test_rating_system_inconsistency.py, test_session_analytics_gaps.py. Update imports from 'cultivation.scripts.flashcore' to 'flashcore'. Update fixtures to use temp databases with explicit paths (no config.settings).

**Test Strategy:**

Run 'pytest tests/ -v' - all tests should pass. Verify test coverage >80% with 'pytest --cov=flashcore tests/'.
