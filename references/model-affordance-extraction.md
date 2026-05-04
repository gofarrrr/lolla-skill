# Model Affordance Extraction Contract

This document defines the dormant model-affordance layer. It is a contract for
future extraction and review work, not runtime behavior. PR 1 creates rails only:
schema, fixtures, documentation, and validation. It must not change chat, memo,
Step 6, Step 8, Lane 4, or Observatory behavior.

## What An Affordance Is

A model affordance is an operational contract for what good use of a mental
model demands.

It is not:

- a definition of the model
- a topic tag
- a summary of the canonical article
- an invitation to mention the model in prose
- a schema-shaped slot to fill for every model

It answers:

- what mechanism must be running before this model earns weight
- what case evidence is required
- what treatment a good answer must perform
- what diagnostic question the model asks, if the source supports one
- what misuse the model guards against
- what should be set aside because the source does not support it

Example distinction:

- Bad: "Use Theory of Constraints to think about bottlenecks."
- Good: "Before optimizing a visible pain point, name the measured binding
  constraint, the dependency it controls, and the first metric that should move."

The second statement can change routing, gap questions, treatment audit, or a
future Observatory trace. The first cannot.

## What Good Use Means

Good use of a model is not naming the model. Good use means the model changes at
least one of these:

- what evidence is required
- what assumption is challenged
- what question should be asked
- what sequence should change
- what threshold or reversal trigger should exist
- what risk treatment is needed
- what option should be set aside
- what alternative mechanism should be considered

If a model does not change any of those, it may be educational, but it has not
earned runtime weight.

The model-use chain is:

```text
source-backed model affordance
  -> runtime activation condition
  -> case evidence quote
  -> treatment requirement
  -> output move
  -> treatment trace
```

If any link is unsupported, record which link failed. Do not smooth the gap.

## Source Authority Order

The authority order is:

1. Raw canonical Markdown source files.
2. Reviewed curation JSON from Wave 1, Wave 2, Wave 3, and later reviewed layers.
3. Compiled artifacts derived from reviewed curation.
4. Runtime interpretation.

Reviewed curation is operational normalization. It is not more authoritative
than the source. If a curated field and raw Markdown disagree semantically, the
Markdown wins and the disagreement should be visible in review notes.

Existing curation may be used as context in an extraction packet. It must not be
used as a shortcut around reading the full canonical Markdown.

## LLM-Driven Extraction Requirement

Semantic extraction must be performed by an LLM reading the source packet.

The extraction packet should contain:

- full canonical source Markdown for the model
- current Wave 1 activation curation, if available
- current Wave 2 intervention curation, if available
- current Wave 3 relation curation, if available
- relevant compiled model object, if useful for orientation
- target schema
- this contract
- any known omission or review notes

The LLM must read the full source packet and produce fewer, sharper records over
broader coverage. It should prefer one strong affordance to five weak ones.

The LLM must not treat headings, bullets, or field names as automatic semantic
truth. A heading such as "Risks and Mitigations" can point the reader to useful
material, but it does not by itself create a `misuse_guard`.

## What Python May Do

Python may:

- enumerate source files
- assemble extraction packets
- include source Markdown and curation JSON in a packet
- validate JSON shape
- validate enum values
- check exact `source_quote` substrings against source files
- detect missing evidence spans
- detect duplicate IDs
- apply the finite genericity gate defined below
- hash source files
- serialize reviewed records
- count coverage and absence states
- write quality reports
- compile reviewed artifacts in a later PR
- render Observatory-only diagnostics in a later PR

## What Python Must Not Do

Python must not:

- infer affordances from keywords
- infer semantic fields from headings
- infer relations from word overlap
- convert every "Danger when" bullet into a misuse guard without LLM judgment
- bulk-fill fields to satisfy a schema
- generate diagnostic questions from the model name
- decide a model was used well by substring matching alone
- silently promote low-confidence or weak-support records into runtime packets

Python validates and reports. It does not read meaning.

## Source Evidence

Every semantic field needs source evidence. A source evidence span contains:

- `source_file`
- `source_quote`
- `section_hint`
- `extraction_type`
- `confidence`

`source_quote` must be an exact substring copied from the canonical source file.
No paraphrase can masquerade as a quote.

Allowed `extraction_type` values:

- `explicit`: the source directly states the extracted material
- `normalized`: the source supports the material, but the affordance wording is
  reviewed operational normalization
- `not_supported_by_source`: used in absence records when the closest source
  material explains why a field was not extracted
- `review_note`: reviewer context, not runtime material

Allowed `confidence` values:

- `high`
- `medium`
- `weak`
- `not_applicable`

Weak evidence should stay review-only or Observatory-only until later evidence
proves it useful. It should not affect user-facing output by default.

## Status Values

Allowed status values:

- `supported`: source-backed and operationally useful
- `weak_support`: some support exists, but review or Observatory-only handling is
  needed before any runtime use
- `not_supported_by_source`: the attempted field was reviewed and the source did
  not support it
- `source_too_thin`: the source is too thin to support a runtime-useful field
- `duplicate_of_existing_field`: the material is already represented elsewhere
- `deferred_for_review`: extraction should stop until review resolves ambiguity

Status values are not quality theater. A `source_too_thin` record is a valid
substrate result. A `supported` record with generic material is not.

## Absence Records

Absence is a first-class substrate fact.

Use an absence record when:

- the source does not support an affordance
- the source supports a model concept but not an operational diagnostic question
- a misuse guard would be useful but is not source-backed
- a treatment requirement would be plausible but invented
- an existing field already carries the same material
- review should decide before extraction continues

An absence record contains:

- `attempted_field`
- `status`
- `reason`
- `runtime_policy`
- optional `source_evidence`

The reason should be specific enough to stop future agents from repeatedly
trying to fill the same unsupported slot.

Good absence:

```json
{
  "attempted_field": "diagnostic_questions",
  "status": "not_supported_by_source",
  "reason": "The source explains the model conceptually but does not provide an operational diagnostic prompt.",
  "runtime_policy": "do_not_promote",
  "source_evidence": []
}
```

Bad absence:

```json
{
  "attempted_field": "diagnostic_questions",
  "status": "not_supported_by_source",
  "reason": "Not found.",
  "runtime_policy": "do_not_promote"
}
```

The bad record records a missing slot but not a review judgment.

## No Completeness Theater

The goal is not to make every model satisfy every field.

Allowed outcomes:

- zero affordances for a model
- one strong affordance instead of several weak ones
- `not_supported_by_source`
- `source_too_thin`
- `duplicate_of_existing_field`
- `deferred_for_review`
- a recommendation to keep the model out of runtime use until source support is
  stronger

Forbidden outcomes:

- uniform-looking records for every model
- generic affordances that could apply to almost any model
- fields inferred because a future lane would like them
- source quotes that do not actually support the normalized field
- watery paraphrases that make strong source material less precise

The system should adapt to the knowledge base. The knowledge base should not be
stretched to make the system look complete.

## Finite Genericity Gate

The Python validator may reject only obvious generic boilerplate using this
finite, dumb rule set:

- `name` must be at least 24 characters.
- `mechanism` must be at least 40 characters.
- `name` and `mechanism` must not contain any of these lowercase substring
  fragments after whitespace normalization:
  - `careful thinking`
  - `think more carefully`
  - `think carefully`
  - `consider the problem`
  - `consider the risks`
  - `use this model`
  - `apply this model`
  - `analyze the situation`
  - `make a better decision`
  - `improve the reasoning`
  - `look at the bigger picture`
  - `be more thoughtful`

That is the entire genericity gate. No TF-IDF, embeddings, cosine similarity,
semantic scoring, "sounds mechanistic" checks, operationality scoring, or
question-quality judgment belongs in Python. If a check requires understanding
the meaning of the field, it belongs in LLM extraction or human review.

## Observatory-Only By Default

Model affordances are not user-facing product copy.

Until later PRs prove value against baseline behavior, affordance records are:

- offline extraction artifacts
- validation inputs
- review artifacts
- future Observatory/debug material

They must not alter:

- chat output
- memo output
- Step 6 reconsideration
- Step 8 pressure check
- Lane 4 gap questions
- runtime routing

Future promotion requires evidence that the affordance layer adds
non-duplicative user value. If that evidence is weak, the layer remains
Observatory/debug infrastructure.

## Validation Gates For PR 1

PR 1 validation should catch:

- missing required fields
- unknown statuses
- missing `source_quote`
- affordances without `source_evidence`
- duplicate affordance IDs
- the finite genericity gate above
- supported records with zero affordances and no explicit absence reason
- invalid absence records

Validation may check exact source quote substrings when source roots are
available. It must not perform semantic extraction.

## Future Extraction Checklist

For each model:

1. Read the full canonical Markdown source.
2. Read existing curation as context, not authority over the source.
3. Extract only affordances that would change evidence, questions, sequencing,
   treatment, set-aside, or audit behavior.
4. Attach exact source quotes to every semantic claim.
5. Prefer fewer, sharper affordances.
6. Record absence instead of inventing weak fields.
7. Mark weak support and duplicates honestly.
8. Keep the artifact Observatory-only until later evaluation proves runtime value.
