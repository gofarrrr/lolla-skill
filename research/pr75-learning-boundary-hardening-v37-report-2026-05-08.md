# PR75 v37 Learning Boundary Hardening Report

Date: 2026-05-08

Branch: `feature/knowledge-substrate-pr75-learning-boundary-v37`

## Verdict

PASS as dormant reviewed substrate.

PR75 does not touch `/lolla`, prompts, lane adapters, packet rendering, or live product behavior. It is a learning/metacognition hardening pass only.

## Why This PR Exists

The completed v36 corpus still has single-affordance learning records that are source-rich but should not be blindly split. PR75 audits whether the learning/metacognition cluster needs more positive affordance identity or sharper transaction boundaries.

The answer is: no new positive splits.

The useful work is boundary precision:

- keep broad scaffolding and educational scaffolding from coactivating as the same card;
- prevent growth mindset from overriding feasibility evidence and stop criteria;
- make tacit perceptual cue extraction operational without turning it into generic expert interviewing;
- make metacognitive questioning close the loop from variables to next question to consolidation.

## Source Files Re-Read

Canonical/source-custodied files were read directly:

- `Scaffolding_rag.md`
- `Scaffolding_Educational_rag.md`
- `Growth_Mindset_rag.md`
- `Perceptual_Learning_rag.md`
- `Metacognitive_Questioning_rag.md`

Adjacent ownership was also checked from the current records:

- `metacognitive-questioning.expert-process-elicitation`
- `cognitive-load-theory.cognitive-load-source-diagnosis`
- `expertise-reversal-effect.expertise-calibrated-support-retuning`
- `desirable-difficulties.productive-struggle-calibrator`
- `base-rates.outside-view-reference-class-anchor`
- `sunk-cost-fallacy.stop-loss-reframe`

## Changes Made

### Scaffolding

No new positive affordance.

Added absence/routing guard:

- `instructional-novice-scaffold-as-generic-scaffolding`

Purpose:

Broad scaffolding owns staged temporary support and workflow sequencing. If the case specifically turns on novice instructional degree-of-freedom reduction, route to `scaffolding-educational` so the receiver preserves the instructional mastery and fading contract.

### Scaffolding Educational

No new positive affordance.

Added absence/routing guard:

- `generic-workflow-staging-as-educational-scaffolding`

Purpose:

Educational scaffolding owns novice-to-autonomy instructional support. If the case is generic project sequencing or temporary process structure without a novice instructional gap, route to `scaffolding`.

### Growth Mindset

No new positive affordance.

Added absence/routing guard:

- `growth-language-overrides-base-rates-or-stop-criteria`

Purpose:

Growth mindset is useful when capability is genuinely developable through feedback and repetition. It should not become persistence rhetoric that overrides base rates, sunk-cost exposure, constraints, missing resources, weak strategy, or stop criteria.

### Perceptual Learning

No new positive affordance.

Existing affordance hardened:

- `perceptual-learning.train-cue-discrimination`

Added treatment requirement:

- `extract-tacit-cues-with-stories-and-pari`

Purpose:

The source supports Cognitive Task Analysis, asking for stories rather than advice, and PARI: precursor, action, result, and interpretation. PR75 makes that operational only when the receiver action is cue discrimination, anomaly detection, or training-surface construction. Generic expert interviewing remains owned by `metacognitive-questioning.expert-process-elicitation`.

### Metacognitive Questioning

No new positive affordance.

Existing affordance hardened:

- `metacognitive-questioning.process-inspection-next-question-gate`

Added treatment requirement:

- `cycle-variables-question-and-consolidation`

Purpose:

The source describes a structured deep-thinking cycle: review relevant variables, define the next-step question, then consolidate gains. PR75 adds that as a treatment requirement so metacognitive questioning does not stop at elegant questions without a changed plan, confidence state, test, owner, or decision.

## v37 Artifact Summary

Compiled artifact:

- `data/compiled/model_affordances/affordances_v37.json`
- `data/compiled/model_affordances/quality_report_v37.md`

Metadata:

- Artifact: `model_affordances_v37`
- Status: `draft_review_only`
- Records: 222
- Affordances: 271
- Absence records: 509
- Schema failures: 0
- Source hash failures: 0
- Source quote rejections: 0

Delta from v36:

- Affordances: 271 -> 271
- Absences: 506 -> 509

## Why This Is Not Bloat

PR75 adds zero positive affordance IDs.

It rejects the tempting expansion path:

- Scaffolding does not split into every staged-workflow use.
- Educational scaffolding does not absorb generic project sequencing.
- Growth mindset does not become motivational persistence.
- Perceptual learning does not become generic expert interviewing.
- Metacognitive questioning does not become reflection ceremony.

The useful work is routing and treatment precision.

## Runtime Safety

This PR remains dormant substrate only.

No live runtime path imports v37. The PR75 test scans:

- `engine/system_b/__init__.py`
- `engine/system_b/pipeline.py`
- `engine/system_b/reasoning_substrate_packet.py`
- `engine/system_b/reasoning_substrate_packet_review.py`
- `scripts/run_pipeline.py`

Expected result: `affordances_v37` and `model_affordances_v37` appear only in tests and compiled artifact files, not live runtime paths.

## Verification

```bash
pytest tests/test_pr75_v37_learning_boundary_hardening.py \
  tests/test_pr74_v36_communication_boundary_hardening.py \
  tests/test_pr73_v35_reasoning_integrity_hardening.py \
  tests/test_model_affordance_compiler.py

rg -n "affordances_v37|model_affordances_v37" engine scripts tests -g '*.py'

git diff --check
```

## Next Corpus Frontier

The next bounded pass should use the decision/risk/probability audit:

- harden `expected-value`;
- add guards for `risk-assessment`, `false-precision-avoidance`, and `bayesian`;
- keep the rest as PASS unless direct source reading finds a receiver-transaction change.
