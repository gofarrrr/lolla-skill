# Lolla agent-only graph-variance calibration result

Status: completed bounded Product Delta diagnostic; frozen question not evaluable

Date: 2026-07-23

Decision: preserve the three valid first-terminal generation outputs, the one
unrecoverable first-terminal failure, both blind reviews, and every available
pair-level observation. Do not replace the failed draw, attribute the observed
answer differences to the graph, expand traversal, or change the live graph,
planner, compiler, runtime, skill, or interface.

Controlling machine result:
[`consolidated-diagnostic.json`](../../research/agent-only-graph-variance-calibration-2026-07-23/consolidated-diagnostic.json)

Frozen prospective contract:
[`lolla-agent-only-graph-variance-calibration-contract-v1.json`](../evals/lolla-agent-only-graph-variance-calibration-contract-v1.json)

Execution plan:
[`lolla-agent-only-graph-variance-calibration-2026-07-23.md`](../../plans/lolla-agent-only-graph-variance-calibration-2026-07-23.md)

## Plain-language result

Imagine asking whether adding a new set of lenses changes an answer. If the
same setup gives almost the same answer every time, then a repeated difference
between “without the extra lenses” and “with the extra lenses” is interesting.
If the same setup gives substantially different answers on its own, then one
cross-setup difference does not tell us what caused it.

This calibration found the second situation:

- the two usable fresh answers from the same graph condition had a material
  difference according to both blind reviewers;
- the usable direct-versus-graph pairs also had differences, but the reviewers
  disagreed on one historical pair;
- one fresh direct-condition draw ended without a recoverable terminal answer;
- because that draw was not replaced, one within-direct pair and one
  direct-versus-graph pair could not be reviewed.

Therefore the frozen question is **not evaluable**. The available evidence
already shows that ordinary run-to-run variation is not negligible. It does
not show that the graph caused a stable difference, that graph pressure was
better, or that the graph is useless.

## What was actually tested

The test reused one checked-in synthetic retailer-pilot conversation and the
exact provider-neutral request packets from the completed graph-increment
rehearsal:

- direct condition: the same two direct candidates;
- graph condition: the same direct candidates plus the current outgoing
  one-hop graph increment;
- no new retrieval, traversal, ranking, prompt, schema, generation-setting, or
  portfolio-policy decision;
- two prospective new draws per condition;
- the historical first draw from each condition retained as draw zero;
- two within-condition comparisons and three cross-condition comparisons;
- two isolated blind reviewers;
- the existing ten qualification traps, exact-duplicate null, legitimate
  stand-down, and atomic-move review grammar.

The four generation attempts and two blind reviews were Codex development
contexts, not exact standalone provider executions of F2 or F3. Ambient
platform context remained present. The repository operator cannot identify
the exact platform route, token accounting, or economic cost. These contexts
must not be described as no-AI or economically free.

Repository provider API calls were zero. Repository provider API cost was
`$0.00`.

## First-terminal generation custody

| Neutral sample | Frozen condition after unblinding | First-terminal state | Candidate custody |
|---|---|---:|---|
| `sample-cinder` | direct, draw 1 | complete | both direct candidates dispositioned |
| `sample-moss` | direct, draw 2 | failed: terminal result unavailable | no answer reconstructed or imputed |
| `sample-slate` | direct plus current one-hop, draw 1 | complete | all five active candidates dispositioned |
| `sample-linen` | direct plus current one-hop, draw 2 | complete | all five active candidates dispositioned |

The `sample-moss` process emitted execution events but ended without a
recoverable first-terminal assistant payload in either the execution session
or persistent session storage. The contract prohibited retry, fallback,
healing, or replacement. The repository therefore records a terminal failure
instead of a synthetic answer.

All three completed JSON outputs pass the inherited response shape, length
bounds, exact candidate-identity check, and existing deterministic pressure
compiler. Those checks prove accountable shape and custody. They do not
validate the semantic correctness of a disposition or answer.

## Blind pair result

Lineage remained hidden until both reviews were frozen.

| Blind case | Unblinded role | Availability | Primary read | Skeptical read |
|---|---|---|---|---|
| `calibration-pair-01` | within direct, fresh | not evaluable | not evaluable | not evaluable |
| `calibration-pair-02` | within graph, fresh | available | material difference present | material difference present |
| `calibration-pair-03` | direct versus graph, historical | available | material difference present | uncertain |
| `calibration-pair-04` | direct versus graph, fresh draw 1 | available | material difference present | material difference present |
| `calibration-pair-05` | direct versus graph, fresh draw 2 | not evaluable | not evaluable | not evaluable |

The available reads stay attributable to each reviewer. “Present” is not a
vote for an arm, a quality judgment, or proof that a difference came from the
graph.

The controls behaved as intended:

- both reviewers marked the exact-duplicate null as having no material
  decision difference;
- both reviewers supported the legitimate stand-down;
- qualification-case dispositions remained case-specific and were not
  converted into a calibration score.

These controls make the reviews more inspectable. They do not make either
reviewer ground truth.

## What varied inside the graph condition

Both complete graph-condition answers accounted for all five active
candidates, but they did not use them identically:

| Candidate | Graph draw 1 | Graph draw 2 |
|---|---|---|
| signaling | apply | apply |
| social proof | apply | apply |
| confirmation bias | apply | apply |
| incentives | reject | park |
| abstraction | park | apply |

The historical graph draw had applied all five. This is useful process
evidence: graph-derived candidates survived into reconsideration and the
reasoner exercised apply/reject/park rather than mechanically accepting every
lens. It also shows why a single draw is inadequate. Candidate presence is
deterministic under the frozen packet; interpretation and answer composition
remain probabilistic.

The graph did not certify relevance. The differing dispositions do not prove
that one draw reasoned better or worse.

## Why the frozen question is not evaluable

The prospective question was whether cross-condition differences were more
consistent than ordinary differences between fresh outputs from the same
condition.

That comparison requires:

1. a within-direct fresh pair;
2. a within-graph fresh pair;
3. all three predeclared cross-condition pairs.

The failed direct draw removes item 1 and one of the three cross-condition
pairs. Replacing it would answer a different, post-failure question and would
break the no-retry contract.

Even before considering that missingness, the complete within-graph pair was
materially different for both reviewers. This means the observed
within-condition variation is large enough that the original single
direct-versus-graph difference cannot responsibly be treated as graph
attribution.

The correct result state is therefore `not_evaluable`, not positive, negative,
or mixed graph value.

## What this changes

It changes our confidence in the earlier automated rehearsal:

- the earlier result remains real evidence that a fixed graph increment
  survived custody and coincided with an inspectable answer difference;
- it is no longer reasonable to treat that single observed difference as
  stable merely because two blind reviewers saw it;
- same-condition variation must be measured in any future graph comparison;
- automation must preserve terminal failures as first-class outcomes.

It does not change:

- the canonical 222-model source substrate;
- the 1,358 authored directed relations;
- compiler inputs or published graph artifacts;
- the current outgoing one-hop policy;
- the constitutional graph-survival rule;
- the apply/reject/park contract;
- the live skill;
- the Atlas;
- the Decision Trail or Decision Work sidecar;
- the prohibition on probabilistic pre-deletion of bounded candidates.

## Automation lessons

### 1. The evaluator can run without founder labeling

The frozen packets, generation contexts, deterministic compiler validation,
neutral pair construction, blind reviews, unblinding, and consolidation all
ran without founder participation. This demonstrates an automated internal
diagnostic path.

It does not replace principal-human review or establish human usefulness.

### 2. Terminal capture is part of the experiment

The missing draw was caused by loss of a recoverable terminal payload, not by
a semantic rejection. Later contexts used a restart-safe first-message capture
and completed. Future contracts should preserve terminal payloads directly at
the context boundary from the start.

That operational repair cannot be applied retroactively to `sample-moss`
without becoming a replacement attempt.

### 3. Failure must affect the interpretation

The automation did not reduce the denominator, silently compare only the
successful cases, or fill the missing arm with another model response. The
failure made two comparisons unavailable and forced the overall calibration to
`not_evaluable`.

This is desired receipt behavior: the process record tells the truth about
what happened instead of protecting a clean narrative.

## What this does not show

This result is not:

- principal-human review;
- a source-first human target;
- provider execution;
- exact execution of a standalone F2 or F3 envelope;
- a provider or model comparison;
- a statistically powered variance estimate;
- proof that the graph relations are correct or relevant;
- graph causation, graph value, or graph usefulness evidence;
- proof that any answer is better, safer, clearer, or more useful;
- expected model behavior;
- completion of the consumer-context experiment;
- permission to add incoming edges, a second hop, community search,
  embeddings, or a graph database;
- permission to change the portfolio, planner, compiler, runtime, skill,
  Atlas, Observatory, Decision Work, or user interface.

## Next opportunity

Do not expand or “improve” the graph in response to this result.

The smallest scientifically coherent continuation would be a new,
prospectively frozen calibration that:

- uses restart-safe terminal capture for every draw;
- retains within-condition replication as a first-class requirement;
- separates transport failure from semantic invalidity;
- has enough complete draws to preserve both within-condition baselines;
- preferably adds a second case only after an exact comparable current
  direct/direct-plus-graph envelope exists;
- keeps every pair-level and reviewer-level observation non-scalar.

That is a new experiment and is not authorized by this completed contract.
Before it begins, its case set, context count, failure policy, comparison plan,
and scope ceiling must be frozen. Wider traversal is not the next move.

The current operational decision is:

`preserve_not_evaluable_variance_result_and_do_not_attribute_or_expand_graph`

## Evidence inventory

Generation and execution custody:

- [`generation-packets.json`](../../research/agent-only-graph-variance-calibration-2026-07-23/generation-packets.json)
- [`sealed-manifest.json`](../../research/agent-only-graph-variance-calibration-2026-07-23/sealed-manifest.json)
- [`terminal-output-sample-cinder.json`](../../research/agent-only-graph-variance-calibration-2026-07-23/terminal-output-sample-cinder.json)
- [`terminal-failure-sample-moss.json`](../../research/agent-only-graph-variance-calibration-2026-07-23/terminal-failure-sample-moss.json)
- [`terminal-output-sample-slate.json`](../../research/agent-only-graph-variance-calibration-2026-07-23/terminal-output-sample-slate.json)
- [`terminal-output-sample-linen.json`](../../research/agent-only-graph-variance-calibration-2026-07-23/terminal-output-sample-linen.json)
- [`blind-review-packet.json`](../../research/agent-only-graph-variance-calibration-2026-07-23/blind-review-packet.json)
- [`execution-sealed-manifest.json`](../../research/agent-only-graph-variance-calibration-2026-07-23/execution-sealed-manifest.json)

Frozen blind reviews:

- [`pair-review-primary.json`](../../reviews/codex-assisted/agent-only-graph-variance-calibration-v1/pair-review-primary.json)
- [`pair-review-skeptical.json`](../../reviews/codex-assisted/agent-only-graph-variance-calibration-v1/pair-review-skeptical.json)

Deterministic machinery:

- [`product_delta_graph_variance_calibration_result.py`](../../engine/system_b/product_delta_graph_variance_calibration_result.py)
- [`build_product_delta_graph_variance_calibration_result.py`](../../scripts/evals/build_product_delta_graph_variance_calibration_result.py)
- [`test_product_delta_graph_variance_calibration_result.py`](../../tests/test_product_delta_graph_variance_calibration_result.py)
