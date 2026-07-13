# Case 01 extraction-admission smoke v1 — review

Status: **passed; untouched Stage A contract planning is authorized**

## What ran

The frozen contract
`c4b3aef3990c4a7bb28ca4816562ba35f3d3a86b429ed50ed5437af2f3af1638`
ran exactly once with run ID
`admission_smoke_case01_v1_20260710_a1`.

The fixture was the heavily reused six-turn enterprise-logo-beta
conversation. Its prior semantic, downstream, receipt, review, and Teacher use
was disclosed before the call. It is permanently excluded from future holdout
claims.

## Result

All frozen admission gates passed:

- output parent and call sidecar were absent before execution;
- output preflight created the parent before the provider boundary;
- capture was full and healthy: 6/6 turns, zero omitted;
- one initial OpenRouter call ran; no quote-repair or experiment retry ran;
- the transactional sidecar persisted one exact call record;
- `provider_call_custody` consistently recorded attempted call, persisted
  record, and admissible extraction;
- all three reasoning passages were literal source spans; zero failed quote
  matches;
- requested model was exactly `google/gemini-3.1-flash-lite`;
- served model was the compatible dated alias
  `google/gemini-3.1-flash-lite-20260507`, with zero attribution mismatch;
- usage was complete: 1,552 prompt tokens, 535 completion tokens, 2,087 total;
- estimated cost was `$0.001190`, below the frozen `$0.02` ceiling;
- wall time was 2.618 seconds, below the frozen 120-second ceiling;
- no embeddings, graph, pressure pipeline, reconsideration, evaluator, or
  downstream arm ran.

The review-safe result and extraction contain no raw provider response. Raw
content remains only in the local run-scoped call sidecar. A durable sanitized
`call-evidence.json` preserves every non-content call field plus the raw
response hash and character count, so restart does not depend on `/tmp`.

## What this proves

This is clean live evidence that the repaired extraction-admission boundary
can, on one familiar strategic case:

- prepare and preserve its artifacts;
- distinguish call attempt, call record, and admissible extraction;
- preserve complete conversation and exact quote custody;
- enforce model, call, time, token, and cost accountability;
- seal a one-attempt result without retry.

It repairs the operability gate that blocked progression after Case 12.

## What this does not prove

The extraction was not semantically scored in this smoke. A passed custody
gate does not establish that its interpretation was complete, wise, or useful.
This one short, familiar case does not prove long-conversation reliability,
failure-path reliability under a live provider error, graph relevance,
pressure quality, reconsideration value, receipt usefulness, or better
decisions.

The smoke does not authorize runtime integration or a paired downstream call.
It does not restore Case 01 as untouched evidence, and this run ID will never
be invoked again.

## Decision and next boundary

The next separate goal may select one genuinely untouched case and freeze a
Stage A extraction-plus-pipeline contract before any call. Planning and
contract freeze are authorized. Execution is authorized only through that new
prospective contract with source, prompts, code, provider/model, direct
OpenAI-only embedding policy, call/time/cost ceilings, stop rules, and no-retry
rules locked first.

Stage B remains blocked. No control or treatment answer may be generated until
the new Stage A run passes and its pressure packet is source-traceable and
hash-locked before either downstream arm.

- Stage A contract planning: **authorized**
- Stage A execution outside a frozen contract: **not authorized**
- paired downstream calls: **not authorized**
- graph or runtime promotion: **not authorized**

## Verification

- 87 focused extraction, custody, model-attribution, capture, run-state, cost,
  and pipeline-compatibility tests passed before/around contract freeze;
- 3,980 non-network repository tests passed with one expected skip under
  Python 3.12 after the sealed result and docs were added;
- the legacy stability-check module remained excluded because it makes
  unmocked OpenAI embedding calls;
- contract, result, extraction, call-evidence, and decision JSON parse cleanly;
- Python compilation, prompt/hash revalidation, secret/path scans, and
  whitespace checks passed;
- provider calls made by this goal: exactly one frozen OpenRouter extraction
  call; zero embedding, evaluator, graph, reconsideration, or experiment-retry
  calls.
