# Decision Work Brief Draft Pilot v0

Status: PR116 Codex-assisted provisional draft pilot
Date: 2026-07-01
Schema: `lolla.decision_work_brief_draft_pilot.v0`

## Purpose

PR116 is the first tiny checked-in-safe pilot that drafts a provisional
Decision Work Brief from PR115 packet output.

It asks one narrow question:

> Can the Decision Work Brief shape communicate what the decision process made
> visible or actionable, while keeping uncertainty, custody, and non-claims
> explicit?

The answer from this slice is a cautious yes for one case. The pilot is not a
renderer, not a runtime integration, not product proof, not human validation,
not answer-quality measurement, and not agent action authorization.

## Scope

PR116 uses one completed run:

- `ceo-remove-founding-cofounder/20260627T093131Z_59d153`

A PR115 metadata-only packet was generated locally for this run. The packet was
used as bounded source and custody input, but it was not checked in. No
local-private include-text packet was used for the checked-in draft.

The durable artifact is:

- [`review.json`](../../reviews/codex-assisted/decision-work-brief-draft-pilot-v0/review.json)

The embedded draft brief conforms to:

- [Decision Work Brief schema v0](decision-work-brief-v0.json)

## Relationship To PR114 And PR115

PR114 defined the user-facing Decision Work Brief contract:

```text
lolla.decision_work_brief.v0
```

PR115 defined the deterministic packet-preparation contract:

```text
lolla.decision_work_brief_packets.v0
```

PR116 uses those layers in order:

```text
Completed Lolla run artifacts
  -> PR115 metadata-only packet
  -> Codex-assisted provisional interpretation
  -> embedded PR114-shaped Decision Work Brief draft
```

The packet tells the reviewer what sources exist, what is redacted, what is
private, and what the future brief sections must answer. The draft brief tells
the decision story only where the safe source surface can support a provisional
read.

## Runtime Boundary

PR116 is offline and downstream from the Lolla runtime.

It does not:

- run `$lolla`;
- invoke the Lolla skill;
- call providers or external model APIs from repo code;
- mutate archives;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- change runtime behavior;
- add model-call code;
- create a Markdown renderer;
- create a board or customer demo;
- run a broad batch;
- measure answer quality;
- create automatic labels;
- authorize agent action;
- claim product proof.

## What The Draft Includes

The checked-in review JSON includes:

- `schema_version: lolla.decision_work_brief_draft_pilot.v0`
- one source packet summary for a PR115 metadata-only packet;
- conservative custody flags;
- one embedded `lolla.decision_work_brief.v0` object;
- all eight required Decision Work Brief sections;
- explicit non-claims;
- human follow-up questions;
- an action-consequence read;
- uncertainty and missingness notes;
- a lost-value or possible-overcorrection note.

The embedded brief sections are:

- `decision`
- `starting_direction`
- `what_lolla_pressed_on`
- `what_changed`
- `what_this_means_for_action`
- `what_still_might_be_wrong`
- `what_was_not_proven`
- `evidence_receipt`

Every section preserves the PR114 shared section shape:

- `status`
- `source_status`
- `source_refs`
- `interpreted_by`
- `human_validated`
- `uncertainty`
- `value`
- `empty_meaning`

## What The Draft Says, Provisionally

For the one case, the draft reads the decision story this way:

- the decision appears to concern whether a CEO should remove a founding
  cofounder from operating product leadership while preserving transition,
  customer continuity, and team clarity;
- the likely starting direction may have left more room for a reset or
  cooperation test before fully moving authority;
- Lolla appears to have pressed on authority ambiguity, stop conditions, and
  whether a polished hybrid role would obscure the delivery problem;
- the provisional change is to move authority first, narrow the transition
  role, and set escalation triggers before the conversation;
- the action consequence is clearer precommitment before the CEO-cofounder
  conversation;
- the strongest uncertainty is whether the raw/private context would change
  the starting-direction read, lost-value severity, or relationship-risk
  interpretation.

This is a decision story draft, not a receipt inventory. It is also not a
claim that the decision, the advice, or the draft is correct.

## Source And Privacy Handling

The checked-in artifact does not include:

- raw conversation text;
- raw revised answer text;
- raw memo text;
- live transcript text;
- provider text;
- private ledgers;
- local absolute paths;
- secrets.

The locally generated PR115 metadata-only packet recorded structured artifact
availability and redaction/private status. It did not contribute private text
to the checked-in PR116 artifact.

The draft also cites existing checked-in safe Decision Trail specialist review
artifacts as sanitized support:

- [Decision Trail Local-Private Specialist Output Pilot v0](decision-trail-local-private-specialist-output-pilot-v0.md)
- [Decision Trail Specialist Output Pilot Review v0](decision-trail-specialist-output-pilot-review-v0.md)

## Main Useful Signal

The pilot suggests the Decision Work Brief shape can communicate decision
consequence more directly than the receipt/debug-summary layer.

In this case, the user-facing story is not merely that artifacts exist. It is:

```text
move authority before more cooperation testing;
narrow the cofounder's transition role;
set stop conditions before the conversation;
keep relationship and governance uncertainty visible.
```

That is closer to the product target: "what did this process make me see or do
differently?"

## Main Risk

The draft can sound more settled than the evidence allows.

The starting direction, user intent, lost-value severity, and legal or
governance constraints depend on source surfaces that are not checked in here.
The draft therefore keeps high uncertainty in the starting-direction and
what-still-might-be-wrong sections, and it carries human follow-up questions
instead of treating the Codex-assisted read as settled.

The important failure mode is overclaiming: a clean brief may feel more
trustworthy than its source boundary permits.

## Product Read

PR116 supported trying a tiny renderer next, with caution. PR117 has now added
that renderer, and PR118 has reviewed the rendered result.

The right interpretation is:

> A provisional Decision Work Brief can be more useful than a receipt inventory
> when it preserves action consequence, uncertainty, source refs, and non-claims
> together.

The wrong interpretation is:

> The checked-in draft proves Lolla improved the decision.

It does not.

## Follow-On Slices

PR117 is now complete:

```text
PR117 Decision Work Brief Markdown Renderer v0
```

It renders the PR114 brief shape from checked-in-safe draft data while keeping
source status, uncertainty, custody flags, and non-claims visible.

PR118 is now complete:

```text
PR118 Decision Work Brief Usefulness Review And Delivery Gate v0
```

It decided the rendered brief is promising but still thin, and chose
`proceed_to_tiny_second_case`.

Recommended next slice:

```text
PR119 Decision Work Brief Second Tiny Case Pilot v0
```

PR119 should not broaden to many cases, hide uncertainty, change the live
runtime, or claim product proof.

## Non-Claims

PR116 is not:

- human review;
- ground truth;
- product proof;
- answer-quality measurement;
- automatic labeling;
- runtime integration;
- a broad judge;
- evidence that clean artifacts mean good advice;
- agent action authorization.
