# PR44 V10 Graph-Only Priority Audit

**Date:** 2026-05-07
**PR slice:** PR44 - after-v10 graph-only priority audit
**Status:** docs/research audit; no extraction, runtime, prompt, lane, model-call,
judge, UI, memo, or user-facing surface
**Decision label:** `v10_graph_only_priority_audit_complete`

## Purpose

PR43 showed that v10 risk controls / reversibility / failure-containment depth
improves one stable-nomination packet handoff. The next question is not "how do
we finish the remaining 100?"

The next question is:

> After v10, which remaining graph-only capability family is most likely to
> weaken future reasoning packets, and why should it be enriched next instead
> of left graph-only for now?

This audit answers that question before opening another extraction batch.

## Method

The audit uses structured repo artifacts only:

- `data/knowledge_graph.json`
- `data/compiled/model_affordances/affordances_v10.json`
- `data/model_sources/manifest.json`
- `data/curated/compiled_chunks.json`
- existing static route signals in the runtime graph

No source parsing, regex extraction, model calls, judges, live lanes, prompt
changes, or affordance extraction were performed.

The audit treats deterministic counts as custody and prioritization evidence,
not semantic judgment. Family labels below are reviewer groupings for planning;
they are not runtime classes and must not become case-type rules.

The added PR44 audit criterion is:

> Prefer families where reviewed depth would help the next LLM notice that the
> nominated shelves may be using the wrong frame, wrong reasoning mode,
> missing counterfactual, or overconfidently narrow evidence base before action.

## Corpus State After V10

| Measure | Count |
| --- | ---: |
| Runtime graph models | 222 |
| Repo-custodied source files | 222 |
| v10 reviewed records | 122 |
| v10 reviewed affordances | 158 |
| v10 absence records | 229 |
| Graph-only runtime models after v10 | 100 |
| v10 status | `draft_review_only` |

Source custody is complete for all 222 runtime models. Reviewed operational
depth is not complete. The remaining 100 graph-only models are still eligible
for lane-nominated packet shelves, but their packet cards must remain honestly
labeled as graph-only unless and until reviewed records exist.

## Reasoning-Type Gaps After V10

The largest remaining graph-only gaps are broad reasoning operations:

| Reasoning type | Runtime models | v10 reviewed | Graph-only after v10 |
| --- | ---: | ---: | ---: |
| `diagnostic` | 102 | 48 | 54 |
| `metacognitive` | 77 | 29 | 48 |
| `systems` | 87 | 57 | 30 |
| `causal` | 77 | 50 | 27 |
| `probabilistic` | 34 | 20 | 14 |
| `analogical` | 18 | 5 | 13 |
| `deductive` | 26 | 16 | 10 |
| `counterfactual` | 27 | 20 | 7 |
| `abductive` | 5 | 1 | 4 |

This does not mean the next batch should be "diagnostic" in general. That
category is too wide. It means any next family should carry diagnostic or
metacognitive operational value without becoming internal cleverness.

## Static Lane-Signal Read

After v10, the highest remaining graph-only static lane signals are:

| Model ID | Static lane signals | Primary signal sources |
| --- | ---: | --- |
| `creative-destruction` | 5 | Lane 3 reframing, Lane 4 structural |
| `brainstorming` | 4 | Lane 3 reframing |
| `chain-of-thought` | 4 | Lane 1 compiled chunks |
| `cultural-intelligence` | 4 | Lane 3 reframing |
| `curiosity` | 4 | Lane 3 reframing |
| `dialectical-reasoning` | 4 | Lane 1 compiled chunks, Lane 3 reframing |
| `einstellung-effect` | 4 | Lane 3 reframing |
| `internal-locus-of-control` | 4 | Lane 1 compiled chunks |
| `latticework-of-mental-models` | 4 | Lane 3 reframing |
| `metacognitive-questioning` | 4 | Lane 3 reframing |
| `reasoning-mode-router` | 4 | Lane 3 reframing |
| `reframing-perspective` | 4 | Lane 3 reframing |
| `regret-theory` | 4 | Lane 3 reframing |
| `theory-induced-blindness` | 4 | Lane 3 reframing |
| `variation-and-selection` | 4 | Lane 3 reframing |
| `cognitive-gaps-assessment` | 3 | Lane 1 compiled chunks |
| `counterfactual-reasoning` | 3 | Lane 3 reframing |
| `lateral-thinking` | 3 | Lane 3 reframing |
| `power-laws` | 3 | Lane 1 compiled chunks, Lane 4 structural |
| `circle-of-competence` | 2 | Lane 1 compiled chunks, Lane 4 structural |
| `critical-thinking` | 2 | Lane 1 compiled chunks |

This is a real constraint on PR44. The remaining graph-only corpus is no longer
mainly about execution, trust, negotiation, risk, or reversibility. The largest
visible gap is frame selection and metacognitive correction.

That does not make the recommendation automatic. This is also the family most
likely to drift into "think harder" advice, mental-model name-dropping, or
deterministic reasoning-mode routing if handled carelessly.

## What Is Already Stronger After V5-V10

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

These are not "complete." They are simply strong enough that the next batch
should not revisit them unless a packet review exposes a concrete thinness
problem.

## Candidate Families Considered

### 1. Frame Correction / Metacognitive Blind-Spot Discipline

Representative graph-only shelves:

- `cognitive-gaps-assessment`
- `critical-thinking`
- `counterfactual-reasoning`
- `metacognitive-questioning`
- `reasoning-mode-router`
- `reframing-perspective`
- `theory-induced-blindness`
- `einstellung-effect`
- `dialectical-reasoning`
- `bias-blind-spot`
- `false-precision-avoidance`
- `wysiati`

Why it is attractive:

- It is the strongest remaining static lane-signal cluster after v10.
- It directly targets a live packet weakness: a later LLM may receive strong
  evidence, execution, risk, and reversibility cards but still apply them to
  the wrong frame or reasoning mode.
- It can help packets ask whether the current explanation is too narrow, the
  counterfactual is missing, the chosen model has become blinding, or the
  evidence set is only what is available.
- It is broad enough to matter across user domains but still near the product
  promise: before acting, check whether the advice is using the right frame.

Why it is risky:

- It is closest to the old danger of "more thinking about thinking."
- It can become generic critique if records do not force evidence, dismissal,
  treatment, and misuse boundaries.
- `chain-of-thought` and `latticework-of-mental-models` have high static
  signals, but they are especially likely to become internal prompt mechanics
  or mental-model encyclopedia texture, so they are not recommended for the
  first batch in this family.

Recommended status: best PR45 candidate family, but only under a strict
source-backed extraction contract that treats absence as useful and blocks
generic metacognitive advice.

### 2. Market / Customer / Economic Dynamics

Representative graph-only shelves:

- `creative-destruction`
- `elasticity`
- `price-discrimination`
- `supply-and-demand`
- `scale-economies`
- `usability-heuristics`
- `user-experience-research-methods`

Why it is attractive:

- Product, market, and adoption cases are likely future user scenarios.
- Several shelves could produce operational evidence requirements around
  demand, price sensitivity, switching behavior, usability failures, and market
  disruption.

Why it is not first:

- Product/customer depth already improved through `jobs-to-be-done`,
  `user-centered-design`, `lean-startup-methodology`, `lock-in`, and
  `switching-costs`.
- This family is domain-narrower than frame correction for the broad
  "before you act on plausible advice" surface.

Recommended status: later controlled batch if packet reviews keep pulling
market/customer/economic shelves.

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

- Learning and expertise cases are common in personal, student, research, and
  team contexts.
- These shelves could help the next LLM distinguish skill acquisition,
  instructional scaffolding, overload, practice design, and transfer limits.

Why it is not first:

- It is less central to the near-action pressure pass than frame correction.
- Many learning cards may be useful only for education/coaching cases, not
  general decision pressure.

Recommended status: later family if user cases repeatedly involve learning,
skill building, training design, or capability development.

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

- These can strengthen quantitative claims, forecast quality, sampling
  concerns, and base-rate mistakes.
- Some are action-adjacent when advice includes numbers, forecasts, or model
  claims.

Why it is not first:

- v5-v10 already include strong uncertainty, probability, risk, statistical
  discipline, expected value, base rates, and confidence-calibration records.
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
  leadership, and adoption cases.
- Some of these may add useful context around audience, legitimacy, and
  communication fit.

Why it is not first:

- v7 and v8 already improved communication, feedback, trust, persuasion,
  diplomacy, and signaling.
- This family should wait for a concrete packet showing that graph-only
  cultural/social cards are weakening the handoff.

Recommended status: later controlled batch, not PR45 by default.

## Recommended PR45 Family

Recommended family:

> Frame correction / metacognitive blind-spot discipline.

Decision label for PR45 if opened:

> `controlled_frame_correction_enrichment_ready`

This family is not selected because it wins a deterministic ranking. It is
selected because after v10 the next product question is:

> Once advice is plausible, executable, and risk-checked, is it being evaluated
> through the right frame, evidence boundary, reasoning mode, and
> counterfactual?

That is the next place where a graph-only packet can become dangerously thin.

## Recommended PR45 Target Set

Recommended cap: 12 models.

| Model ID | Reasoning types | Static lane signals | Source bytes | Why it belongs |
| --- | --- | ---: | ---: | --- |
| `cognitive-gaps-assessment` | diagnostic, metacognitive | 3 | 18625 | Tests what relevant evidence, perspective, or capability is missing before acting. |
| `critical-thinking` | diagnostic, metacognitive | 2 | 17377 | Converts broad critique into claim/evidence/assumption checks. |
| `counterfactual-reasoning` | counterfactual, causal | 3 | 20809 | Forces comparison against plausible alternatives and paths not taken. |
| `metacognitive-questioning` | metacognitive, diagnostic | 4 | 14124 | Makes the reasoning process inspectable without turning every packet into introspection. |
| `reasoning-mode-router` | diagnostic, metacognitive | 4 | 16652 | Helps the LLM decide whether a case needs causal, probabilistic, systems, deductive, or counterfactual treatment. |
| `reframing-perspective` | metacognitive, systems | 4 | 17539 | Tests whether the original problem frame is hiding a better action path. |
| `theory-induced-blindness` | metacognitive, diagnostic | 4 | 13849 | Guards against overcommitting to the favored model or explanation. |
| `einstellung-effect` | metacognitive, counterfactual | 4 | 14203 | Catches familiar-solution lock-in when the current answer may need a different approach. |
| `dialectical-reasoning` | metacognitive, deductive | 4 | 17380 | Preserves opposing truths or trade-offs instead of collapsing into one-sided advice. |
| `bias-blind-spot` | metacognitive, diagnostic | 0 | 14725 | Prevents the reviewer from treating bias as only the other party's problem. |
| `false-precision-avoidance` | metacognitive, causal | 0 | 17020 | Blocks polished but unsupported specificity in advice, estimates, or confidence. |
| `wysiati` | diagnostic, metacognitive, probabilistic | 0 | 15275 | Forces explicit attention to what evidence is missing from the visible story. |

The byte counts are not proof of source quality. They are only a custody/richness
sanity check. PR45 extraction must still allow `thin_narrow_affordance_record`,
`absence_record`, or `do_not_promote_recommendation` if the source does not
support operational depth.

## Extraction Standard If PR45 Opens

PR45 should read each source file directly and extract only source-supported
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

- turning metacognition into generic "think harder" advice;
- treating model selection as something Python can decide deterministically;
- making `reasoning-mode-router` into a new lane or case-type router;
- extracting prompt-mechanics advice instead of source-backed operational
  reasoning checks;
- using cognitive-bias labels as accusations;
- reframing for cleverness without changing evidence, action, or dismissal
  conditions;
- adding counterfactuals without realistic alternative paths;
- treating false precision as a style issue rather than a decision-quality
  risk;
- inventing fields because metacognitive sources sound broadly wise.

## Required PR46 Proof

If PR45 opens and enriches this family, PR46 must be a same-nomination packet
usefulness review before any further extraction begins.

PR46 should compare a v10/v11 frame-correction packet with the same nominations
and ask:

> Did reviewed frame-correction / metacognitive depth make the future LLM
> better equipped to use, merge, ignore, or set aside these shelves without
> increasing candidate count or selecting a final answer?

PR46 should not answer the user case, choose final Decision Pressure, write
product copy, run live lanes, or promote the compiled artifact into runtime.

## What PR44 Does Not Authorize

PR44 does not authorize:

- runtime packet production;
- prompt changes;
- lane rewrites;
- live `/lolla`;
- model calls;
- judges;
- broad Batch 3b;
- extraction of all 100 graph-only models;
- deterministic reasoning-mode routing;
- deterministic pressure selection;
- user-facing Decision Pressure output.

## Recommendation

Open PR45 as one controlled extraction batch for the 12 frame correction /
metacognitive blind-spot models above.

Then require PR46 to compare a v10/v11 packet using the same nominations before
any further extraction begins.

The loop stays:

> Audit the gap. Enrich a narrow family. Prove packet usefulness. Stop before
> the next batch.
