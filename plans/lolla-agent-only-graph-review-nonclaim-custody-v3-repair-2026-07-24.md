# Agent-only graph review nonclaim-custody V3 repair plan

Date: 2026-07-24

Status: provider-free repair complete; semantic execution not authorized

Owner: existing offline Product Delta evaluation

Machine contract:
[`lolla-agent-only-graph-review-nonclaim-custody-v3-contract-v1.json`](../docs/evals/lolla-agent-only-graph-review-nonclaim-custody-v3-contract-v1.json)

Provider/API calls authorized or made: **0**

Provider/API cost authorized or incurred: **$0.00**

## One falsifiable question

Can deterministic input-packet custody preserve the exact ten post-reveal
nonclaims while the model-authored response omits every nonclaim echo field?

The allowed causal change is only the ownership of those ten statements:

```text
V2
  deterministic packet contains nonclaims
  + model must copy the same ten strings into its response

V3
  deterministic packet owns stable IDs, exact strings, order, count, and hash
  + model response contains no acknowledgment or echo field
```

The source case, eight answers, two valid V2 blind reviews, deterministic
lineage reveal, eight comparison records, response semantics, and Product
Delta validation remain frozen.

## Why the V2 boundary failed

Both V2 post-reveal contexts returned ten strings, but both paraphrased the
frozen nonclaims. The JSON Schema required ten strings; it did not require the
exact ten values. The local validator correctly rejected both first-terminal
payloads. The result remained `not_evaluable`.

That failure measured exact text reproduction, not graph contribution. Asking
the model to restate the experiment limits also created a misleading authority
signal: a copied string or schema-forced boolean would not prove that the model
understood or followed the limit.

## V3 ownership decision

Deterministic code owns exact nonclaim presentation.

Each V3 packet contains:

- stable IDs `NC-01` through `NC-10`;
- the exact ten V2 nonclaim strings;
- exact order and count;
- one SHA-256 over the compact ordered string array;
- an explicit `model_response_echo_required: false`;
- an explicit `proves_internal_compliance: false`.

The V3 response schema removes `nonclaims_acknowledged`. It does not replace
the field with booleans, a summary, or a second free-text acknowledgment.

This proves which constraints were supplied in the packet. It does not prove
that a future reasoner followed them. Semantic compliance remains a property
of the complete response and evidence, not a deterministic receipt claim.

## Existing owner and absence of parallel systems

This repair deepens Product Delta:

- V2 packets and schemas remain immutable inputs;
- the existing conservative JSON-Schema-subset validator remains the
  structural owner;
- the existing Product Delta post-reveal validator remains the semantic-shape
  owner, with its historical echo check enabled by default;
- V3 invokes the same validator with only the prospective echo requirement
  disabled;
- no new graph compiler, reader, planner, conversation interpreter, sidecar,
  or runtime is created.

## Frozen inputs

The machine contract byte- and hash-locks:

- the consumed V2 envelope contract;
- both V2 post-reveal schemas and shape fixtures;
- both V2 post-reveal packets;
- both valid V2 blind reviews;
- both V2 post-reveal failure receipts;
- the V2 consolidated `not_evaluable` result.

Any drift stops the provider-free builder.

## Provider-free fixture gate

For each lane, V3 creates:

1. a prospective V3 response schema;
2. a deterministic V3 input packet;
3. a valid structural fixture with no nonclaim echo;
4. a legacy-shaped fixture that still contains
   `nonclaims_acknowledged`.

The gate requires:

- two valid fixtures with zero schema or Product Delta errors;
- two legacy fixtures rejected only for the unexpected echo field;
- two input packets with zero exact nonclaim-custody errors;
- a mutation of a nonclaim to fail exact statements and hash custody in tests;
- zero semantic contexts.

These are development fixtures. They do not validate response meaning, model
compliance, graph value, answer quality, or usefulness.

## Current authorization

Authorized and completed:

- provider-free implementation;
- schemas, packets, fixtures, hashes, and receipt;
- exact V2 input locks;
- local tests and documentation.

Not authorized:

- a corrected V2 response;
- semantic salvage from either failed V2 terminal payload;
- a V3 Codex context;
- a provider call;
- graph, traversal, policy, compiler, planner, skill, runtime, or interface
  change;
- principal-human or private-archive work;
- graph, answer-quality, or usefulness claims.

## Prospective run boundary

The contract describes, but does not authorize, a possible two-context V3 run:

- reuse the two already-valid V2 blind reviews;
- run one fresh primary and one fresh skeptical post-reveal context;
- run both once even if one fails;
- maximum two Codex contexts;
- zero generation and zero blind-review contexts;
- zero repository provider/API calls and `$0.00` repository provider cost;
- no retry, fallback, healing, replacement, reformatting, or semantic salvage;
- preserve each first-terminal state.

Codex platform route, tokens, and economic cost would remain unavailable to the
repository operator unless the platform exposes them. They must not be
reported as zero.

The exact separate authorization would be:

```text
AUTHORIZE_LOLLA_GRAPH_REVIEW_NONCLAIM_CUSTODY_V3: reuse_frozen_v2_blind_reviews=true; post_reveal_contexts=2; maximum_codex_contexts=2; repository_provider_api_calls=0; repository_provider_api_cost_usd=0.00; no_retry=true
```

This plan does not supply that authorization.

## Stop rules

Stop before execution if:

- any frozen V2 byte count or SHA-256 changes;
- any semantic response field other than the nonclaim echo changes;
- current Codex CLI or official structured-output behavior is not rechecked;
- the exact future authorization is absent;
- work would require a provider API, private archive, principal-human field,
  graph change, runtime change, or interface change.

Never report input custody as internal model compliance or schema validity as
semantic correctness.
