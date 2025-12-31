# Task ID: 9

**Title:** Finalize and Document Migration

**Status:** pending

**Dependencies:** 8

**Priority:** medium

**Description:** Complete the migration process and document the new architecture and usage.

**Details:**

CRITICAL (PRD Section 4 Feature Branch Workflow): Remove HPE_ARCHIVE/ directory before final merge. Execute: 'git rm -r HPE_ARCHIVE/' and commit with message 'chore(repo): Remove HPE_ARCHIVE after successful pivot'. Document in README.md: (1) Installation: 'pip install flashcore', (2) Usage examples with explicit db_path, (3) Architecture: Hub-and-Spoke model, (4) Dependency constraints (no torch/fsrs-optimizer), (5) Migration guide from old system. Update pyproject.toml metadata (setup.py is deprecated/removed). PRD Section 5 Verification Checklist: Confirm no torch or fsrs-optimizer in pyproject.toml dependencies, pytest tests/ passes (all tests), flashcore CLI ingest/review/stats runs without error on migrated sample data, and assets referenced by YAML (images/audio) load correctly.

**Test Strategy:**

Verify HPE_ARCHIVE/ does not exist in git tree. README.md contains installation, usage, architecture, and migration guide sections. Confirm: (1) No torch/transformers/fsrs-optimizer in dependencies, (2) pytest tests/ passes, (3) flashcore CLI ingest/review/stats works on migrated sample data, (4) images/audio referenced in YAML load correctly.

## Subtasks

### 9.1. Remove HPE_ARCHIVE Before Final Merge

**Status:** pending  
**Dependencies:** None  

Remove legacy archive directory to prevent dual source-of-truth confusion.

**Details:**

Execute: git rm -r HPE_ARCHIVE/ and commit with message 'chore(repo): Remove HPE_ARCHIVE after successful pivot'.

### 9.2. Update README and Documentation

**Status:** pending  
**Dependencies:** 9.1  

Document installation, usage, architecture, constraints, and migration guide.

**Details:**

Update README.md: installation, usage examples with explicit db_path, architecture (Hub-and-Spoke), dependency constraints (no torch/transformers/fsrs-optimizer), and migration guide.

### 9.3. Run Verification Checklist

**Status:** pending  
**Dependencies:** 9.2  

Run PRD Section 5 verification checklist with explicit, testable criteria.

**Details:**

Confirm: (1) No torch/transformers/fsrs-optimizer in dependencies, (2) pytest tests/ passes, (3) flashcore CLI ingest/review/stats runs on migrated sample data, (4) assets referenced by YAML load correctly.
