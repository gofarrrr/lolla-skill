# Plan: Reasoning Substrate Affordance Transaction Handover

> Date: 2026-05-08
> Audience: future decoder / implementation session with no prior chat context
> Status: planning handover only; do not implement without explicit approval
> Current repo: `/Users/marcin/Desktop/Apps/lolla-skill`
> Current substrate assumption: latest compiled affordance artifact, currently `data/compiled/model_affordances/affordances_v18.json`

## Purpose

Build a careful path for using reviewed affordance cards as a reasoning
addendum without turning them into mental-model theater.

The goal is not to force the LLM to use curated cards. The goal is to make sure
the LLM gives every nominated card a fair, high-standard hearing:

- use it when it creates a concrete reasoning delta;
- reject it only with grounded, inspectable reasons;
- defer it when it may matter but the case evidence is not present;
- preserve a ledger so reviewers can see what happened under the hood.

The central doctrine:

> The LLM has freedom of conclusion, but not freedom from consideration.

## Current Grounding

Read these files before implementation:

- `SKILL.md`
  - Current doctrine: Codex is a pure orchestrator. Semantic judgment runs
    through OpenRouter prompts. Four lanes exist: structural pressure, model
    companion, frame pressure, and structural coverage.
- `HOW_IT_WORKS.md`
  - Current trust order: canonical markdown, curated JSON, compiled graph,
    embeddings, runtime LLM judgment.
  - Current split: LLMs detect patterns, embeddings suggest candidates,
    deterministic graph code routes and packages curated material.
- `engine/system_b/pipeline.py`
  - Current runtime orchestrator. Do not modify live runtime path in the first
    implementation slice.
- `engine/system_b/ir_constructor.py`
  - Current deterministic conversation IR constructor.
- `engine/system_b/reasoning_substrate_packet.py`
  - Existing dormant packet builder. It already packages explicit nominations
    into `reasoning_substrate_packet.v1`.
- `engine/system_b/reasoning_substrate_packet_review.py`
  - Existing review-only Markdown renderer. It rejects non-dormant packets.
- `references/model-affordance-extraction.md`
  - Defines affordances as operational contracts, not definitions or topic
    tags.
- `research/enriched-mental-model-packet-strategy-2026-05-06.md`
  - Existing architecture correction: lanes pull shelves, deterministic code
    enriches cards, LLM reasons.
- `research/reasoning-substrate-packet-v1-spec-2026-05-06.md`
  - Current packet spec and non-goals.
- `research/reasoning-substrate-lane-placement-audit-2026-05-06.md`
  - Placement decision: future packet producer belongs after existing lanes,
    next to route-trace serialization. It is not a fifth lane.
- `research/pr11-gate4-edge-probe-brief-2026-05-05.md`
  - Prior experiment pattern for activation calls, set-asides, edge probes, and
    validated affordance traces.
- `research/pr54-controlled-final-graph-only-enrichment-report-2026-05-08.md`
  - Current full-corpus coverage report. PR54 completes reviewed
    source-backed coverage for all 222 runtime shelves, but still does not
    runtime-promote affordances.
- `data/compiled/model_affordances/affordances_v18.json`
  - Current compiled reviewed affordance artifact: 222 records, 258
    affordances, 429 absence records, `draft_review_only`.

## Non-Goals

Do not use this plan to:

- change live `/lolla` behavior;
- change `scripts/run_pipeline.py`;
- import packet review modules into `engine/system_b/pipeline.py`;
- change lane prompts;
- add user-facing Decision Pressure copy;
- make deterministic code select final wisdom, final pressure, final wording, or
  final mental-model usage;
- infer new affordances from source text;
- turn every nominated card into visible output;
- score answer quality with regexes;
- demote LLM reasoning into a schema-filling exercise.

## Design Principle

The affordance packet should be treated as a silver platter, not a verdict.

The deterministic system may:

- validate artifact shape;
- cap packet size;
- preserve source custody;
- attach graph context;
- attach reviewed affordance snippets;
- preserve absence records;
- render review-only inspection views;
- validate returned ledger shape and trace IDs.

The LLM / decoder owns:

- semantic use, rejection, or deferral;
- card merging;
- prioritization;
- deciding whether the card changes the final answer;
- deciding whether the model name should be visible to the user;
- final wording.

## Target User Story

As a reviewer or future runtime decoder, I want to hand the LLM a compact set of
curated reasoning cards, then inspect how each card was handled, so that the
system can benefit from reviewed cognitive affordances without forcing
decorative mental-model usage.

## Durable Decisions

- **Packet placement**: after existing lane outputs, next to route-trace or
  review-only serialization. Not a fifth lane.
- **Initial status**: `draft_review_only` and `runtime_dormant`.
- **Affordance source**: latest compiled artifact under
  `data/compiled/model_affordances/affordances_v*.json`.
- **Source custody**: exact source quotes remain validated by the existing
  affordance compiler and schema tests.
- **Card count**: keep the normal target near 5-12 candidate model cards.
- **Snippet count**: keep 1-3 high-value snippets per card unless later eval
  proves more is worth the burden.
- **Decision vocabulary**: every card transaction resolves to `used`,
  `rejected`, or `deferred`.
- **Visibility rule**: the final user answer does not need to name a mental
  model. Silent application is preferred when naming adds no value.

## Proposed Object Model

### Existing Input: Candidate Card

The current packet builder already produces:

```json
{
  "card_id": "card-001-power-dynamics",
  "model_id": "power-dynamics",
  "display_name": "Power Dynamics",
  "pulled_by": ["lane3_frame_route"],
  "why_pulled": [],
  "coverage_status": "reviewed_affordance_available",
  "source_custody": {},
  "runtime_graph_fields": {},
  "reviewed_affordance_fields": {},
  "absence_records": [],
  "do_not_overclaim": [],
  "llm_instruction": "Consider, merge, set aside, or ignore. Do not force use."
}
```

This should remain valid for backward compatibility.

### Required Improvement: Preserve Per-Affordance Grouping

Current `reviewed_affordance_fields` flattens fields across affordances. That is
useful for compact review, but it is too lossy for a decoder that must explain
which affordance was used, rejected, or deferred.

Add an optional field while preserving the old flat field:

```json
{
  "reviewed_affordance_cards": [
    {
      "affordance_id": "power-dynamics.outside-option-credibility",
      "status": "supported",
      "confidence": "high",
      "activation_shape": {
        "use_when": [],
        "do_not_use_when": [],
        "case_evidence_needed": []
      },
      "treatment_requirements": [
        {
          "requirement_id": "outside-option-map",
          "description": "Separate formal authority from actual ability to walk away.",
          "evidence_required": [],
          "good_output_shape": []
        }
      ],
      "diagnostic_questions": [],
      "misuse_guards": [],
      "source_evidence": []
    }
  ]
}
```

Rules:

- Keep `reviewed_affordance_fields` for current renderers and tests.
- Add `reviewed_affordance_cards` for exact transaction traceability.
- Do not add affordance cards for graph-only, missing, source-too-thin, or
  absence-only material unless the reviewed record contains actual supported
  affordances.
- Include `affordance_id` on treatment requirements in the new grouped object.
- Cap by the same `snippet_target_max_per_card`.
- Do not rank affordances semantically in Python. Preserve record order unless a
  later evaluation proves a deterministic ordering rule is needed.

### New Output: Card Transaction Ledger

The decoder should return an observatory/review-only ledger:

```json
{
  "ledger_version": "card_transaction_ledger.v1",
  "packet_id": "same-packet-id",
  "status": "draft_review_only",
  "runtime_policy": "runtime_dormant",
  "card_transactions": [
    {
      "card_id": "card-001-power-dynamics",
      "model_id": "power-dynamics",
      "disposition": "deferred",
      "effect_type": "diagnostic_question",
      "affordance_ids_considered": [
        "power-dynamics.outside-option-credibility"
      ],
      "strongest_plausible_application": "The case may treat formal agreement as control while practical walk-away power differs.",
      "grounding_check": {
        "case_quote": "",
        "evidence_status": "missing",
        "missing_evidence": [
          "each party's outside options",
          "irreversible commitments already made"
        ]
      },
      "decision_reason": "The card may matter, but the transcript does not reveal alternatives or lock-in.",
      "risk_if_forced": "Would imply hidden power asymmetry without evidence.",
      "residue": "Ask about walk-away alternatives and reversibility.",
      "final_answer_delta": "Add one question about outside options; do not assert a power imbalance.",
      "final_answer_visibility": "visible_question"
    }
  ],
  "summary": {
    "used_count": 0,
    "rejected_count": 0,
    "deferred_count": 1,
    "visible_delta_count": 1,
    "silent_delta_count": 0,
    "no_effect_count": 0
  }
}
```

Allowed `disposition` values:

- `used`
- `rejected`
- `deferred`

Allowed `effect_type` values:

- `direct_answer_delta`
- `diagnostic_question`
- `guardrail`
- `counterframe`
- `speculative_probe`
- `no_effect`

Allowed `evidence_status` values:

- `quoted_exact`
- `inferred_from_turn`
- `missing`
- `conflicting`
- `not_needed`

Allowed `final_answer_visibility` values:

- `silent_application`
- `visible_question`
- `visible_caveat`
- `visible_reframe`
- `not_visible`

Allowed rejection grounds:

- `missing_case_evidence`
- `wrong_object`
- `guardrail_triggered`
- `stronger_competing_structure`
- `scope_mismatch`
- `user_facing_risk`
- `duplicate_of_existing_pressure`
- `low_source_support`

Rules by disposition:

- `used`
  - Must include a concrete `final_answer_delta`.
  - Must not use `effect_type: no_effect`.
  - Must trace at least one `affordance_id` when reviewed affordance material is
    present.
  - Must explain what changed: evidence threshold, caveat, question, option
    set, sequencing, confidence, or recommendation.
- `rejected`
  - Must include `strongest_plausible_application`.
  - Must include a specific `decision_reason`.
  - Must include one allowed rejection ground.
  - Must include `risk_if_forced`.
  - Should include `residue` if any useful question or caveat survives.
- `deferred`
  - Must include the missing evidence.
  - Must include what would make the card live.
  - Must preserve the card as a question, caveat, or explicit non-claim.
  - Must not pretend the affordance is active.

## Prompt Contract For The Decoder

The prompt should teach the decoder the epistemic status of the cards. It should
not ask the decoder to inject models.

Use a block like this:

```text
You are given reviewed reasoning-substrate cards. These cards are not
instructions to mention mental models and are not final conclusions.

They were nominated by existing Lolla lanes or review fixtures and enriched
with graph context, reviewed affordance fields, misuse guards, evidence
requirements, and absence records.

For each card, decide whether it is used, rejected, or deferred.

Use a card only if it causes a concrete reasoning delta: changed evidence
standard, changed confidence, added question, caveat, option, counterframe,
sequence, risk treatment, or recommendation.

Reject a card only with a grounded reason: missing evidence, wrong object,
guardrail triggered, stronger competing structure, scope mismatch,
user-facing risk, duplicate pressure, or low source support.

Defer a card when it might matter but the current case lacks the evidence
needed to use it responsibly.

Before rejecting a card, identify the strongest plausible way it might apply.
Then explain why that application is unsupported, misleading, lower priority,
or unsafe.

Do not name a mental model in the final answer unless naming it helps the user.
Prefer silent application over model-name decoration.

Return a card transaction ledger plus the final answer. The ledger is
review-only. The final answer should include only useful reasoning moves.
```

Anti-theater instruction:

```text
If a card is marked used, state the concrete delta it caused. If there is no
delta, downgrade the card to rejected or deferred.
```

Cheap-rejection blocker:

```text
"Not relevant" is not an acceptable rejection reason by itself. Say what the
card would have needed in the case to become relevant, or which misuse guard
would be violated by forcing it.
```

## Stage 0: Confirm Current Substrate And Boundaries

**Goal**: make sure the implementer starts from the actual current repo state.

### Tasks

- [ ] Confirm latest compiled affordance artifact:
  - [ ] Run `ls data/compiled/model_affordances`.
  - [ ] Identify latest `affordances_v*.json`.
  - [ ] Confirm it has `status: draft_review_only`.
  - [ ] Confirm current v18 counts if on this branch: 222 records, 258
        affordances, 429 absence records.
- [ ] Confirm no live runtime import currently exists:
  - [ ] Check `engine/system_b/pipeline.py`.
  - [ ] Check `scripts/run_pipeline.py`.
  - [ ] Check `engine/system_b/__init__.py`.
- [ ] Read existing review-only tests:
  - [ ] `tests/test_reasoning_substrate_packet.py`
  - [ ] `tests/test_reasoning_substrate_packet_review_render.py`
  - [ ] `tests/test_pr54_batch17_records.py`

### Acceptance Criteria

- [ ] Implementer can state which affordance artifact is current.
- [ ] Implementer can state that affordances are still dormant.
- [ ] Implementer can state that the first slice must not touch live pipeline
      behavior.

## Stage 1: Extend Packet Shape Without Runtime Promotion

**Goal**: add enough grouped affordance detail for later decoder transactions,
without changing live behavior or existing review render contract.

### Likely Files

- `engine/system_b/reasoning_substrate_packet.py`
- `tests/test_reasoning_substrate_packet.py`
- New or updated fixture under `tests/fixtures/reasoning_substrate_packet/`

### Tasks

- [ ] Add optional `reviewed_affordance_cards` to candidate cards.
- [ ] Preserve existing `reviewed_affordance_fields` exactly enough that old
      tests still pass.
- [ ] For every included affordance card:
  - [ ] Include `affordance_id`.
  - [ ] Include `status`.
  - [ ] Include `confidence`.
  - [ ] Include grouped `activation_shape`.
  - [ ] Include grouped `treatment_requirements`.
  - [ ] Include grouped `diagnostic_questions`.
  - [ ] Include grouped `misuse_guards`.
  - [ ] Include grouped `source_evidence`.
- [ ] Add tests proving:
  - [ ] grouped affordance cards are present for reviewed cards;
  - [ ] grouped affordance cards preserve exact `affordance_id`;
  - [ ] treatment requirements remain traceable to an affordance;
  - [ ] graph-only cards do not get fake affordance cards;
  - [ ] source-too-thin and absence-only cards do not invent affordances;
  - [ ] packet status remains `draft_review_only`;
  - [ ] runtime policy remains `runtime_dormant`;
  - [ ] live runtime files do not import the packet review or decoder modules.

### Acceptance Criteria

- [ ] Existing packet tests pass.
- [ ] New grouped-affordance tests pass.
- [ ] No user-facing output changes.
- [ ] No pipeline import changes.

## Stage 2: Define Card Transaction Ledger Schema

**Goal**: create a strict, review-only output contract for how the decoder
handled each card.

### Likely Files

- New: `engine/system_b/card_transaction_ledger.py`
- New: `tests/test_card_transaction_ledger.py`
- Optional: `data/schemas/card_transaction_ledger.schema.json`
- Optional: `research/card-transaction-ledger-v1-spec-2026-05-08.md`

### Tasks

- [ ] Implement dataclass or validation functions for
      `card_transaction_ledger.v1`.
- [ ] Validate top-level fields:
  - [ ] `ledger_version`
  - [ ] `packet_id`
  - [ ] `status`
  - [ ] `runtime_policy`
  - [ ] `card_transactions`
  - [ ] `summary`
- [ ] Validate every transaction:
  - [ ] `card_id` must exist in the packet.
  - [ ] `model_id` must match that card.
  - [ ] `disposition` must be allowed.
  - [ ] `effect_type` must be allowed.
  - [ ] `final_answer_visibility` must be allowed.
  - [ ] `affordance_ids_considered` must exist on that card when non-empty.
- [ ] Validate `used` rules:
  - [ ] non-empty `final_answer_delta`;
  - [ ] not `effect_type: no_effect`;
  - [ ] at least one considered affordance for reviewed cards unless the card
        is graph-only.
- [ ] Validate `rejected` rules:
  - [ ] non-empty `strongest_plausible_application`;
  - [ ] allowed `rejection_ground`;
  - [ ] non-empty `risk_if_forced`.
- [ ] Validate `deferred` rules:
  - [ ] `grounding_check.evidence_status` is `missing`, `conflicting`, or
        `inferred_from_turn`;
  - [ ] non-empty `missing_evidence` or non-empty `residue`;
  - [ ] no false activation claim.
- [ ] Compute summary counts mechanically.

### Deterministic Code Must Not

- [ ] Judge whether the semantic reason is good.
- [ ] Decide whether the LLM should have used a card.
- [ ] Rewrite ledger rationales.
- [ ] Promote ledger output to user-facing copy.

### Acceptance Criteria

- [ ] Invalid IDs fail validation.
- [ ] Missing required disposition fields fail validation.
- [ ] A ledger can say all cards were rejected or deferred if the reasons are
      structurally valid.
- [ ] The validator is shape-and-trace only, not semantic judging.

## Stage 3: Create Decoder Prompt Fixture

**Goal**: test the card transaction contract offline before any runtime
integration.

### Likely Files

- New: `research/card-transaction-decoder-prompt-v1-2026-05-08.md`
- New: `tests/fixtures/card_transaction_decoder/`
- Optional script later:
  - `scripts/run_card_transaction_decoder_fixture.py`

### Tasks

- [ ] Write the decoder prompt using the prompt contract above.
- [ ] Include a compact packet fixture with:
  - [ ] at least one reviewed affordance card;
  - [ ] at least one graph-only or weak-support style card if available on
        older branches;
  - [ ] at least one absence record;
  - [ ] at least one card that should be deferred.
- [ ] Require the decoder to output:
  - [ ] `card_transaction_ledger`;
  - [ ] optional `final_answer_draft`;
  - [ ] no public mental-model list unless useful.
- [ ] Require exact-card accounting:
  - [ ] every candidate card gets one transaction;
  - [ ] no transaction for a missing card;
  - [ ] suppressed candidates are not recovered as pressures.

### Acceptance Criteria

- [ ] Fixture output contains one transaction per candidate card.
- [ ] Fixture output contains concrete deltas for used cards.
- [ ] Rejected cards include strongest plausible application and risk if
      forced.
- [ ] Deferred cards preserve useful questions or caveats.
- [ ] Final answer can be shorter than the ledger and does not need to expose
      machinery.

## Stage 4: Add Review-Only Ledger Renderer

**Goal**: make the under-the-hood reasoning inspectable without changing the
user surface.

### Likely Files

- New: `engine/system_b/card_transaction_ledger_review.py`
- New: `tests/test_card_transaction_ledger_review_render.py`
- New checked-in render:
  - `research/card-transaction-ledger-fixture-review-render-2026-05-08.md`

### Tasks

- [ ] Render packet identity:
  - [ ] `packet_id`
  - [ ] ledger version
  - [ ] status
  - [ ] runtime policy
- [ ] Render summary counts:
  - [ ] used
  - [ ] rejected
  - [ ] deferred
  - [ ] visible deltas
  - [ ] silent deltas
  - [ ] no-effect
- [ ] Render transaction table:
  - [ ] card ID;
  - [ ] model ID;
  - [ ] disposition;
  - [ ] effect type;
  - [ ] strongest plausible application;
  - [ ] decision reason;
  - [ ] final answer delta;
  - [ ] residue.
- [ ] Render trace warnings:
  - [ ] unknown affordance ID;
  - [ ] used card with no delta;
  - [ ] rejected card with no rejection ground;
  - [ ] deferred card with no missing evidence.
- [ ] Keep renderer review-only:
  - [ ] reject non-`runtime_dormant` ledgers;
  - [ ] tests prove live runtime paths do not import it.

### Acceptance Criteria

- [ ] Reviewer can tell what was used, rejected, deferred, and why.
- [ ] Renderer does not produce user-facing answer text as product copy.
- [ ] Renderer preserves machinery boundary.

## Stage 5: Offline Evaluation Before Promotion

**Goal**: prove the affordance transaction layer adds value beyond a strong
generic prompt.

### Test Arms

- **Arm A**: existing output without reasoning substrate card transaction.
- **Arm B**: strong generic prompt with model names only.
- **Arm C**: same prompt plus reviewed affordance cards and required
  transaction ledger.

This mirrors the prior PR11 edge-probe design.

### Tasks

- [ ] Select archived cases with varied domains:
  - [ ] decision under uncertainty;
  - [ ] negotiation or power;
  - [ ] execution/follow-through;
  - [ ] framing problem;
  - [ ] personal/professional high-stakes case.
- [ ] For each case, generate the same candidate nominations across arms.
- [ ] Run Arm B and Arm C with the same model, provider, temperature, and token
      budget.
- [ ] Judge outputs with a rubric that rewards:
  - [ ] concrete reasoning delta;
  - [ ] better evidence thresholds;
  - [ ] useful deferrals;
  - [ ] grounded rejection;
  - [ ] fewer unsupported claims;
  - [ ] no name-dropping theater;
  - [ ] final answer usefulness.
- [ ] Judge outputs with a rubric that penalizes:
  - [ ] forced model mentions;
  - [ ] invented case facts;
  - [ ] generic mental-model explanation;
  - [ ] rejecting cards cheaply;
  - [ ] using cards without a delta;
  - [ ] making final answers longer without making them better.

### Minimum Promotion Bar

- [ ] Arm C beats Arm B on decision usefulness in a clear majority of cases.
- [ ] Arm C has fewer cheap dismissals than Arm B.
- [ ] Arm C does not increase hallucinated case facts.
- [ ] At least 80% of used-card traces point to valid card or affordance IDs.
- [ ] Reviewer can understand every rejection or deferral from the ledger.

## Stage 6: Skill-Level Integration Doctrine

**Goal**: teach the skill how to talk about the packet without overclaiming.

### Likely Files

- `SKILL.md`
- `HOW_IT_WORKS.md`
- Possibly a new `references/card-transaction-ledger.md`

### Tasks

- [ ] Add a short doctrine section only after offline evidence exists.
- [ ] Explain that cards are:
  - [ ] reviewed reasoning substrate;
  - [ ] optional but not disposable;
  - [ ] use/reject/defer objects;
  - [ ] not instructions to name mental models.
- [ ] Explain the rejection standard:
  - [ ] name attempted application;
  - [ ] name failed condition;
  - [ ] name risk if forced;
  - [ ] preserve useful residue when possible.
- [ ] Explain the under-the-hood ledger:
  - [ ] what was considered;
  - [ ] what was used;
  - [ ] what was rejected;
  - [ ] what was deferred;
  - [ ] what changed in the final answer.
- [ ] Keep all language clear that semantic judgment remains with the LLM.

### Acceptance Criteria

- [ ] Skill docs make the layer understandable to future operators.
- [ ] Skill docs do not imply deterministic wisdom selection.
- [ ] Skill docs do not tell Codex to do semantic card selection itself.

## Stage 7: Optional Review-Only Runtime Adapter

**Goal**: only after offline validation, attach the packet and ledger to a
review-only run artifact without changing user-facing output.

### Likely Files

- New adapter near route-trace serialization.
- Do not start in `pipeline.py` unless previous stages prove the design.
- Possible output under run artifacts:
  - `reasoning_substrate_packet.json`
  - `card_transaction_ledger.json`
  - `card_transaction_review.md`

### Tasks

- [ ] Define where existing lane nominations are collected.
- [ ] Convert lane outputs into explicit `CandidateNomination` objects.
- [ ] Build `reasoning_substrate_packet.v1` with latest affordance artifact.
- [ ] Send packet to decoder only when an explicit review flag is enabled.
- [ ] Validate returned ledger.
- [ ] Write ledger to run artifacts.
- [ ] Do not change final answer.
- [ ] Do not change memo.
- [ ] Do not change Observatory unless a separate UI review slice is approved.

### Acceptance Criteria

- [ ] Review flag off: byte-identical or behavior-identical live output.
- [ ] Review flag on: additional artifacts only.
- [ ] Ledger validates shape and trace IDs.
- [ ] No user-facing card copy appears.

## Stage 8: Promotion Gate For User-Facing Use

**Goal**: define what must be true before any visible answer uses the card
transaction output.

### Required Evidence

- [ ] Offline Arm C beats Arm B.
- [ ] Review-only runtime artifacts show useful card handling on real runs.
- [ ] Cheap rejection rate is low.
- [ ] Forced-use theater rate is low.
- [ ] Hallucinated case-fact rate does not increase.
- [ ] Final answers get shorter or clearer where possible, not merely more
      elaborate.
- [ ] Users or reviewers can understand why a card was used, rejected, or
      deferred.

### Promotion Rules

- [ ] Promote only the final reasoning delta, not the machinery.
- [ ] Keep ledger inspectable but not user-facing by default.
- [ ] Never require a mental model name in the answer.
- [ ] Allow zero-card visible output.
- [ ] Allow all cards to be deferred or rejected.
- [ ] Keep deterministic code out of final semantic selection.

## Implementation Order

Recommended sequence:

1. Stage 0: confirm current substrate.
2. Stage 1: grouped affordance cards in dormant packet.
3. Stage 2: ledger schema and validator.
4. Stage 3: decoder prompt fixture.
5. Stage 4: review-only renderer.
6. Stage 5: offline evaluation.
7. Stage 6: update skill doctrine.
8. Stage 7: review-only runtime adapter.
9. Stage 8: possible promotion.

Do not skip from Stage 1 to live runtime. The whole point is to learn whether
the ledger creates useful, grounded reasoning rather than merely prettier
explanations.

## Verification Checklist

For any future PR implementing part of this plan:

- [ ] `pytest tests/test_reasoning_substrate_packet.py`
- [ ] `pytest tests/test_reasoning_substrate_packet_review_render.py`
- [ ] `pytest tests/test_model_affordance_schema.py`
- [ ] `pytest tests/test_model_affordance_compiler.py`
- [ ] New card transaction ledger tests.
- [ ] New review renderer tests.
- [ ] Grep live runtime paths to prove no forbidden import.
- [ ] Confirm generated packet remains `draft_review_only`.
- [ ] Confirm generated ledger remains `runtime_dormant`.
- [ ] Confirm no user-facing prose field is introduced in packet builder.

## Open Questions For Product Review

- Should `deferred` cards be allowed to create visible questions in the final
  answer, or should they remain reviewer-only at first?
- Should the decoder see suppressed candidates, or only the packet builder's
  summary of suppression?
- Should graph-only cards on older branches be eligible for transaction ledger
  entries, or should ledger entries be limited to reviewed affordance cards?
- Should the final answer be generated in the same decoder call as the ledger,
  or should the ledger be a first pass consumed by a second answer-writer call?
- Should the ledger be hidden from normal Observatory users and exposed only in
  a debug/review mode?

## Final Doctrine For The Decoder

Do not make the cards mandatory. Make them costly to dismiss cheaply.

The desired behavior is:

- high freedom;
- high accountability;
- no forced use;
- no casual rejection;
- no model-name decoration;
- source-backed affordance handling;
- inspectable under-the-hood ledger;
- final answer that only reflects genuine reasoning deltas.
