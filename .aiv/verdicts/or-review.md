# 🔬 Orchestrator Review — PR (F169 / C2) — Round 1

**Verdict: ⚠️ WARN** — the substantive fix is correct and fully verified by live-fire
behavioral evidence; the WARN is driven by one non-load-bearing contract deviation ([9]
commit-author identity + branch-name) and one human-gate item pending operator confirmation
([12] review quiet window). No load-bearing claim falsified; no commit-hook bypass; no
unexplained patch.

- **Mode:** STRICT — human-written contract found at
  `.aiv/launch-briefs/pr-f169-fsrs-elapsed-days/pr-f169-fsrs-elapsed-days-completion-contract.md`
  (13 items). Read verbatim; not derived.
- **Head SHA:** `57af6d0fd350a82ece4cc0f8abdc8262923bd45f` · **Branch:** `feat/c2-fsrs-harness`
- **Config:** no `.aiv-workflow.yml` present → defaults used (`aiv` CLI, packets dir
  `.github/aiv-packets`, contracts dir `.aiv/launch-briefs`, `merge.strategy=rebase`).
  `review.coord_file` unbound → coord-file sub-check dropped (one-line note only).
- **Path fork resolved:** **Option A** (transient `last_review_date` on `Card` model, plumbed
  by the hub) — locked in plan §D1 with one-sentence rationale; Option B (scheduler-only
  stability approximation) explicitly rejected and absent from the diff.

> Read-only review. `gh` unavailable in this worktree → this verdict is written to
> `.aiv/verdicts/or-review.md` instead of being posted as a PR comment. No merge, no commit,
> no test-suite execution beyond targeted static probes.

---

## Contract items (11/13 verified, 0 falsified, 2 open)

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 1 | On-time review → `elapsed_days > 0` | ✅ VERIFIED | `head_green.txt`: `test_on_time_review_elapsed_days_positive PASSED`; `head_direct_probe.txt`: `elapsed_days = 14` |
| 2 | On-time vs same-day stability distinct | ✅ VERIFIED | `head_green.txt`: `test_on_time_vs_same_day_review_stability_distinct PASSED`; direct probe HEAD `stability=44.8064` vs baseline `14.0000` |
| 3 | Path decision documented + implemented (fork) | ✅ VERIFIED | Plan §D1 "LOCKED: Path A" + rationale; my grep: `last_review_date` in models.py:61 / review_processor.py:104 / scheduler.py:211; Option-B regex → no output |
| 4 | Learning-state guard correct (no None arithmetic) | ✅ VERIFIED | New-card branch guarded by `if card.state != CardState.New`; `test_first_review_new_card PASSED` (`head_full_scheduler.txt`); bug-catalog "None-stability arithmetic guard" entry |
| 5 | No regression — 15 existing scheduler tests pass | ✅ VERIFIED | `head_full_scheduler.txt`: **17 passed** (15 existing + 2 new) |
| 6 | Bug site replaced (`last_review = fsrs_card.due` gone) | ✅ VERIFIED | My grep `grep -n "last_review = fsrs_card.due" flashcore/scheduler.py` → no output (exit 1) |
| 7 | Typecheck clean on touched files | ✅ VERIFIED | My run: `mypy flashcore/scheduler.py flashcore/models.py` → **Success: no issues found in 2 source files**. Pre-existing `bleach`/`yaml` stub errors (`mypy_clean.txt`) are in untouched files |
| 8 | Packet validates (`aiv check`) | ✅ VERIFIED | `aiv check` on all 5 `PACKET_c2_f169_*.md` → **0 blocking errors** each (warnings only, exit 0). Warnings are E004 (Class-E plain-text ref) — informational per project memory. *Naming note: contract referenced a single `PACKET_f169-fsrs-elapsed-days.md`; the change shipped as 5 split packets — all pass.* |
| 9 | No attribution / branch shape correct | ⚠️ PARTIAL | `Co-Authored-By` tag is **explicitly allowed** by contract [9] ("present if pair-authored") ✅. **But:** (a) commit author is `Claude <noreply@anthropic.com>` — contract [9] literally reads "no commit author is an AI agent"; (b) branch is `feat/c2-fsrs-harness`, not the contract's `feat/c2-pr-f169-fsrs-elapsed-days-b1`. See discrepancies below. |
| 10 | Local CI passes | ✅ VERIFIED | `full_suite_head.txt`: **483 passed, 1 skipped** (baseline 480 + 3 new tests); CI green (14 checks) per operator context |
| 11 | Progress-tracker closure | ✅ VERIFIED | `.taskmaster/tasks/task_008.md:58`: "F169 — FSRS elapsed_days=0 for on-time reviews (ADDRESSED, 2026-06-19)" |
| 12 | Review quiet window | 🟡 OPEN (human gate) | CodeRabbit status = success, 0 unresolved actionable (operator context). Reviewer has read the full diff. Final operator `AskUserQuestion` confirmation is the human merge gate — cannot be machine-closed here. |
| 13 | Finding closed | ✅ VERIFIED | Closure recorded in `task_008.md` (F169 ADDRESSED). The contract's `artifacts/`/`audit/` grep targets don't exist in this worktree; closure is recorded in the progress tracker instead, which the contract accepts as an equivalent. |

`N = 13` counted from `^\[[0-9]+\]` items in the contract (no skipped numbers).

---

## Per-angle findings

**1 — Contract conformance.** 11/13 items verified against ground truth; the two open items are
a non-load-bearing provenance/branch-shape deviation ([9]) and a human-gate operator
confirmation ([12]). The load-bearing correctness items [1]–[7] are all green with independent
re-execution or evidence cross-check.

**2 — Fix correctness / root cause.** The root cause is fixed at its source, not symptomatically:
`scheduler.py:211-217` now derives `last_review` from `card.last_review_date` (ground-truth prior
review date) and leaves `last_review` unset only for genuinely first-ever reviews — replacing the
`last_review = fsrs_card.due` proxy that pinned `elapsed_days=0`. The new block sits at the correct
indent (inside `if card.state != CardState.New`, outside the `next_due_date` block), so the
elapsed-days computation at `:223-229` reads the right anchor. Direct probe confirms behavioral
delta: baseline `elapsed_days=0, stability=14.0` → HEAD `elapsed_days=14, stability=44.8064`.

**3 — Ground-truth plumbing (hub-and-spoke).** Option A respects the architecture: the spoke
(`scheduler.py`) stays pure (no DB handle, no new import — confirmed Class C), and the hub
(`review_processor.py:99-104`) consumes the DB-recorded value via
`get_latest_review_for_card` (verified to exist at `flashcore/db/database.py:834`) before
`compute_next_state`. The `isinstance(prior_review, Review)` guard (`:103`) correctly prevents
test-double mocks from triggering Pydantic validation. This consumes the recorded value rather
than approximating it — consistent with the project's ground-truth-over-approximation discipline.

**4 — Evidence quality (live-fire).** This is the strength of the change: a Layer-B integration
test (`test_on_time_review_persists_positive_elapsed_days`) drives a **real in-memory DB + real
scheduler** end-to-end and asserts the persisted `elapsed_days_at_review > 0`
(`layerb_integration.txt` PASSED) — infra-boundary validation, not unit tests alone. A
baseline-vs-HEAD direct probe demonstrates the bug present at base and absent at HEAD. The
oracle-corrections record (`.aiv/oracle-corrections/c2-f169-impl.md`) justifies each pre-existing
test-setup edit independently of the implementation (old oracle relied on the buggy due-date
proxy) — clean oracle-guard discipline.

**5 — Scope / deferrals.** Deferrals are explicitly classified, not silently dropped: the
bug-catalog "Skipped" set (`tests/test_scheduler.bug-catalog.md` §3) records B2 (negative
`elapsed_days` for *early* reviews → new finding **F169b**, deferred to stage-c2 audit), B3
(CardState/FSRSState parity), and B4 (cosmetic). These match the contract's OUT-OF-SCOPE
reminders and are architectural-correctness/nice-to-have, not primary-deliverable dependencies —
appropriate to defer. The `pyproject.toml` tool-version pins (commit `9bbb2ec`) are explained by
the CI packet (deterministic lint gate across platforms) and corroborated by the full-suite
recovery from "467 passed, 16 collection errors" in the early impl packet to "483 passed, 1
skipped" at HEAD — i.e. not an unexplained patch.

---

## Verification claims (4a–4c) — adversarial probes I ran myself

| # | Load-bearing claim | Probe | Result |
|---|--------------------|-------|--------|
| C1 | Bug line `last_review = fsrs_card.due` removed | `grep -n` on scheduler.py | **VERIFIED** — no output (exit 1) |
| C2 | Option A in all 3 files; Option B absent | `grep -n last_review_date` ×3; Option-B regex | **VERIFIED** — present in models/review_processor/scheduler; B regex no output |
| C3 | `get_latest_review_for_card` is a real hub method (not a stub) | `grep -rn "def get_latest_review_for_card"` | **VERIFIED** — `flashcore/db/database.py:834` |
| C4 | mypy clean on touched files | ran `mypy scheduler.py models.py --ignore-missing-imports` | **VERIFIED** — "Success: no issues found in 2 source files" |
| C5 | All 5 packets pass `aiv check` with 0 blocking errors | ran `aiv check` ×5 | **VERIFIED** — 0 blocking errors each (warnings only, exit 0) |
| C6 | F169 marked closed in tracker | `grep -rn F169 .taskmaster/tasks/` | **VERIFIED** — `task_008.md:58` "(ADDRESSED, 2026-06-19)" |
| C7 | No `--no-verify` / `--amend` / hook bypass on the branch | `git log origin/main..HEAD -B` scan | **VERIFIED** — none found |
| C8 | New-card path has no None-stability arithmetic | code read `:200/:223-229` + bug-catalog | **VERIFIED** — guarded by `state != CardState.New` |

0 of 8 load-bearing claims falsified.

---

## Discrepancies (transparency — operator decides)

1. **[9] Commit author identity vs contract text.** Every branch commit is authored by
   `Claude <noreply@anthropic.com>` with `Co-Authored-By: Claude Sonnet 4.6` trailers. Contract
   [9] permits the `Co-Authored-By` tag ("present if pair-authored") but also says "no commit
   author is an AI agent." **Why I did NOT trip the skill's attribution stop-condition / FAIL:**
   the governing STRICT contract explicitly sanctions the tag, and the project's own `CLAUDE.md`
   *mandates* ending every commit with a `Co-Authored-By: Claude …` + `Claude-Session:` trailer —
   so this is disclosed, project-mandated convention, not undisclosed agent attribution sneaking
   toward a merge. There is no deception. I flag it because the literal "no commit author is an
   AI agent" clause is in tension with the de-facto pipeline convention; the operator should
   confirm this is the intended committer identity. *(Side note: trailers say "Opus 4.8" in
   CLAUDE.md vs "Sonnet 4.6" in the commits — cosmetic, immaterial.)*
2. **[9] Branch name.** Contract [9] expects `feat/c2-pr-f169-fsrs-elapsed-days-b1`; the actual
   branch is `feat/c2-fsrs-harness`. The finding header itself authorizes `feat/c2-fsrs-harness`,
   so this is operator-known, but it diverges from the contract's literal acceptance string.
3. **[8] Packet naming.** Contract names one packet (`PACKET_f169-fsrs-elapsed-days.md`); the
   change shipped 5 split packets (`PACKET_c2_f169_{impl,tests,ci,determinism,oracle_corr}.md`).
   All validate. Non-blocking; noted for the contract-to-artifact mapping.
4. **AIV class coverage (process, non-blocking).** The narrow R0 `oracle_corr` packet carries only
   Class B + E and omits A/C/D/F without explicit `N/A` markers (operator mandate #9 asks for an
   `N/A — reason` stub rather than silent omission). All six classes A–F are present and
   substantive across the packet set as a whole (notably the `impl` packet). `aiv check` reports 0
   blocking errors, so this is a discipline nit, not a gate failure. Several packets also leave
   `classification_rationale: "TODO: …"` placeholders.

---

## Recommendation

The F169 fix is **substantively correct, root-caused, and backed by live-fire evidence** (Layer-B
DB integration test + baseline/HEAD behavioral probe + 17/17 scheduler + 483/483 suite + clean
mypy + 5 clean packets). It is **not blocked** by any falsified claim, hook bypass, or unexplained
patch. Before merge the operator should: (a) confirm the **[9] committer-identity / branch-name**
deviations are acceptable under project convention (they appear to be, given `CLAUDE.md`); and
(b) answer the **[12]** pre-merge `AskUserQuestion` (full diff read + no blocking comments —
CodeRabbit already reports success, 0 unresolved). Human owns the merge gate; rebase strategy per
defaults. **WARN, not PASS**, solely because [9] and [12] remain operator-side; **WARN, not
FAIL**, because nothing load-bearing is broken.

---

## Machine-checkable data

```json or_review_verdict
{
  "round": 1,
  "head_ref_oid": "57af6d0fd350a82ece4cc0f8abdc8262923bd45f",
  "verdict": "WARN",
  "contract_total": 13,
  "contract_verified": 11,
  "falsified_load_bearing": 0,
  "unverified": 2,
  "stop_condition_tripped": "none",
  "coderabbit_actionable": 0,
  "aiv_classes_present": ["A", "B", "C", "D", "E", "F"],
  "aiv_classes_vacuous": []
}
```
