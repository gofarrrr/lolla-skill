# Problem and Thesis

This page explains why Lolla exists. For the runtime sequence, read
[../../HOW_IT_WORKS.md](../../HOW_IT_WORKS.md) first.

## The Problem

AI advice is now cheap, fast, and fluent. That changes the failure mode.

The old problem was: "Can the model answer at all?"

The new problem is: "Can I tell when a good-sounding answer has weak
structure?"

Strategic advice fails in ways that are hard to see from the final prose:

- The answer inherits the user's frame instead of testing it.
- A constraint is acknowledged once and then disappears from the recommendation.
- A risky option gets called "worth it" without a stop rule.
- A safe option gets dismissed as delay without testing its upside.
- A spouse, employee, customer, regulator, or stakeholder is treated as a
  variable instead of an actor with their own constraints.
- The answer sounds balanced because it mentions both sides, but it never names
  what evidence would change the conclusion.

More context does not reliably fix this. Better prose does not fix this. A
second generic model can help, but it often shares the same conversational
gravity: be helpful, be coherent, make the user feel understood, and converge.

The missing layer is structured counter-pressure.

## The Thesis

Lolla's core thesis is:

> AI advice needs a reasoning audit layer that is separate from answer
> generation.

That layer should do four things:

1. **Read the conversation, not just the topic.** It should understand the
   actual decision, constraints, open threads, and the answer being audited.
2. **Detect reasoning shape.** It should notice premature closure, inherited
   framing, missing reversal conditions, weak evidence gates, and untested
   assumptions.
3. **Route through curated knowledge.** It should not invent "be careful"
   commentary. It should connect the detected pattern to a reviewed substrate
   of mental models, failure modes, premortem questions, and antagonistic
   lenses.
4. **Make the revision accountable.** The assistant should have to say what
   survived, what it takes back, and what actually changes.

The point is not to make the model sound more cautious. The point is to make
the decision process less blind.

## Why Mental Models

Lolla is named after the Lollapalooza effect: Munger's idea that major
misjudgment often happens when several cognitive tendencies reinforce each
other.

That is a useful lens for AI advice because bad recommendations are often
compound failures:

- overoptimism plus authority pressure
- social proof plus availability
- doubt avoidance plus sunk cost
- framing effects plus missing reversibility
- vivid personal desire plus weak evidence gates

Munger's 25 tendencies give Lolla a failure ontology: a vocabulary for the
recurring ways reasoning goes wrong. The 222-model substrate gives Lolla a
correction vocabulary: models that can challenge, deepen, or reframe the
answer.

The bridge between them is the product. Lolla is not "this is a business
question, use game theory." It is closer to:

> The answer treats a spouse's support as sufficient approval for a family-risk
> decision. That is a reasoning-shape problem: permission is being confused
> with operating terms. Route to models that force stakeholder load, stop-loss
> criteria, and reversibility into view.

That is why the system reads structure before topic.

## What Lolla Is

Lolla is a knowledge-first reasoning-about-reasoning engine.

It does not try to be the world's best domain expert. It tries to make the next
answer harder to trust blindly.

The system combines:

- a captured conversation
- structured extraction of the decision shape
- four independent audit lanes
- a curated substrate of mental models and cognitive tendencies
- private source-backed enrichment
- output and live-transcript hygiene
- archive-time graph survival and reasoning-trace manifests
- optional usefulness and outcome review artifacts

The public product is the revised answer. The system product is the run record.

## What Success Looks Like

Lolla succeeds when the revised advice is more decision-useful than the first
answer because it now includes one or more of these:

- a sharper question
- a real walk-away condition
- an evidence gate decided before desire takes over
- a narrower recommendation
- a safer sequence
- a better distinction between necessary and sufficient conditions
- a named failure mode
- a stakeholder or operational cost the first answer underweighted
- a valid reason to set aside a critique instead of overcorrecting

It does not need to reverse the original answer to be useful. Often the best
run says: "The direction still holds, but it needs these gates before it earns
the confidence I gave it."

## What It Is Not

Lolla is not:

- a fact-checker
- a compliance classifier
- a domain expert replacement
- a generic "devil's advocate" prompt
- a guaranteed truth machine
- a system that forces every surfaced lens into public prose

The deepest design constraint is humility: the system cannot know the future.
It can only make the reasoning process more explicit, better challenged, and
more inspectable.

## Why The Archive Matters

Early versions of reasoning tools often end at the final answer. Lolla treats
that as insufficient.

A real audit needs custody:

- What conversation was captured?
- Which model calls ran?
- Which lenses were selected?
- Which lenses were suppressed because of budget?
- Which private chunks were used, rejected, deferred, or kept as guardrails?
- Did the live transcript leak old-case content?
- Did the provider return unexpected metadata?
- Did the user later find the audit useful?
- Did a later outcome show a suppressed lens was important?

That is why Lolla archives `reasoning_trace.json`, `graph_survival_report.*`,
run-health metadata, run events, private ledgers, usefulness reviews, and
outcome reviews. The vision is not only a better answer today. It is a corpus
of reasoning audits that can teach us where the system helps, where it
overreaches, and what kinds of structural pressure actually change decisions.
