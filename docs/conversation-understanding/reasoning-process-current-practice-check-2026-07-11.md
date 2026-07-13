# Reasoning-process current-practice check

Status: completed for Phase 0  
Checked: 2026-07-11

## Scope

This check covers structured model output, local validation, provider
portability, retry behavior, and evaluation practice. It does not select a new
framework or model and does not authorize provider calls.

## Sources checked

- [OpenAI structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
- [OpenAI evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
- [OpenRouter structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs)
- [Google Gemini structured outputs](https://ai.google.dev/gemini-api/docs/structured-output)
- [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12)
- [PydanticAI repository](https://github.com/pydantic/pydantic-ai)
- [PydanticAI output validation](https://pydantic.dev/docs/ai/core-concepts/output/)
- [Instructor structured-output repository documentation](https://github.com/jxnl/instructor/blob/main/docs/index.md)
- the supplied focused-agent pipeline article and Lolla's completed July 2026
  decomposition evidence.

## Adopted practices

### One typed contract and local admission authority

OpenAI, OpenRouter, and Gemini all support structured output but each supports a
provider-specific subset of JSON Schema. Schema adherence controls shape, not
semantic truth. Lolla therefore keeps one internal contract, emits shallow
model-facing projections, and always runs local cross-field, source, custody,
and product-boundary validation.

### Explicit strict model-facing shapes

Every model-facing object has:

- clear field names and descriptions;
- strong types and enums;
- all properties required;
- `additionalProperties: false` on every object;
- explicit empty arrays instead of missing fields;
- bounded arrays and shallow nesting;
- a versioned checked-in schema snapshot.

The bounded-view schema is 2,302 bytes at depth 8. The process-assessment
schema is 1,733 bytes at depth 8. Both remain under the frozen 12,000-byte and
depth-8 ceilings.

### Transport and semantic validation remain separate

OpenAI recommends Structured Outputs over basic JSON mode when the model
supports it. OpenRouter also recommends strict schemas and exposes
provider-parameter checks. Gemini documents that even syntactically valid
structured output requires application validation and that large or deeply
nested schemas may be rejected.

The prospective rule is therefore:

1. preflight the exact model and provider;
2. use strict structured output only when that route supports the frozen
   schema without adaptation;
3. otherwise use JSON object transport with the exact schema in the prompt;
4. apply the same unchanged local admission contract either way;
5. preserve provider or schema failure rather than healing it.

If OpenRouter strict output is later selected, `require_parameters: true` must
prevent routing to a provider that cannot honor the requested parameter.

### Eval-driven, task-specific development

The current OpenAI guidance recommends scoped task-specific evals, complete
logging, automation where appropriate, and human-feedback calibration. Lolla's
adoption is stricter at the current stage:

- one semantic hypothesis per experiment;
- source-first evidence review;
- prospective fixtures, hashes, budgets, and stop rules;
- per-stage and per-dimension results rather than one composite metric;
- preserved failures and no post-hoc scorer repair;
- human calibration before any public quality language.

The OpenAI-hosted Evals platform is scheduled to become read-only on
2026-10-31 and shut down on 2026-11-30. Lolla therefore does not introduce a
dependency on that platform; its frozen local evidence packages remain the
authority.

## Deliberate departures

### No automatic validation retry

PydanticAI and Instructor support feeding validation errors back to a model and
retrying. That is useful for many application workflows. Lolla deliberately
does not adopt it in this research path because the first malformed or
semantically invalid output is evidence about reliability. Automatic retry
would blur attempt identity, change the prompt context, and make failure rates
look better unless separately designed as the experiment.

One prospectively authorized generic repair across cases remains allowed; it is
not an in-run retry.

### No response healing or silent coercion

OpenRouter offers response healing. Lolla leaves it disabled because repaired
JSON would obscure whether the selected model/provider honored the frozen
contract. Source IDs, semantic labels, and malformed structures are never
silently corrected.

### No new agent or validation framework

PydanticAI, Instructor, and Inspect provide useful typed-output, retry,
observability, and evaluation machinery. Phase 0 needs none of those
dependencies. The repository's standard-library validators already preserve
the product-specific distinctions that generic frameworks cannot supply:
semantic versus mechanical authority, exact source custody, parked-item
lineage, no-quality-score boundaries, and provider-free evidence replay.

### No universal compressed summary

The supplied focused-agent pattern remains valid only when fan-in is also
bounded. Lolla's previous small-window design produced 88–95 overlapping events
and recreated overload at synthesis. Phase 0 therefore defines five
question-specific bounded views rather than another universal compressed
handoff.

## Result

The current-practice check refines transport and validation controls but does
not change Lolla's architecture thesis. Probabilistic components interpret
messy meaning. Deterministic components validate and preserve identity,
lineage, budgets, failures, and boundaries. Structured output constrains shape;
source-reviewed evaluation determines whether the semantic work is adequate.

