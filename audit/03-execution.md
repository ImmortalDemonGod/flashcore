# 03 — Execution

_Generated 2026-06-17 21:55:05 · branch `claude/nifty-brahmagupta-0tq0vy` · forensic-audit-pipeline (consolidated)_

**Measured coverage:** 93% ⚠️ (NOT confirmed by the verifier).


## Observed behaviors

| Entry | Behavior |
| --- | --- |
| make test → pytest tests/ via Makefile | 480 tests passed, 1 skipped, 93% line coverage across 26 flashcore modules. All assertions satisfied; no test triggered a RuntimeError or assertion failure during production-code execution. |
| flashcore/review_manager.py:initialize_session | Called by test suite (98% file coverage, lines 206-207 missed). Review queue construction at line 109 executed: cards fetched by DB due-date order then re-sorted by modified_at without test detecting the ordering change. |
| flashcore/scheduler.py:compute_next_state | Called at 96% file coverage (lines 71, 176, 236 missed). Lines 211-212 (last_review=due_date assignment) executed; tests passed without asserting on elapsed_days value or FSRS retrievability. |
| flashcore/session_manager.py:record_card_review | Called at 95% coverage (lines 522-559, 758-760 missed). Lines 205-213 (deck_access_order append guard) and line 643 (deck_switch_efficiency formula) both executed; no test asserted on correct deck-switch count or efficiency clamp. |
| flashcore/cli/_vet_logic.py:_validate_and_normalize_card | Executed at 99% coverage (line 135 missed). Line 80 (Card(**mapped_card_dict)) executed with mapped dict that retains 's' and 'id' keys; tests did not supply cards with those fields, so no ValidationError was triggered. |
| flashcore/db/database.py (multiple functions) | 81% coverage, 84 lines missed. Core CRUD paths executed; error-handling branches (rollback paths, constraint violations, large-batch edge cases) not reached. |
| flashcore/db/db_utils.py:create_backup | 85% coverage; lines 219-249 (backup filename construction and file-copy operations) not executed. Naive local-time datetime at line 269 was NOT in the missed set—it was executed—but no test verified timezone correctness. |
| pytest direct invocation (without make) | Commands 'pytest -v ...' and 'pytest tests/ -q ...' both failed with exit code 4: ModuleNotFoundError for pydantic when invoked outside the venv. Only 'make test' (which activates the venv) succeeded. |

## Finding deltas (runtime)

| ID | Delta | Class | Note/Evidence |
| --- | --- | --- | --- |
| F1 | confirmed | — | All cited line(s) [109] in flashcore/review_manager.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F2 | confirmed | — | All cited line(s) [80] in flashcore/cli/_vet_logic.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F3 | refined | — | Cited range includes both covered lines [276, 277, 278, 279] and uncovered lines [135] in flashcore/cli/_vet_logic.py. Part of the described behavior ran (covered lines confirm presence of the pattern); uncovered lines were not exercised. |
| F4 | confirmed | — | All cited line(s) [211, 212] in flashcore/scheduler.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F5 | confirmed | — | All cited line(s) [205, 206, 207, 208, 209, 210, 211, 212, 213] in flashcore/session_manager.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F6 | confirmed | — | All cited line(s) [643] in flashcore/session_manager.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F7 | confirmed | — | All cited line(s) [269] in flashcore/db/db_utils.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F8 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F9 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F10 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F11 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F12 | untested | — | Non-Python file (.github/init.sh:35-36,63); Python line coverage does not apply. |
| F13 | untested | — | Non-Python file (.github/init.sh:36,63); Python line coverage does not apply. |
| F14 | refined | — | File-level location; flashcore/yaml_validators.py has partial coverage (2 missed lines). Parts of the described behavior may be untested. |
| F15 | untested | — | Non-Python file (flashcore/scripts/dump_history.py:45); Python line coverage does not apply. |
| F16 | untested | — | Non-Python file (.github/workflows/rename_project.yml:6); Python line coverage does not apply. |
| F17 | untested | — | Non-Python file (.github/workflows/rename_project.yml:43); Python line coverage does not apply. |
| F18 | untested | — | Non-Python file (.github/workflows/aiv-guard.yml:33); Python line coverage does not apply. |
| F19 | untested | — | Non-Python file (.github/workflows/main.yml:25-26,.github/workflows/release.yml:21,38,.github/workflows/rename_project.yml:13,39,.github/workflows/aiv-guard.yml:21,26); Python line coverage does not apply. |
| F20 | untested | — | Non-Python file (.github/workflows/rename_project.yml:37); Python line coverage does not apply. |
| F21 | untested | — | Non-Python file (.github/rename_project.sh:26-30); Python line coverage does not apply. |
| F22 | confirmed | — | All cited line(s) [93] in flashcore/yaml_models.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F23 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F24 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F25 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F26 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F27 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F28 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F29 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F30 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F31 | untested | — | Non-Python file (Containerfile:1); Python line coverage does not apply. |
| F32 | untested | — | Non-Python file (.github/workflows/main.yml:25); Python line coverage does not apply. |
| F33 | untested | — | Non-Python file (.github/workflows/release.yml:51); Python line coverage does not apply. |
| F34 | untested | — | Non-Python file (.aiv.yml:13); Python line coverage does not apply. |
| F35 | confirmed | — | flashcore/cli/_review_logic.py is 100% covered; all statements exercised, the described behavior ran without test detection. |
| F36 | untested | — | Non-Python file (Makefile:101); Python line coverage does not apply. |
| F37 | untested | — | Non-Python file (.env.example:1); Python line coverage does not apply. |
| F38 | untested | — | Non-Python file (.github/init.sh:62); Python line coverage does not apply. |
| F39 | refined | — | Cited range includes both covered lines [543, 544, 545, 546, 547, 548, 549] and uncovered lines [525, 526] in flashcore/cli/main.py. Part of the described behavior ran (covered lines confirm presence of the pattern); uncovered lines were not exercised. |
| F40 | untested | — | Non-Python file (Makefile:83); Python line coverage does not apply. |
| F41 | untested | — | Non-Python file (.windsurfrules:1); Python line coverage does not apply. |
| F42 | confirmed | — | flashcore/models.py is 100% covered; all statements exercised, the described behavior ran without test detection. |
| F43 | refined | — | File-level location; flashcore/db/database.py has partial coverage (84 missed lines). Parts of the described behavior may be untested. |
| F44 | untested | — | Non-Python file (mkdocs.yml:1); Python line coverage does not apply. |
| F45 | untested | — | Non-Python file (requirements-test.txt:1); Python line coverage does not apply. |
| F46 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F47 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F48 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F49 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F50 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F51 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F52 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F53 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F54 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F55 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F56 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F57 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F58 | confirmed | — | flashcore/cli/_review_logic.py is 100% covered; all statements exercised, the described behavior ran without test detection. |
| F59 | refined | — | File-level location; flashcore/db/database.py has partial coverage (84 missed lines). Parts of the described behavior may be untested. |
| F60 | confirmed | — | All cited line(s) [292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325] in flashcore/yaml_models.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F61 | refined | — | File-level location; flashcore/yaml_validators.py has partial coverage (2 missed lines). Parts of the described behavior may be untested. |
| F62 | confirmed | — | All cited line(s) [269] in flashcore/db/db_utils.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F63 | refined | — | Cited range includes both covered lines (489-521) and uncovered lines [522, 523, 525, 530, 531, 532, 538, 553, 555, 557, 558, 559] in flashcore/session_manager.py. Part of the described behavior ran (covered lines confirm presence of the pattern); uncovered lines were not exercised. |
| F64 | confirmed | — | All cited line(s) [112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158] in flashcore/cli/_review_all_logic.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F65 | confirmed | — | flashcore/exceptions.py is 100% covered; all statements exercised, the described behavior ran without test detection. |
| F66 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F67 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F68 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F69 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F70 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F71 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F72 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F73 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F74 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F75 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F76 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F77 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F78 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F79 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F80 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F81 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F82 | confirmed | — | flashcore/cli/review_ui.py is 100% covered; all statements exercised, the described behavior ran without test detection. |
| F83 | confirmed | — | All cited line(s) [59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80] in flashcore/cli/_vet_logic.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F84 | confirmed | — | All cited line(s) [204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214] in flashcore/session_manager.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F85 | confirmed | — | flashcore/cli/_review_logic.py is 100% covered; all statements exercised, the described behavior ran without test detection. |
| F86 | confirmed | — | All cited line(s) [277, 278] in flashcore/cli/_vet_logic.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F87 | confirmed | — | All cited line(s) [211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224] in flashcore/scheduler.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F88 | confirmed | — | All cited line(s) [643, 644] in flashcore/session_manager.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F89 | confirmed | — | All cited line(s) [269] in flashcore/db/db_utils.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F90 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F91 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F92 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F93 | confirmed | — | All cited line(s) [267] in flashcore/yaml_validators.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F94 | untested | — | Non-Python file (.github/rename_project.sh:26-29); Python line coverage does not apply. |
| F95 | untested | — | Non-Python file (.github/workflows/rename_project.yml:37); Python line coverage does not apply. |
| F96 | untested | — | Non-Python file (.github/workflows/rename_project.yml:6); Python line coverage does not apply. |
| F97 | untested | — | Non-Python file (.github/workflows/aiv-guard.yml:33); Python line coverage does not apply. |
| F98 | untested | — | Non-Python file (Containerfile:1-5); Python line coverage does not apply. |
| F99 | untested | — | Non-Python file (.github/init.sh:63); Python line coverage does not apply. |
| F100 | confirmed | — | All cited line(s) [91, 92] in flashcore/yaml_models.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F101 | confirmed | — | All cited line(s) [120, 121, 122, 123] in flashcore/db/db_utils.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F102 | untested | — | Non-Python file (Containerfile:2); Python line coverage does not apply. |
| F103 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F104 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F105 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F106 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F107 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F108 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F109 | untested | — | Non-Python file (Containerfile:1); Python line coverage does not apply. |
| F110 | untested | — | Non-Python file (.github/workflows/release.yml:51); Python line coverage does not apply. |
| F111 | refined | — | File-level location; flashcore/yaml_validators.py has partial coverage (2 missed lines). Parts of the described behavior may be untested. |
| F112 | confirmed | — | All cited line(s) [543] in flashcore/cli/main.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F113 | untested | — | Non-Python file (.github/workflows/aiv-guard.yml:21); Python line coverage does not apply. |
| F114 | confirmed | — | flashcore/cli/_review_logic.py is 100% covered; all statements exercised, the described behavior ran without test detection. |
| F115 | confirmed | — | All cited line(s) [86, 87] in flashcore/scheduler.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F116 | confirmed | — | All cited line(s) [278] in flashcore/cli/_vet_logic.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F117 | untested | — | Non-Python file (.aiv.yml:13); Python line coverage does not apply. |
| F118 | untested | — | Non-Python file (.windsurfrules:1); Python line coverage does not apply. |
| F119 | confirmed | — | flashcore/models.py is 100% covered; all statements exercised, the described behavior ran without test detection. |
| F120 | untested | — | Non-Python file (Makefile:101); Python line coverage does not apply. |
| F121 | untested | — | Non-Python file (.env.example:1); Python line coverage does not apply. |
| F122 | untested | — | Non-Python file (requirements-test.txt:1); Python line coverage does not apply. |
| F123 | refined | — | File-level location; flashcore/db/database.py has partial coverage (84 missed lines). Parts of the described behavior may be untested. |
| F124 | confirmed | — | All cited line(s) [185] in flashcore/cli/_review_all_logic.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F125 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F126 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F127 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F128 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F129 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F130 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F131 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F132 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F133 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F134 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F135 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F136 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F137 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F138 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F139 | confirmed | — | flashcore/cli/_review_logic.py is 100% covered; all statements exercised, the described behavior ran without test detection. |
| F140 | confirmed | — | All cited line(s) [156, 157, 158] in flashcore/db/db_utils.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F141 | confirmed | — | All cited line(s) [140, 141, 142, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158] in flashcore/cli/_review_all_logic.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F142 | refined | — | File-level location; flashcore/yaml_validators.py has partial coverage (2 missed lines). Parts of the described behavior may be untested. |
| F143 | confirmed | — | flashcore/cli/review_ui.py is 100% covered; all statements exercised, the described behavior ran without test detection. |
| F144 | untested | — | Non-Python file (flashcore/scripts/migrate.py:184-204); Python line coverage does not apply. |
| F145 | confirmed | — | All cited line(s) [183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200] in flashcore/cli/_review_all_logic.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F146 | confirmed | — | All cited line(s) [292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323] in flashcore/yaml_models.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F147 | confirmed | — | All cited line(s) [248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320] in flashcore/review_manager.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F148 | confirmed | — | All cited line(s) [269] in flashcore/db/db_utils.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F149 | refined | — | Cited range includes both covered lines [50, 54, 55, 56, 57, 58] and uncovered lines [53] in flashcore/cli/main.py. Part of the described behavior ran (covered lines confirm presence of the pattern); uncovered lines were not exercised. |
| F150 | confirmed | — | All cited line(s) [491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505] in flashcore/session_manager.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F151 | confirmed | — | flashcore/review_processor.py is 100% covered; all statements exercised, the described behavior ran without test detection. |
| F152 | confirmed | — | flashcore/models.py is 100% covered; all statements exercised, the described behavior ran without test detection. |
| F153 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F154 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F155 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F156 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F157 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F158 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F159 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F160 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F161 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F162 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F163 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F164 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F165 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F166 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F167 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F168 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F169 | confirmed | — | All cited line(s) [211, 212] in flashcore/scheduler.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F170 | confirmed | — | All cited line(s) [109] in flashcore/review_manager.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F171 | confirmed | — | All cited line(s) [205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215] in flashcore/session_manager.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F172 | confirmed | — | All cited line(s) [267] in flashcore/yaml_validators.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F173 | confirmed | — | All cited line(s) [277, 278, 279] in flashcore/cli/_vet_logic.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F174 | confirmed | — | All cited line(s) [643, 644] in flashcore/session_manager.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F175 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F176 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F177 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F178 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F179 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F180 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F181 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F182 | confirmed | — | All cited line(s) [267] in flashcore/yaml_validators.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F183 | untested | — | Non-Python file (.github/workflows/aiv-guard.yml:33); Python line coverage does not apply. |
| F184 | untested | — | Non-Python file (.github/workflows/rename_project.yml:6); Python line coverage does not apply. |
| F185 | untested | — | Non-Python file (.github/workflows/rename_project.yml:37); Python line coverage does not apply. |
| F186 | untested | — | Non-Python file (.github/workflows/main.yml:25-26, release.yml:29, rename_project.yml:39); Python line coverage does not apply. |
| F187 | untested | — | Non-Python file (Containerfile:1); Python line coverage does not apply. |
| F188 | untested | — | Non-Python file (.github/rename_project.sh:26-29); Python line coverage does not apply. |
| F189 | untested | — | Non-Python file (.github/workflows/main.yml:207); Python line coverage does not apply. |
| F190 | confirmed | — | All cited line(s) [92, 93, 94, 95] in flashcore/yaml_models.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F191 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F192 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F193 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F194 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F195 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F196 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F197 | untested | — | Non-Python file (Containerfile:1); Python line coverage does not apply. |
| F198 | refined | — | Cited range includes both covered lines [543, 544, 545, 546, 547, 548, 549] and uncovered lines [525, 526] in flashcore/cli/main.py. Part of the described behavior ran (covered lines confirm presence of the pattern); uncovered lines were not exercised. |
| F199 | untested | — | Non-Python file (.github/workflows/release.yml:51); Python line coverage does not apply. |
| F200 | refined | — | File-level location; flashcore/yaml_validators.py has partial coverage (2 missed lines). Parts of the described behavior may be untested. |
| F201 | untested | — | Non-Python file (Makefile:84); Python line coverage does not apply. |
| F202 | untested | — | Non-Python file (.github/workflows/main.yml:25-26); Python line coverage does not apply. |
| F203 | untested | — | Non-Python file (.windsurfrules:9,535,1062); Python line coverage does not apply. |
| F204 | confirmed | — | All cited line(s) [265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325] in flashcore/yaml_models.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F205 | untested | — | Non-Python file (.taskmaster/config.json:28); Python line coverage does not apply. |
| F206 | untested | — | Non-Python file (Makefile:101); Python line coverage does not apply. |
| F207 | confirmed | — | flashcore/cli/_review_logic.py is 100% covered; all statements exercised, the described behavior ran without test detection. |
| F208 | untested | — | Non-Python file (.aiv.yml:13); Python line coverage does not apply. |
| F209 | untested | — | Non-Python file (.github/init.sh:35); Python line coverage does not apply. |
| F210 | confirmed | — | flashcore/models.py is 100% covered; all statements exercised, the described behavior ran without test detection. |
| F211 | untested | — | Non-Python file (flashcore/scripts/dump_history.py:45); Python line coverage does not apply. |
| F212 | untested | — | Non-Python file (requirements-test.txt:1); Python line coverage does not apply. |
| F213 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F214 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F215 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F216 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F217 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F218 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F219 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F220 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F221 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F222 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F223 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F224 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F225 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F226 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |
| F227 | confirmed | — | flashcore/cli/_review_logic.py is 100% covered; all statements exercised, the described behavior ran without test detection. |
| F228 | confirmed | — | All cited line(s) [156, 157, 158] in flashcore/db/db_utils.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F229 | refined | — | File-level location; flashcore/yaml_validators.py has partial coverage (2 missed lines). Parts of the described behavior may be untested. |
| F230 | refined | — | File-level location; flashcore/yaml_validators.py has partial coverage (2 missed lines). Parts of the described behavior may be untested. |
| F231 | confirmed | — | All cited line(s) [292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305] in flashcore/yaml_models.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F232 | confirmed | — | All cited line(s) [318, 319, 320, 321, 322, 323] in flashcore/yaml_models.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F233 | confirmed | — | flashcore/exceptions.py is 100% covered; all statements exercised, the described behavior ran without test detection. |
| F234 | refined | — | Cited range includes both covered lines [473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521] and uncovered lines [522, 523, 525, 530, 531, 532, 538, 553, 555, 557, 558, 559] in flashcore/session_manager.py. Part of the described behavior ran (covered lines confirm presence of the pattern); uncovered lines were not exercised. |
| F235 | confirmed | — | All cited line(s) [269] in flashcore/db/db_utils.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F236 | confirmed | — | All cited line(s) [31, 32] in flashcore/cli/_review_all_logic.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F237 | confirmed | — | All cited line(s) [543, 544, 545, 546, 547, 548, 549] in flashcore/cli/main.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection. |
| F238 | confirmed | — | Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding. |

## Un-executed (100% accounting — each carries proof-of-attempt)

| Region | Reason | Command tried | Failure |
| --- | --- | --- | --- |
| flashcore/db/database.py:366-369 (delete_card error/rollback path) | dead | make test | Lines 366-369 had hits=0 in coverage.xml; no test exercised the delete_card rollback branch. |
| flashcore/db/database.py:450-457 (bulk_insert error path) | dead | make test | Lines 450-457 had hits=0; bulk insert error handling not triggered by any test. |
| flashcore/db/database.py:530,549-553 (get_cards_by_deck error branches) | dead | make test | Lines 530, 549-550, 553 had hits=0; error/empty-result branches not reached. |
| flashcore/db/database.py:604-605,657-658 (update_card/tag error paths) | dead | make test | Lines 604-605, 657-658 had hits=0; update error branches not exercised. |
| flashcore/db/database.py:821-822,883-884,898-899,926,933-934,951 (session update error paths) | dead | make test | Lines 821-822, 883-884, 898-899, 926, 933-934, 951 had hits=0; session-record update error handling not reached. |
| flashcore/db/database.py:961-971,991,996 (stats/aggregation error branches) | dead | make test | Lines 961-971, 991, 996 had hits=0; DB stats query error paths not triggered. |
| flashcore/db/database.py:1028-1038,1065-1071,1095-1096,1104,1110-1118 (advanced query error paths) | dead | make test | Blocks of missed lines (1028-1038, 1065-1071, 1095-1096, 1104, 1110-1118) had hits=0. |
| flashcore/db/database.py:1156,1162-1163,1166-1167,1170,1191-1200,1204-1205,1208-1212 (export/report error paths) | dead | make test | Multiple blocks near end of database.py had hits=0; export and report error handling not reached. |
| flashcore/db/database.py:42 (module-level logger setup branch) | dead | make test | Line 42 had hits=0; conditional logger initialisation branch not taken. |
| flashcore/db/database.py:205-206 (connection init error branch) | dead | make test | Lines 205-206 had hits=0; connection error handling path not exercised. |
| flashcore/session_manager.py:522-559 (error handling in session calculation block) | dead | make test | Lines 522-559 had hits=0; complex session metric calculation error path or edge-case branch not reached. |
| flashcore/session_manager.py:758,760 (session finalization edge case) | dead | make test | Lines 758, 760 had hits=0; session finalization conditional branch not exercised. |
| flashcore/db/db_utils.py:219-249 (backup file creation) | dead | make test | Lines 219, 221, 239-241, 243-245, 248-249 had hits=0; backup creation paths not exercised by any test. |
| flashcore/parser.py:119,182,192-193,228,242 (parser edge-case branches) | dead | make test | Lines 119, 182, 192, 193, 228, 242 had hits=0; malformed or edge-case YAML input paths not reached. |
| flashcore/scheduler.py:71,176,236 (scheduler edge cases) | dead | make test | Lines 71, 176, 236 had hits=0; scheduler edge-case branches (new-card special case, stability limit, or error path) not exercised. |
| flashcore/yaml_models.py:193,196-197,216,248,250,255,257,259 (Pydantic validator edge cases) | dead | make test | Lines 193, 196-197, 216, 248, 250, 255, 257, 259 had hits=0; Pydantic field-validator error branches not triggered. |
| flashcore/yaml_validators.py:176,216 (YAML validation error branches) | dead | make test | Lines 176, 216 had hits=0; specific YAML validation failure branches not reached. |
| flashcore/cli/_review_all_logic.py:143 (review-all error branch) | dead | make test | Line 143 had hits=0; error handling in review-all logic not reached. |
| flashcore/cli/_vet_logic.py:135 (vet error branch) | dead | make test | Line 135 had hits=0; vet error handling not reached by test suite. |
| flashcore/cli/main.py:53,342-343,347,471,517,525-526,657 (CLI error/option branches) | dead | make test | Lines 53, 342, 343, 347, 471, 517, 525, 526, 657 had hits=0; CLI conditional branches (startup guard, option paths, error exits) not exercised. |
| flashcore/db/connection.py:91-92 (connection error branch) | dead | make test | Lines 91-92 had hits=0; database connection error handling path not reached. |
| flashcore/db/schema_manager.py:57 (schema rollback error branch) | dead | make test | Line 57 had hits=0; schema rollback error path not triggered. |
| flashcore/review_manager.py:206-207 (review manager error branch) | dead | make test | Lines 206-207 had hits=0; specific ReviewManager error/edge-case branch not exercised. |
| pytest direct invocation (no venv activation) | requires-submodule | pytest -v --cov-config .coveragerc --cov=flashcore -l --tb=short --maxfail=1 tests/ | Exit code 4: ModuleNotFoundError: No module named 'pydantic'. Direct pytest invocation without make/venv activation fails because pydantic is installed only in the project venv, not in the system Python. |


## Machine-checkable data

```json
{
  "coverage_pct": 93,
  "coverage_verified": false,
  "observed": [
    {
      "entry": "make test → pytest tests/ via Makefile",
      "behavior": "480 tests passed, 1 skipped, 93% line coverage across 26 flashcore modules. All assertions satisfied; no test triggered a RuntimeError or assertion failure during production-code execution."
    },
    {
      "entry": "flashcore/review_manager.py:initialize_session",
      "behavior": "Called by test suite (98% file coverage, lines 206-207 missed). Review queue construction at line 109 executed: cards fetched by DB due-date order then re-sorted by modified_at without test detecting the ordering change."
    },
    {
      "entry": "flashcore/scheduler.py:compute_next_state",
      "behavior": "Called at 96% file coverage (lines 71, 176, 236 missed). Lines 211-212 (last_review=due_date assignment) executed; tests passed without asserting on elapsed_days value or FSRS retrievability."
    },
    {
      "entry": "flashcore/session_manager.py:record_card_review",
      "behavior": "Called at 95% coverage (lines 522-559, 758-760 missed). Lines 205-213 (deck_access_order append guard) and line 643 (deck_switch_efficiency formula) both executed; no test asserted on correct deck-switch count or efficiency clamp."
    },
    {
      "entry": "flashcore/cli/_vet_logic.py:_validate_and_normalize_card",
      "behavior": "Executed at 99% coverage (line 135 missed). Line 80 (Card(**mapped_card_dict)) executed with mapped dict that retains 's' and 'id' keys; tests did not supply cards with those fields, so no ValidationError was triggered."
    },
    {
      "entry": "flashcore/db/database.py (multiple functions)",
      "behavior": "81% coverage, 84 lines missed. Core CRUD paths executed; error-handling branches (rollback paths, constraint violations, large-batch edge cases) not reached."
    },
    {
      "entry": "flashcore/db/db_utils.py:create_backup",
      "behavior": "85% coverage; lines 219-249 (backup filename construction and file-copy operations) not executed. Naive local-time datetime at line 269 was NOT in the missed set—it was executed—but no test verified timezone correctness."
    },
    {
      "entry": "pytest direct invocation (without make)",
      "behavior": "Commands 'pytest -v ...' and 'pytest tests/ -q ...' both failed with exit code 4: ModuleNotFoundError for pydantic when invoked outside the venv. Only 'make test' (which activates the venv) succeeded."
    }
  ],
  "deltas": [
    {
      "id": "F1",
      "delta": "confirmed",
      "evidence": "All cited line(s) [109] in flashcore/review_manager.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F2",
      "delta": "confirmed",
      "evidence": "All cited line(s) [80] in flashcore/cli/_vet_logic.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F3",
      "delta": "refined",
      "evidence": "Cited range includes both covered lines [276, 277, 278, 279] and uncovered lines [135] in flashcore/cli/_vet_logic.py. Part of the described behavior ran (covered lines confirm presence of the pattern); uncovered lines were not exercised."
    },
    {
      "id": "F4",
      "delta": "confirmed",
      "evidence": "All cited line(s) [211, 212] in flashcore/scheduler.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F5",
      "delta": "confirmed",
      "evidence": "All cited line(s) [205, 206, 207, 208, 209, 210, 211, 212, 213] in flashcore/session_manager.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F6",
      "delta": "confirmed",
      "evidence": "All cited line(s) [643] in flashcore/session_manager.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F7",
      "delta": "confirmed",
      "evidence": "All cited line(s) [269] in flashcore/db/db_utils.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F8",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F9",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F10",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F11",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F12",
      "delta": "untested",
      "evidence": "Non-Python file (.github/init.sh:35-36,63); Python line coverage does not apply."
    },
    {
      "id": "F13",
      "delta": "untested",
      "evidence": "Non-Python file (.github/init.sh:36,63); Python line coverage does not apply."
    },
    {
      "id": "F14",
      "delta": "refined",
      "evidence": "File-level location; flashcore/yaml_validators.py has partial coverage (2 missed lines). Parts of the described behavior may be untested."
    },
    {
      "id": "F15",
      "delta": "untested",
      "evidence": "Non-Python file (flashcore/scripts/dump_history.py:45); Python line coverage does not apply."
    },
    {
      "id": "F16",
      "delta": "untested",
      "evidence": "Non-Python file (.github/workflows/rename_project.yml:6); Python line coverage does not apply."
    },
    {
      "id": "F17",
      "delta": "untested",
      "evidence": "Non-Python file (.github/workflows/rename_project.yml:43); Python line coverage does not apply."
    },
    {
      "id": "F18",
      "delta": "untested",
      "evidence": "Non-Python file (.github/workflows/aiv-guard.yml:33); Python line coverage does not apply."
    },
    {
      "id": "F19",
      "delta": "untested",
      "evidence": "Non-Python file (.github/workflows/main.yml:25-26,.github/workflows/release.yml:21,38,.github/workflows/rename_project.yml:13,39,.github/workflows/aiv-guard.yml:21,26); Python line coverage does not apply."
    },
    {
      "id": "F20",
      "delta": "untested",
      "evidence": "Non-Python file (.github/workflows/rename_project.yml:37); Python line coverage does not apply."
    },
    {
      "id": "F21",
      "delta": "untested",
      "evidence": "Non-Python file (.github/rename_project.sh:26-30); Python line coverage does not apply."
    },
    {
      "id": "F22",
      "delta": "confirmed",
      "evidence": "All cited line(s) [93] in flashcore/yaml_models.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F23",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F24",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F25",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F26",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F27",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F28",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F29",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F30",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F31",
      "delta": "untested",
      "evidence": "Non-Python file (Containerfile:1); Python line coverage does not apply."
    },
    {
      "id": "F32",
      "delta": "untested",
      "evidence": "Non-Python file (.github/workflows/main.yml:25); Python line coverage does not apply."
    },
    {
      "id": "F33",
      "delta": "untested",
      "evidence": "Non-Python file (.github/workflows/release.yml:51); Python line coverage does not apply."
    },
    {
      "id": "F34",
      "delta": "untested",
      "evidence": "Non-Python file (.aiv.yml:13); Python line coverage does not apply."
    },
    {
      "id": "F35",
      "delta": "confirmed",
      "evidence": "flashcore/cli/_review_logic.py is 100% covered; all statements exercised, the described behavior ran without test detection."
    },
    {
      "id": "F36",
      "delta": "untested",
      "evidence": "Non-Python file (Makefile:101); Python line coverage does not apply."
    },
    {
      "id": "F37",
      "delta": "untested",
      "evidence": "Non-Python file (.env.example:1); Python line coverage does not apply."
    },
    {
      "id": "F38",
      "delta": "untested",
      "evidence": "Non-Python file (.github/init.sh:62); Python line coverage does not apply."
    },
    {
      "id": "F39",
      "delta": "refined",
      "evidence": "Cited range includes both covered lines [543, 544, 545, 546, 547, 548, 549] and uncovered lines [525, 526] in flashcore/cli/main.py. Part of the described behavior ran (covered lines confirm presence of the pattern); uncovered lines were not exercised."
    },
    {
      "id": "F40",
      "delta": "untested",
      "evidence": "Non-Python file (Makefile:83); Python line coverage does not apply."
    },
    {
      "id": "F41",
      "delta": "untested",
      "evidence": "Non-Python file (.windsurfrules:1); Python line coverage does not apply."
    },
    {
      "id": "F42",
      "delta": "confirmed",
      "evidence": "flashcore/models.py is 100% covered; all statements exercised, the described behavior ran without test detection."
    },
    {
      "id": "F43",
      "delta": "refined",
      "evidence": "File-level location; flashcore/db/database.py has partial coverage (84 missed lines). Parts of the described behavior may be untested."
    },
    {
      "id": "F44",
      "delta": "untested",
      "evidence": "Non-Python file (mkdocs.yml:1); Python line coverage does not apply."
    },
    {
      "id": "F45",
      "delta": "untested",
      "evidence": "Non-Python file (requirements-test.txt:1); Python line coverage does not apply."
    },
    {
      "id": "F46",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F47",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F48",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F49",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F50",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F51",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F52",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F53",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F54",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F55",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F56",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F57",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F58",
      "delta": "confirmed",
      "evidence": "flashcore/cli/_review_logic.py is 100% covered; all statements exercised, the described behavior ran without test detection."
    },
    {
      "id": "F59",
      "delta": "refined",
      "evidence": "File-level location; flashcore/db/database.py has partial coverage (84 missed lines). Parts of the described behavior may be untested."
    },
    {
      "id": "F60",
      "delta": "confirmed",
      "evidence": "All cited line(s) [292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325] in flashcore/yaml_models.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F61",
      "delta": "refined",
      "evidence": "File-level location; flashcore/yaml_validators.py has partial coverage (2 missed lines). Parts of the described behavior may be untested."
    },
    {
      "id": "F62",
      "delta": "confirmed",
      "evidence": "All cited line(s) [269] in flashcore/db/db_utils.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F63",
      "delta": "refined",
      "evidence": "Cited range includes both covered lines (489-521) and uncovered lines [522, 523, 525, 530, 531, 532, 538, 553, 555, 557, 558, 559] in flashcore/session_manager.py. Part of the described behavior ran (covered lines confirm presence of the pattern); uncovered lines were not exercised."
    },
    {
      "id": "F64",
      "delta": "confirmed",
      "evidence": "All cited line(s) [112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158] in flashcore/cli/_review_all_logic.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F65",
      "delta": "confirmed",
      "evidence": "flashcore/exceptions.py is 100% covered; all statements exercised, the described behavior ran without test detection."
    },
    {
      "id": "F66",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F67",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F68",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F69",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F70",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F71",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F72",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F73",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F74",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F75",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F76",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F77",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F78",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F79",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F80",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F81",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F82",
      "delta": "confirmed",
      "evidence": "flashcore/cli/review_ui.py is 100% covered; all statements exercised, the described behavior ran without test detection."
    },
    {
      "id": "F83",
      "delta": "confirmed",
      "evidence": "All cited line(s) [59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80] in flashcore/cli/_vet_logic.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F84",
      "delta": "confirmed",
      "evidence": "All cited line(s) [204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214] in flashcore/session_manager.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F85",
      "delta": "confirmed",
      "evidence": "flashcore/cli/_review_logic.py is 100% covered; all statements exercised, the described behavior ran without test detection."
    },
    {
      "id": "F86",
      "delta": "confirmed",
      "evidence": "All cited line(s) [277, 278] in flashcore/cli/_vet_logic.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F87",
      "delta": "confirmed",
      "evidence": "All cited line(s) [211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224] in flashcore/scheduler.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F88",
      "delta": "confirmed",
      "evidence": "All cited line(s) [643, 644] in flashcore/session_manager.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F89",
      "delta": "confirmed",
      "evidence": "All cited line(s) [269] in flashcore/db/db_utils.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F90",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F91",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F92",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F93",
      "delta": "confirmed",
      "evidence": "All cited line(s) [267] in flashcore/yaml_validators.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F94",
      "delta": "untested",
      "evidence": "Non-Python file (.github/rename_project.sh:26-29); Python line coverage does not apply."
    },
    {
      "id": "F95",
      "delta": "untested",
      "evidence": "Non-Python file (.github/workflows/rename_project.yml:37); Python line coverage does not apply."
    },
    {
      "id": "F96",
      "delta": "untested",
      "evidence": "Non-Python file (.github/workflows/rename_project.yml:6); Python line coverage does not apply."
    },
    {
      "id": "F97",
      "delta": "untested",
      "evidence": "Non-Python file (.github/workflows/aiv-guard.yml:33); Python line coverage does not apply."
    },
    {
      "id": "F98",
      "delta": "untested",
      "evidence": "Non-Python file (Containerfile:1-5); Python line coverage does not apply."
    },
    {
      "id": "F99",
      "delta": "untested",
      "evidence": "Non-Python file (.github/init.sh:63); Python line coverage does not apply."
    },
    {
      "id": "F100",
      "delta": "confirmed",
      "evidence": "All cited line(s) [91, 92] in flashcore/yaml_models.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F101",
      "delta": "confirmed",
      "evidence": "All cited line(s) [120, 121, 122, 123] in flashcore/db/db_utils.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F102",
      "delta": "untested",
      "evidence": "Non-Python file (Containerfile:2); Python line coverage does not apply."
    },
    {
      "id": "F103",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F104",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F105",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F106",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F107",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F108",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F109",
      "delta": "untested",
      "evidence": "Non-Python file (Containerfile:1); Python line coverage does not apply."
    },
    {
      "id": "F110",
      "delta": "untested",
      "evidence": "Non-Python file (.github/workflows/release.yml:51); Python line coverage does not apply."
    },
    {
      "id": "F111",
      "delta": "refined",
      "evidence": "File-level location; flashcore/yaml_validators.py has partial coverage (2 missed lines). Parts of the described behavior may be untested."
    },
    {
      "id": "F112",
      "delta": "confirmed",
      "evidence": "All cited line(s) [543] in flashcore/cli/main.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F113",
      "delta": "untested",
      "evidence": "Non-Python file (.github/workflows/aiv-guard.yml:21); Python line coverage does not apply."
    },
    {
      "id": "F114",
      "delta": "confirmed",
      "evidence": "flashcore/cli/_review_logic.py is 100% covered; all statements exercised, the described behavior ran without test detection."
    },
    {
      "id": "F115",
      "delta": "confirmed",
      "evidence": "All cited line(s) [86, 87] in flashcore/scheduler.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F116",
      "delta": "confirmed",
      "evidence": "All cited line(s) [278] in flashcore/cli/_vet_logic.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F117",
      "delta": "untested",
      "evidence": "Non-Python file (.aiv.yml:13); Python line coverage does not apply."
    },
    {
      "id": "F118",
      "delta": "untested",
      "evidence": "Non-Python file (.windsurfrules:1); Python line coverage does not apply."
    },
    {
      "id": "F119",
      "delta": "confirmed",
      "evidence": "flashcore/models.py is 100% covered; all statements exercised, the described behavior ran without test detection."
    },
    {
      "id": "F120",
      "delta": "untested",
      "evidence": "Non-Python file (Makefile:101); Python line coverage does not apply."
    },
    {
      "id": "F121",
      "delta": "untested",
      "evidence": "Non-Python file (.env.example:1); Python line coverage does not apply."
    },
    {
      "id": "F122",
      "delta": "untested",
      "evidence": "Non-Python file (requirements-test.txt:1); Python line coverage does not apply."
    },
    {
      "id": "F123",
      "delta": "refined",
      "evidence": "File-level location; flashcore/db/database.py has partial coverage (84 missed lines). Parts of the described behavior may be untested."
    },
    {
      "id": "F124",
      "delta": "confirmed",
      "evidence": "All cited line(s) [185] in flashcore/cli/_review_all_logic.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F125",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F126",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F127",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F128",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F129",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F130",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F131",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F132",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F133",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F134",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F135",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F136",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F137",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F138",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F139",
      "delta": "confirmed",
      "evidence": "flashcore/cli/_review_logic.py is 100% covered; all statements exercised, the described behavior ran without test detection."
    },
    {
      "id": "F140",
      "delta": "confirmed",
      "evidence": "All cited line(s) [156, 157, 158] in flashcore/db/db_utils.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F141",
      "delta": "confirmed",
      "evidence": "All cited line(s) [140, 141, 142, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158] in flashcore/cli/_review_all_logic.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F142",
      "delta": "refined",
      "evidence": "File-level location; flashcore/yaml_validators.py has partial coverage (2 missed lines). Parts of the described behavior may be untested."
    },
    {
      "id": "F143",
      "delta": "confirmed",
      "evidence": "flashcore/cli/review_ui.py is 100% covered; all statements exercised, the described behavior ran without test detection."
    },
    {
      "id": "F144",
      "delta": "untested",
      "evidence": "Non-Python file (flashcore/scripts/migrate.py:184-204); Python line coverage does not apply."
    },
    {
      "id": "F145",
      "delta": "confirmed",
      "evidence": "All cited line(s) [183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200] in flashcore/cli/_review_all_logic.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F146",
      "delta": "confirmed",
      "evidence": "All cited line(s) [292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323] in flashcore/yaml_models.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F147",
      "delta": "confirmed",
      "evidence": "All cited line(s) [248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320] in flashcore/review_manager.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F148",
      "delta": "confirmed",
      "evidence": "All cited line(s) [269] in flashcore/db/db_utils.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F149",
      "delta": "refined",
      "evidence": "Cited range includes both covered lines [50, 54, 55, 56, 57, 58] and uncovered lines [53] in flashcore/cli/main.py. Part of the described behavior ran (covered lines confirm presence of the pattern); uncovered lines were not exercised."
    },
    {
      "id": "F150",
      "delta": "confirmed",
      "evidence": "All cited line(s) [491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505] in flashcore/session_manager.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F151",
      "delta": "confirmed",
      "evidence": "flashcore/review_processor.py is 100% covered; all statements exercised, the described behavior ran without test detection."
    },
    {
      "id": "F152",
      "delta": "confirmed",
      "evidence": "flashcore/models.py is 100% covered; all statements exercised, the described behavior ran without test detection."
    },
    {
      "id": "F153",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F154",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F155",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F156",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F157",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F158",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F159",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F160",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F161",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F162",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F163",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F164",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F165",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F166",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F167",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F168",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F169",
      "delta": "confirmed",
      "evidence": "All cited line(s) [211, 212] in flashcore/scheduler.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F170",
      "delta": "confirmed",
      "evidence": "All cited line(s) [109] in flashcore/review_manager.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F171",
      "delta": "confirmed",
      "evidence": "All cited line(s) [205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215] in flashcore/session_manager.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F172",
      "delta": "confirmed",
      "evidence": "All cited line(s) [267] in flashcore/yaml_validators.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F173",
      "delta": "confirmed",
      "evidence": "All cited line(s) [277, 278, 279] in flashcore/cli/_vet_logic.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F174",
      "delta": "confirmed",
      "evidence": "All cited line(s) [643, 644] in flashcore/session_manager.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F175",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F176",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F177",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F178",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F179",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F180",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F181",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F182",
      "delta": "confirmed",
      "evidence": "All cited line(s) [267] in flashcore/yaml_validators.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F183",
      "delta": "untested",
      "evidence": "Non-Python file (.github/workflows/aiv-guard.yml:33); Python line coverage does not apply."
    },
    {
      "id": "F184",
      "delta": "untested",
      "evidence": "Non-Python file (.github/workflows/rename_project.yml:6); Python line coverage does not apply."
    },
    {
      "id": "F185",
      "delta": "untested",
      "evidence": "Non-Python file (.github/workflows/rename_project.yml:37); Python line coverage does not apply."
    },
    {
      "id": "F186",
      "delta": "untested",
      "evidence": "Non-Python file (.github/workflows/main.yml:25-26, release.yml:29, rename_project.yml:39); Python line coverage does not apply."
    },
    {
      "id": "F187",
      "delta": "untested",
      "evidence": "Non-Python file (Containerfile:1); Python line coverage does not apply."
    },
    {
      "id": "F188",
      "delta": "untested",
      "evidence": "Non-Python file (.github/rename_project.sh:26-29); Python line coverage does not apply."
    },
    {
      "id": "F189",
      "delta": "untested",
      "evidence": "Non-Python file (.github/workflows/main.yml:207); Python line coverage does not apply."
    },
    {
      "id": "F190",
      "delta": "confirmed",
      "evidence": "All cited line(s) [92, 93, 94, 95] in flashcore/yaml_models.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F191",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F192",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F193",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F194",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F195",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F196",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F197",
      "delta": "untested",
      "evidence": "Non-Python file (Containerfile:1); Python line coverage does not apply."
    },
    {
      "id": "F198",
      "delta": "refined",
      "evidence": "Cited range includes both covered lines [543, 544, 545, 546, 547, 548, 549] and uncovered lines [525, 526] in flashcore/cli/main.py. Part of the described behavior ran (covered lines confirm presence of the pattern); uncovered lines were not exercised."
    },
    {
      "id": "F199",
      "delta": "untested",
      "evidence": "Non-Python file (.github/workflows/release.yml:51); Python line coverage does not apply."
    },
    {
      "id": "F200",
      "delta": "refined",
      "evidence": "File-level location; flashcore/yaml_validators.py has partial coverage (2 missed lines). Parts of the described behavior may be untested."
    },
    {
      "id": "F201",
      "delta": "untested",
      "evidence": "Non-Python file (Makefile:84); Python line coverage does not apply."
    },
    {
      "id": "F202",
      "delta": "untested",
      "evidence": "Non-Python file (.github/workflows/main.yml:25-26); Python line coverage does not apply."
    },
    {
      "id": "F203",
      "delta": "untested",
      "evidence": "Non-Python file (.windsurfrules:9,535,1062); Python line coverage does not apply."
    },
    {
      "id": "F204",
      "delta": "confirmed",
      "evidence": "All cited line(s) [265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325] in flashcore/yaml_models.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F205",
      "delta": "untested",
      "evidence": "Non-Python file (.taskmaster/config.json:28); Python line coverage does not apply."
    },
    {
      "id": "F206",
      "delta": "untested",
      "evidence": "Non-Python file (Makefile:101); Python line coverage does not apply."
    },
    {
      "id": "F207",
      "delta": "confirmed",
      "evidence": "flashcore/cli/_review_logic.py is 100% covered; all statements exercised, the described behavior ran without test detection."
    },
    {
      "id": "F208",
      "delta": "untested",
      "evidence": "Non-Python file (.aiv.yml:13); Python line coverage does not apply."
    },
    {
      "id": "F209",
      "delta": "untested",
      "evidence": "Non-Python file (.github/init.sh:35); Python line coverage does not apply."
    },
    {
      "id": "F210",
      "delta": "confirmed",
      "evidence": "flashcore/models.py is 100% covered; all statements exercised, the described behavior ran without test detection."
    },
    {
      "id": "F211",
      "delta": "untested",
      "evidence": "Non-Python file (flashcore/scripts/dump_history.py:45); Python line coverage does not apply."
    },
    {
      "id": "F212",
      "delta": "untested",
      "evidence": "Non-Python file (requirements-test.txt:1); Python line coverage does not apply."
    },
    {
      "id": "F213",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F214",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F215",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F216",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F217",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F218",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F219",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F220",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F221",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F222",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F223",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F224",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F225",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F226",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    },
    {
      "id": "F227",
      "delta": "confirmed",
      "evidence": "flashcore/cli/_review_logic.py is 100% covered; all statements exercised, the described behavior ran without test detection."
    },
    {
      "id": "F228",
      "delta": "confirmed",
      "evidence": "All cited line(s) [156, 157, 158] in flashcore/db/db_utils.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F229",
      "delta": "refined",
      "evidence": "File-level location; flashcore/yaml_validators.py has partial coverage (2 missed lines). Parts of the described behavior may be untested."
    },
    {
      "id": "F230",
      "delta": "refined",
      "evidence": "File-level location; flashcore/yaml_validators.py has partial coverage (2 missed lines). Parts of the described behavior may be untested."
    },
    {
      "id": "F231",
      "delta": "confirmed",
      "evidence": "All cited line(s) [292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305] in flashcore/yaml_models.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F232",
      "delta": "confirmed",
      "evidence": "All cited line(s) [318, 319, 320, 321, 322, 323] in flashcore/yaml_models.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F233",
      "delta": "confirmed",
      "evidence": "flashcore/exceptions.py is 100% covered; all statements exercised, the described behavior ran without test detection."
    },
    {
      "id": "F234",
      "delta": "refined",
      "evidence": "Cited range includes both covered lines [473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521] and uncovered lines [522, 523, 525, 530, 531, 532, 538, 553, 555, 557, 558, 559] in flashcore/session_manager.py. Part of the described behavior ran (covered lines confirm presence of the pattern); uncovered lines were not exercised."
    },
    {
      "id": "F235",
      "delta": "confirmed",
      "evidence": "All cited line(s) [269] in flashcore/db/db_utils.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F236",
      "delta": "confirmed",
      "evidence": "All cited line(s) [31, 32] in flashcore/cli/_review_all_logic.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F237",
      "delta": "confirmed",
      "evidence": "All cited line(s) [543, 544, 545, 546, 547, 548, 549] in flashcore/cli/main.py were executed (hits>0 in coverage.xml). The described defect was present in covered code; tests passed through it without detection."
    },
    {
      "id": "F238",
      "delta": "confirmed",
      "evidence": "Test file: the test executed and passed (480 passed, 1 skipped); the described weak/incorrect assertion pattern ran without triggering a production defect, confirming the finding."
    }
  ],
  "unexecuted": [
    {
      "region": "flashcore/db/database.py:366-369 (delete_card error/rollback path)",
      "reason": "dead",
      "command": "make test",
      "failure": "Lines 366-369 had hits=0 in coverage.xml; no test exercised the delete_card rollback branch."
    },
    {
      "region": "flashcore/db/database.py:450-457 (bulk_insert error path)",
      "reason": "dead",
      "command": "make test",
      "failure": "Lines 450-457 had hits=0; bulk insert error handling not triggered by any test."
    },
    {
      "region": "flashcore/db/database.py:530,549-553 (get_cards_by_deck error branches)",
      "reason": "dead",
      "command": "make test",
      "failure": "Lines 530, 549-550, 553 had hits=0; error/empty-result branches not reached."
    },
    {
      "region": "flashcore/db/database.py:604-605,657-658 (update_card/tag error paths)",
      "reason": "dead",
      "command": "make test",
      "failure": "Lines 604-605, 657-658 had hits=0; update error branches not exercised."
    },
    {
      "region": "flashcore/db/database.py:821-822,883-884,898-899,926,933-934,951 (session update error paths)",
      "reason": "dead",
      "command": "make test",
      "failure": "Lines 821-822, 883-884, 898-899, 926, 933-934, 951 had hits=0; session-record update error handling not reached."
    },
    {
      "region": "flashcore/db/database.py:961-971,991,996 (stats/aggregation error branches)",
      "reason": "dead",
      "command": "make test",
      "failure": "Lines 961-971, 991, 996 had hits=0; DB stats query error paths not triggered."
    },
    {
      "region": "flashcore/db/database.py:1028-1038,1065-1071,1095-1096,1104,1110-1118 (advanced query error paths)",
      "reason": "dead",
      "command": "make test",
      "failure": "Blocks of missed lines (1028-1038, 1065-1071, 1095-1096, 1104, 1110-1118) had hits=0."
    },
    {
      "region": "flashcore/db/database.py:1156,1162-1163,1166-1167,1170,1191-1200,1204-1205,1208-1212 (export/report error paths)",
      "reason": "dead",
      "command": "make test",
      "failure": "Multiple blocks near end of database.py had hits=0; export and report error handling not reached."
    },
    {
      "region": "flashcore/db/database.py:42 (module-level logger setup branch)",
      "reason": "dead",
      "command": "make test",
      "failure": "Line 42 had hits=0; conditional logger initialisation branch not taken."
    },
    {
      "region": "flashcore/db/database.py:205-206 (connection init error branch)",
      "reason": "dead",
      "command": "make test",
      "failure": "Lines 205-206 had hits=0; connection error handling path not exercised."
    },
    {
      "region": "flashcore/session_manager.py:522-559 (error handling in session calculation block)",
      "reason": "dead",
      "command": "make test",
      "failure": "Lines 522-559 had hits=0; complex session metric calculation error path or edge-case branch not reached."
    },
    {
      "region": "flashcore/session_manager.py:758,760 (session finalization edge case)",
      "reason": "dead",
      "command": "make test",
      "failure": "Lines 758, 760 had hits=0; session finalization conditional branch not exercised."
    },
    {
      "region": "flashcore/db/db_utils.py:219-249 (backup file creation)",
      "reason": "dead",
      "command": "make test",
      "failure": "Lines 219, 221, 239-241, 243-245, 248-249 had hits=0; backup creation paths not exercised by any test."
    },
    {
      "region": "flashcore/parser.py:119,182,192-193,228,242 (parser edge-case branches)",
      "reason": "dead",
      "command": "make test",
      "failure": "Lines 119, 182, 192, 193, 228, 242 had hits=0; malformed or edge-case YAML input paths not reached."
    },
    {
      "region": "flashcore/scheduler.py:71,176,236 (scheduler edge cases)",
      "reason": "dead",
      "command": "make test",
      "failure": "Lines 71, 176, 236 had hits=0; scheduler edge-case branches (new-card special case, stability limit, or error path) not exercised."
    },
    {
      "region": "flashcore/yaml_models.py:193,196-197,216,248,250,255,257,259 (Pydantic validator edge cases)",
      "reason": "dead",
      "command": "make test",
      "failure": "Lines 193, 196-197, 216, 248, 250, 255, 257, 259 had hits=0; Pydantic field-validator error branches not triggered."
    },
    {
      "region": "flashcore/yaml_validators.py:176,216 (YAML validation error branches)",
      "reason": "dead",
      "command": "make test",
      "failure": "Lines 176, 216 had hits=0; specific YAML validation failure branches not reached."
    },
    {
      "region": "flashcore/cli/_review_all_logic.py:143 (review-all error branch)",
      "reason": "dead",
      "command": "make test",
      "failure": "Line 143 had hits=0; error handling in review-all logic not reached."
    },
    {
      "region": "flashcore/cli/_vet_logic.py:135 (vet error branch)",
      "reason": "dead",
      "command": "make test",
      "failure": "Line 135 had hits=0; vet error handling not reached by test suite."
    },
    {
      "region": "flashcore/cli/main.py:53,342-343,347,471,517,525-526,657 (CLI error/option branches)",
      "reason": "dead",
      "command": "make test",
      "failure": "Lines 53, 342, 343, 347, 471, 517, 525, 526, 657 had hits=0; CLI conditional branches (startup guard, option paths, error exits) not exercised."
    },
    {
      "region": "flashcore/db/connection.py:91-92 (connection error branch)",
      "reason": "dead",
      "command": "make test",
      "failure": "Lines 91-92 had hits=0; database connection error handling path not reached."
    },
    {
      "region": "flashcore/db/schema_manager.py:57 (schema rollback error branch)",
      "reason": "dead",
      "command": "make test",
      "failure": "Line 57 had hits=0; schema rollback error path not triggered."
    },
    {
      "region": "flashcore/review_manager.py:206-207 (review manager error branch)",
      "reason": "dead",
      "command": "make test",
      "failure": "Lines 206-207 had hits=0; specific ReviewManager error/edge-case branch not exercised."
    },
    {
      "region": "pytest direct invocation (no venv activation)",
      "reason": "requires-submodule",
      "command": "pytest -v --cov-config .coveragerc --cov=flashcore -l --tb=short --maxfail=1 tests/",
      "failure": "Exit code 4: ModuleNotFoundError: No module named 'pydantic'. Direct pytest invocation without make/venv activation fails because pydantic is installed only in the project venv, not in the system Python."
    }
  ],
  "deep": null,
  "run_commands": [
    {
      "cmd": "python3 -m venv .venv",
      "code": 0
    },
    {
      "cmd": "./.venv/bin/pip install -U pip",
      "code": 0
    },
    {
      "cmd": "pip install -e .[test]",
      "code": 0
    },
    {
      "cmd": "make install",
      "code": 0
    },
    {
      "cmd": "source .venv/bin/activate",
      "code": 127
    },
    {
      "cmd": "pytest -v --cov-config .coveragerc --cov=flashcore -l --tb=short --maxfail=1 tests/",
      "code": 4
    },
    {
      "cmd": "pytest tests/ -q --tb=short",
      "code": 4
    },
    {
      "cmd": "make test",
      "code": 0
    },
    {
      "cmd": "coverage xml",
      "code": 0
    },
    {
      "cmd": "coverage html",
      "code": 0
    },
    {
      "cmd": "pytest -s -vvvv -l --tb=long --cov=flashcore --cov-report=xml --cov-report=html tests",
      "code": 4
    }
  ]
}
```
