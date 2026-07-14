# R3 task-shape current-practice check

Status: complete; provider-free design input

Date checked: 2026-07-13

Provider calls: zero

## Exact local signature

The repaired R3 request reached Gemini 3.1 Flash-Lite and returned strict JSON.
Eight of nine pressure rows had no mechanical finding. One row simultaneously
selected `park` and the material effect `uncertainty_change`, while leaving its
public and private effects empty. The response therefore passed transport and
syntax but failed one explicit cross-field business rule.

This check asks a narrower question than the earlier structured-extraction
research: what is current practice when a structured reasoning response is
schema-valid but two individually valid controlled fields contradict each
other? It does not assume that the model was overloaded.

## Sources checked

### Provider and routing documentation

- [Gemini structured outputs](https://ai.google.dev/gemini-api/docs/structured-output),
  last updated 2026-07-07. Google says Gemini supports a JSON Schema subset,
  recommends clear descriptions and strong types, requires applications to
  validate returned values, and explicitly calls for error handling when an
  output is schema-compliant but semantically incorrect. It warns that large or
  deeply nested schemas may be rejected.
- The same Google page now demonstrates `anyOf` for conditional output using a
  Gemini 3.5 Interactions API example. That is evidence that conditional branch
  shapes are current Gemini practice. It is not evidence that the exact
  OpenRouter Chat Completions translation to Gemini 3.1 Flash-Lite on Google
  Vertex accepts the same union shape.
- [OpenRouter structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs)
  documents strict `json_schema`, `require_parameters: true`, and optional
  response healing. [Provider routing](https://openrouter.ai/docs/guides/routing/provider-selection)
  documents `only`, `order`, disabled fallbacks, data policy, and price bounds.
  OpenRouter normalizes provider parameters, so native Gemini examples remain
  informative but not exact route proofs.

### Primary research

- [The Format Tax](https://arxiv.org/abs/2604.03616) separates prompt-level
  formatting pressure from decoder constraints. It reports that combining
  reasoning and strict formatting can reduce performance in some settings and
  that delayed formatting can recover performance. It also reports little or
  no format tax for several recent closed models, so it does not prove that
  R3 needs two passes.
- [Capacity, Not Format](https://arxiv.org/abs/2606.09410) finds that structured
  output cost depends on model headroom and task difficulty. Schema complexity
  increases the penalty near a model's capacity boundary, while delayed
  structure helps. The experiments use different models and reasoning
  benchmarks; they support a capacity hypothesis, not a diagnosis of R3.
- [The Constraint Tax](https://arxiv.org/abs/2605.26128) shows that schema
  validity, answer accuracy, executable accuracy, and wrong-valid-schema rate
  must be measured separately. Its main evidence concerns sub-3B local models,
  so its effect sizes do not transfer to Gemini 3.1 Flash-Lite.
- [JSONSchemaBench](https://arxiv.org/abs/2501.10868) treats schema coverage,
  conformance efficiency, and output quality as separate dimensions across
  constrained decoders. Its maintained
  [benchmark repository](https://github.com/guidance-ai/jsonschemabench)
  supports testing exact provider/schema combinations rather than assuming
  generic JSON Schema portability.

### Maintained practitioner patterns

- [Pydantic AI output documentation](https://ai.pydantic.dev/output/) separates
  typed output parsing from application validation and supports validators and
  retry feedback. This validates the need for explicit local invariants. Lolla
  rejects the automatic retry part for this experiment because retries would
  hide first-pass reliability and spend.
- [Instructor](https://github.com/567-labs/instructor) likewise combines typed
  models, field/model validators, and automatic retry. It is evidence that
  cross-field validation is normal production practice, not evidence that
  Lolla should adopt a repair loop.
- [JSON Schema conditional validation](https://json-schema.org/understanding-json-schema/reference/conditionals)
  can express dependencies with `if`/`then`/`else` in the full standard. The
  exact Gemini subset does not document those keywords, and OpenRouter route
  translation is another boundary, so Lolla should not depend on them here.

## Local-to-external mapping

| External finding | Local evidence | Interpretation |
| --- | --- | --- |
| Valid JSON is not semantic correctness | Strict JSON contained `park` plus `uncertainty_change` | Direct match |
| Validate values in application code | Canonical compiler stopped the response | Existing design is correct |
| Schema complexity can consume capacity | One call handled ten semantic responsibilities and nine rows | Plausible, not causal proof |
| Delayed formatting can help | R3 combines disposition and answer drafting | Candidate ablation, not default architecture |
| Conditional schemas can encode branches | Google shows `anyOf` on Gemini 3.5 Interactions | Not exact-route proof; portability risk |
| Typed validators often feed retries | Pydantic AI and Instructor expose this pattern | Validation adopted; retry rejected |

## Practices adopted

- Keep transport validity, mechanical contract validity, and semantic review
  as separate gates.
- Preserve deterministic cross-field validation and first-failure custody.
- Remove redundant independent output labels when an exact controlled combined
  label can preserve the model's judgment.
- Measure the whole job: semantic responsibilities, schema, prompts, fan-in,
  calls, serial depth, maximum cost, and transfer boundaries.
- Treat a two-pass design as an empirical alternative whose extra call and
  transfer surface must be earned.

## Practices rejected for this goal

- No retry with validator feedback, response healing, or post-hoc correction.
- No model judge, majority vote, premium escalation, or provider shopping.
- No deterministic choice between the conflicting `park` and
  `uncertainty_change` labels in the preserved response.
- No assumption that one observed inconsistency proves model overload.
- No `anyOf`, `if`/`then`, or provider-native conditional dependency in the
  selected portable candidate until the exact route is tested prospectively.
- No free-form-first formatter call merely because papers show it can help on
  other tasks.

## Design consequence

The smallest justified alternative is a one-pass controlled outcome vocabulary:

```text
reject
park
apply_reframe
apply_new_condition
apply_new_alternative
apply_uncertainty_change
apply_reversal_rule
apply_reinforces_existing
```

The LLM still chooses the semantic outcome. Deterministic code maps that exact
label to the canonical disposition/effect pair, validates source and effect
custody, and fails closed. This removes the observed independent-label conflict
without deciding relevance or increasing call count.

A separate disposition-plus-synthesis design remains in the counterfactual
comparison. It should be selected only if evidence implicates simultaneous
answer drafting, not merely because decomposition is fashionable.

## Remaining unknowns

- Whether the pinned OpenRouter/Google Vertex route accepts the exact collapsed
  schema.
- Whether Gemini 3.1 Flash-Lite selects source-grounded combined outcomes.
- Whether a mechanically valid answer contributes non-forced value beyond a
  strong fresh baseline.
- Whether answer drafting creates over-absorption or public bloat across more
  than one case.

Those are empirical questions. This goal authorizes no provider call.
