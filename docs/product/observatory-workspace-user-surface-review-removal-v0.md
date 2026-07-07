# Observatory Workspace User Surface Review Removal

Status: implemented product-surface correction.

Date: 2026-07-07

Decision gate: `proceed_to_observatory_data_exposure_audit`

## Product Correction

The previous Observatory workspace exposed internal review mechanics as if they
were part of the user product. The sidebar showed a `Review Guide` panel, and
Receipts included a `Human review` block that asked the viewer to judge whether
the workspace read as one product journey.

That was the wrong information layer. Review mechanics are internal process,
not a user-facing feature.

## UX Change

The user-facing workspace now keeps the product path:

```text
Outcome -> Learn -> Models -> Relations -> Map -> Receipts
```

The sidebar still contains:

- run context;
- switch run;
- reading path.

The sidebar no longer contains:

- `Review Guide`;
- `Open review guide`;
- review instructions for judging the product.

Receipts still contains:

- trust summary;
- Teacher packet status;
- Conversation Understanding status;
- Process Brief status;
- visible non-claims;
- optional technical inspection;
- source and missingness details.

Receipts no longer asks the user to review the product. The workspace does not link to `/review/observatory-workspace`.

The server-rendered review guide route remains available only as internal
maintainer process. It is not advertised in the product surface.

## Why This Matters

The default user path should explain what the system saw, what it taught, which
mental models are relevant, how those models relate, where the user can
navigate next, and what claims are not being made.

It should not ask the user to grade the product while they are trying to
understand the run.

## What This Does Not Solve

This correction does not yet decide the full information hierarchy. The next
step is an explicit data exposure audit:

- what data is gathered;
- what data can be presented safely;
- what belongs in the default first read;
- what belongs behind expansion;
- what belongs in technical inspection;
- what belongs in agent-only memory or internal custody;
- what is not currently represented in the graph.

Technical inspection remains optional. Direct audit routes still exist for
builders and maintainers.

## Boundary

This slice:

- does not run Lolla;
- does not invoke the Lolla skill;
- does not call providers or model APIs;
- does not create a new run;
- does not generate or attach sidecars;
- does not wire skill runtime behavior;
- does not mutate archives;
- does not edit `observatory/build`;
- does not touch `SKILL.md`;
- does not touch `scripts/skill/*`;
- does not touch `scripts/archive_run.py`;
- does not claim product proof;
- does not claim human validation;
- does not claim answer correctness;
- does not claim advice correctness;
- does not authorize automatic action;
- does not treat graph edges as proof;
- does not treat relation confidence as certification.

Recommended next gate:

`proceed_to_observatory_data_exposure_audit`
