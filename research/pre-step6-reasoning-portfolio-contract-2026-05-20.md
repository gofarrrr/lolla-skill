# Pre-Step-6 Reasoning Portfolio Contract

Date: 2026-05-20

Status: research-only contract. This file does not change default `/lolla`
runtime behavior, `SKILL.md`, public output, or promotion policy.

Source PRD: `plans/lolla-solver-control-layer-prd-2026-05-19.md`

## Purpose

Build a local experiment for preparing Step 6 with a compact reasoning
portfolio instead of a raw artifact dump or a narrow monolithic control note.

Core rule:

```text
No artifact dump. No premature pruning.
Cap prose, not possibility.
Broad availability, compact representation, delayed rejection.
```

The deterministic layer may preserve source refs, enforce schemas, route
candidates, apply attention budgets, keep protected slots, and record receipts.
It may not decide final advice or silently erase off-frame material just
because it looks low-fit.

## Runtime Policy

All new artifacts in this contract use:

```json
{
  "status": "research_only",
  "runtime_policy": "runtime_dormant"
}
```

Automated tests must use static fixtures or deterministic baselines. Provider,
OpenRouter, and sub-agent calls are manual-only and must not run inside tests.

## Autoresearch Loop

This experiment should be iterated using the local autoresearch program:

```text
research/pre-step6-autoresearch-program-2026-05-20.md
```

The adapted loop is:

```text
hypothesis -> smallest research-only change -> fixed case-suite evaluation
-> log keep/retest/discard/boundary_case -> repeat
```

Unlike Karpathy's training setup, Lolla does not have one scalar metric like
validation bits per byte. The fixed evaluation is a case suite plus rubric:

- founder high-clutter for positive edge-pressure preservation;
- PhD for live-tension and active/parked placement;
- consultant for negative-control stand-down behavior;
- mother for humane weak-evidence negative-control behavior.

The loop must optimize for quality of Step 6 context, not prompt minimalism by
itself. A simpler handoff is a win only if it preserves breadth, source
grounding, and off-frame reasoning receipts. A broader handoff is a win only if
it improves Step 6 without public bloat or over-control.

## Schemas

### problem_state.v1

Describes the problem without solving it.

Required fields:

- `schema_version`
- `status`
- `runtime_policy`
- `case_id`
- `source_refs`
- `user_goal`
- `problem_type`
- `knowns`
- `unknowns`
- `constraints`
- `success_condition`
- `missing_user_owned_info`
- `suggested_next_move`
- `why`

Allowed `problem_type` values:

```text
decision_evaluation
action_planning
causal_diagnosis
critique
explanation
prediction
design
unclear
```

Allowed `suggested_next_move` values:

```text
answer_now
ask_user
audit_first
stop_capture_or_scope_issue
stop_insufficient_grounding
```

### candidate_inventory.v1

Lists candidate reasoning material from existing engineered artifacts. It
preserves availability and source/expansion refs. It does not decide usefulness.

Required fields:

- `schema_version`
- `status`
- `runtime_policy`
- `case_id`
- `source_refs`
- `candidates`

Each candidate requires:

- `candidate_id`
- `origin`
- `artifact_ref`
- `selection_basis`
- `summary`
- `source_refs`
- `expansion_ref`

### reasoning_affordance.v1

Names what one candidate might reveal, what boundary controls it, and how Step
6 can test it cheaply.

Required fields:

- `schema_version`
- `status`
- `runtime_policy`
- `case_id`
- `artifact_id`
- `source_refs`
- `selection_basis`
- `affordance_class`
- `protected_slot`
- `what_it_might_reveal`
- `source_grounding`
- `cheap_test_for_step6`
- `hard_boundary`
- `relaxation_condition`
- `discard_condition`
- `risk_if_forced`
- `risk_if_ignored`
- `attention_weight`
- `expansion_ref`

Allowed `affordance_class` values:

```text
direct_pressure
structural_lens
contrarian_edge
weak_signal
negative_space
duplicate_support
false_friend
parked_receipt
```

Allowed `protected_slot` values:

```text
inversion
denominator
incentive
disconfirmation
opportunity_cost
lollapalooza
model_forcing_risk
sequence_stop_rule
negative_space
none
```

Allowed `attention_weight` values:

```text
active
brief
scan
parked
```

### step6_attention_map.v1

Fan-in object for Step 6. It is a private attention map, not a verdict.

Required fields:

- `schema_version`
- `status`
- `runtime_policy`
- `case_id`
- `source_refs`
- `problem_read`
- `active_working_set`
- `edge_latticework_reserve`
- `weak_or_negative_space_receipts`
- `parked_but_preserved`
- `ask_user_if_any`
- `review_admission`
- `full_archive_refs`
- `step6_instruction`

Allowed `review_admission` values:

```text
none
optional_review
manual_only
stop_insufficient_grounding
```

### lens_probe.v1

Private cognitive enrichment probe for a named lens pack. It maps the lens onto
already surfaced artifacts and attention-map material. It does not choose the
answer, does not add public labels, and does not become a new default lane.

Initial allowed lens packs:

```text
bevelin_seeking_wisdom_v0
polya_problem_solving_v0
```

Required fields:

- `schema_version`
- `status`
- `runtime_policy`
- `case_id`
- `lens_pack`
- `source_refs`
- `problem_state_ref`
- `attention_map_ref`
- `lens_candidates`
- `off_narrative_preservation`
- `do_not_force`

Each `lens_candidate` requires:

- `lens_id`
- `lens_name`
- `why_it_might_matter`
- `source_hooks`
- `supported_by_artifact_ids`
- `cheap_test_for_step6`
- `risk_if_forced`
- `risk_if_ignored`
- `suggested_attention`
- `false_friend_warning`

Allowed `suggested_attention` values:

```text
active
scan
parked
```

The `off_narrative_preservation` field exists to prevent early castration of
strange but potentially useful material. It preserves one item as `scan` or
`parked`, with a reactivation condition and a force-risk warning.

### lens_answer_core.v1

Research-only answer-core candidate produced after applying a lens probe to an
attention map. It is used to compare whether the lens improves Step 6 output.
It is not runtime behavior.

Required fields:

- `schema_version`
- `status`
- `runtime_policy`
- `case_id`
- `lens_pack`
- `source_attention_map`
- `source_attention_map_render_sha256`
- `source_lens_probe`
- `answer_core`
- `expected_inclusions`
- `expected_exclusions`
- `lens_effect`

`answer_core` must be public-clean. It must not expose private terms such as
`attention map`, `portfolio`, `artifact`, `bundle`, `worker`, `lens pack`,
`lens probe`, `Bevelin`, or `Munger`.

`lens_effect` requires:

- `preserved_from_base`
- `changed_by_lens`
- `kept_private_or_discarded`

### lens_comparison.v1

Research-only comparison gate for rendered-hybrid, base-portfolio, and
lens-enhanced answer cores.

Required fields:

- `schema_version`
- `status`
- `runtime_policy`
- `experiment_id`
- `case_id`
- `comparison_kind`
- `lens_pack`
- `candidate_refs`
- `criteria`
- `tie_break_rule`
- `aggregate_winner_arm`
- `aggregate_decision`
- `promotion_read`

Required rubric order:

```text
decision_usefulness
source_grounding
overclaim_risk
answer_length_cognitive_load
machinery_hygiene
conflict_preservation
edge_pressure_preservation
breadth_depth_preservation
premature_pruning_risk
negative_control_discipline
```

Allowed aggregate decisions:

```text
lens_improves
lens_retest
lens_boundary_case
lens_discard
```

Allowed promotion reads:

```text
expand_replay
retest
stop
discard
```

The promotion rule is intentionally asymmetric. A lens may be worth preserving
as a boundary insight even when it does not beat the previous answer. It may
only proceed to replay when it improves the fixed-suite comparison without
leaking machinery, narrowing useful breadth, or pushing negative controls to
over-promote.

### lens_step6_replay.v1

Research-only replay record for a lens-enhanced answer after the lens has
already passed the comparison gate.

Required fields:

- `schema_version`
- `status`
- `runtime_policy`
- `case_id`
- `replay_mode`
- `source_attention_map`
- `source_attention_map_render_sha256`
- `source_lens_answer_core`
- `prior_portfolio_replay`
- `lens_comparison_ref`
- `cognitive_gate`
- `replay_answer`
- `expected_inclusions`
- `expected_exclusions`
- `comparison_vs_prior_replay`
- `gates`
- `outcome`

The `cognitive_gate` is mandatory because replay quality is not a deterministic
property. It requires:

- `judgment_mode`
- `cognitive_question`
- `cognitive_inputs`
- `deterministic_checks`
- `cognitive_judgment`
- `why_this_is_not_deterministic`

Allowed `judgment_mode` values:

```text
human_static_research_judgment
manual_llm_reviewer_judgment
```

The deterministic layer validates:

- source refs and hashes;
- schemas and required fields;
- public-answer hygiene;
- inclusion/exclusion checks;
- comparison consistency;
- runtime and skill-promotion blocks.

The cognitive layer judges:

- whether the answer is more useful;
- whether the lens preserved meaningful edge pressure;
- whether the answer became bloated, abstract, or over-controlled;
- whether the lens pruned useful breadth too early;
- whether a negative-control case should stand down.

This is the intended gate shape:

```text
cognitive reviewer makes the quality judgment
deterministic validator constrains and records the judgment
```

The validator must never infer quality from counts alone.

### live_cognitive_gate.v1

Research-only live comparison record for blinded answer-core candidates. This
gate exists to test reviewer behavior, not to wire runtime selection.

Required fields:

- `schema_version`
- `status`
- `runtime_policy`
- `case_id`
- `gate_kind`
- `judgment_source`
- `provider_metadata`
- `candidate_refs`
- `blind_map`
- `reviewer_output`
- `static_expectation`
- `agreement`
- `gates`
- `notes`

The reviewer sees only blinded candidate labels and answer cores. The reviewer
must not see static expectations or source arm names. The important lesson from
the first live run is that answer-core replacement is too narrow: rendered
hybrid often wins because it preserves concrete case nuance that a shorter lens
answer core can accidentally shave off.

### context_composition_gate.v1

Research-only live comparison record for private Step 6 context packets. This
is the preferred experimental shape after the answer-core gate result.

Candidate arms:

```text
rendered_only
rendered_plus_bevelin_receipts
rendered_plus_polya_receipts
rendered_plus_dual_receipts
```

The comparison question is:

```text
Which private context packet best equips Step 6 without doing Step 6's job?
```

The gate must apply both enrichment pressure and a complexity tax:

```text
Do not prune useful edge pressure too early.
The smallest sufficient packet wins.
Each extra receipt carries a complexity tax unless it adds novel decision pressure.
```

The live result does not justify runtime promotion yet. No-tax composition
over-promoted dual receipts in negative controls. Complexity-tax composition
made negative controls safer, but left positive cases at `stop` or `retest`.
The next experiment should filter receipts for novelty against the rendered
anchor before asking the gate to compare.

### step6_card_deck.v1

Research-only private context deck for Step 6. This is the current best
expression of the non-castrating design: provide Step 6 with the clean hybrid
anchor plus private lens cards, then let Step 6 decide what to use, combine,
reject, defer, or keep private.

Required fields:

- `schema_version`
- `status`
- `runtime_policy`
- `case_id`
- `problem_read`
- `source_refs`
- `cards`
- `deterministic_limits`
- `step6_consideration_contract`
- `render_budget`

The initial card ids are:

```text
clean_hybrid_card
bevelin_card
polya_card
```

The deterministic layer may:

- validate source custody;
- label source arms privately;
- render the deck;
- preserve receipts and expansion refs;
- detect literal overlap hints;
- enforce public hygiene and runtime-promotion blocks.

It may not:

- decide cognitive usefulness;
- discard a card because it seems off-frame;
- rewrite lens material into final advice;
- force Step 6 to use every card visibly.

The deck renderer must include this limit in substance:

```text
Code validates custody, labels sources, and renders the deck; it does not
decide cognitive usefulness.
```

### card_deck_replay.v1

Research-only live replay where Step 6 receives the full private card deck and
returns a public-clean answer core plus a private card consideration ledger.

Required fields:

- `schema_version`
- `status`
- `runtime_policy`
- `case_id`
- `replay_mode`
- `source_card_deck`
- `provider_metadata`
- `step6_output`
- `gates`
- `notes`

`step6_output` requires:

- `answer_core`
- `private_card_consideration_ledger`

The ledger must account for all three initial cards in order. Allowed
dispositions:

```text
used
rejected
deferred
combined
private_guardrail
```

Each ledger item also records a private `novelty_role` so Step 6 can
distinguish visible contribution from private confirmation:

```text
visible_backbone
additive_pressure
confirming_support
private_guardrail
```

The replay prompt must preserve the user's core value:

```text
Use the cards to enrich Step 6, not to narrow Step 6.
Write as short as possible, but no shorter.
Do not compress away concrete tripwires, conditions, actor-specific steps, or
irreversible-risk distinctions merely to be concise.
The ledger is where card consideration lives; do not lengthen the public answer
merely to prove every card was considered.
Do not shorten by deleting concrete anchor payload such as named channels or
resources, communication boundaries, dated windows, gates, actor sequence,
tripwires, and evidence checks.
```

### card_deck_replay_comparison.v1

Research-only cognitive comparison of the visible clean-hybrid answer against
the visible card-deck Step 6 replay.

The reviewer is blinded. It receives answer A and answer B only, not source-arm
names and not `deck_effect`. The reviewer judges visible answer quality. The
deterministic layer privately maps the blind winner to:

```text
card deck wins -> improves
clean hybrid wins -> regresses
tie -> equivalent
```

This matters because the first live attempt exposed a gate bug: a blinded
reviewer cannot reliably report whether the card deck improved, because it
does not know which blind label is the deck. That mapping is bookkeeping, not
cognition. The cognitive act remains the blinded A/B/tie quality judgment.

The validator rejects internally inconsistent artifacts and keeps both product
promotion gates false:

```json
{
  "runtime_wiring_allowed": false,
  "skill_update_allowed": false
}
```

### card_deck_visibility_policy.v1

Research-only policy artifact for the stand-down case. This exists because a
card deck can improve private reasoning without needing to become the visible
answer. The policy records when Step 6's own ledger says non-anchor cards were
only confirming support or private guardrails, then pairs that deterministic
read with a cognitive comparison.

Required fields:

- `schema_version`
- `status`
- `runtime_policy`
- `case_id`
- `policy_kind`
- `source_refs`
- `ledger_summary`
- `deterministic_read`
- `cognitive_confirmation`
- `visible_policy`
- `gates`
- `notes`

Allowed `policy_kind`:

```text
ledger_based_anchor_standdown
```

The deterministic read may set `anchor_standdown_eligible: true` only when all
non-anchor cards are `confirming_support` or `private_guardrail`. It must also
set:

```json
{
  "deterministic_quality_decision": false
}
```

The visible policy may only choose an anchor-visible result after cognitive
confirmation:

```text
anchor_visible_after_cognitive_confirmation
card_deck_visible_after_cognitive_confirmation
retest_required
```

This keeps the distinction clean:

```text
code records Step 6's private ledger roles
cognition judges visible answer quality
```

## Attention Budgets

Research defaults:

- `active_working_set`: 4-7 target items, fewer allowed for small fixtures.
- `edge_latticework_reserve`: 6-12 target items, fewer allowed for small
  fixtures.
- `weak_or_negative_space_receipts`: 3-8 target items, fewer allowed for small
  fixtures.
- `parked_but_preserved`: render-budget capped.
- `step6_instruction`: max 90 words.

These budgets control prompt size. They are not a deterministic permission
system for what Step 6 may think about.

## Forbidden Language

Pre-Step-6 artifacts must not contain:

- final advice;
- answer outlines;
- "correct answer";
- "best option";
- "final recommendation";
- "Step 6 should conclude";
- "use this because it is correct";
- "drop this because it is not relevant";
- generic "add nuance";
- generic "improve clarity";
- runtime promotion;
- public model-name parade;
- hidden chain-of-thought style reasoning.

## TDD Rules

Use vertical slices:

```text
RED: one behavior test fails
GREEN: smallest implementation passes
REFACTOR: cleanup only after green
```

Tests should exercise public validator, renderer, or builder interfaces. They
should not mock private implementation details or assert internal call counts.

## Promotion Gate

Do not update default skill behavior until local evidence shows:

- fixtures validate;
- portfolio rendering is smaller and clearer than raw dump;
- protected edge material is preserved or receipted;
- negative-control cases can decline extra active pressure;
- comparison readouts identify falsifiers;
- intentional skipped post-Step-6 pressure checks remain valid receipts.
