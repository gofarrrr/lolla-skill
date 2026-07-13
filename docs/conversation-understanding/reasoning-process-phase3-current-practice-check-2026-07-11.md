# Phase 3 current-practice check

Status: completed before provider calls  
Checked: 2026-07-11

## Scope

This check covers only the five-call bounded reasoning-process development
probe: model availability, structured response transport, provider routing,
exact-source validation, prompt decomposition, and evaluation custody. It does
not authorize graph, runtime, embeddings, final-answer evaluation, or a model
framework migration.

## Official sources checked

- OpenRouter model catalog: <https://openrouter.ai/api/v1/models>
- OpenRouter structured outputs:
  <https://openrouter.ai/docs/guides/features/structured-outputs>
- OpenRouter provider routing:
  <https://openrouter.ai/docs/features/provider-routing>
- the Phase-0 official-source check in
  `reasoning-process-current-practice-check-2026-07-11.md`

## Adopted for Phase 3

- `google/gemini-3.1-flash-lite` through OpenRouter because this is Lolla's
  established small-call model line and the current catalog lists strict
  structured output, `temperature`, `seed`, reasoning control, and the needed
  token parameter;
- one narrow process question per call;
- strict JSON Schema with every property required and
  `additionalProperties: false` at each object;
- a 2,558-byte, depth-8 provider schema under the frozen 12,000-byte/depth-8
  ceilings;
- `provider.require_parameters: true` and `allow_fallbacks: false`;
- temperature zero and seed zero, without claiming bitwise determinism;
- reasoning explicitly disabled with the supported reasoning control;
- exact speaker, turn, and contiguous quote in the response, followed by local
  deterministic resolution to stable source span IDs;
- application validation after schema validation, including exact source,
  cross-field state, auxiliary-ID, fan-in, and product-boundary checks;
- no retry, fallback model, response healing, evaluator call, or silent repair.

## Prospective response-contract correction

The Phase-0 provider projection asked the model to return stable span IDs and
source observation IDs. Phase 2 demonstrated that a target may be visible in
the authoritative conversation while absent from the auxiliary ledger. Asking
the model to invent an unseen span ID would therefore be an invalid contract.

Phase 3 instead asks for exact `speaker`, `turn_index`, and `quote`. Local code
resolves the quote to a stable source span or quarantines the result. Auxiliary
observation IDs are optional and locally checked. The model explicitly declares
that the unselected complement may be parked for this view, allowing compact
output with complete deterministic disposition expansion.

To keep the provider schema within depth eight, evidence is a deduplicated
top-level table and view items reference evidence IDs. This is a transport
shape only; it does not change semantic authority.

## Deliberate non-adoptions

- no model migration or flagship-model comparison: the purpose is to test the
  decomposed architecture on Lolla's established small, repeatable OpenRouter
  route, not to confound architecture with a provider change or maximum spend;
- no model judge or automatic semantic scorer;
- no chain-of-thought or reasoning-token request;
- no dynamic semantic pruning of the conversation or auxiliary ledger;
- no use of the Phase-2 protected targets or source-review addenda in prompts;
- no conversation-only ablation inside the five-call baseline;
- no new agent, prompt, or validation framework.

## Remaining uncertainty

Catalog support does not prove that the routed endpoint will accept the exact
schema, nor that valid structured output will preserve the five protected
process meanings. Those are the operational and semantic questions Phase 3 is
designed to answer. A valid empty response remains allowed, but it will fail a
known protected target during source-first review rather than being silently
converted into coverage.
