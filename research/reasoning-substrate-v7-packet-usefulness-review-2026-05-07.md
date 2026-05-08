# PR35 V7 Packet Usefulness Review

**Status:** dormant packet-quality review, no runtime promotion

**Decision label:** `v7_packet_handoff_useful`

**Branch:** `feature/reasoning-substrate-pr35-v7-packet-usefulness-review`

## Purpose

PR35 tests the question PR34 left open:

> Did the controlled Batch 6/v7 enrichment make a communication/competition
> packet more useful for the next reasoning actor, or did it merely increase
> corpus size?

This is a handoff-quality review only. It does not answer the synthetic case,
choose final Decision Pressure, create user-facing copy, run live lanes, or
promote v7 into runtime.

## Method

PR35 creates the same explicit 9-card nomination set twice:

1. `pr35-v6-communication-competition-packet-review`
   - Uses `affordances_v6.json`.
   - The PR34 target models are still graph-only.
2. `pr35-v7-communication-competition-packet-review`
   - Uses `affordances_v7.json`.
   - The same PR34 target models now carry reviewed affordance depth.

Both packets are generated through the dormant explicit-nomination producer.
No live lanes are run.

The synthetic transaction is a partner-feedback / competitive-copying review
where an assistant recommends clarifying expectations, giving feedback, and
matching a competitor quickly without testing:

- stable best responses;
- mutual defection incentives;
- listening quality;
- feedback specificity;
- SBI structure;
- analogy fit;
- adaptive selection conditions;
- cross-cultural frame translation;
- counterparty payoff response.

## Compared Packet Shape

| Measure | v6 packet | v7 packet | Delta |
| --- | ---: | ---: | ---: |
| Candidate cards | 9 | 9 | 0 |
| Suppressed duplicates | 1 | 1 | 0 |
| Reviewed cards | 2 | 9 | +7 |
| Graph-only cards | 7 | 0 | -7 |
| Missing reviewed records | 7 | 0 | -7 |
| Absence-only cards | 0 | 0 | 0 |
| Source-too-thin cards | 0 | 0 | 0 |
| Weak/conflicting cards | 0 | 0 | 0 |

The useful signal is stable shape with deeper cards. PR35 does not add more
candidates to create the appearance of improvement.

## Card-Level Read

`nash-equilibrium` improves the strategic-interdependence part of the packet.
It asks whether each party's current move is already a stable best response and
separates stable, reachable, and desirable. The absence record blocks the lazy
mistake that stable means good.

`prisoners-dilemma` improves the cooperation/defection part of the packet. It
helps the receiver test whether bad collective behavior comes from incentives
before assigning bad intent. The absence records block turning every
coordination problem into betrayal.

`active-listening` improves the conversation-diagnosis part of the packet. It
pushes the receiver to understand the other side's constraint or disagreement
before rebuttal or advice. The absence records block performative listening and
sweeping interpretation.

`constructive-feedback-models` improves the feedback-standard part of the
packet. It requires observed behavior, standard, impact, and actionable
adjustment rather than vague managerial advice or rank-backed correction.

`feedback-models-sbi` improves the feedback-structure part of the packet. It
separates situation, behavior, impact, invitation, and receiver constraints
instead of letting "give feedback" remain generic.

`analogies-and-metaphors` improves the analogy-transfer part of the packet. It
turns a competitor playbook analogy into a structural-fit test and blocks using
a vivid analogy as proof.

`natural-selection-analogy` improves the adaptive-learning part of the packet.
It asks for variants, fitness criteria, feedback channels, and retention rules
before invoking adaptation. The absence records block survival-proves-optimal
reasoning and simplistic competition metaphors.

## Usefulness Verdict

The v7 packet is more useful as handoff material than the v6 packet.

Reason:

- the same nominations are used;
- candidate count stays fixed at `9`;
- duplicate suppression remains visible;
- the seven PR34 graph-only shelves become reviewed handoff cards;
- each upgraded card carries activation, evidence-needed, do-not-use, misuse,
  treatment, source-evidence, and absence signals;
- the reviewer-only render stays compact enough to inspect;
- no final pressure, user-facing prose, memo copy, or runtime output appears.

This is productive movement. PR34 enrichment improved the next LLM/reviewer
packet without Python choosing the answer.

## What This Does Not Prove

PR35 does not prove:

- the v7 packet produces a better final user answer;
- the receiver will always use the new cards well;
- runtime packet production is ready;
- v7 should be imported by live lanes;
- another extraction batch should be broad;
- the remaining 134 graph-only models are all equally important.

## Recommendation

PR36 may be another controlled enrichment batch only if the next targets are
selected by capability gaps and likely packet usefulness.

The strongest remaining direction is not "finish the corpus." It is to choose
one narrow capability family where graph-only cards are likely to appear in
packets and remain thin. Candidate families to inspect before extracting:

- planning and prioritization residues not covered by v6/v7;
- trust, relationship repair, or negotiation communication beyond feedback;
- abductive and analogical hypothesis generation if future packets need
  exploratory reasoning;
- customer/market dynamics if additional product cases keep pulling graph-only
  shelves.

Do not start runtime work from PR35. The next safe production move is still
controlled enrichment or another packet comparison, not live integration.

## Non-Promotion Boundary

PR35 does not:

- run live `/lolla`;
- change prompts;
- rewrite lanes;
- build a live lane adapter;
- add runtime packet production;
- promote v7 into runtime;
- create user-facing Decision Pressure;
- wire Observatory, memo, Step 8, Step 6, or Lane 4 runtime;
- call models;
- run judges;
- create Batch 3b;
- make Python choose final pressure.
