# AIV spec audit — F169 / C2 packet set (content audit; follow-up to shape review)

Shape (`aiv check --strict --audit-links`) was verified separately (see below). This audit
verifies packet **content** against the spec at `/home/user/aiv-protocol/SPECIFICATION.md`
(**AIV Canonical Specification**, §§ resolved at audit time). `gh` is unavailable in this
environment, so this audit is written to a file rather than posted as a PR comment.

> **Config note.** No `.aiv-workflow.yml` at repo root — defaults applied: `aiv.cli=aiv`,
> `aiv.spec_path=aiv-protocol/SPECIFICATION.md` (resolved to `/home/user/aiv-protocol/SPECIFICATION.md`),
> `aiv.packets_dir=.github/aiv-packets`, `evidence.mandate_all_classes=true`,
> `evidence.exclude_classes=[G]`, `branch.base=origin/main`.

**Scope sampled:** all 5 F169 packets — `PACKET_c2_f169_impl.md` (functional fix),
`PACKET_c2_f169_tests.md` (RED tests), `PACKET_c2_f169_oracle_corr.md` (oracle-correction doc),
`PACKET_c2_f169_ci.md` (black reformat), `PACKET_c2_f169_determinism.md` (dep pin).
Branch `feat/c2-fsrs-harness` @ `53fba9e`, base `origin/main` @ `b5e1c4b`.

**Headline:** `PACKET_c2_f169_oracle_corr.md` **silently omits 4 of 6 evidence classes**
(A, C, D, F) — including **Class A (Execution), which §6.1 marks Required at R1** — yet its own
Evidence-References table claims classes "A, B, E". Under the all-class mandate
(`evidence.mandate_all_classes=true`) a silently-omitted class is a **BLOCKING** finding. The
underlying *fix* is well-evidenced (probes + Layer-B integration verified below); the defect is
in **packet completeness**, which the shape validator does not catch.

---

## Shape check (validator — not re-derived here)

`aiv check <packet> --strict --audit-links` over all 5 packets: **0 blocking error(s)** each
(strict mode reports "Validation Failed" only on WARN/INFO: E016 Class-B location hints, E004
Class-E plain-text URL [non-blocking per project CLAUDE.md], E020 "R1: Class C recommended but
not required"). The shape gate is therefore **clean on blocking errors**. Every finding below is
a *content* finding the validator structurally cannot raise — most importantly, `aiv check` does
**not** flag the missing required Class A in `oracle_corr` because it grades per the spec's
tier-conditional matrix, treating non-A/B/E classes as optional at R1.

---

## Finding 1 — `oracle_corr` omits required Class A + 3 further classes (§6.1; all-class mandate) — **BLOCK**

Spec §6.1 Evidence Class Summary (verbatim):

> | **A** | Execution | Proves tests passed in defined environment | ✓ | ✓ | ✓ | ✓ |
> **Legend:** ✓ = Required

Class A is **Required at every tier including R1**. `PACKET_c2_f169_oracle_corr.md` (self-declared
`risk_tier: R1`) contains **only `### Class B` and `### Class E` sections** — no `### Class A`,
no `### Class C`, no `### Class D`, no `### Class F`. Confirmed: the packet body
(`.github/aiv-packets/PACKET_c2_f169_oracle_corr.md:43-58`) jumps from the Evidence-References
table straight to Class B then Class E.

Two compounding problems:
1. **Internal contradiction.** The Evidence-References table
   (`PACKET_c2_f169_oracle_corr.md:39`) declares the evidence file carries classes **"A, B, E"**,
   but there is **no Class A section** to carry it. The Class E prose even asserts the doc
   *"provides the execution evidence that the old setup would cause both assertions to fail"* —
   i.e. execution evidence is *referenced* but never presented in a Class A section with
   pass/fail/skip counts (§6.2.1 / A-003).
2. **All-class mandate violation.** Per the operator mandate (`evidence.mandate_all_classes=true`),
   every packet must *address* A–F; a class that does not apply still needs an explicit `### Class X`
   section marked `N/A — <falsifiable reason>`. Classes A/C/D/F are **silently absent** — strictly
   worse than vacuous, and a **BLOCKING** finding by the audit's own rule.

**Cascade:** because Class A is genuinely missing, the packet cannot demonstrate that the
oracle-correction claims (tests fail under old setup, pass under corrected code) were executed —
the very thing the packet exists to prove.

---

## Finding 2 — `classification_rationale` is a literal `TODO` in 4 of 5 packets (§5.5-F2) — **BLOCK**

Spec §5.5 lists `classification_rationale: string # REQUIRED; explanation of tier assignment`
and **Finding (5.5-F2): Classification rationale missing or inadequate.**

The following packets ship the placeholder verbatim:

| Packet | Line | `classification_rationale` value |
|---|---|---|
| `PACKET_c2_f169_impl.md` | :22 | `"TODO: Describe why this tier was chosen"` |
| `PACKET_c2_f169_tests.md` | :22 | `"TODO: Describe why this tier was chosen"` |
| `PACKET_c2_f169_ci.md` | :22 | `"TODO: Describe why this tier was chosen"` |
| `PACKET_c2_f169_oracle_corr.md` | :22 | `"TODO: Describe why this tier was chosen"` |

A required field whose content is an unfilled TODO is "inadequate" per 5.5-F2. (`determinism`
is the only packet with a real rationale — see Finding 4 for its separate defect.) Trivially
remediable; blocking until filled because the field is REQUIRED.

---

## Finding 3 — Class A: no immutable CI reference / SHA binding across **all** packets (A-001, A-002; A-F1) — **WARN now → BLOCK if L2+/conformance is claimed**

Spec §6.2.2:

> | A-001 | CI run reference MUST be immutable per §3.3 | BLOCK |
> | A-002 | CI run commit SHA MUST match packet `head_sha` | BLOCK |

Every packet's Class A cites **local host execution**, not an immutable CI run:
- `impl` :53 — *"Live-execution results against real in-memory DB"*; `python -m pytest …`
- `ci` :46 — *"Live-execution results on this host (Linux, black==25.12.0)"*
- `determinism` :45 — `python -m pytest …` on the runner
- `tests` :50 — `pytest … (commit 61d6a20)`

Pass/fail/skip **counts are present** (A-003 satisfied — e.g. `tests` "17 collected: 15 PASSED,
2 FAILED"; `ci`/`determinism` "483 passed, 1 skipped"), and the captured outputs are retained
under `.github/aiv-packets/evidence/` and hashed in `MANIFEST.md`. But **no commit-SHA-bound CI
run permalink exists** (A-001/A-002 unmet → A-F1). At R1→L1 (§8.2) this is tolerable as a
process gap; it becomes BLOCKING the moment L2+ or formal conformance is claimed.
**No read-only harvest path** — `gh` is unavailable and no CI run exists to permalink; the local
captures in `evidence/` are the only available substrate and are not immutable CI references.

---

## Finding 4 — `determinism` packet: invalid `blast_radius` enum + understated tier (§5.5-F1, §5.1) — **WARN**

`PACKET_c2_f169_determinism.md:21` sets `blast_radius: pyproject.toml`. Spec §5.5 fixes the enum:
`local | component | service | cross-service | organization`. `pyproject.toml` is **not a valid
value** → **Finding (5.5-F1): Missing or incomplete classification record.**

Separately, the packet self-declares **R0** for a change that pins `flake8/black/isort/mypy` to
`==` versions. Spec §5.1 lists **"dependency changes"** and **"configuration changes"** as **R2**
examples ("Library upgrades", "feature flags"). The packet's rationale ("installed binaries
unchanged; only the declared constraint tightened") is defensible for behavior-preservation, but
the tier is at least debatable. **Cascade if upheld as R2:** Class C becomes Required (§6.1) and
SoD S1 / independent verifier becomes Required (§5.4) — which a self-verified packet would not
meet. Operator decides; flagged, not graded as BLOCK.

---

## Finding 5 — Packet `Repository` field mislabels provenance (§6.3 self-containment) — **WARN**

All 5 packets set **`Repository | github.com/ImmortalDemonGod/aiv-protocol`** (e.g.
`impl` :7). The actual repository is **flashcore** — the Class E intent links and Class B code
anchors all correctly target `github.com/ImmortalDemonGod/flashcore` (`impl` :90,
`tests` :105). A reviewer constructing canonical commit-SHA permalinks from the packet's
`Repository` field (§6.3.1 Code Permalinks) would resolve against the **wrong repo**. Cosmetic in
origin (template/`aiv close` default) but material to B-001/B-003 link resolvability and
self-containment. WARN.

---

## Claim-evidence correspondence (sampled)

| Packet · Claim | Embedded / cited evidence | Supports? |
|---|---|---|
| `impl` C4 "`last_review = fsrs_card.due` removed; replaced with conditional" | `git diff origin/main..HEAD -- flashcore/scheduler.py` shows exactly this (lines removed, `if card.last_review_date is not None:` added) | ✓ |
| `impl` C5 "None → last_review unset → elapsed_days=0" | Diff `# else: last_review unset → elapsed_days=0`; `baseline_direct_probe.txt` shows elapsed_days=0 | ✓ |
| `impl` AC-1/AC-2 "elapsed_days>0; stability distinct" | `head_direct_probe.txt`: elapsed_days=14, stability=44.8064 (vs baseline 0 / 14.0); `head_green.txt`: both tests PASS | ✓ |
| `impl` AC-12 "Layer-B: elapsed_days_at_review>0 in DB row" | `layerb_integration.txt`: `test_on_time_review_persists_positive_elapsed_days PASSED` (real SQLite, real scheduler) | ✓ (live-fire, Class A) |
| `impl` AC-3 "bug line absent" | re-ran `git grep -nE 'last_review = fsrs_card\.due' HEAD -- flashcore/scheduler.py` → 0 hits | ✓ |
| `impl` Class D "467 passed, 1 skipped, **16 errors**" | `full_suite_head.txt` (HEAD) shows "**483 passed, 1 skipped**", no errors | ⚠ partial — reconcilable (467+16≈483; the 16 were collection errors at the earlier `37a0dec` snapshot, resolved by HEAD), but **cross-packet count inconsistency** is uncaptured; should be noted in `known_limitations` |
| `tests` C5/C6 "RED: elapsed_days=0; ValidationError extra_forbidden" | `baseline_red.txt` + Class A inline FAILED block | ✓ |
| `oracle_corr` all claims | **no Class A section** to bind execution claims; relies on prose only | ✗ (Finding 1) |

Scope inventory cross-check (`impl`): `git diff --name-only c832b15..37a0dec` = models.py,
scheduler.py, review_processor.py + 3 evidence files — **matches** the packet's Class B inventory
(B-003 satisfied).

---

## Summary table

| Dimension | Status |
|---|---|
| Shape (`aiv check`, blocking) | PASS (0 blocking; WARN/INFO only) |
| Tier defensibility (impl/tests/ci) | OK — FSRS scheduler touches **no §5.2 critical surface**; R1 defensible (no 5.2-F1) |
| Tier defensibility (determinism) | QUESTIONED — R0 for a dep/config pin; §5.1 → arguably R2 (Finding 4) |
| Evidence-class completeness | **FAIL** — `oracle_corr` omits A/C/D/F incl. required Class A (Finding 1) |
| Classification record | **FAIL** — TODO rationale ×4 (Finding 2); invalid blast_radius enum ×1 (Finding 4) |
| Class A immutability/CI binding | WARN — local-only, no immutable CI ref (Finding 3) |
| Claim↔evidence (functional fix) | STRONG — probes + Layer-B integration verified; one cross-packet count note |
| Self-containment / provenance | WARN — `Repository` field names wrong repo (Finding 5) |

---

## Harvested evidence (read-only — attach to amendment packet)

**Finding 1 remediation — Class C re-run (the grep the packets claim was performed):**
```bash
$ git grep -nE 'last_review = fsrs_card\.due' HEAD -- flashcore/scheduler.py
(0 hits — bug line absent at HEAD)
```
Tool: git 2.43.0; pattern: `last_review = fsrs_card\.due`; scope: `flashcore/scheduler.py` @ `53fba9e`.
Result: 0 hits — confirms AC-3 / the negative-evidence claim.

**Finding 1 remediation — Class A substrate for `oracle_corr` (Layer-B + direct probes already captured):**
```
layerb_integration.txt → test_on_time_review_persists_positive_elapsed_days PASSED (1 passed, 0.15s)
head_green.txt         → test_on_time_review_elapsed_days_positive PASSED;
                         test_on_time_vs_same_day_review_stability_distinct PASSED (2 passed, 0.14s)
head_direct_probe.txt  → elapsed_days=14, stability=44.8064 (FIX CONFIRMED)
baseline_direct_probe  → elapsed_days=0,  stability=14.0000 (BUG CONFIRMED at b5e1c4b)
```
These already-captured artifacts are pasteable into a `### Class A` section for `oracle_corr`
(with pass/fail counts) to satisfy §6.2.1 A-003.

**Finding 3 candidate / Class F — SHA-256 manifest of cited evidence artifacts (verified present):**
| Path (`.github/aiv-packets/evidence/`) | SHA-256 |
|---|---|
| baseline_direct_probe.txt | `3863d463df5b1c04a39f2206dea1029cf33c2b05ae826f59b5b5c7366c62fffb` |
| baseline_red.txt | `a4155a5abed242bcd918b0dd8abe9df6f42c2cb4034a2ab0e034772ca1496bfc` |
| full_suite_head.txt | `1a3004173fc26d636af23b60285622c302b63aada2ede9e51e0c817ae00e112c` |
| head_direct_probe.txt | `abac58d9dd4b924140d193c81aafb71091ad3fc53b219420f0211db3099fb9b2` |
| head_full_scheduler.txt | `3d3abad8f71b2ff8929bb8e7907ee34ba65e819c88e80d2e0fafc890a212f721` |
| head_green.txt | `ce2d454d0423458a33322be2c2eeb4eeca1c34bbfc7155c7b5494896f31d7db9` |
| layerb_integration.txt | `ef464c8516c87fe30761ff666b9937ad5211ab14be7cdcdbdff8843132a98c59` |
| mypy_clean.txt | `b1e664b8e68424a40aeefdca9ecd2696f222f86d562e015d06dd1533e31a5334` |
| MANIFEST.md | `0034b07eec834b42e0ead3c1a29d6b251e019c4af9b367784c86f8f78ab143db` |

Hashes match `evidence/MANIFEST.md` exactly (re-`sha256sum` confirmed). Per §6.1, Class F is
Required only at R3; at R1 the defensible state is **this manifest + an honest `N/A — no signing
infra; SHA-256 manifest provided` rationale** for cryptographic provenance — **not** a hard Class F
BLOCK. No Sigstore/CI-OIDC infra exists → no read-only harvest path for cryptographic attestation.

**Finding 5 remediation — canonical permalink base:**
Replace `Repository | github.com/ImmortalDemonGod/aiv-protocol` with
`github.com/ImmortalDemonGod/flashcore` in all 5 packets; Class B/E links already use the correct
org/repo, so only the Identification field needs correction.

**Findings 2 & 4 — no harvest needed:** these are author-supplied fields (fill the TODO rationale;
correct `blast_radius` to a valid enum value and re-evaluate R0-vs-R2). Operator action.

---

## Recommendations (operator decides; this audit is read-only)

1. **Amend `oracle_corr` (Finding 1, highest fidelity).** Add `### Class A` (paste the harvested
   Layer-B + probe results with counts), and add `### Class C / ### Class D / ### Class F`
   sections — each either real or `N/A — <falsifiable reason>` (e.g. Class D `N/A — doc-only
   change, no production surface`; Class F `N/A — no signing infra; sha256 manifest in evidence/`).
   Fix the Evidence-References "A, B, E" row to match what is actually present.
2. **Fill the TODO rationale in 4 packets (Finding 2)** and **correct `determinism`'s
   `blast_radius` enum + revisit R0/R2 (Finding 4).** Cheap, removes two classification findings.
3. **File a documented exception** (spec §10) for Class A CI-immutability (Finding 3) if no CI
   infra will be wired before merge — the captured local outputs + sha256 manifest support the
   exception rationale; record the snapshot/CI obligation per §10.4.
4. **Record the cross-packet count discrepancy** (impl "467+16err" vs HEAD "483") in
   `known_limitations` so a reader is not misled (§7.5).

- Generated by aiv-audit, read-only (audit + evidence harvest). Human remains the merge gate; a
  clean content audit would still not authorize merge.

## Machine-checkable data

```json
{
  "schema": "aiv_audit_result@1",
  "packet_decision": "NON-COMPLIANT",
  "shape_check_passed": true,
  "blocking_findings": [
    {"packet": "PACKET_c2_f169_oracle_corr.md", "spec_finding_id": "§6.1 / A-F3 (+ all-class mandate)", "detail": "Class A (Execution) REQUIRED at R1 is absent; classes C/D/F also silently omitted with no N/A rationale; Evidence-References table claims 'A, B, E' but only B and E sections exist."},
    {"packet": "PACKET_c2_f169_impl.md / tests.md / ci.md / oracle_corr.md", "spec_finding_id": "5.5-F2", "detail": "classification_rationale is the literal placeholder 'TODO: Describe why this tier was chosen' in 4 packets (line 22 each); REQUIRED §5.5 field is inadequate."}
  ],
  "classes_vacuous_or_na_unjustified": [
    "PACKET_c2_f169_oracle_corr.md: Class A omitted (REQUIRED at R1 per §6.1)",
    "PACKET_c2_f169_oracle_corr.md: Class C omitted, no N/A rationale",
    "PACKET_c2_f169_oracle_corr.md: Class D omitted, no N/A rationale",
    "PACKET_c2_f169_oracle_corr.md: Class F omitted, no N/A rationale"
  ]
}
```
