# Context-Engineered Provisional Review Architecture v0

Status: docs/design only
Date: 2026-06-29
Review capacity mode: `codex_assisted_provisional`
Slice: PR79 Context-Engineered Provisional Review Architecture v0

## Purpose

PR79 defines the approved architecture for the Product Delta eval lane after
[Product Delta Evidence Boundary Lint v0](product-delta-evidence-boundary-lint-v0.md).

It does not implement specialist schemas, packet builders, trap fixtures,
Codex-assisted review runs, fan-in reports, model calls, runtime integration,
archive mutation, prompt changes, `SKILL.md` changes, answer-quality scoring,
automatic labels, or `safe_for_agent_use`.

The purpose is to make the next LLM-assisted review phase hard to misread as a
judge, a shadow runtime, a product-proof system, or an approval surface.

## Core Doctrine

Lolla should not replace human judgment with an LLM judge.

The approved direction is:

```text
decompose probabilistic judgment
-> narrow, inspectable specialist reads
-> typed provisional outputs
-> deterministic custody and validation
-> preserved uncertainty and disagreement
-> later human judgment
```

LLMs may help with messy interpretation: conversation shape, likely action,
friction, lost value, interpretation adequacy, and overclaim risk.
Deterministic code must preserve custody: inputs, source references,
missingness, schema validity, privacy boundaries, lint results, non-claims, and
disagreement.

Human reviewers later decide whether a revised answer actually improved the
decision. Specialist reads are scaffolding for that later judgment, not a
substitute for it.

## Runtime And Eval Boundary

The runtime/eval split is load-bearing.

```text
Lolla runtime:
  captures the current conversation
  runs OpenRouter-backed audit lanes
  produces the revised answer
  persists custody artifacts, memo, Observatory, and archive

Product Delta eval lane:
  reads existing safe artifacts later
  packetizes cases
  supports provisional specialist review outside runtime
  validates schemas and non-claims
  preserves disagreement and uncertainty
  prepares later human validation
```

The runtime produces the object of study. The eval lane studies it later.

The Product Delta eval lane must not:

- invoke `$lolla`;
- invoke the Lolla skill;
- run skill setup;
- call `scripts/skill/*`;
- create `/tmp/lolla_*` runtime state;
- call OpenRouter or provider APIs as part of normal validation;
- mutate archive case folders;
- persist revised answers;
- render memos;
- launch Observatory;
- alter `SKILL.md`;
- change runtime prompts;
- change caller behavior;
- feed provisional review outputs back into runtime automatically.

PR79 is an offline architecture note for the eval lane only.

## Rejected Broad Judge

Do not collapse Product Delta review into one broad question.

Rejected prompts include:

- "Did Lolla improve this answer?"
- "Which answer is better?"
- "Score the revised answer."
- "Approve this for agent use."

A broad judge collapses too many tasks into one fluent answer:

- understanding the original conversation;
- inferring the vanilla likely action;
- understanding the Lolla revised answer;
- comparing the delta;
- separating useful friction from caution;
- detecting lost value;
- checking interpretation adequacy;
- enforcing non-claims;
- producing a final verdict.

That is the abstraction Lolla exists to distrust. It is smooth, hard to audit,
easy to overread, and prone to authority leakage.

## Context Engineering Lesson

The architecture should use context engineering rather than broad judge
iteration.

The lesson is architectural, not clinical proof for Lolla:

- broad context plus iterative correction can produce weak first passes;
- correction loops can repair visible defects while introducing new semantic
  errors;
- focused context narrows each probabilistic task;
- typed specialist reads make inputs, outputs, uncertainty, and missingness
  easier to inspect;
- deterministic fan-in can preserve disagreement instead of smoothing it away.

This does not mean every specialist read is correct. It means the review
surface is decomposed enough for deterministic code and later humans to see
where uncertainty entered.

## Approved Architecture

The approved Product Delta specialist-review architecture is:

```text
existing artifacts
-> deterministic packetization
-> focused provisional specialist reads
-> typed outputs
-> deterministic schema validation
-> PR78 evidence-boundary lint
-> disagreement-preserving conservative synthesis
-> later human review
```

Each stage has a different job:

| stage | responsibility | boundary |
|---|---|---|
| Existing artifacts | Provide the archived object of study or checked-in safe summaries. | No new runtime run. |
| Deterministic packetization | Select allowed inputs and record what was included or omitted. | No semantic labels. |
| Focused provisional specialist reads | Interpret one narrow question at a time. | Not judges, not voters. |
| Typed outputs | Preserve status, basis, uncertainty, and source refs. | No scores or approval fields. |
| Schema validation | Check structure and required fields. | Not answer-quality judgment. |
| PR78 lint | Enforce evidence-boundary rules. | Not product proof. |
| Conservative synthesis | Preserve disagreement, missingness, and downgrade pressure. | No majority rule. |
| Later human review | Validate, correct, or reject candidate reads. | Human-owned product judgment. |

## Future Specialist Roles

PR80 defines schemas for these roles. PR79 names the roles and their
boundaries.

### Conversation Interpretation Read

Question:

```text
What did the conversation appear to be about?
```

Future output should identify the decision question, live options, constraints,
stakeholders, values/priorities, assistant influence, dropped threads,
unresolved questions, and uncertainty.

Boundary:

This read does not decide whether the revised answer was useful.

### Vanilla Likely Next-Action Read

Question:

```text
What would the user likely do after the vanilla conversation or final answer?
```

Future output should separate explicit action from reviewer inference and state
how uncertain the inference is.

Boundary:

This read does not inspect the Lolla revised answer.

### Lolla Likely Next-Action Read

Question:

```text
What would the user likely do after the Lolla revised answer?
```

Future output should preserve source basis and uncertainty.

Boundary:

This read does not decide whether the new likely action is better.

### Structural Delta Read

Question:

```text
What structurally changed between the likely actions?
```

Future output should check action, threshold, sequence, evidence gate, stop
rule, written term, scope, overclaim retraction, and user-answerable question.

Boundary:

This read identifies changed structure. It does not score the change.

### Useful/Noisy Friction And Lost-Value Read

Question:

```text
Was the added friction grounded, actionable, and proportionate, and what value
may have been lost?
```

Future output should look for useful friction, noisy friction, missing
friction, momentum loss, courage loss, clarity loss, user-specific ambition
loss, simplicity loss, actionability loss, and useful original advice that may
have weakened.

Boundary:

This read is the skeptic. It must not become a positivity filter.

### Interpretation Adequacy Read

Question:

```text
Did Lolla understand the conversation well enough for the audit to be trusted
as a review object?
```

Future output should look for decision-question drift, option loss, constraint
flattening, stakeholder erasure, value overwrite, transient-emotion hardening,
assistant-influence blindness, false consensus, dropped-thread blindness,
grounding misread, uncertainty collapse, and risk-mode mismatch.

Boundary:

This read does not prove advice quality. It tests reviewability.

### Advisory Overclaim Read

Question:

```text
Did the artifact imply more certainty or authority than the evidence supports?
```

Future output should identify possible claims of human validation, product
proof, judge calibration, answer-quality scoring, automatic labels, agent
approval, clean-artifact authority, or runtime integration.

Boundary:

This read supports PR78-style evidence-boundary protection. It does not judge
the advice.

### Conservative Fan-In Read

Question:

```text
What can be synthesized while preserving disagreement, uncertainty, and
non-claims?
```

Future output should carry conflicts forward, downgrade overconfident reads,
record missingness, and prepare human follow-up questions.

Boundary:

Fan-in must not become majority rule, vote counting, aggregate scoring, or a
"specialists agree" product claim.

## Specialist Non-Authority Rules

Every future specialist output must preserve these rules:

- specialists are not judges;
- specialists are not voters;
- specialist agreement is not correctness;
- specialist disagreement is not failure by itself;
- fan-in must not become majority rule;
- no aggregate score;
- no answer-quality rating;
- no winner;
- no pass/fail verdict;
- no "5 of 7 specialists agree" claim;
- no agent approval;
- no automatic label;
- no `safe_for_agent_use`.

The purpose of decomposition is not to manufacture certainty. It is to make
probabilistic review easier to inspect and easier for humans to correct.

## Input Modes

Future packetization should support two input modes.

### `checked_in_safe_mode`

Use this mode for repo-safe fixtures and docs.

Requirements:

- no raw transcripts;
- no raw revised answers;
- no raw memos;
- no provider text;
- no private reasoning;
- paraphrase-only packets;
- path-safe relative references;
- no local absolute paths;
- no secrets or private content;
- safe for checked-in review fixtures.

This is the default mode for public repo artifacts.

### `local_private_mode`

Use this mode only when explicitly allowed for local review.

Requirements:

- may reference local raw artifacts when the operator explicitly permits it;
- remains read-only;
- records exactly what was read;
- records what was not read;
- keeps archive mutation false;
- keeps runtime invocation false;
- does not copy raw/private content into checked-in outputs;
- emits checked-in summaries only as paraphrase-safe artifacts.

This mode may improve reviewer context, but it does not change the claim level.
Outputs remain provisional until human validation.

## How PR78 Fits

PR78 is the deterministic evidence-boundary seatbelt for this architecture.

Future Product Delta artifacts must pass PR78 lint before they are treated as
review packets. The lint should remain downstream and read-only. It should
continue to block unsafe metadata, authority fields, scoring fields, taxonomy
score drift, missing lower-claim review fields, and privacy markers.

Passing PR78 lint means only:

```text
The checked artifact stayed inside Product Delta evidence-boundary rules.
```

Passing PR78 lint does not mean:

- Lolla improved the decision;
- the revised answer is correct;
- a human validated the case;
- a judge is calibrated;
- the artifact is product proof;
- an agent may act on the answer.

## What PR79 Does Not Prove

PR79 does not prove:

- Lolla improves decisions;
- Codex or any LLM can replace human judgment;
- the PR76 candidate reads are correct;
- a judge has been calibrated;
- the Product Delta eval lane is product proof;
- clean artifacts imply good advice;
- specialist agreement would imply correctness;
- Product Delta review should be integrated into runtime;
- an agent may act on any revised answer.

PR79 is an architecture guardrail. It says how future provisional review should
be decomposed before it is implemented.

## Next PRs

PR80 has now defined the typed Product Delta specialist-review contracts:
[Product Delta Specialist Review Contracts v0](product-delta-specialist-review-contracts-v0.md).

PR81 has now implemented deterministic checked-in-safe packetization for those
contracts:
[Product Delta Specialist Packet Builder v0](product-delta-specialist-packet-builder-v0.md).

PR82 has now added checked-in-safe trap fixtures for future specialist-review
discipline:
[Provisional Reviewer Trap Set v0](provisional-reviewer-trap-set-v0.md).

PR83 has now run the first Codex-assisted specialist-review batch:
[Codex-Assisted Specialist Review Batch v0](codex-assisted-specialist-review-batch-v0.md).

PR84 has now added the fan-in/disagreement report over PR76 and PR83:
[Product Delta Fan-In / Disagreement Report v0](product-delta-fan-in-disagreement-report-v0.md).

Recommended sequence after PR84:

1. **Stop and package PR71-PR84**
   - keep the provisional Product Delta scaffold coherent and reviewable;
   - avoid expanding semantic evidence before human-review routing is clearer.
2. **If continuing, PR85 Cleanup / Packaging Gate v0**
   - check source references, touched-doc alignment, and validation commands;
   - preserve disagreements and uncertainty without scoring or majority rule.

Every future slice should remain downstream/offline, pass PR78 lint where it
emits Product Delta artifacts, and preserve the runtime/eval boundary.
