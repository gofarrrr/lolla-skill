# Reasoning portfolio two-stage holdout protocol v0

Status: prospective evaluation protocol; no runtime behavior authorized

## Purpose

Test whether Lolla-selected pressure changes a fresh reconsideration beyond a
strong transcript-only control without choosing the treatment prompt after
seeing the control. Case09 showed that freezing only the semantic gate is not
enough: a treatment arm also needs a frozen provider, model, prompt shape,
output cap, and typed output contract.

## Stage A — pipeline admission

Before any Stage A call, freeze:

- source conversation path and hash;
- extraction and pipeline code/artifact hashes;
- capture, fabrication, stage-call, total-call, and cost ceilings;
- an outer wall-clock ceiling, not only a provider socket timeout;
- preliminary novelty thresholds;
- stop rules and non-claims.

Hash custody includes transitive code that can change admission semantics or
artifact persistence, not only the top-level scripts. At minimum, a future
contract must lock the shared quote matcher and any output-path preflight used
by extraction. Optional `additional_hash_locks` carry `path`, `sha256`, and a
short reason so the sealer can verify these dependencies without growing a
case-specific schema.

Run extraction and the pipeline once, with only the predeclared quote-repair
path allowed. Seal review-safe snapshots. Stop if admission or preliminary
novelty fails.

Provider-bound call evidence must be persisted on every terminal extraction
path, including provider error, empty or invalid JSON, `not_strategic`, missing
required fields, and quote-repair failure. The receipt distinguishes a call
attempt, a persisted call record, and an admissible extraction. If a call was
attempted but usage evidence is absent, call count, tokens, served model, and
cost are `unknown`; a numeric zero is forbidden. Missing call evidence is an
admission failure even when the conversation capture and error artifact are
otherwise complete.

The prospective implementation is
`lolla.extraction_admission_smoke_contract.v1`. It freezes separate provider
and outer wall-clock timeouts and consumes the
`lolla.extraction_call_custody.v0` block. Provider-free verification of this
machinery does not itself satisfy Stage A; a new designated non-holdout smoke
must still pass before an untouched holdout is selected.

The Case 01 contract-v1 non-holdout smoke has now passed. This clears the
pre-Stage-A operability gate only. A new untouched case may be selected and its
Stage A extraction-plus-pipeline contract frozen prospectively. Stage B remains
forbidden until that Stage A result passes and its source-traceable pressure
packet is locked before either downstream arm.

Stage A may determine whether a downstream experiment is worth constructing.
It must not expose a control answer that could be used to tailor treatment.

## Stage B — paired downstream contract

Only after Stage A passes, a reviewer may construct the source-traceable
pressure packet. Before **either** downstream call, hash-lock one contract
containing:

- the complete conversation hash and original-answer boundary;
- pipeline gate, private-table/V60 snapshot, pressure-review, and packet
  hashes;
- the strong-control and treatment arm definitions;
- identical provider, model, temperature, reasoning configuration, neutral
  instruction, maximum output tokens, timeout, and typed output schema;
- randomized blind labels;
- exactly one generation call per arm, zero evaluator calls, and no retry;
- source-fidelity red lines and stop rules.

The control receives the complete conversation and neutral reconsideration
task. The treatment receives those identical inputs plus a small pressure
packet. Pressure must be framed as questions to consider, not expected
conclusions. The generator must not receive expected deltas, provisional
review labels, or the comparison rubric.

The paired arms should run from the same frozen contract, preferably together,
using `scripts/evals/run_downstream_utility_pilot.py`. Its prospective
`output_contract.field_types` support should be used so arrays cannot silently
arrive as bullet-delimited strings.

Recommended field types:

```json
{
  "decision_state_read": "string",
  "updated_position": "string",
  "what_survived": "array_of_strings",
  "take_backs_or_set_aside": "array_of_strings",
  "material_shifts": "array_of_objects",
  "next_actions": "array_of_strings",
  "uncertainties": "array_of_strings"
}
```

Each `material_shifts` object must contain exactly three strings: `shift`,
`source_basis`, and `action_consequence`.

When a treatment requires per-pressure dispositions, the typed contract must
also constrain each returned `pressure_id` to the exact frozen packet IDs.
Semantic similarity or a friendly renamed label is not valid custody. Review
must compare `visible_effect` and `private_guardrail` against the actual
material shifts and public output; a private label cannot hide visible use.

## Review and stopping

Review remains separate from generation. Compare source fidelity, preserved
value, unique actionable pressure, forcing, noise, bloat, and traceability.

Stop after the paired calls when:

- control contains the same material delta;
- treatment is only longer, more cautious, or better organized;
- treatment forces a selected model onto the case;
- either arm fabricates facts, loses a non-negotiable constraint, or makes an
  unsupported reversal;
- treatment creates no distinct action, evidence gate, sequence, stop rule,
  question, or important private guardrail.

A positive pair remains provisional. It cannot authorize runtime integration,
product claims, or graph promotion. Case09 must not be rerun under this repair;
the protocol applies to another untouched holdout.
