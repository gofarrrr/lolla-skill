# PR37 V8 Packet Usefulness Review

**Status:** dormant packet-quality review, no runtime promotion

**Decision label:** `v8_packet_handoff_useful`

**Branch:** `feature/reasoning-substrate-pr37-v8-packet-usefulness-review`

## Purpose

PR37 tests the question PR36 left open:

> Did the controlled Batch 7/v8 enrichment make a trust repair, negotiation,
> influence, and signaling packet more useful for the next reasoning actor, or
> did it merely increase corpus size?

This is a handoff-quality review only. It does not answer the synthetic case,
choose final Decision Pressure, create user-facing copy, run live lanes, or
promote v8 into runtime.

## Method

PR37 creates the same explicit 10-card nomination set twice:

1. `pr37-v7-trust-negotiation-packet-review`
   - Uses `affordances_v7.json`.
   - The PR36 target models are still graph-only.
2. `pr37-v8-trust-negotiation-packet-review`
   - Uses `affordances_v8.json`.
   - The same PR36 target models now carry reviewed affordance depth.

Both packets are generated through the dormant explicit-nomination producer.
No live lanes are run.

The synthetic transaction is a founder trust-repair / negotiation review where
an assistant recommends transparency, empathy, boundaries, a concession, and a
public commitment without testing:

- observation/need/request separation;
- emotional landing and standards;
- hidden motivations versus mind-reading;
- ownership boundaries versus avoidance;
- candor with substance;
- non-malice explanations versus repeated harm;
- reciprocal value versus obligation pressure;
- persuasion with autonomy and evidence preserved;
- negotiation substance/signaling/stakeholder sequencing;
- costly proof versus cheap symbolic promise.

## Compared Packet Shape

| Measure | v7 packet | v8 packet | Delta |
| --- | ---: | ---: | ---: |
| Candidate cards | 10 | 10 | 0 |
| Suppressed duplicates | 1 | 1 | 0 |
| Reviewed cards | 0 | 10 | +10 |
| Graph-only cards | 10 | 0 | -10 |
| Missing reviewed records | 10 | 0 | -10 |
| Absence-only cards | 0 | 0 | 0 |
| Source-too-thin cards | 0 | 0 | 0 |
| Weak/conflicting cards | 0 | 0 | 0 |

The useful signal is stable shape with deeper cards. PR37 does not add more
candidates to create the appearance of improvement.

## Card-Level Read

`non-violent-communication` improves the repair-note part of the packet. It
turns vague "be transparent and empathize" advice into an observation, need,
and request check while blocking conflict avoidance.

`emotional-intelligence` improves the emotional-landing part of the packet. It
helps the receiver treat emotion as evidence about adoption, trust, and fairness
without using empathy as a substitute for standards.

`understanding-motivations` improves the interpersonal-inference part of the
packet. It asks for a hidden-driver hypothesis and disconfirming evidence
instead of letting the receiver mind-read resistance.

`boundaries` improves the ownership-reset part of the packet. It separates
inside, outside, and influenceable work while blocking boundaries that merely
protect comfort.

`authenticity` improves the candor-and-trust part of the packet. It requires
real experience or constraint to be tied to evidence and accountable action
rather than self-expression theater.

`hanlons-razor` improves the intent-attribution part of the packet. It delays
malice attribution long enough to test coordination, overload, incentives, and
neglect while preserving escalation for repeated harm.

`reciprocity-principle` improves the concession part of the packet. It separates
real costly value from obligation pressure and keeps independent evaluation
visible.

`persuasion-principles` improves the adoption-design part of the packet. It
allows better framing only when the underlying insight is sound and audience
autonomy remains protected.

`international-negotiation-and-diplomacy-models` improves the settlement part of
the packet. It ties substance, signaling, stakeholders, concessions, sequencing,
and durable alignment together without rewarding tactical point-scoring.

`signaling` improves the commitment-proof part of the packet. It asks whether
the proposed signal is costly, observable, and followed through rather than a
cheap symbolic promise.

## Usefulness Verdict

The v8 packet is more useful as handoff material than the v7 packet.

Reason:

- the same nominations are used;
- candidate count stays fixed at `10`;
- duplicate suppression remains visible;
- the ten PR36 graph-only shelves become reviewed handoff cards;
- each upgraded card carries activation, evidence-needed, do-not-use, misuse,
  treatment, source-evidence, and absence signals;
- the reviewer-only render stays inspectable;
- no final pressure, user-facing prose, memo copy, or runtime output appears.

This is productive movement. PR36 enrichment improved the next LLM/reviewer
packet without Python choosing the answer.

## What This Does Not Prove

PR37 does not prove:

- the v8 packet produces a better final user answer;
- the receiver will always use the new cards well;
- runtime packet production is ready;
- v8 should be imported by live lanes;
- interpersonal/influence packets are product-ready;
- another extraction batch should be broad;
- the remaining 124 graph-only models are all equally important.

## Recommendation

PR38 may be another controlled enrichment batch only if the next targets are
selected by capability gaps and likely packet usefulness.

The strongest remaining direction is not "finish the corpus." It is to choose
one narrow family where graph-only cards are likely to appear in packets and
remain thin. Candidate families to inspect before extracting:

- planning and prioritization residues not covered by v6/v8;
- exploratory hypothesis generation and abductive reasoning;
- risk, resilience, and operational failure-mode diagnosis;
- market/customer dynamics if product cases keep pulling graph-only shelves;
- ethics, incentives, or governance if decision packets keep needing them.

Do not start runtime work from PR37. The next safe production move is still
controlled enrichment or another packet comparison, not live integration.

## Non-Promotion Boundary

PR37 does not:

- run live `/lolla`;
- change prompts;
- rewrite lanes;
- build a live lane adapter;
- add runtime packet production;
- promote v8 into runtime;
- create user-facing Decision Pressure;
- wire Observatory, memo, Step 8, Step 6, or Lane 4 runtime;
- call models;
- run judges;
- create Batch 3b;
- make Python choose final pressure.
