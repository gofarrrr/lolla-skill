# Bridge Step 6 Ledger Replay Readout

Date: 2026-05-21

Status: research-only. `SKILL.md` and runtime remain untouched.

## Slice

Experiment id:

```text
bridge_step6_ledger_replay_v0
```

New artifacts:

```text
pre_step6_bridge_step6_ledger_replay.v1
pre_step6_bridge_step6_ledger_replay_result.v1
```

Files:

- `scripts/research/pre_step6_bridge_step6_ledger_replay.py`
- `tests/test_pre_step6_bridge_step6_ledger_replay.py`
- `research/pre-step6-bridge-step6-ledger-replays/*.bridge-step6-ledger-replay.v1.json`
- `research/pre-step6-bridge-step6-ledger-replays/bridge-step6-ledger-replay-result.v1.json`

## Question

The visibility-policy redesign depends on one upstream claim:

```text
Step 6 can supply the cognitive signal through its own private ledger.
```

The previous redesign fixtures assumed `step6_ledger_signal:
additive_pressure_present` for the bridge cases. This slice tested whether a
live Step 6-style replay actually produces that signal when given the
pre-registered bridge packets.

## Live Run

Model:

```text
openai/gpt-5.1-chat
```

Command:

```text
LOLLA_LLM_TIMEOUT=60 PYTHONPATH=. python3 scripts/research/pre_step6_bridge_step6_ledger_replay.py --live --all --provider openrouter --model openai/gpt-5.1-chat --env-file /Users/marcin/Desktop/Apps/Lolla/.env.openai.local
```

## Result

All three bridge cases produced `additive_pressure_present` from Step 6's
private ledger.

| Case | Ledger Signal | Redesigned Policy Dependency |
| --- | --- | --- |
| `bridge-high-clutter-sensitive-overlay` | `additive_pressure_present` | unlocked |
| `bridge-sensitive-anchor-misses-tripwire` | `additive_pressure_present` | unlocked |
| `bridge-sequencing-sensitive-boundary` | `additive_pressure_present` | unlocked |

Aggregate:

```text
replay_result: step6_additive_signal_supported
promotion_effect: none_research_only
runtime_wiring_allowed: false
skill_update_allowed: false
```

## What Step 6 Did

Step 6 did not simply pick the longer candidate. In all three cases it used the
anchor as the visible backbone and marked the deck-pressure candidate as
`additive_pressure`:

- Founder/equity case: deck pressure added evidence checks, separation between
  empathy and commitment, and investor-facing boundaries.
- Sensitive parent/minor case: deck pressure added explicit escalation
  tripwires and the warning that a quiet phone is not proof of safety.
- PhD sequencing case: deck pressure added advisor-first alignment, data and
  funding checks, PI/authorship questions, and an 18-month checkpoint.

That is the behavior we wanted: Step 6 thinks with the broad private packet and
records why the non-anchor pressure mattered. Deterministic code only validates
the ledger schema and derives the signal.

## What This Proves

This clears the immediate evidence gap in the visibility redesign:

```text
The bridge cases can produce additive Step 6 ledger signals without a reviewer
loop.
```

The redesigned policy is no longer only a hypothetical contract for these
bridge packets. It has live Step 6 replay support for the ledger dependency.

## What This Does Not Prove

This is still not runtime promotion evidence.

The replay used pre-registered bridge packets, not the full production path for:

- card compilation and cache hits;
- Bevelin/Polya/source-card generation on arbitrary cases;
- V60/card overlap in live selected chunks;
- protected-payload omission checks on the bridge packets;
- calibrated false-standdown and false-promotion rates across 12-20 cases.

## Recommendation

Keep runtime dormant.

The next design step can now treat Step 6's private ledger as a plausible
cognitive signal for a research integration draft. Promotion should still remain
blocked until either the calibration floor is met or the board explicitly
approves a narrow experimental path with cache, payload, ledger, and audit
guardrails still off by default.
