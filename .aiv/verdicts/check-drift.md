# check-drift audit — Plan: Fix F169 (FSRS on-time elapsed_days)

Plan audited: `.aiv/plans/c2-f169-plan.md`
Config: **no `.aiv-workflow.yml`** at repo root (and `$AIV_WORKFLOW_CONFIG` empty) — all values are skill
defaults; `plans.archetypes.*`, `quality.code_health_*`, `quality.coverage_floor`, `memory.*` all blank.

=== PHASE 0: R-TIER ===
Declared: **R1** (plan line 8)
Inferred: **R1** (basis: 4 atomic commits; 3 source files MOD [`models.py`, `scheduler.py`,
`review_processor.py`] + 1 test file; 0 migrations; 0 new data-access methods — Commit 3 *consumes*
the pre-existing `db.get_latest_review_for_card`; transient `exclude=True` field, no persistence)
Reconciled: **R1** (no mismatch). Caveat: the change spans 3 subsystems (model + hub + scheduler);
that touches the R2 boundary, but with no migration / no new DB method / no new dispatcher it stays R1.
Audit depth (R1): Phase 1 full; Phase 2 = 2.1, 2.2, 2.3, 2.5, 2.8; Phase 3 = 3.1, 3.5.

=== PHASE 1: STRUCTURAL DRIFT ===
REFERENCE: **NONE** — `1b: no R1 archetype configured (plans.archetypes.R1 blank, no config file) —
running section-presence + series-gap checks against the canonical list only, no reference diff.`

SECTION-PRESENCE (required-at-R1 checked):
- §1 Context: PRESENT (finding statement + Goal in brief mirror; plan opens with finding/line cite).
- §2 Verified state (N Explore agents, YYYY-MM-DD): **MISSING** — the brief says "verify each yourself"
  but the plan records no verified-state block with agent count + date.
- §5 Memory + lesson references: **MISSING** in plan (no memory store loaded → see 2.8 for the universal
  principles check that substitutes).
- §6 Strict scope boundaries (IN/OUT): PRESENT (OUT = "Scope guard — out of this PR" table with
  follow-up dispositions; IN = "Files touched" table). No explicit "does NOT do" philosophical line.
- §7 Locked design decisions (D-numbered, operator-confirmed + date): **PARTIAL** — "Path decision:
  Option A" with a rationale is present, but it is **not D-numbered** and carries **no operator-confirmed
  date**. The brief flags Option A as a path-fork requiring operator sign-off before widening to
  `review_processor.py`; the plan asserts the choice without recording confirmation.
- §9 Sequenced atomic-commit plan (B0…Bn): PRESENT (Commit 1–4, ordered, one file each). Naming is
  "Commit N" not "Bn" — cosmetic.
- §10 Critical files (NEW/MOD/UNTOUCHED): **PARTIAL** — MOD table present; **no UNTOUCHED sub-section**
  (also flagged at 3.9).
- §11 Reused utilities (must consume, not reimplement) [literal phrase]: **MISSING** — the plan notes
  `get_latest_review_for_card` "already exists" inline but has no "Reused utilities" section. Verified:
  the method does exist at `flashcore/db/database.py:834` returning `Optional[Review]`.
- §14 Acceptance criteria (outcome-shaped): PRESENT (two named acceptance tests + "Test layers" table).
- §15 Risks + mitigations + stop conditions (RED): **MISSING** — no risk register, no RED stop
  conditions in the plan (the iter budget lives in the brief, not the plan).
- §19 Locked PR sequence position: **PARTIAL** — successors named in scope-guard (backfill / DB-migration
  follow-ups) but no explicit predecessor / parallel-safe-with declaration.
- §20 After-merge handoff: **MISSING** in plan (POST-MERGE bookkeeping lives in the completion contract,
  not the plan; task-tracker row / memory writes not carried into the plan).
- Extra non-canonical: "E010 / packet hygiene notes" (useful, project-specific) — not a defect.
- Out-of-order: n/a (plan is not numbered to the canonical scheme).

NUMBERED-SERIES GAPS:
- Commit-series: Commit 1→4 contiguous, no gaps/dupes. CLEAN.
- D-decisions: none numbered (single unnumbered path decision) — see §7 flag.
- R-risks / Q-questions: none present (see §15 flag; no §8 open-questions section).

STREAM STRUCTURE (R3): n/a (R1).

SUBSTANTIVE LOSSES / ADDITIONS: not computed — no reference configured (1b).

=== PHASE 2: PLAN-QUALITY ===

2.1 DESIGN-TESTS COVERAGE:
| File | Bug-catalog? | Plan to add? |
|---|---|---|
| `flashcore/models.py` | not present (`models.py.bug-catalog.md` absent) | MISSING — not planned |
| `flashcore/scheduler.py` | not present | MISSING — relies on 2 pytest acceptance tests |
| `flashcore/review_processor.py` | not present | MISSING — **no test at all** (see 2.2c) |
FLAG: bug-catalog-first standard not met. The two new pytest tests are acceptance-shaped (good) but are
not a substitute for a bug catalog, and they do not cover the processor plumbing.

2.2a VERIFICATION MATRIX: n/a (R2+ when criteria>3; R1 here).
2.2b ACCEPTANCE vs VERIFICATION: **distinct** — acceptance = `elapsed_days>0` and `stab` differs (two
named tests); verification = regression suite / mypy / `aiv check`. Not collapsed.
2.2c TEST LAYERS (advisory at R1):
- Layer A unit: PRESENT (the two new scheduler tests).
- Layer B integration: **MISSING — and load-bearing.** Commit 3 adds a DB-read on the hot path
  (`db_manager.get_latest_review_for_card(card.uuid)` → `card.last_review_date = prior_review.ts.date()`).
  This is the *novel Option-A plumbing* and the part most likely to be wrong, yet **no test exercises
  `review_processor.process_review` end-to-end**. Both new tests set `card.last_review_date` by hand and
  call the scheduler directly — they would pass even if Commit 3 were never written. The fix can be
  "green" in tests while the real review path stays broken. This is the single most important finding.
- Layer C E2E: n/a (no UI/route/auth).
- Layer D coverage ratchet: `quality.coverage_floor` blank — no numeric target; functional LOC is added,
  so a ratchet layer *should* at least be named. Not declared.
- Layer E local-CI replica: PRESENT (full-suite layer + contract [10]).
- Layer F operator drill: n/a (no subprocess/daemon).

2.3 PACKET PRE-READ: none cited. The change touches `review_processor` / scheduler surfaces; no prior
AIV packet pre-read is named. Minor at R1, but the processor write-path has prior packets worth citing.

2.4 AUTOMATE-OVER-OPERATOR (advisory): the path-fork (Option A) and code-review read are routed to
operator AskUserQuestion in the brief — acceptable (genuine design + review gates). No mechanical
operator-only step that has a code path is parked on the human. OK.

2.5 CODE-HEALTH BASELINE:
- `2.5: no per-file code-health tool configured (quality.code_health_cmd blank) — skipped.`
- `2.5: no change-set code-health tool configured (quality.code_health_changeset_cmd blank) — skipped.`

2.6 FAN-OUT TRIGGER: n/a at R1 audit depth. (Were it run: borderline-NO — 3 files but one subsystem
chain, claims already cross-checked in this audit against the live code.)

2.7 CODE-REVIEW RESILIENCE: n/a at R1 (no prior automated-review contact established).

2.8 MEMORY COVERAGE (no memory store; universal-principles substitute):
| Principle | Applies? | Honored? |
|---|---|---|
| Never merge autonomously; human is merge gate | yes | yes (contract PRE-MERGE AskUserQuestion) |
| Author packets to shape; validate via `aiv` CLI | yes | yes (AIV commit sequence + `aiv check`) |
| Merge by rebase, not squash | yes | not stated in plan (brief sets merge.strategy=rebase) — soft |
| Run local-CI replica before every push | yes | yes (full-suite layer + contract [10]) |
| Wall-clock e2e drill for subprocess/daemon | n/a | — |
| **Exercise DB-write/read paths against the real DB, not a surrogate** | **yes** | **NO** — Commit 3's DB read is never exercised against the DB (ties to 2.2c Layer B) |
| Behavior-pinning + green existing tests for refactor | partial (not a refactor; regression required) | yes (15 existing tests must stay green) |

=== PHASE 3: PLAN-GRAPH + TEMPORAL (R>=2 sections; R1 runs 3.1, 3.5) ===

3.1 BASE-SHA DRIFT: **base SHA not pinned in the plan.** Plan declares "off `origin/main`" but carries no
§0 metadata base-SHA. Finding header cites base `origin/main @ b5e1c4b`; current worktree branch
`feat/c2-fsrs-harness @ 311e046`; the plan's target branch `feat/c2-pr-f169-fsrs-elapsed-days-b1` does
not yet exist. Risk: **low** (fresh branch, no drift to measure) — but pin the base SHA in §0 before B0.

3.5 STOP CONDITIONS (RED): **MISSING.** No risk has a RED threshold (LOC drift %, iter cap, CI-fail
pattern, wall-clock cap) or escalation action in the plan. The brief carries a 2-cycle iter budget with
one escalation trigger; the plan does not carry it. Flag: add stop conditions / iter budget to the plan.

=== OVERALL VERDICT ===
Plan structural integrity: **fail** — multiple required-at-R1 sections missing (§2 verified-state,
§11 reused-utilities, §15 risks/RED-stop-conditions, §20 after-merge) and §7/§10 partial (path decision
not D-numbered/operator-dated; no UNTOUCHED sub-section).
Plan quality audit: **partial** — the scheduler fix and acceptance gates are sound and well-specified,
BUT (a) the Option-A processor plumbing (Commit 3) has zero test coverage — the two new tests pass
without it; (b) Commit 4's test code references a `make_review_card(...)` helper that **does not exist**
in `tests/test_scheduler.py` (verified: no `def make_review_card`); (c) the test code uses bare
`date`/`timedelta`/`time`/`timezone`/`date.today()`/`UTC` while the file imports `import datetime`
(module form) and accesses `datetime.date(...)` — the plan's claim that "`date`/`timedelta` imports
should already be present" is false and the tests would `NameError` as written; (d) no bug-catalog.
Plan-graph readiness: **partial** — base SHA unpinned (low risk) and RED stop conditions absent.

HARD STOPS:
- **H-A (phase 2.2c / 2.8):** Acceptance gates [1]/[2] cannot be trusted to validate the fix — both new
  tests bypass `review_processor` (Commit 3) entirely, so a fully green test run does not prove the
  on-time review path is fixed. Add a Layer-B test that drives `process_review` and asserts the persisted
  `elapsed_days_at_review > 0`.
- **H-B (phase 2.1 / Commit 4):** Commit 4's tests are written against a non-existent `make_review_card`
  helper and bare datetime names not imported in the file; as written they fail to collect/run, so the
  acceptance commands in the completion contract cannot pass. Resolve before B0 (create the helper +
  correct imports, or rewrite the tests against the existing `Card(...)` + `scheduler` fixture pattern).

Recommended next action: revise the plan before exiting plan mode — (1) add the missing §2/§11/§15/§20
sections, D-number + operator-date the Option-A decision, add the §10 UNTOUCHED list; (2) add a Commit
covering `review_processor` population against a real/seeded DB (Layer B); (3) fix Commit 4's test code
(non-existent helper + import names) so acceptance [1]/[2] actually run; (4) pin the base SHA and add RED
stop conditions / the 2-cycle iter budget into the plan.

=== SURVIVORSHIP-BIAS DISCLOSURE ===
This template is induced from the project's own plan corpus (plans.dir), weighted toward plans that
shipped — a survivorship sample. It tells you what merged plans happened to contain, not what plans need
to succeed. No archetype/config was available this run, so structural drift was section-presence-only
against the canonical list (no reference diff). A clean structural pass would mean "matches the surviving
corpus," not "cannot fail"; this plan did not pass. Sections marked OPTIONAL are observed-rare-but-
load-bearing; the load-bearing gap here (untested Option-A plumbing) is a quality failure mode the bare
section-presence check would have missed — it was caught by Phase 2.2c, which is why Phase 2 is not
skippable.

## Machine-checkable data

```json
{
  "schema": "check_drift_verdict@1",
  "r_tier": "R1",
  "audit_depth_complete": true,
  "structural_integrity": "fail",
  "plan_quality": "partial",
  "plan_graph": "partial",
  "hard_stops": [
    {"id": "H-A", "phase": "2.2c", "detail": "Acceptance tests [1]/[2] bypass review_processor (Commit 3); a green run does not prove the on-time path is fixed — no Layer-B/integration test drives process_review against the DB."},
    {"id": "H-B", "phase": "2.1", "detail": "Commit 4 tests reference a non-existent make_review_card helper and use bare datetime names (date/timedelta/time/timezone/UTC) not imported in tests/test_scheduler.py; tests fail to run, so acceptance commands cannot pass."}
  ],
  "open_substantive_losses": 0,
  "iteration": 1
}
```
