# Lolla Reasoning Preservation Core Vision

Date: 2026-05-14

Status: research control document. This does not promote runtime behavior,
mutate `SKILL.md`, mutate `HOW_IT_WORKS.md`, change default `/lolla` runs, add a
Bevelin lane, or change the canonical knowledge base.

## Purpose

This is the re-entry document for the Bevelin / Lane 1 / Step 6 / context
engineering work.

Future sessions should start here before reopening the whole research pile.
This file preserves:

- where we currently stand;
- what we already decided;
- what evidence supports those decisions;
- what is parked;
- what remains open;
- what the next research loop should test;
- which deeper docs to read for each question.

The goal is to stop rediscovering the same ideas every session.

Current decision register:

- `research/lolla-big-picture-decision-register-2026-05-14.md`
- `research/pre-step6-cognitive-worker-system-plan-2026-05-16.md`
- `research/pre-step6-comparison-subagent-readout-2026-05-16.md`
- `research/pre-step6-handoff-best-practices-as-of-2026-05-16.md`
- `research/pre-step6-raw-artifact-consumption-discipline-2026-05-16.md`
- `research/pre-step6-raw-artifact-consumption-readout-2026-05-16.md`
- `research/meta-reasoning-corpus-question-bank-2026-05-15.md`
- `research/post-lane-inquiry-card-vision-2026-05-15.md`
- `research/provider-use-operating-structure-2026-05-15.md`
- `research/lane1-reasoning-bridge-subagent-slice-readout-2026-05-15.md`
- `research/subagent-cognitive-worker-architecture-vision-2026-05-15.md`
- `research/subagent-cognitive-worker-contract-slice-2026-05-15.md`
- `research/subagent-cognitive-worker-live-replay-readout-2026-05-15.md`
- `research/subscription-orchestrator-handoff-local-test-readout-2026-05-15.md`
- `research/source-gate-first-survivor-inspection-2026-05-14.md`
- `research/pre-step6-bevelin-candidate-shift-plan-2026-05-14.md`
- `research/pre-step6-candidate-shift-schema-slice-2026-05-14.md`
- `research/pre-step6-manual-lane1-handoff-dry-run-2026-05-14.md`
- `research/pre-step6-openrouter-candidate-shift-dry-run-2026-05-14.md`
- `research/pre-step6-subagent-candidate-shift-dry-run-2026-05-14.md`
- `research/pre-step6-subagent-candidate-shift-dry-run-v2-2026-05-14.md`
- `research/pre-step6-subagent-candidate-shift-expansion-dry-run-2026-05-14.md`
- `research/pre-step6-subagent-candidate-shift-consumption-probe-2026-05-14.md`
- `research/pre-step6-subagent-candidate-shift-check-only-probe-2026-05-14.md`
- `research/pre-step6-subagent-candidate-shift-check-only-strict-probe-2026-05-14.md`
- `research/pre-step6-subagent-candidate-shift-strict-control-ablation-2026-05-14.md`
- `research/step6-source-discipline-rule-slice-2026-05-14.md`
- `research/step6-source-discipline-prompt-only-probe-2026-05-14.md`
- `research/step6-source-discipline-refined-prompt-only-probe-2026-05-14.md`
- `research/step6-source-discipline-runtime-placement-slice-2026-05-14.md`
- `research/step6-source-discipline-runtime-placement-probe-2026-05-14.md`
- `research/step6-provenance-revision-packet-slice-2026-05-14.md`
- `research/step6-provenance-clean-renderer-probe-2026-05-14.md`
- `research/step6-provenance-audit-passed-decision-comparison-2026-05-14.md`
- `research/step6-reviewer-smoothness-bias-audit-2026-05-15.md`
- `research/step6-grounded-practical-force-principle-2026-05-15.md`
- `research/step6-grounded-practical-force-card-provider-strategy-2026-05-15.md`
- `research/step6-card-consumption-ablation-readout-2026-05-15.md`
- `research/step6-card-consumption-operational-gate-followup-2026-05-15.md`
- `research/step6-central-gate-card-consumption-readout-2026-05-15.md`
- `research/lolla-judgment-learning-loop-2026-05-14.md`

## One-Screen Current Position

Lolla is not trying to make deterministic code reason better than an LLM.

The system works because each layer has a different job:

- LLMs do cognition: detect, localize, interpret, argue, reject, defer, and
  translate.
- Embeddings improve recall and vocabulary bridging, but do not decide truth.
- Deterministic code preserves custody: source identity, routing, caps, schema,
  validation, traceability, telemetry, and public/private hygiene.

The main current bottleneck is not lack of more labels or another lane.

The bottleneck is reasoning preservation:

- useful pressure can be selected by a lane;
- routed to mental models or V60 material;
- rendered into cards;
- and still lose value if the later agent receives only labels, names, or
  generic caution instead of case-local pressure.

Bevelin's best role is not as a new taxonomy. His best role is interpretation
grammar over already-selected pressure:

- what is the real issue;
- who is acting and what reward, fear, pain, status, or relief matters to them;
- what yardstick or denominator is missing;
- what alternative is being displaced;
- what would disprove the conclusion;
- what happens if the conclusion is wrong;
- what goes wrong if this model is forced.

The current best direction is:

> Keep the Munger tendency spine stable. Use Bevelin to make selected pressure
> more interpretable, source-bound, and useful to the final reasoning agent.

The newest corpus direction is broader than Bevelin:

> Ask selected books about the process of thinking itself: how to form better
> questions, build evidence gates, set calibration boundaries, compress rich
> cognition, decide what to set aside, and choose when OpenRouter or subagents
> are worth using.

This is not a new knowledge-base ingestion project. It is a research question
bank for improving the system's reasoning process.

Important correction:

> The main inquiry layer should not run before Lolla has produced
> differentiated findings. It should run after lanes, retrieval, selected
> pressure, and source custody, when questions can be about what the system
> actually found.

Current priority correction:

> The question corpus should wait. The immediate architecture problem is how to
> give Claude Code, or any future orchestrator, only relevant cognitive pressure.
> The latest evidence says to test raw `reasoning_artifact.v1` consumption
> discipline before building bundle or worker machinery. Subagents remain a
> bounded worker-as-tool research option, not a true handoff or runtime default.

Latest live replay correction:

> The worker/dossier contract can execute locally, but OpenRouter should not be
> treated as the final consumer in operational or legal-adjacent cases. In the
> first three replays, worker packets were valid, while final consumption
> reintroduced serious unsupported claims in parenting and whistleblower. This
> supports the provider split: OpenRouter for narrow work and ablations;
> high-context reasoners/subagents for final synthesis or quality review.

Product-cost correction:

> Lolla is for people already working inside Claude Code, Codex, or another
> high-context orchestrator. The system should respect that subscription-first
> reality. OpenRouter/API calls should be used only when they create a narrow,
> schema-bound artifact that prevents larger context bloat later, enables
> controlled prompting, or supplies a focused audit. Do not spend API tokens on
> work the orchestrator is already better positioned to do.

Local-test correction:

> Before touching `SKILL.md`, prove the handoff locally. The current safe test
> shape is a small `orchestrator_handoff_pack.v1` that references the full
> conversation by path, carries only critical source anchors and a compact
> dossier, and lets Claude Code/Codex do the final reasoning. The first
> parenting test fixed the OpenRouter final-consumer age/actor error, but this
> is not promotion evidence yet.

Latest Lane 1 bridge correction:

> The most promising current Bevelin placement is a source-bound bridge between
> existing Lane 1/V60 outputs and Step 6. Bevelin is used as reasoning
> discipline, not content: evidence gate, calibration boundary, sequence of
> use, and set-aside condition. A local subagent slice produced three bridge
> cards across real-estate and oncologist artifacts. One first-run card failed
> deterministic validation for being too long; after prompt compression, all
> three cards validated. This proves the contract is plausible, not that final
> answers improve.

2026-05-16 current preferred research path:

> Test raw `reasoning_artifact.v1` consumption discipline first. Keep live lanes
> and V60 unchanged. Let deterministic code prepare source-grounded, capped
> private artifacts; let Step 6 arbitrate, reject, relax, or use them. Subagents
> remain bounded worker-as-tool candidates only after admission, and
> `reasoning_bundle.v1` is an optional challenger only if raw artifacts create
> real clutter. OpenRouter remains secondary for strict JSON audits, cheap
> ablations, and narrow repeatable checks. No product docs or runtime behavior
> change until promotion evidence exists.

## Decisions Already Made

### 1. No Bevelin Lane 1.5 For Now

Decision: parked.

Reason:

- Bevelin overlaps too much with the current Munger tendency spine.
- The differentiated Bevelin material is mostly calibration, boundary, and
  interpretation material.
- A separate lane would add brand and architecture complexity without enough
  differentiated signal.

Primary docs:

- `research/bevelin-only-tendency-map-2026-05-12.md`
- `research/bevelin-munger-fit-audit-2026-05-12.md`
- `research/bevelin-canonical-mental-model-map-2026-05-12.md`

### 2. Do Not Mutate The Canonical Knowledge Base

Decision: no canonical KB mutation from Bevelin during this research phase.

Reason:

- The canonical corpus has a reviewed distribution.
- Adding one new source after the fact can over-promote it.
- If the source was not in the original corpus process, do not quietly pretend
  it was evenly distributed.

Allowed:

- research-only maps;
- off-by-default local candidate artifacts;
- prompt interpretation experiments;
- mental-model scope audits that propose future review work.

Not allowed yet:

- default graph changes;
- public Bevelin labels;
- new Bevelin tendency IDs;
- hidden KB mutation.

Primary docs:

- `research/bevelin-canonical-mental-model-map-2026-05-12.md`
- `research/lane1-bevelin-handoff-artifact-2026-05-13.md`

### 3. Bevelin Can Enrich Munger, But Carefully

Decision: keep Munger IDs. Use Bevelin to sharpen activation language and
boundaries under existing tendencies.

Candidate areas:

- Twaddle: say-something syndrome.
- Inconsistency-Avoidance: status quo and do-nothing as active choice.
- Social-Proof: inaction as social proof.
- Reward and Punishment: immediate reward versus delayed cost.
- Availability: missing information, unseen denominator, non-events, abstract
  costs.
- Reason-Respecting: story closure and believe-first dynamics.
- Doubt-Avoidance: action or belief as uncertainty relief.
- Contrast-Misreaction: first frame, anchor, or reference point hiding the
  absolute standard.

Guardrails:

- add evidence handles, not stricter gates;
- preserve useful recall from thin conversations;
- avoid turning every omission into a bias;
- include "do not fire when" boundaries;
- evaluate downstream usefulness, not merely more picks.

Primary docs:

- `research/bevelin-munger-fit-audit-2026-05-12.md`
- `research/lane1-bevelin-enrichment-local-rollup-2026-05-12.md`
- `research/lane1-bevelin-supervised-research-loop-readout-2026-05-14.md`

### 4. Source Evidence Must Actually Reach The Reasoning Agent

Decision: preserving source evidence in the artifact is not enough. It must be
rendered where Step 6 or a future agent can use it.

Evidence:

- Earlier source-bound artifacts improved when `source_evidence` was actually
  rendered to the Step 6-style consumer.
- More abstract or prettier interpretations were often downgraded by stricter
  judging.
- Exact evidence pins alone did not beat the current full source-evidence
  renderer.

Current local best:

- full deterministic source-evidence rendering.

Parked:

- `source_pin` as runtime/default candidate.

Kept:

- `source_pin` as off-by-default diagnostic renderer and negative evidence.

Primary docs:

- `research/reasoning-preservation-doctrine-2026-05-13.md`
- `research/lane1-bevelin-source-pin-shaping-readout-2026-05-14.md`
- `research/lane1-bevelin-source-evidence-withheld-and-carry-source-readout-2026-05-13.md`
- `research/lane1-bevelin-source-specific-handle-readout-2026-05-13.md`
- `research/candidate-shift-source-preservation-repair-readout-2026-05-14.md`
- `research/candidate-shift-source-use-adjudication-readout-2026-05-14.md`
- `research/candidate-shift-adjudicated-source-use-repair-readout-2026-05-14.md`

### 5. Do Not Add Bevelin Directly To Step 6 As Prompt Bloat

Decision: blocked.

Reason:

- Step 6 is already the heaviest reasoning step.
- It holds full user context, original advice, lane pressure, anchor treatment,
  V60 chunks, private ledger thinking, public prose, hygiene, and voice.
- Adding "also think with Bevelin" increases attention competition.

Better direction:

- prepare smaller candidate pressures before Step 6;
- preserve source, evidence gate, consequence, and risk-if-forced;
- let Step 6 synthesize, argue, accept, reject, defer, or translate.

Primary docs:

- `research/step6-decomposition-red-team-2026-05-14.md`
- `research/lolla-context-engineering-lessons-2026-05-14.md`
- `research/lolla-architecture-bottleneck-audit-2026-05-14.md`

### 6. Sub-Agents Are A Research Candidate Before Step 6, Not A Decided Runtime Change

Decision: keep local, do not promote yet.

Current product shape:

- Step 6 writes the updated position.
- Step 6b persists answer and V60 ledger.
- Step 7 pressure-check sub-agents run after Step 6b.
- Step 8 compares Step 6 against their outputs.

Potential research variant:

- run sub-agents before Step 6;
- change their job from "check Step 6" to "prepare candidate shifts";
- each sub-agent receives one narrow lane context;
- each returns a compact candidate packet;
- Step 6 waits, then synthesizes from full user context plus candidate packets.

Important:

- do not move current Step 7 earlier as-is;
- current Step 7 asks "what did Step 6 miss?";
- pre-Step6 agents must instead ask "what should Step 6 seriously consider?"

Latest ablation:

- strict check-only subagent candidate checks previously produced 2 real wins
  against a weaker control;
- when the deterministic control received the same strict source-discipline
  rule, both fair cases tied 9 vs 9;
- the extra subagent checks did not show clear decision-quality lift beyond the
  stricter prompt rule;
- this weakens the runtime case for a pre-Step6 subagent layer;
- the stronger surviving lesson is the strict private use rule: do not add new
  concrete categories unless they are present in the conversation or source
  evidence.

Current implication:

- keep subagents for fresh-context research audits, red-team checks, and
  comparisons;
- do not add a pre-Step6 subagent runtime layer until it beats strict
  prompt-only controls across multiple case families;
- the standalone research helper for that rule is now
  `build_step6_source_discipline_rule(...)`.
- first prompt-only probe on two non-Availability cases is mixed: strict source
  discipline won Social Proof 10 vs 8 but lost Twaddle 8 vs 9.
- refined prompt-only probe on three broader historical/withheld cases was
  positive: refined source discipline won 3/3, removed decision-relevant
  unsupported precision from the refined variants, and preserved useful answer
  movement.
- a small default-off runtime-placement hook now exists for archived-case
  testing:
  `--revision-source-discipline-rule-file`.
- runtime-shaped fixed-card testing was mixed-negative: the rule helped
  decision interpretation but did not solve grounding, and raw source context
  made the answer worse.
- a provenance-shaped revision packet contract now exists; it separates user
  facts, assistant-draft claims, audit pressures, and concrete claims to verify
  or soften.
- the producer/consumer probe worked as internal custody but exposed patch
  machinery, so a clean renderer was added as a research-only follow-up;
- the clean renderer improved readability and removed visible machinery, but
  still showed `precision_rebound_in_clean_rendering` and then
  `certainty_rebound_after_numeric_precision_repair`;
- a focused post-render audit now exists; v1 was too lenient, while the
  hardened v2 audit correctly returned `revise_material` for the modal-guard
  renderer output;
- audit-driven clean revision then passed the hardened re-audit on the
  real-estate case;
- decision-quality comparison then preferred the audit-passed answer over the
  prior grounded-draft and deterministic-control variants on that same case;
- broader parenting repeat then exposed a too-narrow claim-type contract,
  repaired it with generic non-financial claim types, and completed the full
  packet/patch/render/audit/revision/re-audit/comparison sequence;
- the parenting audit-passed answer also won decision comparison, 9 vs 8 vs 6,
  but the run cost 35,390 tokens;
- whistleblower / institutional-risk repeat passed the first post-render audit
  without targeted revision and won decision comparison 9 vs 8 vs 7 at 24,640
  tokens;
- current next test should package the same sequence as a reusable
  off-by-default research harness and inspect cost, not add a new conceptual
  layer.

Primary docs:

- `research/step6-decomposition-red-team-2026-05-14.md`
- `research/pre-step6-bevelin-candidate-shift-plan-2026-05-14.md`
- `research/pre-step6-subagent-candidate-shift-strict-control-ablation-2026-05-14.md`
- `research/step6-source-discipline-rule-slice-2026-05-14.md`
- `research/step6-source-discipline-prompt-only-probe-2026-05-14.md`
- `research/step6-source-discipline-refined-prompt-only-probe-2026-05-14.md`
- `research/step6-source-discipline-runtime-placement-slice-2026-05-14.md`
- `research/step6-source-discipline-runtime-placement-probe-2026-05-14.md`
- `research/step6-provenance-revision-packet-slice-2026-05-14.md`
- `research/step6-provenance-clean-renderer-probe-2026-05-14.md`
- `references/sub-agent-prompts.md`
- `SKILL.md`
- `HOW_IT_WORKS.md`

### 7. Product Docs Should Not Carry Experimental Claims Yet

Decision: do not put this research into product docs until promoted.

Reason:

- `SKILL.md` and `HOW_IT_WORKS.md` are product/runtime documentation.
- This work is still research.
- Product docs must describe stable behavior, not experiments.

Known doc mismatch to resolve before promotion:

- `SKILL.md` says Step 7 pressure-check sub-agents launch only after Step 6b and
  V60 ledger finalization.
- `HOW_IT_WORKS.md` still describes the older timing where sub-agents launch
  before Step 6 in the background.

This mismatch is a blocker before changing runtime architecture.

Primary docs:

- `research/step6-decomposition-red-team-2026-05-14.md`
- `SKILL.md`
- `HOW_IT_WORKS.md`

### 8. Source Detail Is Pressure, Not Truth

Decision: do not promote the current post-Step6 source-preservation repair pass.

Reason:

- It reduced source omissions in some runs.
- But it also over-preserved weak source details, revived invented thresholds,
  or worsened source omissions depending on prompt wording.
- The failure is not "source details are useless." The failure is that a single
  repair call is trying to notice omissions, decide whether the omitted detail
  should be used, and rewrite the answer.

Important distinction:

- source omission means useful pressure may have been lost;
- it does not mean the omitted detail is true;
- a Lane 1 source detail may need to be preserved, converted into a question,
  converted into a gate, held privately, or set aside.

Next research direction:

- keep the narrow LLM source-use adjudicator as local research machinery;
- keep deterministic code limited to custody, schema, routing, validation, and
  receipts;
- do not add another repair prompt until the evaluation conflict is understood;
- require direct comparison against deterministic carry-detail and manual
  overclaim reads before promotion.

Current adjudication evidence:

- the first source-use adjudication slice validated the narrower object shape;
- v2 adjudicated 3 comparable withheld cases and skipped the unsupported
  control;
- it surfaced overclaim risk explicitly;
- but v2 still leaned toward preserving or gating every material detail;
- v3 made `set_aside` and `hold_private` real choices, setting aside the
  unsupported real-estate certainty and PhD base-rate/silent-loser claims while
  preserving only the safer smart-hybrid framing;
- adjudicated repair v2 improved against unrepaired source-gate-first but still
  lost against deterministic carry-detail;
- the repair slice exposed an evaluation conflict: strict judges often reward
  concrete thresholds, while grounding diagnostics penalize unsupported
  precision;
- the grounded/unit judge slice made this sharper: even when the judge lists
  unsupported precision, it may still reward the answer containing it;
- current decision: keep local, do not promote, and decompose evaluation before
  another rewrite slice.

Primary docs:

- `research/candidate-shift-source-preservation-repair-readout-2026-05-14.md`
- `research/candidate-shift-source-use-adjudication-readout-2026-05-14.md`
- `research/candidate-shift-adjudicated-source-use-repair-readout-2026-05-14.md`
- `research/candidate-shift-packet-evidence-synthesis-2026-05-14.md`
- `research/candidate-shift-handoff-research-plan-2026-05-14.md`

## Architecture We Are Optimizing Toward

The desired shape is not "more deterministic intelligence."

The desired shape is better reasoning transport:

```text
conversation
  -> LLM lane detection and interpretation
  -> embeddings as additive recall where appropriate
  -> deterministic custody, caps, validation, and artifact trails
  -> relevance assembly for narrow reasoning_workpack.v1 tasks
  -> subagent cognitive workers where judgment is worth the cost
  -> compact source-backed reasoning_artifact.v1 outputs
  -> reasoning_bundle.v1 map of pressure / duplicate / conflict / discard / boundary
  -> Step 6 final LLM synthesis with freedom to use, reject, defer, or translate
```

The final agent must remain a reasoner, not a stenographer.

Sub-agents, OpenRouter calls, V60 chunks, Lane 1 findings, anchors, frame
pressure, strict source-discipline rules, post-lane inquiry questions, and gap
questions are all candidates. They are not commands.

Do not solve a prompt-discipline problem by adding an agent layer. First make
the final reasoner source-disciplined. Only add the agent layer if it beats that
cleaner control. If subagents are added, they must be cognitive workers with
narrow workpacks and compact outputs, not a larger after-check committee.

Narrow workpacks still need a shared understanding of the conversation. Each
worker should get a small situation brief with the user question, decision
situation, live constraints, available lane artifacts, and the reason this
worker exists. Then it gets only the source excerpts and artifacts needed for
its local question.

This keeps the boundary clean:

```text
shared situation brief = relevance to the whole conversation
reasoning_workpack.v1 = focused reasoning task
reasoning_artifact.v1 = compact worker/lane pressure
Reasoning Bundle = map of pressure, conflict, duplicate, discard, and boundary
Step 6 = final cognition and public answer
```

If the shared brief is missing, workers risk producing irrelevant fragments. If
the local workpack is too large, workers become another bloated Step 6.

The system wins when the final answer becomes more accurate, sharper, more
honest, and more decision-useful while public prose remains free of machinery.

## OpenRouter Versus Claude Sub-Agents

### Subscription-First Provider Budget

Assume the user is already paying for the main coding/reasoning environment.

That means the system should not casually add paid API calls just because they
are easy to script.

Default posture:

```text
main orchestrator subscription = high-context synthesis and final judgment
OpenRouter/API = narrow controlled artifact when the contract justifies it
deterministic code = custody, validation, caps, receipts
```

Use OpenRouter when the API boundary gives us something specific:

- strict JSON;
- repeatable schema-bound output;
- cheap parallel ablation;
- small candidate pressure;
- focused source/overclaim audit;
- artifact generation that reduces later prompt bloat.

Do not use OpenRouter for broad synthesis just to avoid thinking with the
orchestrator. That burns tokens and usually produces weaker context handling.

### OpenRouter Is Best For

- narrow tasks;
- schema-bound outputs;
- repeatable checks;
- parallelizable calls;
- source-constrained interpretation;
- cheap candidate generation;
- "produce a possible Bevelin-style gate for this one selected finding."

OpenRouter is not the right owner for:

- final answer synthesis;
- deciding the whole human situation;
- fusing all lanes, V60, user nuance, and product voice;
- iterative repair of weak final answers.

### Claude Sub-Agents Are Best For

- stronger reasoning in clean context;
- one lane or one angle at a time;
- independent dissent;
- compact candidate-shift generation;
- asking whether a finding creates a real decision movement or only generic
  caution.

Claude sub-agents are not the right owner for:

- writing the final answer without full conversation context;
- resolving all lanes in isolation;
- replacing the main orchestrator;
- producing committee prose.

## Candidate Packet Shape

This is the working unit for the next experiment.

```text
CandidateShiftPacket
- source_ref
- source_kind
- source_evidence
- proposed_shift
- why_it_may_matter
- evidence_gate
- consequence_if_ignored
- risk_if_forced
- recommended_route
- confidence_or_uncertainty
- set_aside_reason_if_weak
```

Rules:

- no new findings without a source finding;
- no public Bevelin labels;
- no tendency remapping;
- no final answer prose from the packet;
- every packet must include both best plausible use and risk if forced;
- Step 6 must be allowed to reject the packet.

The newer central-gate card is an even smaller survivor candidate for Step 6
handoff:

```text
CentralGateCard
- source_basis
- central_evidence_gate
- central_calibration_boundary
- central_sequence_or_stop_rule
- set_aside_reason
- recommended_use
```

The meta-reasoning corpus work should test whether this shape is enough, too
small, or the wrong compression boundary.

The post-lane inquiry card is a separate research object:

```text
PostLaneInquiryCard
- central_question
- linked_pressure_or_lane
- why_it_matters
- missing_fact_or_denominator
- evidence_gate
- alternative_frame_or_disconfirmation
- overreach_warning
- answer_now_or_ask_user
- user_facing_question_if_blocking
- private_use_instruction
```

It should be generated from selected lanes, retrieved chunks, and source
evidence, not from the raw conversation alone. Its job is to ask the question
that controls how selected pressure should be used, set aside, or translated.

The first worker/dossier slice used two additional research-only objects:

```text
CognitiveWorkpack
- workpack_id
- work_type
- decision_situation
- selected_lane_or_pressure
- source_evidence
- relevant_chunks
- known_constraints
- forbidden_moves
- output_contract

CognitionDossier
- central_pressure
- central_question_or_gate
- strongest_alternative_frame
- source_overclaim_boundary
- set_aside_notes
- final_reasoner_instruction
```

Those names are now historical scaffolding. The current favored family is:

```text
reasoning_workpack.v1 -> reasoning_artifact.v1 -> reasoning_bundle.v1
```

The lesson survives: the orchestrator should receive a compact indexed handoff,
not raw worker output.

## Next Research Loop

Do not promote runtime behavior yet.

Latest prompt-only result:

```text
refined source discipline vs baseline Step6-style control
  -> Whistleblower: refined wins, 9 vs 8
  -> Parenting teen: refined wins, 9 vs 7
  -> Real estate: refined wins, 9 vs 8
```

The refined rule reduced aggregate overclaim risk from 8 to 5 and removed
decision-relevant unsupported precision from the refined variants, while
preserving useful decision movement.

That made the refined rule a promotion candidate for a small off-by-default
prompt PR, but the later runtime-shaped fixed-card probe weakened that simple
promotion story: the rule helped interpretation but did not solve grounding.

The current next loop is now:

```text
audit-passed revised clean answer
  -> decision-quality comparison against prior best controls
  -> if it wins locally, repeat on broader case families
  -> only then consider an off-by-default promotion candidate
```

Run this before adding any pre-Step6 subagent layer or default runtime change.

Parked architecture variants to revisit only after the provenance-rendering and
post-render audit path is understood:

### Baseline

Current flow:

- four lanes;
- V60 private enrichment;
- Step 6;
- Step 6b ledger;
- Step 7/8 post-hoc pressure check.

### Variant A: OpenRouter Micro-Bevelin

- keep current lane outputs stable;
- after selected Lane 1 findings, run narrow OpenRouter calls;
- generate small Bevelin interpretation candidates;
- Step 6 receives compact candidates;
- normal post-check remains for measurement.

### Variant B: Pre-Step6 Candidate-Shift Sub-Agents

- keep lane outputs stable;
- before Step 6, run one sub-agent per non-empty lane;
- each sub-agent returns `CandidateShiftPacket`;
- Step 6 waits and synthesizes from full context plus packets;
- optional post-check remains during research.

### Variant C: Hybrid

- OpenRouter prepares Bevelin handles for selected Lane 1 findings;
- Lane 1 sub-agent evaluates those handles;
- all lane sub-agents return candidate shifts;
- Step 6 synthesizes.

## Success Criteria

A candidate architecture is useful only if final answers improve.

Look for:

- clearer "what actually shifted";
- better evidence gates;
- better diagnostic questions;
- fewer meaningful Step 8 divergences;
- stronger grounded set-asides;
- less generic caution;
- no public machinery leakage;
- no collapse in Lane 1 useful recall;
- improvement across multiple case types, not one fixture family;
- defensible cost and latency;
- preserved ability for Step 6 to reject weak pressure.

Intermediate artifacts are not enough. A beautiful packet that does not improve
the final answer is not a win.

## Falsifiers

Park or reject the candidate if:

- final prose becomes committee synthesis;
- answers become longer but not more decisive;
- Bevelin output becomes generic "be careful" language;
- source details still disappear;
- Step 8 catches the same misses;
- cost roughly doubles without clear final-answer improvement;
- sub-agents overcorrect from narrow lane context;
- deterministic routing starts pretending it knows truth;
- docs and runtime drift further apart.

## Evidence Ledger

### Strong Evidence

- Bevelin and Munger overlap too much for a clean second Lane 1.5.
- Bevelin is valuable as interpretation grammar.
- Source evidence has to be rendered, not merely stored.
- Exact source pins alone are too thin when they remove decision context.
- Step 6 is overloaded enough that adding more theory directly is risky.
- Product docs should not include experiments before promotion.
- Strict source discipline improves the research direction: the final reasoner
  should not add new concrete categories unless they appear in the conversation
  or source evidence.
- A prompt-discipline problem should not be solved by adding an agent layer
  until that layer beats a cleaner prompt-only control.

### Medium Evidence

- Full source-evidence rendering is current local best among tested private
  addendum shapes.
- OpenRouter can be useful for narrow source-bound interpretation calls.
- Pre-Step6 candidate-shift sub-agents may reduce Step 6 overload.
- Handoff packets are the right architecture object to test.
- Manual archived Lane 1 handoff can be transported into the new packet schema
  cleanly, but that proves custody and shape only.
- OpenRouter producer quality is still untested for the new handoff contract:
  the first 2026-05-14 dry run hit `missing_api_key` on all 7 attempted calls.
- A single subagent producer dry run produced real candidate reasoning, but did
  not validate cleanly because one packet leaked an internal step name.
- The tightened subagent rerun validated cleanly on the same case, giving the
  first clean subagent producer sample.
- Expanded subagent producer dry run validated on three withheld Availability
  cases with 6 packets after failures exposed label leakage and per-packet
  precision drift.
- Tiny subagent consumption probe on two fair withheld cases produced 2 weak
  candidate wins and 0 real candidate wins against the deterministic
  carry-detail control. It sharpened source-specific questions, but all four
  answer variants still had decision-relevant unsupported precision, and the
  real-estate candidate increased overclaim risk.
- Check-only subagent rendering kept the 2 weak candidate wins and 0 real wins,
  while reducing candidate decision-relevant unsupported precision from 2 cases
  to 1 and lowering real-estate overclaim risk from 3 to 2. It is the current
  best local pre-Step6 subagent consumption shape, but still not promotable.
- Strict check-only subagent rendering was the best local subagent shape before
  ablation: the same
  two fair cases produced 2 real candidate wins, 0 weak wins, 0 public
  machinery leaks, and 0 candidate variants with decision-relevant unsupported
  precision. It is still not promotable because the test confounds the strict
  no-new-concrete-categories rule with the subagent checks themselves.
- Strict-control ablation weakened the subagent-layer case: when the
  deterministic control received the same strict source-discipline rule, both
  fair cases tied 9 vs 9. The extra subagent checks did not prove decision
  lift beyond the stricter prompt rule.
- Prompt-only source-discipline probe produced mixed evidence: strict won one
  non-Availability case and baseline won one. This blocks promotion but keeps
  the principle alive for refinement.
- Refined prompt-only source-discipline probe produced positive broader
  evidence: refined won 3/3 across whistleblower, parenting teen, and real
  estate; baseline had 2 variants with decision-relevant unsupported precision,
  refined had 0; refined overclaim risk sum was 5 versus baseline 8. This makes
  the refined rule a small off-by-default prompt PR candidate, not a runtime
  default.
- Widening source evidence and adding carry-detail rules reduces source
  omissions, but does not yet solve high-severity threshold preservation.
- Micro-generated full packets can preserve source details but may damage final
  answer quality when they own too much framing.
- Step 6 presentation matters, but source-first ordering and compact
  source-detail contracts do not yet beat deterministic carry-detail.
- Provenance-shaped revision is promising as internal custody: the packet can
  catch unsupported draft numbers, the clean renderer can remove visible patch
  machinery, and a hardened post-render audit can drive a revision that passes
  the same audit on the first real-estate case. The audit-passed answer also won
  the first decision-quality comparison on that case. The broader parenting
  repeat then passed the same gates after a claim-type contract repair. It is
  now joined by a whistleblower / institutional-risk pass. This is a real
  off-by-default promotion candidate, but not a default-runtime change, because
  the path is serial, costly, and still concentrated in one provider family.
- Friction-aware review is necessary because generic blind review can prefer
  smooth support over useful System B pressure. It is still only secondary
  evidence, but it caught that the card-consumption variants lost too much hard
  gate / counsel / safety friction in parenting and whistleblower.
- Grounded practical force is the current transferable Step 6 principle:
  concrete conditional action plus evidence gate plus calibration boundary plus
  sequence / next check minus unsupported exactness.
- A separate grounded-practical-force card is promising but not promotable. In
  the first card-consumption ablation, `strict_card` won both generic and
  friction-aware review on real-estate boundary, but lost friction-aware review
  to `deterministic_control` in parenting and whistleblower.
- The operational-gate follow-up improved the weak operational card variants
  but still lost to `deterministic_control` in parenting and whistleblower. It
  also slightly hurt the already-good real-estate boundary case by adding
  unnecessary shape.
- The smaller central-gate card then produced the strongest card signal so far:
  it won friction-aware review on parenting, whistleblower, and real-estate
  boundary after a valid whistleblower rerun. Promotion is still blocked because
  manual inspection found remaining source/overclaim and public-prose risks.

### Weak Or Untested

- Whether pre-Step6 sub-agents outperform strict prompt-only controls across
  more than the two fair Availability-family cases.
- Whether OpenRouter micro-Bevelin adds value beyond Claude sub-agents.
- Whether OpenRouter can produce valid `candidate_shift_handoff.v1` packets at
  all once a provider key is available.
- Whether subagents can produce valid packets after prompt tightening and exact
  source-ref copying across more than one case. Current answer: yes for three
  withheld Availability producer-only dry runs, not yet for final-answer
  improvement.
- Whether a hybrid path is worth the coordination cost.
- Whether the provenance/audit/revision gains hold with lower cost and an
  independent reviewer/provider check.
- Whether a revised grounded-practical-force card can preserve hard operational
  gates without creating fake force in lower-action cases.
- Whether a smaller central-gate card works better than the current larger
  card-consumption prompt.
- Whether central-gate wins survive focused source/overclaim audit and
  high-context review.
- How V60 ledger timing should work if candidate-shift agents run before Step 6.
- Whether the hybrid micro-carry result holds outside the withheld availability
  case family.

## Reading Map

### Start Here

- `research/subagent-cognitive-worker-architecture-vision-2026-05-15.md`
- `research/meta-reasoning-corpus-question-bank-2026-05-15.md`
- `research/post-lane-inquiry-card-vision-2026-05-15.md`
- `research/reasoning-preservation-doctrine-2026-05-13.md`
- `research/lane1-bevelin-handoff-artifact-2026-05-13.md`
- `research/lolla-architecture-bottleneck-audit-2026-05-14.md`
- `research/lolla-context-engineering-lessons-2026-05-14.md`
- `research/step6-decomposition-red-team-2026-05-14.md`

### Meta-Reasoning Corpus

- `research/subagent-cognitive-worker-architecture-vision-2026-05-15.md`
- `research/meta-reasoning-corpus-question-bank-2026-05-15.md`
- `research/post-lane-inquiry-card-vision-2026-05-15.md`
- `/Users/marcin/Desktop/ksiazki pdf/outbox/ready`

### Bevelin Versus Munger

- `research/bevelin-only-tendency-map-2026-05-12.md`
- `research/bevelin-munger-fit-audit-2026-05-12.md`
- `research/bevelin-canonical-mental-model-map-2026-05-12.md`
- `/Users/marcin/Desktop/Apps/Lolla-system-b/munger_structural_mapping.md`
- `/Users/marcin/Desktop/Apps/Lolla-system-b/The_Psychology_of_Human_Misjudgment.md`
- `/Users/marcin/Desktop/Apps/Lolla-system-b/munger_knowledge_project_transcript.md`
- `/Users/marcin/Desktop/ksiazki pdf/outbox/processing/Peter Bevelin - Seeking Wisdom.md`

### Lane 1 Enrichment And Tests

- `research/lane1-bevelin-enrichment-local-rollup-2026-05-12.md`
- `research/lane1-bevelin-pass2-local-eval-2026-05-12.md`
- `research/lane1-bevelin-trigger-flip-review-post-all-repairs-live-valid-2026-05-12.md`
- `research/lane1-bevelin-supervised-research-loop-readout-2026-05-14.md`

### Interpretation And Step 6 Consumption

- `research/bevelin-general-purpose-interpretation-layer-2026-05-13.md`
- `research/lane1-bevelin-interpretation-artifact-expanded-pass3-overclaim-repair-2026-05-13.md`
- `research/lane1-bevelin-step6-consumption-2026-05-13.md`
- `research/lane1-bevelin-source-bound-step6-consumption-2026-05-13.md`
- `research/lane1-bevelin-source-bound-step6-consumption-post-priority-repair-2026-05-13.md`
- `research/candidate-shift-packet-carry-detail-readout-2026-05-14.md`
- `research/candidate-shift-packet-micro-carry-merged-readout-2026-05-14.md`
- `research/candidate-shift-packet-micro-carry-merged-historical-readout-2026-05-14.md`
- `research/candidate-shift-packet-micro-carry-only-withheld-readout-2026-05-14.md`
- `research/candidate-shift-packet-source-exact-carry-withheld-readout-2026-05-14.md`
- `research/pre-step6-subagent-candidate-shift-consumption-probe-2026-05-14.md`
- `research/pre-step6-subagent-candidate-shift-check-only-probe-2026-05-14.md`
- `research/pre-step6-subagent-candidate-shift-check-only-strict-probe-2026-05-14.md`
- `research/step6-provenance-audit-passed-decision-comparison-2026-05-14.md`
- `research/step6-reviewer-smoothness-bias-audit-2026-05-15.md`
- `research/step6-grounded-practical-force-principle-2026-05-15.md`
- `research/step6-grounded-practical-force-card-provider-strategy-2026-05-15.md`
- `research/step6-card-consumption-ablation-readout-2026-05-15.md`
- `research/step6-card-consumption-operational-gate-followup-2026-05-15.md`
- `research/step6-central-gate-card-consumption-readout-2026-05-15.md`
- `plans/pi-coding-agent-lessons-for-lolla-handover-2026-05-14.md`

### Source Evidence And Negative Results

- `research/lane1-bevelin-source-evidence-renderer-repair-2026-05-13.md`
- `research/lane1-bevelin-source-specific-handle-readout-2026-05-13.md`
- `research/lane1-bevelin-source-omission-diagnostic-readout-2026-05-13.md`
- `research/lane1-bevelin-source-pin-shaping-readout-2026-05-14.md`
- `research/lane1-bevelin-withheld-source-evidence-vs-source-pin-strict-direct-gpt4o-2026-05-14.md`

### Runtime Contracts To Check Before Promotion

- `SKILL.md`
- `HOW_IT_WORKS.md`
- `references/private-enrichment-treatment.md`
- `references/anchor-treatment.md`
- `references/sub-agent-prompts.md`
- `references/presentation-voice.md`
- `references/anti-bullshit-doctrine.md`

## Working Protocol For Future Sessions

1. Read this file first.
2. Read only the linked deep docs relevant to the next decision.
3. State whether the work is research-only or runtime promotion.
4. Keep product docs unchanged unless explicitly promoting stable behavior.
5. Run one small slice at a time.
6. Measure final-answer improvement, not artifact beauty.
7. Record negative evidence with the same care as wins.
8. Update this file when a decision changes.

## Current Next Move

The next useful work is not another Bevelin taxonomy pass and not runtime
promotion.

Latest 2026-05-15 update:

- generic reviewers may reward smoothness, so friction-aware review is now part
  of the research evaluation loop;
- friction-aware review still preferred deterministic controls in parenting and
  whistleblower, so the latest losses were not explained mainly by reviewer
  smoothness bias;
- direct control inspection produced the transferable principle:

```text
grounded practical force =
  concrete conditional action
  + evidence gate
  + calibration boundary
  + sequence / next check
  - unsupported exactness
```

## Subscription Handoff Harness

Latest 2026-05-15 local architecture result:

```text
worker/dossier receipt
  -> small path-based orchestrator handoff pack
  -> high-context orchestrator answer
  -> focused source/overclaim audit
  -> comparison against current controls
```

This keeps the cognition/flexibility boundary clear:

```text
OpenRouter/API:
  narrow packet generation or focused audit

deterministic code:
  schema, path custody, caps, validation, receipts

high-context orchestrator:
  synthesis, judgment, product reasoning
```

Three-case local result:

```text
parenting:
  high-context handoff answer passed source audit
  OpenRouter final-consumer answer was rejected for changing daughter 14 to 19

real_estate_boundary:
  high-context handoff answer passed
  OpenRouter final-consumer answer also passed, but manual review still flags
  unsupported future-supply comfort

whistleblower:
  high-context handoff answer passed
  OpenRouter final-consumer answer moved from revise to pass on rerun, exposing
  reviewer instability

central-gate controls:
  source audit passed on final rerun
  but whistleblower earlier surfaced an unsupported spouse-protection claim,
  then contradicted itself

direct friction-aware comparison:
  parenting winner: high-context handoff
  real_estate_boundary winner: central-gate final
  whistleblower winner: high-context handoff
```

Current doctrine:

```text
source audits are useful secondary evidence
manual/high-context review remains authority for product judgment
do not promote until the exact runtime-shaped path beats clean controls
do not force heavier handoff where a smaller central gate is sufficient
```

Receipt:

```text
research/subscription-orchestrator-handoff-local-test-readout-2026-05-15.md
```

- OpenRouter can generate schema-bound cards cheaply, but the first
  whistleblower card overclaimed with conclusion-shaped language, so validation
  must block unsupported legal/safety/conclusion terms;
- first card-consumption ablation showed a mixed result:

```text
parenting: generic strict_card win, friction-aware deterministic_control win
whistleblower: deterministic_control wins both reviews
real_estate_boundary: strict_card wins both reviews
```

- operational-gate follow-up then tested the obvious repair and did not close
  the gap:

```text
parenting: deterministic_control still wins
whistleblower: deterministic_control still wins
real_estate_boundary: prior strict_card still wins
```

- decision: do not promote the card, do not add it to product docs, do not add a
  new lane, and do not mutate the knowledge base;
- next research slice should not keep enlarging the consumer prompt. Design a
  smaller central-gate card shape containing only central evidence gate,
  central calibration boundary, central sequence / stop-rule, and set-aside
  reason; then test whether the final reasoner can use or reject that smaller
  shape.
- central-gate card then became the best card result so far:

```text
parenting: central_gate_card wins friction-aware review
whistleblower: central_gate_card wins valid friction-aware rerun
real_estate_boundary: central_gate_card wins friction-aware review
```

- promotion remains blocked because manual inspection found remaining risks: a
  legal-ish spouse-confidant claim in whistleblower, an awkward clipped opening
  in parenting, and no independent source/overclaim audit yet;
- next slice should audit central-gate final answers for source grounding and
  overclaim before any further promotion discussion.
- in parallel, the meta-reasoning corpus question bank now preserves the next
  design direction:

```text
store rich cognition for audit;
inject only compressed survivor pressure;
use books to improve the thinking process, not to add more names.
```

- the first RAG batch should use the compact 24-question universal set against
  Bevelin, Dewey, Asking the Right Questions, Scout Mindset, Annie Duke,
  Thinking in Systems, Framers, Calling Bullshit, Co-Intelligence, SkillNet,
  and Sycophantic AI. The 120-question bank is only an appendix for later depth,
  not the default extraction surface.
- the inquiry-layer correction is now explicit: do not optimize for generic
  pre-system questions. The promising feature is a post-lane inquiry card
  generated from selected system findings, source evidence, and retrieved
  chunks, then carried privately into final synthesis when useful.
- priority now shifts from the book-question corpus to implementation
  architecture: design a small off-by-default subagent cognitive-worker slice
  where a narrow workpack becomes a validated worker packet, then a compact
  cognition dossier for the final reasoner. The current Step 7 after-check
  remains the product/control path until this proves better.

Latest 2026-05-14 update:

- strict check-only subagent checks produced 2 real candidate wins against a
  weaker control;
- the strict-control ablation then gave the deterministic control the same
  strict source-discipline rule;
- both fair cases tied 9 vs 9;
- the extra subagent checks did not show useful decision-quality lift beyond
  the stricter private prompt rule;
- the stronger surviving lesson is strict source discipline, not a new
  pre-Step6 agent layer;
- the first prompt-only test was mixed;
- refined source-discipline wording then won 3/3 broader prompt-only cases,
  reduced aggregate overclaim risk, and removed decision-relevant unsupported
  precision from refined variants;
- a default-off runtime-placement hook now exists and is covered by focused
  tests;
- the first runtime-shaped fixed-card probe was mixed-negative: refined source
  discipline improved decision interpretation but not grounding; grounded-draft
  wording was least bad; raw source context was worst and was not kept as a
  runtime hook.
- the provenance-shaped packet contract now exists and is covered by focused
  tests.
- the producer/consumer and clean-renderer probes completed on the real-estate
  case:

```text
source-provenance packet producer
  -> validator
  -> patch-style revision consumer
  -> clean final-answer renderer
```

- the result is `revise`, not promote: numeric rebound improved after prompt
  hardening, but certainty rebound remained.
- the first post-render audit v1 was too lenient and passed the flawed answer;
- the hardened audit v2 returned `revise_material` and flagged the buffer,
  boiler, and unsupported certainty issues.
- audit-driven clean revision then passed hardened re-audit:

```text
clean final answer
  -> source-grounding and modal-strength audit
  -> audit-driven clean revision
  -> audit again
```

- next slice broadened beyond the real-estate fixture into another reasoning
  shape and completed after a useful claim-type contract repair.
- decision-quality comparison V2 completed:

```text
audit_passed_revision: 9
prior_grounded_draft: 6
deterministic_control: 5
recommended_next_action: broaden_reasoning_shapes
```

- broader reasoning-shape repeat completed:

```text
packet validation: valid
first audit: revise_minor
re-audit after targeted revision: pass
decision comparison:
  audit_passed_revision: 9
  prior_grounded_draft: 8
  deterministic_control: 6
total tokens: 35390
```

- whistleblower / institutional-risk repeat completed:

```text
packet validation: valid
first audit: pass
decision comparison:
  audit_passed_revision: 9
  prior_grounded_draft: 8
  deterministic_control: 7
total tokens: 24640
```

- next slice is reusable harness packaging and cost-control inspection, not a
  new layer or default runtime change.

Older run-record context remains below because it explains why we arrived at
this stricter prompt-discipline path.

Candidate-shift handoff now has a clearer mixed signal:

- carry-detail candidate packets won 3 of 3 withheld answer-quality
  comparisons;
- they won 3 of 3 strict direct comparisons against current source-evidence;
- they reduced material source omissions from 7 to 5;
- they still left 4 high-severity omissions.
- full micro-Bevelin packets improved source preservation but hurt answer
  quality;
- hybrid micro-carry packets won 3 of 3 answer-quality comparisons, won 3 of 3
  strict direct comparisons against both current source-evidence and
  deterministic carry-detail, and reduced material omissions to 3 with 2
  high-severity omissions.
- on historical cases, hybrid micro-carry still won 6 of 6 versus no-addendum
  baseline, but deterministic carry-detail also won 6 of 6;
- historical source-omission diagnostics were worse for hybrid: 14 material
  omissions and 9 high-severity omissions versus deterministic 12 and 7;
- historical strict direct compare favored deterministic carry-detail: 2 real
  hybrid wins, 3 deterministic wins, and 1 tie.
- carry-only micro detail won 3 of 3 versus no-addendum on withheld, but strict
  direct comparison against deterministic was mixed and source omissions were
  not good enough: 6 material and 3 high-severity.
- source-exact carry generated cleanly and cheaply, but Step 6 consumption won
  only 2 of 3 withheld cases against no-addendum baseline; the PhD case
  regressed.

This means the next bottleneck is not "can packets help?" and not simply "make
the source detail more exact." The next bottleneck is experiment control:
context-visible content, context-invisible state, artifact completeness, stop
gates, and promotion evidence need to be explicit before another packet shape.

The first Pi-informed run-record slice now exists:

- `lolla_experiment_run_record.v1` is implemented in the research loop.
- It separates context-visible Step 6 additions from context-invisible
  validation, telemetry, judge output, raw receipts, and failure reasons.
- It marks missing required receipts and unknown artifact references.
- It records whether the run is complete and why a branch is parked or kept.
- A complete parked source-exact carry receipt now exists at
  `research/candidate-shift-run-record-source-exact-carry-withheld-2026-05-14.md`.
- A complete `kept_local` deterministic carry-detail control receipt now exists
  at
  `research/candidate-shift-run-record-deterministic-carry-detail-withheld-2026-05-14.md`.
- A complete parked historical hybrid-vs-deterministic comparison receipt now
  exists at
  `research/candidate-shift-run-record-historical-hybrid-vs-deterministic-carry-2026-05-14.md`.

The run-record-based branch choice is recorded at
`research/candidate-shift-run-record-branch-decision-2026-05-14.md`.

`source_first_deterministic_carry_renderer` has now been tested on withheld
cases twice. The first live run had a research-harness wiring issue: metadata
recorded `source_first`, but the Step 6 prompt builder did not receive the
render mode. The corrected promptfix run is the evidence to trust:

- it won 2 of 3 against no-addendum;
- strict direct comparison against deterministic carry-detail was mixed: 1 real
  source-first win, 1 deterministic win, 1 tie;
- omissions stayed at 5 material and 4 high-severity;
- the complete receipt is
  `research/candidate-shift-run-record-source-first-carry-detail-withheld-2026-05-14.md`.

The compact source-detail contract was also tested:

- it won 3 of 3 against no-addendum;
- strict direct comparison against deterministic carry-detail favored the
  reference: 1 real contract win, 2 deterministic wins;
- high-severity omissions improved from 4 to 3, but material omissions worsened
  from 5 to 6.

The presentation-audit readout is stored at
`research/candidate-shift-step6-presentation-audit-readout-2026-05-14.md`.

The case-level answer audit is stored at
`research/candidate-shift-case-level-step6-output-audit-2026-05-14.md`.

Its key finding:

- the exact source evidence is present in the packet;
- the packet's generic `proposed_shift` and `evidence_gate` wording often makes
  Step 6 translate the source into generic evidence-seeking;
- the next candidate should expose a source-specific decision gate before
  generic tendency wording, without adding generated rejection requirements.

The source-gate-first readout is stored at
`research/candidate-shift-source-gate-first-readout-2026-05-14.md`.

Its key finding:

- source-specific decision gates produced the strongest recent strict answer
  signal: 2 real wins against deterministic carry-detail, 1 reference win;
- source omissions worsened from 5 material / 4 high-severity to 6 material / 5
  high-severity;
- the PhD answer invented optimistic thresholds, so the variant is not safe to
  promote.

The packet evidence synthesis is recorded at
`research/candidate-shift-packet-evidence-synthesis-2026-05-14.md`.

The focused post-Step6 source-preservation QA/repair pass has now been tested.
It is useful local machinery, but not promotable.

The next useful work is evaluation decomposition:

1. Do not add another repair prompt yet.
2. Do not keep enlarging the pairwise judge prompt.
3. Run source-grounding/precision audit as a focused artifact.
4. Feed that audit into a separate decision-quality comparison judge.
5. Keep deterministic code in routing, validation, receipt, and artifact-passing
   mode, not winner-deciding mode.
6. Continue only if the decomposed evaluation gives a more stable read on
   source precision versus decision usefulness.

Concrete execution plan:

- `research/candidate-shift-handoff-research-plan-2026-05-14.md`
- `research/candidate-shift-research-harness-reset-2026-05-14.md`
- `experiments/candidate-shift-handoff/autoresearch.md`

Harness reset:

- the large interpretation artifact script is now treated as a legacy research
  harness, not the place to grow new experiment families;
- the active decomposed evaluator starts in
  `scripts/research/candidate_shift_eval/grounding.py`;
- first live readout:
  `research/grounding-audited-source-gate-vs-deterministic-readout-2026-05-14.md`;
- the immediate goal is not a new repair path but a cleaner read on whether
  candidate answers improve reasoning or merely sound more concrete;
- deterministic code remains responsible for routing, validation, receipts, and
  summaries;
- LLMs and sub-agents remain responsible for the cognitive judgment, with their
  outputs treated as receipts to inspect rather than truth by authority.

Current evaluator finding:

- small OpenRouter was cheap but not strict enough for the audit role;
- direct OpenAI completed the stricter evaluator;
- source-gate-first did not beat deterministic carry-detail on the withheld set;
- this supports keeping deterministic carry-detail as the local control while
  studying whether any source-gate-first reasoning move can be preserved without
  unsupported precision.

Pre-Step6 subagent producer and consumption finding:

- producer validation now works on three withheld Availability cases after
  prompt/validator hardening;
- the first fair consumption probe used two cases, because PhD remains excluded
  until long-context visibility is fixed;
- adding validated subagent checks to the deterministic carry-detail control
  produced 2 weak candidate wins and 0 real wins;
- friendship improved modestly by making the stabilization test cleaner and
  lowering overclaim;
- real estate improved the `$20K-$60K` stress-test question but increased
  unsupported precision and overclaim risk;
- check-only rendering then removed broad `proposed_shift` prose from
  final-reasoner context;
- check-only kept 2 weak wins and 0 real wins, improved grounding on friendship,
  and reduced real-estate overclaim, but still left decision-relevant
  unsupported precision in real estate;
- strict check-only added a private no-new-concrete-categories rule and won
  2 real comparisons against the weaker control;
- strict-control ablation then tied both fair cases when the deterministic
  control received the same strict source-discipline rule;
- current best local lesson is not "add a subagent." It is: keep source
  evidence exact and prevent the final reasoner from adding new concrete
  categories unless source-backed.

Until that evidence exists, the standing recommendation is:

- keep current post-Step6 pressure checks in production;
- keep Bevelin as research interpretation grammar;
- keep Lane 1 Munger spine stable;
- do not mutate canonical KB;
- do not stuff Bevelin into Step 6;
- do not move sub-agents before Step 6 unless they beat strict prompt-only
  controls across more case families;
- do not promote global hybrid micro-carry;
- do not promote carry-only micro detail;
- do not promote source-exact carry;
- do not promote source-first rendering;
- do not promote the compact source-detail contract;
- do not promote adjudicated source-use repair;
- do not treat the current direct-comparison judge as a promotion oracle;
- do not let generated rejection gates become stronger than source evidence;
- do not let a thin detail field replace a source-exact threshold or sequence;
- do not keep adding prompt variants before the actual answer differences have
  been inspected case by case.

## Provenance Harness Packaging

The provenance-shaped revision path is now packaged as a reusable
off-by-default research harness:

```text
scripts/research/candidate_shift_eval/provenance_sequence.py
tests/test_revision_provenance_sequence.py
```

It preserves the big-picture doctrine:

- LLM calls do the judgment-heavy work in narrow stages;
- deterministic code records custody, validation, stage order, metadata, and
  token totals;
- no canonical KB change;
- no product-doc change;
- no default `/lolla` behavior change.

The packaged sequence is:

```text
packet -> patch -> renderer -> audit -> optional revision -> optional re-audit -> comparison
```

The important design choice is that the extra repair call is conditional. If
the first grounding/modal audit passes, the harness skips audit-driven revision
and compares the rendered answer directly. This keeps the loop from becoming a
habitual correction machine.

Current packaging tests:

```text
pytest tests/test_revision_provenance_packet.py tests/test_revision_provenance_sequence.py -q
21 passed
```

This moves the bottleneck. We no longer need to ask whether the sequence can be
repeated without one-off scripts. The next questions are:

- can cost come down without losing the quality signal;
- can an independent reviewer/provider confirm the model-judge result;
- should the renderer enforce exact Step 6 public heading style;
- can this remain optional and reversible if promoted as a runtime-shaped
  research branch.

First harness smoke attempt:

```text
research/spikes/candidate-shift-handoff/step6-provenance-harness-smoke-whistleblower-v1-2026-05-14.json
status: packet_call_failed
call failure: missing_api_key
tokens: 0
```

This is useful negative evidence about execution setup, not about the method.
The harness now records call failures separately from validation failures so we
do not confuse missing infrastructure with bad reasoning.

Do not reopen pre-Step6 subagent promotion until the provenance-shaped revision
path has cost-control and independent-review evidence.

## Red-Team Update

Fresh subagent review agrees the deterministic/LLM boundary is mostly clean:

- deterministic code orchestrates, validates, records metadata, records token
  totals, and stops on failed custody;
- LLM stages still do the packet interpretation, repair, rendering, audit, and
  comparison;
- default runtime and product docs remain unchanged.

But the strongest objection is evaluator endogeneity:

```text
The same family of model reasoning may be shaping the answer, auditing the
answer, and judging the answer.
```

This means the three positive case families should be treated as medium
evidence, not promotion-grade evidence. They show the path is promising. They
do not prove that users or independent judges prefer the result.

Updated next test:

```text
blind independent review
  -> judge sees conversation and final answers only
  -> no provenance packet
  -> no answer labels
  -> separate scores for usefulness, grounding, answer thinness, calibration
```

Cost ablation should come after or alongside that blind review:

```text
full sequence vs cheaper sequence
  -> skip patch where renderer can use packet directly
  -> skip comparison where runtime would not need a research judge
  -> preserve grounding/modal audit as the safety gate
```

Recorded but not edited:

- `SKILL.md` and `HOW_IT_WORKS.md` appear to disagree about Step 7 timing
  relative to Step 6 finalization.
- Product docs remain untouched during this research slice.

## Blind Review Result

The blind review contract now exists:

```text
scripts/research/candidate_shift_eval/blind_review.py
tests/test_revision_provenance_blind_review.py
```

It hides provenance labels and asks for separate scores on usefulness,
grounding, answer-thinness risk, and calibration.

First whistleblower result:

- v1 blind review picked the provenance answer, but the payload was invalid
  because the reviewer used `label_visibility_issues` for visible heading style;
- v2 clarified the contract and produced a valid blind review;
- v2 winner was anonymous Answer A, which maps to `deterministic_control`;
- the reason was practical force: the deterministic answer gave more concrete
  sequencing and attorney questions, while the provenance answer was cleaner
  but slightly more inert.

This is the most important current correction to the vision:

```text
Source discipline is not enough. The system must preserve decision force.
```

The research target is therefore sharper:

```text
reduce unsupported precision
without
reducing useful operational movement
```

The provenance path remains useful research machinery, but blind review has
lowered confidence in promotion. The next evidence gate should broaden blind
review before adding features or runtime wiring.

Broader blind review now covers the three existing case families:

```text
real estate: provenance wins
parenting: deterministic control wins
whistleblower: deterministic control wins
```

What this means in simple terms:

The provenance path helps most when the problem is a numeric boundary and the
answer benefits from removing unsupported estimates. It struggles when the user
needs concrete operational help, because the cleanup step can remove too much
useful movement.

Updated bottleneck:

```text
not enough grounded force preservation
```

The system needs to distinguish:

- unsupported precision that should be softened or removed;
- useful conditional action that should stay because it helps the user move;
- public process clutter that should be hidden;
- answer-thinning that should be penalized.

So the next architectural question is not "more models?" It is:

```text
Can a focused model call preserve practical force while obeying source
discipline?
```

That is the real Bevelin value now: better judgment about what a clue means,
what it supports, and how much action it justifies.

Next slice plan:

```text
research/step6-grounded-force-preservation-plan-2026-05-14.md
```

## Live Harness Confirmation

After loading provider credentials from `.env`, the packaged provenance harness
completed on the whistleblower case:

```text
research/spikes/candidate-shift-handoff/step6-provenance-harness-smoke-whistleblower-v2-2026-05-15.json
```

Result:

```text
status: complete
final audit: pass
internal comparison winner: audit_passed_revision
scores: 9 vs 7 vs 6
tokens: 24144
```

This confirms the harness works as research machinery. It does not settle the
architecture question, because the blind review on the same case chose
deterministic control for practical force.

Current doctrine therefore stands:

```text
use provenance to control unsupported precision
add grounded-force preservation before considering promotion
judge promotion through blind final-answer review
```

Grounded-force slice result:

```text
parenting:
  grounded-force audit says revise_for_both
  force_score 6
  grounding_score 9

whistleblower:
  grounded-force audit says keep
  force_score 9
  grounding_score 10
  but blind review of the live harness answer still picks deterministic control
```

Meaning:

The new audit can catch obvious thinning, as in parenting. But a one-answer
audit can still miss relative force loss compared with a stronger control. For
whistleblower, it thought the answer was good enough; blind review disagreed.

Next architecture lesson:

```text
Force preservation should be contrastive when possible.
```

Do not only ask "is this answer useful?" Ask:

```text
what practical force did the better control preserve that this answer lost?
```

## Reviewer Smoothness Bias Correction

Latest 2026-05-15 correction:

The contrastive force path improved the provenance candidate in parenting and
produced valid revised answers, but the generic blind reviewer still preferred
deterministic control in parenting and whistleblower.

This blocks promotion. It does not prove the path is useless.

System B already had this warning in B-Repo:

```text
smooth downstream output is not the same thing as better reasoning
LLM judges are secondary evidence, not the source of truth
LLMs can smooth useful friction into plausible balance
```

Relevant recovered docs:

```text
/Users/marcin/Desktop/Apps/Lolla-system-b/plans/benchmark-design-cautions-from-lolla-next.md
/Users/marcin/Desktop/Apps/Lolla-system-b/plans/benchmark-judge-layer-follow-on.md
/Users/marcin/Desktop/Apps/Lolla-system-b/plans/benchmark-phase1-contract.md
research/step6-reviewer-smoothness-bias-audit-2026-05-15.md
```

Current generic blind review checks:

```text
decision usefulness
grounding
answer thinness
calibration
winner
```

That is useful, but incomplete. It does not directly check whether the added
System B / Bevelin pressure survived as productive friction:

```text
stop-rule
evidence gate
hard question
branch condition
falsification check
counsel/safety-mediated check
decision threshold
```

So a new friction-aware research prompt/validator now exists:

```text
scripts/research/candidate_shift_eval/blind_review.py
build_friction_aware_blind_review_prompt
validate_friction_aware_blind_review
tests/test_revision_provenance_blind_review.py
```

It restores the old adoption labels:

```text
correctly_used
correctly_ignored
smoothed_useful_friction
used_as_filler
ignored_as_noise
overweighted_advisory
```

Friction-aware rerun result:

```text
parenting: deterministic_control still wins
whistleblower: deterministic_control still wins
```

This matters because the reviewer was explicitly told not to reward smoothness
by itself. It was asked to score productive friction: stop-rules, evidence
gates, branch conditions, calibration, and uncomfortable but useful pressure.
The result therefore strengthens the negative signal against the current
provenance / contrastive repair path.

What it does not prove:

```text
Bevelin/source discipline is useless
```

What it does show:

```text
the current repair implementation still loses practical friction in operational
cases, even under a friction-aware automated reviewer
```

Current decision:

```text
do not promote
do not add another repair layer yet
extract the winning practical-force principle from deterministic control
keep human/high-context review as the final source of truth
```

The extracted principle is now tracked here:

```text
research/step6-grounded-practical-force-principle-2026-05-15.md
```

Short form:

```text
grounded practical force =
  concrete conditional action
  + evidence gate
  + calibration boundary
  + sequence / next check
  - unsupported exactness
```

## Latest 2026-05-15: Lane 1 Bridge Final-Consumption Slice

New readout:

```text
research/lane1-bridge-final-consumption-readout-2026-05-15.md
```

The Lane 1 bridge candidate was tested where it matters: final-answer
consumption.

The test compared:

```text
control = conversation + selected-model context
bridge  = conversation + selected-model context + compact validated bridge card
```

Two cases were run:

```text
real-estate-reward-repair
oncologist-reward-repair
```

Result:

```text
both bridge answers won narrowly under a friction-aware review
both controls were already strong
both raw reviewers violated the enum contract
```

This is important. The bridge has a positive signal, but the reviewer drift
proves again that LLM judges remain secondary evidence. The system must preserve
validator and human/high-context review gates instead of treating reviewer
preference as truth.

Current decision:

```text
keep the Lane 1 bridge as a local research candidate
do not promote into SKILL.md, HOW_IT_WORKS.md, default /lolla, Lane 1, V60, or
Step 6 runtime
```

The bridge is useful only if it compresses Bevelin-style reasoning hygiene into:

```text
why this was surfaced
what evidence controls use
what boundary prevents overclaim
how to use it
when to discard it
```

The bridge is not useful if it becomes:

```text
another lane
another knowledge-base layer
another model-picking system
another smooth paragraph
```

Updated definition of good:

```text
good = grounded practical force survives
     + the model is used or rejected for source-bound reasons
     + useful friction becomes a gate, no-signal, branch, or stop-rule
     - public machinery leakage
     - unsupported precision
     - generic caution
     - smoothness-as-quality
```

Next required evidence:

```text
irrelevant bridge case -> correctly ignored
speculative EV case -> discarded rather than turned into fake math
excellent-control case -> bridge must add real value or tie/lose
multi-model case -> useful model survives, weak model is set aside
human/high-context review -> reviewer smoothness does not decide alone
```

Boundary follow-up:

```text
research/lane1-bridge-final-consumption-readout-2026-05-15.md
```

Two more probes were run:

```text
real-estate script-only:
  bridge narrow win

speculative EV boundary:
  control win
  bridge_adoption_label: smoothed_useful_friction
```

This is the most useful update so far because it shows the system can reject the
bridge when it smooths away a hard boundary. In the speculative EV case, the
control preserved the sharper stop-rule:

```text
no concrete access, no $12,000 spend
```

The bridge correctly avoided fake EV math, but softened the force of the answer.
That is not good enough. This should remain a core promotion blocker:

```text
bridge loses when it turns a hard source-grounded stop-rule into cleaner,
softer prose
```

Updated state:

```text
3 narrow bridge wins
1 control win on a boundary case
```

Decision remains unchanged:

```text
keep local research candidate
do not promote
test more negative and excellent-control cases
```

Hard-stop v2 follow-up:

```text
speculative EV hard-stop repair:
  bridge narrow win
  preserved: no concrete access, no $12,000 spend

speculative EV concrete-access relaxation:
  tie
  preserved: old hard no relaxes after two confirmed relevant meetings
  preserved: no numerical EV and no spend unless the downside plan survives
```

This is the clearest current shape:

```text
the bridge is valuable when it preserves source-grounded friction
the bridge is dangerous when it makes friction sound nicer
the bridge must be allowed to change the boundary when source facts change
the bridge must tie or lose when the control already reasons well
```

The research prompt now explicitly says:

```text
If the bridge context names a hard stop-rule, preserve it as a hard boundary
unless the conversation gives new evidence that changes it; do not soften it
into general caution.
```

Decision still remains unchanged:

```text
keep local research candidate
do not promote
```

Multi-lane handoff reminder:

```text
Lane 1 bridge is one advisory artifact, not the full final context.
```

The final Claude Code, Codex, or other orchestrator will likely receive a
bundle, not a single bridge card:

```text
Lane 1 tendency reasoning
Lane 2 mental-model / canonical support
deterministic affinities and antagonists
other lane findings
other subagent worker artifacts
task-specific user constraints
```

This changes what "good" means. A bridge card can be good in isolation and bad
inside the bundle if it consumes too much attention or repeats what another lane
already carries.

Updated doctrine:

```text
optimize the final handoff, not any single artifact
```

Each artifact should therefore carry:

```text
local reason for inclusion
source-grounded boundary
relaxation or discard condition
priority humility
```

Priority humility means:

```text
this artifact explains why it may matter
it does not claim the final answer should revolve around it
```

First bundled-handoff result:

```text
speculative EV concrete-access bundled probe:
  control wins narrowly
```

Bundle:

```text
control = selected-model context + other lane opportunity-cost artifact
bridge  = same bundle + Lane 1 bridge
```

Why this matters:

```text
the other lane artifact already carried the key friction
```

It preserved the contractor-help alternative, onboarding, three pilots, and the
rule that confirmed meetings are access but not funding probability. The bridge
was correct, but mostly repeated the bundle. The reviewer preferred the control
because it preserved the concrete opportunity cost more explicitly.

Updated doctrine:

```text
isolated bridge quality is insufficient
the bridge must earn attention inside a bundle
```

Practical implication:

```text
if another lane already carries the stronger source-grounded pressure,
the Lane 1 bridge should become quiet, redundant, or lower priority
```

Reasoning Bundle v1 follow-up:

```text
research/reasoning-bundle-v1-pre-step6-handover-2026-05-15.md
```

The local bundle path now models the actual final boss more directly:

```text
Claude Code / Codex receives multiple artifacts
Claude Code / Codex rethinks its standpoint
Claude Code / Codex chooses what to use, reject, demote, or keep private
```

The first valid bundle had:

```text
primary: opportunity-cost pressure
lower-priority duplicate/support: expected-value bridge
```

The answer preserved the useful friction without public machinery:

```text
concrete access exists
but do not spend most remaining cash unless the known revenue path survives
```

This is closer to the target than isolated bridge testing because it treats
Step 6 as an arbiter of noisy evidence, not a passive consumer of cards.

Updated doctrine:

```text
not-smoothed private context is acceptable
unstructured clutter is not
the bundle must explain why each artifact exists and how to demote it
```

Live follow-up confirms the distinction:

```text
raw context can be useful
indexed context is for arbitration under clutter
```

In the speculative EV case, the raw subagent answer was also good. That means we
should not claim the bundle is magic. The value claim is narrower:

```text
when multiple artifacts compete for attention, the bundle gives the final
reasoner a map of priority, duplication, conflict, boundary, relaxation, and
discard conditions
```

This preserves the bigger doctrine:

```text
cognition and flexibility belong in the final reasoner
deterministic structure should prepare and present, not decide the answer
```

Bevelin's strongest current role is compatible with that doctrine:

```text
Bevelin-style workers produce evidence gates and boundaries
Step 6 decides how much those gates matter in the whole case
```

Conflict/overload follow-up refined the doctrine:

```text
raw artifacts with humility fields can already support good reasoning
```

This means the system should not rely only on a central bundle layer to create
discipline. Discipline should exist at two levels:

```text
inside each artifact:
  why it matters
  when to relax
  when to discard
  risk if forced

across the bundle:
  what is primary
  what is duplicate
  what conflicts
  what is quiet
```

The final reasoner remains the cognition point. The deterministic system helps
prepare a better surface for reasoning; it does not replace reasoning.

## Cases Are Only Reasoning Fixtures

Do not treat successful or failed examples as domain lessons.

The founder-retreat example is not about founder retreats. A legal-adjacent
example would not be about law. A parenting example would not be about
parenting.

Each example is useful only if it exposes an abstract reasoning move:

```text
relaxing a rule
preserving a boundary
demoting duplicates
holding conflict
discarding weak pressure
avoiding overclaim
compressing noisy worker output for a final reasoner
```

This distinction matters because Lolla is not trying to deterministically solve
the factual state of the case. It is trying to create a better structure for
LLM cognition: the final reasoner should understand why something was surfaced,
what to do with it, and when to reject it.
