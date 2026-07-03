# Decision Work Generated Read Second Brief Rendering Pilot v0

Status: PR189 second rendering pilot
Date: 2026-07-03

## Purpose

PR189 runs the generated-read-to-brief path on a second checked-in-safe case:
`deploy-assisted-intake-routing`.

The goal is to test whether the PR182 -> PR186 -> PR187 path generalizes beyond
the launch-beta case into a healthcare operations/workflow decision with
compliance caveats.

Inputs:

- PR189 generated read:
  [read.json](../../reviews/codex-assisted/decision-work-generated-read-second-brief-rendering-pilot-v0/read.json);
- PR189 intake result:
  [intake.json](../../reviews/codex-assisted/decision-work-generated-read-second-brief-rendering-pilot-v0/intake.json);
- PR186 supply packet generated during validation by:

```bash
python3 scripts/evals/build_decision_work_generated_read_brief_supply.py \
  --read reviews/codex-assisted/decision-work-generated-read-second-brief-rendering-pilot-v0/read.json \
  --intake reviews/codex-assisted/decision-work-generated-read-second-brief-rendering-pilot-v0/intake.json \
  --out /tmp/decision_work_generated_read_second_brief_supply.json \
  --pretty
```

Rendered output:

- [Generated-read rendered deploy-intake brief](decision-work-generated-read-rendered-deploy-assisted-intake-routing-v0.md).

This pilot is still offline and deterministic after the checked-in read exists.
It does not call providers/models, create a queue worker, create a new Lolla
run, enrich a brief, generate triage, mark resolver refs usable, update runtime
sidecars, claim semantic correctness, claim product proof, claim human
validation, score answer quality, or authorize action.

## Findings

The second generated-read path works on a different decision family without a
renderer or adapter change.

The PR182 intake accepts the deploy-intake generated read. The PR186 adapter
emits `ready_for_offline_brief_rendering`. The PR187 renderer produces a
reader-facing Markdown brief that preserves:

- the decision question;
- the action consequence;
- source refs;
- source status;
- uncertainty;
- privacy limits;
- evidence-only exclusions;
- non-claims.

The rendered brief keeps the domain caveat visible: the artifact is not
operational, legal, compliance, or clinical clearance. It also keeps the narrow
deployment boundary visible: one-clinic, staff-controlled scheduling and billing
routing, a 48-hour backlog diagnostic, four must-pass operating gates, hard
pause triggers, compliance readiness, and narrowed sales language.

## Risks

The strongest remaining risk is overtrust. A readable generated-read brief in a
clinic workflow domain can feel more actionable than the sources warrant. The
brief mitigates this by stating that human review is required before treating it
as operational guidance and that sidecar updates, resolver ref use, triage,
enrichment, and action authorization remain out of scope.

The source-depth risk also remains. The checked-in-safe artifacts do not include
full private conversation context, and the read intentionally excludes fields
such as `lost_value`, `noisy_friction`, and `live_options` from the user-facing
brief feed.

## Decision Gate

Selected next step:

```text
proceed_to_two_case_generated_read_brief_pattern_review
```

Recommended next PR:

```text
PR190 Two-Case Generated Read Brief Pattern Review v0
```

Reason:

The generated-read brief path now renders two checked-in-safe cases from two
different decision families while preserving uncertainty, source refs, privacy
limits, domain caveats, and non-claims. The next safe step is a pattern review
across both generated-read-rendered briefs before any generated-read triage
supply, resolver ref use, sidecar update, or broader automation.

## Follow-Up Review

PR190 is implemented as
[Decision Work Generated Read Brief Two-Case Pattern Review](decision-work-generated-read-brief-two-case-pattern-review-v0.md).

That review compares the launch-beta and deploy-intake generated-read-rendered
briefs together and selects a generated-read triage supply plan next, while
still stopping before triage generation, resolver ref use, runtime sidecar
update, model calls, proof claims, scoring, or action authorization.
