# Decision Work Automatic Triage Contract v0

Status: PR154 automatic triage contract

Date: 2026-07-02

Schema: `lolla.decision_work_automatic_triage_contract.v0`

## Purpose

PR154 defines the future automatic triage layer that can sit between
conversation interpretation, enriched Decision Work Brief evidence, and any
user-facing or agent-inspection surface.

The triage layer should decide routing and attention, not correctness. It
should help a later system decide whether a brief is a normal summary
candidate, agent-inspection-only, source-depth-blocked, private-context-bound,
high-overtrust-risk, or domain/human-calibration-needed.

The machine-readable contract is:

- [Decision Work Automatic Triage Contract JSON](decision-work-automatic-triage-contract-v0.json)

PR154 is docs/schema/tests only. It does not build a triage packet builder,
run triage reads, call models, fill human-review answers, or attach anything
to runtime.

## Core Doctrine

LLM interpretation owns messy semantic judgments. Deterministic code owns
custody, source refs, missingness, schema validity, private/redacted
availability, non-claims, and forbidden-authority checks.

Automatic triage may route attention and recommend escalation. It must not
become a score, approval, certification, answer-quality grade, product proof,
or agent action authorization.

Human review is a calibration layer for this automatic triage surface. It is
not the intended normal operating mode for every completed run.

## What Triage Can Answer

The future triage layer should help answer:

- Is this brief a candidate for normal user-facing summary?
- Should this stay agent-inspection-only?
- Is source context too thin?
- Is private context required?
- Is this high-stakes enough to recommend human, domain, legal, or compliance
  review?
- Is the brief likely to create false confidence?
- Does the final answer appear to risk losing important value?
- Does the process look genuinely challenged or merely polished?
- What should a downstream agent inspect first?

These are routing questions. They are not proof that the answer is correct.

## Contract Shape

The contract defines:

- triage metadata;
- input refs;
- conservative custody flags;
- triage scope;
- triage categories;
- triage field groups;
- routing outputs;
- escalation outputs;
- agent-inspection outputs;
- brief-surface outputs;
- human-calibration outputs;
- non-claims.

Every triage field declares an owner, status vocabulary, allowed values, source
ref requirement, uncertainty requirement, privacy handling, user-surface and
agent-inspection handoff flags, runtime-blocking behavior, human/domain review
requirements, and `must_not_be_used_as_quality_label: true`.

## Routing Outputs

Allowed route values are:

- `allowed_with_caveats`
- `agent_only`
- `requires_human_calibration`
- `requires_domain_review`
- `blocked_source_depth`
- `blocked_overtrust_risk`
- `blocked_runtime`
- `not_ready`
- `not_evaluated`

Those values route attention. They do not approve advice or authorize action.

## Human Calibration

PR153 pauses the human-review lane because no real human response exists yet.
PR154 does not undo that pause. Instead, it clarifies the future product model:
human review calibrates the automatic triage layer, while routine operation
should eventually be automatic and custody-preserving.

A later human-review response may teach the triage layer what reviewers find
overtrust-inducing, too thin, too operationally decisive, or useful-but-not-
validated. That calibration still must not become a hidden quality label.

## Explicit Non-Claims

PR154 does not:

- run `$lolla`;
- invoke the Lolla skill;
- call provider or model APIs;
- mutate archives;
- change runtime behavior;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- create a new Lolla run;
- create a new interpretation read;
- create a new builder output;
- create a populated triage example;
- build a triage packet builder;
- fill human review answers;
- claim human validation;
- claim product proof;
- score answer quality;
- create approval or certification labels;
- authorize agent action;
- implement runtime attachment.

## Recommended Next Slice

Recommended next slice:

```text
PR155 Decision Work Automatic Triage Packet Builder v0
```

That slice should build only the deterministic packet/preparation layer for
future LLM triage. It should still avoid model calls, runtime integration,
scoring, approval, product proof, and agent action authorization.
