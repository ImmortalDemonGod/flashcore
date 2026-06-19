# AIV Verification Packet (v2.2)

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/ImmortalDemonGod/aiv-protocol |
| **Change ID** | c2-f169-oracle-corr |
| **Commits** | `19499a3` |
| **Head SHA** | `19499a3` |
| **Base SHA** | `cdbe6bf` |
| **Created** | 2026-06-19T05:50:16Z |

## Classification

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: component
  classification_rationale: "R1 — commits the oracle-correction record that independently justifies why two pre-existing FSRS scheduler tests encoded the F169 defect and required setup corrections; errors in this record could mask invalid test weakening, making it part of the correctness verification chain for a production bug fix."
  classified_by: "Claude"
  classified_at: "2026-06-19T05:50:16Z"
```

## Claims

1. test_review_lapsed_card old setup omitted last_review_date, causing scheduler to measure elapsed_days from due-date proxy; on-time elapsed=0 despite card having prior-review history — silent pass on primary F169 defect
2. test_review_early_card old setup omitted last_review_date, causing scheduler to produce elapsed_days=-2 for early review; negative elapsed_days is semantically invalid output that the old oracle accepted as correct
3. Commit 19499a3 (this change's sole commit) adds only two new files (.aiv/oracle-corrections/c2-f169-impl.md and its evidence file); `git show 19499a3 --stat` shows 2 files changed, 211 insertions, 0 deletions — no pre-existing file was modified. Claims 1-2 describe WHY the old test setups were defective; the actual test corrections (adding last_review_date to test_review_lapsed_card and test_review_early_card) were applied at commit c829e46 (c2-f169-impl packet commit), not in this commit. This document provides the independent justification required before those corrections could be accepted.

---

## Evidence References

| # | Evidence File | Commit SHA | Classes |
|---|---------------|------------|---------|
| 1 | EVIDENCE_.AIV_ORACLE_CORRECTIONS_C2_F169_IMPL.MD.md | `19499a3` | A, B, E |



### Class A (Behavioral / Direct Evidence)

The oracle-correction claims are behavioral: they assert that the old test setups produced specific defective values under the buggy scheduler. The following execution evidence supports claims 1 and 2:

```
# Both tests pass with the corrected setup (last_review_date supplied):
$ python -m pytest tests/test_scheduler.py::test_review_lapsed_card \
                   tests/test_scheduler.py::test_review_early_card -v
2 passed

# Without last_review_date, both tests FAIL under the corrected scheduler code
# (scheduler finds no last_review_date, sets elapsed_days=0, making
#  lapsed > on_time: 0 > 0 = False and early < on_time: 0 < 0 = False).
# This confirms the corrections are load-bearing, not cosmetic.
# Verified inline in .aiv/oracle-corrections/c2-f169-impl.md#L116-L138.
```

This commit (19499a3) adds documentation only; no executable behavioral change is introduced by this commit itself. The behavioral evidence above is drawn from the oracle-corrections document's "Evidence of execution" section and from the live test run on branch HEAD.

### Class B (Referential Evidence)

**Scope Inventory** (from 1 file references across evidence files)

- `.aiv/oracle-corrections/c2-f169-impl.md#L1-L149`

### Class C (Negative Evidence)

Searched for and did NOT find in commit 19499a3:

- Any modification to Python source files: `git show 19499a3 --stat` → only `.aiv/oracle-corrections/c2-f169-impl.md` and its evidence file (2 files, 0 deletions); no Python file touched.
- Any test assertion weakened or skipped: no `.py` file changed in this commit; confirmed by `git show 19499a3 --name-only | grep "\.py$"` → no output.
- Any production logic introduced: this commit is documentation-only; grep for `def ` in the oracle-corrections file → only markdown content, no code.
- No scope creep: the oracle-corrections document names exactly two tests (test_review_lapsed_card, test_review_early_card) and two defective behaviors (elapsed=0 on-time, elapsed=-2 early). No other tests or invariants are implicated.

### Class D (Static Analysis)

N/A for type/lint analysis — commit 19499a3 adds only a Markdown document (`.aiv/oracle-corrections/c2-f169-impl.md`) and its evidence file; no Python files were modified. No ruff/mypy/flake8 errors can be introduced by a Markdown-only commit.

Full-suite at branch HEAD (b9c7234): `python -m pytest tests/ -q --tb=no` → **483 passed, 1 skipped**. This commit contributes no test count change (documentation only).

### Class E (Intent Alignment)

Intent: https://github.com/ImmortalDemonGod/flashcore/blob/bc19321bc72cf2467d57ffebc24b92a341ea10d6/audit/02-static-audit.md#L179

This change satisfies the oracle-guard requirement that each edited inherited test have a written
justification anchored to the finding (F169), independent of the implementation.  The oracle-corrections
document at `.aiv/oracle-corrections/c2-f169-impl.md` names both modified tests, explains why their
old setups encoded the F169 elapsed-days defect (not "I changed it to pass"), and provides the
execution evidence that the old setup would cause both assertions to fail under the corrected code.

### Class F (Provenance)

Git chain-of-custody for files touched by commit 19499a3:

```
git show 19499a3 --stat
  .aiv/oracle-corrections/c2-f169-impl.md                        | 149 ++++
  .github/aiv-evidence/EVIDENCE_...C2_F169_IMPL.MD.md            |  62 ++++
  2 files changed, 211 insertions(+), 0 deletions(-)
```

- `.aiv/oracle-corrections/c2-f169-impl.md` — new file created at 19499a3; no prior history.
- The two pre-existing tests documented here (test_review_lapsed_card, test_review_early_card) were in origin/main (L252, L289); modified at c829e46 to add last_review_date; reformatted at b9c7234 (whitespace only). No test assertions were removed or weakened in either commit.
- No test file was touched by commit 19499a3 itself.

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

Change 'c2-f169-oracle-corr': 1 commit(s) across 1 file(s).
