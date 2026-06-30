# Lolla Product Evals Board Brief v0

Status: board-facing product brief
Date: 2026-06-30

## Plain-English Summary

Lolla's evaluation work is trying to answer one product question:

> Did the Lolla audit create a decision-useful change compared with the original AI conversation?

It is not trying to give Lolla a score.

It is not trying to declare that the second answer is better.

It is trying to make the difference between the original answer and the revised answer inspectable.

## The Baseline

The baseline is not a weak model or a toy prompt.

The baseline is the real thing:

> A serious user has a conversation with a strong AI model, receives a plausible answer, and may be ready to act.

That is the real workflow Lolla is trying to improve.

So the evaluation question is:

> Given the original strong-model conversation, what did Lolla change, and does that change look decision-useful?

## Why We Do Not Use A Simple Judge

A simple judge would ask:

> Which answer is better?

That is too soft.

It rewards:

- longer answers;
- smoother prose;
- more caveats;
- more confident structure;
- generic balance;
- impressive-looking artifacts.

That would be exactly the wrong product signal.

Lolla's evals instead ask concrete questions:

- Did the likely next action change?
- Did the threshold for action change?
- Did the sequence change?
- Did Lolla add an evidence gate?
- Did it add a stop rule?
- Did it narrow scope?
- Did it retract an overclaim?
- Did it surface a stakeholder, value, or constraint?
- Did it add useful friction or noisy friction?
- Did it lose momentum, simplicity, courage, or ambition?
- Did it misunderstand the conversation?

This keeps the eval focused on decision movement, not answer polish.

## What Product Delta Means

Product Delta means:

> The observable difference between the original AI advice and the Lolla revised advice.

A useful delta might be:

- "Do not launch broadly; run one pilot first."
- "Treat spouse approval as necessary but not sufficient."
- "Move authority first, with transition limits and stop conditions."
- "Raise prices only with account segmentation and written thresholds."
- "Do not treat enterprise logo interest as buyer proof."

A weak delta might be:

- "The revised answer is longer."
- "The revised answer adds more caveats."
- "The revised answer sounds more mature."
- "The revised answer says to be careful but does not change action."

The eval system is built to separate these.

## What The Eval Lane Does Now

The eval lane is offline.

It studies completed Lolla runs later. It does not run the Lolla skill.

It can:

1. Check whether a case has enough safe artifacts to review.
2. Build a structured review packet.
3. Ask provisional non-human readers to fill the packet.
4. Preserve uncertainty, missingness, and disagreement.
5. Run deterministic lint against overclaiming.
6. Produce reports that say what the evidence does and does not show.

The current eval lane is internal evidence scaffolding, not customer-facing proof.

## What We Check

For each case, the eval protocol tries to capture:

- vanilla likely next action;
- Lolla likely next action;
- material difference;
- structural delta;
- decision leverage;
- useful friction;
- noisy friction;
- lost value;
- interpretation adequacy;
- net decision read;
- human follow-up questions;
- what would make the read false.

The most important fields are not the final candidate labels. The most important fields are the reasons, caveats, lost-value notes, and follow-up questions.

## How Deterministic And Probabilistic Parts Work Together

The eval lane uses the same philosophy as the rest of Lolla.

### LLM-Assisted Parts

LLMs or Codex-assisted passes are used for provisional interpretation:

- comparing likely actions;
- seeing structural deltas;
- reading useful versus noisy friction;
- spotting lost value;
- noticing interpretation gaps.

These are lower-claim reads. They are not human labels.

### Deterministic Parts

Deterministic code is used to keep the evaluation honest:

- check whether artifacts exist;
- validate JSON shape;
- require conservative metadata;
- preserve source references;
- block forbidden authority fields;
- scan for private-content markers;
- prevent product-proof language;
- make missingness explicit;
- keep human validation fields false or blank.

The system is not trying to automate taste. It is trying to make taste reviewable later.

## What We Found So Far

The non-human Product Delta phase inspected 14 existing cases.

Twelve were ready for provisional review.

The broad Codex-assisted review found candidate deltas in many cases, often around:

- evidence gates;
- thresholds;
- scope changes;
- written terms;
- action changes;
- stop rules;
- user-answerable questions.

But the important finding was not a win count.

The important finding was that specialist review could make the evidence less flattering.

In one case, `accept-operations-role-startup`, the broad read was:

> material improvement candidate

After specialist review preserved lost value, ambition risk, value-overwrite risk, and written-gate proportionality concerns, the read became:

> partial improvement candidate

That is healthy.

It means the eval harness can downgrade itself instead of only producing positive evidence.

## What The Evals Suggest

The early evals suggest Lolla's candidate value is often not a prettier answer.

The candidate value is more often:

- turning vague advice into gates;
- adding thresholds;
- narrowing scope;
- adding stop rules;
- making assumptions visible;
- changing when to act;
- changing what evidence is required before acting.

That is the product direction.

Lolla should be judged by whether it changes decision leverage, not by whether the revised answer feels more polished.

## What The Evals Warn Us About

The evals also warn us not to overclaim.

Current risks:

- The evidence is not human-validated.
- Codex-assisted reads may be biased toward agreement.
- Checked-in-safe summaries may be too compressed.
- Positive cases may be overrepresented.
- There are not enough no-change, noisy, worse, or inconclusive real-case examples.
- The system may over-credit Lolla for improvements already present in the original conversation.
- The revised answer may add caution while losing speed, courage, simplicity, or user-specific ambition.

This is why the eval lane refuses to produce a score.

## What We Can Say Now

We can say:

- Lolla has a coherent offline eval method for studying completed runs.
- The eval method focuses on concrete decision changes, not answer polish.
- The method tracks both useful friction and lost value.
- The method has deterministic overclaim protection.
- The early non-human evidence shows promising candidate deltas.
- The strongest healthy signal is a downgrade from material to partial in one case.

We cannot say:

- Lolla improves decisions generally.
- The candidate labels are correct.
- The evals are calibrated.
- Codex-assisted reads are human review.
- A clean artifact package proves a good answer.
- Agents can use eval outputs as approval.

## What A Board Demo Should Show

A good eval demo should use one case and show:

1. The original answer the user may have acted on.
2. The Lolla revised answer.
3. The likely action before and after.
4. The concrete delta: action, threshold, gate, sequence, scope, or stop rule.
5. The useful friction.
6. The noisy friction risk.
7. The lost value.
8. The interpretation uncertainty.
9. The human question that remains.

The point is not to say:

> Lolla won.

The point is to say:

> Here is what changed, here is why it might matter, here is what we still cannot claim.

## Product Pros

The eval lane gives Lolla:

- a non-naive way to study whether the audit mattered;
- protection against rewarding longer prose;
- a way to find lost value and overcaution;
- a way to preserve disagreement;
- a way to prepare future human review;
- a way to make product evidence more honest before selling the claim.

## Product Cons And Risks

The eval lane can also create false comfort if misunderstood.

Risks:

- People may treat candidate reads as labels.
- People may treat clean lint as proof.
- People may want a simple score.
- The system may produce impressive reports without enough real negative cases.
- Human review is still required for the product claim.

The product must make the boundary visible:

> Evals help us inspect the delta. They do not certify the decision.

## Where The Eval Work Goes Next

The current non-human eval phase should not expand by default.

The next useful step is human review:

- validate or reject the candidate deltas;
- check whether useful friction was actually useful;
- identify noisy friction and lost value;
- correct interpretation mistakes;
- decide which fields are worth showing to users;
- find cases where Lolla did not help.

After that, Lolla can decide whether to:

- simplify the report;
- improve conversation capture;
- add better specialist interpretation;
- create a small user-facing demo;
- or stop adding machinery.

## Source Docs

For implementation-level detail, see:

- [Product Delta Docs Index](../evals/README.md)
- [Product Delta Evidence Thesis](../evals/product-delta-evidence-thesis-v0.md)
- [Product Delta Provisional Report](../evals/product-delta-provisional-report-v0.md)
- [Product Delta Fan-In / Disagreement Report](../evals/product-delta-fan-in-disagreement-report-v0.md)
- [Product Delta Packaging Gate](../evals/product-delta-pr71-pr84-packaging-gate-v0.md)
- [Decision Trail Specialist Pilot Phase Closure Gate](../conversation-understanding/decision-trail-specialist-pilot-phase-closure-gate-v0.md)
