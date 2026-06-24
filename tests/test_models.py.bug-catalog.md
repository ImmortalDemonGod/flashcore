# Bug Catalog — `tests/test_models.py`

> Generated: 2026-06-26 | Finding: F354 (medium, doc_code_drift)
> Source module: `flashcore/models.py`
> Canonical intent: https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L364

---

## Module summary (Step 1 — code reading)

### Public interface
`flashcore/models.py` exports five core domain types re-exported via
`flashcore/__init__.py:3-5`:

| Type | Kind | Line | Description |
|---|---|---|---|
| `CardState` | `IntEnum` | L21 | FSRS-defined card memory states: New=0, Learning=1, Review=2, Relearning=3 |
| `Rating` | `IntEnum` | L32 | User recall rating: Again=1, Hard=2, Good=3, Easy=4 |
| `Card` | `BaseModel` | L43 | Pydantic model for flashcard content + FSRS parameters (20 fields + 1 validator + 1 method) |
| `Review` | `BaseModel` | L186 | Pydantic model for a single review event (14 fields + 1 validator) |
| `Session` | `BaseModel` | L285 | Pydantic model for review session tracking (12 fields + 4 methods + 2 properties) |

### Load-bearing comments
- `CardState` docstring (L22-24): "Represents the FSRS-defined state of a card's memory trace" — anchors the enum to the FSRS specification
- `Rating` docstring (L32-34): "Represents the user's rating of their recall performance" — anchors values to FSRS Again/Hard/Good/Easy semantics
- `Card.calculate_complexity_metrics` docstring (L139-155): enumerates all four metrics populated; critical for understanding side-effects
- `Session.add_card_review` (L310-329): comment "If we added a new deck and it's not the first deck, count as switch" — explains non-obvious guard condition
- `Session.end_session` (L305): "If the session is already ended (end_ts is not None), this method does nothing" — idempotency contract

### IO boundaries
- `uuid.uuid4()` — randomness (Card.uuid default, Session.session_uuid default)
- `datetime.now(timezone.utc)` — wall-clock time (Card.added_at/modified_at, Review.ts, Session.start_ts/end_ts)
- `Path` objects — filesystem references (Card.media, Card.source_yaml_file)
- `re.match(KEBAB_CASE_REGEX_PATTERN, tag)` — regex engine boundary

### Branching points
- `Card.validate_tags_kebab_case` — iterates tags set; raises ValueError on non-kebab-case match
- `Card.calculate_complexity_metrics` — 4 conditional assignments: `front_length = len(self.front) if self.front else 0`, etc.
- `Review.check_review_type_is_allowed` — returns v or raises based on set membership
- `Session.calculate_duration` — returns None if `end_ts is None`; fast-path return
- `Session.end_session` — guards on `self.end_ts is None`; no-op if already ended
- `Session.add_card_review` — conditional `deck_switches` increment (two guards)
- `Session.cards_per_minute` — returns None for None or zero `total_duration_ms`; guard on `minutes > 0`

### Type definitions of magic-string contracts
- `CardState = IntEnum` with values `New=0, Learning=1, Review=2, Relearning=3` — four-state FSRS model
- `Rating = IntEnum` with values `Again=1, Hard=2, Good=3, Easy=4` — matches FSRS 1-4 scale
- `Review.review_type: Optional[str]` — allowed values `{"learn", "review", "relearn", "manual"}` enforced by `check_review_type_is_allowed`
- `KEBAB_CASE_REGEX_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"` — kebab-case validation contract

### Existing tests (tests/test_models.py)
- `TestCardModel` — 11 tests: creation (minimal, full), UUID generation, UTC timestamps, kebab-case validation (valid + 6 invalid parametrized), max-length (front/back), min-length (deck_name), extra-forbid, validate_assignment
- `TestReviewModel` — 10 tests: creation (minimal, full), UTC ts, rating validation (valid/invalid), resp_ms, stab_after, elapsed_days, scheduled_interval, review_type (valid parametrized + invalid), extra-forbid
- `TestCardModel` additional: 2 complexity_metrics tests
- `TestSessionModel` — 8 tests: minimal creation, end_session, calculate_duration, add_card_review, record_interruption, cards_per_minute (2: normal + zero-duration edge case)
- **No test** currently asserts the module-level docstring is present or non-placeholder

---

## Bug Catalog (Step 2)

### B1: Module docstring is the `_summary_` template placeholder (F354)
- **The bug**: `flashcore/models.py` module-level docstring at line 2-3 reads exactly
  `"_summary_\n"` — a template placeholder that was never replaced with actual content.
  Any tool or human reading the module docstring (via `help()`, `pydoc`, Sphinx,
  IDE hover, `inspect.getdoc()`) sees only the placeholder text.
- **Blast radius**: Low — no functional impact. But module is the package's core domain
  layer exporting 5 types; missing docstring degrades developer experience and
  documentation tooling output.
- **Why it's plausible**: The placeholder was introduced in initial commit `d7c3702`
  (2025-12-31) and never modified. No CI doc-lint gate (pydocstyle D100 / ruff D100)
  exists to catch it. No test asserts docstring presence. Six months of development
  happened around it without detection — the blind spot is real.
- **Test type(s)**: Captured bug / contract pin + Negative path
- **Rank**: 1 (only catalogued bug; highest blast×plausibility by default)

### B2: Module docstring exists but is semantically empty (generic variant of B1)
- **The bug**: Even if the placeholder were replaced with _any_ text, the docstring might
  be generic boilerplate that does not actually describe the module's contents (e.g.,
  "Models for the application."). Tools/humans get text but not useful information.
- **Blast radius**: Low — same as B1; subtle form of doc_code_drift
- **Why it's plausible**: If the fix is rushed, a well-meaning but generic replacement
  could be committed. Without a semantic check, this wouldn't be caught.
- **Test type(s)**: Invariant (docstring MUST reference at least one of the five exported types)
- **Rank**: 2 (less likely if fix is deliberate; still worth characterizing)

### B3: Docstring references a type that doesn't exist in the module (stale reference)
- **The bug**: A future edit renames or removes a class (e.g., `Card`) but fails to update
  the module docstring, leaving a stale reference. Tools/humans are misled about the module's API.
- **Blast radius**: Medium — documentation claims a type exists in the module but imports fail.
- **Why it's plausible**: Class renames/removals happen; the docstring has no automated
  consistency check against actual module contents.
- **Test type(s)**: Invariant (every type name mentioned in the docstring MUST resolve to
  a class defined in the module)
- **Rank**: 3 (forward-looking; guards against regression after fix)

---

## Skipped (negative space — considered, explicitly not tested)

| Bug | Reason |
|---|---|
| Missing class-level docstrings | All 5 classes already have proper docstrings. Not a gap. |
| Missing method docstrings | All public methods have docstrings. Not a gap. |
| Docstring formatting violations (D209, D400, etc.) | No pydocstyle in project; adding formatting checks is deferred as nice-to-have (see plan §6 Out of Scope) |
| Other modules with template docstrings | `grep -rn "_summary_" --include="*.py"` returns exactly 1 hit (`models.py:2`). No other module has this defect. |
| Docstring internationalization / encoding | Out of scope — project has no i18n infrastructure |

---

## Test design (Step 3 — match each bug to test type)

| Bug | Test | Type | Rationale |
|---|---|---|---|
| B1 | `test_module_docstring_is_not_placeholder` | Captured bug / Negative path | Direct assertion: `__doc__` ≠ `_summary_` placeholder. Catches the exact F354 defect. |
| B2 | `test_module_docstring_references_exported_types` | Invariant | Asserts docstring mentions at least one of the five exported type names; guards against vacuous replacement. |
| B3 | `test_module_docstring_type_references_resolve` | Invariant (forward-looking) | Asserts every capitalized word in docstring that names a member of `__all__` actually resolves to a class in the module. Guards against stale references after refactors. |

**Composition note**: B1 and B2 are composed into a single test for efficiency — the placeholder check is the primary assertion; the content check is a strengthening assertion that also catches the "generic replacement" variant. B3 is a separate test because it exercises a different invariant (name resolution).

---

## Self-critique (Step 4)

### test_module_docstring_is_not_placeholder
- **What specific catalog bug does this catch?** B1 (placeholder `_summary_`).
- **Would this pass for wrong-but-stable output?** No — it explicitly checks for the
  exact placeholder text. If someone writes a wrong docstring that isn't `_summary_`,
  this test passes, but B2 catches that case.
- **Would this fail under a non-behavior-changing refactor?** No — `__doc__` is the
  Python-standard module docstring attribute. A refactor that changes module contents
  without touching the docstring would not break this test (correct). A refactor that
  renames classes but leaves stale docstring references would not be caught by B1
  but IS caught by B3.

### test_module_docstring_references_exported_types
- **What specific catalog bug does this catch?** B2 (vacuous replacement) + B1
  (placeholder doesn't reference types either).
- **Would this pass for wrong-but-stable output?** No — requires at least one type
  name to appear in the docstring. A docstring that says "Utility functions for the
  app" would fail.
- **Would this fail under a non-behavior-changing refactor?** Only if a refactor
  removes all type references from the docstring — which is exactly the class of
  regression B2 is designed to catch. Acceptable.

### test_module_docstring_type_references_resolve
- **What specific catalog bug does this catch?** B3 (stale reference after rename/removal).
- **Would this pass for wrong-but-stable output?** No — it verifies referential integrity
  between docstring text and actual module members via `__all__` and `getattr`.
- **Would this fail under a non-behavior-changing refactor?** No — it only fails if
  the docstring names a type that isn't in the module. Adding a new type and mentioning
  it in the docstring would pass (correct). Renaming a type without updating the
  docstring would fail (correct — that's the bug).

---

## Final evaluation (Step 6)

### Bugs caught (test failed first run — requires fix)
- **B1**: `test_module_docstring_is_not_placeholder` — expected to FAIL because
  `__doc__` currently equals `"_summary_\n"`.
- **B2**: `test_module_docstring_references_exported_types` — expected to FAIL because
  `"_summary_"` contains no type names from the module.
- **B3**: `test_module_docstring_type_references_resolve` — expected to PASS (no
  stale references exist; the placeholder contains no type names, so the "every
  mentioned name resolves" check is vacuously true).

### Bugs characterized (test passed first run)
- **B3** (vacuous pass — no type names in the placeholder, so no stale references to
  check; the test is forward-looking for post-fix regression protection)

### Bugs discovered during writing
- None beyond the F354 finding. Placeholder is the sole defect in this module's docstring.

---

## Investigation pass (Step 7)

### Pass+suspect items
- **B3 vacuous pass**: The test passes because the `_summary_` placeholder contains
  no type names, so the "resolve every mentioned name" iteration is a no-op. This is
  a true characterization — when the placeholder is replaced with actual type names,
  B3 becomes a live guard. **Retained as forward-looking guard.**

### "0 bugs caught" pre-investigation check
Not applicable here — B1 and B2 are expected to FAIL (RED). This is a genuine bug
catalog with 2 expected failures.

### Post-investigation final stats
- **Expected RED tests**: 2 (B1 + B2 — placeholder + vacuous content)
- **Expected GREEN tests**: 1 (B3 — vacuous pass, no stale refs in placeholder)
- **Confirmed real bug**: B1/B2 are the same defect viewed from two angles — the
  `_summary_` placeholder is both non-descriptive (B1) and doesn't reference module
  types (B2).

---

## Test file impact

Tests to be added to `tests/test_models.py` at module level (outside existing test
classes, since they test the module itself rather than a specific class):

1. `test_module_docstring_is_not_placeholder` — RED (fails on current `_summary_`)
2. `test_module_docstring_references_exported_types` — RED (fails on current `_summary_`)
3. `test_module_docstring_type_references_resolve` — GREEN (vacuous pass on current `_summary_`; live guard post-fix)

All three tests use only the public Python interface (`import flashcore.models`,
`flashcore.models.__doc__`, `flashcore.models.__all__`, `getattr`). No implementation
coupling.
