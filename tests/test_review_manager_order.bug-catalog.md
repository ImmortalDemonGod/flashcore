# Bug Catalog for ReviewManager Sorting Bug

## Public Interface
- `ReviewManager.initialize_session()` populates `self.review_queue`.
- `self.review_queue` is consumed by the review UI to present the next card.

## Load-bearing Comments
- None identified beyond ordering comment in `review_manager.py`.

## IO Boundaries
- Reads due cards from DB via `self.db.get_due_cards()`.
- No external file or network I/O in this module.

## Branching Points
- Sorting of `due_cards` by `modified_at` (line 109).
- Potential early‑return if no due cards.

## Magic‑string Contracts
- Ordering clause in DB query: `next_due_date ASC NULLS FIRST, added_at ASC`.
- No string literals used for status.

## Existing Tests
- `tests/test_review_manager.py` checks basic queue non‑emptiness but does **not** verify ordering by due date.

## Bug Catalog
| ID | Bug Description | Blast Radius | Plausibility Reason | Test Type |
|----|----------------|-------------|--------------------|-----------|
| B1 | `ReviewManager` re‑sorts due cards by `modified_at` instead of `next_due_date`, causing overdue cards to be delayed and breaking spaced‑repetition guarantees. | Users miss review windows, learning efficiency drops. | Sorting key is unrelated to scheduling logic and is applied unconditionally. | Decision‑table unit test verifying ordering by `next_due_date`.

## Skipped Bugs
- None – all identified plausible bugs are covered.

## Evaluation (to be filled after tests)
- Bugs caught:
- Bugs characterized:
- Bugs discovered during writing:

---

### Class A
N/A — No behavioral evidence collected yet (tests not run).

### Class B
N/A — No external references needed.

### Class C
N/A — No negative evidence.

### Class D
N/A — No static analysis evidence yet.

### Class E
https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L180

### Class F
N/A — No provenance claim needed for catalog creation.
