---
name: audit-lolla-boundaries
description: Audit proposed or implemented changes to Lolla's conversation interpretation, knowledge substrate, graph compiler, pressure planner, Decision Trail, Decision Work sidecars, receipts, or cross-component connections. Use when maintaining this repository, deciding whether a graph opportunity is missing or merely unproven, planning a graph or semantic-supply experiment, checking for parallel systems or external-checkout dependencies, or preparing a PRD/plan without silently changing runtime behavior. Do not use this maintainer skill to run a user-facing Lolla audit.
---

# Audit Lolla Boundaries

Keep one existing product legible while separating what the system preserves,
what an LLM interprets, what the graph traverses, what a receipt proves, and
what only a human can decide.

## Start from current authority

1. Read `AGENTS.md`, `PROJECT_STATUS.md`, `HOW_IT_WORKS.md`, and
   `docs/README.md` in that order.
2. Read the task lane named by `AGENTS.md`. For graph work, always include
   `docs/conversation-understanding/lolla-self-contained-graph-substrate-and-skill-result-2026-07-22.md`
   and `references/knowledge-substrate-operations.md`. For Decision Trail,
   always include
   `docs/conversation-understanding/lolla-decision-trail-stage-lineage-2026-07-22.md`.
3. Read [the evidence-gate reference](references/evidence-gates.md) before
   proposing a new connection, traversal, reader, receipt field, or sidecar.
   For reconsideration or graph-value evaluation, also validate
   `docs/evals/lolla-consumer-context-pressure-ablation-contract-v0.json` so
   same-context self-justification is not confused with upstream graph
   deletion or fresh-context over-absorption.
4. Treat dated experiments as evidence for their named checkpoint, never as
   current authorization.

## Run the audit

### 1. Freeze one question

State one falsifiable question and one allowed causal change. Examples:

- Can a source-first reviewer reconstruct why this model reached pressure?
- Does the current outgoing one-hop policy miss a named useful lens versus a
  no-graph control?
- Does this receipt expose complete bounded path custody without implying
  relevance?
- Does a fixed pressure payload receive materially different treatment in an
  isolated trajectory continuation versus a fresh reconstruction?

Reject bundles such as “add incoming edges, two hops, global search, a graph
database, and a new reader.”

### 2. Map the existing owner

Use `rg` before designing. Identify the current source, compiler, immutable
reader, versioned planner, live caller, ledger, archive, and projection. Mark
each proposed connection as one of:

- live call;
- artifact handoff;
- optional/default-off hook;
- offline evaluator;
- read-only projection;
- absent and unauthorized.

Deepen or reuse the existing owner. Do not create a second compiler, graph
loader, planner, conversation reader, sidecar generator, or skill runtime.

### 3. Separate authority classes

For every field and transformation, label the owner:

- LLM: provisional conversational meaning;
- deterministic code: identity, exact evidence, bounds, traversal, replay,
  budgets, missingness, and ledgers;
- graph: curated relationship hypotheses and bounded reachability;
- reconsidering reasoner: apply, reject, or park;
- human: semantic correction, usefulness, and action authority.

Do not convert deterministic cleanliness into semantic correctness. Preserve
`complete`, `completed_zero`, `partial`, `failed`, and `missing` distinctly.

### 4. Keep evidence vectors separate

Record at least these dimensions independently:

- source and process custody;
- semantic fidelity to the conversation;
- pressure-specific usefulness and forced association;
- answer-level value and lost value;
- privacy, cost, and human correction burden.

Never collapse them into one quality score. Call development fixtures,
maintainer reads, provider output, and principal-human evidence by their exact
evidence class.

### 5. Write into the existing audit trail

Use
`docs/conversation-understanding/lolla-graph-substrate-audit-workbook-2026-07-22.md`
as the current graph/substrate scriptbook. Add a dated prospective section or
create a named result only when the lifecycle changes. Preserve frozen
experiment artifacts and PR104's blank human fields.

Every audit output must say:

- what was inspected;
- what changed and did not change;
- evidence class and exact limitations;
- provider calls and cost;
- the next decision and who owns it.

### 6. Verify proportionately

Run the smallest relevant provider-free checks while iterating, then the
repository checks prescribed by `AGENTS.md` before a handoff. Always run
`git diff --check`, validate changed JSON, inspect `git status`, and confirm no
frozen R4 or PR104 evidence drifted.

## Stop conditions

Stop and return the decision to the founder when work would:

- call a provider or rebuild embeddings;
- inspect private archives or fill principal-human fields;
- change graph direction, hop depth, active/reserve policy, ranking, or live
  receipt claims;
- replace the live same-context host with a fresh consumer or call either mode
  independent judgment;
- connect a candidate reader or sidecar to runtime;
- revive R3/R4, expand Atlas/Teacher, or claim usefulness;
- require a product choice between pressure-now and understand-later.

Offer the smallest frozen contract for that decision. “Continue,” a green
test, or a complete schema is not authorization.
