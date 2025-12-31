# Task ID: 2

**Title:** Migrate Core Data Models

**Status:** pending

**Dependencies:** 1

**Priority:** medium

**Description:** Transfer and refactor core data models from HPE_ARCHIVE to the new library structure.

**Details:**

Copy HPE_ARCHIVE/flashcore/card.py to flashcore/models.py. This file contains Card, Review, Session, and CardState models using Pydantic v2. Remove all imports referencing 'cultivation.scripts.flashcore' and replace with relative imports (e.g., 'from .db import ...'). Ensure Pydantic v2 syntax is maintained (Field, model_validate, model_dump). PRD Phase 2 Step 1.

**Test Strategy:**

Import models.py and instantiate Card/Review objects. Run 'python -c "from flashcore.models import Card, Review, Session, CardState"' to verify no import errors.

## Subtasks

### 2.1. Copy card.py to models.py

**Status:** pending  
**Dependencies:** None  

Transfer the Card, Review, Session, and CardState models from HPE_ARCHIVE.

**Details:**

Execute: cp HPE_ARCHIVE/flashcore/card.py flashcore/models.py. This is the foundation data layer.

### 2.2. Remove Cultivation Import References

**Status:** pending  
**Dependencies:** 2.1  

Replace absolute imports with relative imports for library portability.

**Details:**

Search for 'from cultivation.scripts.flashcore' in models.py and replace with relative imports. Example: 'from cultivation.scripts.flashcore.config import X' becomes 'from .config import X' or remove if not needed.

### 2.3. Verify Pydantic v2 Compatibility

**Status:** pending  
**Dependencies:** 2.2  

Ensure all Pydantic models use v2 syntax (no deprecated v1 patterns).

**Details:**

Check for: Field() usage, model_validate() instead of parse_obj(), model_dump() instead of dict(). Verify ConfigDict is used instead of class Config.

### 2.4. Add Type Hints and Documentation

**Status:** pending  
**Dependencies:** 2.3  

Ensure all models have complete type hints and docstrings.

**Details:**

Verify Card, Review, Session classes have docstrings explaining their purpose. Ensure all fields have type annotations.

### 2.5. Copy config.py for FSRS Constants

**Status:** pending  
**Dependencies:** 2.4  

Transfer FSRS configuration constants from HPE_ARCHIVE.

**Details:**

Execute: cp HPE_ARCHIVE/flashcore/config.py flashcore/config.py. CRITICAL: Remove Settings class and all path defaults (db_path, yaml_source_dir, assets_dir, export_dir, user_uuid) - these violate DI pattern. KEEP ONLY: DEFAULT_PARAMETERS (lines 58-80) and DEFAULT_DESIRED_RETENTION (line 83). These FSRS constants are imported by scheduler.py line 16-19. The library must not contain hardcoded paths.

### 2.6. Create __init__.py Exports

**Status:** pending  
**Dependencies:** 2.5  

Expose models in flashcore/__init__.py for clean imports.

**Details:**

Add to flashcore/__init__.py: 'from .models import Card, Review, Session, CardState, ReviewRating'. This allows 'from flashcore import Card'.
