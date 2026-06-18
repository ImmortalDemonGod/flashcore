# Forensic Audit — Pause / Resume

This audit is produced by `audit/forensic_pipeline.mjs`, a long-running, multi-stage
driver. It is designed to survive a paused or reclaimed container **without losing
completed work**. This file documents how that durability works and how to resume.

## What is durable (committed + pushed to this branch)

| Path | Role |
|---|---|
| `audit/forensic_pipeline.mjs` | the orchestrator (reproducible driver) |
| `audit/0N-*.md` | the five human-readable stage artifacts |
| `audit/.work/state.json` | which stages are complete (the resume index) |
| `audit/.work/stageN.json` | each completed stage's structured output (reloaded on resume) |

## What is intentionally NOT durable (local scratch, regenerated each run)

`audit/.work/run.log`, `audit/.work/pipeline.stdout.log`, the per-agent handoff files
(`audit/.work/a_*.json`) and prompt spills. These are high-churn and carry no state the
pipeline needs to resume — they are gitignored so they never dirty the tree.

## How resume works

`main()` computes, per stage, `run = !state.completed["stageN"]`. On startup it reads
`audit/.work/state.json`; any stage already marked complete is **skipped** and its
`stageN.json` is **reloaded** from disk to feed the later stages. So a fresh container
that has cloned this branch already has everything it needs.

Resume granularity is **per stage**: completed stages are never re-run. The
*in-progress* stage re-runs — except Stage 2, which additionally resumes mid-stage by
reloading the partial findings from a committed `stage2.json`.

## Commands

```bash
cd <repo-root>

# Verify the agent path works in the new container FIRST (one cheap call):
node audit/forensic_pipeline.mjs --preflight

# Resume: with no flags it auto-continues from the first incomplete stage.
node audit/forensic_pipeline.mjs

# Force re-run from a specific stage (reuses earlier artifacts):
node audit/forensic_pipeline.mjs --from 3

# Run exactly one stage:
node audit/forensic_pipeline.mjs --stage 2

# Tear everything down and start clean (DELETES audit/, including this file):
node audit/forensic_pipeline.mjs --fresh
```

## Preconditions in a new container

- The `claude` CLI must be installed and authenticated — `--preflight` proves it.
- Stage 3 installs the project's own dependencies itself (discovered from the repo);
  no manual setup is required.
- The branch is derived at runtime from `git rev-parse --abbrev-ref HEAD`; nothing is
  hardcoded, so resuming on the same branch "just works".
