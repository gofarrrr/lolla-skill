# V5 Reviewed Model Capability Audit

**Date:** 2026-05-07
**PR slice:** PR31 - v5 reviewed-model capability audit
**Status:** docs/research audit of the current reviewed affordance corpus; no
extraction, runtime, prompt, lane, model-call, judge, UI, memo, or user-facing
surface
**Decision label:** `v5_capability_audit_complete`

## Blunt Answer

Yes. The current `65` reviewed models can already tell us something important.

They do not tell us "the product is solved." They do not tell us which final
Decision Pressure should surface. They do not tell us the remaining `157`
graph-only models are unimportant.

They do tell us this:

> A reviewed mental-model card is useful when it turns a plausible AI answer
> into operational reasoning material: when to apply a lens, what evidence is
> required, when not to use it, how it is commonly misused, what the answer must
> do differently, and where the source does not support overclaiming.

That is the thing we are testing.

The 65 reviewed models are enough to test whether Lolla can give the next LLM
better reasoning substrate across evidence, uncertainty, risk, resource
allocation, causal diagnosis, incentives, social trust, bias, and learning.

They are not enough for broad product confidence. They are the first working
depth layer.

## Corpus Shape

Current compiled artifact:

`data/compiled/model_affordances/affordances_v5.json`

Measured shape:

| Item | Count |
| --- | ---: |
| Reviewed model records | 65 |
| Reviewed affordances | 101 |
| Absence records | 115 |
| Source-evidence references inside affordances | 889 |
| Treatment requirements | 208 |
| Diagnostic questions | 397 |
| Misuse guards | 372 |
| Runtime graph models | 222 |
| Graph-only runtime models after v5 | 157 |

This matters because the corpus is no longer just "mental model names." It now
contains hundreds of source-backed operational fragments that can be offered to
the next LLM.

## What We Are Checking

We are not checking whether Python can pick the best pressure.

We are checking whether reviewed cards improve the reasoning handoff.

For each reviewed model, the real test is:

1. **Activation clarity**
   Can the card tell the LLM when this model actually applies?

2. **Evidence-needed clarity**
   Can it tell the LLM what must be true in the user/assistant transaction
   before leaning on the model?

3. **Do-not-use clarity**
   Can it tell the LLM when the model would be a bad fit?

4. **Misuse guard usefulness**
   Can it prevent generic, theatrical, or misleading use of the model?

5. **Treatment usefulness**
   Can it tell the LLM what a better answer should do differently?

6. **Absence / overclaim protection**
   Can it say what the source does not support, so the LLM does not invent
   confident-looking structure?

7. **Packet burden**
   Can the card stay compact enough to help reasoning rather than drown it?

This is the current evaluation target.

## What The 65 Can Tell Us

The reviewed corpus can already support eight useful capability families.

These families are reviewer groupings, not deterministic runtime classes. A
model can belong to more than one family.

### 1. Evidence Discipline And Falsification

The corpus can ask:

> What would prove this advice wrong, and what evidence is missing before
> commitment?

Strong reviewed shelves include:

- `falsifiability`
- `scientific-method-evidence-testing`
- `experimentation`
- `chain-of-verification`
- `confirmation-bias`
- `base-rates`
- `statistical-discipline`
- `law-of-large-numbers`
- `survivorship-bias`
- `correlation-vs-causation`
- `root-cause-analysis`
- `five-whys-method`

What this gives the next LLM:

- reversal conditions;
- hypothesis thresholds;
- make-or-break premise chains;
- disconfirming evidence equality checks;
- reference-class discipline;
- hidden denominator recovery;
- causal mechanism checks.

This is one of the strongest current corpus areas.

### 2. Commitment, Trade-Off, And Resource Discipline

The corpus can ask:

> What does this yes displace, what boundary governs it, and what stop or
> exclusion condition is missing?

Strong reviewed shelves include:

- `opportunity-cost`
- `trade-offs`
- `prioritization`
- `constraints`
- `optimization-theory`
- `theory-of-constraints`
- `pareto-principle`
- `comparative-advantage`
- `multi-criteria-decision-analysis`
- `sunk-cost-fallacy`
- `optionality`
- `circle-of-control`

What this gives the next LLM:

- displaced-alternative gates;
- allocation-backed sacrifice;
- capacity-constrained sequencing;
- objective/constraint/trade-off fit;
- constraint-first intervention;
- future-value recommitment;
- reversible learning paths.

This is also strong and directly useful near action.

### 3. Uncertainty, Probability, And Risk

The corpus can ask:

> What kind of uncertainty is this, how confident can we be, and what exposure
> should be bounded before action?

Strong reviewed shelves include:

- `aleatory-epistemic-uncertainty-recognition`
- `true-uncertainty-navigation`
- `probabilistic-thinking`
- `confidence-calibration`
- `expected-value`
- `decision-trees`
- `risk-assessment`
- `calculated-risk-taking`
- `margin-of-safety`
- `black-swan-events`
- `resilience`
- `antifragility`

What this gives the next LLM:

- uncertainty-type routing;
- range and sensitivity checks;
- earned confidence sizing;
- branch triggers and branch kills;
- thresholded downside governance;
- evidence-sized buffers;
- robust actions under ambiguity.

This is strong for "before you act" pressure.

### 4. Causal And Systems Diagnosis

The corpus can ask:

> Is this advice treating symptoms, isolated parts, or correlations as if they
> were the real causal machine?

Strong reviewed shelves include:

- `systems-thinking`
- `complex-adaptive-systems`
- `emergence`
- `leverage-points`
- `network-effects`
- `second-order-thinking`
- `decomposition`
- `inversion`
- `first-principles-thinking`
- `problem-framing-and-reframing`
- `occams-razor`
- `lindy-effect`

What this gives the next LLM:

- recurring-event structure checks;
- feedback-loop maps;
- interaction-produced behavior checks;
- critical-mass proof before naming network effects;
- downstream reversal stress tests;
- test-cuts before trusting branches;
- frame assumption exposure.

This is good, but it is broad. It needs careful packet caps so it does not
become "systems prose."

### 5. Incentives, Agency, Information, And Power

The corpus can ask:

> Who has information, incentives, authority, downside exposure, or bargaining
> leverage that the advice is underweighting?

Strong reviewed shelves include:

- `incentives`
- `principal-agent-problem`
- `moral-hazard`
- `adverse-selection`
- `information-asymmetry`
- `power-dynamics`
- `authority-bias`
- `social-proof`

What this gives the next LLM:

- reward-structure maps before behavior judgment;
- delegated alignment drift audits;
- downside exposure alignment;
- hidden-type selection filters;
- observability redesign for party-controlled evidence;
- outside-option credibility;
- domain-bound deference checks;
- independent dissent channels.

This is useful but still incomplete. Competitive-dynamics and negotiation
coverage remain too thin.

### 6. Bias, Metacognition, And Correction

The corpus can ask:

> Is the advice being pulled by anchors, authority, consensus, preferred
> conclusions, or unearned confidence?

Strong reviewed shelves include:

- `anchoring`
- `confirmation-bias`
- `authority-bias`
- `social-proof`
- `survivorship-bias`
- `intellectual-humility`
- `confidence-calibration`
- `inversion`
- `step-back`

What this gives the next LLM:

- provisional-anchor correction;
- disconfirming-evidence equality;
- context-matched proof instead of generic social proof;
- corrigible confidence review;
- disconfirmation before defense;
- reorientation before execution.

This is strong for "unknown unknown" discovery because the user often does not
ask for these checks.

### 7. Learning, Experiment Design, And Adaptation

The corpus can ask:

> What would we have to test, bound, or learn before this recommendation
> becomes safe enough to act on?

Strong reviewed shelves include:

- `experimentation`
- `scientific-method-evidence-testing`
- `falsifiability`
- `antifragility`
- `resilience`
- `optionality`
- `complex-adaptive-systems`
- `leverage-points`

What this gives the next LLM:

- hypothesis-bound tests that must move a decision;
- variable-separated causal probes;
- bounded stress learning;
- disciplined recovery with continued function;
- reversible paths to buy learning;
- ordered adaptive learning loops.

This is product-relevant because it turns "think harder" into "test this
before commitment."

### 8. Human Context, Trust, And Team Process

The corpus can ask:

> What stakeholder context, candor, trust, or interpersonal signal would change
> whether the advice should be followed?

Reviewed shelves include:

- `empathy`
- `psychological-safety`
- `johari-window`
- `power-dynamics`
- `flow`
- `six-thinking-hats`

What this gives the next LLM:

- stakeholder evidence before reframing;
- reflection that requires confirmation, not diagnosis;
- withheld-risk signal checks;
- candor converted into correction;
- specific feedback/disclosure loops;
- mode-separated deliberation.

This family is useful but not deep enough yet. It needs more conversation,
communication, and cross-cultural models before we trust it broadly.

## What The 65 Cannot Tell Us Yet

The current reviewed corpus is useful, but uneven.

It cannot yet give enough reviewed depth for:

1. **Competitive dynamics and negotiation**
   The old PhD competitive-dynamics blank is still a warning. Models like
   `batna`, `game-theory-payoffs`, `nash-equilibrium`, `prisoners-dilemma`, and
   `red-queen-effect` remain graph-only.

2. **Delay, obligation, control, and procedural discipline**
   Existing static lane signals still point at graph-only models such as
   `delays`, `obligations-controls-mapping`, `formal-reasoning`, and
   `checklists`.

3. **Peer review and external correction**
   `peer-review-your-perspectives` remains graph-only even though it has strong
   lane signal and fits the receiver-review/product doctrine well.

4. **Product/customer/market framing**
   `jobs-to-be-done`, `user-centered-design`, `lock-in`, and
   `path-dependence` remain graph-only. These matter if Lolla is used for
   product, founder, or strategy advice.

5. **Communication and relational judgment**
   `active-listening`, `constructive-feedback-models`,
   `feedback-models-sbi`, and `cross-cultural-communication-frameworks`
   remain graph-only. This limits emotionally or organizationally textured
   cases.

6. **Planning and status quo bias**
   `optimism-bias-and-planning-fallacy`, `status-quo-bias`,
   `commitment-bias`, and related models remain graph-only. These are likely
   to matter near action.

7. **Analogical and abductive reasoning**
   The reviewed corpus has comparatively light coverage of analogical and
   abductive reasoning types. This does not break the current packet strategy,
   but it means Lolla is stronger at operational checks than creative analogy
   or explanatory inference.

## What The Absence Records Tell Us

The `115` absence records are not leftovers. They are part of the knowledge.

They say things like:

- do not turn `five-whys-method` into emotional why-loops;
- do not turn `authority-bias` into blind credential deference;
- do not turn `first-principles-thinking` into ignoring constraints;
- do not turn `chain-of-verification` into exhaustive sign-off theater;
- do not turn `step-back` into indefinite reflection;
- do not turn `probabilistic-thinking` into fake exact point estimates;
- do not turn `social-proof` into automatic compliance.

This is important because much of Lolla's value is not only adding thoughts.
It is preventing the next LLM from using a mental model in the cheap generic
way.

## What We Can Achieve With The 65

With the current reviewed corpus, we can credibly test this product thesis:

> When existing lanes nominate candidate shelves, reviewed affordance cards can
> give the next LLM better operational reasoning material than graph-only model
> names and summaries.

We can especially test whether Lolla improves advice by adding:

- falsification gates;
- evidence requirements;
- stop / kill / dismissal conditions;
- downside thresholds;
- resource trade-off clarity;
- causal mechanism checks;
- hidden incentive and information checks;
- uncertainty-type routing;
- bias and overclaim guards;
- compact next-action discipline.

That is enough for meaningful internal testing.

It is not enough for:

- product launch;
- user-facing claims;
- broad domain confidence;
- full 222-model parity;
- deterministic pressure selection;
- "we can find any unknown unknown."

The honest claim is narrower:

> We now have enough reviewed depth to test whether enriched reasoning packets
> improve downstream LLM judgment in several high-value decision-pressure
> families.

## Next Enrichment Direction

We should not extract the remaining `157` by count momentum.

But we also should not stop.

The next controlled enrichment batch should fill gaps that are both:

1. likely to be nominated by existing lanes or product-relevant decision
   moments; and
2. likely to add operational handoff depth that graph-only cards cannot carry.

Recommended next controlled batch:

1. `delays`
2. `obligations-controls-mapping`
3. `peer-review-your-perspectives`
4. `formal-reasoning`
5. `checklists`
6. `status-quo-bias`
7. `commitment-bias`
8. `optimism-bias-and-planning-fallacy`
9. `batna`
10. `game-theory-payoffs`
11. `red-queen-effect`
12. `jobs-to-be-done`
13. `user-centered-design`
14. `lock-in`
15. `path-dependence`
16. `cross-cultural-communication-frameworks`

This is not broad Batch 3b. It is a controlled depth patch aimed at current
capability gaps:

- action-delay and obligation discipline;
- peer review and correction;
- procedural/formal reasoning;
- planning/status quo/commitment bias;
- competitive and bargaining pressure;
- product/customer/market lock-in;
- cross-cultural communication.

If any source does not support operational depth, the correct output is an
absence record or `do_not_promote_recommendation`, not a forced affordance.

## Decision

`v5_capability_audit_complete`

The 65 reviewed records are good enough to support serious handoff testing and
targeted enrichment. They are not enough to stop enriching, and they are not
enough to promote runtime behavior.

The next production-oriented slice should be a controlled extraction batch
against the recommended gap list, unless product review explicitly chooses to
run a receiver-side LLM review first.
