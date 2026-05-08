# PR46 V11 Frame-Correction Packet Usefulness Review

**Date:** 2026-05-07
**Branch:** `feature/reasoning-substrate-pr46-v11-frame-packet-usefulness-review`
**Status:** dormant packet-quality review, no extraction, runtime, prompt,
lane, model-call, judge, memo, UI, or user-facing surface
**Decision label:** `v11_frame_correction_packet_handoff_useful`

## Question

Did PR45 make a frame-correction / metacognitive packet better handoff
material for the next LLM, or did it merely add internal reasoning vocabulary?

PR46 evaluates handoff quality only. It does not answer the synthetic case,
choose Decision Pressure, rank final wisdom, write memo copy, promote v11,
change prompts, rewrite lanes, run live `/lolla`, call models, or run judges.

## Method

PR46 uses the same explicit 12-card nomination set twice:

1. v10 baseline packet, where the PR45 models are still graph-only.
2. v11 treatment packet, where the same models have reviewed source-backed
   affordance depth.

The transaction is synthetic review-only. It represents a leadership team ready
to act on a plausible AI rescue memo that may be overfit to visible evidence,
familiar playbooks, crisp dates, and one favored frame.

Generated artifacts:

- `tests/fixtures/reasoning_substrate_packet/pr46_v10_frame_correction_packet_review.json`
- `tests/fixtures/reasoning_substrate_packet/pr46_v11_frame_correction_packet_review.json`
- `research/reasoning-substrate-packet-pr46-v10-review-render-2026-05-07.md`
- `research/reasoning-substrate-packet-pr46-v11-review-render-2026-05-07.md`
- `research/reasoning-substrate-packet-pr46-v10-v11-comparison-render-2026-05-07.md`

## Count Delta

| Measure | v10 packet | v11 packet | Delta |
| --- | ---: | ---: | ---: |
| Candidate cards | 12 | 12 | 0 |
| Suppressed duplicates | 1 | 1 | 0 |
| Reviewed cards | 0 | 12 | +12 |
| Graph-only cards | 12 | 0 | -12 |
| Missing reviewed records | 12 | 0 | -12 |
| Weak/conflicting cards | 0 | 0 | 0 |
| Visible reviewed source refs | 0 | 12 | +12 |
| Visible absence records | 0 | 12 | +12 |
| Fixture bytes | 45,528 | 70,921 | +25,393 |

The candidate count did not increase. PR45's depth shows up as better card
material for the same nominated shelves, not as more shelves.

## Handoff Judgment

Verdict:

> v11 frame-correction depth is useful handoff material.

The improvement is not that the packet sounds more intellectual. The
improvement is that the same frame-correction shelves now tell a future
LLM/reviewer how to use or set them aside:

- what activates the model;
- what evidence must be present;
- when the model should not be used;
- what misuse looks like;
- what a better answer should do differently;
- what the source does not support.

That is real depth at the correct layer. Python still does not decide which
card matters or what the final answer should say.

## Model-By-Model Review

| Model | v10 handoff | v11 handoff | Net judgment |
| --- | --- | --- | --- |
| `cognitive-gaps-assessment` | Graph-only shelf hint about missing information or capability. | Adds a missing-reality-gap audit: name the missing condition, evidence needed, and plan consequence. Absence blocks gap-mapping rituals with no plan change. | Useful depth. |
| `critical-thinking` | Broad graph-only prompt to scrutinize reasoning. | Separates claim, evidence, assumption, authority, emotion, and story. Absence blocks detachment theater and endless questioning. | Useful depth. |
| `counterfactual-reasoning` | Graph-only reminder to consider alternatives. | Requires plausible alternative branches tied to real decision context, assumptions, and failure paths. Absence blocks fictional counterfactual discipline. | Useful depth. |
| `metacognitive-questioning` | Light shelf hint to inspect the reasoning process. | Turns self-questioning into a bounded next-question gate with an action, evidence check, or owner. Absence blocks infinite deferral. | Useful depth. |
| `reasoning-mode-router` | Risky graph-only label that could tempt routing machinery. | Adds mode fit as reviewer handoff only: name stage, mode, fit, and switch evidence. Absence explicitly blocks deterministic case-type routing. | Useful depth with important guardrail. |
| `reframing-perspective` | Generic reminder to reframe the situation. | Requires the reframe to change a decision variable, success criterion, trade-off, evidence condition, or next action. Absence blocks euphemism. | Useful depth. |
| `theory-induced-blindness` | Graph-only warning that models can blind. | Requires naming the favored framework, what it makes visible, what it filters out, and what alternative cut would test it. Absence blocks endless theory shopping. | Useful depth. |
| `einstellung-effect` | Graph-only caution about familiar solutions. | Tests whether the familiar playbook fits this case and what would expose stale pattern lock-in. Absence blocks rejecting all prior knowledge. | Useful depth. |
| `dialectical-reasoning` | Broad reminder to consider opposing truths. | Requires thesis, strongest antithesis, preserved evidence, and bounded synthesis or next step. Absence blocks endless contrarianism. | Useful depth. |
| `bias-blind-spot` | Graph-only bias warning. | Turns bias checking inward before diagnosing only the other party. Absence blocks performative self-knowledge and other-people-only bias labels. | Useful depth. |
| `false-precision-avoidance` | Graph-only warning about over-exactness. | Distinguishes decision-relevant precision from confidence theater, and asks for a range, threshold, or approximation that changes action. | Useful depth. |
| `wysiati` | Graph-only warning that visible evidence may be incomplete. | Requires missing denominator, absent disconfirming case, and reason the absence matters. Absence blocks coherent story as proof. | Useful depth. |

## What Improved

### Activation Clarity

Improved. The v10 packet mostly says "this model may be relevant." The v11
packet says when each card should activate:

- confidence outruns named reality gaps;
- one story is standing in for evidence;
- one realized path hides the decision-quality question;
- a familiar solution arrived too fluently;
- precision creates confidence without changing the decision.

### Evidence-Needed Clarity

Improved. The v11 packet asks for concrete case evidence: the current claim,
the preferred path, the reasoning stage, the active frame, the familiar
template, the missing denominator, and the estimate or precise claim under
review.

### Do-Not-Use Clarity

Improved. This is especially valuable for a metacognitive family. The packet
now tells the next LLM not to use a card when the missing facts are already
named, the next discriminating question is already explicit, the reframe is
only a slogan, the alternative branch is fictional, or the domain genuinely
requires precise calculation.

### Misuse Guards

Improved. The important misuse guards are not decorative:

- do not use gap language to postpone action;
- do not use critical thinking as refusal to decide;
- do not invent counterfactuals;
- do not turn mode fit into deterministic routing;
- do not reframe for cleverness;
- do not treat all frameworks as suspect;
- do not use bias labels only against other people;
- do not treat story quality as evidence completeness.

### Treatment Usefulness

Improved. The v11 cards tell a later answer what to do differently: convert
gaps into decision conditions, separate claim/evidence/assumption, recover
plausible branches, name the next discriminating question, name stage and mode
fit, show which variable changes under a reframe, and replace fake exactness
with ranges or thresholds.

### Absence / Overclaim Protection

Improved. Visible absence records matter here because this family is vulnerable
to vague sophistication. The v11 packet carries absence records that prevent
"more thinking about thinking" from becoming a substitute for evidence,
action, or decision boundaries.

## Packet Burden

Judgment: acceptable.

The fixture grows by about 25 KB, but the growth is operational. It does not
increase candidate count, add a final answer, or add internal ranking. The
review render remains readable because each card exposes one compact set of
activation, evidence, dismissal, misuse, treatment, source, and absence
signals.

The burden would become too high if future batches add multiple affordances per
card without a packet cap or if frame-correction cards are nominated too often
without a real case signal. PR46 does not justify that.

## What Still Feels Thin Or Risky

- The family is inherently close to prompt mechanics and can become internal
  vocabulary if it is not anchored to case evidence.
- `reasoning-mode-router` remains useful only as reviewed handoff material.
  It must not become Python routing, a new lane, or a deterministic case-type
  classifier.
- The packet renderer shows only one absence record per card because of the
  snippet cap. That keeps the packet compact, but reviewers should remember
  the underlying records contain two absences each.
- The fixture proves one synthetic packet handoff, not product readiness.
- It does not prove final-answer quality, runtime readiness, or that more
  extraction should continue automatically.

## Boundary

PR46 adds packet review artifacts only:

- no extraction;
- no affordance record edits;
- no compiled v12;
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

## Recommendation

Do not start another extraction batch by momentum.

Recommended next slice: an after-v11 graph-only priority audit. The loop should
continue only if the remaining 88 graph-only models reveal a specific packet
weakness:

> audit the gap, enrich a narrow family, prove packet usefulness, then stop
> again.

Decision label:

> `v11_frame_correction_packet_handoff_useful`
