# Role-first v2 model-control result

Status: both model routes fail semantics; provider calls stopped; contract clarification required  
Date: 2026-07-12

## Controlled question

Was DeepSeek V4 Flash's role fragmentation mainly a cheap-model limitation, or
did the role/component contract remain ambiguous?

The GLM 5.2 control kept the same conversation, role packets, prompt hashes,
response schemas, relation derivation, protected target, and source-review
gates. Only the model/operator and frozen price changed.

## DeepSeek result

- Four of four calls were served and admitted.
- Cost: $0.00085626.
- Every role split into two one-alias, one-component records.
- Starting lost desired reach and identity uncertainty.
- Current lost the widget and stop actions.
- Qualification lost protected e056.
- The relation call joined fragments into two artificial mini-trajectories.

## GLM result

- Three role calls were served; the relation call was correctly blocked.
- Local estimated cost: $0.00375615; provider-reported cost: $0.00274815.
- Starting returned valid empty because GLM read “starting” as requiring a
  stance before the initial visible endpoint.
- Current returned two e049-only fragments and omitted e050/e051.
- Qualification returned valid empty because GLM treated user uncertainty as
  not a qualification and assistant-introduced limits as mere commentary.
- Protected e056 again disappeared.

## What we learned

The stronger, different-family model did not repair record grouping or
qualification recall. Model capacity is therefore not a sufficient explanation.
The contract is the leading cause:

- `starting` lacks an explicit endpoint definition;
- `record` versus aligned `component` identity is underspecified;
- the qualification task does not explicitly distinguish
  assistant-introduced process pressure from user endorsement;
- valid empty can be chosen before all focal aliases are considered.

This matches current extraction research that separates object detection from
field extraction and treats schema descriptions as part of the semantic
contract. It does not justify copying iterative judge/retry architectures into
Lolla.

## Decision

Stop model shopping and provider calls. No same-case retry is allowed. The next
work is provider-free and prompt/packet-only: clarify endpoint, coherent-record,
component, coverage, and speaker-ownership semantics while leaving response
schemas, validators, exact evidence custody, fan-in, and the four-call ceiling
unchanged.

That prospective amendment must pass local prompt and adversarial review. A
later live test needs another newly frozen ambiguous multi-turn case; this
journalism case is now exposed.
