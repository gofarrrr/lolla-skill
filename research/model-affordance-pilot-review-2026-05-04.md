# Model Affordance Pilot Review - 2026-05-04

Status: draft. This pilot targets `feature/knowledge-use-schema`, not `main`.

## Pilot Summary

This PR extracted ten model-affordance records from copied canonical Markdown sources under `data/model_sources/`. The residency decision is path A: the ten source files live in-repo for exact-quote validation, and `data/model_sources/manifest.json` records a SHA-256 hash for each copied file.

Extraction used one fresh isolated Codex worker session per model. No batch extraction, OpenRouter call, live `/lolla` run, runtime lane, chat output, memo output, or Observatory panel was added. The worker sessions used PR 1's extraction contract, schema, validator, the copied raw Markdown source, and the three reviewed System B curation waves for the assigned model only.

Affordance distribution:

- 3 models have 1 affordance: `base-rates`, `premortem`, `second-order-thinking`.
- 3 models have 2 affordances: `theory-of-constraints`, `power-dynamics`, `optionality`.
- 3 models have 3 affordances: `inversion`, `problem-framing-and-reframing`, `confidence-calibration`.
- 1 model has 4 affordances: `systems-thinking`.
- 2 records carry absence records: `base-rates` and `problem-framing-and-reframing`.

## Schema And Validator Findings

One PR 1 validator bug was found during PR 2 setup: `affordance_id` values matched the dotted namespace regex but were not required to start with the record's `model_id`. PR 1 was amended on `feature/knowledge-use-schema` in commit `9e1df41` to reject mismatched namespaces, and the pilot branch was fast-forwarded over that fix.

The pilot also produced real record-side validation catches:

- `optionality` initially had source quotes that crossed Markdown bold boundaries. The exact-substring validator rejected them, and the worker narrowed the quotes to literal source spans.
- `confidence-calibration` had the same class of source quote failure around bold/colon markup. Those quotes were corrected before the record entered the repo.
- `problem-framing-and-reframing` rejected a Wave 2 curation prompt because the exact string was absent from the canonical Markdown. The record kept only source-backed normalized treatment language.

No runtime behavior changed. The validator remains dormant review tooling for this PR.

## Per-Model Notes

### theory-of-constraints

Extracted two affordances: measured constraint-first intervention and post-change constraint retesting. The source is unusually operational, with direct support for named bottlenecks, quantified limits, local-optimization guards, and re-scoring constraints after each major change.

Review question: the risk-and-mitigation tables read partly like later curation, but they are present in the canonical Markdown and all evidence spans validate there. A future reviewer should confirm that this enriched Markdown is acceptable as raw source authority.

### second-order-thinking

Extracted one affordance: a downstream reversal stress test. It asks the answer to map the dependency chain, first reversal threshold, local metric-protection incentive, and the behavior surrounding actors may learn to repeat.

Dropped material includes broad domino analogies, general systems explanation, and relation-context sections. Those are explanatory, but the risk-table prompts create the sharper operational contract.

### power-dynamics

Extracted two affordances: outside-option credibility before terms and commitment-gradient leverage inversion. The source directly supports mapping walk-away credibility, hidden fallback options, enforcement costs, and the point where post-signature lock-in changes bargaining power.

Dropped weakest-link and relation-semantic material for now. It may matter later, but it did not earn a cleaner standalone model-use contract in this pass.

### base-rates

Extracted one affordance: an outside-view reference-class anchor before case-specific updating. The record requires a named reference class, historical frequency or range data, a structural fit check, and update discipline.

Added one absence record for `advertising-message-targeting-affordance`. The source has one advertising example, but it does not support a reusable treatment requirement beyond reference-class anchoring. This is the pilot's clearest thin-source absence case inside a one-affordance record.

### optionality

Extracted two affordances: create a non-binary option set before selection and preserve reversible paths to buy learning. The source supports both: generate at least three options before choosing, compare option economics, use reversible staged moves under uncertainty, and define when optionality expires.

The first validation pass caught non-exact source quotes around Markdown formatting. Correcting those quotes proved the provenance rail catches real extraction mistakes rather than only malformed JSON.

### premortem

Extracted one affordance: simulated future failure converted into plan changes. The source strongly supports prospective hindsight before commitment, assumption surfacing, domino effects, and converting retained risks into owners, mitigations, reversal triggers, thresholds, or decision changes.

Dropped relation-context material around systems thinking, second-order thinking, competitive strategy, and organizational design. In this source they sharpen the same premortem operation rather than creating separate affordances.

### inversion

Extracted three affordances: anti-goal failure mechanism mapping, disconfirmation before defense, and obstacle removal before added force. The source contains many direct prompts and warnings, so compression was the main review choice.

The record should be reviewed for granularity. The first two affordances are central to inversion. The third is source-backed through Lewin force-field material, but it may be better as a supporting treatment or relation-aware layer rather than a standalone affordance.

### problem-framing-and-reframing

Extracted three affordances: define the problem before analysis deepens, test alternative frames before choosing the lens, and falsify assumptions that lock a frame in place. The source gives direct support for precise decision-maker-centered problem definition, testing multiple frames, and surfacing would-have-to-believe assumptions.

Added one absence record for `persona-configuration-affordance`. The AI persona material is source-backed as an example, but too thin as a reusable problem-framing treatment contract. The worker also refused to quote a Wave 2 prompt that was not present in raw Markdown.

### confidence-calibration

Extracted three affordances: size commitments to earned confidence ranges, audit instrument trust before precise-looking confidence, and interrogate confidence by method before weighing claims. The source supports action thresholds, data-generating-process checks, and the confidence-number/reasons/method sequence.

The record needs review for scope: the method-first affordance spans learning, expertise, and business claims. It validates, but a later pass may split or narrow it.

### systems-thinking

Extracted four affordances: structure-over-events diagnosis, feedback-loop mapping, metric/leverage design, and architecture-misdiagnosis testing. This is the broadest record, which fits the breadth of the source but also makes it the highest-risk completeness-theater candidate.

The strongest two affordances are feedback-loop mapping and metric/leverage design because they demand concrete evidence, sequence, and progress signals. The structure-over-events and architecture-misdiagnosis affordances should get especially careful review before any runtime promotion.

## Cross-Cutting Observations

- The schema can express useful operational records without forcing smooth coverage. The pilot produced 1, 2, 3, and 4 affordance records, plus explicit absences.
- Exact source-quote provenance is doing real work. It caught quote spans that were semantically close but not literal substrings.
- Raw Markdown authority matters. The problem-framing worker rejected curation text that was not present in the source file.
- Broad models tend to sprawl. `systems-thinking`, `inversion`, and `confidence-calibration` validate mechanically but need reviewer narrowing before they become operational substrate.
- The current schema handles absence records well enough for thin examples and rejected affordance attempts.
- The `section_hint` requirement did not block the pilot, but it still adds extraction friction and should be watched in PR 3 or future bulk work.

## Audit Value Cases

1. `theory-of-constraints.constraint-first-cap` would let a reviewer flag a ToC-labeled treatment that never names the binding constraint, governing metric, current cap, or movement evidence.
2. `base-rates.outside-view-reference-class-anchor` would flag a base-rates mention that gives generic caution about statistics but does not define a reference class, historical frequency, and structural fit test.
3. `power-dynamics.commitment-gradient-inversion` would flag negotiation advice that celebrates up-front terms while ignoring when integration, migration, data access, or switching costs invert leverage after signature.

## Records To Drop Or Rewrite First

These are not validation failures. They are reviewer-eye targets before runtime promotion.

1. `systems-thinking.structure-over-events`: likely rewrite or merge with feedback-loop mapping unless reviewers want a separate two-level diagnosis contract.
2. `inversion.obstacle-removal-before-added-force`: source-backed, but may belong as supporting force-field treatment rather than a standalone inversion affordance.
3. `confidence-calibration.method-first-self-interrogation`: useful, but broad enough that it may need splitting between learning/mastery calibration and business-claim confidence.

## Reviewer-Eye Gate Status

- One zero-or-one-affordance record with explicit absence reason: satisfied by `base-rates`.
- At least seven records look more operational than existing failure-mode prose: likely satisfied, but human signoff is still required.
- Three audit-value cases: listed above.
- Three drop/rewrite candidates: listed above.
- At least one schema/validator bug found and fixed on PR 1: satisfied by the `affordance_id` namespace bug.
- At least one real extraction failure caught and fixed: satisfied by exact-source-quote failures in `optionality` and `confidence-calibration`.

Keep this PR draft until PR 1 is merged and the reviewer decides whether these records prove the schema is worth carrying forward.
