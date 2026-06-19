# c2-f82 Plan — Bound Infinite Retry Loop in `start_review_flow`

**Finding:** F82 (audit/02-static-audit.md#L92)
**Stage:** c2 (write-code follows)
**Risk tier:** R1
**Branch:** `fix/c2-f82`
**check-drift iteration 1 verdict:** `.aiv/verdicts/c2-f82/check-drift.md` — PARTIAL. One hard stop resolved in this revision: GT-3 (Drives A/D/E) — gate [5] re-tagged from static grep to CliRunner execution test; `tests/cli/test_main.py` added to scope; Commit 5 (new) delivers the live-fire exit-code proof.

> **AskUserQuestion gate status:** The tool was invoked twice in the plan stage and
> returned a tool error both times. Design decisions in §7 are locked via operator
> cost-function scoring (rationale provided per decision). The human must confirm or
> override these choices before any code is written at the write-code stage.

---

## §1 Context

`start_review_flow()` (`flashcore/cli/review_ui.py:68-128`) manages the interactive
CLI review loop. On every iteration it calls `manager.get_next_card()`, which always
returns `review_queue[0]` without consuming it (`review_manager.py:127`). When
`submit_review()` raises an exception, the handler at `review_ui.py:106-111` logs the
error, prints a message, and calls `continue` — but never removes the failed card from
the queue. Because `_remove_card_from_queue()` is private and is only invoked on the
success path (`review_manager.py:210`), the failed card stays at `review_queue[0]`
and is returned again on the next `get_next_card()` call, creating an unbounded
infinite retry loop for any persistent error (DB corruption, scheduler failure, etc.).

Two additional gaps: (a) "Well done" is emitted unconditionally at `review_ui.py:127`
regardless of how many reviews failed; (b) `start_review_flow` returns `None` and its
only caller (`_review_logic.py:43`) ignores the return, so total failure is
undetectable by the process exit code.

**Canonical Class E intent anchor (all AIV claims must cite this SHA-pinned URL):**
`https://github.com/ImmortalDemonGod/flashcore/blob/5bb2ea2ab72239e0d2de7cc51fd4b5b766e44bfb/audit/02-static-audit.md#L92`

---

## §2 Verified state (direct reads, 2026-06-19)

No Explore agents used. All anchors below were confirmed by direct `Read` tool calls
on 2026-06-19.

| # | Claim | Source anchor | Status |
|---|-------|---------------|--------|
| V1 | `get_next_card()` returns `review_queue[0]` without popping | `review_manager.py:127` | VERIFIED |
| V2 | `_remove_card_from_queue()` called only on `submit_review` success path | `review_manager.py:210` | VERIFIED |
| V3 | `submit_review` exception path re-raises without mutating queue | `review_manager.py:214-216` | VERIFIED |
| V4 | `continue` in exception handler does not remove the failed card | `review_ui.py:111` | VERIFIED |
| V5 | "Well done" printed unconditionally at loop end | `review_ui.py:127` | VERIFIED |
| V6 | `start_review_flow` return annotation is `-> None` | `review_ui.py:70` | VERIFIED |
| V7 | `_review_logic.py:43` discards the return value of `start_review_flow` | `_review_logic.py:43` | VERIFIED |
| V8 | CLI exit convention: `raise typer.Exit(code=1)` | `main.py:58` | VERIFIED |
| V9 | Existing exception test uses `get_next_card.side_effect = [card, None]`, masking the infinite-loop path | `test_review_ui.py:133` | VERIFIED |
| V10 | No existing test asserts "Well done" present or absent | `test_review_ui.py` full read | VERIFIED |
| V11 | `start_review_flow` has exactly one caller | `_review_logic.py:43` | VERIFIED |
| V12 | `_remove_card_from_queue` uses a list-comprehension filter; UUID-not-found is a safe no-op | `review_manager.py:151-153` | VERIFIED |
| V13 | `test_review_all_logic.py` does not import from `review_ui.py` | `test_review_all_logic.py:1-18` | VERIFIED |
| V14 | `_review_logic.py` does not currently import `typer` | `_review_logic.py:1-8` | VERIFIED |
| V15 | No taskmaster entry tracks F82 | `grep -rn "F82" .taskmaster/tasks/` → no output | VERIFIED |
| V16 | Test baseline: 480 tests, 1 skipped | CLAUDE.md | VERIFIED (documented) |
| V17 | `tests/cli/test_main.py` exists and uses `CliRunner` + `result.exit_code == 1` at ~14 sites — live-fire CLI exit-code pattern is established in the project | `grep -c "exit_code" tests/cli/test_main.py` — pre-change read confirmed non-zero | VERIFIED |

---

## §5 Memory + lesson references

No `MEMORY.md` or lesson store present (brief confirms: "no MEMORY.md found; lesson
store skipped"). Lessons are sourced from CLAUDE.md and the brief.

**Active lessons applied in this plan:**

- **E010 trap:** avoid "fix/fixed/resolve/resolved/patch/hotfix" in all AIV `-c`
  claim text; rephrase to "corrects", "bounds", "suppresses", "updates", "advances".
  Source: CLAUDE.md § Known AIV Gotchas.
- **Intent URL must be SHA-pinned:** Class E anchor is the audit record at
  `5bb2ea2ab72239e0d2de7cc51fd4b5b766e44bfb` — not a mutable branch ref and not a
  taskmaster task (no taskmaster entry for F82 confirmed by V15).
- **Never merge autonomously:** H2 (judge + merge) is the human's act.
- **`aiv abandon` requires piped confirmation:** `echo "y" | aiv abandon`.
- **`--skip-checks` is R0-only:** Do not pass `--skip-checks` with `-t R1` or higher.
- **Test layer contract:** Unit tests must explicitly set all inputs that callers
  produce; never assume mock defaults simulate real behavior.

---

## §6 Strict scope boundaries

### IN SCOPE (every site where the loop-boundedness invariant must hold)

| File | Why in scope |
|------|-------------|
| `flashcore/review_manager.py` | Must expose a public API so `review_ui.py` can advance past a failed card without reaching into a private method |
| `flashcore/cli/review_ui.py` | Primary bug site: exception handler, counter tracking, conditional message, return type |
| `flashcore/cli/_review_logic.py` | Single caller; must wire the bool return to `typer.Exit(code=1)` on total failure |
| `tests/cli/test_review_ui.py` | Strengthen masked test; add all-fail test; add Well-done regression guard |
| `tests/cli/test_main.py` | CliRunner exit-code assertion: `result.exit_code == 1` when all reviews fail — live-fire proof of the `typer.Exit` wiring in `_review_logic.py` (evidence class A/B; established convention, V17) |
| `audit/02-static-audit.md` | Finding status must be updated to record the correcting commit SHA (gate [12]) |

### OUT OF SCOPE (classified per operator cost function Drive A)

| File / Item | Classification | Justification |
|-------------|---------------|---------------|
| `flashcore/cli/_review_all_logic.py` | nice-to-have | Separate code path; uses a simple for-loop over cards, not a queue-based retry; the loop-boundedness invariant does not apply there |
| `tests/cli/test_review_all_logic.py` | nice-to-have | Tests a separate module; `start_review_flow` tests do not belong here |
| Retry-with-backoff / per-card retry budget | nice-to-have | Architectural policy decision; out of scope by design |
| `ReviewSessionManager` iterator refactor | nice-to-have | Architectural; separate concern |
| F83–F114 audit findings | nice-to-have | Each is a separate PR |
| F85 (`_review_logic.py` DB connection leak) | nice-to-have | Separate finding; separate PR |

**Drive A justification:** All sites where the loop-boundedness invariant must hold
have been enumerated. Only `start_review_flow` in `review_ui.py` has the queue-based
retry pattern. No other code path shares this invariant; the in-scope list is
semantically complete.

---

## §7 Locked design decisions

> These decisions are locked based on the operator cost function. Operator must
> confirm or override before writing code. AskUserQuestion was attempted twice in
> this stage and returned tool errors; decisions are scored explicitly below.

### Decision 1 — Advance mechanism: PATH A with new public `skip_card()` method

**Chosen:** Path A, sub-option A1 — add `skip_card(self, card_uuid: UUID) -> None`
to `ReviewSessionManager`; call it from the exception handler in `review_ui.py`.

**Cost-function scoring:**

| Drive | Path A + public `skip_card()` | Path A + private `_remove_card_from_queue` | Path B (break) |
|-------|-------------------------------|-------------------------------------------|----------------|
| A (scope/root-cause) | Fixes root cause: card removed from queue, loop advances | Fixes root cause | **DISFAVORED** — masks root cause; card remains in queue; other cards not reviewed |
| B (exemption) | None needed | None needed | Implicitly exempts un-reviewed remaining cards without justification |
| C (ground-truth) | Reuses existing `_remove_card_from_queue` logic (V12) | Same | N/A |
| D (no false completion) | Session completes; all remaining cards reviewed | Same | **DISFAVORED** — session silently truncates; caller believes session ran to completion |
| E (live-fire) | Unit + integration; no extra infra boundary | Same | Same |

Public `skip_card()` is preferred over private access because `review_ui.py` is a
CLI presentation module that should not reach into private internals of a domain-logic
class. The `_`-prefix is a Python convention for "do not call outside the class".
Adding a one-line public wrapper (`def skip_card(self, card_uuid: UUID) -> None: self._remove_card_from_queue(card_uuid)`) correctly exposes the intended
capability without leaking queue internals.

Path B is **DISFAVORED**: it does not fix the root cause (card stays in queue; loop
just doesn't run again because the session exits), silently drops remaining cards
(Drive D), and masks a design flaw rather than correcting it.

### Decision 2 — End-of-session message: NEUTRAL ("Well done" only on 100% success)

**Chosen:**
- All succeed → `"Review session finished. Well done!"`
- Mixed (some failed, some succeeded) → `"Review session finished."`
- All failed → `"Review session failed."`

**Rationale:** "Well done" when any submission failed misleads the user about session
quality (Drive D: false completion). The finding's gate [3] already mandates
suppressing it on total failure; extending to mixed is the consistent honest rule with
zero additional cost. The "show error count" variant is a nice-to-have that can be
added in a follow-up without changing semantics.

### Decision 3 — Failure signal: RETURN BOOL + CALLER RAISES `typer.Exit`

**Chosen:** `start_review_flow` returns `bool`. `_review_logic.py` captures the
return value and raises `typer.Exit(code=1)` when it is `False`.

**Return-value semantics:**
- `False`: `due_cards_count > 0` AND `success_count == 0` AND `failed_count > 0`
  (total failure — cards were attempted and all failed)
- `True`: empty session (vacuous success), all-success, or mixed outcome

**Cost-function rationale:** Raising `typer.Exit` directly from `review_ui.py` would
add a framework dependency to a non-entry-point module and make the function
untestable without mocking typer internals. Returning a bool keeps `start_review_flow`
framework-agnostic; all typer coupling stays in `_review_logic.py`, which already
orchestrates DB, scheduler, and manager construction. "Log-only" is **DISFAVORED**
(Drive D: callers cannot detect total failure; silent degradation).

### Decision 4 — Test location: `test_review_ui.py` for unit tests; `test_main.py` for CLI exit-code proof

**Chosen:** Unit tests for `start_review_flow` (bounded loop, conditional message, bool
return) go in `tests/cli/test_review_ui.py`. The execution proof that `typer.Exit(code=1)`
is actually raised when the caller (`_review_logic.py`) handles `False` goes in
`tests/cli/test_main.py` as a CliRunner test, following the established project convention
(V17, ~14 existing sites). This two-file placement separates concerns: unit behavior of
`start_review_flow` vs live-fire CLI exit-code wiring of the full command.

**Rationale:** `start_review_flow` unit tests belong in `test_review_ui.py` (module
alignment). The CLI exit-code assertion is NOT a `start_review_flow` unit test — it is a
live-fire test of the `_review_logic.py → typer.Exit` wiring, which is exercised only at
the CLI invocation boundary. The project's own convention for this evidence class is
CliRunner + `result.exit_code == 1` in `test_main.py` (V17); using the same file and
pattern provides evidence class A/B (live-fire). GT-3 from check-drift iteration 1
establishes that the grep-only proof is NOT sufficient and that an execution test is
demonstrably possible — which rules out declaring it out-of-scope (Drive B: exemption
must be impossible, not merely costly).

---

## §9 Sequenced atomic-commit plan

**Branch:** `fix/c2-f82` (current, confirmed by `git branch --show-current`)
**AIV change ID:** `c2-f82`

**Pre-work:**
```bash
aiv status
# If stale context exists:
echo "y" | aiv abandon
# Open the change:
aiv begin c2-f82 --mode pr \
  --description "Bound infinite retry loop in start_review_flow [F82]"
```

---

### Commit 1 — `flashcore/review_manager.py`

**What changes:** Add `skip_card(self, card_uuid: UUID) -> None` as a public method
immediately after `_remove_card_from_queue`. Body: `self._remove_card_from_queue(card_uuid)`.

**Test-layer note:** This method is a one-line delegation. Unit test coverage is
provided by the integration with `start_review_flow` (tested in Commit 4). No
standalone unit test is needed for a delegation wrapper.

```bash
git add flashcore/review_manager.py
aiv commit flashcore/review_manager.py \
  -m "feat(review_manager): add public skip_card method to advance past failed card" \
  -t R1 \
  -c "skip_card(card_uuid) delegates to _remove_card_from_queue; callers in the UI layer can advance past a failed card without crossing the private-method boundary" \
  -i "https://github.com/ImmortalDemonGod/flashcore/blob/5bb2ea2ab72239e0d2de7cc51fd4b5b766e44bfb/audit/02-static-audit.md#L92" \
  --requirement "Path A public-API prerequisite — gates [1] [7]" \
  -r "R1: new public one-line method on existing class; no schema changes; no security surface" \
  -s "Expose queue-advancement capability publicly so review_ui.py does not reach into private manager internals"
```

---

### Commit 2 — `flashcore/cli/review_ui.py`

**What changes:**
1. Add `import typer` — NOT needed here (typer coupling stays in `_review_logic.py`).
2. Change return annotation: `-> None` → `-> bool`.
3. Add counters before the while loop: `success_count = 0` and `failed_count = 0`.
4. In the exception handler (after `console.print`): add
   `manager.skip_card(card.uuid)` then `failed_count += 1` (keep `continue`).
5. On the success path (after `submit_review` returns): add `success_count += 1`.
6. Replace the unconditional "Well done" print at the end of the while loop with a
   conditional block:
   ```python
   if failed_count > 0 and success_count == 0:
       console.print("[bold red]Review session failed.[/bold red]")
       return False
   elif failed_count > 0:
       console.print("[bold cyan]Review session finished.[/bold cyan]")
       return True
   else:
       console.print("[bold cyan]Review session finished. Well done![/bold cyan]")
       return True
   ```
7. Change the early-exit for no-cards path (`due_cards_count == 0`) to `return True`
   (vacuous success; nothing failed).

**Test-layer contract for Commit 2:**
- `manager` (a `ReviewSessionManager`) is produced by the hub caller `_review_logic.py`.
  Unit tests must supply it as `MagicMock(spec=ReviewSessionManager)` with explicit
  `review_queue`, `get_next_card.side_effect`, `submit_review.side_effect`, and
  `skip_card.side_effect` set. The unit test does NOT assert that `typer.Exit` is
  raised — that is the integration layer's responsibility (asserted after Commit 3).

```bash
git add flashcore/cli/review_ui.py
aiv commit flashcore/cli/review_ui.py \
  -m "feat(review_ui): bound retry loop, track outcome counts, suppress Well-done on total failure [F82]" \
  -t R1 \
  -c "manager.skip_card called in exception handler advances queue; loop is bounded by queue length not by error persistence" \
  -c "success_count and failed_count counters correctly classify session outcome as total-failure, mixed, or all-success" \
  -c "Well-done message suppressed when success_count == 0 and failed_count > 0; Review-session-failed message emitted instead" \
  -c "start_review_flow return annotation updated to bool; returns False only on total failure (due_cards_count > 0 and all reviews raise)" \
  -i "https://github.com/ImmortalDemonGod/flashcore/blob/5bb2ea2ab72239e0d2de7cc51fd4b5b766e44bfb/audit/02-static-audit.md#L92" \
  --requirement "loop bounded [gate 1]; finite termination [gate 2]; Well-done suppressed [gate 3]; Well-done preserved on success [gate 4]; failure signal returned [gate 5]" \
  -r "R1: logic change in presentation layer; no schema changes; single caller verified by V11" \
  -s "Core F82 correction: bounded loop + conditional message + bool return"
```

---

### Commit 3 — `flashcore/cli/_review_logic.py`

**What changes:**
1. Add `import typer` at the top.
2. Change `start_review_flow(manager, tags=tags)` →
   ```python
   result = start_review_flow(manager, tags=tags)
   if not result:
       raise typer.Exit(code=1)
   ```

**Test-layer contract for Commit 3:**
The unit tests for `start_review_flow` (in `test_review_ui.py`, Commit 4) verify the
bool return value. The execution proof that `typer.Exit(code=1)` is actually raised by
`review_logic()` when `start_review_flow` returns `False` is a CLI-layer concern and is
delivered by **Commit 5** (`tests/cli/test_main.py`, CliRunner test, evidence class A/B).
The static grep approach (previously proposed for gate [5]) is **DISFAVORED per GT-3**:
string-presence cannot detect mis-wiring of the condition, and the project's existing
CliRunner convention makes execution proof demonstrably possible (Drive E cannot claim
"impossible"; Drive D forbids treating grep-presence as PASS). Gate [5] is satisfied by
the Commit 5 CliRunner execution test, not by grep.

```bash
git add flashcore/cli/_review_logic.py
aiv commit flashcore/cli/_review_logic.py \
  -m "feat(review_logic): propagate start_review_flow failure signal to CLI exit [F82]" \
  -t R1 \
  -c "result = start_review_flow(...) captures bool return; typer.Exit(code=1) raised when result is False, signaling total-review-failure to the process" \
  -i "https://github.com/ImmortalDemonGod/flashcore/blob/5bb2ea2ab72239e0d2de7cc51fd4b5b766e44bfb/audit/02-static-audit.md#L92" \
  --requirement "failure signal wired to CLI layer [gate 5]" \
  -r "R1: two-line change to existing caller; no logic change to manager or UI" \
  -s "Wire bool return from start_review_flow to typer.Exit(code=1) on total failure"
```

---

### Commit 4 — `tests/cli/test_review_ui.py`

**What changes (three test modifications):**

#### 4a — Strengthen `test_start_review_flow_submit_review_exception`

Remove the `get_next_card.side_effect = [card, None]` approach (which masked the
infinite-loop bug by making the mock terminate independently of `skip_card`). Replace
with a closure-based side_effect that simulates real queue behaviour:

```python
# Test-layer contract for Commit 4a:
# Input produced by unit-under-test's hub/caller: manager.review_queue (set explicitly)
# Input produced by manager internals: get_next_card reads queue state; skip_card mutates it
# The UNIT test must simulate both via explicit side_effects so the assertion proves
# the loop is bounded because skip_card was called, not because of a [card, None] shortcut.

queue = [card]

def _get_next():
    return queue[0] if queue else None

def _skip(uuid):
    nonlocal queue
    queue = [c for c in queue if c.uuid != uuid]

mock_manager.review_queue = list(queue)
mock_manager.get_next_card.side_effect = _get_next
mock_manager.skip_card.side_effect = _skip
mock_manager.submit_review.side_effect = ValueError("Card not found")

# ... call start_review_flow ...

assert mock_manager.get_next_card.call_count == 2  # card once, None once
assert mock_manager.skip_card.call_count == 1
assert mock_manager.skip_card.call_args[0][0] == card.uuid
result = start_review_flow(mock_manager)
assert result is False
```

#### 4b — New test: `test_start_review_flow_all_fail_suppresses_well_done`

Three-card queue; all `submit_review` calls raise; `skip_card` simulates real queue
advancement via the same closure pattern. Asserts:
- `"Well done"` not in `captured.out`
- `"Review session failed"` in `captured.out`
- `mock_manager.get_next_card.call_count == 4` (3 cards + 1 final None)
- `mock_manager.skip_card.call_count == 3`
- Return value is `False`

This is the primary gate [1], [2], [3] test. The 10-second timeout (gate [2]) is
enforced by `--timeout=10` in the completion contract's verification command.

#### 4c — New test: `test_start_review_flow_success_emits_well_done`

One-card queue; `submit_review` succeeds. For the success path, `submit_review`
itself (in real code) calls `_remove_card_from_queue`; in mock we simulate this via
`get_next_card.side_effect = [card, None]` (the `[card, None]` pattern is valid here
because we are NOT testing the failure path — we are testing that the success path
emits "Well done" and returns `True`). Asserts:
- `"Review session finished. Well done!"` in `captured.out`
- Return value is `True`
- `mock_manager.skip_card` not called

**Test-layer contract for Commit 4:**
- All inputs that `_review_logic.py` (the hub/caller) would produce are set
  explicitly: `manager` as MagicMock, `review_queue`, `get_next_card.side_effect`,
  `submit_review.side_effect`, `skip_card.side_effect`.
- The unit tests assert the bool return of `start_review_flow`, not `typer.Exit`
  (that is the integration layer's concern).
- The display and rating prompts are short-circuited via
  `patch("flashcore.cli.review_ui._display_card", return_value=1000)` and
  `patch("flashcore.cli.review_ui._get_user_rating", return_value=(3, 500))`.

All test assertions are tagged: UNVERIFIED — pending execution at write-code stage.

```bash
git add tests/cli/test_review_ui.py
aiv commit tests/cli/test_review_ui.py \
  -m "test(review_ui): strengthen exception test; add all-fail and success regression tests [F82]" \
  -t R1 \
  -c "test_start_review_flow_submit_review_exception no longer uses [card, None] to mask infinite-loop path; skip_card.side_effect simulates real queue advancement; get_next_card call_count asserted bounded" \
  -c "test_start_review_flow_all_fail_suppresses_well_done: three-card queue, all submit_review calls raise; asserts Well-done absent, Review-session-failed present, call_count bounded at 4, return value False" \
  -c "test_start_review_flow_success_emits_well_done: one-card success path regression guard; asserts Well-done present and return value True" \
  -i "https://github.com/ImmortalDemonGod/flashcore/blob/5bb2ea2ab72239e0d2de7cc51fd4b5b766e44bfb/audit/02-static-audit.md#L92" \
  --requirement "existing exception test strengthened [gate 6]; all-fail test [gate 8]; success regression guard [gate 4]" \
  -r "R1: test-only change; no production logic modified" \
  -s "Test coverage for bounded loop and conditional Well-done message"
```

---

### Commit 5 — `tests/cli/test_main.py`

**What changes:** Add one new CliRunner test that invokes the `review` CLI command
with `start_review_flow` patched to return `False` (and any session/DB setup patched
per the patterns already used in this file), and asserts `result.exit_code == 1`.

This is the **live-fire proof** (evidence class A/B) that the `if not result: raise typer.Exit(code=1)`
wiring in `_review_logic.py` (Commit 3) operates correctly at the CLI boundary.
Following the project convention: CliRunner invocation + `result.exit_code == 1`
assertion (V17, ~14 existing sites in this file).

**Test-layer contract for Commit 5:**
- Input produced by the CLI layer: `runner.invoke(app, ["review"])` — the CliRunner is
  the hub that drives the full `review` command stack.
- `start_review_flow` is patched at `flashcore.cli._review_logic.start_review_flow` to
  return `False` — simulating a total-failure session without needing a real DB or
  `ReviewSessionManager`.
- Any DB/session/scheduler setup in `review_logic()` is patched per the patterns
  already established in `test_main.py` (inspect the file's existing mock fixtures before
  writing; do NOT reinvent the setup pattern).
- The assertion `result.exit_code == 1` confirms the full chain:
  `False` return → `if not result:` branch → `raise typer.Exit(code=1)` → CLI exit code 1.
- Evidence class: A/B (live-fire at CLI boundary); NOT synthetic unit (D/E).

All test assertions are tagged: UNVERIFIED — pending execution at write-code stage.

```bash
git add tests/cli/test_main.py
aiv commit tests/cli/test_main.py \
  -m "test(main): add CliRunner exit-code assertion for review command on total failure [F82]" \
  -t R1 \
  -c "CliRunner invokes the review CLI command with start_review_flow patched to return False; result.exit_code == 1 confirms typer.Exit(code=1) wiring in _review_logic.py at the CLI boundary (evidence class A/B)" \
  -i "https://github.com/ImmortalDemonGod/flashcore/blob/5bb2ea2ab72239e0d2de7cc51fd4b5b766e44bfb/audit/02-static-audit.md#L92" \
  --requirement "failure signal confirmed live at CLI boundary — gate [5]" \
  -r "R1: test-only change; no production logic modified; follows established CliRunner pattern (V17)" \
  -s "Live-fire CLI exit-code proof for typer.Exit wiring on total review failure (GT-3 remediation)"
```

---

### Commit 6 — `audit/02-static-audit.md`

**What changes:** Locate the F82 finding entry near line 92 and append or update a
status note: `CORRECTED: bounded loop + conditional message — <commit-sha of commit 2>`.

**Note:** No taskmaster task entry for F82 found (V15). No `.taskmaster` update
needed.

```bash
git add audit/02-static-audit.md
aiv commit audit/02-static-audit.md \
  -m "docs(audit): record F82 corrected — bounded loop + conditional end-of-session message" \
  -t R0 \
  --skip-checks \
  --skip-reason "Documentation-only update; no executable logic changed" \
  -c "F82 status in audit/02-static-audit.md updated to record the correcting commit SHA" \
  -i "https://github.com/ImmortalDemonGod/flashcore/blob/5bb2ea2ab72239e0d2de7cc51fd4b5b766e44bfb/audit/02-static-audit.md#L92" \
  --requirement "finding closed in commit log [gate 12]; progress tracker closure [gate 10 — N/A for taskmaster, satisfied here]" \
  -r "R0: documentation-only; no logic change" \
  -s "Mark F82 corrected in audit record"
```

---

### Close, validate, and push

```bash
aiv close
aiv check .github/aiv-packets/PACKET_c2-f82*.md
# Fix any blocking errors (do NOT use --no-verify; fix the root cause):
# - E010: rephrase claim text (remove "fix/fixed/resolve" words)
# - Other blocking errors: investigate and correct, then:
git add .github/aiv-packets/PACKET_c2-f82*.md
git commit -m "docs(aiv): address packet validation errors — <what was corrected>"

source .venv/bin/activate && make lint && pytest tests/ -q --tb=short
# Must exit 0 with >= 482 tests (480 baseline + >= 2 new) before pushing.

git push -u origin fix/c2-f82
gh pr create \
  --title "feat: bound infinite retry loop in start_review_flow [F82]" \
  --body "$(cat .github/aiv-packets/PACKET_c2-f82*.md)"
```

---

## §10 Critical files

| File | Role | Change type |
|------|------|-------------|
| `flashcore/cli/review_ui.py` | Primary bug site | Logic: counters, `skip_card` call, conditional message, return type |
| `flashcore/review_manager.py` | Queue management | New public method `skip_card` |
| `flashcore/cli/_review_logic.py` | Single caller | Wire failure signal + `import typer` |
| `tests/cli/test_review_ui.py` | Test coverage | Strengthen 1 + add 2 new tests (unit layer) |
| `tests/cli/test_main.py` | CLI exit-code proof | Add 1 CliRunner test asserting exit_code==1 (live-fire, evidence class A/B) |
| `audit/02-static-audit.md` | Finding status | Status annotation for F82 |

**Files confirmed NOT requiring changes:**

| File | Reason |
|------|--------|
| `flashcore/cli/main.py` | No change needed; typer.Exit propagates from `_review_logic.py` through typer automatically |
| `flashcore/cli/_review_all_logic.py` | Separate code path; different loop architecture (for-loop, no queue-based retry) |
| `tests/cli/test_review_all_logic.py` | Confirmed no `review_ui` imports (V13); tests a separate module |

---

## §11 Reused utilities (must consume, not reimplement)

| Utility | Location | Consumed by | Constraint |
|---------|----------|-------------|-----------|
| `_remove_card_from_queue(card_uuid)` | `review_manager.py:144-153` | `skip_card` wraps it | NEVER reimplement queue removal inline in `review_ui.py`; always delegate through the new public method |
| `typer.Exit(code=1)` | Convention from `main.py:58` | `_review_logic.py` | Use the established pattern; do NOT invent a new exit mechanism |
| `MagicMock(spec=ReviewSessionManager)` | `test_review_ui.py:17-21` (fixture) | New tests reuse the existing `mock_manager` fixture | Extend via `side_effect` assignment; do NOT create a second mock class |

---

## §14 Acceptance criteria

Directly maps to completion contract VERIFY slots [1]–[12].

| Gate | Criterion | Verification command | Status |
|------|-----------|----------------------|--------|
| [1] | Loop bounded when all `submit_review` calls raise | `pytest tests/cli/test_review_ui.py -q -k "exception or all_fail"` | UNVERIFIED — pending execution |
| [2] | Session terminates in finite time | `pytest tests/cli/test_review_ui.py -q -k "all_fail" --timeout=10` | UNVERIFIED — pending execution |
| [3] | "Well done" absent on total failure | `pytest -k "all_fail"` → assert `"Well done" not in captured.out` | UNVERIFIED — pending execution |
| [4] | "Well done" present on all-success | `pytest -k "success"` → assert `"Well done!" in captured.out` | UNVERIFIED — pending execution |
| [5] | Failure signal confirmed live at CLI boundary | `pytest tests/cli/test_main.py -q -k "review_command_exits" --tb=short` → exits 0; `result.exit_code == 1` assertion passes (evidence class A/B; Commit 5 CliRunner test) | UNVERIFIED — pending execution |
| [6] | Existing exception test strengthened | `pytest tests/cli/test_review_ui.py::test_start_review_flow_submit_review_exception -v` passes; `grep -n "side_effect.*None" tests/cli/test_review_ui.py` confirms `[card, None]` pattern removed from that test | UNVERIFIED — pending execution |
| [7] | Advance mechanism recorded in commit log | `git log --oneline HEAD~5..HEAD` shows "skip_card" or "public skip_card" | UNVERIFIED — pending execution |
| [8] | New all-fail test collected and passes | `pytest tests/cli/test_review_ui.py --co -q` lists `test_start_review_flow_all_fail_suppresses_well_done` | UNVERIFIED — pending execution |
| [9] | Full suite passes; ≥482 tests | `source .venv/bin/activate && pytest tests/ -q --tb=short` exits 0; count ≥482 | UNVERIFIED — pending execution |
| [10] | Lint passes | `source .venv/bin/activate && make lint` exits 0; 0 new mypy/flake8/black errors | UNVERIFIED — pending execution |
| [11] | AIV packet validates | `aiv check .github/aiv-packets/PACKET_c2-f82*.md` exits 0 | UNVERIFIED — pending execution |
| [12] | F82 in commit log | `git log --oneline --grep="F82" HEAD~10..HEAD` returns ≥1 result | UNVERIFIED — pending execution |

---

## §15 Risks + mitigations + stop conditions (RED)

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| mypy rejects `-> None` → `-> bool` return-type change | Medium | Run `mypy flashcore/cli/review_ui.py flashcore/cli/_review_logic.py` after each change; the only caller (V11) assigns the return to `result`, which is valid for `bool` |
| E010 blocking error in AIV packet | Medium (known trap) | All `-c` claim text in §9 uses "advances / bounds / suppresses / corrected / updated / records"; review before `aiv commit` |
| `skip_card` called with UUID not in queue | Low | `_remove_card_from_queue` is a no-op when UUID not found (V12); safe by design |
| Existing tests break due to return-type change | Low | Only one caller (V11); existing `test_review_ui.py` tests do not assert on return value; UNVERIFIED — pending execution |
| `test_review_all_logic.py` incidentally breaks | Very low | Confirmed: does not import from `review_ui` (V13); UNVERIFIED — pending execution |
| Stale `aiv` context from a prior abandoned change | Known | Run `aiv status` first; `echo "y" | aiv abandon` if stale |
| `aiv commit` primary-file constraint violated | Known | All six commits use files that exist on disk and have changes relative to HEAD; deleted files are never used as primary |
| `test_main.py` CliRunner test requires complex mocking of DB/session/scheduler | Medium | Read `test_main.py` existing fixtures BEFORE writing; reuse the established mock pattern verbatim rather than inventing a new one; if `review_logic()` setup cannot be patched cleanly, escalate to operator before writing — do NOT fall back to grep-only proof |
| `make lint` fails on new `import typer` in `_review_logic.py` | Low | `typer` is already a project dependency (`main.py` imports it); no new dep needed |

**RED STOP conditions (block all pushes until resolved):**
- Any new mypy error → diagnose and resolve before pushing; never use `# type: ignore` as a bypass
- `aiv check` blocking error (any code other than E004) → rephrase claim text or correct evidence; never `--no-verify`
- `pytest` failure count > 0 → investigate immediately; never rewrite a test to make it pass without establishing which side is wrong
- Test count drops below 480 (baseline) → investigate before pushing

---

## §19 Locked PR sequence position

This PR (F82) is an isolated correctness fix. No predecessor PRs must merge first;
no downstream PRs are blocked on it (confirmed by completion contract "Unblock: none
identified").

- **Predecessor:** none
- **Position:** can merge independently once H2 adjudicates
- **Successor:** none blocked

---

## §20 After-merge handoff

1. **Retro-verify:** Run `pytest tests/cli/test_review_ui.py -q` on `main` after
   merge; record pass/fail in the PR comment thread.

2. **No other `skip_card` callers:** `grep -rn "skip_card" flashcore/ tests/`
   Expected: only `flashcore/review_manager.py` (definition) and
   `flashcore/cli/review_ui.py` (call site).

3. **No other `start_review_flow` callers:** `grep -rn "start_review_flow" flashcore/`
   Expected: only `flashcore/cli/_review_logic.py:43`.

4. **Taskmaster:** No entry for F82 found (V15); no follow-up action needed.

5. **Audit entry:** Confirm `audit/02-static-audit.md` line ~92 shows the correcting
   commit SHA after merge.

6. **Unblocked work:** No downstream PRs are blocked. F83–F114 continue independently.

---

## Revision log

| Iteration | Date | Hard stop resolved | What changed |
|-----------|------|--------------------|--------------|
| 1 → 2 | 2026-06-19 | GT-3 (Drives A/D/E): gate [5] verified by grep-only, not execution | (1) §2 V17 added — confirmed `tests/cli/test_main.py` has established CliRunner+exit_code convention. (2) §6 IN SCOPE: `tests/cli/test_main.py` added with A/B evidence classification. (3) §7 Decision 4: extended to clarify CliRunner test placement in `test_main.py` vs unit tests in `test_review_ui.py`; GT-3 rationale added. (4) §9 Commit 3 test-layer contract: "out-of-scope" language for integration test removed; replaced with forward-reference to Commit 5. (5) §9: new Commit 5 (`tests/cli/test_main.py` CliRunner test) inserted; old Commit 5 renumbered to Commit 6. (6) §10: `tests/cli/test_main.py` added to critical files. (7) §14 gate [5]: verification command changed from static grep to `pytest tests/cli/test_main.py -k "review_command_exits"` with evidence class A/B. (8) §15: risk row added for `test_main.py` mocking complexity with escalation instruction. No other sections changed. |
