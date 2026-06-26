# Specialist Extractor Offline Probe v0

PR28 reviews whether existing specialist extractors can address the repeated
semantic coverage gaps found by PR27 before Lolla invents a new IR, new
extractor, graph memory, embeddings, or runtime integration.

This is a docs-only probe plan. It does not run specialist extractors, call
models, change prompts, mutate archives, or change normal `$lolla` behavior.

## Why This Probe Exists

PR27 showed a repeated corpus-level pattern:

- `user_values_or_priorities_signal`: `not_measured` in `67/67` records.
- `assistant_stance_or_recommendation_lineage`: `partial` in `67/67`.
- assistant stance grounding: `artifact_present_only` in `67/67`.
- `live_constraints` grounding: `turn_ref` in `66/67`, `none` in `1/67`.
- most records are still legacy semantic backfill, so runtime architecture
  should not overfit old artifact limits.

The right next question is narrower than "build conversation understanding":

> Can existing specialist extractors improve grounding offline?

## Existing Specialist Extractors

The relevant existing modules are:

- `engine/system_b/live_constraints_extraction.py`
- `engine/system_b/stance_extraction.py`
- `engine/system_b/dropped_threads_extraction.py`
- `engine/system_b/ir_constructor.py`

The extractor APIs already produce source-grounded IR objects when they
validate:

| extractor | output object | intended grounding | source surface | model call required |
|---|---|---|---|---|
| `extract_live_constraints(...)` | `UserIssueEvent` | `span` or `derivation` | user turns | yes |
| `extract_stance_events(...)` | `StanceEvent` | `span` | assistant turns | yes |
| `extract_dropped_threads(...)` | `UserIssueEvent` | `span` | user and assistant turns | yes |

Each extractor takes a `ConversationContext` and a `boundary` object with
`run_json(...)`. Candidate events come from the boundary call, then local
validation drops invalid turns, invalid taxonomy labels, and non-substring
claims. The validation layer is useful and deterministic, but candidate
generation is LLM-backed.

The IR constructor already supports injectable hooks:

- `stance_extractor`
- `live_constraints_extractor`
- `dropped_threads_extractor`

Default construction does not use these hooks. That is good: normal runtime
behavior stays unchanged unless a future PR explicitly wires them in.

## Modern Sample

The first probe sample should reuse the four modern current-main archives:

| case | run_id |
|---|---|
| `launch-limited-beta-workflow` | `20260626T125112Z_b861fd` |
| `initiate-pre-sale-coffee` | `20260626T131939Z_368960` |
| `implement-price-increase-three` | `20260626T132915Z_49172d` |
| `five-person-saas-team` | `20260626T133147Z_99712f` |

Current PR26/PR27 coverage for the sample:

| element | beta workflow | coffee pre-sale | pricing renewal | five-person SaaS team |
|---|---|---|---|---|
| `live_constraints` | partial / `turn_ref` | partial / `turn_ref` | partial / `turn_ref` | partial / `turn_ref` |
| `changed_constraints_or_later_pushback` | partial / `turn_ref` | not measured / `none` | not measured / `none` | not measured / `none` |
| `dropped_or_under_carried_threads` | partial / `turn_ref` | not measured / `artifact_present_only` | not measured / `artifact_present_only` | not measured / `artifact_present_only` |
| `assistant_stance_or_recommendation_lineage` | partial / `artifact_present_only` | partial / `artifact_present_only` | partial / `artifact_present_only` | partial / `artifact_present_only` |
| `user_values_or_priorities_signal` | not measured / `none` | not measured / `none` | not measured / `none` | not measured / `none` |

This table contains only coverage labels and grounding types. It does not copy
raw transcript, memo, revised-answer, model-message, provider-reasoning, or
failed-quote text.

## Probe Shape

A future offline runner should:

1. Load one archive run directory.
2. Build `ConversationContext` from `conversation.txt` and `extraction.json`.
3. Build the baseline PR26 semantic coverage report.
4. Run selected specialist extractors through an explicit boundary client.
5. Rebuild `ConversationIR` using the constructor injection hooks.
6. Compare baseline coverage against specialist-enhanced coverage.
7. Export only counts, grounding types, validation stats, hashes, artifact
   availability, and improvement flags.

The runner should be local-only and should not write into archive folders.

## Expected Call Shape

For the four-run sample, a full probe of all three existing specialists would
require:

| specialist | calls per run | four-run sample calls |
|---|---:|---:|
| live constraints | 1 | 4 |
| stance events | 1 | 4 |
| dropped threads | 1 | 4 |
| total | 3 | 12 |

Estimated cost is not recorded here because the probe did not run model calls
and cost depends on the configured boundary model and provider pricing. A
future runner should record requested model, served model when available,
input/output tokens, estimated cost, and validation counts per call.

## Probe Output Contract

For each sampled run, a future probe should report:

- baseline semantic coverage status and grounding;
- specialist attempted: live constraints, stance, dropped threads;
- whether model calls were made;
- requested model and cost estimate if model calls were made;
- raw candidate count;
- validated event count;
- validation failure counts;
- grounding counts: `span`, `turn_ref`, `derivation`, `none`;
- whether the semantic coverage report would improve;
- whether output looks stable enough to consider later integration.

Do not include:

- raw transcript text;
- memo text;
- revised-answer text;
- model messages;
- provider reasoning details;
- failed quote text;
- absolute local archive paths;
- control argument values.

## What Existing Specialists Can And Cannot Address

Likely addressable:

- `live_constraints`: the existing specialist can emit span-grounded user-side
  constraints and derivation-grounded cross-turn constraints.
- `assistant_stance_or_recommendation_lineage`: the existing stance specialist
  can emit span-grounded assistant stance events.
- `dropped_or_under_carried_threads`: the existing dropped-thread specialist can
  emit span-grounded user or assistant open-loop events.

Not addressed by current specialists:

- `user_values_or_priorities_signal`: no existing first-class specialist emits
  user values or stated priorities. Keep this as a separate future design
  question.

Unproven until a real probe:

- whether extracted events are stable across runs;
- whether validation drops too many candidates;
- whether cost is acceptable;
- whether specialist-enhanced IR actually improves PR26 coverage enough to
  justify integration.

## Decision Outcome

Outcome: **E. Probe cannot be run cleanly in this PR without significant
harness/model-call work.**

Reason: all three existing specialist extractors require an LLM boundary call
to generate candidate events. The deterministic validation code is ready, and
the IR constructor injection points exist, but a real probe needs an explicit
boundary/cost/custody runner with model-call approval.

Secondary outcome: **D. Existing specialists do not address user values.**

Reason: user values and priorities remain `not_measured` in PR27 and no current
specialist produces a first-class values/priorities event.

## Recommended Next Slice

Recommended next slice:

`specialist_extractor_probe_runner_v0`

Scope:

- offline/local only;
- explicit model-call approval before use;
- fixed four-run modern sample;
- no archive mutation;
- no runtime integration;
- no production prompt changes;
- output only counts, grounding, validation stats, and improvement flags.

If model calls are not approved, the next slice should stay docs-only and
define a fake-boundary fixture harness for validating output handling without
claiming real extraction quality.

## Non-Goals

- no `$lolla` runtime changes;
- no `SKILL.md` changes;
- no `archive_run.py` integration;
- no semantic coverage report archive integration;
- no production extraction prompt change;
- no new user-values extractor;
- no graph DB;
- no embeddings;
- no chunking;
- no `conversation_understanding_ir.v0`;
- no LLM judge;
- no answer-quality scoring;
- no provider-boundary policy change;
- no automatic human-review labels.
