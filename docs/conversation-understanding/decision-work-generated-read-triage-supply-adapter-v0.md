# Decision Work Generated Read Triage Supply Adapter v0

Status: PR192 deterministic adapter
Date: 2026-07-03

Schema: `lolla.decision_work_generated_read_triage_supply.v0`

## Purpose

PR192 implements the deterministic adapter planned by PR191.

The adapter prepares a generated-read triage-supply packet for a later offline
triage generation or review step. It consumes the generated-read chain that is
already safe enough for offline brief rendering:

- generated interpretation read JSON;
- PR182 intake result JSON;
- PR186 generated-read brief supply JSON;
- generated-read rendered brief Markdown;
- optional queue item or prompt packet refs.

It validates and normalizes refs, status, source linkage, uncertainty, privacy,
custody, and non-claims. It does not generate triage, create a triage read,
mark resolver refs usable, update runtime sidecars, wire runtime behavior, call
models/providers, score answer quality, claim product proof, claim human
validation, validate advice correctness, or authorize action.

## CLI

```bash
python3 scripts/evals/build_decision_work_generated_read_triage_supply.py \
  --read reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/read.json \
  --intake reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/intake.json \
  --brief-supply /tmp/decision_work_generated_read_brief_supply_launch.json \
  --rendered-brief docs/conversation-understanding/decision-work-generated-read-rendered-launch-public-enterprise-beta-v0.md \
  --out /tmp/decision_work_generated_read_triage_supply_launch.json \
  --pretty
```

The CLI writes a JSON result for ready, deferred, and blocked states. It records
safe refs and statuses only. It does not copy raw source text from the generated
read, rendered brief, or private archives.

## Output Shape

The packet includes:

- `schema_version`;
- `triage_supply_metadata`;
- `source_case`;
- `source_read_ref`;
- `source_intake_ref`;
- `source_brief_supply_ref`;
- `source_rendered_brief_ref`;
- `optional_queue_item_ref`;
- `optional_prompt_packet_ref`;
- `triage_supply_status`;
- `blocker_reasons`;
- `allowed_routing_inputs`;
- `evidence_only_inputs`;
- `forbidden_route_claims`;
- `required_source_refs`;
- `uncertainty_summary`;
- `privacy_summary`;
- `custody_flags`;
- `non_claims`;
- `downstream_allowed`;
- `downstream_forbidden`;
- `route_categories_allowed`;
- `route_categories_forbidden`.

## Statuses

The adapter emits:

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

`ready_for_offline_triage_generation` means only that a future offline triage
generation or review step has enough safe structured supply to run. It is not a
triage result, not a quality label, not product proof, not human validation, and
not permission for runtime sidecar use.

## Allowed Routing Inputs

Allowed routing inputs are copied from already validated generated-read and
brief-supply artifacts:

- case id and decision family;
- intake status;
- brief-supply status;
- rendered brief availability;
- `decision_question`;
- `revised_direction_or_action_consequence`;
- `evidence_gates`;
- `what_the_final_answer_does_not_prove`;
- source refs;
- source status;
- uncertainty;
- interpretation basis;
- privacy limits;
- non-claims.

These inputs may route attention only. They must not be used to decide whether
the answer was good, bad, correct, safe to act on, or proof that Lolla improved
the decision.

## Evidence-Only Inputs

The adapter preserves evidence-only field names from PR191 and PR186, including:

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

It may record that those fields are evidence-only or missing. It does not fill
them, infer their meaning, or turn them into route conclusions.

## Downstream Boundary

For every result, these remain false:

- `can_update_sidecar`;
- `can_approve_resolver_refs`;
- `can_authorize_agent_action`;
- `can_authorize_automatic_action`;
- `can_be_used_as_quality_label`;
- `product_proof`;
- `human_validated`;
- `answer_quality_scored`.

The adapter allows `can_generate_offline_triage: true` only when the packet is
ready and only for a future offline triage generation or review step.

## Decision Gate

Selected next step:

```text
proceed_to_generated_read_triage_generation_pilot
```

Recommended next PR:

```text
PR193 Decision Work Generated Read Triage Generation Pilot v0
```

Reason:

The launch-beta and deploy-intake generated-read paths can now produce
triage-supply packets that preserve refs, uncertainty, privacy limits, custody
flags, non-claims, and forbidden route concepts. The next risk boundary is the
first generated triage pilot, not runtime wiring or sidecar update.
