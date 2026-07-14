# R4 matched residual holdout: current provider practice and pricing

Date checked: 2026-07-14

This is a provider-free custody record for a possible future matched experiment. It records the official documentation and conservative arithmetic used while freezing the design. It does not authorize, request, or perform provider calls.

## Primary documentation checked

- Google, [Gemini 3.1 Flash-Lite model](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite): the stable model supports structured outputs and thinking, with a 1,048,576-token input limit and a 65,536-token output limit. The holdout's 1,600-token output cap remains well within that published boundary.
- Google, [Gemini 3 developer guide](https://ai.google.dev/gemini-api/docs/gemini-3): Gemini 3.1 Flash-Lite standard text/image/video input is listed at $0.25 per million tokens and output, including thinking tokens, at $1.50 per million tokens.
- Google, [Structured outputs](https://ai.google.dev/gemini-api/docs/structured-output): structured output uses a supported subset of JSON Schema. The documentation recommends clear property descriptions and application-side validation because syntactically valid JSON can still be semantically wrong.
- Google, [Long context](https://ai.google.dev/gemini-api/docs/long-context): for many long-context queries, placing the question at the end can improve the response. Both matched arms therefore preserve source, then prior, then task ordering and the task-at-end invariant.
- Google, [Prompt design strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies): few-shot examples should use consistent formatting and varied examples. The experiment keeps each already-frozen arm's own examples and changes no development evidence after freeze.
- OpenRouter, [Gemini 3.1 Flash Lite provider page](https://openrouter.ai/google/gemini-3.1-flash-lite-20260507/providers): the route advertises the same $0.25 input and $1.50 output prices and support for `reasoning`, `max_tokens`, `seed`, and `response_format`.
- OpenRouter, [Structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs): strict JSON Schema is supported through `response_format`, and `require_parameters` can restrict routing to providers that support all supplied parameters.
- OpenRouter, [Provider routing](https://openrouter.ai/docs/guides/routing/provider-selection): `order`, `only`, `allow_fallbacks`, `require_parameters`, `data_collection`, `zdr`, and maximum-price controls are documented provider-selection and privacy controls.
- OpenRouter, [Reasoning tokens](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens): `reasoning.effort: minimal` maps to Google's minimal setting, but the provider determines the actual reasoning allocation; reasoning tokens are charged as output. `reasoning.exclude: true` requests that reasoning not be returned.
- OpenRouter, [Usage accounting](https://openrouter.ai/docs/cookbook/administration/usage-accounting): completed non-streaming responses include token usage and provider-reported cost. The future runner requires both and preserves the first raw terminal result.

## Practices adopted in the frozen design

- Exact model: `google/gemini-3.1-flash-lite`.
- Exact provider route: `google-vertex`, with `order` and `only` limited to that route.
- Fallbacks disabled and all supplied parameters required.
- Data collection denied and zero-data-retention routing required.
- Non-streaming requests, strict JSON Schema response format, one fixed seed per case, and a 1,600-token output cap.
- Minimal reasoning requested and returned reasoning excluded. The future runner treats returned reasoning content as a custody failure; it does not assume that the request makes internal reasoning usage or billing zero.
- Complete source and unchanged fallible-prior context in source → prior → task order, with the task at the end.
- Exact provider identity, generation identity, usage, reported cost, request hash, and raw-response hash required for every terminal result.
- First failure stops the experiment. There are no retries, fallback routes, response healing, evaluator calls, embeddings, relationship calls, graph calls, pipeline calls, or runtime calls.

## Changes considered and rejected for this matched design

- No switch to a newer model alias or alternative provider route: either would confound the single semantic-task intervention.
- No provider auto-routing or fallback: either would weaken operator attribution and matched custody.
- No streaming: it would add assembly and usage-custody complexity without testing the causal question.
- No prompt caching assumption or discounted-token assumption: neither is needed for the tiny budget, and relying on either would make the estimate less conservative.
- No reduction of source, removal or re-authoring of priors, relevance filtering, summary, chunking, or task splitting: each would change a matched dimension.
- No deterministic semantic gate or output healing: either could obscure the provider contract's actual behavior.
- No scalar evaluator or model-graded score: the source-first vector and precommitted categorical matrix remain the evaluation boundary.

## Conservative estimate and proposed ceiling

The builder estimates input tokens for every exact request component using the repository's declared deterministic estimator and assumes that every call consumes the full 1,600-token output allocation. The arithmetic uses $0.25 per million input tokens and $1.50 per million output tokens. It does not apply caching, batching, or other discounts.

| Case | Arm A maximum estimate | Arm B maximum estimate | Matched case estimate |
|---|---:|---:|---:|
| 01, oral-history release | $0.0053845 | $0.0053760 | $0.0107605 |
| 02, serialized-audio pilot | $0.0052450 | $0.00523625 | $0.01048125 |
| 03, research-data stewardship | $0.0053245 | $0.00531575 | $0.01064025 |
| 04, cross-campus language program | $0.0052945 | $0.0052860 | $0.0105805 |
| Eight calls total |  |  | $0.0424625 |

The proposed future hard ceilings are $0.015 per matched case and $0.06 total. Those ceilings leave room for tokenizer-estimation error and provider-counted reasoning tokens while remaining small and independently enforceable. They are proposals embedded in a non-authorizing package, not permission to spend.

## Boundary

The current package authorizes exactly 0 provider calls and $0.00 provider cost. The estimate and proposed hard ceiling do not authorize execution. A later execution would require a separate founder action matching the exact frozen contract, call plan, call ceiling, and cost ceilings.
