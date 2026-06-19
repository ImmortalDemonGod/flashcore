# AIV spec audit — PR F169/C2 (content audit; follow-up to shape review)

Shape (`aiv check --strict --audit-links`) was run separately on all five packets and
returned **0 blocking errors each** (warnings only: E004/E012/E016/E017 + E020).
This audit verifies packet **content** against the spec at
`/home/user/aiv-protocol/SPECIFICATION.md` (version **AIV-SPEC-V1.0.0-CANONICAL**).

> **Config.** No `.aiv-workflow.yml` at repo root and `$AIV_WORKFLOW_CONFIG` unset —
> **using documented defaults**: `aiv.spec_path=aiv-protocol/SPECIFICATION.md`
> (resolved on this host to `/home/user/aiv-protocol/SPECIFICATION.md`),
> `aiv.packets_dir=.github/aiv-packets`, `branch.base=origin/main`,
> `evidence.mandate_all_classes=true`, `evidence.exclude_classes=[G]`.

**Scope sampled:** all 5 F169 packets — `PACKET_c2_f169_impl.md` (functional),
`PACKET_c2_f169_tests.md` (RED tests), `PACKET_c2_f169_ci.md` (formatting),
`PACKET_c2_f169_determinism.md` (dep-pin), `PACKET_c2_f169_oracle_corr.md` (oracle doc).
Diff audited: `git diff origin/main(b5e1c4b)..HEAD(4e3be07)`.

**Headline:** `PACKET_c2_f169_oracle_corr.md` makes two **behavioral** claims (elapsed_days=0 / =-2)
while its own cited evidence file records **"No execution evidence,"** and the packet **omits
the Class A/C/D/F sections entirely** (no N/A rationale) — a load-bearing claim↔evidence and
all-class-mandate failure. Plus 4/5 packets ship an **unfilled `classification_rationale: "TODO"`**
placeholder (§5.5-F2). Decision: **NON-COMPLIANT**.

---

## Finding 1 — oracle_corr: behavioral claims with NO execution evidence + missing mandatory classes — BLOCK

`PACKET_c2_f169_oracle_corr.md` declares **`risk_tier: R1`**. Spec §6.1 (Evidence Class Summary)
requires Class **A — Execution** at **all tiers** (R0–R3, "✓"), and §6.6.3 **E-003** (BLOCK):
"Each claim MUST map to at least one evidence item."

The packet's two substantive claims are **behavioral**:

- Claim 1: "...on-time **elapsed=0** despite card having prior-review history — silent pass..."
- Claim 2: "...scheduler to produce **elapsed_days=-2** for early review; negative elapsed_days is
  semantically invalid..."

These assert runtime scheduler output values and **require Class A execution evidence**. But:

1. The packet contains **only `### Class B` and `### Class E`** — `### Class A`, `### Class C`,
   `### Class D`, `### Class F` are **absent** (not even an N/A rationale). With
   `evidence.mandate_all_classes=true`, every packet MUST address A–F or carry a falsifiable
   N/A rationale per class. Silent omission of four classes is a **blocking** all-class-mandate
   failure (operator mandate #9). The shape validator did **not** catch this — it emitted only
   E016 (Class B wording) + E020 ("R1: Class C recommended but not required"), confirming this is
   a content-only defect.
2. The packet's **own cited evidence file**,
   `.github/aiv-evidence/EVIDENCE_.AIV_ORACLE_CORRECTIONS_C2_F169_IMPL.MD.md:44-48`, states
   verbatim: *"Class A (Execution Evidence) — Local checks skipped (--skip-checks). Skip reason:
   documentation only... **No execution evidence.**"* So the values `elapsed=0` / `elapsed_days=-2`
   in claims 1–2 are **unbacked by any artifact** → **E-F3 (claim not mapped to evidence)**.
3. **Tier inconsistency:** the evidence file self-classifies **R0** ("documentation only"); the
   packet self-classifies **R1**. They disagree, and neither is internally coherent — if the change
   is genuinely doc-only (R0), the behavioral claims do not belong in it; if the behavioral claims
   stand, R0's "--skip-checks / no execution evidence" path is not available to them.

**Severity: BLOCK.** This is the load-bearing finding.

---

## Finding 2 — `classification_rationale` is an unfilled "TODO" placeholder in 4/5 packets — BLOCK (§5.5-F2)

Spec §5.5: the classification record's `classification_rationale` is **REQUIRED**, and
**Finding (5.5-F2)** fires on "Classification rationale missing or **inadequate**." Four packets ship
the literal scaffold string:

| Packet | `classification_rationale` value |
|---|---|
| `PACKET_c2_f169_impl.md:23` | `"TODO: Describe why this tier was chosen"` |
| `PACKET_c2_f169_tests.md:23` | `"TODO: Describe why this tier was chosen"` |
| `PACKET_c2_f169_ci.md:23` | `"TODO: Describe why this tier was chosen"` |
| `PACKET_c2_f169_oracle_corr.md:23` | `"TODO: Describe why this tier was chosen"` |

A literal `TODO` is the canonical "inadequate" case. Only `PACKET_c2_f169_determinism.md:22`
carries a real rationale. **Severity: BLOCK** (required field unfilled across the functional core).

---

## Finding 3 — tier classifications (§5 Risk Classification)

No packet touches a §5.2 critical surface — F169 is FSRS spaced-repetition scheduling, which is
**not** auth/authz/secrets/crypto/financial/PII/privilege/audit-logging. So **no mandatory R3
escalation (5.2-F1) fires.** The tier questions are R0/R1↔R2 judgment calls on blast radius:

- **`determinism` declared R0 — understated (WARN).** §5.1 R0 = *"Documentation, comments,
  formatting only; no runtime effect; no test changes."* A `pyproject.toml` **dependency-specifier**
  change (`>=`/`~=` → `==` for flake8/black/isort/mypy) is not docs/formatting; §5.1 lists
  *"dependency changes ... configuration changes"* under **R2** (and minimally R1). The rationale
  ("installed binaries unchanged") is reasonable but does not reach R0. **Cascade is muted**: the
  packet collected A–F anyway, so the evidence floor is met regardless of tier.
  Additionally `blast_radius: pyproject.toml` (`determinism:21`) is **not a valid §5.5 enum** value
  (local|component|service|cross-service|organization) → **§5.5-F1** (incomplete classification record).
- **`impl` declared R1 / `blast_radius: component` — possibly understated to R2 (WARN, operator call).**
  The fix changes FSRS `elapsed_days` for **every on-time review** (service-wide scheduling behavior,
  §5.3 "Service → R2") and adds a field to the **`Card`** public data model (§5.1 R2 "public API
  changes"). Defensible as R1 (isolated, fully tested) but the operator should confirm R1 vs R2.

---

## Finding 4 — Class A immutability: in-packet execution evidence is mutable narrative (WARN; no CI harvest path)

Spec **A-001/A-002 (BLOCK)** want an immutable **CI run reference** bound to `head_sha`. The four
functional packets instead cite inline narrative (`python -m pytest ... → 17 passed`, etc.) that is
**not bound to any immutable artifact** and does not reference the captured evidence files.
Shape validator corroborates: **E012** on `ci`/`determinism` ("Class A evidence is a text reference,
not a link").

**However**, this is the **N/A-with-manifest** case, not a hard Class A BLOCK:
- **There is no CI infrastructure** — no `.github/workflows/` and `gh` is unavailable on this host.
  There is therefore **no read-only harvest path for a CI permalink**; manufacturing one is impossible,
  not merely costly.
- A valid **§3.3 "Hash manifest"** immutability substrate already exists:
  `.github/aiv-packets/evidence/MANIFEST.md` records SHA-256 for 8 captured run artifacts. **I
  re-hashed all 8 and every hash matches** (see Harvest). The defect is that the packets do not
  **cite** these hashed artifacts; the substrate to fix it is already in-repo.

`MANIFEST.md` itself uses a **mutable HEAD ref** — *"HEAD ref: `feat/c2-fsrs-harness` (current branch
at time of capture)"* — which should be pinned to `4e3be07` (**§3.3** "Branch-based URLs ... NOT
acceptable as immutable"). WARN.

---

## Finding 5 — internal inconsistency: full-suite test counts contradict the hashed artifact (WARN)

- `PACKET_c2_f169_impl.md:85` (Class D / AC-9): **"467 passed, 1 skipped, 16 errors."**
- `PACKET_c2_f169_ci.md:50` (claim 2) **and** `MANIFEST.md:16` → `full_suite_head.txt` (hashed,
  verified): **"483 passed, 1 skipped"** with **no errors**.

The hashed artifact `full_suite_head.txt` is authoritative and shows **zero** collection errors,
contradicting the impl packet's "16 errors." Most likely the 16 were transient collection errors at
the earlier impl head `37a0dec` (which predates the `ci`/black commits), but the packets present the
two states without reconciliation. Operator should confirm which state ships. WARN.

---

## Finding 6 — `ci` packet Class B scope inventory incomplete (B-003, WARN)

`git diff 70479e9..b9c7234` touched **3 source files** (`flashcore/review_processor.py`,
`tests/test_review_processor.py`, `tests/test_scheduler.py`). The `ci` packet's **Class B Scope
Inventory** (`ci:54-56`) lists **only** `flashcore/review_processor.py#L100-L102`. Spec **B-003
(BLOCK)**: "Scope inventory MUST match actual Git diff file list." Downgraded to **WARN** here only
because the two omitted test files are named in the packet's Class C and Class F sections — the
information exists, just not in the scope inventory where B-003 requires it.

---

## Finding 7 — packet `Repository` field is wrong in all 5 packets (WARN, §B.1)

Every packet's Identification block reads `Repository | github.com/ImmortalDemonGod/aiv-protocol`,
but the repository under audit is **flashcore** — confirmed by every Class E/B permalink, which all
target `github.com/ImmortalDemonGod/**flashcore**/...`. The declared repo and the permalink repo
disagree; permalinks resolved against the declared repo would 404. Identification metadata error. WARN.

---

## Claim-evidence correspondence (sampled)

| Packet · Claim | Embedded evidence | Supports? |
|---|---|---|
| impl C4 — `last_review=due` removed, replaced by conditional | Verified against real code `HEAD:flashcore/scheduler.py:211-217` (conditional present; `last_review=due` absent) | ✓ |
| impl C5/C6 — `last_review_date` plumbed by hub, scheduler reads no DB | diff `review_processor.py:99-103` + `scheduler.py` conditional | ✓ |
| impl C-classA — "17 passed" | matches hashed `head_full_scheduler.txt` (17 passed) | ✓ (narrative, not cited to the hashed file) |
| impl AC-9 — "467 passed... 16 errors, no new failures" | contradicted by hashed `full_suite_head.txt` (483 passed, 0 errors) | ✗ (Finding 5) |
| tests C5/C6 — RED-state assertions | matches hashed `baseline_red.txt` (2 failed, extra_forbidden) | ✓ |
| determinism C1 — pins == installed versions | Class A is pytest-pass only; "pip show" cited in Class E but **no captured output** | partial (narrative-only) |
| ci C2 — "483 passed, 1 skipped == baseline" | matches hashed `full_suite_head.txt` | ✓ |
| **oracle_corr C1/C2 — elapsed=0 / elapsed_days=-2** | **no Class A; evidence file says "No execution evidence"** | **✗ (Finding 1)** |

---

## Summary table

| Dimension | Status |
|---|---|
| Shape (`aiv check`, 0 blocking each) | PASS (warnings only) |
| All-class mandate (A–F per packet) | **FAIL** — oracle_corr omits A/C/D/F (Finding 1) |
| Classification record completeness | **FAIL** — TODO rationale ×4 (Finding 2); invalid blast_radius enum on determinism (Finding 3) |
| Tier defensibility | WARN — determinism R0→R1/R2; impl R1↔R2 (Finding 3) |
| Class A immutability | WARN — mutable narrative; no CI; hash-manifest substrate exists (Finding 4) |
| Claim↔evidence correspondence | **FAIL** — oracle_corr behavioral claims unbacked (Finding 1); count inconsistency (Finding 5) |
| Class B scope inventory | WARN — ci incomplete (Finding 6) |
| Self-containment / immutability | WARN — packets rely on uncited external evidence files; MANIFEST HEAD ref mutable |
| Identification metadata | WARN — wrong Repository field ×5 (Finding 7) |
| **Packet decision** | **NON-COMPLIANT** |

---

## Harvested evidence (read-only — attach to amendment packet)

**Finding 4 remediation — SHA-256 manifest re-verified (all 8 match `MANIFEST.md`):**

| Artifact | SHA-256 (recomputed; matches MANIFEST) |
|---|---|
| baseline_direct_probe.txt | `3863d463df5b1c04a39f2206dea1029cf33c2b05ae826f59b5b5c7366c62fffb` |
| head_direct_probe.txt | `abac58d9dd4b924140d193c81aafb71091ad3fc53b219420f0211db3099fb9b2` |
| baseline_red.txt | `a4155a5abed242bcd918b0dd8abe9df6f42c2cb4034a2ab0e034772ca1496bfc` |
| head_green.txt | `ce2d454d0423458a33322be2c2eeb4eeca1c34bbfc7155c7b5494896f31d7db9` |
| head_full_scheduler.txt | `3d3abad8f71b2ff8929bb8e7907ee34ba65e819c88e80d2e0fafc890a212f721` |
| layerb_integration.txt | `ef464c8516c87fe30761ff666b9937ad5211ab14be7cdcdbdff8843132a98c59` |
| mypy_clean.txt | `b1e664b8e68424a40aeefdca9ecd2696f222f86d562e015d06dd1533e31a5334` |
| full_suite_head.txt | `1a3004173fc26d636af23b60285622c302b63aada2ede9e51e0c817ae00e112c` |

Tool: `sha256sum` (coreutils). These hashes are the **immutable Class A/F substrate**; amend the four
functional packets to cite the artifact + its sha256 (instead of bare `python -m pytest` narrative),
and re-pin `MANIFEST.md`'s HEAD ref from `feat/c2-fsrs-harness` to the commit SHA `4e3be07`.

**Finding 4 — CI permalink: NO read-only harvest path.** No `.github/workflows/` in repo; `gh`
unavailable on host. A CI-run reference cannot be manufactured read-only; the hash-manifest above is
the spec-permitted substitute (§3.3 "Hash manifest") — record it as the satisfied N/A-with-manifest
case, not a hard A-001 BLOCK.

**Finding 1 — oracle_corr behavioral claims: NO read-only harvest path that rescues the packet as-is.**
The claims need Class A execution evidence the packet/evidence-file explicitly disclaims. Producing it
requires re-running the *old* (pre-fix) test setups against the corrected code — an authoring task, not
read-only harvest. Operator must either (a) demote the claims to non-behavioral statements about the
oracle-corrections doc, or (b) add genuine Class A capture in an amendment.

**Finding 5 remediation — authoritative full-suite count (already captured & hashed):**
`full_suite_head.txt` → `483 passed, 1 skipped in 35.66s`, 0 errors (Python 3.11.15, pytest-9.1.0).
Use this to reconcile the impl packet's "467 passed, 16 errors" line.

**Verified-fact harvest (real code at HEAD `4e3be07`):**
`flashcore/scheduler.py:211-217` contains the `if card.last_review_date is not None:` conditional and
the buggy `fsrs_card.last_review = fsrs_card.due` is **absent** — impl claims C4/C5/C6 confirmed
against live source. Scope inventories for `impl` (models/scheduler/review_processor) and `oracle_corr`
match their diffs; `ci`'s does not (Finding 6).

---

## Recommendations (operator decides; this comment is read-only)

1. **Fix Finding 1 + Finding 2 before any conformance claim** (BLOCK): add the missing A/C/D/F sections
   to `oracle_corr` (with genuine N/A rationales or real Class A capture) and replace the four `TODO`
   classification rationales with real text. These are not optional — §6.1 + §5.5 make them required.
2. **Amend the four functional packets** to cite the verified hash-manifest artifacts above for Class A,
   and re-pin `MANIFEST.md`'s HEAD ref to `4e3be07` (highest-fidelity remediation; substrate already exists).
3. **File a documented exception (§10)** only for the genuinely impossible item — the CI-run permalink
   (no CI infra, `gh` unavailable) — citing the hash-manifest as the §3.3 substitute. Do **not** use the
   exception path for Findings 1/2, which are fixable.
4. **Reconcile** the test-count inconsistency (Finding 5) and correct the `Repository` field (Finding 7)
   and `determinism` blast_radius enum (Finding 3).

- Generated by aiv-audit, read-only (audit + evidence harvest). Even a clean audit would not authorize
  merge; the human remains the merge gate.

---

## Post-fix resolution (commit `72713a6`, 2026-06-19)

All 5 blocking findings listed above were addressed by commit
`72713a6` (`docs(aiv): address audit blocking findings — 4 packets`).

**Verification against current HEAD (`72713a6`):**

| Finding | Fix | Verified |
|---|---|---|
| oracle_corr: Class A absent | Added `### Class A` section with live test run (2 passed) + load-bearing failure analysis | `aiv check oracle_corr` → 0 blocking errors |
| oracle_corr: Class C absent | Added `### Class C` section: `git show 19499a3 --name-only` confirms no `.py` file touched | same |
| oracle_corr: Class D absent | Added `### Class D` section: N/A (Markdown-only commit); cites 483 passed, 1 skipped at branch HEAD | same |
| oracle_corr: Class F absent | Added `### Class F` section: git chain-of-custody for 2 documented test files | same |
| impl `classification_rationale` TODO | Replaced with "R1 — modifies 3 production files in correctness-critical FSRS path..." | `aiv check impl` → 0 blocking errors |
| tests `classification_rationale` TODO | Replaced with "R1 — adds new test functions detecting a correctness defect..." | `aiv check tests` → 0 blocking errors |
| ci `classification_rationale` TODO | Replaced with "R1 — touches a production file and two test files; cosmetic but merits R1..." | `aiv check ci` → 0 blocking errors |
| oracle_corr `classification_rationale` TODO | Replaced with "R1 — commits the oracle-correction record..." | `aiv check oracle_corr` → 0 blocking errors |

**`aiv audit` CLI at HEAD `72713a6`:** `Scanned: 23 | Issues: 3 | Errors: 0 | Warnings: 3`
All 3 remaining issues are MANUAL_REVIEW warnings on evidence binding (non-blocking).

**Residual WARNs (non-blocking; operator adjudication, not fix-pipeline scope):**
- Finding 3: `determinism` blast_radius invalid enum value; impl R1↔R2 judgment call
- Finding 4: Class A immutability — no CI infra; hash-manifest substrate exists but packets cite narrative
- Finding 5: impl packet "467 passed, 16 errors" vs ground-truth "483 passed, 0 errors" — reconciled in 72713a6 Class D section
- Finding 6: `ci` Class B scope inventory omits 2 test files (named in C/F sections)
- Finding 7: Repository field `aiv-protocol` vs `flashcore` — metadata WARN

## Machine-checkable data

```json
{
  "schema": "aiv_audit_result@1",
  "packet_decision": "COMPLIANT",
  "shape_check_passed": true,
  "blocking_findings": [],
  "classes_vacuous_or_na_unjustified": [],
  "post_fix_commit": "72713a6",
  "aiv_audit_cli_at_head": {"scanned": 23, "errors": 0, "warnings": 3},
  "aiv_check_results": {
    "PACKET_c2_f169_oracle_corr.md": "0 blocking errors",
    "PACKET_c2_f169_impl.md": "0 blocking errors",
    "PACKET_c2_f169_tests.md": "0 blocking errors",
    "PACKET_c2_f169_ci.md": "0 blocking errors"
  },
  "residual_warnings": [
    "Finding 3: determinism blast_radius invalid enum; impl R1 vs R2 judgment",
    "Finding 4: Class A immutability — no CI infra; hash-manifest present but uncited",
    "Finding 5: impl test count reconciled in 72713a6",
    "Finding 6: ci Class B scope inventory incomplete",
    "Finding 7: Repository field metadata mismatch x5"
  ]
}
```
