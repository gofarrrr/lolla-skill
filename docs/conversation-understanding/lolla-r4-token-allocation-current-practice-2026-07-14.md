# R4 complementary-reader token-allocation practice check — 2026-07-14

Status: narrow provider-free correction basis complete; no additional call authorized

## Trigger

The first authorized R4 complementary-reader attempt reached the pinned
`google/gemini-3.1-flash-lite` model through Google Vertex twice. Both
uncertainty responses ended with `finish_reason: length` before returning a
parseable JSON object:

- Case 02 used 865 of 885 completion tokens for reasoning, leaving a
  20-token non-reasoning remainder;
- Case 03 used 861 of 886 completion tokens for reasoning, leaving a
  25-token non-reasoning remainder.

The relationship stage did not run. The exact cost was `$0.009036`.

## Current primary guidance

[OpenRouter's reasoning-token documentation](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens)
states that reasoning tokens count as output tokens. For Gemini 3 models,
OpenRouter maps `reasoning.effort` to Google's `thinkingLevel`; Google, not the
caller, determines the actual token consumption at a given level. Passing a
numeric reasoning budget to Gemini 3 is not precise because Google maps it back
to a thinking level.

[Google's Gemini 3 guide](https://ai.google.dev/gemini-api/docs/gemini-3)
describes thinking levels as relative allowances rather than strict token
guarantees. Gemini 3.1 Flash-Lite supports `minimal`, `low`, `medium`, and
`high`; `minimal` is intended for high-throughput work and behaves like little
or no thinking for most queries.

[Google's Gemini 3.1 Flash-Lite model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite)
lists structured outputs and thinking as supported and identifies lightweight
data extraction as a target use case. The model's large nominal output limit
does not change the per-request `max_tokens` boundary we supplied through
OpenRouter.

[OpenRouter's model page](https://openrouter.ai/google/gemini-3.1-flash-lite)
confirms the full thinking-level set and the current `$0.25/M` input and
`$1.50/M` output prices.

## Repository evidence

The affordable-operator investigation already found that medium reasoning used
909 of 984 completion tokens and truncated a small JSON response. Factoring
that task and moving to low reasoning repaired the smaller microtask. That
evidence did not establish that low reasoning was safe for a 12–13k-token
full-source semantic reader.

The R4 preparation therefore made one incorrect planning transfer: it treated
the output schema as small without separately budgeting for model-controlled
thinking on a much larger input task. This is a token-allocation mistake, not
evidence that deterministic gating should interpret the conversation or that
the semantic reader should be split further.

## Prospective correction

Change only the uncertainty transport allocation:

- `reasoning.effort`: `low` to `minimal`;
- `max_tokens`: `900` to `1600`.

Keep unchanged:

- source conversations and prior role records;
- prompts and strict response schema;
- source aliases, IDs, and hash custody;
- model, provider, seed, temperature behavior, and routing policy;
- relationship task at `minimal` reasoning and `700` maximum tokens;
- one attempt per task, no retry, no fallback, no healing;
- `$0.015` per case and `$0.03` total hard ceilings;
- source-first hidden targets and review dimensions.

The extra 700-token uncertainty allowance adds at most `$0.00105` per case at
the frozen output price. The provider-free conservative four-call estimate
therefore rises from `$0.0160615` to `$0.0181615`, still below the `$0.03`
ceiling.

## Why this is the narrow correction

`minimal` directly addresses the observed reasoning allocation. Increasing the
completion boundary to `1600` gives the model room for both unavoidable
thinking and the bounded JSON object. Neither setting guarantees completion:
Gemini thinking levels are deliberately non-deterministic token allowances.
The prospective runner must therefore preserve another length failure exactly
and stop without rescue.

We reject for this correction:

- a semantic retry of the failed call;
- reconstructing either partial JSON prefix;
- changing the schema or prompt at the same time;
- splitting the reader again before testing the earned allocation diagnosis;
- switching model or provider;
- numeric `reasoning.max_tokens` as if it were an exact Gemini 3 budget;
- raising the hard cost ceiling;
- opening relationship calls after a failed uncertainty dependency.

## Decision boundary

This practice check authorizes provider-free preparation only. A prospective
contract must hash-lock the historical failed run, prove the request diff is
limited to `/max_tokens` and `/reasoning/effort`, pass local tests, and require
new explicit founder authorization before any network transport.
