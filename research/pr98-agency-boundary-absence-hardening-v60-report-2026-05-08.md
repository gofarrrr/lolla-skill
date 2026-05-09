# PR98 Agency Boundary Absence Hardening v60 Report

Date: 2026-05-08

Branch: `feature/knowledge-substrate-pr98-agency-boundary-v60`

## Scope

PR98 continues the dormant reviewed-affordance enrichment track. It does not
wire affordances into `/lolla`, prompts, lane adapters, packet rendering, or
runtime pickup.

The audit target was an agency, boundary, and self-knowledge ring:

- `boundaries`
- `authenticity`
- `johari-window`
- `circle-of-control`
- `circle-of-competence`
- `internal-locus-of-control`

The operating question stayed the PR55 transaction-identity question:

> Would separating this material change downstream use, reject, defer, merge,
> evidence-gate, treatment, misuse-guard, or final-answer behavior?

Two read-only subagent audits were used as pressure checks. Final adjudication
was made locally after reading the full canonical Markdown, raw source custody,
current records, and adjacent owner records.

## Source-Read Verdict

Positive affordance splits accepted:

- none

Absence rails added:

- `boundaries.clean-boundary-hiding-cross-boundary-dependencies`
- `boundaries.dont-boil-ocean-as-boundaries-split`
- `boundaries.overbroad-system-boundary-as-completeness`
- `authenticity.authentic-conviction-as-evidence`
- `authenticity.emotional-overdrive-as-authentic-candor`
- `authenticity.transparency-without-correction-or-accountability`
- `johari-window.generic-socially-acceptable-feedback-as-blind-spot-reduction`
- `johari-window.curated-disclosure-as-openness`
- `johari-window.feedback-filtered-to-protect-self-image`
- `circle-of-control.no-control-label-before-indirect-influence-test`
- `circle-of-control.evidence-free-control-bucket-map`
- `circle-of-control.local-control-myopia-as-control-affordance`
- `circle-of-competence.expert-status-as-competence-evidence`
- `circle-of-competence.feynman-or-analogy-as-competence-split`
- `internal-locus-of-control.felt-control-as-causality`
- `internal-locus-of-control.deliberate-then-act-as-internal-locus-split`
- `internal-locus-of-control.five-step-process-as-internal-locus-split`
- `internal-locus-of-control.self-script-inner-dialogue-as-internal-locus-split`

No positive splits were accepted because the tempting candidates either
duplicated stronger owner records or belonged inside the existing treatment and
misuse-guard structure.

## Rejected Positive Splits

### `boundaries` expansion

Rejected as positive split.

The source is rich: context windows, MECE, project contracts, don't-boil-the-
ocean, frame blindness, overbroad system boundaries, and circle-of-competence
language all appear. But the current card already owns the live transaction:
define inside, outside, influenceable, and protected capacity when scope,
ownership, decision rights, or relevance are fuzzy.

PR98 added rails so the richness is not lost:

- do not use a clean boundary when it hides feedback loops or cross-boundary
  dependencies;
- do not turn only-enough-facts analysis discipline into a separate Boundaries
  card;
- do not widen system boundaries as if completeness itself improves judgment.

### `authenticity` expansion

Rejected as positive split.

The current card already captures the source's central move: congruent candor
grounded in evidence, preparation, and accountability. Radical transparency,
customer-language fit, AI persona authenticity, and academic-selfie material are
real, but they would duplicate psychological safety, persuasion, JTBD, persona
simulation, or metacognitive owner records if promoted here.

PR98 added rails against:

- genuine conviction being treated as evidence;
- emotion overdrive being treated as authentic candor;
- transparency without correction or accountability.

### `johari-window` expansion

Rejected as positive split.

Feedback seeking and self-disclosure are different moves, but the source treats
them as a reciprocal loop. The current record already keeps two treatment
requirements inside one transaction: surface external view and make disclosure
behavioral. Splitting feedback and disclosure would mostly create packet
surface area without changing downstream use/reject/defer behavior.

PR98 added rails against:

- generic or socially acceptable feedback as blind-spot reduction;
- curated disclosure as openness;
- filtering feedback to protect self-image.

### `circle-of-control` expansion

Rejected as positive split.

The existing control/influence/no-control map already owns classification,
action versus monitoring, evidence for buckets, and reclassification. Local
control myopia, false helplessness, and control illusion are not separate
positive affordances; they are the main ways the bucket map can fail.

PR98 added rails against:

- labeling a difficult factor as no-control before testing indirect influence;
- bucket maps without evidence for each classification;
- treating local-control myopia as a positive control affordance.

### `circle-of-competence` expansion

Rejected as positive split.

The tempting split was external expertise boundary checking. It is source-backed
at the level of content, but the stronger owner record is `authority-bias`,
which already asks for domain fit, reasoning, assumptions, and override
evidence when external authority is influencing a recommendation. Promoting the
same transaction under Circle of Competence would make borrowed expertise appear
twice in future packets.

PR98 added rails against:

- external expert status as competence evidence;
- Feynman or analogy methods becoming separate Circle of Competence cards.

### `internal-locus-of-control` expansion

Rejected as positive split.

The source includes deliberate-then-act, the five-step improvement process,
self-scripting, machine-level diagnosis, and the illusion of conscious control.
The current card owns bounded agency: controllable levers, constraints,
ownership, measurement, acceptance, escalation, and redesign.

Deliberate-then-act is valuable, but as a runtime card it is already owned more
sharply by `self-control.deliberate-pause-before-impulse-action` and
`critical-thinking` evidence/action-threshold checks. Five-step improvement
belongs to process-improvement owner records. Self-script is too thin in this
source to promote.

PR98 added rails against:

- felt control being treated as causal evidence;
- deliberate-then-act as a duplicate Internal LOC split;
- five-step continuous improvement as an Internal LOC split;
- self-script inner dialogue as a thin standalone affordance.

## Quality Interpretation

PR98 is intentionally absence-first. That is not a smaller result. For this
scope, the most dangerous failure mode is duplicate agency/boundary vocabulary:
several cards could all say "scope it," "own it," "get feedback," "be honest,"
or "stay within competence" while losing the specific source-backed transaction.

The enrichment therefore preserves corpus nuance as no-promote records:

- what looks like a promising split;
- why it is rejected;
- which adjacent owner should carry it;
- what misuse the future packet must avoid.

This is especially important before runtime pickup. If every agency/boundary
idea becomes a positive card, future packets will look authoritative while
flattening provenance and owner boundaries.

## v60 Compile Result

Artifact: `model_affordances_v60`

- Status: `draft_review_only`
- Records: `222`
- Affordances: `306`
- Absence records: `697`
- Schema-validation failures: `0`
- Source-quote rejections: `0`

Delta from v59:

- Affordances: `+0`
- Absence records: `+18`
- Runtime references: none

## Runtime Boundary

The v60 artifact remains dormant. PR98 does not:

- import v60 from live runtime paths;
- change packet producer defaults;
- add lane-to-nomination logic;
- change prompts;
- change `/lolla`;
- promote reviewed cards into automatic reasoning instructions.

The runtime question remains later work:

> Can reviewed cards survive pickup, compression, display, and LLM use without
> losing their epistemic shape?

PR98 improves the reviewed substrate by making tempting duplicate or overbroad
agency/boundary moves explicit as rejected material.

## Verification Commands

```bash
python3 scripts/compile_model_affordances.py --record-dir data/model_affordances/pilot --record-dir data/model_affordances/batch_1 --record-dir data/model_affordances/batch_2 --record-dir data/model_affordances/batch_3a --record-dir data/model_affordances/batch_4 --record-dir data/model_affordances/batch_5 --record-dir data/model_affordances/batch_6 --record-dir data/model_affordances/batch_7 --record-dir data/model_affordances/batch_8 --record-dir data/model_affordances/batch_9 --record-dir data/model_affordances/batch_10 --record-dir data/model_affordances/batch_11 --record-dir data/model_affordances/batch_12 --record-dir data/model_affordances/batch_13 --record-dir data/model_affordances/batch_14 --record-dir data/model_affordances/batch_15 --record-dir data/model_affordances/batch_16 --record-dir data/model_affordances/batch_17 --compiled-filename affordances_v60.json --quality-report-filename quality_report_v60.md --artifact-id model_affordances_v60 --report-title "Model Affordance Quality Report v60"
PYTHONPATH=. pytest tests/test_pr98_v60_agency_boundary_absence_hardening.py tests/test_pr97_v59_behavior_self_regulation_enrichment.py tests/test_model_affordance_compiler.py
rg -n "affordances_v60|model_affordances_v60" engine scripts -g '*.py'
git diff --check
```
