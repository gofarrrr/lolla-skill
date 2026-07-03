# Decision Work Generated Read Brief Rendering Pilot v0

Status: PR187 rendering pilot
Date: 2026-07-03

## Purpose

PR187 renders exactly one offline Decision Work Generated Read Brief from the
PR186 generated-read brief supply packet for `launch-public-enterprise-beta`.

This is the first reader-facing artifact produced by the generated-read path.
It remains deliberately narrow: deterministic rendering from an already
accepted PR182 intake result and a ready PR186 supply packet.

PR187 does not generate a new interpretation read, enrich a brief, generate
triage, mark resolver refs usable, update runtime sidecars, wire into runtime, call
providers or model APIs, create queue workers, score answer quality, claim
semantic correctness, claim product proof, claim human validation, or authorize
agent or automatic action.

## Inputs

- PR184 generated read:
  [read.json](../../reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/read.json);
- PR184 intake:
  [intake.json](../../reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/intake.json);
- PR186 generated-read brief supply packet generated during validation by:

```bash
python3 scripts/evals/build_decision_work_generated_read_brief_supply.py \
  --read reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/read.json \
  --intake reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/intake.json \
  --out /tmp/decision_work_generated_read_brief_supply.json \
  --pretty
```

The supply packet is not checked in. The checked-in artifact is the rendered
Markdown brief produced from that packet.

## Renderer CLI

```bash
python3 scripts/evals/render_decision_work_generated_read_brief.py \
  --supply /tmp/decision_work_generated_read_brief_supply.json \
  --case-id launch-public-enterprise-beta \
  --out docs/conversation-understanding/decision-work-generated-read-rendered-launch-public-enterprise-beta-v0.md
```

The renderer validates that the supply packet is ready for offline brief
rendering, has no blockers, preserves source refs and uncertainty, keeps
privacy limits present, and keeps sidecar update, quality-label use, proof
claims, and action authorization closed.

## Rendered Artifact

- [Decision Work Generated Read Rendered Launch Public Enterprise Beta](decision-work-generated-read-rendered-launch-public-enterprise-beta-v0.md)

The rendered brief contains:

- the decision;
- what the generated interpretation adds;
- what changed for action;
- what still might be wrong;
- what this does not prove;
- evidence, source refs, uncertainty, privacy limits, custody flags, and
  non-claims.

## Boundary

The rendered Markdown is a provisional offline product-surface artifact. It is
not semantic truth, product proof, human validation, answer-quality scoring,
advice-correctness proof, resolver ref use, runtime sidecar update, or action
authorization.

## Decision Gate

Selected next step:

```text
proceed_to_generated_read_brief_vs_existing_brief_review
```

Recommended next PR:

```text
PR188 Decision Work Generated Read Brief vs Existing Brief Review v0
```

Reason:

The renderer can produce one checked-in-safe reader-facing brief from a ready
generated-read supply packet while preserving uncertainty, source refs, privacy
limits, and non-claims. The next safe step is to compare this generated-read
brief with the existing checked-in launch-beta Decision Work Brief before any
enrichment, triage, resolver ref use, sidecar update, or broader automation.

## Follow-Up Review

PR188 is implemented as
[Decision Work Generated Read Brief vs Existing Brief Review](decision-work-generated-read-brief-vs-existing-brief-review-v0.md).

That review compares the generated-read launch-beta brief against the existing
rendered and enriched launch-beta brief surfaces. It finds the generated-read
brief preserves the core decision/action consequence and non-claim boundary, but
is thinner than the enriched brief. The review gates to a second generated-read
brief rendering pilot rather than enrichment, triage, resolver ref use, sidecar
update, model calls, proof claims, scoring, or action authorization.

PR189 is implemented as
[Decision Work Generated Read Second Brief Rendering Pilot](decision-work-generated-read-second-brief-rendering-pilot-v0.md).
It runs the same generated-read-to-brief path on `deploy-assisted-intake-routing`
and keeps compliance/workflow caveats visible while still stopping before
enrichment, triage, resolver ref use, sidecar update, model calls, proof claims,
scoring, or action authorization.
