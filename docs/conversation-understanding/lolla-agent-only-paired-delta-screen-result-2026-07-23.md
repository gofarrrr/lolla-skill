# Lolla Agent-Only Paired-Delta Screen Result

Date: 2026-07-23
Status: completed provider-free checked-in-safe diagnostic
Decision: keep the screen as a bounded Product Delta diagnostic; do not change
the graph, planner, runtime, or product claims
Evidence class: fresh-agent blind review of existing checked-in conversations
and answer artifacts, followed by deterministic lineage reveal; not human
review, graph-specific causal evidence, answer-quality measurement, or
real-user usefulness evidence
New provider calls and cost: 0 and `$0.00`

## Plain-language result

We can test an important part of Lolla without asking the founder to run the
skill or grade its answers.

The repository can now take existing conversations and paired answers, hide
which answer received additional external pressure, and ask fresh agents to
identify:

- which reasoning moves are genuinely different;
- which moves merely repeat the conversation;
- which useful source elements were weakened or lost;
- which details were invented;
- which additions create decision leverage;
- which additions create analysis burden;
- when no additional pressure should be forced.

That test worked as a diagnostic. Fresh agents detected both useful reasoning
moves and real harms. They preserved the exact duplicate as equivalent and the
quiet case as a legitimate stand-down. They did not produce a monotonic
“pressure is better” story.

The test does **not** answer whether the relationship graph itself created the
differences. None of the existing answer pairs isolates direct pressure from
graph-expanded pressure. It also does not answer whether a human would
experience an `aha`, make a better decision, or prefer either answer.

## Falsifiable question

> Can a fresh agent distinguish source-grounded answer-exclusive reasoning
> moves from repetition, lost value, unsupported additions, ambiguity, and
> legitimate stand-down across an existing mixed paired corpus?

The bounded answer is **yes, diagnostically**. The screen produced
source-reviewable atomic differences, caught the duplicate null, preserved
stand-down, and exposed disagreement. The broader answer remains **unknown**:
agent detection is not human usefulness, and paired pressure versus no pressure
is not graph-specific attribution.

## Why this is Product Delta work

This is not a new reader, evaluator product, or second graph system. It deepens
the existing offline Product Delta owner:

```text
checked-in source + exact paired answers
  -> deterministic fresh blinding
  -> source-first agent review
  -> frozen non-scalar observations
  -> deterministic lineage reveal
  -> disagreement-preserving diagnostic
```

It does not enter the live Lolla path. It does not run the graph, compiler,
portfolio planner, skill, provider boundary, Decision Work sidecar, Atlas, or
Observatory.

The existing pressure/understanding/graph PRD, consumer-context contract v1,
and role/attribution case candidate remain the prospective graph-comparison
owners. No parallel PRD was created.

## What was inspected

The screen reused all checked-in-safe paired material that met the frozen
contract:

- three complete exact pairs:
  - retailer pilot;
  - museum archive license;
  - independent-consulting launch;
- three older research-only answer-core pairs with partial source views:
  - founder equity;
  - consultant whistleblower report;
  - PhD direction;
- one exact duplicate null made from the retailer control answer;
- one complete quiet library case with a deterministic zero-candidate
  stand-down;
- ten existing adversarial Product Delta reviewer traps.

Fourteen older Product Delta seed cases were explicitly excluded. Their
checked-in-safe material does not contain an exact source-complete answer pair;
the screen did not inspect private archives or pretend that summaries were full
evidence.

The exact inputs, hashes, evidence classes, fresh arm mapping, exclusions, and
historical-reference locators are in the
[sealed manifest](../../research/agent-only-paired-delta-screen-2026-07-23/sealed-manifest.json).
The manifest was not shown to fresh reviewers.

## Method

### 1. Freeze the contract before review

The [review contract](../evals/lolla-agent-only-paired-delta-screen-contract-v1.json)
forbids a winner, score, ranking, vote, certification, arm recommendation,
graph-causation claim, or usefulness claim.

Each atomic move records:

- whether it is shared, A-exclusive, B-exclusive, contradictory, or uncertain;
- the reasoning operation;
- source grounding;
- source evidence;
- possible decision effect;
- cognitive effect.

Answer-level reads separately preserve source value, lost or weakened value,
unsupported additions, and cognitive burden.

### 2. Blind deterministically

The builder:

- reads only declared repository-relative artifacts;
- preserves complete and partial source coverage as different evidence states;
- strips prior outcomes, provider/model metadata, source filenames that reveal
  treatment, and old arm labels from the reviewer packet;
- uses a stable SHA-256-derived orientation to assign fresh A/B labels;
- stores the mapping only in the sealed manifest;
- creates an exact duplicate null;
- reproduces the checked-in packets byte-for-byte under validation.

### 3. Use fresh isolated agent contexts

Two fresh agent contexts were used:

- one context performed the primary paired review;
- one context first performed the ten qualification traps and then performed a
  separate skeptical paired review.

Both pair reviewers were blind to:

- the sealed manifest;
- historical comparison outcomes;
- other repository documents;
- each other's review;
- this development conversation.

The skeptical reviewer is not fully independent of the qualification exercise
because both occurred in one context. That limitation is preserved in the
[consolidation](../../research/agent-only-paired-delta-screen-2026-07-23/consolidated-diagnostic.json).

### 4. Freeze before lineage reveal

All three review files were saved before the maintainer read the sealed
mapping. The deterministic fan-in then added exact lineage facts without
selecting an authoritative reviewer or resolving disagreement by vote.

## Qualification result

The fresh qualification reviewer produced:

| Disposition | Count |
|---|---:|
| `sufficient_for_bounded_comparison` | 8 |
| `blocked_thin_context` | 1 |
| `inconclusive` | 1 |
| `needs_human_review` | 0 |

A maintainer comparison with the sealed trap intent found the intended
discipline in every trap:

- the thin packet stopped instead of manufacturing a comparison;
- longer and cleaner artifacts were not credited as decision value;
- generic caution without leverage was identified;
- an already-present gate was treated as repetition;
- lost options and buried ambition remained visible;
- assistant influence was not rewritten as pure user intent;
- conflicting specialist signals remained inconclusive;
- provisional language was not hardened into authority.

This is agent-reviewer discipline evidence. It is not a calibrated judge,
human validation, or a quality score.

## Paired result

The table records the exact lineage only after both reviews were frozen.
`Material reads` preserves the two reviewers in primary/skeptical order.

| Case | Evidence | Added-context arm | Material reads | What became visible | Harm or limit also visible |
|---|---|---:|---|---|---|
| Retailer pilot | complete exact pair | B | present / present | independent-demand operationalization, audience-transfer testing, downside and signal questions | invented `12%`, week-six, `20%`, and `50%` thresholds; additional negotiation and analysis burden |
| Museum license | complete exact pair | B | uncertain / uncertain | worst-case acceptability and explicit early-reversal questions | existing threshold commitment was understated; mitigations were repeated; non-reversible learning risk could be made to look trigger-solvable |
| Consulting launch | complete exact pair | A | uncertain / present | broader withdrawal of unsupported conversion, timing, and retainer authority; fractional work reframed as an option to test | more qualification burden; the other arm added unsupported external market-rate explanations |
| Founder equity | partial source view | A | uncertain / uncertain | dependency measurement, feedback-loop risk, and refusal/continuity questions | valuation humility weakened; broad measurement and causal chains exceed what the excerpts establish |
| Consultant report | partial source view | B | present / present | the added-context arm sharpened preservation and legal-conclusion boundaries | the raw arm preserved more of the source-named counsel-incentive and Wednesday-protocol nuance; both reviewers guessed that raw arm had received external context |
| PhD direction | partial source view | A | absent / uncertain | operational fallback viability and dated evidence gates | the raw arm preserved fallback decay and base-rate humility; the added arm introduced unsupported identity and parallel-option constraints |
| Duplicate null | complete exact duplicate | indistinguishable | absent / absent | exact equivalence | both arms share the same minor correctness overclaim; there is no paired delta |

The paired reviewers agreed on the material-difference category in five of seven
cases. They disagreed on the consulting case and the partial-view PhD case. The
consolidation preserves those two disagreements rather than computing a net
label.

Both reviewers supported the quiet library stand-down. They separately warned
that forcing more analysis could add generic caution, delay a bounded
experiment, weaken a complete protocol, or manufacture uncertainty from a
mechanical zero.

## What the arm guesses showed

Across twelve non-null reviewer/case guesses:

- six matched the sealed lineage;
- five did not match;
- one declared the arms indistinguishable.

Both reviewers correctly identified the duplicate null as indistinguishable.

This is not a performance score. It is evidence that the fresh blinding did not
leave a consistently reliable “pressure style” shortcut. More importantly,
reviewers could identify the atomic reasoning differences even when they
misidentified which process produced them.

## Relationship to older judgments

The three partial-view pairs were deliberately selected because the historical
research judgments were mixed:

- founder equity: pressure had previously been preferred;
- consultant report: raw had previously been preferred;
- PhD direction: the comparison stopped at a tie.

The fresh reviewers were not shown those outcomes. They recovered the
underlying trade-offs:

- fuller measurement versus valuation humility;
- legal-conclusion restraint versus counsel-incentive and encounter nuance;
- operational fallback gates versus fallback decay and reference-class
  humility.

That is a stronger diagnostic result than reproducing old winner labels. The
screen can surface the reasons on both sides without being told which side the
older review favored.

The earlier quiet consulting review provisionally favored the treatment's more
complete numerical correction. In the new fresh orientation, that treatment
was Arm A. Both new reviewers detected Arm A's broader correction but guessed
that Arm B received the external context. Again, the substantive delta was
more recoverable than its provenance.

## What this says about the graph

### What it supports

The screen supports four narrow statements:

1. Existing pressure-bearing outputs contain agent-detectable reasoning
   differences, not only prose variation.
2. Those differences can include useful-looking questions, gates,
   counterframes, time horizons, or premortems.
3. The same output can also contain repetition, unsupported specificity, lost
   source value, and excessive burden.
4. A source-first, non-scalar review can preserve that mixture and can preserve
   no-pressure behavior.

### What it does not support

The screen cannot say which observed move came from:

- the direct mental-model supply;
- the relationship graph;
- generic additional context;
- the reconsideration instruction;
- model sampling;
- a stronger second pass.

No included case has a matched direct-only versus graph-expanded output pair.
Therefore this result is not evidence for one hop, two hops, incoming
traversal, graph-wide summaries, community detection, new ranking, or more
active pressure.

The screen gives no reason to change the existing graph before the narrower
F2/F3 comparison exists. Expanding traversal now would increase the amount of
unattributed pressure precisely when the current evidence shows that additional
pressure can produce both a useful lens and invented precision in the same
answer.

## Decision

Keep the following as one bounded Product Delta diagnostic owner:

- deterministic mixed-corpus builder;
- blind packet;
- sealed lineage manifest;
- ten qualification traps;
- primary and skeptical fresh-agent reviews;
- deterministic shape/custody validation;
- disagreement-preserving consolidation.

Do not:

- connect it to the live skill;
- turn it into an automatic answer grader;
- use identity-guess agreement as quality evidence;
- fill principal-human fields from agent review;
- reopen R4;
- change graph traversal, direction, ranking, or budget;
- import the screen into Decision Work, Atlas, or Observatory;
- claim that Lolla or the graph improved decisions.

## Opportunities in order

### 1. Reuse the screen as an offline preflight

Future exact paired experiments can use the same null, stand-down, source-first
atomic-move contract, blind freeze, and harm inventory. This can be done without
founder participation as diagnostic engineering, provided the inputs are
already authorized and checked-in-safe.

### 2. Use it on the existing F2/F3 graph question only after that pair exists

The current consumer-context case candidate already defines:

- F2: human-controlled direct-only pressure;
- F3: the same direct component plus graph expansion.

Its provider-neutral envelopes and equality controls exist, but it has no
generated F2/F3 outputs, no signed principal-human source-first target, no
provider/model/cost contract, and no execution authorization. The current
screen is ready to inspect those outputs later; it does not authorize producing
them now.

### 3. Keep agent and human questions separate

Agents can autonomously test:

- packet custody;
- blind-review discipline;
- atomic source grounding;
- null detection;
- stand-down preservation;
- disagreement and provenance reveal.

Only a human decision owner can establish:

- whether a lens created an `aha`;
- whether the added question changed their understanding;
- whether the burden was acceptable;
- whether an omitted concern mattered to them;
- whether the revised reasoning helped their actual decision.

Founder participation is therefore unnecessary for the agent-only preflight
but remains unavoidable for a genuine human-usefulness claim.

### 4. Do not enlarge the corpus dishonestly

The fourteen excluded Product Delta cases should remain excluded until exact
paired, review-safe source content exists under the proper authority. A larger
summary-only corpus would create a more impressive case count and weaker
evidence.

### 5. Do not repeat agents merely to manufacture consensus

More fresh reviewers could estimate review variance, but agreement would still
not become truth. The current two pair reads already exposed stable observations
and real disagreement. The next information-bearing step is a causally cleaner
pair or human evidence, not a larger agent vote.

## What changed

Added:

- `engine/system_b/product_delta_paired_screen.py`;
- `engine/system_b/product_delta_paired_screen_review.py`;
- two provider-free CLIs;
- one frozen review contract;
- blind packets and a sealed manifest;
- three frozen fresh-agent review artifacts;
- one deterministic consolidation;
- regression tests and current documentation.

## What did not change

No source conversation, historical experiment, old review, mental-model
Markdown file, compiled graph, relation, compiler input, planner, direct seed,
graph direction, hop depth, active/reserve budget, live prompt, provider route,
runtime, receipt, Decision Trail field, sidecar, Atlas surface, or human field
changed.

The current live Lolla skill was not invoked. Existing checked-in historical
provider outputs were consumed as inputs, but this diagnostic made no new
provider call and incurred no new provider cost.

## Verification

The deterministic validators check:

- 10 qualification cases, 7 paired cases, and 1 stand-down;
- three complete exact pairs, three partial-view pairs, and one duplicate null;
- exact source and answer hashes;
- stable A/B orientation with both orientations represented;
- absence of lineage and old outcomes from blind packets;
- hidden trap expectations;
- exact duplicate equality;
- complete versus partial source coverage;
- no scalar or authority-bearing review field;
- declared fresh-review custody;
- exact case coverage and atomic-move enum shape;
- exact blind-packet hash in the sealed manifest;
- checked-in artifact regeneration;
- disagreement, duplicate-null, stand-down, and lineage-reveal preservation;
- absence of local paths and secret markers.

Final local handoff verification passed `5,107` tests and all `93` subtests.
The suite reported one pre-existing `datetime.utcnow()` deprecation warning;
there were no failures.

## Next decision

No product decision is required to keep this bounded diagnostic. It is
complete.

The next graph-specific evidence decision remains the existing one: whether the
principal human will complete the source-only target and accept, correct, or
reject the proposed reference condition for the frozen consumer-context case.
That human step does not automatically authorize provider execution.
