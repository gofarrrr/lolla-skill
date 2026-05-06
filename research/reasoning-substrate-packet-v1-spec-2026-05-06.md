# Reasoning Substrate Packet v1 Spec

**Date:** 2026-05-06
**Status:** Dormant research/spec artifact. This is not runtime behavior, not
live `/lolla`, not a prompt change, not a lane rewrite, not a Decision Pressure
producer, and not a user-facing surface.

**Decision label:** `reasoning_substrate_packet_v1_spec_ready`

**Doctrine anchor:** `pull_shelves_enrich_cards_let_llm_reason`

## Purpose

`reasoning_substrate_packet.v1` is the proposed deterministic object for the
next phase of knowledge use.

The packet does not decide the final pressure. It does not contain final memo
copy. It does not tell users what to do.

It packages candidate mental-model shelves for a later LLM or reviewer:

- what was pulled;
- why it was pulled;
- what runtime graph material exists;
- what reviewed v4 affordance material exists;
- what is graph-only or missing;
- what should not be overclaimed.

The intended handoff is:

> Existing lanes pull shelves. Deterministic code enriches cards. The LLM
> reasons.

## What This Is Not

This spec does not authorize:

- runtime integration;
- `/lolla` behavior;
- Observatory rendering;
- memo, Step 8, Step 6, or Lane 4 promotion;
- prompt changes;
- generation changes;
- new affordance extraction;
- broad Batch 3 or Batch 3b;
- user-facing Decision Pressure output;
- deterministic pressure selection;
- deterministic ranking of wisdom, novelty, usefulness, tone, or actionability.

The packet is a silver platter, not the meal.

## Top-Level Shape

```json
{
  "packet_version": "reasoning_substrate_packet.v1",
  "packet_id": "example-review-only-id",
  "status": "draft_review_only",
  "runtime_policy": "runtime_dormant",
  "source_artifacts": [],
  "transaction_context": {},
  "candidate_cards": [],
  "suppressed_candidates": [],
  "coverage_summary": {},
  "packet_policy": {},
  "blocked_surfaces": [],
  "review_notes": []
}
```

### Required Top-Level Fields

| Field | Required value / role |
| --- | --- |
| `packet_version` | `reasoning_substrate_packet.v1` |
| `packet_id` | Stable review identifier for the hand-authored or generated packet |
| `status` | Must remain `draft_review_only` in this phase |
| `runtime_policy` | Must remain `runtime_dormant` in this phase |
| `source_artifacts` | Files or artifacts used to assemble the packet |
| `transaction_context` | Compact summary of the user/assistant transaction |
| `candidate_cards` | Enriched model cards offered to the next LLM |
| `suppressed_candidates` | Candidates removed by caps, duplication, weakness, or coverage honesty |
| `coverage_summary` | Aggregate view of reviewed, graph-only, missing, and absence-only coverage |
| `packet_policy` | Caps, provenance rules, and forbidden deterministic behaviors |
| `blocked_surfaces` | Product/runtime surfaces still blocked |
| `review_notes` | Human-readable review caveats |

## Transaction Context

`transaction_context` should remain compact. It is not a transcript dump.

Suggested fields:

```json
{
  "case_id": "archived-case-or-review-id",
  "user_situation_summary": "One to three sentences.",
  "assistant_advice_summary": "One to three sentences.",
  "known_action_or_commitment": "What the user may do next, if known.",
  "capture_health": "complete | partial | thin",
  "transaction_sources": ["user_turn", "assistant_turn"]
}
```

The transaction context exists so the LLM can reason over the situation. It is
not evidence that Python understood the case semantically.

## Candidate Card Shape

Each candidate card should represent one model or tendency-adjacent model shelf.

```json
{
  "card_id": "card-opportunity-cost-001",
  "model_id": "opportunity-cost",
  "display_name": "Opportunity Cost",
  "pulled_by": [],
  "why_pulled": [],
  "coverage_status": "v4_reviewed_affordance_available",
  "runtime_graph_fields": {},
  "reviewed_affordance_fields": {},
  "absence_records": [],
  "do_not_overclaim": [],
  "llm_instruction": "Consider, merge, set aside, or ignore. Do not force use."
}
```

### Candidate Identity

| Field | Role |
| --- | --- |
| `card_id` | Packet-local ID |
| `model_id` | Runtime graph model ID |
| `display_name` | Human-readable model name from the runtime graph |

`model_id` must resolve against `data/knowledge_graph.json`.

### Pulled By

`pulled_by` records which existing system path nominated the shelf. It must not
pretend to be final pressure selection.

Allowed values:

- `lane1_tendency_route`
- `lane1_neighbor`
- `lane2_detected_model`
- `lane2_companion_chunk`
- `lane3_frame_route`
- `lane4_gap_route`
- `reviewer_note`

Future code may add exact route IDs or evidence IDs, but this spec does not
require a live producer.

### Why Pulled

`why_pulled` preserves route evidence for the next LLM.

Suggested item shape:

```json
{
  "source": "lane1_tendency_route",
  "reason": "Scarce resource commitment without a named displaced alternative.",
  "evidence_source_type": "assistant_turn",
  "evidence_quote": "Short exact quote or null when only route metadata exists.",
  "route_or_artifact_id": "optional"
}
```

Allowed `evidence_source_type` values:

- `user_turn`
- `assistant_turn`
- `lane_gap`
- `graph_recall`
- `embedding_recall`
- `reviewer_note`
- `source_artifact`

Recall can be broad. Attribution must stay narrow.

## Coverage Status

Allowed `coverage_status` values:

- `v4_reviewed_affordance_available`
- `graph_only_runtime_card`
- `absence_only`
- `missing_reviewed_record`
- `source_too_thin`
- `conflicting_or_weak_support`

Meaning:

| Status | Meaning |
| --- | --- |
| `v4_reviewed_affordance_available` | The model has reviewed v4 affordance material with source custody. |
| `graph_only_runtime_card` | The model exists in the 222-model runtime graph but lacks reviewed v4 depth. |
| `absence_only` | Reviewed material exists mainly to say useful affordance support is absent. |
| `missing_reviewed_record` | The runtime graph model has no reviewed v4 record yet. |
| `source_too_thin` | Available source does not support strong operational use. |
| `conflicting_or_weak_support` | Material is relevant but weak, conflicting, or unsafe to overclaim. |

Graph-only is allowed. It is not second-class for recall. It is second-class for
source-backed claims.

## Runtime Graph Fields

Every card may carry selected runtime graph fields:

```json
{
  "source_file": "Canonical_Source_File_rag.md",
  "reasoning_types": ["diagnostic"],
  "select_when": [],
  "danger_when": [],
  "failure_modes": [],
  "premortem_questions": [],
  "heuristics": []
}
```

Caps:

- include at most 1-3 high-value items per field;
- prefer items connected to the route evidence;
- preserve enough material for LLM reasoning;
- do not dump all graph text.

Runtime graph fields give breadth. They are not reviewed v4 source custody.

## Reviewed Affordance Fields

When v4 exists, cards may include reviewed affordance snippets:

```json
{
  "affordance_ids": [],
  "use_when": [],
  "do_not_use_when": [],
  "case_evidence_needed": [],
  "treatment_requirements": [],
  "diagnostic_questions": [],
  "misuse_guards": [],
  "source_evidence": [],
  "confidence": "high"
}
```

Caps:

- use 1-3 high-value snippets per card;
- prefer snippets that change what the LLM should verify, dismiss, stop,
  monitor, or avoid;
- include exact source evidence only when source custody exists;
- keep medium-confidence cautions visible when relevant.

v4 gives depth. It should not swallow breadth.

## Absence Records

`absence_records` should preserve honest blanks.

Suggested item shape:

```json
{
  "model_id": "example-model",
  "attempted_field": "case_evidence_needed",
  "status": "not_supported_by_source",
  "reason": "Source did not support a usable operational constraint."
}
```

Absence records are not failure noise. They tell the next LLM where not to fake
confidence.

## Suppressed Candidates

`suppressed_candidates` records what did not fit the packet or should not be
treated as a strong candidate.

Suggested fields:

- `candidate_id`
- `model_id`
- `suppression_reason`
- `coverage_status`
- `pulled_by`
- `do_not_recover_as_pressure_without_review`

Suppression reasons may include:

- duplicate shelf;
- weaker route evidence;
- packet cap;
- graph-only when reviewed support is required;
- absence-only;
- source too thin;
- likely bloat;
- semantic selection deferred to LLM/reviewer.

Suppressed candidates are audit material, not extra user-facing pressures.

## Coverage Summary

`coverage_summary` should make breadth/depth honest:

```json
{
  "candidate_card_count": 0,
  "v4_reviewed_card_count": 0,
  "graph_only_card_count": 0,
  "absence_only_card_count": 0,
  "missing_reviewed_record_count": 0,
  "source_too_thin_count": 0,
  "missing_reviewed_model_ids": [],
  "high_value_graph_only_model_ids": []
}
```

The summary should help reviewers see whether the packet is grounded,
lopsided, or pretending coverage exists.

## Packet Policy

`packet_policy` should encode the guardrails:

```json
{
  "candidate_card_target_min": 5,
  "candidate_card_target_max": 12,
  "snippet_target_min_per_card": 1,
  "snippet_target_max_per_card": 3,
  "deterministic_role": "validate_package_cap_reference_and_label",
  "semantic_selection_role": "llm_or_reviewer",
  "forbid_user_facing_prose": true,
  "forbid_final_pressure_selection": true,
  "forbid_case_type_templates": true
}
```

Normal target:

- 5-12 candidate cards total;
- 1-3 high-value snippets per card;
- explicit coverage status per card;
- no final pressure selection;
- no user-facing prose.

## Blocked Surfaces

`blocked_surfaces` must remain explicit while this object is dormant:

- live Observatory rendering;
- memo integration;
- Step 8 integration;
- Step 6 integration;
- Lane 4 integration;
- `/lolla` runtime use;
- user-facing Decision Pressure block;
- prompt changes;
- generation changes;
- new extraction;
- Batch 3b;
- paid Gate 4 reruns by default.

## Deterministic Boundaries

Deterministic code may:

- collect lane-nominated candidates;
- validate model IDs and affordance IDs;
- dedupe exact or ID-level duplicates;
- cap packet size;
- attach runtime graph snippets;
- attach reviewed v4 snippets when IDs resolve;
- label graph-only and missing-reviewed coverage;
- preserve absence records;
- produce review-only counts, IDs, and drift reports.

Deterministic code must not:

- choose final pressure quality;
- infer pressure from case type, route label, keyword, or gap label;
- rank novelty, usefulness, tone, wisdom, or actionability;
- merge semantic equivalents as a final product decision;
- smooth missing coverage into generic model-name reasoning;
- generate user-facing pressure prose;
- imitate PR23 examples as templates.

## Non-Normative Card Fragments

These fragments illustrate the distinction between reviewed depth and graph
breadth. They are not a fixture, not a producer contract, and not examples to
imitate.

### v4-Reviewed Card Fragment

```json
{
  "model_id": "opportunity-cost",
  "coverage_status": "v4_reviewed_affordance_available",
  "pulled_by": ["lane4_gap_route", "reviewer_note"],
  "why_pulled": [
    {
      "reason": "The advice commits scarce time or attention without naming the displaced alternative.",
      "evidence_source_type": "assistant_turn"
    }
  ],
  "reviewed_affordance_fields": {
    "affordance_ids": ["opportunity-cost.displaced-alternative-commitment-gate"],
    "case_evidence_needed": [
      "Name the best real alternative using the same scarce resource."
    ],
    "misuse_guards": [
      "Do not inflate imagined alternatives into real opportunity costs."
    ]
  },
  "llm_instruction": "Consider whether this changes verification before action; set aside if the alternative is not real."
}
```

### Graph-Only Card Fragment

```json
{
  "model_id": "chain-of-verification",
  "coverage_status": "graph_only_runtime_card",
  "pulled_by": ["lane2_companion_chunk", "reviewer_note"],
  "runtime_graph_fields": {
    "select_when": [
      "A conclusion depends on a chain where one weak link could collapse the advice."
    ],
    "danger_when": [
      "Verification becomes theater or delays action without changing the decision."
    ]
  },
  "do_not_overclaim": [
    "No reviewed v4 affordance record is available in the current corpus."
  ],
  "llm_instruction": "Use as broad graph context only; do not claim source-backed v4 treatment requirements."
}
```

## Future Validation Ideas

If a later slice is explicitly approved, mechanical validation could check:

- `runtime_policy` remains `runtime_dormant`;
- packet has 5-12 cards unless reviewer override is present;
- every `model_id` resolves in `data/knowledge_graph.json`;
- v4 affordance IDs resolve when used;
- graph-only cards do not include reviewed v4 fields;
- reviewed cards preserve source evidence and confidence;
- missing reviewed coverage is explicit;
- no final pressure or user-facing copy fields are present.

This spec does not add that validator.

## Decision

`reasoning_substrate_packet.v1` is ready as a dormant planning/spec object.

It preserves the current architecture:

> 222 gives breadth. v4 gives depth. Existing lanes pull shelves. Deterministic
> code enriches cards. The LLM reasons. Python does not decide wisdom.
