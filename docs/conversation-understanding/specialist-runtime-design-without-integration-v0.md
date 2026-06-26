# Specialist Runtime Design Without Integration v0

PR29C designs how the existing specialist extractors could later enter a
product path. It does not integrate them.

This note uses PR29B evidence to decide where specialist calls might belong,
what gates they would need, and what they must not imply.

## Context

PR29B ran the existing specialist extractors on four modern baseline archives:

| metric | value |
|---|---:|
| model calls | 12 |
| estimated cost USD | 0.008547 |
| boundary status | `ok:12` |
| provider-boundary warnings | 12 |
| live-constraints runs improved | 4/4 |
| stance-lineage runs improved | 4/4 |
| dropped-thread runs improved | 4/4 |
| validated candidates | all candidates |
| grounding | all span-level |

The result supports one conclusion:

```text
existing_specialists_worth_later_runtime_design
```

It does not support immediate runtime integration. It also leaves
`user_values_or_priorities_signal` unsolved because the current specialists do
not extract user values or priorities.

## Design Decision

Specialist extraction should not run during normal `$lolla` by default.

The recommended product path is:

1. Keep normal `$lolla` unchanged.
2. Keep specialist extraction as an explicit, operator-approved deeper mode or
   offline review path first.
3. Preserve semantic coverage deltas as the acceptance surface.
4. Require validated, span-grounded events before any specialist output can
   influence archived semantic coverage.
5. Treat provider-boundary warnings separately from extractor quality.
6. Keep user-values extraction out of scope.

The specialists make runs more inspectable. They should not, by themselves,
make a degraded run safe for agent use.

## Candidate Modes

### Mode 0: No Specialist Calls

This remains the default.

Normal `$lolla` should continue to use the current artifact chain without extra
specialist model calls. This protects latency, cost, provider-boundary exposure,
and the current run contract.

Use when:

- the user runs ordinary `$lolla`;
- no explicit deeper review is approved;
- model-call budget is unavailable;
- provider-boundary strictness is the priority.

### Mode 1: Offline Operator-Approved Probe

This is the current safe path proven by PR29A and PR29B.

Specialists run against existing archives. Outputs are written outside archive
folders unless a later PR explicitly adds archive integration.

Use when:

- the operator wants to inspect semantic coverage improvement;
- model-call cost is explicitly approved;
- outputs can remain local-only;
- no runtime behavior should change.

This mode is recommended for the next real use of the specialists.

### Mode 2: Explicit Deep Review Mode

This is a possible future product mode, not implemented here.

In this mode, a user or operator explicitly asks for deeper semantic review
after the normal run. Specialist calls would be opt-in and cost-gated. The
result would be a separate specialist-enrichment artifact or report, not a
silent change to the revised answer.

Use only if later evidence shows:

- specialists improve semantic coverage beyond the four-run probe;
- output remains custody-safe;
- provider-boundary warnings are handled by existing run-health policy;
- the cost and latency are acceptable to the operator.

### Mode 3: Runtime Archive Integration

This is later work and should remain blocked for now.

If integrated, specialist outputs would need a durable artifact contract,
reasoning-trace indexing, evaluation checks, semantic coverage deltas, and
agent-result summary rules. That is a separate design and implementation
sequence.

Do not implement this until offline and explicit deep-review modes prove stable
on a broader modern sample.

## Cost And Approval

Specialist calls must be explicit and budgeted.

Recommended initial cap:

| item | value |
|---|---:|
| specialists | 3 |
| calls per run | 3 |
| models/providers | OpenRouter only until provider-specific telemetry expands |
| approval | explicit flag or operator action |
| default hidden calls | 0 |

Any future product mode should surface:

- expected maximum call count;
- provider and requested model;
- actual served model when available;
- token usage when available;
- estimated cost;
- whether cost telemetry is complete, partial, or unavailable.

If complete cost telemetry is unavailable for a provider, the mode should be
rejected or clearly marked as unsupported. PR29B intentionally kept real-probe
cost telemetry OpenRouter-only.

## Output Custody

Specialist outputs should stay custody-bounded.

They may include:

- event counts;
- validation counts;
- validation failure categories;
- grounding counts;
- turn indexes;
- span offsets or span hashes when supported;
- semantic coverage deltas;
- model-call count and cost metadata;
- provider-boundary warning counts.

They must not include:

- raw transcript text;
- memo text;
- revised-answer text;
- raw model messages;
- provider reasoning details;
- failed quote text;
- absolute archive paths;
- control argument values;
- credentials or secret markers.

Output paths must remain outside archive folders unless a future archive
integration PR defines and tests the artifact contract.

## Archive Options

There are three possible archive strategies.

### Option A: External Report Only

Recommended for now.

The specialist result stays outside the archive, normally under `/tmp` or a
review workspace. The archive remains immutable. The report can be regenerated
from the archive plus explicit model calls.

Tradeoff: best custody isolation, weaker long-term reproducibility unless the
operator preserves the external report.

### Option B: Optional Archived Specialist Artifact

Possible later.

If later approved, a specialist artifact could be archived as a separate
product surface. It would need:

- schema version;
- source scope flags;
- no raw text leakage;
- validation counts;
- coverage deltas;
- model-call and cost receipt;
- provider-boundary warning summary;
- reasoning-trace indexing;
- evaluation custody checks.

Tradeoff: stronger reproducibility, higher archive surface area and privacy
responsibility.

### Option C: Fold Into Existing Extraction

Not recommended.

Folding specialist output directly into `extraction.json` risks making optional
semantic enrichment look like baseline extraction. It also makes it easier to
smuggle a broader IR into runtime without a clean artifact boundary.

## Semantic Coverage

Specialist outputs should be judged by semantic coverage deltas, not by how
plausible the extracted text sounds.

The target elements are:

- `live_constraints`;
- `assistant_stance_or_recommendation_lineage`;
- `dropped_or_under_carried_threads`.

The expected improvement is:

- `turn_ref` or `artifact_present_only` grounding becoming `span` grounding;
- `partial` status becoming stronger when validated evidence exists;
- review-needed notes becoming more specific;
- validation failures remaining visible.

The current specialists should not change:

- `user_values_or_priorities_signal`;
- answer-quality scoring;
- agent readiness;
- provider-boundary policy.

## Evaluation Implications

If specialist artifacts are ever archived, `evaluation.json` should initially
check custody, not semantic correctness.

Possible future checks:

- artifact present when the mode claims it ran;
- schema version valid;
- no raw text leakage markers;
- model-call receipt present;
- output path not inside archive before archive finalization;
- validation counts internally consistent;
- semantic coverage delta block present;
- provider-boundary warnings surfaced.

Evaluation should not say the conversation was understood correctly. It should
only say the specialist artifact is present, shaped correctly, and custody-safe.

## Agent Result Implications

Specialist success should make a run more inspectable, not automatically more
usable.

Future `agent_result.json` integration, if any, should summarize only:

- specialist mode used;
- validated event counts;
- target elements improved;
- review-needed count;
- provider-boundary warning count;
- cost receipt state.

It should not:

- approve an action;
- override provider-boundary degradation;
- convert a partial run into a clean run;
- hide validation failures;
- expose raw specialist claims as instructions to an agent.

## Validation Failure Policy

Invalid specialist candidates should be dropped and counted.

Recommended behavior:

- drop invalid candidates from enhanced coverage;
- record failure categories;
- keep baseline semantic coverage available;
- mark the specialist as not improving its target element when validated event
  count is zero;
- do not degrade the whole run solely because optional specialist validation
  failed;
- do not retry automatically without an explicit budget and retry policy.

If validation failures dominate on a broader sample, the decision should be
`keep_offline_or_research`, not runtime integration.

## Provider-Boundary Handling

PR29B saw provider-boundary reasoning metadata warnings on all 12 specialist
calls. That must stay separate from extractor quality.

Design rules:

- do not export provider reasoning details;
- count provider-boundary warnings;
- keep current provider-boundary policy unchanged;
- do not let specialist success cancel provider-boundary degradation;
- do not treat provider-boundary warnings as validation failures;
- require the final product surface to say whether the run is more inspectable
  or more usable.

Under current policy, contained provider-boundary warnings can still make an
agent-facing result partial or degraded even when specialist extraction itself
validated cleanly.

## Preventing Hidden IR Drift

Specialist integration must not become a hidden
`conversation_understanding_ir.v0`.

Guardrails:

- use current `ConversationContext` and current `ConversationIR` injection
  points unless a later PR explicitly designs a new durable IR;
- keep raw transcript as source of truth;
- keep specialist outputs in a separate artifact or external report;
- preserve baseline versus enhanced semantic coverage comparison;
- avoid new global ontology fields;
- avoid broad memory, retrieval, graph, embedding, or chunking changes;
- do not make specialist outputs authoritative without validation and review.

If a new durable IR becomes necessary, it should be justified by repeated
missing fields and designed as its own PR.

## User Values Are Out Of Scope

`user_values_or_priorities_signal` remains unsolved.

The current specialists do not extract user values or priorities. That is not a
bug in PR29B; it is a boundary.

User-values extraction is more interpretive and riskier than identifying
constraints, stance shifts, or dropped threads. It can easily overstate what a
user cares about unless it is source-grounded, reviewable, and carefully
worded.

Do not include user-values extraction in any specialist runtime integration
proposal. Treat it as a separate future design question.

## Recommended Next Step

The next implementation step should not be runtime integration.

Recommended sequence:

1. Keep PR29B as evidence that specialists are worth designing around.
2. Use this design as the boundary for any future explicit deeper-mode or
   offline specialist-enhanced semantic coverage work.
3. Before runtime integration, run a broader approved modern sample and confirm
   that specialists still improve coverage with acceptable cost, validation,
   and provider-boundary behavior.
4. Only then design archive integration, evaluation checks, or agent-result
   summaries.

## Non-Goals

- no `$lolla` runtime changes;
- no `SKILL.md` changes;
- no prompt changes;
- no `archive_run.py` integration;
- no semantic coverage archive integration;
- no specialist artifact archive generation;
- no graph DB;
- no embeddings;
- no chunking;
- no `conversation_understanding_ir.v0`;
- no user-values extractor;
- no LLM judge;
- no answer-quality scoring;
- no provider-boundary policy change;
- no automatic human-review labels.
