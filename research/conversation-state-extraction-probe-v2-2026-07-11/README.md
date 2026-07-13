# Conversation-state extraction probe v2

Status before execution: frozen, dry-run passed, one-time authorization issued.

V1 is preserved as a failed experiment: OpenRouter routed the structured-output
request to Google AI Studio, which returned `INVALID_ARGUMENT` before output or
usage. V2 changes only the response schema's fixed `schema_version` keyword from
JSON Schema `const` to a one-value `enum`, matching Google's documented schema
subset. The extraction prompt, two cases, model, cost ceiling, stop rule,
source-first axes, and all graph/full-pipeline prohibitions remain unchanged.

Authentication remains OpenRouter. No Google API key is used. No OpenAI call is
part of this probe because it contains no embeddings.
