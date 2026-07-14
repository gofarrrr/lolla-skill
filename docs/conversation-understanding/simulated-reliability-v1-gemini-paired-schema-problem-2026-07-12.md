# Gemini paired-schema calibration problem

Status: exact failure classified; prospective wire-only repair selected  
Date: 2026-07-12

## Observed signature

The first V1 calibration run used the frozen Gemini 3.5 Flash / Google Vertex
route. The starting-position request passed strict structured output, local
compilation, and call custody. The immediately following current/qualification
request returned HTTP 400 before inference:

```text
INVALID_ARGUMENT: Request contains an invalid argument.
```

OpenRouter attributed the error to Google. No response candidate, token usage,
or provider cost was returned for that request. The completed starting call and
the failed paired call remain preserved. No retry or response healing occurred.

This matches the broader problem already observed with Gemini 3.1 Flash Lite:
Google can accept a smaller schema and reject a larger nested schema before
inference even when other providers accept it. Gemini 3.5 improved the model but
did not remove the provider-schema boundary.

## External-to-local mapping

Google's current structured-output documentation says Gemini supports only a
subset of JSON Schema and that large or deeply nested schemas may be rejected.
OpenRouter distinguishes strict `json_schema` from basic `json_object` transport
and recommends application validation in either workflow. Maintained typed-
output frameworks similarly separate native schema enforcement from parsing and
local validation, and their issue histories show that advertised schema support
does not guarantee every model/provider/schema combination.

The Lolla paired schema is 2,397 bytes at depth 11. It is locally valid and
semantically bounded, but exact Google acceptance—not abstract JSON Schema
validity—is the failed gate.

## Prospective repair

Only the failing task's wire changes:

- `response_format` becomes `json_object`;
- the exact unchanged JSON Schema is appended to the checked user prompt;
- the same schema hash, compiler, cross-field rules, source custody, model,
  provider, ZDR route, reasoning level, seed, and output limit remain;
- the effective prompt and request bytes receive new hashes;
- local validation remains the admission authority; and
- the repair receives a new run ID, contract, authorization, and fresh call
  identities for every calibration sentinel.

This is not a fallback to free-form acceptance. A malformed or semantically
invalid JSON object still fails the run. It is also not a new agent, reader,
retry loop, semantic gate, or architecture layer.

## Alternatives rejected

- retrying the identical strict-schema request;
- weakening local semantic validation;
- removing current/qualification comparison merely to satisfy the provider;
- switching back to a weaker cheap model after the stronger model hit the same
  provider boundary;
- adding response healing or validation feedback retries; and
- changing all tasks to prompt-only JSON before evidence requires it.

The calibration question for the new route is now precise: can Gemini 3.5 Flash
produce a locally admissible paired object through JSON-object transport, and is
that object source-faithful? Wire success alone will not pass the sentinel.

## Sources

- [Google structured outputs](https://ai.google.dev/gemini-api/docs/structured-output)
- [OpenRouter structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs)
- [OpenRouter provider routing](https://openrouter.ai/docs/guides/routing/provider-selection)
- [PydanticAI repository](https://github.com/pydantic/pydantic-ai)

