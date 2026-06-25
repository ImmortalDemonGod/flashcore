# Bug Catalog for ReviewManager Scheduling Bug

## Summary
The `ReviewSessionManager.initialize_session` incorrectly re-sorts due cards by `modified_at`, overriding the intended order from the database (`next_due_date ASC NULLS FIRST, added_at ASC`). This causes newly added cards to be prioritized incorrectly after any review, breaking the spaced‑repetition contract.

## Bugs

| ID | Bug Description | Blast Radius | Plausibility Reason | Test Type |
|----|-----------------|--------------|--------------------|-----------|
| B1 | Review queue is ordered by `modified_at` instead of `next_due_date`, causing overdue cards to be delayed. | Users see cards out of intended schedule, reducing learning efficiency and potentially causing forgetting. | `initialize_session` re‑sorts the list returned by `db.get_due_cards` without considering `next_due_date`. | Decision‑table unit test (assert ordering based on due dates). |
| B2 | After a card is reviewed, its `modified_at` is updated, moving it to the end of the queue regardless of its next due date, breaking FSRS scheduling. | Scheduler contract violated; cards may become overdue unnoticed. | `modified_at` is set on every review (db.update_review) and then used for sorting. | Red integration test (full session flow). |

## Skipped Bugs
- **B3**: Failure to handle `NULL` `next_due_date` values – currently the DB orders `NULLS FIRST` which is acceptable; not changing behavior here.
- **B4**: Minor UI display ordering – out of scope for backend scheduling tests.

## Test Plan
- **Test B1**: Create three cards with distinct `next_due_date` values, mock DB to return them unsorted, run `initialize_session`, assert `review_queue` respects `next_due_date` order.
- **Test B2**: Perform a review on the earliest‑due card, then request next card; assert that the next card is still the one with the earliest upcoming `next_due_date`, not the just‑reviewed card.

## Evaluation (to be filled after running tests)
- Bugs caught:
- Bugs characterized:
- Pass + suspect items:
