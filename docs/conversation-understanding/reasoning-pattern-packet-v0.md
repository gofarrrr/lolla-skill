# Reasoning Pattern Packet v0

Status: design-only output of Core Semantic Validation Case 01  
Runtime status: not integrated  
Graph status: unchanged

Governing architecture:
`docs/conversation-understanding/hybrid-reasoning-boundary-v0.md`. In
particular, deterministic graph selection is candidate recall under declared
rules, not semantic applicability judgment.

## Purpose

The reasoning-pattern packet creates the boundary between conversation
understanding and deterministic graph selection.

The full conversation and source-linked semantic interpretation remain outside
the graph. A probabilistic interpreter may propose reasoning mechanisms, but
the graph receives only a validated routing projection containing controlled
mechanism identifiers and structural relations.

This is controlled decontextualization:

```text
verbatim conversation
  -> source-linked semantic events
  -> provisional reasoning-pattern hypotheses
  -> fact-leak validation
  -> sealed graph routing projection
  -> deterministic model/relationship selection
  -> facts reattached when pressure is applied
```

## Two surfaces, one artifact

The persisted artifact has two deliberately different surfaces.

### 1. Provenance surface

This surface allows a reviewer to trace each pattern hypothesis back to
source-linked semantic item IDs. It may contain case and artifact references,
but it must not contain raw conversation text or quotes.

The graph must not receive this surface.

### 2. Routing projection

This is the only surface eligible for graph input. It contains:

- local pattern IDs such as `rp_001`;
- controlled mechanism IDs;
- whether the mechanism is present, a missing protection, or a tension;
- whether it belongs to user, assistant, or joint-process reasoning;
- structural relationships between pattern nodes.

It does not contain:

- people, companies, products, or organizations;
- raw quotes or paraphrased case narrative;
- dates, deadlines, monetary amounts, percentages, or case quantities;
- desired outcomes or recommendations;
- topic labels such as SaaS, healthcare, hiring, or investment;
- embeddings of the source conversation;
- mental-model names selected because of factual topic overlap.

## Initial controlled mechanism vocabulary

The v0 vocabulary is deliberately small and derived from recurrent reasoning
mechanisms, not from the topic of Case 01:

- `status_signal_used_as_evidence`
- `ambiguous_signal_treated_as_commitment`
- `acknowledged_constraint_not_gated`
- `criteria_defined_after_commitment`
- `initial_frame_persists_after_question_change`
- `counterpressure_acknowledged_not_integrated`
- `reversible_path_not_considered`
- `upside_downside_evidence_asymmetry`
- `missing_reversal_condition`
- `other_review_required`

`other_review_required` is never routing-eligible. It preserves an unsupported
or novel hypothesis for human review without allowing free text into the graph.

## Structural relations

The initial relation vocabulary is:

- `precedes`
- `persists_after`
- `reinforces`
- `counterpressure_to`
- `missing_protection_for`

These relations describe reasoning structure. They are not mental-model graph
edges. The deterministic graph may later map validated mechanisms and
relations to its own curated model nodes.

## Pattern acceptance gate

A pattern may enter `routing_projection.pattern_nodes` only when:

1. its mechanism ID is in the controlled vocabulary;
2. it has at least one source semantic item on the provenance surface;
3. all referenced semantic items are source-grounded or explicitly marked as
   provisional derived relationships;
4. the projection contains no free-text case fields;
5. fact-leak lint has passed;
6. `routing_eligible` is true.

Patterns that fail any condition remain in `pattern_hypotheses` for review and
do not enter the routing projection.

## Missingness semantics

Absence must not be manufactured from a single model omission.

For example, `missing_reversal_condition` can be proposed only after the
semantic layer has exhaustively inspected source-linked condition events and
recorded the bounded scope in which no reversal rule was observed. It means
“not observed in the captured conversation,” not “does not exist in reality.”

## Determinism boundary

The end-to-end system remains hybrid:

- interpreting semantic events and proposing patterns is probabilistic;
- validating schema, source references, vocabulary, and fact leakage is
  deterministic;
- building the sealed routing projection is deterministic after validation;
- graph traversal and candidate selection can then be deterministic under a
  declared graph/version/configuration;
- applying selected pressure to the factual case is probabilistic again.

The product must not describe this as deterministic end to end.

## Non-claims

The packet does not prove:

- that a proposed reasoning pattern is correct;
- that the graph will select the best mental model;
- that a missing protection was absent outside the captured conversation;
- that the later advice is correct or safe;
- that source-grounded interpretation is human-validated.

## Downstream consumer boundary

The Case 07 counterfactual tested a tempting shortcut: attach every selected
semantic event to the full conversation and give the whole inventory to the
fresh reasoning consumer.

That shortcut is now blocked.

The actual 27-event SK3 overlay was directionally worse than a transcript-only
strong reconsideration control. It preserved the fact that Seattle was
undecided, but it also carried the prior assistant's “Seattle is the root
decision” stance and failed to explicitly challenge that frame. Adding the one
source-reviewed user self-correction repaired the frame challenge but only
reached rough parity with the transcript-only control.

Source-valid context can therefore still distort attention. The semantic
inventory has value for audit, navigation, and receipt construction, but it is
not itself the reconsideration prompt.

The downstream shape remains:

```text
full conversation remains authoritative
  + source-grounded reasoning-pattern hypotheses
  -> fact-free deterministic graph recall
  -> graph-returned candidate lenses
  -> probabilistic active-pressure composition
  + compact protected edge/weak/parked portfolio receipts
  -> fresh reconsideration with full conversation
```

The case-local pressure composer must:

- see the authoritative full conversation;
- treat graph candidates and semantic events as hypotheses, not commands;
- select a small active set for detailed pressure;
- preserve off-frame candidates compactly in edge, weak, or parked layers when
  they do not earn active detail;
- preserve the strongest valid original advice and user-owned values;
- reject or keep pressure private when it adds no marginal decision value;
- keep exact source handles and the set-aside ledger outside public prose;
- avoid passing the full semantic event inventory merely because it is
  available.

This selection remains an LLM or human semantic job. Deterministic code may
validate exact evidence, controlled mechanism IDs, graph traversal, packet
caps, hashes, and custody. It must not decide relevance with keywords,
reader-family priority, event counts, or a multi-layer gating system.

The downstream consumer contract is now specified in
`docs/conversation-understanding/reasoning-pressure-handoff-v0.md`. Its
dependency-free shadow validator is deliberately narrower than the semantic
work: it can reject bad references, hashes, caps, flags, and shape, but it
cannot certify that a pressure is relevant or useful.

That contract represents only the active working-set slice. The governing
portfolio doctrine remains “broad availability, compact representation,
delayed rejection,” implemented historically by the research-only
`reasoning_affordance.v1` and `step6_attention_map.v1` contracts. A low-fit
candidate may be demoted in attention weight; it must not be silently erased
before the final reasoner can inspect or recover it.

## Next implementation gate

Before any graph integration:

1. run the semantic kernel on the full core corpus;
2. create same-reasoning/different-facts and same-facts/different-reasoning
   pairs;
3. implement a deterministic fact-leak linter;
4. compare routing projections across those pairs;
5. keep the existing live graph input unchanged until the shadow projection
   passes invariance and sensitivity review.
6. compare the final pressure handoff against a transcript-only strong fresh
   reconsideration control;
7. show both a non-obvious unique positive delta and a quiet stand-down without
   public bloat;
8. do not promote a full semantic overlay even if its source validity is
   perfect.
9. compose the lineage-backed active slice with edge, weak, parked, and
   expansion-ref portfolio layers;
10. require exact human review of that complete shadow portfolio before any new
    downstream call;
11. keep live graph, Step 6, and skill integration blocked until the portfolio
    later demonstrates novel exposure without false stand-down, forced
    absorption, or public bloat.
