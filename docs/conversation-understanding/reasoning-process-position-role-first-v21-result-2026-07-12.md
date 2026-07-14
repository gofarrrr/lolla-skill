# Position role-first v2.1 result

Status: provider-free semantic-contract clarification passes; all provider calls stopped  
Date: 2026-07-12

## Why v2 was not enough

Role-first v2 fixed wire burden and failure isolation, but two model families
failed the same new journalism case:

- DeepSeek V4 Flash served all four calls but fragmented every role, omitted
  protected e056, and produced two artificial mini-trajectories.
- GLM 5.2 returned no starting role and no qualification role, fragmented the
  current role, and correctly stopped before the relationship call.

GLM's explanations exposed three contract ambiguities. It read `starting` as a
state before the conversation, treated assistant-introduced limits as irrelevant
commentary, and treated distinct objects as separate records. A stronger model
therefore did not solve the problem.

Current research supports the diagnosis without prescribing Lolla's
implementation. Schema-grounded memory work separates object detection from
field extraction; PARSE treats schema descriptions as part of the semantic
understanding contract; and Executable Schema Contracts cautions that
decomposition without stable identity can underperform. See
[schema-grounded memory](https://arxiv.org/abs/2604.27906),
[PARSE](https://aclanthology.org/2025.emnlp-industry.184/), and
[Executable Schema Contracts](https://arxiv.org/abs/2606.05415).

## The v2.1 amendment

V2.1 changes only model-visible packet and prompt meaning:

- starting is the earliest visible endpoint, usually Turn 1, not a
  pre-conversation state;
- current is the later visible endpoint;
- qualification includes user uncertainty and assistant-introduced process
  limits while preserving speaker ownership and non-endorsement;
- one record is one coherent position thread;
- evidence aliases and distinct stance objects are aligned components inside
  that record, not separate records;
- a second record is reserved for a genuinely separate concurrent thread;
- every focal alias must be reviewed before returning valid empty;
- relationships are linked by coherent thread identity, not array order.

Response schemas, validators, exact evidence custody, category enums, joins,
and the four-call ceiling are unchanged. No semantic deterministic gate, retry,
judge, object-detection stage, or forced one-record maximum was added.

## Provider-free result

- Nine reviewed cases replay: the original eight plus the pre-written
  journalism target.
- 27 role records and nine relationship records admit.
- Nine exact-ID joins complete with zero quarantine.
- All response schemas are byte-identical to v2.
- Maximum user prompt size is 5,188 bytes after avoiding repeated contract
  prose.
- Maximum provider calls remain four.
- Provider, evaluator, graph, and runtime calls are zero.
- Six v2.1-specific tests and the broader reasoning-process suite pass.

## What remains unknown

Provider-free replay shows that the clarified contract can represent reviewed
targets. It does not show that a model will obey the clarified record identity,
recover protected qualifications, or avoid forcing coherence.

## Next gate

No provider call is authorized on the exposed agency or journalism cases. The
next live evidence requires another newly frozen, ambiguous multi-turn case
with its source-first target written before execution. If v2.1 again loses a
protected qualification, stop this direct structured-extraction path and
reconsider object/record detection separately rather than tuning models or
adding retries.
