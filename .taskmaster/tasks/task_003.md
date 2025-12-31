# Task ID: 3

**Title:** Refactor Database Layer for Dependency Injection

**Status:** pending

**Dependencies:** 2

**Priority:** high

**Description:** Modify the database layer to eliminate hardcoded paths and enforce dependency injection.

**Details:**

Port the database subsystem from HPE_ARCHIVE into a flashcore/db/ package (NOT a single db.py). CRITICAL REFACTOR (PRD Section 2.B): FlashcardDatabase.`__init__` currently accepts Optional[db_path] and defaults to config.settings (line 44). Change signature to REQUIRE db_path: `def __init__(self, db_path: Union[str, Path], read_only: bool = False)`. Remove all references to config.settings. This enforces the 'Hardcoded Life' fix.

**Test Strategy:**

Instantiate FlashcardDatabase without db_path argument - should raise TypeError. Instantiate with explicit path - should succeed. Run: 'python -c "from flashcore.db import FlashcardDatabase; FlashcardDatabase()"' should fail.

## Subtasks

### 3.1. Create Database Package Structure

**Status:** pending  
**Dependencies:** None  

Port database subsystem to flashcore/db/ package maintaining separation of concerns.

**Details:**

Create directory: mkdir -p flashcore/db. Copy modules: cp HPE_ARCHIVE/flashcore/database.py flashcore/db/database.py; cp HPE_ARCHIVE/flashcore/connection.py flashcore/db/connection.py; cp HPE_ARCHIVE/flashcore/schema_manager.py flashcore/db/schema_manager.py; cp HPE_ARCHIVE/flashcore/db_utils.py flashcore/db/db_utils.py; cp HPE_ARCHIVE/flashcore/schema.py flashcore/db/schema.py. Also copy shared exceptions: cp HPE_ARCHIVE/flashcore/exceptions.py flashcore/exceptions.py (required by DB + CLI). Create `flashcore/db/__init__.py` that exports ONLY: 'from .database import FlashcardDatabase' (keep other modules internal). This maintains architectural separation (focused modules) rather than creating a monolithic 1000+ line file.

### 3.2. Remove config.settings Dependency

**Status:** pending  
**Dependencies:** 3.1  

Eliminate all imports and references to config.settings from db package modules.

**Details:**

In flashcore/db/database.py line 44, `__init__` has 'db_path: Optional[Union[str, Path]] = None' and defaults to settings. Remove this default. In flashcore/db/connection.py line 6, remove 'from .config import settings' import and line 16 'self.db_path_resolved = settings.db_path'. The library must not know about config files.

### 3.3. Make db_path Required Argument

**Status:** pending  
**Dependencies:** 3.2  

Change FlashcardDatabase.`__init__` signature to require db_path.

**Details:**

Change signature from `def __init__(self, db_path: Optional[Union[str, Path]] = None, ...)` to `def __init__(self, db_path: Union[str, Path], read_only: bool = False)`. Update docstring to reflect: db_path is required (no default), accepted types are Union[str, Path], path resolution expectations (cwd vs absolute), and that the path must be writable unless read_only=True.

### 3.4. Update ConnectionHandler for DI

**Status:** pending  
**Dependencies:** 3.3  

Ensure ConnectionHandler also requires db_path and doesn't default to config.

**Details:**

Review ConnectionHandler.`__init__` in connection.py. If it also has Optional db_path with config default, apply same refactor. Ensure it receives db_path from FlashcardDatabase.

### 3.5. Add db Package to `__init__.py` Exports

**Status:** pending  
**Dependencies:** 3.4  

Expose FlashcardDatabase from db package in `flashcore/__init__.py`.

**Details:**

Add to `flashcore/__init__.py`: 'from .db import FlashcardDatabase'. The `db/__init__.py` already exports FlashcardDatabase from .database, so this import works cleanly. This allows 'from flashcore import FlashcardDatabase'.

### 3.6. Remove pandas Dependency from Database Layer

**Status:** pending  
**Dependencies:** 3.5  

Refactor DB queries to avoid pandas (keep dependency footprint small).

**Details:**

HPE_ARCHIVE database layer uses DuckDB's fetch_df() which requires pandas. Refactor flashcore/db/database.py and flashcore/db/db_utils.py to avoid pandas entirely: replace fetch_df() calls with fetchall()/fetchone() and construct row dicts using cursor.description for column names. Remove any pandas imports/usages (e.g., pd.isna) and update marshalling accordingly.

### 3.7. Migrate Database Tests with DI Fixtures (Incremental Verification)

**Status:** pending  
**Dependencies:** 3.6  

Copy and adapt test_database.py to verify DI refactoring works correctly.

**Details:**

Execute: cp HPE_ARCHIVE/tests/test_database.py tests/test_db.py. CRITICAL FIXTURE UPDATE: Replace all fixtures that use 'FlashcardDatabase()' with 'FlashcardDatabase(db_path=tmp_path / "test.db")'. Update conftest.py to provide tmp_path fixture. Update imports from `cultivation.scripts.flashcore` to `flashcore`. This verifies Dependency Injection works and provides safety net for DB refactoring. Also copy test_database_errors.py for error handling tests.
