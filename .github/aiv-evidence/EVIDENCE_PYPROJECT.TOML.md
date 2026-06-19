# AIV Evidence File (v1.0)

**File:** `pyproject.toml`
**Commit:** `fbf96d6`
**Generated:** 2026-06-19T07:53:05Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R0
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "pyproject.toml"
  classification_rationale: "R0: no logic change; dependency pin in pyproject.toml only; --skip-checks justified — pure config, no executable diff"
  classified_by: "Claude"
  classified_at: "2026-06-19T07:53:05Z"
```

## Claim(s)

1. flake8 pinned to ==7.3.0, black to ==25.12.0, isort to ==8.0.1, mypy to ==2.1.0 — these are the currently installed versions
2. Unpinned specifiers (>=, ~=) replaced with == to eliminate cross-runner version drift in CI
3. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/blob/97defc9/.taskmaster/tasks/tasks.json](https://github.com/ImmortalDemonGod/flashcore/blob/97defc9/.taskmaster/tasks/tasks.json)
- **Requirements Verified:** DETERMINISM: CI must be reproducible across runners; pin all declared lint tools to installed versions

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`fbf96d6`](https://github.com/ImmortalDemonGod/flashcore/tree/fbf96d65f5229e45465021714222943c3d80b089))

- [`pyproject.toml#L33-L36`](https://github.com/ImmortalDemonGod/flashcore/blob/fbf96d65f5229e45465021714222943c3d80b089/pyproject.toml#L33-L36)

### Class A (Execution Evidence)

- Local checks skipped (--skip-checks).
- **Skip reason:** pure configuration change; no logic or behavior change; installed versions already in use on this runner


---

## Verification Methodology

**R0 (trivial) -- local checks skipped.**
**Reason:** pure configuration change; no logic or behavior change; installed versions already in use on this runner
Only git diff scope inventory was collected. No execution evidence.

---

## Summary

Pin black/isort/flake8/mypy to installed versions so CI is deterministic across runners
