# Accountability Implementation Decision Gate v0

Status: PR65 docs-only decision gate
Date: 2026-06-29
Owner: Lolla maintainers

PR65 decides what, if anything, should move next from the
Semantica-inspired accountability lane into a future implementation slice. It
does not implement that slice.

Decision:

```text
Outcome A: implement audit_decision_record exporter next.
```

Recommended future slice:

```text
PR66 Audit Decision Record Read-Only Exporter v0
```

PR66 is only a recommendation from this decision gate. PR65 does not start,
implement, scaffold, test, or partially approve PR66.

PR66 has now landed separately as:

- [Audit Decision Record Read-Only Exporter v0](audit-decision-record-readonly-exporter-v0.md)

That follow-through does not change what PR65 was: a docs-only gate. PR66 is
the narrow read-only implementation slice that PR65 recommended.

## Evidence Considered

PR65 considers the landed PR57 through PR64 accountability sequence:

| PR | Evidence | Read |
|---|---|---|
| PR57 | [Lolla Doctor Read-Only CLI](lolla-doctor-readonly-cli-v0.md) | Read-only local preflight can ship safely when custody flags, zero model calls, and archive-mutation boundaries are explicit. |
| PR58 | [Audit Decision Record v0](../conversation-understanding/audit-decision-record-v0.md) | Decision records directly answer what decision changed and map to PR31 actionable-delta labels. |
| PR59 | [Audit Decision Record Fixtures v0](audit-decision-record-fixtures-v0.md) and [review.json](../../reviews/human/audit-decision-record-fixture-review-v0/review.json) | Six paraphrase-only fixtures passed; PR31 mapping was useful in all six; false-certainty risk was none or low. |
| PR60 | [Provenance Map v0](../conversation-understanding/provenance-map-v0.md) | Provenance is useful as lineage, but it should stay lineage-only and avoid compliance, graph DB, memory, or answer-quality claims. |
| PR61 | [Review Conflict Register v0](review-conflict-register-v0.md) | Conflict register is useful for preserving unresolved tensions but must remain human-review-owned and avoid conflict resolution or severity automation. |
| PR62 | [Case Graph Export Design v0](../conversation-understanding/case-graph-export-v0.md) | Case graph can orient review but carries higher graph/memory/GraphRAG/source-of-truth drift risk. |
| PR63 | [Accountability View Fixtures v0](accountability-view-fixtures-v0.md) | Three combined fixture bundles showed all four views together using safe paraphrases, relative artifact refs, and placeholder hashes. |
| PR64 | [Accountability View Fixture Review v0](accountability-view-fixture-review-v0.md) and [review.json](../../reviews/human/accountability-view-fixture-review-v0/review.json) | All three bundles passed; only `audit_decision_record` was ready for a later exporter-design decision on all three fixtures. |

## Why Outcome A

`lolla.audit_decision_record.v0` is the safest next implementation candidate
because it answers the most central review question:

```text
What did Lolla change about the decision?
```

The decision-record lane has the strongest evidence:

- PR59 reviewed six standalone decision-record fixtures and marked all six pass.
- PR59 found PR31 mapping useful in all six.
- PR59 found reviewer use without raw content possible in all six.
- PR64 reviewed three combined accountability-view bundles and marked
  `audit_decision_record` high value in all three.
- PR64 marked `audit_decision_record` ready for exporter design in all three.
- PR64 kept false-certainty risk low on all three bundles.

It is also the least drift-prone accountability primitive:

- it does not require graph logic;
- it does not imply memory;
- it maps directly to the human-owned PR31 actionable-delta rubric;
- it can stay pointer-only or paraphrase-only;
- it makes clean-artifact-is-not-good-advice caveats visible;
- it can remain read-only, local, deterministic, and model-call-free.

## Rejected Or Deferred Alternatives

Outcome B, implement `provenance_map` exporter next:

Deferred. Provenance is useful as artifact-lineage context, but PR64 marked it
medium value and needing more fixtures on all three bundles. It should not be
implemented until custody details are narrower and the output cannot be mistaken
for advice quality, compliance provenance, RDF/PROV-O/W3C compliance, graph DB,
or memory.

Outcome C, implement `review_conflict_register` helper/exporter next:

Deferred. The conflict register had high review value in PR64, but every row
still marked it as needing more fixtures before helper/exporter design. Its
wording discipline is delicate: it must preserve unresolved tensions without
resolving conflicts, scoring severity, enforcing policy, creating labels, or
claiming domain authority.

Outcome D, implement `case_graph` exporter next:

Rejected for now. PR64 put case graph on hold for all three fixtures. It can
orient review, but it has the highest risk of decorative structure, memory
vibes, graph DB drift, GraphRAG drift, entity-resolution drift, and false
source-of-truth posture.

Outcome E, do more fixtures/review before any implementation:

Rejected for `audit_decision_record`; accepted for the other views. PR59 and
PR64 together provide enough evidence for a narrow read-only decision-record
exporter design prototype. Provenance map, review conflict register, and case
graph should still wait.

Outcome F, stop the accountability-view lane for now:

Rejected. The audit decision record has repeated value across standalone
fixtures and combined bundles, and it answers a concrete review need without
requiring platform scope.

## Future PR66 Boundary

Maintainers later approved PR66 as:

```text
PR66 Audit Decision Record Read-Only Exporter v0
```

Boundary for that slice:

- read existing local archive artifacts only;
- prefer explicit external output by default;
- do not write into archives unless a later separate PR approves archive
  integration;
- emit `lolla.audit_decision_record.v0`;
- remain deterministic and model-call-free;
- do not run `$lolla`;
- do not mutate archives;
- do not change prompts;
- do not change `SKILL.md`;
- do not change provider-boundary policy;
- do not relax `caller_action`;
- do not create human-review labels;
- do not score answer quality;
- do not implement an LLM judge;
- do not create high-stakes evidence;
- do not add graph DB, embeddings, chunking, memory, GraphRAG, entity
  resolution, or policy enforcement;
- do not copy raw transcript, raw memo, raw revised-answer text, provider/model
  text, or private reasoning into checked-in examples or default output;
- treat every populated semantic field as a review projection, not truth,
  approval, or autonomous reliance.

PR66 follows this boundary by adding a local exporter that emits
`lolla.audit_decision_record.v0` to an explicit external output path, refuses
output inside the run directory, keeps `model_calls: 0` and
`archive_mutated: false`, and does not read raw transcript, memo,
revised-answer, provider/model, or private reasoning content.

## Non-Goals

PR65 does not add or approve:

- PR66 implementation;
- any exporter code;
- tests;
- schemas under `engine/`;
- CLI support;
- runtime integration;
- archive reading behavior;
- archive mutation;
- `$lolla` runs;
- model calls;
- prompt changes;
- `SKILL.md` changes;
- provider-boundary policy changes;
- `caller_action` changes;
- high-stakes runs;
- high-stakes archive evidence;
- answer-quality scoring;
- LLM judges;
- automatic human-review labels;
- automatic `safe_for_agent_use`;
- graph DB;
- embeddings;
- chunking;
- memory;
- GraphRAG;
- entity resolution;
- conflict resolution;
- severity automation;
- policy enforcement;
- Semantica-style platform work.

## Stop Conditions

Stop after PR65.

At PR65 time, the stop condition was: do not start PR66 in that sequence.
Maintainers later approved PR66 as a separate slice, now documented in
[Audit Decision Record Read-Only Exporter v0](audit-decision-record-readonly-exporter-v0.md).

PR67 has now landed separately as a smoke review of PR66 exporter output:
[Audit Decision Record Export Smoke Review v0](audit-decision-record-export-smoke-review-v0.md).

The current stop condition after PR67 is: do not start PR68 automatically.
Before any future implementation slice begins, maintainers should review PR67
and confirm that the next work remains read-only where appropriate, local,
deterministic, model-call-free, archive-safe, raw-content-safe, and outside
labels, scoring, judges, graph DB, memory, archive integration, automatic
generation, and runtime integration unless explicitly approved.

Current anti-drift sentence:

```text
doctor != runtime approval
decision record != truth
provenance map != advice quality
conflict register != conflict resolution
case graph != memory
fixtures != real runtime feature
design JSON != shipped artifact
```
