# R4 separated-surface experiment current provider practice

Status: official-practice check complete; provider-free design only

Checked: 2026-07-14

Provider calls: 0

Provider cost: `$0.00`

## Primary sources checked

- Google Gemini 3.1 Flash-Lite model card:
  https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite
- Google Gemini 3 developer guide:
  https://ai.google.dev/gemini-api/docs/gemini-3
- Google structured-output guide:
  https://ai.google.dev/gemini-api/docs/structured-output
- Google Gemini API pricing:
  https://ai.google.dev/gemini-api/docs/pricing
- OpenRouter Gemini 3.1 Flash-Lite model/provider page:
  https://openrouter.ai/google/gemini-3.1-flash-lite-20260507/providers
- OpenRouter provider routing:
  https://openrouter.ai/docs/guides/routing/provider-selection
- OpenRouter reasoning controls:
  https://openrouter.ai/docs/guides/best-practices/reasoning-tokens
- OpenRouter usage accounting:
  https://openrouter.ai/docs/cookbook/administration/usage-accounting
- OpenRouter API response and generation metadata:
  https://openrouter.ai/docs/api/reference/overview

## Current findings

Google identifies `gemini-3.1-flash-lite` as the stable May 2026 model, with a
1,048,576-token input limit, 65,536-token output limit, text output, structured
output support, and thinking support. The twelve frozen requests are far below
those published limits.

Google's current Gemini 3 guidance lists `minimal` thinking for Gemini 3.1
Flash-Lite and states that thinking levels are relative rather than strict token
guarantees. OpenRouter documents direct mapping of `reasoning.effort` to
Google's thinking level and `reasoning.exclude: true` for excluding returned
reasoning content. The design therefore retains the already-published R4
envelope: `minimal`, excluded from the response, with deterministic failure if
reasoning content is nevertheless returned.

Google documents structured output for this model and warns that only a subset
of JSON Schema is supported and that schema validity does not prove semantic
validity. The paired schema reuses the published residual schema. The separated
schemas make only the container and surface-enum changes required to request a
single review. Local admission remains deterministic and does not repair
meaning.

OpenRouter currently lists `google/gemini-3.1-flash-lite` at `$0.25` per
million input tokens and `$1.50` per million output tokens. Google publishes the
same text input/output rates. OpenRouter continues to expose the
`google-vertex` provider slug; its routing guide states that the base slug
matches Vertex regions and variants.

OpenRouter continues to document all frozen routing controls:

- `order` and `only` for the Google Vertex route;
- `allow_fallbacks: false`;
- `require_parameters: true`;
- `data_collection: "deny"`;
- `zdr: true`;
- provider `max_price` controls.

Its provider directory currently labels Google Vertex as no-training and ZDR.
That is current routing evidence, not a permanent third-party privacy warranty.
The request declares both `data_collection: "deny"` and `zdr: true`, and a
future execution must stop rather than reroute if the exact endpoint is not
available under those constraints.

OpenRouter documents prompt, completion, reasoning, total-token, and exact cost
fields in the non-streaming response usage object, plus a non-empty generation
ID. The runner requires those fields from the first terminal response and does
not make a second metadata or evaluator call.

## Adopted practices

- Keep the GA request slug `google/gemini-3.1-flash-lite` and accept only the
  published generic or dated served identities already used by R4.
- Pin `google-vertex` through both `order` and `only`, with fallbacks disabled.
- Require parameter support, deny data collection, request ZDR, and cap provider
  prices at the published `$0.25` input and `$1.50` output rates.
- Use strict JSON Schema, non-streaming responses, minimal thinking, and
  excluded returned reasoning.
- Preserve exact response bytes, generation identity, provider identity,
  native usage, reasoning-token count, and provider-reported cost.
- Keep local admission structural and preserve semantic review for the frozen
  source-first target after any future execution.

## Rejected changes

- No model upgrade or comparison: it would add a second causal variable.
- No Google AI Studio route: the experiment pins Google Vertex through
  OpenRouter.
- No streaming: it would change response and usage custody.
- No larger thinking level or explicit thinking budget: it would alter the
  operator and would not provide a strict Gemini token guarantee.
- No schema enrichment, prompt warning, authority repair, new examples, or new
  evidence rule: those would change semantics alongside task shape.
- No request compression, summarization, chunking, or context filtering.
- No asynchronous generation-metadata lookup: response usage is required in
  the terminal non-streaming payload, avoiding an extra call and new custody
  path.

## Remaining uncertainty and stop rule

Documentation establishes supported interfaces, not that this exact model will
follow the semantic contract. Provider availability, endpoint routing, and
prices may change after this freeze. A future execution must recheck the exact
operator against the frozen maximum prices and stop before transport if the
model, Vertex route, structured output, reasoning/privacy controls, or usage
custody is unavailable. This document creates no execution authorization.
