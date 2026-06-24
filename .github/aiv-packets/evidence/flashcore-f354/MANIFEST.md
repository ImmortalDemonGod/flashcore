# Evidence Manifest — F354 (module docstring `_summary_` placeholder)

## Artifact Inventory

| Artifact | SHA256 | AIV Class | Claim |
|---|---|---|---|
| `baseline_red.txt` | `9ae5c0c4bc248077d3d790dd818d59f4dc69802385c3aff1e4b9e73f9f8ffe39` | A, D | B1: docstring IS `_summary_` on baseline → 2 FAILED, 1 PASSED |
| `head_green.txt` | `c4e27f925027b2a0855355e2c9a1aa87ddf133bca0bd79c76e86cba49d52d465` | A, D | B1+B2+B3: docstring replaced, references types, no stale refs → 3 PASSED |
| `class_c_negative_search.txt` | `bc5e733d7d1aa175f15ec45fb678585d819841eb528be7b725fb7292f43a5842` | C | Negative: `_summary_` absent from `flashcore/` source |
| `class_d_docstring_diff.txt` | `4acf48ffcbce8437e5898116d2225238220291b46df0e5f2586877a10271d540` | D | Before/after diff: `_summary_` → full descriptive docstring |
| `MANIFEST.md` | (self-referential; SHA pinned in commit) | B, F | This manifest |

## Cited Baselines

- **Finding baseline**: `fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965` (origin/main)
- **HEAD**: `fb7df83` — `docs(models): replace _summary_ placeholder with accurate module docstring`

## Claim Verdicts

| Claim | Verdict | Primary Artifact | Evidence |
|---|---|---|---|
| Module imports cleanly | PASS | `head_green.txt` | Targeted F354 test run: 3 passed (B1, B2, B3). Full suite also verified: 496 passed, 1 skipped (pre-existing DB skip) — see Independent Assessor below. |
| Docstring present (pydocstyle/inspection) | PASS | `head_green.txt` | B1: `__doc__` ≠ `_summary_`; B2: docstring references all 5 core types (`Card`, `CardState`, `Rating`, `Review`, `Session`); B3: all references resolve to actual classes |
| Defect EXISTS on baseline (fb1ae5a1) | PASS | `baseline_red.txt` | B1 FAIL: docstring IS `_summary_`; B2 FAIL: no type references in placeholder; B3 vacuous PASS (no names to resolve) |
| Defect GONE at HEAD (fb7df83) | PASS | `head_green.txt` | B1 PASS: docstring ≠ `_summary_`; B2 PASS: 5 type references found; B3 PASS: all resolve |

## Live-fire (Drive E)

N/A — this change is a module-level docstring text replacement with no infra boundary (no DB/subprocess/network/filesystem). The composed-path proof is the pytest run importing the actual `flashcore.models` module and inspecting `__doc__`; this is captured in the Class A/D artifacts.

## AIV Class Coverage

### Class A — Execution
**PRESENT**: pytest contract tests run at baseline (2 FAILED, 1 PASSED, exit 1) and HEAD (3 PASSED, exit 0) — captured in `baseline_red.txt` and `head_green.txt`. Full suite at HEAD: 496 passed, 1 skipped (pre-existing DB skip) — verified in Independent Assessor section below. Artifacts: `baseline_red.txt`, `head_green.txt`.

### Class B — Referential
**PRESENT**: All artifacts SHA256-pinned in this manifest. Claim→artifact map above. Test code reads `flashcore.models.__doc__` — the live module attribute, not a hardcoded string. Artifacts: `MANIFEST.md`.

### Class C — Negative
**PRESENT**: `grep -rn "_summary_" --include="*.py" flashcore/` returns zero hits (exit 1 — grep returns 1 on no-match, which is the expected result). The `_summary_` placeholder is absent from the entire `flashcore/` source tree. Scope searched: `flashcore/*.py` (recursive). Artifacts: `class_c_negative_search.txt`.

### Class D — Differential
**PRESENT**: `git diff fb1ae5a1..HEAD -- flashcore/models.py` shows exact before/after: `_summary_` (1 line) → 8-line descriptive docstring naming all five core domain types. Artifacts: `class_d_docstring_diff.txt`, `baseline_red.txt`, `head_green.txt`.

### Class E — Intent
**PRESENT**: Canonical audit record at https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L364 (immutable SHA-pinned). Finding F354: module docstring reads `_summary_` — template placeholder never replaced. Goal: module imports cleanly; docstring present (pydocstyle/inspection).

### Class F — Provenance
**PRESENT**: SHA256 manifest (this file) covers all 5 artifact files. Test file provenance: F354 tests added in commits `70e2f3a` → `86e52f0` → committed with fix in `fb7df83`. Full signing infra not available; manifest serves as content-addressable proof.

**Operator provenance attestation (per HUMAN review comment on PR #51):** The commits in this branch authored as "Claude noreply@anthropic.com" were actually written by DeepSeek V4 Pro. The git author metadata is incorrect due to pipeline configuration; the AIV packet `classified_by` fields have been corrected to `deepseek/deepseek-v4-pro`. See commit `16000c8` and `PACKET_flashcore_f354_ci.md` Class F for updated provenance chain.

## Adversarial Probe

**Probe**: "Does the test actually exercise the changed code path, or does it merely test a string constant?"  
**Result**: VERIFIED. Tests `import flashcore.models` and read `flashcore.models.__doc__` — the live module attribute. On baseline `fb1ae5a1`, `__doc__` returns `'\n_summary_\n'`; on HEAD `fb7df83`, it returns the full descriptive docstring. The probe confirms the change IS exercised at the module level through Python's standard import + `__doc__` mechanism.

**Probe**: "Could a vacuous replacement (e.g., 'Models here.') pass B1 but still leave the module undocumented?"  
**Result**: CAUGHT by B2 (`test_module_docstring_references_exported_types`). A generic docstring without type names would fail because `_EXPORTED_TYPE_NAMES` ∩ docstring would be empty. The B2 test gates against vacuous replacement.

**Probe**: "Could a renamed/removed class leave stale docstring references after the fix?"  
**Result**: CAUGHT by B3 (`test_module_docstring_type_references_resolve`). Every type name mentioned in the docstring must resolve via `getattr(flashcore.models, name)` to an actual class. B3 is forward-looking — vacuous pass on baseline, live guard on HEAD.

## Independent Assessor

All three F354 tests were run independently in a fresh git worktree of the baseline (`/tmp/flashcore-f354_base` at `fb1ae5a1`) and at HEAD. The test file was copied verbatim; the only variable was the module code. The baseline produced the expected RED failures; HEAD produced GREEN passes. Full suite at HEAD confirms no regressions (496/496 passed).
