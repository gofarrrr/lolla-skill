# Simulated reliability V1 current-practice check

Status: complete before V1 calibration calls  
Checked: 2026-07-12 13:47 UTC

## Scope

This check covers the exact moving parts needed by V1: current Gemini models,
OpenRouter model and endpoint metadata, provider pinning, strict structured
outputs, schema design, thinking controls, privacy, retries, output validation,
and blind evaluation. It does not authorize a call by itself.

## Sources checked

Primary provider and model sources:

- [OpenRouter structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs)
- [OpenRouter provider routing](https://openrouter.ai/docs/guides/routing/provider-selection)
- [OpenRouter models API](https://openrouter.ai/api/v1/models)
- [OpenRouter zero data retention](https://openrouter.ai/docs/guides/features/zdr)
- [OpenRouter data collection](https://openrouter.ai/docs/guides/privacy/data-collection)
- [OpenRouter reasoning controls](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens)
- [Gemini structured outputs](https://ai.google.dev/gemini-api/docs/structured-output)
- [Gemini 3.5 Flash guidance](https://ai.google.dev/gemini-api/docs/whats-new-gemini-3.5)
- [Gemini release notes](https://ai.google.dev/gemini-api/docs/changelog)

Maintained implementation evidence:

- [PydanticAI repository and releases](https://github.com/pydantic/pydantic-ai)
- [PydanticAI OpenAI-compatible model implementation](https://github.com/pydantic/pydantic-ai/blob/main/pydantic_ai_slim/pydantic_ai/models/openai.py)

The repository evidence was used as an implementation comparison, not adopted
as a new framework dependency.

## Current model decision

Use `google/gemini-3.5-flash-20260519` through OpenRouter and the Google Vertex
provider for the two role tasks, controlled-mechanism interpretation, and all
three fresh-reasoning arms.

The public catalog retrieved on 2026-07-12 reports:

- stable alias `google/gemini-3.5-flash`;
- canonical slug `google/gemini-3.5-flash-20260519`;
- 1,048,576-token context;
- 65,536 maximum completion tokens;
- structured outputs, response format, seed, reasoning effort, and temperature
  support; and
- standard list pricing of $1.50 per million prompt tokens and $9.00 per
  million completion or internal-reasoning tokens.

Gemini 3.5 Flash is the current GA Flash model recommended by Google for tasks
that need greater reasoning depth. Gemini 3.1 Flash Lite remains the appropriate
cheap model for simple extraction, but Lolla's prior evidence shows that the
combined position schema was rejected by the Google route and that nominal
schema success did not establish semantic fidelity. V1 therefore pays for the
stronger model at the calibration boundary rather than changing models between
semantic stages or between comparison arms.

This is a task-specific development choice, not a production winner. The
calibration sentinels can reject it on wire, contract-execution, source-fidelity,
restraint, or cost grounds.

## Adopted request practice

Every request will:

- use the canonical model slug rather than a moving alias;
- pin `provider.only` to `google-vertex`;
- set `require_parameters: true` and `allow_fallbacks: false`;
- set `data_collection: "deny"` and `zdr: true`;
- cap provider pricing at the documented standard rate;
- use non-streaming strict `json_schema` output with `strict: true`;
- omit response healing and tools;
- omit `temperature` and `top_p` for Gemini 3.5 Flash, following Google's
  current model guidance;
- use `reasoning.effort: "medium"` and `reasoning.exclude: true`;
- use a prospectively declared seed, while treating seed as a variance control
  rather than a determinism guarantee;
- write a durable started record before network transport;
- persist provider error, model, provider, usage, cost, latency, raw-response
  hash, parsed candidate, local validation, and terminal state; and
- perform zero automatic retries.

OpenRouter documents that ZDR removes Google AI Studio while Vertex remains
available. This makes Vertex the privacy-compatible Google route for full
conversation payloads. OpenRouter stores request metadata, but its documentation
states prompt and response logging is opt-in. Lolla still treats provider
processing as an external disclosure and must not claim local-only custody.

## Structured-output decision

OpenRouter recommends strict schema mode, supported-parameter enforcement, and
property descriptions. Google documents only a JSON Schema subset, warns that
large or deeply nested schemas may be rejected, and requires application-side
validation because schema-valid values can still be semantically wrong.

V1 therefore uses:

- shallow, bounded role-specific tasks rather than the failed combined reader;
- required properties, enums, array caps, and `additionalProperties: false`;
- checked schema bytes and depth before each call;
- exact local cross-field, ID, evidence, turn, graph, and disposition validation;
- no silent alias repair, JSON healing, semantic coercion, or valid-empty
  substitution after a malformed response; and
- a provider-free preflight over all 20 sources before calibration.

The largest current role prompt is 18,929 UTF-8 bytes. The largest role schema
is 2,397 bytes at depth 11. The maximum thirteen-candidate pressure schema is
about 2.6 KB at depth 8. All remain below the project's 12 KB schema ceiling,
but actual Google Vertex acceptance is still an empirical calibration gate.

## Reasoning and prompt decision

Gemini 3.5 Flash has mandatory thinking and defaults to medium. V1 states
medium explicitly so provider defaults cannot drift. Internal reasoning is not
requested in the artifact: it is probabilistic hidden computation, not the
auditable process Lolla claims to preserve. The auditable evidence is the
source-linked structured output, candidate ledger, dispositions, public answer,
and call custody.

The pressure reasoner remains one bounded call rather than a chain of candidate
judges followed by a synthesizer. This is deliberate. Splitting consideration
would let an upstream probabilistic layer re-domesticate graph pressure before
the answer-producing reasoner sees it. Thirteen active candidates is the
calibration ceiling; failure at that fan-in triggers redesign rather than
automatic batching.

## Retry and failure decision

PydanticAI and other maintained frameworks support validation feedback and
automatic retry. V1 deliberately does not adopt that behavior because first
attempt failure is reliability evidence. Response healing, fallback providers,
model fallback, silent coercion, majority vote, and same-run semantic repair are
disabled.

A separately recorded identical transport reattempt may be made only for a
pre-inference 429 or 5xx after the required cool-off, under a predeclared
one-reattempt ceiling. The first failure remains in the scorecard. Schema or
semantic failure is never retryable inside V1.

## Evaluation decision

Outputs will be blind-labeled and compared without arm identity, candidate
ledger, source-review stratum, or builder explanation. The review records
source fidelity, useful contribution, accountable rejection, unsupported
specificity, forced absorption, false stand-down, lost original value, bloat,
and public-behavior fit separately. No winner is required and no scalar quality
score is computed.

The first blind model review is a triage aid, not the grader of record. Human
calibration remains required before any usefulness language. Same-model family
review is an acknowledged limitation; fresh context and hidden arm identity
address trajectory bias but not shared model bias.

## Practices rejected for V1

- Gemini 3.1 Flash Lite as the main reasoner solely because it is cheaper;
- a moving `latest` model alias;
- unpinned provider routing or provider fallback;
- AI Studio for full conversations under the ZDR requirement;
- response healing or validation-error retry;
- framework adoption merely to replace working local custody validators;
- dumping all 47 graph neighbors into context;
- an LLM relevance gate before graph consideration;
- hidden chain-of-thought as receipt evidence; and
- a composite reasoning-quality or proof-of-work badge.

