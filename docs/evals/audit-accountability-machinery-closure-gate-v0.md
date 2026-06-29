# Audit / Accountability Machinery Closure Gate v0

Status: PR70 docs-only decision gate and phase closure
Date: 2026-06-29
Owner: Lolla maintainers

PR70 closes the current audit/accountability machinery phase as done enough
for now.

This does not mean the machinery is complete forever. It means the repo now
has enough deterministic custody, review surfaces, readiness checks, and
accountability shells to stop adding infrastructure by default and ask the
harder product question:

```text
Does Lolla materially improve actual strong-model conversations before action?
```

The next phase is **Product Delta Evidence**.

PR70 is docs-only. It does not run `$lolla`, call models, mutate archives,
change prompts, touch `SKILL.md`, change runtime behavior, add archive
integration, add automatic generation, add labels, add scoring, add a judge, or
start PR71.

## Decision

The audit/accountability machinery lane is closed as done enough for now.

Careful meaning:

- not complete forever;
- not production-proof for every use;
- not agent-autonomous;
- not high-stakes-approved;
- not a judge;
- not answer-quality scoring;
- not automatic labels;
- sufficient as support structure for the next product-eval phase.

The closure decision is:

```text
Stop expanding accountability machinery by default. Use the existing custody
and review surfaces to prove product delta.
```

Future machinery is not banned. It must earn its way back in by answering a
product-evidence need, not by being the next elegant artifact to add.

## Evidence For Closure

The prior lane built or reviewed enough support structure to pause machinery
expansion:

- PR57 implements the read-only Lolla doctor/preflight CLI:
  [Lolla Doctor Read-Only CLI](lolla-doctor-readonly-cli-v0.md).
- PR58 designs the audit decision record:
  [Audit Decision Record v0](../conversation-understanding/audit-decision-record-v0.md).
- PR59 reviews six audit decision record fixtures:
  [Audit Decision Record Fixtures v0](audit-decision-record-fixtures-v0.md).
- PR60 designs the provenance map:
  [Provenance Map v0](../conversation-understanding/provenance-map-v0.md).
- PR61 designs the review conflict register:
  [Review Conflict Register v0](review-conflict-register-v0.md).
- PR62 designs the case graph export/view:
  [Case Graph Export Design v0](../conversation-understanding/case-graph-export-v0.md).
- PR63 creates combined accountability-view fixtures:
  [Accountability View Fixtures v0](accountability-view-fixtures-v0.md).
- PR64 reviews the combined accountability-view fixtures:
  [Accountability View Fixture Review v0](accountability-view-fixture-review-v0.md).
- PR65 chooses the audit decision record exporter as the first implementation:
  [Accountability Implementation Decision Gate v0](accountability-implementation-decision-gate-v0.md).
- PR66 implements the read-only audit decision record exporter:
  [Audit Decision Record Read-Only Exporter v0](audit-decision-record-readonly-exporter-v0.md).
- PR67 smoke-reviews exporter output and finds useful shells but empty-field
  confusion:
  [Audit Decision Record Export Smoke Review v0](audit-decision-record-export-smoke-review-v0.md).
- PR68 refines field population and bucket status:
  [Audit Decision Record Schema / Exporter Refinement v0](audit-decision-record-schema-exporter-refinement-v0.md).
- PR69 re-runs the review and confirms the fix:
  [Audit Decision Record Export Review Re-Run v0](audit-decision-record-export-review-rerun-v0.md).

The PR69 re-run is the closure hinge:

- empty PR31 bucket clarity improves to 7/7 `clear_non_claim`;
- semantic empty-field clarity is 7/7 `clear_non_claim`;
- implementation readiness is 7/7 `ready_for_integration_plan`;
- raw content safety remains 7/7 safe;
- no reviewer needed docs to avoid the basic non-claim misread.

That is enough accountability evidence to stop the machinery lane and use the
machinery for product evidence instead.

## What Is Built

The current built or usable support structure includes:

- core Lolla runtime/archive flow;
- `agent_result.json`;
- `evaluation.json`;
- `reasoning_trace.json`;
- review corpus export and manifest machinery;
- human-review schemas and review artifacts;
- risk-mode caveats and reliance counts;
- user-values/priorities worksheet helper lane as human-owned review support;
- read-only doctor/preflight CLI;
- read-only audit decision record exporter;
- audit decision record review evidence showing clear non-claim behavior.

This is enough for product-eval support. It is not proof that Lolla improves
answers.

## What Is Designed But Deferred

The following remain explicitly deferred:

- provenance map exporter;
- review conflict register exporter or helper;
- case graph exporter/view;
- automatic audit decision record generation inside archives;
- Observatory UI for audit decision records;
- archive integration for audit decision records;
- `conversation_understanding_ir.v0`;
- graph DB;
- embeddings or chunking;
- memory;
- GraphRAG;
- Semantica-style platform work.

These are not deleted ideas. They are deliberately not the next default move.

## What Must Not Be Claimed

The closure decision depends on keeping claims modest:

- clean artifacts do not mean good advice;
- an audit decision record exists does not mean answer quality;
- PR31 bucket presence is not a score;
- empty PR31 buckets are non-claims unless `bucket_status` says otherwise;
- doctor pass/warn status does not approve the advice;
- human review owns improvement judgment;
- agents may inspect metadata but must not treat it as permission to act;
- accountability artifacts are custody and review aids, not domain authority.

## Why We Are Pivoting

The next product question is not:

```text
Can we create more accountability artifacts?
```

The next product question is:

```text
Does Lolla materially improve actual strong-model conversations before action?
```

Accountability machinery can now support that question. It should not postpone
that question.

## Product Delta Evidence North Star

The north-star question for the next phase is:

```text
Did Lolla change what a serious person would do next, in a way a human reviewer
can explain, without confusing caution, structure, or artifact cleanliness for
truth?
```

This question keeps Lolla honest. It asks for decision usefulness, not merely
more polished artifacts.

## First Baseline

The first baseline is the actual vanilla conversation:

- user talks to Codex, Claude, or the best available model;
- model gives a plausible answer;
- user is about to act.

This is the real workflow Lolla is trying to improve.

Cheap controls matter later. The first proof should compare Lolla against the
real vanilla workflow, because that is where users decide whether Lolla is
worth the interruption.

## First Wedge

The first eval wedge should be founder/operator strategic decisions.

Reasons:

- the existing corpus already fits;
- deltas are concrete;
- stakes are real without making domain-authority claims;
- action, threshold, sequence, and gate changes are legible;
- reviewers can explain whether friction changed the next move.

This wedge is narrow enough to review honestly and close enough to Lolla's
current evidence base to avoid inventing a broad benchmark too early.

## Improvement Definition

Lolla improvement is not:

- longer prose;
- more cautious prose;
- more balanced prose;
- more comprehensive prose;
- more artifact-rich output;
- more judge-friendly output;
- more responsible-sounding output.

Lolla improvement is:

- more decision-leveraged;
- more assumption-aware;
- more bounded or reversible where needed;
- more protective of real constraints and stakeholders;
- less seduced by status, fluency, user pressure, or false certainty;
- still actionable.

The next phase should reward useful changes to decisions, not merely better
documentation around the same decision.

## Decision Leverage Concept

The next phase should introduce `decision_leverage` as a core review concept.

Working vocabulary:

- `structural_delta`: an action, threshold, sequence, gate, stop rule, written
  term, scope, overclaim, or user question changed.
- `decision_leverage`: the change would plausibly alter what the user does,
  delays, asks, refuses, narrows, or monitors.
- `lost_value`: what the revision made weaker, less courageous, less clear, or
  less useful.
- `net_decision_read`: `material_improvement`, `partial`, `no_change`,
  `worse`, or `inconclusive`.

PR31 labels are not a score. One decisive gate can matter more than five
low-leverage deltas. Product Delta Evidence should review leverage, not count
labels.

## Eval Phase Questions

PR71 and later should answer:

- What would the user do differently after Lolla?
- Is that difference justified?
- What did Lolla add?
- What did Lolla lose?
- Was the friction useful or noisy?
- Did Lolla preserve courage and action where action was warranted?
- Did Lolla become a hesitation machine?
- Did the reviewer need artifacts to understand the improvement?
- Could a cheap second-pass checklist get most of the same value?

These are product questions. They are not machinery questions.

## Next Recommended PR Sequence

Recommended next phase:

```text
Product Delta Evidence
```

Suggested sequence:

1. PR71 Product Delta Evidence Thesis v0
   - docs/design;
   - define the eval claim, improvement definition, `decision_leverage`,
     `lost_value`, useful/noisy friction, and non-claims.

2. PR72 Vanilla-vs-Lolla Pair Review Protocol v0
   - docs/JSON schema;
   - compare actual vanilla conversation answer against Lolla revised answer;
   - include likely action after vanilla, likely action after Lolla, material
     difference, `decision_leverage`, `lost_value`, useful friction, noisy
     friction, and `net_decision_read`.

3. PR73 Cheap Control / Trap Fixture Design v0
   - docs/JSON fixtures;
   - define simple second-pass controls and realistic traps: longer but not
     better, more cautious but lower leverage, second-draft improvement without
     Lolla, over-caution, status/prestige seduction, stakeholder flattening,
     and user-pressure sycophancy.

4. PR74 Paired Human Review Seed Batch v0
   - human-review/data;
   - review 15-20 vanilla-vs-Lolla pairs in founder/operator strategic
     decisions.

5. PR75 Eval Failure Taxonomy v0
   - docs/JSON;
   - classify how Lolla fails: no-op prose, caveat bloat, false precision,
     overcorrection, values overwrite, stakeholder flattening, diligence
     theater, hesitation machine, and artifact authority leak.

6. PR76 Product Eval Report v0
   - docs/report;
   - summarize wins, losses, caveats, examples, and failure modes without fake
     scoring.

7. PR77 User-Facing Demo Pack v0
   - docs/demo;
   - show concrete before/after decision moments and what Lolla changed.

Do not start PR71 from PR70. PR70 closes the current phase and stops.

## Product Delta Evidence Stop Rule

The next phase is done enough for a first user presentation when:

- product eval thesis exists;
- pair protocol exists;
- 15-20 pair seed is reviewed;
- failure taxonomy exists;
- at least 3 demo-ready improvement examples exist;
- at least 1 documented non-helpful or worse case exists;
- no judge, answer-quality score, automatic labeler, or automatic agent
  reliance has been added;
- user-facing report explains what Lolla can and cannot claim.

This stop rule keeps the next phase from becoming another infrastructure
ladder.

## Explicit Non-Build List

We are willing not to build now:

- no dashboard unless a Markdown report is insufficient;
- no judge;
- no automatic labels;
- no automatic audit decision record generation;
- no case graph implementation;
- no graph DB;
- no memory;
- no broad benchmark;
- no high-stakes domain authority product claim;
- no "Lolla improves AI answers" general claim.

## Final Gate

PR70's final gate is:

```text
The next approved work should prove product delta. It should not add another
accountability artifact unless the product-delta review shows that the existing
machinery cannot answer the question.
```

Stop after PR70. Do not start PR71.
