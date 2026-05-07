# Decision Pressure Product Doctrine

**Date:** 2026-05-06
**Status:** Product doctrine after PR29 v5 packet handoff-depth review. This
is not a runtime proposal, prompt change, broad extraction brief, or
user-facing launch plan.

**Doctrine label:** `broad_intake_disciplined_output`

**Current posture:** `v5_packet_depth_improved`

**Architecture simplification:** `research/enriched-mental-model-packet-strategy-2026-05-06.md`

**Source/packet audit brief:** `research/source-understanding-and-reasoning-packet-audit-brief-2026-05-06.md`

**Current source/packet audit:** `research/source-understanding-and-reasoning-packet-audit-2026-05-06.md`

**Current packet spec:** `research/reasoning-substrate-packet-v1-spec-2026-05-06.md`

**Current controlled extraction report:** `research/pr28-controlled-graph-only-extraction-report-2026-05-06.md`

**Current v5 packet depth review:** `research/reasoning-substrate-v5-packet-depth-review-2026-05-07.md`

**Next-session handover:** `research/reasoning-substrate-next-session-handover-2026-05-06.md`

## Core Doctrine

> Broad intake, disciplined output.

Lolla should remain broad in the kinds of users, domains, decisions, and
pressures it can inspect. But the surfaced output must stay narrow, compact,
dismissible, source-backed or coverage-honest, and action-relevant.

Lolla is moment-first, not persona-first.

The repeatable moment is:

> I have AI advice. It sounds plausible. I may act. What important operational
> pressure am I not seeing?

The public promise is:

> Before you act on AI advice, Lolla shows what might be missing.

The internal promise is:

> Lolla turns AI advice into a source-backed decision-pressure pass: what to
> verify, why it matters, how to dismiss it, what tripwire or action to set,
> and where coverage is missing.

## Why This Doctrine Exists

The PR13-PR23 stack found a useful surface, but it also exposed the project's
main product risk.

The good version:

> Lolla gives a compact source-backed pressure pass before action.

The bad version:

> Lolla becomes more analysis, more questions, more mental-model names, or a
> deterministic case-pattern machine.

This doctrine protects the good version.

It lets Lolla search across a wide possible pressure space without dumping that
space onto the user. The user should not need to know which lens to ask for.
That is the point: if the user already knows to ask for opportunity cost,
falsifiability, incentive misalignment, downside risk, or reversibility, a good
LLM can respond. Lolla is most valuable when the user does not know which
pressure matters before acting.

## What Lolla Is

Lolla is a pressure pass over advice near action.

It may be used by:

- founders making strategy, hiring, equity, fundraising, or product calls;
- lawyers and legal operators checking reasoning quality;
- managers and teams reviewing plans;
- students and researchers choosing paths under uncertainty;
- people making personal, family, career, money, or relocation decisions;
- agents checking their own plans before execution;
- teams preserving decision records;
- ordinary AI users asking for serious advice.

These are not separate products yet. They are examples of the same moment:

> A human or agent is about to rely on plausible advice, and an important
> operational pressure may be missing.

## What Lolla Is Not

Lolla is not:

- persona-first;
- mental-model browsing;
- generic critique;
- a second chatbot that says more things;
- a dashboard of thoughts;
- raw model-output enrichment;
- a pile of gap questions;
- a demand that every run produce insight;
- deterministic pressure selection;
- case-type routing rules;
- examples becoming templates;
- Python deciding wisdom.

The substrate matters, but the user should not experience the product as a
mental-model encyclopedia. Mental models are source material. Decision Pressure
is the product-shaped object.

## The Product Moment

The product moment has six parts:

1. The user has a situation, plan, answer, or recommendation.
2. The advice sounds plausible enough to act on.
3. Acting may create commitment, cost, exposure, drift, or missed opportunity.
4. The user does not necessarily know which pressure matters.
5. Lolla surfaces one or a few compact operational pressures.
6. The user leaves with a better decision position: what to verify, dismiss,
   monitor, delay, document, stop, or do next.

The moment can appear in many domains, but it is not every conversation. Lolla
is strongest near action, commitment, irreversibility, coordination, scarce
resources, fragile evidence, uncertainty, or AI overconfidence.

## Broad Intake

The possible pressure space should stay broad.

Eligible pressure domains include, but are not limited to:

- opportunity cost;
- downside and tail risk;
- reversibility and commitment;
- incentive misalignment;
- stakeholder trust and power;
- evidence quality;
- falsifiability and kill criteria;
- uncertainty type;
- probability calibration;
- resource allocation;
- sequencing and timing;
- option value;
- governance and decision rights;
- safety and instrument trust;
- competitive dynamics;
- coverage gaps.

This breadth is necessary for unknown-unknown discovery. The user often cannot
name the lens because the missing pressure is precisely what is outside their
current frame.

## Disciplined Output

Any domain of pressure is eligible. Not every interesting pressure deserves to
surface.

A surfaced Decision Pressure must clear the pressure contract:

1. **Relevant**
   It connects to the actual situation, plan, answer, or decision.

2. **Action-delta**
   It changes what the user should verify, delay, test, document, monitor,
   dismiss, or stop.

3. **Compact**
   It can be stated as one focused pressure, not a mini-essay or dashboard.

4. **Dismissible**
   The user can know what would make the pressure no longer matter.

5. **Tripwire or next action**
   It identifies what to do, watch, decide, or write down before acting.

6. **Source-backed or coverage-honest**
   It is grounded in reviewed substrate, or it honestly says the substrate is
   missing.

7. **Non-duplicative**
   It does not merely restate what the original answer already handled well.

8. **No fake precision**
   It does not manufacture specificity, numbers, citations, or confidence.

9. **No deterministic template**
   It does not surface because a case matches a remembered example.

The allowed output is compact pressure. The forbidden output is clever noise.

## Unknown Unknowns, Grounded

Lolla can look for unknown unknowns, but that phrase must stay grounded.

Bad framing:

> Lolla discovers unknown unknowns.

Better framing:

> Lolla looks for the operational pressure the user may not know to ask about
> before acting.

This matters because "unknown unknowns" can become mystical. Lolla should not
surface interesting abstractions simply because they are surprising. It should
surface operational pressure because it changes the user's next verification,
commitment, dismissal, tripwire, or action.

## What PR13-PR23 Proved

The merged PR13-PR23 stack does not prove that Decision Pressure is
runtime-ready.

It does prove a narrower product-shaped claim:

> Messy AI advice can often be compressed into one or a few operational checks
> before action, with provenance, dismissal, tripwire, suppression, and coverage
> honesty.

The stack supports:

- Decision Pressure as a compact audit surface;
- v4 affordances as useful reviewed substrate;
- coverage transparency as a trust feature;
- zero-output as a valid outcome;
- trace contracts and adapter reports as dormant review infrastructure;
- directional generalization across five additional archived cases;
- anti-casuistry rails that prevent examples from becoming deterministic
  templates.

The stack does not support:

- runtime promotion;
- live `/lolla` use;
- live Observatory;
- memo, Step 8, Step 6, or Lane 4 wiring;
- prompt changes;
- generation changes;
- Batch 3b;
- broad corpus extraction;
- paid reruns by default;
- deterministic pressure selection;
- user-facing Decision Pressure blocks.

## Architecture Boundary

The current runtime/affordance split is mapped in
`research/knowledge-matching-current-state-audit-2026-05-06.md`. Future
sessions should keep that distinction explicit: the active runtime graph has
222 models, while the v4 affordance corpus has 55 reviewed source-backed
records and remains dormant review substrate.

The simplification note in
`research/enriched-mental-model-packet-strategy-2026-05-06.md` is the current
anti-drift correction:

> Pull shelves, enrich cards, let the LLM reason.

Existing lanes should nominate candidate mental-model shelves. Deterministic
code may enrich those shelves with source-backed v4 card snippets, provenance,
caps, and coverage status. It must not become a deterministic pressure solver.

The deterministic layer may enforce:

- schema shape;
- max selected-pressure count;
- runtime dormancy;
- provenance classes;
- source-affordance references;
- explicit coverage gaps;
- blocked-surface declarations;
- review-only counts, IDs, and drift reports.

The deterministic layer must not:

- choose which pressure is good;
- infer a pressure from case type, route label, keyword, or gap label;
- rank novelty, tone, actionability, or user usefulness;
- merge pressures based on semantic similarity;
- smooth missing coverage into generic model-name reasoning;
- generate user-facing pressure prose;
- imitate PR13/PR23 examples.

LLM/reviewer synthesis owns semantic selection and wording. Python owns
custody, validation, packaging, and drift detection.

## Public Message

Candidate public message:

> Before you act on AI advice, Lolla shows what might be missing.

Expanded public message:

> Lolla gives AI advice a second-pass decision audit. It surfaces the pressure
> you may not know to ask about: what to verify, what would dismiss the concern,
> what tripwire to set, and where the knowledge base has no coverage.

Avoid public messages like:

- "better answers through more reasoning";
- "all mental models applied to your decision";
- "find every blind spot";
- "unknown unknown detector";
- "AI that thinks harder";
- "automated wisdom";
- "complete decision analysis."

Those either overclaim or push the product toward bloat.

## Internal Product Language

Use:

- pressure pass;
- decision-pressure pass;
- compact safeguard before action;
- operational pressure;
- dismissal path;
- tripwire;
- coverage honesty;
- source-backed audit;
- improves the user's decision position.

Avoid:

- more analysis;
- deeper thoughts;
- more lenses;
- comprehensive critique;
- case templates;
- automatic wisdom;
- model browsing;
- question wall.

## Promotion Bar

Runtime or user-facing promotion should stay blocked until evidence shows:

1. Users understand the pressure without reading the full trace.
2. The pressure changes what users verify, delay, test, document, monitor,
   dismiss, or stop.
3. Users experience the output as relief or clarity, not more homework.
4. Multiple reviewers can converge without relying on example imitation.
5. Coverage gaps increase trust rather than feeling like product failure.
6. The surface works across domains without case-type rules.
7. The deterministic layer remains custody/validation/reporting only.
8. The output can be compact enough for the eventual receiving surface.

After the May 6 continuation decision, the posture is:

> `source_understanding_packet_audit_complete`

This lifted the post-PR23 pause only for the docs/research Source Understanding
And Reasoning Packet Audit and dormant packet spec. It does not authorize
runtime promotion, prompt changes, lane rewrites, broad extraction, Batch 3b,
paid runs, or user-facing Decision Pressure output.

After PR24 review, the temporary active next-session posture was:

> `stop_and_consolidate_after_pr24_review`

PR25 later reopened forward work explicitly and only along the corrected
enrichment architecture:

> `fixture_packet_producer_ready`

PR26 then completed deterministic source custody backfill:

> `source_custody_backfill_complete`

PR27 then completed one review-only mixed packet fixture:

> `mixed_packet_fixture_useful`

PR28 then completed one controlled graph-only extraction batch:

> `controlled_graph_only_extraction_batch_ready`

PR29 then completed one v5 packet handoff-depth review:

> `v5_packet_depth_improved`

Future sessions should read
`research/reasoning-substrate-next-session-handover-2026-05-06.md` first and
treat PR26 as source custody, not extraction, and PR27 as fixture-usefulness
evidence, not runtime production. Treat PR28 as a controlled extraction quality
loop, not v5 runtime promotion or Batch 3b. Treat PR29 as handoff-depth
evidence, not final-answer evidence or deterministic pressure-selection
permission. Existing lanes stay intact, reviewed affordances are additive to
lane-selected candidates, graph-only models remain eligible, and Python
packages reasoning material for LLM/reviewer judgment. Do not start runtime
packet production, prompt changes, lane rewrites, broad extraction, Batch 3b,
paid runs, or user-facing Decision Pressure output by default.

## Next Product Work, Not Engineering Work

The next useful work is not Decision Pressure machinery.

The completed source/packet audit answered the immediate slice question:

> Can the existing lane system produce candidate shelves that can be enriched
> into a compact, source-aware packet for the next LLM?

PR27 added the first fixture answer:

> Yes, mixed v4 + source-custodied graph-only packets are useful handoff
> material, but graph-only cards are still thinner than reviewed affordance cards.

PR28 added the first controlled extraction answer:

> Yes, the first ten graph-only sources can produce compact reviewed affordance
> cards when exact source custody and absence records are enforced.

PR29 added the first v5 handoff-depth answer:

> Yes, the same PR27 nominations become more useful LLM handoff material when
> regenerated against v5: four formerly graph-only cards gain clearer
> activation, evidence, do-not-use, misuse, treatment, and absence signals
> without changing candidate count or letting Python choose the conclusion.

The next useful product questions are:

1. Does a receiver-side LLM/reviewer actually use the added v5 depth to choose,
   merge, ignore, or set aside candidate shelves more cleanly?
2. Which PR28 cards remain useful when tested in additional candidate mixes,
   and which merely add internal bulk?
3. Which decision moments most clearly need pressure before action?
4. What would make a user trust a pressure pass?
5. What would make the output feel like noise?
6. What is the smallest public promise that is true?
7. What evidence would justify promotion into a real surface?
8. What evidence would tell us the product is only interesting to us?

Do not answer these by adding machinery. Answer them with product review,
manual examples, packet comparison, user conversations, and decision-moment
analysis.

## One-Line Guardrail

> Keep the world of possible pressures broad. Keep the surfaced pressure
> contract strict.
