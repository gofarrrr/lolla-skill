# R4 matched holdout v2: current provider practice and pricing

Date checked: 2026-07-14

This is a provider-free custody record for a possible future execution of the
leakage-corrected matched holdout. It records current official documentation,
adopted practices, rejected changes, conservative arithmetic, and a proposed
anti-runaway ceiling. It does not authorize, request, or perform provider calls.

## Official documentation checked

- Google, [Gemini 3.1 Flash-Lite model](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite): the exact model code is `gemini-3.1-flash-lite`; the page lists a 1,048,576-token input limit, a 65,536-token output limit, structured outputs, and thinking.
- Google, [Gemini API release notes](https://ai.google.dev/gemini-api/docs/changelog): the stable `gemini-3.1-flash-lite` release became generally available on 2026-05-07 and the preview ID was shut down on 2026-05-25. The stable ID remains pinned; no newer alias is substituted.
- Google, [Gemini 3 developer guide](https://ai.google.dev/gemini-api/docs/gemini-3): the table lists `$0.25` per million text/image/video input tokens and `$1.50` per million output tokens for Gemini 3.1 Flash-Lite. The guide's broad statement that Gemini 3 models are preview conflicts with the model-specific page and release note for this stable ID; the design records that documentation inconsistency rather than changing the operator.
- Google, [Structured outputs](https://ai.google.dev/gemini-api/docs/structured-output): JSON Schema is supported only as a subset; clear descriptions, strong types, application validation, and robust handling of schema-compliant but semantically wrong values remain required. Very large or deeply nested schemas may be rejected.
- Google, [Long context](https://ai.google.dev/gemini-api/docs/long-context): Google says long-context performance is generally better when the query appears after the context and warns that multi-needle accuracy can vary. Both arms preserve complete source → prior → task order and task-at-end, while provider-free validity does not claim long-context success.
- OpenRouter, [Gemini 3.1 Flash-Lite providers](https://openrouter.ai/google/gemini-3.1-flash-lite-20260507/providers): the page lists the `google/gemini-3.1-flash-lite` slug, Google Vertex route, `$0.25` input and `$1.50` output list prices, and support for `reasoning`, `max_tokens`, `seed`, and `response_format`.
- OpenRouter, [Structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs): strict `json_schema` output, schema descriptions, and `require_parameters: true` are the documented controls used here.
- OpenRouter, [Provider routing](https://openrouter.ai/docs/guides/routing/provider-selection): `order`, `only`, `allow_fallbacks`, `require_parameters`, `data_collection`, `zdr`, and `max_price` remain documented request-level routing, privacy, and cost controls.
- OpenRouter, [Reasoning tokens](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens): `reasoning.effort: minimal` maps to Google's minimal thinking level; Google determines actual usage; reasoning is charged as output; and `exclude: true` requests that reasoning not be returned.
- OpenRouter, [Usage accounting](https://openrouter.ai/docs/cookbook/administration/usage-accounting): non-streaming responses include usage in the complete response, including native token counts, reasoning counts where applicable, and `usage.cost`; no follow-up usage call is required. The response ID remains the generation identity preserved by the runner.

## Practices adopted

- Exact model: `google/gemini-3.1-flash-lite`.
- Exact provider route: `google-vertex`, with both `order` and `only` restricted to that route.
- Fallbacks disabled; all supplied parameters required; data collection denied; ZDR routing required.
- Strict JSON Schema, non-streaming requests, one fixed seed per case, and a 1,600-token total output cap.
- Minimal reasoning requested and returned reasoning excluded. The future runner still inspects the response envelope and fails closed on reasoning content rather than assuming exclusion succeeded.
- Complete source and unchanged fallible priors in source → prior → task order, with the task last.
- Exact model/provider attribution, response ID, usage, reported cost, request hash, and raw terminal-response hash required.
- The first terminal result is preserved exactly and any failure stops later transport.
- Application-side schema admission preserves provider behavior; it does not repair, heal, or semantically reinterpret output.

## Changes considered and rejected

- No switch to Gemini 3.5 Flash, another model alias, another provider, or auto-routing: any would confound the one semantic-task intervention.
- No fallback, retry, semantic retry, healing, evaluator, embedding, relationship, graph, pipeline, or runtime call.
- No streaming: it would add assembly and usage-custody complexity without testing the causal question.
- No prompt-cache or discounted-price assumption: the estimate uses full list price.
- No source or prior summary, reordering, relevance filtering, chunking, or removal.
- No prior rewrite, paired-task split, governed-pending output, deterministic semantic gate, or scalar evaluator.
- No use of the stable release as a claim that the model will follow the residual ontology; release status is operator identity, not semantic evidence.

## Conservative estimate and proposed ceiling

The deterministic estimator uses `ceil(UTF-8 context bytes / 2)` for every exact
request, assumes all 1,600 output tokens are consumed and billed at the output
rate, and applies no caching or batching discount.

| Case | Arm A estimate | Arm B estimate | Matched case estimate |
|---|---:|---:|---:|
| 01, community audio archive | `$0.00515125` | `$0.00514275` | `$0.01029400` |
| 02, serialized essay pilot | `$0.00501375` | `$0.00500525` | `$0.01001900` |
| 03, research workspace service | `$0.00503750` | `$0.00502875` | `$0.01006625` |
| 04, shared language course | `$0.00507525` | `$0.00506650` | `$0.01014175` |
| Eight calls total |  |  | `$0.04052100` |

For a future founder decision, the proposed hard ceilings are exactly `$0.03`
per matched case and `$0.12` total, with an absolute maximum of eight calls.
That is substantial margin over the conservative estimate while still failing
closed on loops, retries, fallback routing, duplicated calls, or anomalous
provider-reported cost. The founder's broader testing balance does not remove
these experiment-specific guards.

## Boundary

Current authorization remains exactly 0 provider calls and `$0.00`. The future
estimate and proposed ceilings are design facts only. A later execution requires
a separate founder action matching the final frozen contract, all eight request
hashes, call order, model and route, call ceiling, and both cost ceilings.
