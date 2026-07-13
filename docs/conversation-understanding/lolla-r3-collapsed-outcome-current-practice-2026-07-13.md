# Lolla R3 collapsed-outcome current-practice check

Status: checked before execution freeze; provider calls: zero

Date: 2026-07-13

## Question

Has current provider practice changed enough to invalidate the cheap operator or
the strict one-pass contract selected for the prospective collapsed-outcome
test?

## Official-source findings

- OpenRouter still lists `google/gemini-3.1-flash-lite` at `$0.25` per million
  input tokens and `$1.50` per million output tokens. It describes the model as
  a GA high-efficiency option for low-latency, high-volume work and simple data
  extraction. Source:
  [OpenRouter model and pricing page](https://openrouter.ai/google/gemini-3.1-flash-lite/pricing).
- OpenRouter's structured-output guidance continues to recommend
  `response_format.type=json_schema`, `strict=true`, property descriptions, and
  `require_parameters=true` for compatible routing. Response healing exists,
  but Lolla deliberately excludes it because an experiment must preserve the
  model's first result. Source:
  [OpenRouter structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs).
- OpenRouter's current routing contract still supports explicit provider
  `order`, `only`, `allow_fallbacks`, `require_parameters`, `data_collection`,
  and `max_price`. Lolla uses those controls to pin Google Vertex, deny
  fallback, require the schema parameter, deny data-collecting routes, and cap
  the advertised price. Source:
  [OpenRouter provider routing](https://openrouter.ai/docs/guides/routing/provider-selection).
- Google's current Gemini 3.1 Flash-Lite model page identifies the model as a
  stable GA release and lists structured outputs among its supported features.
  Source:
  [Google Gemini 3.1 Flash-Lite](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite).

## Local interpretation

The selected operator remains proportionate for this experiment. The question
is whether the smaller controlled outcome contract removes the observed
cross-field failure while preserving source-grounded judgment. Buying Gemini
3.5 or shopping multiple models would answer a different question and would
spend more of the founder's small test balance.

The frozen request therefore keeps:

- one Gemini 3.1 Flash-Lite call through OpenRouter;
- Google Vertex global as the only ordered route;
- strict JSON Schema and `require_parameters=true`;
- `data_collection=deny`, with no unsupported ZDR claim;
- no fallback, retry, healing, model switch, judge, or quiet control;
- a local maximum estimate below one cent and a provider-reported cost ceiling
  of `$0.01`.

This check confirms operator compatibility and pricing only. It does not prove
that the provider will accept this exact request, that its answer will pass the
mechanical compiler, or that the pressure will be useful.
