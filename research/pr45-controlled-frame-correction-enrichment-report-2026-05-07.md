# PR45 Controlled Frame Correction Enrichment Report

**Date:** 2026-05-07
**Branch:** `feature/reasoning-substrate-pr45-controlled-frame-correction-enrichment`
**Status:** controlled reviewed extraction batch, draft/review-only
**Decision label:** `controlled_frame_correction_enrichment_ready`

## Question

Can source-backed frame correction / metacognitive blind-spot records help
future reasoning packets test whether plausible, executable, and risk-checked
advice is still being evaluated through the wrong frame, evidence boundary,
reasoning mode, or counterfactual?

PR45 answers this only at the substrate layer. It does not answer a user case,
choose Decision Pressure, wire runtime, change prompts, rewrite lanes, call
models, run judges, or promote v11. It reads 12 repo-custodied canonical source
files and extracts only the operational depth those files support.

## Batch Shape

| Measure | Count |
| --- | ---: |
| Runtime graph models | 222 |
| Repo-custodied source files | 222 |
| v10 reviewed records before PR45 | 122 |
| PR45 target models | 12 |
| PR45 batch records | 12 |
| PR45 affordances | 12 |
| PR45 absence records | 24 |
| v11 reviewed records after PR45 | 134 |
| v11 reviewed affordances | 170 |
| v11 absence records | 253 |
| Runtime models still graph-only after v11 | 88 |
| v11 source evidence references | 3300 |
| v11 treatment requirements | 277 |
| v11 diagnostic questions | 604 |
| v11 misuse guards | 579 |

Compiled artifact:

- `data/compiled/model_affordances/affordances_v11.json`
- `data/compiled/model_affordances/quality_report_v11.md`
- status: `draft_review_only`
- schema validation failures: `0`
- source quote rejections: `0`

## Target Outcomes

| Model | Source file | Extraction outcome | Reviewed affordance | Absences |
| --- | --- | --- | --- | ---: |
| `cognitive-gaps-assessment` | `Cognitive_Gaps_Assessment_rag.md` | `strong_affordance_record` | `cognitive-gaps-assessment.missing-reality-gap-audit` | 2 |
| `critical-thinking` | `Critical_Thinking_rag.md` | `strong_affordance_record` | `critical-thinking.claim-evidence-assumption-check` | 2 |
| `counterfactual-reasoning` | `Counterfactual_Reasoning_rag.md` | `strong_affordance_record` | `counterfactual-reasoning.plausible-alternative-branch-test` | 2 |
| `metacognitive-questioning` | `Metacognitive_Questioning_rag.md` | `strong_affordance_record` | `metacognitive-questioning.process-inspection-next-question-gate` | 2 |
| `reasoning-mode-router` | `Reasoning_Mode_Router_rag.md` | `strong_affordance_record` | `reasoning-mode-router.context-driven-mode-selection-check` | 2 |
| `reframing-perspective` | `Reframing_Perspective_rag.md` | `strong_affordance_record` | `reframing-perspective.decision-variable-reframe-test` | 2 |
| `theory-induced-blindness` | `Theory_Induced_Blindness_rag.md` | `strong_affordance_record` | `theory-induced-blindness.favored-framework-blindness-check` | 2 |
| `einstellung-effect` | `Einstellung_Effect_rag.md` | `strong_affordance_record` | `einstellung-effect.familiar-solution-lock-in-interrupt` | 2 |
| `dialectical-reasoning` | `Dialectical_Reasoning_rag.md` | `strong_affordance_record` | `dialectical-reasoning.bounded-antithesis-synthesis-test` | 2 |
| `bias-blind-spot` | `Bias_Blind_Spot_rag.md` | `strong_affordance_record` | `bias-blind-spot.self-bias-accountability-check` | 2 |
| `false-precision-avoidance` | `False_Precision_Avoidance_rag.md` | `strong_affordance_record` | `false-precision-avoidance.decision-relevant-precision-boundary` | 2 |
| `wysiati` | `WYSIATI_rag.md` | `strong_affordance_record` | `wysiati.missing-evidence-denominator-audit` | 2 |

All 12 target models were graph-only in v10. Each now has one compact reviewed
affordance and two absence records. None were rescued with generic mental-model
knowledge. The records are intentionally narrow enough that PR46 can test
whether they improve the same packet handoff rather than merely increase corpus
size.

## What The Source Reading Added

`cognitive-gaps-assessment` now gives the packet missing-reality gap auditing.
It asks whether the advice lacks information, capability, perspective, or
communication transfer before action. Its absence records block gap-mapping
rituals and expertise-as-gap-closure.

`critical-thinking` now gives the packet claim/evidence/assumption separation.
It asks whether story, authority, emotion, or first impression is doing work
that evidence has not earned. Its absence records block detachment theater and
endless questioning as false rigor.

`counterfactual-reasoning` now gives the packet plausible alternative branch
testing. It asks which omitted path, failure branch, or alternative scenario was
genuinely open before commitment. Its absence records block fictional
counterfactuals and hindsight-contaminated alternatives.

`metacognitive-questioning` now gives the packet a bounded next-question gate.
It asks how the answer knows, where the chain is weak, and which question would
change the path. Its absence records block infinite deferral and strategy-only
questioning that ignores execution.

`reasoning-mode-router` now gives the packet context-driven mode selection. It
asks whether the case needs diagnosis, creative exploration, adversarial
critique, execution planning, or another mode. Its absence records are the most
important guardrail in the batch: no deterministic case-type mode router, and
no routing debate as progress.

`reframing-perspective` now gives the packet decision-variable reframing. It
asks whether a new frame changes the success criterion, primary variable,
visible trade-off, or next action. Its absence records block euphemism and
conversation reset.

`theory-induced-blindness` now gives the packet favored-framework blindness
checking. It asks what the current model makes visible, what it filters out,
and which alternative cut would expose missing signal. Its absence records
block endless theory shopping and treating a framework as complete territory.

`einstellung-effect` now gives the packet familiar-solution lock-in
interruption. It asks whether the first solution arrived too fast because prior
experience supplied a stale template. Its absence records block rejecting all
prior knowledge and mistaking fluency for template fit.

`dialectical-reasoning` now gives the packet bounded antithesis and synthesis.
It asks for the strongest opposing view and the partial truth each side
preserves before producing a bounded synthesis or next step. Its absence
records block endless contrarianism and compromise for peace.

`bias-blind-spot` now gives the packet self-bias accountability. It asks where
the reviewer or advising party may be distorted before diagnosing only the
other side. Its absence records block performative humility and bias labels for
other people only.

`false-precision-avoidance` now gives the packet decision-relevant precision
boundaries. It asks whether exactness changes the decision or only the feeling
of confidence, and whether a range or threshold would be better. Its absence
records block simplicity that hides uncertainty and simplicity as weak-analysis
excuse.

`wysiati` now gives the packet missing-evidence denominator auditing. It asks
what evidence, denominator, disconfirming case, or absent briefing side is
missing from the coherent story. Its absence records block coherent story as
proof and available evidence as the complete picture.

## Corpus Lessons

Frame-correction depth is not generic metacognition. The useful material is
operational:

- convert a suspected gap into a named missing condition and plan consequence;
- separate claim, evidence, assumption, authority, emotion, and story;
- recover plausible alternative branches without hindsight fiction;
- name the next discriminating question and the action attached to it;
- suggest reasoning mode only as reviewer/LLM handoff material, not runtime
  routing;
- show which decision variable changes under a new frame;
- ask what the favored framework filters out;
- interrupt familiar solution lock-in without rejecting useful expertise;
- preserve opposing truths without endless contrarianism;
- turn bias checks inward before diagnosing others;
- replace fake exactness with ranges, thresholds, or useful approximation;
- name the missing denominator behind a coherent story.

No target source was too thin for a compact reviewed affordance. The important
caveat is that each record is still one operational card, not full doctrine.
PR45 should not be read as proof that the frame-correction family is complete
or that v11 is ready for runtime.

## Boundary

PR45 adds reviewed substrate only:

- no live `/lolla`;
- no prompt changes;
- no lane rewrites;
- no live lane adapter;
- no runtime packet production;
- no v11 runtime promotion;
- no model calls;
- no judges;
- no Batch 3b;
- no Observatory, memo, Step 8, Step 6, or Lane 4 runtime wiring;
- no user-facing Decision Pressure;
- no deterministic final pressure selection;
- no deterministic reasoning-mode routing.

Python validates schema, quote custody, compile shape, counts, and dormancy. It
does not decide what a future packet should use, merge, ignore, or set aside.

## Recommendation

PR46 should be a same-nomination packet usefulness review:

1. Build or regenerate a frame-correction packet against v10, where the 12 PR45
   models are graph-only.
2. Build or regenerate the same nomination set against v11, where those 12
   cards have reviewed depth.
3. Compare handoff usefulness only:
   - activation clarity;
   - evidence-needed clarity;
   - do-not-use clarity;
   - misuse guard usefulness;
   - treatment usefulness;
   - absence/overclaim protection;
   - burden.

Do not extract another family until PR46 shows that PR45 made the handoff
better rather than merely heavier.
