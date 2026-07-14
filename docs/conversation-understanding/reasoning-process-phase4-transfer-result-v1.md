# Reasoning-process Phase-4 transfer result

Status: transfer gate failed; useful records produced, minority-signal stability not established  
Date: 2026-07-11

## Simple explanation

We tested the Case-02 design on two other conversations selected mechanically,
not because their content looked easy. Each case used four whole-conversation
readers and seven small chronological exploration readers.

The machinery worked. After preserving one OpenRouter 429 and completing that
same call once after a cool-off, all 22 jobs completed. Every dimension produced
source-linked records, all admitted aliases resolved, no model record required
deterministic semantic repair, and no record was quarantined.

The semantic transfer gate did not work well enough. The readers recovered all
five protected minority targets in neither case:

- Case 05 recovered one exactly, semantically preserved one with stronger
  adjacent evidence, partially preserved one, and missed two;
- Case 01 recovered four exactly and partially preserved one;
- across both cases, the evidence reader lost part or all of the protected
  claim-boundary relationship.

This is not an empty-system result. The run produced 52 useful, inspectable
records and no critical dimension was empty. It is also not permission to call
the system reliable. A reader can cover the broad topic while still missing the
small detail that changes how the reasoning should be understood.

## What this teaches us

Stable aliases, strict schemas, record-level custody, and small output contracts
solve mechanical reliability. They do not solve salience selection over a full
conversation. In Case 05, evidence and uncertainty readers filled their
four-record budget with plausible major themes while omitting protected details.
The position reader returned one coherent trajectory but dropped its
deadline-based reopen condition. The challenge reader found other pressures but
missed the clearest direct correction.

The local exploration design transferred better: both protected
alternative-plus-attached-limit pairs were recovered exactly. Its advantage is
not a smarter model or a deterministic relevance rule. It gives the model a
smaller chronological semantic job and lets deterministic code enforce only
source regions, identities, budgets, and custody.

## Accounting

- first attempts: 22 provider requests;
- first-attempt operational success: 21/22;
- separately frozen cooled operational completion: 1 request;
- eventual completion: 22/22 jobs;
- admitted records: 52;
- quarantined records: 0;
- protected exact visibility: 5/10;
- semantic target review: 6 supported, 2 partial, 2 not observed;
- estimated cost: $0.03333325;
- automatic retries, semantic retries, fallback models, evaluator, embedding,
  graph, pipeline, and runtime calls: zero.

These are an evidence vector, not a quality, effort, proof-of-work, or trust
score.

## Decision

Phase 4 fails its prospectively frozen transfer gate. We do not tune either
completed case, repeat for stability, or proceed to graph/runtime integration.

The next step is provider-free architecture work: replace the four global
selection jobs with bounded chronological shards while keeping LLMs responsible
for semantic interpretation and deterministic code responsible only for
chronology, visible source regions, exact evidence, budgets, and terminal
custody. We should reject any redesign that uses deterministic semantic gating,
recreates a global synthesizer, or expands into an uncontrolled event flood.

## Continuation evidence

- frozen transfer contract:
  `research/reasoning-process-phase4-transfer-design-2026-07-11/contract.json`;
- first attempts:
  `research/reasoning-process-phase4-transfer-run-2026-07-11/`;
- preserved operational completion:
  `research/reasoning-process-phase4-transfer-retry-2026-07-11/`;
- mechanical and source-first reviews:
  `research/reasoning-process-phase4-transfer-review-2026-07-11/`.

An append-only correction in that review directory fixes an alias-description
mistake in the original human review without changing the frozen original,
exact-visibility gate, or transfer decision.
