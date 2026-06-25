# AIV Claim

## Claim

The test `test_review_manager_ordering_by_due_date` will fail when the buggy sorting by `modified_at` is present, confirming the bug.

## Evidence Classes

### Class A
N/A — test not yet executed.

### Class B
N/A — no external references.

### Class C
The bug is present in current code: `self.review_queue = sorted(due_cards, key=lambda c: c.modified_at)` sorts incorrectly, which will cause the test to fail.

### Class D
N/A — static analysis not performed yet.

### Class E
https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L180

### Class F
N/A — provenance claim not required.
