# PR33 V6 Packet Usefulness Review

**Status:** dormant packet-quality review, no runtime promotion

**Decision label:** `v6_packet_handoff_useful`

**Branch:** `feature/reasoning-substrate-pr33-v6-packet-usefulness-review`

## Purpose

PR33 tests the question PR32 left open:

> Did the controlled Batch 5/v6 enrichment make the reasoning-substrate packet
> more useful for the next reasoning actor, or did it merely make the corpus
> bigger?

This is not a final-answer test. It does not ask which Decision Pressure should
surface, does not answer the synthetic transaction, and does not create
user-facing copy. It compares handoff quality only.

## Method

PR33 creates the same explicit 10-card nomination set twice:

1. `pr33-v5-capability-gap-packet-review`
   - Uses `affordances_v5.json`.
   - The PR32 target models are still graph-only.
2. `pr33-v6-capability-gap-packet-review`
   - Uses `affordances_v6.json`.
   - The same PR32 target models now carry reviewed affordance depth.

Both packets are generated through the dormant explicit-nomination producer.
No live lanes are run.

The synthetic transaction is an international platform-renewal / market-entry
review where an assistant recommends speed and continuity but leaves several
candidate shelves underdeveloped:

- fallback credibility;
- counterparty response;
- relative competitive position;
- feedback delay;
- obligation/control traceability;
- customer job evidence;
- lock-in and path dependence;
- cross-cultural frame translation;
- opportunity cost.

## Compared Packet Shape

| Measure | v5 packet | v6 packet | Delta |
| --- | ---: | ---: | ---: |
| Candidate cards | 10 | 10 | 0 |
| Suppressed duplicates | 1 | 1 | 0 |
| Reviewed cards | 1 | 10 | +9 |
| Graph-only cards | 9 | 0 | -9 |
| Missing reviewed records | 9 | 0 | -9 |
| Absence-only cards | 0 | 0 | 0 |
| Source-too-thin cards | 0 | 0 | 0 |
| Weak/conflicting cards | 0 | 0 | 0 |

The useful signal is not the raw count increase. The useful signal is that the
same shelves now carry activation, evidence-needed, do-not-use, misuse,
treatment, source-evidence, and absence material without increasing the
candidate count.

## Card-Level Read

`batna` improved in a product-honest way. The v6 card gives a credible
walk-away test, but it also carries the absence record that the source does not
support full textbook BATNA doctrine. This is exactly the desired behavior:
make the shelf useful without rescuing weak source support with generic
knowledge.

`game-theory-payoffs` moved from a graph-only competitive hint to a
counterparty response map. The reviewed card tells the receiver to name players,
moves, payoff drivers, and decisive branches, while warning against same-game
assumptions and ornate payoff-tree theater.

`red-queen-effect` became clearer as a relative-position check. It tells the
receiver to separate true advantage from merely keeping up, and its absence
record blocks "arms race everything" reasoning.

`delays` became operational. Instead of just hinting at timing, the reviewed
card asks for the lagged feedback signal, review window, and the boundary
between useful waiting and avoidant drift.

`obligations-controls-mapping` now gives live control traceability. It requires
obligation, control, owner/checkpoint, and observed operation, while rejecting
documentation theater.

`jobs-to-be-done` now helps the receiver avoid treating feature requests as
proof of demand. It asks for adoption, switching, abandonment, workaround, or
repeated-use evidence and blocks preference-as-job overclaiming.

`lock-in` and `path-dependence` improved the dependency side of the packet.
They make reversal costs, installed paths, interfaces, contracts, and unwind
costs visible instead of letting the assistant treat the current platform as a
neutral default.

`cross-cultural-communication-frameworks` became useful because it is not a
stereotype card. It asks whether the same message survives translation into the
audience's action frame, while explicitly blocking cultural shortcut reasoning.

## Usefulness Verdict

The v6 packet is more useful as handoff material than the v5 packet.

Reason:

- the same nominations are used;
- the same candidate count is preserved;
- duplicate suppression remains visible;
- graph-only shelves become reviewed handoff cards;
- BATNA stays medium-confidence and source-limited;
- absence records are visible as anti-overclaim material;
- the reviewer-only render remains compact enough to inspect;
- no final pressure, user-facing prose, memo copy, or runtime output appears.

This is the right kind of progress. It does not prove product readiness, but it
does prove that controlled enrichment can improve the reasoning substrate
without making Python choose the answer.

## What This Does Not Prove

PR33 does not prove:

- the v6 packet produces a better final user answer;
- the receiver will always use the new cards well;
- runtime packet production is ready;
- v6 should be imported by live lanes;
- another extraction batch should be broad;
- the remaining 141 graph-only models are all equally important.

## Recommendation

PR34 may be another controlled enrichment batch, but only if it is selected by
capability gaps and likely packet usefulness, not spreadsheet completion.

The strongest remaining candidates are not "whatever is still graph-only." They
are the shelves likely to improve packets in families still thin after v6:

- remaining competitive dynamics: `nash-equilibrium`, `prisoners-dilemma`;
- communication and feedback: `active-listening`,
  `constructive-feedback-models`, `feedback-models-sbi`;
- correction / external review: adjacent models around perspective challenge
  and calibration if lane artifacts keep pulling them;
- analogical and abductive reasoning if a future packet needs hypothesis
  generation rather than execution discipline.

Do not start runtime work from PR33. The next safe production move is still
controlled enrichment or another packet comparison, not live integration.

## Non-Promotion Boundary

PR33 does not:

- run live `/lolla`;
- change prompts;
- rewrite lanes;
- build a live lane adapter;
- add runtime packet production;
- promote v6 into runtime;
- create user-facing Decision Pressure;
- wire Observatory, memo, Step 8, Step 6, or Lane 4 runtime;
- call models;
- run judges;
- create Batch 3b;
- make Python choose final pressure.
