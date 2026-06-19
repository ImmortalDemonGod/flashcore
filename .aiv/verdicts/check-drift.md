# check-drift verdict — c2-f169-plan.md (PR-F169 elapsed_days fix)

Plan: `.aiv/plans/c2-f169-plan.md` · Repo: flashcore · Working branch: `feat/c2-fsrs-harness` @ 861a89c · Base `origin/main` @ b5e1c4b · iteration 4

=== PHASE 0: R-TIER ===
Declared: R1 (§1, §6, all commits tagged `-t R1`)
Inferred: R1 (basis: 5 commits; 3 prod files + 1 test; 0 migrations; no new dispatcher; the
  ground-truth read it *should* use is an EXISTING data-access method, `get_latest_review_for_card`,
  not a new one → does not trip the R2 "new data-access method" heuristic for the planned scope)
Reconciled: R1 (declared == inferred). NOTE: if the corrected ground-truth path were to also persist
  `last_review_date` (it must not in this PR — explicitly deferred), the migration would push R2.
  Scope-as-planned stays R1.
Audit depth: Phase 1 full · Phase 2 {2.1, 2.2, 2.3, 2.5, 2.8} · Phase 3 {3.1, 3.5}

Config: `.aiv-workflow.yml` ABSENT — using inline defaults (plans.dir `~/.claude/plans` [empty],
all archetypes blank, branch.base `origin/main`, quality.* code-health tools blank, coverage_floor
blank). Stated per skill requirement.

=== PHASE 1: STRUCTURAL DRIFT ===
REFERENCE: NONE — no R1 archetype configured (`plans.archetypes.R1` blank) and `~/.claude/plans` is
empty. 1b: running section-presence + series-gap checks against the canonical list only, no reference
diff. No substantive-loss diff is produced (no reference available).

SECTION-PRESENCE (required-at-R1 set):
- Present: §1 Context, §2 Verified state, §5 Memory refs, §6 Scope, §7 Locked decisions,
  §9 Sequenced commits, §10 Critical files, §11 Reused utilities, §14 Acceptance criteria,
  §15 Risks+stop conditions, §19 PR sequence, §20 After-merge handoff.
- Missing required at R1:
  - §10 lacks an explicit `UNTOUCHED (explicitly out of scope)` sub-section. The canonical §10 row
    (NEW / MOD / **UNTOUCHED**) is required at R1+. §6 lists out-of-scope files, which partly covers
    it, but §10's critical-files table lists only touched files — the structural primitive that pins
    untouched files during execution is absent from §10. FLAG (minor; structural).
- Extra non-canonical: none.
- Out-of-order: none (ascending; R2+ sections correctly omitted at R1).
- §7 decisions are not D-numbered and carry no explicit operator-confirmation + date. At R1 §7 is
  required; the path-fork is documented and "LOCKED", but the operator-confirmation date stamp is
  absent. FLAG (minor).

NUMBERED-SERIES GAPS:
- B-commits: B1…B5 (Commit 1–5) — clean, no gap/dup.
- D-decisions: not D-numbered (one PATH-FORK + sub-decisions 1–5) — naming drift, not a gap.
- R-risks / Q-questions: §15 risks not R-numbered; §8 Open-questions absent (not required at R1). No
  series gaps.

STREAM STRUCTURE (R3): n/a (R1).

SUBSTANTIVE LOSSES / ADDITIONS: n/a — no reference available (1b).

=== PHASE 2: PLAN-QUALITY ===

2.1 DESIGN-TESTS COVERAGE:
| File | Bug-catalog? | Plan to add? |
|---|---|---|
| `flashcore/scheduler.py` (MOD, bug site) | not present (`scheduler.py.bug-catalog.md` absent) | not planned — plan adds 2 acceptance tests only |
| `flashcore/models.py` (MOD) | not present | n/a (one-field addition) |
| `flashcore/review_processor.py` (MOD) | not present | not planned |
| `tests/test_scheduler.py` (MOD) | n/a (test file) | n/a |
FLAG: the CRITICAL bug site (`scheduler.py`) has no bug-catalog companion. Plan offers 2 acceptance
tests, not bug-catalog-first design tests. For a CRITICAL correctness finding this is a gap (non-
blocking at R1, but the two tests as written would NOT catch the core defect — see HARD STOP GT-1:
the on-time test uses `stability=1.5`, exercising the *approximation* branch, so it passes even
though the dominant production path is still approximated, not ground-truth).

2.2 TESTABILITY:
- 2.2a Verification matrix: n/a at R1 (matrix required R2+). §14 is a flat AC list — acceptable at R1.
- 2.2b Acceptance vs verification: §14 mixes outcome AC (AC-1 elapsed_days>0) with mechanical checks
  (AC-3 grep, AC-6 tests pass). Reasonably distinct. OK.
- 2.2c Test layers: Layer A (unit) present. Layer B (integration, real DB) MISSING — and this is the
  crux: the fix touches a DB-write path (review_processor → add_review_and_update_card) and the
  correct ground-truth path REQUIRES a DB read (`get_latest_review_for_card`). The plan tests only
  the in-memory scheduler with hand-built Card objects; it never exercises a card loaded from the
  real DB, which is exactly the path that is left approximated. FLAG (load-bearing — ties to GT-1).

2.3 PACKET PRE-READ: No prior AIV packet exists for these surfaces (first PR touching them in this
  stage). Code-view sufficient for all three MOD files. §10 "Read before touching" list is adequate.
  OK.

2.5 CODE-HEALTH BASELINE:
2.5 (per-file): no per-file code-health tool configured (`quality.code_health_cmd` blank) — skipped.
2.5 (change-set): no change-set code-health tool configured (`quality.code_health_changeset_cmd`
  blank) — skipped.

2.8 MEMORY COVERAGE:
| Principle | Applies | Honored? |
|---|---|---|
| Never merge autonomously; human is merge gate | yes | YES (§5, §19, §15 RED) |
| Author packets to shape; validate via `aiv` CLI not by eye | yes | YES (§9 Commit 5, AC-8) |
| Merge by rebase, not squash | yes | NOT CITED — flag (atomic-commit plan implies it; §20 should state rebase-not-squash) |
| Run local-CI replica before every push | yes | partial — §14 AC-9 runs full suite; `ci.local_replica_cmd` unconfigured, so "full pytest" is the stand-in. OK |
| Wall-clock drill for subprocess/daemon | n/a | no subprocess/daemon touched |
| Exercise DB-write paths against the REAL database, not a surrogate | YES | **NOT HONORED** — see GT-1 / 2.2c. The plan's tests build Card objects in-memory and never exercise the real DB-write/read path. This memory principle is directly violated. |
| Behavior-pinning tests + green existing tests for refactor | yes (15 existing must stay green) | YES (§15, AC-6) |
FLAG: "real-DB for DB-write paths" principle uncited and violated.

=== PHASE 3: PLAN-GRAPH + TEMPORAL (R1 → 3.1, 3.5) ===

3.1 BASE-SHA DRIFT: Plan declares base `origin/main @ b5e1c4b`; current `origin/main` == b5e1c4b →
  0 commits drift. Risk: LOW. (Working branch is `feat/c2-fsrs-harness`, not the plan's declared
  `feat/c2-pr-f169-fsrs-elapsed-days-b1` — branch-name MISMATCH; reconcile §1/§19 before VERIFY [9]
  / before opening the PR. Not a hard stop, but VERIFY [9]/[10] will fail against the wrong name.)

3.5 STOP CONDITIONS (RED): §15 declares RED stop conditions with escalation actions (edit-existing-
  test → stop & determine which side is wrong; mypy new error → escalate; aiv check non-zero after 2
  attempts; persistence-doubt → escalate as scope-widen to R2). Thresholds + actions present. PASS.

=== GROUND-TRUTH-OVER-APPROXIMATION GATE (task-mandated) ===

**HARD STOP — GT-1 (ground-truth-over-approximation violation).**

The plan's locked Path A (§7 sub-decision 2 + §9 Commit 2) replaces the wrong `last_review = due`
proxy with:
```
elif card.stability is not None:
    fsrs_card.last_review = fsrs_card.due - timedelta(days=max(1, round(card.stability)))
```
i.e. it APPROXIMATES the prior-review date from stability for any card whose `last_review_date` is
None. `last_review_date` is set ONLY for same-session re-reviews (§9 Commit 3 sets it on the object
returned by `add_review_and_update_card`). For the **production-dominant path** — a card loaded fresh
from the DB and reviewed — `last_review_date` is None, so every such review uses the stability
approximation.

But the ACTUAL prior-review timestamp is RECORDED and RETRIEVABLE:
- `cards.last_review_id` (models.py:57 `Card.last_review_id`; schema.py:16) points at the most-recent
  review row.
- `reviews.ts TIMESTAMP WITH TIME ZONE NOT NULL` (schema.py:39) is the exact prior-review timestamp.
- An EXISTING data-access method already returns it:
  `db_manager.get_latest_review_for_card(card_uuid) -> Optional[Review]`
  (flashcore/db/database.py:836; built on `get_reviews_for_card(..., order_by_ts_desc=True)`,
  database.py:788). `Review.ts` is the ground-truth date.

§1 correctly names the root cause ("no prior-review timestamp exists on the Card model… forced to use
`due` as a proxy"). Path A as planned removes the `due` proxy for same-session cards but SUBSTITUTES A
SECOND APPROXIMATION (stability) for the fresh-from-DB case instead of consuming the recorded value.
The hub (review_processor) has the db_manager handle and can call `get_latest_review_for_card(
card.uuid)` to populate `last_review_date` from `reviews.ts` BEFORE calling `compute_next_state`,
giving the scheduler ground-truth on the common path. The plan never does this.

Per the pipeline ground-truth gate ("before deriving/estimating ANY value, check whether the real
value is already recorded or retrievable; if it is, consume it — never approximate what you can look
up"), approximating elapsed_days from stability while `reviews.ts` is sitting in the DB behind an
existing accessor is a gate violation, not a design preference. The stability fallback is acceptable
ONLY as a last resort for a card that genuinely has no prior review row (`last_review_id is None` and
`get_latest_review_for_card` returns None) — never as the default for fresh-from-DB cards.

Required correction (does NOT widen to R2 — uses the existing read, no migration):
- In `review_processor` (hub), before/around `compute_next_state`, when `card.last_review_date is
  None and card.last_review_id is not None`, set `card.last_review_date =
  db_manager.get_latest_review_for_card(card.uuid).ts.date()` (ground-truth). Keep the stability
  approximation in the scheduler strictly as the no-prior-review fallback.
- Add the missing Layer-B integration test (real DB): persist a review, reload the card from DB,
  re-review on its due date, assert `elapsed_days_at_review` reflects the true gap (> 0 and equal to
  the recorded `reviews.ts` delta), not `round(stability)`. The current AC-1 test (stability=1.5,
  in-memory) exercises only the approximation branch and would pass against the defective design.

This blocks B0.

=== OVERALL VERDICT ===
Plan structural integrity: FAIL — §10 UNTOUCHED sub-section missing (required R1+); §7 decisions not
  operator-confirmed/dated.
Plan quality audit: FAIL — ground-truth gate violation (GT-1); DB-write path not exercised against
  real DB (2.2c / 2.8); CRITICAL bug site has no bug-catalog and the proposed acceptance test does
  not cover the dominant (approximated) path (2.1).
Plan-graph readiness: PASS — for the R1 phase-3 checks run (3.1 base-SHA drift 0 = LOW; 3.5 RED stop
  conditions present). Branch-name mismatch noted as a reconcile item, not a gate failure.
HARD STOPS:
  - GT-1 (ground-truth-over-approximation, gate): plan approximates prior-review date via
    `max(1, round(stability))` for fresh-from-DB cards while `reviews.ts` is recorded and retrievable
    via `card.last_review_id` / `get_latest_review_for_card` (database.py:836). Blocks B0.
Recommended next action: revise §7/§9 — populate `last_review_date` from the recorded `reviews.ts`
  (via `get_latest_review_for_card`) in the hub for fresh-from-DB cards; demote the stability formula
  to a no-prior-review fallback only; add a real-DB Layer-B integration test for the on-time path;
  add §10 UNTOUCHED sub-section; reconcile the declared branch name. Then re-run check-drift.

=== SURVIVORSHIP-BIAS DISCLOSURE ===
This template is induced from the project's own plan corpus (`plans.dir`), weighted toward plans that
shipped — a survivorship sample telling you what merged plans happened to contain, NOT what plans
need to succeed. Here the corpus is empty (`~/.claude/plans` absent/empty; no archetypes configured),
so Phase 1 ran section-presence + series-gap against the canonical list only — no reference diff, no
calibration to a surviving sample. A clean structural pass would mean "matches the canonical list",
not "cannot fail". Sections marked OPTIONAL are observed-rare-but-load-bearing; sections not in the
template may still be load-bearing for failure modes not yet seen. Promotion criterion for any new
template section: name the specific failure mode it would have prevented. NOTE: GT-1 is a failure
mode (silent approximation of a recorded value) that pure structural matching would NOT have caught —
it required reading the schema + data-access layer, not the plan's section list.

## Machine-checkable data

```json
{
  "schema": "check_drift_verdict@1",
  "r_tier": "R1",
  "audit_depth_complete": true,
  "structural_integrity": "fail",
  "plan_quality": "fail",
  "plan_graph": "pass",
  "hard_stops": [
    {
      "id": "GT-1",
      "phase": "ground-truth-gate",
      "detail": "Plan approximates prior-review date via max(1, round(card.stability)) for fresh-from-DB cards (production-dominant path), but the actual prior-review timestamp is recorded in reviews.ts (schema.py:39) and retrievable via card.last_review_id (models.py:57) using the existing accessor db_manager.get_latest_review_for_card (flashcore/db/database.py:836). Hub must consume the recorded value, not approximate. Blocks B0."
    }
  ],
  "open_substantive_losses": 0,
  "iteration": 4
}
```
