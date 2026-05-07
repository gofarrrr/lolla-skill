# PR36 Controlled Trust And Negotiation Enrichment Report

**Status:** controlled reviewed enrichment quality loop, dormant/review-only

**Decision label:** `controlled_trust_negotiation_enrichment_ready`

**Branch:** `feature/reasoning-substrate-pr36-controlled-trust-negotiation-enrichment`

## Purpose

PR36 follows PR35's packet-usefulness review. PR35 showed that v7 reviewed
depth improved a communication/competition packet with stable nominations. PR36
takes the next small, gap-driven enrichment step in a neighboring family that
PR35 identified as still likely to appear in packets and remain thin:

- trust and relationship repair: `non-violent-communication`,
  `emotional-intelligence`, `authenticity`, `boundaries`, `hanlons-razor`;
- motivation and interpersonal inference: `understanding-motivations`;
- negotiation influence and proof: `reciprocity-principle`,
  `persuasion-principles`, `international-negotiation-and-diplomacy-models`,
  `signaling`.

This is not broad Batch 3b, runtime promotion, a live lane adapter, prompt
work, receiver-side answer generation, or user-facing Decision Pressure. The
point is to read ten repo-custodied graph-only sources, extract only
source-supported operational depth, and preserve absence records where tempting
uses are unsupported.

## Batch Shape

- Target runtime graph models: `10`
- Source-custodied source files used: `10`
- Models already present in v7: `0`
- New batch directory: `data/model_affordances/batch_7/`
- Batch records added: `10`
- Batch affordances added: `10`
- Batch absence records added: `20`
- Compiled artifact: `data/compiled/model_affordances/affordances_v8.json`
- Compiled artifact status: `draft_review_only`
- v8 compiled model records: `98`
- v8 compiled affordances: `134`
- v8 compiled absence records: `181`
- Runtime graph models still graph-only after v8: `124`
- Source-evidence references in v8 records: `1604`
- Treatment requirements in v8 affordances: `241`
- Diagnostic questions in v8 affordances: `496`
- Misuse guards in v8 affordances: `471`

## Target Selection

| model_id | why selected | source file | outcome | affordances | absences |
| --- | --- | --- | --- | ---: | ---: |
| `non-violent-communication` | Trust repair and hard conversation gap beyond feedback forms | `Non_Violent_Communication_rag.md` | `strong_affordance_record` | 1 | 2 |
| `emotional-intelligence` | Human-context adoption and emotional evidence gap | `Emotional_Intelligence_rag.md` | `strong_affordance_record` | 1 | 2 |
| `understanding-motivations` | Hidden driver and resistance diagnosis gap | `Understanding_Motivations_rag.md` | `strong_affordance_record` | 1 | 2 |
| `boundaries` | Scope, ownership, and relationship boundary gap | `Boundaries_rag.md` | `strong_affordance_record` | 1 | 2 |
| `authenticity` | Trust-through-congruence and candor gap | `Authenticity_rag.md` | `strong_affordance_record` | 1 | 2 |
| `hanlons-razor` | Conflict de-escalation and intent-attribution gap | `Hanlons_Razor_rag.md` | `strong_affordance_record` | 1 | 2 |
| `reciprocity-principle` | Trust-building before asks and negotiation gap | `Reciprocity_Principle_rag.md` | `strong_affordance_record` | 1 | 2 |
| `persuasion-principles` | Adoption and influence-with-substance gap | `Persuasion_Principles_rag.md` | `strong_affordance_record` | 1 | 2 |
| `international-negotiation-and-diplomacy-models` | Multi-party substance/signaling settlement gap | `International_Negotiation_and_Diplomacy_Models_rag.md` | `strong_affordance_record` | 1 | 2 |
| `signaling` | Credible proof and cheap-signal distinction gap | `Signaling_rag.md` | `strong_affordance_record` | 1 | 2 |

## Extraction Outcomes

`non-violent-communication` produced a needs-observations-request clarifier.
Strong fields: observable fact, relationship concern, need, request, directness
without accusation. Missing or weak fields: conflict avoidance and
empathy-over-interest were rejected.

`emotional-intelligence` produced an emotion evidence landing check. Strong
fields: emotional signal, validation, adoption risk, fairness/trust concerns,
and standards that remain intact. Missing or weak fields: empathy as substitute
for standards and unvalidated emotional reading were rejected.

`understanding-motivations` produced a hidden driver hypothesis test. Strong
fields: visible behavior, stated motive, inferred driver, optimization target,
and disconfirming check. Missing or weak fields: over-psychologizing simple
constraints and treating stated motives as final truth were rejected.

`boundaries` produced a scope ownership decision-rights filter. Strong fields:
inside/outside/influenceable, finite capacity, core objective, and exclusion
criteria. Missing or weak fields: comfort-protection boundaries and premature
narrowing were rejected.

`authenticity` produced a congruence candor substance check. Strong fields:
genuine experience, trust through congruence, evidence grounding, and
accountable candor. Missing or weak fields: authentic style without substance
and "my truth" as accountability escape were rejected.

`hanlons-razor` produced a non-malice diagnostic delay. Strong fields:
coordination breakdown, incentive/training/overload explanation, evidence for
malice versus neglect, and corrective system action. Missing or weak fields:
repeat-harm excuse and automatic good-intentions presumption were rejected.

`reciprocity-principle` produced a costly reciprocal value trust test. Strong
fields: real value offered first, relevance, costliness, goodwill, and
independent merit evaluation. Missing or weak fields: obligation without
evaluation and favor distraction from substance were rejected.

`persuasion-principles` produced a substance-preserving adoption design card.
Strong fields: sound underlying insight, adoption barrier, audience processing
mode, packaging, and preserved evidence/autonomy. Missing or weak fields:
better packaging for weak answers and autonomy-bypassing influence were
rejected.

`international-negotiation-and-diplomacy-models` produced a substance signaling
settlement map. Strong fields: interdependent goals, substance, signaling,
stakeholder interpretation, concessions, sequencing, and durable alignment.
Missing or weak fields: tactical point-scoring and content-only negotiation
were rejected.

`signaling` produced a costly proof of intent test. Strong fields: observable
signal, costliness, follow-through, unstaged proof, and next proof demand.
Missing or weak fields: cheap symbolic signal as proof and
impression-management as substance were rejected.

## Corpus Lessons

The batch supports another controlled enrichment step without expanding by
count momentum. All ten sources produced compact reviewed depth with exact
source custody and absence records. The strongest product value is in the
tensions the records create:

- `non-violent-communication`, `boundaries`, and `authenticity` distinguish
  hard relational clarity from politeness, comfort-protection, or
  self-expression.
- `emotional-intelligence`, `understanding-motivations`, and `hanlons-razor`
  help a receiver read human signals without mind-reading, over-psychologizing,
  or excusing repeat harm.
- `reciprocity-principle`, `persuasion-principles`, and `signaling` separate
  trust-building influence from obligation pressure, autonomy bypass, and cheap
  symbolic proof.
- `international-negotiation-and-diplomacy-models` ties substance, signaling,
  stakeholders, concessions, and sequencing together without promoting tactical
  point-scoring.

The important lesson is not "v8 is closer to complete." The lesson is that
trust and negotiation packets can now receive reviewed handoff material that
keeps candor, influence, and proof disciplined instead of generic.

## Non-Promotion Boundary

PR36 does not:

- run live `/lolla`;
- change prompts;
- rewrite lanes;
- build a live lane adapter;
- add runtime packet production;
- promote v8 into runtime;
- create user-facing Decision Pressure;
- wire Observatory, memo, Step 8, Step 6, or Lane 4 runtime;
- call models;
- run judges;
- broaden beyond the 10 target models;
- create Batch 3b;
- make Python choose final pressure.

## Recommendation For PR37

PR37 should probably be another packet-usefulness review, not another
extraction batch by default.

Recommended slice:

1. Create one review-only packet fixture that nominates PR36-upgraded models in
   a realistic trust repair / negotiation / influence case.
2. Compare a v7-style packet against a v8 packet using the same nominations.
3. Render both with the reviewer-only packet renderer.
4. Judge whether the PR36 cards help a receiver decide what to use, merge,
   ignore, or set aside.

Only if PR37 finds that v8 improves handoff usefulness without creating
interpersonal or influence clutter should another small controlled enrichment
batch begin. The next extraction batch should remain capability-gap driven, not
broad 222-model completion.
