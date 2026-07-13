# Joint-Process Reasoning Target v0

Status: research-only; runtime dormant  
Date: 2026-07-10

## Target

The routing question is:

> After reading the complete conversation, which abstract reasoning weakness
> remains unresolved in the joint reasoning trajectory?

It is not:

- Which weakness did the user display at any moment?
- Which mistake did the assistant make before later repairing it?
- Which mental-model label can plausibly describe one isolated turn?

The raw conversation and actor-specific observations remain part of the audit.
They do not automatically become graph seeds.

## Why this replaces the Batch 3 target

Batch 3 allowed `user`, `assistant`, and `joint_process` scopes inside the same
routing projection. On the improved fixture, the interpreter still diagnosed
the user's initial framing even though the assistant later supplied the missing
evidence and constraint gates. On fact-swapped copies of the same reasoning,
it also chose different plausible labels.

That result exposed a consumer mismatch. The graph does not need a catalog of
every locally present pattern; the reconsideration consumer needs weaknesses
that survived the conversation and may still deserve pressure.

The Batch 3 result remains frozen. This target is tested only on new fixtures.

## Required semantic review

The LLM reviews every controlled mechanism exactly once and assigns one joint
status:

| status | meaning | routing effect |
| --- | --- | --- |
| `unresolved` | The weakness remains operative after the complete exchange | active deterministic seed routing |
| `resolved_in_conversation` | It appeared but was materially repaired later | audit only; no seed |
| `ambiguous` | Evidence supports competing readings | compact edge reserve; no active seed |
| `not_observed` | The complete exchange does not support the mechanism | audit only; no seed |

`resolved_in_conversation` does not erase history. Source and resolution turns
remain in the audit packet. `ambiguous` does not become a false stand-down; it
remains inspectable outside the active seed set.

`other_review_required` is the ontology escape hatch. When unresolved or
ambiguous, it enters a manual-review reserve and never receives an automatic
graph seed.

## Division of labor

The LLM or human decides:

- whether a mechanism appeared;
- whether later reasoning repaired it;
- whether it remains unresolved or ambiguous;
- which turns support that interpretation.

Deterministic code:

- requires exactly one row per controlled mechanism;
- validates allowed statuses and source-turn references;
- requires resolution evidence for `resolved_in_conversation`;
- seals a fact-free routing projection;
- routes only rows declared `unresolved`;
- retains ambiguous and resolved rows in the audit packet;
- never changes a semantic status to make results stable.

## Non-claims

Passing a fixture pair would show that this abstraction behaved as specified
on that pair. It would not prove open-domain stability, model applicability,
graph value, reasoning quality, or readiness for live integration.
