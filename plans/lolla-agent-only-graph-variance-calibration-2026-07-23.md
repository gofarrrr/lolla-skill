# Agent-only graph variance calibration plan

Date: 2026-07-23

Status: prospective provider-free contract frozen before new semantic outputs;
execute only after the contract PR is merged

Owner: existing offline Product Delta evaluation

Repository provider/API calls authorized: 0

Graph, planner, compiler, runtime, skill, interface, and traversal changes
authorized: none

## Plain-language purpose

The first automated graph rehearsal found a real difference between two
answers, but it could not tell us why.

One answer received the direct lenses. One received the same direct lenses plus
the current graph increment. However, each condition was run only once. Two
fresh reasoners can write different answers even when they receive exactly the
same material. Therefore:

```text
observed difference
        =
possible graph-associated difference
        +
ordinary fresh-reasoner variation
```

This calibration holds the source, prompts, schemas, candidate portfolios,
current one-hop paths, and generation wrapper fixed. It reruns each exact
condition twice. Blind reviewers can then compare:

- fresh direct versus fresh direct;
- fresh graph versus fresh graph;
- the historical direct versus historical graph pair;
- fresh direct versus fresh graph for replicate 1;
- fresh direct versus fresh graph for replicate 2.

The purpose is not to find a winner. It is to learn whether the cross-condition
differences look more repeatable than the differences that occur when the
condition did not change.

## Founder decision and authority

The founder asked the repository to automate the test without founder
participation. That authorizes the six exact Codex collaboration-agent contexts
declared here:

- four isolated generation contexts;
- two isolated blind-review contexts.

It does not authorize:

- a repository provider/API call;
- reporting the Codex platform route, token use, or economic cost as known or
  zero;
- a retry, healed response, fallback, replacement, or premium route;
- principal-human labels or filling the paused human target with agent output;
- graph traversal, relation, ranking, portfolio, planner, or compiler changes;
- live-skill, runtime, Decision Work, Observatory, Atlas, or interface changes;
- a score, winner, vote, significance test, causal claim, or usefulness claim.

## Falsifiable question

> When the exact frozen direct-only and direct-plus-current-one-hop request
> packets are each given to two more isolated fresh Codex contexts, are the
> blind source-reviewable differences across conditions more consistent than
> the ordinary differences between two fresh outputs from the same condition?

Allowed answers include:

- cross-condition differences appear more consistent than the two observed
  within-condition differences;
- the cross-condition differences are not distinguishable from observed
  within-condition variation;
- reviewers disagree or the pattern is mixed;
- one or more first-terminal results fail, so the calibration is not
  evaluable.

None of those answers changes the graph.

## Why there is one case, not several

The repository contains many historical three-arm bundles, but they are not
interchangeable with the current case:

- most later transfer cases deterministically stood down;
- the active older bundles belong to earlier simulated-reliability calibration
  machinery;
- no second checked-in case currently has both exact current F2 and F3 request
  envelopes.

Mixing those artifacts into this run would change the pipeline at the same time
as the case. That would create another confound instead of removing the one we
already found.

The smallest honest next step is therefore within-case variance calibration.
A later multi-case replication may be frozen only after this result is
consolidated and only after comparable current direct/graph envelopes exist.

## Reused owners

This is a prospective extension of the completed graph-increment rehearsal, not
a parallel graph or evaluation product.

| Responsibility | Reused owner |
| --- | --- |
| Complete authoritative source | frozen retailer rehearsal source |
| Direct and graph candidate allocation | frozen F2/F3 provider-neutral previews |
| Current outgoing one-hop graph increment | frozen graph-increment rehearsal |
| Response schema and generation instruction | exact predecessor packets |
| Candidate accounting and strict compilation | existing pressure compiler |
| Atomic answer comparison | Product Delta paired-screen contract |
| Qualification, duplicate-null, and stand-down controls | existing paired screen |
| Historical draw zero | first terminal outputs from the completed rehearsal |
| Source-first reference | completed frozen agent-proxy reads; not rerun or promoted |

The only new deterministic code packages, hashes, aliases, validates, and later
consolidates these existing artifacts.

## Frozen sample design

The completed rehearsal contributes one immutable historical draw per
condition:

```text
D0 = historical direct-only output
G0 = historical direct + current-one-hop output
```

Four new isolated samples are predeclared:

```text
D1, D2 = two new exact direct-only reruns
G1, G2 = two new exact direct + current-one-hop reruns
```

The public generation artifact uses only neutral sample aliases. Their
condition and replicate numbers live in a separate sealed manifest. Each
generation context receives one packet and cannot receive sibling packets,
outputs, reviews, source-proxy reads, or the sealed lineage map.

The embedded semantic request remains unredacted because the reasoner must see
the actual lenses and graph paths. Neutral aliases hide experiment lineage;
they do not pretend the reasoning material itself is invisible.

## Five blind comparisons

After all four first-terminal outputs validate, deterministic code will build
five neutrally named pairs:

| Sealed role | Comparison |
| --- | --- |
| within direct | D1 versus D2 |
| within graph | G1 versus G2 |
| historical cross-condition | D0 versus G0 |
| fresh cross-condition 1 | D1 versus G1 |
| fresh cross-condition 2 | D2 versus G2 |

Arm orientation will be deterministic and separately sealed for every pair.
Reviewers receive the complete source, answer text, the existing qualification
cases, exact duplicate null, legitimate stand-down, and non-scalar atomic
review contract. They do not receive pair roles, condition lineage, candidate
origins, candidate-disposition ledgers, source-proxy reads, or the other
reviewer's work before both reviews freeze.

Reviewers record atomic reasoning moves and answer-level preservation, loss,
unsupported content, burden, and uncertainty. They do not score or choose an
answer.

## Deterministic consolidation

Only after both reviews are frozen may deterministic code reveal:

- the sample-to-condition map;
- each pair's within-condition or cross-condition role;
- exact source, request, schema, output, review, and predecessor hashes;
- compiler and exact-candidate-accounting receipts;
- every reviewer observation side by side;
- whether each reviewer marked each pair's material difference as present,
  absent, or uncertain;
- bounded qualitative recurrence and disagreement.

The consolidation may describe one of the contract's four interpretation
states, but it may not compute a scalar, statistical significance, answer
ranking, majority vote, or automatic graph decision.

## Execution order

1. Publish and merge this plan, machine contract, deterministic packet builder,
   generated pre-output packets, sealed manifest, documentation updates, and
   tests.
2. Start four isolated fresh generation contexts from the four checked-in
   neutral packets. Preserve each first terminal result without retry or
   repair.
3. Validate every result through the inherited schema and existing pressure
   compiler. Stop the failed sample if exact candidate custody or high-stakes
   factual safety fails.
4. Build the five-pair blind packet and its separate execution manifest.
5. Start two isolated fresh blind reviewers. Preserve both first terminal
   reviews without retry or correction.
6. Deterministically unblind and consolidate without scores, winners, votes, or
   semantic arbitration.
7. Publish the terminal artifacts and bounded result in a second PR. Run the
   focused and full repository verification suites before merge.

## Stop rules

Stop before or at:

- any drift in a locked predecessor input;
- any change to inherited messages, schema, wrapper, or generation settings;
- any allocation other than exactly two new samples per condition;
- generation-context exposure to a sibling packet, output, review, or lineage;
- the first terminal failure of each sample, without replacement;
- invented high-stakes facts or causal assertions;
- reviewer exposure to lineage, pair role, candidate origin, or sibling review
  before review freeze;
- collapsing pair observations into a score, significance claim, vote, or
  winner;
- calling unavailable platform cost, tokens, or route zero;
- a graph-causation, graph-relevance, expected-model-behavior, answer-quality,
  human-usefulness, or runtime claim;
- any provider call, private archive read, graph/planner/compiler/runtime/skill
  change, or interface work.

## Decision after the result

Do not expand traversal merely because the run completes.

- If cross-condition moves repeat while within-condition pairs remain
  materially closer, the next eligible graph experiment is a separately frozen
  multi-case replication using comparable current envelopes.
- If within-condition variation is similar to or larger than cross-condition
  variation, do not attribute the first result to the graph. Improve the
  replication design or stand down.
- If burden repeats specifically across graph-condition draws, inspect the
  current exact one-hop paths before considering any expansion.
- If reviewers disagree, preserve the disagreement and do not vote.
- If a sample or review fails, preserve the failure and do not replace it.

Incoming edges, a second hop, community search, embeddings, graph databases,
portfolio-policy changes, and interface work remain outside this plan.
