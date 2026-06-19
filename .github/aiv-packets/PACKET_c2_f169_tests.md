# AIV Verification Packet (v2.2)

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/ImmortalDemonGod/aiv-protocol |
| **Change ID** | c2-f169-tests |
| **Commits** | `3dde24b`, `61d6a20` |
| **Head SHA** | `61d6a20` |
| **Base SHA** | `4739dde` |
| **Created** | 2026-06-19T04:50:42Z |

## Classification

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: component
  classification_rationale: "R1 — adds new test functions (RED state) that detect a correctness defect in a production scheduling path; no production files touched, but test design requires precise behavioral coverage of a FSRS algorithm invariant; R0 excluded because failing or incorrect tests can mask a production bug with real user impact."
  classified_by: "Claude"
  classified_at: "2026-06-19T04:50:42Z"
```

## Claims

1. catalog identifies B1 (last_review=due yields elapsed_days=0 for on-time FSRS reviews) as sole in-scope finding; six entries in Skipped section with explicit reasons
2. catalog designates Path A (last_review_date transient field on Card) as the correction path with one-sentence rationale contrasting Path B approximation limitations
3. test design section for B1-A and B1-B passes all four design-tests criteria: failure under non-trivial defect introduction, pass under behavior-preserving refactor, observable behavior, public interface only
4. Within the c2-f169-tests change context (commits 3dde24b, 61d6a20), no pre-existing test functions were modified: `git show 61d6a20 -- tests/test_scheduler.py | grep "^-" | grep -v "^---"` produces no output (only additions, zero deletions). At branch scope, test_review_lapsed_card (origin/main:L252) and test_review_early_card (origin/main:L289) had last_review_date added to their Card() constructors at commit c829e46 (c2-f169-impl packet commit); that modification is outside this change context and is justified by the oracle-correction record at .aiv/oracle-corrections/c2-f169-impl.md.
5. elapsed_days is 0 instead of >0 when a CardState.Review card (stability=14.0, next_due_date=2024-03-15) is reviewed at 2024-03-15T10:00Z; root cause confirmed at scheduler.py:212 where last_review is assigned fsrs_card.due making the delta zero
6. Card.model_config extra='forbid' raises pydantic ValidationError when last_review_date is supplied to Card constructor; confirms Path A transient field is absent from flashcore/models.py at time of RED-test commit
7. 15 pre-existing tests/test_scheduler.py tests continue to pass after adding two intentionally-failing assertions (17 collected, 2 failed, 15 passed); baseline preserved with no regression

---

## Evidence References

| # | Evidence File | Commit SHA | Classes |
|---|---------------|------------|---------|
| 1 | EVIDENCE_TESTS_TEST_SCHEDULER.BUG_CATALOG.MD.md | `3dde24b` | A, B, E |
| 2 | EVIDENCE_TESTS_TEST_SCHEDULER.md | `61d6a20` | A, B, E |



### Class A (Behavioral / Direct Evidence)

```
pytest tests/test_scheduler.py -v  (commit 61d6a20)
  17 collected: 15 PASSED, 2 FAILED (intentional RED state)

FAILED test_on_time_review_elapsed_days_positive
  AssertionError: elapsed_days=0; assert 0 > 0
  SchedulerOutput.elapsed_days == 0 for Card(state=Review, next_due_date=2024-03-15)
  reviewed at 2024-03-15T10:00Z — confirms F169 at scheduler.py:212.

FAILED test_on_time_vs_same_day_review_stability_distinct
  pydantic_core.ValidationError: extra_forbidden on field 'last_review_date'
  Card.model_config extra='forbid'; Path A transient field absent — confirms
  models.py has no last_review_date at HEAD.

Full-suite (464 passed, 2 failed) — 2 failures are the two new RED tests;
all other 462 tests unaffected.
```

### Class B (Referential Evidence)

**Scope Inventory** (from 2 file references across evidence files)

- `tests/test_scheduler.bug-catalog.md#L1-L249` @ commit `3dde24b`
- `tests/test_scheduler.py#L695-L803` @ commit `61d6a20`

Bug site reference: `flashcore/scheduler.py:211-212` — `fsrs_card.last_review = fsrs_card.due`
(confirmed via `grep -n "last_review = fsrs_card.due" flashcore/scheduler.py`).

### Class C (Negative Evidence)

**Semantic diff check (change-context scope: commits 3dde24b, 61d6a20):**

- `git show 61d6a20 -- tests/test_scheduler.py | grep "^-" | grep -v "^---"` → empty output; zero lines deleted from test_scheduler.py; 61d6a20 is additions-only for that file.
- `git show 3dde24b --name-only` → only `tests/test_scheduler.bug-catalog.md` and evidence file created (new files, no pre-existing file modified).

**grep checks (confirming RED state / no production drift):**

- `grep -n "last_review_date" flashcore/models.py` → 0 matches (field not yet added; RED state confirmed)
- `grep -n "last_review_date" flashcore/scheduler.py` → 0 matches (scheduler unchanged in this context)
- `grep -n "last_review_date" flashcore/review_processor.py` → 0 matches (hub unchanged in this context)
- No production file (`flashcore/**/*.py`) was modified in commits 3dde24b or 61d6a20.

**Branch-scope context (beyond this change):**

At branch scope, test_review_lapsed_card and test_review_early_card had `last_review_date` added in commit c829e46 (c2-f169-impl packet commit). Those modifications are in the c2-f169-impl change context, not this one, and are justified in `.aiv/oracle-corrections/c2-f169-impl.md`.

**Bugs explicitly not tested** (catalog Skipped section, `tests/test_scheduler.bug-catalog.md#L175-L196`):
- B2: negative elapsed_days for early reviews → deferred F169b
- B3: CardState/FSRSState value-parity assumption → deferred
- B4: REVIEW_TYPE_MAP silent default → deferred (cosmetic)

### Class D (Static Analysis)

```
ruff:  pre-existing lint errors unrelated to this change (test file import style);
       no new ruff errors introduced by the two new test functions.
mypy:  4 errors in 3 files — all pre-existing; 0 new errors introduced;
       `mypy flashcore/scheduler.py flashcore/models.py --ignore-missing-imports`
       exits with same error count as baseline.
```

### Class E (Intent Alignment)

Intent source (SHA-pinned, immutable):
`https://github.com/ImmortalDemonGod/flashcore/blob/bc19321bc72cf2467d57ffebc24b92a341ea10d6/audit/02-static-audit.md#L179`

Alignment:
- VERIFY [1]: `test_on_time_review_elapsed_days_positive` present in `tests/test_scheduler.py` (line 697) — RED as required.
- VERIFY [2]: `test_on_time_vs_same_day_review_stability_distinct` present in `tests/test_scheduler.py` (line 734) — RED as required.
- VERIFY [5]: 15 pre-existing tests pass; no regression.
- Design-tests stage scope: catalog written before tests; catalog committed before test code; path decision (A) documented with rationale; no production code modified.

### Class F (Provenance)

Git chain-of-custody for touched test files:

```
git log --oneline tests/test_scheduler.py | head -5
61d6a20  test(scheduler): add RED tests for F169 elapsed_days=0 on-time FSRS review
(prior history: 15 pre-existing tests, author ImmortalDemonGod)

git log --oneline tests/test_scheduler.bug-catalog.md | head -3
3dde24b  docs(tests): add F169 design-tests catalog for elapsed_days scheduler finding
(new file, no prior history)
```

No test files were deleted or renamed. No pre-existing test was modified.
Both new test files are on branch `feat/c2-fsrs-harness`, base `origin/main` @ `b5e1c4b`.

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

Change 'c2-f169-tests': 2 commit(s) across 2 file(s).
