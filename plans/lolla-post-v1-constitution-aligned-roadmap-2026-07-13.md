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

Status: collapsed-outcome operational attempt closed and prospective validator
corrected provider-free (2026-07-13); semantic exit condition not met; paid R3,
quiet control, and further calls deferred

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

Provider-free task-shape reassessment result:

- the exact response returned all nine rows and had one mechanical finding;
- the finding is a direct contradiction between independent `park` and
  `uncertainty_change` labels, not evidence that the complete task overloaded
  the model;
- a controlled outcome vocabulary maps one explicit LLM judgment to the
  canonical disposition/effect pair without deterministic relevance inference;
- the selected one-pass design keeps all nine pressures, one call, zero
  transfer boundaries, 13 schema properties, and a `$0.00816725` maximum
  estimate;
- a separated disposition/synthesis design would require two serial calls, a
  disposition-ledger transfer, and a `$0.01180325` maximum stress estimate;
- current evidence does not implicate answer drafting, so the split is not
  earned;
- local apply/reject/park, identity, custody, adversarial, fan-in, cost, and
  no-semantic-repair gates pass with zero provider calls;
- the redesign is prospective and not model-validated; no runtime integration
  or further call is authorized.

See
`docs/conversation-understanding/lolla-r3-task-shape-reassessment-result-2026-07-13.md`.

Prospective collapsed-outcome case preparation result:

- a new 28-message synthetic reliability case was frozen before pressure
  selection or expected outcomes;
- six source-grounded patterns were mapped only to existing canonical IDs and
  the deterministic graph added three inspectable pressures without deletion;
- the protected source-first review was authored and committed only after the
  source and pressure portfolio were frozen;
- the exact one-pass request, cheap operator, one-cent envelope, first-failure
  stop rule, no-retry runner, and non-authorizing founder decision template are
  sealed under hashes;
- mocked success, provider failure, malformed JSON, authorization, hidden
  review, budget, identity, and tamper paths pass locally;
- provider calls made and currently authorized remain zero.

The provider-free R3 preparation boundary is met. The remaining R3 decision is
founder-owned: authorize or defer one exact Gemini 3.1 Flash-Lite attempt with a
hard `$0.01` ceiling. See
`docs/conversation-understanding/lolla-r3-collapsed-outcome-case-preparation-result-2026-07-13.md`.

Collapsed-outcome execution result:

- the founder authorized exactly one attempt with a hard `$0.01` ceiling;
- Gemini 3.1 Flash-Lite returned strict JSON through the pinned Google route at
  an exact provider-reported cost of `$0.005517`;
- all nine controlled outcomes compiled without retry, fallback, healing, or
  candidate modification;
- the frozen runner nevertheless failed its complete mechanical gate because
  it treated any `reasoning_details` record as returned reasoning content;
- the actual payload had no `message.reasoning`, reasoning text, summary, or
  encrypted data, only signature and format metadata;
- the frozen result remains failed and is not reclassified; source-first
  semantic review was not opened, so the R3 semantic hypothesis remains
  unresolved;
- exact cost, generation identity, raw-payload hashes, redaction, compiler
  output, and one-call custody are preserved; no additional call or quiet
  control is authorized.

The next boundary is a narrow provider-free prospective correction of the
reasoning-content validator. The frozen result must remain unchanged and must
not be reopened for semantic review. After that correction, explicitly defer
further paid R3 work or prepare a genuinely new prospective case before any
new call. See
`docs/conversation-understanding/lolla-r3-collapsed-outcome-execution-result-2026-07-13.md`.

Prospective reasoning-exclusion correction result:

- current OpenRouter reasoning-detail fields and aliases were checked again;
- a new prospective R3 validator distinguishes actual returned content from
  absent, empty, and signature-only metadata without reading provider values;
- plaintext, summaries, encrypted data, compatible content aliases, mixed
  records, and malformed/unknown shapes fail closed;
- 35 focused fixtures cover the contract, while the broader relevant slice
  passes 72 tests provider-free;
- seven historical execution files remain pinned under exact hashes;
- the frozen runner classification and mechanical failure remain unchanged,
  and semantic review remains closed;
- the correction made zero provider calls and authorizes zero further calls,
  retries, judges, premium models, or runtime integration;
- paid R3 is explicitly deferred unless a new falsifiable question survives
  provider-free review and receives separate founder authorization.

See
`docs/conversation-understanding/lolla-r3-reasoning-exclusion-correction-result-2026-07-13.md`.

## R4 — Multi-thread conversation state and reasoning abstraction

Status: provider-free inventory/replay and missingness-aware fan-in complete;
corrected complementary-reader diagnostic closed; token allocation repaired;
semantic-distinction holdout closed mechanically complete but semantically
unsupported; provider-free causal diagnosis and residual-task identity repair
complete; v1 matched design rejected for evidence leakage; provider-free
leakage-corrected v2 matched holdout and its one-use execution complete;
execution result published; five-record provider-free false-positive causal
diagnosis complete; no provider call or follow-on experiment authorized

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

First replay result:

- all twelve 24-message source hashes reproduce;
- 400 unique case-linked JSON artifacts and 543 case/artifact links now have a
  metadata-only, hash-locked inventory;
- seven transfer paths completed, one failed at role custody, and four failed
  before inference;
- exact mechanical role/source/fan-in/custody facts are now separated from
  semantic judgments that still require probabilistic or human review;
- five reviewed completed cases stood down correctly and two stood down
  falsely because material pressure was absent upstream of deterministic
  recall;
- unresolved matter, reopen condition, and cross-thread relationship lack
  distinct primary contract surfaces;
- primary graph value remains unmeasured because zero graph candidates became
  active in transfer;
- one next task is earned: design a missingness-aware system-level
  conversation-state fan-in contract. It must preserve explicit reader output,
  overlap, source locators, and missing/empty/partial/failed states without
  deterministic semantic inference.

See
`docs/conversation-understanding/lolla-r4-provider-free-corpus-replay-result-2026-07-13.md`.

Missingness-aware fan-in result:

- a strict explicit tagged union now separates `complete`, `completed_zero`,
  `partial`, `failed`, and `missing` reader results;
- six required surfaces remain visible: starting, current, qualification,
  unresolved matter, reopen condition, and cross-thread relationship;
- complete provider-authored payloads, exact source locators, speakers, turns,
  artifact hashes, and exact relationship endpoints survive;
- complementary overlapping records are counted but never merged, ranked, or
  voted away;
- fan-in is frozen at twelve readers, 48 records, 256 KiB of semantic payload,
  and a 1 MB handoff;
- four representative V1 replays preserve 24 explicit reader results: five
  complete, one completed-zero, two partial, two failed, and fourteen missing;
- seven admitted semantic records and 21 exact source locators reproduce with
  all handoffs inside bounds and no provider call;
- Case 02 now exposes a completed-zero qualification separately from missing
  unresolved, reopen, and relationship readers;
- no prompt, model, runtime, graph, semantic merge, quality score, or semantic
  absence inference was added.

The assembly defect is repaired provider-free. The semantic defect remains:
primary V1 produced no distinct records for the three missing surfaces. A
bounded complementary-reader experiment is therefore worth preparing, but
this result authorizes neither a provider call nor runtime integration. See
`docs/conversation-understanding/lolla-r4-conversation-state-fan-in-result-2026-07-13.md`.

Complementary-reader preparation result:

- one exposed false-stand-down target and one matched restraint control were
  frozen source-first before the execution contract;
- the first reader separately returns unresolved-matter and reopen-condition
  reviews, each with explicit present, quiet, and ambiguous behavior;
- the second reader sees unchanged admitted semantic payloads and exact record
  IDs, and may complete with zero rather than manufacture a relationship;
- the provider-visible schemas use only Google's documented structured-output
  subset and are 1,653 and 1,442 canonical bytes;
- the fixed route is Gemini 3.1 Flash Lite through pinned OpenRouter Google
  Vertex with ZDR, data-collection denial, no fallbacks, no healing, and exact
  provider attribution;
- the four-call maximum has a `$0.015` per-case and `$0.03` total ceiling; the
  conservative provider-free estimate is `$0.0160615` total;
- positive, quiet, ambiguous, missing, failed, bad-alias, bad-endpoint,
  artifact-drift, dynamic relationship, fan-in, and cost paths pass locally;
- structural fixtures are explicitly not provider output or semantic evidence;
- no provider call, runtime change, graph change, model comparison, semantic
  gate, or quality score was added.

Every provider-free gate now passes. The preparation does not authorize a
call. The next founder-owned decision is whether to authorize this exact
four-call maximum causal diagnostic. See
`docs/conversation-understanding/lolla-r4-complementary-reader-preparation-result-2026-07-13.md`.

First execution and token-correction result:

- the founder authorized the exact prepared diagnostic, and the runner made
  two uncertainty calls before the dependency stop rule closed both
  relationship paths;
- both calls reached Gemini 3.1 Flash Lite through the pinned Google provider,
  but ended at `finish_reason: length` with unterminated JSON;
- the target used 865 of 885 completion tokens for reasoning and the control
  used 861 of 886, leaving only 20 and 25 non-reasoning tokens;
- no candidate was parsed or admitted, so material recovery, restraint,
  evidence precision, role placement, and relationship fidelity remain not
  evaluable; partial prefixes are not semantic evidence;
- two exact calls cost `$0.009036`; there was no retry, fallback, healing,
  evaluator, embedding, graph, pipeline, runtime, or relationship call;
- the historical attempt is hash-locked and closed without reclassification;
- current OpenRouter and Google guidance confirms that reasoning consumes the
  output allowance and Gemini thinking levels are relative rather than strict
  budgets;
- a prospective provider-free correction changes only uncertainty
  `/reasoning/effort` from `low` to `minimal` and `/max_tokens` from `900` to
  `1600`; every semantic input and the relationship allocation remain
  unchanged;
- the corrected four-call conservative estimate is `$0.0181615`, still inside
  the original `$0.015` per-case and `$0.03` total ceilings;
- closeout, exact request-diff, fake four-call, global-restoration,
  authorization, custody, and zero-network tests pass locally.

The first authorization was consumed. At that boundary the new prospective
contract authorized zero calls and made the corrected diagnostic the next
founder-owned decision. That decision was subsequently authorized and closed
as recorded below. Runtime integration, model comparison, wider corpus work,
and semantic deterministic gating remained unauthorized. See
`docs/conversation-understanding/lolla-r4-complementary-reader-execution-result-2026-07-14.md`.

Corrected diagnostic and source-first review:

- the founder authorized the separate token correction, changing only the
  uncertainty allocation from `900/low` to `1600/minimal`;
- all four calls completed with strict parseable JSON and exact intended-model
  attribution; both relationship dependencies and both final fan-ins opened;
- exact corrected-run cost was `$0.010835`, with no retry, fallback, healing,
  evaluator, embedding, graph, pipeline, runtime, or model comparison;
- the target narrowly passed material recovery by preserving the temporary-
  support and hidden steady-state labor pressure, while missing the wider
  cross-setting and accessible-supply parts of the frozen target;
- the restraint control failed: the reader converted an earlier gap and
  already operationalized boundary/review criteria into three uncertainty
  records and two relationships;
- exact aliases, separate role surfaces, and exact relationship endpoint IDs
  worked mechanically, but evidence precision and relationship restraint did
  not;
- all four usage records report zero reasoning tokens while the frozen runner's
  broad reasoning-field flag is true; field values were not preserved, so the
  calls are not reclassified and future runners must reuse R3's stricter
  content-shape validator;
- there is no scalar score, production-model selection, runtime/graph
  integration, wider-corpus authorization, or additional call authorization.

The semantic hypothesis is not supported. The next goal is the provider-free
semantic-distinction contract in
`plans/lolla-r4-semantic-distinction-plan-2026-07-14.md`. It must teach the
probabilistic reader—not deterministic Python—to distinguish genuinely
remaining uncertainty from adopted preconditions, safeguards, written
processes, and scheduled reviews. Current cases become development evidence;
any later provider validation requires a newly frozen holdout.

Provider-free semantic-distinction result:

- nine exposed development fixtures now distinguish genuine unresolved and
  reopen records from later resolution, adopted preconditions, existing
  safeguards, scheduled reviews, ambiguity, and endpoint-restating
  relationships;
- the probabilistic v2 prompt contract carries those semantic distinctions;
  deterministic code remains limited to schema, identity, evidence, endpoint,
  bound, budget, and custody checks;
- an additive runner reuses the strict R3 reasoning-envelope inspector and
  leaves the historical v1 prompt and runner byte-frozen;
- one untouched false-stand-down target and one untouched restraint control
  were frozen source-first before request previews;
- the exact maximum is four Gemini 3.1 Flash-Lite calls through the pinned
  Google Vertex OpenRouter route, with a conservative `$0.0280125` estimate and
  a `$0.03` hard ceiling;
- all local gates and the full repository suite pass; provider calls made and
  currently authorized remain zero.

See
`docs/conversation-understanding/lolla-r4-semantic-distinction-preparation-result-2026-07-14.md`.

Semantic-distinction holdout execution result:

- the founder authorized the exact two-case, four-call maximum
  `lolla-r4-semantic-distinction-holdout-a3` package;
- all four Gemini 3.1 Flash-Lite calls completed with strict JSON, intended
  Google attribution, metadata-only reasoning envelopes, local admission,
  both relationship dependencies, and both final fan-ins;
- exact provider-reported cost was `$0.01107025`, with no retry, fallback,
  healing, evaluator, embedding, graph, pipeline, runtime, or model change;
- Case 01 narrowly recovered a durable city operating-capability dependency
  but missed its central recurring funding/ownership structure and used
  imprecise evidence;
- Case 01 also recast a precondition and adopted process as a reopen condition;
- Case 04 failed restraint by converting deferred redesign work, predefined
  thresholds, fallbacks, and a fixed twelve-month review into three
  uncertainty records and two relationships;
- exact aliases, role separation, and exact relationship IDs passed
  mechanically, while false-positive restraint, evidence precision, and
  semantic relationship fidelity failed;
- the semantic hypothesis is not supported, the authorization is consumed,
  and Case 01/04 are now exposed development evidence;
- no retry, further call, runtime/graph integration, wider-corpus work, R5
  promotion, production-model selection, model comparison, or scalar score is
  authorized.

See
`docs/conversation-understanding/lolla-r4-semantic-distinction-execution-result-2026-07-14.md`.

Provider-free causal diagnosis result:

- all eight admitted Case 01/04 records are mapped to exact authoritative
  aliases, current-position treatment, all supplied prior role records,
  applicable frozen prompt clauses, and source-first verdicts;
- disconfirming evidence leads the diagnosis: the v2 prompt already contains
  the intended exclusions, no same-case causal ablation exists, and Case 04's
  pending design is broadly "unresolved" in ordinary language;
- semantic ontology/task mismatch is nevertheless the best-supported primary
  explanation because the output consistently inventories broad unresolved
  and reopen surfaces instead of subtracting work already operationalized by
  the current position;
- fallible-prior anchoring is a supported amplifier, but it cannot explain the
  threshold and hydraulic/process false positives that have no matching prior
  gap;
- paired generative completion pressure remains plausible but unisolated, and
  model/context limitation is not supported as primary because late endpoint
  evidence was retrieved and used coherently;
- the frozen target already selects the product ontology, so no new founder
  ontology decision is required for this holdout;
- the diagnosis made zero provider calls and changed no prompt, relationship
  reader, historical evidence, runtime, graph, model, route, or holdout.

The one earned next unit is a separately scoped provider-free semantic-task
repair. Do not bundle it with context authority, task shape, relationship
reading, or model/context changes. See
`docs/conversation-understanding/lolla-r4-semantic-distinction-causal-diagnosis-2026-07-14.md`.

Provider-free residual-task identity repair result:

- a new additive prompt makes residual discovery—not broad inventory—the
  complete provider-visible role, operation, surface vocabulary, example set,
  schema description, and output rule;
- provider-facing `residual_decision_gap` and
  `residual_reconsideration_dependency` values map deterministically to the
  existing canonical `unresolved_matter` and `reopen_condition` roles without
  reading free text;
- paired response structure, fields, record bounds, aliases, zero, ambiguity,
  complete source/prior context and order, relationship behavior, model,
  provider route, runtime, and graph remain unchanged;
- the complete A3 Case 01/04 contexts appear in provider-ready request previews
  with per-component hashes, bytes, conservative token estimates, schema size,
  task-at-end custody, changed fields, unchanged dimensions, and declared
  omissions;
- all nine historical semantic-distinction fixtures are reused through a
  separate additive catalog; Case 04 locally expects zero on both residual
  surfaces, while Case 01 preserves only the recurring operations
  funding/ownership residual;
- the prompt is 191 UTF-8 bytes and 96 deterministically estimated tokens
  shorter than v2; the schema is 122 bytes larger only because of longer
  residual labels and the dual-basis evidence description;
- historical v1/v2, target, authorization, execution, evidence, and
  relationship hashes reproduce; frozen replay remains 12 cases, 543 links,
  and 400 unique artifacts;
- zero provider calls were made, no holdout was prepared, and provider-free
  contract validity is explicitly not model semantic validation.

The completion decision is
`residual_contract_ready_for_new_holdout_design`. A new holdout-design goal
must be started separately and must preserve this single-variable contract.
See
`docs/conversation-understanding/lolla-r4-residual-task-identity-repair-result-2026-07-14.md`.

Provider-free matched residual holdout-design result:

- four genuinely new 28-message simulated conversations and four fallible
  prior artifacts are frozen before request previews across oral-history
  release, serialized audio, research-data stewardship, and cross-campus
  language-program domains;
- two cases are governed-pending restraint controls, one with a broad prior
  gap anchor and one without; one case contains a genuine recurring
  ownership/funding/capacity residual; one contains a genuine distinct future
  dependency failure outside adopted machinery;
- protected source-first targets freeze both canonical surface dispositions,
  strongest aliases, machinery reasoning, speaker/modal ownership, predicted
  false positives, limitations, and ontology assumptions before any provider
  output;
- each case has an exact frozen-v2 arm and exact residual-task arm with source,
  prior, order, model, route, seed, 1,600-token cap, minimal reasoning,
  streaming, strict JSON, and privacy controls held equal;
- eight context manifests account for artifact/canonical hashes, component
  sizes and estimates, exact order, task-at-end, complete inclusion, all
  declared deltas, unchanged dimensions, and omissions;
- a counterbalanced eight-call maximum, ten-dimension non-scalar evaluation
  vector, categorical decision matrix, exact-authorization shape, raw terminal
  result custody, and stop-on-first-failure runner are frozen;
- official Google and OpenRouter practice and pricing were rechecked; the
  conservative estimate is `$0.0424625`, with proposed future ceilings of
  `$0.015` per matched case and `$0.06` total;
- historical v1/v2/residual hashes reproduce and replay remains 12 cases, 543
  links, and 400 unique artifacts after explicit exclusion of the new roots;
- the package makes and authorizes zero provider calls at `$0.00` and does not
  establish model semantic success or product usefulness.

The provider-free design decision is
`matched_residual_holdout_ready_for_founder_authorization`. This is eligibility
for a separate founder decision, not an authorization request or execution
instruction. See
`docs/conversation-understanding/lolla-r4-matched-residual-holdout-design-result-2026-07-14.md`.

Matched-holdout v2 leakage-correction result:

- commit `b46464278e86f4c5d6c53e154bc272d93f09b116` and all v1 artifacts remain
  immutable, but v1 is rejected permanently because its sources and priors
  disclosed expected classifications; it had no authorization, output, call,
  or cost;
- four additive v2 sources and priors use new case IDs and distributed
  operational evidence; each source has 28 messages, the prohibited-language
  scan is zero, and the exact human declaration `human leakage review passes`
  is bound to every source/prior hash;
- the human review records that no assistant states the expected category, the
  broad Case 01 prior does not self-discount, no conversation instructs a
  provider what to return, and the last four messages are insufficient to
  determine both surfaces in every case;
- Cases 01 and 02 retain the honest limitation that their final summaries give
  some recency assistance without revealing or independently determining the
  complete target;
- the protected source-first target was frozen before request previews and
  honestly supports two quiet controls, one continuing ownership/funding/
  capacity matter, and one premise-breaking designation dependency;
- complete source/prior bytes and source → prior → task order are identical
  between arms; model, Google Vertex route, seed, 1,600-token cap, minimal
  excluded reasoning, streaming, strict JSON, privacy, and paired response
  shape are equal;
- only the declared residual-task identity intervention may differ; exact
  delta manifests reject any undeclared change;
- the runner and execution-visible manifest have no target or review path,
  require an exact separate authorization, construct no transport on dry run,
  stop on the first failure, and permit no retry, fallback, healing,
  relationship, evaluator, embedding, graph, pipeline, runtime, or model
  substitution;
- official pricing was rechecked; the conservative estimate is `$0.040521`,
  with proposed anti-runaway ceilings of `$0.03` per matched case and `$0.12`
  total;
- frozen replay remains exactly 12 cases, 543 links, and 400 unique artifacts;
  zero provider calls were made and no authorization artifact exists.

The corrected provider-free decision is
`matched_residual_holdout_v2_ready_for_founder_authorization`. This is only
eligibility for a separate founder decision. See
`docs/conversation-understanding/lolla-r4-matched-holdout-v2-leakage-correction-result-2026-07-14.md`.

Matched-holdout v2 execution and false-positive diagnosis result:

- the canonically published A1 execution completed all eight frozen calls once
  for an exact provider-reported `$0.01408165`; its authorization is consumed
  and its frozen decision is `residual_task_repair_insufficient`;
- the residual arm retained the genuine Case 03 present gap and Case 04 future
  dependency but produced five false-positive records and failed both quiet
  controls;
- Cases 01 and 02 disconfirm paired completion as a general cause: both were
  quiet targets, yet the residual arm emitted governed thresholds and a
  scheduled decision without any genuine companion finding to complete;
- pairing remains a bounded causal rival for Case 03 and Case 04, where a
  legitimate record was accompanied by an unsupported record on the opposite
  surface; the same duplicate pattern also appeared in Case 03 Arm A;
- source-authority failure is directly present in the Case 04
  assistant-proposal record, while governed-machinery boundary failure is the
  repeated quiet-control pattern; no single prompt-wording repair is supported
  by the evidence;
- the completed provider-free diagnosis made zero calls and created no prompt,
  schema, request, fixture, runner, holdout, authorization, or implementation.

The diagnosis decision is `r4_separated_surface_experiment_earned`. This earns
only a separately authorized provider-free design of a paired-versus-separated
task-shape ablation. It does not establish that separation is a repair, and the
future design must retain quiet controls so governed-machinery errors cannot be
mistaken for a pairing effect. See
`docs/conversation-understanding/lolla-r4-residual-false-positive-causal-diagnosis-2026-07-14.md`.

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

The final A2 evidence is canonical through PR #370 at merge
`34d0e1a8f6e80d72622deb59b10a81262344fc85`. Its frozen decision remains
`separated_tasks_ineffective_companions_persist`: both genuine findings
survived, but neither positive-case companion disappeared under separated
generation, and the separated dependency calls continued to misclassify
governed machinery.

The provider-free R4 product and architecture closeout is now complete. Its
decision is:

```text
stop_current_r4_reader_preserve_core_pressure_and_decision_trail
```

Consequences:

- stop the current residual and separated-surface reader architecture;
- preserve its prompts, cases, requests, outputs, and reviews as immutable
  research evidence;
- preserve complete available prose-conversation custody as the authoritative
  source;
- preserve the live four-lane pressure engine, curated mental-model graph,
  constitutional graph-survival portfolio, and apply/reject/park custody as the
  experimental core;
- preserve Decision Work as an optional, derivative, operator-directed sidecar
  and Observatory as its read-only inspection surface;
- do not use the R4 reader as automatic Decision Work semantic supply;
- do not infer product usefulness from mechanical operation.

The immediate operational decision is whether to publish the closeout without
changing its product decision. After publication, the next eligible goal is a
provider-free completed-run artifact-to-Decision-Trail coverage audit. It
should map every desired Decision Trail field to current artifacts and classify
it as deterministic, provisional semantic interpretation, human-review
required, unavailable, private/locator-only, or unsafe. It must not generate a
new semantic read, inspect private archives without explicit scope, mutate a
real archive, call a provider, change runtime, or claim product usefulness.

No A3, replacement call, prompt tweak, task variant, new holdout, model
comparison, integration, or R5 work is authorized. A materially different
reader, real-user sidecar review, and R5 pressure-versus-neutral-control work
remain separate later founder decisions.

See
`docs/conversation-understanding/lolla-r4-product-architecture-closeout-2026-07-14.md`
and `plans/lolla-r4-product-architecture-closeout-plan-2026-07-14.md`.
