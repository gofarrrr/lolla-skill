# Reasoning-process ledger and bounded views goal

Status: active; provider compatibility is isolated, but no July 2026 model/operator pair passes the combined stance-object semantic contract  
Date: 2026-07-11

## Goal

Build and validate a source-linked representation of a multi-turn reasoning
process that lets Lolla inspect how the work was done without evaluating the
final memo, collapsing the process into one quality score, or feeding factual
conversation state directly into the mental-model graph.

The system must preserve broad process evidence in one canonical ledger and
derive bounded, purpose-specific views from that ledger. A future reader must
be able to inspect the evidence behind each interpretation and recover material
that a compact view did not show by default.

## Product boundary

The following objects remain distinct:

1. **Final output or memo** — the recommendation or deliverable. Its quality is
   outside this goal.
2. **Original conversation** — the one-to-one authoritative source.
3. **Canonical reasoning-process ledger** — source-linked observations,
   interpretations, ambiguity, revisions, and terminal dispositions.
4. **Bounded process views** — replaceable projections for a particular
   reasoning question or consumer.
5. **Reasoning abstraction and graph pressure** — a later fact-stripped stage.
   It is not authorized until the process representation passes this goal.

A persuasive memo may have a weak process. A strong process may still reach an
uncertain or wrong conclusion. Lolla must preserve that distinction.

## Governing evidence

This plan responds to four closed findings:

- Full-conversation, one-call-per-family extraction failed across three cases:
  strict constraint recall remained about 0.20–0.22, source strength was
  inflated, positions fragmented, and thread trajectories were lost or falsely
  resolved.
- Small-window harvesting was operationally reliable and recovered 30/32
  reviewed transfer targets across complementary lenses, but expanded a
  fourteen-message conversation into 88–95 overlapping events.
- A fresh global synthesizer over those events failed after one generic repair;
  it recreated overload at fan-in and produced no semantically passing
  end-to-end case.
- Two normalized turn-record designs passed provider-free representation but
  failed model probes. After repair, the compact single reader retained only
  one-third of reviewed moves and threads and one-fifth of reviewed
  claim-plus-strength targets. The three-lens consolidator remained malformed
  in one window and lost the same minority signals.

These results reject the tested implementations, not the hybrid product thesis.
They show that broad custody and compact attention cannot be forced into one
universal model-facing artifact.

## Technical hypothesis

A broad append-only ledger can preserve process evidence without being used as
one giant synthesis prompt. Separate bounded probabilistic views can answer
specific process questions while deterministic code preserves identity,
lineage, budgets, validation, quarantine, and replay.

The views should be scoped by semantic job rather than produced as one universal
summary:

- **position and decision trajectory** — what the working position was, who
  developed or qualified it, and how it changed;
- **exploration and alternatives** — which questions, options, branches, and
  opportunities appeared, were pursued, or were left open;
- **evidence and assumption discipline** — which claims were evidence,
  inference, reported statement, possibility, preference, or concern;
- **uncertainty and unresolved state** — what remained unknown, conditional,
  deferred, contradicted, or capable of reopening the decision;
- **challenge and revision response** — which user, agent, or Lolla pressures
  were considered and whether they changed, guarded, deferred, or failed to
  affect the reasoning.

No deterministic rule may decide that a messy conversational item is relevant,
accepted, resolved, or semantically equivalent. Those remain probabilistic
judgments made with sufficient visible context.

## Required data contracts

### A. Authoritative conversation

- immutable message order, speaker, exact text, and conversation hash;
- stable turn and span identities;
- exact-text retrieval by identity;
- no summary may replace this source.

### B. Canonical process ledger

Every proposed observation must have:

- stable observation and source IDs;
- observation family and prompt/model/version provenance;
- exact source references resolved deterministically;
- the model's semantic interpretation without silent deterministic repair;
- explicit ambiguity or unsupported state;
- terminal custody: admitted, quarantined, merged by a probabilistic step,
  excluded from a view with reason, or failed operationally;
- links to later revisions, contradictions, dispositions, or superseding items;
- zero direct graph eligibility.

The ledger preserves candidates and their fates. Presence in the ledger does not
mean that an interpretation is correct or important.

### C. Bounded process view

Every view must declare:

- the process question it answers and the context it received;
- included ledger IDs and exact source lineage;
- excluded or parked ledger IDs with inspectable dispositions;
- unresolved ambiguities and missing evidence;
- input candidate count, serialized bytes/tokens, and output budget;
- prompt, model, schema, and run identity;
- no overall quality or trust score.

A view may be compact and lossy only because the ledger remains authoritative
and omitted material is recoverable.

### D. Process-evaluation observation

An evaluation statement must use one of:

- `supported` — the cited process evidence supports the statement;
- `mixed` — cited evidence supports materially different readings;
- `unclear` — available evidence cannot resolve the question;
- `not_observed` — the process record contains no support for the behavior.

Every statement must cite ledger items. `Not observed` must not be presented as
proof that the behavior did not occur outside the captured conversation.

## Execution plan

### Phase 0 — Freeze the product and evaluation contract

Status: complete on 2026-07-11. The frozen contract, provider projections,
current-practice check, validators, and 19 focused adversarial tests are in:

- `docs/conversation-understanding/reasoning-process-contract-v0.md`;
- `docs/conversation-understanding/reasoning-process-current-practice-check-2026-07-11.md`;
- `docs/evals/reasoning-process-phase0-contract-v0.json`;
- `engine/system_b/reasoning_process_contracts.py`;
- `tests/test_reasoning_process_contracts.py`.

1. Encode the boundary above in a schema and a short human-readable contract.
2. Define which fields are source observations, probabilistic interpretations,
   deterministic custody metadata, and later process evaluations.
3. Freeze the failure taxonomy, numeric gates, call budget, stop rules, and
   source-review method before any provider call.
4. Check current July 2026 structured-output, prompt-decomposition, provenance,
   and evaluation practices against official model/provider documentation and
   relevant current practitioner or repository evidence. Record adopted and
   rejected practices; do not add a framework merely because it is current.

Exit: contracts validate provider-free and cannot confuse the final memo with
the process record or give deterministic code semantic authority.

### Phase 1 — Build the provider-free canonical ledger

Status: complete on 2026-07-11. The five reviewed sources, 79 harvest events,
55 synthesis records, and 120 scoped family outcomes were imported into five
canonical ledgers with raw records, artifact hashes, original state histories,
exact source lineage, full terminal custody, and zero graph seeds. Evidence:

- `docs/conversation-understanding/reasoning-process-ledger-v1.md`;
- `docs/evals/reasoning-process-phase1-ledger-contract-v1.json`;
- `engine/system_b/reasoning_process_ledger.py`;
- `scripts/evals/build_reasoning_process_phase1_ledger.py`;
- `tests/test_reasoning_process_ledger.py`;
- `research/reasoning-process-phase1-ledger-2026-07-11/`.

The import honestly exposes zero dedicated
`challenge_and_revision_response` observations in the frozen source artifacts.
Phase 2 must preserve that as missingness and cannot manufacture a complete
challenge view. Any provider-free source-review addition requires a prospective
contract rather than a silent expansion of Phase 1.

1. Reuse the existing stable source catalog, typed candidate contracts,
   candidate ledger, and quarantine machinery.
2. Import the five reviewed ambiguous conversations and all existing harvested
   candidates without new calls.
3. Preserve cross-family overlap rather than treating families as exclusive.
4. Add explicit lineage for probabilistic merge, exclusion, revision,
   contradiction, and supersession.
5. Produce per-case fan-out counts and a lossless custody report.

Exit gates across all five cases:

- 100% message and exact-source custody;
- 100% terminal disposition for every imported candidate and failure;
- zero unresolved admitted source references;
- zero direct factual graph seeds;
- all reviewed material present somewhere in the ledger or recorded as a known
  source-review disagreement;
- no deterministic semantic merge, relevance filter, or silent repair.

### Phase 2 — Design bounded, question-specific views provider-free

Status: complete on 2026-07-11 under a revised two-part gate. Phase 1 disproved the assumption
that every intended view already has represented input: the frozen ledgers have
zero dedicated `challenge_and_revision_response` observations. Phase 2 must
therefore establish coverage adequacy before it constructs views.

The completed source-first review found that 11/25 protected targets had any
exact Phase-1 span overlap but only 1/25 was fully represented by an existing
observation. Twenty-four prospective append-only source-review observations
were required to create adequate non-independent development fixtures. This
does not show model failure: the inherited observations were produced for
different earlier jobs. It does show that the Phase-1 ledger cannot replace the
authoritative conversation as the semantic input to the bounded readers.

Phase 2 therefore froze target-blind probe packets that always retain the full
conversation and include the auxiliary Phase-1 ledger only as a complete
all-or-none budget unit. All five current cases include the complete auxiliary
ledger and remain below 16,813 bytes. A real 24-message stress case remains
below 24,000 bytes by omitting its 32-observation auxiliary ledger whole rather
than deterministically selecting a semantic subset. The protected targets and
source-review addenda never enter these probe packets.

Evidence:

- `docs/conversation-understanding/reasoning-process-bounded-views-v1.md`;
- `docs/evals/reasoning-process-phase2-coverage-contract-v1.json`;
- `docs/evals/reasoning-process-phase2-coverage-review-v1.json`;
- `engine/system_b/reasoning_process_views.py`;
- `scripts/evals/build_reasoning_process_phase2_views.py`;
- `tests/test_reasoning_process_views.py`;
- `research/reasoning-process-phase2-views-2026-07-11/`.

#### Phase 2A — Coverage adequacy

1. Freeze source-linked protected targets for every intended process question
   across the five reviewed conversations.
2. Resolve target quotes to exact source spans deterministically.
3. Measure any-family evidence availability separately from semantically usable
   observation coverage.
4. Classify every case/view as ready, partial, or blocked; a zero must remain
   visible.
5. Add missing provider-free source-review observations only through a
   prospective append-only addendum with exact lineage and non-independent-gold
   labeling. Never modify the Phase-1 ledgers in place.

Exit: every protected target is covered by a source-reviewed ledger observation
or remains explicitly blocked with a reason. No provider call and no transcript
keyword rule may manufacture coverage.

#### Phase 2B — Bounded-view construction

1. Build fixture views for the five semantic jobs in the technical hypothesis.
2. Ensure each view receives only context capable of supporting its labels.
3. Measure candidate count and byte/token fan-in independently for every view.
4. Preserve a protected minority/edge set so unusual but source-valid material
   cannot disappear merely to satisfy compactness.
5. Compare view outputs with the broad ledger and the reviewed handoffs.
6. Freeze per-view fan-in budgets from the observed distribution before model
   execution; budgets must cover longer-than-fourteen-message stress fixtures,
   not only the current development cases.

Exit: every reviewed process item is either visible in its applicable view or
has an explicit, recoverable disposition. No single global view receives the
entire 88–95-event ledger.

### Phase 3 — Run one bounded development probe

Status: complete on 2026-07-11 with **material redesign required**. Case 02
was selected mechanically from the four cases whose five protected targets all
required Phase-2 addenda. The target-blind baseline used Gemini 3.1 Flash Lite
through OpenRouter. Two calls passed operational and custody gates; the third
received an OpenRouter 429 rate-limit error and stopped the baseline. Source-
first review found one protected target and one prompt-level minority-signal
omission.

The one allowed generic repair required a chronological full-conversation scan
and up to four materially distinct items. All five calls completed, four were
admitted, and those four recovered their protected targets. Exploration was
quarantined for a non-contiguous ellipsis quote and still omitted the protected
ownership limit. One admitted position item also overclaimed its cited evidence.
The repair therefore finished at 4/5 typed admission, 4/5 protected-target
visibility, 28/29 exact source references, one invalid admitted item, one
source-strength inflation, one context-invisible label, and one critical zero.
No second repair or Phase-4 transfer is authorized.

Evidence:

- `docs/conversation-understanding/reasoning-process-phase3-development-result-v1.md`;
- `docs/evals/reasoning-process-phase3-probe-contract-v1.json`;
- `docs/evals/reasoning-process-phase3-repair-contract-v1.json`;
- `research/reasoning-process-phase3-development-2026-07-11/decision.json`;
- `research/reasoning-process-phase3-development-2026-07-11/result.md`.

1. Select one already-reviewed development case mechanically; do not call it a
   holdout or product-effect test.
2. Run only the minimum probabilistic calls needed to populate the five scoped
   views. Use JSON transport plus unchanged local typed validation, temperature
   zero, no fallback, no automatic retry, and complete call/usage custody.
3. Review source-first before examining polish or narrative coherence.
4. Permit one generic prompt or representation repair only if the failure is
   correctly classified and the repair does not weaken a gate.

Provisional call gate:

- 100% valid source lineage and terminal custody;
- every protected item included or explicitly parked with a grounded reason;
- no source-strength inflation;
- no context-invisible ownership, origin, acceptance, or trajectory label;
- every view remains inside its prospectively frozen fan-in and output budget;
- `unclear` and valid empty outputs remain possible.

### Phase 4 — Prospective transfer and stability

Status: complete with a preserved transfer-gate failure on 2026-07-11. The
failure-derived sentence-alias redesign and relationship-
explicit v2 contracts fixed source custody and support the position, evidence,
uncertainty, and challenge readers on Case 02. The exploration-only local
chronological harvester now also passes the Case-02 development gate: it
recovered the protected `e026/e027` alternative-limit pair, completed all seven
windows, admitted 13 source-supported records, and quarantined one exact prior-
window duplicate through record-level custody. One original 429 remains
preserved beside a separately frozen, cooled operational completion. Evidence:

- `docs/conversation-understanding/reasoning-process-view-specific-development-result-v2.md`;
- `docs/conversation-understanding/reasoning-process-exploration-local-development-result-v1.md`;
- `research/reasoning-process-view-specific-interface-2026-07-11/report.json`;
- `research/reasoning-process-view-specific-v2-2026-07-11/report.json`;
- `research/reasoning-process-exploration-local-terminal-2026-07-11/terminal-result.json`.

The Phase-4 contract mechanically selected Case 05 and Case 01. Because the
validated exploration design decomposes one former global job into seven local
windows, an explicit budget amendment changed the two-case first-attempt count
from ten to twenty-two calls without changing semantic scope. The contract
preserved one OpenRouter 429 and allowed one separately frozen, cooled
operational completion using the identical packet, prompt, schema, model, and
route.

All 22 jobs eventually completed and produced 52 admitted, source-valid records
with zero quarantines. Every semantic dimension was non-empty in both cases.
The protected minority-signal gate nevertheless failed: exact visibility was
1/5 on Case 05 and 4/5 on Case 01. Source review classified the ten targets as
six supported, two partial, and two not observed. Both evidence readers lost
part or all of the protected claim-boundary pair. This is a transfer failure of
global semantic selection, not schema, source-ID, custody, or empty-output
operability. Evidence:

- `docs/conversation-understanding/reasoning-process-phase4-transfer-result-v1.md`;
- `research/reasoning-process-phase4-transfer-design-2026-07-11/contract.json`;
- `research/reasoning-process-phase4-transfer-review-2026-07-11/source-review.json`.
- `research/reasoning-process-phase4-transfer-review-2026-07-11/source-review-correction-v1.json`.

1. Two additional reviewed cases were frozen mechanically and run without
   tuning completed cases.
2. Every first attempt and the separate operational completion were preserved.
3. Stability repeats were not authorized because both transfer cases did not
   pass.
4. The same load-bearing evidence-boundary failure appeared on both cases, so
   the frozen stop rule fired.

Exit: failed. More than one case produced useful bounded records and no critical
dimension was zero, but protected minority relationships did not survive
reliably. The four global selection jobs require material redesign before this
goal can proceed to Phase 5.

### Phase 5 — Evaluate the reasoning process, not the answer

Generate an evidence vector, never a composite badge:

1. exploration and alternative coverage;
2. evidence-versus-assumption discipline;
3. position and decision trajectory;
4. response to challenge, correction, and counterpressure;
5. uncertainty, unresolved matters, and reopen conditions;
6. Lolla pressure disposition when such pressure exists;
7. missing evidence and limits of the assessment.

Each observation must carry its status and citations. Activity counts, token
counts, model calls, number of turns, or number of mental models may be reported
as telemetry but cannot become evidence of reasoning quality.

Exit: a cold reader can distinguish what happened, what Lolla interpreted, what
remains unknown, and why no claim about final-answer correctness follows.

### Phase 6 — Close with an integration decision

Produce one immutable evidence package containing:

- frozen contracts and hashes;
- provider-free and model-backed results;
- call, cost, token, retry, and failure custody;
- source-first review;
- fan-out and fan-in measurements;
- per-view semantic results and case floors;
- unknowns and non-claims;
- a terminal decision: integrate a minimal shadow surface, redesign materially,
  or stop this path.

Only a passing decision may authorize later reasoning-pattern abstraction,
graph-pressure testing, receipt presentation, or runtime integration.

## Scorecard

The goal is evaluated as a vector:

| dimension | evidence required |
| --- | --- |
| source custody | exact message/span validity and hashes |
| candidate custody | every proposal and failure has a terminal state |
| concept coverage | reviewed material survives somewhere in the ledger |
| semantic placement | material appears in a view usable for its question |
| temporal fidelity | introduction, revision, strengthening, and unresolved state remain distinct |
| minority-signal survival | protected edge material is visible or explicitly parked and recoverable |
| bounded fan-in | candidate and token burden is measured and stays inside the frozen contract |
| process-assessment grounding | every assessment cites evidence and admits mixed/unclear/not-observed states |
| stability | passing behavior transfers before repeat claims are made |
| operability | calls, retries, tokens, latency, cost, and preserved failures are complete |

There is no combined score and no “proof of reasoning” badge.

## Stop rules

- No provider calls before Phases 0–2 pass provider-free.
- No weakening of gold, semantic floors, custody, or budgets after seeing output.
- No case-specific examples or prompts.
- No silent source-ID repair, response healing, fallback, or automatic retry.
- No deterministic keywords, rules, or layered gates that infer conversational
  meaning.
- No second generic prompt repair for the same design.
- Stop if compactness repeatedly deletes protected signals.
- Stop if broad capture is merely moved into another overloaded fan-in.
- Stop if a process assessment cannot be supported by the context supplied to
  its task.
- No graph, downstream answer pair, final-memo evaluation, or live runtime call
  under this goal.

## Explicit non-goals

- scoring whether the final memo or recommendation is correct;
- producing a scalar trust, effort, depth, or proof-of-work score;
- proving that more calls or more mental models mean better reasoning;
- graph-value attribution or graph expansion;
- cross-run knowledge-base design;
- organization-level comparison;
- repository gardening or public-release preparation;
- framework, provider, or model migration without a demonstrated need.

## Completion definition

This goal is complete only when:

1. the ledger, bounded-view, and process-assessment contracts exist and pass
   adversarial provider-free tests;
2. the five reviewed cases replay with complete source and candidate custody;
3. one bounded development probe and prospective transfer either pass the
   frozen gates or reach a preserved stop-rule conclusion;
4. the process-evaluation vector is demonstrated without referring to final
   answer quality or issuing a composite score;
5. an immutable evidence package records the result, unknowns, non-claims, and
   next integration or redesign decision;
6. governing documentation and the restart-safe roadmap are updated to match
   the evidenced conclusion.

Success is not defined as forcing the architecture to pass. A well-evidenced
material-redesign or stop decision also completes the goal.

## Current authorization

Phases 0–4 and the view-specific development and transfer experiments are
complete. Phase 4 failed the protected minority-signal gate while passing
source, schema, custody, and non-empty-dimension floors. The first provider-free
chronological-shard representation now passes: 60 packets across five cases,
20/20 protected full-reader targets co-located, maximum packet size 6,013 bytes,
and a nineteen-call/thirty-eight-record ceiling per fourteen-message case when
combined with existing exploration. Current-practice evidence supports smaller
multi-needle jobs but does not prove this shard count is optimal.

The next authorized work is provider-free family-specific prompt, schema,
role-limited context, and record-level custody design. That interface and its
smallest probe are now complete. Chronology recovered the Case-05 and Case-01
evidence targets and the Case-05 direct challenge, but the four-call family
batch failed: position prose did not express its cited trajectory, uncertainty
split one reopen relationship across records, and a second challenge record
reversed semantic roles. The full nineteen-call case is blocked.

The role-specific work is now complete. V2 separately represents position
starting/current/qualification/trajectory meaning, uncertainty
unresolved/reopen/relationship meaning, and challenge
prior-frame/challenge/response/revision/relationship meaning. Evidence remains
byte-equivalent to the passing reference. All 60 prompts and 20 protected
fixtures pass provider-free, seven adversarial outcomes preserve the intended
probabilistic/deterministic boundary, and the then-current regression suite
passed.

One prospectively frozen Case-05 position endpoint probe corrected the prior
missing-current-position failure: all four role meanings and their evidence are
present. It nevertheless failed the frozen source-strength gate because the
model promoted “I want the archive organized first” into “insisted on the
entire archive” and “total archival completion.” The completed case may not be
tuned or retried.

Modal-strength v3 is now complete as a bounded negative experiment. It adds
categorical starting/current force and qualification modalities without scores,
ordinals, deterministic label inference, comparison, or prose keyword gates.
All 60 prompts built, 20/20 reviewed fixtures compiled, non-position interfaces
remained byte-identical to v2, the adversarial gate passed, and 167
reasoning-process tests passed before the call.

One mechanically selected fresh Case-03 position endpoint call was
operationally and structurally successful: two records admitted, zero
quarantined, and estimated cost was $0.00185025. Source review failed. Gemini
classified “I think the final third needs a major re-edit” as a `decision`,
strengthened it to a “firm belief” and “immediate, unilateral assessment,” and
omitted the protected revised-cut possibility plus open-partnership
relationship. A second record showed that one force label cannot cleanly cover
both “I will propose X” and uncertainty about accepting X.

Stance-object v4 is now complete as a bounded operational stop. It separates
belief, proposal/action, intended outcome, acceptance/willingness, and reported
position landscapes inside one compact temporal-role component array. All 60
prompts and 20 reviewed fixtures passed provider-free, nine adversarial
outcomes passed, non-position interfaces remained byte-identical, and 184
reasoning-process tests passed before execution. The schema was reduced from a
6,941-byte three-array draft to one 3,919-byte array.

The single frozen Case-04 request did not reach inference. Google returned HTTP
400 `INVALID_ARGUMENT`; no candidate, compiled record, usage, cost, or semantic
result exists. The exact invalid argument is not exposed. Depth/complexity is a
plausible but unproven cause because v4 adds a nested component evidence array
and reaches depth 11, while the previously served v3 schema was depth 9. The
failed request is preserved and Case-04 may not be repaired or retried.

Stance-object v4.1 is now complete as a second bounded operational stop. It
preserves object-specific semantics on a 3,654-byte depth-9 provider wire using
five index-aligned columns, then deterministically reconstructs normal
components. All 20 legacy and three new reviewed fixtures compiled, 12
adversarial outcomes passed, and 200 reasoning-process tests passed before the
call. Three new fourteen-message cases were frozen before use, and career
transition was selected mechanically by SHA-256.

The single career-transition call again failed with Google HTTP 400
`INVALID_ARGUMENT` before inference. No semantic result exists. A current local
`google-genai` 2.11.0 audit then identified a probable compatibility cause:
native `Schema` rejects inherited `uniqueItems` on the three v2 position
evidence arrays, while the complete v4.1 schema validates after removing only
those keywords. The provider error does not name the field, so this is
high-confidence compatibility evidence rather than provider-confirmed root
cause. The older v3 success does not establish current compatibility.

Stance-object v4.2 is now complete as a third bounded operational stop. It made
only the authorized wire correction: three position `uniqueItems` keywords
were removed while prompts, stance semantics, parallel-column reconstruction,
source custody, validators, and deterministic duplicate rejection remained
unchanged. All 63 prompts and 23 reviewed fixtures passed, the adversarial and
cold-reader gates passed, and current `google-genai` 2.11.0 native `Schema`
validation changed from v4.1 fail to v4.2 pass.

The one frozen community-space request still returned Google HTTP 400
`INVALID_ARGUMENT` before inference. No candidate, compiled record, usage,
cost, or semantic result exists. Therefore `uniqueItems` was a real SDK fault
but not a sufficient provider-side explanation. Depth is also not sufficient.
The exact remaining schema/translation constraint is unknown and no published
exact provider limit identifies it.

Community space is closed. Agency acquisition remains reserved and may not be
used under v4.2. No additional provider, uncertainty/challenge, full-case,
stability, live-skill, graph, final-output, receipt, or runtime call is
authorized. The next bounded development question is provider compatibility
itself: first build a provider-free, one-dimension-at-a-time schema reduction
matrix; only a later prospectively authorized non-semantic compatibility probe
may spend calls. Do not use valuable multi-turn semantic cases until the wire
is known to be served.

The July 2026 model/operator selection goal is now complete. The unchanged
v4.2 schema was served by four non-Google pairs, disproving a universal schema
limit. GLM 5.2/DeepInfra returned empty, DeepSeek V4 Flash/Alibaba came closest
but omitted the visible starting role, DeepSeek V4 Pro/Alibaba repeated the
cross-field defect at higher cost, and MiniMax M3/Parasail returned empty. A
prompt-only v4.3 amendment made the existing role/component invariant explicit
without changing schema or validation; no pair passed source review.

DeepSeek V4 Flash/Alibaba is the low-cost development reference, not a
production selection. Agency acquisition remains reserved. No more model calls
are authorized for the combined contract. The next authorized work is
provider-free decomposition: one semantic role-trajectory reader, separate
per-role stance-object readers, and a deterministic join limited to exact role
and evidence identifiers. This must not introduce keyword gates, semantic
compatibility matrices, graph behavior, or runtime integration.

The provider-free decomposition and its reserved probe are now complete. V1
split the closed monolith into one role-trajectory call and up to three
role-specific stance calls. Seven eligible reviewed fixtures passed locally,
but the one agency-acquisition trajectory call failed: it cited a starting
state while selecting the no-start category, omitted e057 qualification
evidence, truncated two interpretations, and was quarantined. The stop rule
prevented the remaining three calls. Exact route custody passed; total cost was
$0.000273092. The frozen v1 join also falsely labeled the zero-observation join
complete, so v1 is closed.

The prospective role-first v2 repair is provider-free complete. Starting,
current, and qualification are independent jobs; a fourth compact task relates
exact role-record IDs; there is no categorical trajectory label. All eight
reviewed position fixtures replay with 24 admitted role records, eight admitted
relationships, eight complete joins, zero quarantine, a four-call ceiling, a
six-record relation fan-in ceiling, and maximum 4,017-byte user prompt. The
current reasoning-process suite passes 252 tests.

No provider, graph, runtime, downstream reconsideration, or receipt call is
authorized. Every existing reviewed position case has now been exposed. The
next evidence need is a newly frozen, ambiguous multi-turn development case
whose source-first target, budgets, and stop rules are written before any
role-first v2 call.

That new journalism-platform case was then written with its source-first target
and protected e056 qualification before execution. DeepSeek V4 Flash served
all four role-first calls for $0.00085626, but fragmented every role into two
one-alias records, omitted e051 and protected e056, and joined the fragments
into artificial mini-trajectories. After the mandatory problem-class research,
GLM 5.2/DeepInfra ran the unchanged stronger control. It returned empty
starting and qualification roles, split current into two e049-only records, and
correctly blocked the relation call. Estimated cost was $0.00375615;
provider-reported cost was $0.00274815.

Model capacity is not a sufficient explanation and model shopping is stopped.
The leading problem is semantic-contract ambiguity: starting endpoint versus
pre-conversation state, coherent record versus component, and assistant-
introduced process qualification versus user endorsement.

Prospective v2.1 is now provider-free complete. It clarifies those meanings in
the model-visible packet and prompt only. Response schemas, validators, exact
evidence custody, joins, and the four-call ceiling remain unchanged. Nine
reviewed cases replay with 27 role records, nine relationships, nine complete
joins, zero quarantine, and maximum 5,188-byte prompt. No v2.1 provider call is
authorized without another new pre-frozen case. If protected qualification
loss repeats, stop direct structured extraction and reconsider record/object
detection separately rather than adding retries or more model controls.

Continuation evidence:

- `docs/conversation-understanding/reasoning-process-chronological-shards-design-v1.md`;
- `docs/conversation-understanding/reasoning-process-chronological-shards-current-practice-2026-07-11.md`;
- `research/reasoning-process-chronological-shards-2026-07-11/report.json`;
- `research/reasoning-process-chronological-shards-2026-07-11/protected-target-review.json`;
- `docs/conversation-understanding/reasoning-process-chronological-shard-probe-result-v1.md`;
- `research/reasoning-process-chronological-shard-family-batch-run-2026-07-11/source-review.json`;
- `docs/conversation-understanding/reasoning-process-role-explicit-v2-result-2026-07-12.md`;
- `research/reasoning-process-role-explicit-v2-position-probe-2026-07-12/source-review.json`;
- `docs/conversation-understanding/reasoning-process-modal-strength-v3-result-2026-07-12.md`;
- `research/reasoning-process-modal-strength-v3-probe-2026-07-12/source-review.json`;
- `docs/conversation-understanding/reasoning-process-stance-object-v4-result-2026-07-12.md`;
- `research/reasoning-process-stance-object-v4-probe-2026-07-12/operational-review.json`;
- `docs/conversation-understanding/reasoning-process-stance-object-v41-result-2026-07-12.md`;
- `research/reasoning-process-stance-object-v41-probe-2026-07-12/compatibility-diagnosis.json`;
- `docs/conversation-understanding/reasoning-process-stance-object-v42-result-2026-07-12.md`;
- `research/reasoning-process-stance-object-v42-2026-07-12/google-schema-preflight.json`;
- `research/reasoning-process-stance-object-v42-probe-2026-07-12/compatibility-diagnosis.json`;
- `docs/conversation-understanding/reasoning-process-model-operator-selection-result-2026-07-12.md`;
- `research/reasoning-process-model-operator-selection-2026-07-12/terminal-review.json`;
- `docs/conversation-understanding/reasoning-process-structured-output-problem-class-research-2026-07-12.md`;
- `docs/conversation-understanding/reasoning-process-position-decomposition-result-2026-07-12.md`;
- `research/reasoning-process-position-decomposition-probe-2026-07-12/source-review.json`;
- `docs/conversation-understanding/reasoning-process-position-role-first-v2-result-2026-07-12.md`;
- `research/reasoning-process-position-role-first-v2-2026-07-12/report.json`;
- `docs/conversation-understanding/reasoning-process-role-first-fragmentation-problem-class-2026-07-12.md`;
- `research/reasoning-process-position-role-first-v2-probe-2026-07-12/source-review-deepseek.json`;
- `research/reasoning-process-position-role-first-v2-glm-control-2026-07-12/source-review.json`;
- `docs/conversation-understanding/reasoning-process-role-first-model-control-result-2026-07-12.md`;
- `docs/conversation-understanding/reasoning-process-position-role-first-v21-result-2026-07-12.md`;
- `research/reasoning-process-position-role-first-v21-2026-07-12/report.json`.

## Role-first v2.2 terminal state — 2026-07-12

The v2.1 succession probe preserved protected qualification e056 but
quarantined that record because its parallel component arrays had unequal
lengths. V2.2 replaced those columns with nested atomic component objects while
keeping v2.1 semantics, relation behavior, deterministic boundaries, and call
ceilings unchanged. Ten reviewed cases and ten local/adversarial tests passed
provider-free.

A genuinely new cooperative case was source-first frozen and run once. All
four DeepSeek V4 Flash/Alibaba calls, all admissions, and the exact-ID join
passed for $0.000991064. Protected e056 irreversibility and assistant ownership
survived, so the protected-loss stop condition did not repeat.

The complete semantic gate nevertheless failed. The current role absorbed the
unresolved e052 qualification; starting components flattened expressed user
attitudes to `reported_without_endorsement`; and the relationship dropped some
specific expansion and irreversible-exit meaning. Therefore v2.2 is retained
as the structural reference but graph/runtime integration remains blocked.

The next bounded goal is provider-free: clarify the role boundary between a
working position and an unresolved matter, and clarify stance-expression
treatment, without deterministic keyword gates, semantic classification,
chronological gating, retries, or model shopping. Only after local gates pass
may a genuinely new transfer case authorize another bounded call.

Continuation evidence:

- `docs/conversation-understanding/reasoning-process-position-role-first-v22-result-2026-07-12.md`;
- `research/reasoning-process-position-role-first-v22-probe-2026-07-12/source-review.json`.

## Role-first v2.3 terminal state — 2026-07-12

V2.3 made the current/qualification boundary and source-speaker expression
meaning explicit in the model-visible packet only. Eleven reviewed cases and
the adversarial gates passed provider-free. The new museum/AI-license source
and protected target were frozen before execution.

The fixed DeepSeek V4 Flash/Alibaba route completed four calls and one exact-ID
join for $0.001047746. Starting expression ownership improved, and protected
qualification e040 survived with assistant ownership. The core role-boundary
failure repeated: unresolved e036 was included in current as well as
qualification despite the explicit instruction.

Prompt-only refinement is closed. Do not retry, tune the completed case, shop
models, subtract aliases deterministically, or integrate graph/runtime. The
next bounded provider-free decision is between limited probabilistic cross-role
context and one compact semantic reconciliation task. Judge both against call
budget, contamination risk, legitimate mixed-meaning aliases, evidence
custody, speaker ownership, and preservation of disagreement.

Continuation evidence:

- `docs/conversation-understanding/reasoning-process-position-role-first-v23-result-2026-07-12.md`;
- `research/reasoning-process-position-role-first-v23-probe-2026-07-12/source-review.json`.

## Paired role-first v2.4/v2.4.1 terminal state — 2026-07-12

Independent current and qualification readers were replaced by one paired
semantic allocation task. Starting remains separate and relationship fan-in
uses exact IDs, reducing the maximum from four calls to three. Shared aliases
remain legal only as a model-interpreted distinction between meanings; code
does not enforce exclusivity or subtract evidence.

V2.4 passed 12-case provider-free representation and adversarial gates. Its
new registry case produced source-faithful paired semantics but failed
admission because redundant envelope statuses said `not_found` beside populated
supported records. No retry occurred. V2.4.1 removed only those provider status
fields and derives bookkeeping mechanically from role-labeled records.

The new housing-retrofit v2.4.1 probe passed all three calls and exact joining
for $0.000959574. It correctly separated conditional approval and unresolved
opt-out meanings within shared e034 and preserved protected path dependence.
This validates the paired architecture at development level. It does not prove
production semantic quality: force, category, evidence precision, allocation-
note fidelity, and prose-length defects remain.

Next work is provider-free corpus-level evaluation. Keep allocation,
qualification survival, ownership, evidence precision, modal force, category
precision, and relationship preservation separate; do not collapse them into a
score. Use that evidence to decide between another transfer call and read-only
shadow graph integration. Neither is currently authorized.

Continuation evidence:

- `docs/conversation-understanding/reasoning-process-position-role-first-v24-v241-result-2026-07-12.md`;
- `research/reasoning-process-position-role-first-v241-probe-2026-07-12/source-review.json`.

## Paired corpus evaluation terminal state — 2026-07-12

The non-scalar corpus review compares v2.2, v2.3, v2.4, and v2.4.1 across
central allocation, protected qualification, ownership, evidence precision,
force, category precision, and relationship preservation. All evidence paths
are checked and no provider, evaluator, graph, or runtime call was made.

Both independent-reader cases fail central allocation. Both paired-reader
cases pass, including legitimate shared-alias meanings. Protected qualification
and material ownership survive in all four. Evidence, force, and category
precision remain partial across every architecture. V2.4.1 supplies the first
fully operational paired relationship pass.

The next selected experiment is read-only shadow graph impact, not another
transfer call. Compare source-first and preserved provider role records first
at the graph-input boundary, then under a separate frozen contract compare
candidate/embedding selection. Do not run reconsideration, mutate runtime,
write receipts, score one path automatically, or authorize production.

Continuation evidence:

- `docs/conversation-understanding/reasoning-process-paired-corpus-evaluation-result-2026-07-12.md`;
- `research/reasoning-process-paired-corpus-evaluation-2026-07-12/validation-report.json`.

## Graph-impact shadow terminal state — 2026-07-12

The shadow did not feed role prose directly to routing. Codex-assisted
provisional interpretations first produced controlled fact-free reasoning-
pattern packets. Source-first and provider projections matched in both paired
cases, as did deterministic seed models and one-hop neighborhoods. A missing-
reversal ablation removed `commitment-bias`, `premortem`, and
`sunk-cost-fallacy`, so the shadow detects the protected mechanism.

The repository graph loader expects `build/relationship_graph.json`, while
this checkout carries `data/relationship_graph.json`. The shadow loads the
declared data artifact explicitly and fails closed if empty; runtime was not
changed.

Current official OpenAI documentation confirms the existing
`text-embedding-3-large` 3,072-dimensional contract. A typed, fact-free
shadow adapter and one batch request embedded only two controlled projection
strings. No activation tiebreaker fired; embedding did not change selection.

Conditional result: observed paired-extraction noise does not alter graph
pressure after faithful abstraction. The automatic abstraction bridge remains
unproven. Next work is provider-free role-record-to-pattern contract design,
then a bounded source/provider invariance probe with an ablation control. No
production graph integration, reconsideration, runtime mutation, or receipt
work is authorized.

Continuation evidence:

- `docs/conversation-understanding/reasoning-process-graph-impact-shadow-result-2026-07-12.md`;
- `research/reasoning-process-graph-impact-shadow-2026-07-12/impact-review.json`.
