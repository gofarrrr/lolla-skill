# Decision Work Brief Human Review Pilot Scaffold v0

Status: PR151 human-review pilot scaffold

Date: 2026-07-01

Review schema: `lolla.decision_work_brief_human_review_pilot_scaffold.v0`

Response template schema:
`lolla.decision_work_brief_human_review_response_template.v0`

## Purpose

PR151 prepares the materials for a future human-review pilot over the three
builder-generated enriched Decision Work Brief examples.

This is not completed human review. It is a runnable scaffold: reviewer
instructions, target artifacts, a blank response template, stop conditions, and
conservative non-claims.

## What The Decision Work Brief Is

The Decision Work Brief is an offline artifact over completed Lolla runs. It is
meant to help a reader understand the decision work behind an AI-assisted
answer:

- what decision was being made;
- what the process pressed on;
- what changed for action;
- what remains uncertain;
- what the final answer does not prove;
- what evidence and limits travel with the output.

The enriched section, `What the interpretation adds`, is a narrow offline
addition from an existing provisional interpretation read. It should clarify
what appears to have been sharpened, what may already have been present, and
what remains source-limited. It must not prove that the advice is good.

## What Reviewers Should Judge

For each case, a human reviewer should answer whether the enriched brief is:

- useful to a busy decision-maker;
- clear about the action consequence;
- explicit about uncertainty and source limits;
- careful about private-context gaps;
- not overtrust-inducing;
- not too operationally decisive;
- safe enough for more review, internal evidence use, or user-surface testing.

In short, the reviewer should judge usefulness, clarity, caveats, source limits,
and overtrust risk, not answer correctness.

Reviewers must not infer that clean artifacts prove good advice, that Lolla
improved the decision, that a human already validated the interpretation, or
that an agent may act.

## Pilot Packet Scope

The pilot covers exactly three cases.

### Launch Public Enterprise Beta

- Enriched brief:
  [Decision Work Brief Builder-Enriched Launch Beta](decision-work-brief-builder-enriched-launch-public-enterprise-beta-v0.md)
- Original rendered brief:
  [Decision Work Brief Rendered Launch Beta](decision-work-brief-rendered-launch-public-enterprise-beta-v0.md)
- Interpretation read:
  `reviews/codex-assisted/decision-work-conversation-interpretation-tiny-offline-read-v0/read.json`
- Source review:
  `reviews/codex-assisted/decision-work-brief-enrichment-builder-rule-patch-review-v0/review.json`
- Highest-risk uncertainty: the brief may make the paid private-pilot path
  feel more validated than the compressed checked-in sources can prove.

### Deploy Assisted Intake Routing

- Enriched brief:
  [Decision Work Brief Builder-Enriched Intake Routing](decision-work-brief-builder-enriched-deploy-assisted-intake-routing-v0.md)
- Original rendered brief:
  [Decision Work Brief Rendered Intake Routing](decision-work-brief-rendered-deploy-assisted-intake-routing-v0.md)
- Interpretation read:
  `reviews/codex-assisted/decision-work-conversation-interpretation-second-tiny-offline-read-v0/read.json`
- Source review:
  `reviews/codex-assisted/decision-work-brief-enrichment-builder-rule-patch-review-v0/review.json`
- Highest-risk uncertainty: deployment-control language can sound safe or
  validated unless patient-risk, compliance, and pause-trigger caveats stay
  visible.

### CEO Remove Founding Cofounder

- Enriched brief:
  [Decision Work Brief Builder-Enriched CEO Remove Founding Cofounder](decision-work-brief-builder-enriched-ceo-remove-founding-cofounder-v0.md)
- Original rendered brief:
  [Decision Work Brief Rendered CEO Remove Founding Cofounder](decision-work-brief-rendered-ceo-remove-founding-cofounder-v0.md)
- Interpretation read:
  `reviews/codex-assisted/decision-work-conversation-interpretation-third-tiny-offline-read-v0/read.json`
- Source review:
  `reviews/codex-assisted/decision-work-brief-third-builder-case-output-v0/review.json`
- Highest-risk uncertainty: authority-transfer language can sound like legal or
  operational advice unless governance, employment, board, equity,
  relationship, team, and customer-trust caveats stay close.

## Response Template

The blank response template is:

`docs/conversation-understanding/decision-work-brief-human-review-response-template-v0.json`

It sets `review_status` to `not_started` and
`human_review_completed` to `false`. Case answers are not prefilled with Codex
opinions; they remain `not_reviewed`, `null`, or empty arrays for a real
reviewer to complete later.

Allowed answer values:

- `yes`
- `partly`
- `no`
- `unclear`
- `not_reviewed`

## Stop Conditions

The pilot should stop or mark the brief surface not ready if:

- the reviewer cannot tell what changed for action;
- caveats are too buried;
- source limits are unclear;
- the brief sounds like proof of good advice;
- the cofounder case sounds like legal or operational advice;
- the reviewer cannot distinguish evidence from interpretation;
- private context would be necessary to judge usefulness;
- the response template forces fake certainty.

## Decision Gate

PR151 chooses:

```text
ready_to_run_human_review
```

Recommended next PR:

```text
PR152 Decision Work Brief Human Review Pilot Run v0
```

The next step should be a real human-review pilot using the blank response
template. If no human reviewer is available, pause or package the scaffold
rather than filling human fields with Codex judgments.

## Boundary

PR151 does not:

- run `$lolla`;
- invoke the Lolla skill;
- call provider or model APIs;
- mutate archives;
- change runtime behavior;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- create a new Lolla run;
- create a new interpretation read;
- create a new builder output;
- check in local-private text;
- fill human review answers;
- claim human validation;
- claim product proof;
- score answer quality;
- add automatic labels;
- authorize agent action;
- implement runtime attachment.
