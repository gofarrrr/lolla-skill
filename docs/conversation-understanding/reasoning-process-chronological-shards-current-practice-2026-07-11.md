# Chronological shard redesign: July 2026 practice check

Status: checked before prompt/schema or provider-probe authorization  
Date: 2026-07-11

## Why this check matters

Phase-4 transfer showed that strict schemas and exact aliases did not prevent
whole-conversation readers from losing small protected relationships. Before
adding more extraction machinery, the redesign was checked against current
official Gemini and OpenRouter guidance.

## Current evidence

Google's Gemini long-context guidance, updated 2026-06-22, explicitly warns
that performance varies when a request contains multiple needles. It notes that
high accuracy across many separate pieces of information may require separate
requests and describes the resulting retrieval-versus-cost tradeoff. It also
recommends placing the query after long context rather than before it:

- https://ai.google.dev/gemini-api/docs/long-context

This supports testing smaller semantic jobs. It does not prove that three
shards, nineteen calls, or Lolla's role contracts are optimal.

Google's structured-output guidance, updated 2026-07-07, says structured output
constrains syntax but does not guarantee semantic correctness, recommends clear
property descriptions and strong types, and warns against excessive schema
complexity:

- https://ai.google.dev/gemini-api/docs/structured-output?lang=rest

OpenRouter's current structured-output documentation recommends strict JSON
Schema and `require_parameters: true`. Its routing documentation shows that
fallbacks are enabled by default unless explicitly disabled. Its error guidance
says 429 and 503 responses may carry `Retry-After` and documents provider
overload errors injected after generation begins:

- https://openrouter.ai/docs/guides/features/structured-outputs
- https://openrouter.ai/docs/guides/routing/provider-selection
- https://openrouter.ai/docs/api/reference/errors-and-debugging

## Adopted for the next design step

- reduce multi-needle competition through deterministic chronological shards;
- keep each shard a single semantic family and at most two records;
- serialize visible source context before restating the exact task at the end
  of the future prompt;
- retain strict JSON Schema, short enums, descriptions, and local semantic-role
  validation;
- require supported parameters and disable provider fallbacks explicitly;
- preserve every provider error and `Retry-After` header when present;
- keep source-first semantic review because schema conformance is not semantic
  correctness.

## Deliberately not adopted

- response healing, because it would obscure the model's original failure;
- context compression, because exact visible source custody matters more than
  reducing packets already below 6.1 KB;
- fallback models, because transfer and stability require one frozen route;
- automatic retries, because first-attempt operability must remain visible;
- context caching in the first redesign probe, because packets are small and a
  cache changes cost/latency accounting without solving semantic selection;
- one request per protected target, because protected targets must remain
  hidden and the production job cannot depend on evaluation answers.

## Lolla-specific conclusion

The current-practice evidence supports decomposing the overloaded semantic job,
but it does not authorize an uncontrolled microtask explosion. The provider-free
v1 design therefore caps each fourteen-message case at twelve new shards plus
the existing seven exploration windows: nineteen calls and at most thirty-eight
records, with no global synthesis or semantic merge. Whether that added cost
buys sufficient minority-signal recall remains an empirical question.
