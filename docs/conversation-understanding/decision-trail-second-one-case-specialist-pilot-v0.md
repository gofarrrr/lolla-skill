# Decision Trail Second One-Case Specialist Pilot v0

Status: second one-case local-private specialist-output pilot
Date: 2026-06-30
Slice: PR100 Decision Trail Second One-Case Specialist Pilot v0

## Purpose

PR100 runs one more local-private specialist-output pilot after PR99 patched
the contracts and packet metadata.

The question is deliberately narrow:

> Do the PR99 fields make the specialist lane more disciplined on a second
> completed run, or do the same overclaim risks remain?

This is not a broad batch. It is not product proof. It is not runtime
integration.

## Case

The PR100 pilot uses:

```text
accept-founding-engineer-role/20260627T073034Z_a7c221
```

This case was already covered by the PR96 metadata-only local-private packet
smoke path, but it was not the PR97 specialist-output pilot case. That makes it
useful for a second one-case check without broadening the lane.

The selected run is a career/family/startup decision. The user is choosing
between:

- a new FAANG staff+ role;
- a Series B founding-engineer role;
- staying where staff scope appears structurally blocked.

The checked-in review does not include raw conversation text, raw revised
answer text, memo text, provider text, private ledgers, local absolute paths,
or local packet output.

## Local Packet Handling

PR100 generated local-private packet outputs under local temp paths only:

- metadata-only packet;
- include-text packet.

Both local packet outputs were deleted after review. The checked-in review
records only a paraphrase-safe summary.

The include-text packet read 16 artifact records:

- 12 records were read as complete text;
- 4 records were truncated;
- the main conversation, revised answer, and memo were complete;
- some structured trace artifacts were still truncated.

Every specialist role had to cite source-scope and truncation impact.

## PR99 Fields Exercised

PR100 exercises all PR99 fields:

- `assistant_influence_source_status`;
- `vanilla_overlap_read`;
- `lost_value_severity_read`;
- `severity_source_status`;
- `source_scope_and_truncation_impact`;
- `downgrade_triggers`;
- `not_ready_reason`.

These fields do not make the reads true. They make the reads harder to
overstate.

## Main Result

The strongest useful signal is not a new positive claim.

The strongest useful signal is that `vanilla_overlap_read` forced a more
conservative interpretation:

```text
net_read_candidate: local_private_specialist_read_partly_useful
```

The revised answer did add useful gates:

- spouse support is necessary but no longer sufficient;
- startup quality and role reality must clear evidence gates;
- family protection becomes operational;
- the FAANG option becomes a designed bridge if the startup fails gates;
- stop/revisit criteria become explicit.

But the vanilla conversation already contained a large part of the action
sequence:

- spouse conversation;
- extension request;
- diligence calls;
- equity review;
- CEO conversation;
- A as fallback if spouse support is weak;
- do not stay by default.

So the pilot should not be read as clean material action change. It is better
read as threshold, evidence-gate, and stop-rule sharpening around an already
partly-present plan.

That is exactly why the PR99 patch mattered. It prevented the second pilot from
over-crediting the revised answer for moves that were partly already in the
vanilla conversation.

## What The Specialists Made Easier To See

The patched specialist shape made these things easier to inspect:

- where the top-level action overlapped with the vanilla answer;
- where the revised answer made a necessary condition non-sufficient;
- where useful friction could become process bloat;
- where lost value exists but severity remains source-limited;
- where assistant influence is visible but not causally judged;
- why fan-in should downgrade to partial usefulness instead of sounding
  verdict-like.

## What Remains Missing

PR100 still cannot answer:

- whether the spouse actually supported the startup path;
- whether the startup passed real diligence;
- whether the FAANG role was a genuine diagnostic bridge;
- whether lost momentum was acceptable;
- whether a human reviewer would call the revised answer materially better,
  partly better, worse, or mostly a disciplined restatement.

The missing parts are messy interpretation and human judgment. Deterministic
code should not invent them.

## Boundary

PR100 did not:

- run `$lolla`;
- invoke the Lolla skill;
- call provider or model APIs;
- mutate archives;
- change runtime behavior;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- add a broad judge;
- add answer-quality scoring;
- create automatic labels;
- authorize agent action;
- add graph DB, memory, embeddings, chunking, or GraphRAG;
- check in local-private packet output.

## Next Slice

The next conservative slice should be a comparison/decision gate, not another
automatic pilot:

```text
PR101 Decision Trail Specialist Pilot Comparison Gate v0
```

PR101 has now compared PR97 and PR100:

- [Decision Trail Specialist Pilot Comparison Gate v0](decision-trail-specialist-pilot-comparison-gate-v0.md)

PR101 decided not to broaden. PR102 has now used the one diversity-targeted
third one-case pilot it allowed:

- [Decision Trail Third One-Case Diversity Pilot v0](decision-trail-third-one-case-diversity-pilot-v0.md)

PR102 selected a deployment-controls case and recommends closing the pilot
phase before any fourth one-case pilot. A closure gate should decide whether
to:

- pause and simplify;
- patch contracts again;
- or prepare a very small multi-case review.

It should not broaden by default. PR100's partial-usefulness result remains a
reason to think before scaling.

## Files

- [`review.json`](../../reviews/codex-assisted/decision-trail-second-one-case-specialist-pilot-v0/review.json)
