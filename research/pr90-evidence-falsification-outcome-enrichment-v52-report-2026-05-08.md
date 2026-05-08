# PR90 Evidence, Falsification, And Outcome-Quality Enrichment v52 Report

Date: 2026-05-08

Status: PASS as dormant reviewed substrate. REVISE before runtime pickup.

## Scope

PR90 reviewed an evidence/falsification/outcome-quality ring after v51:

- `counterfactual-reasoning`
- `true-uncertainty-navigation`
- `scientific-method-evidence-testing`
- `premortem`
- `logical-fallacies`
- `falsifiability`
- `step-back`

Two read-only explorer audits were used as cross-checks. The implementation remained data-only: no runtime, prompt, lane, packet, product, or user-facing behavior changed.

## Contradicting Evidence First

The risky interpretation would be: “these sources are rich, so split them heavily.” That would be wrong.

Most of the source richness is method detail, examples, or adjacent ownership:

- SMET work planning and MECE material belongs inside the existing falsifiable threshold-test card or adjacent experimentation/verification records.
- Falsifiability’s red-team, dialectic, sensitivity, and Feynman material supports the existing reversal-gate affordance.
- Premortem’s tail risk, known/unknowns, second-order thinking, and competitive strategy material supports one core operation: simulated failure before commitment converted into plan changes.
- Logical fallacies should not become a general wrong-model detector, debate scorer, or causal-proof duplicate.
- Step Back already has the right transaction: bounded reorientation before execution, then return to a concrete move.

The source-backed split was narrower:

- `counterfactual-reasoning` needed a separate retrospective outcome-quality card.
- `true-uncertainty-navigation` needed a separate outcome-decoupled decision-quality card.

These look similar at first. The boundary is:

- Counterfactual reasoning reconstructs plausible branches and outcomes from the decision time after an outcome exists.
- True uncertainty evaluates whether the decision process fit preferences, available information, and uncertainty level, without treating the result as proof.

## Accepted Positive Splits

### Counterfactual Reasoning

Retained and narrowed:

- `counterfactual-reasoning.plausible-alternative-branch-test`

It now focuses on pre-commitment branch pressure: expose plausible omitted paths before a preferred path locks in.

Key source support:

- `Best when leaders need to expose omitted scenarios before locking in a plan`
- `Works when learning depends on exploring omitted paths, not just observed results`
- `Challenging the Initial Hypothesis`
- `challenged and pressure-tested`

Added:

- `counterfactual-reasoning.outcome-quality-retrospective`

This card activates after an outcome exists and the team is confusing the result with decision quality. It reconstructs what was known at the time, which branches were plausible, and what hindsight is now distorting.

Key source support:

- `placing the actual outcome in the proper context of other potential outcomes that existed at the time a decision was made`
- `reconstructing a simplified version of the decision process and exploring paths not taken`
- `separate "what happened" from "what could reasonably have happened" under the information available at the time`
- `a team is treating one outcome as proof that the decision process was right or wrong`
- `the actual outcome to "overfit" the decision quality`

Added absence rail:

- `bad-outcome-excuse-only-counterfactuals`

Why:

- The source warns that people are `more eager to put bad outcomes in context than good ones`.

### True Uncertainty Navigation

Retained:

- `true-uncertainty-navigation.scenario-bound-robust-action`

It remains the prospective card for moving from single-forecast false certainty to plausible paths, triggers, options, and commitment shape.

Added:

- `true-uncertainty-navigation.outcome-decoupled-decision-quality`

This card activates when outcome quality, luck, regret, blame, or helplessness is being confused with whether a decision was good under true uncertainty.

Key source support:

- `separating the quality of the *decision* from the quality of the *outcome*`
- `a good decision is one that is consistent with the preferences and complete information of a decision maker; a good outcome is desirable`
- `the best way to achieve good outcomes in the long run, short of being all-knowing`
- `overcome feelings of helplessness that often paralyze their actions`

Added absence rail:

- `outcome-quality-as-decision-quality-proof`

Why:

- A desirable or undesirable outcome should not be promoted as proof that the decision process was sound or unsound.

## Accepted Absence Rails

### Scientific Method Evidence Testing

Added:

- `premature-data-analysis-as-evidence-testing`

Why:

- The source warns against jumping into data or powerful tools before problem structure and testable hypotheses are defined.

Key source support:

- `wade prematurely into data using powerful tools without first thinking through the underlying structure of the problem`
- `jump prematurely into data without defining the problem structure or testable hypotheses`
- `Focus first on **rigorously framing the question or hypothesis** before starting complex data work.`

No positive split was added. The current SMET affordance already covers hypothesis, falsifier, proxy, threshold, and evidence use.

### Premortem

Added:

- `pro-con-list-as-premortem-substitute`
- `runtime-simulation-or-ai-persona-behavior`

Why:

- A pro-con list makes positives more available and misses the backward failure-simulation move.
- Digital twins and multi-agent simulations appear as advanced stress-testing examples, not as a requirement or permission for runtime persona simulation.

Key source support:

- `a simple pro-con list tends to accentuate the positives and overlook negatives, the exact opposite of the Premortem's goal`
- `using **Digital Twins** or multi-agent simulations to pre-validate decisions *in silico* and stress-test edge cases with "extreme" AI personas`

No positive split was added. The premortem transaction remains simulated failure before commitment converted into owners, mitigations, thresholds, or decision changes.

### Logical Fallacies

Added:

- `logical-validity-as-implementation-plan`

Why:

- The source says logic may fail to bridge from knowing what to do to executing how to do it. This is an important anti-reasoning-theater guard.

Key source support:

- `Logic often fails to bridge the gap between understanding *what* to do and executing *how* to do it`
- `overlooks the complexity of human action`

No positive split was added. Logical fallacies remains an argument-validity inspection card, not a fallacy classifier, implementation planner, or debate weapon.

## No-Change Decisions

### Falsifiability

No change.

Reason:

- The current `falsifiability.disconfirming-reversal-gate` already carries the source’s core transaction: user-verifiable dismissal path, kill criterion, reversal condition, and anti-theater guard.
- Sensitivity analysis, dialectic, red-team, five-whys, and Feynman material support the same reversal-gate operation or belong to adjacent records.

### Step Back

No change.

Reason:

- The current `step-back.reorientation-before-execution-gate` already captures the source’s transaction: pause when reorientation improves the next concrete move.
- Logic trees, Feynman learning gaps, and story/pitch packaging are techniques or adjacent-owner material, not separate step-back affordances.

## Anti-Sycophancy Review

Verdict: PASS as dormant substrate. REVISE before runtime pickup.

What would have to be true:

- Counterfactual retrospective and true-uncertainty decision-quality cards must remain distinguishable. Status: SOLID in data shape, UNTESTED in packet display.
- New absence rails must block overclaiming rather than become negative-use affordances. Status: SOLID in data, UNTESTED in receiver behavior.
- No source-rich but transaction-weak material should be promoted. Status: SOLID for this PR.
- Runtime must not automatically pick up v52. Status: SOLID.

Potential failure modes:

- Receiver collapses both outcome-quality cards into generic “don’t judge by outcomes” advice.
- Counterfactual retrospective becomes excuse-making after failure.
- True uncertainty card becomes deterministic hindsight grading.
- Premortem simulation absence is misread as forbidding all simulation context rather than forbidding runtime persona overclaiming.
- Absence rails remain hidden in future packets and fail to influence LLM behavior.

What would falsify this PR direction:

- Static packet stress review shows the two new positive cards are indistinguishable to reviewers.
- The counterfactual card is repeatedly used without reconstructing what was known at the time.
- The true uncertainty card is repeatedly used without preferences, available information, or uncertainty level.
- The new absence rails do not change reviewer/LLM treatment of fake rigor, pro-con premortems, or logic-as-implementation.

## Compiled Artifact

Compiled with:

- Artifact: `model_affordances_v52`
- Status: `draft_review_only`
- Records: `222`
- Affordances: `298`
- Absence records: `578`
- Schema-validation failures: `0`
- Source-quote rejections: `0`

Delta from v51:

- Positive affordances: `+2`
- Absence records: `+6`
- Model coverage: unchanged
- Runtime imports: unchanged

## Validation

Commands:

```bash
python3 scripts/compile_model_affordances.py --record-dir data/model_affordances/pilot --record-dir data/model_affordances/batch_1 --record-dir data/model_affordances/batch_2 --record-dir data/model_affordances/batch_3a --record-dir data/model_affordances/batch_4 --record-dir data/model_affordances/batch_5 --record-dir data/model_affordances/batch_6 --record-dir data/model_affordances/batch_7 --record-dir data/model_affordances/batch_8 --record-dir data/model_affordances/batch_9 --record-dir data/model_affordances/batch_10 --record-dir data/model_affordances/batch_11 --record-dir data/model_affordances/batch_12 --record-dir data/model_affordances/batch_13 --record-dir data/model_affordances/batch_14 --record-dir data/model_affordances/batch_15 --record-dir data/model_affordances/batch_16 --record-dir data/model_affordances/batch_17 --compiled-filename affordances_v52.json --quality-report-filename quality_report_v52.md --artifact-id model_affordances_v52 --report-title "Model Affordance Quality Report v52"
PYTHONPATH=. pytest tests/test_pr90_v52_evidence_falsification_outcome_enrichment.py tests/test_pr89_v51_customer_product_evidence_enrichment.py tests/test_model_affordance_compiler.py
git diff --check
rg -n "affordances_v52|model_affordances_v52" engine scripts -g '*.py'
```

## Runtime Boundary

`affordances_v52.json` is a dormant reviewed artifact. There are no live runtime references to:

- `affordances_v52`
- `model_affordances_v52`

Future live pickup still requires explicit artifact selection, lane provenance preservation, grouped affordance identity, confidence visibility, absence visibility, and receiver-side use/reject/defer grammar.

## Bottom Line

PR90 adds outcome-quality discipline without turning the corpus into a generic rigor sermon.

The new positive cards are intentionally narrow:

- Counterfactual reasoning: reconstruct plausible branches from the time of decision after an outcome exists.
- True uncertainty navigation: evaluate decision quality under ambiguity from preferences, information, and uncertainty level.

The absence rails block fake rigor: data analysis without hypothesis, pro-con lists pretending to be premortems, runtime simulation overclaims, logic-as-implementation, outcome-resulting, and counterfactual excuse-making.
