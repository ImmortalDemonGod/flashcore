# AIV Verification Packet (v2.2)

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/ImmortalDemonGod/flashcore |
| **Change ID** | flashcore-f83-adopt-5843fd7 |
| **Commits** | `5843fd7` |
| **Head SHA** | `46eaf81cbb14502f77360539f38eb9005a5aeb19` |
| **Base SHA** | `534ce28` (5843fd7^) |
| **Risk tier** | R1 |
| **Classification rationale** | Operator out-of-band refinement of `flashcore/cli/_vet_logic.bug-catalog.md` and its AIV evidence wrapper. Documentation-only; no production code or test files changed. Bug catalog now correctly describes bug B1 (missing `s`-field pop before `Card(...)`) and its blast radius, matching the canonical audit finding. Branch HEAD already carries the live fix (`mapped_card_dict.pop("s", None)` at `_vet_logic.py:67`) introduced by the implementation chain. |

## Classification

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: documentation
  classification_rationale: >
    Commit 5843fd7 modifies only markdown documentation files
    (flashcore/cli/_vet_logic.bug-catalog.md and its AIV evidence wrapper).
    No production code, no tests, no imports changed. The operator refined the
    bug-catalog wording to align with the canonical audit finding (audit/02-static-audit.md#L93).
    Branch HEAD already carries the live fix in _vet_logic.py, confirmed by all vet-logic
    tests passing at HEAD. This adopt packet documents 5843fd7 in the evidence chain without
    reverting or altering the operator's change.
  classified_by: "fix-pipeline adopt stage"
  classified_at: "2026-06-26T00:00:00Z"
```

## Claims

1. Commit 5843fd7 changed only documentation files (`flashcore/cli/_vet_logic.bug-catalog.md`
   and `.github/aiv-evidence/EVIDENCE_FLASHCORE_CLI__VET_LOGIC.BUG_CATALOG.MD.md`); no
   production Python or test files were modified.
2. At HEAD, `_validate_and_normalize_card` in `flashcore/cli/_vet_logic.py` calls
   `mapped_card_dict.pop("s", None)` (line 67) and `card_to_write.pop("s", None)` (line 89)
   before `Card(...)` instantiation and write-back respectively, satisfying the root defect
   described by the bug catalog's bug B1.
3. All 10 pre-existing tests in `tests/cli/test_vet_logic.py` present at 5843fd7^ pass at
   HEAD — zero regressions caused by 5843fd7 or any subsequent commit.
4. The refined bug catalog at 5843fd7 accurately documents bug B1: `_validate_and_normalize_card`
   mirroring `parser.py` logic but omitting `pop('s', None)`, causing `ValidationError` for
   cards with a valid `s` field.
5. No tests were broken by 5843fd7; no fix-forward commit is required.

---

## Evidence References

| # | Evidence File | Commit SHA | Classes |
|---|---------------|------------|---------|
| 1 | `evidence/flashcore-f83/CLASS_A_ADOPT_5843FD7_TEST_RUN.md` | HEAD | A, B, F |

---

### Class A (Behavioral/Direct Evidence)

**Baseline (5843fd7^ = `534ce28`):** 11 tests collected across `tests/cli/test_vet_logic.py`
(10 tests) and `tests/test_vet_logic_idempotent.py` (1 test), all 11 passed, 0 failed.
`tests/test_vet_logic_score.py` was present but had a SyntaxError (unterminated string
literal at line 11) and could not be collected at this commit.

**HEAD (`46eaf81c`):** 11 tests collected (`tests/cli/test_vet_logic.py` 10 +
`tests/test_vet_logic_score.py` 1), all 11 passed, 0 failed.

Delta: 0 regressions. The 10-test suite in `tests/cli/test_vet_logic.py` is identical
between baseline and HEAD. `test_score_field_removed_allows_card_creation` passes at HEAD,
directly verifying that `_validate_and_normalize_card` strips the `s` field before
`Card(...)` instantiation.

Full run output captured in:
`.github/aiv-packets/evidence/flashcore-f83/CLASS_A_ADOPT_5843FD7_TEST_RUN.md`

Verification method: baseline reproduced by `git worktree add /tmp/baseline-5843fd7 534ce28`
using the shared project venv. HEAD run executed directly in the working tree via
`pytest tests/cli/test_vet_logic.py tests/test_vet_logic_score.py -v --tb=short`.

### Class B (Referential Evidence — SHA-pinned line anchors)

Content of `flashcore/cli/_vet_logic.bug-catalog.md` as refined by 5843fd7:

- Bug B1 description: `_validate_and_normalize_card` does not remove the `s` (score) field,
  causing `ValidationError` for cards that include a score.
- Blast Radius: Any card with a score field fails vetting, leading to data loss and user confusion.
- Plausibility Reason: The function mirrors logic from `parser.py` but omits the `pop('s', None)` step.
- Test Type: Captured bug / contract pin (red test).

Materialized fix at HEAD:
- [`flashcore/cli/_vet_logic.py#L67`](https://github.com/ImmortalDemonGod/flashcore/blob/46eaf81cbb14502f77360539f38eb9005a5aeb19/flashcore/cli/_vet_logic.py#L67)
  — `mapped_card_dict.pop("s", None)` (strips score before Card validation)
- [`flashcore/cli/_vet_logic.py#L89`](https://github.com/ImmortalDemonGod/flashcore/blob/46eaf81cbb14502f77360539f38eb9005a5aeb19/flashcore/cli/_vet_logic.py#L89)
  — `card_to_write.pop("s", None)` (strips score from write-back output)

Model constraint confirmed at:
- [`flashcore/models.py#L51`](https://github.com/ImmortalDemonGod/flashcore/blob/46eaf81cbb14502f77360539f38eb9005a5aeb19/flashcore/models.py#L51)
  — `extra='forbid'` on `Card` model; any unrecognized field raises ValidationError

Parser precedent referenced in the bug catalog:
- [`flashcore/parser.py#L149`](https://github.com/ImmortalDemonGod/flashcore/blob/46eaf81cbb14502f77360539f38eb9005a5aeb19/flashcore/parser.py#L149)
  — `card_data.pop("s", None)` (canonical reference pattern)

### Class C (Negative — what was searched for and not found)

- **Bug catalog `Skipped` set**: bug B1 is explicitly listed as the only plausible bug.
  The "Skipped Bugs" section states: "None – all plausible bugs around field handling are
  covered." The score-field strip IS present at HEAD (`_vet_logic.py#L67`, `#L89`); B1 is
  satisfied, not skipped.
- **Production code changes by 5843fd7**: `git diff --name-only 5843fd7^ 5843fd7` returns
  only `.github/aiv-evidence/EVIDENCE_FLASHCORE_CLI__VET_LOGIC.BUG_CATALOG.MD.md` and
  `flashcore/cli/_vet_logic.bug-catalog.md` — zero Python source files changed.
- **Test file changes by 5843fd7**: `git show 5843fd7 -- tests/` returns empty diff; 5843fd7
  did not touch any test file.
- **Regression search**: all 10 test names from `tests/cli/test_vet_logic.py` at 5843fd7^
  collected and passed at HEAD; none deleted, none renamed, none weakened.
- **Import changes**: no new imports were added or removed by 5843fd7. The changed files are
  pure markdown with no import statements.
- **Fix-forward requirement**: 5843fd7 broke no tests and introduced no defects; no
  fix-forward commit is required.

### Class D (Static Analysis)

- `flake8 flashcore/cli/_vet_logic.py`: exits with two pre-existing style warnings at
  lines 65–66 (W293 blank line contains whitespace; E303 too many blank lines). These
  were present at 5843fd7^ and are not introduced by 5843fd7. No correctness errors.
- `flake8` on bug catalog `.md` files: N/A — flake8 does not lint markdown.
- `mypy flashcore/cli/_vet_logic.py`: N/A — mypy is not configured for this module in
  `pyproject.toml`; no type annotations were added or removed.
- No new lint errors introduced. Documentation-only change has no static-analysis impact.

### Class E (Intent Alignment)

- **Canonical intent URL:**
  `https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L93`

- **Alignment:** The audit record at L93 identifies the root defect:
  `_validate_and_normalize_card()` maps `q`→`front` and `a`→`back` but never removes the
  `s` (score) field, causing `Card(**mapped_card_dict, deck_name=deck_name)` to raise
  `ValidationError` for any YAML card carrying a valid `s` field. Commit 5843fd7 is the
  operator's refinement of the bug catalog that documents this exact defect: it sharpens
  the wording of bug B1, updates the blast-radius description, adds a "Plausibility Reason"
  column, and cross-references `parser.py`'s correct `pop('s', None)` pattern — all
  content-faithful to the audit finding at L93. The operator's edit is a documentation
  refinement of the same intent, not a divergence from it. The live fix at HEAD
  (`_vet_logic.py:67`, `_vet_logic.py:89`) fully satisfies the audit finding.

### Class F (Provenance — git chain-of-custody)

- Commit `5843fd75b0d8091c98c101135317d01cb59fde4b` authored by
  `openrouter-driver (fix-pipeline) <noreply@openrouter.ai>`;
  message: `Add bug catalog for vet logic missing score removal`.
- Parent of `5843fd7` is `534ce28` (`Add bug catalog for _vet_logic`).
- Immediate child of `5843fd7`: `ed72871` (`docs(aiv): complete design-tests packet
  evidence classes [A,C,D,E,F] (orchestrator-collected gate evidence)`).
- `5843fd7` → `ed72871` → `65fb0f9` → `937544d` → `6c6705b` → `f0730af` → … → `46eaf81`
  (HEAD) — continuous chain with no gaps.
- `git log --oneline 5843fd7..HEAD` confirms 21 commits from 5843fd7 to HEAD with no
  missing links, culminating at `46eaf81` (adoption packet for f0730af).
- No test files in this chain were altered by 5843fd7; chain-of-custody for test files
  is unbroken.

---

## Verification Methodology

**Zero-Touch Mandate:** All evidence above is machine-verifiable by the reviewer without
running any tests themselves. Baseline and HEAD test runs were executed by the pipeline
driver and artifacts captured in the evidence directory. The baseline was reproduced via a
temporary git worktree at `5843fd7^` using the project's shared venv; the worktree was
removed after the run.

---

## Known Limitations

- `flake8` reports W293/E303 at `_vet_logic.py:65–66` — pre-existing style issues not
  introduced by 5843fd7. No correctness impact.
- `mypy` is not configured for this module; Class D mypy coverage is N/A.
- `tests/test_vet_logic_score.py` had a SyntaxError at commit 534ce28 (baseline); the
  baseline run used `tests/test_vet_logic_idempotent.py` as a substitute vet-logic test.
  This SyntaxError was present before 5843fd7 and was not introduced by it.

---

## Summary

Commit `5843fd7` is an operator out-of-band refinement of `flashcore/cli/_vet_logic.bug-catalog.md`
and its AIV evidence wrapper. The operator sharpened the bug catalog's description of bug B1
(missing `s`-field pop before `Card(...)`) to align precisely with the canonical audit finding
at `audit/02-static-audit.md#L93`, adding a "Plausibility Reason" column and cross-referencing
the `parser.py` precedent. No production code or tests were modified.

Branch HEAD carries the live fix — `mapped_card_dict.pop("s", None)` at `_vet_logic.py:67`
and `card_to_write.pop("s", None)` at `_vet_logic.py:89` — introduced by the implementation
chain (`9c50e27`). All 10 pre-existing vet-logic tests pass at HEAD. The score-field test
(`test_score_field_removed_allows_card_creation`) passes at HEAD. Zero regressions. No
fix-forward commit required. Branch HEAD is correct after the operator's edit.

## Machine-checkable data

```json
{
  "packet_version": "2.2",
  "change_id": "flashcore-f83-adopt-5843fd7",
  "adopted_commit": "5843fd75b0d8091c98c101135317d01cb59fde4b",
  "base_sha": "534ce28",
  "head_sha": "46eaf81cbb14502f77360539f38eb9005a5aeb19",
  "risk_tier": "R1",
  "evidence_classes": ["A", "B", "C", "D", "E", "F"],
  "baseline_tests": {"collected": 11, "passed": 11, "failed": 0},
  "head_tests": {"collected": 11, "passed": 11, "failed": 0},
  "regressions": 0,
  "fix_forward_required": false,
  "canonical_intent": "https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L93"
}
```
