# Role-boundary and expression current-practice check — 2026-07-12

## Question

Does current practice support a small prompt/packet clarification for semantic role boundaries and expression ownership, or does it justify a more complex architecture before another bounded test?

## Sources checked

- Google Gemini's current prompt-design guidance says to prioritize critical behavioral constraints and role definitions, and to make instructions clear and specific: https://ai.google.dev/gemini-api/docs/prompting-strategies
- Anthropic's current prompting guidance likewise emphasizes clear, direct instructions and explicit context: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- OpenRouter's current structured-output guidance recommends strict JSON Schema plus clear property descriptions, and distinguishes schema-valid output from the semantic work described by the prompt: https://openrouter.ai/docs/guides/features/structured-outputs
- OpenRouter's model metadata exposes whether a route supports structured outputs, while provider preferences can require supported parameters: https://openrouter.ai/docs/guides/overview/models

## Application to Lolla

These sources support the narrow v2.3 direction:

1. Put the role distinction and expression meaning directly in the model-visible contract.
2. Retain strict structured output for shape and exact deterministic admission.
3. Do not infer semantic correctness from schema validity.
4. Keep the exact model/operator route fixed during a prospective comparison.

The sources do not prove that clearer instructions will solve Lolla's semantic problem. They also do not justify retries, response healing, deterministic keyword classification, additional gating layers, or a new provider. That evidence must come from a prospectively frozen source review.

## Examples decision

Few-shot examples can improve classification, but this experiment does not add them. A role example close to the test cases could leak the protected distinction and make it harder to know whether the model understood the general contract or copied a pattern. V2.3 therefore uses concise definitions and contrastive boundary statements only.

## Decision

Proceed with provider-free v2.3 and one genuinely new source-first transfer case if local gates pass. Preserve v2.2's nested wire, strict schema, exact route, zero retry, and source review. Treat any successful wire result as operational evidence only until semantic review is complete.
