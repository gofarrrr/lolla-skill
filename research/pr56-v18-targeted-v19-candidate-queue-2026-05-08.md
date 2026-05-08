# PR56 Targeted v19 Candidate Queue

Date: 2026-05-08

Branch: `feature/knowledge-substrate-pr56-source-adequacy-audit`

Status: candidate queue only; do not edit affordance records in PR56

## Purpose

This queue turns the full-corpus PR56 audit into a low-level handover for a later targeted v19 PR.

It is not a rewrite batch. It is a proof queue.

Every candidate must prove that the source-backed material changes downstream card transaction behavior. If it does not, the later PR should prefer absence enrichment, display hardening, or no change.

## Gate 0: Non-Negotiables

Before editing any record:

- read the full canonical Markdown source again;
- read the current individual affordance JSON;
- read the compiled v18 record;
- identify the exact source-backed operational cluster;
- decide whether the issue is positive affordance, absence/guard, rewrite, weak support, or packet shape;
- preserve current source custody;
- keep artifact status dormant / review-only;
- do not use "latest artifact wins" logic;
- do not modify runtime pickup.

## Gate 1: Positive Split Proof

A positive split candidate may be edited only if the new affordance has a different:

- activation condition;
- case evidence needed;
- do-not-use boundary;
- treatment requirement;
- misuse guard;
- source confidence;
- receiver action: use, reject, defer, merge, or absence-block;
- final-answer pressure.

If the candidate fails this test, use absence enrichment or no change.

## P1 Positive Split Candidates

| Model | Candidate new affordance shape | Must prove |
| --- | --- | --- |
| `category-decisions` | category synthesis / grouped-findings-to-insight | that synthesis into a governing insight is not already owned by `synthesis-and-integration` or current category validation |
| `power-dynamics` | multi-party weakest-link leverage dependency | that weakest-link constraint changes treatment beyond bilateral outside-option mapping |
| `mental-models-of-reality` | infer/adapt to another actor's mental model | that stakeholder/counterpart map inference has distinct evidence and misuse guards from map-territory testing |
| `critical-thinking` | problem-structure discipline | that disaggregation, hypothesis, WHTB, and MECE are not already sufficiently covered by `consulting-firms-methodology`, `decomposition`, or `scientific-method-evidence-testing` |
| `metacognitive-questioning` | ask-how-not-what expert elicitation | that process/criteria/skills elicitation changes receiver action beyond next-question gating |
| `commitment-bias` | constructive commitment architecture | that follow-through design is distinct from escalation-stop / recommitment review |
| `conjunction-fallacy` | disjunctive failure-risk aggregation | that "any one failure can break the plan" requires different treatment than sequential success gates |
| `emotional-intelligence` | self-regulation under emotional activation | that own-state regulation is distinct from stakeholder emotional adoption |
| `evolutionary-pressure` | threat-response communication packaging | that communication under threat/hot cognition is distinct from selection-environment diagnosis |
| `feedback-loops` | reinforcing/balancing loop polarity | that polarity changes the intervention: dampen, stabilize, amplify, or monitor |
| `international-negotiation-and-diplomacy-models` | adversarial game/simulation countermove reasoning | that adversarial strategy review differs from durable-settlement stakeholder mapping |
| `lock-in` | deliberate productive standardization | that stability/consistency/trust compounding is a positive lock-in action, not merely an exception to exit-risk analysis |
| `mental-simulation` | skill rehearsal / anticipatory practice | that training responses differs from assumption-bound decision scenario rehearsal |
| `path-dependence` | cognitive/habit/schema reproduction | that reframing or habit redesign differs from installed dependency unwind |
| `redundancy` | cognitive redundancy for retention/communication | that reinforcement for learning/clarity is not wasteful duplicate capacity |
| `switching-costs` | adoption friction / incumbent loyalty | that adoption and competitive friction differs from platform/ERP exit planning |

## P2 Split Watch

| Model | Watch question | Likely safer path |
| --- | --- | --- |
| `theory-of-constraints` | Is stakeholder / decision-right bottleneck a separate ownership-specific affordance? | absence enrichment unless replay cases prove different action |
| `problem-framing-and-reframing` | Is organizational/social-context framing a fourth affordance? | absence enrichment unless it changes the frame-selection action |
| `baseline-establishment` | Is goal-solution separation a separate baseline transaction? | guard/absence first |
| `chain-of-thought` | Is anti-rationalization a positive affordance? | no; enrich absences and misuse guards instead |

## P1 Absence Or Guard Enrichment

| Model | Recommended enrichment | Why positive split is not default |
| --- | --- | --- |
| `chain-of-thought` | block step-by-step prompting as runtime policy; block user-facing reasoning chain as evidence; block reasoning transcript without verification or implementation path | source warning is mainly misuse prevention |
| `game-theory-payoffs` | commitments, threats, and promises need credibility devices | current payoff mapping is good; missing blocker is credibility |
| `problem-framing-and-reframing` | visible guard for organizational, political, fear, management-style, or social-system frames | may be covered by alternative-frame testing, but should not disappear |
| `theory-of-constraints` | false bottleneck certainty, visible-work optimization, stakeholder/ownership constraints | current affordances mostly capture the positive move |
| `baseline-establishment` | prevent goal/baseline definition from importing solutions or execution plans | likely a guard on baseline setting |
| `elasticity` | reject low-quality, irrelevant, or skewing retrieved snippets | source issue is retrieval quality, not new reasoning mode |
| `constructive-feedback-models` | preserve process/system diagnosis before personal correction | feedback model is otherwise adequate |
| `internal-locus-of-control` | agency can become overcontrol, ego, or selective perception | source warning is a misuse guard |
| `meta-cognitive-reflection` | rationalization dressed as reflection; cognitive-cost / calm-window boundary | source issue is over-reflection misuse |
| `anchoring` | clarify system-risk / conjunctive-disjunctive stress boundary | better routed to risk/uncertainty cards unless a split is proven |
| `multi-criteria-decision-analysis` | post-outcome process review and communication simplification notes | current matrix transaction is intact |
| `active-listening` | do not abandon emotional content after vulnerability is surfaced | main listening transaction is intact |
| `agile-methodologies` | fixed external commitments/interfaces/regulatory constraints can block agile iteration | main inspect-adapt transaction is intact |
| `chaos-theory` | do not impose a preferred will on the system while ignoring observed behavior | main nonlinear-resilience transaction is intact |

## Weak-Support Do-Not-Upgrade Queue

These records should remain visibly cautious unless new source material is added:

- `price-discrimination`
- `devops-and-continuous-integration`
- `markov-chains`
- `six-thinking-hats`
- `adverse-selection`
- `batna`
- `comparative-political-systems-analysis`
- `cultural-dimensions-theory`
- `tier-2-high-value`

Rules:

- do not infer textbook doctrine from weak proxy material;
- do not expand for symmetry;
- do not hide medium confidence;
- do not let reviewed substrate make weak cards look equally authoritative.

## Broad / Meta Packet Queue

These may be source-adequate but still dangerous in receiver packets:

- `systems-thinking`
- `latticework-of-mental-models`
- `cognitive-biases`
- `reasoning-mode-router`
- `mental-models-of-reality`
- `critical-thinking`
- `meta-cognitive-reflection`

Packet hardening should:

- cap broad/meta cards;
- label them as meta-checks, not automatic reasoning directives;
- require concrete case relevance;
- preserve per-affordance grouping;
- show absences and confidence visibly;
- let the receiver reject the card without apology.

## PR57 Suggested Work Order

1. Start with P1 split candidates that are least likely to be covered elsewhere:
   - `power-dynamics`
   - `commitment-bias`
   - `feedback-loops`
   - `lock-in`
   - `mental-simulation`
   - `redundancy`
   - `switching-costs`
2. Then review split candidates that may overlap existing cards:
   - `critical-thinking`
   - `category-decisions`
   - `metacognitive-questioning`
   - `mental-models-of-reality`
   - `path-dependence`
3. Then handle absence/guard enrichments.
4. Then recompile v19 as `draft_review_only`.
5. Then re-run packet stress review from PR55 against v19.

## Definition Of Done For A v19 Change

Each changed model must include:

- explicit source refs;
- an updated `review_notes` explanation;
- if positive split: a distinct affordance id and per-affordance identity;
- if absence enrichment: a clear `absence_id` that can block overclaim;
- confidence unchanged unless the source actually supports changing it;
- no runtime imports;
- updated compiled artifact;
- validation showing schema/source quote/hash failures remain zero.

## Bottom Line

The next move is not more extraction by default.

The next move is targeted preservation of source-supported cognition where v18 compression changed the receiver's possible action.
