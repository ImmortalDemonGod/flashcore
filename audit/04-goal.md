# 04 — Goal + Research

_Generated 2026-06-17 23:42:19 · branch `claude/nifty-brahmagupta-0tq0vy` · forensic-audit-pipeline (consolidated)_

## Candidate goals (plural by design; judged by a 3-vote panel)

| Goal | Status | Judge grounding |
| --- | --- | --- |
| Provide a local-first, CLI-driven spaced-repetition flashcard ENGINE: author cards in YAML, vet/ingest them into a DuckDB-backed store, schedule reviews with FSRS parameters, conduct review sessions, and export to Anki/Markdown. | grounded | 3/3 |
| Operate the repository as a rigorously governed, auditable engineering codebase where every change is gated by the AIV commit-packet protocol plus CI and tagged-release automation. | grounded | 3/3 |
| Enable a one-time, validated MIGRATION of flashcard/review/session data from a legacy database into the new DuckDB store. | grounded | 3/3 |
| Serve as / retain heritage of a reusable Python project TEMPLATE with self-rename and bootstrap scaffolding (template-derived origin). | speculative | 0/3 |

### GROUNDED — Provide a local-first, CLI-driven spaced-repetition flashcard ENGINE: author cards in YAML, vet/ingest them into a DuckDB-backed store, schedule reviews with FSRS parameters, conduct review sessions, and export to Anki/Markdown.
- ✅ Typer console app exposes the full lifecycle pipeline (vet, ingest, stats, review, review_all, export anki/md, restore) — _flashcore/cli/main.py:99 (vet), :298 (ingest), :418 (stats), :455 (review), :503 (review_all), :544 (export_anki), :553 (export_md), :594 (restore); console_script flashcore = flashcore.__main__:main at pyproject.toml:47_
- ✅ Scheduling is driven by FSRS via py-fsrs DEFAULT_PARAMETERS / DEFAULT_DESIRED_RETENTION — _flashcore/scheduler.py:17-30 (imports fsrs Card/Rating/State/Scheduler), :92-94 (default_factory tuple(DEFAULT_PARAMETERS), desired_retention=DEFAULT_DESIRED_RETENTION)_
- ✅ Self-described as a local-first SRS engine on FSRS + DuckDB — _pyproject.toml:8 description = "High-performance, local-first Spaced Repetition System engine using FSRS and DuckDB"_
- ✅ YAML authoring and Anki/Markdown export paths exist — _flashcore/parser.py (load_and_process_flashcard_yamls), flashcore/cli/_export_logic.py:15 (export_to_markdown), flashcore/cli/main.py:544/:553 (export_anki/export_md)_
- ❌ FSRS scheduling computes CORRECT review intervals (core engine promise) — _scheduler.py:212 sets fsrs_card.last_review=fsrs_card.due then computes elapsed_days at :219-222, yielding 0 for on-time reviews and forcing R=1.0 instead of ~0.9 — produces incorrect new intervals (Stage-2 finding)_
- ❌ Review queue is ordered by due-date priority (most-overdue first), as an SRS requires — _database.py:459 fetches due cards ordered by next_due_date ASC then initialize_session re-sorts by c.modified_at, overriding due-date priority (Stage-2 finding)_
### GROUNDED — Operate the repository as a rigorously governed, auditable engineering codebase where every change is gated by the AIV commit-packet protocol plus CI and tagged-release automation.
- ✅ AIV packet validation runs as a required PR gate — _.github/workflows/aiv-guard.yml (name: AIV Packet Validation (Python); on pull_request to main; step 'Run AIV Guard' → python -m aiv.guard)_
- ✅ CI enforces lint + pytest — _.github/workflows/main.yml; Makefile lint target (flake8/black/mypy) and test target_
- ✅ Tagged-release publishing pipeline exists — _.github/workflows/release.yml (name: Upload Python Package; on push tags; contents: write)_
- ✅ Mandatory aiv commit workflow is documented and binding — _CLAUDE.md 'AIV Commit Workflow (mandatory for all commits)' with begin/commit/close/check flow and risk tiers_
- ❌ Supply-chain hardening of the governance toolchain itself — _aiv-guard.yml installs aiv-protocol from git HEAD with no SHA pin; actions pinned to mutable tags (@v6) (Stage-2 SEC findings)_
### GROUNDED — Enable a one-time, validated MIGRATION of flashcard/review/session data from a legacy database into the new DuckDB store.
- ✅ Legacy-DB extraction to JSON utility exists — _flashcore/scripts/dump_history.py (dump_table/dump_database over cards, reviews, sessions tables)_
- ✅ Import + completeness-validation tooling into new DuckDB exists — _flashcore/scripts/migrate.py:1-18 docstring (import then validate migration completeness; import/validate subcommands)_
- ✅ Scripts are intentionally out-of-package one-off utilities — _CLAUDE.md 'Scripts (flashcore/scripts/): utility scripts, NOT part of the installed package'; located under flashcore/scripts/ not exported_
### SPECULATIVE — Serve as / retain heritage of a reusable Python project TEMPLATE with self-rename and bootstrap scaffolding (template-derived origin).
- ✅ Template rename/init scaffolding is present in-repo — _.github/workflows/rename_project.yml; .github/init.sh; .github/rename_project.sh; .github/release_message.sh_
- ❌ Rename automation is an ACTIVE goal vs vestigial template residue — _rename_project.yml on: workflow_dispatch only, guarded by if !contains(github.repository,'/python-project-template'); no scheduled/push trigger — consistent with one-time/dormant template residue rather than an ongoing objective (Invariant 8: stated/structural negatives not ground truth — unconfirmed)_

## External research 

| Idea | Advances | Corroboration |
| --- | --- | --- |
| Upgrade to FSRS v6 via the latest py-fsrs release (21 configurable parameters; improved same-day-review and forgetting-rate modeling over FSRS v4.5) | Flashcore uses FSRS-style parameters but the current implementation's elapsed_days calculation is already identified as broken (top finding #4). FSRS v6 is the consensus production standard (adopted by Anki Oct 2023, RemNote 2025) and reduces required reviews by ~20-30% vs. SM-2. Upgrading py-fsrs and aligning the elapsed_days fix to v6 semantics delivers both correctness and scheduling efficiency simultaneously. | corroborated |
| Integrate fsrs-optimizer (v6.5.0) to personalize FSRS parameters from a user's own review-history CSV exported from the DuckDB store | Flashcore hardcodes DEFAULT_PARAMETERS. The fsrs-optimizer library processes review logs following a standardised schema (invocable as `python -m fsrs_optimizer revlog.csv`) and produces per-user optimal weights, directly improving scheduling accuracy without changing the core engine. The DuckDB reviews table already holds the data needed to produce this export. | corroborated |
| Use DuckDB stream windowing functions (added in v1.2, May 2025) and time_bucket() for in-process retention-curve and scheduling-heatmap analytics | Flashcore's stats command currently performs Python-level aggregation. DuckDB v1.2-v1.4 added stream windowing, time_bucket(), and MERGE INTO, enabling SQL-expressed rolling retention rates, overdue-card trends, and daily-review heatmaps—all without leaving the embedded DB. This aligns with the existing DuckDB storage choice and avoids adding a new dependency. | corroborated |
| Enable DuckDB v1.4 AES-256 at-rest encryption for the flashcard database to protect review history and card content | Flashcore stores potentially sensitive learning data (medical, legal, language) in a local DuckDB file with no encryption. DuckDB v1.4 (LTS, Sept 2025) added native AES-256 encryption as a first-party extension, requiring only a connection-string key parameter—no schema changes or external tools. This directly addresses data-at-rest risk flagged by the AIV governance model. | single-source |
| Add an LLM-based card-generation pipeline (using genanki + Claude/OpenAI API) to auto-produce YAML drafts from user-supplied documents or notes | Flashcore's authoring path requires hand-written YAML. Multiple open-source projects (Anki-LLM 2025, anki-card-generator, anki-deck-generator built on Typer) demonstrate the pattern: send document chunks to an LLM, receive structured Q/A pairs, write them as YAML decks for ingest. Since flashcore already owns the YAML→DuckDB ingest path, an LLM front-end would extend authoring reach without touching core scheduling logic. | corroborated |
| Implement semantic deduplication of YAML card libraries using lightweight embedding similarity (e.g., SemHash with Model2Vec + Approximate Nearest Neighbor search) | The vet command currently detects exact UUID collisions but not near-duplicate cards with rephrased wording. SemHash processes millions of records on CPU in seconds and flags pairs exceeding a configurable cosine-similarity threshold. Adding a `flashcore vet --dedup` mode would surface semantic duplicates before ingest, improving deck quality without requiring a GPU or external service. | corroborated |
| Adopt a Yanki-compatible YAML/Markdown bidirectional authoring format to enable round-trip sync with Obsidian and Logseq spaced-repetition plugins | Flashcore's YAML schema is proprietary. The Yanki project (GitHub: Nielius/Yanki) and its companion Obsidian plugin demonstrate a plain-text YAML/Markdown format with Jinja templating that imports directly into Anki and syncs from Obsidian vaults. Aligning flashcore's YAML schema to Yanki conventions would let users author in Obsidian (1,500+ plugins, active FSRS plugin) and ingest into flashcore without conversion, extending the authoring surface to the dominant PKM ecosystem. | corroborated |
| Apply contextual-interference / interleaved deck ordering in the review queue to improve long-term retention based on established cognitive science consensus | Flashcore's initialize_session currently sorts by modified_at (a known bug) but the correct fix is not simply due-date ASC—research consistently shows that randomly interleaving cards across decks outperforms blocked same-deck sequences for delayed retention. Implementing a weighted interleave that mixes decks proportionally to their due-card count would be scientifically grounded and address the queue-ordering bug simultaneously. | corroborated |
| Add Hypothesis property-based testing (stateful RuleBasedStateMachine) to validate FSRS scheduling invariants across arbitrary review sequences | Flashcore's test suite has conflicting assertions about deck_switches across two test files (top findings #10). Property-based testing with Hypothesis automatically generates arbitrary review sequences and checks invariants (e.g., stability must increase after a correct review; difficulty must stay within [1,10]; deck_switches must equal the actual number of deck transitions). This would have caught the existing scheduling bugs mechanically and would prevent regressions in the fixed code. | corroborated |
| Migrate models from Pydantic v1 to Pydantic v2 (Rust-core pydantic-core) to reduce validation overhead in the hot ingest and review paths | Flashcore uses Pydantic models extensively (Card, Review, Session, YAMLCard, CardState, etc.) with extra='forbid' constraints. Pydantic v2's Rust core delivers 5-50x faster validation (benchmarked at ~17x for flat models), cleaner model_validate/model_dump API, and improved error messages that would surface the extra-key ValidationError (top finding #2) with better diagnostics. The bump-pydantic migration tool automates most of the conversion. | corroborated |
| Complement the AIV commit-packet governance with Sigstore + GitHub Actions Trusted Publishing (PEP 740) to add cryptographic provenance attestations to PyPI releases | Flashcore's AIV workflow governs commit-level provenance but PyPI releases currently have no attestation. PEP 740 (standardised in 2024, ~17% PyPI adoption by Mar 2026) allows GitHub Actions OIDC to automatically sign releases with Sigstore Cosign at zero workflow cost—meeting SLSA L3 build provenance. This directly extends the repo's existing governance ethos (AIV packet = commit provenance; Sigstore = release provenance) without changing the release.yml structure materially. | corroborated |
| Pin all GitHub Actions to full commit SHAs (replacing mutable version tags like actions/checkout@v6) to eliminate the supply-chain risk already identified in the top findings | Top finding #19 flags mutable action tags across main.yml, release.yml, and rename_project.yml. The GitHub security hardening guide and SLSA framework both require SHA-pinned actions for SLSA L2+. The fix is mechanical (one-line change per action), aligns with the AIV governance model, and closes the most immediately exploitable CI vector without adding dependencies. | corroborated |
| Expose a Markdown export path that produces Yanki-compatible or Obsidian-SR-compatible Markdown alongside the existing `export md` command, enabling round-trip import into Obsidian spaced-repetition plugins | Flashcore already has `export md` but its output format is undocumented relative to any interop standard. The Obsidian Spaced Repetition plugin (Stephen Mwangi, active through Apr 2026) and Yanki Obsidian plugin both consume specific Markdown card syntax. Aligning flashcore's Markdown export to one of these formats would make flashcore a drop-in card store for the large Obsidian user base without requiring users to maintain two separate tools. | corroborated |
| Upgrade py-fsrs dependency to FSRS-6 (v6.x): adopt the 21-parameter model (2 new params added in v6.0.0, May 2024) that explicitly handles same-day (short-term) reviews and improves forgetting-rate modelling for all cards. Requires migrating existing 19-parameter DEFAULT_PARAMETERS to 21 params (append 0.0 and 0.5) and updating the compute_next_state call site for the breaking API change where Card.get_retrievability() moved to Scheduler.get_card_retrievability(card). | Flashcore's FSRS implementation is the core scheduling engine. FSRS-6 measurably improves interval accuracy for cards reviewed more than once per day and corrects the stability-update formula used in retrievability; staying on FSRS-5 (19 params) means scheduling quality diverges from the current research baseline as the open-spaced-repetition project continues to iterate only on v6+. | corroborated |
| Integrate the FSRS Optimizer (fsrs-optimizer v6, or the lighter fsrs-rs-python v0.8.x which uses Rust/burn-rs instead of PyTorch, shrinking the dependency from ~2 GB to ~6 MB) to personalize the 21 scheduler parameters from a user's own review history. Add a `flashcore optimize` CLI command that reads the reviews table from DuckDB, exports the log format the optimizer expects, runs optimization, and writes the resulting parameters back as a user config override of DEFAULT_PARAMETERS. The optimizer requires ~1,000 reviews before improvements exceed noise. | Flashcore currently hard-codes DEFAULT_PARAMETERS for all users. Personal optimization is the primary practical advantage FSRS has over SM-2 in real-world deployments; without it, flashcore leaves its largest accuracy gain unused. The fsrs-rs-python path avoids pulling PyTorch into a CLI tool's dependency graph. | corroborated |
| Add a `flashcore generate` command that calls an LLM (via OpenRouter or the Anthropic API) to convert a plain-text document, PDF, or Markdown file into a draft YAML deck file conforming to flashcore's existing YAML schema. The output is a human-reviewable YAML file that can then be vetted and ingested through the normal pipeline, not auto-ingested. Several open-source reference implementations exist (LLM-Anki_FlashCard_Generator, anki_generator CLI, Median app). | Card authoring is currently manual YAML editing, the highest friction step for new users. LLM-assisted generation reduces authoring time to near zero for document-to-deck conversion while keeping the existing vet/ingest governance intact. The YAML-first output preserves the audit trail. | corroborated |
| Expose flashcore as an MCP (Model Context Protocol) server so AI coding assistants and agent workflows can query due cards, submit reviews, add decks, and read stats programmatically. The 'spacedrep' project (listed in awesome-fsrs) demonstrates the pattern: a CLI tool that doubles as an MCP server with .apkg import/export. Multiple AnkiConnect MCP servers (ankimcp/anki-mcp-server, spacholski1225/anki-connect-mcp) confirm MCP is the 2025 standard integration surface for flashcard tools and LLM agents. | Flashcore is currently only accessible via its Typer CLI. An MCP layer would let users drive reviews inside Claude Desktop or any MCP-capable agent, enable AI-assisted card generation pipelines that directly call ingest, and position the tool in the growing ecosystem of agent-accessible knowledge tools without requiring a GUI. | corroborated |
| Use DuckDB window functions (LAG/LEAD, moving averages, percentile_cont) already available in the embedded DuckDB instance to add a `flashcore analytics` command surfacing: (a) workload forecast — how many cards come due each day over the next 30 days, using a GROUP BY next_due_date query; (b) per-deck retention curves — rolling 7-day pass rate; (c) overdue card age distribution; (d) stability growth over successive reviews per card. These can be computed entirely in SQL against the existing reviews and cards tables with no new dependencies. | The existing `stats` command returns only aggregate counts. DuckDB's analytical SQL (already a dependency) can derive forgetting-curve and workload-forecast data that directly validates whether the FSRS scheduling parameters are working correctly — a prerequisite for informed parameter optimization and a key user-facing value-add. | corroborated |
| Adopt UTC-exclusive datetime handling throughout flashcore, matching the convention py-fsrs v6 enforces internally ('all datetime operations use UTC exclusively'). Specifically: replace the naive `datetime.now()` in db_utils.py:269 (backup filename timestamping) with `datetime.now(timezone.utc)`, and audit all other datetime construction sites for timezone-naive instances. This also unblocks using chronological filename sort for backup discovery (find_latest_backup) correctly across DST transitions. | The backup filename timezone bug (db_utils.py:269) is an identified defect in the top-findings list. py-fsrs v6 has already made this decision for the scheduling layer; aligning the rest of the codebase removes an entire class of subtle, hard-to-reproduce bugs when users are in non-UTC timezones or cross DST boundaries. | corroborated |
| Extend the YAML card schema with a `cloze:` field type that accepts a sentence with {{cloze}} markers and auto-expands into one Card per deletion at ingest time, matching Anki's native Cloze note type. The feature is well-understood (Anki's cloze type has existed for years; Wikipedia documents the cloze test format) and would allow YAML authors to write 'The capital of France is {{Paris}}' and get a front/back pair generated automatically. | Cloze deletions are the dominant card type in medical, language, and fact-heavy domains. Currently flashcore YAML only supports explicit front/back pairs. Adding cloze support in the YAMLProcessor's _validate_and_normalize_card would expand the authoring surface for the most common real-world Anki deck pattern without changing the storage model (each cloze still becomes a standard Card). | unverified |
| Implement SSP-MMC (Stochastic Shortest Path — Minimum Memory Cost) scheduling as an optional scheduler alternative to FSRS. SSP-MMC, developed by MaiMemo and documented in the paper 'Optimizing Spaced Repetition Schedule by Capturing the Dynamics of Memory', frames scheduling as a stochastic shortest-path problem to minimise total review workload while hitting a target retention. It is listed in the open-spaced-repetition awesome-fsrs resource list alongside FSRS as a production-grade alternative. | FSRS optimises interval length given a desired retention. SSP-MMC explicitly minimises expected future workload, which is a different objective that may suit users with large backlogs or strict time budgets. Offering it as a --scheduler flag on `review` would make flashcore the only Python CLI SRS with both scheduling philosophies available. | single-source |
| Add a `flashcore ingest --from-anki <file.apkg>` import path using genanki's sister library anki-export (or direct SQLite reads of the .apkg zip) to round-trip cards from existing Anki collections into flashcore's DuckDB store. Several Python libraries (anki-export on PyPI, anki-apkg-export on GitHub) provide .apkg parsing. This is the inverse of the existing `export anki` command and would let users migrate their Anki history into flashcore rather than starting from zero. | The existing pipeline only exports to Anki; there is no import path from Anki. Users with existing Anki collections have no migration route into flashcore, making adoption a cold-start problem. Bi-directional .apkg support completes the interoperability story implied by the existing export command. | corroborated |
| Replace the bare-string SQL f-string table interpolation pattern in flashcore/scripts/dump_history.py (line 45: `f'SELECT * FROM {table_name}'`) and flashcore/scripts/migrate.py (lines 247, 320) with DuckDB's identifier-quoting mechanism (`duckdb.identifier()` or double-quote escaping) to eliminate the latent SQL-injection surface. The callers currently restrict table names to a hard-coded tuple, but the function interfaces accept arbitrary strings, making future callers unsafe. DuckDB 0.9+ exposes parameterised identifier binding. | The top-findings list flags this as a security defect (SQL injection via table name interpolation). DuckDB's own documentation recommends parameterised queries for all user-supplied identifiers. Fixing this in the script layer is a prerequisite for any future feature that derives table names from user input (e.g., multi-schema exports or user-defined deck-namespace tables). | corroborated |
| Upgrade to FSRS-6 via py-fsrs v6.3.1 (21-parameter scheduler with revised same-day stability formula and Scheduler.get_card_retrievability API) | flashcore currently uses an older py-fsrs API with 19 parameters and a now-removed Card.get_retrievability() method. Upgrading to FSRS-6 (py-fsrs>=6.3.1) corrects the forgetting-curve decay, produces more accurate recall predictions, and fixes the retrievability call-site bug identified in the top findings (compute_next_state sets last_review=due_date, yielding R=1.0 for on-time reviews). | corroborated |
| Add a `flashcore optimize` command using fsrs-optimizer to derive personalized FSRS parameters from the user's DuckDB review log | fsrs-optimizer (v6.3.1, same org as py-fsrs) runs gradient descent over a user's review history to produce a personalized 21-float parameter vector and an optimal desired_retention value. This directly addresses the cold-start and one-size-fits-all problems in the current DEFAULT_PARAMETERS. Requires only a DuckDB export of the reviews table as input. | corroborated |
| Enable DuckDB full-text search (fts extension) for card content search | DuckDB's built-in FTS extension (Okapi BM25) can be enabled with INSTALL fts; LOAD fts; and a CREATE FTS INDEX on the cards table. This lets flashcore expose a `flashcore search <query>` command without any external search engine dependency, staying fully within the existing DuckDB storage layer. | corroborated |
| Add semantic card clustering via DuckDB VSS extension and sentence-transformers embeddings | DuckDB's vss extension provides an HNSW index for vector similarity search directly in the .duckdb file. Combined with sentence-transformers (all-MiniLM-L6-v2, 384-dim, ~50ms on CPU), flashcore could detect near-duplicate cards, group cards by topic, and produce prerequisite YAML configs — all without a separate vector database. No surveyed open-source SRS tool currently implements this as a CLI command. | single-source |
| Expose a flashcore-mcp Model Context Protocol server as a new spoke over the existing domain logic | Multiple independent Anki MCP servers (ankimcp, spacholski1225, nailuoGG, dhkim0124) validate the pattern: tools for create_card, search_cards, get_due_cards, record_review and resources for decks and stats. A flashcore-mcp server would let Claude or any MCP client author YAML cards via natural language and query DuckDB review history, fitting directly into the hub-and-spoke architecture as a new CLI-side spoke. | corroborated |
| Add LLM-based card generation (`flashcore generate --from <doc>`) producing native YAML output from PDFs or text files | Multiple open-source pipelines (anki-llm, RemNote flashcard generator, AutoAnki, LLM-Anki FlashCard Generator) validate PDF/text-to-flashcard via LLM. flashcore's YAML-first authoring format is an ideal target for structured LLM output. A litellm or direct Anthropic SDK call could produce YAML cards in flashcore's _RawYAMLCardEntry schema from any document, reducing authoring friction. | corroborated |
| Support multi-modal APKG export by passing card image/audio paths to genanki Package(media_files=[...]) | genanki's Package class accepts a media_files list that bundles any image or audio path into the .apkg ZIP alongside the SQLite collection. The YAML _RawYAMLCardEntry schema already has front/back string fields that can hold media references. Passing those paths through the export anki command produces fully valid multi-media Anki decks without changing the storage schema. | corroborated |
| Add anki-connect export mode for live sync to a running Anki instance (complement to existing genanki offline export) | anki-connect exposes a localhost HTTP API (port 8765) that supports addNote, createDeck, findNotes, and sync actions. This enables a `flashcore export anki --live` mode that syncs incrementally to Anki without generating a full .apkg — useful for users who keep Anki open alongside a terminal workflow. No additional dependencies beyond requests. | corroborated |
| Add a `--shuffle-topics` / interleaving flag to `flashcore review` to mix card topics within a session | The contextual interference effect (replicated across motor and verbal learning) shows interleaved practice produces stronger long-term retention than blocked practice, even though it feels harder and scores lower immediately. flashcore's current FSRS due-date sort already partially interleaves, but an explicit flag would let users opt into aggressive topic mixing, leveraging spacing and interleaving benefits simultaneously. | corroborated |
| Use Item Response Theory (IRT) via py-irt for cold-start difficulty estimation on new cards before any reviews | IRT estimates item difficulty and user ability as separate latent variables. For flashcore, this addresses the cold-start problem: a new card with zero reviews gets a meaningful initial difficulty prior from its estimated IRT parameters rather than defaulting to FSRS's D0 formula. IRT complements FSRS — IRT handles difficulty estimation at-a-point, FSRS handles time-decay scheduling. | corroborated |
| Target DuckDB v1.0+ stable on-disk file format and add Parquet export for analytics portability | DuckDB hit v1.0 (stable on-disk format guarantee) in June 2024 and is at v1.3.2 as of May 2025. Explicitly requiring >=1.0.0 in pyproject.toml gives users a forward-compatibility guarantee for their .duckdb files. Adding a `flashcore export parquet` command produces snapshots readable by Pandas, Polars, R, or any analytics tool without DuckDB installed. | corroborated |
| Implement MotherDuck ATTACH for optional cloud sync of the local DuckDB store | MotherDuck's hybrid sync model lets a local .duckdb file mirror to the cloud with a single ATTACH 'md:my_db'; statement. This would give flashcore users cross-device review continuity without a custom sync protocol, keeping the pure DuckDB storage layer unchanged. The feature is production-ready as of 2025. | corroborated |
| Benchmark flashcore's architecture and analytics against True Recall (closest open-source analog: FSRS-6 + local SQLite/DB + 25 analytics widgets + Anki export) | True Recall (Obsidian plugin, pieralukasz/true-recall) uses ts-fsrs (FSRS-6), stores all scheduling state in a local SQLite database, exposes 25+ analytics as inline codeblock widgets, and exports to Anki. It is the nearest architectural analog to flashcore. Benchmarking would identify analytics gaps (forgetting-curve charts, stability histograms, workload forecasts) that flashcore's `stats` command could add. | corroborated |
| Adopt CrowdAnki JSON deck format as a git-friendly alternative export alongside .apkg | CrowdAnki exports Anki decks as a folder with a human-readable deck.json and media files. The format can be committed to git and diffed line-by-line, making deck versioning and review auditable in a way .apkg (binary SQLite ZIP) cannot be. This aligns directly with flashcore's rigorous change-governance ethos (AIV commit workflow). The anki-dm Python tool reads these JSON files programmatically. | corroborated |
| Use the srs-benchmark repository and its anki-revlogs-10k / FSRS-Anki-20k Hugging Face datasets for algorithm validation | The open-spaced-repetition/srs-benchmark repo provides a TimeSeriesSplit sklearn pipeline that evaluates recall RMSE and log-loss across FSRS versions, HLR, Ebisu, and SM-2 on 1.7 billion real Anki reviews. Adding a `flashcore benchmark` command that runs the same evaluation on a user's own review log would let them verify that their personalized FSRS parameters actually improve recall predictions — making the optimize workflow falsifiable. | corroborated |


## Machine-checkable data

```json
{
  "candidates": [
    {
      "goal": "Provide a local-first, CLI-driven spaced-repetition flashcard ENGINE: author cards in YAML, vet/ingest them into a DuckDB-backed store, schedule reviews with FSRS parameters, conduct review sessions, and export to Anki/Markdown.",
      "status": "grounded",
      "signals": [
        {
          "signal": "Typer console app exposes the full lifecycle pipeline (vet, ingest, stats, review, review_all, export anki/md, restore)",
          "evidence": "flashcore/cli/main.py:99 (vet), :298 (ingest), :418 (stats), :455 (review), :503 (review_all), :544 (export_anki), :553 (export_md), :594 (restore); console_script flashcore = flashcore.__main__:main at pyproject.toml:47",
          "met": true
        },
        {
          "signal": "Scheduling is driven by FSRS via py-fsrs DEFAULT_PARAMETERS / DEFAULT_DESIRED_RETENTION",
          "evidence": "flashcore/scheduler.py:17-30 (imports fsrs Card/Rating/State/Scheduler), :92-94 (default_factory tuple(DEFAULT_PARAMETERS), desired_retention=DEFAULT_DESIRED_RETENTION)",
          "met": true
        },
        {
          "signal": "Self-described as a local-first SRS engine on FSRS + DuckDB",
          "evidence": "pyproject.toml:8 description = \"High-performance, local-first Spaced Repetition System engine using FSRS and DuckDB\"",
          "met": true
        },
        {
          "signal": "YAML authoring and Anki/Markdown export paths exist",
          "evidence": "flashcore/parser.py (load_and_process_flashcard_yamls), flashcore/cli/_export_logic.py:15 (export_to_markdown), flashcore/cli/main.py:544/:553 (export_anki/export_md)",
          "met": true
        },
        {
          "signal": "FSRS scheduling computes CORRECT review intervals (core engine promise)",
          "evidence": "scheduler.py:212 sets fsrs_card.last_review=fsrs_card.due then computes elapsed_days at :219-222, yielding 0 for on-time reviews and forcing R=1.0 instead of ~0.9 — produces incorrect new intervals (Stage-2 finding)",
          "met": false
        },
        {
          "signal": "Review queue is ordered by due-date priority (most-overdue first), as an SRS requires",
          "evidence": "database.py:459 fetches due cards ordered by next_due_date ASC then initialize_session re-sorts by c.modified_at, overriding due-date priority (Stage-2 finding)",
          "met": false
        }
      ],
      "judge_grounded_votes": "3/3"
    },
    {
      "goal": "Operate the repository as a rigorously governed, auditable engineering codebase where every change is gated by the AIV commit-packet protocol plus CI and tagged-release automation.",
      "status": "grounded",
      "signals": [
        {
          "signal": "AIV packet validation runs as a required PR gate",
          "evidence": ".github/workflows/aiv-guard.yml (name: AIV Packet Validation (Python); on pull_request to main; step 'Run AIV Guard' → python -m aiv.guard)",
          "met": true
        },
        {
          "signal": "CI enforces lint + pytest",
          "evidence": ".github/workflows/main.yml; Makefile lint target (flake8/black/mypy) and test target",
          "met": true
        },
        {
          "signal": "Tagged-release publishing pipeline exists",
          "evidence": ".github/workflows/release.yml (name: Upload Python Package; on push tags; contents: write)",
          "met": true
        },
        {
          "signal": "Mandatory aiv commit workflow is documented and binding",
          "evidence": "CLAUDE.md 'AIV Commit Workflow (mandatory for all commits)' with begin/commit/close/check flow and risk tiers",
          "met": true
        },
        {
          "signal": "Supply-chain hardening of the governance toolchain itself",
          "evidence": "aiv-guard.yml installs aiv-protocol from git HEAD with no SHA pin; actions pinned to mutable tags (@v6) (Stage-2 SEC findings)",
          "met": false
        }
      ],
      "judge_grounded_votes": "3/3"
    },
    {
      "goal": "Enable a one-time, validated MIGRATION of flashcard/review/session data from a legacy database into the new DuckDB store.",
      "status": "grounded",
      "signals": [
        {
          "signal": "Legacy-DB extraction to JSON utility exists",
          "evidence": "flashcore/scripts/dump_history.py (dump_table/dump_database over cards, reviews, sessions tables)",
          "met": true
        },
        {
          "signal": "Import + completeness-validation tooling into new DuckDB exists",
          "evidence": "flashcore/scripts/migrate.py:1-18 docstring (import then validate migration completeness; import/validate subcommands)",
          "met": true
        },
        {
          "signal": "Scripts are intentionally out-of-package one-off utilities",
          "evidence": "CLAUDE.md 'Scripts (flashcore/scripts/): utility scripts, NOT part of the installed package'; located under flashcore/scripts/ not exported",
          "met": true
        }
      ],
      "judge_grounded_votes": "3/3"
    },
    {
      "goal": "Serve as / retain heritage of a reusable Python project TEMPLATE with self-rename and bootstrap scaffolding (template-derived origin).",
      "status": "speculative",
      "signals": [
        {
          "signal": "Template rename/init scaffolding is present in-repo",
          "evidence": ".github/workflows/rename_project.yml; .github/init.sh; .github/rename_project.sh; .github/release_message.sh",
          "met": true
        },
        {
          "signal": "Rename automation is an ACTIVE goal vs vestigial template residue",
          "evidence": "rename_project.yml on: workflow_dispatch only, guarded by if !contains(github.repository,'/python-project-template'); no scheduled/push trigger — consistent with one-time/dormant template residue rather than an ongoing objective (Invariant 8: stated/structural negatives not ground truth — unconfirmed)",
          "met": false
        }
      ],
      "judge_grounded_votes": "0/3"
    }
  ],
  "research": [
    {
      "idea": "Upgrade to FSRS v6 via the latest py-fsrs release (21 configurable parameters; improved same-day-review and forgetting-rate modeling over FSRS v4.5)",
      "advances": "Flashcore uses FSRS-style parameters but the current implementation's elapsed_days calculation is already identified as broken (top finding #4). FSRS v6 is the consensus production standard (adopted by Anki Oct 2023, RemNote 2025) and reduces required reviews by ~20-30% vs. SM-2. Upgrading py-fsrs and aligning the elapsed_days fix to v6 semantics delivers both correctness and scheduling efficiency simultaneously.",
      "corroboration": "corroborated",
      "sources": [
        "https://github.com/open-spaced-repetition/py-fsrs",
        "https://pypi.org/project/fsrs/",
        "https://changes.ankiweb.net/changes/23.10.html",
        "https://www.remnote.com/feature/fsrs",
        "https://github.com/open-spaced-repetition/awesome-fsrs"
      ]
    },
    {
      "idea": "Integrate fsrs-optimizer (v6.5.0) to personalize FSRS parameters from a user's own review-history CSV exported from the DuckDB store",
      "advances": "Flashcore hardcodes DEFAULT_PARAMETERS. The fsrs-optimizer library processes review logs following a standardised schema (invocable as `python -m fsrs_optimizer revlog.csv`) and produces per-user optimal weights, directly improving scheduling accuracy without changing the core engine. The DuckDB reviews table already holds the data needed to produce this export.",
      "corroboration": "corroborated",
      "sources": [
        "https://github.com/open-spaced-repetition/fsrs-optimizer",
        "https://pypi.org/project/fsrs/",
        "https://github.com/open-spaced-repetition/awesome-fsrs"
      ]
    },
    {
      "idea": "Use DuckDB stream windowing functions (added in v1.2, May 2025) and time_bucket() for in-process retention-curve and scheduling-heatmap analytics",
      "advances": "Flashcore's stats command currently performs Python-level aggregation. DuckDB v1.2-v1.4 added stream windowing, time_bucket(), and MERGE INTO, enabling SQL-expressed rolling retention rates, overdue-card trends, and daily-review heatmaps—all without leaving the embedded DB. This aligns with the existing DuckDB storage choice and avoids adding a new dependency.",
      "corroboration": "corroborated",
      "sources": [
        "https://duckdb.org/2025/05/02/stream-windowing-functions",
        "https://medium.com/@varun.kulkarnni/introducing-duckdb-the-embedded-analytics-database-changing-data-science-e3123fcb9523",
        "https://duckdb.org/2024/10/04/duckdb-user-survey-analysis"
      ]
    },
    {
      "idea": "Enable DuckDB v1.4 AES-256 at-rest encryption for the flashcard database to protect review history and card content",
      "advances": "Flashcore stores potentially sensitive learning data (medical, legal, language) in a local DuckDB file with no encryption. DuckDB v1.4 (LTS, Sept 2025) added native AES-256 encryption as a first-party extension, requiring only a connection-string key parameter—no schema changes or external tools. This directly addresses data-at-rest risk flagged by the AIV governance model.",
      "corroboration": "single-source",
      "sources": [
        "https://medium.com/@2nick2patel2/duckdb-time-travel-tables-versioned-analytics-without-a-warehouse-upgrade-491dba34bc0e"
      ]
    },
    {
      "idea": "Add an LLM-based card-generation pipeline (using genanki + Claude/OpenAI API) to auto-produce YAML drafts from user-supplied documents or notes",
      "advances": "Flashcore's authoring path requires hand-written YAML. Multiple open-source projects (Anki-LLM 2025, anki-card-generator, anki-deck-generator built on Typer) demonstrate the pattern: send document chunks to an LLM, receive structured Q/A pairs, write them as YAML decks for ingest. Since flashcore already owns the YAML→DuckDB ingest path, an LLM front-end would extend authoring reach without touching core scheduling logic.",
      "corroboration": "corroborated",
      "sources": [
        "https://www.blog.brightcoding.dev/2025/12/12/anki-llm-revolutionize-your-flashcard-creation-with-ai-powered-cli-tools/",
        "https://github.com/kerrickstaley/genanki",
        "https://github.com/tryingtogetlogin/anki-card-generator",
        "https://github.com/eujuliu/anki-deck-generator"
      ]
    },
    {
      "idea": "Implement semantic deduplication of YAML card libraries using lightweight embedding similarity (e.g., SemHash with Model2Vec + Approximate Nearest Neighbor search)",
      "advances": "The vet command currently detects exact UUID collisions but not near-duplicate cards with rephrased wording. SemHash processes millions of records on CPU in seconds and flags pairs exceeding a configurable cosine-similarity threshold. Adding a `flashcore vet --dedup` mode would surface semantic duplicates before ingest, improving deck quality without requiring a GPU or external service.",
      "corroboration": "corroborated",
      "sources": [
        "https://medium.com/@sreeprad99/how-semhash-simplifies-semantic-deduplication-for-llm-data-a0b1a53e84fe",
        "https://docs.nvidia.com/nemo/curator/curate-text/process-data/deduplication/semdedup",
        "https://futuresearch.ai/semantic-deduplication/"
      ]
    },
    {
      "idea": "Adopt a Yanki-compatible YAML/Markdown bidirectional authoring format to enable round-trip sync with Obsidian and Logseq spaced-repetition plugins",
      "advances": "Flashcore's YAML schema is proprietary. The Yanki project (GitHub: Nielius/Yanki) and its companion Obsidian plugin demonstrate a plain-text YAML/Markdown format with Jinja templating that imports directly into Anki and syncs from Obsidian vaults. Aligning flashcore's YAML schema to Yanki conventions would let users author in Obsidian (1,500+ plugins, active FSRS plugin) and ingest into flashcore without conversion, extending the authoring surface to the dominant PKM ecosystem.",
      "corroboration": "corroborated",
      "sources": [
        "https://github.com/Nielius/Yanki",
        "https://github.com/kitschpatrol/yanki-obsidian",
        "https://www.obsidianstats.com/plugins/yanki",
        "https://stephenmwangi.com/obsidian-spaced-repetition/"
      ]
    },
    {
      "idea": "Apply contextual-interference / interleaved deck ordering in the review queue to improve long-term retention based on established cognitive science consensus",
      "advances": "Flashcore's initialize_session currently sorts by modified_at (a known bug) but the correct fix is not simply due-date ASC—research consistently shows that randomly interleaving cards across decks outperforms blocked same-deck sequences for delayed retention. Implementing a weighted interleave that mixes decks proportionally to their due-card count would be scientifically grounded and address the queue-ordering bug simultaneously.",
      "corroboration": "corroborated",
      "sources": [
        "https://en.wikipedia.org/wiki/Contextual_Interference",
        "https://en.wikipedia.org/wiki/Spacing_effect",
        "https://link.springer.com/article/10.1007/s10648-025-10035-1",
        "https://www.nature.com/articles/s41539-023-00159-w"
      ]
    },
    {
      "idea": "Add Hypothesis property-based testing (stateful RuleBasedStateMachine) to validate FSRS scheduling invariants across arbitrary review sequences",
      "advances": "Flashcore's test suite has conflicting assertions about deck_switches across two test files (top findings #10). Property-based testing with Hypothesis automatically generates arbitrary review sequences and checks invariants (e.g., stability must increase after a correct review; difficulty must stay within [1,10]; deck_switches must equal the actual number of deck transitions). This would have caught the existing scheduling bugs mechanically and would prevent regressions in the fixed code.",
      "corroboration": "corroborated",
      "sources": [
        "https://oneuptime.com/blog/post/2026-01-30-how-to-build-property-based-testing-with-hypothesis/view",
        "https://www.marktechpost.com/2026/04/18/a-coding-guide-for-property-based-testing-using-hypothesis-with-stateful-differential-and-metamorphic-test-design/",
        "https://pytest-with-eric.com/pytest-advanced/hypothesis-testing-python/"
      ]
    },
    {
      "idea": "Migrate models from Pydantic v1 to Pydantic v2 (Rust-core pydantic-core) to reduce validation overhead in the hot ingest and review paths",
      "advances": "Flashcore uses Pydantic models extensively (Card, Review, Session, YAMLCard, CardState, etc.) with extra='forbid' constraints. Pydantic v2's Rust core delivers 5-50x faster validation (benchmarked at ~17x for flat models), cleaner model_validate/model_dump API, and improved error messages that would surface the extra-key ValidationError (top finding #2) with better diagnostics. The bump-pydantic migration tool automates most of the conversion.",
      "corroboration": "corroborated",
      "sources": [
        "https://docs.pydantic.dev/latest/migration/",
        "https://thedataquarry.com/blog/why-pydantic-v2-matters/",
        "https://github.com/pydantic/bump-pydantic",
        "https://medium.com/codex/migrating-to-pydantic-v2-5a4b864621c3"
      ]
    },
    {
      "idea": "Complement the AIV commit-packet governance with Sigstore + GitHub Actions Trusted Publishing (PEP 740) to add cryptographic provenance attestations to PyPI releases",
      "advances": "Flashcore's AIV workflow governs commit-level provenance but PyPI releases currently have no attestation. PEP 740 (standardised in 2024, ~17% PyPI adoption by Mar 2026) allows GitHub Actions OIDC to automatically sign releases with Sigstore Cosign at zero workflow cost—meeting SLSA L3 build provenance. This directly extends the repo's existing governance ethos (AIV packet = commit provenance; Sigstore = release provenance) without changing the release.yml structure materially.",
      "corroboration": "corroborated",
      "sources": [
        "https://blog.trailofbits.com/2024/11/14/attestations-a-new-generation-of-signatures-on-pypi/",
        "https://securityboulevard.com/2024/11/attestations-a-new-generation-of-signatures-on-pypi/",
        "https://aquilax.ai/blog/supply-chain-artifact-signing-slsa",
        "https://edu.chainguard.dev/compliance/slsa/what-is-slsa/"
      ]
    },
    {
      "idea": "Pin all GitHub Actions to full commit SHAs (replacing mutable version tags like actions/checkout@v6) to eliminate the supply-chain risk already identified in the top findings",
      "advances": "Top finding #19 flags mutable action tags across main.yml, release.yml, and rename_project.yml. The GitHub security hardening guide and SLSA framework both require SHA-pinned actions for SLSA L2+. The fix is mechanical (one-line change per action), aligns with the AIV governance model, and closes the most immediately exploitable CI vector without adding dependencies.",
      "corroboration": "corroborated",
      "sources": [
        "https://aquilax.ai/blog/supply-chain-artifact-signing-slsa",
        "https://blog.intelligencex.org/secure-supply-chain-with-sigstore-cosign-slsa-framework",
        "https://edu.chainguard.dev/compliance/slsa/what-is-slsa/"
      ]
    },
    {
      "idea": "Expose a Markdown export path that produces Yanki-compatible or Obsidian-SR-compatible Markdown alongside the existing `export md` command, enabling round-trip import into Obsidian spaced-repetition plugins",
      "advances": "Flashcore already has `export md` but its output format is undocumented relative to any interop standard. The Obsidian Spaced Repetition plugin (Stephen Mwangi, active through Apr 2026) and Yanki Obsidian plugin both consume specific Markdown card syntax. Aligning flashcore's Markdown export to one of these formats would make flashcore a drop-in card store for the large Obsidian user base without requiring users to maintain two separate tools.",
      "corroboration": "corroborated",
      "sources": [
        "https://stephenmwangi.com/obsidian-spaced-repetition/",
        "https://system3.md/observatory/plugins/obsidian-spaced-repetition",
        "https://github.com/Nielius/Yanki",
        "https://publish.obsidian.md/hub/02+-+Community+Expansions/02.01+Plugins+by+Category/Spaced+Repetition+Plugins"
      ]
    },
    {
      "idea": "Upgrade py-fsrs dependency to FSRS-6 (v6.x): adopt the 21-parameter model (2 new params added in v6.0.0, May 2024) that explicitly handles same-day (short-term) reviews and improves forgetting-rate modelling for all cards. Requires migrating existing 19-parameter DEFAULT_PARAMETERS to 21 params (append 0.0 and 0.5) and updating the compute_next_state call site for the breaking API change where Card.get_retrievability() moved to Scheduler.get_card_retrievability(card).",
      "advances": "Flashcore's FSRS implementation is the core scheduling engine. FSRS-6 measurably improves interval accuracy for cards reviewed more than once per day and corrects the stability-update formula used in retrievability; staying on FSRS-5 (19 params) means scheduling quality diverges from the current research baseline as the open-spaced-repetition project continues to iterate only on v6+.",
      "corroboration": "corroborated",
      "sources": [
        "https://github.com/open-spaced-repetition/py-fsrs/releases",
        "https://pypi.org/project/fsrs/",
        "https://snyk.io/advisor/python/fsrs"
      ]
    },
    {
      "idea": "Integrate the FSRS Optimizer (fsrs-optimizer v6, or the lighter fsrs-rs-python v0.8.x which uses Rust/burn-rs instead of PyTorch, shrinking the dependency from ~2 GB to ~6 MB) to personalize the 21 scheduler parameters from a user's own review history. Add a `flashcore optimize` CLI command that reads the reviews table from DuckDB, exports the log format the optimizer expects, runs optimization, and writes the resulting parameters back as a user config override of DEFAULT_PARAMETERS. The optimizer requires ~1,000 reviews before improvements exceed noise.",
      "advances": "Flashcore currently hard-codes DEFAULT_PARAMETERS for all users. Personal optimization is the primary practical advantage FSRS has over SM-2 in real-world deployments; without it, flashcore leaves its largest accuracy gain unused. The fsrs-rs-python path avoids pulling PyTorch into a CLI tool's dependency graph.",
      "corroboration": "corroborated",
      "sources": [
        "https://github.com/open-spaced-repetition/fsrs-optimizer",
        "https://pypi.org/project/FSRS-Optimizer/5.0.6/",
        "https://github.com/open-spaced-repetition/fsrs-rs-python",
        "https://pypi.org/project/fsrs-rs-python/0.8.0/"
      ]
    },
    {
      "idea": "Add a `flashcore generate` command that calls an LLM (via OpenRouter or the Anthropic API) to convert a plain-text document, PDF, or Markdown file into a draft YAML deck file conforming to flashcore's existing YAML schema. The output is a human-reviewable YAML file that can then be vetted and ingested through the normal pipeline, not auto-ingested. Several open-source reference implementations exist (LLM-Anki_FlashCard_Generator, anki_generator CLI, Median app).",
      "advances": "Card authoring is currently manual YAML editing, the highest friction step for new users. LLM-assisted generation reduces authoring time to near zero for document-to-deck conversion while keeping the existing vet/ingest governance intact. The YAML-first output preserves the audit trail.",
      "corroboration": "corroborated",
      "sources": [
        "https://github.com/msgpo/LLM-Anki_FlashCard_Generator",
        "https://github.com/5uru/Median",
        "https://github.com/topics/flashcard-generator",
        "https://studycardsai.com/blog/ai-flashcard-generator-for-free"
      ]
    },
    {
      "idea": "Expose flashcore as an MCP (Model Context Protocol) server so AI coding assistants and agent workflows can query due cards, submit reviews, add decks, and read stats programmatically. The 'spacedrep' project (listed in awesome-fsrs) demonstrates the pattern: a CLI tool that doubles as an MCP server with .apkg import/export. Multiple AnkiConnect MCP servers (ankimcp/anki-mcp-server, spacholski1225/anki-connect-mcp) confirm MCP is the 2025 standard integration surface for flashcard tools and LLM agents.",
      "advances": "Flashcore is currently only accessible via its Typer CLI. An MCP layer would let users drive reviews inside Claude Desktop or any MCP-capable agent, enable AI-assisted card generation pipelines that directly call ingest, and position the tool in the growing ecosystem of agent-accessible knowledge tools without requiring a GUI.",
      "corroboration": "corroborated",
      "sources": [
        "https://github.com/open-spaced-repetition/awesome-fsrs",
        "https://github.com/ankimcp/anki-mcp-server",
        "https://mcpservers.org/servers/spacholski1225/anki-connect-mcp",
        "https://glama.ai/mcp/servers/samefarrar/mcp-ankiconnect"
      ]
    },
    {
      "idea": "Use DuckDB window functions (LAG/LEAD, moving averages, percentile_cont) already available in the embedded DuckDB instance to add a `flashcore analytics` command surfacing: (a) workload forecast — how many cards come due each day over the next 30 days, using a GROUP BY next_due_date query; (b) per-deck retention curves — rolling 7-day pass rate; (c) overdue card age distribution; (d) stability growth over successive reviews per card. These can be computed entirely in SQL against the existing reviews and cards tables with no new dependencies.",
      "advances": "The existing `stats` command returns only aggregate counts. DuckDB's analytical SQL (already a dependency) can derive forgetting-curve and workload-forecast data that directly validates whether the FSRS scheduling parameters are working correctly — a prerequisite for informed parameter optimization and a key user-facing value-add.",
      "corroboration": "corroborated",
      "sources": [
        "https://medium.com/@Quaxel/time-series-crunching-with-duckdb-without-losing-your-mind-fd129ba7173f",
        "https://motherduck.com/glossary/time-series/",
        "https://medium.com/@hadiyolworld007/window-functions-101-analytics-tricks-in-duckdb-sql-6637294fae54",
        "https://www.marktechpost.com/2026/04/13/an-implementation-guide-to-building-a-duckdb-python-analytics-pipeline-with-sql-dataframes-parquet-udfs-and-performance-profiling/"
      ]
    },
    {
      "idea": "Adopt UTC-exclusive datetime handling throughout flashcore, matching the convention py-fsrs v6 enforces internally ('all datetime operations use UTC exclusively'). Specifically: replace the naive `datetime.now()` in db_utils.py:269 (backup filename timestamping) with `datetime.now(timezone.utc)`, and audit all other datetime construction sites for timezone-naive instances. This also unblocks using chronological filename sort for backup discovery (find_latest_backup) correctly across DST transitions.",
      "advances": "The backup filename timezone bug (db_utils.py:269) is an identified defect in the top-findings list. py-fsrs v6 has already made this decision for the scheduling layer; aligning the rest of the codebase removes an entire class of subtle, hard-to-reproduce bugs when users are in non-UTC timezones or cross DST boundaries.",
      "corroboration": "corroborated",
      "sources": [
        "https://github.com/open-spaced-repetition/py-fsrs/releases",
        "https://pypi.org/project/fsrs/",
        "https://snyk.io/advisor/python/fsrs"
      ]
    },
    {
      "idea": "Extend the YAML card schema with a `cloze:` field type that accepts a sentence with {{cloze}} markers and auto-expands into one Card per deletion at ingest time, matching Anki's native Cloze note type. The feature is well-understood (Anki's cloze type has existed for years; Wikipedia documents the cloze test format) and would allow YAML authors to write 'The capital of France is {{Paris}}' and get a front/back pair generated automatically.",
      "advances": "Cloze deletions are the dominant card type in medical, language, and fact-heavy domains. Currently flashcore YAML only supports explicit front/back pairs. Adding cloze support in the YAMLProcessor's _validate_and_normalize_card would expand the authoring surface for the most common real-world Anki deck pattern without changing the storage model (each cloze still becomes a standard Card).",
      "corroboration": "unverified",
      "sources": [
        "https://en.wikipedia.org/wiki/Cloze_test",
        "https://en.wikipedia.org/wiki/Anki_(software)"
      ]
    },
    {
      "idea": "Implement SSP-MMC (Stochastic Shortest Path — Minimum Memory Cost) scheduling as an optional scheduler alternative to FSRS. SSP-MMC, developed by MaiMemo and documented in the paper 'Optimizing Spaced Repetition Schedule by Capturing the Dynamics of Memory', frames scheduling as a stochastic shortest-path problem to minimise total review workload while hitting a target retention. It is listed in the open-spaced-repetition awesome-fsrs resource list alongside FSRS as a production-grade alternative.",
      "advances": "FSRS optimises interval length given a desired retention. SSP-MMC explicitly minimises expected future workload, which is a different objective that may suit users with large backlogs or strict time budgets. Offering it as a --scheduler flag on `review` would make flashcore the only Python CLI SRS with both scheduling philosophies available.",
      "corroboration": "single-source",
      "sources": [
        "https://github.com/open-spaced-repetition/awesome-fsrs"
      ]
    },
    {
      "idea": "Add a `flashcore ingest --from-anki <file.apkg>` import path using genanki's sister library anki-export (or direct SQLite reads of the .apkg zip) to round-trip cards from existing Anki collections into flashcore's DuckDB store. Several Python libraries (anki-export on PyPI, anki-apkg-export on GitHub) provide .apkg parsing. This is the inverse of the existing `export anki` command and would let users migrate their Anki history into flashcore rather than starting from zero.",
      "advances": "The existing pipeline only exports to Anki; there is no import path from Anki. Users with existing Anki collections have no migration route into flashcore, making adoption a cold-start problem. Bi-directional .apkg support completes the interoperability story implied by the existing export command.",
      "corroboration": "corroborated",
      "sources": [
        "https://github.com/kerrickstaley/genanki",
        "https://pypi.org/project/anki-export/",
        "https://github.com/repeat-space/anki-apkg-export",
        "https://audrey.feldroy.com/articles/2025-01-19-Genanki-and-fastcore"
      ]
    },
    {
      "idea": "Replace the bare-string SQL f-string table interpolation pattern in flashcore/scripts/dump_history.py (line 45: `f'SELECT * FROM {table_name}'`) and flashcore/scripts/migrate.py (lines 247, 320) with DuckDB's identifier-quoting mechanism (`duckdb.identifier()` or double-quote escaping) to eliminate the latent SQL-injection surface. The callers currently restrict table names to a hard-coded tuple, but the function interfaces accept arbitrary strings, making future callers unsafe. DuckDB 0.9+ exposes parameterised identifier binding.",
      "advances": "The top-findings list flags this as a security defect (SQL injection via table name interpolation). DuckDB's own documentation recommends parameterised queries for all user-supplied identifiers. Fixing this in the script layer is a prerequisite for any future feature that derives table names from user input (e.g., multi-schema exports or user-defined deck-namespace tables).",
      "corroboration": "corroborated",
      "sources": [
        "https://medium.com/@ThinkingLoop/duckdb-the-quiet-powerhouse-of-2025-analytics-b85a86655364",
        "https://deepnote.com/blog/ultimate-guide-to-duckdb-library-in-python"
      ]
    },
    {
      "idea": "Upgrade to FSRS-6 via py-fsrs v6.3.1 (21-parameter scheduler with revised same-day stability formula and Scheduler.get_card_retrievability API)",
      "advances": "flashcore currently uses an older py-fsrs API with 19 parameters and a now-removed Card.get_retrievability() method. Upgrading to FSRS-6 (py-fsrs>=6.3.1) corrects the forgetting-curve decay, produces more accurate recall predictions, and fixes the retrievability call-site bug identified in the top findings (compute_next_state sets last_review=due_date, yielding R=1.0 for on-time reviews).",
      "corroboration": "corroborated",
      "sources": [
        "https://github.com/open-spaced-repetition/py-fsrs/releases",
        "https://pypi.org/project/fsrs/",
        "https://github.com/open-spaced-repetition/awesome-fsrs/wiki/The-Algorithm",
        "https://domenic.me/fsrs/"
      ]
    },
    {
      "idea": "Add a `flashcore optimize` command using fsrs-optimizer to derive personalized FSRS parameters from the user's DuckDB review log",
      "advances": "fsrs-optimizer (v6.3.1, same org as py-fsrs) runs gradient descent over a user's review history to produce a personalized 21-float parameter vector and an optimal desired_retention value. This directly addresses the cold-start and one-size-fits-all problems in the current DEFAULT_PARAMETERS. Requires only a DuckDB export of the reviews table as input.",
      "corroboration": "corroborated",
      "sources": [
        "https://pypi.org/project/FSRS-Optimizer/",
        "https://github.com/open-spaced-repetition/fsrs-optimizer",
        "https://deepwiki.com/open-spaced-repetition/py-fsrs/5-the-fsrs-algorithm"
      ]
    },
    {
      "idea": "Enable DuckDB full-text search (fts extension) for card content search",
      "advances": "DuckDB's built-in FTS extension (Okapi BM25) can be enabled with INSTALL fts; LOAD fts; and a CREATE FTS INDEX on the cards table. This lets flashcore expose a `flashcore search <query>` command without any external search engine dependency, staying fully within the existing DuckDB storage layer.",
      "corroboration": "corroborated",
      "sources": [
        "https://duckdb.org/docs/current/core_extensions/full_text_search",
        "https://duckdb.org/2025/06/13/text-analytics",
        "https://motherduck.com/blog/search-using-duckdb-part-3/"
      ]
    },
    {
      "idea": "Add semantic card clustering via DuckDB VSS extension and sentence-transformers embeddings",
      "advances": "DuckDB's vss extension provides an HNSW index for vector similarity search directly in the .duckdb file. Combined with sentence-transformers (all-MiniLM-L6-v2, 384-dim, ~50ms on CPU), flashcore could detect near-duplicate cards, group cards by topic, and produce prerequisite YAML configs — all without a separate vector database. No surveyed open-source SRS tool currently implements this as a CLI command.",
      "corroboration": "single-source",
      "sources": [
        "https://sbert.net/examples/sentence_transformer/applications/clustering/README.html",
        "https://duckdb.org/docs/current/core_extensions/full_text_search",
        "https://duckdb.org/2025/06/13/text-analytics"
      ]
    },
    {
      "idea": "Expose a flashcore-mcp Model Context Protocol server as a new spoke over the existing domain logic",
      "advances": "Multiple independent Anki MCP servers (ankimcp, spacholski1225, nailuoGG, dhkim0124) validate the pattern: tools for create_card, search_cards, get_due_cards, record_review and resources for decks and stats. A flashcore-mcp server would let Claude or any MCP client author YAML cards via natural language and query DuckDB review history, fitting directly into the hub-and-spoke architecture as a new CLI-side spoke.",
      "corroboration": "corroborated",
      "sources": [
        "https://github.com/ankimcp/anki-mcp-server",
        "https://github.com/spacholski1225/anki-connect-mcp",
        "https://github.com/nailuoGG/anki-mcp-server",
        "https://modelcontextprotocol.io/",
        "https://mcpservers.org/servers/spacholski1225/anki-connect-mcp"
      ]
    },
    {
      "idea": "Add LLM-based card generation (`flashcore generate --from <doc>`) producing native YAML output from PDFs or text files",
      "advances": "Multiple open-source pipelines (anki-llm, RemNote flashcard generator, AutoAnki, LLM-Anki FlashCard Generator) validate PDF/text-to-flashcard via LLM. flashcore's YAML-first authoring format is an ideal target for structured LLM output. A litellm or direct Anthropic SDK call could produce YAML cards in flashcore's _RawYAMLCardEntry schema from any document, reducing authoring friction.",
      "corroboration": "corroborated",
      "sources": [
        "https://github.com/raine/anki-llm",
        "https://github.com/GrannyProgramming/remnote-flashcard-generator",
        "https://github.com/msgpo/LLM-Anki_FlashCard_Generator",
        "https://github.com/jqhoogland/autoanki",
        "https://www.lesswrong.com/posts/hGhBhLsgNWLCJ3g9b/creating-flashcards-with-llms"
      ]
    },
    {
      "idea": "Support multi-modal APKG export by passing card image/audio paths to genanki Package(media_files=[...])",
      "advances": "genanki's Package class accepts a media_files list that bundles any image or audio path into the .apkg ZIP alongside the SQLite collection. The YAML _RawYAMLCardEntry schema already has front/back string fields that can hold media references. Passing those paths through the export anki command produces fully valid multi-media Anki decks without changing the storage schema.",
      "corroboration": "corroborated",
      "sources": [
        "https://github.com/kerrickstaley/genanki",
        "https://deepwiki.com/kerrickstaley/genanki",
        "https://pypi.org/project/md2anki/"
      ]
    },
    {
      "idea": "Add anki-connect export mode for live sync to a running Anki instance (complement to existing genanki offline export)",
      "advances": "anki-connect exposes a localhost HTTP API (port 8765) that supports addNote, createDeck, findNotes, and sync actions. This enables a `flashcore export anki --live` mode that syncs incrementally to Anki without generating a full .apkg — useful for users who keep Anki open alongside a terminal workflow. No additional dependencies beyond requests.",
      "corroboration": "corroborated",
      "sources": [
        "https://github.com/GitCrush/Anki-Connect-Tools",
        "https://pypi.org/project/AnkiIn/",
        "https://github.com/Stvad/CrowdAnki"
      ]
    },
    {
      "idea": "Add a `--shuffle-topics` / interleaving flag to `flashcore review` to mix card topics within a session",
      "advances": "The contextual interference effect (replicated across motor and verbal learning) shows interleaved practice produces stronger long-term retention than blocked practice, even though it feels harder and scores lower immediately. flashcore's current FSRS due-date sort already partially interleaves, but an explicit flag would let users opt into aggressive topic mixing, leveraging spacing and interleaving benefits simultaneously.",
      "corroboration": "corroborated",
      "sources": [
        "https://en.wikipedia.org/wiki/Varied_practice",
        "https://en.wikipedia.org/wiki/Spacing_effect",
        "https://en.wikipedia.org/wiki/Desirable_difficulty"
      ]
    },
    {
      "idea": "Use Item Response Theory (IRT) via py-irt for cold-start difficulty estimation on new cards before any reviews",
      "advances": "IRT estimates item difficulty and user ability as separate latent variables. For flashcore, this addresses the cold-start problem: a new card with zero reviews gets a meaningful initial difficulty prior from its estimated IRT parameters rather than defaulting to FSRS's D0 formula. IRT complements FSRS — IRT handles difficulty estimation at-a-point, FSRS handles time-decay scheduling.",
      "corroboration": "corroborated",
      "sources": [
        "https://en.wikipedia.org/wiki/Item_response_theory",
        "https://arxiv.org/pdf/2105.15106",
        "https://github.com/open-spaced-repetition/srs-benchmark"
      ]
    },
    {
      "idea": "Target DuckDB v1.0+ stable on-disk file format and add Parquet export for analytics portability",
      "advances": "DuckDB hit v1.0 (stable on-disk format guarantee) in June 2024 and is at v1.3.2 as of May 2025. Explicitly requiring >=1.0.0 in pyproject.toml gives users a forward-compatibility guarantee for their .duckdb files. Adding a `flashcore export parquet` command produces snapshots readable by Pandas, Polars, R, or any analytics tool without DuckDB installed.",
      "corroboration": "corroborated",
      "sources": [
        "https://duckdb.org/2024/06/10/delta",
        "https://motherduck.com/blog/duckdb-ecosystem-newsletter-february-2025/"
      ]
    },
    {
      "idea": "Implement MotherDuck ATTACH for optional cloud sync of the local DuckDB store",
      "advances": "MotherDuck's hybrid sync model lets a local .duckdb file mirror to the cloud with a single ATTACH 'md:my_db'; statement. This would give flashcore users cross-device review continuity without a custom sync protocol, keeping the pure DuckDB storage layer unchanged. The feature is production-ready as of 2025.",
      "corroboration": "corroborated",
      "sources": [
        "https://motherduck.com/docs/concepts/architecture-and-capabilities/",
        "https://motherduck.com/docs/sql-reference/motherduck-sql-reference/attach/"
      ]
    },
    {
      "idea": "Benchmark flashcore's architecture and analytics against True Recall (closest open-source analog: FSRS-6 + local SQLite/DB + 25 analytics widgets + Anki export)",
      "advances": "True Recall (Obsidian plugin, pieralukasz/true-recall) uses ts-fsrs (FSRS-6), stores all scheduling state in a local SQLite database, exposes 25+ analytics as inline codeblock widgets, and exports to Anki. It is the nearest architectural analog to flashcore. Benchmarking would identify analytics gaps (forgetting-curve charts, stability histograms, workload forecasts) that flashcore's `stats` command could add.",
      "corroboration": "corroborated",
      "sources": [
        "https://forum.obsidian.md/t/fully-native-srs-in-obsidian-true-recall/112879",
        "https://github.com/pieralukasz/true-recall",
        "https://github.com/open-spaced-repetition/awesome-fsrs"
      ]
    },
    {
      "idea": "Adopt CrowdAnki JSON deck format as a git-friendly alternative export alongside .apkg",
      "advances": "CrowdAnki exports Anki decks as a folder with a human-readable deck.json and media files. The format can be committed to git and diffed line-by-line, making deck versioning and review auditable in a way .apkg (binary SQLite ZIP) cannot be. This aligns directly with flashcore's rigorous change-governance ethos (AIV commit workflow). The anki-dm Python tool reads these JSON files programmatically.",
      "corroboration": "corroborated",
      "sources": [
        "https://github.com/Stvad/CrowdAnki",
        "https://pypi.org/project/AnkiIn/"
      ]
    },
    {
      "idea": "Use the srs-benchmark repository and its anki-revlogs-10k / FSRS-Anki-20k Hugging Face datasets for algorithm validation",
      "advances": "The open-spaced-repetition/srs-benchmark repo provides a TimeSeriesSplit sklearn pipeline that evaluates recall RMSE and log-loss across FSRS versions, HLR, Ebisu, and SM-2 on 1.7 billion real Anki reviews. Adding a `flashcore benchmark` command that runs the same evaluation on a user's own review log would let them verify that their personalized FSRS parameters actually improve recall predictions — making the optimize workflow falsifiable.",
      "corroboration": "corroborated",
      "sources": [
        "https://github.com/open-spaced-repetition/srs-benchmark",
        "https://github.com/open-spaced-repetition/fsrs-optimizer"
      ]
    }
  ],
  "research_blocked": false
}
```
