# Conversation-event architecture A–E handoff

Status: terminal; material redesign required  
Date: 2026-07-11

## Goal completed

The A–E program tested whether small-window semantic harvesting plus fresh
cross-turn synthesis could produce Lolla's source-linked conversation-state
handoff without deterministic semantic gating.

- Phase A passed provider-free representation and custody.
- Phase B established operationally reliable, high-recall harvesting but exposed
  overlapping candidate growth and narrowly failed the frozen transfer gate.
- Phase C failed after its one generic repair.
- Phase D recorded the end-to-end hard stop.
- Phase E was not executed because D did not pass.

The terminal evidence is
`research/conversation-event-a-e-conclusion-2026-07-11/decision.json`.

## Current boundary

Keep:

- turn-pair source windows;
- stable span IDs and deterministic exact-text retrieval;
- typed contracts generated from one source of truth;
- complementary probabilistic lenses;
- complete candidate and failure custody;
- fresh-context global interpretation;
- fail-closed compilation;
- zero direct factual graph routing.

Do not keep as the next architecture:

- a global synthesizer over 88–95 overlapping raw events;
- global reclassification of claim strength without local attribution context;
- exclusive family routing;
- another prompt-only repair of the closed Phase C design;
- silent schema widening, response healing, retries, or deterministic relevance
  filters.

## Closest next goal

Provider-free first:

1. specify a bounded normalized turn record;
2. compare two semantic designs—one consolidated per-window reader versus three
   lenses plus a per-window probabilistic consolidator;
3. preserve every input candidate and consolidation disposition;
4. classify claim strength locally and make global relabeling explicit or
   forbidden;
5. freeze an event/token budget for global fan-in;
6. replay all five reviewed cases through the representation and compiler;
7. only then authorize a one-case provider probe and prospective transfer.

This is a new material-design goal, not unfinished prompt tuning in the closed
A–E program.
