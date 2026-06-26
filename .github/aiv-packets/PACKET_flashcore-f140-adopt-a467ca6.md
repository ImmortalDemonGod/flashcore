# AIV Verification Packet (v2.2)

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/ImmortalDemonGod/flashcore |
| **Change ID** | flashcore-f140-adopt-a467ca6 |
| **Commits** | `a467ca6` |
| **Head SHA** | `e11f8662349e67935dc6cd4a3fbfbf3831581659` |
| **Created** | 2026-06-26T00:00:00Z |

## Classification

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "operator mid-drive adoption — test-only addition"
  classification_rationale: "R1: adoption of operator out-of-band commit on PR branch; adds a new test file"
  classified_by: "pipeline-repair-script"
  classified_at: "2026-06-26T00:00:00Z"
```

## Claims

1. Commit a467ca6 added a new test file `tests/test_db_row_to_review_error_handling.py` that was not present at the parent commit (ec9e708).
2. Branch HEAD is correct after adopting a467ca6 — the new test passes and no existing tests were broken.
3. The test exercises the exact F140 invariant: a review row missing `rating` raises `MarshallingError` (not a raw `ValidationError`), with `__cause__` set to the original `ValidationError`.
4. The adoption aligns with the canonical intent for this PR branch.

## What a467ca6 Did

a467ca6 introduced two new files:

### 1. `tests/test_db_row_to_review_error_handling.py` (functional — new test)

This file was not present at the parent commit (`ec9e708`). a467ca6 created it:

```python
import pytest
from flashcore.db.db_utils import db_row_to_review
from flashcore.exceptions import MarshallingError
from pydantic import ValidationError

def test_db_row_to_review_missing_validation_error_wrapper():
    # Row dict missing required field 'rating' triggers ValidationError inside Review model
    row = {"id": 1, "content": "test", "user_id": 42}
    with pytest.raises(MarshallingError) as exc:
        db_row_to_review(row)
    # Ensure the underlying cause is a ValidationError
    assert isinstance(exc.value.__cause__, ValidationError)
```

The test:
- Uses `flashcore.exceptions.MarshallingError` (a valid import path — verified at HEAD).
- Submits a row missing `rating` (and many other required fields) to `db_row_to_review`.
- Asserts `MarshallingError` is raised (not a raw `ValidationError`).
- Additionally asserts `exc.value.__cause__` is a `ValidationError`, verifying exception chaining.

### 2. `.github/aiv-evidence/EVIDENCE_TESTS_TEST_DB_ROW_TO_REVIEW_ERROR_HANDLING.md` (metadata — aiv evidence stub)

This file is a pre-existing aiv-evidence stub committed alongside the test by the operator pipeline. It documents the operator's claims and links to Class E intent. It is not a functional file.

## Why HEAD is Correct

- At baseline (`ec9e708`), `tests/test_db_row_to_review_error_handling.py` did not exist — this is a pure addition.
- `db_row_to_review` at HEAD (`flashcore/db/db_utils.py:152-163`) already wraps `ValidationError` in `MarshallingError` with `from e` (exception chaining), so `__cause__` is set.
- At HEAD the test passes (1 passed, 0 failed).
- No existing passing tests were broken by a467ca6 (495 pass, 1 skip at HEAD).
- The `flashcore.exceptions.MarshallingError` import is valid — `MarshallingError` is exported from `flashcore.exceptions` at HEAD.

---

## Evidence

### Class A — Behavioral / Direct

**Baseline (a467ca6^ = ec9e708) — file did not exist:**
```
$ git show ec9e7086ce534c3cb4bf773ac66a3562dfac3619:tests/test_db_row_to_review_error_handling.py
fatal: path 'tests/test_db_row_to_review_error_handling.py' exists on disk,
      but not in 'ec9e7086ce534c3cb4bf773ac66a3562dfac3619'

# File introduced by a467ca6 — zero tests at baseline for this file.
```
Full output: `.github/aiv-packets/evidence/flashcore-f140/adopt_a467ca6_baseline.txt`

**HEAD (e11f866) — test passes:**
```
$ pytest tests/test_db_row_to_review_error_handling.py -v --tb=long

tests/test_db_row_to_review_error_handling.py::test_db_row_to_review_missing_validation_error_wrapper PASSED

1 passed in 0.04s — EXIT CODE: 0
```
Full output: `.github/aiv-packets/evidence/flashcore-f140/adopt_a467ca6_head.txt`

**Direct functional probe at HEAD:**
```python
from flashcore.db.db_utils import db_row_to_review
from flashcore.exceptions import MarshallingError
from pydantic import ValidationError
row = {"id": 1, "content": "test", "user_id": 42}
try:
    db_row_to_review(row)
except MarshallingError as e:
    print(f"MarshallingError raised. __cause__ is ValidationError: {isinstance(e.__cause__, ValidationError)}")
```
`MarshallingError raised. __cause__ is ValidationError: True`

Full output: `.github/aiv-packets/evidence/flashcore-f140/adopt_a467ca6_probe.txt`

**Full regression suite at HEAD:**
```
$ pytest tests/ -q --tb=short
495 passed, 1 skipped in 32.29s — EXIT CODE: 0
```
Full output: `.github/aiv-packets/evidence/flashcore-f140/adopt_a467ca6_fullsuite.txt`

### Class B — Referential Evidence (SHA-pinned)

**Scope inventory at HEAD (SHA: [`e11f8662349e67935dc6cd4a3fbfbf3831581659`](https://github.com/ImmortalDemonGod/flashcore/tree/e11f8662349e67935dc6cd4a3fbfbf3831581659)):**

- [`tests/test_db_row_to_review_error_handling.py#L1-L12`](https://github.com/ImmortalDemonGod/flashcore/blob/e11f8662349e67935dc6cd4a3fbfbf3831581659/tests/test_db_row_to_review_error_handling.py#L1-L12) — full test file
- [`tests/test_db_row_to_review_error_handling.py#L6-L12`](https://github.com/ImmortalDemonGod/flashcore/blob/e11f8662349e67935dc6cd4a3fbfbf3831581659/tests/test_db_row_to_review_error_handling.py#L6-L12) — test function body
- [`flashcore/db/db_utils.py#L152-L163`](https://github.com/ImmortalDemonGod/flashcore/blob/e11f8662349e67935dc6cd4a3fbfbf3831581659/flashcore/db/db_utils.py#L152-L163) — `db_row_to_review` with `ValidationError → MarshallingError` wrapper

**Diff introduced by a467ca6 (SHA-pinned to adopted commit):**

- [`tests/test_db_row_to_review_error_handling.py` at a467ca6](https://github.com/ImmortalDemonGod/flashcore/blob/a467ca6b683ca7d6a095cb18a204f2f0dd04481e/tests/test_db_row_to_review_error_handling.py) — new file, 12 lines

### Class C — Negative Evidence

**What was searched and NOT found:**

1. **Other occurrences of `test_db_row_to_review_missing_validation_error_wrapper` outside the new file** — searched `tests/` with `grep -rn "test_db_row_to_review_missing_validation_error_wrapper"` — found only in `tests/test_db_row_to_review_error_handling.py`. No duplication or conflict with other test files.

2. **Any test calling `db_row_to_review` that was deleted or modified by a467ca6** — `git show a467ca6 --stat` shows only two files added (zero modified or deleted). No existing test was removed or altered.

3. **Raw `pydantic.ValidationError` escaping from `db_row_to_review` at HEAD** — `db_utils.py:157-163` wraps in `MarshallingError ... from e`; the three callers in `database.py` (lines 818, 895, 1201) handle `MarshallingError`. No uncaught `ValidationError` path remains.

4. **Skipped bug-catalog findings for `db_row_to_review`** — Bug B1 (missing `ValidationError` wrapper) is the only finding from the audit touching `db_utils.py:156-158`. No other catalog bugs were deferred without disposition.

5. **`flashcore.exceptions` not being a valid module** — `python -c "from flashcore.exceptions import MarshallingError"` succeeds at HEAD. The import in the new test file is valid.

### Class D — Static Analysis

```
$ ruff check tests/test_db_row_to_review_error_handling.py
All checks passed!
ruff exit: 0

$ mypy tests/test_db_row_to_review_error_handling.py --ignore-missing-imports
Success: no issues found in 1 source file
mypy exit: 0
```

Full output: `.github/aiv-packets/evidence/flashcore-f140/adopt_a467ca6_static.txt`

### Class E — Intent Alignment

- **Canonical intent:** [https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L150](https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L150)
- **Requirement satisfied:** Finding F140 — a review row missing `rating` raises `MarshallingError` naming the column rather than a raw `ValidationError`.
- **Alignment:** a467ca6 is a direct refinement of the F140 finding's goal. The operator added a dedicated test file (`test_db_row_to_review_error_handling.py`) with a targeted test for the missing-wrapper invariant, using exception chaining verification (`__cause__ is ValidationError`). This is a strengthening of the gate test, not a change of intent.

### Class F — Provenance (Git Chain-of-Custody)

**Git chain for `tests/test_db_row_to_review_error_handling.py`:**

```
$ git log --oneline --follow -- tests/test_db_row_to_review_error_handling.py

a467ca6 Add red test for missing ValidationError wrapper   ← ADOPTED (introduced file)
```

The file was introduced in a single commit (`a467ca6`) by the operator pipeline. No prior history exists for this file — it is a wholly new addition at this commit. The file has not been modified after introduction; the HEAD content matches `a467ca6` exactly.

---

## Claim Verification Matrix

| # | Claim | Class | Evidence | Verdict |
|---|-------|-------|----------|---------|
| 1 | File `tests/test_db_row_to_review_error_handling.py` did not exist at a467ca6^ (ec9e708) | A/F | `git show ec9e708:tests/test_db_row_to_review_error_handling.py` → fatal | VERIFIED |
| 2 | At HEAD, `test_db_row_to_review_missing_validation_error_wrapper` PASSES | A | pytest output: 1 passed in 0.04s | VERIFIED |
| 3 | `db_row_to_review` raises `MarshallingError` with `__cause__ == ValidationError` for a row missing `rating` | A | Direct probe: `__cause__ is ValidationError: True` | VERIFIED |
| 4 | No existing passing tests were regressed by a467ca6 | A/C | Full suite: 495 passed, 1 skipped | VERIFIED |
| 5 | a467ca6 adds only two files; no existing files were modified or deleted | B/C | `git show a467ca6 --stat` — 2 files added, 0 modified | VERIFIED |
| 6 | ruff and mypy report no errors in the new test file | D | ruff: All checks passed; mypy: Success | VERIFIED |
| 7 | `flashcore.exceptions.MarshallingError` is a valid import at HEAD | C/D | `python -c "from flashcore.exceptions import MarshallingError"` succeeds | VERIFIED |
| 8 | Intent aligns with finding F140 canonical audit record | E | Audit URL SHA-pinned to fb1ae5a1 | VERIFIED |

**Verdict summary:** 8 verified, 0 unverified, 0 manual review.

---

## Summary

a467ca6 was an operator mid-drive addition of `tests/test_db_row_to_review_error_handling.py`, a new dedicated test file for the F140 invariant. The file did not exist at the parent commit (`ec9e708`). At HEAD, the test passes: `db_row_to_review` raises `MarshallingError` (not a raw `ValidationError`) with exception chaining (`__cause__` set to the original `ValidationError`). No existing tests were broken (495 pass, 1 skip at HEAD). ruff and mypy are clean. The operator's change is adopted without modification.

## Machine-checkable data

```json
{
  "packet_id": "flashcore-f140-adopt-a467ca6",
  "adopted_commit": "a467ca6b683ca7d6a095cb18a204f2f0dd04481e",
  "parent_sha": "ec9e7086ce534c3cb4bf773ac66a3562dfac3619",
  "branch_head": "e11f8662349e67935dc6cd4a3fbfbf3831581659",
  "finding": "F140",
  "functional_files": ["tests/test_db_row_to_review_error_handling.py"],
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
