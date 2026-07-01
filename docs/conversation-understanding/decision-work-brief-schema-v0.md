# Decision Work Brief Schema v0

Status: PR114 schema contract
Date: 2026-07-01
Schema: `lolla.decision_work_brief.v0`

## Purpose

The Decision Work Brief is the user-facing layer above the current custody and
debug artifacts.

It should answer the reader's practical question:

> What did this process make me see or do differently?

The brief is not an artifact inventory. It explains the decision, the likely
starting direction, what Lolla pressed on, what changed, what action consequence
follows, what still might be wrong, and what the audit must not claim.

The machine-readable contract is:

- [Decision Work Brief Schema JSON](decision-work-brief-v0.json)

This PR defines the schema only. It does not add a generator, packet builder,
Markdown renderer, runtime integration, model call, or populated checked-in
brief.

## Layering

The intended stack is:

```text
Revised answer
-> Decision Work Brief
-> Evidence Receipt
-> Local private archive
```

The brief tells the decision story. The Evidence Receipt backs the story with
custody, source status, missingness, redaction/private availability, linked
reports, and non-claims.

The current receipt and debug summary remain internal or maintainer-facing:

- [Decision Work Receipt Schema](decision-work-receipt-v0.json)
- [Decision Work Receipt Exporter](decision-work-receipt-exporter-v0.md)
- [Decision Work Receipt Debug Summary](decision-work-receipt-debug-summary-v0.md)

The Decision Trail remains the answer-plus-process report shell that can supply
supporting structured or interpreted evidence when available:

- [Decision Trail Report Schema](decision-trail-report-v0.json)
- [Decision Trail Report PRD](decision-trail-report-prd-v0.md)

## Contract Shape

The required top-level fields are:

- `schema_version`
- `brief_metadata`
- `mode`
- `source_refs`
- `custody_flags`
- `sections`
- `non_claims`

The schema version is fixed:

```text
lolla.decision_work_brief.v0
```

The allowed modes are:

- `checked_in_safe_mode`
- `local_private_mode`
- `future_runtime_mode_not_implemented`

`checked_in_safe_mode` is suitable for committed contracts and tests. It must
not include raw transcript text, raw revised-answer text, raw memo text,
provider text, private reasoning, secrets, local absolute paths, or private
archive content.

`local_private_mode` is future vocabulary for operator-controlled local work. It
may let a later packet or interpretation step read private context locally, but
the brief contract still records whether private content was included. Checked
in artifacts must remain safe.

`future_runtime_mode_not_implemented` is reserved vocabulary only. It does not
mean the live skill produces Decision Work Briefs today.

## Required Sections

The `sections` object requires these semantic sections:

- `decision`
- `starting_direction`
- `what_lolla_pressed_on`
- `what_changed`
- `what_this_means_for_action`
- `what_still_might_be_wrong`
- `what_was_not_proven`
- `evidence_receipt`

Each section uses the same structure:

- `status`
- `source_status`
- `source_refs`
- `interpreted_by`
- `human_validated`
- `uncertainty`
- `value`
- `empty_meaning`

This is deliberate. A populated sentence is not enough. The brief must say where
the read came from, whether it was interpreted, whether a human validated it,
how uncertain it is, and what an empty field means.

## Status Vocabulary

Section status values are intentionally conservative:

- `populated_from_llm_interpretation`
- `populated_from_human_review`
- `available_from_structured_artifact`
- `not_supplied`
- `requires_llm_interpretation`
- `requires_human_review`
- `available_in_private_artifact_not_exported`
- `available_but_redacted_in_safe_mode`
- `unclear`

Source status values are separate:

- `checked_in_safe_structured_artifact`
- `local_private_artifact`
- `review_artifact`
- `external_report_reference`
- `not_supplied`
- `redacted`
- `missing`
- `malformed`
- `unclear`

This keeps source custody distinct from semantic interpretation. A source may
exist privately while the user-facing section is still not populated in a safe
artifact.

## Interpretation Boundary

Populated semantic sections require LLM or human interpretation unless the value
already exists in a safe structured artifact.

LLMs or humans may interpret:

- the likely starting direction;
- what Lolla pressed on;
- what changed in recommendation, threshold, sequence, evidence gate, stop rule,
  or scope;
- what action would be different now;
- what remains unresolved;
- what value or momentum may have been lost.

Deterministic validation may protect:

- schema shape;
- required fields;
- source refs;
- source status;
- custody flags;
- artifact health;
- missingness;
- redaction/private availability;
- non-claims;
- forbidden authority fields.

Deterministic validation must not decide whether the advice is good, whether
Lolla improved the decision, or what the messy conversation truly meant.

## Custody Flags

The brief schema requires explicit lower-claim custody flags. In this PR114
contract, the conservative defaults and constants keep the schema honest:

- `human_validated` defaults to `false` unless a human review artifact is
  explicitly referenced.
- `product_proof` is `false`.
- `answer_quality_scored` is `false`.
- `agent_action_authorized` is `false`.
- `runtime_invoked` is `false`.
- `skill_invoked` is `false`.
- `archive_mutated` is `false`.
- `model_calls` is an integer with default `0` for deterministic schema work.
- `raw_private_content_included` is `false`.
- `provider_text_included` is `false`.

The schema supports human review only by explicit marking: if a section or brief
claims human validation, it must be marked as human-reviewed and point to review
refs. Unmarked LLM interpretation remains provisional.

## Non-Claims

Every brief must carry explicit non-claims:

- `not_correctness_proof`
- `not_answer_quality_score`
- `not_agent_action_authorization`
- `not_human_validated_unless_marked`
- `clean_artifacts_do_not_imply_good_advice`
- `process_evidence_is_not_decision_certification`
- `llm_interpretation_is_provisional_unless_human_reviewed`

These non-claims are product-critical. Clean artifacts can make a decision path
more inspectable, but they do not certify the decision.

## Authority Guard

The schema must not introduce fields that sound like approval, certification,
winner selection, broad judging, or answer-quality scoring. PR114 tests reject
those authority fields in the schema contract.

Acceptable language:

```text
source-supported but unvalidated
requires LLM interpretation
available in private artifact but not exported
not human validated unless marked
process evidence is not decision certification
```

Unacceptable field meanings:

```text
safe for agent action
approved decision
certified recommendation
pass/fail verdict
winner selection
quality or improvement score
```

## What Is Not Implemented

PR114 deliberately does not add:

- a packet builder;
- a brief generator;
- a Codex-assisted draft pilot;
- a Markdown renderer;
- runtime integration;
- prompt changes;
- archive mutation;
- provider or model calls from repo code;
- broad judging;
- answer-quality scoring;
- automatic labels;
- agent action authorization;
- product proof.

The next intended slice is PR115: Decision Work Brief Local Packet Builder v0.
That future PR should prepare local packets for bounded interpretation without
generating populated briefs.

## Relationship To The PRD

The product target and PR113-PR118 delivery sequence live in:

- [Decision Work Brief PRD v0](decision-work-brief-prd-v0.md)

PR114 makes the Decision Work Brief a first-class system contract. It does not
yet prove that a populated brief is useful. PR118 is the later usefulness gate.
