# Decision Trail Specialist Pilot Comparison Gate v0

Status: comparison and decision gate
Date: 2026-06-30
Slice: PR101 Decision Trail Specialist Pilot Comparison Gate v0

## Purpose

PR101 compares the two local-private Decision Trail specialist-output pilots
before any third pilot or broader batch.

It asks:

> Did the second pilot make the specialist lane disciplined enough to broaden,
> or should the lane stay narrow?

The answer is narrow and conservative:

```text
Do not run a broad specialist-output batch yet.
Allow at most one more diversity-targeted one-case pilot.
```

This is not product proof, not human validation, not runtime integration, and
not a verdict that Lolla improved either decision.

## Inputs

PR101 reads only checked-in summary artifacts:

- [Decision Trail Local-Private Specialist Output Pilot v0](decision-trail-local-private-specialist-output-pilot-v0.md)
- [`PR97 review.json`](../../reviews/codex-assisted/decision-trail-local-private-specialist-output-pilot-v0/review.json)
- [Decision Trail Specialist Output Pilot Review v0](decision-trail-specialist-output-pilot-review-v0.md)
- [Decision Trail Specialist Contract And Packet Patch v0](decision-trail-specialist-contract-and-packet-patch-v0.md)
- [Decision Trail Second One-Case Specialist Pilot v0](decision-trail-second-one-case-specialist-pilot-v0.md)
- [`PR100 review.json`](../../reviews/codex-assisted/decision-trail-second-one-case-specialist-pilot-v0/review.json)

PR101 does not read local-private packet outputs, raw conversations, raw revised
answers, raw memos, provider text, private ledgers, or local absolute paths.

## Comparison

PR97 was the first one-case pilot. It showed that local-private specialist
reads can make the Decision Trail more concrete than a sparse report shell.
The case was:

```text
ceo-remove-founding-cofounder/20260627T093131Z_59d153
```

The useful signal was real but source-limited: the specialist outputs made
authority transfer, stop conditions, and relationship-cost tension easier to
see. The weakness was also clear: vanilla overlap, lost-value severity,
assistant-influence source status, truncation impact, and fan-in downgrade
rules were not first-class enough.

PR100 was the second one-case pilot. It used the PR99 patched shape on:

```text
accept-founding-engineer-role/20260627T073034Z_a7c221
```

The useful signal was different and healthier: the patched fields made the
read less positive. The `vanilla_overlap_read` field showed material overlap
between the vanilla conversation and the revised answer, so the net read
downgraded to:

```text
local_private_specialist_read_partly_useful
```

That downgrade is the strongest evidence that the specialist lane can preserve
friction instead of only making Lolla look better.

## Gate Decision

PR101 does not approve broadening.

Two one-case pilots are still too thin:

- both are Codex-assisted and unvalidated;
- both are local-private and summarized into checked-in artifacts;
- one pilot used the pre-PR99 contract shape;
- the post-PR99 pilot is only one case;
- there is still no human review;
- there is still no real no-change, noisy, worse, or clearly inconclusive
  local-private specialist-output case;
- both cases are high-agency founder/operator/career decisions.

The lane is useful enough to keep testing, but not mature enough for a broad
batch.

The next slice may be one more one-case pilot only if it is deliberately
different from PR97 and PR100. It should target a different decision family
such as deployment controls, enterprise beta launch, pricing, or another
completed run that is not primarily a founder/cofounder/career identity case.

## What PR101 Makes Clear

PR101 clarifies four things:

- local-private specialist packets are useful because they expose information
  that sparse checked-in-safe reports cannot;
- patched specialist contracts are better than the original PR90 shape because
  they force downgrade pressure;
- vanilla overlap is load-bearing and must remain first-class;
- the lane is still a research/eval scaffold, not a product surface or runtime
  feature.

## What Remains Missing

PR101 cannot answer:

- whether either revised answer was actually better;
- whether the specialist reads are reliable across case types;
- whether the current contracts catch noisy or worse revisions often enough;
- whether humans would agree with any candidate read;
- whether a future agent could safely consume semantic fields beyond routing
  and inspection metadata.

Those are still future evaluation questions.

## Boundary

PR101 did not:

- run `$lolla`;
- invoke the Lolla skill;
- call provider or model APIs;
- generate new specialist outputs;
- read local-private packet content;
- mutate archives;
- change runtime behavior;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- add a broad judge;
- add answer-quality scoring;
- create automatic labels;
- authorize agent action;
- add graph DB, memory, embeddings, chunking, or GraphRAG.

## Next Slice

The next conservative slice, if we continue, should be:

```text
PR102 Decision Trail Third One-Case Diversity Pilot v0
```

PR102 should run at most one more local-private specialist-output pilot using
the PR99/PR100 shape. It should select a different decision family and should
pre-register why that case is a useful contrast.

If PR102 cannot find a safe, diverse completed run, stop. If PR102 produces
another positive or partial read without revealing a new failure shape, stop
and prepare human-review intake or simplify. Do not turn PR102 into a broad
batch by momentum.

## Files

- [`report.json`](../../reviews/codex-assisted/decision-trail-specialist-pilot-comparison-gate-v0/report.json)
