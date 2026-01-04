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
<!-- Prove absence: no deleted tests, no removed dependencies, no config usage -->

**Claim 3: No regressions**
- Zero deleted assertions or test functions
- Verification: `git diff main...BRANCH -- tests/ | grep -E "^-.*assert|^-.*def test_"` → 0 results

**Claim X: No [unwanted dependency]**
- Verification: `grep -rn "pattern" path/` → No matches

### Class L (UI/Visual Evidence)
<!-- REQUIRED if user-visible changes. Use GIF/Loom, not static screenshots -->

- **Before:** [Loom/GIF link]
- **After:** [Loom/GIF link]
- **Interaction flow:** [Description]

### Class D (State Evidence)
<!-- DB schema, migrations, state transitions (if applicable) -->

- N/A (or provide schema dumps, migration output)

---

## Reproduction
<!-- Copy-pastable commands for verifier to inspect evidence -->

**Verify [Claim X]:**
```bash
command-to-verify
# Expected: [expected output]
```

**Run Tests:**
```bash
pytest tests/ -v
# Expected: XXX passed
```

**Check Coverage:**
```bash
pytest tests/ --cov=module --cov-report=term-missing
# Expected: XX% overall coverage
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
