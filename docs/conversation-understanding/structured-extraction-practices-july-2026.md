# Structured extraction practices — July 2026

Status: standing design and preflight rule  
Date checked: 2026-07-11

## Why this exists

Lolla combines probabilistic semantic interpretation with deterministic
custody. That boundary only works when the model receives a task it can perform
reliably and deterministic code validates what it is actually qualified to
validate. The failed conversation-state probe showed that a valid JSON envelope
does not imply good conversation understanding.

Before freezing any new extraction prompt, output schema, or composition path,
the owner must check current documentation from the selected model provider and
at least one maintained structured-extraction implementation. Record the check
date, links, provider/model, output mode, schema subset, and any deliberate
departures. “The API accepted JSON” is not a best-practice check.

## July 2026 source review

Primary sources reviewed:

- OpenAI structured outputs:
  https://developers.openai.com/api/docs/guides/structured-outputs
- Google Gemini structured outputs and troubleshooting:
  https://ai.google.dev/gemini-api/docs/structured-output
  https://ai.google.dev/gemini-api/docs/troubleshooting
- OpenRouter structured outputs and model capability metadata:
  https://openrouter.ai/docs/guides/features/structured-outputs
  https://openrouter.ai/api/v1/models
- PydanticAI output modes and validation:
  https://pydantic.dev/docs/ai/core-concepts/output/
- Instructor structured extraction:
  https://github.com/567-labs/instructor
- Outlines constrained generation:
  https://github.com/dottxt-ai/outlines

These are design inputs, not authorities that override Lolla's constitution or
evaluation doctrine.

## What current practice says

### 1. Use one typed definition as the source of truth

Generate the provider schema and local validator from the same typed model
(Pydantic, dataclass/TypedDict adapter, or an equivalent checked definition).
Do not separately hand-maintain prompt schema text, provider JSON Schema, and
Python validation rules. OpenAI explicitly recommends native Pydantic/Zod
support or CI checks to prevent schema/type divergence.

Lolla implication: the packet type owns field names, enums, descriptions,
nullability, and serialization. Provider-specific adapters may remove or
translate unsupported schema features, but must hash and record the projection.

### 2. Select the output mode deliberately

The modes are not equivalent:

- native structured output constrains shape but has provider/model schema
  restrictions;
- required tool output is appropriate when structured data is an application
  handoff and the provider reliably supports forced tool choice;
- prompted JSON mode guarantees at most valid JSON and relies on local
  validation for shape;
- constrained decoding/grammar systems such as Outlines can make invalid syntax
  impossible for supported local or integrated models.

PydanticAI explicitly describes prompted JSON as the least reliable general
mode. Lolla must not silently fall back between modes. The selected mode and its
expected guarantees belong in the frozen contract and custody record.

### 3. Keep provider schemas shallow and simple

Google warns that large or deeply nested schemas may be rejected. OpenAI also
supports a defined subset and requires root objects, required fields, and
`additionalProperties: false` for strict output. Provider subsets differ.

Lolla implication: do not make one call populate the final rich handoff. Prefer
small record schemas with clear descriptions, required fields, enums, explicit
nullable fields, and bounded arrays. Run a provider-schema compatibility test
before the evaluation call, using no case semantics.

### 4. Split semantic work, not just prompts

OpenAI recommends changing instructions, adding examples, or splitting tasks
into simpler subtasks when structured outputs contain mistakes. Our failed
probe asked one model call to discover current positions, reconstruct thread
trajectories, calibrate claim strength, copy evidence, and assemble a final
nested packet. That was too much semantic work in one boundary.

The minimal Lolla decomposition is:

1. position/contribution candidates;
2. focal thread/trajectory candidates;
3. atomic constraint/source-strength candidates;
4. deterministic validation of each candidate set;
5. deterministic assembly of validated records into a handoff.

These are not deterministic semantic gates. Models still decide meaning. Code
only preserves candidate identity, validates source custody and vocabulary, and
prevents invalid records from entering the current projection.

### 5. Make evidence selection easier than quote invention

Copying long exact quotations invites accidental joins and paraphrases. Before
model extraction, deterministically assign stable IDs to source turns and, when
safe, sentence/clause spans. The model selects source IDs and may return a short
excerpt; code resolves and verifies it. The catalog does not decide relevance.

Do not ask a model for character offsets unless the selected provider/model has
been separately shown reliable at that task. Do not let fuzzy matching convert
a paraphrase into exact-span evidence.

### 6. Support abstention and ambiguity explicitly

Structured-generation projects commonly model a valid fallback such as “not
enough information.” Lolla needs typed states such as `supported`, `unclear`,
and `not_found`, plus valid empty candidate lists. This prevents required fields
from forcing invented threads, ownership, or constraints.

An abstention is observable extraction behavior, not an error to fill
automatically.

### 7. Separate syntax, custody, semantics, and composition

Four different questions must remain separate:

1. Is the response parseable and schema-valid?
2. Are source IDs and quotes exact and internally consistent?
3. Are the semantic labels and coverage good enough?
4. Can validated candidate records compose without losing provenance?

Native structured output answers only part of question 1. It does not prove
semantic correctness. Deterministic validation answers parts of 1, 2, and 4;
source-first review or a separately justified evaluator answers 3.

### 8. Preserve candidates and failures before assembly

Every proposed candidate needs a durable terminal state: validated, invalid
evidence, ambiguous competing read, set aside, or selected. Invalid packets
must never receive an accepted observed-state path. They may be stored only in
an explicitly quarantined failure location with their validation errors.

The compiler may assemble validated records by stable IDs. It may not merge two
constraints because their text seems similar or infer that a missing assistant
contribution probably existed.

### 9. Treat retries as a product decision

Instructor and PydanticAI commonly feed validation errors back to the model
under bounded retry budgets. That is useful production practice, but it changes
the task, cost, and evidence. Lolla evaluation continues to use zero automatic
retries so first-pass capability is visible.

A future repair attempt, if tested, must be a separately recorded call with the
previous output, exact validation errors, prompt hash, cost, and disposition. It
must never overwrite the original attempt or be described as the same call.

### 10. Test parts and composition separately

Required provider-free tests before calls:

- typed model generates the expected provider projection;
- every field has a description and controlled null/empty behavior;
- provider projection uses only the selected provider's supported subset;
- source IDs cannot point to the wrong speaker or turn;
- non-contiguous quotes fail;
- joint ownership without both speakers fails;
- focal-thread omission is measurable, not hidden by other returned threads;
- mixed-strength constraints cannot be silently merged;
- invalid candidates never enter the current handoff;
- an empty or unclear result composes correctly;
- separately valid micro-results assemble without provenance loss;
- no deterministic component makes a semantic relevance decision.

## What changes for Lolla now

Adopt now:

- one typed source of truth;
- provider-specific schema projection and preflight;
- shallow candidate schemas;
- three semantic micro-extractors plus deterministic assembly;
- stable source IDs;
- explicit abstention/ambiguity;
- candidate ledger and strict invalid quarantine;
- part-level and composition-level evals.

Do not adopt now:

- a new agent framework;
- hidden automatic retries;
- multi-layer deterministic semantic gating;
- graph integration;
- a large orchestration rewrite;
- constrained-decoding infrastructure for local models;
- tuning only to the failed Case 03 fixture.

## Standing freeze checklist

No extraction call is authorized until the frozen contract answers yes to all:

- current provider and practitioner guidance checked and dated;
- output mode chosen explicitly;
- provider/model capability verified from a current primary source;
- typed source of truth and provider projection hashes recorded;
- schema depth, size, supported keywords, descriptions, and required fields
  checked;
- abstention and empty outcomes defined;
- semantic task narrow enough for one call;
- exact source identity strategy defined;
- invalid and partial output custody defined;
- retry policy explicit;
- per-part and composition evals frozen;
- cost, call count, stop rule, and non-claims frozen.
