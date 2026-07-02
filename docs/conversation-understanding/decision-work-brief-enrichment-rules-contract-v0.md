# Decision Work Brief Enrichment Rules Contract v0

Status: PR139 rules contract
Date: 2026-07-01
Schema: `lolla.decision_work_brief_enrichment_rules_contract.v0`

## Purpose

PR139 formalizes the rules for turning a provisional conversation
interpretation read into a small user-facing enrichment inside a Decision Work
Brief.

The machine-readable contract is:

- [Decision Work Brief Enrichment Rules Contract JSON](decision-work-brief-enrichment-rules-contract-v0.json)

This PR is docs/schema/tests only. It does not build the offline enriched brief
builder, create more enriched briefs, call models, run Lolla, change runtime,
or claim product proof.

## Why This Contract Exists

PR135 and PR137 showed that interpretation can improve a brief when it is
constrained. The useful pattern was not "add all interpretation fields." The
useful pattern was a short plain-language section that explains:

- what may already have been present;
- what the audit process appears to have sharpened;
- what remains uncertain.

PR138 found that pattern stable enough to formalize rules before any builder or
broader automation.

## Fields Allowed In The User-Facing Enrichment

The following interpreted fields may feed the user-facing brief:

- `decision_question`
- `likely_starting_direction`
- `revised_direction_or_action_consequence`
- `decision_thresholds`
- `evidence_gates`
- `useful_friction`
- `what_the_final_answer_does_not_prove`

Rules:

- `likely_starting_direction` must show uncertainty.
- `useful_friction` must be descriptive, not a score.
- action consequence must not say Lolla caused everything.
- every field must preserve source refs and uncertainty.
- every field must say if human review is required.
- every field must not be used as a quality label.

## Evidence-Only Fields

The following fields must stay evidence-only or unresolved unless a future
explicit approval slice changes the rule:

- `live_options`
- `abandoned_or_rejected_options`
- `noisy_friction`
- `lost_value`
- `user_values_or_priorities`
- `stakeholder_obligations`
- `assistant_influence_on_user_framing`
- `sycophancy_or_over_accommodation_risk`
- `safe_to_show_user`
- `safe_for_agent_inspection_only`

These fields may matter, but the current checked-in-safe reads do not support
turning them into smooth user-facing claims.

## Enrichment Section

The user-facing section is:

```text
What the interpretation adds
```

Its purpose is narrow:

- clarify what appears sharpened;
- clarify what may already have been present;
- keep uncertainty visible.

It must not become a field dump, source-status inventory, quality label, or
claim that Lolla improved the decision.

## Builder Requirements For PR140

A future builder must:

- accept an original rendered brief;
- accept an interpretation read;
- accept this rules contract;
- output a separate enriched Markdown file;
- preserve the original brief unchanged;
- include only allowed user-facing fields;
- list excluded fields in Evidence and limits or review JSON;
- preserve non-claims;
- preserve source and privacy limits;
- make no model calls;
- invoke no runtime;
- run no Lolla skill;
- mutate no archives.

## Non-Claims

This contract is not:

- runtime integration;
- product proof;
- human validation;
- answer-quality scoring;
- agent action authorization;
- a model-call implementation;
- a broad judge;
- a customer-readiness claim.

## Decision Gate

PR139 produces a coherent rules contract and tests it. The next slice may build
the deterministic offline builder:

```text
PR140 Offline Enriched Brief Builder v0
```

That builder must remain offline, deterministic, source-preserving, and
non-claiming.

## Follow-On Status

PR140 implements the offline builder required by this contract. It creates
separate builder-enriched launch-beta and intake-routing Markdown files without
overwriting original briefs or hand-built enriched examples.

PR141 reviews those generated outputs. The review finds the rules worked:
allowed fields entered the enrichment, evidence-only fields stayed out of the
main body, and non-claims remained visible. The review also finds the output is
too templated compared with the hand-built examples, so it gates to:

```text
proceed_to_builder_rule_patch
```

Runtime integration remains out of scope.
