# PR74 v36 Communication Boundary Hardening Report

Date: 2026-05-08

Branch: `feature/knowledge-substrate-pr74-communication-boundary-v36`

## Verdict

PASS as dormant reviewed substrate.

PR74 does not touch `/lolla`, prompts, lane adapters, packet rendering, or live product behavior. It is a communication-cluster hardening pass only.

## Why This PR Exists

PR72 proved that positive splits are useful only when the downstream receiver transaction changes. PR73 then showed that many rich reasoning records need better requirements and absence rails, not more positive affordance identity.

PR74 applies that standard to communication and persuasion records. The risk in this cluster is especially high because communication models sound broadly useful and can easily become persuasive theater, story theater, or listening theater.

The operating question was:

> Can the communication cards preserve richer source nuance without turning every communication model into a generic advice card?

## Source Files Re-Read

Canonical source files were read directly from `MM_CANONICAL_216` and cross-checked against the source-custodied repo copies:

- `Active Listening_rag.md`
- `Constructive_Feedback_Models_rag.md`
- `Feedback_Models_Sbi_rag.md`
- `Persuasion_Principles_rag.md`
- `Information_Theory_rag.md`
- `Curse_of_Knowledge_rag.md`
- `Narratives_rag.md`
- `Storytelling_Frameworks_rag.md`
- `Pre_Suasion_rag.md`
- `Non_Violent_Communication_rag.md`

Subagent review agreed that this ring should avoid positive splits. One candidate split for Active Listening was rejected after review because the existing affordance already owns asking how the speaker thinks before advice.

## Changes Made

### Active Listening

No new positive affordance.

Existing affordance hardened:

- `active-listening.hidden-disagreement-diagnostic-loop`

Added treatment requirement:

- `capture-process-before-abstracting-advice`

Added absence/routing guard:

- `listening-through-adversarial-incentives`

Purpose:

The source contains real expert-process and customer-discovery material: ask how people think, gather stories, facts, timelines, and decision walkthroughs. But that does not need a second positive affordance because the existing card already owns diagnosis before advice. The new treatment requirement prevents tacit knowledge from being flattened into generic best-practice advice.

The new absence guard prevents “listen harder” from being promoted when adversarial incentives reward withholding and the case first needs payoff, incentive, or trust-structure diagnosis.

### Curse of Knowledge

No new positive affordance.

Existing affordance hardened:

- `curse-of-knowledge.audience-starting-state-reconstruction`

Added treatment requirement:

- `verify-with-novice-demonstration`

Purpose:

The existing card already rebuilds the recipient model. PR74 makes the demonstration standard sharper: when novice use matters, expert predictions are not enough. Use teach-back, worked examples, or observed novice interaction.

### Information Theory

No new positive affordance.

Added absence/routing guard:

- `compression-that-strips-system-or-human-signal`

Purpose:

Information Theory should preserve signal under cognitive constraint. It should not compress away system interconnections, meaningful weak signals, emotional adoption context, or implementation complexity as if those were noise.

### Persuasion Principles

No new positive affordance.

Added absence/routing guard:

- `mindless-compliance-as-persuasion-goal`

Purpose:

The source names automatic compliance as a mechanism and risk. The reviewed affordance supports substance-preserving adoption design only when evidence, autonomy, and flaw-revealing friction remain visible.

### Storytelling Frameworks

No new positive affordance.

Existing affordance hardened:

- `storytelling-frameworks.structure-behavior-change-message`

Added treatment requirement:

- `cut-search-story-and-excess-baggage`

Purpose:

The source distinguishes the story the audience needs from the story the communicator wants to tell. PR74 makes that distinction operational: tell the story of the solution or decision, not the communicator's search process, and cut details that do not earn their place.

### Narratives

No new positive affordance.

Added absence/routing guard:

- `narrative-when-protocol-or-threshold-needed`

Purpose:

Narratives own causal meaning for action. They should not be promoted when the receiver needs a direct protocol, checklist, threshold rule, or stopping rule.

### Constructive Feedback Models

No new positive affordance.

Existing affordance hardened:

- `constructive-feedback-models.specific-standard-correction`

Added treatment requirement:

- `check-machine-level-when-pattern-repeats`

Purpose:

The source says high-value feedback checks the machine level that produced the outcome, not only the case-at-hand. PR74 makes that a positive treatment requirement when a deviation repeats or appears process-produced.

### Feedback Models SBI

No new positive affordance.

Added absence/routing guard:

- `sbi-with-incomplete-or-motivated-information`

Purpose:

SBI can make a bad feedback transaction look objective if the initial Information step is incomplete, motivated, or selectively framed. The guard tells future packet receivers to defer SBI until the concrete situation and behavior are validated.

## v36 Artifact Summary

Compiled artifact:

- `data/compiled/model_affordances/affordances_v36.json`
- `data/compiled/model_affordances/quality_report_v36.md`

Metadata:

- Artifact: `model_affordances_v36`
- Status: `draft_review_only`
- Records: 222
- Affordances: 271
- Absence records: 506
- Schema failures: 0
- Source hash failures: 0
- Source quote rejections: 0

Delta from v35:

- Affordances: 271 -> 271
- Absences: 501 -> 506

## Why This Is Not Bloat

PR74 adds zero positive affordance IDs.

It rejects the tempting expansion path:

- Active Listening does not split into every listening technique.
- Persuasion does not split into influence-principle tactics.
- Storytelling does not split into named story templates.
- Information Theory does not become generic simplification.
- Feedback models do not become generic conflict or system-diagnosis cards.

The useful work is boundary precision: richer treatment requirements where the card already owns the transaction, and absence/routing guards where another card should own it.

## Runtime Safety

This PR remains dormant substrate only.

No live runtime path imports v36. The PR74 test scans:

- `engine/system_b/__init__.py`
- `engine/system_b/pipeline.py`
- `engine/system_b/reasoning_substrate_packet.py`
- `engine/system_b/reasoning_substrate_packet_review.py`
- `scripts/run_pipeline.py`

Expected result: `affordances_v36` and `model_affordances_v36` appear only in tests and compiled artifact files, not live runtime paths.

## Verification

```bash
pytest tests/test_pr74_v36_communication_boundary_hardening.py \
  tests/test_pr73_v35_reasoning_integrity_hardening.py \
  tests/test_pr72_v34_split_candidate_enrichment.py \
  tests/test_model_affordance_compiler.py

rg -n "affordances_v36|model_affordances_v36" engine scripts tests -g '*.py'

git diff --check
```

## Next Corpus Frontier

The next rings should use the completed read-only audits:

- learning/metacognition: scaffolding, scaffolding-educational, growth-mindset, perceptual-learning, metacognitive-questioning;
- decision/risk/probability: expected-value, risk-assessment, false-precision-avoidance, bayesian.

The same rule should hold: add a positive affordance only when downstream use/reject/defer behavior changes. Otherwise prefer treatment hardening, absence rails, and routing guards.
