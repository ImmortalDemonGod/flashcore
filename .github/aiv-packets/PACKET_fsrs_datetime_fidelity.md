# AIV Verification Packet (v2.2)

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/ImmortalDemonGod/aiv-protocol |
| **Change ID** | fsrs-datetime-fidelity |
| **Commits** | `dfd5d5f`, `0440ed3`, `47f0ba7`, `5d96cc4`, `5f034db`, `103312d`, `85959f3`, `e8df5fb`, `966032e`, `fd41993`, `2d28a38`, `d7a5cdf`, `77929c7`, `f97a3ca`, `661a3f9`, `b826924` |
| **Head SHA** | `b826924` |
| **Base SHA** | `fb1ae5a` |
| **Created** | 2026-06-29T20:47:54Z |

## Classification

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: component
  classification_rationale: "R1 correctness-critical FSRS scheduling path plus a DB schema migration (next_due_date/next_due DATE->TIMESTAMPTZ, +cards.step); blast radius is the scheduler/hub data flow and the kernel due predicates."
  classified_by: "Miguel Ingram"
  classified_at: "2026-06-29T20:47:54Z"
```

## Claims

1. Card.next_due_date and last_review_date are typed datetime (not date) so sub-day FSRS spacing is representable
2. Card.step (Optional int) is added under extra=forbid for persisting the FSRS learning-step index
3. No existing tests were modified or deleted during this change.
4. FSRS_Scheduler.compute_next_state returns next_due as a datetime preserving sub-day learning-step spacing
5. FSRS_Scheduler.compute_next_state restores and emits the FSRS learning step so Learning cards progress across reviews
6. ReviewProcessor.process_review sets last_review_date from the full prior-review timestamp not its date
7. ReviewProcessor.process_review persists the scheduler step via add_review_and_update_card new_step
8. cards.next_due_date and reviews.next_due are TIMESTAMP WITH TIME ZONE and cards has a step column
9. FlashcardDatabase.get_due_cards compares next_due_date against a timestamp, coercing a bare date to end-of-day
10. FlashcardDatabase persists the FSRS step via the cards upsert and the post-review card update
11. card_to_db_params_list includes card.step as the trailing value of the cards insert tuple
12. start_review_flow computes days-until-due from next_due_date.date() so it works with datetime dues
13. _review_all_logic computes days-until-due from next_due_date.date() so it works with datetime dues
14. migrate_to_datetime_fidelity converts the due columns to TIMESTAMPTZ, adds cards.step, and backfills step=0 for Learning/Relearning idempotently
15. test_scheduler asserts learning-step next_due is a future sub-day datetime and that step persistence graduates a card
16. test_db asserts next_due_date.date() since the column is now a timestamp
17. test_review_manager SchedulerOutput fixtures include step and use datetime next_due
18. test_review_processor SchedulerOutput fixtures include step and assert datetime next_due
19. test_review_logic_duplication SchedulerOutput fixture includes the step field
20. test_review_ui mocks next_due_date as a datetime so .date() resolves
21. test_review_all_logic mocks next_due_date as a datetime so .date() resolves

---

## Evidence References

| # | Evidence File | Commit SHA | Classes |
|---|---------------|------------|---------|
| 1 | EVIDENCE_FLASHCORE_MODELS.md | `dfd5d5f` | A, B, E |
| 2 | EVIDENCE_FLASHCORE_SCHEDULER.md | `0440ed3` | A, B, E |
| 3 | EVIDENCE_FLASHCORE_REVIEW_PROCESSOR.md | `47f0ba7` | A, B, E |
| 4 | EVIDENCE_FLASHCORE_DB_SCHEMA.md | `5d96cc4` | A, B, E |
| 5 | EVIDENCE_FLASHCORE_DB_DATABASE.md | `5f034db` | A, B, E |
| 6 | EVIDENCE_FLASHCORE_DB_DB_UTILS.md | `103312d` | A, B, E |
| 7 | EVIDENCE_FLASHCORE_CLI_REVIEW_UI.md | `85959f3` | A, B, E |
| 8 | EVIDENCE_FLASHCORE_CLI__REVIEW_ALL_LOGIC.md | `e8df5fb` | A, B, E |
| 9 | EVIDENCE_SCRIPTS_MIGRATE_TO_DATETIME_FIDELITY.md | `966032e` | A, B, E |
| 10 | EVIDENCE_TESTS_TEST_SCHEDULER.md | `fd41993` | A, B, E |
| 11 | EVIDENCE_TESTS_TEST_DB.md | `2d28a38` | A, B, E |
| 12 | EVIDENCE_TESTS_TEST_REVIEW_MANAGER.md | `d7a5cdf` | A, B, E |
| 13 | EVIDENCE_TESTS_TEST_REVIEW_PROCESSOR.md | `77929c7` | A, B, E |
| 14 | EVIDENCE_TESTS_TEST_REVIEW_LOGIC_DUPLICATION.md | `f97a3ca` | A, B, E |
| 15 | EVIDENCE_TESTS_CLI_TEST_REVIEW_UI.md | `661a3f9` | A, B, E |
| 16 | EVIDENCE_TESTS_CLI_TEST_REVIEW_ALL_LOGIC.md | `b826924` | A, B, E |

### Class E (Intent Alignment)

- **Requirement:** Live deck 2026-06-29: FSRS learning steps collapsed to a 0-day due-today because next_due was truncated to a DATE and the learning step index was never persisted; Learning cards never spaced or graduated except via Easy. Fix restores datetime fidelity + step persistence.

### Class B (Referential Evidence)

**Scope Inventory** (from 69 file references across evidence files)

- `flashcore/models.py#L11`
- `flashcore/models.py#L61`
- `flashcore/models.py#L64-L66`
- `flashcore/models.py#L69`
- `flashcore/models.py#L71-L75`
- `flashcore/models.py#L88-L95`
- `flashcore/models.py#L252`
- `flashcore/models.py#L254-L258`
- `flashcore/scheduler.py#L41-L43`
- `flashcore/scheduler.py#L48`
- `flashcore/scheduler.py#L208-L212`
- `flashcore/scheduler.py#L214-L216`
- `flashcore/scheduler.py#L218`
- `flashcore/scheduler.py#L268-L270`
- `flashcore/scheduler.py#L277`
- `flashcore/review_processor.py#L104-L106`
- `flashcore/review_processor.py#L132-L133`
- `flashcore/review_processor.py#L135-L137`
- `flashcore/review_processor.py#L140`
- `flashcore/db/schema.py#L17`
- `flashcore/db/schema.py#L21`
- `flashcore/db/schema.py#L46`
- `flashcore/db/database.py#L145-L146`
- `flashcore/db/database.py#L176-L180`
- `flashcore/db/database.py#L400-L407`
- `flashcore/db/database.py#L416`
- `flashcore/db/database.py#L453-L462`
- `flashcore/db/database.py#L467`
- `flashcore/db/database.py#L533`
- `flashcore/db/database.py#L704`
- `flashcore/db/database.py#L717-L718`
- `flashcore/db/database.py#L726`
- `flashcore/db/database.py#L733-L736`
- `flashcore/db/database.py#L746`
- `flashcore/db/database.py#L758`
- `flashcore/db/database.py#L783-L786`
- `flashcore/db/database.py#L807`
- `flashcore/db/db_utils.py#L97`
- `flashcore/cli/review_ui.py#L125-L127`
- `flashcore/cli/_review_all_logic.py#L88`
- `scripts/migrate_to_datetime_fidelity.py#L1-L151`
- `tests/test_scheduler.py#L53-L61`
- `tests/test_scheduler.py#L128-L131`
- `tests/test_scheduler.py#L215`
- `tests/test_scheduler.py#L241-L242`
- `tests/test_scheduler.py#L254`
- `tests/test_scheduler.py#L369-L370`
- `tests/test_scheduler.py#L395-L396`
- `tests/test_scheduler.py#L505`
- `tests/test_scheduler.py#L510`
- `tests/test_scheduler.py#L527`
- `tests/test_scheduler.py#L530`
- `tests/test_scheduler.py#L613-L614`
- `tests/test_scheduler.py#L820-L901`
- `tests/test_db.py#L1009-L1010`
- `tests/test_db.py#L1050-L1051`
- `tests/test_review_manager.py#L48`
- `tests/test_review_manager.py#L52`
- `tests/test_review_manager.py#L563`
- `tests/test_review_processor.py#L57`
- `tests/test_review_processor.py#L62`
- `tests/test_review_logic_duplication.py#L68`
- `tests/cli/test_review_ui.py#L5`
- `tests/cli/test_review_ui.py#L55`
- `tests/cli/test_review_ui.py#L98-L100`
- `tests/cli/test_review_ui.py#L341`
- `tests/cli/test_review_ui.py#L382`
- `tests/cli/test_review_all_logic.py#L138-L140`
- `tests/cli/test_review_all_logic.py#L538-L540`

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence was collected by `aiv commit` during the change lifecycle.
Packet generated by `aiv close`.

---

## Known Limitations

- Evidence references point to Layer 1 evidence files at specific commit SHAs.
  Use `git show <sha>:.github/aiv-evidence/<file>` to retrieve.

---

## Summary

Change 'fsrs-datetime-fidelity': 16 commit(s) across 16 file(s).
