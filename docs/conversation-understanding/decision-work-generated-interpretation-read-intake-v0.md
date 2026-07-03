# Decision Work Generated Interpretation Read Intake v0

Status: PR182 intake / validation gate
Date: 2026-07-03
Schema: `lolla.decision_work_generated_interpretation_read_intake.v0`

## Purpose

PR182 adds the first validation gate after a future operator or Codex session
produces a candidate Decision Work conversation interpretation read.

It accepts an externally supplied JSON read and emits a structured intake
result that says whether the read is:

- accepted for later offline downstream use;
- rejected for a hard blocker;
- unsupported because the schema is not known;
- or requires operator repair before it can feed later steps.

This is not an interpreter. It does not generate a read, rewrite a read, call a
provider, render a Decision Work Brief, enrich a brief, create triage, update
resolver-approved refs, update runtime sidecars, mutate archives, score advice,
or authorize action.

## Where It Fits

The automatic semantic supply path remains:

```text
completed archive
-> deterministic packet
-> offline interpretation queue
-> bounded operator/Codex interpretation read
-> generated-read intake validation
-> Decision Work Brief render
-> enrichment
-> triage read
-> resolver-approved refs
-> runtime sidecar update or deferred/blocked state
```

PR182 implements only the `generated-read intake validation` step.

## What The Validator Reads

The CLI reads:

- a candidate interpretation read JSON;
- optionally, the queue item that led to the read;
- optionally, the operator/Codex prompt packet used to shape the read.

Supported read schema names:

- `lolla.decision_work_conversation_interpretation_read.v0`;
- `lolla.decision_work_conversation_interpretation_tiny_offline_read.v0`;
- `lolla.decision_work_conversation_interpretation_second_tiny_offline_read.v0`.

The two tiny-read schema names are accepted as legacy-compatible wrappers
because the checked-in PR131 and PR132 reads use them while preserving the same
field, custody, source-ref, uncertainty, and non-claim pattern that PR133 later
formalized.

## What The Validator Checks

The validator checks deterministic safety and structure:

- supported schema/version;
- required top-level read fields;
- interpreted field shape;
- source refs on interpreted fields;
- uncertainty on interpreted fields;
- privacy limits and source limitations;
- conservative custody flags;
- non-claims;
- absence of local absolute paths;
- absence of raw/private markers;
- absence of product-proof, human-validation, quality-label, correctness, and
  action-authorization claims.

It does not try to prove that the interpretation is semantically true.

## Intake Result Shape

Result schema:

```text
lolla.decision_work_generated_interpretation_read_intake.v0
```

Top-level result fields include:

- `schema_version`;
- `intake_metadata`;
- `source_read_ref`;
- `source_queue_item_ref`;
- `source_prompt_packet_ref`;
- `read_schema_detected`;
- `intake_status`;
- `blocker_reasons`;
- `repair_required`;
- `accepted_for_downstream`;
- `downstream_allowed`;
- `field_validation_summary`;
- `source_ref_validation`;
- `uncertainty_validation`;
- `privacy_validation`;
- `custody_validation`;
- `non_claim_validation`;
- `semantic_limits`;
- `output_refs`;
- `non_claims`.

## Intake Statuses

The current validator can emit:

- `accepted`;
- `rejected_schema_invalid`;
- `rejected_missing_source_refs`;
- `rejected_missing_uncertainty`;
- `rejected_privacy_risk`;
- `rejected_authority_claim`;
- `rejected_quality_label`;
- `rejected_action_authorization`;
- `rejected_human_validation_claim`;
- `rejected_product_proof_claim`;
- `rejected_local_absolute_path`;
- `requires_operator_repair`;
- `unsupported_schema`.

Acceptance means only that the read can be considered by later offline steps.
It is not direct runtime approval.

## Downstream Boundary

When a read is accepted, PR182 may set these later offline affordances to true:

- `can_feed_brief`;
- `can_feed_enrichment`;
- `can_feed_triage_packet`;
- `can_feed_resolver`.

In PR182 these remain false for every result:

- `can_update_sidecar`;
- `can_authorize_agent_action`;
- `can_be_used_as_quality_label`.

That distinction matters. A read can be structurally eligible for later offline
brief generation without being safe for runtime sidecar update or agent action.

## CLI

Example:

```bash
python3 scripts/evals/validate_decision_work_generated_interpretation_read.py \
  --read reviews/codex-assisted/decision-work-conversation-interpretation-third-tiny-offline-read-v0/read.json \
  --out /tmp/decision_work_generated_read_intake.json \
  --pretty
```

Optional refs:

```bash
python3 scripts/evals/validate_decision_work_generated_interpretation_read.py \
  --read <candidate-read-json> \
  --queue-item <queue-item-json> \
  --prompt-packet docs/conversation-understanding/decision-work-operator-codex-interpretation-prompt-packet-v0.json \
  --out /tmp/decision_work_generated_read_intake.json \
  --pretty
```

The CLI writes a JSON intake result for accepted and rejected reads. It exits
nonzero only for mechanical input/output errors, not merely because a candidate
read is rejected.

## Compatibility Fixtures

PR182 validates the three existing checked-in reads:

- launch-public-enterprise-beta;
- deploy-assisted-intake-routing;
- ceo-remove-founding-cofounder.

These are compatibility fixtures, not proof that future generated reads will be
good. They demonstrate that the validator accepts the existing safe source-ref,
uncertainty, custody, and non-claim pattern.

## What This Does Not Do

PR182 does not:

- run `$lolla`;
- invoke the Lolla skill;
- call provider or model APIs;
- create a new Lolla run;
- mutate archives;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- generate an interpretation read;
- modify an interpretation read;
- render a Decision Work Brief;
- enrich a brief;
- generate triage;
- update resolver-approved refs;
- update runtime sidecars;
- make runtime attachment default-on;
- claim product proof;
- claim human validation;
- score answer quality;
- claim advice correctness;
- prove Lolla improved the decision;
- authorize agent action;
- authorize automatic action.

## Decision Gate

Selected next step:

```text
proceed_to_three_case_generated_read_intake_review
```

Recommended next PR:

```text
PR183 Three-Case Generated Interpretation Read Intake Review v0
```

Reason:

PR182 now validates existing and synthetic candidate reads, but it does not yet
review the intake behavior across the three cases as a product surface. PR183
should inspect accepted and rejected intake results before any regeneration
pilot, queue-to-brief path, or sidecar update path is attempted.

PR183 is now implemented as:

- [Decision Work Generated Interpretation Read Intake Review](decision-work-generated-interpretation-read-intake-review-v0.md)

It confirms the PR182 validator boundary over the three existing reads and
temporary synthetic rejection cases, then selects one bounded operator/Codex
generated-read pilot as the next safe slice.

PR184 is now implemented as:

- [Decision Work Operator/Codex Generated Read Pilot](decision-work-operator-codex-generated-read-pilot-v0.md)

It creates exactly one checked-in-safe launch-beta generated-read candidate and
validates it through this PR182 intake path. The intake result is accepted for
later offline planning only: it still cannot update runtime sidecars, authorize
agent action, or be used as a quality label.
