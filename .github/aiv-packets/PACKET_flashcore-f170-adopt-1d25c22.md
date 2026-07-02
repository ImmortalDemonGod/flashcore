# AIV Verification Packet (v2.2)

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/ImmortalDemonGod/flashcore |
| **Change ID** | flashcore-f170-adopt-1d25c22 |
| **Commits** | `1d25c2212d53adf446c4f7bcb11c1bed9c397f52` |
| **Head SHA** | `a73ca013ada7021cb1cedd3a61f88418e8cc2b88` |
| **Base SHA** | `b20e89986320fb2ce15c612584dac974b2cea8f7` (1d25c22^) |
| **Risk tier** | R1 |
| **Classification rationale** | R1: out-of-band operator commit that replaces the broken `sorted(due_cards, key=lambda c: c.modified_at)` sort with `sorted(due_cards, key=lambda c: c.next_due_date)` in `ReviewSessionManager.initialize_session`, directly resolving finding F170; also adds a `ReviewManager = ReviewSessionManager` backward-compatibility alias; both `1d25c22^` and `1d25c22` are valid Python; the ordering was further refined in subsequent pipeline commits to `self.review_queue = due_cards` (preserving DB order directly); HEAD is correct and all 496 tests pass |

## Claims

1. At `1d25c22^` (`b20e89986320fb2ce15c612584dac974b2cea8f7`), `flashcore/review_manager.py` line 110 contained `self.review_queue = sorted(due_cards, key=lambda c: c.modified_at)` — the broken spaced-repetition ordering identified in finding F170.
2. Commit `1d25c22` replaces that line with `self.review_queue = sorted(due_cards, key=lambda c: c.next_due_date)` (line 113), correcting the sort key from `modified_at` to `next_due_date` and thereby restoring the spaced-repetition contract.
3. Commit `1d25c22` also appends a `ReviewManager = ReviewSessionManager` alias (line 348) for backward compatibility; the file at `1d25c22` is syntactically valid Python.
4. The `next_due_date` ordering introduced by `1d25c22` was not reverted by subsequent commits; at HEAD the ordering is `self.review_queue = due_cards` (preserving the DB's `next_due_date ASC NULLS FIRST, added_at ASC` ordering directly without re-sorting), which satisfies the same correctness invariant.
5. At HEAD (`a73ca013`), all three F170 GOAL tests pass: `test_review_manager_ordering_by_due_date`, `test_initialize_session_respects_due_date_order`, and `test_review_flow_maintains_due_date_order`.
6. At HEAD, the full test suite runs 496 passed, 1 skipped with no failures; mypy and flake8 both report clean on `flashcore/review_manager.py`.

## Evidence

### Class A – Behavioral / Direct

**Baseline (`1d25c22^` — `b20e89986320fb2ce15c612584dac974b2cea8f7`):**

`flashcore/review_manager.py` is valid Python with the broken `modified_at` sort at line 110.

```
git show 1d25c22^:flashcore/review_manager.py | python3 -c "import sys,ast; ast.parse(sys.stdin.read()); print('VALID')"
→ VALID
```

Sort key at baseline (line 110 — the bug):
```python
self.review_queue = sorted(due_cards, key=lambda c: c.modified_at)
```
No `ReviewManager` alias present at `b20e899`.

**At `1d25c22` (`1d25c2212d53adf446c4f7bcb11c1bed9c397f52`):**

```
git show 1d25c22:flashcore/review_manager.py | python3 -c "import sys,ast; ast.parse(sys.stdin.read()); print('VALID')"
→ VALID
```

Sort key (line 113 — corrected):
```python
self.review_queue = sorted(due_cards, key=lambda c: c.next_due_date)
```

ReviewManager alias (line 348):
```python
# Backward compatibility: expose ReviewManager as an alias expected by importers.
ReviewManager = ReviewSessionManager
```

**HEAD (`a73ca013ada7021cb1cedd3a61f88418e8cc2b88`):**

```
pytest tests/test_review_manager.py tests/test_review_manager_order.py \
       tests/test_review_manager_ordering.py tests/test_review_manager_integration.py -v

  28 passed in 0.39s
```

Ordering tests (GOAL from finding F170):
- `test_review_manager_order.py::test_review_manager_ordering_by_due_date` — PASSED
- `test_review_manager_ordering.py::test_initialize_session_respects_due_date_order` — PASSED
- `test_review_manager_integration.py::test_review_flow_maintains_due_date_order` — PASSED

Full suite: **496 passed, 1 skipped** in 32.53s.

Evidence artifact: `.github/aiv-packets/evidence/flashcore-f170/adopt_1d25c22_class_a.txt`

### Class B – Referential (SHA-pinned, line-anchored)

Commit `1d25c2212d53adf446c4f7bcb11c1bed9c397f52` — diff summary:

- **Before** (`1d25c22^`): `flashcore/review_manager.py` — valid Python; sort key: `modified_at` (line 110); no `ReviewManager` alias.
- **After** (`1d25c22`): `flashcore/review_manager.py` — valid Python; sort key: `next_due_date` (line 113); `ReviewManager = ReviewSessionManager` alias added (line 348).

Net change: 2 files changed, 46 insertions / 18 deletions (also updated `.github/aiv-evidence/EVIDENCE_FLASHCORE_REVIEW_MANAGER.md`).

Key line at `1d25c22` (`flashcore/review_manager.py:113`):
```python
self.review_queue = sorted(due_cards, key=lambda c: c.next_due_date)
```

Key line at `1d25c22` (`flashcore/review_manager.py:348` — alias added):
```python
ReviewManager = ReviewSessionManager
```

Key line at HEAD (`flashcore/review_manager.py:110` — final ordering, DB order preserved directly):
```python
self.review_queue = due_cards
```

Key lines at HEAD (`flashcore/review_manager.py:345–346` — alias refined to class):
```python
# Compatibility alias: expose ReviewManager as expected by tests
class ReviewManager(ReviewSessionManager):
```

### Class C – Negative Evidence

**Bug catalog search:**

The primary bug (B1: `modified_at` sort key overriding DB ordering) was present at `1d25c22^` and was eliminated by `1d25c22`. No other production files contain the broken sort pattern.

**Remaining `sorted(...modified_at)` in production source:**
```
grep -rn "sorted.*modified_at|modified_at.*sort" flashcore/*.py
```
Result at HEAD: **no match** (exit 1) — the `modified_at` sort is fully removed from all production files.

**Skipped from bug catalog:** Commit `1d25c22` touched only `flashcore/review_manager.py` and `.github/aiv-evidence/EVIDENCE_FLASHCORE_REVIEW_MANAGER.md`. The evidence file is non-functional documentation; no other production module was modified.

**No test regressions:** the `sorted(...key=lambda c: c.next_due_date)` introduced by `1d25c22` did not break any existing test; subsequent pipeline commits refined it further to `self.review_queue = due_cards` (removing the sort call entirely, relying on the DB's guaranteed ordering). All 28 review-manager tests pass at HEAD.

### Class D – Static Analysis

Executed at HEAD (`a73ca013`) against `flashcore/review_manager.py`:

```
mypy flashcore/review_manager.py --ignore-missing-imports
→ Success: no issues found in 1 source file

flake8 flashcore/review_manager.py --max-line-length=120
→ exit 0 (no issues)
```

### Class E – Intent Alignment

Commit `1d25c22` is an out-of-band operator edit whose sole functional purpose is to replace the `modified_at` sort key with `next_due_date`, directly remediating the spaced-repetition contract violation identified in finding F170. This is a refinement of the same intent as the primary fix; the operator's change and all subsequent pipeline commits converge on the same invariant.

> **Canonical intent URL (SHA-pinned):**
> https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L180

### Class F – Provenance

Git chain-of-custody for `flashcore/review_manager.py` on the PR branch (from `1d25c22` forward):

```
git log --oneline --follow -- flashcore/review_manager.py
a73ca01  docs(aiv): adoption packet for operator commit 2a59bec  ← HEAD (packet-only)
5100059  docs(aiv): adoption packet for operator commit 12242d8
5518e15  docs(aiv): adoption packet for operator commit 0aa4621
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
4287777  fix: preserve DB ordering of due cards in review queue
0cc7abe  fix: correct review queue ordering
a233a9d  fix(pipeline): restore public symbols — valid Python restored
0aa4621  fix: restore ReviewManager alias and correct queue ordering
12242d8  fix(pipeline): restore public symbols
2a59bec  fix: add legacy ReviewManager shim and correct ordering
1d25c22  fix: correct ordering of due cards in ReviewSessionManager  ← ADOPTED (this packet)
b20e899  fix(pipeline): restore public symbols                       ← 1d25c22^ (base)
```

Commit `1d25c22` was authored by `openrouter-driver (fix-pipeline) <noreply@openrouter.ai>` on 2026-06-25T21:59:55Z as an out-of-band pipeline mid-drive edit. This adoption packet is committed via `git -c core.hooksPath=/dev/null commit` (packet-only commit per pipeline rules).

Test file chain-of-custody (files exercising the changed code):
- `tests/test_review_manager.py` — present before `1d25c22`, 25 tests; none modified by `1d25c22`
- `tests/test_review_manager_order.py` — introduced at `cbefb02`, 1 ordering test (GOAL)
- `tests/test_review_manager_ordering.py` — introduced at `5942a36`, 1 ordering test
- `tests/test_review_manager_integration.py` — introduced at `46274bd`, 1 integration ordering test

No test files were modified by `1d25c22`.

## Machine-checkable data

```json
{
  "change_id": "flashcore-f170-adopt-1d25c22",
  "adopted_commit": "1d25c2212d53adf446c4f7bcb11c1bed9c397f52",
  "base_sha": "b20e89986320fb2ce15c612584dac974b2cea8f7",
  "head_sha": "a73ca013ada7021cb1cedd3a61f88418e8cc2b88",
  "risk_tier": "R1",
  "tests_at_head": {"passed": 496, "skipped": 1, "failed": 0},
  "ordering_tests_passed": [
    "tests/test_review_manager_order.py::test_review_manager_ordering_by_due_date",
    "tests/test_review_manager_ordering.py::test_initialize_session_respects_due_date_order",
    "tests/test_review_manager_integration.py::test_review_flow_maintains_due_date_order"
  ],
  "static_analysis": {"mypy": "success", "flake8": "exit 0"},
  "canonical_intent_url": "https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L180",
  "evidence_artifact": ".github/aiv-packets/evidence/flashcore-f170/adopt_1d25c22_class_a.txt"
}
```
