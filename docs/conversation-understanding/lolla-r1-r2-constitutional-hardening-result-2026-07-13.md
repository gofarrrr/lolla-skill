# Lolla R1/R2 constitutional hardening result

Status: complete provider-free

Date: 2026-07-13

Provider calls made: zero

## Outcome

R1 and R2 now implement the smallest live correction required by the product
constitution. Lolla preserves the complete available prose conversation,
states what any bounded processing view omitted, freezes provider cost and data
policy before a call, and no longer lets the current probabilistic verifier
silently decide which admitted deterministic graph pressure is allowed to
reach the final reasoner.

This is a mechanical and architectural milestone, not product proof. It says
the system now preserves and exposes the experiment it intends to run. It does
not say the pressure is useful, the revised answer is better, or the receipt is
a certificate of reasoning quality.

## R1: honest source, reliance, provider, and ledger custody

The live run now has these enforceable properties:

- `conversation.txt` is the authoritative complete available prose transcript;
- large input produces a separately named
  `conversation_processing_view.{txt,json}` with hashes, lengths, retained
  windows, and exact omission metadata;
- `lolla_agent_result.v2` gives a healthy standard run the neutral action
  `review_revised_answer`, while degraded, incomplete, capture-critical, and
  high-stakes boundaries remain conservative;
- every model stage declares an output-token ceiling;
- OpenRouter requests declare price, provider order, fallback, supported-
  parameter, data-collection, and optional ZDR policy;
- a durable provider-budget ledger reserves both calls and worst-case USD
  before the network and blocks attempts that exceed the envelope;
- provider response ID and exact `usage.cost`, when returned, survive beside
  the local estimate; missing-key and budget-preflight outcomes are not counted
  as provider attempts;
- every private-table item that requires a ledger disposition is either fully
  inline or points to the exact complete JSON material the consumer can read;
- live price verification is separated from the byte-frozen historical pricing
  artifact, preserving evaluation replay integrity.

The current provisional default remains Gemini 3.1 Flash-Lite through
OpenRouter, pinned to `google-vertex/global` with fallback disabled. On the
2026-07-13 verification, its published rates remained $0.25/M fresh input,
$0.025/M cached input, and $1.50/M output. This records a price contract; it is
not evidence that the model is the best semantic operator.

## R2: deterministic pressure survives probabilistic verification

The pipeline now builds `constitutional_graph_survival` immediately after the
canonical recall pool is assembled and before the LLM verifier runs. The
legacy verifier and companion output still provide interpretation telemetry,
but their applicability judgments cannot delete or admit portfolio items.

The portfolio has two deliberately different layers:

1. A detailed active set: up to six direct canonical recalls plus one exact
   antagonist, tension, and ally relationship slot where available.
2. Compact reserve custody: direct capacity overflow, graph cap or duplicate
   overflow, duplicate input, and malformed/noncanonical input remain separate
   and inspectable.

Every active pressure item carries:

- canonical model and pressure identity;
- direct or graph origin and admission rank;
- exact source and relationship references;
- strongest plausible application and a concrete test;
- a boundary against forcing it and a boundary against ignoring it;
- an exact locator for the material the final consumer received.

Step 6 must disposition every active item as:

- `apply`: record a visible effect or private guardrail;
- `reject`: state the attempted application and failed condition;
- `park`: state the attempted application and reopen condition.

Rejecting or parking a pressure does not require adding it to public prose.
`not_considered` is invalid because it would erase custody. The final ledger is
hash-locked to the portfolio and finalized before the other private ledgers and
archive.

## Bounds and provider-free evidence

An exhaustive sliding-window measurement covered all 163 possible 60-ID
windows in the current 222-model registry. The observed worst cases were:

| packet | observed maximum | frozen ceiling |
| --- | ---: | ---: |
| active items plus ledger skeleton | 4,690 estimated tokens | 6,000 |
| complete compact reserve | 9,510 estimated tokens | 12,000 |

The estimate is the ceiling of compact JSON UTF-8 bytes divided by four. It is
a deterministic fan-in guard, not a claim about model attention quality.

Provider-free fixtures cover:

- 140-turn authoritative conversation preservation;
- neutral reliance and legacy-receipt compatibility;
- request policy, output ceiling, exact cost, response identity, and provider
  budget preflight;
- survival of all 60 admitted direct candidates into active or reserve;
- survival of a protected strange candidate even when later rejected;
- separate direct, graph, cap, duplicate, malformed, reject, and park paths;
- exact consumer visibility under a deliberately small rendered-table cap;
- complete apply/reject/park coverage without mandatory public bloat;
- portfolio tamper detection and historical frozen-evaluation compatibility.

## What remains unknown

R1/R2 do not answer the semantic product questions:

- Will a fresh reasoner make good use of the pressure instead of absorbing it?
- Can it reject noise specifically and honestly?
- Will a useful original answer survive the extra pressure?
- Does graph pressure add anything beyond a strong fresh neutral second pass?
- Can the public answer remain decisive and compact?
- Will a cold future reader understand the receipt without treating it as a
  quality badge?

These unknowns must remain evaluation targets. They must not be replaced with
deterministic semantic gates or marketing claims.

## Next boundary: R3

R3 may now prepare one fresh-consumer proof. Before any paid request, it must
freeze locally:

- Case 01 source and preservation packet;
- the exact active pressure portfolio and hash;
- model, OpenRouter provider policy, schema, prompt, and prompt hash;
- no-retry, no-fallback, no-healing behavior;
- stage output ceiling and a total $0.01 budget.

Only then may one Gemini 3.1 Flash-Lite pressure attempt run. Its evaluation
must separate grounding, disposition quality, non-forced contribution,
preservation, unsupported claims, private over-absorption, public bloat, cost,
and failure custody. If it fails, preserve the failure and return to
provider-free diagnosis. If it passes every gate, the roadmap permits one
separately capped quiet control. Neither outcome proves reliability.
