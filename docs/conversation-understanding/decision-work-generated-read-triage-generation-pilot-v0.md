# Decision Work Generated Read Triage Generation Pilot v0

Status: PR193 generated triage pilot
Date: 2026-07-03

Schema: `lolla.decision_work_generated_read_triage.v0`

## Purpose

PR193 creates the first tiny generated-read triage read over exactly one case:

```text
launch-public-enterprise-beta
```

This is the lower-risk launch/GTM case. It is used to test the generated-read
triage read shape before trying domain-sensitive healthcare or
governance/relationship cases.

The pilot is offline, checked-in-safe, and Codex-assisted. It does not call
providers or model APIs from repo code, create runtime triage, mark resolver
refs usable, update runtime sidecars, wire runtime behavior, score answer
quality, claim semantic correctness, claim product proof, claim human
validation, validate advice correctness, or authorize action.

## Inputs

The pilot uses:

- PR184 generated read:
  [read.json](../../reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/read.json);
- PR184 intake:
  [intake.json](../../reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/intake.json);
- PR186 generated-read brief-supply packet generated during validation;
- PR187 generated-read rendered launch-beta brief:
  [Decision Work Generated Read Rendered Launch Public Enterprise Beta](decision-work-generated-read-rendered-launch-public-enterprise-beta-v0.md);
- PR192 generated-read triage-supply packet generated during validation.

The generated PR192 triage-supply packet is not checked in. The checked-in
triage read records only its schema/status relationship as
`temporary_validation_output:decision_work_generated_read_triage_supply_launch.json`.

## Triage Read

- [Generated Read Triage Pilot Read](../../reviews/codex-assisted/decision-work-generated-read-triage-generation-pilot-v0/triage.json)

The read selects conservative route categories:

- `ordinary_caveated_offline_brief_candidate`;
- `source_depth_insufficient`;
- `private_context_required`;
- `high_overtrust_risk`;
- `runtime_attachment_blocked`.

These categories route attention. They do not grade the answer, approve advice,
prove product value, establish human validation, or authorize action.

The launch-beta pattern is:

- the generated-read brief can be treated as an ordinary caveated offline brief
  candidate;
- private context remains required before stronger claims;
- source depth is still limited to checked-in-safe summaries;
- overtrust risk remains present because reader-facing prose can feel more
  complete than the source depth warrants;
- runtime attachment remains blocked for automatic user confidence and resolver
  use.

## Review

- [Generated Read Triage Generation Pilot Review](../../reviews/codex-assisted/decision-work-generated-read-triage-generation-pilot-v0/review.json)

The review confirms that the pilot preserves source refs, uncertainty, privacy
limits, non-claims, and the no-runtime/no-action boundary. It selects a
review-only next PR before trying a second case.

## Boundary

PR193 does not:

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
- authorize agent or automatic action.

## Decision Gate

Selected next step:

```text
proceed_to_generated_read_triage_pilot_review
```

Recommended next PR:

```text
PR194 Decision Work Generated Read Triage Pilot Review v0
```

Reason:

The first triage read stays in the intended lane: route attention, preserve
uncertainty and source-depth limits, and keep runtime/action boundaries closed.
Before applying the pattern to deploy-intake, a review-only PR should inspect
whether the route vocabulary reads as triage rather than answer-quality
judgment or action permission.

## Implemented Follow-Up

PR194 implements that review as
[Decision Work Generated Read Triage Pilot Review](decision-work-generated-read-triage-pilot-review-v0.md).
The review confirms the launch-beta triage read routes attention rather than
grading advice, preserves uncertainty/source-depth/runtime boundaries, and is
safe enough to attempt a second generated-read triage pilot on
`deploy-assisted-intake-routing`.
