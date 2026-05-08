# PR55 Per-Affordance Traceability Review

Date: 2026-05-08

Branch: `feature/knowledge-substrate-pr55-v18-pickup-quality-audit`

Status: review-only audit artifact

Scope: dormant reasoning substrate packet shape, review renderer, and future decoder/receiver needs.

## Verdict

The current dormant packet shape supports card-level inspection. It does not reliably support affordance-level transactions.

That distinction matters.

Card-level review asks:

> Is this model a plausible nominated shelf, and what reviewed material exists for it?

Affordance-level transaction asks:

> Which exact affordance did the receiver use, reject, defer, merge, or block, and why?

The current flattened shape can help a human reviewer. It is too lossy for a future decoder ledger.

## What Current Shape Preserves

The current packet preserves useful model-level context:

- `model_id`;
- lane nomination reason;
- graph neighbors;
- source custody fields;
- aggregate coverage status;
- reviewed affordance snippets;
- absence records;
- source references;
- blocked surfaces;
- do-not-overclaim notes.

This is enough for static inspection and dormant stress review.

## Where Traceability Breaks

| Surface | Current behavior | Runtime consequence |
| --- | --- | --- |
| `affordance_ids` | IDs are exposed as a pooled list, capped per model. | Receiver can see names but not reliably bind each ID to its activation, evidence, guard, and treatment fields. |
| `use_when` | Flattened across reviewed affordances. | A use condition can become detached from the affordance it belongs to. |
| `do_not_use_when` | Flattened across reviewed affordances. | A rejection reason may not clearly block the correct affordance. |
| `case_evidence_needed` | Flattened across reviewed affordances. | Evidence gates can blur together, especially on multi-affordance cards. |
| `treatment_requirements` | Flattened rows do not preserve `affordance_id` in the review-facing structure. | A receiver cannot cleanly audit whether it honored the treatment requirement for a specific affordance. |
| `diagnostic_questions` | Flattened. | Questions can become generic prompts rather than scoped tests. |
| `misuse_guards` | Flattened. | Misuse warnings may appear model-level even when they belong to one affordance. |
| `source_evidence` | Includes `affordance_id`, but is pooled and capped. | Better than other fields, but still not enough for grouped transaction identity. |
| `confidence` | Aggregated. | Medium or weak confidence can be hidden when the model has mixed support. |
| `absence_records` | Model-level records, displayed sparingly. | Absence can block a whole card, but the receiver lacks a clear rule for which affordance is blocked. |
| Review renderer | Displays one detail item per field. | Useful for compact inspection, but hides decisive second or third details. |

## Why This Is A Runtime Blocker

A future decoder ledger needs stable action grammar:

- `used`;
- `rejected`;
- `deferred`;
- `merged`;
- `blocked_by_absence`;
- `weak_support_not_promoted`.

That grammar should attach to an affordance identity, not just a model identity.

Without grouped structure, a receiver can still write a convincing explanation, but the audit trail will be mushy. It may say "used systems thinking" while silently blending boundary selection, feedback loops, leverage points, and structure-over-events.

That is exactly the kind of cognition theater this project is trying to avoid.

## Required Future Shape

A future packet should preserve a grouped structure like:

```json
{
  "model_id": "chain-of-thought",
  "reviewed_affordance_cards": [
    {
      "affordance_id": "chain-of-thought.audit-stepwise-reasoning",
      "label": "audit stepwise reasoning",
      "use_when": ["..."],
      "do_not_use_when": ["..."],
      "case_evidence_needed": ["..."],
      "treatment_requirements": ["..."],
      "diagnostic_questions": ["..."],
      "misuse_guards": ["..."],
      "source_refs": ["..."],
      "confidence": "high",
      "record_status": "supported",
      "related_absence_ids": ["..."]
    }
  ]
}
```

The key is not this exact JSON. The key is that the receiver sees an affordance as a complete unit.

## Decoder Ledger Implication

If the system wants a decoder later, the ledger should be able to record:

```json
{
  "model_id": "chain-of-thought",
  "affordance_id": "chain-of-thought.audit-stepwise-reasoning",
  "receiver_action": "deferred",
  "reason": "case lacks externally checkable intermediate claims",
  "blocking_absence_ids": ["chain-of-thought.trace-as-proof"],
  "source_refs_considered": ["..."],
  "confidence_treatment": "high confidence card, but evidence gate unmet"
}
```

That is not possible cleanly if affordance fields are pooled.

## What Should Not Happen

Do not make Python decide semantic importance.

The packet layer may:

- preserve IDs;
- preserve provenance;
- preserve source fields;
- cap display size;
- label weak support;
- expose absences;
- keep grouped structure.

The packet layer should not:

- infer new affordances;
- choose final reasoning moves;
- promote broad cards because they sound strategic;
- automatically pick the latest artifact;
- rewrite the LLM's answer.

## Review-Only Acceptance Criteria

For PR55, success means documenting this blocker clearly. It does not require implementing the grouped packet.

A later implementation PR should require:

- grouped affordance cards in packet internals;
- a renderer that can show one compact affordance unit without flattening;
- explicit confidence and weak-support display;
- absence records that can be linked as blockers;
- a decoder ledger schema that records use/reject/defer/merge decisions;
- no live pickup until static replay shows the receiver can honor the grammar.

## Bottom Line

The current packet shape is good enough to inspect whether v18 exists and looks plausible.

It is not good enough to know what happened under the hood when a receiver uses, rejects, or defers an affordance.
