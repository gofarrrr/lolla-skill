# Stance-object structured extraction: current-practice check

Status: checked before v4 schema implementation  
Checked: 2026-07-12

## Official guidance checked

- Google Gemini structured outputs:
  <https://ai.google.dev/gemini-api/docs/structured-output>
- OpenRouter structured outputs:
  <https://openrouter.ai/docs/guides/features/structured-outputs>
- OpenRouter provider routing:
  <https://openrouter.ai/docs/guides/routing/provider-selection>

## Adopted

- Use strict structured output with explicit descriptions and enums.
- Keep the schema shallow and bounded because Gemini supports a JSON Schema
  subset and warns that very large or deeply nested schemas may be rejected.
- Validate all output application-side.
- Treat schema-valid semantic errors as expected failure states requiring
  source review.
- Require providers to support requested parameters and disable fallbacks for
  a frozen experiment.
- Keep response healing disabled so the preserved result is the model/provider
  result rather than a repaired derivative.

## Rejected or deferred

- No `oneOf` or conditional polymorphic schema for object-specific force types;
  the simpler flat component schema is easier to emit and inspect.
- No semantic object/expression compatibility matrix in code.
- No response-healing plugin, provider fallback, semantic retry, or judge.
- No framework migration; existing direct OpenRouter custody remains adequate
  for this bounded experiment.
- No model change without a separately demonstrated need.

## Nonclaim

Strict structured output improves shape reliability. It does not establish
semantic correctness, source fidelity, reasoning quality, or product value.
