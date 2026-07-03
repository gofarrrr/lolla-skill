# Decision Work Generated Read Brief Two-Case Pattern Review v0

Status: PR190 pattern review
Date: 2026-07-03

## Purpose

PR190 reviews the two generated-read-rendered Decision Work Briefs together:

- [Launch-beta generated-read brief](decision-work-generated-read-rendered-launch-public-enterprise-beta-v0.md);
- [Deploy-intake generated-read brief](decision-work-generated-read-rendered-deploy-assisted-intake-routing-v0.md).

This is a docs/review/tests-only gate. It does not generate a new read, render a
third case, enrich, generate triage, mark resolver refs usable, update runtime
sidecars, call providers/models, claim semantic correctness, claim product
proof, claim human validation, score answer quality, or authorize action. Put
plainly: PR190 does not generate triage.

## Stable Useful Signals

Across the two cases, the generated-read brief path consistently preserves:

- the decision question;
- the action consequence;
- evidence gates;
- source refs;
- source status;
- uncertainty;
- privacy limits;
- evidence-only exclusions;
- product-proof false;
- human-validation false;
- answer-quality scoring false;
- sidecar update unavailable;
- action authorization false.

The path also preserves the generated-read origin. Both rendered briefs state
that they are provisional offline artifacts rendered from PR186 supply and that
they format supplied fields only.

## Unstable Or Weak Signals

The generated-read briefs are useful but thin. They do not carry the richer
context from the earlier enriched briefs, and they intentionally exclude fields
such as `lost_value`, `noisy_friction`, `live_options`, and
`assistant_influence_on_user_framing` from the user-facing brief feed.

The deploy-intake case shows the most important product-surface risk: readable
briefs in healthcare operations contexts can sound more operationally complete
than the source depth warrants. The brief mitigates this by preserving
compliance/workflow caveats and explicitly refusing operational, legal,
compliance, or clinical clearance.

## Pattern Assessment

The two-case pattern is strong enough to plan triage supply, but not to generate
triage yet. The conclusion is to plan triage supply, not to generate triage yet.

The next layer should define how an accepted generated read and generated-read
brief supply may safely become triage supply while preserving source refs,
uncertainty, privacy limits, and non-claims. That future plan must still keep
runtime sidecar update, resolver ref use, action authorization, product proof,
human validation, answer-quality scoring, and advice-correctness claims closed.

## Decision Gate

Selected next step:

```text
proceed_to_generated_read_triage_supply_plan
```

Recommended next PR:

```text
PR191 Decision Work Generated Read Triage Supply Plan v0
```

Reason:

The generated-read brief path has now rendered two checked-in-safe cases across
different decision families while preserving action consequence, uncertainty,
source limits, privacy limits, and non-claims. The next safe step is a triage
supply plan, not triage generation or runtime sidecar work.

## Follow-Up Plan

PR191 is implemented as
[Decision Work Generated Read Triage Supply Plan](decision-work-generated-read-triage-supply-plan-v0.md).

That plan defines the allowed generated-read triage supply inputs, routing
fields, evidence-only fields, blocked fields, route categories, custody
requirements, and forbidden quality/authority route concepts. It selects a
deterministic triage supply adapter next while still stopping before generated
triage, resolver ref use, runtime sidecar update, model calls, proof claims,
scoring, or action authorization.
