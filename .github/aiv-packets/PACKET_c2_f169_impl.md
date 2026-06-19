# AIV Verification Packet (v2.2)

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/ImmortalDemonGod/aiv-protocol |
| **Change ID** | c2-f169-impl |
| **Commits** | `e0f6519`, `3fa913a`, `37a0dec` |
| **Head SHA** | `37a0dec` |
| **Base SHA** | `c832b15` |
| **Created** | 2026-06-19T05:37:06Z |

## Classification

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: component
  classification_rationale: "TODO: Describe why this tier was chosen"
  classified_by: "Claude"
  classified_at: "2026-06-19T05:37:06Z"
```

## Claims

1. Card model lacks last_review_date field before this commit; field added as Optional[date] default None at flashcore/models.py:61
2. ConfigDict extra=forbid preserved at flashcore/models.py:51; field declared on model class so Pydantic accepts it without extra-fields rejection
3. No existing tests were modified or deleted during this change.
4. Line 212 assignment last_review=due removed at flashcore/scheduler.py:211-217; replaced with conditional on card.last_review_date
5. When last_review_date is None (hub not populated), last_review remains unset at flashcore/scheduler.py:217; elapsed_days=0 (correct for New/first-ever review)
6. Scheduler at flashcore/scheduler.py:223-229 does not read DB directly; last_review_date populated by hub before this call (no new import to scheduler)
7. get_latest_review_for_card called at flashcore/review_processor.py:100 before compute_next_state at line 105; card.last_review_date set from prior_review.ts.date() at line 102 when returned object is a Review instance
8. updated_card.last_review_date set to ts.date() at flashcore/review_processor.py:133 after add_review_and_update_card at line 129 for same-session re-review caching
9. isinstance(prior_review, Review) guard at flashcore/review_processor.py:101 prevents MagicMock test doubles from triggering Pydantic validation on last_review_date assignment

---

## Evidence References

| # | Evidence File | Commit SHA | Classes |
|---|---------------|------------|---------|
| 1 | EVIDENCE_FLASHCORE_MODELS.md | `e0f6519` | A, B, E |
| 2 | EVIDENCE_FLASHCORE_SCHEDULER.md | `3fa913a` | A, B, E |
| 3 | EVIDENCE_FLASHCORE_REVIEW_PROCESSOR.md | `37a0dec` | A, B, E |

---

### Class A (Behavioral / Direct Evidence)

Live-execution results against real in-memory DB and real FSRS scheduler:

- `python -m pytest tests/test_scheduler.py -q --tb=short` → **17 passed** (15 existing + 2 new RED→GREEN)
- `python -m pytest tests/test_scheduler.py::test_on_time_review_elapsed_days_positive -v` → **1 passed**; `elapsed_days > 0` confirmed
- `python -m pytest tests/test_scheduler.py::test_on_time_vs_same_day_review_stability_distinct -v` → **1 passed**; `stab_on_time != stab_same_day` confirmed
- `python -m pytest tests/test_review_processor.py::TestReviewProcessorIntegration::test_on_time_review_persists_positive_elapsed_days -v` → **1 passed**; `elapsed_days_at_review > 0` in SQLite row confirmed (Layer-B: real DB, real scheduler)
- `python -m pytest tests/test_review_processor.py -q` → **12 passed**
- `grep -n "last_review = fsrs_card.due" flashcore/scheduler.py` → no output (bug line removed)
- `grep -n "get_latest_review_for_card" flashcore/review_processor.py` → line 100 (hub DB lookup confirmed)

### Class B (Referential Evidence)

**Scope Inventory** (SHA-pinned line anchors across implementation commits)

- `flashcore/models.py#L61-L64` @ `e0f6519` — `last_review_date: Optional[date] = Field(default=None)`
- `flashcore/scheduler.py#L211-L217` @ `3fa913a` — conditional `fsrs_card.last_review = combine(last_review_date)` replacing buggy `last_review = due`
- `flashcore/review_processor.py#L99-L103` @ `37a0dec` — `get_latest_review_for_card` call; `card.last_review_date = prior_review.ts.date()`
- `flashcore/review_processor.py#L132-L133` @ `37a0dec` — `updated_card.last_review_date = ts.date()` (same-session cache)

### Class C (Negative Evidence)

Searched for and did NOT find:

- `grep -n "stability.*timedelta\|timedelta.*stability\|round.*stability" flashcore/scheduler.py` → no output; stability-approximation branch was not introduced (Path B rejected per §7 D1)
- `grep -rn "last_review_date" flashcore/db/schema.py flashcore/db/database.py` → no output; no DB schema change; `last_review_date` remains transient this PR
- `grep -rn "from flashcore.scripts" flashcore/` → no import from scripts in core (hub-and-spoke discipline maintained)
- Bug-catalog entries B2, B3 (out-of-scope stability-approximation variants): searched, not introduced
- `grep -n "last_review = fsrs_card.due" flashcore/scheduler.py` → no output (AC-3 confirmed)

### Class D (Static Analysis)

- `mypy flashcore/scheduler.py flashcore/models.py --ignore-missing-imports` → no new errors; pre-existing `yaml` stub warning unchanged (not introduced by this PR)
- `python -m pytest tests/ -q --tb=short` → 467 passed, 1 skipped, 16 errors; the 16 errors are pre-existing (in `tests/test_db.py`, `tests/test_parser.py`, `tests/test_yaml_validators.py`, `tests/cli/`); none in files touched by this PR; net new tests from this PR change set: +2 unit (test_scheduler.py), +1 integration (test_review_processor.py) = +3 tests, all GREEN

### Class E (Intent Alignment)

**Intent reference (SHA-pinned):**
`https://github.com/ImmortalDemonGod/flashcore/blob/27797f4/.taskmaster/tasks/task_008.md`

**Requirement satisfied:** D1 (Path A, operator-confirmed 2026-06-19) — consume ground-truth DB-recorded prior-review `ts` via `get_latest_review_for_card` before every `compute_next_state` call; no stability approximation; `elapsed_days=0` only when no prior review exists in DB (genuinely first-ever review).

**AC coverage:**

| AC | Criterion | Status |
|----|-----------|--------|
| AC-1 | `test_on_time_review_elapsed_days_positive` passes; `elapsed_days > 0` | PASS |
| AC-2 | `test_on_time_vs_same_day_review_stability_distinct` passes | PASS |
| AC-3 | Bug line `last_review = fsrs_card.due` absent | PASS |
| AC-4 | `last_review_date` present in all 3 implementation files | PASS |
| AC-5 | Learning-state guard correct; new/learning tests unaffected | PASS |
| AC-6 | All 15 existing scheduler tests pass; 17 total | PASS |
| AC-7 | mypy clean on touched files | PASS |
| AC-9 | Full suite: 467+ passed, 1 skipped, no new failures | PASS |
| AC-12 | Layer-B integration test: `elapsed_days_at_review > 0` in DB row | PASS |
| AC-13 | No stability-approximation branch in scheduler | PASS |
| AC-14 | Hub DB lookup `get_latest_review_for_card` present before `compute_next_state` | PASS |

### Class F (Provenance)

Git chain-of-custody for touched test files:

- `tests/test_scheduler.py` — RED tests added at `61d6a20` (design-tests phase, before this change context); tests updated to include `last_review_date` in card constructors at same commit, anticipating Path A; implementation commits `e0f6519`, `3fa913a`, `37a0dec` make these tests GREEN; no test assertions modified by implementation commits
- `tests/test_review_processor.py` — Layer-B integration test `test_on_time_review_persists_positive_elapsed_days` added at `c832b15` (design-tests packet commit); made GREEN by implementation commit `37a0dec` (review_processor hub reads prior-review ts from DB)
- Neither test file was modified by the 3 implementation commits tracked in this change context; test correctness is unchanged; implementation side provides the missing data flow

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence was collected by `aiv commit` during the change lifecycle.
Packet generated by `aiv close`.

---

## Known Limitations

- Evidence references point to Layer 1 evidence files at specific commit SHAs.
  Use `git show <sha>:.github/aiv-evidence/<file>` to retrieve.

---

## Summary

Change 'c2-f169-impl': 3 commit(s) across 3 file(s).
