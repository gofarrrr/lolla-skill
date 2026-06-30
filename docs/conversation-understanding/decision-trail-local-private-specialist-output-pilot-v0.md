# Decision Trail Local-Private Specialist Output Pilot v0

Status: tiny local-private specialist-output pilot
Date: 2026-06-30
Slice: PR97 Decision Trail Local-Private Specialist Output Pilot v0

## Purpose

PR97 is the first tiny pilot that fills PR90-shaped specialist outputs from a
PR95 local-private packet.

It answers one narrow question:

> Can bounded specialist reads over local-private packet context expose more
> useful Decision Trail information than the sparse shell while preserving
> uncertainty, source refs, limitations, and non-claims?

The answer from this slice is a cautious yes for one case. It is not enough for
a broad batch, runtime integration, product proof, scoring, automatic labels,
or agent action.

## Scope

PR97 uses one operator-selected completed run:

- `ceo-remove-founding-cofounder/20260627T093131Z_59d153`

The pilot used the PR95 packet builder in local-private include-text mode under
`/tmp`. The private packet output was not checked in. The checked-in review
contains paraphrase-only candidate specialist reads and sanitized source refs.

## Runtime Boundary

PR97 is offline and downstream from the Lolla runtime.

It does not:

- run `$lolla`;
- invoke the Lolla skill;
- call providers or external model APIs;
- mutate archives;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- change runtime behavior;
- score answer quality;
- create automatic labels;
- authorize agent action;
- claim product proof.

## What The Pilot Filled

PR97 fills all four PR90 specialist roles for one case:

- `conversation_shape_reader`
- `likely_action_reader`
- `friction_lost_value_reader`
- `conservative_fan_in_reader`

Each read keeps:

- source refs;
- source status;
- uncertainty;
- evidence strength;
- limitations;
- non-claims;
- lower-claim boundary metadata.

The durable review artifact is:

- [`review.json`](../../reviews/codex-assisted/decision-trail-local-private-specialist-output-pilot-v0/review.json)

## Main Useful Signal

The local-private packet made the Decision Trail interpretation more concrete
than the sparse shell:

- the decision shape can be described as authority transfer versus continued
  reset/cooperation testing;
- the likely action delta can be framed as moving authority first, narrowing
  the transition role, and adding stop conditions;
- lost value remains visible as possible relationship simplicity, trust, and
  momentum cost;
- fan-in can preserve the tension between strong structural delta and
  unresolved stakeholder/value risk.

This is useful because the same fields were only missing or source-limited in
the sparse Decision Trail shell.

## Main Risk

The pilot also shows why the next step must stay small.

The include-text packet is private, large, truncated, and unsafe for commit.
Several fields remain candidate-only:

- whether the vanilla answer already contained the same authority-transfer
  sequence;
- how much assistant influence shaped the user's frame;
- whether moving authority first creates useful friction or avoidable
  relationship damage;
- whether legal, financial, or governance details were outside the packet's
  current interpretive scope.

Clean specialist outputs could make the system look more certain than it is.
That is the main overtrust risk.

## Product Read

PR97 supports the specialist lane as a next-step research path. It does not
support broad automation.

The right interpretation is:

> Local-private specialist reads can add useful Decision Trail content, but the
> output must remain provisional and source-limited until human review or a
> stronger validation process exists.

## Recommended Next Slice

PR98 has now reviewed this pilot:

- [Decision Trail Specialist Output Pilot Review v0](decision-trail-specialist-output-pilot-review-v0.md)

PR98 decided not to broaden yet and recommended PR99. PR99 has now applied
that patch:

```text
Decision Trail Specialist Contract And Packet Patch v0
```

See:

- [Decision Trail Specialist Contract And Packet Patch v0](decision-trail-specialist-contract-and-packet-patch-v0.md)

PR99 patches the contracts and packet metadata before a second one-case pilot.
The patch areas are:

- vanilla-overlap read;
- lost-value severity read;
- assistant-influence source status;
- source-scope and truncation impact;
- fan-in downgrade triggers;
- local-private packet retention/deletion status.

PR99 did not run another specialist pilot, add runtime integration, measure
answer quality, add automatic labels, authorize agent action, add graph/memory
work, or use product-proof language.

PR100 has now run the second one-case pilot using the patched shape:

- [Decision Trail Second One-Case Specialist Pilot v0](decision-trail-second-one-case-specialist-pilot-v0.md)

PR101 has now compared PR97 and PR100:

- [Decision Trail Specialist Pilot Comparison Gate v0](decision-trail-specialist-pilot-comparison-gate-v0.md)

It decides broad specialist-output batches are not ready and allows at most one
diversity-targeted third one-case pilot before stopping or simplifying.
