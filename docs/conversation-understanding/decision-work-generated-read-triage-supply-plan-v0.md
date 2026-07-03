# Decision Work Generated Read Triage Supply Plan v0

Status: PR191 plan gate
Date: 2026-07-03

## Purpose

PR191 defines the safe path from generated-read artifacts into future automatic
triage supply.

This is a plan/gate only. It does not generate triage, create a triage read,
mark resolver refs usable, update runtime sidecars, change runtime behavior,
call providers/models, create workers, claim semantic correctness, claim product
proof, claim human validation, score answer quality, or authorize action.

Source artifacts reviewed:

- [Decision Work Generated Read Brief Two-Case Pattern Review](decision-work-generated-read-brief-two-case-pattern-review-v0.md);
- [Decision Work Generated Read Brief Supply Adapter](decision-work-generated-read-brief-supply-adapter-v0.md);
- [Decision Work Generated Interpretation Read Intake](decision-work-generated-interpretation-read-intake-v0.md);
- [Decision Work Automatic Triage Contract](decision-work-automatic-triage-contract-v0.md);
- [Decision Work Automatic Triage Packet Builder](decision-work-automatic-triage-packet-builder-v0.md).

## Triage Supply Inputs

Future generated-read triage supply should consume all of these refs together:

- generated interpretation read JSON;
- PR182 intake result JSON;
- PR186 generated-read brief supply JSON;
- generated-read rendered brief Markdown;
- optional queue item or prompt packet refs.

The rendered brief is not the source of semantic truth. It is a checked summary
surface that helps future triage confirm the reader-facing artifact preserved
caveats, uncertainty, source refs, privacy limits, and non-claims.

## Allowed Routing Fields

Allowed routing inputs are status and custody signals, not quality verdicts:

- case id and decision family;
- intake status and blocker reasons;
- brief-supply status and blocker reasons;
- rendered brief availability;
- allowed brief-feed field names;
- evidence-only field names;
- required source refs and source-ref status;
- uncertainty status and missing uncertainty;
- privacy status and privacy blockers;
- custody flags;
- non-claims;
- source-depth limits;
- domain/compliance sensitivity already explicit in checked-in-safe metadata.

Generated-read fields that may provide routing context:

- `decision_question`;
- `revised_direction_or_action_consequence`;
- `evidence_gates`;
- `what_the_final_answer_does_not_prove`.

Those fields may help route attention only when their source refs, uncertainty,
privacy limits, and `must_not_be_used_as_quality_label: true` travel with them.
They must not be used to decide whether the answer was good, bad, correct, or
safe to act on.

## Evidence-Only And Blocked Fields

These fields remain evidence-only or blocked from route conclusions unless a
future read and validator explicitly make them safe:

- `lost_value`;
- `noisy_friction`;
- `useful_friction`;
- `live_options`;
- `abandoned_or_rejected_options`;
- `assistant_influence_on_user_framing`;
- `stakeholder_obligations`;
- `user_values_or_priorities`;
- `safe_for_agent_inspection_only`;
- `safe_to_show_user`.

The adapter may record that these fields are missing or evidence-only. It may
route to `lost_value_risk_unresolved`, `private_context_required`, or
`source_depth_insufficient` when the absence matters. It must not fill the
missing semantics or infer whether friction was useful, noisy, or outcome
improving.

## Allowed Route Categories

Future triage supply may allow these route categories for later offline triage
generation:

- `source_depth_insufficient`;
- `private_context_required`;
- `high_overtrust_risk`;
- `domain_review_recommended`;
- `legal_or_compliance_review_recommended`;
- `relationship_or_governance_sensitive`;
- `lost_value_risk_unresolved`;
- `agent_inspection_only`;
- `not_ready_for_user_surface`;
- `runtime_attachment_blocked`.

These categories route attention. They are not answer-quality labels and do not
authorize action.

Forbidden route concepts:

- `good_answer`;
- `bad_answer`;
- `approved`;
- `certified`;
- `safe_to_act`;
- `correct_advice`;
- `lolla_improved_decision`;
- `human_validated`;
- `product_proof`;
- `agent_action_authorized`;
- `automatic_action_authorized`.

## Deterministic Allowances

A future adapter may:

- validate the generated read, intake result, supply packet, and rendered brief;
- copy safe refs and statuses;
- normalize allowed routing inputs;
- preserve missingness and blockers;
- preserve evidence-only fields;
- preserve source refs, uncertainty, privacy limits, custody flags, and
  non-claims;
- derive route-supply readiness from explicit statuses only.

It must not:

- generate semantic triage;
- decide answer quality;
- decide advice correctness;
- infer new messy-conversation meaning;
- mark resolver refs usable;
- update runtime sidecars;
- call models/providers;
- authorize agent or automatic action.

## Required Statuses

Future triage supply should support:

- `ready_for_offline_triage_generation`;
- `deferred_missing_rendered_brief`;
- `deferred_missing_brief_supply`;
- `blocked_intake_not_accepted`;
- `blocked_brief_supply_not_ready`;
- `blocked_missing_source_refs`;
- `blocked_missing_uncertainty`;
- `blocked_privacy_risk`;
- `blocked_authority_claim`;
- `requires_operator_repair`.

## Decision Gate

Selected next step:

```text
proceed_to_generated_read_triage_supply_adapter
```

Recommended next PR:

```text
PR192 Decision Work Generated Read Triage Supply Adapter v0
```

Reason:

The two generated-read-rendered briefs show that the pre-triage path can carry
safe fields, refs, uncertainty, privacy limits, and non-claims across two
decision families. The next safe implementation is a deterministic triage-supply
adapter that prepares a packet for future triage generation without generating
triage, marking resolver refs usable, updating sidecars, or calling models.
