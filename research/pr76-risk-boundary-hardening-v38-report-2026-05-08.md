# PR76 v38 Risk Boundary Hardening Report

Date: 2026-05-08

Branch: `feature/knowledge-substrate-pr76-risk-boundary-v38`

## Verdict

PASS as dormant reviewed substrate.

PR76 does not touch `/lolla`, prompts, lane adapters, packet rendering, or live product behavior. It is a risk/probability boundary hardening pass only.

## Why This PR Exists

The completed v37 corpus still has probability and risk records where the positive affordance is already strong, but the runtime boundary could be too smooth if the card is later compressed into a receiver packet.

The answer is: no new positive splits.

The useful work is transaction boundary precision:

- make Expected Value disclose assumptions and boundary conditions, not just calculate;
- keep Risk Assessment from treating human-system risk as purely technical;
- keep False Precision Avoidance from rounding away decision-relevant probability work;
- keep Bayesian from absorbing short-run noise or structural-shift claims without an explicit prior/evidence/posterior threshold.

## Source Files Re-Read

Canonical/source-custodied files were read directly:

- `Expected_Value_rag.md`
- `Risk_Assessment_rag.md`
- `False_Precision_Avoidance_rag.md`
- `Bayesian_rag.md`
- `Regression_To_The_Mean_rag.md`
- `Law_of_Large_Numbers_rag.md`

Adjacent ownership was checked through current records and source boundaries:

- `base-rates.outside-view-reference-class-anchor`
- `bayesian.explicit-prior-evidence-update`
- `regression-to-the-mean`
- `law-of-large-numbers`
- `calculated-risk-taking`
- human-context records such as empathy, emotional-intelligence, and understanding-motivations

## Changes Made

### Expected Value

No new positive affordance.

Existing affordance hardened:

- `expected-value.probability-weighted-payoff-boundary`

Added treatment requirement:

- `communicate-assumptions-and-boundary-conditions`

Purpose:

Expected Value should not hand the receiver a single calculated answer that looks self-authorizing. The source explicitly requires sensitivity analysis, assumption disclosure, and boundary-condition communication. PR76 makes that a treatment requirement so EV output remains conditional on the assumptions that make the calculation credible.

### Risk Assessment

No new positive affordance.

Added absence/routing guard:

- `human-system-risk-without-personal-data-routing`

Purpose:

Risk Assessment owns conversion of material downside into mitigations, thresholds, monitoring, decisions, and safeguards. It should not treat a case as purely technical when personal data about how people feel materially changes the risk surface. Collection and interpretation of that human context belongs to adjacent human-context models before risk-assessment converts it into governance.

### False Precision Avoidance

No new positive affordance.

Added absence/routing guard:

- `precision-avoidance-that-blocks-needed-probability-update`

Purpose:

False Precision Avoidance is useful when extra detail does not change action. It becomes dangerous if simplicity removes precision that changes a base-rate comparison or a Bayesian update. PR76 makes that boundary first-class: when the decision turns on meaningful probability variation, route to `base-rates` or `bayesian` rather than simplifying it away.

### Bayesian

No new positive affordance.

Added absence/routing guard:

- `short-run-structural-shift-claim-without-explicit-update`

Purpose:

Bayesian can handle short-run evidence only when the prior, signal reliability, posterior movement, and action threshold are visible. If a short run of wins, losses, or experiment results is being treated as structural change without that update discipline, the receiver should route first to `regression-to-the-mean` or `law-of-large-numbers`.

## v38 Artifact Summary

Compiled artifact:

- `data/compiled/model_affordances/affordances_v38.json`
- `data/compiled/model_affordances/quality_report_v38.md`

Metadata:

- Artifact: `model_affordances_v38`
- Status: `draft_review_only`
- Records: 222
- Affordances: 271
- Absence records: 512
- Schema failures: 0
- Source hash failures: 0
- Source quote rejections: 0

Delta from v37:

- Affordances: 271 -> 271
- Absences: 509 -> 512

## Why This Is Not Bloat

PR76 adds zero positive affordance IDs.

It rejects the tempting expansion path:

- Expected Value does not split into every supporting method such as decision trees, scenario analysis, or business-case writing.
- Risk Assessment does not become generic human-context diagnosis.
- False Precision Avoidance does not become permission to be vague.
- Bayesian does not become a generic short-run evidence story.

The useful work is routing and treatment precision.

## Runtime Safety

This PR remains dormant substrate only.

No live runtime path imports v38. The PR76 test scans:

- `engine/system_b/__init__.py`
- `engine/system_b/pipeline.py`
- `engine/system_b/reasoning_substrate_packet.py`
- `engine/system_b/reasoning_substrate_packet_review.py`
- `scripts/run_pipeline.py`

Expected result: `affordances_v38` and `model_affordances_v38` appear only in tests and compiled artifact files, not live runtime paths.

## Verification

```bash
pytest tests/test_pr76_v38_risk_boundary_hardening.py \
  tests/test_pr75_v37_learning_boundary_hardening.py \
  tests/test_pr74_v36_communication_boundary_hardening.py \
  tests/test_model_affordance_compiler.py

rg -n "affordances_v38|model_affordances_v38" engine scripts tests -g '*.py'

git diff --check
```

## Next Corpus Frontier

The next bounded pass should continue the same method:

- pick a coherent cluster from the remaining corpus;
- reread full source markdown, not just current JSON;
- add positive affordances only when a distinct receiver transaction is supported;
- otherwise prefer absence guards, routing boundaries, and treatment hardening.
