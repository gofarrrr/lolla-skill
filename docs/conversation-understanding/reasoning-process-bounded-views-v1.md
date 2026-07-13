# Reasoning-process bounded views v1

Status: Phase 2 provider-free pass; bounded model probe is next  
Date: 2026-07-11

## Plain-language result

We tested whether the broad Phase-1 ledger already contains enough meaning to
answer five separate questions about a conversation:

1. how the position or decision changed;
2. which alternatives were explored;
3. whether evidence was kept separate from assumptions;
4. what remained uncertain;
5. how the reasoning responded to challenge or correction.

The answer is **mostly no**. Out of 25 protected case/question targets, 11 had
some exact source overlap with a Phase-1 observation, but only one Phase-1
interpretation preserved the complete protected meaning. The other overlaps
usually retained one half of a useful relationship: the plan without its
qualification, the uncertainty without why it matters, or the topic of a
challenge without the fact that the user caused a revision.

This is not a model-quality result. Phase 1 imported artifacts built for
earlier extraction jobs; it was not asked to perform the five new bounded jobs.
The result tells us that source custody and semantic adequacy are different.
A ledger can be broad and perfectly auditable while still being an inadequate
semantic input for a particular question.

## What changed in the design

The authoritative conversation must remain visible to a bounded reader. The
Phase-1 ledger is useful auxiliary context and custody, but it cannot replace
the conversation or silently decide what is relevant.

The target architecture for the next probe is therefore:

1. give one reader one narrow process question;
2. always give it the exact authoritative conversation;
3. include the complete Phase-1 auxiliary ledger only when the whole ledger
   fits the frozen byte budget;
4. never select a semantic subset with keywords, family gates, or deterministic
   ranking;
5. require speaker, turn, and exact quote in the response;
6. resolve those quotes and attach stable span IDs deterministically;
7. append validated observations to custody and construct the bounded view;
8. compare the result source-first with the protected fixture.

If the complete auxiliary ledger does not fit, it is omitted whole. The
conversation is not dropped, summarized, or semantically pruned. This is a
mechanical budget decision, not a claim that the ledger is irrelevant.

## Why the source-review addenda exist

Phase 2 adds 24 observations through prospective append-only source-review
addenda. They establish what a minimally adequate provider-free fixture looks
like and let us test lineage, view accounting, and budgets. They do not modify
the Phase-1 ledgers.

The addenda are evaluation references, not input answers. The future bounded
reader must not receive protected target descriptions, target evidence, or the
source-review addenda. The checked-in target-blind probe packets enforce this
separation.

## Measured evidence

| measure | result |
| --- | ---: |
| reviewed conversations | 5 |
| bounded process questions per conversation | 5 |
| protected targets | 25 |
| targets with any exact Phase-1 span overlap | 11 |
| targets fully represented by Phase 1 after source review | 1 |
| prospective append-only observations required | 24 |
| provider-free bounded view fixtures | 25 |
| largest fixture-view observation fan-in | 29 of 32 |
| largest fixture-view compact ledger bytes | 8,775 of 24,000 |
| largest target-blind development probe packet | 16,813 of 24,000 bytes |
| longer stress conversation | 24 messages |
| stress post-extraction view fan-in | 32 of 32 observations; 7,851 bytes |
| stress target-blind probe input | 21,307 of 24,000 bytes |
| stress auxiliary-ledger treatment | omitted whole; 0 of 32 included |
| provider, embedding, evaluator, graph, pipeline, runtime calls | 0 |

All 25 views have exact input dispositions. Every omitted item remains
recoverable from its immutable base ledger or append-only manifest. Every
source-review observation is graph-ineligible.

## What Phase 2 proves

- exact source custody, append-only corrections, complete view dispositions,
  and target-blind probe inputs can coexist;
- deterministic overlap must not be treated as semantic coverage;
- the five narrow jobs fit independently within the current development
  budgets;
- a real 24-message conversation fits when the optional auxiliary ledger is
  handled as an all-or-none budget unit;
- the existing Phase-1 ledger is not a sufficient semantic substitute for the
  conversation.

## What Phase 2 does not prove

- that a model can produce the five views reliably;
- that the protected fixtures are independent gold;
- that the auxiliary ledger helps rather than distracts the reader;
- that the 24 KB policy works when the authoritative conversation alone exceeds
  it;
- that any view measures reasoning quality, effort, trust, or correctness;
- that graph or runtime integration is justified.

## Phase 3 decision

Proceed to one bounded development probe. The probe should use one already
reviewed case and at most five model calls, one per semantic job. It must use
the checked-in target-blind packet, never the source-review addendum. Results
must be checked against the protected targets source-first, with `unclear` and
valid empty outputs allowed.

The first five-call development probe should use the frozen target-blind packet
and must not spend the separate repair allowance on an auxiliary-ledger
ablation. If its source-first result leaves anchoring as the material unknown, a
later one-view conversation-only control can be frozen under separate
authorization. That would answer whether the inherited ledger helps the reader
or anchors it to incomplete earlier interpretations without confusing a control
with a prompt repair.

No graph, live skill, final-memo evaluation, or reasoning-quality badge is
authorized by this result.

## Evidence and replay

- coverage contract:
  `docs/evals/reasoning-process-phase2-coverage-contract-v1.json`;
- prospective source review:
  `docs/evals/reasoning-process-phase2-coverage-review-v1.json`;
- builder and validators:
  `engine/system_b/reasoning_process_views.py`;
- replay command:
  `scripts/evals/build_reasoning_process_phase2_views.py`;
- tests:
  `tests/test_reasoning_process_views.py`;
- immutable research artifacts:
  `research/reasoning-process-phase2-views-2026-07-11/`.
