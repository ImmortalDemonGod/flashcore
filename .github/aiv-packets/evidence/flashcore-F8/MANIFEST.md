# F8 prove-it Evidence Manifest

Finding: F8 — missing `timedelta` import in `tests/conftest.py`
Baseline ref: `fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965` (origin/main)
HEAD ref: `646f6f31f296dd39de256355bd6e06a22d987ee7` (fix/flashcore-F8)
Date: 2026-06-24

| sha256 | artifact | claim proven | cited baseline ref | AIV class |
|--------|----------|--------------|-------------------|-----------|
| `17fd8679d283eb978fdfed0929627dab727fd330e9d29295ad659a4c3b18ce6b` | `baseline_red.txt` | DEFECT CONFIRMED at fb1ae5a: 4 ERRORs (NameError: timedelta not defined in conftest.py) + 1 FAIL (timedelta absent from conftest namespace) on RED tests | fb1ae5a | A + D |
| `6a088be650fd73cd5f8fb0850a873a77e0455e21f23c63569225825148d8a2e9` | `head_green.txt` | FIX CONFIRMED at HEAD: all 6 RED tests PASS; fixtures resolve without NameError; timedelta present in conftest namespace | fb1ae5a (diff against) | A + D |
| `6f62eee01613950128f7370bff1d11d94ebaac353b275f6bf294337efed2babd` | `head_full_suite.txt` | Full suite at HEAD: 499 passed, 1 skipped — zero regressions from the import change | fb1ae5a | A |
| `93f617c3a8df27443794d49f078ebe1dcd0b9babe395dab20060c724dd376ef0` | `import_diff.txt` | Before/after diff of conftest.py import line bound to fb1ae5a vs 646f6f3; shows `timedelta` added to datetime import | fb1ae5a | D |
| `a19a550089ec6872568b37c49bf27b01b4c4f50b2d9842b3d46063bdfdfb06bc` | `class_c_negative.txt` | Class C: bare `timedelta` symbol not imported in any `flashcore/` production file; flashcore/scheduler.py uses `datetime.timedelta` (qualified form only); change is test-only | fb1ae5a | C |

## Independent assessor verdicts

| artifact | verdict | note |
|---|---|---|
| baseline_red.txt | CONFIRMED | NameError traces directly to conftest.py:180 and :202 |
| head_green.txt | CONFIRMED | All 6 RED tests pass; namespace probe passes |
| head_full_suite.txt | CONFIRMED | 499 passed, 1 skipped, zero failures |
| import_diff.txt | CONFIRMED | `timedelta` addition corroborated by live conftest.py line 6 |
| class_c_negative.txt | CONFIRMED (with clarification) | `datetime.timedelta` (qualified) appears in scheduler.py — bare name not imported; claim holds |

## Anti-theater summary

- **baseline_red.txt** run in `git worktree add /tmp/flashcore-F8_base origin/main` (HEAD `fb1ae5a`), RED test file copied in. NameError traces to `conftest.py:180` and `conftest.py:202` exactly.
- **head_green.txt** run on real system at HEAD (`646f6f3`) using system Python 3.13.12. No mocks, no stubs.
- Worktree removed after evidence capture: `git worktree remove /tmp/flashcore-F8_base --force`
