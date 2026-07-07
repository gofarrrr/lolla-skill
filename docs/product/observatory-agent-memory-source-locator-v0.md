# Observatory Agent Memory Source Locator v0

Status: implemented renderer slice, locally validated.

Date: 2026-07-07

Decision gate: `proceed_to_agent_memory_download_ux_review`

## Purpose

The verification checklist made the Conversation Memory export easier to
inspect, but each row still pointed to section and artifact names only. A future
reader knew what to check, but still had to hunt for the relevant section.

This slice adds stable source-locator hints to the rendered Markdown without
adding a stronger summary.

## Product Behavior

The renderer now emits stable anchors for ordinary sections:

```text
cm-section-claim-verification-checklist
cm-section-conversation-interpretation
cm-section-what-changed
cm-section-open-questions
cm-section-run-health-and-readiness
cm-section-artifact-custody
```

It also emits stable anchors for source excerpts when those excerpts are
included:

```text
cm-source-full-transcript
cm-source-memo
cm-source-revised-answer
```

The `Claim Verification Checklist` now includes a `Source locator` column. Each
row links to the nearest relevant rendered section or source excerpt. For
example:

- decision situation links to transcript, conversation interpretation, and
  decision situation;
- generated synthesis links to conversation interpretation, transcript, memo,
  and revised answer;
- changed advice links to `What Changed`, transcript, and revised answer;
- run readiness links to run health and artifact custody.

When a source excerpt is not embedded in a privacy mode, the locator degrades to
plain text such as `Transcript (artifact not embedded)` instead of creating a
dead local anchor.

## Why This Shape

This is deliberately not a dashboard and not an interactive UI. The Markdown
file must remain portable and readable by a future agent or human without a
server.

The locator layer gives the artifact a better reading path while preserving the
core posture:

- source inspection before reliance;
- synthesis as something to verify;
- no proof claim;
- no action authorization;
- no runtime integration.

## What This Proves And Does Not Prove

Useful signal:

- each checklist row now has a local navigation target;
- the Observatory Markdown download inherits those anchors and links;
- source excerpts have stable explicit anchors instead of relying only on
  renderer-specific heading slug behavior;
- source locators avoid dead links when raw source excerpts are not embedded.

Non-claims:

- this is not human validation;
- this is not product proof;
- this does not prove the advice is correct;
- this does not prove the answer is correct;
- this does not authorize action;
- this does not authorize runtime integration;
- this does not make generated synthesis a source of truth;
- this does not guarantee every claim has exact line-level transcript evidence.

## Recommended Next Slice

The next useful step should move from artifact mechanics back to user-visible
Observatory experience:

```text
proceed_to_agent_memory_download_ux_review
```

That review should open the Observatory page, download the Markdown, and decide
whether the main page now explains this feature clearly enough for the user:

- what the download is;
- why an agent would use it;
- what it contains;
- what it does not prove;
- where it should sit on the main page.

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
