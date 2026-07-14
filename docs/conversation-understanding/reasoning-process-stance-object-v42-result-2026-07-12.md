# Reasoning-process stance-object v4.2 result

Status: wire correction passes locally; provider still rejects before inference  
Date: 2026-07-12

## Simple result

V4.2 made exactly the compatibility correction authorized after v4.1. It
removed `uniqueItems` from the three position evidence arrays sent to the
provider, while keeping the same semantic prompts, parallel-column stance
representation, compiler, exact source custody, and deterministic duplicate
rejection.

That correction worked locally. The complete v4.2 schema passes the current
`google-genai` 2.11.0 native `Schema` validator, where v4.1 fails. All 63
prompts remained byte-identical to v4.1; all 23 reviewed fixtures compiled; the
adversarial, cold-reader, and regression gates passed; and duplicate evidence
IDs are still rejected by deterministic code.

The one frozen community-space request still returned Google HTTP 400
`INVALID_ARGUMENT` before inference. There was no candidate, compiled record,
usage, cost, or semantic result. No retry, fallback, healing, or second case
was used.

## What this means

`uniqueItems` was a real current SDK incompatibility, but it was not the whole
provider problem. V4.2 also shows that a local native-SDK schema pass is a
necessary compatibility check, not proof that the routed provider will accept
the request.

The exact remaining cause is unknown. The provider response names no field or
limit. The position schema is still a relatively broad structured-output
contract: 3,597 bytes, reported depth 9, nine array-schema nodes, nineteen
property declarations, and thirty-seven enum values. Current Gemini guidance
warns that very large or deeply nested schemas may be rejected, but it does not
publish an exact rejection boundary for this request. See
[Gemini structured outputs](https://ai.google.dev/gemini-api/docs/structured-output).

Depth alone is not a sufficient explanation: v4.1 and v4.2 are shallower than
v4 but were also rejected. We also cannot claim that enum count, property
count, array count, translation through OpenRouter, or another schema feature
is the cause. Those are hypotheses, not evidence.

## Product interpretation

The stance-object idea remains locally promising because it exposes the
difference between belief, proposed action, intended outcome, willingness to
accept, and another person's reported position. But v4 through v4.2 provide no
new model-semantic evidence: their calls never reached an observable model
output.

This is an operational compatibility block, not a reason to replace semantic
interpretation with brittle deterministic gates. It is also not a reason to
keep simplifying the product contract blindly until an HTTP request happens to
pass.

## Decision and next work

V4.2 is complete as a preserved operational negative. It is not ready for
integration, graph, runtime, stability, full-case, receipt, or product-value
claims. Community space is closed. Agency acquisition remains reserved and is
not authorized under v4.2.

The next work should separate provider compatibility from semantic evaluation:

1. build a provider-free matrix that reduces one schema dimension at a time;
2. identify the smallest diagnostic contracts that distinguish enum, property,
   array, and nesting/translation hypotheses;
3. only under a new prospective authorization, use non-semantic compatibility
   probes before spending another multi-turn reasoning case;
4. once a wire contract is actually served, freeze it and return to fresh
   semantic source review;
5. keep the v4.1/v4.2 stance representation as the current local reference
   unless a documented product tradeoff justifies changing it.

Primary evidence:

- `research/reasoning-process-stance-object-v42-2026-07-12/report.json`;
- `research/reasoning-process-stance-object-v42-2026-07-12/google-schema-preflight.json`;
- `research/reasoning-process-stance-object-v42-2026-07-12/adversarial-review.json`;
- `docs/evals/reasoning-process-stance-object-v42-cold-reader-review.json`;
- `research/reasoning-process-stance-object-v42-probe-2026-07-12/result.json`;
- `research/reasoning-process-stance-object-v42-probe-2026-07-12/compatibility-diagnosis.json`.
