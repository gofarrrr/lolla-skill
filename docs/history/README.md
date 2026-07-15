# Historical documentation guidance

Lolla's repository preserves a long design, experiment, and product-discovery
history. That history is evidence. It is not one integrated current product.

Use [PROJECT_STATUS.md](../../PROJECT_STATUS.md) and
[docs/README.md](../README.md) for current truth before reading older material.

## How to read historical files

Treat each file according to its explicit lifecycle:

- an immutable experiment result proves only the recorded experiment;
- a plan records intended work at that time, not current authorization;
- a PRD describes a possible product shape, not reachable behavior;
- a fixture demonstrates a bounded input, not real-user evidence;
- a review records the reviewer and scope it actually covered;
- a successful schema or test proves mechanical shape, not semantic truth;
- an old “next step” is superseded by a later explicit closeout or roadmap.

## Preserved chronology

The previous root README and HOW_IT_WORKS documents accumulated a detailed
chronology of Decision Work, Product Delta, Observatory, R3, R4, and related
experiments. The public-handoff gardening pass replaced those root entrypoints
with current architecture documents because the chronology obscured
reachability and lifecycle status.

No underlying experiment or product document was deleted. Git history at the
Stage 0 merge `fc30bd944bfb91fbff0cc09190487997f3fe3185` preserves the exact
previous root versions. The detailed artifacts remain in `docs/`, `plans/`,
`research/`, `reviews/`, and `tests/fixtures/`.

The exact historical Decision Work and Product Delta titles formerly repeated
through the root documents now have a dedicated
[discoverability registry](decision-work-product-delta-discoverability.md).

## Status precedence

When files conflict, use this order:

1. binding Constitution v5;
2. current `PROJECT_STATUS.md` and Stage 0 addendum;
3. the newest explicit product or experiment closeout for that component;
4. current live contracts (`SKILL.md` and `docs/skill/STEPS.md`);
5. historical plans, PRDs, results, and reviews within their original scope.

Frozen evidence must not be rewritten merely to make its old language look
current. Current indexes should classify it instead.

## Deletion and archival rule

Do not delete, move, normalize, close, or archive a historical artifact merely
because it is old or confusing. First classify it as one of:

- current entrypoint;
- live implementation contract;
- bounded workflow;
- immutable evidence;
- superseded proposal;
- generated artifact;
- fixture/test only;
- genuinely redundant material.

The repository gardening audit records remaining branch, PR, worktree, and
large-artifact debt. Those operations require separate custody decisions.
