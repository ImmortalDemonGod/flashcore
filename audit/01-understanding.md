# 01 — Understanding

_Generated 2026-06-17 19:14:17 · branch `claude/nifty-brahmagupta-0tq0vy` · forensic-audit-pipeline (consolidated)_

**Coverage denominator:** 118 files (every one classified — see appendix).

## Architecture

flashcore is a Python flashcard/spaced-repetition system built on a deliberate Hub-and-Spoke layout (per CLAUDE.md): the spoke `flashcore/` holds pure domain logic (Card, Review, Session, CardState, Rating, FSRS DEFAULT_PARAMETERS/DEFAULT_DESIRED_RETENTION, FlashcardDatabase over DuckDB, and a YAMLProcessor for authoring), while the hub `flashcore/cli/` injects all paths at runtime and exposes a Typer console app (`flashcore` console_script and `python -m flashcore`) with commands vet, ingest, stats, review, review_all, export anki, export md, and restore. Non-installed utility scripts under `flashcore/scripts/` (dump_history.py, migrate.py) handle legacy-DB extraction to JSON and import/validation into the new DuckDB store. The repo is template-derived, evidenced by .github automation: CI (main.yml lint+pytest), tagged-release publishing (release.yml + release_message.sh), an AIV commit-integrity gate (aiv-guard.yml), and template rename/init tooling (rename_project.yml, init.sh, rename_project.sh), with a Makefile orchestrating install/fmt/lint/test/docs/release. The 118-file inventory skews toward docs (37) and config (23) over source (27) and tests (24), consistent with a packaged, heavily-governed library plus its task/governance scaffolding. PROVISIONAL: file-level role counts and entry-point descriptions are taken from the supplied Stage-1 inventory and not independently re-read here.

## Provisional intent

PROVISIONAL: The apparent goal is to provide a packaged, CLI-driven spaced-repetition flashcard engine — authoring cards from YAML, ingesting/vetting them into a DuckDB-backed store, scheduling reviews via FSRS-style parameters, and exporting to Anki/Markdown — while migrating data from a legacy database. A strong secondary intent is rigorous change governance: the AIV commit-packet workflow, CI/release automation, and template-based project scaffolding suggest the repo doubles as a disciplined, auditable engineering template. This intent is inferred from entry points, exported API symbols, and CLAUDE.md conventions and should be verified against primary source before being treated as fact.

## Role distribution

| Role | Count |
| --- | --- |
| config | 22 |
| doc | 37 |
| asset | 3 |
| source | 30 |
| dead | 2 |
| test | 24 |

## Entry points (13)

| Entry | What |
| --- | --- |
| .github/workflows/main.yml | GitHub Actions CI entry point: triggers on push/PR, runs lint then pytest suite |
| .github/workflows/release.yml | GitHub Actions release entry point: triggers on version tag push, builds and publishes release |
| .github/workflows/aiv-guard.yml | GitHub Actions gate: blocks PRs that lack a valid AIV commit-integrity packet |
| .github/workflows/rename_project.yml | GitHub Actions workflow_dispatch entry point: executes rename_project.sh to rebrand from template |
| .github/init.sh | Shell script entry point: initialises repo from template (run manually or via make init) |
| .github/release_message.sh | Shell script entry point: generates release changelog from git shortlog (called by release workflow) |
| .github/rename_project.sh | Shell script entry point: renames project slug/author across files (called by rename_project.yml) |
| Makefile | Make entry point: exposes targets help, install, fmt, lint, test, watch, clean, virtualenv, release, docs, init |
| flashcore/__main__.py | python -m flashcore entry point; calls flashcore.cli.main:main() |
| flashcore/cli/main.py:main | console_scripts entry point 'flashcore' declared in pyproject.toml [project.scripts]; runs the Typer app with commands: vet, ingest, stats, review, review_all, export anki, export md, restore |
| flashcore/__init__.py | Installed Python package public API; importable as `import flashcore`; exports Card, Review, Session, CardState, Rating, DEFAULT_PARAMETERS, DEFAULT_DESIRED_RETENTION, FlashcardDatabase, YAMLProcessor, YAMLProcessorConfig |
| flashcore/scripts/dump_history.py:main | Standalone CLI script (not installed); invoked directly with python flashcore/scripts/dump_history.py --db OLD --out-dir DIR; exports legacy DB tables to JSON |
| flashcore/scripts/migrate.py:main | Standalone CLI script (not installed); invoked directly with python flashcore/scripts/migrate.py import\|validate ...; imports JSON exports into new DuckDB or validates migration |


## Machine-checkable data

```json
{
  "denominator": 118,
  "roleCounts": {
    "config": 22,
    "doc": 37,
    "asset": 3,
    "source": 30,
    "dead": 2,
    "test": 24
  },
  "entry_points": [
    {
      "entry": ".github/workflows/main.yml",
      "what": "GitHub Actions CI entry point: triggers on push/PR, runs lint then pytest suite"
    },
    {
      "entry": ".github/workflows/release.yml",
      "what": "GitHub Actions release entry point: triggers on version tag push, builds and publishes release"
    },
    {
      "entry": ".github/workflows/aiv-guard.yml",
      "what": "GitHub Actions gate: blocks PRs that lack a valid AIV commit-integrity packet"
    },
    {
      "entry": ".github/workflows/rename_project.yml",
      "what": "GitHub Actions workflow_dispatch entry point: executes rename_project.sh to rebrand from template"
    },
    {
      "entry": ".github/init.sh",
      "what": "Shell script entry point: initialises repo from template (run manually or via make init)"
    },
    {
      "entry": ".github/release_message.sh",
      "what": "Shell script entry point: generates release changelog from git shortlog (called by release workflow)"
    },
    {
      "entry": ".github/rename_project.sh",
      "what": "Shell script entry point: renames project slug/author across files (called by rename_project.yml)"
    },
    {
      "entry": "Makefile",
      "what": "Make entry point: exposes targets help, install, fmt, lint, test, watch, clean, virtualenv, release, docs, init"
    },
    {
      "entry": "flashcore/__main__.py",
      "what": "python -m flashcore entry point; calls flashcore.cli.main:main()"
    },
    {
      "entry": "flashcore/cli/main.py:main",
      "what": "console_scripts entry point 'flashcore' declared in pyproject.toml [project.scripts]; runs the Typer app with commands: vet, ingest, stats, review, review_all, export anki, export md, restore"
    },
    {
      "entry": "flashcore/__init__.py",
      "what": "Installed Python package public API; importable as `import flashcore`; exports Card, Review, Session, CardState, Rating, DEFAULT_PARAMETERS, DEFAULT_DESIRED_RETENTION, FlashcardDatabase, YAMLProcessor, YAMLProcessorConfig"
    },
    {
      "entry": "flashcore/scripts/dump_history.py:main",
      "what": "Standalone CLI script (not installed); invoked directly with python flashcore/scripts/dump_history.py --db OLD --out-dir DIR; exports legacy DB tables to JSON"
    },
    {
      "entry": "flashcore/scripts/migrate.py:main",
      "what": "Standalone CLI script (not installed); invoked directly with python flashcore/scripts/migrate.py import|validate ...; imports JSON exports into new DuckDB or validates migration"
    }
  ]
}
```
