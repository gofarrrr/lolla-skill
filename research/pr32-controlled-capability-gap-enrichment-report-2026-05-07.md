# PR32 Controlled Capability-Gap Enrichment Report

**Status:** controlled reviewed enrichment quality loop, dormant/review-only

**Decision label:** `controlled_capability_gap_enrichment_ready`

**Branch:** `feature/reasoning-substrate-pr32-controlled-capability-gap-enrichment`

## Purpose

PR32 follows the PR31 capability audit. It does not extract by corpus-count
momentum. It targets named gaps where the v5 reviewed corpus was light:
delay/obligation discipline, peer review, formal/checklist discipline,
planning/status quo/commitment bias, competitive and bargaining pressure,
product/customer/market lock-in, and cross-cultural communication.

This is not Batch 3b, runtime promotion, a live lane adapter, prompt work,
receiver-side answer generation, or user-facing Decision Pressure. The point is
to read sixteen repo-custodied graph-only sources, extract only source-supported
operational depth, and preserve absence records where a tempting affordance is
not supported.

## Batch Shape

- Target runtime graph models: `16`
- Source-custodied source files used: `16`
- Models already present in v5: `0`
- New batch directory: `data/model_affordances/batch_5/`
- Batch records added: `16`
- Batch affordances added: `16`
- Batch absence records added: `32`
- Compiled artifact: `data/compiled/model_affordances/affordances_v6.json`
- Compiled artifact status: `draft_review_only`
- v6 compiled model records: `81`
- v6 compiled affordances: `117`
- v6 compiled absence records: `147`
- Runtime graph models still graph-only after v6: `141`
- Source-evidence references in v6 records: `1487`
- Treatment requirements in v6 affordances: `224`
- Diagnostic questions in v6 affordances: `445`
- Misuse guards in v6 affordances: `420`

## Target Selection

| model_id | why selected | source file | outcome | affordances | absences |
| --- | --- | --- | --- | ---: | ---: |
| `delays` | PR31 gap: delay and procedural discipline | `Delays_rag.md` | `strong_affordance_record` | 1 | 2 |
| `obligations-controls-mapping` | PR31 gap: obligation/control traceability | `Obligations_Controls_Mapping_rag.md` | `strong_affordance_record` | 1 | 2 |
| `peer-review-your-perspectives` | PR31 gap: peer/external correction | `Peer_Review_Your_Perspectives_rag.md` | `strong_affordance_record` | 1 | 2 |
| `formal-reasoning` | PR31 gap: procedural and formal discipline | `Formal_Reasoning_rag.md` | `strong_affordance_record` | 1 | 2 |
| `checklists` | PR31 gap: checklist/procedure discipline | `checklists_rag.md` | `strong_affordance_record` | 1 | 2 |
| `status-quo-bias` | PR31 gap: planning/status quo risks | `Status_Quo_Bias_rag.md` | `strong_affordance_record` | 1 | 2 |
| `commitment-bias` | PR31 gap: commitment and escalation risk | `Commitment_Bias_rag.md` | `strong_affordance_record` | 1 | 2 |
| `optimism-bias-and-planning-fallacy` | PR31 gap: planning optimism | `Optimism_Bias_and_Planning_Fallacy_rag.md` | `strong_affordance_record` | 1 | 2 |
| `batna` | PR31 gap: negotiation and bargaining pressure | `Batna_rag.md` | `thin_narrow_affordance_record` | 1 | 2 |
| `game-theory-payoffs` | PR31 gap: competitive/counterparty dynamics | `Game_Theory_Payoffs_rag.md` | `strong_affordance_record` | 1 | 2 |
| `red-queen-effect` | PR31 gap: competitive adaptation pressure | `Red_Queen_Effect_rag.md` | `strong_affordance_record` | 1 | 2 |
| `jobs-to-be-done` | PR31 gap: product/customer reasoning | `Jobs_To_Be_Done_rag.md` | `strong_affordance_record` | 1 | 2 |
| `user-centered-design` | PR31 gap: product/user evidence loops | `User_Centered_Design_rag.md` | `strong_affordance_record` | 1 | 2 |
| `lock-in` | PR31 gap: market/platform dependency risk | `Lock_In_rag.md` | `strong_affordance_record` | 1 | 2 |
| `path-dependence` | PR31 gap: installed-path constraints | `Path_Dependence_rag.md` | `strong_affordance_record` | 1 | 2 |
| `cross-cultural-communication-frameworks` | PR31 gap: communication and relational reasoning | `Cross_Cultural_Communication_Frameworks_rag.md` | `strong_affordance_record` | 1 | 2 |

## Extraction Outcomes

`delays` produced a lagged-feedback intervention timing check. Strong fields:
delay mechanism, feedback lag, premature judgment guard, intervention timing,
and wait/update criteria. Missing or weak fields: instant causality and
wait-passively guidance were recorded as absences.

`obligations-controls-mapping` produced an obligation-to-control coverage map.
Strong fields: obligation inventory, control owner, evidence, cadence, and gap
visibility. Missing or weak fields: compliance theater and undocumented control
claims were rejected.

`peer-review-your-perspectives` produced an adversarial peer challenge gate.
Strong fields: outside reviewer choice, disconfirming critique, blind-spot
surfacing, and update requirements. Missing or weak fields: rubber-stamp review
and status-based deference were rejected.

`formal-reasoning` produced a premise-validity proof check. Strong fields:
premise naming, inference structure, validity vs truth separation, and
counterexample testing. Missing or weak fields: formalism-as-certainty and
symbolic theater were rejected.

`checklists` produced an omission-risk execution gate. Strong fields:
critical checks, before/during/before-scaling structure, and checklist
anti-bureaucracy guard. Missing or weak fields: tick-box resolution and generic
checklists for novel problems were rejected.

`status-quo-bias` produced an incumbent-option inertia test. Strong fields:
default vs alternative comparison, real switching cost separation, loss
aversion/precedent guard, and evidence for staying. Missing or weak fields:
legacy-equals-bad and novelty-seeking change were rejected.

`commitment-bias` produced a recommitment stop-rule review. Strong fields:
prior commitment, sunk/public/identity pressure, stop rules, and recommitment
without sunk-costs. Missing or weak fields: sunk-cost defense and
consistency-equals-correctness were rejected.

`optimism-bias-and-planning-fallacy` produced an outside-view pre-mortem
forecast check. Strong fields: reference classes, disaster imagination,
conjunctive dependencies, and enthusiasm-vs-evidence separation. Missing or
weak fields: morale-as-forecast-evidence and step-by-step-plan-as-proof were
rejected.

`batna` produced a credible walk-away alternative test, but the record is
intentionally marked thin/narrow because the source explicitly says BATNA is not
defined or discussed in the source corpus. Useful reviewed depth exists for
credible fallback comparison, but full textbook negotiation doctrine was not
extracted. Missing or weak fields: textbook BATNA definition and vague fallback
as BATNA were rejected.

`game-theory-payoffs` produced a counterparty response payoff map. Strong
fields: players, actions, information, payoff drivers, counterparty response,
and decisive-branch pruning. Missing or weak fields: same-game assumptions and
ornate payoff-tree building were rejected.

`red-queen-effect` produced a relative-position adaptation test. Strong fields:
maintenance vs advantage, standing-still risk, non-optional adaptation, and
where not to compete. Missing or weak fields: arms-race-everything and
feature-parity motion were rejected.

`jobs-to-be-done` produced a real-progress job discovery card. Strong fields:
customer adoption/switching/abandonment, real progress, feature-vs-job
separation, and evidence requirements. Missing or weak fields:
preference-as-job and surface-wants-as-job were rejected.

`user-centered-design` produced a prototype user-evidence loop. Strong fields:
observed user evidence, fuzzy problem framing, bounded prototype tests, and
decision-relevant discovery. Missing or weak fields: anecdotes-as-strategy and
open-ended empathy theater were rejected.

`lock-in` produced a reversal-cost dependency audit. Strong fields: dual-run
trap, option decay, integration debt, retraining, workarounds, and hidden
reversal costs. Missing or weak fields: switch-later-same-cost and
identity-protective architecture defense were rejected.

`path-dependence` produced an installed-dependency unwind map. Strong fields:
early choices, installed customers/contracts/interfaces/incentives/approvals,
target-state sequencing, and clean-slate correction. Missing or weak fields:
clean-slate comparison and history-as-excuse were rejected.

`cross-cultural-communication-frameworks` produced a frame-translation action
check. Strong fields: sender/receiver frame mismatch, audience translation,
implementation action, and hard-tradeoff preservation. Missing or weak fields:
stereotype shortcuts and harmony-hidden trade-offs were rejected.

## Corpus Lessons

The batch supports controlled enrichment as a product-quality loop. Fifteen of
sixteen sources provided strong operational depth under exact quote custody. One
source, `batna`, provided useful but intentionally narrow depth because the
source itself includes a custody caveat. That is a healthy result: the batch
does not rescue weak source support with generic mental-model knowledge.

The added records also patch real capability families that v5 was light on:

- procedural discipline: `delays`, `obligations-controls-mapping`,
  `formal-reasoning`, `checklists`;
- correction and bias review: `peer-review-your-perspectives`,
  `status-quo-bias`, `commitment-bias`,
  `optimism-bias-and-planning-fallacy`;
- competitive and negotiation dynamics: `batna`, `game-theory-payoffs`,
  `red-queen-effect`;
- product/customer and dependency reasoning: `jobs-to-be-done`,
  `user-centered-design`, `lock-in`, `path-dependence`;
- communication and relational translation:
  `cross-cultural-communication-frameworks`.

The important lesson is not that v6 is closer to "complete." The lesson is that
source-backed reviewed records can turn graph-only shelf hints into cards with
clearer activation, evidence-needed, do-not-use, misuse, treatment, and absence
signals. The next proof still has to happen at the packet handoff layer.

## Non-Promotion Boundary

PR32 does not:

- run live `/lolla`;
- change prompts;
- rewrite lanes;
- build a live lane adapter;
- add runtime packet production;
- promote v6 into runtime;
- create user-facing Decision Pressure;
- wire Observatory, memo, Step 8, Step 6, or Lane 4 runtime;
- call models;
- run judges;
- broaden beyond the 16 target models;
- create Batch 3b;
- make Python choose final pressure.

## Recommendation For PR33

PR33 should be a packet-quality comparison against v6, not another extraction
batch by default.

Recommended slice:

1. Create one or two review-only mixed packet fixtures that actually nominate
   several PR32-upgraded models.
2. Render them with the PR30 reviewer-only renderer.
3. Compare graph-only/v5-style handoff material against v6 reviewed cards where
   possible.
4. Judge whether the added depth helps a receiver decide which shelves to use,
   merge, ignore, or set aside.

Only if PR33 finds that v6 cards improve handoff quality without bloating the
packet should another controlled extraction batch begin. The next extraction
batch should still be gap-driven and small, not broad 222-count completion.
