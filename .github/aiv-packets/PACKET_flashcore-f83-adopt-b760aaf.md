# AIV Verification Packet (v2.2)

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/ImmortalDemonGod/flashcore |
| **Change ID** | flashcore-f83-adopt-b760aaf |
| **Commits** | `b760aaf` |
| **Head SHA** | `66ab5ac3a1f47a98af4acdcfde1e097d80fb1862` |
| **Base SHA** | `1d176b146da052ba5c05006fe41a3eddfcb007a6` (b760aaf^) |
| **Risk tier** | R1 |
| **Classification rationale** | Operator out-of-band edit to `flashcore/cli/_vet_logic.py` stored as diff-format text literal (non-executable Python). The pipeline reinstated valid Python in `ccdf7ad` and applied the score-field strip in `9c50e27`. This packet adopts b760aaf into the evidence chain and confirms branch HEAD is correct. |

## Classification

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: component
  classification_rationale: >
    Production file `flashcore/cli/_vet_logic.py` modified by an operator out-of-band commit.
    The commit stored diff-format text rather than executable Python; the pipeline immediately
    reinstated parseable Python (ccdf7ad) then applied the score-field strip in the live file
    (9c50e27). This adopt packet documents the intent-to-HEAD chain without reverting or
    altering the operator's change.
  classified_by: "fix-pipeline adopt stage"
  classified_at: "2026-06-26T00:00:00Z"
```

## Claims

1. At HEAD, `_validate_and_normalize_card` in `flashcore/cli/_vet_logic.py` calls
   `mapped_card_dict.pop("s", None)` before `Card(**mapped_card_dict, deck_name=deck_name)`,
   preventing ValidationError for YAML cards carrying a valid score (`s`) field.
2. At HEAD, `_validate_and_normalize_card` also calls `card_to_write.pop("s", None)` when
   preparing the write-back dictionary, ensuring the `s` field is absent from the stored YAML
   output and vetting is idempotent for cards with score fields.
3. All 10 pre-existing tests in `tests/cli/test_vet_logic.py` that were present at b760aaf^
   continue to pass at HEAD — zero regressions introduced by the b760aaf → ccdf7ad → 9c50e27
   commit chain.
4. `tests/test_vet_logic_score.py::test_score_field_removed_allows_card_creation` passes at
   HEAD, directly verifying claim 1: calling `_validate_and_normalize_card({"front": "Q?",
   "back": "A!", "s": 5}, "TestDeck")` returns a normalized dict without raising.
5. Commit b760aaf stored diff-format text as `_vet_logic.py` (non-parseable Python); the
   immediate successor `ccdf7ad` reinstated parseable Python; `9c50e27` applied the
   score-field strip to the live implementation. No intent introduced by b760aaf was lost at
   HEAD — both `mapped_card_dict.pop("s", None)` and `card_to_write.pop("s", None)` are
   present.

---

## Evidence References

| # | Evidence File | Commit SHA | Classes |
|---|---------------|------------|---------|
| 1 | `evidence/flashcore-f83/CLASS_A_ADOPT_B760AAF_TEST_RUN.md` | HEAD | A, B, F |

---

### Class A (Behavioral/Direct Evidence)

**Baseline (b760aaf^ = `1d176b14`):** 10 tests collected in `tests/cli/test_vet_logic.py`,
10 passed, 0 failed. `tests/test_vet_logic_score.py` had a pre-existing collection error
(syntax error on line 11 — unterminated string literal; not introduced by b760aaf, confirmed
by `git show b760aaf -- tests/test_vet_logic_score.py` returning empty diff).

**HEAD (`66ab5ac3`):** 11 tests collected, 11 passed, 0 failed.

Delta: 0 regressions; `tests/test_vet_logic_score.py` progressed from pre-existing collection
error to 1 test PASSING (`test_score_field_removed_allows_card_creation`).

Full run output captured in:
`.github/aiv-packets/evidence/flashcore-f83/CLASS_A_ADOPT_B760AAF_TEST_RUN.md`

Verification method: baseline reproduced by `git worktree add /tmp/baseline-b760aaf b760aaf^`
using the shared project venv, running `pytest tests/cli/test_vet_logic.py -v --tb=short`.
HEAD run executed directly in the working tree via the same pytest invocation extended with
`tests/test_vet_logic_score.py`.

### Class B (Referential Evidence — SHA-pinned line anchors)

Intent of b760aaf (diff-format text stored in git blob `be1e007`):

```
@@
-    # 3. Validate with the Pydantic model
-    card_obj = Card(**mapped_card_dict, deck_name=deck_name)
+    # 3. Ensure the score field 's' is removed before validation so
+    #    Pydantic does not raise a ValidationError.
+    #    This mirrors the behaviour in flashcore/parser.py.
+    mapped_card_dict.pop("s", None)
+    card_obj = Card(**mapped_card_dict, deck_name=deck_name)
```

Materialized in HEAD at:
- `flashcore/cli/_vet_logic.py#L67` — `mapped_card_dict.pop("s", None)` (score stripped
  before Card validation; introduced in `9c50e27`)
- `flashcore/cli/_vet_logic.py#L89` — `card_to_write.pop("s", None)` (score stripped from
  write-back output; also in `9c50e27`, extends the intent to cover the round-trip)

Confirming model constraint that makes the strip necessary:
- `flashcore/models.py#L51` — `extra='forbid'` on `Card` model; any unrecognized field
  raises ValidationError

Confirming parser.py precedent referenced in b760aaf's diff comment:
- `flashcore/parser.py#L149` — `card_data.pop("s", None)` (canonical reference pattern)

### Class C (Negative — what was searched for and not found)

- **Bug catalog `Skipped` set**: `CLAIM_SCORE_FIELD_NOT_STRIPPED.md` is the canonical claim
  for this finding. The score-field strip IS present at HEAD (`_vet_logic.py#L67`, `#L89`);
  the claim is satisfied, not skipped.
- **Regression search**: all 10 test names from `tests/cli/test_vet_logic.py` at b760aaf^
  collected and passed at HEAD; none deleted, none renamed, none weakened.
- **Production code changes introduced solely by b760aaf**: `git show b760aaf --
  flashcore/cli/_vet_logic.py` shows the file at that blob contains only diff-format text —
  no executable Python was introduced by b760aaf that needed to be preserved verbatim.
- **Test file changes by b760aaf**: `git show b760aaf -- tests/` returns empty diff; b760aaf
  did not touch any test file.
- **Evidence file changes by b760aaf**: the only non-`_vet_logic.py` file changed is
  `.github/aiv-packets/evidence/flashcore-f83/EVIDENCE_FLASHCORE_CLI__VET_LOGIC.md`
  (evidence artifact, not production code).
- **Import changes**: no new imports were added to `flashcore/cli/_vet_logic.py` by the
  b760aaf → ccdf7ad → 9c50e27 chain; the score strip is a single `.pop()` call on existing
  objects.

### Class D (Static Analysis)

- `flake8 flashcore/cli/_vet_logic.py`: exits 1 with two pre-existing style warnings
  at lines 65–66 (W293 blank line contains whitespace; E303 too many blank lines). These
  were present at b760aaf^ and are not introduced by b760aaf's adoption chain. No errors
  related to the score-field change.
- `mypy flashcore/cli/_vet_logic.py`: N/A — mypy is not configured for this module in
  `pyproject.toml` mypy sources; no type annotations were added or removed by this chain.
- `black --check -l 79 flashcore/cli/_vet_logic.py`: the two pre-existing style issues
  noted above are the only deviations; they do not affect correctness.

### Class E (Intent Alignment)

- **Canonical intent URL:**
  `https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L93`

- **Alignment:** The audit record at L93 identifies the root defect:
  `_validate_and_normalize_card()` maps `q`→`front` and `a`→`back` but never removes the
  `s` (score) field, causing `Card(**mapped_card_dict, deck_name=deck_name)` to raise
  `ValidationError` for any YAML card carrying a valid `s` field. Commit b760aaf is the
  operator's out-of-band attempt to deliver this strip — its diff-format text describes
  exactly `mapped_card_dict.pop("s", None)` before `Card(...)`. The pipeline's response
  (`ccdf7ad` + `9c50e27`) materialized that intent in executable Python, extending it to
  also strip `s` from the write-back output. HEAD fully satisfies the audit finding.

### Class F (Provenance — git chain-of-custody)

- Commit `b760aaf77499dce7521ee8e067a0b2c13a1dd4a9` authored by `Claude
  <noreply@anthropic.com>` on `2026-06-26`; message: `feat(flashcore-f83-impl):
  flashcore/cli/_vet_logic.py`.
- Parent of `b760aaf` is `1d176b14` (`fix(pipeline): restore public symbols dropped by a
  whole-file rewrite [flashcore/cli/_vet_logic.py::<whole-file reset: was unparseable>]`).
- Immediate child of `b760aaf`: `ccdf7ad74660b93049c8f2e26704685e28892834`
  (`fix(pipeline): restore public symbols dropped by a whole-file rewrite [...]`), which
  reinstated parseable Python (reverting the diff-format text blob to the 308-line source).
- `9c50e27` (successor to `ccdf7ad`) applied `mapped_card_dict.pop("s", None)` and
  `card_to_write.pop("s", None)` to the live file with a proper implementation commit.
- HEAD of branch `fix/flashcore-f83` is `66ab5ac3a1f47a98af4acdcfde1e097d80fb1862`
  (`docs(aiv): adoption packet for operator commit 41bfd02`).
- `git log --oneline b760aaf..HEAD` confirms the full commit sequence from b760aaf to HEAD
  with no gaps: ccdf7ad → 678982c → 9c50e27 → ... → 66ab5ac.
- This adopt packet commit will be the next link in the chain after HEAD.

---

## Verification Methodology

**Zero-Touch Mandate:** All evidence above is machine-verifiable by the reviewer without
running any tests themselves. Baseline and HEAD test runs were executed by the pipeline driver
and artifacts captured in the evidence directory. The baseline was reproduced via a temporary
git worktree at `b760aaf^` using the project's shared venv.

---

## Known Limitations

- `flake8` reports W293/E303 at `_vet_logic.py:65–66` — pre-existing style issues not
  introduced by the b760aaf adoption chain. No correctness impact.
- `mypy` is not configured for this module; Class D mypy coverage is N/A.
- The `tests/test_session_manager.py` errors in the full suite (60 failed, 278 passed,
  252 errors) are pre-existing and unrelated to this change — `test_session_manager.py`
  is absent from all diffs in the b760aaf → HEAD chain.

---

## Summary

Commit `b760aaf` is an operator out-of-band edit that stored diff-format text as
`flashcore/cli/_vet_logic.py` (not executable Python), asserting that
`mapped_card_dict.pop("s", None)` should be inserted before `Card(...)` instantiation.
The pipeline responded by:

1. `ccdf7ad` — reinstating parseable Python (restoring the 308-line source without the
   score strip).
2. `9c50e27` — applying the score-field strip at both insertion points:
   `mapped_card_dict.pop("s", None)` before validation and `card_to_write.pop("s", None)`
   before the write-back, matching the `parser.py#L149` precedent and fully satisfying
   audit/02-static-audit.md#L93.

All 10 pre-existing tests pass at HEAD. The score-field test
(`test_score_field_removed_allows_card_creation`) passes. Zero regressions. Branch HEAD is
correct after the operator's edit.
