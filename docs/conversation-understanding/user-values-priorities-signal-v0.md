# User Values / Priorities Signal v0

Status: design-only
Date: 2026-06-27
Review slice: `user_values_priorities_signal_v0`

PR34 designs the missing `user_values_or_priorities_signal` surface that
semantic coverage and human review have repeatedly exposed.

This is not an implementation PR. It does not run `$lolla`, call models, change
runtime behavior, change prompts, change `SKILL.md`, mutate archives, implement
extraction, add a report builder, create a schema-enforced runtime artifact,
add a judge, add answer-quality scoring, or populate labels automatically.

The design question is:

```text
How should Lolla represent user values, priorities, tradeoffs, and
non-negotiables in a way that improves reasoning audit without becoming a
generic memory product, personality model, or values-judging system?
```

## Why This Exists

PR30, PR31, PR32, and PR33 established the evaluation flywheel:

- PR30: six complex human-reviewed seed runs;
- PR31: actionable-delta rubric;
- PR32: adversarial pair fixtures;
- PR33: broader human-review corpus batch.

The current system can preserve a local artifact chain, validate capture,
validate quotes, expose run custody, record answer-level human review, and label
action-changing deltas. It still does not represent user values and priorities
as first-class review evidence.

That missing signal matters because many Lolla improvements are not only about
facts or constraints. They are about what the user is trying to preserve,
trade, refuse, or prioritize:

- household capacity before career ambition;
- authority clarity before founder loyalty;
- buyer proof before enterprise aura;
- current obligations before market excitement;
- clinic operability before broad AI launch language;
- cash runway without destroying brand trust.

Today those signals appear implicitly in conversation, extraction summaries,
revised answers, memos, and human notes. PR34 defines how to talk about them
before any extraction work begins.

## Scope And Boundaries

This signal is audit context, not action approval.

It should help reviewers ask:

- Did the revised answer preserve what the user says matters?
- Did it confuse a constraint for a value?
- Did it over-infer a stable identity from a transient emotion?
- Did it flatter the user's preferred self-story instead of testing the
  decision?
- Did it erase a stakeholder obligation or unresolved tradeoff?

It should not:

- infer stable personality traits;
- create personal memory;
- rank values automatically;
- moralize values;
- decide what the user should value;
- treat values as permanent across conversations;
- turn emotional language into durable doctrine;
- approve actions;
- override deterministic run readiness;
- replace human review.

Raw transcript remains the source of truth. Shareable corpus and review
artifacts should not store raw sensitive text. When an example needs evidence,
use turn references, span references, or hashes rather than raw quote text.

## What Counts

A user value or priority is a trace-grounded signal that explains what the user
is trying to preserve, increase, reduce, trade, or refuse while making the
decision.

It can be explicit:

- "I will not take a role that makes my spouse carry the household alone."
- "Patient safety matters more than launch speed."

It can be inferred, but only with caution:

- repeated concern about household load may support a priority around family
  capacity;
- repeated insistence on written scope may support a priority around operating
  clarity.

It can be conflictual:

- wanting loyalty to a cofounder while needing authority to move;
- wanting cash now while preserving brand trust;
- wanting enterprise proof while protecting product reliability.

It can be provisional:

- a user may express a value for this decision without making a claim about
  their entire life or personality.

## What Does Not Count

The following are not user values or priorities by themselves:

- a factual constraint, such as runway, headcount, legal terms, calendar time,
  or procurement process;
- a generic preference, such as liking a cleaner interface or shorter answer;
- a fear, anxiety, or frustration that has not been tied to a chosen tradeoff;
- an identity statement that is not connected to action or willingness to pay a
  cost;
- a stakeholder's possible preference when the user has not adopted it as an
  obligation;
- model speculation about motives, status, personality, avoidance, ambition, or
  courage;
- a value-like phrase introduced only by the assistant or audit;
- a statement from a prior run or future memory layer;
- a moral ranking invented by Lolla.

When in doubt, mark the item as `needs_review` or leave the signal partial.

## Distinctions

### Explicit Value

A direct user statement about what matters, what must be preserved, or what the
user refuses to sacrifice.

Use when: the user says the value plainly enough that a reviewer can point to a
turn or span.

Avoid when: the value is only the reviewer's interpretation of a mood.

### Inferred Priority

A decision-relevant priority derived from repeated statements, constraints, or
tradeoff behavior.

Use when: the inference is grounded and useful, but not directly stated.

Rules: confidence should usually be `medium` or `low`, and `needs_review` should
be true unless a human reviewer has accepted it.

### Constraint

A fact or condition that limits the decision: money, time, authority, staffing,
policy, contract terms, health, legal exposure, or operational capacity.

Constraints may imply priorities, but they are not values by themselves. A
support burden is a constraint; preserving support-team credibility may be a
priority if grounded.

### Preference

A lighter-weight want that can influence the decision but may be traded without
changing the user's core commitment.

Preference is not a non-negotiable. A reviewer should not inflate preference
into value language just because it appears repeatedly.

### Fear Or Anxiety

An emotional signal about possible loss, embarrassment, regret, risk, or
conflict.

Fear may reveal a value, but only after grounding. "The user is anxious about
failure" is not enough. A useful value item would say what the user is trying to
protect and what evidence supports that.

### Identity Statement

A statement about who the user is, wants to be, or fears becoming.

Identity statements are high-risk for overclaiming. Treat them as decision
context, not personality diagnosis. Link them to a concrete tradeoff before
using them as audit evidence.

### Stakeholder Obligation

A duty, promise, dependency, or care responsibility involving another person or
group.

Examples include household load, current customer obligations, team capacity,
patient safety, partner trust, and buyer commitments. Stakeholder obligations
may be values, constraints, or both; the signal should distinguish the role.

### Tradeoff Willingness

Evidence that the user is willing to give up one thing for another under stated
conditions.

This is often the most useful form for Lolla because it directly affects
answer quality. It should name the traded item, the protected item, and the
condition.

### Non-Negotiable

A boundary the user says should not be traded away.

Use sparingly. A non-negotiable should require explicit grounding or human
review. Do not infer non-negotiables from strong adjectives alone.

## Proposed Schema Shape

This is a design schema, not production code.

```json
{
  "schema_version": "lolla.user_values_priorities_signal.v0",
  "status": "partial",
  "items": [
    {
      "id": "uvp_001",
      "label": "household_capacity_before_role_acceptance",
      "type": "stakeholder_obligation",
      "polarity": "must_preserve",
      "confidence": "high",
      "grounding": "turn_ref",
      "source_turn_refs": ["turn_015"],
      "quote_hash_or_span_ref": "span_ref_or_hash_only",
      "review_note": "The decision should not treat family support as a soft vibe check.",
      "needs_review": false
    }
  ],
  "conflicts": [
    {
      "value_a": "uvp_001",
      "value_b": "uvp_002",
      "conflict_type": "capacity_vs_ambition",
      "review_note": "The user wants a harder build but must preserve household capacity."
    }
  ],
  "open_questions": [
    {
      "question": "What weekly load would make the role unacceptable at home?",
      "why_it_matters": "Without this threshold, spouse support can be misread as blanket permission."
    }
  ]
}
```

Recommended top-level `status` values:

- `present`: at least one grounded item exists and is reviewable;
- `partial`: some items exist but grounding, conflict mapping, or confidence is
  incomplete;
- `missing`: the conversation likely contains values/priorities, but the signal
  did not capture them;
- `not_measured`: the run or corpus record did not attempt this signal.

Recommended item `type` values:

- `explicit_value`
- `inferred_priority`
- `preference`
- `constraint_related_priority`
- `stakeholder_obligation`
- `tradeoff_willingness`
- `non_negotiable`
- `identity_statement`

Recommended `polarity` values:

- `wants_more`
- `wants_less`
- `must_preserve`
- `willing_to_trade`
- `refuses_to_trade`

Recommended `confidence` values:

- `high`
- `medium`
- `low`

Recommended `grounding` values:

- `span`: source span exists and can be checked locally;
- `turn_ref`: source turn reference exists, but span grounding is not available;
- `derivation`: item is derived from multiple signals and needs review;
- `none`: item is ungrounded and should not be trusted.

`quote_hash_or_span_ref` should not contain raw quote text in corpus-safe
exports. It can hold a local span id, source locator, or hash that lets a local
reviewer recover the evidence from the raw transcript.

## Grounding And Confidence Rules

Use the strongest available grounding:

1. `span` with local source reference.
2. `turn_ref` when span is unavailable.
3. `derivation` when the item comes from multiple trace facts.
4. `none` only as an error or review placeholder.

Confidence should follow grounding:

- `high`: explicit user language or repeated evidence with clear turn/span
  support;
- `medium`: grounded inference that a reviewer can inspect;
- `low`: plausible but fragile inference, conflict, or unstated priority.

Derived values should usually be:

- `grounding: derivation`;
- `confidence: medium` or `low`;
- `needs_review: true`.

Do not mark a derived value as `high` unless a human reviewer ratifies it or
the evidence is nearly explicit across multiple turns.

## Conflicts

The signal should preserve conflicts rather than resolve them automatically.

Examples:

- loyalty to a cofounder conflicts with moving decision rights;
- household stability conflicts with startup learning;
- brand trust conflicts with immediate cash;
- enterprise opportunity conflicts with reliability and support load;
- patient access conflicts with clinic safety and operability.

A conflict record should name the two items, describe the conflict type, and
explain why it matters for the audit. It should not decide which value wins.
The revised answer may propose a gate or sequence, but that is answer-level
reasoning, not automatic value ranking.

## Reviewer Use

Human reviewers should use the signal to inspect whether Lolla preserved the
right decision context.

Useful review questions:

- Did the revised answer protect the user's stated non-negotiables?
- Did it convert vague values into concrete terms without distorting them?
- Did it confuse a hard constraint for a value?
- Did it over-flatter the value the user seemed to prefer?
- Did it preserve stakeholder obligations?
- Did it name unresolved conflicts and ask the user the right question?
- Did it change action, threshold, sequence, evidence, scope, or stop rules
  because of the value signal?

The signal can support PR31 labels:

- `user_question_added` when an unresolved value conflict requires user input;
- `threshold_changed` when a priority becomes a concrete gate;
- `sequence_changed` when a protected value must be checked before action;
- `written_term_added` when a value must become an operating agreement;
- `scope_narrowed` when a priority makes a smaller path safer;
- `overclaim_retracted` when Lolla stops pretending it knows the user's motives.

The signal should not create a new answer-quality score.

## Overclaim And Sycophancy Failure Modes

PR34 makes these failure modes explicit before implementation:

| failure | description | safer behavior |
|---|---|---|
| personality overreach | Turns a decision statement into a stable personality claim. | Keep the item decision-local and mark inference as low confidence. |
| identity flattery | Echoes the user's preferred self-story without testing it. | Require action, evidence, or tradeoff grounding. |
| transient-emotion hardening | Treats fear, frustration, or excitement as durable value. | Mark as emotion/context unless tied to a stated tradeoff. |
| moral ranking | Implies one value is morally superior. | Preserve conflict without ranking values automatically. |
| stakeholder erasure | Treats another person's obligation as optional color. | Represent stakeholder obligation separately from user preference. |
| constraint laundering | Rebrands a factual constraint as a value to make it sound profound. | Keep constraints as constraints unless priority evidence exists. |
| invented motive | Adds motive or status psychology unsupported by the trace. | Use `needs_review` or omit the item. |
| memory drift | Carries a value beyond the current run as if persistent. | Keep values run-local unless a future explicit memory design exists. |
| approval laundering | Uses a value signal to approve action. | Keep values as audit context; reliance remains human-owned. |

## Corpus-Safe Examples

These are paraphrased examples from PR30 and PR33. They are not raw transcript,
memo, revised-answer, or provider text.

| case pattern | possible signal | review implication |
|---|---|---|
| Career decision with household load | Household capacity is a stakeholder obligation and possible non-negotiable; role ambition is a competing priority. | The answer should require written load and support terms before acceptance. |
| Cofounder authority decision | Loyalty and continuity matter, but authority clarity is the priority that protects the company. | The answer should not let a warm cooperation reset replace decision-rights movement. |
| Enterprise beta decision | Buyer proof should outrank status aura when choosing launch priority. | The answer should require same-shape paid-pilot proof rather than privileging the bigger prospect. |
| Product pivot | Higher-ACV market opportunity conflicts with capacity and current customer obligations. | The answer should sequence capacity and obligation gates before market validation. |
| Clinic assisted intake | Patient safety and clinic operability are must-preserve priorities. | The answer should narrow launch scope and add stop/rollback conditions. |
| Pre-sale or consulting offer | Cash runway matters, but brand trust and client-ready scope cannot be traded away blindly. | The answer should prefer bounded commitment tests over broad promise-making. |

## Artifact And Eval Surface

PR34 proposes this as a semantic coverage field:

```text
user_values_or_priorities_signal
```

It should appear first in review or offline evaluation artifacts, not runtime
product output. The initial surface could be:

- a human-review worksheet section;
- an offline semantic coverage report field;
- a local-only corpus summary;
- a future candidate field in `conversation_understanding_ir.v0`, if that IR is
  later approved.

It should not be automatically populated into archive records or used to change
`caller_action` until a later PR explicitly approves extraction, validation,
and reliance rules.

## Relation To Risk Mode

PR36 now defines risk mode as a review and reliance policy layer, not domain
authority:

```text
docs/evals/risk-mode-behavior-plan-v0.md
```

Values and priorities can help reviewers understand why a high-stakes or
risk-sensitive answer needs stronger gates, stop rules, stakeholder questions,
or domain review. They must not be used to infer that the user approves action,
that Lolla has resolved a value conflict, or that `safe_for_agent_use` can be
upgraded automatically.

PR37 turns that policy into fixtures:

```text
docs/evals/risk-mode-fixture-matrix-v0.md
```

Those fixtures may use values/priorities as review context, but they preserve
the same boundary: value signals explain why reliance should be stricter; they
do not approve action.

PR38 reviewed the fixture matrix and added the explicit high-stakes unresolved
values/stakeholder-obligation fixture:

```text
docs/evals/risk-mode-fixture-review-v0.md
```

## Deterministic Vs Probabilistic Work

Deterministic code could later validate:

- schema shape;
- allowed enum values;
- stable item ids;
- source turn refs exist;
- span refs point into the local transcript;
- `needs_review` is true when grounding is `derivation` or `none`;
- raw quote text is absent from corpus-safe exports;
- conflicts reference existing item ids;
- item counts and status summaries are present;
- no value item is marked high confidence without grounding.

Probabilistic extraction would be required to:

- notice implicit priorities across turns;
- distinguish fear from value;
- map stakeholder obligations;
- identify tradeoff willingness;
- propose value conflicts;
- phrase open questions;
- avoid overclaiming motives.

Human review remains required to:

- ratify inferred values;
- decide whether a priority mattered to answer quality;
- decide whether the revised answer preserved or distorted the value;
- resolve ambiguous or conflicting values;
- accept any future calibration examples.

## Future Implementation Gate

Implementation should remain blocked until a later approved PR can answer:

- Which artifact will carry the signal first: worksheet, offline report, or IR
  projection?
- Will the signal be extracted manually, by offline LLM extraction, or both?
- What exact privacy rules prevent raw sensitive text from entering exported
  corpora?
- How will span or turn grounding be validated?
- What false-positive examples prove the overclaim guardrails work?
- How many human-reviewed records show that this signal changes review quality?
- How will provider-boundary and cost exposure be handled if an LLM extractor
  is used?
- What does the system do when the signal is `partial`, `missing`, or
  `not_measured`?

Recommended next implementation sequence, if approved later:

1. Add a local human-review worksheet section for values/priorities.
2. Add an offline, read-only values/priorities report over selected archives.
3. Measure whether reviewers find the report useful and low-noise.
4. Only then consider archive integration or `conversation_understanding_ir.v0`.

Do not jump directly from this design to runtime extraction.

PR49 now turns the first step into a docs-only worksheet plan:

```text
../evals/user-values-priorities-worksheet-plan-v0.md
```

That plan is still human-review-only. It does not add extraction, exports,
runtime behavior, memory, automatic labels, `conversation_understanding_ir.v0`,
or a judge.

PR50 now tests that worksheet shape with paraphrase-only fixtures:

```text
../evals/user-values-priorities-worksheet-fixtures-v0.md
../evals/user-values-priorities-worksheet-fixtures-v0.json
```

Those fixtures are examples for human review. They do not copy raw archive
content, implement extraction, add export code, populate labels, change runtime
behavior, or approve a judge.

PR51 now reviews the fixture pack:

```text
../evals/user-values-priorities-worksheet-fixture-review-v0.md
../../reviews/human/user-values-priorities-worksheet-fixture-review-v0/review.json
```

The review finds all six fixtures understandable and useful for human review,
with stakeholder obligations and unresolved conflicts preserved. It recommends
blank worksheet/export structure as the next narrow slice, not extraction,
runtime behavior, automatic labels, or judging.

PR52 now adds that blank deterministic structure:

```text
../evals/user-values-priorities-blank-worksheet-export-v0.md
../../engine/system_b/user_values_priorities_worksheet.py
../../scripts/build_user_values_priorities_worksheet.py
```

The helper creates empty `lolla.user_values_priorities_worksheet.v0` JSON with
optional compact case/run metadata. It does not read archives, infer values,
populate labels, change runtime behavior, or add a judge.

PR53 now pilots human-filled worksheets on existing reviewed records:

```text
../evals/user-values-priorities-worksheet-human-pilot-v0.md
../../reviews/human/user-values-priorities-worksheet-pilot-v0/worksheets.json
```

The pilot fills four worksheets by hand from reviewed summaries and local
human-review records. It keeps notes paraphrase-only, leaves all raw/private
inclusion flags false, records all inferred value items as requiring user
confirmation, and handed off to PR54 rather than extraction, runtime
integration, automatic labels, or judging.

PR54 now reviews that pilot and closes the lane at v0 for human-owned review:

```text
../evals/user-values-priorities-pilot-review-v0.md
../../reviews/human/user-values-priorities-pilot-review-v0/review.json
```

The lane is paused before extraction, memory, runtime integration, automatic
labels, `safe_for_agent_use` automation, or judging.

## PR34 Answers

Is `user_values_or_priorities_signal` a field in semantic coverage?

Yes. PR34 defines it as a first-class semantic coverage field that is currently
designed but not implemented.

Should it be part of future `conversation_understanding_ir.v0`?

Possibly, but only after offline worksheet/report evidence proves the shape is
useful and safe. PR34 does not approve a new IR.

Should it be human-review-only first?

Yes. The first surface should be human-review or offline evaluation, not normal
runtime.

Which parts can be deterministic validation?

Schema, enums, ids, turn/span references, grounding/status consistency,
conflict references, and corpus-safe text boundaries.

Which parts require LLM extraction if later implemented?

Implicit priority detection, conflict mapping, stakeholder-obligation
classification, tradeoff interpretation, and open-question drafting.

What would make a values signal unsafe or noisy?

Ungrounded motives, personality claims, moralized ranking, memory drift,
transient-emotion hardening, stakeholder erasure, or approval laundering.

What evidence would justify implementation in a later approved PR?

A small human-reviewed worksheet or offline report showing that the signal
helps reviewers explain useful, noisy, or missing friction better than current
artifacts, without adding overclaim or privacy risk.

What did PR49 add?

PR49 adds the human worksheet plan that PR34 recommended as the first safe
surface. It makes the signal reviewable, not automatic.

What did PR50 add?

PR50 adds paraphrase-only worksheet fixtures so reviewers can test whether the
human worksheet shape is understandable before export, extraction, runtime
integration, or judging.

What did PR51 add?

PR51 reviews those fixtures and records that all six pass as human-review
examples. It makes the next safe step blank worksheet/export structure, still
without extraction, runtime integration, automatic labels, or judging.

What did PR52 add?

PR52 adds the blank worksheet builder and validator. It makes the empty local
artifact shape available for human pilots without extracting values, reading
archives, changing runtime behavior, populating labels, or judging.

What did PR53 add?

PR53 pilots four human-filled worksheets from existing reviewed summaries. It
shows that the worksheet can add review structure while preserving unresolved
conflicts and confirmation needs, but it still does not extract values, update
memory, change runtime behavior, populate automatic labels, or judge.

What did PR54 add?

PR54 reviews the PR53 pilot and closes the worksheet lane at v0 for
human-owned review. All four pilot worksheets pass, all inferred values remain
confirmation-needed, and the lane is paused before extraction, memory, runtime
integration, automatic labels, `safe_for_agent_use` automation, or judging.

## Review Receipt

- PR34 is docs/design-only.
- No `$lolla` run.
- No model calls.
- No runtime files changed.
- No prompts changed.
- No `SKILL.md` changes.
- No extraction implemented.
- No report builder added.
- No schema-enforced runtime artifact added.
- No judge or answer-quality score added.
- No automatic labels added.
- PR49 through PR54 now provide a human-owned worksheet surface and v0 review
  decision, but still no automated values extraction or runtime integration.
