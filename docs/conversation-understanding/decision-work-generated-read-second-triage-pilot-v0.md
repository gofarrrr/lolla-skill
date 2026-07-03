# Decision Work Generated Read Second Triage Pilot v0

Status: PR195 second triage pilot
Date: 2026-07-03

Schema: `lolla.decision_work_generated_read_triage.v0`

## Purpose

PR195 creates the second generated-read triage pilot over exactly one case:

```text
deploy-assisted-intake-routing
```

This case is intentionally higher risk than the launch-beta triage pilot. It
touches outpatient clinic workflow, compliance, scheduling and billing routing,
admin load, and pause triggers. The purpose is to test whether the generated
triage shape can route domain risk without becoming an approval, a quality
score, clinical/legal clearance, or deployment permission.

The pilot is offline, checked-in-safe, and Codex-assisted. It does not call
providers or model APIs from repo code, create runtime triage, mark resolver
refs usable, update runtime sidecars, wire runtime behavior, score answer
quality, claim semantic correctness, claim product proof, claim human
validation, validate advice correctness, or authorize action.

## Inputs

The pilot uses:

- PR189 generated read:
  [read.json](../../reviews/codex-assisted/decision-work-generated-read-second-brief-rendering-pilot-v0/read.json);
- PR189 intake:
  [intake.json](../../reviews/codex-assisted/decision-work-generated-read-second-brief-rendering-pilot-v0/intake.json);
- PR186 generated-read brief-supply packet generated during validation;
- PR189 generated-read rendered deploy-intake brief:
  [Decision Work Generated Read Rendered Deploy Assisted Intake Routing](decision-work-generated-read-rendered-deploy-assisted-intake-routing-v0.md);
- PR192 generated-read triage-supply packet generated during validation.

The generated PR186 and PR192 packets are not checked in. The checked-in triage
read records only their schema/status relationship as temporary validation
outputs.

## Triage Read

- [Second Generated Read Triage Pilot Read](../../reviews/codex-assisted/decision-work-generated-read-second-triage-pilot-v0/triage.json)

The read selects conservative route categories:

- `source_depth_insufficient`;
- `private_context_required`;
- `high_overtrust_risk`;
- `domain_review_recommended`;
- `legal_or_compliance_review_recommended`;
- `not_ready_for_user_surface`;
- `agent_inspection_only`;
- `runtime_attachment_blocked`.

The deploy-intake read deliberately does not use
`ordinary_caveated_offline_brief_candidate`. In this healthcare workflow case,
the safer route is domain-sensitive inspection, not ordinary offline
candidacy. That does not mean the generated-read brief is useless; it means the
brief is useful only as a caveated offline artifact requiring domain,
compliance, and private-context review before any operational use.

These categories route attention. They do not grade the answer, approve the
advice, prove product value, establish human validation, clear legal or
clinical adequacy, or authorize action.

## Review

- [Second Generated Read Triage Pilot Review](../../reviews/codex-assisted/decision-work-generated-read-second-triage-pilot-v0/review.json)

The review confirms that the deploy-intake triage read preserves source refs,
uncertainty, privacy limits, non-claims, domain caveats, and the
no-runtime/no-action boundary. It selects a two-case triage pattern review
before any resolver-supply planning.

## Boundary

PR195 does not:

- run `$lolla`;
- invoke the Lolla skill;
- call provider/model APIs;
- create new Lolla runs;
- mutate archives;
- change prompts;
- touch `SKILL.md` or `scripts/skill/*`;
- make runtime attachment default-on;
- add direct runtime interpretation;
- add queue workers/daemons;
- approve resolver refs;
- update runtime sidecars;
- wire anything into runtime;
- score answer quality;
- add approval labels;
- claim product proof;
- claim human validation;
- claim advice correctness;
- claim proof that Lolla improved decisions;
- claim legal, compliance, clinical, or deployment clearance;
- authorize agent or automatic action.

## Decision Gate

Selected next step:

```text
proceed_to_two_case_generated_read_triage_pattern_review
```

Recommended next PR:

```text
PR196 Two-Case Generated Read Triage Pattern Review v0
```

Reason:

The second triage read preserves the attention-routing boundary in a higher
risk domain. It escalates deploy-intake to domain/compliance review and
agent-inspection-only review rather than treating the generated-read brief as
safe for user-facing or operational use. The next safe step is to compare the
launch-beta and deploy-intake triage reads together before any resolver-supply
plan, runtime sidecar update, or automation.
