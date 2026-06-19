# check-drift audit — Plan: Fix F169 (FSRS on-time elapsed_days)

Plan audited: `.aiv/plans/c2-f169-plan.md`
Config: **no `.aiv-workflow.yml`** at repo root (`git rev-parse --show-toplevel` = `/home/user/fc-c2-harness`;
`$AIV_WORKFLOW_CONFIG` empty) — all values are skill defaults. `plans.archetypes.*`,
`quality.code_health_cmd`, `quality.code_health_changeset_cmd`, `quality.coverage_floor`,
`memory.dir`/`memory.index`, `ci.local_replica_cmd` all blank/absent.
Iteration: this is **Loop #1, iteration 2** (plan revision log §"Loop #1, iteration 2" added Commit 5;
a prior `check-drift.md` verdict from iteration 1 was present and overwritten).

=== PHASE 0: R-TIER ===
Declared: **R1** (plan line 8).
Inferred: **R1** (basis: 5 atomic commits; 3 source files MOD [`models.py`, `scheduler.py`,
`review_processor.py`] + 2 test files; 0 migrations; 0 new data-access methods — Commit 3 *consumes* the
pre-existing `db.get_latest_review_for_card`, verified at `flashcore/db/database.py:834`; the new field is
transient `exclude=True`, no persistence).
Reconciled: **R1** (no mismatch). Caveat: the change spans 3 subsystems (model + hub + scheduler),
brushing the R2 boundary, but with no migration / no new DB method / no new dispatcher it stays R1.
Audit depth (R1): Phase 1 full; Phase 2 = 2.1, 2.2, 2.3, 2.5, 2.8; Phase 3 = 3.1, 3.5.

=== PHASE 1: STRUCTURAL DRIFT ===
REFERENCE: **NONE** — `1b: no R1 archetype configured (plans.archetypes.R1 blank, no config file) —
running section-presence + series-gap checks against the canonical list only, no reference diff.`

SECTION-PRESENCE (required-at-R1 checked):
- §1 Context: **PRESENT** — opens with finding statement + `scheduler.py:212` cite (verified: bug is at
  `flashcore/scheduler.py:211-212`, `fsrs_card.last_review = fsrs_card.due`).
- §2 Verified state (N Explore agents, YYYY-MM-DD): **MISSING** — no verified-state block with agent
  count + date. (I independently verified the plan's factual claims; see Phase 2/3 — they hold.)
- §5 Memory + lesson references: **MISSING** — no memory section (no memory store loaded; universal-
  principles substitute checked at 2.8).
- §6 Strict scope boundaries (IN/OUT): **PRESENT** — "Files touched" (IN) + "Scope guard — out of this
  PR" table (OUT) with follow-up dispositions. No "does NOT do" philosophical line (minor).
- §7 Locked design decisions (D-numbered, operator-confirmed + date): **PARTIAL** — "Path decision:
  Option A" with a one-sentence rationale is present (satisfies the brief's path-fork requirement to pick
  one), but it is **not D-numbered** and carries **no operator-confirmed date**. The launch brief
  explicitly gates this: "Path choice ... wants operator sign-off **before widening scope to
  `review_processor.py`**" — Commit 3 widens to `review_processor.py` with no recorded confirmation.
- §9 Sequenced atomic-commit plan (B0…Bn): **PRESENT** — Commit 1–5, ordered, one file each. Named
  "Commit N" not "Bn" (cosmetic).
- §10 Critical files (NEW/MOD/**UNTOUCHED**): **PARTIAL** — MOD table present; **no UNTOUCHED
  sub-section** (also flagged at 3.9 — scope-drift primitive absent).
- §11 Reused utilities (must consume, not reimplement) [literal phrase]: **MISSING as a section** — plan
  notes `get_latest_review_for_card` "already exists" inline (verified: `database.py:834`,
  returns `Optional[Review]`) but no dedicated "Reused utilities" section.
- §14 Acceptance criteria (outcome-shaped): **PRESENT** — two named acceptance tests + "Test layers"
  table (elapsed_days>0; stability distinct).
- §15 Risks + mitigations + stop conditions (RED): **MISSING** — no risk register, no RED thresholds
  (also flagged at 3.5).
- §19 Locked PR sequence position (predecessor/successor/parallel-safe): **MISSING** — scope guard names
  successor follow-ups (backfill PR, stage-c2 DB migration PR) but no locked-position section.
- §20 After-merge handoff: **PARTIAL** — handoff content (progress-tracker, post-merge bookkeeping)
  lives in the *completion-contract* artifact, not the plan; the plan itself has only the AIV commit
  sequence + scope guard.

NUMBERED-SERIES GAPS (R≥1):
- B-commits: **clean** — Commit 1–5 contiguous, no gap/duplicate.
- D-decisions: **none numbered** (Path decision not D-numbered — presence issue, see §7, not a gap).
- R-risks / Q-questions: **none present** (no risk register / no open-questions section).

STREAM STRUCTURE (R3): n/a (R1).
SUBSTANTIVE LOSSES / ADDITIONS: n/a — no reference available (no archetype configured).

=== PHASE 2: PLAN-QUALITY ===

2.1 DESIGN-TESTS COVERAGE:

| File (MOD/NEW) | Bug-catalog? | Plan to add? |
|---|---|---|
| `flashcore/models.py` | none (repo keeps no `.bug-catalog.md`) | not planned |
| `flashcore/scheduler.py` | none | not planned |
| `flashcore/review_processor.py` | none | not planned |

Flag (soft): not bug-catalog-first. **Mitigation:** the repo corpus keeps no `.bug-catalog.md` files at
all (`ls **/*.bug-catalog.md` → none), so the standard is not project convention; the two named Layer-A
acceptance tests + one Layer-B integration test are specified concretely (not "we'll write tests"), which
substitutes adequately at R1.

2.2a VERIFICATION MATRIX: n/a (R2+ when criteria >3; R1).
2.2b ACCEPTANCE vs VERIFICATION: **distinct** — acceptance (elapsed_days>0; on-time stab ≠ same-day stab)
is separated from mechanical verification (mypy, `aiv check`, regression count) in the Test-layers table.
2.2c TEST LAYERS: Layer-A (unit) + Layer-B (integration) declared. **Positive — verified executable:**
the Layer-B test (`test_on_time_review_elapsed_days_persisted`) genuinely exercises the Commit 3→2 chain.
I traced it: `add_review_and_update_card` → `_update_card_after_review` (`database.py:693`) writes
`last_review_id = $1`, and `get_card_by_uuid` reloads it, so `card_after_first.last_review_id` is set →
Commit 3's `if card.last_review_id is not None` guard fires on the second review → `last_review_date` =
prior review's `2024-06-01` → elapsed_days = 10. The integration gate is not a no-op. Layer-B uses
`in_memory_db` (real SQLite `:memory:`, the real dialect — not a mock surrogate), satisfying the
real-DB-write principle. No Layer C/F needed (no UI/route, no subprocess/daemon).

2.3 PACKET PRE-READ: **none declared.** No AIV packet pre-reads cited for the three MOD files. Acceptable
at R1 — these surfaces are being modified fresh and the plan reads them by code-view (line cites
throughout); note only.

2.5 CODE-HEALTH BASELINE:
- `2.5: no per-file code-health tool configured (quality.code_health_cmd blank) — skipped.`
- `2.5: no change-set code-health tool configured (quality.code_health_changeset_cmd blank) — skipped.`

2.6 FAN-OUT TRIGGER: n/a at R1 audit depth (2.6 not in R1 table). For the record the trigger would be
borderline-NO (3 critical files but single well-scoped finding, claims already verified inline here).

2.7 CODE-REVIEW RESILIENCE: n/a (R2+; no prior automated-review contact on this branch).

2.8 MEMORY COVERAGE (universal principles — no memory store loaded):

| Principle | Applies? | Honored? |
|---|---|---|
| Never merge autonomously; human is merge gate | yes | **yes** — contract PRE-MERGE AskUserQuestion; brief `merge.autonomous=false` |
| Author packets to shape; validate via `aiv` CLI | yes | **yes** — plan runs `aiv close` + `aiv check` before push |
| Merge by rebase, not squash (atomic commits) | yes | **yes** — atomic 5-commit sequence; brief `merge.strategy=rebase` |
| Run local-CI replica before push | yes | **partial** — `ci.local_replica_cmd` unconfigured; plan runs full `pytest tests/` (`aiv check` pre-push) as the replica |
| Wall-clock drill for subprocess/daemon | no | n/a |
| Exercise DB-write paths against real DB | yes | **yes** — Layer-B drives real in-memory SQLite |
| Behavior-pinning + green existing tests (refactor) | partial | **yes** — fix keeps all 15 existing scheduler tests green (else-fallback in Commit 2 specifically preserves `test_review_lapsed_card`) |

No uncited applicable project memories (none exist). PASS.

=== PHASE 3: PLAN-GRAPH + TEMPORAL (R≥2 depth; R1 runs 3.1, 3.5) ===

3.1 BASE-SHA DRIFT: **0 commits — low risk.** Finding states authored off `origin/main @ b5e1c4b`;
`git log -1 origin/main` = `b5e1c4b`; `git rev-list --count b5e1c4b..origin/main` = `0`. No drift; the
pre-authoring verifications need no re-run. (Note: plan has no §0 base-SHA pin — not required at R1, but
the pin would make this check self-contained rather than relying on the finding header.)

3.5 STOP CONDITIONS (RED): **MISSING.** No §15 risk register → no RED thresholds (LOC drift %, iter#
cap, CI-fail pattern, wall-clock cap) and no escalation actions in the plan. The launch brief carries an
iter budget (2 cycles + an escalation-via-AskUserQuestion trigger), but the plan does not import it.
Flag: add RED stop conditions before execution.

3.2 / 3.3 / 3.4 / 3.6 / 3.7 / 3.8 / 3.9: not in R1 audit depth — but two are cheap and informative:
- 3.2 CONFLICTS-WITH (informational): only `.aiv/plans/c2-f169-plan.md` exists; no in-flight plan touches
  the same files → no collision.
- 3.9 UNTOUCHED FILES (informational): **MISSING** (mirrors §10 PARTIAL) — no `UNTOUCHED` sub-section;
  scope-drift primitive absent.

=== OVERALL VERDICT ===
Plan structural integrity: **fail** — multiple required-at-R1 sections missing/partial: §2 verified-state
(MISSING), §5 memory refs (MISSING), §11 reused-utilities section (MISSING), §15 risks + RED stop
conditions (MISSING), §19 PR sequence position (MISSING); §7 path-decision not D-numbered / no operator
sign-off despite the brief's explicit gate; §10 no UNTOUCHED sub-section; §20 handoff only in the
contract, not the plan.
Plan quality audit: **partial** — testability is strong (Layer-A + verified-executable Layer-B, real-DB
writes, distinct acceptance vs verification, all universal principles honored); soft gaps are no
bug-catalog/design-tests-first (mitigated — repo keeps none) and no packet pre-read (acceptable at R1).
Plan-graph readiness: **partial** — 3.1 base-SHA drift = 0 (clean); 3.5 RED stop conditions MISSING.
HARD STOPS: **none** — no `blocks-B0` open-question structure is present and Phase 3.3 is not run at R1;
the §7 operator-sign-off gap is recorded as a structural flag + top revision, not a machine hard-stop.
Recommended next action: **do not exit plan mode yet — revise, then re-run check-drift.** Priority order:
(1) §7 — D-number the Option-A decision and record the brief-required operator sign-off for widening to
`review_processor.py`; (2) add §15 risks + RED stop conditions (import the brief's 2-cycle iter budget +
escalation trigger); (3) add §10 `UNTOUCHED (explicitly out of scope)` sub-section; (4) add §2
verified-state block (the claims are already verified above — record them) and a §11 reused-utilities
line for `get_latest_review_for_card`. Implementation design itself is sound and the acceptance gates are
real; the failures are plan-structure, not plan-logic.

=== SURVIVORSHIP-BIAS DISCLOSURE ===
This template is induced from the project's own plan corpus (plans.dir), weighted toward plans that
shipped. The corpus is a survivorship sample: it tells you what plans that merged happened to contain,
NOT what plans need to succeed. Sections marked OPTIONAL are observed-rare-but-load-bearing. Sections NOT
in the template may still be load-bearing for failure modes not yet encountered. A clean structural pass
means "matches the surviving corpus", not "cannot fail". Here there is no configured archetype, so only
section-presence + series-gap ran — the substantive vs-reference diff was disabled. Promotion criterion
for adding any new section: name the specific failure mode it would have prevented.

## Machine-checkable data

```json
{
  "schema": "check_drift_verdict@1",
  "r_tier": "R1",
  "audit_depth_complete": true,
  "structural_integrity": "fail",
  "plan_quality": "partial",
  "plan_graph": "partial",
  "hard_stops": [],
  "open_substantive_losses": 0,
  "iteration": 2
}
```
