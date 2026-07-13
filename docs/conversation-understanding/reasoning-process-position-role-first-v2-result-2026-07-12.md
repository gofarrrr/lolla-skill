# Position role-first v2 result

Status: provider-free contract passed; two model controls failed semantics; superseded prospectively by v2.1  
Date: 2026-07-12

## Failure-driven change

V1 made stance classification role-specific but still asked one call to find
all temporal roles and their relationship. The reserved probe showed that this
call could remain a bottleneck and delete protected qualification evidence.

V2 changes the decomposition boundary:

1. one starting-position job;
2. one current-position job;
3. one qualification job;
4. one relationship job over the admitted role records.

Each role job selects its own evidence, writes one interpretation, and
decomposes only that role's stance objects. The relationship job sees a compact
projection with exact role-record IDs, interpretations, evidence text, and
limitations. It does not receive full compiler custody or request a categorical
trajectory label.

## Provider-free result

- All eight reviewed position fixtures replayed, including the now-exposed
  agency case.
- 24 role records and eight relationship records admitted.
- All eight exact-ID joins completed.
- Zero records were quarantined.
- The maximum remains four provider calls per shard.
- Relation fan-in is capped at six role records and two relationships.
- The largest role schema is 1,854 bytes; the relation schema is 1,005 bytes;
  the closed monolith was 3,597 bytes.
- The largest user prompt is 4,017 bytes after removing provenance, hashes,
  and stance compiler details from the relation packet.
- Ten adversarial tests prove that wrong roles, invisible aliases, cross-role
  relationship IDs, quarantine, and missing relationships remain visible.
- Valid but semantically dubious object/expression pairs are still admitted for
  source review; deterministic code does not repair meaning.
- The full reasoning-process regression is 252 passing tests.

## What this proves

The role-first representation can hold the reviewed semantics without a
categorical trajectory gate, a hidden semantic join, or unbounded fan-in. It
also repairs the false-complete join condition prospectively.

## What this does not prove

- Models have not run against v2.
- Independent role jobs may still miss or misplace evidence.
- The relationship job may still force coherence or omit disagreement.
- More calls may cost more without producing better source fidelity.
- V2 has not improved reconsideration, receipts, or user decisions.

## Provider-backed outcome

A newly frozen journalism-platform case was written with a protected e056
qualification before execution. DeepSeek V4 Flash served and admitted all four
calls but fragmented every role into one-alias records, omitted e056, and
joined the fragments into two artificial trajectories. GLM 5.2 then ran the
unchanged contract as a stronger model control: it returned empty starting and
qualification roles, fragmented current, and blocked the relation call.

The repeated failure makes contract ambiguity the leading explanation, not
model capacity. See the
[model-control result](reasoning-process-role-first-model-control-result-2026-07-12.md).

## Decision and next gate

V2 is closed as an automatic contract. No additional v2 provider call is
authorized. The prospective v2.1 amendment clarifies endpoint, coherent-record,
component, coverage, and speaker-ownership semantics without changing response
schemas or validators. It must be tested only on a new pre-frozen case.
