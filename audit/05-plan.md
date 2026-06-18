# 05 — Execution Plan

_Generated 2026-06-18 00:13:47 · branch `claude/nifty-brahmagupta-0tq0vy` · forensic-audit-pipeline (consolidated)_

**49 change items** — convergence: NOT-CONVERGED: ["C33"].

| ID | Change | Links | Location | Verification | Depends |
| --- | --- | --- | --- | --- | --- |
| C1 | Unify the review rating scale to a single canonical 1-4 (Rating enum) across UI capture, ReviewProcessor, and DB persistence; remove the implicit UI(0-3)->DB(+1) conversion so there is one source of truth. Document the canonical scale in flashcore/constants.py. | F47,F74,F129,F160,F168,F181,F215,F250,F289,F331,F361,Goal:engine | flashcore/review_processor.py:140-183, flashcore/review_manager.py, flashcore/cli/review_ui.py:68-127, flashcore/constants.py:10-13 | grep -r 'rating.*[0-3]' flashcore/ returns no off-by-one conversion sites; new test asserts a UI rating maps to the identical DB rating with no +1 offset | none |
| C2 | Fix FSRS elapsed_days computation: stop setting fsrs_card.last_review = fsrs_card.due (line 212); use the card's actual previous review timestamp so on-time reviews yield elapsed_days>0 and correct retrievability instead of R=1.0. | F4,F87,F169,F255,F115,Goal:engine | flashcore/scheduler.py:211-224 (and docstring example at 86) | tests/test_scheduler.py: on-time review produces elapsed_days>0 and stability differs from a same-day re-review; existing scheduler tests still pass | none |
| C3 | Verify/align DEFAULT_PARAMETERS against the installed py-fsrs v6 weight vector (21 params) and update the scheduler docstring example at line 86 to match. | F360,F115,Goal:engine | flashcore/constants.py:10-13, flashcore/scheduler.py:86 | python -c "from fsrs import FSRS; from flashcore.constants import DEFAULT_PARAMETERS; assert len(DEFAULT_PARAMETERS)==len(FSRS().w)" passes | C2 |
| C4 | Resolve dead/over-generic exceptions: either raise MarshallingError where DB<->model conversion fails or remove it; narrow generic FlashcardDatabaseError uses to specific subclasses where the operation is card/review/session-specific. | F65,F233,F287,Goal:engine | flashcore/exceptions.py:45,64-67 | grep -r 'raise MarshallingError' flashcore/ returns >=1 hit (or the class is deleted); no remaining bare FlashcardDatabaseError raises for typed operations | none |
| C5 | Add error handling to db_row_to_review mirroring db_row_to_card: wrap Review(**row_dict) in try/except, log the missing/invalid column, and raise MarshallingError with context instead of an uncaught Pydantic ValidationError. | F7,F62,F89,F101,F140,F148,F228,F235,F259,F329,F375,Goal:engine | flashcore/db/db_utils.py:120-123,156-158 | tests/test_db_errors.py: a review row missing 'rating' raises MarshallingError naming the column rather than a raw ValidationError | C4 |
| C6 | Make backup_database timestamps timezone-safe by using datetime.now(timezone.utc) to avoid cross-timezone backup filename collisions. | F7,F62,F89,F148,F235,F259,F329,F375,Goal:engine | flashcore/db/db_utils.py:269 | unit test: backup filename matches a UTC-derived timestamp pattern; two backups across simulated TZs do not collide | none |
| C7 | Fix the connection-state guard default: change getattr(conn,'closed',True) to default False so rollback is attempted when the attribute is absent; verify tag filtering (list_contains on JSON tags) returns correct rows and clarify affected-rows semantics in upsert. | F59,F302,F372,F376,F328,Goal:engine | flashcore/db/database.py:255,475-484,481-484,600,628,736,963,1030 | tests/test_db_errors.py: mock connection lacking 'closed' attribute still triggers rollback; get_due_cards tag filter integration test returns the tagged card | none |
| C8 | Consolidate review submission through a single shared ReviewProcessor instance (created once per session, not per card) and add a duplicate-submission guard so a double-submit of the same card cannot create two reviews. | F124,F145,F151,F236,F282,F306,F377,Goal:engine | flashcore/review_processor.py:9,140-183, flashcore/cli/_review_all_logic.py:183-200,185 | tests/test_review_processor.py: ReviewProcessor.__init__ invoked once per review-all run; second identical process_review_by_uuid call is rejected or no-ops | C1 |
| C9 | Remove the re-sort of already-due-ordered cards by modified_at; preserve next_due_date ASC ordering so overdue cards are reviewed first (SRS priority invariant). | F1,F170,F326,Goal:engine | flashcore/review_manager.py:109 | tests/test_review_manager.py: with three cards due on distinct dates, review_queue[0] is the earliest-due card | none |
| C10 | Stop silently swallowing session-analytics failures in ReviewManager: propagate or flag start_session/end_session failures and add defensive null-checks before deriving cards_per_minute/accuracy so DB failures don't crash or emit garbage metrics. | F147,F324,Goal:engine | flashcore/review_manager.py:91-103,248-320 | tests/test_review_manager.py: mocked start_session raising yields graceful basic-stats path; end_session returning null durations does not raise ZeroDivisionError | none |
| C11 | Correct deck-switch accounting (count transitions, not first-access), clamp active duration and deck_switch_efficiency to non-negative, surface (not swallow) update_session failures, and validate row keys in _get_session_reviews before constructing Review objects. | F5,F6,F63,F84,F88,F150,F171,F234,F256,F262,F327,F373,F374,Goal:engine | flashcore/session_manager.py:204-215,229-238,255-264,337-338,473-558,643-644 | tests/test_session_model.py + tests/test_session_manager.py: reviewing same deck twice keeps deck_switches==0; pause>total clamps duration>=0; switches=15 yields efficiency>=0; missing review column logs + raises typed error | C5 |
| C12 | Harden review_ui flow: distinguish retryable vs permanent errors instead of catching all and continuing; track a reviewed_count and only print the success ('Well done') message when at least one card was actually reviewed; fail the session on un-updated cards. | F82,F143,F324,Goal:engine | flashcore/cli/review_ui.py:68-127,100-111,127 | tests/cli/test_review_all_logic.py / review_ui test: when all submit_review calls fail, output omits 'Well done' and exit signals failure | C1,C8 |
| C13 | Add explicit, wrapped schema-initialization error handling in the single-deck review entrypoint so initialize_schema failures surface a clear DatabaseError rather than a raw traceback. | F35,F58,F85,F114,F139,F207,F227,F258,F300,Goal:engine | flashcore/cli/_review_logic.py:31-43 | flashcore review <deck> against an uninitializable DB prints a clear error; covered by a CLI test asserting the message and non-zero exit | none |
| C14 | Improve review-all robustness: log exceptions with logger.exception (including the SQL) instead of console-only prints, and document/justify the date.today() timezone assumption for due-card selection. | F64,F141,F145,Goal:engine | flashcore/cli/_review_all_logic.py:31-32,112-158,140-158 | injected DB error is recorded with traceback+SQL in the log; due-card boundary test (today vs today+1) selects only today | C8 |
| C15 | Fix vet ingest path handling: validate source_dir exists before globbing (report 'directory not found' rather than 'no files found'), and make UUID handling robust so a parse failure does not silently drop a card's UUID. | F2,F3,F83,F86,F116,F173,F257,F325,Goal:engine | flashcore/cli/_vet_logic.py:59-80,80,276-279 | flashcore vet --source-dir /nonexistent reports a missing-directory error; vetting a valid file twice is idempotent (no UUID churn) | none |
| C16 | Close the media-path traversal gap: replace the str(...).startswith(assets_root) prefix check with full_media_path.resolve().relative_to(abs_assets_root) guarded by ValueError, so symlink/../ escapes are rejected. | F14,F93,F111,F142,F172,F182,F229,F267,F301,F323,F338,Goal:engine | flashcore/yaml_validators.py:267 (within 1-553) | tests/test_yaml_validators.py: a media path resolving outside the assets root (incl. via symlink/..) is rejected; in-root paths still validate | none |
| C17 | Make secret detection check both front and back and report all matched fields (not just the first), keeping content referenced by field-name only (never echo the secret value). | F61,F230,F260,Goal:engine,Goal:governance | flashcore/yaml_validators.py:64-90,115-136 | tests/test_yaml_validators.py: a card with secrets in both fields reports both field names; error message contains no secret substring | C16 |
| C18 | Fix YAML model edge cases: normalize tags=None to [] before KebabCase validation, and fix the question-snippet truncation off-by-one so the documented max length matches output. | F22,F60,F100,F146,F190,F204,F231,F232,F304,F305,Goal:engine | flashcore/yaml_models.py:91-95,265,291-325 | tests/test_yaml_validators.py / model test: 'tags: null' validates to []; a 50-char snippet produces the documented length | none |
| C19 | Harden the parser: guard against missing q/a keys in _prepare_card_data with an explicit error, and move the fail_fast raise before partial results are appended so fail_fast has clean stop semantics; add the missing module docstring. | F230,F261,F274,Goal:engine | flashcore/parser.py:1,144-163,225-228 | tests/test_parser.py: a card dict missing 'q' raises a clear error; fail_fast=True on a multi-file load excludes downstream-file cards | none |
| C20 | Add module docstrings / clarify the spoke models entrypoint so flashcore/models.py documents the Card/Review/Session public surface (template heritage cleanup, no logic change). | F42,F119,F152,F210,F354,Goal:engine | flashcore/models.py:1-4 | module imports cleanly; docstring present (pydocstyle/inspection) | none |
| C21 | Fix the migration validator state comparison so it handles state stored as enum-name vs integer consistently (normalize before the != 'New' check), preventing false negatives during the one-time legacy->DuckDB migration. | F144,F284,F371,Goal:migration | flashcore/scripts/migrate.py:122,184-204 | migrate a legacy DB with integer-coded state; validate_migration correctly flags/accepts states; row-count and orphan checks pass | C1 |
| C22 | Document/parameterize the hardcoded table-name SQL in dump_history (the f-string is safe because the names are a fixed tuple) — add an assertion/comment asserting no user input reaches the query. | F15,F211,F268,F342,Goal:engine | flashcore/scripts/dump_history.py:45 | code review confirms table names come only from the literal tuple; assertion guards against external input | none |
| C23 | Make the Anki export command fail explicitly: print the not-implemented message AND raise typer.Exit(code=1) so callers/scripts detect the failure; verify db-path resolution helper raises a catchable error rather than calling typer.Exit from a helper. | F39,F112,F149,F198,F237,F328,F353,F378,Goal:engine | flashcore/cli/main.py:51-53,199-201,543-549 | flashcore export anki && echo OK does not print OK (exit code 1); unit test of db-path resolver catches an exception without process exit | none |
| C24 | Pin the container base image to a supported, digest-pinned Python (e.g. python:3.11-slim@sha256:...) matching pyproject's requires-python, replacing the EOL/unpinned base. | F31,F98,F102,F109,F187,F197,F270,F340,Goal:governance | Containerfile:1-5 | docker/podman build succeeds; image python version satisfies requires-python; base referenced by digest | none |
| C25 | Pin all GitHub Actions to immutable commit SHAs (checkout/setup-python/action-gh-release) across release.yml, main.yml, rename_project.yml, and aiv-guard.yml, replacing floating @vN tags. | F19,F32,F33,F110,F186,F199,F202,F273,F303,F341,F355,Goal:governance | .github/workflows/release.yml:21,29,38,51, .github/workflows/main.yml:25-26, .github/workflows/rename_project.yml:13,39, .github/workflows/aiv-guard.yml:21,26 | grep for 'uses:.*@v' across .github/workflows returns no floating tags; workflows still parse (actionlint) and a dry release run succeeds | none |
| C26 | Pin the aiv-protocol git dependency to a specific commit SHA in both the workflow install and pyproject so the AIV guard runs deterministically. | F18,F97,F113,F183,F269,F337,F343,F358,Goal:governance | .github/workflows/aiv-guard.yml:33,44, pyproject.toml:43 | aiv-guard install resolves to the pinned SHA; pyproject and workflow reference the same commit; aiv check output stable across reruns | none |
| C27 | Harden the template rename workflow: scope down 'write-all' permissions to least privilege, quote variable expansions, and remove/guard the --force push so it cannot overwrite protected branches. | F16,F17,F20,F95,F96,F184,F185,F272,F275,F339,Goal:template,Goal:governance | .github/workflows/rename_project.yml:6,37,39,43 | actionlint passes; permissions block lists only contents/pull-requests; no unquoted ${{ }} in shell; no unconditional --force | none |
| C28 | Make the rename sed script injection-safe: quote filenames, escape regex/replacement metacharacters in author/name substitutions, and write a .bak for recovery (or port to a small Python replacement). | F21,F94,F188,F271,F334,F335,Goal:template | .github/rename_project.sh:26-30 | running the script with author values containing / & and filenames with spaces completes without corruption; .bak files exist | none |
| C29 | Fix the bootstrap init script: correct the shell syntax error (stray brace ~line 62), quote/validate template path and URL before clone/source to prevent injection, and validate template selection. | F12,F13,F38,F99,F209,F286,F336,Goal:template | .github/init.sh:13,14,35-36,62,63 | bash -n .github/init.sh passes (no syntax error); shellcheck reports no unquoted-injection warnings for template path/URL | none |
| C30 | Tighten dependabot config to constrain updates to direct dependencies with an explicit versioning strategy. | F276,Goal:governance | .github/dependabot.yml:4 | dependabot config validates; only direct github-actions updates are proposed | C25 |
| C31 | Correct .aiv.yml functional-prefix scope so operational CI/workflow edits do not falsely trigger AIV functional-change revalidation while code paths still do. | F34,F117,F208,F356,Goal:governance | .aiv.yml:13-14 | editing only a .github/workflows file does not require a functional packet; editing flashcore/ still does (aiv check on a sample diff) | none |
| C32 | Replace template placeholders in the Makefile: derive the release author from git config instead of the hardcoded 'rochacbruno', and drop non-ASCII content from release commit messages. | F36,F40,F120,F201,F206,Goal:template,Goal:governance | Makefile:83-84,101 | make release (dry) produces a commit authored from git config with an ASCII-only message; no 'rochacbruno' remains in the Makefile | none |
| C33 | Clean residual template scaffolding/config: set .taskmaster projectName to 'flashcore', strengthen the placeholder task verification strategy, fix the duplicated/invalid-glob .windsurfrules, document .env.example required keys, complete mkdocs.yml metadata, and update the stale CLAUDE.md test baseline reference. | F37,F41,F44,F45,F118,F121,F122,F203,F205,F212,F283,F285,F357,F359,Goal:template,Goal:governance | .taskmaster/config.json:28, .taskmaster/tasks/tasks.json:92, .windsurfrules:1,9,535,1062, .env.example:1, mkdocs.yml:1, CLAUDE.md:154, requirements-test.txt:1 | no 'Taskmaster'/template author placeholders remain; mkdocs build succeeds; .windsurfrules has a single DEV_WORKFLOW + valid glob; baseline note matches actual pytest count | none |
| C34 | Replace the rating-inconsistency 'documentation' tests that assert the bug exists (DB=UI+1) with tests that assert the unified 1-4 scale end to end; remove tests that would now be tautological. | F47,F74,F129,F160,F168,F181,F215,F250,F289,F331,F361,Goal:engine,Goal:governance | tests/test_rating_system_inconsistency.py:33,321-357 | pytest tests/test_rating_system_inconsistency.py passes asserting one canonical scale; no test asserts a +1 conversion | C1 |
| C35 | Convert test_review_logic_duplication.py from documenting-the-duplication (asserting interface specs / step counts / NaN workarounds) into real behavioral tests of the consolidated ReviewProcessor, or fold them into test_review_processor.py. | F49,F75,F76,F77,F126,F127,F128,F165,F216,F217,F248,F249,F264,F290,F299,F319,F320,F330,F362,F367,F382,Goal:engine,Goal:governance | tests/test_review_logic_duplication.py:1-10,141-148,167-211,279-370 | pytest of the rewritten file exercises ReviewProcessor outputs (not metadata assertions); grep confirms no 'assert len(duplication_steps)' style checks remain | C8 |
| C36 | Convert test_session_analytics_gaps.py from GAP-comment placeholders that assert features are missing into real assertions that session lifecycle/analytics persist and compute correctly (after C11). | F48,F55,F79,F130,F131,F132,F166,F167,F180,F218,F219,F251,F252,F253,F254,F288,F294,F313,F314,F315,F316,F317,F318,F321,F363,F364,F370,Goal:engine,Goal:governance | tests/test_session_analytics_gaps.py:1-13,26-34,59,135-499 | pytest of the rewritten file asserts session rows persist and metrics (deck switches/efficiency/duration) are correct; no '# GAP' comment stands in for an assertion | C11 |
| C37 | Strengthen DB tests: de-duplicate fixtures (import from conftest instead of redefining), make connection/get-all tests assert real content not just non-null/len, replace over-mocked schema-constraint tests with real :memory: inserts, and un-skip the force_recreate test against the current API. | F26,F56,F69,F70,F71,F133,F155,F156,F161,F224,F225,F244,F296,F308,F309,F345,F348,F352,F365,F380,F381,Goal:engine,Goal:governance | tests/test_db.py:25-93,111,283,344-395,415-433,597-605,942 | pytest tests/test_db.py passes with fixtures sourced from conftest; constraint tests use a real DB; no unexplained skips remain | C7 |
| C38 | Replace over-mocked coverage tests with real DB behavior (closed-connection upsert, recreate-order, safety-check messages) and rename gap-named tests to guard-style names. | F72,F73,F91,F157,F158,F245,F246,F279,F291,F310,F311,F347,Goal:engine,Goal:governance | tests/test_db_coverage.py:18,55,65-66,88,96-112,158-178 | pytest tests/test_db_coverage.py passes using a real DB for closed-connection/recreate paths; pytest.raises calls include match= on messages | C7 |
| C39 | Fix DB error tests to assert behavior over implementation detail: replace logger call-count assertions and bare exception catches with message-matched assertions, pass valid objects where the test currently passes a wrong type, and correct the read-only setup ordering. | F11,F54,F92,F137,F159,F220,F247,F266,F295,F312,F368,F384,Goal:engine,Goal:governance | tests/test_db_errors.py:83,336,391,413,464-474,509-514,636 | pytest tests/test_db_errors.py passes; each pytest.raises includes match=; read-only test initializes schema before reopening read-only | C5,C7 |
| C40 | Tighten session model/manager tests: assert deck-switch tracking both directions, de-flake the pause/resume timing assertion (mock time or assert state not magnitude), and complete any truncated test bodies. | F10,F51,F80,F81,F134,F138,F177,F179,F226,F298,F332,F333,F349,F369,Goal:engine,Goal:governance | tests/test_session_model.py:144-148,271-297, tests/test_session_manager.py:168-177,237-253,1003 | pytest of both files passes deterministically (run x10 with no flake); switch-back increments the counter | C11 |
| C41 | De-mock review-manager tests so they exercise real review logic against a DB, and replace enum-arithmetic magic (Rating.Again.value+1) with explicit Rating members. | F53,F108,F135,F178,F221,F222,F293,F322,Goal:engine,Goal:governance | tests/test_review_manager.py:106,134-135,171-173,502 | pytest tests/test_review_manager.py passes verifying the card was actually updated; no Rating value arithmetic remains | C1,C9,C10 |
| C42 | Complete the incomplete review_processor logging test (add real assertions) and relocate the misplaced review_processor success test out of test_scheduler.py into test_review_processor.py. | F78,F52,Goal:engine,Goal:governance | tests/test_review_processor.py:320, tests/test_scheduler.py:477 | pytest both files pass; the relocated test lives only in test_review_processor.py (grep confirms single definition) | C8 |
| C43 | Strengthen parser tests: assert error content/file (not just counts) and extract duplicated inline YAML fixtures into a shared fixture. | F24,F104,F195,F196,F350,Goal:engine,Goal:governance | tests/test_parser.py:82,344-361 | pytest tests/test_parser.py passes asserting offending file name in errors; YAML literals sourced from one fixture | C19 |
| C44 | Fix yaml_validator tests: stop mocking Path.resolve and use real tmp dirs, split the over-mocked combined-validator test into per-validator tests, add the negative assertion to the 'skipped' test, and parameterize hardcoded deck/tag data. | F23,F28,F29,F103,F107,F191,F193,F278,F351,Goal:engine,Goal:governance | tests/test_yaml_validators.py:74,98-102,216,277-285 | pytest tests/test_yaml_validators.py passes against real paths; the traversal/skipped cases assert the would-fail path | C16,C17,C18 |
| C45 | Improve CLI main tests: add real-DB integration coverage alongside the heavily-mocked unit tests, replace double-negative success assertions with direct exit_code==0 checks, assert required-arg help text, and share strip_ansi via conftest. | F27,F30,F57,F67,F106,F136,F154,F162,F164,F194,F214,F239,F240,F241,F242,F280,F344,Goal:engine,Goal:governance | tests/cli/test_main.py:24,557,697-747,886-893,912,944-1044 | pytest tests/cli/test_main.py passes; resolve-db-path test asserts exit_code==0 directly; strip_ansi defined once in conftest | C23 |
| C46 | Fix flashcards-CLI fixture hygiene (explicit yield/cleanup) and ensure the fixture exercises real file ingestion paths. | F46,F66,F125,F163,F213,F238,F297,F366,F383,Goal:governance | tests/cli/test_flashcards_cli.py:79-91 | pytest tests/cli/test_flashcards_cli.py passes with no orphaned temp files | C15 |
| C47 | Complete/verify the review-all failed-review test so it asserts the failure path end to end (output, exit, and that other cards still process). | F9,F176,F265,Goal:engine,Goal:governance | tests/cli/test_review_all_logic.py:190 | pytest tests/cli/test_review_all_logic.py::<failed_review test> passes asserting the failure is surfaced and remaining cards proceed | C12,C14 |
| C48 | Repair conftest fixtures shared by the suite: add the missing timedelta import, move in-function imports (logging) to module level, generate UUIDs dynamically instead of hardcoding, and remove global sys.path mutation side effects. | F8,F25,F50,F68,F90,F105,F133,F153,F175,F192,F223,F243,F263,F277,F281,F292,F307,F346,F379,Goal:governance | tests/conftest.py:5,22-25,83,104-120,148,180,182,202 | pytest tests/ collects with no import error; fixtures produce distinct UUIDs across runs; no sys.path side effects leak between tests | none |
| C49 | Run the full suite and reconcile the documented baseline: after all production+test changes, capture the new expected pass count and update CLAUDE.md so the baseline reflects reality (closes the governance loop). | F357,Goal:governance | CLAUDE.md:154 (and tests/ overall) | source .venv/bin/activate && pytest tests/ -q passes; CLAUDE.md baseline line matches the observed count/skip | C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11,C12,C13,C14,C15,C16,C17,C18,C19,C21,C23,C34,C35,C36,C37,C38,C39,C40,C41,C42,C43,C44,C45,C46,C47,C48 |


## Machine-checkable data

```json
{
  "items": [
    {
      "id": "C1",
      "change": "Unify the review rating scale to a single canonical 1-4 (Rating enum) across UI capture, ReviewProcessor, and DB persistence; remove the implicit UI(0-3)->DB(+1) conversion so there is one source of truth. Document the canonical scale in flashcore/constants.py.",
      "links_to": "F47,F74,F129,F160,F168,F181,F215,F250,F289,F331,F361,Goal:engine",
      "location": "flashcore/review_processor.py:140-183, flashcore/review_manager.py, flashcore/cli/review_ui.py:68-127, flashcore/constants.py:10-13",
      "verification": "grep -r 'rating.*[0-3]' flashcore/ returns no off-by-one conversion sites; new test asserts a UI rating maps to the identical DB rating with no +1 offset",
      "depends_on": "none"
    },
    {
      "id": "C2",
      "change": "Fix FSRS elapsed_days computation: stop setting fsrs_card.last_review = fsrs_card.due (line 212); use the card's actual previous review timestamp so on-time reviews yield elapsed_days>0 and correct retrievability instead of R=1.0.",
      "links_to": "F4,F87,F169,F255,F115,Goal:engine",
      "location": "flashcore/scheduler.py:211-224 (and docstring example at 86)",
      "verification": "tests/test_scheduler.py: on-time review produces elapsed_days>0 and stability differs from a same-day re-review; existing scheduler tests still pass",
      "depends_on": "none"
    },
    {
      "id": "C3",
      "change": "Verify/align DEFAULT_PARAMETERS against the installed py-fsrs v6 weight vector (21 params) and update the scheduler docstring example at line 86 to match.",
      "links_to": "F360,F115,Goal:engine",
      "location": "flashcore/constants.py:10-13, flashcore/scheduler.py:86",
      "verification": "python -c \"from fsrs import FSRS; from flashcore.constants import DEFAULT_PARAMETERS; assert len(DEFAULT_PARAMETERS)==len(FSRS().w)\" passes",
      "depends_on": "C2"
    },
    {
      "id": "C4",
      "change": "Resolve dead/over-generic exceptions: either raise MarshallingError where DB<->model conversion fails or remove it; narrow generic FlashcardDatabaseError uses to specific subclasses where the operation is card/review/session-specific.",
      "links_to": "F65,F233,F287,Goal:engine",
      "location": "flashcore/exceptions.py:45,64-67",
      "verification": "grep -r 'raise MarshallingError' flashcore/ returns >=1 hit (or the class is deleted); no remaining bare FlashcardDatabaseError raises for typed operations",
      "depends_on": "none"
    },
    {
      "id": "C5",
      "change": "Add error handling to db_row_to_review mirroring db_row_to_card: wrap Review(**row_dict) in try/except, log the missing/invalid column, and raise MarshallingError with context instead of an uncaught Pydantic ValidationError.",
      "links_to": "F7,F62,F89,F101,F140,F148,F228,F235,F259,F329,F375,Goal:engine",
      "location": "flashcore/db/db_utils.py:120-123,156-158",
      "verification": "tests/test_db_errors.py: a review row missing 'rating' raises MarshallingError naming the column rather than a raw ValidationError",
      "depends_on": "C4"
    },
    {
      "id": "C6",
      "change": "Make backup_database timestamps timezone-safe by using datetime.now(timezone.utc) to avoid cross-timezone backup filename collisions.",
      "links_to": "F7,F62,F89,F148,F235,F259,F329,F375,Goal:engine",
      "location": "flashcore/db/db_utils.py:269",
      "verification": "unit test: backup filename matches a UTC-derived timestamp pattern; two backups across simulated TZs do not collide",
      "depends_on": "none"
    },
    {
      "id": "C7",
      "change": "Fix the connection-state guard default: change getattr(conn,'closed',True) to default False so rollback is attempted when the attribute is absent; verify tag filtering (list_contains on JSON tags) returns correct rows and clarify affected-rows semantics in upsert.",
      "links_to": "F59,F302,F372,F376,F328,Goal:engine",
      "location": "flashcore/db/database.py:255,475-484,481-484,600,628,736,963,1030",
      "verification": "tests/test_db_errors.py: mock connection lacking 'closed' attribute still triggers rollback; get_due_cards tag filter integration test returns the tagged card",
      "depends_on": "none"
    },
    {
      "id": "C8",
      "change": "Consolidate review submission through a single shared ReviewProcessor instance (created once per session, not per card) and add a duplicate-submission guard so a double-submit of the same card cannot create two reviews.",
      "links_to": "F124,F145,F151,F236,F282,F306,F377,Goal:engine",
      "location": "flashcore/review_processor.py:9,140-183, flashcore/cli/_review_all_logic.py:183-200,185",
      "verification": "tests/test_review_processor.py: ReviewProcessor.__init__ invoked once per review-all run; second identical process_review_by_uuid call is rejected or no-ops",
      "depends_on": "C1"
    },
    {
      "id": "C9",
      "change": "Remove the re-sort of already-due-ordered cards by modified_at; preserve next_due_date ASC ordering so overdue cards are reviewed first (SRS priority invariant).",
      "links_to": "F1,F170,F326,Goal:engine",
      "location": "flashcore/review_manager.py:109",
      "verification": "tests/test_review_manager.py: with three cards due on distinct dates, review_queue[0] is the earliest-due card",
      "depends_on": "none"
    },
    {
      "id": "C10",
      "change": "Stop silently swallowing session-analytics failures in ReviewManager: propagate or flag start_session/end_session failures and add defensive null-checks before deriving cards_per_minute/accuracy so DB failures don't crash or emit garbage metrics.",
      "links_to": "F147,F324,Goal:engine",
      "location": "flashcore/review_manager.py:91-103,248-320",
      "verification": "tests/test_review_manager.py: mocked start_session raising yields graceful basic-stats path; end_session returning null durations does not raise ZeroDivisionError",
      "depends_on": "none"
    },
    {
      "id": "C11",
      "change": "Correct deck-switch accounting (count transitions, not first-access), clamp active duration and deck_switch_efficiency to non-negative, surface (not swallow) update_session failures, and validate row keys in _get_session_reviews before constructing Review objects.",
      "links_to": "F5,F6,F63,F84,F88,F150,F171,F234,F256,F262,F327,F373,F374,Goal:engine",
      "location": "flashcore/session_manager.py:204-215,229-238,255-264,337-338,473-558,643-644",
      "verification": "tests/test_session_model.py + tests/test_session_manager.py: reviewing same deck twice keeps deck_switches==0; pause>total clamps duration>=0; switches=15 yields efficiency>=0; missing review column logs + raises typed error",
      "depends_on": "C5"
    },
    {
      "id": "C12",
      "change": "Harden review_ui flow: distinguish retryable vs permanent errors instead of catching all and continuing; track a reviewed_count and only print the success ('Well done') message when at least one card was actually reviewed; fail the session on un-updated cards.",
      "links_to": "F82,F143,F324,Goal:engine",
      "location": "flashcore/cli/review_ui.py:68-127,100-111,127",
      "verification": "tests/cli/test_review_all_logic.py / review_ui test: when all submit_review calls fail, output omits 'Well done' and exit signals failure",
      "depends_on": "C1,C8"
    },
    {
      "id": "C13",
      "change": "Add explicit, wrapped schema-initialization error handling in the single-deck review entrypoint so initialize_schema failures surface a clear DatabaseError rather than a raw traceback.",
      "links_to": "F35,F58,F85,F114,F139,F207,F227,F258,F300,Goal:engine",
      "location": "flashcore/cli/_review_logic.py:31-43",
      "verification": "flashcore review <deck> against an uninitializable DB prints a clear error; covered by a CLI test asserting the message and non-zero exit",
      "depends_on": "none"
    },
    {
      "id": "C14",
      "change": "Improve review-all robustness: log exceptions with logger.exception (including the SQL) instead of console-only prints, and document/justify the date.today() timezone assumption for due-card selection.",
      "links_to": "F64,F141,F145,Goal:engine",
      "location": "flashcore/cli/_review_all_logic.py:31-32,112-158,140-158",
      "verification": "injected DB error is recorded with traceback+SQL in the log; due-card boundary test (today vs today+1) selects only today",
      "depends_on": "C8"
    },
    {
      "id": "C15",
      "change": "Fix vet ingest path handling: validate source_dir exists before globbing (report 'directory not found' rather than 'no files found'), and make UUID handling robust so a parse failure does not silently drop a card's UUID.",
      "links_to": "F2,F3,F83,F86,F116,F173,F257,F325,Goal:engine",
      "location": "flashcore/cli/_vet_logic.py:59-80,80,276-279",
      "verification": "flashcore vet --source-dir /nonexistent reports a missing-directory error; vetting a valid file twice is idempotent (no UUID churn)",
      "depends_on": "none"
    },
    {
      "id": "C16",
      "change": "Close the media-path traversal gap: replace the str(...).startswith(assets_root) prefix check with full_media_path.resolve().relative_to(abs_assets_root) guarded by ValueError, so symlink/../ escapes are rejected.",
      "links_to": "F14,F93,F111,F142,F172,F182,F229,F267,F301,F323,F338,Goal:engine",
      "location": "flashcore/yaml_validators.py:267 (within 1-553)",
      "verification": "tests/test_yaml_validators.py: a media path resolving outside the assets root (incl. via symlink/..) is rejected; in-root paths still validate",
      "depends_on": "none"
    },
    {
      "id": "C17",
      "change": "Make secret detection check both front and back and report all matched fields (not just the first), keeping content referenced by field-name only (never echo the secret value).",
      "links_to": "F61,F230,F260,Goal:engine,Goal:governance",
      "location": "flashcore/yaml_validators.py:64-90,115-136",
      "verification": "tests/test_yaml_validators.py: a card with secrets in both fields reports both field names; error message contains no secret substring",
      "depends_on": "C16"
    },
    {
      "id": "C18",
      "change": "Fix YAML model edge cases: normalize tags=None to [] before KebabCase validation, and fix the question-snippet truncation off-by-one so the documented max length matches output.",
      "links_to": "F22,F60,F100,F146,F190,F204,F231,F232,F304,F305,Goal:engine",
      "location": "flashcore/yaml_models.py:91-95,265,291-325",
      "verification": "tests/test_yaml_validators.py / model test: 'tags: null' validates to []; a 50-char snippet produces the documented length",
      "depends_on": "none"
    },
    {
      "id": "C19",
      "change": "Harden the parser: guard against missing q/a keys in _prepare_card_data with an explicit error, and move the fail_fast raise before partial results are appended so fail_fast has clean stop semantics; add the missing module docstring.",
      "links_to": "F230,F261,F274,Goal:engine",
      "location": "flashcore/parser.py:1,144-163,225-228",
      "verification": "tests/test_parser.py: a card dict missing 'q' raises a clear error; fail_fast=True on a multi-file load excludes downstream-file cards",
      "depends_on": "none"
    },
    {
      "id": "C20",
      "change": "Add module docstrings / clarify the spoke models entrypoint so flashcore/models.py documents the Card/Review/Session public surface (template heritage cleanup, no logic change).",
      "links_to": "F42,F119,F152,F210,F354,Goal:engine",
      "location": "flashcore/models.py:1-4",
      "verification": "module imports cleanly; docstring present (pydocstyle/inspection)",
      "depends_on": "none"
    },
    {
      "id": "C21",
      "change": "Fix the migration validator state comparison so it handles state stored as enum-name vs integer consistently (normalize before the != 'New' check), preventing false negatives during the one-time legacy->DuckDB migration.",
      "links_to": "F144,F284,F371,Goal:migration",
      "location": "flashcore/scripts/migrate.py:122,184-204",
      "verification": "migrate a legacy DB with integer-coded state; validate_migration correctly flags/accepts states; row-count and orphan checks pass",
      "depends_on": "C1"
    },
    {
      "id": "C22",
      "change": "Document/parameterize the hardcoded table-name SQL in dump_history (the f-string is safe because the names are a fixed tuple) — add an assertion/comment asserting no user input reaches the query.",
      "links_to": "F15,F211,F268,F342,Goal:engine",
      "location": "flashcore/scripts/dump_history.py:45",
      "verification": "code review confirms table names come only from the literal tuple; assertion guards against external input",
      "depends_on": "none"
    },
    {
      "id": "C23",
      "change": "Make the Anki export command fail explicitly: print the not-implemented message AND raise typer.Exit(code=1) so callers/scripts detect the failure; verify db-path resolution helper raises a catchable error rather than calling typer.Exit from a helper.",
      "links_to": "F39,F112,F149,F198,F237,F328,F353,F378,Goal:engine",
      "location": "flashcore/cli/main.py:51-53,199-201,543-549",
      "verification": "flashcore export anki && echo OK does not print OK (exit code 1); unit test of db-path resolver catches an exception without process exit",
      "depends_on": "none"
    },
    {
      "id": "C24",
      "change": "Pin the container base image to a supported, digest-pinned Python (e.g. python:3.11-slim@sha256:...) matching pyproject's requires-python, replacing the EOL/unpinned base.",
      "links_to": "F31,F98,F102,F109,F187,F197,F270,F340,Goal:governance",
      "location": "Containerfile:1-5",
      "verification": "docker/podman build succeeds; image python version satisfies requires-python; base referenced by digest",
      "depends_on": "none"
    },
    {
      "id": "C25",
      "change": "Pin all GitHub Actions to immutable commit SHAs (checkout/setup-python/action-gh-release) across release.yml, main.yml, rename_project.yml, and aiv-guard.yml, replacing floating @vN tags.",
      "links_to": "F19,F32,F33,F110,F186,F199,F202,F273,F303,F341,F355,Goal:governance",
      "location": ".github/workflows/release.yml:21,29,38,51, .github/workflows/main.yml:25-26, .github/workflows/rename_project.yml:13,39, .github/workflows/aiv-guard.yml:21,26",
      "verification": "grep for 'uses:.*@v' across .github/workflows returns no floating tags; workflows still parse (actionlint) and a dry release run succeeds",
      "depends_on": "none"
    },
    {
      "id": "C26",
      "change": "Pin the aiv-protocol git dependency to a specific commit SHA in both the workflow install and pyproject so the AIV guard runs deterministically.",
      "links_to": "F18,F97,F113,F183,F269,F337,F343,F358,Goal:governance",
      "location": ".github/workflows/aiv-guard.yml:33,44, pyproject.toml:43",
      "verification": "aiv-guard install resolves to the pinned SHA; pyproject and workflow reference the same commit; aiv check output stable across reruns",
      "depends_on": "none"
    },
    {
      "id": "C27",
      "change": "Harden the template rename workflow: scope down 'write-all' permissions to least privilege, quote variable expansions, and remove/guard the --force push so it cannot overwrite protected branches.",
      "links_to": "F16,F17,F20,F95,F96,F184,F185,F272,F275,F339,Goal:template,Goal:governance",
      "location": ".github/workflows/rename_project.yml:6,37,39,43",
      "verification": "actionlint passes; permissions block lists only contents/pull-requests; no unquoted ${{ }} in shell; no unconditional --force",
      "depends_on": "none"
    },
    {
      "id": "C28",
      "change": "Make the rename sed script injection-safe: quote filenames, escape regex/replacement metacharacters in author/name substitutions, and write a .bak for recovery (or port to a small Python replacement).",
      "links_to": "F21,F94,F188,F271,F334,F335,Goal:template",
      "location": ".github/rename_project.sh:26-30",
      "verification": "running the script with author values containing / & and filenames with spaces completes without corruption; .bak files exist",
      "depends_on": "none"
    },
    {
      "id": "C29",
      "change": "Fix the bootstrap init script: correct the shell syntax error (stray brace ~line 62), quote/validate template path and URL before clone/source to prevent injection, and validate template selection.",
      "links_to": "F12,F13,F38,F99,F209,F286,F336,Goal:template",
      "location": ".github/init.sh:13,14,35-36,62,63",
      "verification": "bash -n .github/init.sh passes (no syntax error); shellcheck reports no unquoted-injection warnings for template path/URL",
      "depends_on": "none"
    },
    {
      "id": "C30",
      "change": "Tighten dependabot config to constrain updates to direct dependencies with an explicit versioning strategy.",
      "links_to": "F276,Goal:governance",
      "location": ".github/dependabot.yml:4",
      "verification": "dependabot config validates; only direct github-actions updates are proposed",
      "depends_on": "C25"
    },
    {
      "id": "C31",
      "change": "Correct .aiv.yml functional-prefix scope so operational CI/workflow edits do not falsely trigger AIV functional-change revalidation while code paths still do.",
      "links_to": "F34,F117,F208,F356,Goal:governance",
      "location": ".aiv.yml:13-14",
      "verification": "editing only a .github/workflows file does not require a functional packet; editing flashcore/ still does (aiv check on a sample diff)",
      "depends_on": "none"
    },
    {
      "id": "C32",
      "change": "Replace template placeholders in the Makefile: derive the release author from git config instead of the hardcoded 'rochacbruno', and drop non-ASCII content from release commit messages.",
      "links_to": "F36,F40,F120,F201,F206,Goal:template,Goal:governance",
      "location": "Makefile:83-84,101",
      "verification": "make release (dry) produces a commit authored from git config with an ASCII-only message; no 'rochacbruno' remains in the Makefile",
      "depends_on": "none"
    },
    {
      "id": "C33",
      "change": "Clean residual template scaffolding/config: set .taskmaster projectName to 'flashcore', strengthen the placeholder task verification strategy, fix the duplicated/invalid-glob .windsurfrules, document .env.example required keys, complete mkdocs.yml metadata, and update the stale CLAUDE.md test baseline reference.",
      "links_to": "F37,F41,F44,F45,F118,F121,F122,F203,F205,F212,F283,F285,F357,F359,Goal:template,Goal:governance",
      "location": ".taskmaster/config.json:28, .taskmaster/tasks/tasks.json:92, .windsurfrules:1,9,535,1062, .env.example:1, mkdocs.yml:1, CLAUDE.md:154, requirements-test.txt:1",
      "verification": "no 'Taskmaster'/template author placeholders remain; mkdocs build succeeds; .windsurfrules has a single DEV_WORKFLOW + valid glob; baseline note matches actual pytest count",
      "depends_on": "none"
    },
    {
      "id": "C34",
      "change": "Replace the rating-inconsistency 'documentation' tests that assert the bug exists (DB=UI+1) with tests that assert the unified 1-4 scale end to end; remove tests that would now be tautological.",
      "links_to": "F47,F74,F129,F160,F168,F181,F215,F250,F289,F331,F361,Goal:engine,Goal:governance",
      "location": "tests/test_rating_system_inconsistency.py:33,321-357",
      "verification": "pytest tests/test_rating_system_inconsistency.py passes asserting one canonical scale; no test asserts a +1 conversion",
      "depends_on": "C1"
    },
    {
      "id": "C35",
      "change": "Convert test_review_logic_duplication.py from documenting-the-duplication (asserting interface specs / step counts / NaN workarounds) into real behavioral tests of the consolidated ReviewProcessor, or fold them into test_review_processor.py.",
      "links_to": "F49,F75,F76,F77,F126,F127,F128,F165,F216,F217,F248,F249,F264,F290,F299,F319,F320,F330,F362,F367,F382,Goal:engine,Goal:governance",
      "location": "tests/test_review_logic_duplication.py:1-10,141-148,167-211,279-370",
      "verification": "pytest of the rewritten file exercises ReviewProcessor outputs (not metadata assertions); grep confirms no 'assert len(duplication_steps)' style checks remain",
      "depends_on": "C8"
    },
    {
      "id": "C36",
      "change": "Convert test_session_analytics_gaps.py from GAP-comment placeholders that assert features are missing into real assertions that session lifecycle/analytics persist and compute correctly (after C11).",
      "links_to": "F48,F55,F79,F130,F131,F132,F166,F167,F180,F218,F219,F251,F252,F253,F254,F288,F294,F313,F314,F315,F316,F317,F318,F321,F363,F364,F370,Goal:engine,Goal:governance",
      "location": "tests/test_session_analytics_gaps.py:1-13,26-34,59,135-499",
      "verification": "pytest of the rewritten file asserts session rows persist and metrics (deck switches/efficiency/duration) are correct; no '# GAP' comment stands in for an assertion",
      "depends_on": "C11"
    },
    {
      "id": "C37",
      "change": "Strengthen DB tests: de-duplicate fixtures (import from conftest instead of redefining), make connection/get-all tests assert real content not just non-null/len, replace over-mocked schema-constraint tests with real :memory: inserts, and un-skip the force_recreate test against the current API.",
      "links_to": "F26,F56,F69,F70,F71,F133,F155,F156,F161,F224,F225,F244,F296,F308,F309,F345,F348,F352,F365,F380,F381,Goal:engine,Goal:governance",
      "location": "tests/test_db.py:25-93,111,283,344-395,415-433,597-605,942",
      "verification": "pytest tests/test_db.py passes with fixtures sourced from conftest; constraint tests use a real DB; no unexplained skips remain",
      "depends_on": "C7"
    },
    {
      "id": "C38",
      "change": "Replace over-mocked coverage tests with real DB behavior (closed-connection upsert, recreate-order, safety-check messages) and rename gap-named tests to guard-style names.",
      "links_to": "F72,F73,F91,F157,F158,F245,F246,F279,F291,F310,F311,F347,Goal:engine,Goal:governance",
      "location": "tests/test_db_coverage.py:18,55,65-66,88,96-112,158-178",
      "verification": "pytest tests/test_db_coverage.py passes using a real DB for closed-connection/recreate paths; pytest.raises calls include match= on messages",
      "depends_on": "C7"
    },
    {
      "id": "C39",
      "change": "Fix DB error tests to assert behavior over implementation detail: replace logger call-count assertions and bare exception catches with message-matched assertions, pass valid objects where the test currently passes a wrong type, and correct the read-only setup ordering.",
      "links_to": "F11,F54,F92,F137,F159,F220,F247,F266,F295,F312,F368,F384,Goal:engine,Goal:governance",
      "location": "tests/test_db_errors.py:83,336,391,413,464-474,509-514,636",
      "verification": "pytest tests/test_db_errors.py passes; each pytest.raises includes match=; read-only test initializes schema before reopening read-only",
      "depends_on": "C5,C7"
    },
    {
      "id": "C40",
      "change": "Tighten session model/manager tests: assert deck-switch tracking both directions, de-flake the pause/resume timing assertion (mock time or assert state not magnitude), and complete any truncated test bodies.",
      "links_to": "F10,F51,F80,F81,F134,F138,F177,F179,F226,F298,F332,F333,F349,F369,Goal:engine,Goal:governance",
      "location": "tests/test_session_model.py:144-148,271-297, tests/test_session_manager.py:168-177,237-253,1003",
      "verification": "pytest of both files passes deterministically (run x10 with no flake); switch-back increments the counter",
      "depends_on": "C11"
    },
    {
      "id": "C41",
      "change": "De-mock review-manager tests so they exercise real review logic against a DB, and replace enum-arithmetic magic (Rating.Again.value+1) with explicit Rating members.",
      "links_to": "F53,F108,F135,F178,F221,F222,F293,F322,Goal:engine,Goal:governance",
      "location": "tests/test_review_manager.py:106,134-135,171-173,502",
      "verification": "pytest tests/test_review_manager.py passes verifying the card was actually updated; no Rating value arithmetic remains",
      "depends_on": "C1,C9,C10"
    },
    {
      "id": "C42",
      "change": "Complete the incomplete review_processor logging test (add real assertions) and relocate the misplaced review_processor success test out of test_scheduler.py into test_review_processor.py.",
      "links_to": "F78,F52,Goal:engine,Goal:governance",
      "location": "tests/test_review_processor.py:320, tests/test_scheduler.py:477",
      "verification": "pytest both files pass; the relocated test lives only in test_review_processor.py (grep confirms single definition)",
      "depends_on": "C8"
    },
    {
      "id": "C43",
      "change": "Strengthen parser tests: assert error content/file (not just counts) and extract duplicated inline YAML fixtures into a shared fixture.",
      "links_to": "F24,F104,F195,F196,F350,Goal:engine,Goal:governance",
      "location": "tests/test_parser.py:82,344-361",
      "verification": "pytest tests/test_parser.py passes asserting offending file name in errors; YAML literals sourced from one fixture",
      "depends_on": "C19"
    },
    {
      "id": "C44",
      "change": "Fix yaml_validator tests: stop mocking Path.resolve and use real tmp dirs, split the over-mocked combined-validator test into per-validator tests, add the negative assertion to the 'skipped' test, and parameterize hardcoded deck/tag data.",
      "links_to": "F23,F28,F29,F103,F107,F191,F193,F278,F351,Goal:engine,Goal:governance",
      "location": "tests/test_yaml_validators.py:74,98-102,216,277-285",
      "verification": "pytest tests/test_yaml_validators.py passes against real paths; the traversal/skipped cases assert the would-fail path",
      "depends_on": "C16,C17,C18"
    },
    {
      "id": "C45",
      "change": "Improve CLI main tests: add real-DB integration coverage alongside the heavily-mocked unit tests, replace double-negative success assertions with direct exit_code==0 checks, assert required-arg help text, and share strip_ansi via conftest.",
      "links_to": "F27,F30,F57,F67,F106,F136,F154,F162,F164,F194,F214,F239,F240,F241,F242,F280,F344,Goal:engine,Goal:governance",
      "location": "tests/cli/test_main.py:24,557,697-747,886-893,912,944-1044",
      "verification": "pytest tests/cli/test_main.py passes; resolve-db-path test asserts exit_code==0 directly; strip_ansi defined once in conftest",
      "depends_on": "C23"
    },
    {
      "id": "C46",
      "change": "Fix flashcards-CLI fixture hygiene (explicit yield/cleanup) and ensure the fixture exercises real file ingestion paths.",
      "links_to": "F46,F66,F125,F163,F213,F238,F297,F366,F383,Goal:governance",
      "location": "tests/cli/test_flashcards_cli.py:79-91",
      "verification": "pytest tests/cli/test_flashcards_cli.py passes with no orphaned temp files",
      "depends_on": "C15"
    },
    {
      "id": "C47",
      "change": "Complete/verify the review-all failed-review test so it asserts the failure path end to end (output, exit, and that other cards still process).",
      "links_to": "F9,F176,F265,Goal:engine,Goal:governance",
      "location": "tests/cli/test_review_all_logic.py:190",
      "verification": "pytest tests/cli/test_review_all_logic.py::<failed_review test> passes asserting the failure is surfaced and remaining cards proceed",
      "depends_on": "C12,C14"
    },
    {
      "id": "C48",
      "change": "Repair conftest fixtures shared by the suite: add the missing timedelta import, move in-function imports (logging) to module level, generate UUIDs dynamically instead of hardcoding, and remove global sys.path mutation side effects.",
      "links_to": "F8,F25,F50,F68,F90,F105,F133,F153,F175,F192,F223,F243,F263,F277,F281,F292,F307,F346,F379,Goal:governance",
      "location": "tests/conftest.py:5,22-25,83,104-120,148,180,182,202",
      "verification": "pytest tests/ collects with no import error; fixtures produce distinct UUIDs across runs; no sys.path side effects leak between tests",
      "depends_on": "none"
    },
    {
      "id": "C49",
      "change": "Run the full suite and reconcile the documented baseline: after all production+test changes, capture the new expected pass count and update CLAUDE.md so the baseline reflects reality (closes the governance loop).",
      "links_to": "F357,Goal:governance",
      "location": "CLAUDE.md:154 (and tests/ overall)",
      "verification": "source .venv/bin/activate && pytest tests/ -q passes; CLAUDE.md baseline line matches the observed count/skip",
      "depends_on": "C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11,C12,C13,C14,C15,C16,C17,C18,C19,C21,C23,C34,C35,C36,C37,C38,C39,C40,C41,C42,C43,C44,C45,C46,C47,C48"
    }
  ],
  "_ambiguous": [
    "C33"
  ]
}
```
