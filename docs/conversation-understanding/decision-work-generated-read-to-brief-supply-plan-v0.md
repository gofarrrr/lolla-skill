# Decision Work Generated Read To Brief Supply Plan v0

Status: PR185 supply plan gate
Date: 2026-07-03
Review schema: `lolla.decision_work_generated_read_to_brief_supply_plan.v0`

## Purpose

PR185 defines the safe path from an accepted PR182 generated-read intake result
to a future deterministic brief-supply packet.

This is plan, review, and tests only. It does not generate a new read, generate
a Decision Work Brief, enrich a brief, generate triage, approve resolver refs,
update runtime sidecars, change runtime behavior, call providers or model APIs,
score answer quality, claim product proof, claim human validation, claim advice
correctness, or authorize action.

## Source Artifacts Reviewed

The plan reviews:

- [Decision Work Operator/Codex Generated Read Pilot](decision-work-operator-codex-generated-read-pilot-v0.md);
- [PR184 generated read](../../reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/read.json);
- [PR184 intake result](../../reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/intake.json);
- [Decision Work Generated Interpretation Read Intake](decision-work-generated-interpretation-read-intake-v0.md);
- [Decision Work Brief Enrichment Rules Contract](decision-work-brief-enrichment-rules-contract-v0.json);
- [Decision Work Brief Offline Enriched Builder](decision-work-brief-offline-enriched-builder-v0.md).

Machine-readable review:

- [`review.json`](../../reviews/codex-assisted/decision-work-generated-read-to-brief-supply-plan-v0/review.json)

## Required Intake State

The future adapter may prepare supply only when the intake result says:

- `intake_status: accepted`;
- `accepted_for_downstream: true`;
- `downstream_allowed.can_feed_brief: true`;
- `downstream_allowed.can_update_sidecar: false`;
- `downstream_allowed.can_authorize_agent_action: false`;
- `downstream_allowed.can_be_used_as_quality_label: false`.

The source read ref in the intake result must match the read being adapted. The
intake result must not claim that a brief, enriched brief, triage packet,
resolver ref, or runtime sidecar was already generated.

## Fields That May Feed A Brief

PR185 reuses the PR139 enrichment rules rather than defining a new semantic
policy. A future adapter may carry these fields forward for later offline brief
or enrichment rendering:

- `decision_question`;
- `likely_starting_direction`;
- `revised_direction_or_action_consequence`;
- `decision_thresholds`;
- `evidence_gates`;
- `useful_friction`;
- `what_the_final_answer_does_not_prove`.

Every allowed field must keep:

- source refs;
- source status;
- uncertainty;
- interpretation basis;
- privacy limit;
- human-review flag;
- `must_not_be_used_as_quality_label: true`.

Minimal supply requires:

- `decision_question`;
- `revised_direction_or_action_consequence`;
- `what_the_final_answer_does_not_prove`.

Other allowed fields may be absent. Missing optional fields should be recorded
as missing, not invented.

## Evidence-Only Fields

These fields may travel as evidence-only metadata or blocker context, but must
not enter the user-facing brief body in this layer:

- `live_options`;
- `abandoned_or_rejected_options`;
- `noisy_friction`;
- `lost_value`;
- `assistant_influence_on_user_framing`;
- `safe_for_agent_inspection_only`.

Reason:

These fields are too easy to overstate from checked-in-safe context. They often
require richer source depth, human review, or a separate routing decision.

## Blocked Concepts

The future adapter must block or exclude:

- answer-quality scores;
- improvement scores;
- approval or certification labels;
- product-proof claims;
- human-validation claims;
- advice-correctness claims;
- proof that Lolla improved the decision;
- agent action authorization;
- automatic action authorization;
- runtime sidecar update authorization;
- raw conversation text;
- raw revised answer text;
- raw memo text;
- provider text;
- private ledgers;
- local absolute paths;
- secrets;
- hidden reasoning material.

## Deterministic Allowances

The future adapter may:

- verify the intake result is accepted;
- verify the source read ref matches the read;
- copy allowed field values without expanding meaning;
- copy source refs, source status, uncertainty, and privacy limits;
- normalize field order and status names;
- emit missing required field names;
- emit evidence-only field names;
- emit blocker reasons;
- emit non-claims and conservative custody flags.

The adapter must not:

- fill missing fields;
- infer starting direction when unresolved;
- judge whether advice was good;
- judge whether Lolla improved the decision;
- decide whether friction was useful or noisy without a supplied field;
- convert evidence gates into validated evidence sufficiency;
- convert action consequences into action authorization;
- write new user-facing brief prose.

## Blocking Rules

The future adapter should block when:

- intake is not accepted;
- required fields are missing;
- any allowed field lacks source refs;
- any allowed field lacks uncertainty;
- any allowed field lacks a privacy limit;
- source refs contain local absolute paths;
- raw/private markers appear;
- custody flags claim product proof, human validation, answer-quality scoring,
  model calls, action authorization, raw/private content, provider text, or
  local paths;
- non-claims are missing.

## Main Risks

Strongest useful signal:

> PR185 turns the PR184 accepted read into a concrete deterministic supply
> contract: later code can validate and carry allowed fields forward without
> inventing meaning.

Strongest unresolved risk:

> A future supply adapter can still make an accepted read look more complete
> than it is if missing optional fields, evidence-only fields, and uncertainty
> are not kept visible.

## Decision Gate

Selected next step:

```text
proceed_to_generated_read_brief_supply_adapter
```

Recommended next PR:

```text
PR186 Decision Work Generated Read Brief Supply Adapter v0
```

PR186 is now implemented as:

- [Decision Work Generated Read Brief Supply Adapter](decision-work-generated-read-brief-supply-adapter-v0.md).

Reason:

The field policy is clear enough for a deterministic adapter. The adapter should
validate an accepted intake result and source read, emit a supply JSON packet,
and stop before brief rendering, enrichment, triage, resolver approval, runtime
sidecar update, queue workers, provider/model calls, product proof, human
validation, scoring, or action authorization.

The implemented adapter emits ready, deferred, blocked, or repair-required
supply states. It copies only allowed fields with their source refs,
source-status, uncertainty, interpretation basis, privacy limits, and non-claim
flags; evidence-only fields stay out of brief feed; sidecar updates, quality
labels, proof claims, and action authorization remain unavailable.
