# Reasoning-process model/operator selection result

Status: provider compatibility resolved; no tested model passes the combined semantic contract  
Date: 2026-07-12

## Simple result

The Google failure was real but incomplete. Gemini 3.1 Flash Lite rejected the
v4.2 schema before inference. The exact same 3,597-byte schema was accepted by
GLM 5.2 through DeepInfra, DeepSeek V4 Flash and Pro through Alibaba, and
MiniMax M3 through Parasail. The schema is therefore not universally invalid or
too complex.

Changing providers solved transport. Changing to stronger models did not solve
semantic reliability.

| Model/operator pair | Wire | Local disposition | Source review | Observed behavior |
|---|---|---|---|---|
| DeepSeek V4 Flash / Alibaba | Pass | Admitted after v4.3 | Fail | Closest result, but denies the visible starting role while describing it in trajectory prose. |
| GLM 5.2 / DeepInfra | Pass | Reviewed empty | Fail | Invents a schema mismatch and returns `not_found`. |
| DeepSeek V4 Pro / Alibaba | Pass | Quarantined | Fail | Repeats the missing starting-component defect at much higher cost. |
| MiniMax M3 / Parasail | Pass | Reviewed empty | Fail | Treats the undecided starting preference as no starting state. |

DeepSeek V4 Flash through Alibaba is the cheapest and closest development
candidate, not a production winner. Its clarified v4.3 call cost about
$0.00030. DeepSeek V4 Pro cost about $0.00291 and did not repair the defect.
General benchmark strength did not predict Lolla source fidelity on this task.

## What changed in v4.3

The DeepSeek v4.2 compatibility output exposed an unfair contract gap. Our
deterministic validator required every non-empty starting/current/qualification
role to have a matching stance component, but that cross-field rule was only
implicit in the prompt and cannot be expressed by the current provider schema.

V4.3 made that existing rule explicit in one prompt sentence. It did not change
the provider schema, validator, semantic vocabulary, compiler boundary, or
deterministic/LLM division of labor.

The correction allowed DeepSeek V4 Flash to produce an admitted record, but
source review still failed because the model avoided the requirement by
declaring the visible starting role empty. This is useful evidence: the issue is
not merely schema syntax or an unstated mechanical rule.

## What we learned about model selection

We must select a model/operator pair through three separate gates:

1. **Wire compatibility:** can the provider accept the exact structured-output
   request?
2. **Contract execution:** can the model return a locally admissible object?
3. **Source fidelity:** does the admitted object preserve the actual starting,
   current, qualification, and trajectory meanings without omission or
   strengthening?

Wire success is not intelligence. Deterministic admission is not semantic
correctness. A general intelligence benchmark is a useful shortlist signal but
not a Lolla eval.

The live July 2026 scan used OpenRouter's current model and endpoint catalogs,
strict structured-output support, exact provider pinning, and no fallbacks.
OpenRouter recommends checking supported parameters and using
`require_parameters: true`; our probes did so. See [structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs),
[provider routing](https://openrouter.ai/docs/guides/routing/provider-selection),
and the [models API](https://openrouter.ai/docs/guides/overview/models).

## Call custody

One first batch exposed a harness defect: its aggregate artifact was written
only after both calls, so process termination left the external call count
unknown. We did not rerun that contract. The replacement runner writes a durable
started marker and per-call result before moving to the next job. That custody
pattern is now required for future batches.

The preserved successful calls cost $0.005799432 in total. One DeepInfra call
returned a pre-inference 429 with no retry. The interrupted batch may have made
zero, one, or two additional calls, and its cost cannot be attributed with the
available non-management API key.

## Decision and next work

The model search is complete for this combined contract. No additional model,
reserved-case, graph, runtime, stability, or integration call is authorized.
The agency-acquisition case remains untouched.

The evidence supports a smaller semantic decomposition, not more deterministic
semantic gates:

1. one LLM microtask extracts starting, current, qualification, and trajectory
   with exact evidence;
2. a separate LLM microtask decomposes stance objects for one declared role and
   evidence set at a time;
3. deterministic code joins only exact role/evidence identifiers, validates
   shapes, and preserves missingness or disagreement;
4. DeepSeek V4 Flash / Alibaba is the first low-cost development operator after
   provider-free contracts pass;
5. the reserved agency case remains closed until a synthetic development case
   and a distinct transfer fixture both pass source-first review.

This is the same product direction—probabilistic interpretation plus
deterministic custody—but with smaller jobs that better match what models do
reliably.

Primary evidence:

- `research/reasoning-process-model-operator-selection-2026-07-12/current-practice-snapshot.json`;
- `research/reasoning-process-model-operator-compatibility-2026-07-12/custody-incident.json`;
- `research/reasoning-process-model-operator-compatibility-recovery-2026-07-12/result.json`;
- `research/reasoning-process-deepseek-alibaba-compatibility-2026-07-12/result.json`;
- `research/reasoning-process-model-operator-v43-development-2026-07-12/source-review.json`;
- `research/reasoning-process-model-operator-v43-controls-2026-07-12/result.json`;
- `research/reasoning-process-model-operator-selection-2026-07-12/terminal-review.json`.
