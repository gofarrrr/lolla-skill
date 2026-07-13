# Lolla post-V1 constitution-aligned roadmap

Status: active next-development sequence

Date: 2026-07-13

Source audit: `docs/conversation-understanding/lolla-current-state-constitutional-audit-2026-07-13.md`

## Goal

Make the live one-run-plus-receipt product constitutionally honest and testable
without redesigning Lolla from scratch.

The sequence preserves the product boundary:

```text
LLMs interpret messy meaning.
Deterministic code owns identity, custody, bounds, replay, budgets, and ledgers.
The graph introduces pressure but does not certify relevance.
The final reasoner may apply, reject, or park pressure.
The public answer stays disciplined.
The receipt records process without certifying wisdom.
The human owns the decision.
```

There are five development stages after this completed audit. They are likely
to require roughly six to nine bounded implementation/evaluation goals, because
the graph-survival and semantic-representation stages should each be split if
their provider-free gates expose more than one causal defect. This is not a
calendar promise and not an invitation to add architecture.

## R0 — Constitutional audit and development freeze

Status: complete

Completed:

- traced the live skill from capture through archive;
- compared the live runtime with Constitution v0–v5 and evaluation doctrine;
- inspected four recent local runs without copying conversation text;
- separated live behavior from research-only corrections;
- checked current OpenRouter and Gemini practice;
- froze paid work and premium-model experimentation;
- published a machine-readable drift register.

Exit condition: met.

## R1 — Provider-free trust, capture, cost, privacy, and custody hardening

Status: complete (2026-07-13; provider calls: zero)

Purpose: make a run honest about what it captured, what it spent, what the
provider could do with the data, and what its receipt actually proves.

Implement in one bounded goal where possible:

1. Replace clean-run `use_revised_answer` with a neutral review action. Preserve
   explicit degraded, incomplete, and high-stakes stop behavior.
2. Preserve the complete available prose transcript as the authoritative
   artifact. Move compaction into a separately named processing view with exact
   omission metadata.
3. Add stage-specific output ceilings, call ceilings, an estimated and exact
   USD envelope, `provider.max_price`, and a no-call preflight.
4. Persist OpenRouter response ID, exact `usage.cost`, requested model, served
   model, and declared provider routing policy. Keep the local estimate as a
   comparison, not the billing source of truth.
5. Define an explicit provider data policy. Test `data_collection=deny` and ZDR
   capability provider-free through request construction; do not claim ZDR
   availability without endpoint evidence.
6. Add the private-table invariant: every ledger-required atom is fully visible
   or exactly resolvable by the consumer.
7. Refresh the price table from the current models API and make staleness a
   visible preflight condition.
8. Correct current product documentation and examples to match the neutral
   reliance contract.

Provider calls: zero.

Acceptance contract:

- a 140-turn fixture preserves the complete authoritative transcript and marks
  its processing view partial;
- no clean fixture returns an action that implies advice approval;
- every boundary request has an output ceiling and price envelope;
- a fixture cannot exceed its call or USD contract;
- exact provider cost and response identity have schema custody when present;
- privacy posture and fallback policy are explicit in request and receipt;
- table/ledger visibility equivalence holds under an intentionally tiny cap;
- existing failure artifacts remain preserved without automatic retry or
  healing;
- all affected tests pass provider-free.

Implementation result:

- `conversation.txt` remains the complete authoritative prose artifact; a
  bounded `conversation_processing_view.{txt,json}` now carries separate
  partial-view hashes, lengths, and omission metadata;
- `lolla_agent_result.v2` returns `review_revised_answer` for a clean standard
  run and maps it to `require_external_review`;
- every OpenAI-compatible boundary request now has a stage output ceiling,
  price envelope, cumulative call/USD reservation, explicit fallback/data
  policy, and visible price-table freshness;
- the default Gemini Lite OpenRouter route is pinned to
  `google-vertex/global`, fallbacks are off, parameter support is required,
  and data collection defaults to `deny`; ZDR remains opt-in and is never
  claimed without the request flag;
- response IDs and provider-reported `usage.cost` survive into call records,
  usage summaries, the budget ledger, and compact receipts alongside local
  estimates;
- preflight blocks and missing keys are recorded as non-attempts rather than
  provider work;
- private-table source atoms now remain fully inline or resolve to the exact
  complete JSON material required by their ledger;
- the 140-turn, request-construction, exact-cost, call-ceiling, USD-ceiling,
  neutral-reliance, and ledger-custody fixtures pass locally.

Stop rule: if a proposed repair requires deterministic semantic inference,
split the goal and redesign the interface. Do not add a keyword or chronology
gate.

## R2 — Constitutional graph-survival path

Status: complete (2026-07-13; provider calls: zero)

Purpose: stop deleting independent deterministic pressure while keeping the
consumer context bounded.

Implement the smallest live correction by reusing research contracts where
they fit:

1. Start from controlled canonical model IDs only.
2. Keep direct and graph recall provenance separate.
3. Build a small detailed active set and a compact edge reserve. Bounds are
   frozen from provider-free token and fixture measurements, not chosen by a
   relevance LLM.
4. Let a probabilistic formatter compact pressure, but not delete admitted
   candidates.
5. Give every admitted candidate a strongest plausible application, concrete
   test, force boundary, ignore boundary, and exact source/graph reference.
6. Require the final consumer to apply, reject, or park each candidate. A
   semantic rejection must state the attempted application and failed
   condition; `not_considered` remains a technical custody failure only.
7. Preserve the full candidate pool and deterministic suppression reasons in
   the receipt.

Provider calls: zero until every fixture and invariant passes.

Acceptance contract:

- no candidate disappears between bounded graph admission and consumer packet;
- no probabilistic applicability gate controls graph survival;
- all canonical IDs resolve exactly;
- direct, graph, duplicate, cap, malformed, and parked paths are distinguishable;
- active and reserve token load is measured at fan-in;
- a strange protected candidate survives even when it is later rejected;
- a forced-use fixture proves that rejection is allowed and public bloat is not
  required;
- every ledger disposition resolves to material the consumer actually saw.

Implementation result:

- the live pipeline now creates `constitutional_graph_survival` immediately
  after deterministic/embedding recall and before the probabilistic verifier;
- the existing verifier and companion card remain available as interpretation
  telemetry, but none of their applicability fields control survival in the
  constitutional portfolio;
- up to six direct recalled canonical IDs enter the detailed active set, with
  one exact antagonist, tension, and ally slot added where the relationship
  graph supplies them; direct overflow, graph overflow, duplicate inputs, and
  malformed inputs remain distinguishable in compact reserve custody;
- every active item carries its strongest plausible application, a concrete
  test, force and ignore boundaries, graph/source provenance, a stable pressure
  ID, and an exact consumer locator;
- Step 6 receives the complete active material and must disposition every item
  as `apply`, `reject`, or `park`; rejection records the failed condition,
  parking records the reopen condition, and neither requires public prose;
- the disposition ledger is hash-locked to the portfolio, finalized before
  archive, and surfaced in run health and graph-survival reporting;
- exhaustive provider-free measurement over all 163 possible 60-ID windows in
  the 222-model registry observed a maximum of 4,690 estimated active tokens
  and 9,510 estimated reserve tokens; frozen runtime ceilings are 6,000 and
  12,000 respectively;
- protected-strange-candidate, forced rejection, parking, exact visibility,
  tamper, malformed, duplicate, and bounded-fan-in fixtures pass locally.

Stop rule: do not route all 60 current candidates into Step 6. “No premature
pruning” means bounded inspectable possibility, not context dumping.

## R3 — One fresh-consumer proof, then a quiet control

Status: repaired operational attempt closed (2026-07-13); transport repair
confirmed; semantic exit condition not met; quiet control and further calls
not authorized

Purpose: test the corrected pressure interface without the original reasoner's
same-context trajectory.

Only after R1 and R2 pass:

1. Freeze Case 01 source, packet, model, provider policy, strict small schema,
   prompt hash, graph identity, call ceiling, output ceiling, and $0.01 total
   budget.
2. Run one Gemini 3.1 Flash-Lite fresh consumer through OpenRouter.
3. Allow no retry, fallback, response healing, prompt change, or post-hoc gold
   repair.
4. Review separately:
   - source grounding;
   - apply/reject/park quality;
   - non-forced graph contribution;
   - preservation of useful original advice;
   - unsupported-claim leakage;
   - private over-absorption;
   - public bloat and hedging;
   - exact cost and failure custody.
5. If the pressure case passes, freeze and run one quiet/stand-down consumer to
   test restraint. If it fails, preserve the failure and return provider-free.

Maximum authorized provider work: one $0.01 pressure attempt. The frozen R3
contract may automatically authorize one separately capped cheap quiet case
only if every pressure-case gate passes; no additional founder confirmation is
required. Gemini 3.5 is not authorized.

Exit condition: at least one source-grounded non-forced contribution or
valuable grounded rejection, with no custody failure and no public friction
theater. One success is diagnostic evidence, not product reliability.

Result:

- every provider-free gate passed and the Case 01 source, original answer,
  nine-item constitutional portfolio, reserve, prompt, schema, request, model,
  endpoint, and budget were frozen under exact hashes;
- the one authorized Gemini 3.1 Flash-Lite request reached Google through the
  pinned OpenRouter route but returned HTTP 400 `INVALID_ARGUMENT` before
  inference;
- no candidate, usage record, generation identity, or exact cost was returned;
  the budget ledger conservatively accounts the full `$0.00816425` reservation
  without claiming that amount was charged;
- the raw failure remains privately preserved and a hash-linked redaction is
  checked in; no retry, fallback, response healing, premium model, or quiet
  control ran;
- semantic review dimensions are explicitly not evaluable; failure custody is
  a partial pass because exact cost was unavailable;
- current Google documentation and repository history narrow the likely issue
  to structured-schema subset or complexity interoperability, but the generic
  provider error does not prove one offending field.

R3 is closed as an honest negative experiment, not as product or semantic
failure. Before R4, the next provider-free boundary is to project the response
schema onto Google's documented subset, keep business-rule validation local,
and freeze a smaller compatibility-tested request. Any further call requires a
new explicit authorization. See
`docs/conversation-understanding/lolla-r3-fresh-consumer-result-2026-07-13.md`.

Provider-free repair result:

- the failed R3 request remains unchanged and reproducible;
- a separate prospective projection reduces provider-visible properties from
  18 to 14 and removes all 22 string-length constraints from the wire;
- the projection passes a local lint limited to Google's documented schema
  subset and does not exceed the 14-property count of a smaller historical
  Gemini 3.1 Flash-Lite success;
- deterministic compilation restores redundant model/risk custody, maps the
  explicit disposition boundary, enforces the original text and cross-field
  rules, and performs no semantic applicability judgment;
- the complete source, original answer, nine active pressures, reserve,
  provider policy, and review vector remain unchanged;
- the prospective maximum estimate is `$0.0081855`, provider calls remain
  zero, and the frozen repair contract authorizes zero future calls.

The provider-free repair boundary is met. See
`docs/conversation-understanding/lolla-r3-provider-schema-repair-result-2026-07-13.md`.

Repaired execution result:

- a separate exact authorization permitted one repaired Gemini 3.1 Flash-Lite
  pressure attempt and no quiet control, retry, fallback, healing, or premium
  model;
- Google accepted the projected schema and returned strict JSON, so the earlier
  provider-schema transport gap is closed for this request;
- the call cost exactly `$0.0062705`, within the one-cent pressure ceiling;
- the response failed one deterministic cross-field rule: a `park` disposition
  claimed the material effect `uncertainty_change`;
- the exact candidate was not changed or rescued, and the canonical compiler
  failure reproduced during closeout;
- source-first semantic review was prohibited, seven semantic axes remain not
  evaluable, and exact cost/failure custody passed;
- no quiet control or further provider call ran.

R3 is semantically closed without meeting its exit condition. See
`docs/conversation-understanding/lolla-r3-repaired-pressure-result-2026-07-13.md`.

## R4 — Multi-thread conversation state and reasoning abstraction

Purpose: improve what the pressure system understands without turning Python
into a semantic state machine.

Use the role-first research selectively:

- represent separate starting position, current position, qualification,
  unresolved matter, and reopen condition where the supplied context supports
  them;
- preserve multiple strategic threads and cross-thread relationships;
- keep exact source spans, speakers, turns, and ambiguity;
- let complementary readers overlap instead of becoming routing silos;
- fan in through a bounded synthesis contract;
- create controlled fact-stripped reasoning patterns for graph recall;
- never let deterministic code infer semantic role from keywords, turn counts,
  or chronology alone.

First evaluate on the existing 12 naturalized, 24-message V1 conversations.
They are realistic simulations for system reliability, not real-user proof.

Provider calls: local fixture and sealed-output replay first. New calls require
one falsifiable gap that cannot be answered from existing artifacts.

Exit condition: system-level coverage, role placement, temporal fidelity,
source precision, fan-in load, and false-stand-down behavior improve separately
without weakening graph survival or custody.

## R5 — Product evidence and receipt reconstruction

Purpose: determine whether the product is actually useful and whether its
receipt transfers reasoning context to a fresh reader.

Required evidence:

1. Compare a strong fresh neutral control with the corrected pressure path.
2. Score a vector, never one quality number:
   - capture/custody;
   - semantic coverage;
   - temporal fidelity;
   - direct versus graph attribution;
   - disposition quality;
   - restraint and false stand-down;
   - useful falsifier, question, frame, condition, or decision delta;
   - over-absorption, bloat, hedging, and unsupported claims;
   - operability and exact cost;
   - receipt reconstruction.
3. Give a cold agent or human only the frozen receipt package and test whether
   they can reconstruct what happened without treating it as certification.
4. Seek genuine real-user conversations only when they become available; do
   not fabricate a reliability claim from polished simulations.
5. Update public claims only after evidence supports them.

Exit condition: a decision can be made about whether to integrate, revise, or
stop the V2 pressure path. “Promising” is not an automatic integration result.

## R6 — Later product work, explicitly not on the critical path

These remain outside the current development sequence:

- project-level knowledge base across receipts;
- organization-wide comparisons;
- reasoning teacher and graph visualization;
- SDK/API productization beyond the minimum fresh-consumer harness;
- tool-call transcript expansion;
- premium model tier;
- public sharing and repository gardening beyond claim accuracy.

They become relevant only after the one-run product shows useful pressure and a
receipt that a fresh reader can reconstruct.

## Immediate next goal

Provider-free R3 task-shape reassessment. The repaired call proved transport
compatibility but failed the explicit response contract, so another paid call
would be an ungrounded retry. Use the preserved candidate and local fixtures to
identify whether disposition, cross-field consistency, answer drafting, or
their one-pass combination is the smallest falsifiable defect. Compare only
constitutionally honest alternatives, including keeping one pass, separating
disposition from synthesis, or reserving a stronger final operator. Preserve
LLM ownership of semantic applicability and deterministic ownership of
identity, custody, vocabulary, bounds, budgets, and explicit consistency.

Do not begin provider-backed R4 work, shop models, or authorize a quiet control
until this reassessment produces a frozen hypothesis, local acceptance
contract, cost consequence, and stop rule. R4 remains the next major roadmap
stage; this closeout prevents its design from inheriting an unexplained R3
failure.
