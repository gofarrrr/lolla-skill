# Decision Work Brief Expansion / Runtime Attachment Decision Gate v0

Status: PR126 expansion/runtime decision gate
Date: 2026-07-01
Schema: `lolla.decision_work_brief_expansion_runtime_decision_gate.v0`

## Purpose

PR126 follows the PR125 gate:

```text
proceed_to_expansion_or_runtime_decision_gate
```

It decides the next phase after:

- PR124 found the plain-language brief surface readable enough for
  local-private comparison;
- PR125 completed one launch-beta local-private shadow review and found the
  checked-in-safe brief adequate but still missing private nuance;
- PR122 found a three-case action-consequence pattern.

PR126 is a decision gate only. It does not implement runtime integration,
create new briefs, add a batch, patch the renderer, or run Lolla.

The durable review artifact is:

- [`review.json`](../../reviews/codex-assisted/decision-work-brief-expansion-runtime-decision-gate-v0/review.json)

## Evidence Inputs

PR126 uses these prior artifacts:

- [Decision Work Brief Plain-Language Re-Review v0](decision-work-brief-plain-language-rereview-v0.md)
- [Decision Work Brief Local-Private Adequacy Check v0](decision-work-brief-local-private-adequacy-check-v0.md)
- [Decision Work Brief Three-Case Pattern Review v0](decision-work-brief-three-case-pattern-review-v0.md)

The combined read is:

- readability is good enough for continued review;
- the three checked-in-safe examples consistently name action consequence;
- one local-private check did not undermine the launch-beta brief;
- source-depth and overclaim risk remain material.

## Decision

PR126 selects:

```text
run_more_local_private_adequacy_checks
```

This is deliberately narrower than runtime attachment.

The next phase should compare more existing rendered briefs against
local-private completed-run context before broadening checked-in-safe volume or
planning runtime attachment.

## Why Not Runtime Attachment Yet

Runtime attachment is still premature because the Decision Work Brief lane is:

- offline and downstream;
- Codex-assisted;
- non-human-validated;
- not product proof;
- not answer-quality measurement;
- source-depth-limited;
- tested against local-private context in only one case.

The brief now reads better, and the first local-private check is encouraging.
But integrating it into the live runtime would make it look more official than
the evidence supports.

## What Should Happen Next

Recommended next slice:

```text
PR127 Decision Work Brief Conversation Interpretation Gap Map v0
```

The next slice reframes the source-depth question before running more checks:
which conversation interpretation fields are already present, which are only
available privately, which require LLM or human interpretation, and which are
not captured at all.

That gap map should still treat richer local/private context as read-only and
check in only safe conclusions. It should test whether the brief lane needs an
explicit future contract before more adequacy work tries to compare:

- the decision read;
- the starting-direction read;
- what Lolla pressed on;
- the action consequence read;
- lost value or possible overcorrection;
- overclaim risk.

It should still not implement runtime behavior.

## Boundary

PR126 does not:

- run `$lolla`;
- invoke the Lolla skill;
- call providers or model APIs from repo code;
- mutate archives;
- change runtime behavior;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- add model-call code;
- add a broad judge;
- measure answer quality;
- create automatic labels;
- authorize agent action;
- claim product proof;
- add graph, memory, embedding, chunking, or GraphRAG work;
- integrate the brief into runtime;
- create a dashboard;
- create new cases;
- create a five-case batch;
- patch the renderer.

## Non-Claims

PR126 is not:

- human review;
- product proof;
- answer-quality measurement;
- automatic labeling;
- runtime integration;
- agent action authorization;
- proof that clean artifacts mean good advice;
- proof that one local-private check generalizes;
- approval to attach Decision Work Briefs to live runs.
