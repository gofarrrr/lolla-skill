# Paired role allocation current-practice check — 2026-07-12

## Question

Is a paired current-plus-qualification semantic task compatible with current structured-output and prompt-design practice, without turning Lolla into a larger agent pipeline?

## Evidence

- OpenRouter currently recommends strict JSON Schema, clear field descriptions, and route checks for structured output: https://openrouter.ai/docs/guides/features/structured-outputs
- OpenRouter model metadata exposes structured-output support and stable model metadata for route freezing: https://openrouter.ai/docs/guides/overview/models
- Google's current prompt-design guidance recommends putting critical role definitions and behavioral constraints prominently and making classification instructions clear: https://ai.google.dev/gemini-api/docs/prompting-strategies
- Anthropic's current prompt guidance similarly recommends clear, direct instructions and explicit context: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

## Interpretation

Current practice supports one bounded task when two labels require comparative interpretation. It does not require separate calls for meanings that cannot be allocated independently. A strict schema can carry a single role-labeled record list, while deterministic code can split those explicit labels and validate exact evidence custody.

This does not make the output semantically correct. Schema validity guarantees shape, not whether a current/qualification allocation is faithful. Prospective source review remains mandatory.

## Rejected expansions

- no extra adjudicator call;
- no hard evidence-ID exclusivity;
- no deterministic alias subtraction;
- no semantic keyword or chronology classifier;
- no scalar confidence or quality score;
- no few-shot case examples that could leak the protected distinction;
- no provider or model change.

## Decision

Proceed with v2.4 as three bounded calls: independent starting, paired current-plus-qualification, and exact-ID relationship. Freeze one new case containing a legitimately shared alias before execution. Treat successful strict JSON as operational evidence only; source-review the allocation and component force before any integration claim.
