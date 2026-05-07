# PR38 V8 Graph-Only Priority Audit

**Date:** 2026-05-07
**PR slice:** PR38 - after-v8 graph-only priority audit
**Status:** docs/research audit; no extraction, runtime, prompt, lane, model-call,
judge, UI, memo, or user-facing surface
**Decision label:** `v8_graph_only_priority_audit_complete`

## Purpose

PR37 showed that v8 reviewed depth improves one trust/negotiation packet
handoff. The next question is not "how do we finish the remaining 124?"

The next question is:

> Which remaining graph-only family is likely to make future packets thin enough
> that controlled enrichment is justified?

This audit answers that question before opening another extraction batch.

## Method

The audit uses structured repo artifacts only:

- `data/knowledge_graph.json`
- `data/compiled/model_affordances/affordances_v8.json`
- `data/model_sources/manifest.json`
- `data/curated/compiled_chunks.json`
- existing static route signals in the runtime graph

No source parsing, regex extraction, model calls, judges, live lanes, prompt
changes, or affordance extraction were performed.

The audit treats deterministic counts as custody and prioritization evidence,
not semantic judgment. Family labels below are reviewer groupings for planning;
they are not runtime classes and must not become case-type rules.

## Corpus State After V8

| Measure | Count |
| --- | ---: |
| Runtime graph models | 222 |
| Repo-custodied source files | 222 |
| v8 reviewed records | 98 |
| v8 reviewed affordances | 134 |
| v8 absence records | 181 |
| Graph-only runtime models after v8 | 124 |
| v8 status | `draft_review_only` |

## Reasoning-Type Gaps After V8

The largest remaining graph-only gaps are still broad reasoning operations:

| Reasoning type | Runtime models | v8 reviewed | Graph-only after v8 |
| --- | ---: | ---: | ---: |
| `diagnostic` | 102 | 43 | 59 |
| `metacognitive` | 77 | 27 | 50 |
| `systems` | 87 | 40 | 47 |
| `causal` | 77 | 35 | 42 |
| `probabilistic` | 34 | 18 | 16 |
| `analogical` | 18 | 5 | 13 |
| `deductive` | 26 | 13 | 13 |
| `counterfactual` | 27 | 16 | 11 |
| `abductive` | 5 | 1 | 4 |

This does not mean the next batch should simply be "diagnostic." The category
is too wide. It means any next family should probably carry diagnostic,
systems, causal, or metacognitive operational value.

## Static Lane-Signal Read

After v8, the highest remaining graph-only static lane signals are:

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

This is a real constraint on the recommendation.

If PR39 were selected by static lane signal alone, the next batch would be
metacognitive/reframing/exploration heavy. That is a plausible later family,
but it has a near-term risk: many of those cards can become "think about your
thinking" material, which may add analysis texture without improving the
action handoff.

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

- It has the strongest remaining static lane-signal cluster.
- It directly supports unknown-unknown discovery and frame shifts.

Why it is not first:

- It is closest to the old danger of "more thinking about thinking."
- It may produce packets that sound sophisticated but do not change execution.
- Several graph-only cards may be sufficient as lightweight neighboring shelf
  hints until a concrete packet shows they are thin.

Recommended status: keep as a serious later candidate, but do not make it the
next extraction batch by default.

### 2. Execution / Implementation / Follow-Through Discipline

Representative graph-only shelves:

- `algorithmic-thinking`
- `auditability-traceability`
- `baseline-establishment`
- `bottlenecks`
- `debugging-strategies`
- `devops-and-continuous-integration`
- `feedback-loops`
- `goal-setting`
- `habit-formation`
- `input-vs-output-goals`
- `iteration`
- `lean-startup-methodology`

Why it is attractive:

- It tests the next product gap after evidence, competition, communication,
  trust, persuasion, and signaling: advice turning into execution.
- It is action-adjacent without being user-facing output.
- The graph fields already point at handoffs, baselines, feedback, bottlenecks,
  checkpoints, error correction, and repeated behavior.
- These cards are likely to help the next LLM ask, "What makes this plan
  executable, inspectable, adjustable, and stoppable?"

Why it is not a deterministic slam dunk:

- It does not dominate the static lane-signal table.
- Some candidates have low static route counts and are selected by product
  hypothesis plus graph-field fit, not by frequency alone.

Recommended status: best PR39 candidate family, because the product gap is
strong and the likely packet handoff is concrete.

### 3. Market / Customer / Product Dynamics

Representative graph-only shelves:

- `lean-startup-methodology`
- `user-experience-research-methods`
- `usability-heuristics`
- `price-discrimination`
- `supply-and-demand`
- `switching-costs`

Why it is attractive:

- Product and market cases are likely future user scenarios.
- Several shelves could produce operational evidence and misuse guards.

Why it is not first:

- It is narrower than the execution family.
- Some product/customer depth already exists after PR32 via
  `jobs-to-be-done` and `user-centered-design`.

Recommended status: later controlled batch if product cases keep pulling these
models.

### 4. Risk / Resilience / Operational Failure

Representative graph-only shelves:

- `risk-vs-uncertainty`
- `redundancy`
- `regulatory-horizon-scanning`
- `cybersecurity-thinking-models`
- `non-linear-dynamics`
- `tipping-points`

Why it is attractive:

- Strong before-action relevance.
- Could produce tripwires, monitoring, fallback, and failure-mode depth.

Why it is not first:

- v5/v6 already contain strong uncertainty, risk, resilience, and systems
  support.
- This family should be selected when a packet shows the existing risk layer is
  thin, not because the names are obviously useful.

Recommended status: defer until a packet gap points at it.

## Recommended PR39 Family

Recommended family:

> Execution / implementation / follow-through discipline.

Decision label for PR39 if opened:

> `controlled_execution_followthrough_enrichment_ready`

This family is not selected because it wins every deterministic count. It is
selected because it best matches the next product question:

> Once AI advice sounds plausible, what operational conditions make acting on it
> executable, inspectable, adjustable, and stoppable?

That is exactly the place where a graph-only packet can become thin.

## Recommended PR39 Target Set

Recommended cap: 12 models.

| Model ID | Reasoning types | Static lane signals | Source bytes | Why it belongs |
| --- | --- | ---: | ---: | --- |
| `algorithmic-thinking` | deductive, systems | 0 | 17495 | Turns plans into repeatable steps, handoffs, inputs, and output checks. |
| `auditability-traceability` | deductive, systems | 3 | 15346 | Keeps decisions and outputs inspectable instead of opaque. |
| `baseline-establishment` | diagnostic, systems | 0 | 15150 | Defines starting facts and success criteria before comparison. |
| `bottlenecks` | systems, causal | 1 | 16007 | Identifies the true throughput limiter instead of local noise. |
| `debugging-strategies` | causal, diagnostic | 0 | 15370 | Converts ambiguous failure into a testable failure condition and cause search. |
| `devops-and-continuous-integration` | systems, causal | 0 | 17761 | Tests delivery reliability, rollback, integration friction, and operator constraints. |
| `feedback-loops` | causal, systems | 1 | 16855 | Requires observed consequences to change the next action. |
| `goal-setting` | deductive, systems | 0 | 16360 | Aligns trade-offs, sequencing, and measurement around one explicit outcome. |
| `habit-formation` | causal, metacognitive | 1 | 15715 | Moves execution from one heroic effort to repeated behavior design. |
| `input-vs-output-goals` | causal, diagnostic | 0 | 15582 | Distinguishes desired results from repeatable behaviors and checkpoints. |
| `iteration` | causal, metacognitive | 2 | 13284 | Adds prototype-test-learn cycles, thresholds, and stop rules. |
| `lean-startup-methodology` | causal, diagnostic | 1 | 15033 | Tests fragile product/market hypotheses before polished execution. |

The byte counts are not proof of source quality. They are only a custody/richness
sanity check. PR39 extraction must still allow `thin_narrow_affordance_record`,
`absence_record`, or `do_not_promote_recommendation` if the source does not
support operational depth.

## Extraction Standard If PR39 Opens

PR39 should read each source file directly and extract only source-supported
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

- turning execution discipline into generic productivity advice;
- treating process as proof of judgment;
- confusing output metrics with meaningful progress;
- adding checklists without failure conditions;
- using iteration to avoid commitment;
- using traceability as documentation theater;
- treating habits as moral virtue rather than environment/behavior design.

## What PR38 Does Not Authorize

PR38 does not authorize:

- runtime packet production;
- prompt changes;
- lane rewrites;
- live `/lolla`;
- model calls;
- judges;
- broad Batch 3b;
- extraction of all 124 graph-only models;
- deterministic pressure selection;
- user-facing Decision Pressure output.

## Recommendation

Open PR39 as one controlled extraction batch for the 12 execution /
implementation / follow-through models above.

Then require PR40 to compare a v8/v9 execution packet using the same
nominations before any further extraction begins.

The loop stays:

> Audit the gap. Enrich a narrow family. Prove packet usefulness. Stop before
> the next batch.
