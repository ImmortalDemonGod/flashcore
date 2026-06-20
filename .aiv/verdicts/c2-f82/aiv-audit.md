# AIV spec audit — c2-f82 (content audit; follow-up to shape review)

Shape (`aiv check --strict --audit-links`) was verified separately and is reported below.
This audit verifies packet **content** against the canonical spec at
`/home/user/aiv-protocol/SPECIFICATION.md` (`AIV-SPEC-V1.0.0-CANONICAL`, v1.0.0).

> **Config note.** No `.aiv-workflow.yml` at the repo root; skill defaults applied
> (`evidence.mandate_all_classes=true`, `evidence.exclude_classes=[G]`, `branch.base=origin/main`).
> Spec resolved to `/home/user/aiv-protocol/SPECIFICATION.md` (the repo-root default
> `aiv-protocol/SPECIFICATION.md` does not exist under the flashcore checkout). `gh` is
> **unavailable** — no PR comment posted; this audit is written to
> `.aiv/verdicts/c2-f82/aiv-audit.md` per stage contract.

**Scope sampled (all 5 F82 packets):** `PACKET_c2_f82_impl.md` (functional core),
`PACKET_c2_f82_tests.md` (RED tests + bug catalog), `PACKET_c2_f82_ci.md` (R0 black reformat),
`PACKET_c2_f82_crv.md` (coverage follow-up), `PACKET_c2_f82_crv2.md` (stats-correction follow-up).

**Headline:** All five packets carry the **correct canonical Class E intent target** and a
**concrete, accurate intent-alignment assessment**; no evidence class is vacuous; the behavioral
substrate (baseline-RED / head-GREEN) is genuine and its sha256 manifest **verifies**. The only
spec deviations are the project-wide **Class A immutable-CI-reference** gap (A-001/A-002 — WARN per
the project's enforced gate, mitigated by a verified hash manifest) and a cosmetic `Repository`
metadata error. **No blocking findings → PR is READY for human adjudication.** Decision:
**CONDITIONAL** (clean on every load-bearing dimension; two non-blocking WARNs recorded for H2).

---

## Shape check (`aiv check`) — recorded, not re-derived

| Packet | Blocking errors | Warnings | Notes |
|---|---|---|---|
| `PACKET_c2_f82_impl.md`  | **0** | 9 | E016 (Class B per-claim anchor suggestions ×8), E004 (Class E plain-text — informational per CLAUDE.md) |
| `PACKET_c2_f82_tests.md` | **0** | 5 | E011 (Class F justification suggestion), E016 ×2, E012, E004 |
| `PACKET_c2_f82_ci.md`    | **0** | 2 | E012 (Class A is text not CI link — **WARN**), E004 |
| `PACKET_c2_f82_crv.md`   | **0** | 1 | E012 (Class A text not CI link — **WARN**) |
| `PACKET_c2_f82_crv2.md`  | **0** | 1 | E012 (Class A text not CI link — **WARN**) |

All packets report **0 blocking error(s)**. (`aiv check` prints "Validation Failed" whenever any
warning exists; the load-bearing signal is the blocking-error count, which is zero everywhere.)
→ `shape_check_passed = true`.

---

## Finding 1 (LOAD-BEARING) — Class E intent-target correctness: **PASS** (no finding)

Per spec §6.6.2 the requirement reference MUST be immutable; per the stage contract every packet's
Class E MUST point to the **original audit source** that produced finding F82 — the canonical URL
`https://github.com/ImmortalDemonGod/flashcore/blob/5bb2ea2ab72239e0d2de7cc51fd4b5b766e44bfb/audit/02-static-audit.md#L92`.

| Packet | Class E target location | Correct canonical audit source? |
|---|---|---|
| impl  | L137 — `…/5bb2ea2ab72239e0d2de7cc51fd4b5b766e44bfb/audit/02-static-audit.md#L92` | ✓ exact match |
| tests | L95  — same canonical URL | ✓ exact match |
| ci    | L114 — same canonical URL | ✓ exact match |
| crv   | L70  — same canonical URL | ✓ exact match |
| crv2  | L76  — same canonical URL | ✓ exact match |

**No packet points to a taskmaster `task_NNN.md`, `tasks.json`, or the pipeline launch-brief.** The
intent-provenance is intact and immutable (commit-SHA-pinned permalink, §3.3). The committed
`evidence/c2-f82/MANIFEST.md` `Intent:` line carries the same canonical URL. **No finding.**

---

## Finding 2 (LOAD-BEARING) — Class E intent-alignment (actual correspondence): **PASS** (no finding)

I read the cited intent source (`audit/02-static-audit.md#L92`, captured from `git diff` and the
origin/main baseline) **and** `git diff origin/main..HEAD`, and confirmed each packet's change
addresses what the source records. The source records one critical defect in `start_review_flow()`:
**B1** infinite retry (failed card never removed; `get_next_card()` always returns `review_queue[0]`);
the packets additionally decompose **B2** unconditional "Well done!" and **B3** no failure signal.

| Packet | Source records | Diff does (verified at file:line, HEAD `24a518a`) | Addresses? |
|---|---|---|---|
| impl  | B1 infinite retry; B2 false success; B3 no failure signal | `skip_card()` added `review_manager.py:156-161` and called in the except handler `review_ui.py:119` (bounds loop by queue length); counters gate the end message `review_ui.py:138-148` (suppress "Well done!" on total failure); `-> bool` `review_ui.py:70` + `return False` `:140`; `_review_logic.py:45-47` `raise typer.Exit(code=1)` on `not result` | ✓ directly addresses B1+B2+B3 |
| tests | The F82 defect (quoted verbatim in packet) | Adds bug catalog + RED tests that FAIL on baseline; `baseline_red.txt` shows all 4 RED tests fail on `5bb2ea2` with failure modes mapping to B1/B2/B3 | ✓ (design-tests stage: RED-on-baseline by contract) |
| ci    | F82 remediation pipeline (prerequisite) | `black -l 79` reformat of `review_manager.py:237-239`; zero logic change | ✓ (declared prerequisite sub-step; honest R0) |
| crv   | Coverage gap in the F82 correction (`review_ui.py:138-148` elif) | Adds `test_start_review_flow_mixed_outcome_no_well_done` exercising the `failed>0 & success>0` elif | ✓ (closes a branch introduced by the F82 fix) |
| crv2  | Stats inflation caused by the F82 `skip_card` (skipped cards counted as reviewed) | `skipped_card_count` `review_manager.py:71`; `get_session_stats` subtracts it `:237-238` | ✓ (corrects a direct consequence of the F82 fix) |

No Class E is a bare URL: every packet reads-and-maps the intent to its claims. crv/crv2 cite
*downstream-of-the-fix* intents (Codecov / CodeRabbit comments) but **anchor Class E to the same
canonical audit URL** and justify the causal link to F82 — acceptable and honest. **No finding.**

---

## Finding 3 — Vacuous / empty evidence classes (all-class mandate): **PASS** (no finding)

`evidence.mandate_all_classes=true`, `exclude=[G]`. Every packet addresses A–F; each section sampled
for substance vs. vacuity:

- **impl**: A (per-commit pytest 490-passed table + RED-gate + live-fire exit-code proof), B (21-ref
  scope inventory), C (4 enumerated negative searches + bug-catalog Skipped set), D (ruff/mypy +
  return-type analysis), E (B1/B2/B3 alignment table), F (3-file test chain-of-custody). Non-vacuous.
- **tests**: A (483P/2F RED counts), B, C (masking-test analysis), D, E, F. Non-vacuous.
- **ci**: A (`black --check` EXIT 0 + suite 493P/1S), B, C (`git diff … tests/ | wc -c` = 0), D, E,
  F (`git show --name-only`). Full A–F supplied for an R0. Non-vacuous.
- **crv**: A, B, C, D, E, F. Class C "Coverage-catalog Skipped set: **N/A — adds test coverage only;
  no production logic modified**" — a **falsifiable** N/A rationale, not an empty section. Non-vacuous.
- **crv2**: A, B, C, D, E, F. Non-vacuous.

No empty or rationale-free class. **No finding.**

---

## Finding 4 (WARN, non-blocking) — Class A immutable CI reference (A-001 / A-002 / E012)

Spec §6.2.1 requires an **immutable CI Run Reference bound to the exact `commit_sha`** (A-001 BLOCK,
A-002 BLOCK). **No F82 packet cites a CI-run permalink** — all cite **local-venv pytest runs**
(impl: "validated by `aiv commit` running the full pytest suite"; ci: inline `black/ruff/mypy/pytest`
captures; crv/crv2: inline pytest counts). `aiv check` flags this as **E012 — WARN** on the Class A
packets, i.e. the project's enforced gate treats missing-CI-link as a warning, not a blocker.

**Why this is WARN-not-BLOCK here, and not load-bearing:**
1. **Project-enforced severity is WARN** (E012), and the skill forbids escalating a WARN to a BLOCK.
2. **An immutable substrate exists and was verified by this audit.** §3.3 lists "Hash manifest —
   SHA-256 in packet + separate storage" as an *acceptable* immutability mechanism. The committed
   `evidence/c2-f82/MANIFEST.md` records sha256 for `head_green.txt` and `baseline_red.txt`; I
   recomputed both and they **MATCH** (see Harvest). So the execution evidence is content-addressed
   and immutable — the deviation is the *citation form* (inline prose vs. referencing the hashed
   artifact), not the absence of immutable evidence.
3. **A-003 is satisfied** — pass/fail/skip *counts* are present everywhere (490 passed/1 skipped;
   483 passed/2 failed; 493 passed/1 skipped), not bare "tests pass".
4. **Pre-existing, program-level pattern** — every packet in this repo uses the `aiv commit` local
   execution model (CLAUDE.md "Testing"); this is a §1.6.2 Program-scope tooling gap, not a
   per-change defect specific to F82.

**Recommendation (operator):** append the hashed evidence artifacts as the Class A immutability
mechanism, or attach a CI permalink once `gh` access is available (harvest blocked — see below).

---

## Finding 5 (WARN, non-blocking) — Identification `Repository` metadata is wrong

All five packets' Identification table reads `Repository | github.com/ImmortalDemonGod/aiv-protocol`,
but the code, the Class B permalinks (e.g. ci packet L66 `…/flashcore/blob/6d2ab98…`), and the
Class E intent URL all correctly reference **`ImmortalDemonGod/flashcore`**. The `Repository` field
is a copy-paste error. Non-load-bearing (the actual evidence URLs resolve to the correct repo) and
shape-clean, but should be corrected. Presented as a **verified fact** for operator adjudication.

---

## Claim-evidence correspondence (sampled)

| Packet · Claim | Embedded evidence | Supports? |
|---|---|---|
| impl C1 `skip_card` delegates to `_remove_card_from_queue` | `review_manager.py:156-161` (verified) | ✓ |
| impl C3 except handler calls `skip_card`; loop bounded by queue length | `review_ui.py:119` + head_green.txt loop-terminates | ✓ |
| impl C5 Well-done suppressed when `success==0 & failed>0` | `review_ui.py:138-140` (verified) | ✓ |
| impl C6/C7 `-> bool`; `typer.Exit(code=1)` on False | `review_ui.py:70,140` + `_review_logic.py:45-47` (verified) | ✓ |
| impl C12 CliRunner live-fire `exit_code==1` | `test_main.py::test_review_command_exits_on_total_failure` cited | ✓ (Class A/B) |
| tests C5 2 RED tests FAIL on baseline | baseline_red.txt: 4 RED fail on `5bb2ea2`, modes map to B1/B2/B3 | ✓ |
| ci C1 `black -l 79 --check` exits 0 | inline capture "EXIT: 0" | ✓ |
| crv C1 elif branch now exercised | `test_…_mixed_outcome_no_well_done` @ `test_review_ui.py:352-401` | ✓ |
| crv2 C2 `reviewed_cards = total - queue_len - skipped_count` | `review_manager.py:237-238` (verified) | ✓ |

No ✗ rows. No forward-reference-only claims; each packet is self-contained.

---

## Self-containment + immutability cross-check

- **Self-containment: PASS.** Each packet stands alone — claims are backed by its own commit's
  evidence, not "covered in a later commit". crv/crv2 are *additive follow-ups* (coverage, stats),
  not forward-references that complete an earlier claim.
- **Immutability: PASS for intent (Class E SHA-pinned permalinks) and behavioral artifacts (sha256
  manifest, verified).** The one gap is Class A *citation form* (Finding 4, WARN).
- **No `~/`-rooted or branch-URL artifact citations** in any F82 packet.

---

## Summary table

| Dimension | Status |
|---|---|
| Shape (`aiv check`, 0 blocking) | ✅ PASS |
| Class E intent-**target** correctness (canonical audit source) | ✅ PASS |
| Class E intent-**alignment** (change ↔ recorded defect) | ✅ PASS |
| No vacuous/empty evidence class (A–F, falsifiable N/A) | ✅ PASS |
| Claim-evidence correspondence | ✅ PASS |
| Self-containment | ✅ PASS |
| Behavioral evidence genuine (manifest hashes verified) | ✅ PASS |
| Class A immutable CI reference (A-001/A-002) | ⚠️ WARN (mitigated; Finding 4) |
| `Repository` metadata field | ⚠️ WARN (cosmetic; Finding 5) |
| **Packet decision** | **CONDITIONAL — 0 blocking; READY for human adjudication** |

---

## Harvested evidence (read-only — attach to amendment packet)

**Finding 4 remediation — sha256 manifest VERIFIED (immutable substrate for Class A):**

| Path | Claimed sha256 | Recomputed | Match |
|---|---|---|---|
| evidence/c2-f82/head_green.txt | `de9db74…841078b` | `de9db7419271739cba93abef41d8c4738e2016bd6d5df516c78904402841078b` | ✅ |
| evidence/c2-f82/baseline_red.txt | `a69af0e…43e452` | `a69af0e24fc49ebca6cf575f3609073077f0f8359462485f95bf02f80243e452` | ✅ |

These hashed, committed artifacts satisfy the §3.3 *hash-manifest* immutability mechanism and carry
the pass/fail/skip counts (head: `490 passed, 1 skipped`; baseline: `4 RED failed`). Citing them as
the Class A immutability mechanism closes Finding 4 without CI access.

**Finding 4 remediation — CI permalink: NO read-only harvest path available.**
CI infrastructure exists (`.github/workflows/main.yml`, `aiv-guard.yml`, `release.yml`), so an
immutable CI-run permalink bound to `head_sha` is in principle harvestable — but **`gh` is
unavailable in this environment**, so `gh run list --branch fix/c2-f82 …` cannot be executed.
Requires operator/`gh` access. (Operator action — outside this audit's read-only scope.)

**Line-anchor resolution (Class B spot-check, all resolve at HEAD `24a518a`):**
```
review_manager.py:71   self.skipped_card_count: int = 0
review_manager.py:156  def skip_card(self, card_uuid: UUID) -> None:
review_manager.py:237-238  reviewed_cards = (total_cards - len(self.review_queue) - self.skipped_card_count)
review_ui.py:70   ) -> bool:
review_ui.py:119  manager.skip_card(card.uuid)
review_ui.py:138-148  if failed_count>0 and success_count==0: … return False / elif / else "Well done!"
_review_logic.py:45-47  result = start_review_flow(...) ; if not result: raise typer.Exit(code=1)
```

---

## Recommendations (operator decides; this audit is read-only)

1. **Accept as READY** — 0 blocking findings; the load-bearing dimensions (Class E target + alignment,
   no vacuous class, genuine verified behavioral evidence) all PASS. The merge act itself is H2.
2. **Optional amendment (Finding 4)** — cite the verified sha256 evidence artifacts as the Class A
   immutability mechanism, and/or attach a CI permalink once `gh` is available (§10 exception path
   also available if the program elects to defer CI-permalink immutability for R0/R1 local-exec).
3. **Optional fix (Finding 5)** — correct the `Repository` Identification field to
   `github.com/ImmortalDemonGod/flashcore` in all five packets.

- Generated by aiv-audit, read-only (content audit + evidence harvest). `gh` unavailable → no PR comment; written to `.aiv/verdicts/c2-f82/aiv-audit.md`.

## Machine-checkable data

```json
{
  "schema": "aiv_audit_result@1",
  "packet_decision": "CONDITIONAL",
  "shape_check_passed": true,
  "blocking_findings": [],
  "classes_vacuous_or_na_unjustified": []
}
```
