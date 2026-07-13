# Simulated reliability V1 constitutional gap audit

Status: provider-free design decision; no V1 pipeline call authorized  
Date: 2026-07-12

## Decision

Lolla is ready to move from source construction to a bounded reliability
experiment. It is not ready for runtime integration or a usefulness claim.

The next experiment must compare three fresh-context arms on the same complete
conversation:

1. **transcript-only** — a strong fresh reconsideration without Lolla pressure;
2. **direct pressure** — the same reconsideration contract plus canonical
   mental models recalled directly from controlled reasoning mechanisms; and
3. **graph-expanded pressure** — the complete direct portfolio plus a small,
   structurally diverse set of one-hop relationship-graph candidates.

This is the smallest comparison that can separate the benefit of a fresh
second pass, the benefit of controlled direct pressure, and the incremental
effect of the relationship graph. The outputs are compared as a scorecard, not
collapsed into a quality score.

## What the current loop actually proves

The minimum viable loop already demonstrates:

- complete transcript custody;
- probabilistic, source-linked interpretation of position and uncertainty;
- probabilistic selection from nine controlled reasoning-mechanism identities;
- deterministic union of canonical direct mental-model seeds;
- an empty-portfolio stand-down when no mechanism is unresolved;
- fresh apply/reject/park dispositions for every presented candidate;
- one useful non-obvious pressure result and one correct quiet result; and
- a self-contained machine-readable receipt with preserved failures.

Those are real capabilities, but the graph was dormant. The frozen routing
policy explicitly sets `graph_expansion` to `false`. The prior graph shadow
proved only that a source-reviewed, fact-free mechanism projection can change
the graph neighborhood. It did not prove that graph-only candidates improve or
protect reconsideration.

## Current constitutional fit

| constitutional requirement | present evidence | V1 state |
| --- | --- | --- |
| raw conversation stays authoritative | full transcript and hashes survive the minimum loop and V1 source freeze | retain |
| LLMs interpret messy meaning | role and mechanism interpretation are probabilistic | retain; test transfer |
| code controls custody, identity, replay, and bounds | exact IDs, hashes, schemas, and deterministic seed union are validated | retain |
| pressure is a hypothesis | portfolios deny semantic applicability and consumer dispositions allow rejection | retain |
| freedom of conclusion, not freedom from consideration | every active candidate receives apply/reject/park custody | retain |
| strange pressure is allowed | direct candidates are not relevance-prefiltered | incomplete until graph-only pressure is tested |
| unknown unknowns become questions, not facts | V2 consumer contract forbids manufactured precision and unsupported facts | test transfer |
| private breadth differs from public friction | private dispositions and a public reconsidered answer are distinct | test bloat, forcing, and stand-down |
| receipt proves process, not wisdom | non-claims and preserved failures are explicit | test reconstruction; never issue a badge |
| builder and grader are separated | cold-reader work exists, but the V1 blinded comparative review is not frozen | incomplete |
| current practice is dated | prior provider/schema research exists | refresh before calls |
| bounded decomposition includes fan-in | current packet caps ten candidates | incomplete for direct plus graph fan-in |
| controlled identities, probabilistic applicability | direct routing uses canonical IDs and does not certify fit | retain |
| graph recall is not probabilistically re-domesticated | no graph candidates reach the consumer today | unproved |

## The graph volume problem

The controlled routing table contains 19 unique direct seed models across nine
mechanisms. The frozen relationship graph contains 1,358 edges. Those 19 seeds
have 134 eligible outgoing one-hop edges reaching 47 distinct targets; the
direct-plus-neighbor union contains 52 models.

Dumping that neighborhood into one prompt would violate the fan-in and context
dumping rules. Asking another LLM to remove low-fit candidates would violate
the rule against probabilistic re-domestication. Pretending that graph affinity
proves applicability would also violate the constitution.

V1 therefore uses a declared structural bound:

- direct candidates are preserved exactly as produced by the controlled
  mechanism-to-seed union, deduplicated by canonical model ID;
- the direct active portfolio is capped at ten, matching the already tested
  fresh-pressure contract; any overflow remains in a visible reserve with a
  capacity reason, never a semantic rejection;
- the graph-expanded arm retains every direct active candidate and adds at most
  three graph-only candidates, for an active maximum of thirteen;
- the three graph slots are structural diversity slots: one `antagonist`, one
  `tension`, and one `ally` when available;
- within a slot, source IDs and target IDs are ordered lexically and replayed
  deterministically; no conversation keyword, embedding, affinity score, or
  LLM relevance judgment affects admission;
- all eligible one-hop edges, deduplication events, selected candidates, and
  capacity-overflow candidates remain in the private graph ledger; and
- the fresh reasoner sees every active graph candidate and may apply, reject,
  or park it. Selection is never described as proof that the model applies.

The three-slot rule is an experimental bound, not a claim that three graph
models are optimal. If a relation type has no eligible graph-only target, its
slot stays empty; it is not filled through semantic guessing. A later version
may test batching or a larger reserve only if V1 shows that graph pressure is
useful enough to justify more fan-in.

## Why this does not become a brittle gating system

The only deterministic decisions are identity validation, exact graph
traversal, deduplication, structural relation diversity, volume limits,
ordering, hashing, and custody labels. Code never decides whether the
conversation exhibits a mechanism or whether a mental model applies.

The probabilistic mechanism interpreter may select none, one, or several
controlled mechanisms. The fresh reasoner may reject all mental models. These
are valid outcomes rather than failures to be repaired.

## V1 comparisons and non-claims

The primary incremental comparisons are:

- transcript-only versus direct pressure: controlled-pressure contribution;
- direct pressure versus graph-expanded pressure: graph contribution;
- transcript-only versus graph-expanded pressure: complete bounded-loop effect.

The graph comparison includes the cost and attention burden of up to three
additional candidates. That burden is part of the treatment and must be
reported. V1 will not claim a pure causal effect of graph topology independent
of candidate volume, a universally optimal graph cap, human usefulness,
decision correctness, or production reliability.

An unchanged recommendation can still contain useful pressure: a novel
falsifier, verification target, boundary, contingency, or accountable
rejection. A changed recommendation can still be worse. Review must therefore
look for contribution and harm separately.

## Remaining gates before a provider call

1. Implement the three-arm packet and graph-ledger builders locally.
2. Prove deterministic replay, no-deletion custody, direct-arm identity, and
   graph-slot diversity with fixtures.
3. Refresh and record July 2026 model/provider, structured-output, privacy,
   seed, and routing practice.
4. Freeze exact prompts, schemas, models, provider endpoints, prices, budgets,
   repetitions, call order, blind labels, review instructions, and stop rules.
5. Run provider-free negative tests for malformed IDs, graph-path mismatch,
   candidate overflow, duplicate provenance, empty portfolios, incomplete
   dispositions, and fabricated terminal success.

Only then may calibration sentinels be called. The twelve transfer cases remain
untouched until calibration passes and the runtime contract is sealed.

## Frozen inputs inspected for this audit

- `lolla-product-constitution-v5.md` —
  `c8e6f4f09f24ad6512edb5a3478cbcbcd5659886dea373e8e43c90d53d1b9b7b`
- `lolla-evaluation-doctrine-v0.md` —
  `a236fea812b8edf593aa9f0c1e063acedb13896592bce4187bc6cee8c149f04e`
- `reasoning-pattern-shadow-routing-v0.json` —
  `ab5bb347a4f0fc272dfb61b2ff82a8285f5e17b4297587253d286f947a3055ef`
- `data/relationship_graph.json` —
  `89808c4585498f3880b4d7fa0110d64cd46f7acff312c0870fc6cb9a97e752cf`
- `fresh_reasoning_pressure.py` —
  `5633c13b5d074f67797f9ab4fb268b713ee400696e9928cd27815f8db099e2ef`
- `companion_routing.py` —
  `f45d070e1ff3eac7c990da869fd11f149eaceefd7d0d5c347009774310b6014b`
- V1 source manifest —
  `93fabb750960e9c3c2b683f8ae576ca61ca2c50204039718cde0aff7c9ffbb27`

