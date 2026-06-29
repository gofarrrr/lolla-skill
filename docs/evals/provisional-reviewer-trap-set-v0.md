# Provisional Reviewer Trap Set v0

Status: docs/fixture design
Date: 2026-06-29
Review capacity mode: `codex_assisted_provisional`
Slice: PR82 Provisional Reviewer Trap Set v0

## Purpose

PR82 creates a small adversarial trap set for the Product Delta specialist
architecture before any real specialist batch is run.

The trap set is:

- a contract expectation fixture;
- paraphrase-only and checked-in safe;
- designed to test review discipline;
- not human-labeled eval data;
- not product proof;
- not judge calibration data;
- not answer-quality scoring;
- not runtime integration;
- not agent approval.

The companion JSON fixture is:

```text
docs/evals/provisional-reviewer-trap-set-v0.json
```

## Why Traps Come First

PR79 defined the architecture:

```text
existing artifacts
-> deterministic packetization
-> focused provisional specialist reads
-> typed outputs
-> deterministic schema validation
-> PR78 evidence-boundary lint
-> disagreement-preserving conservative synthesis
-> later human review
```

PR80 defined the specialist contracts. PR81 built checked-in-safe packet
scaffolding. PR82 now tests the shape before PR83 uses it on more real cases.

This order matters because a future specialist batch can fail in a polished
way. It can over-credit long revised answers, treat caution as leverage, miss
lost value, smooth away disagreement, or harden candidate reads into proof. The
trap set makes those failure modes visible before the repo adds another
Codex-assisted batch.

## Runtime And Eval Boundary

PR82 remains entirely downstream and offline.

```text
Lolla runtime:
  captures the current conversation
  runs OpenRouter-backed audit lanes
  produces the revised answer
  persists custody artifacts, memo, Observatory, and archive

Product Delta eval lane:
  reads existing safe artifacts later
  packetizes cases
  supports provisional specialist review outside runtime
  validates schemas and non-claims
  preserves disagreement and uncertainty
  prepares later human validation
```

The runtime produces the object of study. The eval lane studies it later.

PR82 does not run `$lolla`, invoke the Lolla skill, call providers, mutate
archives, change prompts, touch `SKILL.md`, change runtime behavior, create
specialist-review outputs, or run a model.

## How The Trap Set Relates To Prior Slices

| Slice | Role | PR82 relationship |
|---|---|---|
| [PR78 boundary lint](product-delta-evidence-boundary-lint-v0.md) | Deterministically blocks overclaim and privacy drift. | Trap artifacts must pass lint; one trap checks hardening risk. |
| [PR79 architecture](context-engineered-provisional-review-architecture-v0.md) | Defines decomposition and fan-in doctrine. | Traps target the architecture's expected discipline. |
| [PR80 contracts](product-delta-specialist-review-contracts-v0.md) | Defines typed specialist outputs. | Traps name which specialist roles should resist each failure. |
| [PR81 packet builder](product-delta-specialist-packet-builder-v0.md) | Builds input packets only. | Traps should be usable as future packet/reviewer checks without filling answers. |

## Trap Families

The JSON fixture includes ten trap families:

| Trap family | What it tests | Expected provisional behavior |
|---|---|---|
| `thin_context_should_stay_inconclusive` | Safe context is too compressed. | Block, downgrade, or ask for more source context. |
| `longer_revised_no_action_change` | Revised answer is longer but action shape does not change. | Do not credit length or organization as Product Delta evidence. |
| `caution_without_decision_leverage` | Revised answer adds caution without actionability. | Treat as noisy friction or partial at most. |
| `gate_already_present_in_vanilla` | Lolla repeats a gate that vanilla already had. | Do not credit Lolla with adding the gate. |
| `lost_live_option` | Revised answer drops an option the user had not rejected. | Flag interpretation adequacy and lost value. |
| `ambition_buried_by_generic_prudence` | User-specific urgency or agency is buried under generic caution. | Record lost value and value-overwrite risk. |
| `assistant_influence_blindness` | The baseline assistant shaped the user's frame. | Preserve assistant influence as part of interpretation. |
| `specialist_disagreement_must_survive` | Structural delta is strong but skeptic reads are weak. | Preserve disagreement; do not synthesize by majority. |
| `clean_artifact_not_quality_proof` | Artifact health is clean but advice may be weak. | Keep custody separate from advice usefulness. |
| `provisional_language_hardening` | Candidate language starts sounding authoritative. | Soften or reject the hardening and require non-claims. |

## What Passing A Trap Means

Passing a trap means a future specialist-review setup stayed inside the
contract expectation for that fixture. For example, it may mean the reviewer
was willing to say inconclusive, identify lost value, preserve disagreement,
or refuse a proof-like claim.

Passing a trap does not mean:

- Lolla improved a decision;
- the trap expectation is a human label;
- Codex produced ground truth;
- a judge is calibrated;
- an answer-quality score exists;
- a Product Delta case is product proof;
- an agent may act.

## What Failure Means

A trap failure is a design warning. It means the specialist contract, packet
shape, reviewer instruction, lint surface, or fan-in design may be too easy to
misuse.

The right response is to repair the review surface before PR83 runs real
specialist role-passes. The wrong response is to weaken the boundary or hide
the failure under smoother prose.

## Good Specialist Behavior

A good provisional specialist architecture is not one that finds more Lolla
wins. It is one that becomes more disciplined:

- less over-inference;
- more explicit uncertainty;
- better lost-value detection;
- better interpretation-adequacy detection;
- more willingness to mark inconclusive, noisy, no-material-change, or worse;
- clearer human follow-up questions;
- fewer overclaim risks.

## How PR83 Should Use This

PR83 has now run the first Codex-assisted specialist-review batch using the
PR82 traps:
[Codex-Assisted Specialist Review Batch v0](codex-assisted-specialist-review-batch-v0.md).

Future specialist batches should continue to run or manually inspect the PR82
trap set against the same contracts and packet shape. They should report:

- which traps the specialist setup resisted;
- which traps exposed over-inference or hardening;
- whether any contract or packet shape needs repair;
- whether the future batch should be delayed until the trap failure is fixed.

If the trap set reveals a repeated failure, the reviewer should treat that as a
review-surface problem, not as evidence about Lolla's product value.

## Validation Meaning

Validation can show:

- the trap JSON is well-formed;
- required trap families are present;
- lower-claim metadata remains conservative;
- privacy markers are absent;
- PR78 lint accepts the trap artifacts;
- the traps target PR80 specialist roles.

Validation cannot show:

- Lolla changes decisions usefully;
- future specialist reads will be correct;
- the trap expectations are human labels;
- a broad judge is safe to use;
- product claims are established.

## Next PR

Recommended next slice:

```text
PR84 Fan-In / Disagreement Report v0
```

PR84 should compare PR83 specialist outputs to PR76 broad reads and focus on
preserving disagreement without majority voting, scoring, product proof, or
runtime integration.
