# Decision Work Generated Read Brief Supply Adapter v0

Status: PR186 deterministic adapter
Date: 2026-07-03
Output schema: `lolla.decision_work_generated_read_brief_supply.v0`

## Purpose

PR186 implements the deterministic adapter selected by PR185. It takes:

- an accepted PR182 generated-read intake result;
- the generated interpretation read referenced by that intake result;
- optional queue item and prompt packet refs;

and emits a safe brief-supply packet for later offline brief rendering.

The adapter validates, normalizes, and copies allowed fields. It does not add
new semantic interpretation, generate a read, render a Decision Work Brief,
enrich a brief, generate triage, mark resolver refs usable, update runtime
sidecars, change runtime behavior, call providers or model APIs, score answer
quality, claim product proof, claim human validation, claim advice correctness,
or authorize action.

## CLI

```bash
python3 scripts/evals/build_decision_work_generated_read_brief_supply.py \
  --read reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/read.json \
  --intake reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/intake.json \
  --out /tmp/decision_work_generated_read_brief_supply.json \
  --pretty
```

Optional refs:

```bash
python3 scripts/evals/build_decision_work_generated_read_brief_supply.py \
  --read <generated-read-json> \
  --intake <generated-read-intake-json> \
  --queue-item <queue-item-json> \
  --prompt-packet <prompt-packet-json> \
  --out /tmp/decision_work_generated_read_brief_supply.json \
  --pretty
```

The command writes a JSON packet for ready, deferred, blocked, or
repair-required supply states. It exits nonzero only for mechanical
input/output errors.

## Output Shape

Result schema:

```text
lolla.decision_work_generated_read_brief_supply.v0
```

Top-level fields include:

- `schema_version`;
- `supply_metadata`;
- `source_read_ref`;
- `intake_ref`;
- `queue_item_ref`;
- `prompt_packet_ref`;
- `supply_status`;
- `blocker_reasons`;
- `allowed_brief_feed`;
- `evidence_only_fields`;
- `missing_required_fields`;
- `source_ref_summary`;
- `uncertainty_summary`;
- `privacy_summary`;
- `custody_flags`;
- `downstream_allowed`;
- `non_claims`.

## Statuses

The adapter can emit:

- `ready_for_offline_brief_rendering`;
- `deferred_missing_required_fields`;
- `blocked_intake_not_accepted`;
- `blocked_missing_source_refs`;
- `blocked_missing_uncertainty`;
- `blocked_privacy_risk`;
- `blocked_authority_claim`;
- `requires_operator_repair`.

## Allowed Supply Fields

The adapter reuses the PR185 field policy and the PR139 enrichment contract.
Allowed feed fields are:

- `decision_question`;
- `likely_starting_direction`;
- `revised_direction_or_action_consequence`;
- `decision_thresholds`;
- `evidence_gates`;
- `useful_friction`;
- `what_the_final_answer_does_not_prove`.

Minimal ready supply requires:

- `decision_question`;
- `revised_direction_or_action_consequence`;
- `what_the_final_answer_does_not_prove`.

Every copied field keeps its source refs, source status, uncertainty,
interpretation basis, privacy limit, human-review flag, and
`must_not_be_used_as_quality_label: true`.

## Blocking Rules

The adapter blocks when:

- the intake result is not accepted;
- the intake result does not point to the supplied read;
- required fields are missing;
- source refs are missing or malformed;
- uncertainty is missing;
- privacy limits are missing;
- raw/private markers or local paths appear;
- custody flags claim model calls, product proof, human validation, answer
  scoring, action authorization, raw/private content, provider text, or local
  paths;
- intake claims sidecar update, agent action, or quality-label use.

## Runtime And Authority Boundary

Even when supply is ready, these stay false:

- `can_update_sidecar`;
- `can_authorize_agent_action`;
- `can_be_used_as_quality_label`;
- `product_proof`;
- `human_validated`;
- `answer_quality_scored`.

Ready supply means only that later offline brief rendering may consider the
copied field packet. It is not semantic truth, product proof, human validation,
runtime permission, or action authorization.

## Decision Gate

Selected next step:

```text
proceed_to_generated_read_brief_rendering_pilot
```

Recommended next PR:

```text
PR187 Decision Work Generated Read Brief Rendering Pilot v0
```

Reason:

The adapter can produce ready, deferred, blocked, and repair-required supply
states without interpretation. The next safe step is a one-case offline
rendering pilot that consumes a ready supply packet, while still stopping before
triage, resolver ref use, runtime sidecar updates, queue workers,
provider/model calls, product proof, human validation, scoring, or action
authorization.
