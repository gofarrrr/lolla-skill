# Lolla R4 product and architecture closeout plan

Date: 2026-07-14

Status: complete provider-free closeout

Canonical starting commit:
`34d0e1a8f6e80d72622deb59b10a81262344fc85`

## Goal

Close the incremental R4 conversation-reader program after the canonical A2
result, state which product and architecture components survive, remove stale
handoff instructions, and leave one cold-start path for the next developer.

The closeout answers one question:

> Given that paired and separated residual tasks both produced unsafe semantic
> companions, what should Lolla preserve, stop, and investigate next without
> confusing that reader failure with the rest of the product?

## Binding inputs

Read in this order:

1. `docs/conversation-understanding/lolla-product-constitution-v5.md`;
2. `docs/conversation-understanding/lolla-current-state-constitutional-audit-2026-07-13.md`;
3. `plans/lolla-post-v1-constitution-aligned-roadmap-2026-07-13.md`;
4. `docs/conversation-understanding/lolla-r4-separated-surface-execution-a2-result-2026-07-14.md`;
5. `docs/board/decision-work-sidecar-internal-v1-current-state.md`;
6. `docs/conversation-understanding/decision-work-conversation-interpretation-contract-v0.md`;
7. the live capture, pipeline, graph-survival, sidecar, and Observatory
   entrypoints named in the result note.

## Scope

This goal may:

- inspect current code and documentation read-only;
- distinguish authoritative source, live pressure, experimental readers,
  Decision Work sidecar, Observatory, and future Teacher responsibilities;
- make a provider-free product and architecture decision;
- add a closeout result note;
- update `AGENTS.md`, the roadmap, README status, `HOW_IT_WORKS.md`, and the eval
  index so they point to the same current boundary;
- run provider-free documentation, link, syntax, and repository tests.

This goal may not:

- call a provider or create an execution authorization;
- change prompts, schemas, models, routes, seeds, runners, or frozen evidence;
- retry A1, A2, or any earlier R4 call;
- integrate an R4 reader into runtime or graph behavior;
- change the live relationship reader, reconsiderer, or sidecar behavior;
- build a replacement semantic reader;
- start R5, a model comparison, or a real-user usefulness claim;
- collapse the evidence into a scalar score;
- publish, push, open a pull request, or merge without a separate decision.

## Method

1. Reproduce the canonical A2 and publication boundary from Git history and
   existing evidence.
2. Trace the actual live path from full prose capture through
   `ConversationContext`, `ConversationIR`, the four lanes, graph survival,
   reconsideration, archive, optional Decision Work sidecar, and Observatory.
3. Prove that the R4 residual/separated readers are research modules and were
   not integrated into that live path.
4. Separate mechanical operation from product evidence: a path can run without
   having established unique user value.
5. Select one architecture decision and record its consequences and
   non-claims.
6. Replace stale A1/publication handoffs with the canonical A2/closeout state.
7. Define exactly one next provider-free goal.

## Completion conditions

The goal is complete when:

- one closeout decision is explicit;
- full-conversation custody and long-context processing limits are explicit;
- the live mental-model pressure path is distinguished from R4;
- the Decision Work sidecar is described as derivative, optional, and
  semantically incomplete rather than as a second runtime;
- every major component has a keep, stop, defer, or research-only disposition;
- the next goal is singular and provider-free;
- current entrypoints no longer instruct a developer to publish or resume A1;
- frozen evidence remains byte-identical;
- provider calls and cost remain zero.

## Verification

Run:

```bash
git diff --check
PYTHONPATH=. python3 scripts/evals/seal_r4_separated_surface_execution_a2.py --validate-only
PYTHONPATH=. python3 scripts/evals/finalize_r4_separated_surface_execution_a2.py --validate-only
PYTHONPATH=. pytest -q tests/test_r4_separated_surface_execution_a2.py
PYTHONPATH=. pytest -q
```

Also verify:

- all changed Markdown links resolve locally;
- no frozen source, prior, target, prompt, request, response, contract, runner,
  or execution artifact changed;
- the worktree contains documentation-only changes;
- no provider transport or authorization artifact exists.
