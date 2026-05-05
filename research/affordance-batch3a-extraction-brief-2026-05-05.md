# Affordance Batch 3a Extraction Brief

**Date:** 2026-05-05
**Status:** PR15 docs/research-only extraction brief. Planning artifact, not
extraction execution.

**Purpose:** Define how to extract a targeted Batch 3a coverage patch without
turning Decision Pressure into coverage theater.

**Inputs:**
- `research/affordance-batch3a-coverage-priority-2026-05-05.md`
- `research/gate4-3case-decision-pressure-dry-surface-2026-05-05.md`
- `research/gate4-3case-decision-pressure-selection-stability-2026-05-05.md`
- `research/gate4-3case-decision-pressure-selection-stability-review-2026-05-05.md`
- `research/decision-pressure-surface-spec-2026-05-05.md`
- `references/model-affordance-extraction.md`
- `data/schemas/model_affordance.schema.json`
- `data/compiled/model_affordances/affordances_v3.json`
- `data/curation/{model_id}.json`
- `data/curation/intervention_semantics/{model_id}.json`
- `data/curation/relation_semantics/{model_id}.json`
- canonical source markdown for each target model

**Target models, exactly five:**
- `opportunity-cost`
- `true-uncertainty-navigation`
- `falsifiability`
- `principal-agent-problem`
- `probabilistic-thinking`

**Core doctrine:** Extract Decision Pressure-ready operational constraints, not
general model explanations.

**Hard constraints:**
- Do not extract records in PR15.
- Do not run model calls.
- Do not run judge calls.
- Do not modify runtime behavior.
- Do not modify prompts.
- Do not modify validators.
- Do not modify existing affordance records.
- Do not start broad Batch 3.
- Do not wire anything into `/lolla`, Observatory, memo, Step 8, or Step 6.
- Do not force all five models to produce rich affordances.

Doctrine line:

> Surface pulls extraction. Extraction does not push the product.

## Why Batch 3a Exists

PR13 showed that the 12-route Gate 4 packet could compress into `3` compact
Decision Pressures. PR14 added a second-review result: `3/3` pressure-cluster
convergence with PR13, with the caveat that the review was not perfectly
blinded.

That is enough for Batch 3a planning. It is not enough for runtime promotion or
for extraction execution without a stricter brief.

Batch 3a exists to patch missing v3 records that repeatedly affect compact
Decision Pressure selection, dismissal, or coverage honesty. It does not exist
to improve corpus completion statistics.

## Allowed Per-Model Outcomes

Each target model may produce one of these outcomes:

- `strong_affordance_record`: the source supports multiple sharp,
  source-backed operational constraints.
- `thin_narrow_affordance_record`: the source supports one or two useful
  constraints, but not a broad runtime-useful record.
- `absence_record`: the source does not support Decision Pressure-ready
  operational affordances for this extraction standard.
- `do_not_promote_recommendation`: the source supports some knowledge, but the
  model should remain Observatory-only or should not be used for compact
  Decision Pressure until later review.

All four outcomes are valid. A forced rich record is a failure.

## Extraction Standard

Extract fields only when the source can help a future compact Decision Pressure
answer one or more of these questions:

- What should the user verify before acting?
- What concrete evidence is needed?
- What would make the pressure live?
- What would dismiss the pressure?
- What tripwire, stop condition, sequencing change, or operational constraint
  follows?
- When should the model not be used because it would create theater, fake
  precision, bad-faith framing, or overreach?

Prioritize:

- `treatment_requirements`
- `case_evidence_needed`
- `misuse_guards`
- `do_not_use_when`
- dismissal logic
- tripwires
- stop conditions
- operational constraints

Do not prioritize:

- model definitions;
- abstract theory;
- elegant summaries;
- broad examples;
- relation edges without an operational move;
- fields that only make the schema look complete.

## Source-Reading Requirements

For each target model:

1. Read the full canonical source markdown. Do not extract from curation files
   alone.
2. Use Wave 1, intervention semantics, and relation semantics only as context
   and warnings, not as substitutes for source truth.
3. Confirm source residency and exact source filename before extraction. If
   the canonical source is not resident in `data/model_sources/`, the extraction
   PR must first make source custody explicit before creating a model record.
4. Preserve exact source quote custody. Every semantic field must be backed by
   an exact `source_quote` that exists in the source file.
5. Mark normalized extraction honestly. Do not present reviewer synthesis as
   explicit source text.
6. Write review notes explaining what was preserved, normalized, dropped, or
   left as absence.
7. Prefer fewer, sharper affordances over complete-looking records.

## Validation Requirements

Any later extraction PR must prove:

- model affordance JSON validates against `data/schemas/model_affordance.schema.json`;
- exact source quote validation passes;
- absence records validate when the source is too thin;
- no existing affordance records are rewritten as part of Batch 3a unless the
  PR explicitly scopes and justifies that change;
- compiled output updates are deterministic;
- quality reporting distinguishes strong records, thin records, absence
  records, and do-not-promote recommendations;
- no runtime code imports or promotes the new records;
- no prompt, validator, or live `/lolla` behavior changes are bundled into
  extraction.

## Model Briefs

### `opportunity-cost`

**Why this model is in Batch 3a:** It is the most frequent missing model in the
full 10-case dry-run: `7` appearances. It appears in repeated
resource-allocation routes and in the 3-case calibration.

**Decision Pressure surface gap it helps:** Resource-allocation pressures need
to name the real sacrifice behind a "yes" before the user commits time, equity,
capital, or scarce attention. It can improve the equity 90-day sprint pressure,
PhD shaping-phase pressure, and future allocation decisions where the selected
action hides displaced work.

**Prioritize high-value fields:**

- treatment requirements for naming the next-best alternative;
- case evidence needed to prove the sacrificed alternative is real and
  executable;
- misuse guards against invented alternatives or false precision;
- do-not-use conditions when the option set is poorly framed;
- dismissal logic when no viable alternative exists;
- tripwires for when the current yes should stop;
- operational constraints around displaced work, fallback, budget, attention,
  and calendar time.

**Weak/generic extraction looks like:**

- "Every choice has a cost."
- examples of opportunity cost without an action gate;
- generic advice to consider alternatives;
- fields that duplicate `trade-offs` or `prioritization` without naming the
  displaced next-best use.

**Prefer an absence record when:**

- the source does not support concrete next-best-alternative checks;
- source material stays at economics explanation level;
- the only extractable content would duplicate existing v3 records without
  improving dismissal or tripwire quality.

**Source-reading focus:** Look for language about next-best alternative, scarce
resources, default continuation, displaced work, fallback options, real
sacrifice, and hidden foreclosure.

**Decision Pressure evaluation later:** A useful record should make future
surfaces better at asking "what is sacrificed if we do this?" and "when should
this yes stop?"

### `true-uncertainty-navigation`

**Why this model is in Batch 3a:** It appears `5` times in the full 10-case
dry-run and `2` times in the 3-case calibration, especially in uncertainty-type
routes with partial coverage.

**Decision Pressure surface gap it helps:** The dry surface selected or
suppressed uncertainty pressures using available records like confidence
calibration and experimentation. This model should help future surfaces decide
whether the right move is robust action under genuine ambiguity, not more
analysis or false certainty.

**Prioritize high-value fields:**

- treatment requirements for robust action under ambiguity;
- case evidence needed to distinguish reducible from irreducible uncertainty;
- misuse guards against scenario theater;
- do-not-use conditions when uncertainty work would not change the next move;
- dismissal logic when uncertainty has been reduced enough to act;
- tripwires for monitoring, commitment sizing, and revisiting assumptions;
- operational constraints around hedging, options, and staged commitment.

**Weak/generic extraction looks like:**

- broad "consider scenarios" language;
- dramatic unknown-unknowns rhetoric;
- scenario lists without monitoring or commitment rules;
- uncertainty framing that postpones action by default.

**Prefer an absence record when:**

- the source supports only general scenario thinking;
- no source-backed commitment-sizing or monitoring constraints exist;
- extracted fields would make uncertainty sound sophisticated without changing
  a user's next action.

**Source-reading focus:** Look for multi-path futures, robust action, active
hypotheses, commitment sizing, monitoring rules, scenario discipline, and
anti-paralysis boundaries.

**Decision Pressure evaluation later:** A useful record should make future
surfaces better at saying "act robustly like this under ambiguity" and "stop
scenario work when these conditions are met."

### `falsifiability`

**Why this model is in Batch 3a:** It appears `4` times in the full 10-case
dry-run and directly supports the Decision Pressure requirement that each
pressure have a dismissal path.

**Decision Pressure surface gap it helps:** It should improve kill criteria,
reversal conditions, and user-verifiable dismissal paths for platform sprints,
PhD shaping phases, and other hypothesis-bearing recommendations.

**Prioritize high-value fields:**

- treatment requirements for stating disconfirming evidence;
- case evidence needed to test the live hypothesis;
- misuse guards against protected-belief theater;
- do-not-use conditions when the hypothesis is too vague to test;
- dismissal logic and reversal conditions;
- tripwires and stop conditions;
- operational constraints that turn a claim into a testable decision.

**Weak/generic extraction looks like:**

- philosophy-of-science explanation;
- "try to prove yourself wrong" without a fieldable test;
- decorative kill criteria invented beyond the source;
- dismissal paths that are tidy but not user-verifiable.

**Prefer an absence record when:**

- source material does not support operational test design;
- the model would mostly restate `experimentation` or `statistical-discipline`;
- the only available output would be generic skepticism.

**Source-reading focus:** Look for disconfirming tests, what would reverse a
claim, falsification conditions, protected beliefs, hypothesis boundaries, and
explicit evidence thresholds.

**Decision Pressure evaluation later:** A useful record should make future
surfaces better at producing `Dismiss if` and `Tripwire or next action` fields
that are source-backed and user-verifiable.

### `principal-agent-problem`

**Why this model is in Batch 3a:** It appears `4` times in the full 10-case
dry-run and `2` times in the 3-case calibration across incentive-alignment
routes.

**Decision Pressure surface gap it helps:** PR14 flagged
`third-year-phd-student / incentive-alignment` as a strong suppressed latent
pressure that lost only to the Compression Gate. Better coverage may make
future incentive-alignment pressures sharper, especially around checkpoint
design and delegated incentives.

**Prioritize high-value fields:**

- treatment requirements for aligning decision rights, effort, accountability,
  and downside exposure;
- case evidence needed to show hidden effort, hidden intention, or objective
  divergence;
- misuse guards against assuming bad faith;
- do-not-use conditions when the issue is capability, capacity, or muddled
  objective rather than incentive misalignment;
- dismissal logic when voluntary alignment evidence is present;
- tripwires around checkpoint design, hidden effort, and task-fit incentives;
- operational constraints for delegated incentives and accountability redesign.

**Special extraction note:** Pay special attention to checkpoint design, hidden
effort, delegated incentives, task-fit incentives, voluntary alignment evidence,
and when incentive framing becomes bad-faith theater.

**Weak/generic extraction looks like:**

- generic "align incentives" language;
- treating every disagreement as agency conflict;
- blaming an agent without diagnosing system design;
- restating `moral-hazard`, `incentives`, or `information-asymmetry` without a
  distinct operational constraint.

**Prefer an absence record when:**

- the source cannot support a distinct move beyond existing incentive records;
- applying the model would mostly produce suspicion or micromanagement;
- no source-backed dismissal path exists for proving alignment is sufficient.

**Source-reading focus:** Look for delegated objective gaps, hidden action,
metric compliance versus real alignment, accountability design, role clarity,
downside exposure, and the boundary between misalignment and capability.

**Decision Pressure evaluation later:** A useful record should make future
surfaces better at asking "who bears the downside, who controls the effort, and
what evidence would show real alignment instead of compliance?"

### `probabilistic-thinking`

**Why this model is in Batch 3a:** It appears `5` times in the full 10-case
dry-run and `2` times in the 3-case calibration, often paired with
`true-uncertainty-navigation`.

**Decision Pressure surface gap it helps:** Future uncertainty pressures need a
way to use probability ranges, sensitivity checks, and false-precision guards
without turning Decision Pressure into numeric theater.

**Prioritize high-value fields:**

- treatment requirements for ranges, sensitivity, and expected-value judgment;
- case evidence needed for a probability estimate to be decision-grade;
- misuse guards against exact-looking numbers without enough evidence;
- do-not-use conditions when probability language delays a needed commitment;
- dismissal logic when the range is narrow enough to act;
- tripwires for when a probability update changes the decision;
- operational constraints around base rates, priors, and confidence ranges.

**Weak/generic extraction looks like:**

- "think in probabilities" as a slogan;
- exact percentages not supported by source;
- probability estimates that look rigorous but do not change the decision;
- fields that duplicate `confidence-calibration` without adding a range,
  sensitivity, or commitment rule.

**Prefer an absence record when:**

- the source supports only broad uncertainty communication;
- no source-backed anti-fake-precision guard can be extracted;
- the model would mostly encourage postponing action.

**Source-reading focus:** Look for probability ranges, uncertainty
communication, expected value, false precision, priors, sensitivity testing,
and the boundary where probability language helps versus delays commitment.

**Decision Pressure evaluation later:** A useful record should make future
surfaces better at saying "what range matters, what update would change the
decision, and when are the numbers pretending to know too much?"

## Batch 3a Success Criteria

Batch 3a succeeds if it:

- improves future Decision Pressure selection, dismissal, or coverage honesty;
- reduces missing-record pressure without creating coverage theater;
- produces source-backed operational constraints;
- preserves exact source quote custody;
- allows honest absence where the source does not support useful affordances;
- keeps records dormant until a later dry surface proves they help compact
  pressure;
- makes at least one future selected, suppressed, or zero-output pressure easier
  to justify through the gates.

Batch 3a does not succeed merely because:

- five model records exist;
- missing-frequency counts improve;
- schema coverage looks smoother;
- all target models produce multiple affordances.

## Failure Modes

Reject or revise extraction if it produces:

- generic model summaries;
- elegant but non-actionable fields;
- fake tripwires;
- fake dismissal conditions;
- model records that exist only to smooth coverage;
- exact-looking operational thresholds not supported by source;
- extracted fields that duplicate existing v3 records without improving compact
  Decision Pressure;
- extraction that makes the graph look smarter without improving compact
  pressure;
- broad Batch 3 momentum disguised as a targeted patch.

## Evaluation After Extraction

After a later Batch 3a extraction PR, evaluate the records against Decision
Pressure, not just schema completeness.

Suggested evaluation questions:

- Would the new record change a selected pressure, suppressed candidate, or
  zero-output decision in the existing 12-route packet?
- Does it improve `Dismiss if` quality?
- Does it improve `Tripwire or next action` quality?
- Does it make coverage transparency more honest?
- Does it prevent fake traces or fake confidence?
- Does it reduce bloat, or does it add more material to compress?
- Would two reviewers apply the new record similarly?

Do not treat Batch 3a as ready for runtime promotion until a later dry review
shows that the extracted records improve compact Decision Pressure under the
same gates.

## Non-Goals For The Later Extraction PR

Even the later extraction PR should not:

- modify runtime behavior;
- modify prompts;
- modify validators unless a validation bug blocks extraction and is explicitly
  scoped;
- modify existing affordance records outside the five target models;
- start broad Batch 3;
- wire records into `/lolla`, Observatory, memo, Step 8, or Step 6;
- make user-facing claims;
- treat PR14 stability as live product proof.

## Roadmap / Schema Doctrine

The existing roadmap and schema docs already point to Batch 3a planning after
PR14 stability and still prohibit extraction execution without a brief. PR15
does not require additional roadmap/schema updates unless this brief is later
changed to authorize extraction execution, runtime use, or a different model
set.
