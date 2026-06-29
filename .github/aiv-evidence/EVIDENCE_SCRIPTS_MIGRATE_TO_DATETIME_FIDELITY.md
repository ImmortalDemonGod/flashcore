# AIV Evidence File (v1.0)

**File:** `scripts/migrate_to_datetime_fidelity.py`
**Commit:** `e8df5fb`
**Generated:** 2026-06-29T20:47:12Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R0
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "scripts/migrate_to_datetime_fidelity.py"
  classification_rationale: "R0 standalone migration script"
  classified_by: "Miguel Ingram"
  classified_at: "2026-06-29T20:47:12Z"
```

## Claim(s)

1. migrate_to_datetime_fidelity converts the due columns to TIMESTAMPTZ, adds cards.step, and backfills step=0 for Learning/Relearning idempotently
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/pull/58](https://github.com/ImmortalDemonGod/flashcore/pull/58)
- **Requirements Verified:** Existing DBs need migration since the schema uses CREATE TABLE IF NOT EXISTS

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`e8df5fb`](https://github.com/ImmortalDemonGod/flashcore/tree/e8df5fbdb20ccf8946f36c2581d4b3647cca04c4))

- [`scripts/migrate_to_datetime_fidelity.py#L1-L151`](https://github.com/ImmortalDemonGod/flashcore/blob/e8df5fbdb20ccf8946f36c2581d4b3647cca04c4/scripts/migrate_to_datetime_fidelity.py#L1-L151)

### Class A (Execution Evidence)

- Local checks skipped (--skip-checks).
- **Skip reason:** Standalone one-shot migration script; not imported by the package, validated by running on a copy of the live DB (types converted, step backfilled, data intact)


---

## Verification Methodology

**R0 (trivial) -- local checks skipped.**
**Reason:** Standalone one-shot migration script; not imported by the package, validated by running on a copy of the live DB (types converted, step backfilled, data intact)
Only git diff scope inventory was collected. No execution evidence.

---

## Summary

Idempotent datetime+step migration
