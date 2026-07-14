# R4 semantic-distinction current-practice check

Status: complete before prospective request previews

Date checked: 2026-07-14

Provider calls: 0

## Question

After the corrected R4 diagnostic completed mechanically but failed restraint,
what current prompting and structured-output practices should inform the next
provider-free contract without redesigning the architecture?

## Current primary guidance

Google's current [Gemini prompt design strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)
recommend clear and specific instructions, explicit definitions for ambiguous
terms, consistent delimiters, critical behavioral constraints in the system
instruction, and—especially for long contexts—placing the context before the
specific task at the end. The guide also treats examples as a strong way to
show the intended distinction and emphasizes iterative evaluation rather than
assuming one prompt is universally correct.

Google's [long-context guidance](https://ai.google.dev/gemini-api/docs/long-context)
likewise says that questions usually perform better after the supplied context
and warns that multi-needle retrieval is harder than finding one isolated fact.
That supports Lolla's decision to keep this reader narrow and to test
unresolved/reopen meaning separately from later reasoning pressure.

Google's [structured-output guidance](https://ai.google.dev/gemini-api/docs/structured-output?lang=rest),
last updated 2026-07-07, recommends clear schema descriptions, strong types,
explicit prompt instructions, application validation, and robust handling of
schema-compliant but semantically wrong values. It also warns that very large
or deeply nested schemas may be rejected. This matches the observed R4 result:
strict JSON and local admission succeeded, but semantic correctness and
restraint did not.

OpenRouter's [structured-output documentation](https://openrouter.ai/docs/guides/features/structured-outputs)
continues to recommend `json_schema`, `strict: true`, property descriptions,
and `provider.require_parameters: true`. Its
[provider-routing documentation](https://openrouter.ai/docs/guides/routing/provider-selection)
continues to expose exact provider order, fallback control, data-collection
denial, and ZDR routing. The R4 transport contract already implements those
practices, so no provider or schema redesign is earned.

OpenRouter's [reasoning-token guidance](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens)
documents that reasoning consumes the output allowance, that `max_tokens` must
leave room beyond the reasoning budget, and that returned reasoning may appear
as `reasoning`, the `reasoning_content` alias, or typed
`reasoning_details`. This confirms two existing decisions: keep the corrected
minimal-reasoning allocation prospective, and reuse the R3 content-shape
validator rather than treating any reasoning-detail metadata as returned
reasoning content.

## Adopted changes

The prospective v2 contract therefore:

- keeps the complete authoritative conversation before the final task;
- uses consistent XML-style sections for role, authority, semantic contract,
  contrastive examples, output rules, context, and task;
- defines unresolved matter, reopen condition, and additive relationship with
  explicit positive and negative contrasts;
- requires the model to compare candidates against the final conversation
  state and fallible current-position interpretation;
- says that later placement alone is not proof of resolution;
- makes zero and ambiguous outcomes first-class;
- keeps the existing small strict schemas and deterministic custody compilers;
- reuses R3's reasoning-detail shape inspection for prospective R4 response
  custody;
- reserves semantic verdicts for source-first review rather than local code.

## Rejected changes

This check does not justify:

- a keyword, chronology, or rule-based semantic classifier;
- a second deterministic gate that decides whether an adopted safeguard counts
  as uncertainty;
- another schema decomposition or additional provider call;
- response healing, retries, model comparison, or premium-model use;
- graph, runtime, revised-answer, receipt, or product-claim changes;
- a scalar quality score.

## Evidence boundary

Current practice supports the shape of the v2 prompt contract. It does not
prove that Gemini 3.1 Flash-Lite—or any other model—will follow that contract.
The exposed Case 02/03 outcomes are development evidence. Any future provider
validation must use the separately frozen Case 01/04 holdout and source-first
vector review.
