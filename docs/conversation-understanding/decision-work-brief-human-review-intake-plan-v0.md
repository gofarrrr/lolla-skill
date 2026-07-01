# Decision Work Brief Human Review Intake Plan v0

Status: PR150 human-review intake plan

Date: 2026-07-01

Review schema: `lolla.decision_work_brief_human_review_intake_plan.v0`

## Purpose

PR150 defines how a future human reviewer should inspect the offline Decision
Work Brief and enriched examples before anyone treats the surface as useful,
safe, or user-facing.

This is not the human review itself. It is the intake plan for that review.

The plan covers exactly the three builder-generated enriched briefs reviewed in
PR149:

- [Decision Work Brief Builder-Enriched Launch Beta](decision-work-brief-builder-enriched-launch-public-enterprise-beta-v0.md)
- [Decision Work Brief Builder-Enriched Intake Routing](decision-work-brief-builder-enriched-deploy-assisted-intake-routing-v0.md)
- [Decision Work Brief Builder-Enriched CEO Remove Founding Cofounder](decision-work-brief-builder-enriched-ceo-remove-founding-cofounder-v0.md)

## What Reviewers Check

A reviewer should inspect each enriched brief for five things:

1. Whether the brief is useful to a busy decision-maker.
2. Whether the action consequence is clear without reading like a command.
3. Whether the enrichment explains what appears sharpened without pretending to
   prove the advice is right.
4. Whether uncertainty, missingness, source limits, and private-context limits
   are visible enough.
5. Whether the brief creates false confidence, especially in the
   cofounder/governance case where authority-transfer language can sound
   operationally decisive.

The reviewer should not score answer quality. The reviewer should not decide
whether Lolla improved the decision. The reviewer should decide whether the
brief shape is useful, bounded, and not overtrust-inducing.

## Case-Specific Focus

Launch-beta:

- Does the brief help a reader distinguish a public launch from a paid, scoped
  private-pilot proof path?
- Does it avoid treating buyer logo size, investor optics, or a public page as
  proof by itself?
- Does it preserve uncertainty about what was already present before the
  Lolla-shaped pressure?

Intake-routing:

- Does the brief keep deployment language bounded to a narrow operating test?
- Does it make backlog diagnosis, clinic scope, compliance readiness, and pause
  triggers clear?
- Does it avoid making the AI routing feature sound validated or safe to deploy
  broadly?

Cofounder/governance:

- Does the brief make authority-transfer consequences clear while avoiding a
  settled recommendation tone?
- Are legal, equity, board, employment, founder-relationship, customer-trust,
  and team-loyalty caveats visible enough?
- Does the enriched section sound too operationally decisive?

## Stop Conditions

Human review should block runtime attachment or customer-facing presentation if
reviewers find any of these patterns:

- the brief reads like advice certification;
- the enriched section creates false confidence;
- missing private context would materially change the decision story;
- evidence-only fields are smoothed into main-body claims;
- source limits are too buried for a busy reader;
- the cofounder/governance case sounds like action authorization;
- reviewers cannot tell what is useful but not validated.

## Allowed Outcomes

The future review should use only these outcome labels:

- `useful_but_needs_source_depth`
- `useful_but_too_overtrust_inducing`
- `readable_but_not_actionable`
- `too_internal_for_user_surface`
- `ready_for_more_human_review`
- `not_ready_for_runtime`
- `needs_simplification`
- `inconclusive`

These outcomes are review outcomes, not product labels. They must not be used
as answer-quality scores or agent-action approvals.

## Decision Gate

PR150 chooses:

```text
run_human_review_pilot
```

Recommended next PR:

```text
PR151 Decision Work Brief Human Review Pilot v0
```

The next useful step is to run a small human-review pilot against the three
builder-generated enriched briefs using this intake plan.

Runtime attachment is still premature.

## Boundary

PR150 does not:

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
- claim human validation;
- claim product proof;
- score answer quality;
- add labels;
- authorize agent action;
- implement runtime attachment.
