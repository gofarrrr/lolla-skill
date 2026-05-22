# False-Standdown Bridge Probe Readout

Date: 2026-05-21

Status: research-only, non-promotional. `SKILL.md` and runtime remain untouched.

## Probe

Probe id:

```text
false_standdown_bridge_probe_v0
```

Source contract:

```text
research/pre-step6-false-standdown-bridge-probe/false-standdown-bridge-probe.v1.json
```

Aggregate result:

```text
research/pre-step6-false-standdown-bridge-probe/false-standdown-bridge-result.v1.json
```

Judgments:

```text
research/pre-step6-false-standdown-bridge-probe/judgments/*.false-standdown-bridge-judgment.v1.json
```

## Pre-Registered Confirmation Rule

`confirmed_false_standdown` means:

```text
Two reviewer judgments label the same case false_standdown under the same
rubric, fresh blind shuffles, and different model families.
```

Single-reviewer false stand-down and human spot-check alone are not confirmed.

Reviewer families used:

- `openai` via `openai/gpt-5.1-chat`
- `google` via `google/gemini-3.1-flash-lite`

## Result

All three probe cases triggered the stop condition.

| Case | Shape | OpenAI | Google | Confirmed Label |
| --- | --- | --- | --- | --- |
| `bridge-high-clutter-sensitive-overlay` | high clutter plus sensitive tone | `false_standdown` | `false_standdown` | `false_standdown` |
| `bridge-sensitive-anchor-misses-tripwire` | sensitive answer where anchor misses safety tripwire | `false_standdown` | `false_standdown` | `false_standdown` |
| `bridge-sequencing-sensitive-boundary` | sequencing pressure plus sensitive boundary | `false_standdown` | `false_standdown` | `false_standdown` |

Aggregate:

```text
probe_result: design_review_required
promotion_effect: none_bridge_only
runtime_wiring_allowed: false
skill_update_allowed: false
```

## What The Probe Shows

The current runtime asymmetry is too conservative if interpreted as:

```text
normal runtime unresolved -> anchor visible, deck private
```

in every unresolved case.

The dangerous pattern is real in the bridge packets: a calm or concise anchor
can look safer while omitting the very pressure that makes the deck useful.
Both reviewer families independently treated suppression of the deck-visible
candidate as a false stand-down in all three cases.

## What The Probe Does Not Show

This is not full runtime evidence.

The bridge probe uses pre-registered packet cases and visible answer candidates.
It does not prove that the production card-deck generator, Step 6 replay,
ledger, omission gate, and visibility policy will produce the same pattern on
live cases.

The correct read is therefore:

```text
design_review_required_before_integration_draft
```

not:

```text
promote_card_deck_runtime
```

## Recommendation

Revise the visibility-policy design before any integration draft.

The likely design change is not "add a runtime reviewer loop." That would undo
the cost/cache precondition.

The better design question is:

```text
Can normal runtime use Step 6's own private ledger as the cognitive signal?
```

Possible revised rule to test:

```text
If Step 6 marks non-anchor cards as additive_pressure and the payload-omission
gate does not detect introduced omission, runtime may show the deck-aware Step 6
answer without a reviewer loop. Anchor-visible remains the fallback when Step 6
marks non-anchor cards private/confirming, when the ledger is missing/unclear,
or when protected payload is lost.
```

This keeps the key philosophy intact:

- Step 6, not deterministic code, supplies the cognitive signal.
- Deterministic code validates ledger shape, payload preservation, cache mode,
  and audit custody.
- Runtime does not add a reviewer loop.
- Anchor bias remains a fallback, not a universal suppressor.

## Next Research Slice

Run a visibility-policy redesign slice before integration:

```text
design_preamble_visibility_policy_redesign_v0
```

Minimum test:

- show current runtime-unresolved anchor bias would suppress all three bridge
  cases;
- define a ledger-mediated runtime rule that can surface deck-aware output when
  Step 6 itself records additive pressure;
- preserve anchor fallback for private/confirming ledgers, missing ledger,
  payload omission, or cache miss;
- keep all artifacts research-only.
