# AIV Verification Packet (v2.2)

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/ImmortalDemonGod/flashcore |
| **Change ID** | flashcore-f83-adopt-b438dbd |
| **Commits** | `b438dbd` (operator out-of-band) |
| **Head SHA** | `b05610c60c9a13e0707100ad5142e2079644d461` |
| **Base SHA** | `4f3ce12bdd49f2eb6b1fc66af7bc63bb2c843613` (b438dbd^) |
| **Risk tier** | R1 |
| **Classification rationale** | Operator out-of-band addition of `.github/aiv-claims/CLAIM_SCORE_FIELD_NOT_STRIPPED.md` (12 lines) and `.github/aiv-evidence/EVIDENCE_.GITHUB_AIV_CLAIMS.md` (73 lines). Both are markdown documentation files; no production Python source was modified. The claim document records the bug's defect assertion (that `_validate_and_normalize_card` does not remove the `s` field) as a named, Class-C evidence artifact, tightening the evidence chain around the canonical audit finding. Risk tier R1 because the files enter the evidence chain with behavioral claims that must be verified against the fix record. |

## Classification

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: ".github/aiv-claims/CLAIM_SCORE_FIELD_NOT_STRIPPED.md, .github/aiv-evidence/EVIDENCE_.GITHUB_AIV_CLAIMS.md"
  classification_rationale: >
    Commit b438dbd adds one claim document and one evidence-wrapper markdown file.
    No production Python files, test files, or existing evidence files were modified or deleted.
    The claim (CLAIM-001) documents the defect described in audit/02-static-audit.md#L93:
    _validate_and_normalize_card does not strip the 's' field before Card instantiation.
    This claim is corroborated by the fix commit (9c50e27) which added pop("s", None)
    and by tests/test_vet_logic_score.py which passes GREEN at HEAD. No behavioral impact;
    zero regressions. Risk tier R1 because new evidence files enter the chain with explicit
    claims that require verification.
  classified_by: "fix-pipeline adopt stage"
  classified_at: "2026-06-26T00:00:00Z"
```

## Claims

1. Commit `b438dbd` added exactly two files:
   `.github/aiv-claims/CLAIM_SCORE_FIELD_NOT_STRIPPED.md` (12 lines — claim document) and
   `.github/aiv-evidence/EVIDENCE_.GITHUB_AIV_CLAIMS.md` (73 lines — operator evidence wrapper).
   No production Python files or existing test files were modified.
2. CLAIM-001 in `CLAIM_SCORE_FIELD_NOT_STRIPPED.md` asserts that `_validate_and_normalize_card`
   does NOT remove the `s` field — documenting the bug as it existed before the fix.
   This claim is corroborated by the primary fix at
   [`flashcore/cli/_vet_logic.py#L67`](https://github.com/ImmortalDemonGod/flashcore/blob/b05610c60c9a13e0707100ad5142e2079644d461/flashcore/cli/_vet_logic.py#L67)
   (`mapped_card_dict.pop("s", None)`) which confirms the field was not removed before the fix.
3. All 10 pre-existing `tests/cli/test_vet_logic.py` tests pass GREEN at HEAD — zero regressions.
4. `tests/test_vet_logic_score.py::test_score_field_removed_allows_card_creation` passes GREEN
   at HEAD, confirming the defect described by CLAIM-001 no longer exists in production.
5. No tests were broken by `b438dbd`; no fix-forward commit is required.

---

## Evidence References

| # | Evidence File | Commit SHA | Classes |
|---|---------------|------------|---------|
| 1 | `evidence/flashcore-f83/CLASS_A_ADOPT_B438DBD_TEST_RUN.md` | `b05610c` | A, B, F |

---

### Class A (Behavioral/Direct Evidence)

**Evidence artifact:** [`.github/aiv-packets/evidence/flashcore-f83/CLASS_A_ADOPT_B438DBD_TEST_RUN.md`](https://github.com/ImmortalDemonGod/flashcore/blob/b05610c60c9a13e0707100ad5142e2079644d461/.github/aiv-packets/evidence/flashcore-f83/CLASS_A_ADOPT_B438DBD_TEST_RUN.md)

**Baseline (b438dbd^ = `4f3ce12`):** 10 tests collected from `tests/cli/test_vet_logic.py` — all 10 PASSED.
`.github/aiv-claims/` did not exist at this commit.
`tests/test_vet_logic_score.py` had a pre-existing SyntaxError and was excluded from the baseline run.

**HEAD (`b05610c`):** 13 tests collected:
`tests/cli/test_vet_logic.py` (10) +
`tests/test_vet_logic_score.py` (1) +
`tests/test_vet_logic_idempotent.py` (1) +
`tests/test_vet_logic.py` (1). All 13 PASSED. Zero failures.

Delta vs baseline: 0 regressions attributable to `b438dbd`. The +3 tests reflect additions
by later commits in the chain; none existed at the baseline. `b438dbd` itself added no test files.

Baseline verification method: `git worktree add /tmp/baseline-b438dbd 4f3ce12` using the shared
project venv. HEAD run executed directly in the working tree at `b05610c` via:
`pytest tests/cli/test_vet_logic.py tests/test_vet_logic_score.py tests/test_vet_logic_idempotent.py tests/test_vet_logic.py -v --tb=short`.

### Class B (Referential Evidence — SHA-pinned line anchors)

**b438dbd changes confirmed:**

- `.github/aiv-claims/CLAIM_SCORE_FIELD_NOT_STRIPPED.md` (added, 12 lines):
  - CLAIM-001 at
    [`CLAIM_SCORE_FIELD_NOT_STRIPPED.md#L4-L8`](https://github.com/ImmortalDemonGod/flashcore/blob/b438dbd048fcd59781a1a5b23bcd6c0a93b3200f/.github/aiv-claims/CLAIM_SCORE_FIELD_NOT_STRIPPED.md#L4)
    — asserts `_validate_and_normalize_card` does NOT remove the `s` field (documents the bug)
  - Evidence Class C note at
    [`CLAIM_SCORE_FIELD_NOT_STRIPPED.md#L10-L12`](https://github.com/ImmortalDemonGod/flashcore/blob/b438dbd048fcd59781a1a5b23bcd6c0a93b3200f/.github/aiv-claims/CLAIM_SCORE_FIELD_NOT_STRIPPED.md#L10)
    — states the output contains the `s` field, therefore lacks correct removal behavior

- `.github/aiv-evidence/EVIDENCE_.GITHUB_AIV_CLAIMS.md` (added, 73 lines):
  — operator's evidence wrapper for the `.github/aiv-claims` directory; contains classification
  yaml, Class E link (canonical intent URL), and Class B scope inventory pinned to `4f3ce12`.

**Materialized fix confirmed at HEAD (related context):**
- [`flashcore/cli/_vet_logic.py#L67`](https://github.com/ImmortalDemonGod/flashcore/blob/b05610c60c9a13e0707100ad5142e2079644d461/flashcore/cli/_vet_logic.py#L67)
  — `mapped_card_dict.pop("s", None)` (score field stripped before Card validation)
- [`flashcore/cli/_vet_logic.py#L89`](https://github.com/ImmortalDemonGod/flashcore/blob/b05610c60c9a13e0707100ad5142e2079644d461/flashcore/cli/_vet_logic.py#L89)
  — `card_to_write.pop("s", None)` (score field stripped from write-back output)

Model constraint confirmed at:
- [`flashcore/models.py#L51`](https://github.com/ImmortalDemonGod/flashcore/blob/b05610c60c9a13e0707100ad5142e2079644d461/flashcore/models.py#L51)
  — `extra='forbid'` on `Card` model (the constraint that makes the bug fatal)

### Class C (Negative — what was searched for and not found)

- **Production code changes**: `git show b438dbd --name-only` returns only
  `.github/aiv-claims/CLAIM_SCORE_FIELD_NOT_STRIPPED.md` and
  `.github/aiv-evidence/EVIDENCE_.GITHUB_AIV_CLAIMS.md` —
  no production Python files modified.
- **Deleted or weakened tests**: `git show b438dbd -- tests/` returns empty diff;
  no test files were touched by `b438dbd`.
- **Regression search**: all 10 test names from `tests/cli/test_vet_logic.py` at `b438dbd^`
  pass at HEAD; none deleted, renamed, or weakened.
- **Bug catalog Skipped set**: no existing Class C claim documents were modified or deleted.
  `b438dbd` creates the first entry in `.github/aiv-claims/`; nothing was overwritten.
- **Fix-forward requirement**: `b438dbd` broke no tests and introduced no defects;
  all tests pass GREEN at HEAD. No fix-forward commit is required.
- **Silent revert**: `b438dbd` adds new files only; no content from the parent state
  (`4f3ce12`) was silently reverted.
- **Subsequent modifications**: `git log --oneline b438dbd..HEAD -- .github/aiv-claims/ .github/aiv-evidence/EVIDENCE_.GITHUB_AIV_CLAIMS.md`
  returns empty — neither file was modified after `b438dbd`. Chain-of-custody is unbroken.

### Class D (Static Analysis)

- `ruff check .github/aiv-claims/ .github/aiv-evidence/EVIDENCE_.GITHUB_AIV_CLAIMS.md` at HEAD:
  `warning: No Python files found under the given path(s) / All checks passed!`
  — Files are markdown; ruff is inapplicable and reports no errors.
- `mypy` is inapplicable to markdown files. Pre-existing mypy errors in
  `flashcore/db/connection.py`, `flashcore/db/schema_manager.py`, `flashcore/db/database.py`,
  and `flashcore/parser.py` are unrelated to `b438dbd` and were present before it.
- No new correctness-class static analysis errors introduced by `b438dbd`.

### Class E (Intent Alignment)

- **Canonical intent URL:**
  `https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L93`

- **Alignment:** The audit record at L93 identifies the root defect:
  `_validate_and_normalize_card()` maps `q`→`front` and `a`→`back` but never removes
  the `s` (score) field, causing `Card(**mapped_card_dict, deck_name=deck_name)` to raise
  `ValidationError` for any YAML card carrying a valid `s` field.

  Commit `b438dbd` adds a named claim document (CLAIM-001) that records this exact defect
  as a structured evidence artifact in the AIV evidence chain. The claim directly names
  the function (`_validate_and_normalize_card`), the field (`s`), and the nature of the
  defect (field NOT removed). This is a direct refinement of the canonical audit finding:
  it formalizes the defect assertion into a named, referenced claim that the fix evidence
  can be measured against. The operator's edit is fully aligned with the audit finding's
  intent — strengthen the evidence chain around the identified defect.

### Class F (Provenance — git chain-of-custody)

- Commit `b438dbd048fcd59781a1a5b23bcd6c0a93b3200f` authored by
  `Claude <noreply@anthropic.com>`;
  message: `test(flashcore-f83-tests): .github/aiv-claims/`.
- Parent of `b438dbd` is `4f3ce12bdd49f2eb6b1fc66af7bc63bb2c843613`
  (`Add red test for score field bug`).
- Chain from `b438dbd` to HEAD: 43 commits with no gaps, confirmed by
  `git log --oneline b438dbd..HEAD` (43 lines).
- `.github/aiv-claims/CLAIM_SCORE_FIELD_NOT_STRIPPED.md` was not modified by any commit
  after `b438dbd`:
  `git log --oneline b438dbd..HEAD -- .github/aiv-claims/` returns empty.
  Chain-of-custody for the claim file is unbroken.
- HEAD is `b05610c60c9a13e0707100ad5142e2079644d461`
  (`docs(aiv): adoption packet for operator commit 6828dc7`).

---

## Verification Methodology

**Zero-Touch Mandate:** All evidence above is machine-verifiable by the reviewer without running
any tests themselves. Baseline and HEAD test runs were executed by the pipeline driver and
artifacts captured in the evidence directory. The baseline was reproduced via a temporary git
worktree at `b438dbd^` using the project's shared venv; the worktree was removed after the run.
HEAD run executed directly in the working tree at `b05610c`.

---

## Known Limitations

- The adopted files are markdown documentation; no Python linting or type-checking applies.
- `mypy` pre-existing errors in `flashcore/db/` and `flashcore/parser.py` are unrelated to
  this change and were present before `b438dbd`.
- `tests/test_vet_logic_score.py` had a SyntaxError at the baseline commit (`4f3ce12`);
  the baseline run excluded it. The SyntaxError was present before `b438dbd` and resolved
  by a later commit in the chain.

---

## Summary

Commit `b438dbd` is the operator's out-of-band addition of a named claim document
(`.github/aiv-claims/CLAIM_SCORE_FIELD_NOT_STRIPPED.md`) and its evidence wrapper.
CLAIM-001 records the defect: `_validate_and_normalize_card` does NOT remove the `s` field,
causing `ValidationError` under `Card(extra='forbid')` for any card carrying a valid `s` value.
This formalizes the defect assertion into the AIV evidence chain for audit/02-static-audit.md#L93.
No production code was modified. All 10 pre-existing `tests/cli/test_vet_logic.py` tests pass
GREEN at HEAD. Zero regressions. No fix-forward commit required. Branch HEAD is correct after
the operator's edit.

## Machine-checkable data

```json
{
  "packet_version": "2.2",
  "change_id": "flashcore-f83-adopt-b438dbd",
  "adopted_commit": "b438dbd048fcd59781a1a5b23bcd6c0a93b3200f",
  "fix_forward_commit": null,
  "base_sha": "4f3ce12bdd49f2eb6b1fc66af7bc63bb2c843613",
  "head_sha": "b05610c60c9a13e0707100ad5142e2079644d461",
  "risk_tier": "R1",
  "evidence_classes": ["A", "B", "C", "D", "E", "F"],
  "baseline_tests": {"collected": 10, "passed": 10, "failed": 0},
  "head_tests": {"collected": 13, "passed": 13, "failed": 0},
  "regressions": 0,
  "fix_forward_required": false,
  "canonical_intent": "https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L93"
}
```
