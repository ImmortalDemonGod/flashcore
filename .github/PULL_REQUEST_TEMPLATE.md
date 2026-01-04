# AIV Verification Packet (v2.1)

**Commit:** `<latest-commit-sha>`  
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

> [!IMPORTANT]
> **Immutability Requirement (Addendum 2.2):**
> - All Class E links MUST use commit SHAs, NOT `main`/`master`/`develop` branches
> - All Class B code links MUST use commit SHAs, NOT mutable branch names
> - CI run links are naturally immutable (actions/runs/XXXXXX)
> - **Validation will FAIL if mutable branch links are detected**
>
> ✅ Good: `/blob/a1b2c3d/file.py` or `/actions/runs/12345`  
> ❌ Bad: `/blob/main/file.py` or `/tree/develop/`

---

## Claim(s)
<!-- List atomic, falsifiable claims. Number each claim. Map to task requirements if applicable. -->

1. [Primary claim - what changed]
2. [Quality claim - tests/coverage/linting]
3. [Safety claim - no regressions]

---

## Evidence

### Class E (Intent Alignment)
<!-- ⚠️ CRITICAL: Must use commit SHA, NOT main/master/develop branch -->
<!-- Example: /blob/a1b2c3d/.taskmaster/tasks/tasks.json (NOT /blob/main/...) -->

- **Link:** [Task #X - "Task Title"](https://github.com/OWNER/REPO/blob/COMMIT_SHA/.taskmaster/tasks/tasks.json#LXX-YY)
- **Requirements Verified:**
  1. ✅ [Requirement 1]
  2. ✅ [Requirement 2]

### Class B (Referential Evidence)
<!-- ⚠️ CRITICAL: All code links must use commit SHA permalinks -->
<!-- Get permalink: View file on GitHub → Press 'y' key → Copy URL -->

**Claim 1: [Description]**
- [`path/to/file.py`](https://github.com/OWNER/REPO/blob/COMMIT_SHA/path/to/file.py) - Description
- Signature: [`def function(...)`](https://github.com/OWNER/REPO/blob/COMMIT_SHA/path/to/file.py#LXX)

### Class A (Execution Evidence)
<!-- CI run links are naturally immutable (actions/runs/XXXXXX) -->
<!-- Link to SPECIFIC run number, not "latest" or workflow file -->

**Claim 2: All tests pass**
- [CI Run #XXXXXXX - All Jobs Successful](https://github.com/OWNER/REPO/actions/runs/XXXXXXX)
  - ✅ tests_linux (3.10, ubuntu-latest)
  - ✅ tests_linux (3.11, ubuntu-latest)
  - ✅ tests_mac (3.10, macos-latest)
  - ✅ tests_mac (3.11, macos-latest)
  - ✅ tests_win (3.10, windows-latest)
  - ✅ tests_win (3.11, windows-latest)

**Claim X: Coverage metrics**
- `module.py`: XX% coverage (YY lines, ZZ uncovered)
- **Overall: XX%**

### Class C (Negative Evidence - Conservation)
<!-- ⚠️ CRITICAL: Use CI artifact links, not "trust me I ran grep" -->
<!-- The CI job "negative-checks" produces architecture_lint.txt artifact -->

**Claim 3: No regressions**
- **Evidence:** [Anti-Cheat Report Artifact](https://github.com/OWNER/REPO/actions/runs/XXXXXX/artifacts/YYYYY)
- Shows: 0 deleted assertions, 0 added skips
- CI Job: `anti-cheat-warning` step

**Claim X: No [unwanted dependency] in [module]**
- **Evidence:** [Architecture Lint Artifact](https://github.com/OWNER/REPO/actions/runs/XXXXXX/artifacts/YYYYY)
- Shows: `✅ PASS: No [pattern] references found`
- CI Job: `negative-checks` → `Architecture Lint - Database Layer` step
- **Methodology:** `grep -rn "pattern" path/` (executed by CI, not verifier)

### Class L (UI/Visual Evidence)
<!-- REQUIRED if user-visible changes. Use GIF/Loom, not static screenshots -->

- **Before:** [Loom/GIF link]
- **After:** [Loom/GIF link]
- **Interaction flow:** [Description]

### Class D (State Evidence)
<!-- DB schema, migrations, state transitions (if applicable) -->

- N/A (or provide schema dumps, migration output)

---

## Verification Methodology
<!-- ⚠️ Zero-Touch Mandate: These commands show HOW evidence was generated -->
<!-- The verifier inspects ARTIFACTS, not runs commands locally -->
<!-- Primary proof = CI artifact link. Commands = context only. -->

**How [Claim X] was verified:**
```bash
command-used-to-generate-evidence
# Result: [actual output that became the artifact]
```

**How tests were verified:**
```bash
pytest tests/ -v
# Result: XXX passed (see CI Run #XXXXXX)
```

**How coverage was measured:**
```bash
pytest tests/ --cov=module --cov-report=term-missing
# Result: XX% overall (see CI coverage report)
```

---

## Summary

**Task #X "[Task Title]" - COMPLETE**

All N subtask requirements verified:
1. ✅ [Requirement 1]
2. ✅ [Requirement 2]

**Quality Metrics:**
- XX% test coverage
- All CI/CD checks passing
- Zero functional regressions

**Zero-Touch Verification:** All evidence provided via immutable CI artifacts at commit `<commit-sha>`.

---

_This packet certifies that all claims are supported by the linked, reproducible evidence per AIV Protocol v2.0 + Addendum 2.7 (Zero-Touch Mandate)._
