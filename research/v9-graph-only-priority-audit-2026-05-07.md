# PR41 V9 Graph-Only Priority Audit

**Date:** 2026-05-07
**PR slice:** PR41 - after-v9 graph-only priority audit
**Status:** docs/research audit; no extraction, runtime, prompt, lane, model-call,
judge, UI, memo, or user-facing surface
**Decision label:** `v9_graph_only_priority_audit_complete`

## Purpose

PR40 showed that v9 execution / implementation / follow-through depth improves
one stable-nomination packet. The next question is not "how do we finish the
remaining 112?"

The next question is:

> After v9, which remaining graph-only capability family is most likely to
> weaken future reasoning packets, and why should it be enriched next instead
> of left graph-only for now?

This audit answers that question before opening another extraction batch.

## Method

The audit uses structured repo artifacts only:

- `data/knowledge_graph.json`
- `data/compiled/model_affordances/affordances_v9.json`
- `data/model_sources/manifest.json`
- `data/curated/compiled_chunks.json`
- existing static route signals in the runtime graph

No source parsing, regex extraction, model calls, judges, live lanes, prompt
changes, or affordance extraction were performed.

The audit treats deterministic counts as custody and prioritization evidence,
not semantic judgment. Family labels below are reviewer groupings for planning;
they are not runtime classes and must not become case-type rules.

The added PR41 audit criterion is:

> Prefer families where reviewed depth would help the next LLM test
> executability, reversibility, escalation, trust, evidence, or stop/change
> thresholds.

## Corpus State After V9

| Measure | Count |
| --- | ---: |
| Runtime graph models | 222 |
| Repo-custodied source files | 222 |
| v9 reviewed records | 110 |
| v9 reviewed affordances | 146 |
| v9 absence records | 205 |
| Graph-only runtime models after v9 | 112 |
| v9 status | `draft_review_only` |

Source custody is complete for all 222 runtime models. Reviewed operational
depth is not complete. The remaining 112 graph-only models are still eligible
for lane-nominated packet shelves, but their packet cards must remain honestly
labeled as graph-only unless and until reviewed records exist.

## Reasoning-Type Gaps After V9

The largest remaining graph-only gaps are still broad reasoning operations:

| Reasoning type | Runtime models | v9 reviewed | Graph-only after v9 |
| --- | ---: | ---: | ---: |
| `diagnostic` | 102 | 47 | 55 |
| `metacognitive` | 77 | 29 | 48 |
| `systems` | 87 | 47 | 40 |
| `causal` | 77 | 43 | 34 |
| `probabilistic` | 34 | 18 | 16 |
| `analogical` | 18 | 5 | 13 |
| `counterfactual` | 27 | 16 | 11 |
| `deductive` | 26 | 16 | 10 |
| `abductive` | 5 | 1 | 4 |

This does not mean the next batch should be "diagnostic" or
"metacognitive." Those categories are too wide. It means the next family should
carry diagnostic, systems, causal, probabilistic, or counterfactual operational
value where future packets would otherwise be thin.

## Static Lane-Signal Read

After v9, the highest remaining graph-only static lane signals are:

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
| `risk-vs-uncertainty` | 4 | Lane 1 compiled chunks |
| `theory-induced-blindness` | 4 | Lane 3 reframing |
| `variation-and-selection` | 4 | Lane 3 reframing |
| `cognitive-gaps-assessment` | 3 | Lane 1 compiled chunks |
| `counterfactual-reasoning` | 3 | Lane 3 reframing |
| `lateral-thinking` | 3 | Lane 3 reframing |
| `power-laws` | 3 | Lane 1 compiled chunks, Lane 4 structural |
| `circle-of-competence` | 2 | Lane 1 compiled chunks, Lane 4 structural |
| `critical-thinking` | 2 | Lane 1 compiled chunks |
| `prospect-theory` | 2 | Lane 3 reframing |

This is a constraint, not an instruction to extract the top list. If PR42 were
selected by static signal alone, the next batch would be heavily
metacognitive/reframing. That may be useful later, but it is also where the
system is most likely to add elegant thinking vocabulary without improving the
near-action handoff.

## What Is Already Stronger After V5-V9

These families are no longer the default next enrichment targets:

- Evidence, falsification, and verification depth improved through v5.
- Customer/product and capability-gap depth improved through v6.
- Communication, feedback, strategic interdependence, analogy, and adaptive
  reasoning improved through v7.
- Trust repair, motivation, boundaries, negotiation, influence, and signaling
  improved through v8.
- Execution, baselines, bottlenecks, audit trails, debugging, feedback loops,
  input/output goals, bounded iteration, and habit design improved through v9.

These are not "complete." They are simply strong enough that the next batch
should not revisit them unless a packet review exposes a concrete thinness
problem.

## Candidate Families Considered

### 1. Metacognitive / Reframing / Exploration

Representative graph-only shelves:

- `brainstorming`
- `curiosity`
- `dialectical-reasoning`
- `einstellung-effect`
- `latticework-of-mental-models`
- `metacognitive-questioning`
- `reasoning-mode-router`
- `reframing-perspective`
- `theory-induced-blindness`
- `variation-and-selection`

Why it is attractive:

- It still dominates the static lane-signal list.
- It directly supports unknown-unknown discovery and frame shifts.
- It may help future packets decide whether the wrong problem frame is active.

Why it is not first:

- It is closest to the old danger of "more thinking about thinking."
- It may produce cards that feel intellectually rich but do not change
  verification, reversibility, escalation, evidence, or stop/change thresholds.
- Many of these graph-only shelves may be sufficient as lightweight neighbors
  until a concrete packet shows they are thin.

Recommended status: serious later candidate, but not the next extraction batch
by default.

### 2. Risk Controls / Reversibility / Failure Containment

Representative graph-only shelves:

- `risk-vs-uncertainty`
- `redundancy`
- `regulatory-horizon-scanning`
- `cybersecurity-thinking-models`
- `non-linear-dynamics`
- `tipping-points`
- `butterfly-effect`
- `chaos-theory`
- `combinatorial-effects`
- `critical-mass`
- `switching-costs`
- `prospect-theory`

Why it is attractive:

- It is the next weak edge of the "before you act" promise after execution has
  been strengthened.
- It can help a future packet test whether advice is reversible, monitorable,
  contained, sized correctly, robust to nonlinear blowback, or vulnerable to
  hidden threshold and cascade effects.
- It is action-adjacent without asking Python to choose the final pressure.
- It can produce operational checks: downside envelope, rollback path,
  single-point failure, monitoring threshold, escalation trigger, loss-frame
  manipulation, migration lock-in, and false certainty under uncertainty.

Why it is not a deterministic slam dunk:

- It does not dominate the static lane-signal table.
- Some targets have low static route counts and are selected by product
  hypothesis plus graph-field fit, not frequency alone.
- Existing reviewed records already contain some risk, uncertainty,
  resilience, and systems support, so PR42 must extract only where the source
  adds concrete operational constraints.

Recommended status: best PR42 candidate family, because future packets are
likely to be thin where plausible advice needs containment, reversibility,
monitoring, escalation, or stop/change thresholds.

### 3. Market / Customer / Product Dynamics

Representative graph-only shelves:

- `user-experience-research-methods`
- `usability-heuristics`
- `price-discrimination`
- `supply-and-demand`
- `switching-costs`
- `creative-destruction`

Why it is attractive:

- Product and market cases are likely future user scenarios.
- Several shelves could produce operational evidence and misuse guards.

Why it is not first:

- Some product/customer depth already exists after v6 and v9 via
  `jobs-to-be-done`, `user-centered-design`, and `lean-startup-methodology`.
- It is narrower than risk controls for the broad "before you act" surface.
- `switching-costs` is more useful in the immediate next family as a
  reversibility and lock-in card.

Recommended status: later controlled batch if product cases keep pulling these
models.

### 4. Cognitive Bias / Learning / Decision-Quality Remainder

Representative graph-only shelves:

- `bias-blind-spot`
- `cognitive-biases`
- `dunning-kruger-effect`
- `hindsight-bias`
- `logical-fallacies`
- `representativeness-heuristic`
- `system-1`
- `system-2`
- `wysiati`

Why it is attractive:

- It could strengthen advice audits around overconfidence, hindsight,
  intuition, and incomplete evidence.
- Some of these models are likely to be pulled by serious user-framing and
  assistant-answer failures.

Why it is not first:

- Several adjacent reviewed records already help with false certainty,
  evidence discipline, confirmation checks, and probabilistic reasoning.
- A batch here could easily become generic "watch for bias" guidance unless a
  future packet proves which bias cards are thin.

Recommended status: later controlled batch, ideally after one packet review
shows repeated bias-family thinness.

## Recommended PR42 Family

Recommended family:

> Risk controls / reversibility / failure containment.

Decision label for PR42 if opened:

> `controlled_risk_reversibility_enrichment_ready`

This family is not selected because it wins every deterministic count. It is
selected because it best matches the next product question:

> Once AI advice is plausible and executable, what keeps acting on it
> reversible, contained, monitorable, escalatable, and stoppable?

That is the place where a graph-only packet can still become dangerously thin.

## Recommended PR42 Target Set

Recommended cap: 12 models.

| Model ID | Reasoning types | Static lane signals | Source bytes | Why it belongs |
| --- | --- | ---: | ---: | --- |
| `risk-vs-uncertainty` | probabilistic, counterfactual | 4 | 16978 | Tests whether commitment size and reversibility match what is measurable versus unknowable. |
| `redundancy` | counterfactual, systems | 0 | 14823 | Adds single-point-failure and backup-path discipline without turning duplication into theater. |
| `regulatory-horizon-scanning` | systems, counterfactual | 0 | 14769 | Converts weak external signals into monitoring thresholds, owners, and response triggers. |
| `cybersecurity-thinking-models` | causal, systems | 0 | 17914 | Tests adversarial incentives, control ownership, attack-surface reality, and cascading failure chains. |
| `non-linear-dynamics` | causal, systems | 1 | 15373 | Adds feedback-loop, delay, and threshold-monitoring discipline where local fixes can backfire. |
| `tipping-points` | causal, systems | 1 | 15554 | Tests whether the claimed breakthrough depends on a real controlling threshold or a romantic threshold story. |
| `butterfly-effect` | causal, systems | 0 | 16561 | Requires plausible cascade paths before treating a small move as safe or dangerous. |
| `chaos-theory` | systems, causal | 0 | 13842 | Favors robustness, monitoring, and reversibility over false precision in unstable environments. |
| `combinatorial-effects` | causal, systems | 0 | 15367 | Checks whether multiple interacting forces create downside or upside that one-cause reasoning misses. |
| `critical-mass` | causal, systems | 1 | 15201 | Tests threshold viability, reinforcement loops, and false confidence from isolated early wins. |
| `switching-costs` | counterfactual, systems | 1 | 20822 | Makes lock-in, dual-run cost, migration friction, and reversal-cost growth visible before commitment. |
| `prospect-theory` | probabilistic, diagnostic | 2 | 13395 | Tests whether loss framing, reference points, or manipulation are distorting risk-taking before action. |

The byte counts are not proof of source quality. They are only a custody/richness
sanity check. PR42 extraction must still allow `thin_narrow_affordance_record`,
`absence_record`, or `do_not_promote_recommendation` if the source does not
support operational depth.

## Extraction Standard If PR42 Opens

PR42 should read each source file directly and extract only source-supported
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

- turning risk into generic caution;
- using uncertainty language to avoid a commitment decision;
- treating redundancy as free insurance;
- treating regulatory trend slides as readiness;
- importing generic cybersecurity doctrine beyond the source;
- using nonlinear/chaos language to dodge concrete monitoring thresholds;
- claiming tipping points without a named threshold variable;
- treating cascade stories as evidence without a transmission path;
- confusing migration reversibility with real switching-cost containment;
- using prospect-theory framing as manipulation rather than decision-quality
  inspection.

## Required PR43 Proof

If PR42 opens and enriches this family, PR43 must be a same-nomination packet
usefulness review before any further extraction begins.

PR43 should compare a v9/v10 risk-controls packet with the same nominations and
ask:

> Did reviewed risk/reversibility/failure-containment depth make the future
> LLM better equipped to use, merge, ignore, or set aside these shelves without
> increasing candidate count or selecting a final answer?

PR43 should not answer the user case, choose final Decision Pressure, write
product copy, run live lanes, or promote the compiled artifact into runtime.

## What PR41 Does Not Authorize

PR41 does not authorize:

- runtime packet production;
- prompt changes;
- lane rewrites;
- live `/lolla`;
- model calls;
- judges;
- broad Batch 3b;
- extraction of all 112 graph-only models;
- deterministic pressure selection;
- user-facing Decision Pressure output.

## Recommendation

Open PR42 as one controlled extraction batch for the 12 risk controls /
reversibility / failure-containment models above.

Then require PR43 to compare a v9/v10 packet using the same nominations before
any further extraction begins.

The loop stays:

> Audit the gap. Enrich a narrow family. Prove packet usefulness. Stop before
> the next batch.
