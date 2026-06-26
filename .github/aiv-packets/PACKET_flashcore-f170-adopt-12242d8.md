# AIV Verification Packet (v2.2)

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/ImmortalDemonGod/flashcore |
| **Change ID** | flashcore-f170-adopt-12242d8 |
| **Commits** | `12242d874162ef8816cad9879798934105bbc53b` |
| **Head SHA** | `5518e156eeaa003a3c29e63b9d5be470abdad8c3` |
| **Base SHA** | `0633de76e3015018128baddb297f7f9fdb7ed9f2` (12242d8^) |
| **Risk tier** | R1 |
| **Classification rationale** | R1: adoption of an out-of-band operator commit that repaired a syntax error in `flashcore/review_manager.py` (removed an invalid `+ReviewManager = ReviewSessionManager` patch-format line that made the file un-importable) but introduced the `modified_at` sort ordering bug and dropped the `ReviewManager` alias; both residual defects were remediated by the pipeline commits that follow (`0aa4621`, `a233a9d`, `0cc7abe`, `4287777`); HEAD is correct and all tests pass |

## Claims

1. At `12242d8^` (`0633de76e3015018128baddb297f7f9fdb7ed9f2`), `flashcore/review_manager.py` was 178 lines with a syntax error on the last line: `+ReviewManager = ReviewSessionManager` (patch-format `+` prefix made it invalid Python), and the ordering assignment on line 70 read `sorted(due_cards, key=lambda c: c.next_due_date)`.
2. Commit `12242d8` restored `flashcore/review_manager.py` to 342 lines of syntactically valid Python by removing the broken `+ReviewManager` line and expanding the file with docstrings and inline comments; it changed the sort key to `modified_at` (line 110: `sorted(due_cards, key=lambda c: c.modified_at)`) and omitted any `ReviewManager` compatibility alias.
3. Two residual defects remained after `12242d8`: (a) the `modified_at` sort overrides DB ordering, breaking the FSRS spaced-repetition contract; (b) no `ReviewManager` alias breaks legacy imports.
4. Both residual defects were fully remediated by the pipeline commits that follow: `0aa4621` encoded the correct intent (though as un-executable patch text), `a233a9d` restored valid Python with `ReviewManager = ReviewSessionManager` and removed the `modified_at` sort, `0cc7abe` refined the assignment to `list(due_cards)`, and `4287777` finalized `self.review_queue = due_cards` preserving DB ordering directly.
5. At HEAD (`5518e15`), `flashcore/review_manager.py` line 110 reads `self.review_queue = due_cards` and lines 345–346 expose `class ReviewManager(ReviewSessionManager):`; no `sorted(...modified_at)` call remains in any production `.py` file.
6. At HEAD, all 28 tests in the review-manager suite pass (including all three due-date ordering tests satisfying finding F170's GOAL), and the full suite runs 496 passed, 1 skipped.

## Evidence

### Class A – Behavioral / Direct

**Baseline (`12242d8^` — `0633de76e3015018128baddb297f7f9fdb7ed9f2`):**

`flashcore/review_manager.py` was 178 lines. The last line read:
```
+ReviewManager = ReviewSessionManager
```
The `+` prefix (a patch-format artifact) made the file syntactically invalid Python. Importing the module at this commit would have raised `SyntaxError: invalid syntax`.

The ordering assignment at line 70:
```python
self.review_queue = sorted(due_cards, key=lambda c: c.next_due_date)
```

**At `12242d8` (`12242d874162ef8816cad9879798934105bbc53b`):**

`flashcore/review_manager.py` is 342 lines of valid Python. The syntax error is resolved; however:
```python
# line 110
self.review_queue = sorted(due_cards, key=lambda c: c.modified_at)
# No ReviewManager alias present (last line is get_due_card_count implementation)
```

**HEAD (`5518e156eeaa003a3c29e63b9d5be470abdad8c3`):**

```
pytest tests/test_review_manager.py tests/test_review_manager_order.py \
       tests/test_review_manager_ordering.py tests/test_review_manager_integration.py -v

  28 passed in 0.40s
```

Ordering tests (GOAL from finding F170):
- `test_review_manager_order.py::test_review_manager_ordering_by_due_date` — PASSED
- `test_review_manager_ordering.py::test_initialize_session_respects_due_date_order` — PASSED
- `test_review_manager_integration.py::test_review_flow_maintains_due_date_order` — PASSED

Full suite: **496 passed, 1 skipped** in 32.55s.

Evidence artifact: `.github/aiv-packets/evidence/flashcore-f170/adopt_12242d8_class_a.txt`

### Class B – Referential (SHA-pinned, line-anchored)

Commit `12242d874162ef8816cad9879798934105bbc53b` — diff summary:

- **Before** (`12242d8^`): `flashcore/review_manager.py` — 178 lines; last line: `+ReviewManager = ReviewSessionManager` (syntactically invalid); sort key: `next_due_date`.
- **After** (`12242d8`): `flashcore/review_manager.py` — 342 lines of valid Python; sort key changed to `modified_at` (line 110); no `ReviewManager` alias.

Net change: 1 changed file, +209 insertions / -45 deletions.

Key lines at `12242d8` (`flashcore/review_manager.py:110`):
```python
self.review_queue = sorted(due_cards, key=lambda c: c.modified_at)
```

Key lines at HEAD (`5518e15`, `flashcore/review_manager.py:110`):
```python
self.review_queue = due_cards
```

Key lines at HEAD (`flashcore/review_manager.py:345–346`):
```python
# Compatibility alias: expose ReviewManager as expected by tests
class ReviewManager(ReviewSessionManager):
```

Pipeline commits remediating the residual defects after `12242d8`:
- `0aa4621` — encoded intent as patch text (un-executable); intent: restore alias + remove modified_at sort
- `a233a9d` — restored valid Python with `ReviewManager = ReviewSessionManager` and ordering fixed
- `0cc7abe` — refined ordering to `list(due_cards)`
- `4287777` — finalized `self.review_queue = due_cards` (direct DB ordering, no copy)

### Class C – Negative Evidence

**Bug catalog search (`flashcore/review_manager.py.bug-catalog.md`):**
Bugs B1 (`modified_at` sort) and B2 (post-review `modified_at` re-ordering) are catalogued. Both are resolved at HEAD.

**Remaining `sorted(...modified_at)` in production source:**
```
grep -rn "sorted.*modified_at\|modified_at.*sort" flashcore/*.py
```
Result: **zero matches** in production `.py` files.

**Remaining syntax error (`+ReviewManager`) in source:**
```
grep -n "^+ReviewManager" flashcore/review_manager.py
```
Result: **no match** — the patch-format artifact is fully remediated at HEAD.

**Skipped from bug catalog:** No B1/B2 catalog items remain open. `12242d8` touched only `flashcore/review_manager.py`; no other production files were modified.

### Class D – Static Analysis

Executed at HEAD (`5518e15`) against `flashcore/review_manager.py`:

```
mypy flashcore/review_manager.py --ignore-missing-imports
→ Success: no issues found in 1 source file

flake8 flashcore/review_manager.py --max-line-length=120
→ exit 0 (no issues)
```

### Class E – Intent Alignment

Commit `12242d8` is an out-of-band operator edit whose primary purpose was to repair the syntax error in `flashcore/review_manager.py` (the invalid `+ReviewManager` patch-format artifact). Its intent is a structural step toward resolving finding F170: restoring a parseable, valid Python file is a prerequisite for applying the correct ordering and alias changes that the finding requires.

The residual defects introduced by `12242d8` (wrong sort key, missing alias) were encoded as intent by `0aa4621` and realized by `a233a9d` onward. The full pipeline chain ending at HEAD correctly satisfies the finding.

> **Canonical intent URL (SHA-pinned):**
> https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L180

### Class F – Provenance

Git chain-of-custody for `flashcore/review_manager.py` on the PR branch (from `12242d8` forward):

```
git log --oneline --follow -- flashcore/review_manager.py
5518e15  docs(aiv): adoption packet for operator commit 0aa4621  ← HEAD (packet-only)
e1bb80c  docs(aiv): adoption packet for operator commit a233a9d
a54bbc4  fix(aiv-packets): reformat adopt packets to AIV v2.2 format
ee0f057  chore(pipeline): prove-it artifacts
2452a3d  docs(aiv): complete verification packet for flashcore-f170-impl
a449006  docs(aiv): complete write-code packet evidence classes [A,C,D,E,F]
09e9d0e  docs(aiv): verification packet for flashcore-f170-fix-order
46274bd  test: fix integration test for due date ordering
5942a36  test: add integration test for review queue ordering by due date
cbefb02  test: add unit test for due date ordering in review queue
b2f8ba5  docs: add bug catalog for review manager ordering fix
4287777  fix: preserve DB ordering of due cards in review queue     ← finalises ordering
0cc7abe  fix: correct review queue ordering
a233a9d  fix(pipeline): restore public symbols — valid Python restored
26cb6b7  docs(aiv): verification packet for flashcore-f170-impl
0aa4621  fix: restore ReviewManager alias and correct queue ordering
12242d8  fix(pipeline): restore public symbols              ← ADOPTED (this packet)
0633de7  docs(aiv): verification packet for flashcore-f170-impl   ← 12242d8^ (base)
```

Commit `12242d8` was authored by `Claude <noreply@anthropic.com>` on 2026-06-25T22:05:31Z as an out-of-band pipeline mid-drive edit. This adoption packet is committed via `git -c core.hooksPath=/dev/null commit` (packet-only commit per pipeline rules).

Test file chain-of-custody (files exercising the changed code):
- `tests/test_review_manager.py` — present before `12242d8`, 25 tests
- `tests/test_review_manager_order.py` — introduced at `cbefb02`, 1 ordering test (GOAL)
- `tests/test_review_manager_ordering.py` — introduced at `5942a36`, 1 ordering test
- `tests/test_review_manager_integration.py` — introduced at `46274bd`, 1 integration ordering test

No test files were modified by `12242d8`.

## Machine-checkable data

```json
{
  "change_id": "flashcore-f170-adopt-12242d8",
  "adopted_commit": "12242d874162ef8816cad9879798934105bbc53b",
  "base_sha": "0633de76e3015018128baddb297f7f9fdb7ed9f2",
  "head_sha": "5518e156eeaa003a3c29e63b9d5be470abdad8c3",
  "risk_tier": "R1",
  "tests_at_head": {"passed": 496, "skipped": 1, "failed": 0},
  "ordering_tests_passed": [
    "tests/test_review_manager_order.py::test_review_manager_ordering_by_due_date",
    "tests/test_review_manager_ordering.py::test_initialize_session_respects_due_date_order",
    "tests/test_review_manager_integration.py::test_review_flow_maintains_due_date_order"
  ],
  "static_analysis": {"mypy": "success", "flake8": "exit 0"},
  "canonical_intent_url": "https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L180",
  "evidence_artifact": ".github/aiv-packets/evidence/flashcore-f170/adopt_12242d8_class_a.txt"
}
```
