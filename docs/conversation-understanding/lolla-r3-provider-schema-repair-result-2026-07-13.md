# Lolla R3 provider-schema repair result

Status: provider-free repair complete; no call authorized

Date: 2026-07-13

Provider calls: zero

## Plain-language outcome

The first R3 attempt did not fail because Lolla produced a bad reconsideration.
Google rejected the request before producing one. We have now repaired the
most likely interoperability boundary locally without changing the product
idea, deleting pressure, or adding deterministic semantic judgment.

The provider-facing schema is smaller and uses only the JSON Schema keywords
currently documented for Gemini structured output. Rules that a schema does
not need to enforce—text lengths, exact packet identity, and valid combinations
of apply/reject/park fields—are enforced by deterministic code after the model
responds. That code validates explicit labels and custody; it does not decide
whether a mental model is relevant.

The repair is ready for a future one-call attempt, but it is not authorized to
make that call. Local compatibility is not provider acceptance proof.

## What changed

The original failed R3 contract and artifacts remain byte-frozen. A separate
projection layer now:

- keeps the complete Case 01 conversation and original final answer unchanged;
- keeps all nine active R2 pressure IDs and the complete reserve unchanged;
- asks for every pressure disposition in exact packet order;
- keeps source turns, strongest application, attempted condition, reason,
  effect, public effect, and private guardrail model-generated;
- combines `failed_condition` and `reopen_condition` into one wire field named
  `disposition_boundary`, then maps it mechanically from the explicit
  disposition;
- restores `model_id`, `risk_if_forced`, and `risk_if_ignored` exactly from the
  matching immutable pressure item rather than asking the model to echo them;
- feeds the restored response into the original R3 canonical compiler;
- enforces the original text ceilings and apply/reject/park combinations
  locally;
- retains the same Gemini 3.1 Flash-Lite model, Google Vertex route, no-
  fallback/data policy, output ceiling, and one-cent envelope;
- authorizes zero calls, retries, fallbacks, healing operations, or premium
  models.

This does not dumb down the reasoning task. It removes redundant output work
and provider-specific schema constraints. The model still performs the messy
semantic task: it must attempt each lens, decide its disposition, ground it in
source turns, and produce the reconsidered answer.

## What we measured

| Provider schema | Object properties | Structural depth | Canonical bytes | String-length constraints | Pattern constraints |
| --- | ---: | ---: | ---: | ---: | ---: |
| Failed R3 request | 18 | 4 | 2,565 | 22 | 0 |
| Repaired projection | 14 | 4 | 2,411 | 0 | 0 |
| Smaller historical Gemini success | 14 | 5 | 1,946 | 8 | 2 |

The historical reference was a successful Gemini 3.1 Flash-Lite/Google call
using a smaller Lolla role schema. It shows that this model/provider can handle
a strict schema of comparable property count. It does **not** prove that its
undocumented length and pattern constraints remain portable or that any one
constraint caused the R3 rejection.

The new documented-subset lint passes the repair and deliberately fails both
the old R3 schema and the historical schema where they use keywords not listed
in current Google documentation. This is conservative by design.

The prospective maximum estimated call cost is `$0.0081855`, still below the
`$0.01` boundary. It is slightly higher than the failed request's `$0.00816425`
estimate because the prompt now explains the projection explicitly. The repair
reduces provider-schema complexity; it is not a cost-optimization claim.

## What local tests establish

- the original failed R3 contract still validates unchanged;
- the repaired provider schema uses the documented subset;
- all nine active pressure identities survive exactly;
- complete source, original-answer, portfolio, reserve, provider, and budget
  custody survive;
- apply, reject, and park compile back into the original canonical shape;
- redundant fields are restored only from the matching immutable pressure
  item;
- removed text-length rules are enforced locally;
- rejects and parks cannot claim public or private effects;
- applies require a material effect, effect custody, and a reopen/falsifier
  boundary;
- identity/order drift, schema drift, provider-policy tampering, and overlong
  text fail locally;
- no keyword, chronology, relevance, or semantic applicability gate was added;
- no provider work is authorized by the frozen repair contract.

## What remains unknown

- whether Google will accept this exact prospective request;
- whether Gemini will return a mechanically valid response on its first pass;
- whether its dispositions will be grounded and non-forced;
- whether the reconsidered answer preserves strong original advice;
- whether graph pressure adds useful friction without public bloat;
- whether the quiet case demonstrates restraint;
- the exact argument that caused the preserved R3 HTTP 400.

These remain provider and semantic evidence questions. Local code must not
pretend to answer them.

## Decision boundary

The provider-free repair is complete. The next action is founder-owned:
authorize or decline one new Gemini 3.1 Flash-Lite pressure attempt bound to the
exact repaired contract.

If authorized, the next execution must retain:

- one pressure attempt maximum;
- `$0.01` total pressure budget;
- no retry, fallback, response healing, prompt/schema mutation, or premium
  model;
- exact failure preservation if rejected again;
- source-first vector review only after a mechanically valid response;
- no quiet control unless every pressure gate passes and its separate cap is
  frozen.

## Evidence

- Repair contract: `docs/evals/lolla-r3-google-schema-repair-contract-v1.json`
- Prospective bundle: `research/lolla-r3-fresh-consumer-2026-07-13/provider-free-repair-v1/prospective-pressure-bundle.json`
- Schema comparison: `research/lolla-r3-fresh-consumer-2026-07-13/provider-free-repair-v1/schema-comparison.json`
- Documented-subset lint: `research/lolla-r3-fresh-consumer-2026-07-13/provider-free-repair-v1/documented-subset-lint.json`
- Provider-free summary: `research/lolla-r3-fresh-consumer-2026-07-13/provider-free-repair-v1/preflight-summary.json`
- Projection implementation: `engine/system_b/r3_google_schema_projection.py`
- Tests: `tests/test_r3_google_schema_projection.py`
