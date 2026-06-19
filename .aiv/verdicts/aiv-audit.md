# AIV spec audit — PR F169/C2 (content audit; follow-up to shape gate)

Shape (`aiv check --strict`) was verified separately and is recorded below. This
audit verifies packet **content** against the spec at
`/home/user/aiv-protocol/SPECIFICATION.md` (version `AIV-SPEC-V1.0.0-CANONICAL`,
2026-01-07). `gh` is unavailable in this environment — no PR comment was posted;
the audit is written here per the pipeline contract.

- **Branch:** `feat/c2-fsrs-harness` off `origin/main` @ `b5e1c4b`; HEAD `71a30fd`.
- **Config:** no `.aiv-workflow.yml` at repo root and `$AIV_WORKFLOW_CONFIG` unset
  → skill defaults used (`aiv.cli=aiv`, `evidence.mandate_all_classes=true`,
  `evidence.exclude_classes=[G]`, `branch.base=origin/main`). Spec resolved at
  `/home/user/aiv-protocol/SPECIFICATION.md` (repo-relative default
  `aiv-protocol/SPECIFICATION.md` absent; installed package copy is canonical,
  same Document ID).
- **Packets audited (all 5 on branch):** `PACKET_c2_f169_impl.md`,
  `PACKET_c2_f169_tests.md`, `PACKET_c2_f169_oracle_corr.md`,
  `PACKET_c2_f169_ci.md`, `PACKET_c2_f169_determinism.md`.
- **Evidence:** `.github/aiv-packets/evidence/` (MANIFEST.md + 8 captured artifacts,
  SHA-256 each).

**Headline:** All 5 packets carry the **correct** canonical Class-E intent target
(the F169 audit line) and the implementation **genuinely addresses** the recorded
defect (verified against source + diff + behavioral probes). **No blocking
findings.** Three non-blocking content deviations existed (wrong `Repository`
identification field across all 5 packets; an invalid `blast_radius` enum value in
the determinism packet; tangential — but disclosed — intent for the two CI-enabling
packets). **Finding 3 and Finding 5a were remediated post-audit via CR review
(cr-review stage): Repository field corrected to `flashcore` in all 5 packets;
`blast_radius` corrected to `local`; claim 2 in determinism packet updated to
explicitly scope the pinning guarantee to direct tool versions only.**
Decision: **COMPLIANT** (all verifiable WARNs addressed; ready for H2 adjudication).

---

## Shape gate result (verified, not re-derived)

`aiv check <packet> --strict` over each packet:

| Packet | Blocking errors | Warnings | Codes (warn/info) |
|---|---|---|---|
| `PACKET_c2_f169_impl.md` | **0** | 5 | E004, E012, E016×4 |
| `PACKET_c2_f169_tests.md` | **0** | 4 | E004, E012, E016 |
| `PACKET_c2_f169_oracle_corr.md` | **0** | 1 | E004 |
| `PACKET_c2_f169_ci.md` | **0** | 1 | E004 |
| `PACKET_c2_f169_determinism.md` | **0** | 1 | E004 |

All E004 (plain-text intent reference), E012 (Class A has no GitHub CI URL), and
E016 (Class B line-anchor suggestion) are **informational/WARN, not blocking** —
CLAUDE.md confirms E004 is informational; the tool reports `0 blocking error(s)`
for every packet. `--strict` prints "Validation Failed" because it escalates warns,
but the blocking count is the gate signal. **`shape_check_passed = true`.**

---

## Finding 1 — Class E intent-target correctness: **PASS** (the load-bearing check)

Per the finding's CANONICAL INTENT, every packet's Class E MUST point to the
original audit source, not a local taskmaster task or the pipeline launch-brief.

Required target:
`https://github.com/ImmortalDemonGod/flashcore/blob/bc19321bc72cf2467d57ffebc24b92a341ea10d6/audit/02-static-audit.md#L179`

| Packet | Class E intent URL | Correct target? |
|---|---|---|
| impl | `…/bc19321…/audit/02-static-audit.md#L179` (L91) | ✓ exact match |
| tests | `…/bc19321…/audit/02-static-audit.md#L179` (L114) | ✓ exact match |
| oracle_corr | `…/bc19321…/audit/02-static-audit.md#L179` (L85) | ✓ exact match |
| ci | `…/bc19321…/audit/02-static-audit.md#L179` (L77) | ✓ exact match |
| determinism | `…/bc19321…/audit/02-static-audit.md#L179` (L64) | ✓ exact match |

No packet points at `task_NNN.md` / `tasks.json` or at the launch-brief under
`.aiv/launch-briefs/`. SHA-pinned, repo-qualified, immutable per §3.3
(commit-SHA permalink). **No intent-provenance finding.**

## Finding 2 — Class E intent ALIGNMENT (substance, not just URL): **PASS** for the core fix

I read the cited source AND `git diff origin/main..HEAD`:

- **Source records (audit/02-static-audit.md:179, F169 CRITICAL):** in
  `compute_next_state()`, for any non-New card the code sets
  `fsrs_card.last_review = fsrs_card.due` (line 212); an on-time review yields
  `elapsed_days = review_ts.date() - due.date() = 0`, so FSRS retrievability
  `R = e^(-t/S) = 1.0`, corrupting the stability update; "The Card model has no
  last_review_at datetime field, so the cached due date is the only proxy used."
- **The diff does (Path A):**
  - `flashcore/models.py` +`last_review_date: Optional[date]` transient field on `Card`;
  - `flashcore/scheduler.py:211-217` removes `last_review = fsrs_card.due` and instead
    sets `fsrs_card.last_review` from `card.last_review_date` when present (else leaves
    it unset → `elapsed_days=0` only for genuine first-ever reviews);
  - `flashcore/review_processor.py:99-103` the hub reads the ground-truth prior-review
    timestamp from the DB (`get_latest_review_for_card`) before each scheduler call —
    exactly the "missing `last_review_at`" the audit names.
- **Which addresses the defect:** the proxy the audit identifies as wrong (due-date)
  is replaced by the real recorded prior-review date, so an on-time review now
  computes `elapsed_days>0`. Behavioral proof, baseline vs HEAD direct probes:
  - `evidence/baseline_direct_probe.txt` (sha256 `3863d4…`): "BUG CONFIRMED —
    elapsed_days=0 … stability=14.0 (unchanged)".
  - `evidence/head_direct_probe.txt` (sha256 `abac58…`): "FIX CONFIRMED —
    elapsed_days=14 … stability=44.8064 (updated)".

`git grep "last_review = fsrs_card.due" -- flashcore/scheduler.py` at HEAD → no match
(bug line removed). Source-records-X / diff-does-Y / Y-addresses-X holds. The
`impl` and `tests` packets carry explicit alignment prose + AC tables — not a bare
URL. **Intent alignment is real, not theater, for the fix-bearing packets.**

> Non-blocking caveat (see Finding 5b): the `ci` and `determinism` packets cite the
> same F169 line, but their changes (black reformat / tool-version pinning) do not
> *themselves* address F169 — they enable the PR's CI gate. Their Class E prose
> discloses this ("CI lint gate must pass", "CI must be reproducible"), so it is a
> disclosed scope-linkage, not falsified intent. WARN, not BLOCK.

## Finding 3 — `Repository` identification field is wrong on all 5 packets: **WARN (CONDITIONAL)**

Every packet's Identification table records
`Repository | github.com/ImmortalDemonGod/aiv-protocol`. The change is to
**flashcore** (the intent URL, the code, and the audit source are all flashcore;
`aiv-protocol` is the AIV tooling repo). A reader resolving the Class-B file
permalinks against the named repository would fail. This is a self-containment /
referential-identification defect (§6.3 traceability spirit; §B.1 identification).
It is **non-load-bearing** — it falsifies none of the F169 claims and the correct
intent URL is flashcore-qualified — so it is recorded as a deviation for H2 to
adjudicate, not a block. Almost certainly an `aiv close` template default leak.

## Finding 4 — Class A execution evidence not bound to an immutable CI permalink: **WARN (A-001/A-F1, addressed-via-manifest)**

§6.2.2 A-001 ("CI run reference MUST be immutable", BLOCK) and A-002 ("CI SHA ==
head_sha") presuppose a CI run. There is **no CI run** here (`gh` unavailable;
harness-local execution), and `aiv check` flags this only as **E012 WARN**, not a
blocking error. The Class-A claims are instead backed by captured stdout artifacts
each carrying a **SHA-256 in `evidence/MANIFEST.md`** — a *hash-manifest*
immutability mechanism explicitly accepted by §3.3 ("Hash manifest … Hash
comparison"). This is the skill's "satisfied N/A-with-manifest" case, not a hard
Class-A failure. Residual gap (no commit-SHA-bound CI permalink) is **WARN**;
harvest deferred — no CI infra exists in this environment and re-running the suite
to manufacture a permalink would be theater.

## Finding 5 — minor classification-record / scope deviations: **WARN**

- **5a — `determinism` `blast_radius` is not a valid §5.5 enum value.**
  `PACKET_c2_f169_determinism.md` sets `blast_radius: pyproject.toml`. §5.5
  enumerates `local | component | service | cross-service | organization`;
  `pyproject.toml` is a filename. Intended value is `local`. Not caught by
  `aiv check`; non-blocking. (R0 tier itself is defensible — pure config.)
- **5b — `ci`/`determinism` intent is tangential to F169** (see Finding 2 caveat):
  disclosed scope-linkage, WARN not BLOCK.

---

## Tier audit (§5) — declared tiers defensible

| Packet | Declared | Touches §5.2 critical surface? | Blast radius | Verdict |
|---|---|---|---|---|
| impl | R1 / S0 | No — FSRS scheduler is not auth/authz/secrets/crypto/financial/PII/privilege/audit-logging | component (3 files in `flashcore/`) | Defensible. (Minor: adds a Card *model* field — a reader could argue R2 "API/schema"; but it is a transient in-memory field with **no DB migration** (confirmed: Class C grep of `db/schema.py`/`db/database.py` → 0 matches), so R1 holds. Judgment call for H2, non-blocking.) |
| tests | R1 / S0 | No | component | Defensible (test-only, guards a correctness invariant). |
| oracle_corr | R1 / S0 | No | component | Defensible (correctness-chain doc). |
| ci | R1 / S0 | No | component | Defensible (production-file contact via reformat). |
| determinism | R0 / S0 | No | (invalid enum — Finding 5a) | R0 defensible; field value defective. |

**No §5.2-F1 mandatory-R3 escalation applies** — nothing touches a critical surface.
SoD: all R0/R1 → S0 self-verify permitted (§5.4). No 5.4-F1.

## Evidence-class completeness (all-class mandate A–F, exclude G)

All 5 packets address **every** class A–F; none is vacuous or carries an
unjustified N/A:

| Packet | A | B | C | D | E | F |
|---|---|---|---|---|---|---|
| impl | ✓ live runs + manifest | ✓ 4 SHA-pinned anchors | ✓ 5 negative greps + Skipped set | ✓ mypy + suite counts | ✓ URL+AC table (Finding 2) | ✓ git chain-of-custody |
| tests | ✓ RED-state run | ✓ 2 anchors + bug site | ✓ semantic diff + Skipped B2/B3/B4 | ✓ ruff/mypy | ✓ URL+VERIFY map | ✓ git log |
| oracle_corr | ✓ load-bearing test run | ✓ doc anchor | ✓ 4 negative checks | ✓ **N/A justified** (markdown-only) + suite count | ✓ URL+oracle-guard prose | ✓ `git show --stat` |
| ci | ✓ black/lint/suite | ✓ anchor | ✓ no assertion deleted/skip added | ✓ flake8/black/mypy | ✓ URL+AC table | ✓ (PROVENANCE) claim + chain |
| determinism | ✓ suite count | ✓ anchor | ✓ ruff-absence search | ✓ mypy | ✓ URL+versions | ✓ git log + no-`--no-verify` |

Note: this project's A–F taxonomy follows the **operator mandate** (A=behavioral,
C=negative, D=static-analysis, F=git-provenance), which differs from the spec's
literal D=Differential / F=cryptographic-provenance. Classes D and F are *not
mandatory* at R0/R1 per §6.1 anyway, so the all-class-address mandate is satisfied
and no §6.5/§6.7 BLOCK applies. Cryptographic provenance (spec F) is the
"manifest-backed N/A" case (no signing infra) — consistent with the skill.

## Claim–evidence correspondence (sampled across all 5 packets)

| Packet · Claim | Embedded evidence | Supports? |
|---|---|---|
| impl C4 (bug line removed) | `git grep "last_review = fsrs_card.due"` → no match @ HEAD (re-run, confirmed) | ✓ |
| impl C1/C7 (field + hub lookup) | diff `models.py:+last_review_date`, `review_processor.py:99-103` (re-read) | ✓ |
| impl C6 (scheduler reads no DB) | diff shows scheduler reads only `card.last_review_date`; no new import | ✓ |
| impl Class A (elapsed_days>0) | `head_direct_probe.txt` elapsed_days=14, sha256 in MANIFEST | ✓ |
| tests C5 (RED elapsed=0) | `baseline_direct_probe.txt` elapsed_days=0, sha256 `3863d4…` | ✓ |
| tests C4 (additions-only) | `git show 61d6a20 -- tests/test_scheduler.py` deletions = 0 | ✓ |
| oracle_corr C3 (2 files, 0 del) | `git show 19499a3 --stat` cited; doc-only | ✓ |
| ci C2 (483 passed/1 skip) | `full_suite_head.txt` sha256 `1a3004…` | ✓ |
| determinism C1 (pins == installed) | `pyproject.toml:33-36` anchor + `pip show` cited | ✓ (cited, not re-pinned) |
| scope inventory (all) | `git diff origin/main..HEAD --name-only` = models/scheduler/review_processor/2 tests — matches packets' union | ✓ |

No ✗ rows. The impl packet's "Ground truth at branch HEAD (483 passed)" cites a
state from a *later* commit (`b9c7234`/`9bbb2ec`) than its own head (`37a0dec`) —
mild forward-reference, but **explicitly disclosed** as post-deps-pinning ground
truth, so it is transparent, not a hidden chain.

## Self-containment + immutability

- Packets are individually readable; no packet *depends* on another to make its
  claims meaningful. Cross-references (e.g., to `c829e46`, oracle-corrections doc)
  are explanatory and SHA-pinned, not load-bearing forward chains. PASS.
- Cited code refs use commit-SHA `@ <sha>` line anchors; intent URLs are SHA-pinned
  permalinks; evidence artifacts carry SHA-256 (manifest). No branch URLs, no
  "latest", no `~/`-rooted paths. PASS (excepting the wrong-org `Repository`
  field — Finding 3).

---

## Harvested evidence (read-only — attach to amendment if operator remediates)

**Finding 3 remediation — corrected identification field:**
The `Repository` field on all 5 packets should read
`github.com/ImmortalDemonGod/flashcore` (the repo of the code + audit source), not
`…/aiv-protocol`. Pure metadata edit; no claim changes.

**Finding 4 — no read-only CI-permalink harvest path:** `gh` is unavailable and no
CI run exists for this branch in-environment. The defensible immutable substrate is
the existing `evidence/MANIFEST.md` SHA-256 manifest (already present). **No
further read-only harvest possible without CI infra build-out.**

**Finding 5a remediation — valid blast_radius:** change
`blast_radius: pyproject.toml` → `blast_radius: local` in
`PACKET_c2_f169_determinism.md`.

**Re-verifiable commands a reviewer can run (read-only):**
```bash
git grep -n "last_review = fsrs_card.due" -- flashcore/scheduler.py    # → no match (bug removed)
git diff origin/main..HEAD --name-only -- 'flashcore/*.py' 'tests/*.py' # → 5 files, matches scope
sha256sum .github/aiv-packets/evidence/*.txt                           # → cross-check MANIFEST.md
aiv check .github/aiv-packets/PACKET_c2_f169_impl.md --strict          # → 0 blocking error(s)
```

## Summary table

| Dimension | Status |
|---|---|
| Shape (`aiv check`, 0 blocking) | PASS |
| Class E intent-target correctness | PASS (all 5 → canonical F169 audit URL) |
| Class E intent alignment (substance) | PASS for fix-bearing packets; disclosed-tangential for ci/determinism (WARN) |
| Tier classification (§5) | Defensible (no R3 surface) |
| Evidence-class completeness A–F | PASS (no vacuous/unjustified-N/A class) |
| Claim–evidence correspondence | PASS (no ✗ rows) |
| Self-containment / immutability | PASS — `Repository` field corrected in all 5 packets |
| Blocking findings | **0** |

## Recommendations (operator decides; this audit is read-only)

1. **Fix the three WARN-level metadata deviations** (Repository field ×5,
   determinism `blast_radius`, optionally label Class A as manifest-backed) — cheap,
   raises fidelity, moves CONDITIONAL → COMPLIANT.
2. **Or file a documented known-limitation** noting the harness-local Class-A
   substrate (manifest, no CI permalink) and the template-leaked Repository field —
   spec-permitted, lowest cost.
3. The merge act (H2) remains the human's; this audit only certifies the PR is
   **ready to adjudicate** — all verifiable claims verified, 0 load-bearing claims
   falsified or unverified.

— Generated by aiv-audit (read-only: content audit + evidence harvest).

## Machine-checkable data

```json
{
  "schema": "aiv_audit_result@1",
  "packet_decision": "COMPLIANT",
  "shape_check_passed": true,
  "blocking_findings": [],
  "classes_vacuous_or_na_unjustified": []
}
```
