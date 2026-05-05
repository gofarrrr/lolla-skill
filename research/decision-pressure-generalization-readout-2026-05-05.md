# Decision Pressure Generalization Readout

**Date:** 2026-05-05
**Status:** No-paid product readout from archived cases. Not formal Gate 4
evidence, not a generated v4 run, not runtime integration, not UI, not
user-facing promotion, not a prompt change, and not extraction.

**Branch:** `feature/decision-pressure-pr23-generalization-readout`

**Decision label:** `generalization_signal_positive_but_not_runtime_ready`

**Doctrine:**

> Surface pulls extraction. Extraction does not push the product.

> Decision Pressure is a compact safeguard before action, not raw gap-question
> output.

> Coverage transparency is a feature, not an apology.

> Decision Pressure is strongest when it compresses a messy situation into one
> source-backed safeguard before action. It is weakest when treated as a full
> extra analysis layer.

## Anti-Casuistry Boundary

This artifact must not become a case catalog.

PR23 reviews five archived cases to test whether the Decision Pressure surface
travels. It does not authorize deterministic rules like:

- whistleblower cases get `risk-response`;
- money/friend cases get `principal-agent-problem`;
- real-estate cases get `margin-of-safety`;
- messy personal cases get a decomposition template;
- archived gap labels map directly to pressure templates.

Those would be casuistic shortcuts: they look scalable because they are
repeatable, but they would make Python imitate semantic judgment badly.

The deterministic system may enforce:

- schema shape and required fields;
- maximum selected-pressure count;
- runtime-dormant policy;
- provenance-class validity;
- source-affordance references existing in the compiled corpus;
- explicit coverage gaps when referenced records are missing;
- blocked-surface declarations;
- review-only counts, IDs, and drift reports.

The deterministic system must not:

- choose which pressure is good;
- infer a pressure from case type, route label, keyword, or gap label;
- rank novelty, tone, actionability, or user usefulness;
- merge pressures based on semantic similarity;
- smooth missing coverage into generic model-name reasoning;
- generate user-facing pressure prose;
- treat repeated PR23 examples as templates for future cases.

Stable gates are allowed as reviewer instructions and schema constraints:
Coverage, Action-Delta, Dismissal, Compression, Bloat, and Tone. They are not
allowed to become deterministic semantic scoring unless a future proposal
defines a separate, falsifiable boundary and proves it improves review without
creating hidden routing rules.

The scaling thesis is:

> Reviewed source-backed records plus LLM/reviewer judgment should generalize;
> case-type heuristics should not.

Falsifiers for the current direction:

- new cases require special case-type rules to produce useful pressure;
- two reviewers cannot converge without seeing PR13/PR23 examples;
- the compact surface only works when a human silently repairs coverage gaps;
- pressure selection starts depending on keyword matching or route labels;
- the trace fixture becomes a library of examples to imitate rather than a
  contract to validate.

## Question

Does the Decision Pressure surface generalize beyond the original PR13 3-case
Gate 4 packet, or did we overfit to equity / mother / PhD?

Short answer:

> It generalizes directionally. Across five different archived cases, the same
> discipline can compress Lane 4 gaps into case-level "before acting, verify
> this" pressure. But the result is still a product readout, not runtime
> evidence. The strongest signal is not novelty; it is clear-thinking
> operationalization: thresholds, gates, sequencing, dismissal paths, and
> coverage honesty.

## Method

Inputs:

- `research/test-cases/README.md`
- `research/test-cases/CORPUS-SUMMARY-2026-04-23-v2.md`
- `research/test-cases/phase2b-lane4-equivalence-2026-04-23/lane4-quality-report.md`
- `research/test-cases/phase2b-lane4-equivalence-2026-04-23/_scratch/*_new_run*.json`
- `research/test-cases/case_*_conversation.txt`
- `data/compiled/model_affordances/affordances_v4.json`
- PR18/PR19/PR21 Decision Pressure trace doctrine

Cases reviewed:

- `whistleblower`
- `multi_offer`
- `friendship_money`
- `real_estate`
- `messy_three_problems`

This readout used existing archived synthetic-case artifacts. It made no model
calls and ran no judges. It did not claim that a runtime producer can generate
these pressures. It asked whether a reviewer can apply the Decision Pressure
surface to fresh archived cases while preserving compression, provenance, and
coverage honesty.

Each case is treated as its own run. The product test is not "select exactly
one pressure forever." The product test is:

> Can the system produce a compact, source-backed pressure that improves the
> user's position before action, or honestly say why it cannot?

## Corpus Context

The archived corpus intentionally spans professional, personal, sparse, messy,
emotional, and high-stakes cases. The v2 corpus summary says all 10 cases pass
the strategic gate after the personal-stakes gate fix.

Lane 4 archived outputs are useful here because they already expose structural
gaps. They are also noisy: raw gap questions are not the product surface. In
these five cases, new-path Lane 4 typically produced 4-5 gap dimensions and
8-15 gap questions per run. Decision Pressure must compress, not display.

## Case Readouts

### 1. `whistleblower`

**Case shape:** Mid-level consultant saw a senior partner shredding client
documents tied to an active regulatory audit. The original advice moves toward
documenting the event, telling spouse carefully, retaining a whistleblower
attorney, and avoiding independent investigation.

**Stable Lane 4 gaps:** `commitment-reversibility`,
`stakeholder-alignment`; additional gaps included `risk-response`,
`competitive-dynamics`, `resource-allocation`, and `incentive-alignment`.

**Selected pressure:**

The reporting path may become irreversible before counsel has defined the stop
conditions and family-risk boundary.

**What to verify:**

Before filing, verify the attorney-governed decision rule: what evidence would
cause counsel to recommend filing, delaying, narrowing, or not filing; what the
family financial runway is if employment breaks; and what the user must not do
without counsel.

**Why it matters:**

The answer correctly pushes toward legal counsel, but "call a lawyer, then
file" can still become a one-way escalator if the user does not know what would
pause or narrow the path. The user's mortgage, kids, spouse, current meetings,
and firm retaliation risk are not side details; they define the survivability
of the reporting plan.

**Dismiss if:**

Counsel gives a clear filing path, the spouse understands the employment-risk
scenario, the family has a runway plan, personal/work-device exposure is
handled, and the user has a written no-self-investigation rule.

**Tripwire or next action:**

Write the counsel decision rule before any report is filed: file / delay /
narrow / do not file, plus the evidence and risk threshold for each branch.

**Source affordance support:**

- `risk-assessment.thresholded-downside-governance`
- `margin-of-safety.evidence-sized-operating-buffer`
- `true-uncertainty-navigation.scenario-bound-robust-action`

**Coverage status:** `partially_source_backed`

**Suppressed candidates:**

- Senior partner countermove strategy: useful but risks legal-strategy
  overreach.
- Internal-versus-external coalition strategy: useful but counsel should own
  it.
- Former senior manager implication: emotionally salient but not the user's
  immediate decision gate.

**Product read:** Strong. Decision Pressure adds a clear-thinking gate without
pretending to give legal advice.

### 2. `multi_offer`

**Case shape:** Senior SWE choosing between another FAANG, a Series B founding
engineer role, or staying. The original advice converges on a family-aligned
startup diligence path if spouse is truly on board.

**Stable Lane 4 gaps:** `competitive-dynamics`, `information-quality`,
`resource-allocation`, `uncertainty-type`.

**Selected pressure:**

The Series B option is not decision-ready until it has a family operating
constraint and disconfirming diligence gate, not just financial EV and desire.

**What to verify:**

Verify four things before accepting: spouse's real yes, extension from the
startup, two non-interview employee diligence calls, and equity/legal review
that names what would kill the offer.

**Why it matters:**

The user is not choosing between compensation packages. He is testing a life
shape: lower base, startup intensity, spouse as primary earner, young children,
and the desire to build something "mine." Without explicit kill criteria, the
startup pull can convert into a romanticized yes.

**Dismiss if:**

The spouse gives an uncoerced yes, the startup accepts a diligence extension,
equity terms survive legal review, current employees confirm the work pattern,
and the CEO agrees to the family operating constraint.

**Tripwire or next action:**

Ask for the 10-14 day extension before deciding. If the startup refuses a
reasonable diligence window or the spouse is a soft no, treat Option B as not
currently feasible.

**Source affordance support:**

- `opportunity-cost.displaced-alternative-commitment-gate`
- `falsifiability.disconfirming-reversal-gate`
- `information-asymmetry.redesign-party-controlled-evidence`
- `probabilistic-thinking.range-and-sensitivity-decision-gate`
- `true-uncertainty-navigation.scenario-bound-robust-action`

**Coverage status:** `fully_source_backed`

**Suppressed candidates:**

- Competitive candidate / startup deadline dynamics: useful but not the main
  user-risk.
- FAANG Option A as two-year bridge: useful memo material, but subordinate to
  the immediate B feasibility gate.
- Startup equity EV: important, but too easy to turn into false precision.

**Product read:** Very strong. This is the cleanest generalization signal.
Decision Pressure turns a vivid career story into a concrete acceptance gate.

### 3. `friendship_money`

**Case shape:** User wants to decline a best friend's request for another
`$10K` after `3` prior asks totaling `$5K` unpaid. The original advice ends on
a `$2K` gift plus legal aid / city resources path.

**Stable Lane 4 gaps:** `commitment-reversibility`, `risk-response`,
`stakeholder-alignment`; additional gaps included `incentive-alignment` and
`timing-sequencing`.

**Selected pressure:**

The smaller `$2K` offer can still become the next precedent unless the user
states the future-money boundary at the same time as the help.

**What to verify:**

Verify that `$2K` is a gift the user can afford to lose, that any partner or
household stakeholder is aligned, and that the offer includes an explicit
future boundary: no additional loans or emergency money without structural
steps already underway.

**Why it matters:**

The original answer wisely avoids the `$10K` loan trap. But a smaller gift
without a future boundary may preserve the same pattern under a more
reasonable-looking amount. The product value is not harshness toward the
friend; it is protecting the friendship from another ambiguous "loan/help"
cycle.

**Dismiss if:**

The user is comfortable treating `$2K` as a non-recoverable gift, the household
impact is acceptable, and the friend accepts non-money help without making the
friendship contingent on more cash.

**Tripwire or next action:**

Use one sentence in the conversation: "I can do this `$2K` gift and help with
legal aid / city resources; I cannot lend more money after this."

**Source affordance support:**

- `risk-assessment.thresholded-downside-governance`
- `opportunity-cost.displaced-alternative-commitment-gate`
- `principal-agent-problem.delegated-alignment-drift-audit`

**Coverage status:** `partially_source_backed`

**Caution:**

`principal-agent-problem` support must stay medium-confidence and non-accusatory.
The pressure is about the structure of repeated requests and unclear
obligation, not suspicion about the friend.

**Suppressed candidates:**

- Child-support enforcement: useful next action, already present in the answer.
- Ex-husband responsibility: true, but can pull the user into someone else's
  legal process.
- Friendship survival test: emotionally important, but too sharp for compact
  user-visible pressure without tone review.

**Product read:** Good but tone-sensitive. Decision Pressure generalizes to
personal emotional cases only if it avoids blame and keeps the boundary humane.

### 4. `real_estate`

**Case shape:** Couple deciding whether to raise a house offer in a bidding war
despite known renovation needs, limited renovation savings, and a spouse who
wants to stretch higher.

**Stable Lane 4 gap:** `commitment-reversibility`; additional gaps included
`risk-response`, `resource-allocation`, `timing-sequencing`,
`uncertainty-type`, and `competitive-dynamics`.

**Selected pressure:**

The bid ceiling is not just the purchase price; it is the purchase price plus
year-one repair sequence plus emergency buffer.

**What to verify:**

Before raising the offer, write the year-one cash stack: mandatory electrical,
roof timing, kitchen stopgaps, emergency reserve, and the boiler-or-hidden-
defect scenario.

**Why it matters:**

The original answer correctly lands on a `$925K` ceiling. Decision Pressure
makes the dismissal path explicit: the ceiling can move only if a real buffer
or new funding source appears. Otherwise the couple is not choosing a house;
they are choosing a no-margin repair exposure.

**Dismiss if:**

The couple can fund mandatory electrical, credible kitchen stopgaps, roof
timing, and a meaningful emergency buffer without consumer debt or marital
stress beyond their stated tolerance.

**Tripwire or next action:**

Tell the spouse: "$925K is the ceiling unless you can show the year-one repair
cash stack and emergency buffer at `$950K`."

**Source affordance support:**

- `margin-of-safety.evidence-sized-operating-buffer`
- `risk-assessment.thresholded-downside-governance`
- `opportunity-cost.displaced-alternative-commitment-gate`
- `probabilistic-thinking.range-and-sensitivity-decision-gate`

**Coverage status:** `fully_source_backed`

**Suppressed candidates:**

- Auction counterparty dynamics: relevant but less important than downside
  affordability.
- Alternative houses / BATNA: useful, but no reviewed `batna` record exists
  yet.
- Renovation sequencing detail: belongs under the cash-stack pressure.

**Product read:** Strong. Decision Pressure makes the clear-thinking move
simple: do not let bidding-war regret hide the repair-state budget.

### 5. `messy_three_problems`

**Case shape:** User is simultaneously dealing with lease non-renewal, a
boyfriend who wants to move in, a Seattle job offer, and a mother beginning to
need more care.

**Stable Lane 4 gaps:** `competitive-dynamics`, `incentive-alignment`,
`stakeholder-alignment`; additional gaps included `information-quality`,
`risk-response`, `resource-allocation`, and `uncertainty-type`.

**Selected pressure:**

The user should not make the Seattle / boyfriend / mother decision until the
lease deadline is decoupled from the life-choice decision.

**What to verify:**

Verify that a short-term rental or sublet can solve the 60-day housing
deadline without forcing a year-long DC lease, cohabitation commitment, or
Seattle decision.

**Why it matters:**

The case feels impossible because four clocks are collapsed into one. The
first clear-thinking move is not to answer Seattle. It is to remove the fake
constraint: "I must solve my whole life before the lease ends." Once the lease
pressure is decoupled, boyfriend commitment, mother's care plan, and Seattle
extension become separate gates.

**Dismiss if:**

No short-term housing option is realistic, the Seattle deadline cannot move,
or the user explicitly chooses to use the offer deadline as the forcing
function.

**Tripwire or next action:**

Spend the next weekend on short-term rental / sublet search while separately
asking Seattle for an extension and scheduling the boyfriend / brother
conversations.

**Source affordance support:**

- `problem-framing-and-reframing.define-before-analysis`
- `problem-framing-and-reframing.test-alternative-frames`
- `prioritization.capacity-constrained-exclusion-and-sequencing`
- `optionality.preserve-reversible-learning`
- `true-uncertainty-navigation.scenario-bound-robust-action`

**Coverage status:** `fully_source_backed`

**Suppressed candidates:**

- Boyfriend specificity test: important, but second after decoupling the lease.
- Mother's cognitive trajectory: important, but second after separating the
  clocks.
- Seattle employer extension: part of the next-action sequence, not the core
  pressure.

**Product read:** Strong. This is the best clear-thinking example in the
generalization sample: the product does not add insight; it removes a false
constraint so the user can think.

## Cross-Case Findings

### 1. Generalization Signal Is Positive

Decision Pressure did not collapse outside the original three cases. It found
useful pressure shapes in:

- ethical/legal-professional risk;
- career/family startup choice;
- friendship and money;
- personal real estate finance;
- messy multi-decision life planning.

This supports the product thesis directionally:

> Decision Pressure is not a domain feature. It is a decision-safeguard
> surface.

### 2. The Value Is Still Operationalization, Not Alien Insight

The selected pressures are not magical. A strong advisor might reach them. The
value is that the surface makes them concrete:

- write the counsel decision rule;
- get spouse yes plus startup kill criteria;
- state the future-money boundary;
- write the repair cash stack;
- decouple the lease clock.

That is monetizable because it helps users act more cleanly. But the public
claim should stay humble:

> Lolla gives you the check you should perform before confidence hardens into
> action.

### 3. Compression Is The Product

Raw archived Lane 4 gap outputs contain too many questions. In the reviewed
cases, each run surfaced multiple gaps and many questions. Showing those
questions would feel like homework. Compressing them into one pressure per case
felt product-shaped.

If Decision Pressure becomes product-visible later, it must remain compact. The
doctrine remains: `1-3` pressures per run, with zero-output allowed.

### 4. Tone Is A Real Product Gate

The personal cases are useful but dangerous:

- `friendship_money` can become accusatory if principal-agent framing is used
  loosely.
- `whistleblower` can overstep into legal advice if the pressure tries to pick
  strategy.
- `messy_three_problems` can overwhelm if the pressure lists every life domain.

The surface must keep its tone: specific, bounded, non-blaming, and
action-clear.

### 5. Coverage Gaps Still Matter

Some archived gaps were dimensions rather than reviewed model affordances:

- `commitment-reversibility`
- `timing-sequencing`
- `competitive-dynamics`
- `batna`-like negotiation outside the reviewed corpus

This does not mean "extract broad Batch 3 now." It means future extraction
should continue to be pulled by repeated surface need. `commitment-reversibility`
and `timing-sequencing` are now plausible future candidates if they keep
blocking pressure quality across more readouts.

### 6. Messy Cases Need Decomposition Before Pressure

`messy_three_problems` shows the right pattern: do not pressure every thread.
First identify the false constraint or binding clock. Decision Pressure should
not become a checklist for each subproblem.

## Decision

`generalization_signal_positive_but_not_runtime_ready`

Interpretation:

- Decision Pressure generalizes directionally beyond the original PR13 packet.
- The strongest product mode is clear-thinking operationalization: gates,
  thresholds, stop conditions, sequencing, and dismissal paths.
- The surface still needs human/reviewer judgment.
- The result does not justify live Observatory, memo, Step 8, Step 6, Lane 4,
  or `/lolla` promotion.
- The result does not justify Batch 3b or a paid Gate 4 rerun by default.

## Recommendation

Move one step forward, but not into live product.

The next useful work should be one of:

1. **Generalization trace fixture, dormant.**
   Represent these five case-level readouts as a reviewed fixture or fixture
   family under the existing `decision_pressure_trace.v1` contract, if the
   contract can handle multi-run readouts without bloat.

2. **Trace contract review.**
   Check whether `decision_pressure_trace.v1` should represent one run only or
   a review packet with multiple case-level traces. Do not change the contract
   yet.

3. **Stop if reviewers think this is enough evidence.**
   The evidence now supports the surface directionally. More infrastructure is
   not automatically better.

Do not build live Observatory yet. Do not build package functions yet. Do not
extract broad Batch 3. Do not rerun paid Gate 4 by default.

## What Remains Blocked

- live Observatory rendering;
- memo integration;
- Step 8 integration;
- Step 6 integration;
- Lane 4 integration;
- `/lolla` runtime use;
- user-facing Decision Pressure blocks;
- prompt changes;
- generation changes;
- new extraction;
- Batch 3b;
- paid Gate 4 reruns by default.
