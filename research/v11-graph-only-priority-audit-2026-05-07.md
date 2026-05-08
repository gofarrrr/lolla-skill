# PR47 V11 Graph-Only Priority Audit

**Date:** 2026-05-07
**PR slice:** PR47 - after-v11 graph-only priority audit
**Status:** docs/research audit; no extraction, runtime, prompt, lane,
model-call, judge, UI, memo, or user-facing surface
**Decision label:** `v11_graph_only_priority_audit_complete`

## Purpose

PR46 showed that v11 frame-correction / metacognitive depth improves one
stable-nomination packet handoff. The next question is not "how do we finish
the remaining 88?"

The next question is:

> After v11, which remaining graph-only capability family is most likely to
> weaken future reasoning packets, and why should it be enriched next instead
> of left graph-only for now?

This audit answers that question before opening another extraction batch.

## Method

The audit uses structured repo artifacts only:

- `data/knowledge_graph.json`
- `data/compiled/model_affordances/affordances_v11.json`
- `data/model_sources/manifest.json`
- `data/curated/compiled_chunks.json`
- existing static route signals in the runtime graph

No source parsing, regex extraction, model calls, judges, live lanes, prompt
changes, or affordance extraction were performed.

The audit treats deterministic counts as custody and prioritization evidence,
not semantic judgment. Family labels below are reviewer groupings for planning;
they are not runtime classes and must not become case-type rules.

The added PR47 audit criterion is:

> Prefer families where reviewed depth would help the next LLM widen the option
> space, generate non-obvious alternatives, test variation, simulate paths, and
> synthesize a bounded next move without turning creativity into brainstorming
> theater.

## Corpus State After V11

| Measure | Count |
| --- | ---: |
| Runtime graph models | 222 |
| Repo-custodied source files | 222 |
| v11 reviewed records | 134 |
| v11 reviewed affordances | 170 |
| v11 absence records | 253 |
| Graph-only runtime models after v11 | 88 |
| v11 status | `draft_review_only` |

Source custody is complete for all 222 runtime models. Reviewed operational
depth is not complete. The remaining 88 graph-only models are still eligible
for lane-nominated packet shelves, but their packet cards must remain honestly
labeled as graph-only unless and until reviewed records exist.

## Reasoning-Type Gaps After V11

The largest remaining graph-only gaps are:

| Reasoning type | Runtime models | v11 reviewed | Graph-only after v11 |
| --- | ---: | ---: | ---: |
| `diagnostic` | 102 | 55 | 47 |
| `metacognitive` | 77 | 40 | 37 |
| `systems` | 87 | 58 | 29 |
| `causal` | 77 | 52 | 25 |
| `analogical` | 18 | 5 | 13 |
| `probabilistic` | 34 | 21 | 13 |
| `deductive` | 26 | 17 | 9 |
| `counterfactual` | 27 | 22 | 5 |
| `abductive` | 5 | 1 | 4 |

This does not mean the next batch should be "diagnostic" in general. That
category is too wide and already has many reviewed records. The more useful
post-v11 question is which remaining family would make packets thin even after
evidence, execution, trust, risk, reversibility, and frame correction have
gotten stronger.

## Static Lane-Signal Read

After v11, the highest remaining graph-only static lane signals are:

| Model ID | Static lane signals | Primary signal sources |
| --- | ---: | --- |
| `creative-destruction` | 5 | Lane 3 reframing, Lane 4 structural |
| `brainstorming` | 4 | Lane 3 reframing |
| `chain-of-thought` | 4 | Lane 1 compiled chunks |
| `cultural-intelligence` | 4 | Lane 3 reframing |
| `curiosity` | 4 | Lane 3 reframing |
| `internal-locus-of-control` | 4 | Lane 1 compiled chunks |
| `latticework-of-mental-models` | 4 | Lane 3 reframing |
| `regret-theory` | 4 | Lane 3 reframing |
| `variation-and-selection` | 4 | Lane 3 reframing |
| `lateral-thinking` | 3 | Lane 3 reframing |
| `power-laws` | 3 | Lane 1 compiled chunks, Lane 4 structural |
| `circle-of-competence` | 2 | Lane 1 compiled chunks, Lane 4 structural |
| `causal-attribution-resistance` | 1 | Lane 4 structural |
| `complexity-bias-resistance` | 1 | Lane 4 structural |
| `compounding` | 1 | Lane 4 structural |
| `data-science-reasoning-framework` | 1 | Lane 1 compiled chunks |
| `feynman-technique` | 1 | Lane 1 compiled chunks |
| `mental-models-of-reality` | 1 | Lane 1 compiled chunks |
| `scale-economies` | 1 | Lane 4 structural |
| `self-control` | 1 | Lane 1 compiled chunks |
| `self-determination-theory` | 1 | Lane 4 structural |
| `specialization` | 1 | Lane 4 structural |
| `statistics-concepts` | 1 | Lane 1 compiled chunks |
| `tradition-vs-innovation-balance` | 1 | Lane 1 compiled chunks |
| `usability-heuristics` | 1 | Lane 4 structural |
| `user-experience-research-methods` | 1 | Lane 1 compiled chunks |

This is a real constraint: the post-v11 high-signal set is no longer mostly
risk, execution, or frame correction. It is now heavily about reframing,
exploration, creativity, agency, culture, and broad mental-model assembly.

The quality risk is also obvious. Several high-signal shelves could become
internal prompt mechanics or mental-model name-dropping if extracted
carelessly. `chain-of-thought` and `latticework-of-mental-models` are
therefore not recommended for the next batch despite high static signal.

## What Is Already Stronger After V5-V11

These families are no longer the default next enrichment targets:

- Evidence, falsification, and verification depth improved through v5.
- Customer/product and capability-gap depth improved through v6.
- Communication, feedback, strategic interdependence, analogy, and adaptive
  reasoning improved through v7.
- Trust repair, motivation, boundaries, negotiation, influence, and signaling
  improved through v8.
- Execution, baselines, bottlenecks, audit trails, debugging, feedback loops,
  input/output goals, bounded iteration, and habit design improved through v9.
- Risk controls, reversibility, failure containment, nonlinear dynamics,
  switching costs, and loss-frame checks improved through v10.
- Frame correction, metacognition, counterfactuals, evidence boundaries,
  false precision, and missing-evidence denominator checks improved through
  v11.

These are not "complete." They are simply strong enough that the next batch
should not revisit them unless a packet review exposes a concrete thinness
problem.

## Candidate Families Considered

### 1. Adaptive Exploration / Option Generation / Synthesis Discipline

Representative graph-only shelves:

- `creative-destruction`
- `brainstorming`
- `curiosity`
- `lateral-thinking`
- `divergent-vs-convergent-thinking`
- `variation-and-selection`
- `adaptation`
- `association`
- `abstraction`
- `synthesis-and-integration`
- `mental-simulation`
- `branch-solve-merge`

Why it is attractive:

- It is now the strongest product-shaped cluster in the remaining graph-only
  set after v11.
- It targets a live packet weakness: a future LLM may receive good evidence,
  execution, risk, and frame-correction cards but still stay inside one
  plausible answer path.
- It can help packets ask whether the answer needs more options, more
  variation, a better abstraction, a simulated path, or a synthesis step before
  commitment.
- It supports the product moment without asking Python to decide wisdom: the
  LLM/reviewer receives better material for widening, testing, and integrating
  options.

Why it is risky:

- It can devolve into creativity theater: generate more ideas, brainstorm more,
  or be curious without changing evidence, decision conditions, or the next
  move.
- It can overlap with PR45 frame correction if extracted as generic reframing.
- It can become prompt mechanics if `chain-of-thought` or
  `latticework-of-mental-models` are included too early.

Recommended status: best PR48 candidate family, under a strict source-backed
extraction contract that makes absence records first-class and blocks creative
vocabulary without operational consequences.

### 2. Market / Economic Dynamics

Representative graph-only shelves:

- `creative-destruction`
- `elasticity`
- `price-discrimination`
- `supply-and-demand`
- `scale-economies`
- `power-laws`
- `compounding`

Why it is attractive:

- Product, market, pricing, and competitive cases are likely future user
  scenarios.
- These shelves could add useful evidence requirements around demand, market
  structure, price sensitivity, distribution of outcomes, scale effects, and
  nonlinearity.

Why it is not first:

- Some product/customer and reversibility depth already exists through
  `jobs-to-be-done`, `user-centered-design`, `lean-startup-methodology`,
  `lock-in`, and `switching-costs`.
- It is more domain-specific than adaptive exploration.
- `creative-destruction` is more useful in the immediate next batch as a
  challenge to stale option spaces than as a pure market-economics card.

Recommended status: later controlled batch if real packets keep pulling
market/economic shelves.

### 3. Learning / Expertise / Skill Acquisition

Representative graph-only shelves:

- `blooms-taxonomy`
- `cognitive-load-theory`
- `deliberate-practice`
- `desirable-difficulties`
- `expertise-reversal-effect`
- `feynman-technique`
- `growth-mindset`
- `learning-curve`
- `perceptual-learning`
- `scaffolding`
- `zone-of-development`

Why it is attractive:

- Learning and capability-building cases are common.
- These shelves could help distinguish skill acquisition, overload, practice
  design, transfer limits, scaffolding, and readiness.

Why it is not first:

- It is less central to the near-action pressure pass than option generation
  and synthesis.
- Many learning cards may be useful only in education, training, coaching, or
  capability-development cases.

Recommended status: later family if archived or live `/lolla` cases repeatedly
involve learning, upskilling, training design, or capability transfer.

### 4. Statistical / Data / Probabilistic Remainder

Representative graph-only shelves:

- `bayesian`
- `conjunction-fallacy`
- `data-science-reasoning-framework`
- `markov-chains`
- `monte-carlo-methods`
- `regression-to-the-mean`
- `representativeness-heuristic`
- `statistics-concepts`
- `statistical-learning-theory`

Why it is attractive:

- These can strengthen numerical claims, forecasting, sampling concerns,
  base-rate mistakes, regression effects, and uncertainty quantification.

Why it is not first:

- v5-v11 already include strong uncertainty, probability, risk, expected
  value, base rates, confidence calibration, false precision, and loss-frame
  checks.
- A batch here should be triggered by a packet with quantitative thinness, not
  by the mere existence of remaining statistical shelves.

Recommended status: later controlled batch when a packet exposes numerical or
forecasting thinness.

### 5. Cultural / Social Context Remainder

Representative graph-only shelves:

- `cultural-intelligence`
- `cultural-dimensions-theory`
- `multicultural-team-dynamics`
- `comparative-political-systems-analysis`
- `liking-principle`
- `pre-suasion`
- `storytelling-frameworks`

Why it is attractive:

- Cross-cultural and social influence gaps can matter in negotiation,
  leadership, adoption, and communication cases.
- `cultural-intelligence` remains high-signal after v11.

Why it is not first:

- v7 and v8 already improved communication, feedback, trust, persuasion,
  diplomacy, and signaling.
- This family should wait for a concrete packet showing that graph-only
  cultural/social cards are weakening the handoff.

Recommended status: later controlled batch, not PR48 by default.

## Recommended PR48 Family

Recommended family:

> Adaptive exploration / option generation / synthesis discipline.

Decision label for PR48 if opened:

> `controlled_adaptive_exploration_enrichment_ready`

This family is not selected because it completes the corpus or wins a
deterministic ranking. It is selected because after v11 the next product
question is:

> Once advice is plausible, evidence-aware, executable, risk-checked, and
> frame-corrected, is the answer still trapped inside too narrow an option
> space?

That is the next place where a graph-only packet can become thin.

## Recommended PR48 Target Set

Recommended cap: 12 models.

| Model ID | Reasoning types | Static lane signals | Source bytes | Why it belongs |
| --- | --- | ---: | ---: | --- |
| `creative-destruction` | causal, abductive | 5 | 13118 | Tests whether a plausible plan ignores displacement, disruption, or a better option space. |
| `brainstorming` | analogical, metacognitive | 4 | 13659 | Converts idea generation into bounded option breadth rather than volume theater. |
| `curiosity` | diagnostic, metacognitive | 4 | 17429 | Makes inquiry decision-relevant instead of decorative openness. |
| `lateral-thinking` | analogical, metacognitive | 3 | 14885 | Helps escape linear obvious-path reasoning when a non-obvious route may matter. |
| `divergent-vs-convergent-thinking` | analogical, metacognitive | 0 | 15544 | Distinguishes when to widen options versus commit and narrow. |
| `variation-and-selection` | abductive, diagnostic | 4 | 14754 | Turns option generation into tested variation and selection criteria. |
| `adaptation` | causal, systems | 0 | 15886 | Connects changing conditions to adjustment signals, not vague flexibility. |
| `association` | analogical, systems | 0 | 16749 | Supports cross-connection discovery while blocking random analogy drift. |
| `abstraction` | systems, deductive | 0 | 14518 | Helps extract transferable structure from details without losing decision constraints. |
| `synthesis-and-integration` | systems, metacognitive | 0 | 16677 | Integrates competing fragments into a bounded next move. |
| `mental-simulation` | systems, counterfactual | 0 | 18466 | Rehearses candidate paths before commitment without pretending simulation is evidence. |
| `branch-solve-merge` | systems, causal | 0 | 13231 | Preserves parallel exploration and disciplined merge points rather than endless branches. |

The byte counts are not proof of source quality. They are only a custody/richness
sanity check. PR48 extraction must still allow `thin_narrow_affordance_record`,
`absence_record`, or `do_not_promote_recommendation` if the source does not
support operational depth.

## Extraction Standard If PR48 Opens

PR48 should read each source file directly and extract only source-supported
operational depth.

High-value fields:

- `use_when`
- `case_evidence_needed`
- `do_not_use_when`
- `treatment_requirements`
- `diagnostic_questions`
- `misuse_guards`
- absence records for unsupported overclaims

Watch especially for these failure modes:

- turning brainstorming into "more ideas" without decision criteria;
- treating curiosity as generic openness;
- using lateral thinking as cleverness without evidence or action change;
- generating variations without selection pressure;
- treating adaptation as vague flexibility;
- using association or abstraction to drift away from the case;
- synthesizing by smoothing over real trade-offs;
- treating mental simulation as proof;
- letting branch/solve/merge become project-management theater;
- including `chain-of-thought` or `latticework-of-mental-models` before there
  is a concrete packet need, because both can become prompt mechanics or
  mental-model encyclopedia texture.

## Required PR49 Proof

If PR48 opens and enriches this family, PR49 must be a same-nomination packet
usefulness review before any further extraction begins.

PR49 should compare a v11/v12 adaptive-exploration packet with the same
nominations and ask:

> Did reviewed adaptive-exploration / option-generation / synthesis depth make
> the future LLM better equipped to widen, test, narrow, merge, or set aside
> candidate paths without increasing candidate count or selecting a final
> answer?

PR49 should not answer the user case, choose final Decision Pressure, write
product copy, run live lanes, or promote the compiled artifact into runtime.

## What PR47 Does Not Authorize

PR47 does not authorize:

- runtime packet production;
- prompt changes;
- lane rewrites;
- live `/lolla`;
- model calls;
- judges;
- broad Batch 3b;
- extraction of all 88 graph-only models;
- deterministic option selection;
- deterministic pressure selection;
- user-facing Decision Pressure output.

## Recommendation

Open PR48 as one controlled extraction batch for the 12 adaptive exploration /
option generation / synthesis models above.

Then require PR49 to compare a v11/v12 packet using the same nominations before
any further extraction begins.

The loop stays:

> Audit the gap. Enrich a narrow family. Prove packet usefulness. Stop before
> the next batch.
