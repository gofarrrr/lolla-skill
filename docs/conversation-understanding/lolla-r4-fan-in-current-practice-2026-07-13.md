# R4 fan-in current-practice check

Date: 2026-07-13

Scope: explicit operational result states, missingness, failure details, and
deterministic validation for the provider-free conversation-state fan-in. This
check does not select an LLM, change a prompt, or propose runtime integration.

## Sources checked

- [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12/draft-bhutton-json-schema-00)
  defines `oneOf` as successful only when exactly one listed schema validates.
  It also provides `const`, `required`, conditional applicators, and closed
  object validation needed for an explicit state-tagged result contract.
- [OpenAPI Specification 3.2.0](https://spec.openapis.org/oas/latest.html)
  describes `oneOf`/`anyOf` polymorphic payloads and discriminator hints. It
  explicitly says a discriminator cannot change JSON Schema validation and
  that possible alternatives must be enumerated.
- [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457.html) separates stable
  machine-readable problem identity from human-readable `detail`, says clients
  should not parse `detail`, and warns against leaking implementation internals.
  Lolla is not adopting the HTTP Problem Details format; it is adopting that
  separation principle for local failure and missingness records.
- [Pydantic union guidance](https://pydantic.dev/docs/validation/latest/concepts/unions/)
  is a maintained practitioner implementation. It recommends discriminated
  unions as more predictable than untagged unions and notes that smart
  untagged matching behavior may evolve.

## Adopted

1. Every reader result has a required explicit `state` tag.
2. The five variants are closed and mutually exclusive: `complete`,
   `completed_zero`, `partial`, `failed`, and `missing`.
3. Unknown states and controlled issue codes fail closed.
4. Machine behavior uses `state` plus a controlled issue `code`; it never
   parses `safe_detail`.
5. `completed_zero` means only that one reader completed with zero records. It
   is not a semantic absence claim.
6. Deterministic replay validates identities, canonical hashes, exact source
   locators, relationship endpoints, counts, and bounds.

## Deliberately not adopted

- No Pydantic dependency: the repository's provider-free boundary is small,
  standard-library validation is already established, and a new framework
  would add migration surface without improving the semantic boundary.
- No OpenAPI discriminator extension: pure JSON Schema `oneOf` plus an explicit
  `state` constant is sufficient, and this is not an HTTP interface.
- No wholesale RFC 9457 error envelope: Lolla already has a domain-specific
  artifact format. Only the machine-code/human-detail and privacy lessons are
  relevant.
- No untagged or order-dependent union matching, default variant, inferred
  absence, or catch-all success state.

## Product consequence

This practice check improves operational clarity, not semantic intelligence.
It prevents a missing read, a failed read, and a completed zero-record read
from collapsing into one ambiguous empty array. It does not tell the system
what a conversation means or whether any pressure is useful.
