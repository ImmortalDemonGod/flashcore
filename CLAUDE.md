# CLAUDE.md — Project Instructions for Claude Code

This file is loaded automatically at the start of every Claude Code session.
Keep it current. Do not pad it with information already derivable from the code.

---

## Branch Discipline

- **Never commit directly to `main`.** All work goes on a feature branch.
  Branch naming convention: `feat/task-<N>-<slug>` (e.g., `feat/task-8-9-data-safety-finalize`).
- Check the current branch before doing any `git` work: `git branch --show-current`.

---

## AIV Commit Workflow (mandatory for all commits)

Every commit on this project must go through `aiv commit`, not plain `git commit`.

### Full flow

```bash
# 1. Check for stale active change context
aiv status

# 2. Abandon stale context if needed (pipe confirmation)
echo "y" | aiv abandon

# 3. Open a new change for this branch
aiv begin <change-id> --mode pr --description "<one-liner>"

# 4. Stage files, then commit each logical unit
git add <files>
aiv commit <primary-file> \
  -m "<conventional commit message>" \
  -t R1 \
  -c "<falsifiable claim>" \
  -c "<falsifiable claim>" \
  -i "<SHA-pinned GitHub URL to task spec>" \
  --requirement "<which specific requirement is satisfied>" \
  -r "<why this risk tier>" \
  -s "<one-line summary>"

# 5. Repeat step 4 for each logical commit

# 6. Close the change — generates the Layer 2 packet
aiv close

# 7. Validate the packet locally before pushing
aiv check .github/aiv-packets/PACKET_<change-id>.md

# 8. Fix any blocking errors, then commit the corrected packet
git add .github/aiv-packets/PACKET_<change-id>.md
git commit -m "docs(aiv): fix packet — <what was corrected>"

# 9. Push and open PR with the packet as the PR body
git push -u origin <branch>
gh pr create --title "..." --body "$(cat .github/aiv-packets/PACKET_<change-id>.md)"
```

### Risk tiers

| Tier | Meaning | `--skip-checks` allowed? |
|------|---------|--------------------------|
| R0   | Trivial (no logic changes) | Yes — must provide `--skip-reason` |
| R1   | Standard feature or refactor | No |
| R2   | High risk (security, data migration) | No |
| R3   | Critical | No |

---

## Known AIV Gotchas

### `aiv commit` FILE argument
- The FILE must **exist on disk** and have **changes relative to HEAD**.
- For deletion-only commits, anchor on a tracking file you update alongside
  the deletion (e.g., mark subtasks done in `.taskmaster/tasks/task_NNN.md`).
- Deleted files (`git rm`) cannot be used as the FILE argument.

### E010 — false-positive bug-fix detection
`aiv check` raises a blocking E010 error when:
1. Any claim description or intent text matches the word-boundary regex:
   `fix(ed|es|ing)?`, `bug(s|fix)?`, `issue #N`, `patch(ed|es)?`,
   `resolve[ds]?`, `closes #N`, `hotfix`
2. AND no claim has `evidence_class == PROVENANCE` (Class F).

**The trap:** Even innocent phrasing like "description **fixed**" or
"**fix** imports" triggers this.

**The fix:** Rephrase the claim to avoid the trigger word
(e.g., "description **updated**" instead of "description **fixed**").
Adding a `### Class F` section in the packet markdown is NOT enough —
the parser requires a claim whose evidence class resolves to PROVENANCE.

### E004 — informational only
"Class E Evidence is a plain text reference, not a URL." — This is non-blocking.
Intent links should still be SHA-pinned GitHub URLs for immutability.

### `aiv abandon` requires interactive confirmation
Pipe `echo "y" |` to skip the prompt:
```bash
echo "y" | aiv abandon
```

### `--skip-checks` is R0-only
Passing `--skip-checks` with `-t R1` or higher is a hard error.
Only use `--skip-checks` for pure documentation, formatting, or deletion commits
at `-t R0`.

---

## Intent URL format (Class E)

Intent (Class E) links must target a **commit SHA**, not a mutable branch, so the
referenced intent can never drift out from under the packet.

**For audit-driven findings, the intent IS the audit record.** Point Class E at the
in-repo audit artifact that actually raised the finding (e.g.
`audit/02-static-audit.md#L179`) — not at an unrelated task file. Do **not** copy a
`task_NNN.md` URL from an example without verifying it genuinely records the intent
for *this* change. A Class E link that doesn't trace to the work is cargo-cult
provenance and defeats the purpose of the evidence class — verify before you cite.

```
# CORRECT — audit-driven finding: the audit record is the intent (SHA-pinned)
https://github.com/ImmortalDemonGod/flashcore/blob/<full-40-char-sha>/audit/02-static-audit.md#L179

# CORRECT — task-driven work: a taskmaster task that genuinely specifies it (SHA-pinned)
https://github.com/ImmortalDemonGod/flashcore/blob/<full-40-char-sha>/.taskmaster/tasks/task_NNN.md

# WRONG — mutable branch ref (drifts out from under the packet)
https://github.com/ImmortalDemonGod/flashcore/blob/main/audit/02-static-audit.md

# WRONG — a file copied from an example that does not record THIS change's intent
```

Find the right SHA for whatever artifact records the intent:
`git log --oneline --follow -- <path/to/intent/artifact>`

---

## Task Tracking

Tasks live in `.taskmaster/tasks/`. Check task status before starting work:

```bash
python3 -c "
import json
d = json.load(open('.taskmaster/tasks/tasks.json'))
for t in d['master']['tasks']:
    print(f'Task {t[\"id\"]}: {t[\"title\"]} — {t[\"status\"]}')
"
```

Mark subtask status in the individual `.taskmaster/tasks/task_NNN.md` files
as part of commits so progress is tracked in git history.

---

## Testing

```bash
# Always use the project venv
source .venv/bin/activate
pytest tests/ -q --tb=short
```

480 tests, 1 skipped is the expected baseline (as of 2026-03-22).

---

## Architecture reminder (Hub-and-Spoke)

- **Spoke** (`flashcore/`): pure logic, no hardcoded paths, no globals.
- **Hub** (`flashcore/cli/`): injects all paths at runtime via flags or `FLASHCORE_DB`.
- **Scripts** (`flashcore/scripts/`): utility scripts, NOT part of the installed package.
  Never import from `flashcore.scripts` in core code.
- `HPE_ARCHIVE/` has been removed. Do not recreate it or reference it.
