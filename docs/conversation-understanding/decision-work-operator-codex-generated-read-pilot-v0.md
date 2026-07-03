# Decision Work Operator/Codex Generated Read Pilot v0

Status: PR184 pilot gate
Date: 2026-07-03

## Purpose

PR184 creates one tiny operator/Codex-assisted generated interpretation read
candidate and sends it through the PR182 generated-read intake validator.

This is not runtime generation. It does not call providers or model APIs from
repo code, create a queue worker, render a Decision Work Brief, enrich a brief,
generate triage, update resolver-approved refs, update runtime sidecars, claim
semantic correctness, claim product proof, claim human validation, score answer
quality, or authorize action.

## Case Selection

Selected case:

```text
launch-public-enterprise-beta
```

Reason:

- it is the lowest-risk of the three checked-in-safe Decision Work examples;
- it already has a rendered brief, builder-enriched brief, and prior checked-in
  interpretation read;
- it avoids the higher governance/legal sensitivity of the cofounder case;
- it is sufficient to prove the intake path for a new generated-read candidate.

## Artifacts

Generated-read candidate:

- [`read.json`](../../reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/read.json)

PR182 intake result:

- [`intake.json`](../../reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/intake.json)

The read uses the formal PR133 schema:

```text
lolla.decision_work_conversation_interpretation_read.v0
```

The intake result uses:

```text
lolla.decision_work_generated_interpretation_read_intake.v0
```

## Intake Result

The PR182 validator accepts the pilot read:

```text
intake_status: accepted
accepted_for_downstream: true
```

Acceptance means the candidate passed structure, source-ref, uncertainty,
privacy, custody, and non-claim checks. It does not mean the interpretation is
semantically true.

The intake result permits later offline planning only:

- `can_feed_brief: true`;
- `can_feed_enrichment: true`;
- `can_feed_triage_packet: true`;
- `can_feed_resolver: true`.

It keeps runtime and authority boundaries closed:

- `can_update_sidecar: false`;
- `can_authorize_agent_action: false`;
- `can_be_used_as_quality_label: false`.

## What The Read Preserves

The checked-in generated-read candidate preserves:

- checked-in-safe source refs;
- source status on each interpreted field;
- uncertainty on each interpreted field;
- privacy limits;
- human-review requirement;
- `must_not_be_used_as_quality_label: true`;
- conservative custody flags;
- explicit non-claims.

The read does not include raw conversation text, raw revised answer text, raw
memo text, provider text, private ledgers, local absolute paths, secrets, or
hidden reasoning material.

## What This Does Not Do

PR184 does not:

- feed the accepted read into brief rendering;
- enrich a brief from the accepted read;
- generate triage;
- approve resolver refs;
- update a runtime sidecar;
- attach anything to runtime;
- create a queue worker;
- call providers or model APIs from repo code;
- claim product proof;
- claim human validation;
- score answer quality;
- claim advice correctness;
- authorize agent or automatic action.

## Main Findings

Strongest useful signal:

> A newly checked-in-safe generated-read candidate can enter the PR182 validator
> and be accepted without weakening the sidecar, action, proof, or quality-label
> boundaries.

Strongest unresolved risk:

> Acceptance still only proves structural and custody eligibility. The system
> still needs a separate plan for how an accepted generated read becomes safe
> brief, enrichment, triage, resolver, and sidecar supply without laundering
> semantic uncertainty into runtime behavior.

## Decision Gate

Selected next step:

```text
proceed_to_generated_read_to_brief_supply_plan
```

Recommended next PR:

```text
PR185 Decision Work Generated Read To Brief Supply Plan v0
```

Reason:

The pilot read is checked-in-safe and accepted by intake, but the system has not
yet defined how accepted generated reads become Decision Work Brief supply. The
next safe slice should plan that transformation before any builder, triage,
resolver, or runtime sidecar wiring consumes this new read.
