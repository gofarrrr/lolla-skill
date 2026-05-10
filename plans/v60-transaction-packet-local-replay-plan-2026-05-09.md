# Plan: V60 Transaction Packet Local Replay Lab

> Date: 2026-05-09
> Status: local dry-run slice implemented on `feat/v60-transaction-local-replay-lab`; not runtime integration
> Posture: dormant, offline, review-only
> Primary source authority: canonical Markdown via `data/model_sources/manifest.json`
> Explicit affordance artifact: `data/compiled/model_affordances/affordances_v60.json`

## Objective

Create a local replay lab that can test whether v60 grouped affordance cards and
absence records are useful internal consideration material for the skill-using
LLM.

The lab should answer this question:

> Given the same conversation, vanilla answer, and existing lane pressure, can a
> decoder use, reject, defer, or privately absorb grouped source-backed v60
> transactions in a way that creates useful reasoning opportunities without
> overfeeding, over-authorizing, or forcing public model theater?

The answer can be "no" on some cases. That is useful evidence.

## 2026-05-09 Execution Update

The first local slice now exists on branch
`feat/v60-transaction-local-replay-lab`.

Implemented:

- grouped `reviewed_affordance_cards` in the dormant packet builder;
- backward-compatible `reviewed_affordance_fields`;
- grouped-card rendering in the review-only Markdown renderer;
- review-only card transaction ledger schema and validator;
- dry-run replay harness for Arm A, Arm B, and Arm C prompt packets;
- compact decoder-facing Arm C packet projection, with full packet retained for
  audit;
- eight-case replay manifest with BATNA and price-discrimination probes;
- generated preflight artifacts under
  `data/evaluations/v60_transaction_replay_lab/2026-05-09-preflight/`;
- expanded configuration matrix artifacts under
  `data/evaluations/v60_transaction_replay_lab/2026-05-09-matrix/`;
- preflight report under
  `research/v60-transaction-replay-preflight-report-2026-05-09.md`.
- matrix report under
  `research/v60-transaction-replay-matrix-report-2026-05-09.md`.

No paid model calls were made. No live `/lolla`, Step 6, Step 8, memo, or
Observatory path was changed.

The dry run exposed two blockers and resolved one locally:

- every case hit the 12-card cap and suppressed six candidates;
- the first uncompressed Arm C shape was roughly 42k-50k estimated tokens;
- the compact Arm C shape is now roughly 12.8k-18.8k estimated tokens, with
  compact card views around 9k-10.4k.

The expanded matrix suggests `cap8_focused` as the first product-shaped pilot
config and `cap12_default_compact` as a research comparison. It also separates
three solution modes that should not be collapsed: answer revision, edge audit,
and question gate.

## 2026-05-10 C4.3 Reframe

C4.2 proved that v60 can sometimes create a useful public edge, but it also
made the product frame too narrow. The next lab question is not "can v60 add one
edge?" It is:

> Was this v60 material useful for Claude Code / Codex to consider, even if it
> was rejected, deferred, kept private, or produced no visible answer change?

The harness now supports:

```bash
--c-variant consideration_router
```

This variant keeps v60 internal to the reasoning model. Arm C returns normal
public answer fields for blind comparison, plus a private
`consideration_usefulness_report` that assesses every candidate card.

The private report records:

- `packet_usefulness`: `useful`, `mixed`, `not_useful`, `overfed`, or
  `underfed`;
- one `chunk_assessment` per candidate card;
- `usefulness_to_consider`: `high`, `medium`, `low`, or `none`;
- `opportunity_role`: frame changer, evidence gate, diagnostic question,
  guardrail, tension maker, boundary marker, compression aid, or rejection aid;
- `route`: private reasoning, public answer delta, diagnostic question,
  evidence gate, guardrail, defer missing evidence, reject irrelevant, or reject
  duplicate;
- up to three selected opportunities;
- retrieval feedback about what would have made the packet more useful.

This is deliberately not a user-facing surface. It is a measurement layer for
the same problem the lanes already face: we do not know truth with certainty; we
can only decide what deserves consideration, then study whether the LLM handled
that consideration responsibly.

The qmd-inspired lesson is hybrid, context-aware selection: lexical matching,
semantic retrieval, context metadata, reranking, and score traces should
eventually help choose affordance and absence chunks. But v60 must keep Lolla's
trust order: embeddings suggest and explain; they do not decide.

## Non-Goals

This plan must not:

- change live `/lolla` behavior;
- import the packet lab into `engine/system_b/pipeline.py`;
- change lane prompts;
- change Step 6, Step 8, memo, or Observatory output;
- auto-select the latest affordance artifact;
- infer new affordances from canonical Markdown;
- add case-specific routing exceptions;
- decide semantic card usefulness in Python;
- reward visible mental-model naming as success.

## Core Design Commitments

- Use `affordances_v60.json` explicitly.
- Treat `data/model_sources/manifest.json` as the local source-custody anchor.
- Preserve canonical Markdown authority over compiled artifacts.
- Keep deterministic code as courier and validator, not judge.
- Keep LLM output accountable through a ledger, not obedient through a forced
  usage prompt.
- Test against strong baselines.
- Report instability rather than hiding it.
- Prefer general mechanisms over case fixes.

## Test Objects

### Case Artifact

Each replay case should have:

- case ID;
- captured conversation text;
- vanilla answer or archived assistant answer;
- extraction JSON if available;
- existing pipeline result if available;
- candidate nominations;
- packet build metadata;
- replay outputs;
- ledger outputs;
- judge or reviewer results.

### Candidate Nomination

For the first lab slice, nominations may be explicit fixtures. Later slices can
adapt existing lane outputs. The nomination shape should preserve:

- `model_id`
- `pulled_by`
- `why_pulled`
- `lane_order`
- `lane_score` when available
- provenance entries for every contributing lane

Dedupe must merge provenance before packet construction.

### Grouped Card

Each reviewed card should preserve grouped affordance identity:

- `affordance_id`
- `status`
- `confidence`
- `activation_shape`
- `treatment_requirements`
- `diagnostic_questions`
- `misuse_guards`
- `source_evidence`

The old flat `reviewed_affordance_fields` may remain for compatibility, but the
decoder-facing transaction unit is the grouped affordance card.

### Absence Blocker

Each candidate card should make absence records visible as possible blockers:

- attempted field;
- status;
- reason;
- source evidence when present;
- runtime policy;
- what claim or split this absence should block.

If the lab cannot yet infer "what claim this blocks" without semantic judgment,
leave the field empty and let the decoder account for the absence record.

### Ledger

Every candidate card gets one transaction:

- `used`
- `rejected`
- `deferred`

No `merged` disposition. Merge is metadata.

## Replay Arms

### Arm A: Vanilla

The original answer, or a fresh strong answer to the captured conversation with
no Lolla pressure.

Purpose: preserve the baseline the user would otherwise receive.

### Arm B: Strong Generic Pressure

A strong reconsideration prompt with current case context and possibly model
names or existing Lolla-style pressure, but no grouped v60 affordance cards.

Purpose: test against "a smart LLM with a good prompt," not against a weak
baseline.

### Arm C: Grouped V60 Transaction Packet

Same case and answer task as Arm B, plus:

- grouped v60 affordance cards;
- absence records;
- confidence and weak-support warnings;
- lane or explicit nomination provenance;
- required use/reject/defer ledger.

Purpose: isolate whether the v60 transaction layer adds useful reasoning
pressure beyond generic prompting.

### Arm C4.3: V60 Consideration Router

Same case and answer task as Arm B, plus compact v60 enrichment. The model must
return public answer fields and a private usefulness report.

Purpose: measure whether selected v60 chunks were worth putting in front of the
reasoning model even when they are not publicly used.

## Measurement Frame

Do not ask "which answer is better?" as the only question. "Better" is too
wide. The lab should first ask whether the selected material was useful to
consider.

Use narrower comparison dimensions:

- useful-to-consider packet quality;
- correct use, rejection, deferral, or private-only handling;
- non-obvious edge surfaced;
- overclaim reduced;
- evidence threshold improved;
- hidden trade-off named;
- confidence calibrated;
- useful question added;
- option set or sequence improved;
- card rejected with grounded reason;
- card deferred into useful residue;
- card kept private as a guardrail or compression aid;
- final answer stayed case-faithful;
- final answer avoided model-name theater;
- final answer avoided invented facts;
- final answer length did not grow without value.

The strongest promotion evidence is not "C used more cards" or even "C visibly
changed the answer." It is "C handled the packet responsibly: it used, rejected,
deferred, or privately absorbed source-backed cognition in a way that a reviewer
can understand and would trust more than unmanaged prompting."

The lab cannot fully know future user value. It can only test whether the
reasoning product becomes more edge-aware, more source-disciplined, more useful
under uncertainty, and less prone to generic confidence. Later product work can
measure user experience directly. This lab should not overfit to imagined user
preference.

## Phase 0: Documentation And Fixtures Only

Goal: make the target explicit before code changes.

Tasks:

- [ ] Mark the 2026-05-08 handover as stale for implementation.
- [ ] Add this v60 local replay plan.
- [ ] Add the v60 handover addendum.
- [ ] Choose initial archived cases, but do not run model calls.
- [ ] Write a no-runtime-promotion checklist.

Acceptance:

- [ ] Future implementer can state the current artifact is v60.
- [ ] Future implementer can state canonical Markdown is the semantic root.
- [ ] Future implementer can state this is not `/lolla` integration.

## Phase 1: Case Selection And Pre-Registration

Goal: choose cases without cherry-picking for visible wins.

Initial case slate should cover:

- decision under uncertainty;
- negotiation or power;
- execution or follow-through;
- framing problem;
- personal/professional high-stakes decision;
- absence-heavy nomination set;
- weak-support or medium-confidence candidate if possible;
- broad/meta-heavy candidate packet;
- narrow/no-meta packet.

Preferred sources:

- archived `/lolla` runs;
- `research/test-cases/`;
- `data/treatment_audits/`;
- existing Gate 4 or treatment-audit cases.

Pre-register for each case:

- why included;
- expected risk of generic output;
- expected risk of overfitting;
- candidate nomination source;
- which lane or fixture pulled each model;
- whether the case is used for exploration or held-out review.

Acceptance:

- [ ] At least 6 cases are selected.
- [ ] At least 2 cases are held out from prompt iteration.
- [ ] Case inclusion does not depend on knowing that v60 will win.
- [ ] Case metadata records limitations.

## Phase 2: Static V60 Packet Builder Slice

Goal: build grouped v60 packets from explicit nominations without runtime
pickup.

Likely files:

- `engine/system_b/reasoning_substrate_packet.py`
- new or updated packet tests;
- new fixtures under `tests/fixtures/reasoning_substrate_packet/`;
- generated review artifacts under `research/`.

Tasks:

- [ ] Require explicit `affordances_v60.json` path in lab fixtures.
- [ ] Add `reviewed_affordance_cards` while preserving
      `reviewed_affordance_fields`.
- [ ] Preserve record order unless a later eval justifies another rule.
- [ ] Preserve source custody and source evidence.
- [ ] Make absence records visible and capped.
- [ ] Surface weak-support and medium-confidence warnings.
- [ ] Keep packet status `draft_review_only`.
- [ ] Keep runtime policy `runtime_dormant`.
- [ ] Prove no live runtime import.

Acceptance:

- [ ] Graph-only cards do not get fake affordances.
- [ ] Absence-only cards do not get fake affordances.
- [ ] Grouped cards preserve exact affordance IDs.
- [ ] Treatment requirements are traceable to their affordance.
- [ ] Existing packet tests still pass.

## Phase 3: Ledger Schema And Validator

Goal: make decoder accountability inspectable without judging semantics in
Python.

Likely files:

- `engine/system_b/card_transaction_ledger.py`
- `tests/test_card_transaction_ledger.py`
- optional JSON schema under `data/schemas/`
- review spec under `research/`

Tasks:

- [ ] Validate top-level ledger shape.
- [ ] Validate one transaction per packet card.
- [ ] Validate card IDs and model IDs against the packet.
- [ ] Validate affordance IDs against grouped card contents.
- [ ] Validate enum values.
- [ ] Validate required fields by disposition.
- [ ] Compute summary counts mechanically.
- [ ] Reject non-dormant ledgers.

Disposition requirements:

- `used` requires a concrete final-answer delta.
- `rejected` requires strongest plausible application, rejection ground, and
  risk if forced.
- `deferred` requires missing evidence, residue, or what would make the card
  live.

Acceptance:

- [ ] Validator catches missing IDs and impossible traces.
- [ ] Validator allows all cards to be rejected or deferred.
- [ ] Validator does not score semantic quality.

## Phase 4: Decoder Prompt Fixture

Goal: test the prompt contract locally before running broad evaluation.

Tasks:

- [ ] Write a decoder prompt that frames cards as candidate reasoning
      transactions, not commands.
- [ ] Require use/reject/defer accounting.
- [ ] Require strongest plausible application before rejection.
- [ ] Require risk if forced.
- [ ] Require concrete delta for used cards.
- [ ] Allow silent application.
- [ ] Tell the decoder not to mention mental models unless naming helps the
      user.
- [ ] Include absence records as blockers and overclaim rails.

Acceptance:

- [ ] A fixture ledger validates.
- [ ] A fixture can reject or defer attractive but unsupported cards.
- [ ] Final answer is not a card dump.

## Phase 5: Dry-Run Harness

Goal: generate all packets and prompts without paid model calls.

Likely script:

- `scripts/run_v60_transaction_replay_lab.py`

Suggested modes:

- `--dry-run`
- `--case <id>`
- `--cases-file <path>`
- `--affordances-path data/compiled/model_affordances/affordances_v60.json`
- `--output-dir data/evaluations/v60_transaction_replay_lab`
- `--arms A,B,C`

Dry-run outputs:

- packet JSON;
- prompt JSON or Markdown;
- token estimate;
- case manifest;
- expected ledger shape;
- omitted candidates;
- warnings.

Acceptance:

- [ ] Dry-run requires explicit affordances path.
- [ ] Dry-run writes no user-facing artifacts.
- [ ] Dry-run reports token/cap pressure.
- [ ] Dry-run can run without network access.

## Phase 6: Controlled Model-Call Replay

Goal: run a small controlled A/B/C replay only after dry-run artifacts are
reviewed.

Rules:

- same provider/model across B and C;
- same temperature;
- same token budget;
- same case text;
- same answer task;
- same nominations;
- ledger required only for C;
- model call costs logged.

Multi-run:

- run at least N=3 on selected cases where cost allows;
- use N=5 for one or two instability probes;
- keep held-out cases untouched until prompt is stable.

Acceptance:

- [ ] Outputs are persisted with metadata.
- [ ] Ledger validates before judging.
- [ ] Invalid ledgers are reported, not repaired semantically.
- [ ] Rerun variance is reported.

## Phase 7: Paired Judgment And Human Review

Goal: evaluate C against A and B without pretending there is one deterministic
truth.

Judgment layers:

- structured LLM judge for paired comparison;
- deterministic validation for quotes, IDs, and ledger shape;
- human review for product sense on a small sample.

Judge rubric should ask:

- Which answer better helps the user make or revise the decision?
- Which answer surfaces a non-obvious edge?
- Which answer is less generic?
- Which answer avoids unsupported confidence?
- Which answer preserves the user's actual facts?
- Which answer handles uncertainty better?
- Did C create value traceable to cards or only add ceremony?
- Did C misuse, force, or overexpose mental models?

Report separately:

- decision-usefulness win/loss/tie;
- edge-discovery win/loss/tie;
- overclaim-reduction win/loss/tie;
- theater penalty;
- hallucinated case-fact count;
- cheap-rejection count;
- forced-use count;
- useful-deferral count;
- source-trace validity.

Acceptance:

- [ ] C is compared against B, not only A.
- [ ] Judge does not see arm labels where feasible.
- [ ] Human review can inspect ledger and final answer side by side.
- [ ] Disagreements are preserved in the report.

## Phase 8: Stability And Generalization Report

Goal: decide whether the lab showed a general mechanism or just case luck.

Report:

- per-case outcomes;
- cross-run ledger disposition drift;
- cross-run final-answer delta drift;
- candidate-card usage distribution;
- rejection and deferral quality;
- where C made things worse;
- where absence records prevented overclaim;
- where weak or medium support caused confusion;
- where packet caps removed important material;
- where broad/meta cards became too theatrical.

Generalization questions:

- Did wins concentrate in one domain?
- Did wins depend on one prompt phrase?
- Did C fail on held-out cases?
- Did the same card behave wildly across reruns?
- Did C create better questions even when it did not change recommendations?
- Did the lab reveal routing or nomination problems upstream?

Product-learning questions for later, not for this local lab:

- Did users notice the added reasoning leverage?
- Did users trust the answer more or less?
- Did users prefer visible questions, silent caveats, or named models?
- Did additional pressure make the product feel clearer or heavier?
- Which deltas led users to revise a real decision?

Acceptance:

- [ ] Report names limitations plainly.
- [ ] Report distinguishes useful diversity from noisy drift.
- [ ] Report recommends either continue, revise, or stop.
- [ ] No runtime integration is recommended without evidence.

## Phase 9: Promotion Gate

The local replay lab may recommend a review-only runtime adapter only if:

- Arm C beats Arm B on decision usefulness in a clear majority of reviewed
  comparisons;
- C does not increase hallucinated case facts;
- C does not create frequent forced model use;
- C produces inspectable ledgers with valid traces;
- cheap rejection is rare or visible;
- absence records visibly prevent overclaim;
- held-out cases do not collapse;
- reviewer can understand what changed and why.

Even then, the next integration is review-only artifacts, not user-facing use.

## Proposed Work Slices

### Slice 1: Planning And Fixtures

- update handover docs;
- select cases;
- define case manifest;
- no model calls;
- no runtime changes.

### Slice 2: Grouped Packet Shape

- add grouped cards;
- add tests;
- generate static fixtures;
- no decoder calls.

### Slice 3: Ledger Contract

- add validator;
- add ledger fixtures;
- add review renderer;
- no semantic judging in Python.

### Slice 4: Dry-Run Replay Harness

- assemble packets and prompts;
- estimate tokens;
- write manifests;
- prove explicit v60 artifact discipline.

### Slice 5: Small Controlled Replay

- run limited A/B/C calls after approval;
- validate ledgers;
- persist outputs.

### Slice 6: Evaluation Report

- paired judge;
- human review;
- stability analysis;
- recommendation.

## No-Runtime-Promotion Checklist

Before merging any implementation slice, verify:

- [ ] no import from packet lab into `engine/system_b/pipeline.py`;
- [ ] no import from packet lab into `scripts/run_pipeline.py`;
- [ ] no change to `SKILL.md` runtime instructions unless explicitly planned;
- [ ] no Step 6 or Step 8 behavior change;
- [ ] no memo behavior change;
- [ ] no Observatory UI behavior change;
- [ ] no default "latest affordance" lookup;
- [ ] no user-facing card prose generated by deterministic code;
- [ ] all new artifacts say `draft_review_only` or `runtime_dormant`.

## Decision At End Of Lab

The lab should end with one of three recommendations:

- **Continue**: grouped cards and ledger create real, stable reasoning deltas.
- **Revise**: signal exists, but packet shape, prompt, cap, absence handling, or
  nomination provenance needs work.
- **Stop**: v60 cards add ceremony, instability, or overclaim without enough
  decision value.

Any of these outcomes is acceptable. The only unacceptable outcome is promoting
the layer because the corpus feels valuable and the demo sounds smart.
