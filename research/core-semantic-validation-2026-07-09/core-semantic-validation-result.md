# Core Semantic Validation — Case 01 Result

Date: 2026-07-09  
Case: `case-01-enterprise-logo-beta`  
Source run: `20260709T201634Z_7a7930`  
Graph runtime changed: no

## Decision

Use a **shared source-grounded semantic kernel with two projections**.

- The pre-audit projection should contain only fields needed to select or
  apply reasoning pressure.
- The post-audit Decision Work projection should contain revision,
  accountability, loss, review, custody, and release fields.
- Do not replace the live compact extractor with all 46 Decision Work fields.
- Do not feed the new shadow interpretation or reasoning-pattern design into
  the graph yet.

The richer shadow path materially outperformed the compact path on Case 01,
but it still has specific coverage and labeling defects. It is ready for the
next corpus experiment, not production promotion.

## Fixed evaluation case

The synthetic six-turn source conversation is now fixed at:

- `tests/fixtures/core_semantic_validation/case_01_enterprise_logo_beta/conversation.txt`
- SHA-256: `17fbd7836acf740c0c9225661a0a5dc7329b9e222be203a203392316b6fb38c5`
- provisional source-first annotations:
  `tests/fixtures/core_semantic_validation/case_01_enterprise_logo_beta/gold.json`

The gold set contains 15 required observations across:

- operative-question change;
- user corrections and counter-pressure;
- assistant stance trajectory;
- constraints, options, and thresholds;
- dropped or under-carried threads;
- uncertainty and evidence boundaries.

It also records five bounded absences, including no explicit logo permission,
stop rule, capacity gate, reversible private path, or supported user change of
mind.

## What was run

### Compact live extraction path

The actual `scripts/run_extract.py` path was executed three times against the
identical conversation.

### Rich shadow / Decision Work-aligned path

The shadow path combines:

- the existing exact-span live-constraint specialist;
- the existing exact-span assistant-stance specialist;
- the existing exact-span dropped-thread specialist;
- one narrow joint-process read for question changes, user pressure, options,
  thresholds, and evidence boundaries;
- a deterministic projection onto selected Decision Work field names.

It was executed three times with four small provider calls per run. The three
persisted runs used 6,752, 6,554, and 6,731 tokens respectively. No raw provider response
text is retained by the evaluation CLI after the custody patch.

## Measured comparison

The deterministic comparison is preserved in:

- `two-path-comparison.json`
- `two-path-comparison.md`

| Measure | Compact path | Shadow path |
| --- | ---: | ---: |
| Repeats | 3 | 3 |
| Stable source-grounded gold observations | 0 / 15 | 11 / 15 |
| Mean exact-span gold recall | 0.000 | 0.778 |
| Mean span repeatability | 0.460 | 0.865 |
| Mean labeled repeatability | 0.460 | 0.827 |

The zero compact score is not a claim that the compact summaries contain no
useful meaning. The metric is deliberately stricter: an observation receives
credit only when the artifact preserves a matching literal source span in the
correct semantic family. Compact constraints and dropped threads are
paraphrases with turn references, not exact-span evidence.

## What the compact path captured

Across three repeats it consistently captured:

- the broad public-beta decision;
- company size, lack of signed commitment, and engineering capacity;
- the same three exact assistant reasoning passages;
- the final recommendation in synthesized prose.

It did not represent:

- the Turn-5 change from “should we launch?” to “what evidence should gate an
  announcement?”;
- user counter-pressure as a trajectory;
- the assistant's commitment, qualification, condition, and deferral events;
- live options and their statuses;
- explicit evidence boundaries;
- the user's opportunity-loss concern;
- criteria being deferred until after action as a first-class event.

Its repeatability defect was semantic, not only lexical:

- constraint counts were 3, 4, and 4;
- the board/name pressure was omitted from one constraint set;
- the single dropped thread changed from board prestige pressure in one run to
  purchase-commitment concern in two runs;
- the current evidence-gate question was not carried as the decision question
  in any run.

## What the shadow path captured

All three final repeats preserved as exact spans:

- the initial question and current evidence-gate question;
- no signed commitment;
- engineering capacity;
- the purchase-commitment concern;
- the opportunity-loss concern;
- the assistant's initial launch commitment;
- the Turn-4 qualification without direction change;
- the email-confirmation threshold;
- the post-launch success-criteria deferral;
- the under-carried purchase-commitment concern.

The following elements were present with the same source spans in every run:

- question events;
- user-pressure events;
- live constraints;
- assistant stance spans;
- the purchase-commitment dropped-thread span.

## What the shadow path still missed or varied

It never recovered three gold observations in the persisted sample:

1. board/name pressure as user counter-pressure;
2. friendly emails as weak evidence in every repeat;
3. the evidence request as a thread that the final answer did not substantively
   answer.

Board/name pressure was recovered as an under-carried thread in two of three
runs, so it was observed but not stable.

It also varied in three ways:

- the final email-before-announcement stance varied between `condition` and
  `commitment`, although the exact span was stable;
- the limited-three-company option appeared in one of three runs;
- evidence-boundary spans and labels had 0.611 pairwise Jaccard;
- dropped-thread counts were 2, 1, and 2, with 0.667 pairwise Jaccard.

These defects imply:

- exact source spans are necessary but not sufficient;
- relation labels need deterministic or adjudicated normalization;
- “dropped” should not be a standalone binary output;
- multi-fact user corrections need an explicit completeness check;
- evidence boundaries need either narrower specialist prompts or a
  deterministic reconciliation layer.

## Field-by-field Decision Work result

All 46 current Decision Work contract fields now have exactly one decision in
`field-decisions.json`:

| Decision | Count | Meaning |
| --- | ---: | --- |
| Keep | 17 | Retain as a distinct semantic, custody, or release field. |
| Merge | 17 | Preserve inside a shared event, metadata, privacy, or review structure. |
| Defer | 10 | Collect only after audit/reconsideration; never use for pre-audit routing. |
| Remove | 2 | Keep as static schema ownership policy, not repeated run semantics. |

The most important changes are:

- `decision_question` becomes a timeline of initial/current question events;
- starting direction becomes the first assistant stance event;
- user mind change is not a boolean; question and stance changes remain
  separate;
- sycophancy language becomes a neutral, source-linked
  alignment-without-integration relation;
- unresolved and dropped threads become one thread-status structure;
- constraints become typed events rather than separate parallel lists;
- option status belongs on each option event;
- momentum loss becomes a subtype of lost-value review;
- deterministic/LLM ownership stays in the schema rather than bloating each
  run.

## Reasoning-pattern packet design

Only after completing the field decisions, a fact-free packet was designed at:

- `docs/conversation-understanding/reasoning-pattern-packet-v0.md`
- `docs/conversation-understanding/reasoning-pattern-packet-v0.json`

The design separates:

1. a provenance surface mapping pattern IDs to source semantic item IDs; and
2. a sealed graph routing projection containing only controlled mechanism IDs,
   subject scope, protection state, and structural relations.

The graph must receive only the second surface. The example packet explicitly
contains no quotes, entities, case quantities, dates, desired outcome, or topic
labels in its routing projection.

## Product conclusion from Case 01

The core semantic problem is real and tractable.

The compact path is economical and useful as a broad summary, but it is not a
sufficient representation of the joint reasoning process. The source-grounded
shadow path provides a materially better substrate for future reasoning-pattern
projection. Its remaining misses are visible, bounded, and testable.

The next development move is to run this same contract across the remaining
core corpus before changing graph input. The graph boundary should be promoted
only after semantic coverage, label normalization, fact-leak lint, and
same-reasoning/different-facts invariance checks pass.
