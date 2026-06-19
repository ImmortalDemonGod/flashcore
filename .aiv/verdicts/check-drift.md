# check-drift verdict — plan `c2-f169-plan.md` (F169 / plan C2)

> Config: **no `.aiv-workflow.yml` at repo root and `$AIV_WORKFLOW_CONFIG` unset → all skill
> defaults** (`plans.dir=~/.claude/plans` [empty/absent], all `plans.archetypes.*` blank,
> `memory.dir=auto`, `quality.code_health_cmd` blank, `quality.code_health_changeset_cmd` blank,
> `quality.coverage_floor` blank, `branch.base=origin/main`). Stated per skill.
>
> **Re-audit (iteration 3). The plan artifact has been REPLACED since iteration 2.** The prior
> verdict (iter 2, PASS) audited a **Path-A** plan (~495 lines, 5 commits, `models.py` +
> `review_processor.py` plumbing, §7 "D1 / Operator-confirmed: 2026-06-19", explicit §10 UNTOUCHED,
> §22 revision log). The file on disk now is a **Path-B** plan (282 lines, 3 commits, `scheduler.py`
> only). It **regressed** two required §-elements the Path-A plan had closed. The prior verdict is
> stale; this audit grades the current artifact. See COORDINATION FLAGS.

=== PHASE 0: R-TIER ===
- **Declared:** R1 (`c2-f169-plan.md:5`)
- **Inferred:** R1 (basis: 3 atomic commits [2 functional + 1 packet]; **1 prod file MOD** —
  `scheduler.py` — + 1 test file; **0 migrations**, **0 model changes** [Path B confines change to
  scheduler.py, `:86-92`]; no new dispatcher/substrate)
- **Reconciled:** R1 (declared == inferred, no mismatch)
- **Audit depth (R1):** Phase 1 full · Phase 2 = 2.1, 2.2, 2.3, 2.5, 2.8 · Phase 3 = 3.1, 3.5

=== PHASE 1: STRUCTURAL DRIFT ===
**REFERENCE:** NONE — `plans.archetypes.R1` blank (no config).
`1b: no R1 archetype configured (plans.archetypes.R1 blank) — running section-presence + series-gap
checks against the canonical list only, no reference diff.`

**SECTION-PRESENCE (required at R1):**
- §1 Context — present (`:10-25`, finding + bug line + brief refs)
- §2 Verified state (N Explore lookups, 2026-06-19) — present (`:29-44`, V1–V9 with path:line)
- §5 Memory + lesson references — present (`:47-59`)
- §6 Strict scope boundaries (IN / OUT-with-disposition) — present (`:63-80`, In-scope +
  Explicitly-out-of-scope each deferred to a named follow-up)
- §7 Locked design decisions (D-numbered, operator-confirmed + date) — **PRESENT BUT DEFICIENT**
  (`:84-114`): decision recorded ("Decision: Path B") with rationale and locked code, but it is
  **NOT D-numbered** (no D1) and carries **NO operator-confirmed date**. Canonical §7 requires
  "D-numbered, operator-confirmed + date" at R1+. The A/B path fork specifically requires operator
  sign-off per the completion contract PRE-MERGE (`…contract.md:86-92`). **Regression vs iter-2
  Path-A plan, which had "D1 / Operator-confirmed: 2026-06-19".**
- §9 Sequenced atomic-commit plan — present (`:118-156`, Commit 1→3 flat, primary-file rule honored)
- §10 Critical files (NEW / MOD / **UNTOUCHED**) — **PRESENT BUT DEFICIENT** (`:160-169`): table of
  NEW/MOD + read-only-reference files, but **no explicit "UNTOUCHED (explicitly out of scope)"
  sub-section**. The untouched set (`models.py`, `review_processor.py`, `db/schema.py`) is declared
  in §6 (`:72-79`) and tagged "Read-only reference" in the §10 table, so the scope-drift primitive
  exists — just not in canonical §10 form. **Regression vs iter-2 Path-A plan.**
- §11 Reused utilities (must consume, not reimplement) — present, literal phrase (`:173-179`)
- §14 Acceptance criteria — present, binary (`:183-198`), AC-1…AC-10; outcome ACs (AC-1/AC-2) +
  mechanical verifications distinguished
- §15 Risks + mitigations + stop conditions (RED) — present (`:202-210`), 5 risks each with a RED
  escalation/stop action
- §19 Locked PR sequence position — present (`:214-226`)
- §20 After-merge handoff — present (`:229-251`)

Sections not required at R1 (R2+/R3) — correctly omitted (na_ok): §0 metadata, §3 pre-authoring
verifications, §4 prior-PR packet pre-reads, §8 open-questions, §12 test-strategy layers, §13
verification matrix, §16 code-review resilience, §17 rituals, §18 iter/wall-clock budget, §21 session
checkpoints, §22 plan revisions. (Header block `:3-6` carries Branch/Base/Risk/Created — a partial
§0; not required at R1.) Note: the launch brief declares a 2-cycle iter budget (`…brief.md:128-134`)
that the plan does not restate — §18 is R2+ so na_ok, but worth carrying forward.

**NUMBERED-SERIES GAPS:**
- D-decisions: **no D-series exists** — the §7 decision is unnumbered (see §7 deficiency above)
- B-commits: clean (Commit 1→2→3, no gaps/dupes)
- R-risks: clean (5 rows, no gaps); Q-questions: n/a (R1, none)

**STREAM STRUCTURE:** n/a (R1, not R3)

**SUBSTANTIVE LOSSES / ADDITIONS:** not assessed — no reference archetype available (`plans.archetypes.R1`
blank). Per skill, vs-reference diff disabled this run. (Cross-artifact regression vs the iter-2
Path-A plan is reported under COORDINATION FLAGS, not as a §-diff.)

=== PHASE 2: PLAN-QUALITY ===

**2.1 DESIGN-TESTS COVERAGE** — `find . -name '*.bug-catalog.md'` → none.

| File | Bug-catalog? | Plan to add? |
|---|---|---|
| `flashcore/scheduler.py` (MOD) | not present | none planned — relies on 2 new Layer-A unit tests |
| `tests/test_scheduler.py` (the tests) | n/a | n/a |

**FLAG:** No bug-catalog companion for the sole MOD file; coverage is "we'll write tests" (two new
unit assertions). Bug-catalog-first standard not met. Mitigant: the two correctness gates are sharp
and outcome-shaped (AC-1 `elapsed_days>0`; AC-2 on-time stability ≠ same-day stability). Quality
flag, not a stop.

**2.2a VERIFICATION MATRIX:** n/a (R2+ when criteria>3).
**2.2b ACCEPTANCE vs VERIFICATION:** distinct — AC-1/AC-2 are outcome-shaped (`elapsed_days>0`;
stability distinct); AC-3/AC-5/AC-6/AC-7/AC-8 are mechanical (tests pass / grep empty / mypy clean /
`aiv check`). Not collapsed. OK.
**2.2c TEST LAYERS:** n/a at R1 by its own gating (2.2c is R2+). Noted for completeness: Layer A
(unit) is the only layer and is sufficient here — **Path B touches no DB-write path** (no
`review_processor`/DB change), so Layer B is correctly not required and the in-memory-surrogate
risk does not arise. Layer C/F n/a (no UI/subprocess). Layer D: functional LOC added but
`quality.coverage_floor` blank → no coverage floor configured (`quality.coverage_floor` blank) — flag
only that no ratchet layer is declared, not a numeric target; acceptable at R1. Layer E:
full-suite + `aiv check` pre-push present (AC-7/AC-8).

**2.3 PACKET PRE-READ:** R2+ section; at R1 **code-view sufficient** for the single MOD file
(`scheduler.py`) — fresh harness, no prior AIV packet on this surface; §2 grounds via direct reads +
launch brief. No gap at R1.

**2.5 CODE-HEALTH BASELINE:**
- `2.5: no per-file code-health tool configured (quality.code_health_cmd blank) — skipped.`
- `2.5: no change-set code-health tool configured (quality.code_health_changeset_cmd blank) — skipped.`

**2.8 MEMORY COVERAGE** — §5 cites CLAUDE.md lessons (E010 trap, `aiv commit` FILE-arg, `aiv abandon`
confirm, SHA-pinned intent, `--skip-checks` R0-only, never-edit-test-to-pass). Universal-principle
cross-check:

| Principle | Applies? | Honored? |
|---|---|---|
| Never merge autonomously; human is merge gate | yes | **yes** — §19 "Autonomous merge: NEVER" (`:221`); contract PRE-MERGE AskUserQuestion |
| Author packets to shape; validate via `aiv` CLI not by eye | yes | **yes** — AC-8 `aiv check` exits 0 (`:196`) |
| Merge by rebase, not squash | yes | **uncited** — not addressed in plan (minor flag) |
| Run local-CI replica before every push | yes | **yes** — AC-7 full suite 480/1-skip pre-push (`:195`) |
| Wall-clock drill for subprocess/daemon | no | n/a |
| Exercise DB-write paths against the real DB, not a surrogate | **no (Path B)** | n/a — Path B touches no DB path |
| Behavior-pinning + green existing tests for refactor | partial (fix, not refactor) | **yes** — 15 existing scheduler tests pinned (AC-3, `:191`) |

Flag: rebase-not-squash uncited. Path B cleanly sidesteps the DB-surrogate principle that dogged the
iter-2 Path-A plan.

=== PHASE 3: PLAN-GRAPH + TEMPORAL (R1 → 3.1, 3.5 only) ===

**3.1 BASE-SHA DRIFT:** Plan declares base `origin/main` @ `b5e1c4b` (`:6`). Probe:
`git rev-list --count b5e1c4b..origin/main` = **0**; `origin/main` HEAD still `b5e1c4b`. **Risk: LOW** —
zero drift; pre-authoring verifications (§2) remain valid.

**3.5 STOP CONDITIONS (RED):** present per risk (`:202-210`) — thresholds/escalations named and
falsifiable: AC-2 fails after 2 iter cycles → escalate via AskUserQuestion (possible switch to Path
A); None-stability TypeError → stop + re-read guard; existing early-card test fails → escalate, do
NOT edit test; E010 → rephrase + re-run; `aiv commit` file-unchanged → diagnose staging. **Pass.**

(3.2 conflicts-with, 3.3 open-questions, 3.4 streams, 3.6–3.9 — not gated at R1. Noted: only one
plan in `.aiv/plans/`, `~/.claude/plans` empty → no conflicts-with collisions; no open-questions
queue; §10 UNTOUCHED primitive present in §6 but not in canonical §10 location — see Phase 1.)

=== ADVERSARIAL GROUNDING (claims re-executed this run) ===
- `flashcore/scheduler.py:211-212` bug confirmed: `# Set last_review to due date…` +
  `fsrs_card.last_review = fsrs_card.due`; elapsed_days at `:218-221` derives from
  `last_review.date()` → 0 for an on-time review. ✓ (read source `:200-224`)
- Outer guard `if card.state != CardState.New:` exists at `scheduler.py:200`; inner
  `if card.next_due_date:` at `:205` — confirms the §7 replacement sits inside both guards (the §7
  inner `card.state != CardState.New` re-check is redundant but harmless). ✓
- `CardState` and `datetime` both already imported (`scheduler.py:10`, `:32`) — confirms §11 "no new
  imports". ✓
- `Card` has `last_review_id` (`models.py:57`) + `next_due_date` (`:61`); **no `last_review_date`** —
  confirms V3 and that Path B requires no model change. ✓
- `tests/test_scheduler.py` has **15** `def test_` — confirms V6 baseline. ✓
- `~/.claude/plans` empty/absent; no `*.bug-catalog.md` anywhere. ✓

=== COORDINATION FLAGS (non-section) ===
1. **Branch-name mismatch.** Plan declares branch `feat/c2-pr-f169-fsrs-elapsed-days-b1` (`:3`) but
   the actual working branch is `feat/c2-fsrs-harness` (FINDING header). Completion-contract VERIFY
   [9] (`…contract.md:58-61`) requires the `…-b1` branch name **exactly**. Reconcile before
   execution / VERIFY [9] — a contract-shape failure as written, not a plan-structure defect.
2. **Artifact regression vs the previously-audited plan.** The iter-2 verdict graded a Path-A plan
   that had closed §7 (D1 + operator-confirm date) and §10 (explicit UNTOUCHED). The on-disk plan is
   now Path B and **dropped both**, plus the §22 revision log. The Path-B choice itself is defensible
   (single-file, no plumbing) and the rationale is sound (`:88-92`), but the two structural elements
   regressed and the path-fork now carries **no recorded operator confirmation** — material because
   the contract demands operator sign-off on A vs B at merge.

=== OVERALL VERDICT ===
- **Plan structural integrity: FAIL** — two required-at-R1 §-elements are deficient: (a) §7 locked
  decision is **not D-numbered and lacks an operator-confirmed date** (canonical §7 R1+ requires
  both; the A/B fork specifically needs operator sign-off); (b) §10 lacks an explicit **UNTOUCHED
  (explicitly out of scope)** sub-section (primitive present in §6, but not in canonical §10 form).
  Both are quick fixes — add `**D1.** … Operator-confirmed: <date>` to §7 and an `UNTOUCHED` block to
  §10 — but as written the plan does not meet the canonical R1 section shape.
- **Plan quality audit: partial** — no bug-catalog companion (test-first, not catalog-first);
  rebase-not-squash uncited. Both non-fatal; correctness gates (AC-1/AC-2) are sharp and Path B
  avoids the DB-surrogate hazard entirely.
- **Plan-graph readiness: pass** — base-SHA drift 0 (low risk); RED stop-conditions present per
  risk; no conflicting in-flight plans.
- **HARD STOPS: none** — no `blocks-B0` open question exists; the branch-name mismatch and missing
  §7 operator-confirmation are pre-VERIFY/pre-merge reconciliations, not B0 blockers.
- **Recommended next action:** revise §7 (D-number + operator-confirmed date for the Path-B
  decision) and §10 (add the explicit UNTOUCHED sub-section), then re-run check-drift. Separately,
  reconcile the declared branch name with the working branch before VERIFY [9]. Optional quality
  lift: add a bug-catalog companion for `scheduler.py`; cite rebase-not-squash in §20.

=== SURVIVORSHIP-BIAS DISCLOSURE ===
This template is induced from the project's own plan corpus (`plans.dir`), weighted toward plans that
shipped. The corpus is a survivorship sample: it tells you what merged plans happened to contain, NOT
what plans need to succeed. Here the corpus is effectively empty (`~/.claude/plans` empty; no
archetypes configured), so Phase 1 ran section-presence + series-gap against the canonical list only —
there is no reference diff and no calibration to a surviving sample. Sections marked OPTIONAL are
observed-rare-but-load-bearing; sections not in the template may still be load-bearing for failure
modes not yet encountered. A clean structural pass would mean "matches the canonical list", not
"cannot fail". Promotion criterion for any new template section: name the specific failure mode it
would have prevented.

## Machine-checkable data

```json
{
  "schema": "check_drift_verdict@1",
  "r_tier": "R1",
  "audit_depth_complete": true,
  "structural_integrity": "fail",
  "plan_quality": "partial",
  "plan_graph": "pass",
  "hard_stops": [],
  "open_substantive_losses": 0,
  "iteration": 3
}
```
