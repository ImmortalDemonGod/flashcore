# Task ID: 3

**Title:** Refactor Database Layer for Dependency Injection

**Status:** pending

**Dependencies:** 2

**Priority:** high

**Description:** Modify the database layer to eliminate hardcoded paths and enforce dependency injection.

**Details:**

Copy HPE_ARCHIVE/flashcore/database.py, connection.py, schema_manager.py, db_utils.py to flashcore/db.py (consolidate into single module). CRITICAL REFACTOR (PRD Section 2.B): FlashcardDatabase.__init__ currently accepts Optional[db_path] and defaults to config.settings (line 44). Change signature to REQUIRE db_path: 'def __init__(self, db_path: Union[str, Path], read_only: bool = False)'. Remove all references to config.settings. This enforces the 'Hardcoded Life' fix.

**Test Strategy:**

Instantiate FlashcardDatabase without db_path argument - should raise TypeError. Instantiate with explicit path - should succeed. Run: 'python -c "from flashcore.db import FlashcardDatabase; FlashcardDatabase()"' should fail.

## Subtasks

### 3.1. Consolidate Database Modules into db.py

**Status:** pending  
**Dependencies:** None  

Merge database.py, connection.py, schema_manager.py, db_utils.py into single flashcore/db.py.

**Details:**

Copy HPE_ARCHIVE/flashcore/database.py as base. Inline ConnectionHandler, SchemaManager classes from their respective files. Keep as internal helpers. This simplifies the library structure per PRD Section 3.1.

### 3.2. Remove config.settings Dependency

**Status:** pending  
**Dependencies:** 3.1  

Eliminate all imports and references to config.settings from db.py.

**Details:**

In HPE_ARCHIVE/flashcore/database.py line 44, __init__ has 'db_path: Optional[Union[str, Path]] = None' and defaults to settings. Remove this default. Delete 'from .config import settings' import. The library must not know about config files.

### 3.3. Make db_path Required Argument

**Status:** pending  
**Dependencies:** 3.2  

Change FlashcardDatabase.__init__ signature to require db_path.

**Details:**

Change signature from 'def __init__(self, db_path: Optional[Union[str, Path]] = None, ...)' to 'def __init__(self, db_path: Union[str, Path], read_only: bool = False)'. Update docstring to reflect this is now required.

### 3.4. Update ConnectionHandler for DI

**Status:** pending  
**Dependencies:** 3.3  

Ensure ConnectionHandler also requires db_path and doesn't default to config.

**Details:**

Review ConnectionHandler.__init__ in connection.py. If it also has Optional db_path with config default, apply same refactor. Ensure it receives db_path from FlashcardDatabase.

### 3.5. Add db.py to __init__.py Exports

**Status:** pending  
**Dependencies:** 3.4  

Expose FlashcardDatabase in flashcore/__init__.py.

**Details:**

Add to flashcore/__init__.py: 'from .db import FlashcardDatabase'. This allows 'from flashcore import FlashcardDatabase'.

### 3.6. Migrate Database Tests with DI Fixtures (Incremental Verification)

**Status:** pending  
**Dependencies:** 3.5  

Copy and adapt test_database.py to verify DI refactoring works correctly.

**Details:**

Execute: cp HPE_ARCHIVE/tests/test_database.py tests/test_db.py. CRITICAL FIXTURE UPDATE: Replace all fixtures that use 'FlashcardDatabase()' with 'FlashcardDatabase(db_path=tmp_path / "test.db")'. Update conftest.py to provide tmp_path fixture. Update imports from 'cultivation.scripts.flashcore' to 'flashcore'. This verifies Dependency Injection works and provides safety net for DB refactoring. Also copy test_database_errors.py for error handling tests.
