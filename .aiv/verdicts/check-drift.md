# check-drift verdict — PR-F169 plan (`.aiv/plans/c2-f169-plan.md`)

Audited 2026-06-19 against the `check-drift` skill. Iteration 3 (plan already revised
in loops #1 and #2 per its own revision log §560-565). Repo: flashcore, branch
`feat/c2-fsrs-harness` @ `origin/main b5e1c4b`.

> Config: no `.aiv-workflow.yml` at repo root — skill defaults used and announced inline.

```
=== PHASE 0: R-TIER ===
Declared:   R1 (plan §1, line 21)
Inferred:   R1 (basis: 3 prod files [models.py, scheduler.py, review_processor.py]
            + 2 test files; 5 logical commits; NO migration, NO new data-access
            method [consumes existing get_latest_review_for_card db/database.py:834],
            NO new dispatcher; transient model field only)
Reconciled: R1 (no mismatch). BORDERLINE note: CRITICAL finding touching the core
            FSRS computation with a new cross-component data flow (model→hub→scheduler)
            leans toward R2; held at R1 because none of the R2 triggers (≥10 commits,
            new data-access method, new dispatcher, migration) are met.
Audit depth: Phase 1 full; Phase 2 = 2.1, 2.2, 2.3, 2.5, 2.8; Phase 3 = 3.1, 3.5
```

```
=== PHASE 1: STRUCTURAL DRIFT ===
REFERENCE: NONE — no R1 archetype configured (plans.archetypes.R1 blank; no config
file). 1b: running section-presence + numbered-series checks against the canonical
list only, no reference diff.

SECTION-PRESENCE (R1-required = canonical 1,2,5,6,7,9,10,11,14,15,19,20):
- §1 Context ✓   §2 Verified state (0 Explore agents, 2026-06-19) ✓
- §5 Memory+lesson refs ✓   §6 Strict scope (IN/OUT) ✓
- §7 Locked design decisions (D1, operator-confirmed 2026-06-19) ✓
- §9 Sequenced atomic-commit plan ✓   §10 Critical files w/ UNTOUCHED sub-section ✓
- §11 Reused utilities (literal phrase present) ✓   §14 Acceptance criteria ✓
- §15 Risks + mitigations + stop conditions (RED) ✓
- §19 Locked PR sequence position ✓   §20 After-merge handoff ✓
- Missing required at R1: NONE
- Extra (above tier, beneficial): Revision log (≈ canonical §22) present — good practice
- Absent R2+ sections (na_ok at R1): §0 metadata block, §3 pre-authoring verifications,
  §4 prior-packet pre-reads, §8 open-questions, §12 full test-strategy layers,
  §13 verification matrix, §17 rituals, §18 iter budget (iter budget lives in launch
  brief instead), §21 session checkpoints
- Out-of-order: none (custom numbering, monotonic)

NUMBERED-SERIES GAPS:
- D-decisions: clean (D1, D1.1–D1.5)
- B-commits: clean (1,2,3,4,4b,5 — "4b" is a deliberate labeled insert, not renumber drift)
- AC-series: clean (AC-1…AC-14)
- R-risks: unnumbered (minor — risks listed as table rows, no R# IDs)
- Q-questions: none (no §8; acceptable at R1)

STREAM STRUCTURE (R3): n/a (R1)

SUBSTANTIVE LOSSES/ADDITIONS: n/a — no reference available (1b)
```

```
=== PHASE 2: PLAN-QUALITY ===

2.1 DESIGN-TESTS COVERAGE:
| File (NEW/MOD)               | Bug-catalog companion?              | Plan to add? |
|------------------------------|-------------------------------------|--------------|
| flashcore/scheduler.py       | absent (no *.bug-catalog.md in repo) | not planned  |
| flashcore/models.py          | absent                              | not planned  |
| flashcore/review_processor.py| absent                              | not planned  |
  FLAG (partial): the project has ZERO *.bug-catalog.md files (repo-wide convention
  absent, not a plan regression). The plan does NOT adopt bug-catalog-first. MITIGATING:
  the plan's design-tests are strong and bug-targeted — test_on_time_review_elapsed_days_positive
  (AC-1) directly pins the F169 regression that the existing suite silently passed
  (plan §2 line 41 documents the silent-pass gap). This is a quality gap on FORM
  (no bug-catalog file), not on the substance of regression coverage.

2.2a VERIFICATION MATRIX: n/a at R1 (R2+ when criteria>3). 14 ACs are a flat checklist.
2.2b ACCEPTANCE vs VERIFICATION: partially collapsed — AC-1/AC-2/AC-12 are outcome-shaped
     (elapsed_days>0, stability distinct), AC-3…AC-11/AC-13/AC-14 are mechanical
     verification (grep/mypy/suite-green) mixed into one table. Acceptable at R1; note only.
2.2c TEST LAYERS: A (unit, Commit 4) ✓, B (integration, Commit 4b) ✓. C n/a (no UI/route),
     D no explicit coverage-ratchet floor (quality.coverage_floor blank — flag the absence
     of a numeric target only), E local-CI replica = full-suite run in §9/AC-9 ✓ implicit,
     F operator-drill n/a. Layer B correctly targets a DB-write path.

2.3 PACKET PRE-READ: §10 "Read before touching" lists the 5 source ranges. No prior AIV
     packet pre-reads cited — none required (no prior packet covers this surface at R1).

2.4 AUTOMATE-OVER-OPERATOR: n/a at R1 depth. Note: pre-merge operator confirmations
     (code-review read, path-decision documented) are inherent merge-gate steps, not
     code-path-testable; AC-1/AC-2/AC-12 already automate the behavioral acceptance.

2.5 CODE-HEALTH BASELINE: skipped — no per-file code-health tool configured
     (quality.code_health_cmd blank); no change-set tool configured
     (quality.code_health_changeset_cmd blank).

2.6 FAN-OUT TRIGGER: n/a at R1 depth. (Would be NO: facts are first-party Read-verified;
     scope is 3 files, well-bounded; no new gates/CLI/env vars.)

2.7 CODE-REVIEW RESILIENCE: n/a — no prior automated-review contact on this branch.

2.8 MEMORY COVERAGE:
| Principle                                              | Applies | Honored? |
|-------------------------------------------------------|---------|----------|
| Never merge autonomously; human is merge gate         | yes     | yes (§19, §15 RED) |
| Author packets to shape; validate via aiv CLI not eye | yes     | yes (§9 Commit 5, AC-8) |
| Merge by rebase, not squash                           | yes     | yes (brief merge.strategy=rebase) |
| Run local-CI replica before push                      | yes     | yes (AC-9 full suite) |
| Wall-clock drill for subprocess/daemon                | no      | n/a |
| Exercise DB-write paths against the REAL database     | yes     | yes — Layer-B uses DuckDB :memory: = SAME engine as prod (db/database.py imports duckdb), NOT a cross-dialect surrogate. NOTE: plan prose mislabels it "in-memory SQLite" (Commit 4b docstring + §title) — factual wording error; engine is DuckDB. Cosmetic, fix before authoring. |
| Behavior-pinning + green existing tests for refactor  | yes     | yes (15 existing stay green, AC-6; 2 new pin the bug) |
  §5 also cites the project's GT-1 lesson, E010 trap, SHA-pinned intent URL, hub-and-spoke.
  No uncited applicable universal principle found.
```

```
=== PHASE 3: PLAN-GRAPH + TEMPORAL (R1 subset: 3.1, 3.5) ===

3.1 BASE-SHA DRIFT: plan base = origin/main @ b5e1c4b; current origin/main @ b5e1c4b.
    git rev-list --count b5e1c4b..origin/main = 0. Drift 0 → LOW risk. Pin valid.
3.2 CONFLICTS-WITH: n/a at R1 depth; probed anyway — only c2-f169-plan.md active in
    .aiv/plans (mtime <14d, no MERGED/SHIPPED suffix). No collision.
3.3 OPEN QUESTIONS: n/a at R1 (no §8). No blocks-B0 item → no HARD STOP from this axis.
3.4 STREAMS: n/a (R1).
3.5 STOP CONDITIONS (RED): present — §15 "RED STOP CONDITIONS" names 5 thresholds
    (existing test needs edit → stop; mypy new error on public interface; aiv check
    non-zero after 2 attempts; persistence-doubt widens to R2; database.py change needed)
    each with escalation action (AskUserQuestion / halt). Iter budget = 2 cycles (brief).
    Gap (minor): no explicit LOC-drift % cap; acceptable for a 3-file R1.
3.6–3.9: n/a (R2+/R3 only).
```

## Task-mandated hard-stop checks (GT + GT-2)

**GT (ground-truth-over-approximation) — NOT TRIGGERED.**
The plan LOCKS Path A (§7 D1), which consumes the DB-recorded prior-review timestamp
(`reviews.ts` via `get_latest_review_for_card`, db/database.py:834-847 — verified) before
every `compute_next_state` call. Path B (stability approximation) is explicitly marked
DISFAVORED (§7 lines 126-130). No value that is recorded/retrievable is approximated:
`elapsed_days=0` results ONLY for genuinely first-ever reviews (no prior `reviews` row).
The earlier `due`-date proxy (root cause, scheduler.py:211-212 — verified on disk) is
removed, not masked. Root cause (no `last_review_date` on the Card model) is fixed at
source (models.py field + hub population). GT gate: PASS.

**GT-2 (executable claims must be executed; test-layer input provenance) — NOT TRIGGERED.**
- No post-change test/runtime behavior is asserted as verified without an execution
  artifact. §15 re-tags the two prior "Verified analytically" predictions
  (`test_review_early_card`, `test_review_lapsed_card`) as "UNVERIFIED — pending
  execution" with the exact commands to run (lines 496-497; remediated loop #2).
  §2's "confirmed by direct Read tool calls" are PRE-change current-state facts
  (Read IS the artifact); §9 "Verification before staging" outputs ("17 passed" etc.)
  are framed as steps-to-run, not asserted results. AC-12's "confirmed" (line 481) is
  the pass-spec for the named command, not a claim of prior verification — acceptable.
- Test strategy states, per unit, WHICH layer supplies each consumed input:
  Commit 4 TEST-LAYER CONTRACT (line 274) — `last_review_date` is hub-produced; the unit
  test sets it explicitly on the Card constructor (simulating the hub), `review_ts` passed
  by caller; end-to-end production deferred to integration. Commit 4b TEST-LAYER CONTRACT
  (line 346) — integration test does NOT set `last_review_date`; the hub produces it from
  the real DB. This directly forecloses the F169 failure mode (a unit test silently
  omitting a caller-supplied input). GT-2 gate: PASS.

```
=== OVERALL VERDICT ===
Plan structural integrity: PASS (all R1-required canonical sections present; series clean)
Plan quality audit: PARTIAL — strong, bug-targeted design-tests and full Layer-A/B
  coverage; gaps are FORM not substance: (1) no *.bug-catalog.md companions (repo-wide
  convention absent), (2) "SQLite" wording mislabels the DuckDB :memory: engine (cosmetic;
  fix before authoring), (3) acceptance vs verification slightly collapsed in the AC table.
  None block execution.
Plan-graph readiness: PASS — base-SHA pin exact (drift 0), no conflicting active plans,
  RED stop conditions present with escalation actions.
HARD STOPS: none
Recommended next action: exit plan mode and proceed to authoring. Before B0, apply two
  cosmetic corrections (no re-audit needed): (a) replace "in-memory SQLite" with
  "in-memory DuckDB" in Commit 4b prose; (b) optionally split the AC table into
  acceptance (outcome) vs verification (mechanical) for clarity. Consider adopting a
  scheduler.bug-catalog.md to formalize the regression catalog, though the inline
  design-tests already capture the F169 bug.
```

```
=== SURVIVORSHIP-BIAS DISCLOSURE ===
No project plan corpus / archetype is configured (plans.archetypes.R1 blank, no
.aiv-workflow.yml), so structural drift was checked against the skill's canonical
22-section list only — no reference diff. A clean structural pass therefore means
"matches the canonical template", NOT "cannot fail". The canonical list is itself
induced from surviving plans; sections it omits may still be load-bearing for failure
modes not yet encountered. Promotion criterion for any new section: name the specific
failure mode it would have prevented.
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
  "hard_stops": [],
  "open_substantive_losses": 0,
  "iteration": 3
}
```
