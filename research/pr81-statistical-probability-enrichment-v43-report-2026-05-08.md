# PR81 Statistical Probability Enrichment v43 Report

Date: 2026-05-08

Branch: `feature/knowledge-substrate-pr81-statistical-probability-v43`

## Verdict

PASS as dormant reviewed substrate enrichment.

PR81 does not wire affordances into `/lolla`, prompts, packet pickup, lane
adapters, Observatory, or product runtime. It improves only the reviewed
knowledge base and compiles a dormant v43 artifact.

## What Changed

PR81 reviews the statistical, probabilistic, model-fit, simulation, and
uncertainty family through the PR55 receiver-transaction lens.

Compiled artifact:

- Artifact: `model_affordances_v43`
- Status: `draft_review_only`
- Records: `222`
- Affordances: `278`
- Absence records: `536`
- Schema failures: `0`
- Source hash failures: `0`
- Source quote rejections: `0`

Delta from v42:

- `+1` affordance
- `+16` absence records
- No live runtime references

## Positive Split

Added one transaction-distinct affordance:

- `data-science-reasoning-framework.assumption-pressure-before-analytic-output`

Why this split clears the bar:

The existing data-science card owns question, measurement, modeling, and
communication handoff. The new card owns a later and different transaction:
when an analytic thesis or model output already looks coherent, the receiver
must expose what would have to be believed, what facts would resolve the issue,
and what antithesis must be met before accepting the output.

This changes activation, evidence, treatment, and use/reject/defer behavior. It
is not a generic red-team card, and it is not runtime model-calling. It is a
source-backed pressure step for analytic outputs whose hidden premises may be
doing too much work.

## Absence Rails Added

Added sixteen absence records:

- `base-rates.old-frequency-after-regime-shift`
- `probabilistic-thinking.standalone-conjunctive-disjunctive-probability-affordance`
- `law-of-large-numbers.large-n-confidence-with-wrong-population`
- `risk-vs-uncertainty.point-estimate-commitment-under-true-uncertainty`
- `false-precision-avoidance.precision-avoidance-in-exact-domain`
- `bayesian.decorative-update-with-weak-priors`
- `data-science-reasoning-framework.proxy-metric-as-underlying-reality`
- `monte-carlo-methods.simulation-erases-unknown-unknowns-or-structural-breaks`
- `monte-carlo-methods.simulation-complexity-over-dominant-driver`
- `statistical-learning-theory.predictive-fit-as-causal-understanding`
- `statistical-learning-theory.confirmation-shaped-model-selection`
- `statistical-learning-theory.training-narrative-with-censored-failures`
- `statistics-concepts.headline-mean-as-full-distribution`
- `regression-to-the-mean.reversion-confidence-from-flawed-mean`
- `markov-chains.unstable-transition-regime-as-stationary-risk`
- `markov-chains.emergent-social-system-as-mechanical-state-path`

These are reject/defer rails, not content dumps. They make future packet use
less likely to launder statistical language into authority:

- old frequencies do not survive real regime shifts;
- probability language should not steal ownership from conjunction/failure-path
  records;
- large samples do not rescue wrong-population evidence;
- point estimates should not size commitments under true uncertainty;
- anti-precision must not erase precision in exact domains;
- Bayesian-looking arithmetic does not calibrate weak priors;
- proxy metrics are not the underlying reality;
- simulations cannot sample unknown unknowns or structural breaks;
- simulation complexity can hide a simpler dominant driver;
- predictive fit is not causal explanation;
- model selection cannot merely confirm a preferred hypothesis;
- training stories with censored failures belong to survivorship checks;
- headline means are not full distributions;
- regression-to-the-mean requires a trustworthy baseline;
- state-transition reasoning cannot assume stationarity under unstable regimes;
- emergent social implementation is not a mechanical state path.

## Compression Decisions

Most rich source material stayed compressed.

Kept as-is:

- `base-rates`: outside-view reference-class anchoring remains one affordance.
- `probabilistic-thinking`: range, tail, sensitivity, and update thresholds
  remain one decision gate.
- `bayesian`: prior, signal, posterior, and commitment remain one update
  discipline.
- `regression-to-the-mean`: baseline-before-causal-story remains one card.
- `law-of-large-numbers`: the existing two-card split remains sufficient:
  repeated-sample stability plus population/distribution-fit validity.
- `statistics-concepts`: sample, denominator, assumption, and distribution
  checks remain one statistics card.
- `statistical-learning-theory`: prediction, generalization, and decision
  usefulness remain one predictive-model card.
- `monte-carlo-methods`: range/tail/input-quality stress testing remains one
  simulation card.
- `markov-chains`: state-transition boundary remains one medium-confidence
  card; new material is guarded as rejection/defer rails.
- `risk-vs-uncertainty`: commitment sizing remains one live-decision card; the
  postmortem decision/outcome idea is left unpromoted because it overlaps
  hindsight/outcome-bias ownership.

Rejected tempting splits:

- standalone conjunctive/disjunctive probability inside probabilistic thinking;
- a third law-of-large-numbers sample-threshold card;
- a standalone Monte Carlo unknown-unknowns card;
- a general data-science red-team workflow;
- a Markov sequential-gate fragility card;
- a risk-vs-uncertainty postmortem review card.

Those ideas are real, but PR81 treats them as guards, handoff conditions, or
adjacent-record ownership unless they create a clean independent transaction.

## Risk Controls

PR81 is aimed at three substrate risks:

- Statistical authority theater: clean numbers, priors, means, or model output
  making weak evidence look earned.
- Simulation theater: ranges and Monte Carlo language hiding bad assumptions,
  unknown unknowns, structural breaks, or simpler drivers.
- Model-fit theater: predictive fit, large samples, or transition paths being
  used outside their valid population, causal boundary, or stationarity
  conditions.

The value of these changes is not more cards for the LLM to recite. The value is
more precise reasons to reject, defer, narrow, or hand off a nominated card.

## Verification

Focused verification should run:

```bash
pytest tests/test_pr81_v43_statistical_probability_enrichment.py tests/test_pr80_v42_communication_guard_enrichment.py tests/test_model_affordance_compiler.py
rg -n "affordances_v43|model_affordances_v43" engine scripts tests -g '*.py'
git diff --check
jq '.compile_metadata.validation' data/compiled/model_affordances/affordances_v43.json
```

Expected result:

- Target records validate against schema and exact source quotes.
- v43 preserves all 222 v42 model IDs.
- v43 adds exactly one affordance ID.
- v43 adds exactly sixteen absence fields.
- v43 remains dormant and unreferenced by live runtime paths.

## Next Ring

Continue family-by-family enrichment under the same rule:

Only add a positive affordance when it creates a materially different receiver
transaction. Otherwise harden treatment, absence rails, or source custody.

Good next candidates are likely decision-method, learning/cognition, and
implementation-followthrough families where sources may contain high-value
reject/defer rails that keep future packets from becoming confident vocabulary
instead of better judgment.
