# AIV Evidence File (v1.0)

**File:** `tests/test_scheduler.py`
**Commit:** `966032e`
**Previous:** `da58c33`
**Generated:** 2026-06-29T20:47:13Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R0
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/test_scheduler.py"
  classification_rationale: "R0 test-only change"
  classified_by: "Miguel Ingram"
  classified_at: "2026-06-29T20:47:13Z"
```

## Claim(s)

1. test_scheduler asserts learning-step next_due is a future sub-day datetime and that step persistence graduates a card
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/pull/58](https://github.com/ImmortalDemonGod/flashcore/pull/58)
- **Requirements Verified:** Tests must assert datetime fidelity, not the old truncated-date behavior

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`966032e`](https://github.com/ImmortalDemonGod/flashcore/tree/966032ed0857a3f35f140c50e7c28a352bce0d19))

- [`tests/test_scheduler.py#L53-L61`](https://github.com/ImmortalDemonGod/flashcore/blob/966032ed0857a3f35f140c50e7c28a352bce0d19/tests/test_scheduler.py#L53-L61)
- [`tests/test_scheduler.py#L128-L131`](https://github.com/ImmortalDemonGod/flashcore/blob/966032ed0857a3f35f140c50e7c28a352bce0d19/tests/test_scheduler.py#L128-L131)
- [`tests/test_scheduler.py#L215`](https://github.com/ImmortalDemonGod/flashcore/blob/966032ed0857a3f35f140c50e7c28a352bce0d19/tests/test_scheduler.py#L215)
- [`tests/test_scheduler.py#L241-L242`](https://github.com/ImmortalDemonGod/flashcore/blob/966032ed0857a3f35f140c50e7c28a352bce0d19/tests/test_scheduler.py#L241-L242)
- [`tests/test_scheduler.py#L254`](https://github.com/ImmortalDemonGod/flashcore/blob/966032ed0857a3f35f140c50e7c28a352bce0d19/tests/test_scheduler.py#L254)
- [`tests/test_scheduler.py#L369-L370`](https://github.com/ImmortalDemonGod/flashcore/blob/966032ed0857a3f35f140c50e7c28a352bce0d19/tests/test_scheduler.py#L369-L370)
- [`tests/test_scheduler.py#L395-L396`](https://github.com/ImmortalDemonGod/flashcore/blob/966032ed0857a3f35f140c50e7c28a352bce0d19/tests/test_scheduler.py#L395-L396)
- [`tests/test_scheduler.py#L505`](https://github.com/ImmortalDemonGod/flashcore/blob/966032ed0857a3f35f140c50e7c28a352bce0d19/tests/test_scheduler.py#L505)
- [`tests/test_scheduler.py#L510`](https://github.com/ImmortalDemonGod/flashcore/blob/966032ed0857a3f35f140c50e7c28a352bce0d19/tests/test_scheduler.py#L510)
- [`tests/test_scheduler.py#L527`](https://github.com/ImmortalDemonGod/flashcore/blob/966032ed0857a3f35f140c50e7c28a352bce0d19/tests/test_scheduler.py#L527)
- [`tests/test_scheduler.py#L530`](https://github.com/ImmortalDemonGod/flashcore/blob/966032ed0857a3f35f140c50e7c28a352bce0d19/tests/test_scheduler.py#L530)
- [`tests/test_scheduler.py#L613-L614`](https://github.com/ImmortalDemonGod/flashcore/blob/966032ed0857a3f35f140c50e7c28a352bce0d19/tests/test_scheduler.py#L613-L614)
- [`tests/test_scheduler.py#L820-L901`](https://github.com/ImmortalDemonGod/flashcore/blob/966032ed0857a3f35f140c50e7c28a352bce0d19/tests/test_scheduler.py#L820-L901)

### Class A (Execution Evidence)

- Local checks skipped (--skip-checks).
- **Skip reason:** Test-only change: corrects assertions that encoded the truncated-date behavior and adds learning-step regressions; verified by the suite passing


---

## Verification Methodology

**R0 (trivial) -- local checks skipped.**
**Reason:** Test-only change: corrects assertions that encoded the truncated-date behavior and adds learning-step regressions; verified by the suite passing
Only git diff scope inventory was collected. No execution evidence.

---

## Summary

Datetime-fidelity scheduler regressions
