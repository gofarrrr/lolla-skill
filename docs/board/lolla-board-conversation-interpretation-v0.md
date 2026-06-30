# Lolla Conversation Interpretation Product Brief v0

Status: board-facing product brief
Date: 2026-06-30

## Plain-English Summary

Lolla is starting to build a way to explain how an AI-assisted decision was formed.

This is the Decision Trail.

The idea is simple:

> If a team is going to rely on an AI-generated recommendation, they should be able to see the decision path behind it.

The final answer is not enough. Users need to know what the conversation contained, what the system understood, what it challenged, what changed, what was dropped, and what remains uncertain.

## Why This Matters

In real work, a difficult decision is rarely decided by one prompt.

It happens through a messy conversation:

- the user shares context;
- the AI asks or fails to ask questions;
- the user pushes toward a preferred answer;
- the AI may agree too easily;
- constraints appear in the middle of the conversation;
- values and trade-offs are implied, not cleanly stated;
- options are considered, then abandoned;
- the final memo may leave out the messy parts.

If the final memo travels without that process, the reviewer sees the conclusion but not the reasoning environment that produced it.

Lolla's Decision Trail is meant to restore that missing context.

## What The Conversation Interpretation Layer Tries To Understand

The layer is trying to answer practical questions a reviewer would ask:

- What decision was being made?
- What was the user likely to do before Lolla intervened?
- What does the revised answer seem to recommend now?
- Which options were live, rejected, deferred, or unclear?
- Which constraints mattered?
- Which stakeholders or obligations mattered?
- Which user values or priorities were visible?
- Did the AI influence the user's framing?
- What pushback did Lolla add?
- What useful friction was added?
- What noisy friction may have been added?
- What value from the original answer may have been lost?
- What still needs human judgment?

These are not simple database fields. They are interpretation questions.

That is why Lolla's principle matters:

> LLMs handle messy interpretation. Deterministic code keeps custody.

## How Probabilistic And Deterministic Parts Work Together

Lolla does not try to make deterministic code understand messy conversation by itself.

That would be brittle.

Instead, the system separates two jobs.

### The LLM Job

LLMs are used, or planned to be used, for the messy parts:

- reading the conversation;
- noticing the decision frame;
- identifying likely actions;
- spotting live options;
- seeing values, stakeholders, and assistant influence;
- distinguishing useful friction from noisy friction;
- noticing lost value;
- preserving uncertainty.

These outputs are treated as candidate reads, not truth.

### The Deterministic Job

Deterministic code handles the custody layer:

- which files exist;
- where the source came from;
- whether content was missing;
- whether content was private or redacted;
- which fields were populated;
- which fields require interpretation;
- whether the report includes forbidden overclaims;
- whether raw/private content was kept out of checked-in artifacts;
- whether human review fields are still blank.

This is the product philosophy in one line:

> Interpretation is probabilistic. Custody is deterministic.

## What Works Now

The live Lolla runtime already captures a compact decision shape and produces audit artifacts.

Separately, the offline Decision Trail lane can now do several things after a run is complete:

1. **Export a sparse Decision Trail report**

   This report shows which artifacts exist, which fields are populated from structured sources, which fields are missing, and which fields need interpretation.

2. **Build checked-in-safe packets**

   These are small safe packets that can be stored in the repo without raw/private conversation content.

3. **Build local-private packets**

   These can read richer local completed-run context, including private content, but their outputs are explicitly unsafe to check in unless summarized.

4. **Run narrow specialist interpretation pilots**

   The project tested four bounded reading roles over three real completed runs.

5. **Prepare human review intake**

   The three pilot cases are now packaged for a future human reviewer, with correction fields left blank.

## The Four Specialist Reads

The interpretation pilots use four simple reading roles.

### 1. Conversation Shape Reader

This reader asks:

> What was this conversation really about?

It looks for the decision, options, constraints, stakeholders, values, assistant influence, dropped threads, and uncertainty.

### 2. Likely Action Reader

This reader asks:

> What was the user likely to do before Lolla, and what does the revised answer make more likely now?

This matters because a revised answer only matters if it changes action, threshold, sequence, scope, or review burden.

### 3. Friction And Lost Value Reader

This reader asks:

> Did Lolla add useful friction, or just slow the user down?

It also asks what may have been lost: speed, simplicity, ambition, courage, relationship trust, or stakeholder detail.

### 4. Conservative Fan-In Reader

This reader asks:

> Given the other reads, what should we preserve as uncertain?

It is not a vote. It does not average opinions. It should downgrade or mark uncertainty when the evidence is thin.

## What The Pilots Found

The three local-private pilots are small, but they taught useful product lessons.

### Cofounder Authority Case

The Decision Trail made authority transfer, transition boundaries, stop conditions, and relationship cost more visible.

The main risk was that a clean report could understate how much legal, financial, governance, or relationship context was still missing.

### Founding Engineer Career Case

The revised answer added gates and stop conditions, but the original conversation already contained much of the action sequence.

This forced a downgrade:

> The revised answer looked partly useful, not cleanly material.

This is a strong product signal because the system became less flattering when vanilla overlap was visible.

### Clinic Deployment Controls Case

The useful delta was not "add more gates."

The useful delta was:

> Reduce noisy process bloat while preserving real operating stop conditions.

This is important. Useful friction is not always more caution. Sometimes it is better-shaped caution.

## What The System Can Figure Out Now

Current Decision Trail work can help identify, as candidate reads:

- the decision question;
- likely vanilla action;
- likely revised action;
- where the revised answer overlaps with the vanilla answer;
- live constraints;
- some live options;
- visible stakeholder and value concerns;
- useful friction;
- noisy friction;
- lost value;
- source limits;
- what a human reviewer should check next.

But these are not validated labels.

They are provisional interpretations held inside a custody system.

## What The System Cannot Claim Yet

The current Decision Trail work cannot yet claim:

- the interpretation is correct;
- the revised answer improved the decision;
- the specialist contracts are final;
- the system is ready for broad automatic batches;
- agents may act on the outputs;
- clean reports prove good reasoning;
- the live Lolla skill automatically produces this full report.

Today this is an offline evidence and product-development lane.

## What Users Could Eventually Get

The target user experience is:

> Send the revised AI decision memo with a compact process report attached.

That report should answer:

- What was the original decision?
- What did the first answer imply?
- What did Lolla challenge?
- What changed?
- What was already present in the original answer?
- What got dropped or weakened?
- What remains unknown?
- What is private, missing, or redacted?
- What should a human review before acting?

This would let a manager, reviewer, investor, operator, or future agent inspect the process, not just the polished conclusion.

## Product Pros

Decision Trail could give users:

- more confidence that the answer was pressured, not merely rewritten;
- visibility into assumptions and missing evidence;
- a way to compare original and revised recommendations;
- a way to preserve tacit context from a messy AI conversation;
- a structured handoff for future reviewers or agents;
- protection against treating fluent prose as proof.

## Product Cons And Risks

The risks are real:

- The report may look more authoritative than the evidence deserves.
- The fields may become too heavy for normal users.
- Non-human specialist reads may inherit Codex or model bias.
- Local-private mode is richer but privacy-sensitive.
- Checked-in-safe mode is safer but thinner.
- Too much interpretation can become a new kind of overclaim.

The product must stay humble:

> Decision Trail is a review surface, not an approval badge.

## Current Product Stage

Decision Trail is not yet a finished customer-facing feature.

It is currently:

- designed;
- partially implemented as offline reporting;
- tested with small local-private specialist pilots;
- packaged for later human correction;
- deliberately stopped before broad automation.

The next useful move is human review of the prepared intake packet.

## Source Docs

For implementation-level detail, see:

- [Decision Trail Web Page Draft](../lolla-decision-trail-web-page-v0.md)
- [Decision Trail Readiness Audit](../conversation-understanding/decision-trail-readiness-audit-v0.md)
- [Decision Trail Interpretation Gap Decision](../conversation-understanding/decision-trail-interpretation-gap-decision-v0.md)
- [Decision Trail Local-Private Specialist Output Pilot](../conversation-understanding/decision-trail-local-private-specialist-output-pilot-v0.md)
- [Decision Trail Second One-Case Specialist Pilot](../conversation-understanding/decision-trail-second-one-case-specialist-pilot-v0.md)
- [Decision Trail Third One-Case Diversity Pilot](../conversation-understanding/decision-trail-third-one-case-diversity-pilot-v0.md)
- [Decision Trail Human Review Intake Packet](../conversation-understanding/decision-trail-human-review-intake-packet-v0.md)
