# Lolla Decision Trail Stage Lineage

Date: 2026-07-22
Status: current decision-lineage correction; no evidence stage authorized
Provider calls: 0
Runtime, semantic-reader, graph-policy, and sidecar changes: none

## Outcome in plain language

Two different pieces of work have both been described near the words
“Decision Trail” and “next stage.” They must not be treated as one continuous
program.

1. In June, Lolla tried to make richer sense of three completed conversations.
   Codex-assisted specialist reads were useful enough to expose possible
   meaning, but they were not human validation. The program stopped after the
   third case. PR104 prepared a principal-human review packet and left every
   human correction field blank. Its current state is still **paused until
   human review capacity returns**.
2. In July, the Constitution restart roadmap proposed a much narrower Stage 1.
   It would ask whether a cold reviewer can tell which fields are source
   custody, provisional interpretation, missing, human-review dependent, or
   non-authorizing by reading existing checked-in-safe artifacts. That review
   is **eligible to be authorized**, but it is not authorized or started.

The July review did not fail, because it never ran. It also did not pass. Most
importantly, it does not supersede the June pause and cannot prove that Lolla
understands conversations correctly. It could produce a clean
interface-truthfulness result while the semantic interpretation problem
remains open.

## Exact lineage

```text
June specialist-output program
  PR97 one local-private case
  PR99 contract repair
  PR100 second case
  PR101 comparison gate
  PR102 third diversity case
  PR103 close the one-case program
  PR104 create human-review intake
        -> 3 cases
        -> candidate reads only
        -> all human correction fields blank
        -> pause until principal-human review capacity returns

July Constitution restart roadmap
  Stage 0   map architecture and evidence
  Stage 0.5 make the map clone-legible
  Stage 0.6 report long-conversation source coverage truthfully
  proposed Stage 1
        -> checked-in-safe labeling/truthfulness review
        -> no private sources
        -> no new semantic interpretation
        -> no provider
        -> unauthorized and unstarted
```

## What actually stopped in June

[PR103's closure gate](decision-trail-specialist-pilot-phase-closure-gate-v0.md)
states that three one-case Codex-assisted pilots had reached the limit of what
additional non-human pilots could show. It prohibited a fourth case and a
broad batch by momentum. The next meaningful evidence had to come from a
principal human reviewer or the program had to pause.

[PR104's intake document](decision-trail-human-review-intake-packet-v0.md) and
its [machine packet](../../reviews/human/decision-trail-human-review-intake-packet-v0/intake.json)
preserve that stop point exactly:

- `intake_mode` is `future_human_review_queue_not_filled`;
- `human_fields_filled` is `false` at packet and case level;
- exactly three prior candidate reads are present;
- raw private content is absent;
- no new model output or automatic label was created;
- the recommended status is
  `pause_until_human_review_capacity_returns`.

No later checked-in artifact fills those human fields. Therefore the repository
has no completed human semantic review of the three candidate reads.

## What July Stage 1 can and cannot answer

The proposed Stage 1 in the
[post-Stage-0 roadmap](../../plans/lolla-post-stage0-addendum-restart-roadmap-2026-07-15.md)
can answer a useful but smaller question:

> Does the existing completed-run presentation make its authority and
> missingness boundaries understandable?

It can expose a label that looks more authoritative than its source status. It
can test whether a reviewer notices a partial extraction view, an unavailable
semantic field, or the fact that a receipt does not authorize action.

It cannot answer:

- whether a candidate interpretation fairly represents a conversation;
- whether the system preserved changes of mind, adoption, influence, values,
  option lifecycle, unresolved matters, or lost value;
- whether graph-selected pressure was semantically relevant;
- whether the revised answer was better or useful;
- whether Decision Work has a trustworthy arbitrary-run meaning supplier;
- whether the June specialist program should restart.

Passing July Stage 1 would mean “the interface told the truth about what it
has.” It would not mean “the system understood the conversation.”

## Relationship to the graph

The graph and the Decision Trail solve different problems:

```text
conversation interpretation
  probabilistic, provisional
  supplies candidate meaning
             |
             v
mental-model graph
  deterministic identity and traversal
  introduces bounded, provenance-bearing pressure
             |
             v
reconsidering reasoner
  may apply, reject, or park
             |
             v
receipt / Decision Trail / sidecars
  preserve what happened and what remains missing
```

The graph cannot repair an incorrect semantic starting point by traversing
more edges. Incoming references, two-hop paths, global search, community
detection, or more receipt fields would increase machinery without proving
that the conversation was understood. Conversely, a truthful receipt can
prove custody and process even when the semantic read is unavailable.

## Current product decision

No evidence stage starts automatically. The present choices must remain
separate:

- **Pressure now:** retain the live four-lane pressure core and truthful
  mechanical receipt as the primary experimental product. Test the semantic
  conversation-to-graph bridge and human usefulness separately before changing
  graph scope.
- **Understand later:** if longitudinal understanding is essential, resume at
  the PR104 human-review stop point. A principal human must correct, reject, or
  mark unavailable the three candidate reads. Do not substitute another AI
  reader, the retired R4 architecture, or guessed private context.
- **Checked-in-safe truthfulness:** authorize July Stage 1 only if its narrow
  interface question is worth answering now. Record its result separately; it
  neither resumes nor closes the June semantic program.

No sidecar automation, resolver, queue, graph expansion, private-source read,
provider call, or runtime change is justified merely by publishing this
lineage.

## Nonclaims

- The June candidate reads are not declared wrong; they are unvalidated.
- The July Stage 1 proposal is not declared useless; it is narrower than the
  unresolved semantic question.
- A blank human packet is not evidence of failure or success.
- This correction does not authorize the founder or an agent to fill human
  fields without source-first human review.
- This correction does not change graph bytes, traversal, active pressure,
  receipts, Decision Work, Observatory, Atlas, or the live skill.
