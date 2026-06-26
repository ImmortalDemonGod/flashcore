# AIV Verification Packet (v2.2)

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/ImmortalDemonGod/flashcore |
| **Change ID** | flashcore-f83-adopt-f0730af |
| **Commits** | `f0730af` |
| **Head SHA** | `d42840e4903e1fa8c5350ba6b0d3df18ef50cd81` |
| **Base SHA** | `6c6705b63070ac50cd0bb864b0d47437d5dfe9eb` (f0730af^) |
| **Risk tier** | R1 |
| **Classification rationale** | Operator out-of-band edit to `flashcore/cli/_vet_logic.py` stored as diff-format text literal (non-executable Python). The pipeline reinstated valid Python in `1d176b1` and ultimately applied the score-field strip in `9c50e27`. This packet adopts f0730af into the evidence chain and confirms branch HEAD is correct. |

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
    reinstated parseable Python (1d176b1) then applied the score-field strip in the live file
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
   preparing the write-back dictionary, ensuring the `s` field is absent from stored YAML
   output and vetting is idempotent for cards with score fields.
3. All 10 pre-existing tests in `tests/cli/test_vet_logic.py` present at f0730af^ continue
   to pass at HEAD — zero regressions introduced by the f0730af → 1d176b1 → … → 9c50e27
   commit chain.
4. `tests/test_vet_logic_score.py::test_score_field_removed_allows_card_creation` passes at
   HEAD, directly verifying claim 1: calling `_validate_and_normalize_card({"front": "Q?",
   "back": "A!", "s": 5}, "TestDeck")` returns a normalized dict without raising.
5. Commit f0730af stored diff-format text as `_vet_logic.py` (non-parseable Python); the
   immediate successor chain (`2887b02` → `1d176b1`) reinstated parseable Python; `9c50e27`
   applied the score-field strip to the live implementation. No intent introduced by f0730af
   was lost at HEAD — both `mapped_card_dict.pop("s", None)` and `card_to_write.pop("s",
   None)` are present.

---

## Evidence References

| # | Evidence File | Commit SHA | Classes |
|---|---------------|------------|---------|
| 1 | `evidence/flashcore-f83/CLASS_A_ADOPT_F0730AF_TEST_RUN.md` | HEAD | A, B, F |

---

### Class A (Behavioral/Direct Evidence)

**Baseline (f0730af^ = `6c6705b6`):** 10 tests collected in `tests/cli/test_vet_logic.py`,
10 passed, 0 failed. `tests/test_vet_logic_score.py` was not present at this commit
(the file was added later in the commit chain as part of implementing the score-field fix).

**HEAD (`d42840e4`):** 11 tests collected, 11 passed, 0 failed.

Delta: 0 regressions; `tests/test_vet_logic_score.py` introduces 1 new passing test
(`test_score_field_removed_allows_card_creation`).

Full run output captured in:
`.github/aiv-packets/evidence/flashcore-f83/CLASS_A_ADOPT_F0730AF_TEST_RUN.md`

Verification method: baseline reproduced by `git worktree add /tmp/baseline-f0730af f0730af^`
using the shared project venv, running `pytest tests/cli/test_vet_logic.py -v --tb=short`.
HEAD run executed directly in the working tree via the same pytest invocation extended with
`tests/test_vet_logic_score.py`.

### Class B (Referential Evidence — SHA-pinned line anchors)

Intent of f0730af (diff-format text stored in git blob, "*** Begin Patch" format):

```
@@
 def _validate_and_normalize_card(
     raw_card_dict: Dict[str, Any], deck_name: str
 ):
-    pass
+    """Normalize a raw card dictionary before Pydantic validation.
+
+    The audit identified that the *s* (score) field, if present, should be
+    removed because ``Card`` is declared with ``extra="forbid"``.  The
+    original implementation in :mod:`flashcore.parser` calls
+    ``card_data.pop("s", None)`` before constructing a ``Card`` instance.
+    """
+    mapped_card_dict = dict(raw_card_dict)
+    mapped_card_dict.pop("s", None)
+    try:
+        return Card(**mapped_card_dict, deck_name=deck_name)
+    except ValidationError as err:
+        console.print(f"[red]Card validation error:[/red] {err}")
+        raise
```

Materialized in HEAD at:
- `flashcore/cli/_vet_logic.py#L67` — `mapped_card_dict.pop("s", None)` (score stripped
  before Card validation; introduced in `9c50e27`)
- `flashcore/cli/_vet_logic.py#L89` — `card_to_write.pop("s", None)` (score stripped from
  write-back output; also in `9c50e27`, extends the intent to cover the round-trip)

Confirming model constraint that makes the strip necessary:
- `flashcore/models.py#L51` — `extra='forbid'` on `Card` model; any unrecognized field
  raises ValidationError

Confirming parser.py precedent referenced in f0730af's diff comment:
- `flashcore/parser.py#L149` — `card_data.pop("s", None)` (canonical reference pattern)

### Class C (Negative — what was searched for and not found)

- **Bug catalog `Skipped` set**: `CLAIM_SCORE_FIELD_NOT_STRIPPED.md` is the canonical claim
  for this finding. The score-field strip IS present at HEAD (`_vet_logic.py#L67`, `#L89`);
  the claim is satisfied, not skipped.
- **Regression search**: all 10 test names from `tests/cli/test_vet_logic.py` at f0730af^
  collected and passed at HEAD; none deleted, none renamed, none weakened.
- **Production code changes introduced solely by f0730af**: `git show f0730af --
  flashcore/cli/_vet_logic.py` shows the file at that blob contains only diff-format text
  ("*** Begin Patch" / "*** End Patch") — no executable Python was introduced by f0730af
  that needed to be preserved verbatim.
- **Test file changes by f0730af**: `git show f0730af -- tests/` returns empty diff; f0730af
  did not touch any test file.
- **Evidence file changes by f0730af**: the only non-`_vet_logic.py` file changed is
  `.github/aiv-packets/evidence/flashcore-f83/EVIDENCE_FLASHCORE_CLI__VET_LOGIC.md`
  (evidence artifact, not production code).
- **Import changes**: no new imports were added to `flashcore/cli/_vet_logic.py` by the
  f0730af → 1d176b1 → 9c50e27 chain; the score strip is a single `.pop()` call on existing
  objects.

### Class D (Static Analysis)

- `flake8 flashcore/cli/_vet_logic.py`: exits 1 with two pre-existing style warnings
  at lines 65–66 (W293 blank line contains whitespace; E303 too many blank lines). These
  were present at f0730af^ and are not introduced by f0730af's adoption chain. No errors
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
  `ValidationError` for any YAML card carrying a valid `s` field. Commit f0730af is the
  operator's out-of-band attempt to deliver this strip — its diff-format text describes
  exactly `mapped_card_dict.pop("s", None)` before `Card(...)`, plus a docstring citing
  the audit. The pipeline's response (`2887b02` → `1d176b1` → `b760aaf` → `ccdf7ad` →
  `9c50e27`) materialized that intent in executable Python, extending it to also strip `s`
  from the write-back output. HEAD fully satisfies the audit finding.

### Class F (Provenance — git chain-of-custody)

- Commit `f0730afa5a7d9d33490fc705629975d03b183b02` authored by `Claude
  <noreply@anthropic.com>`; message: `feat(flashcore-f83-impl): flashcore/cli/_vet_logic.py`.
- Parent of `f0730af` is `6c6705b6` (`chore(aiv): restore valid F83 design-tests packet,
  drop name-collision variant`).
- Immediate child of `f0730af`: `2887b02` (`docs(aiv): verification packet for change
  'flashcore-f83-impl'`), a docs-only commit.
- `1d176b1` (successor to `2887b02`) reinstated parseable Python (reverting the diff-format
  text blob to the 308-line source): `fix(pipeline): restore public symbols dropped by a
  whole-file rewrite [flashcore/cli/_vet_logic.py::<whole-file reset: was unparseable>]`.
- `9c50e27` (reached via `b760aaf` → `678982c` → `ccdf7ad` → `9c50e27`) applied
  `mapped_card_dict.pop("s", None)` and `card_to_write.pop("s", None)` to the live file.
- HEAD of branch `fix/flashcore-f83` is `d42840e4903e1fa8c5350ba6b0d3df18ef50cd81`
  (`docs(aiv): adoption packet for operator commit 1d176b1`).
- `git log --oneline f0730af..HEAD` confirms the full commit sequence from f0730af to HEAD
  with no gaps: 2887b02 → 1d176b1 → b760aaf → 678982c → ccdf7ad → 9c50e27 → ... → d42840e.
- This adopt packet commit will be the next link in the chain after HEAD.

---

## Verification Methodology

**Zero-Touch Mandate:** All evidence above is machine-verifiable by the reviewer without
running any tests themselves. Baseline and HEAD test runs were executed by the pipeline
driver and artifacts captured in the evidence directory. The baseline was reproduced via a
temporary git worktree at `f0730af^` using the project's shared venv.

---

## Known Limitations

- `flake8` reports W293/E303 at `_vet_logic.py:65–66` — pre-existing style issues not
  introduced by the f0730af adoption chain. No correctness impact.
- `mypy` is not configured for this module; Class D mypy coverage is N/A.
- The `tests/test_session_manager.py` errors in the full suite are pre-existing and
  unrelated to this change — `test_session_manager.py` is absent from all diffs in the
  f0730af → HEAD chain.

---

## Summary

Commit `f0730af` is an operator out-of-band edit that stored diff-format text as
`flashcore/cli/_vet_logic.py` (not executable Python), asserting that
`mapped_card_dict.pop("s", None)` should be inserted before `Card(...)` instantiation.
The pipeline responded by:

1. `2887b02` — verification packet (docs only).
2. `1d176b1` — reinstating parseable Python (restoring the 308-line source without the
   score strip).
3. `b760aaf` → `ccdf7ad` — a second operator edit + pipeline restore cycle.
4. `9c50e27` — applying the score-field strip at both insertion points:
   `mapped_card_dict.pop("s", None)` before validation and `card_to_write.pop("s", None)`
   before the write-back, matching the `parser.py#L149` precedent and fully satisfying
   audit/02-static-audit.md#L93.

All 10 pre-existing tests pass at HEAD. The score-field test
(`test_score_field_removed_allows_card_creation`) passes. Zero regressions. Branch HEAD is
correct after the operator's edit.

## Machine-checkable data

```json
{
  "packet_version": "2.2",
  "change_id": "flashcore-f83-adopt-f0730af",
  "adopted_commit": "f0730afa5a7d9d33490fc705629975d03b183b02",
  "base_sha": "6c6705b63070ac50cd0bb864b0d47437d5dfe9eb",
  "head_sha": "d42840e4903e1fa8c5350ba6b0d3df18ef50cd81",
  "risk_tier": "R1",
  "evidence_classes": ["A", "B", "C", "D", "E", "F"],
  "baseline_tests": {"collected": 10, "passed": 10, "failed": 0},
  "head_tests": {"collected": 11, "passed": 11, "failed": 0},
  "regressions": 0,
  "canonical_intent": "https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L93"
}
```
