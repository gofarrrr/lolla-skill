# PR82 Learning/Mastery Enrichment v44 Report

Date: 2026-05-08

## Verdict

PR82 enriches the dormant reviewed affordance substrate only. It does not wire v44 into `/lolla`, runtime lanes, packet production, prompting, or product behavior.

The main quality question for this ring was whether the learning/mastery cluster had been compressed too tightly by the earlier one-affordance coverage pass. The answer is mixed:

- Most records were already correctly compressed.
- Four records contained distinct downstream card transactions that deserved separate affordance identity.
- Several tempting expansions were rejected as treatment detail rather than new affordances.
- Twelve source-backed absence rails were added so learning vocabulary does not promote false mastery, false rigor, or false authority.

## Why This PR Exists

The v18-v43 substrate work made coverage broad enough that the next risk shifted from "missing cards" to "lossy card transactions." A model can have a reviewed card and still be under-extracted if one affordance pools several operational moves that a future receiver may need to use, reject, or defer separately.

PR82 applies that audit lens to the learning/mastery family:

- Does the source support more than one downstream-relevant use mode?
- Would splitting change evidence required, misuse guards, treatment requirements, or use/reject/defer outcomes?
- Can absence records block the most likely overclaim?
- Can we enrich without turning the corpus into a dump?

## Reviewed Scope

Primary records reviewed:

- `deliberate-practice`
- `desirable-difficulties`
- `varied-practice-interleaving`
- `generation-effect`
- `learning-curve`
- `expertise-reversal-effect`
- `cognitive-load-theory`
- `scaffolding`
- `schema-acquisition`
- `zone-of-development`
- `blooms-taxonomy`
- `feynman-technique`
- `growth-mindset`
- `dunning-kruger-effect`
- `curse-of-knowledge`
- `perceptual-learning`
- `scaffolding-educational`
- `confidence-calibration` as a boundary record

The review read the existing JSON records and their canonical Markdown sources under `MM_CANONICAL_216`, using exact source custody. The compiler then validated source hashes and exact source quotes through the mirrored `data/model_sources` files.

## Positive Affordance Splits

Four split affordances were added:

1. `learning-curve.progressive-scaffold-and-handoff`

   Why split:
   The existing learning-curve card measured capability compounding over time. The source also supports a distinct staged handoff transaction: expert demonstration, joint practice, correction, and independent learner execution. That changes the receiver action from "measure improvement" to "design the next handoff step."

   Primary source support:
   - `**The Scaffolding Model ("I Do, We Do, You Do"):**`
   - `gradual handover of control and mastery from teacher/expert to student/novice`
   - `The expert first provides knowledge and demonstration of strategies, then moves to modeling, questioning, and correction, continually restructuring the task until the learner achieves independence.`

2. `expertise-reversal-effect.extract-tacit-expert-cognition-with-stories`

   Why split:
   The existing expertise-reversal card matches support level to audience expertise. The source also supports extracting tacit expert cognition through stories and PARI when direct expert advice is too compressed to train others. That is not the same as deciding whether to scaffold or compress instruction.

   Primary source support:
   - `direct advice is often ineffective because experts may be unconsciously aware of their foundational skills and find it difficult to self-report tacit knowledge.`
   - `**Ask for Stories, Not Advice:** Focusing on narratives helps extract factual details and timelines, which are the raw material for understanding decision-making processes.`
   - `**Use PARI Method:** Have experts discuss typical problems they face, focusing on the **P**recursor, **A**ction, **R**esult, and **I**nterpretation of the events to illuminate the cognitive flow.`

3. `curse-of-knowledge.observed-novice-validation-before-clarity-trust`

   Why split:
   The existing curse-of-knowledge card reconstructs the recipient's missing model from the expert side. The source also supports a separate recipient-side validation requirement: observed novice use, teach-back, and demonstration before trusting clarity. That deserves its own identity because it can block a guessed explanation even when the audience reconstruction sounds plausible.

   Primary source support:
   - `Require recipients to demonstrate understanding by explaining back in their own words or applying the concept to a new example.`
   - `Polite comprehension signals are not evidence of understanding.`
   - `Include genuine novice users in design and testing processes.`
   - `Observe, don't ask — experts predict novice confusion inaccurately because the prediction itself suffers from the curse.`

   Cleanup:
   The novice validation treatment was moved out of the pooled original affordance so future packet review can distinguish "reconstruct audience state" from "verify with recipient evidence."

4. `perceptual-learning.tacit-cue-extraction-before-training`

   Why split:
   The existing perceptual-learning card trains known cue discrimination in noisy domains. The source also supports an upstream extraction transaction when the cue library is tacit: stories, timelines, think-aloud work, and PARI before creating training guidance. That is separate from training a cue that is already known.

   Primary source support:
   - `This family of techniques extracts knowledge from experts by focusing on the **knowledge and skills used as the basis for a decision**, particularly when tasks cannot be reduced to simple procedures.`
   - `Experts often struggle to articulate their tacit knowledge.`
   - `Instead, interviewers should act like journalists, gathering facts and establishing a timeline to walk through decisions step-by-step.`
   - `Focuses on having experts generate typical problems, think aloud while solving them, and rehash the *Precursor, Action, Result, and Interpretation* to reveal hidden cognitive processes.`

   Cleanup:
   The tacit extraction treatment was moved out of the pooled original cue-discrimination affordance to preserve transaction identity.

## New Absence Rails

Twelve absence records were added:

- `practice-entrenches-flawed-model`
- `audience-deciphering-as-rigor`
- `self-generated-model-defense`
- `early-progress-as-scalable-mastery`
- `expert-schema-as-correct-by-default`
- `low-load-fluency-as-mastery`
- `schema-as-execution-mastery`
- `one-shot-stretch-calibration-without-feedback`
- `lower-level-overwork-as-progress`
- `simplified-explanation-without-uncomfortable-evidence`
- `dke-as-intuition-suppression`
- `scaffolded-fluency-as-independent-mastery`

These are anti-overclaim rails. Their job is not to nominate more models. Their job is to prevent attractive learning-language from becoming false authority:

- practice without model correction;
- difficulty as audience burden;
- self-generation as defended ownership;
- early progress as full mastery;
- expert status as correct schema;
- low cognitive load as understanding;
- schema knowledge as execution ability;
- one-shot stretch calibration;
- Bloom lower-level overwork as progress;
- simple explanation without disconfirming evidence;
- Dunning-Kruger as blanket intuition suppression;
- scaffolded fluency as independent mastery.

## Rejected Split Ideas

The review deliberately did not split everything that looked rich.

Rejected as treatment/guard detail:

- Deliberate practice variants around broad expertise, deep work, Feynman, and latticework material.
- Desirable difficulties variants around Feynman, problem disaggregation, and productive discomfort.
- Varied practice/interleaving idea-volume material.
- Generation-effect variants around analogies, interrogatives, and hypothesis formulation.
- Cognitive-load worked examples as a separate affordance.
- Scaffolding framework-fit checks as a separate affordance.
- Schema multi-frame stress testing as a separate affordance.
- Zone-of-development feedback sequencing as a separate affordance.
- Bloom level hierarchy details as separate affordances.
- Feynman analogy and blind-spot details as separate affordances.
- Growth-mindset motivational/self-talk material.
- Dunning-Kruger coaching and circle-of-competence detail.
- Scaffolding-educational seven-stage and active-recall details.
- Confidence-calibration boundary material.

The rule used:

> Split only when the source supports a different downstream transaction with different activation, evidence, treatment, misuse guard, or use/reject/defer outcome.

## Artifact Delta

Compiled artifact:

- `data/compiled/model_affordances/affordances_v44.json`
- `data/compiled/model_affordances/quality_report_v44.md`

Delta from v43:

- Model records: `222` unchanged
- Affordances: `278` to `282`
- Absence records: `536` to `548`
- Schema validation failures: `0`
- Source hash failures: `0`
- Source quote rejections: `0`

## Runtime Safety

PR82 does not import or reference v44 from live runtime paths.

The new test checks that these fragments do not appear in selected live runtime files:

- `affordances_v44`
- `model_affordances_v44`

This keeps v44 in the reviewed substrate lane only.

## Tests

Focused test added:

- `tests/test_pr82_v44_learning_mastery_enrichment.py`

The test verifies:

- target records validate against schema and exact source custody;
- v44 preserves all 222 model IDs from v43;
- v44 adds exactly four affordance IDs and exactly twelve absence fields;
- compiled counts and validation metadata match expected values;
- split affordances preserve transaction identity;
- absence rails carry the intended source-backed warnings;
- live runtime paths do not import v44.

Expected focused verification:

```bash
PYTHONPATH=. pytest tests/test_pr82_v44_learning_mastery_enrichment.py tests/test_pr81_v43_statistical_probability_enrichment.py tests/test_model_affordance_compiler.py
```

## Bottom Line

PR82 is a quality enrichment PR, not a runtime pickup PR.

It keeps the useful lesson from the one-affordance coverage phase while correcting the places where "one card" had started to hide multiple transaction identities. The result is a slightly richer v44 substrate with clearer split points and stronger absence rails, still compact enough to avoid turning the knowledge base into undisciplined model dumping.
