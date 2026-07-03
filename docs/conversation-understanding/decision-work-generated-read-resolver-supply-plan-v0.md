# Decision Work Generated Read Resolver Supply Plan v0

Status: PR197 plan gate
Date: 2026-07-03

## Purpose

PR197 defines the safe path from generated-read artifacts and generated triage
reads into future resolver-supply candidates.

This is a plan/gate only. It does not implement resolver supply code, approve
resolver refs, update runtime sidecars, wire runtime behavior, generate new
triage, call providers/models, create workers, claim semantic correctness,
claim product proof, claim human validation, score answer quality, validate
advice correctness, or authorize action.

Plainly: resolver supply is not resolver approval.

Source artifacts reviewed:

- [Decision Work Generated Read Triage Two-Case Pattern Review](decision-work-generated-read-triage-two-case-pattern-review-v0.md);
- [Decision Work Generated Read Triage Generation Pilot](decision-work-generated-read-triage-generation-pilot-v0.md);
- [Decision Work Generated Read Second Triage Pilot](decision-work-generated-read-second-triage-pilot-v0.md);
- [Decision Work Generated Read Triage Supply Adapter](decision-work-generated-read-triage-supply-adapter-v0.md);
- [Decision Work Generated Read Brief Supply Adapter](decision-work-generated-read-brief-supply-adapter-v0.md);
- [Decision Work Generated Interpretation Read Intake](decision-work-generated-interpretation-read-intake-v0.md).

## Resolver Supply Candidate

A resolver supply candidate is a bounded packet of safe refs, statuses, routes,
missingness, uncertainty, privacy limits, and non-claims that a future resolver
layer may inspect.

It explicitly does not mean:

- resolver refs are approved;
- the generated read is semantically correct;
- the rendered brief is user-surface ready;
- the triage read is an answer-quality label;
- runtime sidecar update is allowed;
- an agent or automatic system may act.

The candidate packet can exist even when runtime use is blocked. For example,
`deploy-assisted-intake-routing` may be eligible to prepare a resolver
candidate packet for maintainer inspection while still carrying
`agent_inspection_only`, `not_ready_for_user_surface`, and
`runtime_attachment_blocked`.

## Allowed Resolver Supply Inputs

Future generated-read resolver supply may consume these refs together:

- generated interpretation read JSON;
- PR182 intake result JSON;
- PR186 generated-read brief supply JSON;
- PR187 generated-read rendered brief Markdown;
- PR192 generated-read triage supply JSON;
- PR193 or PR195 generated triage JSON;
- optional queue item or prompt packet refs.

The adapter may use the refs and statuses only when the intake result,
brief-supply packet, triage-supply packet, rendered brief, and generated triage
read all preserve source refs, uncertainty, privacy limits, custody flags, and
non-claims.

## Safe Ref Candidates

Allowed safe ref candidates are artifact refs and status summaries, not
semantic approval labels:

- source generated-read ref;
- source intake result ref and intake status;
- generated-read brief-supply ref and supply status;
- rendered brief ref and availability status;
- triage-supply ref and triage-supply status;
- generated triage ref and route categories;
- source-ref summary;
- uncertainty summary;
- privacy summary;
- custody summary;
- non-claim summary;
- route summary.

These candidates can help a future resolver understand what exists, what is
missing, what is blocked, and what must remain offline or agent-inspection
only. They must not be promoted into "approved safe refs" by this layer.

## Evidence-Only And Blocked Fields

These fields remain evidence-only:

- decision question;
- revised direction or action consequence;
- evidence gates;
- what the final answer does not prove;
- source-depth limits;
- private-context need;
- overtrust risk;
- domain, legal, compliance, governance, relationship, or safety caveats.

These fields are blocked from resolver-supply conclusions:

- answer quality;
- advice correctness;
- proof that Lolla improved the decision;
- human validation;
- product proof;
- legal, compliance, clinical, governance, or relationship clearance;
- safe-to-act or safe-to-deploy claims;
- resolver-ref approval;
- runtime sidecar permission;
- agent or automatic action permission.

The adapter may record that a field is evidence-only, missing, or blocked. It
must not fill missing semantics or infer whether the advice was good, correct,
approved, or actionable.

## Required Triage Routes

Future resolver supply must preserve triage routes rather than flatten them.
At minimum, it should understand these route effects:

- `ordinary_caveated_offline_brief_candidate` may allow a candidate packet only
  when paired with source-depth, uncertainty, privacy, and runtime-blocker
  caveats.
- `agent_inspection_only` requires the future resolver-supply packet to mark
  user-surface and runtime use blocked.
- `not_ready_for_user_surface` requires the packet to block user-surface
  claims and runtime sidecar updates.
- `runtime_attachment_blocked` requires the packet to keep runtime use blocked
  even if a candidate packet is otherwise prepared.
- `domain_review_recommended` and
  `legal_or_compliance_review_recommended` require visible domain/compliance
  caveats and must not be read as legal, clinical, operational, or compliance
  clearance.

## Resolver Supply Statuses

Future resolver supply should support:

- `ready_for_resolver_candidate_packet`;
- `candidate_packet_with_runtime_block`;
- `deferred_missing_triage`;
- `deferred_missing_rendered_brief`;
- `deferred_missing_brief_supply`;
- `blocked_intake_not_accepted`;
- `blocked_triage_missing`;
- `blocked_privacy_risk`;
- `blocked_authority_claim`;
- `requires_operator_repair`.

The important distinction is that `ready_for_resolver_candidate_packet` and
`candidate_packet_with_runtime_block` both remain candidate states. Neither
approves resolver refs, user-surface readiness, runtime sidecar updates, or
agent action.

## Deterministic Allowances

A future adapter may:

- validate the generated read, intake result, brief supply, rendered brief,
  triage supply, and triage read;
- copy safe refs and statuses;
- normalize route summaries;
- preserve missingness and blockers;
- preserve source refs, uncertainty, privacy limits, custody flags, and
  non-claims;
- derive candidate-packet readiness from explicit statuses and route categories
  only;
- mark runtime use blocked when route categories require it.

It must not:

- approve resolver refs;
- mark refs as safe for runtime use;
- update runtime sidecars;
- wire runtime behavior;
- generate new semantic interpretation;
- generate triage;
- decide answer quality;
- decide advice correctness;
- call models/providers;
- authorize agent or automatic action.

## Decision Gate

Selected next step:

```text
proceed_to_generated_read_resolver_supply_adapter
```

Recommended next PR:

```text
PR198 Decision Work Generated Read Resolver Supply Adapter v0
```

Reason:

The two-case generated-read triage pattern is stable enough to prepare
resolver-candidate packets, as long as the next implementation keeps candidate
supply separate from resolver approval, runtime sidecar updates, user-surface
readiness, scoring, proof claims, and action authorization.

Do not implement resolver approval, runtime sidecar updates, runtime wiring,
model calls, scoring, proof claims, or action authorization from this plan.

## Implemented Follow-Up

PR198 implements this plan as
[Decision Work Generated Read Resolver Supply Adapter](decision-work-generated-read-resolver-supply-adapter-v0.md).
The adapter emits `lolla.decision_work_generated_read_resolver_supply.v0`
candidate packets from generated-read, intake, brief-supply, rendered-brief,
triage-supply, and generated-triage refs. It can produce a launch-beta
candidate packet and a deploy-intake candidate packet that preserves
runtime/user-surface blocking, without approving resolver refs, marking refs
usable, updating sidecars, wiring runtime, calling models, scoring, proving, or
authorizing action.
