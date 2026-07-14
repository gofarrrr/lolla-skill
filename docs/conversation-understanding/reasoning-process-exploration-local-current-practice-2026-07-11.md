# Exploration-local current-practice amendment

Status: completed after the preserved Case-02 429  
Checked: 2026-07-11

## Official sources

- OpenRouter structured outputs:
  <https://openrouter.ai/docs/guides/features/structured-outputs>
- OpenRouter errors and `Retry-After` handling:
  <https://openrouter.ai/docs/api/reference/errors-and-debugging>

## Findings applied

OpenRouter currently recommends strict JSON Schema, descriptive properties,
checking model parameter support, and `require_parameters: true`. The local
harvester already follows those practices and retains local validation as the
actual admission boundary.

OpenRouter classifies `rate_limit_exceeded` as 429 and may provide a standard
`Retry-After` header. Its documentation recommends honoring that duration
before retrying. The current raw-HTTP runner did not preserve response headers,
and this failure arrived inside a completion with `finish_reason: error`, so no
evidenced retry duration exists for this call.

The current evaluation therefore preserves the 429 as an operational failure.
It does not silently retry. A later, separately frozen one-call operational
completion may occur only after a conservative cool-off, with the same packet,
prompt, schema, model, and routing; the original failure must remain in the
receipt. Future runners should preserve response headers and the canonical
`error_type` so an explicitly authorized retry can honor provider evidence
rather than a guessed delay.

## Failure-derived structured-output correction

Strict provider transport did not enforce every semantic or JSON-Schema
relationship in earlier probes. Local application validation remains required.
The exploration-local schema therefore contains only model-authored semantic
fields. Mechanical parking and absent auxiliary-ID fields are not represented
as constants for the model to echo.

## Deliberate non-adoptions

- no response-healing plugin;
- no fallback provider or model;
- no automatic retry loop;
- no retry of semantically invalid records;
- no weakening of focal/context role validation;
- no framework or SDK migration during this development result.
