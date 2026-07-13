# Reasoning-process model/operator current-practice check

Status: frozen shortlist before compatibility calls  
Date: 2026-07-12

## Why this check exists

The v4, v4.1, and v4.2 stance-object requests failed before observable model
inference on Google's structured-output path. That is an operational problem,
not evidence that Gemini 3.1 Flash Lite is semantically too weak. The earlier
served v3 result separately showed semantic defects: belief was promoted to a
decision, source force was inflated, and a qualification was lost.

The next experiment must therefore keep two questions separate:

1. Can a particular model/operator pair accept and fill the unchanged v4.2
   schema?
2. If it can, does the model interpret ambiguous multi-turn stance changes with
   adequate source fidelity?

## July 2026 scan

The live OpenRouter catalog was checked on 2026-07-12 for models advertising
`structured_outputs`, `response_format`, `seed`, `temperature`, `max_tokens`,
and reasoning control, with at least 131,072 context tokens and catalog prices
below $0.50/M input and $2.00/M output.

Two candidates form the first controlled comparison:

| Role | Model | Catalog $/M input/output | Pinned operator $/M input/output | External intelligence index |
|---|---|---:|---:|---:|
| Cost/performance | DeepSeek V4 Flash | $0.077 / $0.154 | DeepInfra $0.09 / $0.18 | 40.3 |
| Stronger reasoning | GLM 5.2 | $0.42 / $1.32 | DeepInfra $0.93 / $3.00 | 51.1 |

DeepInfra is deliberately pinned for both. This costs more than the cheapest
GLM 5.2 endpoint, but it controls the operator while comparing model families
and retains all frozen request parameters. The first calls use a harmless
synthetic color-choice packet, not a reserved multi-turn product case.

GLM 4.7 Flash is not the first GLM candidate because GLM 5.2 is newer and is
the strongest model inside the scan boundary. Qwen 3.7 Plus remains a family-
diversity reserve. DeepSeek V4 Pro remains a within-family semantic-quality
control. Neither should be called merely because the first pair produces an
interesting result.

OpenRouter currently recommends checking model parameter support, sending
strict JSON Schema through `response_format`, and setting
`require_parameters: true`. Provider routing can be pinned and fallbacks
disabled. Lolla already follows those boundaries, and the new probes also
disable retries and response healing. See [structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs),
[provider routing](https://openrouter.ai/docs/guides/routing/provider-selection),
and the [models API](https://openrouter.ai/docs/guides/overview/models).

## Interpretation boundary

The catalog's general intelligence score is only a selection hint. It does not
measure Lolla's actual target: separating belief, action, outcome, acceptance,
reported positions, and qualifications without strengthening or dropping the
source. Only frozen Lolla cases and source-first review can measure that.

Compatibility success means HTTP success plus a strict-schema candidate and
deterministic record custody. It does not mean the interpretation is correct.
Compatibility failure means the model/operator wire cannot serve the frozen
contract; it does not mean the model is unintelligent.
