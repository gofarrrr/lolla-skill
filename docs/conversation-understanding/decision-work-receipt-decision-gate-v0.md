# Decision Work Receipt Decision Gate v0

Status: PR111 docs-only decision gate and phase closure
Date: 2026-06-30

## Decision

Selected outcome: **Outcome A: Receipt shell is enough for now**.

Careful meaning:

> Keep the Decision Work Receipt as a sparse offline work-trail wrapper. Do not
> build a separate Decision Work Receipt interpretation system yet.

PR105 through PR110 show that the receipt is useful for making process evidence
inspectable:

- source/context artifacts;
- raw/private availability and redaction;
- one-shot versus multi-turn process shape;
- visible Lolla challenge surfaces;
- optional Decision Trail and Product Delta references;
- missingness and malformed optional references;
- non-claims and boundary flags.

They do **not** show that the receipt should become a semantic interpreter,
runtime feature, product-facing report, judge, approval badge, or agent action
permission surface.

The Work Receipt should remain the wrapper around the work trail. The messy
semantic interpretation should continue to live in the Decision Trail and
Product Delta lanes, where bounded LLM or later human review can own those
reads under custody.

## Contradicting Evidence First

There is a real argument for Outcome E, bounded specialist interpretation.

PR110 found that the receipt is too thin to explain the story users ultimately
care about:

- what new context mattered;
- which options were explored or abandoned;
- whether the assistant pushed back or merely agreed;
- whether challenge changed a real action, threshold, or evidence gate;
- whether friction was useful or noisy;
- what value was lost;
- whether Lolla improved the decision.

Those are product-important gaps.

But those gaps are not specific to the Decision Work Receipt exporter. They are
the same messy interpretation gaps already identified in the Decision Trail and
Product Delta phases. Building a new Work Receipt specialist lane now would
create a parallel interpretation system and make the architecture harder to
reason about.

So the decision is not:

```text
Never add interpretation.
```

The decision is:

```text
Do not add interpretation inside the Decision Work Receipt lane yet.
Use the receipt as a wrapper over existing and future Decision Trail/Product
Delta interpretation artifacts.
```

## Evidence Considered

PR111 considers the PR105 through PR110 Work Receipt sequence:

| Slice | Evidence | Read |
| --- | --- | --- |
| [PR105 schema](decision-work-receipt-v0.json) | Defines `lolla.decision_work_receipt.v0`. | Good contract for receipt metadata, source inventory, process map, challenge coverage, linked summaries, missingness, non-claims, and boundary. |
| [PR106 source inventory](decision-work-receipt-source-inventory-v0.md) | Read-only checked-in-safe exporter over completed runs. | Useful custody layer; exposes source presence, missingness, redaction/private availability, and attachment/PDF custody gaps. |
| [PR107 process map](decision-work-receipt-conversation-process-map-v0.md) | Deterministic turn-count and capture metadata. | Useful process-shape signal; correctly avoids treating turn count as quality. |
| [PR108 challenge coverage](decision-work-receipt-challenge-coverage-map-v0.md) | Maps visible Lolla challenge surfaces and run-health caveats. | Useful challenge-presence surface; correctly avoids scoring challenge quality. |
| [PR109 exporter](decision-work-receipt-exporter-v0.md) | Composes the sparse receipt and optional Decision Trail/Product Delta refs. | Useful first work-trail shell; optional refs can raise review readiness without validation. |
| [PR110 fixture review](decision-work-receipt-fixture-review-v0.md) | Reviews four safe fixture shapes. | Receipt is useful as a shell, but too thin for the messy semantic story and overtrust-prone if labels are read as approval. |

## What The Receipt Is Good For Now

The Decision Work Receipt is good for internal and maintainer-facing
inspection.

It can answer:

- What artifacts were present?
- What was missing or malformed?
- What raw/private material existed but was not read?
- Does the available metadata look one-shot or multi-turn?
- Were visible Lolla challenge surfaces present?
- Were optional Decision Trail or Product Delta references available?
- Is this only a sparse shell, challenged process evidence, or review-ready
  process evidence?
- What must not be claimed?

That is valuable because it makes the process behind an AI-assisted answer less
invisible.

## What The Receipt Is Not Good For Yet

The receipt is not yet good for product-facing semantic explanation.

It cannot answer:

- What changed in the decision in human terms?
- Which context actually mattered?
- What options were abandoned?
- What did the user lose or preserve?
- Was Lolla's friction useful or noisy?
- Did Lolla improve the answer?

Those require bounded LLM interpretation or later human review. Deterministic
Work Receipt code should not try to solve them.

## Selected Outcome A

The selected path is:

```text
Keep the sparse receipt as a useful internal/workflow artifact.
Do not add Work Receipt runtime integration.
Do not add Work Receipt-specific specialist interpretation yet.
Use Decision Trail and Product Delta artifacts as linked semantic sources when
they exist.
```

This keeps the architecture clean:

- Work Receipt: wraps the work trail and status of artifacts.
- Decision Trail: interprets the answer-plus-process story when bounded
  interpretation exists.
- Product Delta: evaluates the difference between vanilla and Lolla outputs.
- Deterministic code: preserves custody, missingness, statuses, validation, and
  non-claims.
- LLMs/humans: handle messy interpretation.

## Rejected Outcomes

### Outcome B: Improve Runtime Capture

Rejected for now.

PR106 through PR110 expose attachment/PDF and raw/private limitations, but they
do not prove runtime capture must change before the receipt shape is understood.
Runtime capture changes should wait for concrete evidence that a load-bearing
input type repeatedly disappears from completed runs.

### Outcome C: Improve Prompts Or `SKILL.md`

Rejected for now.

PR110 did not show that users are failing to produce enough process evidence
because of skill instructions. The current evidence is fixture-only and cannot
justify prompt or skill changes.

### Outcome D: Improve Deterministic Lane Preparation

Rejected for now.

PR108/PR110 show that challenge surface presence can be represented. They do
not show that audit lanes are missing or mis-preparing inputs. No lane
preparation change is justified by this gate.

### Outcome E: Add Bounded Specialist Interpretation

Rejected inside the Work Receipt lane for now.

Accepted only as a dependency from existing Decision Trail/Product Delta lanes.
If future bounded interpretation exists, the Work Receipt should link it. It
should not become a second semantic interpretation pipeline.

### Outcome F: Simplify

Rejected for now.

PR110 did not show that the receipt is useless bureaucracy. It found the shell
useful for making hidden process state visible. The right simplification is not
to remove the receipt, but to keep it sparse and avoid expanding it into a
parallel product.

## Overtrust Controls

Future users or agents must not read Work Receipt labels as approval.

The risky labels are:

- `multi_turn_unreviewed_process`;
- `challenged_and_revised_process`;
- `decision_trail_review_ready`.

They must remain artifact-state labels only. They do not mean:

- the reasoning was good;
- the challenge was sufficient;
- the revised answer improved;
- the work was human reviewed;
- an agent may act.

Any future UI or agent-facing wrapper must keep these non-claims visible:

- not human validated;
- not product proof;
- not answer-quality scoring;
- not an LLM judge;
- not agent action authorization;
- clean receipt does not imply good advice.

## Work Explicitly Deferred

PR111 does not approve:

- `$lolla` runtime integration for Work Receipts;
- automatic Work Receipt generation inside live runs;
- local-private Work Receipt mode;
- prompt changes;
- `SKILL.md` changes;
- archive mutation;
- attachment/PDF ingestion;
- OCR;
- embeddings, chunking, memory, graph DB, or GraphRAG;
- Work Receipt-specific specialist readers;
- broad conversation-understanding IR;
- dashboards or product UI;
- answer-quality scoring;
- broad LLM judging;
- automatic labels;
- agent action authorization;
- human validation claims.

## What Would Reopen The Lane

The Decision Work Receipt lane should reopen only if future evidence shows a
specific product need:

- repeated missing load-bearing sources that require runtime/archive capture
  changes;
- repeated confusion between missing and private/redacted sources;
- readiness labels causing overtrust in review;
- downstream Decision Trail/Product Delta artifacts becoming hard to locate
  without a receipt wrapper;
- human reviewers asking for a compact work-trail packet across cases;
- product-facing demos needing a receipt that links already-reviewed semantic
  artifacts.

Absent that evidence, keep the receipt as a stable internal artifact.

## Recommended Next Step

Stop the Decision Work Receipt build lane here.

Operationally:

1. Keep PR105 through PR111 as the current Work Receipt package.
2. Do not start PR112 by momentum.
3. Use the receipt on future completed runs as an internal diagnostic.
4. Let Decision Trail/Product Delta work supply semantic interpretation when
   that work is justified.
5. Return to the Work Receipt lane only when a concrete review or product need
   appears.

## Boundary

PR111 is docs-only. It does not:

- run `$lolla`;
- invoke the Lolla skill;
- call providers or models;
- mutate archives;
- change runtime behavior;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- create new semantic reads;
- add an LLM judge;
- score answer quality;
- create automatic labels;
- authorize agent action;
- add graph DB, memory, embeddings, chunking, or GraphRAG.
