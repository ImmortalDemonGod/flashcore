# check-drift verdict — PR-F169 plan (`.aiv/plans/c2-f169-plan.md`)

Iteration 2. Loop #1 failed GATE #1 on ground-truth (GT-1); this run re-audits the revised plan.

> **Config.** No `.aiv-workflow.yml` at repo root (`git rev-parse --show-toplevel` = `/home/user/fc-c2-harness`). All keys use inline skill defaults. `plans.archetypes.R1` blank → structural-drift-vs-reference disabled (1b); section-presence + series checks run against the canonical list only. `quality.code_health_cmd`/`code_health_changeset_cmd` blank → 2.5 skipped. `memory.dir`/`index` absent → universal-principle check only.

=== PHASE 0: R-TIER ===
Declared: **R1** (§1 "Risk tier: R1"; §19; launch brief "Risk tier + scope estimate: R1")
Inferred: **R1** (basis: 3 production files + 2 test files + packet ≈ 6 logical commits; one new transient model field; one hub DB-read added; **no migration, no new data-access method (consumes existing `get_latest_review_for_card` as-is), no new dispatcher**)
Reconciled: **R1** (declared == inferred; no mismatch)
Audit depth: Phase 1 full · Phase 2 {2.1, 2.2, 2.3, 2.5, 2.8} · Phase 3 {3.1, 3.5}

=== PHASE 1: STRUCTURAL DRIFT ===
REFERENCE: NONE — no R1 archetype configured (`plans.archetypes.R1` blank).
1b: no R1 archetype configured — running section-presence + series-gap checks against the canonical list only, no reference diff.

SECTION-PRESENCE (plan uses canonical §-numbering and omits R2+/R3 sections, which is correct at R1):
- Required-at-R1 present: §1 Context · §2 Verified state · §5 Memory+lessons · §6 Scope (IN/OUT) · §7 Locked design (D1, operator-confirmed 2026-06-19) · §9 Sequenced commit plan · §10 Critical files (incl. **UNTOUCHED** sub-section) · §11 Reused utilities (literal phrase present) · §14 Acceptance criteria · §15 Risks + stop conditions (RED) · §19 Locked PR sequence · §20 After-merge handoff · Revision log. **All R1-required sections present.**
- Missing required at R1: **none**.
- Omitted (not required at R1 — OK): §0 metadata, §3 pre-authoring verifs, §4 packet pre-reads, §8 open questions, §12 test strategy, §13 verification matrix, §16 review-resilience, §17 rituals, §18 iter budget, §21 checkpoints, §22 revisions (R2+/R3 gates).
- Extra non-canonical: none.
- Out-of-order: none.

NUMBERED-SERIES GAPS:
- D-decisions: clean — D1 with sub-decisions D1.1–D1.5, no gap/dup.
- B-commits: Commit 1, 2, 3, 4, **4b**, 5 — `4b` is an inserted Layer-B test commit, sequential and explained in the revision log; no true gap.
- R-risks / Q-questions: §15 risks are an unnumbered table (no series to gap-check); no §8 Q-series at R1.

STREAM STRUCTURE (R3): n/a (R1).

SUBSTANTIVE LOSSES / ADDITIONS: n/a — no reference available (no archetype). Section-presence only.

**Phase 1 structural integrity: PASS.**

=== PHASE 2: PLAN-QUALITY ===

**2.1 DESIGN-TESTS COVERAGE**

| File | Bug-catalog? | Plan to add? |
|---|---|---|
| `flashcore/scheduler.py` (MOD, bug site) | not present | MISSING — no `.bug-catalog.md`; tests are concretely specified instead |
| `flashcore/models.py` (MOD) | not present | MISSING |
| `flashcore/review_processor.py` (MOD) | not present | MISSING |

The plan specifies **concrete test function bodies** (AC-1/AC-2 units + AC-12 Layer-B), not "we'll write tests" — stronger than a hand-wave. But the bug-catalog-first standard is not met: no `.bug-catalog.md` companion for the bug site. **Non-blocking at R1; flagged as a quality gap.**

**2.2a VERIFICATION MATRIX:** n/a (R2+ only).
**2.2b ACCEPTANCE vs VERIFICATION:** mostly distinct — AC-1 (`elapsed_days>0`), AC-2 (stability distinct), AC-12 (persisted `elapsed_days_at_review>0`) are outcome-shaped; AC-3/4/13/14 are mechanical greps; AC-6/9 are "tests pass". Both classes live in one §14 table but are individually separable. Acceptable.
**2.2c TEST LAYERS:** Layer A (unit, AC-1/AC-2) present; Layer B (integration) present (Commit 4b, real in-memory DuckDB + real `FSRS_Scheduler`). The PR touches a DB-write path (`review_processor` persists via `add_review_and_update_card`); the Layer-B test exercises it against the **real DuckDB engine** (`:memory:` is real DuckDB, not a foreign surrogate) — satisfies the DB-write principle. Layers C/D/E/F n/a or not required at R1.

**2.3 PACKET PRE-READ:** §10 "Read before touching" lists the five source spans; no prior AIV packet exists for these surfaces to pre-read (none cited, none required at R1). Code-view sufficient for all three MOD files. OK.

**2.5 CODE-HEALTH BASELINE:** 2.5: no per-file code-health tool configured (`quality.code_health_cmd` blank) — skipped. 2.5: no change-set code-health tool configured (`quality.code_health_changeset_cmd` blank) — skipped.

**2.6 FAN-OUT TRIGGER:** n/a at R1 depth (not gated). For the record: would lean NO — single subsystem (FSRS scheduler + its hub), all spec claims already verified against live source this run.

**2.8 MEMORY COVERAGE** (no memory store loaded; universal-principle check):

| Principle | Applies? | Honored? |
|---|---|---|
| Never merge autonomously; human is merge gate | yes | **yes** — §19 "Merge authority: human operator only"; §5 cites it |
| Author packets to shape; validate via `aiv` CLI not by eye | yes | **yes** — §9 uses `aiv commit`/`close`/`check`; AC-8 gates on `aiv check` exit 0 |
| Merge by rebase, not squash | yes | **partial** — launch brief sets `merge.strategy: rebase`; plan relies on atomic commits but does not explicitly restate rebase-not-squash. Minor. |
| Run local-CI replica before every push | yes | **yes** — §9 runs full `pytest tests/` before push-equivalent (AC-9) |
| Wall-clock drill for subprocess/daemon | n/a | no subprocess/daemon touched |
| Exercise DB-write paths against real DB, not surrogate | yes | **yes** — Layer-B test (Commit 4b) drives real in-memory DuckDB |
| Behavior-pinning + green existing tests for refactor | yes | **yes** — 15 existing scheduler tests held green (AC-6); RED stop if any needs editing |

No project memory store configured; no uncited-but-applicable project memory to flag.

=== PHASE 3: PLAN-GRAPH + TEMPORAL (R1 depth: 3.1, 3.5) ===

**3.1 BASE-SHA DRIFT:** plan declares base `origin/main @ b5e1c4b`. Probe: `git rev-list --count b5e1c4b..origin/main` = **0**. origin/main HEAD *is* b5e1c4b. Drift = 0 commits → **LOW risk**; pre-authoring verifications need no re-run.
**3.2 CONFLICTS-WITH:** n/a at R1 depth (not gated). Only `c2-f169-plan.md` exists under `.aiv/plans/`.
**3.3 OPEN QUESTIONS:** n/a (no §8 at R1; none declared).
**3.4 STREAMS:** n/a (R1).
**3.5 STOP CONDITIONS (RED):** §15 "RED STOP CONDITIONS" present with **named thresholds + escalation actions**: (a) any existing scheduler test needs editing → stop + determine wrong side; (b) mypy new error unresolvable without public-interface change → escalate; (c) `aiv check` non-zero after **2** attempts → stop; (d) any doubt on persistence scope → escalate (widens to R2); (e) `get_latest_review_for_card` stale/needs `database.py` change → stop. PRESENT.
**3.6–3.9:** n/a at R1 depth.

=== SPECIAL GATE: GROUND-TRUTH-OVER-APPROXIMATION ===
**Evaluation:** Does the plan approximate/derive any value already recorded or retrievable?

**NO — gate SATISFIED.** The prior-review timestamp ground-truth (`reviews.ts`) is recorded in the DB and retrievable via `flashcore/db/database.py:834 get_latest_review_for_card` (verified: returns `Optional[Review]`, delegates to `get_reviews_for_card`). The plan:
- **Locks Path A** (§7 D1, operator-confirmed 2026-06-19): hub reads `prior_review.ts.date()` before every `compute_next_state` call (D1.2) — consumes recorded data.
- **Explicitly disfavors Path B** (§7) precisely because it would approximate `last_review` from `stability` while ignoring the recorded `reviews.ts` — "A narrower scope is not a valid reason to prefer an approach that ignores recorded data."
- **D1.3** removes the stability-approximation branch from the scheduler entirely; the only `elapsed_days=0` case is a genuine first-ever review (no prior review exists — correct, not an approximation).
- **D1.4** caches `ts.date()` (the exact just-performed review timestamp) for same-session re-reviews — exact value, avoids a redundant lookup, not an estimate.

This is the root-cause path (no `last_review_date` on the model → add it + plumb from the hub), not a symptom mask. The Loop #1 GT-1 failure is corrected (revision log documents the removal of the stability fallback). **No hard stop on ground-truth grounds.**

Minor factual note (non-blocking): the plan and completion contract refer to the store as "SQLite"; the actual engine is **DuckDB** (`flashcore/db/database.py:6 import duckdb`). The `:memory:` integration fixture works identically, so this is a misnomer, not a correctness or ground-truth defect.

=== OVERALL VERDICT ===
Plan structural integrity: **pass** — all R1-required canonical sections present; D-series and commit-series clean; UNTOUCHED sub-section present.
Plan quality audit: **partial** — concrete tests + real-DB Layer-B integration test present and DB-write principle honored; non-blocking gaps: no bug-catalog companion (2.1) and rebase-not-squash not explicitly restated (2.8). Neither is a fail.
Plan-graph readiness: **pass** — base-SHA drift 0 (low risk); RED stop conditions present with thresholds + escalation.
Ground-truth gate: **pass** — Path A consumes recorded `reviews.ts`; approximation path (B) explicitly rejected.
HARD STOPS: **none**.
Recommended next action: **exit plan mode / proceed to implementation.** Optional pre-B0 polish (non-blocking): add a scheduler bug-catalog entry for F169 (2.1); correct "SQLite" → "DuckDB" in §7 D1.1 / §15 / Layer-B docstring.

=== SURVIVORSHIP-BIAS DISCLOSURE ===
This template is induced from the project's own plan corpus (`plans.dir`), weighted toward plans that shipped — a survivorship sample. It tells you what merged plans happened to contain, not what plans need to succeed. With no archetype configured, only section-presence + series checks ran (no substantive reference diff). A clean structural pass means "matches the canonical list", not "cannot fail." Sections marked OPTIONAL are observed-rare-but-load-bearing; sections absent from the template may still be load-bearing for failure modes not yet encountered.

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
  "iteration": 2
}
```
