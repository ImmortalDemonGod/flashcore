# AIV spec audit — c2-f82 (content audit; follow-up to shape review)

Shape (`aiv check`) was run separately (see §Shape). This audit verifies packet **content**
against the AIV Canonical Specification `AIV-SPEC-V1.0.0-CANONICAL` at
`/home/user/aiv-protocol/SPECIFICATION.md` (no `.aiv-workflow.yml` present — using documented
defaults; spec resolved at `$HOME/aiv-protocol/SPECIFICATION.md`, the in-repo default path
`aiv-protocol/SPECIFICATION.md` being absent in this checkout).

**Packets audited:** `PACKET_c2_f82_impl.md` (functional fix), `PACKET_c2_f82_tests.md`
(RED tests + bug catalog), `PACKET_c2_f82_crv.md` (elif-branch coverage). All three sampled
(the complete c2-f82 set).
**Behavioral evidence:** `.github/aiv-packets/evidence/c2-f82/{MANIFEST.md,baseline_red.txt,head_green.txt}`.
**Headline:** All load-bearing content checks PASS — risk tier defensible (no §5.2 critical
surface), Class E points to the exact canonical audit source in all three packets, and the
diff genuinely addresses the recorded defect. 0 BLOCK-severity content findings; 3 WARN-level
findings with harvest paths. **Decision: CONDITIONAL.**

---

## Finding 1 — Tier classification (5.2-F1 / 5.5-F2): DEFENSIBLE, no finding fired

Spec §5.2 mandates R3 only for changes touching a critical surface:
> "A change MUST be classified as **R3** regardless of other factors if it modifies code in any
> of the following critical surfaces" — Authentication, Authorization, Secrets Management,
> Cryptography, Financial Processing, PII Handling, Privilege Boundaries, Audit/Logging.

The c2-f82 change touches `flashcore/cli/review_ui.py`, `flashcore/cli/_review_logic.py`,
`flashcore/review_manager.py` (verified via `git diff origin/main..HEAD`). These implement the
flashcard **review-session loop** and a CLI **exit-code** wiring — none is a §5.2 surface. No
permission check, role/ACL edit, token, secret, cipher, monetary calc, PII path, privilege
boundary, or audit-log write is added or modified. Blast radius is `component` (§5.3: R1–R2).
Self-declared **R1** is defensible; R1 minimum compliance level is **L1** (§8.2), satisfied.
**No tier-misclassification finding.** This removes the cascade that would otherwise pull in
Class C/D/F as mandatory.

> Note: the per-file evidence file `EVIDENCE_FLASHCORE_CLI_REVIEW_UI.md` self-classifies the
> *formatting-only* commit `7911e17` as R0 ("black -l 79 … no logic change"). That evidence file
> describes a different (style) commit than the logic change in `c029942`; not in scope for the
> packet-level tier audit, noted for completeness.

## Finding 2 — Class E intent-target correctness: CORRECT in all three packets (load-bearing)

The mandate: Class E MUST point to the original audit record that produced F82 —
`https://github.com/ImmortalDemonGod/flashcore/blob/5bb2ea2ab72239e0d2de7cc51fd4b5b766e44bfb/audit/02-static-audit.md#L92`
— not a taskmaster task or pipeline launch-brief.

| Packet | Class E target | Verdict |
|---|---|---|
| `PACKET_c2_f82_impl.md:137` | canonical URL `…/5bb2ea2…/audit/02-static-audit.md#L92` | ✓ correct |
| `PACKET_c2_f82_tests.md:95` | canonical URL `…/5bb2ea2…/audit/02-static-audit.md#L92` | ✓ correct |
| `PACKET_c2_f82_crv.md:70` | canonical URL `…/5bb2ea2…/audit/02-static-audit.md#L92` | ✓ correct |

All six per-file evidence files also cite the same canonical URL. None points to
`.taskmaster/task_NNN.md`, `tasks.json`, or `.aiv/launch-briefs/`. The cited base SHA
`5bb2ea2` matches `git rev-parse origin/main`. **No intent-provenance finding.**

## Finding 3 — Class E intent ALIGNMENT (not theater): GENUINE (load-bearing)

The audit source at L92 records three sub-defects in `start_review_flow()`:
(B1) `except…continue` without removing the failed card → `get_next_card()` returns
`review_queue[0]` forever → unbounded infinite retry; (B2) unconditional "Well done!";
(B3) `-> None` so no failure signal reaches the CLI. Read `git diff origin/main..HEAD` —
the change concretely addresses each:

| Recorded defect | What the diff does | Evidence |
|---|---|---|
| B1 infinite retry | adds `ReviewSessionManager.skip_card(uuid)` and calls it in the `except` handler before `continue`, draining the queue → loop bounded by queue length | `review_manager.py:155-158`, `review_ui.py` except block (`manager.skip_card(card.uuid)`) |
| B2 false "Well done" | gates end-of-session message on `success_count`/`failed_count`: "Review session failed." (total fail) / "finished." (mixed) / "Well done!" (all-success) | `review_ui.py:138-148` |
| B3 no failure signal | return type `-> None` → `-> bool`; `_review_logic.py` raises `typer.Exit(code=1)` when `not result` | `review_ui.py:68`, `_review_logic.py:45-47` |

The impl packet's Class E alignment table states exactly this and is not a bare URL. **The
change corresponds to the recorded intent.** The tests packet correctly frames its stage as
producing RED tests (no fix) and the crv packet as closing the elif-branch coverage gap; both
alignments are concrete and accurate. **No intent-alignment finding.**

## Finding 4 — Evidence-class completeness (all-class mandate): no vacuous/unjustified-N/A class

Per the all-class mandate (operator rule 9; spec L1 floor for R1 = A/B/E), every packet must
address A–F (G excluded) with a falsifiable N/A where inapplicable. Audit of each section:

| Class | impl | tests | crv |
|---|---|---|---|
| A Execution | counts present (490 passed/0 failed; live-fire CliRunner exit-code) | counts present (483 passed/2 RED-fail) | counts present (491 passed) |
| B Referential | 21-item scope inventory | 2-item inventory | 1-item inventory |
| C Negative | 4 enumerated searches + bug-catalog Skipped set | 3 searches + Skipped set | falsifiable N/A ("adds coverage only; no production logic modified") |
| D Static | ruff/mypy results + honest 2 pre-existing errors | ruff/mypy clean | ruff/mypy clean |
| E Intent | full B1/B2/B3 alignment table | RED-stage alignment | elif-coverage alignment |
| F Provenance | 3-row test chain-of-custody | 2-file chain-of-custody | 3-commit chain-of-custody |

No section is empty or vacuous; the one N/A (crv Class C) carries a falsifiable rationale.
**No vacuous-class blocking finding.** `classes_vacuous_or_na_unjustified: []`.

## Finding 5 — Behavioral evidence integrity: VERIFIED

The MANIFEST records sha256 for the two captured run logs. Re-hashed at audit time:

| Artifact | MANIFEST sha256 | Recomputed | Match |
|---|---|---|---|
| `baseline_red.txt` | `a69af0e2…0243e452` | `a69af0e2…0243e452` | ✓ |
| `head_green.txt` | `de9db741…2841078b` | `de9db741…2841078b` | ✓ |

`baseline_red.txt` shows the 4 RED tests FAIL on `5bb2ea2` (origin/main) with failure modes
mapping to B1/B2/B3; `head_green.txt` shows 10/10 review_ui tests + 490 passed/1 skipped at
HEAD. This is a §3.3 **hash-manifest** immutability mechanism and constitutes credible Class
A/B behavioral evidence for the change as a whole.

---

## Claim-evidence correspondence (sampled)

| Packet · Claim | Embedded evidence | Supports? |
|---|---|---|
| impl C1 `skip_card` delegates to `_remove_card_from_queue` | `review_manager.py:155-158` diff | ✓ |
| impl C3 loop bounded by queue length | except-handler `skip_card` + head_green RUN1 | ✓ |
| impl C5 "Well done" suppressed on total failure | `review_ui.py:138-148` + head_green | ✓ |
| impl C7 `typer.Exit(code=1)` on `False` | `_review_logic.py:45-47` + live-fire CliRunner test | ✓ |
| impl C12 `exit_code==1` via CliRunner | `tests/cli/test_main.py` test (b927338) | ✓ |
| tests C5 2 new tests FAIL RED | baseline_red.txt §RUN1 (AssertionError / AttributeError) | ✓ |
| crv C1 elif branch exercised | `tests/cli/test_review_ui.py#L352-L401` + 491-pass run | ✓ |
| (all) "no existing tests modified/deleted" | Class F chain-of-custody (backward refs only) | ✓ |

No claim relies on "visual inspection" without capture or on a forward-reference to a
*later* commit's packet. Self-containment holds.

---

## WARN-level findings (CONDITIONAL — do not block; harvest provided)

### W1 — Class A immutable CI reference absent (A-001 / `aiv check` E012) — WARN
Each packet's Class A cites inline pytest counts, not an immutable CI-run permalink bound to
`head_sha`. **No CI infrastructure exists in this environment** (`gh` unavailable; no Actions
run to reference) — so A-001's CI-permalink form is genuinely unobtainable, not merely costly.
The defensible substitute already exists: `MANIFEST.md` carries sha256 hashes of the captured
run logs (verified above) — the §3.3 hash-manifest mechanism. Gap: the packets' Class A
sections do not *cite* those hashed artifacts. A-003 (pass/fail/skip counts) **is** satisfied.
→ The "satisfied N/A-with-manifest" case, not a hard Class A finding.

### W2 — Class B scope inventory uses bare `path#Lline`, not SHA permalinks (B-002 / E016) — WARN
The in-packet Class B inventory lists `path#Lline` without commit-SHA permalink URLs. Per spec
B-002 this is **WARN at R0–R1** (BLOCK only at R2+), so non-blocking here. Traceability is
preserved because the referenced per-file evidence files carry SHA-bound tree URLs (e.g.
`…/tree/026f60c…`) and the Evidence-References table pins each to a commit SHA per §6.11.

### W3 — `Repository` metadata field is wrong in all three packets — WARN
All three packets read `Repository | github.com/ImmortalDemonGod/aiv-protocol`. The actual
repository is **flashcore** (every Class B/E permalink correctly uses `…/flashcore/…`). Cosmetic
template artifact; could mislead an auditor resolving the repo root. Recommend correcting to
`github.com/ImmortalDemonGod/flashcore`.

### W4 — Class E link rendered as plain text in places (E004 / E-F1b) — INFO only
`aiv check` E004 flags the intent reference as plain text in the identification context. The URL
is SHA-pinned and immutable; informational only per project CLAUDE.md.

---

## Shape (`aiv check --strict`)

| Packet | Blocking errors | Warnings |
|---|---|---|
| `PACKET_c2_f82_impl.md` | **0** | 9 (E012 ×1, E016 ×8) |
| `PACKET_c2_f82_tests.md` | **0** | 5 |
| `PACKET_c2_f82_crv.md` | **0** | 1 |

All three return **0 blocking errors**; `--strict` reports "Validation Failed" because it
elevates warnings to non-zero exit. Structural shape (BLOCK-severity) is clean →
`shape_check_passed: true`. The warnings are the same content-quality gaps captured in W1/W2/W4.

---

## Summary table

| Dimension | Status |
|---|---|
| Risk tier defensible (§5.2/§5.3) | ✓ R1 / L1 |
| Class E intent-target = canonical audit source | ✓ all 3 packets |
| Class E intent alignment genuine (diff ↔ recorded defect) | ✓ |
| Evidence-class completeness (A–F, no vacuous/unjustified N/A) | ✓ |
| Behavioral evidence integrity (sha256 manifest) | ✓ verified |
| Claim-evidence correspondence | ✓ sampled clean |
| Self-containment (no forward-reference chain) | ✓ |
| Shape: BLOCK-severity errors | ✓ 0 across all packets |
| WARN findings | 3 (W1–W3) + 1 info (W4) |

---

## Harvested evidence (read-only — attach to amendment packet)

**W1 remediation — sha256 manifest of captured run logs (closes the Class A immutable-artifact citation gap; `gh`/CI unavailable so this IS the immutable substitute):**

| Path | sha256 |
|---|---|
| `.github/aiv-packets/evidence/c2-f82/baseline_red.txt` | `a69af0e24fc49ebca6cf575f3609073077f0f8359462485f95bf02f80243e452` |
| `.github/aiv-packets/evidence/c2-f82/head_green.txt` | `de9db7419271739cba93abef41d8c4738e2016bd6d5df516c78904402841078b` |

Paste into each packet's Class A section: *"Behavioral evidence captured to sha256-pinned logs
(hash-manifest immutability, §3.3): baseline RED `a69af0e2…`, HEAD GREEN `de9db741…`; counts
490 passed/1 skipped at HEAD `c0f4366`."*

**W1 remediation — Class F sha256 manifest of touched test files at HEAD `c61f431`:**

| Path | sha256 |
|---|---|
| `tests/cli/test_review_ui.py` | `c301e89890c6c63948cde14cae724324db299f62558673e51c5613040dc3ac24` |
| `tests/test_review_manager.py` | `dc882d4a2a13d2faccfc5f9336c67b32297b22f7cb998fcebc14b2c4f9313e5d` |
| `tests/cli/test_main.py` | `cd21cfe2572bcf6cd7c7f81faf6634d31a975ba4c8af491fe7c460393c2245cf` |
| `tests/cli/test_review_ui.bug-catalog.md` | `f1d073203d01ef27459db7ccbd13f91b56030cd5de0dee499ec37bc92d0c64b9` |

**Class C re-run (confirms impl packet's single-caller negative claim; line shifted 43→45 post-diff):**
```bash
$ git grep -n "start_review_flow" -- 'flashcore/'   # git 2.43.0
flashcore/cli/_review_logic.py:7:from flashcore.cli.review_ui import start_review_flow
flashcore/cli/_review_logic.py:45:    result = start_review_flow(manager, tags=tags)
flashcore/cli/review_ui.py:68:def start_review_flow(
```
Result: exactly one call site (`_review_logic.py:45`); negative claim holds.

**W2 remediation — canonical SHA-bound permalink form for Class B (head `c61f431`):**
`https://github.com/ImmortalDemonGod/flashcore/blob/c61f43182db1721ce2a34c25e81f204dc985d6a3/flashcore/cli/review_ui.py#L138-L148`
(repeat per cited `path#Lline`; replace `c61f431` with the packet's own `head_sha` for per-stage packets).

**No read-only harvest path** for W3 beyond the correction itself (operator edits the
`Repository` field) and for an actual CI permalink (requires CI infra build-out).

---

## Recommendations (operator decides; this comment is read-only)

1. **Amend packets with harvested blocks above** — cite the sha256 manifests in Class A/F and
   add SHA-bound Class B permalinks (highest fidelity; closes W1/W2).
2. **Correct the `Repository` field** to `github.com/ImmortalDemonGod/flashcore` in all three
   packets (closes W3).
3. **Or file a documented exception / known-limitation** per spec §10 for the absent CI-run
   permalink, noting CI infrastructure is not yet wired and the hash-manifest substitute is in
   place (spec-permitted, lowest cost).

The load-bearing content checks pass; W1–W3 are WARN-severity with remediation paths and do not
block merge readiness. Final merge remains the human's act (H2).

- Generated by aiv-audit, read-only (audit + evidence harvest). `gh` unavailable — written to
  `.aiv/verdicts/c2-f82/aiv-audit.md` instead of posted as a PR comment.

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
