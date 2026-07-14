# Conversation turn-record redesign

Status: terminal; both architectures rejected after one generic repair  
Date: 2026-07-11

## Terminal question

Can Lolla reduce overlapping local observations into a bounded, source-linked
sequence of turn records without giving deterministic code semantic authority,
and can global synthesis then recover position, thread, and constraint state
reliably?

## Architectures compared

### A — one reader per turn pair

One probabilistic reader receives one user/assistant turn pair and returns one
normalized record containing:

- at most two directional moves;
- at most two substantive thread signals;
- at most four atomic claims with locally classified source strength.

The task is wider than a single lens but its context and output are tightly
bounded. It never assigns global ownership, acceptance, introduction, or thread
disposition.

### B — three lenses plus local consolidation

The existing contribution, thread, and claim harvesters run on one turn pair. A
fresh local probabilistic consolidator receives all of that window's candidates
and produces the same normalized turn record. Every input candidate receives a
semantic disposition: preserved, merged into a normalized item, set aside as
locally redundant, or unclear. Deterministic code records and validates those
decisions but never makes them.

## Common normalized record

- stable record and item IDs;
- source span IDs only from the current window;
- exact source text attached deterministically;
- local claim mode fixed at this boundary;
- explicit `supported`, `unclear`, or `not_found` status;
- no global semantic labels;
- no direct graph eligibility.

## Frozen fan-in budget

Per seven-turn-pair conversation:

- maximum normalized items: 56;
- target normalized items: at most 42;
- maximum repeated source selections: 2 per normalized item;
- maximum serialized global synthesis input: 32,000 UTF-8 bytes per family;
- maximum schema depth: 7;
- zero unresolved source IDs;
- zero items without terminal custody.

The budget is a representation gate, not a deterministic relevance rule. A
probabilistic reader or consolidator decides semantic compression; code only
checks the frozen envelope.

## Provider-free success gates

Across all five reviewed cases, both architectures are replayed independently.
An architecture may proceed to calls only if it has:

- 100% reviewed position-contribution source survival;
- 100% reviewed focal-thread introduction/latest survival and at least one
  material response when reviewed;
- 100% reviewed atomic-constraint source survival;
- zero claim-mode changes from the reviewed local source classification;
- zero source, window, ownership-custody, handoff, or graph-boundary violations;
- all input candidates terminally accounted for in Architecture B;
- fan-in within every frozen count and byte budget;
- absence and ambiguity represented without invented items.

Provider-free replay proves representation and custody only, not model quality.

## Provider-call gate

If at least one architecture passes provider-free, freeze one development case
before calls. Use the current OpenRouter Gemini 3.1 Flash Lite model, JSON mode
plus local typed validation, temperature zero, reasoning disabled, no fallback,
response healing, or automatic retry. Architecture comparison uses the same
case and source target. Only a passing design may receive prospective transfer.

## Current practice check

Checked 2026-07-11 before schema work:

- OpenRouter structured output and API parameter documentation;
- the current Gemini 3.1 Flash Lite model capability/pricing page;
- the supplied focused-agent pipeline article;
- Lolla's hash-locked July structured-extraction practice record and its fan-in
  amendment.

Deliberate departures: no agent framework, strict-schema transport, retry loop,
judge/refiner cycle, deterministic semantic filter, graph integration, or live
runtime modification.

## Terminal outcome

Both representations passed provider-free replay across all five reviewed cases,
but neither passed the frozen one-case model probe.

The first probe used 14 calls. Architecture A saturated its schema at 54 items;
Architecture B returned two invalid/incomplete windows. One generic repair made
the schema maxima explicit as caps, targeted three-to-five items per window, and
corrected source-overlap and compact-payload measurement. The repair used 14
calls and still failed:

- A: 38 items and 19.5 KB (budgets pass), but reviewed move/thread survival was
  0.333/0.333 and claim-plus-mode survival was 0.200;
- B: typed admission 0.857, one invalid custody window, 43 items (target fail),
  move/thread survival 0.667/0.333, and claim-plus-mode survival 0.200.

No transfer or global synthesis was authorized. The next issue is a product
boundary: whether broad audit capture and compact reasoning input should be
separate artifacts rather than one normalized record serving both.

Terminal evidence:
`research/conversation-turn-record-redesign-conclusion-2026-07-11/decision.json`.
