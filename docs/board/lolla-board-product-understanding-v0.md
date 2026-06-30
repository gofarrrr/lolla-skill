# Lolla Board Product Understanding v0

Status: board-facing product memo
Date: 2026-06-30

## One-Sentence Product Idea

Lolla helps teams use AI for serious decisions without treating a fluent final answer as enough evidence to act.

It adds a reasoning-audit and decision-trail layer around AI conversations, so a reviewer can see:

- what conversation produced the answer;
- what the system challenged;
- what changed in the revised answer;
- what remains missing or uncertain;
- what should not be treated as proven.

The goal is not certainty. The goal is to be less wrong before a team acts on AI-generated advice.

## The Problem We Are Solving

AI makes it very easy to produce a polished memo.

That creates a new problem: the memo often travels without the process that created it.

A team may see:

> Here is the recommendation.

But not:

- What did the user tell the AI?
- What did the AI accept too quickly?
- Which constraints shaped the recommendation?
- Which options were dropped?
- Which trade-offs were ignored?
- What pushback changed the answer?
- Did the revised answer add decision leverage or just more cautious prose?
- What evidence is missing?
- What should still be checked by a human?

In serious decisions, the process matters almost as much as the output.

Lolla is being built for that gap.

## What Users Should Eventually Receive

The product direction is not just:

> Here is a better AI answer.

The product direction is:

> Here is the revised answer, and here is the decision trail behind it.

A useful Lolla package should include:

1. **The revised answer**

   The answer after structured pressure has been applied.

2. **The decision trail**

   A simple explanation of what the system understood from the conversation: the decision, options, constraints, stakeholders, values, likely actions, pushback, lost value, and open questions.

3. **The audit receipt**

   A custody record showing which artifacts exist, what was missing, what was private or redacted, and what should not be overclaimed.

4. **The evaluation view**

   A careful comparison between the original strong-model answer and the Lolla revised answer: what changed, whether the change looks decision-useful, what may have been lost, and what still needs human judgment.

## Where The Alpha Is

The alpha is not a bigger prompt.

The alpha is the process envelope around AI-generated advice.

Most AI systems optimize for the final answer. Lolla is trying to preserve and inspect the path to the answer.

That matters because serious AI-assisted decisions usually fail in one of these ways:

- the original question framed the problem badly;
- the AI agreed with the user too quickly;
- the answer sounded balanced but skipped the hard constraint;
- the recommendation ignored a stakeholder, obligation, or value;
- the answer added caution but no real decision leverage;
- the revised memo removed uncomfortable caveats before being shared;
- a future reviewer or agent sees the final output without knowing how it was made.

Lolla's opportunity is to make those failure modes visible.

In an AI-first organization, the artifact people share should not only be the memo. It should be the memo plus the trail.

## What Exists Now

The live Lolla skill already does the core audit run:

```text
conversation
-> compact decision extraction
-> structured reasoning audit
-> revised answer
-> archived artifacts
```

That live runtime is not the main focus of this memo. The newer work adds two internal product surfaces around completed runs.

### 1. Decision Trail

Decision Trail asks:

> Can we explain the process behind the revised answer?

It turns completed Lolla runs into reports or packets that preserve:

- what the decision seemed to be;
- what structured artifacts exist;
- which parts are missing;
- which parts are private or redacted;
- which messy interpretation fields require LLM or human review;
- which candidate interpretations were produced in local-private pilots;
- what future human reviewers need to correct.

Today, Decision Trail is offline. It is not automatically triggered by the live Lolla skill.

### 2. Product Delta Evals

Product Delta asks:

> Did the revised answer change anything that matters compared with the original AI conversation?

It does not ask a broad judge, "Which answer is better?"

Instead it asks concrete questions:

- Did the likely next action change?
- Did the threshold for action change?
- Did the sequence change?
- Was an evidence gate added?
- Was a stop rule added?
- Was scope narrowed?
- Was an overclaim retracted?
- Did Lolla add useful friction or noisy friction?
- Did the revised answer lose momentum, simplicity, courage, or user-specific ambition?
- Was the conversation understood well enough to trust the comparison?

Today, this eval lane is also offline and internal. It studies existing artifacts after a run is complete.

## What We Know So Far

The early evidence supports the direction, but not a product-proof claim.

We know:

- The system can preserve more than a final answer.
- The Decision Trail shell is useful for showing custody, missingness, redaction, and non-claims.
- Local-private specialist interpretation can make the decision story much more concrete than a sparse safe report.
- Specialist interpretation can downgrade an overly positive read when the original answer already contained much of the useful action.
- Evals can ask better questions than "Which answer sounds better?"
- The strongest current signal is discipline, not hype: in one key case, the specialist review downgraded a broad positive read from material improvement to partial improvement.

We do not yet know:

- whether Lolla consistently improves real decisions;
- whether current specialist reads are fair without human correction;
- whether the reports are simple enough for users;
- whether the system catches enough no-change, noisy, or worse cases;
- whether the right fields are being captured from long messy conversations;
- whether agents can safely consume these artifacts beyond inspection and routing.

## Current Stop Point

The current stop point is healthy:

> We have built enough non-human scaffolding to inspect the idea, but not enough to claim proof.

The Decision Trail specialist pilot phase is closed.

The Product Delta non-human eval phase is packaged.

The next responsible step is human review of the prepared intake packets, not another automatic pilot by momentum.

## What This Means For The Board

Lolla is moving from:

> AI gives advice.

to:

> AI gives advice, the advice is pressured, the process is preserved, and the delta is inspected.

That is the product thesis.

The system is not ready to be sold as a fully validated decision-quality engine.

It is ready to be described as a reasoning-audit and decision-trail system under development, with strong product logic and conservative evidence discipline.

## What We Should Show In A Demo

A good demo should not start with JSON, schemas, or internal PR names.

It should show one serious decision:

1. The original AI conversation.
2. The answer the user was likely to act on.
3. What Lolla challenged.
4. The revised answer.
5. What changed in action, threshold, gate, sequence, or scope.
6. What may have been lost.
7. What remains unknown.
8. What the report refuses to claim.

The board should feel:

> I understand why the final answer alone is not enough.

## Product Risks

The main risk is not that the architecture is weak.

The main risk is that clean artifacts can make weak reasoning look stronger than it is.

Other risks:

- Too much structure may feel like bureaucracy.
- Non-human interpretation can agree with itself and look more validated than it is.
- Safe checked-in summaries can compress away important context.
- The system may over-credit Lolla for changes already present in the vanilla conversation.
- The system may over-reward caution and under-reward momentum.
- Users may want a simple approval badge, but giving them one would violate the product philosophy.

The product must keep saying:

> Clean process evidence is not proof of a good decision.

## What Needs To Happen Next

The next product work should be:

1. Use the prepared human-review intake packets.
2. Ask a principal human reviewer to correct or reject the candidate reads.
3. Pick one or two real cases for a simple end-to-end board demo.
4. Define the minimum customer-facing Decision Trail report.
5. Decide which fields must become first-class in future runtime artifacts.

Do not add a broad judge.

Do not add scoring.

Do not automate agent approval.

Do not build a graph or memory platform.

The next stage is about proving that the process trail helps humans understand and challenge AI-assisted decisions.

## Source Docs

For implementation-level detail, see:

- [Decision Trail Web Page Draft](../lolla-decision-trail-web-page-v0.md)
- [Decision Trail Human Review Intake Packet](../conversation-understanding/decision-trail-human-review-intake-packet-v0.md)
- [Decision Trail Specialist Pilot Phase Closure Gate](../conversation-understanding/decision-trail-specialist-pilot-phase-closure-gate-v0.md)
- [Product Delta Docs Index](../evals/README.md)
- [Product Delta Provisional Report](../evals/product-delta-provisional-report-v0.md)
- [Product Delta Packaging Gate](../evals/product-delta-pr71-pr84-packaging-gate-v0.md)
