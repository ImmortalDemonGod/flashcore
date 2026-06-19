# check-drift verdict — plan `c2-f169-plan.md` (F169 / plan C2)

> Config: **no `.aiv-workflow.yml` at repo root and `$AIV_WORKFLOW_CONFIG` unset → all defaults**
> (`plans.dir=~/.claude/plans` [empty], all `plans.archetypes.*` blank, `memory.dir=auto`,
> `quality.code_health_cmd` blank, `quality.code_health_changeset_cmd` blank,
> `quality.coverage_floor` blank, `branch.base=origin/main`). Stated per skill.

=== PHASE 0: R-TIER ===
- **Declared:** R1 (`c2-f169-plan.md:8`)
- **Inferred:** R1 (basis: 5 atomic commits; 3 prod files MOD — `models.py`/`scheduler.py`/`review_processor.py` — + 2 test files; **0 migrations** [persistence explicitly deferred, `:367`]; no new dispatcher/substrate; transient `exclude=True` field only)
- **Reconciled:** R1 (declared == inferred, no mismatch)
- **Audit depth (R1):** Phase 1 full · Phase 2 = 2.1, 2.2, 2.3, 2.5, 2.8 · Phase 3 = 3.1, 3.5

=== PHASE 1: STRUCTURAL DRIFT ===
**REFERENCE:** NONE — `plans.archetypes.R1` blank (no config).
`1b: no R1 archetype configured (plans.archetypes.R1 blank) — running section-presence + series-gap checks against the canonical list only, no reference diff.`

**SECTION-PRESENCE (required at R1):**
- §1 Context — present (`:1-28`, finding + Path-decision)
- §2 Verified state (Explore-grounded, 2026-06-19) — present (`:421-428`)
- §5 Memory + lesson references — present (`:430-437`)
- §6 Strict scope boundaries (IN/OUT w/ dispositions) — present (Files-touched `:32-41` = IN; Scope-guard table `:363-371` = OUT w/ deferral targets)
- §7 Locked design decisions (D-numbered, operator-confirmed + date) — **PARTIAL**: decision present & well-argued ("Path decision: Option A" `:12-28`) but **not D-numbered and carries no operator-confirmation date**. Format gap, not absence.
- §9 Sequenced atomic-commit plan — present (Commit 1–5 `:44-261`; flat, labeled "Commit N" not "B0..Bn" — acceptable at R1)
- §10 Critical files (NEW/MOD/**UNTOUCHED**) — **PARTIAL**: NEW/MOD present (Files-touched table); **UNTOUCHED sub-section MISSING** (scope-drift-prevention primitive absent — see 3.9 rationale)
- §11 Reused utilities (must consume, not reimplement) — present, literal phrase (`:439-445`)
- §14 Acceptance criteria — present via completion-contract VERIFY [1]-[13] + Test-layers table (`:265-277`)
- §15 Risks + mitigations + stop conditions (RED) — present, 4 risks each with RED (`:447-454`)
- §19 Locked PR sequence position — present (`:456-461`)
- §20 After-merge handoff — present (completion-contract POST-MERGE `:96-108` + §5 "lessons to CAPTURE post-PR" `:437`)

Sections not required at R1 (R2+/R3): §0/§3/§4/§8/§12/§13/§16/§17/§18/§21/§22 — correctly omitted. Bonus: a Revision log (`:384-417`) is present though not required at R1.

**NUMBERED-SERIES GAPS:**
- D-decisions: not numbered (single Option-A decision; no D1.. series) — see §7 partial above
- B-commits: clean (Commit 1→5, no gaps/dupes)
- R-risks: clean (4 rows, no gaps); Q-questions: n/a (R1, none)

**STREAM STRUCTURE:** n/a (R1, not R3)

**SUBSTANTIVE LOSSES / ADDITIONS:** not assessed — no reference available (archetype blank). Per skill, vs-reference diff disabled this run.

=== PHASE 2: PLAN-QUALITY ===

**2.1 DESIGN-TESTS COVERAGE** — `find . -name '*.bug-catalog.md'` → none.

| File | Bug-catalog? | Plan to add? |
|---|---|---|
| `flashcore/models.py` (MOD) | not present | none planned — relies on Layer-A/B tests |
| `flashcore/scheduler.py` (MOD) | not present | none planned — relies on Layer-A tests |
| `flashcore/review_processor.py` (MOD) | not present | none planned — relies on Layer-B test |

**FLAG:** No bug-catalog companions; coverage is "we'll write tests" (Layer-A + Layer-B). Bug-catalog-first standard not met. Mitigant: the two correctness gates are sharp and outcome-shaped (elapsed_days>0; on-time stability ≠ same-day stability), and a real prior near-miss (by-hand #31 lacked Layer-B) is explicitly addressed by adding Commit 5. Quality flag, not a stop.

**2.2a VERIFICATION MATRIX:** n/a (R2+ when criteria>3).
**2.2b ACCEPTANCE vs VERIFICATION:** distinct — completion-contract separates outcome acceptance ([1] elapsed_days>0, [2] stability distinct) from mechanical verification ([5]/[6]/[7] tests/grep/mypy). Plan's Test-layers table mildly collapses the two but the contract is the gate. OK.
**2.2c TEST LAYERS:** A (unit, Commit 4) present; **B (integration) present and correctly required** — a DB-write path (`add_review_and_update_card`) is touched, and Commit 5 exercises the full `process_review`→scheduler chain. C (E2E) n/a (no UI/route/auth). D (coverage ratchet): functional LOC added but `quality.coverage_floor` blank → no numeric target to cite; ratchet not declared (acceptable at R1). E (local-CI replica): full-suite run + `aiv check` before push present (`:276-277`). F (operator drill): n/a (no subprocess/daemon). No actionable layer-gap.

**2.3 PACKET PRE-READ:** For each MOD file, **code-view sufficient** — these surfaces have no prior AIV packets (fresh harness; §2 grounds via launch-brief, not a prior packet). Packet-pre-read section is R2+ anyway; no gap at R1.

**2.5 CODE-HEALTH BASELINE:**
- `2.5: no per-file code-health tool configured (quality.code_health_cmd blank) — skipped.`
- `2.5: no change-set code-health tool configured (quality.code_health_changeset_cmd blank) — skipped.`

**2.8 MEMORY COVERAGE** — §5 cites CLAUDE.md lessons (E010 trap, aiv-mandatory, SHA-pinned intent, .venv/480-baseline, hub-purity). Universal-principle cross-check:

| Principle | Applies? | Honored? |
|---|---|---|
| Never merge autonomously; human is merge gate | yes | **yes** — contract PRE-MERGE AskUserQuestion `:86-92`, CLAUDE.md |
| Author packets to shape; validate via `aiv` CLI not by eye | yes | **yes** — `:289-358`, `aiv check` gate |
| Merge by rebase, not squash | yes | **uncited** — not addressed in plan (minor flag) |
| Run local-CI replica before every push | yes | **yes** — full suite + `aiv check` pre-push |
| Wall-clock drill for subprocess/daemon | no | n/a |
| Exercise DB-write paths against the **real** database, not an in-memory surrogate | yes | **FLAG** — Layer-B (`:215-261`) uses `in_memory_db` (in-memory SQLite). Same engine/dialect as prod SQLite, so the dialect-bug risk the principle targets is largely mitigated, but strictly the surrogate is used. Note for the operator. |
| Behavior-pinning + green existing tests for refactor PRs | partial (this is a fix, not refactor) | **yes** — 15 existing scheduler tests pinned; RED stop = "any existing scheduler test regresses" |

=== PHASE 3: PLAN-GRAPH + TEMPORAL (R1 → 3.1, 3.5 only) ===

**3.1 BASE-SHA DRIFT:** Plan declares base `origin/main` @ `b5e1c4b` (`:6`, `:428`). Probe: `git rev-list --count b5e1c4b..origin/main` = **0**. origin/main HEAD is still `b5e1c4b`. **Risk: LOW** — zero drift, pre-authoring verifications (§2) remain valid. (Working branch HEAD `cd5f826` is 8 commits ahead of base, but those are pipeline/plan-authoring commits, not the implementation slot.)

**3.5 STOP CONDITIONS (RED):** present per risk (`:447-454`) — thresholds named and falsifiable: "full suite < 480 passed", "any None-arithmetic TypeError in learning/new-card tests", "field reaches the cards table", "`aiv check` returns a blocking error". Escalation = abort/revert. **Pass.**

(3.2 conflicts-with, 3.3 open-questions, 3.4 streams, 3.6–3.9 — not gated at R1. Noted anyway: only one plan in `.aiv/plans/` and `~/.claude/plans` empty → no conflicts-with collisions; no open-questions queue exists; UNTOUCHED-files gap noted under §10 above.)

=== ADVERSARIAL GROUNDING (claims re-executed) ===
- `flashcore/scheduler.py:211-212` bug confirmed: `fsrs_card.last_review = fsrs_card.due` then elapsed_days from `last_review.date()` → 0 on-time. ✓ (read source)
- `get_latest_review_for_card` EXISTS at `flashcore/db/database.py:834`. ✓ (plan said :834 — exact)
- `Card.last_review_id` (`models.py:57`) and `next_due_date` (`:61`) exist; `last_review_date` not yet present (the field this PR adds). ✓
- **Layer-B test soundness confirmed:** `add_review_and_update_card` sets the card's `last_review_id` (`database.py:693` `SET last_review_id = $1`), so after the first `process_review` the returned card has `last_review_id != None` → Commit 3's guard `if card.last_review_id is not None` fires on the second review and the test exercises the real plumbing (not a false-green). ✓
- `tests/test_scheduler.py` has 15 `def test_`; `test_review_lapsed_card` (`:252`, asserts `result_lapsed.elapsed_days > result_on_time.elapsed_days`) confirms the else-fallback rationale at `:95-101` is real. ✓

=== COORDINATION FLAG (non-section) ===
Plan declares branch `feat/c2-pr-f169-fsrs-elapsed-days-b1` (`:6`) but the actual working branch is `feat/c2-fsrs-harness` (matches the FINDING header). Completion-contract VERIFY [9] (`:58-61`) requires the `...-b1` branch name **exactly**. Reconcile before execution/VERIFY [9] — not a plan-structure defect, but it will fail the contract's branch-shape check as written.

=== OVERALL VERDICT ===
- **Plan structural integrity: pass** — every section required at R1 is substantively present; the two gaps are sub-element/format level (§10 UNTOUCHED sub-section missing; §7 not D-numbered/operator-dated), not absent top-level sections.
- **Plan quality audit: partial** — (1) no bug-catalog companions (test-first, not catalog-first); (2) Layer-B uses in-memory SQLite surrogate (mitigated, same engine); (3) rebase-not-squash uncited. All non-fatal; correctness gates and Layer-B plumbing are sound.
- **Plan-graph readiness: pass** — base-SHA drift 0 (low risk); RED stop-conditions present per risk; no conflicting in-flight plans.
- **HARD STOPS: none** (R1 requires no open-questions queue; none block B0).
- **Recommended next action:** proceed to execution. Before B0, optionally tighten: add a §10 **UNTOUCHED** sub-section (e.g., `db/database.py` consumed-not-modified, no migration), D-number the Option-A decision with the operator-confirm date, and **reconcile the branch name** with completion-contract VERIFY [9].

=== SURVIVORSHIP-BIAS DISCLOSURE ===
This template is induced from the project's own plan corpus (`plans.dir`), weighted toward plans that shipped. The corpus is a survivorship sample: it tells you what merged plans happened to contain, NOT what plans need to succeed. Here the corpus is effectively empty (`~/.claude/plans` empty; no archetypes configured), so Phase 1 ran section-presence + series-gap against the canonical list only — there is no reference diff and no calibration to a surviving sample. Sections marked OPTIONAL are observed-rare-but-load-bearing; sections not in the template may still be load-bearing for failure modes not yet encountered. A clean structural pass means "matches the canonical list", not "cannot fail". Promotion criterion for any new template section: name the specific failure mode it would have prevented.

## Machine-checkable data

```json
{
  "schema": "check_drift_verdict@1",
  "r_tier": "R1",
  "audit_depth_complete": true,
  "structural_integrity": "pass",
  "plan_quality": "partial",
  "plan_graph": "pass",
  "hard_stops": [],
  "open_substantive_losses": 0,
  "iteration": 1
}
```
