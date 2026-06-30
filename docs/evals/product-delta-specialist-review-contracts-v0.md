# Product Delta Specialist Review Contracts v0

Status: docs/schema
Date: 2026-06-29
Review capacity mode: `codex_assisted_provisional`
Slice: PR80 Product Delta Specialist Review Contracts v0

## Purpose

PR80 defines typed contracts for the specialist-review architecture introduced
in [Context-Engineered Provisional Review Architecture v0](context-engineered-provisional-review-architecture-v0.md).

The companion schema is:

```text
docs/evals/product-delta-specialist-review-contracts-v0.json
```

These contracts are not a review run. They do not fill any case, call any
model, create a packet builder, create trap fixtures, synthesize fan-in, mutate
archives, change runtime behavior, change prompts, touch `SKILL.md`, add
answer-quality scoring, infer automatic labels, or authorize agent action.

PR80 exists so Product Delta specialist outputs have a narrow typed shape.
PR81 packetization uses that shape. PR82 now adds trap fixtures for testing
future specialist-review discipline; PR83 role-pass review and PR84 fan-in work
remain later slices.

## Doctrine

Lolla should not replace human judgment with an LLM judge.

The Product Delta eval lane should decompose probabilistic judgment into
bounded, inspectable specialist reads, then use deterministic custody to
preserve:

- source references;
- input mode;
- missingness;
- uncertainty;
- disagreement;
- privacy boundaries;
- lower-claim metadata;
- non-claims.

The contracts make future LLM-assisted review easier to inspect. They do not
make it authoritative.

## Runtime Boundary

The runtime/eval split remains unchanged.

```text
Lolla runtime:
  captures current conversation
  runs OpenRouter-backed audit lanes
  produces revised answer
  persists custody artifacts, memo, Observatory, archive

Product Delta eval lane:
  reads existing safe artifacts later
  packetizes cases
  supports provisional specialist review outside runtime
  validates schemas and non-claims
  preserves disagreement and uncertainty
  prepares later human validation
```

The runtime produces the object of study. The eval lane studies it later.

The Product Delta eval lane must not invoke `$lolla`, invoke the Lolla skill,
run skill setup, call `scripts/skill/*`, create `/tmp/lolla_*` runtime state,
call providers as part of normal validation, mutate archives, persist revised
answers, render memos, launch Observatory, alter `SKILL.md`, change prompts,
change caller behavior, or feed provisional outputs back into runtime
automatically.

## Why Not A Broad Judge

PR80 rejects one broad review prompt such as:

- "Did Lolla improve this answer?"
- "Which answer is better?"
- "Score the revised answer."
- "Authorize this for agent action."

Those questions collapse conversation interpretation, likely action,
structural delta, useful friction, noisy friction, lost value, interpretation
adequacy, and overclaim boundaries into one fluent answer.

The specialist contracts keep those jobs separate.

## Contract Family

The schema root uses:

```text
lolla.product_delta_specialist_review_contracts.v0
```

Top-level fields include:

- `schema_version`
- `contract_family`
- `mode`
- `case_id`
- `artifact_refs`
- `input_custody`
- `review_status`
- `specialist_reads`
- `boundary`
- `non_claims`

The root shape is for a future specialist-review packet. PR80 defines that
shape but does not create any packet instances.

## Shared Status Vocabulary

Field/source status is qualitative:

- `explicit`
- `inferred`
- `unclear`
- `not_supplied`
- `contradicted`
- `unavailable_missing_artifact`
- `unavailable_malformed_artifact`
- `not_reviewed`

Evidence strength is qualitative:

- `low`
- `medium`
- `high`
- `unclear`

Read status is provisional:

- `not_run`
- `provisional_candidate`
- `blocked_thin_context`
- `blocked_missing_artifact`
- `blocked_private_content_only`
- `inconclusive`
- `needs_human_review`

None of these values is numeric, final, or human-validated.

## Specialist Reads

### Conversation Interpretation

Purpose:

```text
Check whether Product Delta review has enough understanding of the original
conversation to reason about the delta.
```

The contract covers decision question, live options, option status,
constraints, stakeholders, values or priorities, assistant influence, dropped
threads, unresolved questions, uncertainty notes, source refs, field status,
and what would make the read wrong.

This is not a full conversation-understanding IR. It is scoped to what Product
Delta review needs before comparing vanilla and revised answers.

### Vanilla Likely Next Action

Purpose:

```text
Infer, provisionally, what the user was likely to do after the vanilla answer.
```

The contract covers likely next action, source status, explicit versus inferred
status, uncertainty notes, source refs, alternative plausible actions, and what
would make the read wrong.

It must not claim to know what the user truly would have done.

### Lolla Likely Next Action

Purpose:

```text
Infer, provisionally, what the revised Lolla answer would likely lead the user
to do.
```

The contract mirrors the vanilla likely-action read.

It must not claim the revised likely action is better.

### Structural Delta

Purpose:

```text
Identify what structurally changed between vanilla and revised answers.
```

The contract covers candidate changes in action, threshold, sequence, evidence
gate, stop rule, scope, stakeholder treatment, user-answerable question,
overclaim retraction, and reversibility or bounding.

Each field carries status, description, source refs, and uncertainty notes.
Counts of changed fields are not a score.

### Useful/Noisy Friction And Lost Value

Purpose:

```text
Separate productive audit pressure from friction that merely adds process,
caution, or hesitation.
```

The contract covers useful friction, noisy friction, lost value,
overcorrection risk, momentum or simplicity loss, generic prudence
substitution, decision burden added, uncertainty notes, source refs, and what
would make the read wrong.

Lost value is required even when a future net read is positive.

### Interpretation Adequacy

Purpose:

```text
Identify whether Lolla may have misunderstood the conversation in a way that
weakens downstream review.
```

The contract covers decision-question drift, option loss, constraint
flattening, stakeholder erasure, value overwrite, transient-emotion hardening,
assistant-influence blindness, false consensus, dropped-thread blindness,
quote or grounding misread, uncertainty collapse, risk-mode mismatch, and
overall interpretation adequacy.

Allowed overall values remain provisional:

- `adequate_candidate`
- `partly_adequate_candidate`
- `unclear`
- `inadequate_candidate`
- `not_reviewed`

### Advisory Overclaim

Purpose:

```text
Flag prose that may sound more certain than the metadata supports.
```

This read is advisory only. Blocking enforcement belongs to
[Product Delta Evidence Boundary Lint v0](product-delta-evidence-boundary-lint-v0.md).

The contract requires:

- `advisory_only: true`
- `requires_pr78_lint: true`

It may identify overclaim risks, language to soften, and missing non-claims.
It must not become a semantic judge.

### Conservative Fan-In

Purpose:

```text
Preserve specialist disagreement without voting.
```

The contract covers specialist agreements, specialist disagreements,
downgraded fields, high-uncertainty fields, human-review priorities,
provisional net decision read, why the read is not stronger, what would change
the read, and non-claims.

Allowed `net_decision_read_candidate` values are:

- `material_improvement_candidate`
- `partial_improvement_candidate`
- `no_material_change_candidate`
- `lolla_added_noise_candidate`
- `lolla_worse_candidate`
- `inconclusive`
- `not_reviewed`

Fan-in must not become majority rule, aggregate confidence, specialist
consensus as correctness, or a "5 of 7 specialists agree" claim.

## Input Modes

### `checked_in_safe_mode`

Use this mode for repo-safe docs and fixtures.

Requirements:

- no raw transcripts;
- no raw revised answers;
- no raw memos;
- no provider text;
- no private reasoning;
- paraphrase-only packets;
- path-safe relative refs;
- no local absolute paths;
- no private content copied into checked-in outputs.

### `local_private_mode`

Use this mode only when explicitly allowed for local review.

Requirements:

- may reference local raw artifacts when explicitly allowed;
- remains read-only;
- records exactly what was read;
- records what was not read;
- does not copy raw/private content into checked-in outputs;
- keeps archive mutation false;
- keeps runtime invocation false.

Local private mode may improve context. It does not change the claim level.

## Boundary Metadata

Every future packet using these contracts must preserve:

- `human_validated: false`
- `ground_truth: false`
- `judge_calibration_eligible: false`
- `product_proof: false`
- `answer_quality_scored: false`
- `agent_action_authorized: false`
- `model_calls: 0`
- `archive_mutated: false`
- `runtime_invoked: false`
- `skill_invoked: false`
- `raw_private_content_included: false`
- `automatic_labels_created: false`

The schema intentionally avoids approval fields, winner fields, numeric
answer-quality fields, and pass/fail verdicts.

## Non-Claims

The contract family preserves these non-claims:

- not human validation;
- not ground truth;
- not judge calibration;
- not product proof;
- not answer-quality scoring;
- not agent permission;
- not runtime integration;
- not an automatic labeler.

## PR78 Lint

PR80 contract docs and schema must pass PR78 lint.

Passing lint means only:

```text
The artifact stayed inside Product Delta evidence-boundary rules.
```

Passing lint does not mean a future read is correct, a human validated it, a
judge is calibrated, a revised answer is better, or an agent may act.

## What PR80 Enables

PR80 enabled PR81 to build a read-only specialist packet builder against typed
contracts:
[Product Delta Specialist Packet Builder v0](product-delta-specialist-packet-builder-v0.md).

It also gives PR82 trap fixtures a stable schema target:
[Provisional Reviewer Trap Set v0](provisional-reviewer-trap-set-v0.md).

PR83 has now used the contracts for the first Codex-assisted specialist-review
batch:
[Codex-Assisted Specialist Review Batch v0](codex-assisted-specialist-review-batch-v0.md).

PR84 disagreement-preserving fan-in remains a later slice.

## What PR80 Does Not Prove

PR80 does not prove:

- Lolla changes decisions usefully;
- any Codex-assisted read is correct;
- specialist agreement implies correctness;
- the PR76 candidate distribution is representative;
- a broad judge is calibrated;
- Product Delta eval should enter runtime;
- any case is product proof;
- any agent may act.

PR80 is a contract layer, not evidence that the contracts have been filled well.
