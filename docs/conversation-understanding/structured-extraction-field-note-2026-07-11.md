# Structured extraction field note — OpenRouter/Gemini interoperability

Status: observed bounded-probe evidence; not a general provider claim  
Date: 2026-07-11

## Why this note exists

The provider-free compatibility report for Lolla's shallow conversation-state
schemas passed, but the first bounded live experiment produced different
results for two schemas on the same requested and served model:

- the positions schema was accepted and reached inference;
- the smaller thread schema was rejected by Google AI Studio through OpenRouter
  with HTTP 400 `INVALID_ARGUMENT`.

This is exactly why local schema lint must remain separate from provider
acceptance evidence.

## Current external practice check

The check was refreshed on 2026-07-11 against primary documentation:

- [Gemini structured outputs](https://ai.google.dev/gemini-api/docs/structured-output?lang=rest)
  says Gemini supports a subset of JSON Schema, describes nullable type arrays
  such as `type: ["string", "null"]`, warns that large or deeply nested schemas
  may be rejected, and requires application-side semantic validation.
- [OpenRouter structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs)
  recommends descriptions, strict JSON Schema, checking model support, and
  `require_parameters: true`.
- [OpenRouter provider routing](https://openrouter.ai/docs/guides/routing/provider-selection)
  explains that `require_parameters` filters for providers supporting requested
  parameters; it does not promise that every schema feature will survive every
  downstream provider adapter.

## Provider-free comparison

| Property | Accepted positions | Rejected threads |
|---|---:|---:|
| Schema bytes | 2,864 | 2,294 |
| Measured depth | 6 | 6 |
| `$defs` / `$ref` | yes | yes |
| Nullable representation | `anyOf` object/null | `type` array string/null |

The rejected schema is smaller and no deeper. The distinctive structural
feature is the nullable `superseded_by` string encoded as a type array. That
makes an OpenRouter-to-Google-AI-Studio translation or compatibility issue the
strongest current hypothesis, but one observation does not prove causality.

## Prospective rule

Do not weaken the generic typed source or silently normalize provider output.
If another experiment is authorized:

1. retain the direct-Gemini projection documented by Google;
2. create an explicit OpenRouter-Gemini adapter projection using the `anyOf`
   nullable shape already accepted in this run;
3. constrain model-facing span IDs to the source-specific catalog with a schema
   enum; do not silently restore a missing prefix;
4. freeze and hash that projection before calls;
5. treat provider acceptance, syntactic validity, source custody, semantic
   interpretation, and composition as separate gates;
6. do not use automatic retry or response healing in evaluation.

The related evidence is at
`research/conversation-state-microtask-probe-v1-2026-07-11/`.

## Transfer result

The recommended adapter repair was prospectively frozen and tested on Case 05.
It replaced the nullable type array with `anyOf` and added a source-specific
full-ID enum. Google again returned HTTP 400 `INVALID_ARGUMENT` before inference
on the first thread call. The nullable representation is therefore falsified as
a sufficient repair. Because two schema features changed together, the run does
not isolate whether the remaining incompatibility concerns nullable strings,
the ID enum, another thread-schema feature, or provider translation generally.

Do not spend more evaluation calls performing one-feature-at-a-time diagnosis
through this strict provider path. The next recommended experiment uses JSON
object mode, includes the frozen typed schema in the prompt, and retains local
typed parsing, exact source custody, candidate ledger, and fail-closed
quarantine. Provider-side syntax enforcement and semantic admission remain
separate concerns.

The transfer evidence is at
`research/conversation-state-microtask-probe-v2-2026-07-11/`.
