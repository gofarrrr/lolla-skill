# Reasoning-process ledger v1

Status: Phase 1 complete; provider-free reviewed import  
Date: 2026-07-11  
Governing contract:
`docs/evals/reasoning-process-phase1-ledger-contract-v1.json`

## Why v1 was required

The Phase-0 v0 contract correctly separated the conversation, process ledger,
bounded views, assessment, final memo, and graph. Importing the existing
reviewed artifacts exposed four pieces of custody that v0 did not represent as
first-class data:

- the complete raw candidate or synthesis record;
- the exact source-artifact path and hash;
- the original source state history before canonical admission;
- scoped `not_found` or `unclear` outcomes when a reader inspected a window but
  emitted no candidate.

Flattening those into prose would make the canonical record less complete than
the artifacts it claimed to preserve. V1 is therefore a prospective ledger
extension. It does not alter or overwrite the frozen Phase-0 evidence package.
The bounded-view and assessment contracts remain v0.

## Frozen input boundary

Phase 1 imports only the five source-reviewed provider-free Phase-A-v2 event
and synthesis ledgers. Those artifacts were selected because this phase tests
lossless representation and custody, not automatic model quality.

All records in the frozen inputs are imported:

- 79 local harvest events;
- 55 fresh-context synthesis records;
- 105 turn-window family outcomes;
- 15 conversation-level synthesis-family outcomes;
- 70 original messages across five conversations.

Older model-generated extraction outputs and their source-review failures remain
preserved in their historical evidence packages. They are not silently mixed
into this reviewed fixture ledger, and Phase 1 makes no claim that they are
semantically equivalent to the Phase-A-v2 source.

## Canonical ledger additions

Each observation now preserves:

- its original source artifact and record identity;
- a hash and exact copy of the complete raw record;
- the source-declared family and a reversible primary-family projection;
- exact source-span IDs;
- the original source state history followed by canonical import disposition;
- explicit source-declared relations for syntheses;
- fixture provenance without invented model or prompt identity;
- a false direct-graph-routing flag.

Each imported artifact records its path, hash, schema, record count, scoped
outcome count, and complete-import status. Every source family/window outcome is
preserved separately from candidate observations, so `not_found` remains an
observed scoped result rather than being converted into an error or fabricated
evidence.

## Family projection boundary

The projection is frozen and purely based on declared source-family labels:

| source | destination index |
| --- | --- |
| harvest `contributions` | position and decision trajectory |
| harvest `thread_events` | exploration and alternatives |
| harvest `constraint_claims` | evidence and assumption discipline |
| synthesis `positions` | position and decision trajectory |
| synthesis `threads` | uncertainty and unresolved state |
| synthesis `constraints` | evidence and assumption discipline |

Code does not read candidate prose to choose a family. The mapping drops no
record, merges no record, and cannot be used as an exclusive view gate. The
original family remains attached, and Phase 2 may use evidence across families.
This is mechanical inherited placement, not proof that the semantic role is
correct.

## Provider-free result

Across all five ledgers:

- observations: 134;
- scoped outcomes: 120;
- observed scoped absences: 58;
- terminal failures: 0;
- source-span references: 158, covering 74 unique spans;
- explicit synthesis-to-event relations: 79;
- raw imported record content: 179,915 UTF-8 bytes;
- direct graph seeds: 0;
- provider, embedding, evaluator, graph, pipeline, and runtime calls: 0.

Observation distribution:

| process family | observations |
| --- | ---: |
| evidence and assumption discipline | 93 |
| position and decision trajectory | 20 |
| exploration and alternatives | 16 |
| uncertainty and unresolved state | 5 |
| challenge and revision response | 0 |

The final zero is a product-relevant missingness finding. These frozen reviewed
artifacts were designed around position, thread, and constraint state; they do
not contain a dedicated challenge/revision family. The ledger does not infer
that the conversations lacked correction or counterpressure. It says only that
the selected imported candidate artifacts do not represent that dimension
directly.

## Failure behavior

Adversarial provider-free tests establish that:

- unknown source spans are quarantined with an `RP1` terminal failure;
- raw-proposal hash mismatch is quarantined with `RP0`;
- unknown synthesis-event lineage fails closed;
- raw-record mutation after import is detected;
- deterministic semantic relation authority is rejected;
- graph-boundary changes are rejected;
- family placement does not change when candidate words are replaced, proving
  that the importer does not use keyword semantics.

Quarantined raw data remains preserved. Invalid lineage is not copied into the
normalized relation surface, but remains visible in the exact raw record and
terminal failure.

## Non-claims and next boundary

Phase 1 proves lossless provider-free import and custody. It does not prove:

- automatic extraction quality;
- semantic family placement;
- reasoning-process completeness;
- bounded-view usefulness;
- final-output quality;
- graph or runtime value.

Phase 2 may now design bounded question-specific views over these ledgers. It
must measure input counts and bytes, preserve every input disposition, allow
cross-family evidence, and keep the challenge/revision gap visible. It may not
make provider calls or manufacture missing semantic coverage.

