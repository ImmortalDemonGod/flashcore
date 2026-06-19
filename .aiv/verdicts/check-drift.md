# check-drift verdict — PR-F169 (c2-f169-plan.md)

Audited: `.aiv/plans/c2-f169-plan.md` (iteration 3; revised in loops #1 GT-1 and #2 EXECUTABLE-CLAIMS+TEST-LAYER per its own revision log §560-565).
Repo: flashcore, branch `feat/c2-fsrs-harness` off `origin/main @ b5e1c4b`.
Config: **no `.aiv-workflow.yml` at repo root** — all skill defaults apply; archetypes blank → no reference diff.

```
=== PHASE 0: R-TIER ===
Declared: R1 (§1, line 21)
Inferred: R1 (basis: 6 commits [1,2,3,4,4b,5]; 1 new transient model field; 0 migrations;
          get_latest_review_for_card is CONSUMED as-is, not a new data-access method;
          no new dispatcher; 3 prod files + 2 test files)
Reconciled: R1 (declared == inferred)
Audit depth: Phase 1 full; Phase 2 = 2.1, 2.2, 2.3, 2.5, 2.8; Phase 3 = 3.1, 3.5
```

```
=== PHASE 1: STRUCTURAL DRIFT ===
REFERENCE: NONE — plans.archetypes.R1 blank (no .aiv-workflow.yml).
1b: no R1 archetype configured → running section-presence + series-gap checks
against the canonical list only, no reference diff.

SECTION-PRESENCE (R1-required set):
- §1 Context ✓  §2 Verified state ✓  §5 Memory+lessons ✓  §6 Scope boundaries ✓
- §7 Locked decisions (D1) ✓  §9 Sequenced atomic-commit plan ✓
- §10 Critical files (incl. UNTOUCHED sub-section) ✓  §11 Reused utilities
  (literal "must consume, not reimplement") ✓  §14 Acceptance criteria ✓
- §15 Risks + mitigations + stop conditions (RED) ✓  §19 PR sequence position ✓
- §20 After-merge handoff ✓
- Missing required at R1: NONE
- Extra non-canonical: "Revision log" (§22-class; exceeds R1 requirement; benign, GOOD)
- Out-of-order: none (canonical numbering, non-required sections elided)

NUMBERED-SERIES GAPS:
- D-decisions: D1 + D1.1–D1.5 — clean, no gaps
- Commit-series: 1,2,3,4,4b,5 — clean (4b is an explained insert, revision-log #1)
- AC-series: AC-1 … AC-14 — clean, no gaps/dupes
- R-risks/Q: risks are an unnumbered table (acceptable at R1); no open-Q section (not required at R1)

STREAM STRUCTURE (R3): n/a (R1)
SUBSTANTIVE LOSSES/ADDITIONS: n/a — no reference configured (section-presence only)
```

```
=== PHASE 2: PLAN-QUALITY (R1 subset) ===

2.1 DESIGN-TESTS COVERAGE: SATISFIED (na_ok:true).
    STAGE-ORDERING: *.bug-catalog.md is PRODUCED at design-tests (Stage 5), which runs
    AFTER this plan gate — its file cannot and must not be required now. The plan pins
    the bug BEHAVIORALLY via AC-1 (on-time elapsed_days>0), AC-2 (on-time vs same-day
    stability distinct), AC-12 (persisted elapsed_days_at_review>0), and commits to the
    two named unit tests + one Layer-B test. Commitment present → not blocking.

2.2a VERIFICATION MATRIX: n/a (R2+ only).
2.2b ACCEPTANCE vs VERIFICATION: distinct — outcome-shaped ACs (AC-1/2/12) vs
    mechanical verification (AC-3/4/13/14 greps, AC-6/9 test counts). Not collapsed.
2.2c TEST LAYERS: Layer A (unit, Commit 4) + Layer B (integration, Commit 4b) against
    real SQLite FlashcardDatabase(":memory:") + real FSRS_Scheduler(). Correct: a DB
    read/write path (get_latest_review_for_card / add_review_and_update_card) is touched,
    so Layer B is required and present. SQLite :memory: is the REAL engine (not a
    dict/mock surrogate) → honors "exercise DB-write paths against the real database."
    INPUT-PROVENANCE (GT-2 second clause): SATISFIED. Explicit TEST-LAYER CONTRACT blocks
    state, per unit, which layer supplies each input:
      • Commit 4 (unit): last_review_date set EXPLICITLY on the Card constructor (test
        simulates the hub); review_ts passed literally. Neither generated inside
        compute_next_state.
      • Commit 4b (integration): test does NOT set last_review_date; the hub produces it
        from the real DB — the end-to-end path the unit layer cannot cover.
    This is exactly the F169 failure mode (a consumed input that moves to the caller)
    addressed head-on. PASS.

2.3 PACKET PRE-READ: code-view sufficient for all 3 MOD files — F169 is a fresh finding
    with no prior AIV packet on those surfaces. §10 "Read before touching" lists the exact
    code spans. Adequate at R1.

2.5 CODE-HEALTH BASELINE: 2.5 per-file — no per-file code-health tool configured
    (quality.code_health_cmd blank) — skipped. 2.5 change-set — no change-set code-health
    tool configured (quality.code_health_changeset_cmd blank) — skipped.

2.8 MEMORY COVERAGE: memory index not configured (memory.dir absent). Universal principles:
    | Principle | Honored? |
    |---|---|
    | Never merge autonomously (human merge gate) | yes — §19 "Merge authority: human operator only" |
    | Packets validated via aiv CLI, not by eye | yes — AC-8 `aiv check` exits 0 |
    | Run local-CI replica before push | yes — AC-9 full `pytest tests/` |
    | DB-write paths against real DB, not surrogate | yes — Layer-B uses real SQLite :memory: |
    | Behavior-pinning + green existing tests | yes — 15 existing scheduler tests gated green (AC-6) |
    | Never edit a test to pass w/o deciding which side is wrong | yes — §15 RED stop condition |
    No uncited applicable principle. PASS.

2.4 / 2.6 / 2.7: out of R1 audit depth — not run.
```

```
=== PHASE 3: PLAN-GRAPH + TEMPORAL (R1 subset) ===

3.1 BASE-SHA DRIFT: plan pins base origin/main @ b5e1c4b; worktree HEAD is the same
    commit (finding header). Drift ≈ 0 → LOW risk. Note only.

3.5 STOP CONDITIONS (RED): present with NAMED thresholds + escalation actions —
    (a) any existing scheduler test needs editing → stop, decide which side is wrong;
    (b) mypy new error requiring public-interface change → stop;
    (c) aiv check non-zero after two attempts → stop;
    (d) any doubt last_review_date must be PERSISTED this PR → widens to R2, escalate;
    (e) get_latest_review_for_card needs database.py modification → scope widened, escalate.
    Escalation = AskUserQuestion. PASS.

3.2/3.3/3.4/3.6/3.7/3.8/3.9: out of R1 audit depth — not run.
(3.9 nonetheless satisfied: §10 carries an explicit UNTOUCHED sub-section.)
```

```
=== TASK-INJECTED GATES ===

GT (ground-truth-over-approximation): NOT TRIGGERED — gate SATISFIED.
  Plan LOCKS Path A (D1): the hub consumes the DB-recorded prior-review timestamp via
  get_latest_review_for_card(card.uuid) → prior_review.ts.date() BEFORE every
  compute_next_state call. No value already recorded is approximated/derived: reviews.ts
  is the ground truth and it is READ, not estimated. Path B (stability-as-proxy) is
  explicitly marked DISFAVORED/rejected in §7 precisely because it ignores recorded
  reviews.ts. elapsed_days=0 survives ONLY for genuinely first-ever reviews (no prior
  row) — correct, not approximate. Root cause (no last_review_date on the model) fixed,
  not masked.

GT-2 (executable-claims-must-be-executed + per-unit input layer): NOT TRIGGERED.
  • No post-change runtime/test behavior asserted as VERIFIED/holds/confirmed without a
    run. The two former "Verified analytically" risk rows (test_review_early_card,
    test_review_lapsed_card) are correctly re-tagged "UNVERIFIED — pending execution" with
    exact post-Commit-2 commands (revision-log #2). §2's "confirmed by direct Read" facts
    are STATIC pre-change reads (re-verified below), not post-change executable claims. ACs
    use "cmd → expected result" threshold format (pending execution), not having-passed
    assertions.
  • Per-unit input provenance stated for every unit under test (see 2.2c); the F169-class
    failure (a consumed input silently absent when moved to the caller) is named and
    assigned to the integration layer.
  Independent re-verification of §2 static facts (path:line):
    - scheduler.py:212  `fsrs_card.last_review = fsrs_card.due` — confirmed
    - models.py:43/51   Card has NO last_review_date; ConfigDict(extra="forbid") — confirmed
    - models.py:199     Review.ts present — confirmed
    - database.py:834   get_latest_review_for_card; :788 get_reviews_for_card — confirmed
    - review_processor.py:101-102 compute_next_state(card=, new_rating=, review_ts=ts);
      :124 add_review_and_update_card — confirmed
    - test_review_processor.py:375-393 fixtures in_memory_db/real_scheduler/sample_card
      EXIST; database.py:187 upsert_cards_batch EXISTS — confirmed

  NON-BLOCKING OBSERVATIONS (for design-tests stage, not gate failures):
  - AC-12 phrasing "elapsed_days_at_review > 0 confirmed" — read as the acceptance
    threshold (pending the cmd run), not a having-passed assertion; consider "expected"
    to remove ambiguity.
  - test_on_time_vs_same_day_review_stability_distinct compares an on-time Review card vs
    a fresh New card (same day), not a same-day RE-review of the SAME card as contract
    VERIFY[2] describes; design-tests should confirm the test exercises the intended
    on-time-vs-same-day-re-review distinction.
```

```
=== OVERALL VERDICT ===
Plan structural integrity: PASS (all R1-required sections present; series clean)
Plan quality audit: PASS (2.1 satisfied via behavioral pin + commitment; layers A+B with
  per-unit input provenance; memory principles honored; code-health skipped — no tool)
Plan-graph readiness: PASS (base-SHA drift ~0; RED stop conditions named with escalation)
HARD STOPS: none
  (GT ground-truth gate SATISFIED — Path A reads reviews.ts, no approximation;
   GT-2 SATISFIED — no unexecuted "verified" claims; per-unit input layer stated)
Recommended next action: EXIT plan mode → proceed to design-tests (Stage 5). Carry the
  two non-blocking observations into design-tests; produce the *.bug-catalog.md companion there.
```

```
=== SURVIVORSHIP-BIAS DISCLOSURE ===
No project plan corpus or archetype is configured (no .aiv-workflow.yml), so this run used
the skill's canonical section list only — section-presence + series-gap, no reference diff.
A clean structural pass means "matches the canonical template", NOT "cannot fail". Sections
absent from the template may still be load-bearing for failure modes not yet encountered.
Promotion criterion for any new template section: name the specific failure mode it prevents.
```

## Machine-checkable data

```json
{
  "schema": "check_drift_verdict@1",
  "r_tier": "R1",
  "audit_depth_complete": true,
  "structural_integrity": "pass",
  "plan_quality": "pass",
  "plan_graph": "pass",
  "hard_stops": [],
  "open_substantive_losses": 0,
  "iteration": 3
}
```
