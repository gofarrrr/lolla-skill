# Conversation-state extraction probe v3

V1 and v2 are preserved operational failures: OpenRouter accepted the requests
but the selected upstream endpoint rejected the deep provider-side schema before
inference. V3 retains the same model, semantic prompts, cases, local typed
schema, deterministic sealer, zero-retry rule, cost ceiling, and review axes.
Only the wire response format changes from `json_schema` to `json_object`.

This follows Lolla's intended hybrid boundary: the model performs semantic
extraction, while deterministic code validates exact shape, vocabularies,
source quotes, identities, and graph exclusion. Invalid model output fails and
is not repaired or retried.
