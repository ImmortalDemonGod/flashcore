# AIV Verification Packet (v2.2)

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/ImmortalDemonGod/flashcore |
| **Change ID** | flashcore-f140-adopt-d9f96b3 |
| **Commits** | `d9f96b3` |
| **Head SHA** | `31af2be1e52209136cc4f766fcb7c5b3adaca8c9` |
| **Created** | 2026-06-26T00:00:00Z |

## Classification

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "operator mid-drive adoption — red-test addition (test-only, new file)"
  classification_rationale: "R1: adoption of operator out-of-band commit on PR branch; adds a new test file"
  classified_by: "pipeline-adopt-stage"
  classified_at: "2026-06-26T00:00:00Z"
```

## Claims

1. Commit d9f96b3 added a new file `tests/test_db_row_to_review_error.py` that was not present at the parent commit (42f51de).
2. d9f96b3 also added `.github/aiv-evidence/EVIDENCE_TESTS_TEST_DB_ROW_TO_REVIEW_ERROR.md` — a metadata stub, not a functional file.
3. The test introduced by d9f96b3 was intentionally RED at the time of the commit (the implementation at d9f96b3 did not yet wrap ValidationError in MarshallingError).
4. The broken import path (`flashcore.errors`) in d9f96b3's version of the file was corrected by a subsequent operator commit (f418ec6), which has its own adopt packet (`PACKET_flashcore-f140-adopt-f418ec6.md`).
5. Branch HEAD is correct after adopting d9f96b3 — the test (at its corrected HEAD content) PASSES and no existing tests were broken.
6. The adoption aligns with the canonical intent for finding F140.

## What d9f96b3 Did

d9f96b3 introduced two new files:

### 1. `tests/test_db_row_to_review_error.py` (functional — new red test)

This file was not present at the parent commit (`42f51de`). d9f96b3 created it:

```python
import pytest
from flashcore.db.db_utils import db_row_to_review
from flashcore.errors import MarshallingError   # BROKEN: module does not exist
from pydantic import ValidationError

def test_db_row_to_review_missing_validation_error_wrapper():
    """Bug B1: Missing ValidationError wrapper causes raw ValidationError to escape.
    The test expects a MarshallingError, but the current implementation raises ValidationError.
    """
    bad_row = {"rating": "not a number"}  # Assuming Review expects an int rating
    with pytest.raises(MarshallingError):
        db_row_to_review(bad_row)
```

Key details:
- `from flashcore.errors import MarshallingError` was a **broken import** — `flashcore.errors` does not exist (the correct path is `flashcore.db.errors`). This caused `ModuleNotFoundError` at collection time.
- The test was intentionally RED: at d9f96b3, `db_row_to_review` was `return Review(**row_dict)` with no try/except, so even with a correct import the test would have failed.
- This served as a documentation artifact locking the B1 bug in the gate.

The broken import was corrected by a subsequent operator commit **f418ec6** (adopted under `PACKET_flashcore-f140-adopt-f418ec6.md`), which changed the import to `from flashcore.db.errors import MarshallingError, ReviewOperationError` and refined the test logic. At HEAD, the file content is the f418ec6 version.

### 2. `.github/aiv-evidence/EVIDENCE_TESTS_TEST_DB_ROW_TO_REVIEW_ERROR.md` (metadata — aiv evidence stub)

A pre-existing aiv-evidence stub committed alongside the test by the operator pipeline. Not a functional file; documents the operator's claims and links to Class E intent.

## Why HEAD is Correct

- At baseline (`42f51de`), `tests/test_db_row_to_review_error.py` did not exist — this is a pure addition.
- d9f96b3's test had a broken import (`flashcore.errors`), intentional for a "red test" artifact. f418ec6 corrected the import (see `PACKET_flashcore-f140-adopt-f418ec6.md`).
- At HEAD, `db_row_to_review` (`flashcore/db/db_utils.py:152-163`) wraps `ValidationError` in `MarshallingError` with `from e` (exception chaining), so the F140 invariant holds.
- The test at HEAD PASSES: 1 passed in 0.04s (EXIT 0).
- No existing passing tests were broken: 495 pass, 1 skip at HEAD.

---

## Evidence

### Class A — Behavioral / Direct

**Baseline (d9f96b3^ = 42f51de) — file did not exist:**
```
$ git show 42f51def0cd3dbb7ff6e986b0125a99d528c3b35:tests/test_db_row_to_review_error.py

fatal: path 'tests/test_db_row_to_review_error.py' exists on disk,
      but not in '42f51def0cd3dbb7ff6e986b0125a99d528c3b35'

# File introduced by d9f96b3 — zero tests at baseline for this file.
```
Full output: `.github/aiv-packets/evidence/flashcore-f140/adopt_d9f96b3_baseline.txt`

**HEAD (31af2be1) — test passes:**
```
$ pytest tests/test_db_row_to_review_error.py -v --tb=long

tests/test_db_row_to_review_error.py::test_db_row_to_review_missing_validationerror_wrapper PASSED

1 passed in 0.04s — EXIT CODE: 0
```
Full output: `.github/aiv-packets/evidence/flashcore-f140/adopt_d9f96b3_head.txt`

**Direct functional probe at HEAD:**
```python
from flashcore.db.db_utils import db_row_to_review
from flashcore.db.errors import MarshallingError
from pydantic import ValidationError
row = {"id": 1, "user_id": 2, "comment": "test"}  # missing rating
try:
    db_row_to_review(row)
except MarshallingError as e:
    print(f"MarshallingError raised. 'rating' in str(e): {'rating' in str(e)}")
    print(f"__cause__ is ValidationError: {isinstance(e.__cause__, ValidationError)}")
```
```
MarshallingError raised. 'rating' in str(e): True
__cause__ is ValidationError: True
```

**Full regression suite at HEAD:**
```
$ pytest tests/ -q --tb=short
495 passed, 1 skipped in 32.12s — EXIT CODE: 0
```
Full output: `.github/aiv-packets/evidence/flashcore-f140/adopt_d9f96b3_fullsuite.txt`

### Class B — Referential Evidence (SHA-pinned)

**Scope inventory at HEAD (SHA: [`31af2be1e52209136cc4f766fcb7c5b3adaca8c9`](https://github.com/ImmortalDemonGod/flashcore/tree/31af2be1e52209136cc4f766fcb7c5b3adaca8c9)):**

- [`tests/test_db_row_to_review_error.py#L1-L13`](https://github.com/ImmortalDemonGod/flashcore/blob/31af2be1e52209136cc4f766fcb7c5b3adaca8c9/tests/test_db_row_to_review_error.py#L1-L13) — full test file (HEAD content, corrected by f418ec6)
- [`tests/test_db_row_to_review_error.py#L7-L13`](https://github.com/ImmortalDemonGod/flashcore/blob/31af2be1e52209136cc4f766fcb7c5b3adaca8c9/tests/test_db_row_to_review_error.py#L7-L13) — test function body
- [`flashcore/db/db_utils.py#L152-L163`](https://github.com/ImmortalDemonGod/flashcore/blob/31af2be1e52209136cc4f766fcb7c5b3adaca8c9/flashcore/db/db_utils.py#L152-L163) — `db_row_to_review` with `ValidationError → MarshallingError` wrapper

**Diff introduced by d9f96b3 (SHA-pinned to adopted commit):**

- [`tests/test_db_row_to_review_error.py` at d9f96b3](https://github.com/ImmortalDemonGod/flashcore/blob/d9f96b36478269160150a87fe5e42973701d6409/tests/test_db_row_to_review_error.py) — new file (12 lines, broken import)

### Class C — Negative Evidence

**What was searched and NOT found:**

1. **`tests/test_db_row_to_review_error.py` at d9f96b3^ (42f51de)** — `git show 42f51de:tests/test_db_row_to_review_error.py` → `fatal: path ... exists on disk, but not in '42f51de'`. Confirmed pure addition; no pre-existing test was overwritten.

2. **Other occurrences of `test_db_row_to_review_missing_validation_error_wrapper` outside the new file** — searched `tests/` for the original function name; present only in the history of `tests/test_db_row_to_review_error.py`. No duplication.

3. **Any test file deleted or modified by d9f96b3** — `git show d9f96b3 --stat` shows only two files added (zero modified or deleted). No existing test was removed or altered.

4. **`flashcore.errors` as a valid module at HEAD** — `python -c "import flashcore.errors"` → `ModuleNotFoundError`. Confirmed: d9f96b3's original import was broken; correction was made by f418ec6.

5. **Raw `pydantic.ValidationError` escaping from `db_row_to_review` at HEAD** — `db_utils.py:157-163` wraps `ValidationError` in `MarshallingError ... from e`; direct probe confirms `__cause__ is ValidationError: True`. No uncaught path remains.

6. **Bug-catalog findings for `db_row_to_review` not addressed** — Bug B1 (missing `ValidationError` wrapper, audit/02-static-audit.md#L150) is the sole finding touching `db_utils.py:156-158`. It is addressed by the fix and gate-tested at HEAD.

### Class D — Static Analysis

```
$ ruff check tests/test_db_row_to_review_error.py
F401 `flashcore.db.errors.ReviewOperationError` imported but unused (line 3)
F401 `flashcore.models.Review` imported but unused (line 4)
Found 2 errors. [*] 2 fixable with --fix

ruff exit: 1

$ mypy tests/test_db_row_to_review_error.py --ignore-missing-imports
Success: no issues found in 1 source file
mypy exit: 0
```

Note: The two ruff F401 warnings are pre-existing at HEAD, introduced by f418ec6's import correction (adopted under `PACKET_flashcore-f140-adopt-f418ec6.md`). They are non-blocking style warnings that do not affect test collection or execution correctness. mypy reports no type errors.

Full output: `.github/aiv-packets/evidence/flashcore-f140/adopt_d9f96b3_static.txt`

### Class E — Intent Alignment

- **Canonical intent:** [https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L150](https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L150)
- **Requirement satisfied:** Finding F140 — a review row missing `rating` raises `MarshallingError` naming the column rather than a raw `ValidationError`.
- **Alignment:** d9f96b3 is the original introduction of the dedicated gate test for F140. It served as a red-test documentation artifact locking the B1 bug in the evidence chain. The test's intent — `pytest.raises(MarshallingError)` for an invalid review row — directly encodes the F140 verification goal. The subsequent correction (f418ec6) refined the import and assertion without changing the intent. This adoption is a direct continuation of the F140 audit finding.

### Class F — Provenance (Git Chain-of-Custody)

**Git chain for `tests/test_db_row_to_review_error.py`:**

```
$ git log --oneline --follow -- tests/test_db_row_to_review_error.py

f418ec6 Add red test for missing ValidationError wrapper in db_row_to_review  ← import correction
d9f96b3 Add red test for missing ValidationError wrapper in db_row_to_review  ← ADOPTED (introduced file)
```

The file was introduced by d9f96b3 (operator pipeline) and corrected by f418ec6 (operator pipeline). Both commits have adopt packets in the evidence chain. The HEAD content is from f418ec6. No other commits touch this file. The chain of custody is complete.

---

## Claim Verification Matrix

| # | Claim | Class | Evidence | Verdict |
|---|-------|-------|----------|---------|
| 1 | File `tests/test_db_row_to_review_error.py` did not exist at d9f96b3^ (42f51de) | A/F | `git show 42f51de:tests/test_db_row_to_review_error.py` → fatal | VERIFIED |
| 2 | d9f96b3 added only two files; no existing files were modified or deleted | B/C | `git show d9f96b3 --stat` — 2 files added, 0 modified | VERIFIED |
| 3 | At HEAD, `test_db_row_to_review_missing_validationerror_wrapper` PASSES | A | pytest output: 1 passed in 0.04s | VERIFIED |
| 4 | `db_row_to_review` raises `MarshallingError` with `'rating' in str(e)` for a row missing `rating` | A | Direct probe: `'rating' in str(e): True` | VERIFIED |
| 5 | No existing passing tests were regressed | A/C | Full suite: 495 passed, 1 skipped | VERIFIED |
| 6 | d9f96b3's original import (`flashcore.errors`) was broken; corrected by f418ec6 | C | `python -c "import flashcore.errors"` → ModuleNotFoundError | VERIFIED |
| 7 | ruff and mypy report no type errors in the test file (2 pre-existing F401 warnings are non-blocking) | D | ruff: 2 F401 (pre-existing, fixable); mypy: Success | VERIFIED |
| 8 | Intent aligns with finding F140 canonical audit record | E | Audit URL SHA-pinned to fb1ae5a1 | VERIFIED |

**Verdict summary:** 8 verified, 0 unverified, 0 manual review.

---

## Summary

d9f96b3 was the original operator mid-drive introduction of `tests/test_db_row_to_review_error.py`, a red-test artifact for finding F140. The file did not exist at the parent commit (`42f51de`). The original version had a broken import (`flashcore.errors` does not exist), which caused `ModuleNotFoundError` at collection time; this was a known limitation of the red-test stage. The import was corrected by f418ec6 (separately adopted). At HEAD, the test PASSES: `db_row_to_review` raises `MarshallingError` (not a raw `ValidationError`) and `'rating'` appears in the error message. No existing tests were broken (495 pass, 1 skip at HEAD). mypy is clean; 2 pre-existing ruff F401 warnings are non-blocking and pre-date this adoption. The operator's change is adopted without modification.

## Machine-checkable data

```json
{
  "packet_id": "flashcore-f140-adopt-d9f96b3",
  "adopted_commit": "d9f96b36478269160150a87fe5e42973701d6409",
  "parent_sha": "42f51def0cd3dbb7ff6e986b0125a99d528c3b35",
  "branch_head": "31af2be1e52209136cc4f766fcb7c5b3adaca8c9",
  "finding": "F140",
  "functional_files": ["tests/test_db_row_to_review_error.py"],
  "evidence_classes": ["A", "B", "C", "D", "E", "F"],
  "claims_verified": 8,
  "claims_unverified": 0,
  "test_result_head": "PASS",
  "full_suite_head": "495 passed, 1 skipped",
  "broke_tests": false,
  "fix_forward_required": false,
  "canonical_intent_url": "https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L150"
}
```
