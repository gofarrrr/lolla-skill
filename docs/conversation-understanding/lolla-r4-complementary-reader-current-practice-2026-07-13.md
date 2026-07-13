# R4 complementary-reader current-practice check

Status: complete before execution contract and provider calls
Checked: 2026-07-13
Provider calls: zero

## Question checked

What is the smallest current, provider-compatible boundary for reading an
unresolved matter and a reopen condition from a long conversation, then reading
their relationships through exact admitted record IDs—without turning JSON
validation into a claim of semantic correctness or adding brittle deterministic
meaning gates?

## Current sources

Primary sources checked:

- [Google Gemini structured outputs](https://ai.google.dev/gemini-api/docs/structured-output),
  updated 2026-07-07;
- [OpenRouter structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs);
- [OpenRouter provider routing](https://openrouter.ai/docs/guides/routing/provider-selection);
- [OpenRouter Gemini 3.1 Flash Lite endpoint catalog](https://openrouter.ai/api/v1/models/google/gemini-3.1-flash-lite/endpoints);
- [OpenRouter ZDR endpoint inventory](https://openrouter.ai/api/v1/endpoints/zdr);
- [OpenRouter Gemini 3.1 Flash Lite pricing](https://openrouter.ai/google/gemini-3.1-flash-lite/pricing);
- [OpenRouter DeepSeek V4 Flash pricing](https://openrouter.ai/deepseek/deepseek-v4-flash/pricing).

Maintained practitioner evidence checked:

- [Instructor main documentation](https://github.com/567-labs/instructor/blob/main/docs/index.md),
  which keeps typed extraction, validation, retries, and provider portability
  explicit;
- [PydanticAI issue 4762](https://github.com/pydantic/pydantic-ai/issues/4762),
  a March 2026 practitioner report showing materially better schema adherence
  from native strict JSON Schema than from older JSON-object/tool transport on
  a tested provider, especially as nesting grows.

These sources inform transport and task shape. They do not override Lolla's
constitution or substitute for source-first semantic review.

## Adopted now

### Native strict structured output, with local admission afterward

OpenRouter currently recommends `response_format.type = json_schema`,
`strict: true`, property descriptions, and `require_parameters: true`. Google
states that Gemini structured output guarantees syntactic shape, not semantic
correctness, and that application validation remains necessary.

The experiment therefore freezes strict structured output through OpenRouter
and runs an unchanged local validator afterward. Schema acceptance is the wire
gate; exact alias/ID custody is the local gate; source-first review is the
semantic gate. None substitutes for another.

### Only Google's documented schema subset

Google currently documents object, array, string, number, integer, boolean,
null, properties, required, additional properties, enum, formats, numeric
bounds, array items, tuple prefix items, and item-count bounds. It warns that
large or deeply nested schemas may be rejected.

The model-facing schemas use only:

- objects, arrays, and strings;
- descriptions and string enums;
- required fields and `additionalProperties: false` on every object;
- array `items`, `minItems`, and `maxItems`.

Pattern matching, uniqueness, string lengths, dynamic ID membership, source
hashes, cross-field outcome consistency, and relationship endpoint resolution
remain local checks. The paired uncertainty schema is 1,653 canonical bytes;
the relationship schema is 1,442 bytes. Neither uses `$ref`, unions, optional
fields, or provider-specific coercion.

### One discovery call, then one relationship call

The first call performs one coherent comparison: separately report unresolved
matter and reopen condition, with a valid zero and ambiguous path for each. It
does not also assemble relationships, choose mental models, activate pressure,
or revise advice.

The second call receives only exact admitted record IDs, unchanged semantic
payloads, and their exact source evidence. It may describe a relationship or
complete with zero. Deterministic code checks endpoint membership but never
decides whether the relationship makes sense.

This is smaller than the older uncertainty record that required unresolved,
reopen, and relationship meaning in every record. It also avoids a broad
free-form synthesis call.

### Full source first; fallible prior interpretations second

The unresolved reader needs the complete conversation because the exposed gap
is distributed across pilot scope, geography, transport supply, temporary
coordination, and the final continuation rule. Sharding it by chronology would
reintroduce the very semantic gate being tested.

The prompt places exact source aliases before compact existing position
records. Existing records are labeled fallible context, not source truth. The
model can compare the endpoint against the full conversation without being told
the frozen expected answer.

### Explicit quiet and ambiguity behavior

Both schemas distinguish:

- `records_present`;
- `no_supported_record_observed`;
- `ambiguous_review`.

A valid quiet response has an empty record array. An ambiguous response keeps
an explicit ambiguous semantic record and its evidence; it is not converted to
a semantic zero. At fan-in, operational `completed_zero` still means only that
the reader completed with zero admitted records.

### Pinned private route and bounded cost

The point-in-time endpoint catalog and ZDR inventory both list Gemini 3.1 Flash
Lite through `google-vertex/global` with structured outputs, response format,
seed, and reasoning controls. The route is pinned to `google-vertex`, fallbacks
are disabled, required parameters are enforced, data collection is denied, ZDR
is required, and response healing is disabled.

The planned diagnostic is four calls maximum: two cases times two readers. The
per-case ceiling is `$0.015`; the total ceiling is `$0.03`; there are no retries
or fallback models. Gemini 3.1 Flash Lite is chosen because the repository has
positive small-task evidence and the model is far cheaper than Gemini 3.5. It
is not declared a production winner. DeepSeek V4 Flash remains a cheaper later
comparison only if the frozen task fails and a model-family comparison would
answer a distinct question.

## Deliberate rejections

- No automatic retry or Instructor/PydanticAI repair loop: first-attempt
  failure is evaluation evidence and must not be overwritten.
- No response healing or JSON-object fallback: transport guarantees must not
  change silently.
- No one-call rich final handoff: it recreates the overloaded synthesis defect.
- No deterministic keyword, chronology, lexical similarity, embedding,
  relevance, relationship, pressure, or quality gate.
- No provider-side target examples drawn from the two selected cases: the
  source-first target remains review-only.
- No premium Gemini 3.5 continuation and no broad model shopping in this
  experiment.
- No new orchestration or validation framework: the existing standard-library
  custody layer already expresses Lolla-specific states and boundaries.

## Result

Current practice supports the planned architecture, with one important
qualification: strict structured output can make the two tiny envelopes
reliable to parse, but only the two-case source-first experiment can tell us
whether the semantic decomposition discovers the known gap while remaining
quiet on the control. The local package must pass packet, prompt, schema,
source, relationship, fan-in, budget, and adversarial gates before any call is
authorized.
