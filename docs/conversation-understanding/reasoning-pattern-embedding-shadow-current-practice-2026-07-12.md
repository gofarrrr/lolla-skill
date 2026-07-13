# Reasoning-pattern embedding shadow current-practice check — 2026-07-12

OpenAI's current embeddings guide documents `/v1/embeddings`, `text-embedding-3-small`, and `text-embedding-3-large`. It states that `text-embedding-3-large` returns 3,072 dimensions by default and supports an optional dimensions parameter: https://developers.openai.com/api/docs/guides/embeddings#how-to-get-embeddings

Lolla's stored chunk and activation-condition vectors are already `text-embedding-3-large` at 3,072 dimensions. The shadow therefore preserves that model and default dimension rather than migrating or reducing dimensions. One batch request is sufficient for the two unique fact-free projections.

The external API guidance establishes endpoint and vector compatibility. It does not establish semantic relevance or authorize raw conversation embedding. Lolla's stricter local boundary still applies: only an accepted typed reasoning-shape input may reach the activation matcher.

For this shadow, a research-only adapter converts already linted controlled mechanism nodes into `FingerprintPayload`. It includes only controlled mechanism, subject-scope, and state values. Evidence quotes are empty. It does not read role prose, conversation facts, entities, quantities, desired outcomes, or topic labels.

This adapter is not runtime integration authority. Its sole purpose is a frozen comparison of identical source-first and provider reasoning projections plus a missing-reversal sensitivity control.
