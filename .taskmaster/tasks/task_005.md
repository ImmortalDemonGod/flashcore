# Task ID: 5

**Title:** Refactor Parser Layer to be Stateless

**Status:** pending

**Dependencies:** 3

**Priority:** medium

**Description:** Remove stateful logic from the parser and centralize deduplication checks.

**Details:**

STATELESS REFACTOR (PRD Section 2 Finding 3): HPE_ARCHIVE/flashcore/yaml_processing/yaml_processor.py line 40 contains 'self.seen_questions: Dict[str, Path] = {}' - this is ephemeral state that creates split-brain deduplication. The YAMLProcessor should be a pure function: File -> List[Card]. Remove self.seen_questions entirely. Move ALL deduplication logic to the CLI ingest command, which should query db.get_all_card_fronts_and_uuids() BEFORE processing to get authoritative list, then filter YAMLProcessor output against this list.

**Test Strategy:**

Instantiate YAMLProcessor, call process_file() twice on same file - should return identical results (no state carried between calls). Verify 'grep -n seen_questions flashcore/parser.py' returns no results.

## Subtasks

### 5.1. Copy yaml_processor.py to flashcore/parser.py

**Status:** pending  
**Dependencies:** None  

Transfer the YAML processing module from HPE_ARCHIVE.

**Details:**

Execute: cp HPE_ARCHIVE/flashcore/yaml_processing/yaml_processor.py flashcore/parser.py. Also copy yaml_models.py if it contains necessary Pydantic models for YAML validation.

### 5.2. Remove self.seen_questions State Variable

**Status:** pending  
**Dependencies:** 5.1  

Delete the stateful seen_questions dictionary from YAMLProcessor.__init__.

**Details:**

In parser.py line 40, delete 'self.seen_questions: Dict[str, Path] = {}'. Also remove all references to self.seen_questions in _handle_processed_card method (lines 99-110). The parser should not track duplicates.

### 5.3. Add parser.py to __init__.py Exports

**Status:** pending  
**Dependencies:** 5.2  

Expose YAMLProcessor in flashcore/__init__.py.

**Details:**

Add to flashcore/__init__.py: 'from .parser import YAMLProcessor, YAMLProcessorConfig'. This allows 'from flashcore import YAMLProcessor'.
