# Observatory Agent Memory Verification Checklist v0

Status: implemented renderer slice, locally validated.

Date: 2026-07-07

Decision gate: `proceed_to_agent_memory_source_locator_spike`

## Purpose

The cold-reader orientation made the Conversation Memory export easier to
enter, but diagnostic readers still asked for claim-level verification support.
This slice adds that support without creating a stronger summary.

The renderer now places:

```text
## Claim Verification Checklist
```

immediately after:

```text
## Cold Reader Orientation
```

and before:

```text
## What This File Is
```

The checklist is a checking index, not a conclusion. It points a future reader
to the source material that should be inspected before relying on generated
synthesis.

## Product Behavior

The section renders a compact table with:

- `Claim / item to verify`;
- `Best evidence in this file`;
- `Still verify before relying`.

Rows are produced deterministically from the existing packet:

- decision situation;
- generated synthesized position when present;
- changed advice summary when present;
- main counter-pressure when present;
- revised answer presence when present;
- first structured open question, or a warning that no structured
  open-question rows were supplied;
- run readiness.

The section does not call providers, run Lolla, create a new archive, or infer
new claims from raw transcript text. It only routes attention to already
compiled packet fields and named source artifacts.

## Why This Shape

The main risk in the prior slice was summary anchoring: a polished top-level
answer could make future agents lazy. A longer executive summary would make
that risk worse.

The checklist takes the opposite posture:

- it keeps synthesis visible but unfinished;
- it attaches synthesis to source locations;
- it tells the reader what still needs verification;
- it makes empty open-question rows visibly non-final;
- it ties readiness warnings to reliance limits.

This is closer to an audit index than to a product answer.

## What This Proves And Does Not Prove

Useful signal:

- the export now tells future readers how to check the main generated claims;
- the checklist is inherited by the Observatory Markdown download route;
- tests verify that the checklist appears before the ordinary explanatory
  sections and preserves anti-proof wording.

Non-claims:

- this is not human validation;
- this is not product proof;
- this does not prove the advice is correct;
- this does not prove the answer is correct;
- this does not authorize action;
- this does not authorize runtime integration;
- this does not prove the checklist is a final UX;
- this does not make generated synthesis a source of truth.

## Recommended Next Slice

The next improvement should make source inspection easier without turning the
artifact into a dashboard.

Possible next slice:

```text
proceed_to_agent_memory_source_locator_spike
```

That slice could add stable section labels or source-locator hints so a future
reader can jump from each checklist row to the transcript, memo, revised answer,
run health, or artifact custody section faster.

## Boundary

This slice:

- does not run Lolla;
- does not invoke the Lolla skill;
- does not call providers or model APIs;
- does not create a new run;
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
- does not treat embedding similarity as validated relation semantics.
