# PR86 Reasoning/Debiasing Enrichment v48 Report

Date: 2026-05-08

## Scope

PR86 continues the dormant model-affordance enrichment track. It does not wire affordances into `/lolla`, prompts, lane adapters, packet rendering, or runtime pickup.

The audit target was the reasoning/debiasing ring: confirmation bias, cognitive dissonance, theory-induced blindness, Dunning-Kruger, peer review your perspectives, intellectual humility, and adjacent records such as critical thinking, WYSIATI, false precision avoidance, metacognitive questioning, rationalization, anchoring, representativeness, hindsight bias, Einstellung effect, and cognitive biases.

The operating question was not "can the source say more?" Most sources can. The stricter PR55/PR85 question was: would separating this material change the downstream receiver transaction enough to justify a separate affordance identity?

## Source-Read Verdict

The ring produced two positive split candidates and four absence-rail hardening candidates.

Positive splits:

- `confirmation-bias.first-falsifier-before-approval`
- `cognitive-dissonance.private-doubt-before-group-consensus`

Absence rails:

- `theory-induced-blindness.abstract-framework-without-concrete-action`
- `dunning-kruger-effect.skilled-low-confidence-as-incompetence`
- `peer-review-your-perspectives.same-paradigm-review-as-peer-review`
- `intellectual-humility.excessive-humility-underweights-supported-evidence`

Compression/no-change decisions:

- `critical-thinking` remains one affordance. Its source contains one-day answers, emotional/personal-data cautions, WHTB, MECE, pre-mortem, and framework-fit material, but these do not create a separate transaction inside this record. They are either already carried by the claim/evidence/assumption card or better owned by neighboring records.
- `intellectual-humility` did not receive a believability-weighted positive split. The current card already requires believable critique without blind deference. The stronger change was an absence rail against lowering confidence when evidence is actually strong.
- `peer-review-your-perspectives` did not receive a digital advisory board positive split. The source treats that as an implementation form of independent diverse critique, not a separate receiver transaction.
- `theory-induced-blindness` and `dunning-kruger-effect` did not receive new positive affordances. The useful change was guarding two misuse boundaries that could otherwise look like wisdom: abstract framework talk without concrete action, and low confidence as incompetence.
- Adjacent reasoning records such as `bias-blind-spot`, `rationalization`, `false-precision-avoidance`, `wysiati`, `metacognitive-questioning`, `anchoring`, `representativeness-heuristic`, `hindsight-bias`, `einstellung-effect`, and `cognitive-biases` remain compressed.

## What Changed

### Confirmation Bias

The previous `confirmation-bias.disconfirming-evidence-equality-check` pooled two distinct moves:

- count disconfirming evidence, failed cases, and quiet losses with equal weight;
- before sponsor-backed approval, name and protect the first falsifier.

PR86 narrowed the existing card to the missing-denominator/equal-weight transaction and added `confirmation-bias.first-falsifier-before-approval` for sponsor-backed approval pressure. The split is source-backed by the PR86-read sections on sponsor-backed recommendation defense and the explicit pre-mortem question asking what evidence would appear first if the sponsor's preferred answer were false.

Receiver distinction:

- Use the equality card when the visible evidence set excludes failed, churned, rejected, or abandoned cases.
- Use the first-falsifier card when authority or sponsor preference is shifting review from testing the recommendation to defending it.

### Cognitive Dissonance

The previous `cognitive-dissonance.commitment-evidence-revision-check` covered individual or project commitment defense. PR86 added `cognitive-dissonance.private-doubt-before-group-consensus` for group dissonance, where private doubts are pulled toward public team consensus.

Receiver distinction:

- Use the commitment card when a public, costly, or identity-linked commitment is being defended against contrary signals.
- Use the group card when the next move is to collect independent anonymous assessments before group discussion and protect dissent from social consequences.

### Absence Rails

The four new absence records are not extra positive surface area. They are anti-overclaim rails:

- Theory-induced blindness must not promote abstract framework language as actionable guidance without concrete images, human actions, or operational consequences.
- Dunning-Kruger must not treat low confidence from a capable person as incompetence without objective performance calibration.
- Peer review must not treat same-paradigm confirmation as diverse external scrutiny.
- Intellectual humility must not lower confidence when the evidence deserves a stronger claim.

## v48 Compile Result

Artifact: `model_affordances_v48`

- Status: `draft_review_only`
- Records: `222`
- Affordances: `293`
- Absence records: `562`
- Schema-validation failures: `0`
- Source-quote rejections: `0`
- Source-hash failures: `0`

Delta from v47:

- Affordances: `+2`
- Absence records: `+4`
- Runtime references: none

## Quality Interpretation

PR86 is intentionally small. The most important result is not the count increase; it is the discipline of refusing positive splits where the source was rich but the downstream transaction was not different enough.

This ring supports the larger substrate plan in three ways:

- It preserves affordance identity where pooled fields would blur use/reject/defer decisions.
- It strengthens absence records as first-class anti-overclaim material.
- It demonstrates that "full potential" does not mean dumping every source nuance into positive cards.

## Validation

Focused validation should cover:

- edited records validate against schema and exact source quotes;
- v48 preserves all 222 model IDs from v47;
- v48 adds only the two expected affordance IDs;
- v48 adds only the four expected absence fields;
- adjacent compression-ok reasoning records do not gain positive affordances;
- v48 is not referenced by live runtime paths.

Focused command:

```bash
PYTHONPATH=. pytest tests/test_pr86_v48_reasoning_debiasing_enrichment.py tests/test_pr85_v47_creative_synthesis_enrichment.py tests/test_model_affordance_compiler.py
```

## Runtime Boundary

This PR remains dormant substrate work. It does not:

- change packet producer defaults;
- add a lane-to-nomination adapter;
- import v48 from engine or scripts;
- change prompts or receiver rubrics;
- alter `/lolla` behavior.

Future packet-stress work should continue to ask whether grouped affordance identity, confidence visibility, weak-support warnings, and absence display are strong enough before any live pickup experiment.
