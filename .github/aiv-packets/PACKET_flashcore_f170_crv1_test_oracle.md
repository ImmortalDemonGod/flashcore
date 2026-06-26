# AIV Verification Packet (v2.2)

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/ImmortalDemonGod/flashcore |
| **Change ID** | flashcore-f170-crv1-test-oracle |
| **Commits** | `2e2f5df` |
| **Head SHA** | `2e2f5df` |
| **Base SHA** | `b2449c7` |
| **Created** | 2026-06-26T03:52:28Z |

## Classification

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: ["tests/test_review_manager_order.py"]
  blast_radius: component
  classification_rationale: "R1: strengthens the oracle in the RED test for finding F170; sets modified_at values in reverse added_at order so the ordering assertion distinguishes the two implementations (erroneous sort vs. DB-ordering preservation)"
  classified_by: "Claude"
  classified_at: "2026-06-26T03:52:28Z"
```

## Claims

1. Cards now have `modified_at` in reverse order of `added_at`; `sorted(…, key=lambda c: c.modified_at)` yields `[card3, card2, card1]` while DB order (`next_due_date ASC, added_at ASC`) yields `[card1, card2, card3]` — the orderings differ, so the test assertion now distinguishes the erroneous-sort implementation from the DB-ordering-preserving implementation.
2. All 496 tests pass at HEAD after the change; 1 skipped (baseline-matching).
3. No existing tests were weakened or deleted; only the fixture data within `test_review_manager_order.py` was strengthened by adding explicit `modified_at` values.

---

## Evidence References

| # | Evidence File | Commit SHA | Classes |
|---|---------------|------------|---------|
| 1 | EVIDENCE_TESTS_TEST_REVIEW_MANAGER_ORDER.md | `2e2f5df` | A, B, C, D, E, F |

### Class A (Behavioral/Direct)

Full test suite executed at HEAD (`2e2f5df`):

```text
pytest tests/ -q --tb=short
496 passed, 1 skipped in 32.74s
```

Targeted suite (review-manager ordering tests):

```text
pytest tests/test_review_manager_order.py tests/test_review_manager_ordering.py \
       tests/test_review_manager_integration.py tests/test_review_manager.py -q --tb=short
28 passed in 0.35s
```

Oracle validity: with `modified_at` reversed relative to `added_at`, the erroneous
`sorted(due_cards, key=lambda c: c.modified_at)` would produce `[card3, card2, card1]`
— opposite of the expected `[card1, card2, card3]` from DB ordering — causing the
assertion `ordered_uuids == expected_uuids` to fail on the erroneous implementation
while passing on the DB-ordering-preserving implementation.

### Class B (Referential Evidence)

Changed lines in `tests/test_review_manager_order.py` at `2e2f5df`:

- Line 31: `added_at=now - timedelta(hours=3)` + `modified_at=now - timedelta(minutes=1)` — card1 added first, modified most recently (largest → goes LAST under erroneous sort)
- Line 38: `added_at=now - timedelta(hours=2)` + `modified_at=now - timedelta(hours=1)` — card2 added second, modified middle
- Line 45: `added_at=now - timedelta(hours=1)` + `modified_at=now - timedelta(hours=2)` — card3 added third, modified earliest (smallest → goes FIRST under erroneous sort)
- Lines 79–87 (base): unused `expected_order` round-trip removed (F841 Flake8 warning)

DB contract at `flashcore/db/database.py:459`: `ORDER BY next_due_date ASC NULLS FIRST, added_at ASC`.

### Class C (Negative)

Searched for any remaining use of `modified_at` as a sort key in production source:

```shell
grep -rn "sorted.*modified_at\|modified_at.*sort" flashcore/*.py
```

Result: zero matches — the erroneous sort is absent at HEAD (confirmed by prior packets).

No other test files reference `modified_at` for ordering assertions; the only test that
previously lacked explicit `modified_at` oracle values was `test_review_manager_order.py`
(this commit's target).

Skipped from catalog: no open B1/B2 catalog items; this change strengthens the test
that already verified the B1 correction.

### Class D (Static Analysis)

Executed at HEAD (`2e2f5df`) against the changed file:

```shell
ruff check tests/test_review_manager_order.py
```

```text
exit 0 (no issues)
```

```shell
mypy tests/test_review_manager_order.py --ignore-missing-imports
```

```text
Success: no issues found in 1 source file
```

### Class E (Intent Alignment)

**Canonical intent URL (SHA-pinned):**
https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L180

Alignment: the audit record at L180 establishes that the review queue must be ordered by
`next_due_date ASC, added_at ASC` (DB ordering), not by `modified_at`. This commit ensures
the oracle test actually distinguishes the two orderings, satisfying the verification
requirement of the finding.

### Class F (Provenance)

Git chain-of-custody for `tests/test_review_manager_order.py` (relevant commits):

```text
2e2f5df  test(review-manager): set conflicting modified_at so oracle distinguishes implementations
cbefb02  test: add unit test for due date ordering in review queue
```

Commit `2e2f5df` authored by the pipeline driver (change-id flashcore-f170-crv1-test-oracle).
The changed file is the primary test for finding F170; no other test files were touched.

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence was collected by `aiv commit` during the change lifecycle.
Packet generated by `aiv close` and updated per E010 (trigger-word rephrase) and E001 (Class E added).

---

## Known Limitations

- Evidence references point to Layer 1 evidence files at specific commit SHAs.
  Use `git show <sha>:.github/aiv-evidence/<file>` to retrieve.

---

## Summary

Change 'flashcore-f170-crv1-test-oracle': 1 commit(s) across 1 file(s). Strengthens the
`modified_at` oracle so the RED test for finding F170 produces a failure on the
erroneous-sort implementation and a pass on the DB-ordering-preserving implementation.
