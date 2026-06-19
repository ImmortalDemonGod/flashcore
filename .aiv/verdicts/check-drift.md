# check-drift verdict — c2-f169-plan.md (Finding F169, CRITICAL)

Audited: `.aiv/plans/c2-f169-plan.md` @ branch `feat/c2-fsrs-harness` (HEAD `3e342c0`, base `origin/main @ b5e1c4b`).
Config: **no `.aiv-workflow.yml` at repo root** (`$AIV_WORKFLOW_CONFIG` empty) — skill defaults used; said so per skill contract.

```
=== PHASE 0: R-TIER ===
Declared:   R1 (§1: "standard logic fix; no external API surface; no DB schema change")
Inferred:   R1 (basis: ~6 commits [1,2,3,4,4b,5]; 3 prod files + 2 test files + packet;
            1 NEW model field; 0 migrations; 0 new data-access methods
            [get_latest_review_for_card is CONSUMED, already exists @ db/database.py:834];
            0 new dispatcher. Adds a new data-flow pathway [field on model + hub plumbing]
            which nudges toward R2, but no migration/new-substrate trigger fires.)
Reconciled: R1 (declared==inferred; no mismatch to escalate)
Audit depth: Phase 1 full · Phase 2 {2.1,2.2,2.3,2.5,2.8} · Phase 3 {3.1,3.5}
```

```
=== PHASE 1: STRUCTURAL DRIFT ===
REFERENCE: NONE — no R1 archetype configured (plans.archetypes.R1 blank, no config file).
1b: running section-presence + numbered-series checks against the canonical list only,
    no reference diff.

SECTION-PRESENCE (required at R1):
  §1  Context .......................... present
  §2  Verified state (N agents, date) ... present ("0 Explore agents, 2026-06-19")
  §5  Memory + lesson references ........ present
  §6  Strict scope (IN/OUT) ............. present (IN table + explicit OUT-of-scope)
  §7  Locked design decisions .......... present (D1, operator-confirmed 2026-06-19)
  §9  Sequenced atomic-commit plan ..... present (Commit 1,2,3,4,4b,5)
  §10 Critical files (NEW/MOD/UNTOUCHED) present (UNTOUCHED sub-section present)
  §11 Reused utilities ................. present (literal phrase "must consume, not reimplement")
  §14 Acceptance criteria ............. present (AC-1..AC-14)
  §15 Risks + RED stop conditions ..... present
  §19 Locked PR sequence position ..... present (all-tier requirement)
  §20 After-merge handoff ............. present
  - Missing required at R1: NONE
  - Extra (above-tier, non-blocking): Revision log (§22-equivalent — good hygiene)
  - Out-of-order: none material

NUMBERED-SERIES GAPS:
  - D-decisions: clean (D1 + D1.1–D1.5 sub-decisions, no gap)
  - B-commits:   clean (1,2,3,4,4b,5 — "4b" is a loop-#1 insertion, sequential, no gap)
  - AC series:   clean (AC-1..AC-14, no gap/dup)
  - R-risks:     risks table is UN-numbered (no R1/R2 ids) — minor; not required at R1

STREAM STRUCTURE (R3): n/a (R1)
SUBSTANTIVE LOSSES/ADDITIONS: n/a — no reference available (1b).
```

```
=== PHASE 2: PLAN-QUALITY ===

2.1 DESIGN-TESTS COVERAGE:
  | File                          | Bug-catalog? | Plan to add? |
  |-------------------------------|--------------|--------------|
  | flashcore/scheduler.py (MOD)  | none (repo has ZERO *.bug-catalog.md) | not proposed |
  | flashcore/models.py (MOD)     | none         | not proposed |
  | flashcore/review_processor.py | none         | not proposed |
  FLAG (non-blocking, project-wide): the repo uses NO bug-catalog-first convention
  (`find . -name '*.bug-catalog.md'` → empty). The plan does add behavior-pinning unit
  tests (AC-1/AC-2) + a Layer-B integration test (AC-12) that would catch an F169
  regression, so the *intent* of design-tests is met by tests-as-guards. Partial.

2.2a VERIFICATION MATRIX: n/a — R2+ only; flat AC list acceptable at R1.
2.2b ACCEPTANCE vs VERIFICATION: distinct enough — AC-1/AC-2 are outcome-shaped
     (elapsed_days>0, stability distinct); AC-3/4/6/7/9 are mechanical verification.
2.2c TEST LAYERS:
     A unit ........ present (AC-1, AC-2 in test_scheduler.py)
     B integration . present (AC-12 in TestReviewProcessorIntegration; real FSRS_Scheduler()
                     + FlashcardDatabase(":memory:") — DB-write path exercised against the
                     real SQLite engine, not a foreign surrogate). Fixtures VERIFIED to
                     exist: real_scheduler @ test_review_processor.py:388, in_memory_db:376,
                     sample_card:393. GOOD.
     C E2E ......... n/a (no UI/route/auth touched)
     D ratchet ..... no coverage floor configured (quality.coverage_floor blank) — flag only
                     that functional LOC is added without a numeric ratchet target.
     E local-CI .... ci.local_replica_cmd not configured; plan runs `pytest tests/ -q` pre-push.
     F operator .... n/a (no subprocess/daemon/external-system touched)

2.3 PACKET PRE-READ: §4 (prior-PR packet pre-reads) absent — R2+ only, not required at R1.
     review_processor.py is touched but no prior packet is cited; code-view deemed sufficient.
     Acceptable at R1 (non-blocking).

2.4 AUTOMATE-OVER-OPERATOR (run though table calls it optional at R1):
     §20.5 "Retro-verify (post-integration): spot-check elapsed_days_at_review > 0 in the
     reviews table" is parked as operator-only ("N/A until integration testing available").
     This step HAS a code path and is exactly what AC-12 (Layer-B) already automates against
     :memory: SQLite. Recommend deleting the operator-only retro-verify or pointing it at the
     Layer-B test rather than a human spot-check. Non-blocking observation.

2.5 CODE-HEALTH BASELINE:
     2.5 per-file: no tool configured (quality.code_health_cmd blank) — skipped.
     2.5 change-set: no tool configured (quality.code_health_changeset_cmd blank) — skipped.

2.8 MEMORY COVERAGE:
  | Principle                                              | Honored? |
  |--------------------------------------------------------|----------|
  | Never merge autonomously; human is merge gate          | yes (§5, §19) |
  | Author packets to shape; validate via aiv CLI not eye  | yes (§9 Commit 5, AC-8) |
  | Merge by rebase not squash                             | yes (brief §merge: rebase) |
  | Run local-CI replica before every push                 | yes (AC-9 / pytest tests/) |
  | Wall-clock drill for subprocess/daemon                 | n/a (no subprocess) |
  | DB-write paths against REAL DB not in-memory surrogate | partial — uses :memory: SQLite,
        which IS the real engine/dialect (same as prod FlashcardDatabase); acceptable |
  | Behavior-pinning tests + green existing for refactors  | yes (AC-1/2 pin, AC-6 keeps 15 green) |
  | GROUND-TRUTH over approximation (GT-1)                  | yes — Path A LOCKED; consumes
        reviews.ts via get_latest_review_for_card; Path B approximation explicitly DISFAVORED |
  No project memory index loaded (memory.dir/index absent) — universal-principle check only.
```

```
=== PHASE 3: PLAN-GRAPH + TEMPORAL (R1 → 3.1, 3.5) ===

3.1 BASE-SHA DRIFT: 0 commits. Plan base b5e1c4b == origin/main HEAD b5e1c4b
    (`git rev-list --count b5e1c4b..origin/main` → 0). Risk: LOW. No re-verify needed.

3.5 STOP CONDITIONS (RED): present in §15 with named thresholds + escalation actions:
    - any of 15 existing scheduler tests needs editing → halt, determine which side is wrong
    - mypy introduces new error unfixable without changing Card/SchedulerOutput interface → halt
    - aiv check non-zero after TWO correction attempts → escalate
    - any doubt re: persisting last_review_date → widens to R2, escalate
    - get_latest_review_for_card returns stale/unexpected data needing database.py change → escalate
    All have escalation actions. PASS.

(3.2 conflicts-with: only c2-f169-plan.md itself touches its files — no collision.
 3.3 open-questions / 3.4 streams / 3.6 budget / 3.7 revisions / 3.8 checkpoints / 3.9 untouched:
 outside R1 gate, but note §10 DOES carry an UNTOUCHED sub-section and §15 an iter budget echo —
 above-tier hygiene, no findings.)
```

```
=== GROUND-TRUTH / EXECUTION-ARTIFACT GATES (operator-mandated) ===

GT-1 (ground-truth-over-approximation): SATISFIED — no hard stop.
    The plan LOCKS Path A (D1): the hub reads the DB-recorded prior-review timestamp
    (reviews.ts) via get_latest_review_for_card BEFORE every compute_next_state call, and
    explicitly marks the stability-approximation Path B as DISFAVORED for ignoring recorded
    data. elapsed_days=0 is produced ONLY for genuinely first-ever reviews (no prior row).
    Verified against live code: scheduler.py:212 bug confirmed; Card has no last_review_date
    field (models.py:43-95); get_latest_review_for_card returns Optional[Review] (database.py:834).
    The plan chose the root-cause/ground-truth path over the symptom-masking one. No GT-1 stop.

GT-2 (executable claims must be EXECUTED, never reasoned): >>> HARD STOP — TRIGGERED <<<
    The plan asserts post-change RUNTIME/TEST behavior as proven WITHOUT an execution artifact:
      • §15 risk "Existing test_review_early_card breaks after fix" →
        "Verified analytically: … assertion result_early.elapsed_days < result_on_time.elapsed_days
         holds (0 < 1)"  — an executable test outcome, reasoned not run.
      • §15 risk "test_review_lapsed_card breaks" →
        "Verified analytically: … elapsed_days=10; on-time elapsed_days=1; 10 > 1 holds"
         — executable, reasoned not run.
      • §2 early-review side note → "After the fix, early elapsed_days=0 … The assertion …
         remains satisfied (0 < 1 …)" — post-change behavior asserted as satisfied without a run.
    These mirror INVARIANT #1 (no claim without runnable evidence). They MUST be re-tagged
    "UNVERIFIED — pending execution" or replaced with a real `pytest` artifact before the plan
    can converge. (The §9 per-commit "Verification before staging" blocks listing expected
    counts — 15/17/482/483 passed — are framed as commands TO RUN pre-stage, which is correct;
    they are NOT the violation.)

GT-2 test-input-layer sub-check: MET (with a thin spot).
    The fix MOVES the elapsed_days input source from scheduler-internal (last_review = due) to
    CALLER-supplied (card.last_review_date set by review_processor hub) — the exact F169 shape.
    The plan covers both layers: unit tests (AC-1/2) HARDCODE last_review_date on the Card (test
    supplies the input), and the Layer-B test (AC-12) drives process_review end-to-end so the HUB
    supplies it from the DB. §9 Commit 4b explicitly states the integration test "validates the
    DB-lookup path that in-memory unit tests could not cover" — that IS the input-source mapping.
    Spot: it is stated at the Layer-B rationale, not per-unit; making it explicit per unit test
    ("last_review_date hardcoded here; supplied by review_processor in production") would harden
    against a future hub-rewiring regression that the hardcoded unit test would silently survive.
    Non-blocking given AC-12 exists.
```

```
=== OVERALL VERDICT ===
Plan structural integrity: PASS — all R1-required canonical sections present; series clean.
Plan quality audit: PARTIAL — solid design (ground-truth Path A, A+B test layers, real-engine
    Layer-B with VERIFIED fixtures). Soft gaps: no bug-catalog convention (project-wide), no
    coverage ratchet target, one operator-only retro-verify (§20.5) that is already automatable.
Plan-graph readiness: PASS — base-SHA drift 0 (low risk); RED stop conditions present with
    thresholds + escalation actions; no conflicting in-flight plans.
HARD STOPS:
    - GT-2 / phase 2.2c (execution artifact): §15 + §2 assert post-change test behavior as
      "Verified analytically"/"holds"/"remains satisfied" with NO run. Re-tag UNVERIFIED — pending
      execution, or attach real pytest output.
Recommended next action: revise §15 (two "Verified analytically … holds" risk rows) and §2
    (early-review "remains satisfied" note) to "UNVERIFIED — pending execution"; then the plan is
    ready to exit plan mode and enter execution. No re-verify of base-SHA needed (drift 0).
    Optional hardening: add per-unit input-source note for AC-1/AC-2; delete/automate §20.5
    retro-verify; add a coverage-ratchet target if one exists upstream.
```

```
=== SURVIVORSHIP-BIAS DISCLOSURE ===
No project plan corpus or archetype was configured (plans.archetypes.* blank, no .aiv-workflow.yml),
so structural drift was scored against the skill's canonical 22-section list only — NOT against a
project-induced survivorship sample. A clean structural pass here means "matches the canonical
template," not "cannot fail." Sections marked OPTIONAL / above-tier may still be load-bearing for
failure modes this R1 plan has not encountered. Promotion criterion for any new required section:
name the specific failure mode it would have prevented.
```

## Machine-checkable data

```json
{
  "schema": "check_drift_verdict@1",
  "r_tier": "R1",
  "audit_depth_complete": true,
  "structural_integrity": "pass",
  "plan_quality": "partial",
  "plan_graph": "pass",
  "hard_stops": [
    {"id": "GT-2", "phase": "2.2c", "detail": "§15 (test_review_early_card, test_review_lapsed_card) and §2 early-review note assert post-change test behavior as 'Verified analytically'/'holds'/'remains satisfied' with no execution artifact; re-tag 'UNVERIFIED — pending execution' or attach a real pytest run."}
  ],
  "open_substantive_losses": 0,
  "iteration": 1
}
```
