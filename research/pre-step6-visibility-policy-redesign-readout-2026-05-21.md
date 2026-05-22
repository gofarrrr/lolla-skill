# Visibility Policy Redesign Readout

Date: 2026-05-21

Status: research-only. `SKILL.md` and runtime remain untouched.

## Slice

Experiment id:

```text
design_preamble_visibility_policy_redesign_v0
```

New artifact:

```text
pre_step6_visibility_policy_redesign.v1
```

Files:

```text
scripts/research/pre_step6_visibility_policy_redesign.py
tests/test_pre_step6_visibility_policy_redesign.py
research/pre-step6-visibility-policy-redesign/*.visibility-policy-redesign.v1.json
```

## Problem

The false-standdown bridge probe showed that this runtime rule is too
conservative:

```text
unresolved -> anchor visible, deck private
```

The rule hides useful deck pressure in cases where the anchor looks calmer or
shorter but drops concrete decision payload.

## Redesign

The redesigned rule uses Step 6's own private ledger as the cognitive signal:

```text
If cache is hit,
and Step 6 records additive non-anchor pressure,
and protected anchor payload is preserved,
then deck-aware Step 6 output may be visible.
```

No runtime reviewer loop is added.

Deterministic code remains limited to:

```text
validate_cache_state
validate_step6_ledger_schema
validate_payload_preservation
preserve_audit_custody
```

## Fixture Results

| Case | Legacy Policy | Redesigned Policy |
| --- | --- | --- |
| `bridge-high-clutter-sensitive-overlay` | `anchor_visible_deck_private` | `deck_visible_from_step6_additive_pressure` |
| `bridge-sensitive-anchor-misses-tripwire` | `anchor_visible_deck_private` | `deck_visible_from_step6_additive_pressure` |
| `bridge-sequencing-sensitive-boundary` | `anchor_visible_deck_private` | `deck_visible_from_step6_additive_pressure` |
| `mother-address-year` | `anchor_visible_deck_private` | `anchor_visible_deck_private` |
| `synthetic-cache-miss` | `anchor_visible_deck_private` | `current_step6_visible_no_deck` |
| `synthetic-missing-ledger` | `anchor_visible_deck_private` | `anchor_visible_unclear_ledger_guardrail` |
| `synthetic-payload-omission` | `anchor_visible_deck_private` | `anchor_visible_payload_omission_guardrail` |

## What Changed

The policy no longer treats "no reviewer confirmation" as enough reason to hide
the deck when Step 6 itself has already recorded additive pressure.

This preserves the philosophical boundary:

- Step 6 supplies the cognitive signal.
- Deterministic code checks whether the signal is structurally valid and safe to
  surface.
- Runtime still does not add a reviewer loop.
- Anchor fallback remains available when the signal is private/confirming,
  unclear, cache-missing, or payload-losing.

## What This Does Not Prove

This redesign is a policy contract, not runtime integration.

It assumes the upstream system can provide:

- a cache hit for a compiled deck;
- a valid Step 6 private ledger;
- a payload gate result;
- an answer candidate produced by Step 6.

The bridge cases are still packet-level evidence. They do not prove that the
production card generator will reliably create additive-pressure ledgers in
the same cases.

## Recommendation

Keep runtime dormant.

The redesign clears the specific false-standdown policy flaw, but promotion
still needs either:

- a replay slice proving actual Step 6 bridge ledgers produce the needed
  additive-pressure signal; or
- full calibration-floor curation with same-case V60 on/off pairs.

The next technical slice should be:

```text
bridge_step6_ledger_replay_v0
```

Its purpose would be to test whether the full Step 6 replay path, not just the
packet-level bridge probe, produces the additive ledger signals the redesigned
policy relies on.
