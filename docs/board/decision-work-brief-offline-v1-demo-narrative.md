# Decision Work Brief Offline v1: Making AI-Assisted Decisions Inspectable

Decision Work Brief turns a completed AI-assisted decision process into a
compact explanation of what changed, what evidence exists, what remains
uncertain, and what should not be overtrusted.

## The Problem

AI can produce polished final answers quickly. That polish is useful, but it
can also hide how the decision was made.

In serious work, the process matters. A reader needs to know what assumptions
were accepted, which options were still live, what tradeoffs were pressed, what
context was missing, and which caveats survived the final recommendation.

Without that trail, a final answer can look more settled than it really is.
Teams need a way to inspect the decision work without rereading the whole
conversation every time.

## What Offline v1 Does

Decision Work Brief Offline v1 reads completed Lolla artifacts after the run
and turns them into a compact evidence surface.

It can:

- create a readable Decision Work Brief from completed artifacts;
- explain what decision was being made;
- show what changed for action;
- preserve what remains uncertain;
- add bounded interpretation of what the process appears to have clarified;
- triage whether the brief looks like a normal caveated summary, a
  source-thin case, a high-risk case, an agent-inspection-only case, or a case
  blocked from runtime or user confidence.

The final AI answer alone is cheap. The valuable part is the decision work and
the limits that travel with it.

## Example: Launching A Public Enterprise Beta

One checked-in example is
[`launch-public-enterprise-beta`](../conversation-understanding/decision-work-brief-builder-enriched-launch-public-enterprise-beta-v0.md).

The starting situation was a go-to-market decision: launch a public enterprise
beta next month to secure enterprise prospects and extend runway, or run a
restricted private enterprise pilot first.

The brief says the decision was not simply "launch or do not launch." The
usable decision became more specific:

- Should the larger-logo prospect get priority by default?
- Should public launch count as evidence before buyer behavior is visible?
- What would actually prove enterprise readiness?
- Which stop rules should exist before the next buyer call?

The interpretation layer adds a useful distinction. Some caution may already
have been present in the original safe summary. The audit process appears to
have sharpened the action consequence: give both prospects the same paid,
scoped private-pilot offer; choose based on proof-producing buyer behavior; and
do not treat logo size or a public page as proof by itself.

That is the product value in miniature. The brief does not just repeat an
answer. It makes the decision inspectable:

- the decision was public launch versus constrained private proof;
- the pressure was on launch optics, buyer proof, support load, audit-log
  limits, and stop rules;
- the action consequence was a same-shape paid private pilot offer for both
  prospects;
- the uncertainty was that private buyer reality, fundraising value, recruiting
  value, and raw conversation context are still compressed or unavailable;
- the non-claim was that none of this proves the final advice was correct.

## What The Triage Layer Adds

Offline v1 also includes provisional automatic triage. Triage is routing, not a
rating.

For the launch-beta example, the provisional read routes it as a normal
caveated brief candidate, while still flagging private-context dependency,
human calibration, and runtime attachment as unresolved. A downstream agent
would inspect buyer reality, public-launch upside, and whether the larger-logo
prospect was being treated as evidence or status signal.

Across the three current cases, triage can point attention to:

- source-depth risk;
- overtrust risk;
- private-context dependency;
- domain, legal, compliance, governance, or relationship sensitivity;
- what a downstream agent should inspect first;
- whether runtime attachment remains blocked.

Triage is not a score, approval, or proof of good advice.

## What This Is Not

Decision Work Brief Offline v1 is not:

- runtime integration;
- customer readiness;
- human validation;
- product proof;
- answer-quality scoring;
- proof that the advice was correct;
- permission for an agent to act;
- proof that Lolla improved the decision.

Clean artifacts can still describe a bad recommendation cleanly. The system is
useful because it makes that risk easier to inspect, not because it removes the
risk.

## Why This Matters

Decision Work Brief gives users context, not just an answer. It helps a reader
see the pressure trail behind a serious AI-assisted decision: what was being
decided, what got challenged, what changed for action, what remains missing,
and what the final answer does not prove.

That matters for future agent systems too. If another agent later touches the
same decision, it should not inherit only a polished final answer. It should
inherit the evidence trail, the missingness, the caveats, and the routing flags.

This creates a proof-of-work style layer for AI-assisted decisions. Not proof
that the answer is right, but proof that the decision work is available for
inspection.

## Current Limitations

Offline v1 works after a completed run. It is not automatically attached to
live Lolla runs.

It relies on checked-in-safe, compressed artifacts. Raw/private conversation
details, provider text, private ledgers, and human reviewer responses are not
checked in.

The interpretation and triage reads are Codex-assisted and provisional. Human
calibration is deferred. The examples are not customer-facing yet.

The highest-risk cases, especially healthcare operations and founder
governance, need domain, legal, relationship, and private-context calibration
before anyone treats the brief as more than an offline evidence surface.

## What Comes Next

Read the examples with product, board, and customer eyes:

- Which parts should a user see?
- Which parts should stay agent-facing?
- Where do caveats need to be closer to the action consequence?
- What would a real human reviewer mark as useful, confusing, or
  overtrust-inducing?
- What product surface would make the decision work obvious without burying the
  reader in machinery?

The next evidence step is human calibration when capacity exists. Runtime
attachment should wait until the product surface is clear and the limits remain
visible.
