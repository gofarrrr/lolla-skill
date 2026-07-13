# Role-first record fragmentation: problem-class research

Status: research escalation complete; one unchanged-contract model control authorized  
Date: 2026-07-12

## Exact local signature

Role-first v2 reduced every schema and gave starting, current, and
qualification independent source context. DeepSeek V4 Flash served all four
calls and produced valid, admitted records. Yet:

1. every role became two one-alias, one-component records rather than one
   coherent multi-evidence role record;
2. the starting reader treated organization size as a stance and dropped the
   desired benefit plus identity uncertainty;
3. the current reader omitted e051's conditional widget and stop actions;
4. the qualification reader omitted protected e056;
5. the relation reader faithfully joined the fragments into two artificial
   mini-trajectories.

The same important failure—loss of a protected qualification—has now survived
the combined contract, decomposition v1, and role-first v2. Constitution v3
therefore blocks another prompt edit, provider swap, or architecture layer
until the broader problem class is checked.

## What external evidence adds

The 2026 schema-grounded memory paper separates object detection, field
detection, and field-value extraction. Its object-level accuracy and full
output accuracy are separate metrics, and its best system uses iterative
control rather than assuming that field-valid records have correct object
boundaries. This maps to Lolla's failure: the model filled role fields but did
not identify the coherent role record they belonged to. See
[From Unstructured Recall to Schema-Grounded Memory](https://arxiv.org/abs/2604.27906).

The 2025 PARSE paper treats JSON Schema as a natural-language understanding
contract and reports that ambiguous or incomplete schema specifications can
produce unreliable extraction even under syntactic constraints. Lolla's phrase
“split distinct objects” can plausibly be read as split records, although we
intended separate aligned component indices inside one coherent role record.
See [PARSE](https://aclanthology.org/2025.emnlp-industry.184/).

The 2026 Executable Schema Contracts paper uses explicit identity keys and
structural linking and reports gains over decomposition-based baselines in its
own retrieval setting. The task is not directly equivalent to conversation
interpretation, but it cautions against assuming decomposition is sufficient
without stable object identity. See
[Executable Schema Contracts](https://arxiv.org/abs/2606.05415).

These sources support two competing local explanations:

- contract ambiguity: the model did not understand record versus component
  identity;
- capacity: a low-cost model understood the shallow schema but not the source
  grouping and recall burden.

They do not tell us which explanation dominates Lolla.

## Adopted next experiment

Before changing the prompt or schema, run one stronger, different-family model
on the exact frozen role-first contract and the same already-exposed
development case. GLM 5.2 through pinned DeepInfra is the existing July-2026
stronger control. The comparison answers one question: does a stronger model
recover coherent multi-evidence role records and protected e056 without any
contract assistance?

The control keeps:

- identical role packets, schemas, prompt hashes, relation derivation, target,
  source-review gates, and four-call ceiling;
- no retries, fallback, judge, response healing, graph, or runtime work;
- separate wire, admission, record-grouping, field-recall, protected-target,
  and relationship results.

## Rejected for now

- No same-model prompt retry.
- No deterministic merge of fragments based on alias order or prose.
- No forced one-record maximum; that could hide genuinely concurrent position
  threads and would trade false fragmentation for silent deletion.
- No judge-in-the-loop, local semantic retries, or self-correcting agent. Those
  may help in the cited systems but add calls and semantic authority that Lolla
  has not earned.
- No object-detection stage yet. It would add another bottleneck and at least
  one call before we know whether model capacity is the limiting variable.

## Decision rule after the control

- If GLM preserves coherent role grouping and protected e056, model capacity
  becomes the leading local explanation and model/cost selection can proceed.
- If GLM repeats fragmentation or protected-evidence loss, the contract is the
  leading explanation. Stop model shopping and design a provider-free record
  identity amendment before any more calls.
- In neither outcome does one development case prove production readiness.
