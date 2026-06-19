# F169 prove-it Evidence Manifest

Baseline ref: `b5e1c4b983b33602e8531340f382c72626a0fb59` (origin/main)
HEAD ref: `feat/c2-fsrs-harness` (current branch at time of capture)
Date: 2026-06-19

| sha256 | artifact | claim proven | cited baseline ref | AIV class |
|--------|----------|--------------|-------------------|-----------|
| `3863d463df5b1c04a39f2206dea1029cf33c2b05ae826f59b5b5c7366c62fffb` | `baseline_direct_probe.txt` | BUG CONFIRMED at b5e1c4b: elapsed_days=0 for on-time Review-state review (stability=14.0 unchanged) | b5e1c4b | A + D |
| `abac58d9dd4b924140d193c81aafb71091ad3fc53b219420f0211db3099fb9b2` | `head_direct_probe.txt` | FIX CONFIRMED at HEAD: elapsed_days=14 for on-time Review-state review (stability=44.8064, updated) | b5e1c4b (diff against) | A + D |
| `a4155a5abed242bcd918b0dd8abe9df6f42c2cb4034a2ab0e034772ca1496bfc` | `baseline_red.txt` | F169 test suite FAILS at baseline: Card model rejects last_review_date (extra="forbid"), confirming field is absent on the model at b5e1c4b | b5e1c4b | A + D |
| `ce2d454d0423458a33322be2c2eeb4eeca1c34bbfc7155c7b5494896f31d7db9` | `head_green.txt` | F169 test suite PASSES at HEAD: test_on_time_review_elapsed_days_positive and test_on_time_vs_same_day_review_stability_distinct both pass | b5e1c4b (diff against) | A + D |
| `3d3abad8f71b2ff8929bb8e7907ee34ba65e819c88e80d2e0fafc890a212f721` | `head_full_scheduler.txt` | All 17 scheduler tests pass at HEAD (15 original + 2 new F169 guards) — zero regressions | b5e1c4b | A |
| `ef464c8516c87fe30761ff666b9937ad5211ab14be7cdcdbdff8843132a98c59` | `layerb_integration.txt` | Layer-B: test_on_time_review_persists_positive_elapsed_days PASSES — process_review against real SQLite DB via ReviewProcessor produces elapsed_days_at_review > 0 | b5e1c4b | A (composed path) |
| `b1e664b8e68424a40aeefdca9ecd2696f222f86d562e015d06dd1533e31a5334` | `mypy_clean.txt` | mypy on flashcore/scheduler.py + flashcore/models.py: zero errors in touched files; pre-existing stub errors in yaml_models.py/parser.py are unrelated to F169 | b5e1c4b | D |
| `1a3004173fc26d636af23b60285622c302b63aada2ede9e51e0c817ae00e112c` | `full_suite_head.txt` | Full test suite: 483 passed, 1 skipped (baseline was 480+1; 3 new F169 tests added) | b5e1c4b | A |

## Adversarial review summary

- **baseline_red.txt** was flagged by adversarial probe as proving model-field absence (pydantic ValidationError), not the scheduler defect directly. **Remediated** by `baseline_direct_probe.txt`, which drives the baseline scheduler with a baseline-compatible Card (no last_review_date) and directly observes elapsed_days=0 and stability=14.0 (unchanged — FSRS received elapsed_days=0, produced no meaningful update).
- **head_green.txt** was assessed VALID PROOF by independent assessor: assertions are non-vacuous, Card's extra="forbid" prevents silent field-missing scenarios, no mocks used.
- **layerb_integration.txt**: composed-path proof (real DB + real scheduler + ReviewProcessor hub); no stubs.
