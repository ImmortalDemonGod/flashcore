# check-drift verdict — c2-f82 (Finding F82)

Plan audited: `.aiv/plans/c2-f82-plan.md`
Finding: F82 — unbounded infinite retry loop in `start_review_flow` (`audit/02-static-audit.md#L92`)
Date: 2026-06-19 · Iteration 1

```
=== PHASE 0: R-TIER ===
Declared: R1 (plan header line 5)
Inferred: R1 (basis: 5 commits; 0 new files [skip_card is a method added to an existing
          class]; 0 migrations; no new substrate/dispatcher; presentation-layer logic +
          one public one-line method + test changes)
Reconciled: R1 (declared == inferred; no mismatch)
Audit depth: Phase 1 full · Phase 2 {2.1, 2.2, 2.3, 2.5, 2.8} · Phase 3 {3.1, 3.5}

=== PHASE 1: STRUCTURAL DRIFT ===
REFERENCE: NONE — no R1 archetype configured (.aiv-workflow.yml absent; plans.archetypes.R1
           blank). Per 1b: structural-drift-vs-reference DISABLED for this run — running
           section-presence + numbered-series checks against the canonical list only, no
           reference diff.

SECTION-PRESENCE (against canonical list, R1-required column):
- Present & required at R1: §1 Context, §2 Verified state, §5 Memory+lessons, §6 Strict
  scope (IN/OUT with dispositions), §7 Locked design decisions (D1–D4, dated, operator-
  confirm-pending), §9 Sequenced atomic-commit plan (B1–B5 flat — correct for R1),
  §10 Critical files (NEW/MOD + "Files confirmed NOT requiring changes" = UNTOUCHED),
  §11 Reused utilities (literal phrase present), §14 Acceptance criteria (outcome-shaped),
  §15 Risks + RED stop conditions, §19 Locked PR sequence position, §20 After-merge handoff.
- Missing required at R1: NONE.
- Sections absent but NOT required at R1 (R2+ only — correctly omitted): §0 metadata,
  §3 pre-authoring verifications, §4 prior-PR packet pre-reads, §8 open questions,
  §12 test-strategy layers, §13 verification matrix, §16 code-review resilience,
  §17 rituals, §18 iter budget, §21 session checkpoints, §22 plan revisions.
- Extra non-canonical: AskUserQuestion gate-status note (header) — informational, harmless.
- Out-of-order: none.

NUMBERED-SERIES GAPS:
- D-decisions: D1–D4 — clean, no gap/dup.
- B-commits: Commit 1–5 — clean, no gap/dup.
- V-verifications: V1–V16 — clean.
- Gates [1]–[12] — clean.
- R-risks: listed (un-numbered, acceptable at R1).

STREAM STRUCTURE (R3): N/A — R1, flat ledger is correct.

SUBSTANTIVE LOSSES / ADDITIONS: N/A — no reference available (no archetype configured).

=== PHASE 2: PLAN-QUALITY ===

2.1 DESIGN-TESTS COVERAGE — SATISFIED (na_ok:true).
  Per stage-ordering rule, 2.1 at the plan gate is COMMITMENT-vs-EXISTENCE: the
  *.bug-catalog.md is produced at Stage 5 (design-tests), AFTER this gate, so its file
  cannot be required to exist now. The plan PINS THE BUG BEHAVIORALLY: AC gate [1] (loop
  bounded when all submit_review raise), gate [2] (finite termination, --timeout=10),
  gate [3] ("Well done" absent on total failure), plus three named regression tests
  (Commit 4a/4b/4c). Commitment present → not blocking.
  | File | Bug pinned? |
  |---|---|
  | flashcore/cli/review_ui.py (MOD, primary) | yes — gates [1][2][3] + tests 4a/4b/4c |
  | flashcore/review_manager.py (MOD, +skip_card) | covered via integration in 4a/4b |
  | flashcore/cli/_review_logic.py (MOD) | NOT behaviorally pinned — see 2.2c / HARD STOP GT-3 |

2.2a VERIFICATION MATRIX: n/a at R1 (R2+ when criteria>3). §14 gate×command table is
     matrix-shaped; acceptable.
2.2b ACCEPTANCE vs VERIFICATION: partially collapsed — §14 mixes outcome-shaped acceptance
     ("Well done absent", "loop bounded", "exit signals failure") with mechanical verification
     ("lint passes", "suite ≥482", "aiv check exits 0") in one table. Tolerable at R1; not a
     blocker.
2.2c TEST LAYERS: Layer A (unit) present and well-specified — the plan correctly states,
     per unit, WHICH layer supplies each input (manager is produced by the hub caller
     _review_logic.py; review_queue / get_next_card.side_effect / submit_review.side_effect /
     skip_card.side_effect set explicitly; closure simulates real queue mutation). This
     directly closes the silently-breaking-unit-test failure mode (the masked V9 test at
     test_review_ui.py:133 used `[card, None]` which terminated independent of skip_card).
     ►► LAYER GAP (load-bearing): the finding GOAL clause "exit signals failure" is exercised
     by NO test. The bool return of start_review_flow is unit-tested (4b → return False), but
     the wiring `_review_logic.py: if not result: raise typer.Exit(code=1)` is verified ONLY
     by a static grep (gate [5]). The project HAS an established convention for verifying CLI
     exit codes — `tests/cli/test_main.py` asserts `result.exit_code == 1` via CliRunner at
     ~14 sites. A real exit-code test is therefore demonstrably POSSIBLE, not impossible. See
     HARD STOP GT-3 (Drives A/D/E).

2.3 PACKET PRE-READ: n/a — fresh fix; no prior AIV packets touch these surfaces. MOD files
     verified by direct Read (§2 V1–V14); code-view sufficient.

2.4 AUTOMATE-OVER-OPERATOR: n/a at R1 audit set. Note: the plan's §7 AskUserQuestion gate
     (operator confirms D1–D4) is a design-approval step, not a runtime operator-validation
     step with a code path — no test surface owed.

2.5 CODE-HEALTH BASELINE: 2.5: no per-file code-health tool configured
     (quality.code_health_cmd blank) — skipped. 2.5: no change-set code-health tool configured
     (quality.code_health_changeset_cmd blank) — skipped.

2.6 FAN-OUT TRIGGER: n/a at R1 audit set. (Would be NO regardless: ≤3 effective subsystems,
     no unverified codebase claims — all V1–V16 confirmed by direct read.)

2.7 CODE-REVIEW RESILIENCE: n/a — R1; no prior automated-review contact on this branch.

2.8 MEMORY COVERAGE: no MEMORY.md / lesson store present (plan §5 confirms). Universal
     principles cross-check:
  | Principle | Applies | Honored? |
  |---|---|---|
  | Never merge autonomously; human is merge gate | yes | yes (§5, §19 — H2 only) |
  | Author packets to shape; validate via aiv CLI, not by eye | yes | yes (§9 aiv check before push) |
  | Merge by rebase not squash | yes | not stated, not contradicted — note |
  | Run local-CI replica before push | yes | yes (§9 `make lint && pytest` pre-push) |
  | Wall-clock drill for subprocess/daemon | no | N/A — no subprocess touched |
  | DB-write path against real DB, not surrogate | conditional | N/A — the fix mutates an
    in-memory queue list (skip_card→_remove_card_from_queue); no DB-write path changed |
  | Behavior-pinning + green existing tests for refactor | this is a fix, not refactor | plan
    adds regression tests + keeps suite green (gate [9]) — honored in spirit |

=== PHASE 3: PLAN-GRAPH + TEMPORAL (R1 set: 3.1, 3.5) ===

3.1 BASE-SHA DRIFT: ZERO drift. Current base HEAD = 5bb2ea2, which is identical to the
    Class E intent SHA (5bb2ea2ab72239e0d2de7cc51fd4b5b766e44bfb). `git rev-list --count`
    base..base = 0. Risk: LOW. (Plan declares no §0 base-SHA pin — R2+ feature, not required
    at R1; the all-direct-read verification in §2 was done today against this HEAD.)

3.5 STOP CONDITIONS: PRESENT. §15 RED block names thresholds + escalation: any new mypy
    error → resolve before push (no `# type: ignore` bypass); aiv check blocking error
    (≠E004) → rephrase/correct, never --no-verify; pytest failures >0 → investigate;
    test count <480 → investigate before push. Thresholds + actions both present. Pass.

(3.2 conflicts-with, 3.3 open-questions, 3.4 streams, 3.6 budget, 3.7 revisions, 3.8
 checkpoints, 3.9 untouched — outside R1 audit depth. Spot-checked: 3.2 — the only other
 active plan, c2-f169-plan.md, does NOT touch review_ui.py/review_manager.py/_review_logic.py;
 no collision. 3.9 — UNTOUCHED set is present (§10 "Files confirmed NOT requiring changes").)

=== GROUND-TRUTH-OVER-APPROXIMATION GATE ===
GT-1 (approximation of recorded/retrievable values): CLEAN. The plan consumes ground truth
  rather than approximating: reuses `_remove_card_from_queue` instead of reimplementing queue
  removal (V12); consumes the established `typer.Exit(code=1)` exit convention (main.py:58,
  verified ~20 sites); pins Class E to the real audit SHA (5bb2ea2). It chooses the ROOT-CAUSE
  path (skip_card removes the failed card so the loop advances) over the symptom-masking Path B
  (break out of loop, leaving the card in queue) — §7 Decision 1 disfavors Path B explicitly.
  No timestamp/value is estimated where a stored value exists. No GT-1 hard stop.

GT-2 (post-change behavior asserted VERIFIED without an execution artifact): CLEAN as to
  premature verified-tagging. Every post-change claim is correctly tagged "UNVERIFIED — pending
  execution" (§14 all gates; §9 line 386; §15 lines 508–509). §2 "VERIFIED" rows are direct
  reads of EXISTING (pre-change) code, not post-change behavior — legitimate. The test strategy
  ALSO states, per unit under test, which layer supplies each consumed input (2.2c) — closing
  the silently-breaking-unit-test failure mode. No GT-2 hard stop. (The behavioral-coverage gap
  for "exit signals failure" is a verification-METHOD defect, raised under GT-3, not a
  false-verified-tag defect.)

=== OVERALL VERDICT ===
Plan structural integrity: PASS — all R1-required canonical sections present; series clean;
  no archetype, so section-presence-only as designed.
Plan quality audit: PARTIAL — design is sound and well-grounded; ONE load-bearing verification
  gap: the finding-GOAL clause "exit signals failure" is proven only by a static grep, not by
  execution, despite an in-project CliRunner exit-code convention that makes the execution test
  possible.
Plan-graph readiness: PASS — zero base-SHA drift; RED stop conditions present; no conflicts.

HARD STOPS:
- GT-3 (Drives A, D, E) — "exit signals failure" verified by grep, not execution.
  Drive A: the integration/CLI test that proves the primary-deliverable clause is declared
    "out-of-scope" (Commit 3 contract, plan lines 288–296). "exit signals failure" is named
    in the finding GOAL — it is a primary deliverable, NOT a nice-to-have. Calling its test
    "out-of-scope" is a scope-reducing reinterpretation, not a grounded severance.
  Drive D: gate [5] ("grep -n 'typer.Exit' _review_logic.py" non-empty) is a static-presence
    proxy treated as PASS. The wiring `if not result: raise typer.Exit(code=1)` can be
    mis-wired (wrong condition, swapped branch) and the grep still passes — silence/string-
    presence is UNKNOWN, not PASS.
  Drive E: the project's live-fire convention for exit behavior is CliRunner + `result.exit_code
    == 1` (tests/cli/test_main.py, ~14 sites). The plan substitutes the cheaper grep proxy.
    Adding a CliRunner test for the `review` command asserting exit_code == 1 when all reviews
    fail is demonstrably POSSIBLE (the convention exists) — so the exemption is not "impossible,"
    merely costlier, which Drive B forbids.
  REQUIRED REMEDIATION: add an execution test (CliRunner against the review command, or
  pytest.raises(typer.Exit) on review_logic()) asserting exit code == 1 / typer.Exit(code=1)
  is raised when start_review_flow returns False; re-tag gate [5] from grep to that execution
  artifact. Until then the plan is NOT converged.

No GT-1 hard stop. No GT-2 hard stop. The Drive-A severance of `_review_all_logic.py`,
`test_review_all_logic.py`, retry-backoff, and F83–F114 is VALID and grounded: ground-truth
read confirms `_review_all_logic.py` uses a bounded `for card in all_due_cards:` loop
(lines 49/58/64), NOT a `while get_next_card()` queue-retry — the loop-boundedness invariant
does not apply there, so it correctly ships separately.

Recommended next action: REVISE the plan — convert gate [5] / Commit 3 test-layer contract
from a static grep to a real execution test of the CLI exit code (CliRunner exit_code==1 OR
pytest.raises(typer.Exit) on review_logic), citing AIV evidence class A/B (live-fire), then
re-run check-drift. All other dimensions pass.

=== SURVIVORSHIP-BIAS DISCLOSURE ===
This template is induced from the project's own (here: empty) plan corpus and the canonical
section list, weighted toward plans that shipped. A clean structural pass means "matches the
surviving corpus / canonical list", NOT "cannot fail". No R1 archetype was configured, so the
substantive vs-reference diff was disabled — only section-presence + series checks ran. Sections
not in the template may still be load-bearing for failure modes not yet encountered. Promotion
criterion for any new template section: name the specific failure mode it would have prevented.
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
    {
      "id": "GT-3",
      "phase": "2.2c",
      "detail": "Drives A/D/E: finding-GOAL clause 'exit signals failure' is verified ONLY by static grep (gate [5]: grep typer.Exit non-empty), not by execution. Drive A: the CLI/integration test proving this primary-deliverable clause is declared out-of-scope (plan lines 288-296) — a scope-reducing reinterpretation of a clause named in the finding GOAL. Drive D: a string-presence grep treated as PASS cannot detect mis-wiring of `if not result: raise typer.Exit(code=1)`. Drive E: project has an established CliRunner exit_code==1 convention (tests/cli/test_main.py ~14 sites) making the execution test demonstrably possible; the grep is the cheap proxy. Remediation: add CliRunner/pytest.raises(typer.Exit) test asserting exit code 1 when all reviews fail; re-tag gate [5] to that execution artifact (evidence class A/B)."
    }
  ],
  "open_substantive_losses": 0,
  "iteration": 1
}
```
