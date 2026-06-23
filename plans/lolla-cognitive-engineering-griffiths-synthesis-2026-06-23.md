# Lolla Cognitive Engineering Synthesis

**Date:** 2026-06-23  
**Source:** User-provided transcript from David Eagleman's *Inner Cosmos* interview with Tom Griffiths about *The Laws of Thought*  
**Purpose:** Preserve how the transcript sharpens Lolla's product thesis, reasoning-trace design, eval direction, and System 2 framing.

## Core Takeaway

The Griffiths conversation is unusually relevant to Lolla because it gives a cleaner intellectual frame for the product.

Lolla is not trying to be "another LLM that thinks harder."

Lolla is trying to add explicit inductive bias, structure, uncertainty handling, and trace to AI-assisted reasoning.

Short version:

> Lolla supplies explicit cognitive scaffolding around probabilistic AI.

Sharper version:

> Lolla adds engineered inductive bias to AI-assisted reasoning.

That matters because Griffiths describes intelligence as a hybrid of:

1. **Rules and symbols**: structure, logic, procedures, compositional reasoning.
2. **Networks, features, and spaces**: similarity, fuzziness, embeddings, pattern recognition.
3. **Probability and statistics**: uncertainty, priors, evidence updates, resource-limited inference.

Lolla already spans all three, but we have not been describing it this cleanly.

## Why This Strengthens Lolla's Thesis

Modern LLMs are powerful because they mainly operate through learned representations and probability distributions:

- high-dimensional feature spaces,
- fuzzy similarity,
- next-token prediction,
- learned priors from massive training data,
- probabilistic language modeling,
- enormous scale.

But serious decisions need more than fluent probabilistic output. They need explicit System 2 scaffolding:

- rules,
- schemas,
- traces,
- mental models,
- counter-models,
- evidence gates,
- uncertainty registers,
- reversibility checks,
- outcome review.

This is Lolla's product opening:

> LLMs provide fluent System 1 reasoning. Lolla adds a local System 2 process around the reasoning before it becomes action.

The product should not claim that it knows the "laws of thought." It should claim that partial cognitive formalisms can already improve decision work:

- uncertainty,
- priors,
- evidence,
- mental models,
- reversibility,
- incentives,
- feedback loops,
- resource limits,
- accountable trace.

## Mapping Griffiths' Three Lenses To Lolla

### 1. Rules And Symbols

This maps to Lolla's formal accountability layer.

Examples:

- `ReasoningTrace`
- `CommitmentCandidate`
- `DecisionPacket`
- `DecisionLedger`
- schemas
- policy checks
- gate statuses
- owner/approver fields
- impact classification
- reversibility classification
- rollback fields
- required evidence
- artifact hashes

This layer turns a messy AI-assisted conversation into something inspectable.

For Lolla, the implication is clear:

> Normalization is not bureaucracy. It is how cognition becomes inspectable.

The PRD's "Trace first. Gateway second." framing is consistent with this. Before Lolla can judge or gate a decision, it has to normalize a fuzzy conversation into a structured trace.

### 2. Networks, Features, And Spaces

This maps to Lolla's fuzzy semantic layer.

Examples:

- embeddings,
- semantic recall,
- V60 candidate retrieval,
- mental-model similarity,
- frame matching,
- tendency detection,
- companion-lane model matching,
- suppressed-lens discovery.

This is where Lolla sees things a rigid rules engine would miss.

But the transcript gives an important warning:

> Fuzzy similarity is powerful, but it is not truth.

Therefore embedding hits should be preserved as retrieval/rank signals, not treated as proof that a model applies.

This supports the current graph-survival design:

- selected does not mean correct,
- rejected does not mean useless,
- suppressed does not mean noise,
- unselected lenses may still change the user's view later.

### 3. Probability And Statistics

This maps to Lolla's uncertainty layer, which is still underdeveloped.

Current partial examples:

- `risk-vs-uncertainty`,
- `premortem`,
- `optionality`,
- `expected-value`,
- `confidence-calibration`,
- `regret-theory`,
- `true-uncertainty-navigation`.

Missing or underbuilt examples:

- prior assumptions,
- evidence for,
- evidence against,
- uncertainty type,
- confidence,
- what would change the recommendation,
- factual verification status,
- outcome review.

This may be the most important next conceptual layer. Lolla should not pretend to assign exact probabilities to messy decisions, but it can capture Bayesian-style updates.

Example future artifact:

```json
{
  "claim": "B is worth taking if family and diligence gates clear",
  "prior_assumption": "The user's dissatisfaction is meaningful signal",
  "evidence_for": ["year-long distraction", "startup pull", "current org blocked"],
  "evidence_against": ["family volatility", "A may be real scope", "startup risk"],
  "uncertainty_type": "true_uncertainty",
  "what_would_change_the_view": ["CEO boundary failure", "weak equity terms", "wife soft no"]
}
```

This would bring Lolla closer to Griffiths' idea of probability as a grammar of uncertainty.

## The Inductive Bias Insight

The most important concept from the transcript is inductive bias.

Griffiths explains that humans learn efficiently because we do not start from nowhere. We have priors, constraints, and inductive biases. Current neural networks are more general-purpose and data-hungry because their inductive biases are weaker or differently shaped.

This gives Lolla a strong explanation of its mental-model graph:

> The graph is an explicit inductive-bias layer for reasoning.

Not merely:

> A collection of mental models.

The graph says:

- when a decision has commitment pressure, consider reversibility;
- when a plan sounds emotionally compelling, run a premortem;
- when the user is comparing options, look for opportunity cost;
- when a recommendation is smooth, check hidden assumptions;
- when a model is tempting but unsupported, use absence records to block misuse;
- when a lens is suppressed, preserve it because it might matter later.

LLMs have learned priors from training data. Lolla adds curated priors from cognitive science, decision theory, strategy, behavioral economics, and the user's own local trace history.

This gives us a strong product phrase:

> Lolla is engineered inductive bias for AI-assisted reasoning.

## Why This Is More Than Prompting

The transcript helps explain why "just ask the LLM to think harder" is not enough.

Griffiths describes jagged intelligence: an AI system can look brilliant on one problem and fail weirdly on an adjacent one.

That is exactly Lolla's product wedge.

Lolla exists because:

- LLM reasoning is fluent but jagged.
- Human reasoning is resource-limited.
- Serious decisions need more than polished recommendation text.
- A second process can impose lenses the first process did not naturally select.
- The process must be traceable because the answer alone is not enough.

For the June 22 career-decision case, Lolla did not merely "red team" the answer. It forced the answer through structured opposition:

- trade-offs,
- premortem,
- status quo,
- optionality,
- spouse/stakeholder alignment,
- reversibility,
- risk versus uncertainty,
- suppressed alternatives.

Concrete shift:

- "If wife says yes, take B" became "spouse yes is necessary, not sufficient."
- "A is delay" became "A may be a paid diagnostic if the role has real scope."
- "We can afford it" became "what family trade-offs are being bought with money, stress, evenings, and optionality?"
- "Do startup diligence" became story-based diligence about CEO behavior, missed deadlines, boundaries, runway, cap table, and reversal triggers.

That is System 2 value in practice.

## Evals Implication: Cognitive-Science Style, Not Scoreboard Style

Griffiths says benchmarks are useful as engineering tools, but cognitive scientists want to know how a system solves or fails a problem.

This is directly relevant to Lolla.

We should not evaluate Lolla only with:

> Did the answer get better?

That is too vague.

We should evaluate it like a cognitive science experiment:

- What misconception did the original answer carry?
- Which lens exposed it?
- Which lens was offered but rejected?
- Did the final answer change structurally?
- Did the user view change?
- Did the suppressed lens later matter?
- Did a future outcome reveal a missed failure mode?
- Did the system over-apply a model?
- Did it create useful friction or process theater?

This implies diagnostic eval cases, not generic benchmark scores.

For the career-decision case, contrast conditions could include:

- spouse strongly supports B,
- spouse gives only a soft yes,
- A has title but no authority,
- A has real authority,
- startup has clean terms,
- startup has weak equity terms,
- CEO respects boundaries,
- CEO gives vague hustle answers,
- family finances are robust,
- family finances are fragile.

Then ask:

> Does Lolla's reasoning shift in the right places?

That is closer to cognitive-science-style eval than "score the final answer."

## Curiosity As A Product Feature

The transcript's discussion of curiosity is unexpectedly useful.

Griffiths describes curiosity as attention to things that appear often enough to matter, but not so often that they are already understood.

This maps well to the trace archive.

Lolla should eventually detect:

- a suppressed mental model that appears across several runs,
- a repeated private guardrail,
- a recurring missing-evidence type,
- a repeated user decision pattern,
- a repeated false alarm,
- a repeated outcome failure,
- a model that never changes the answer but often changes the user's view.

This could become a local "curiosity queue."

Example:

```json
{
  "curiosity_signal": "regret-theory repeatedly suppressed in career-risk cases",
  "frequency": "4 of 7 similar traces",
  "status": "worth_reviewing",
  "reason": "Appears often enough to be a pattern, not so often that it is generic"
}
```

This is a useful bridge from local traces to private evals.

## Proposed New Artifact: Reasoning Update Register

The best practical artifact inspired by the transcript is a `reasoning_update_register`.

Purpose:

- capture Bayesian-style update without pretending we have exact probabilities,
- show how the audit changed the answer,
- distinguish "answer became longer" from "reasoning actually updated",
- create a clean object for future evals,
- connect final advice to uncertainty and evidence.

Possible shape:

```json
{
  "reasoning_update_register": [
    {
      "claim_or_recommendation": "...",
      "prior_frame": "...",
      "new_evidence_or_lens": "...",
      "update_type": "strengthened | weakened | reframed | gated | rejected",
      "uncertainty_remaining": "...",
      "what_would_change_this": "..."
    }
  ]
}
```

Example from the career case:

```json
{
  "claim_or_recommendation": "Take B if spouse conversation goes well",
  "prior_frame": "Spouse consent treated as decisive gate",
  "new_evidence_or_lens": "Trade-offs, premortem, stakeholder alignment, optionality",
  "update_type": "gated",
  "uncertainty_remaining": "Startup operating reality and family resilience unknown",
  "what_would_change_this": "Weak equity terms, CEO boundary failure, spouse soft no"
}
```

This would be a strong next trace/eval object because it measures reasoning movement, not merely artifact presence.

## Reorganizing The Missing-Data List

The transcript suggests reorganizing missing data into four layers.

### A. Symbolic / Rules Layer

Needed for accountability:

- owner,
- approver,
- action,
- impact,
- reversibility,
- rollback,
- policy,
- evidence required,
- gate status.

This is DecisionPacket work.

### B. Feature / Similarity Layer

Needed for lens selection:

- embedding hits,
- graph candidates,
- selected lenses,
- suppressed lenses,
- model similarity,
- frame matches,
- companion anchors.

This is what graph survival is beginning to preserve.

### C. Probabilistic / Uncertainty Layer

Needed for reasoning quality:

- prior assumptions,
- evidence for,
- evidence against,
- uncertainty type,
- confidence,
- what would update the view,
- factual verification status,
- outcome review.

This is currently underbuilt.

### D. Resource-Rationality Layer

Needed to avoid analysis paralysis:

- time pressure,
- information budget,
- cost of more thinking,
- decision deadline,
- cognitive load,
- acceptable friction,
- when to stop analysis.

This matters because Lolla cannot just say "think forever." The product needs a theory of enough.

## Rerun Inspection Framework

When inspecting the next Lolla rerun, use the Griffiths lens:

1. **Rules/symbols:** Did it produce structured trace artifacts, commitments, ledgers, and graph survival?
2. **Features/spaces:** Did embeddings and graph selection preserve useful candidate lenses and suppressed lenses?
3. **Probability/uncertainty:** Did the revised answer name uncertainty, evidence gates, and what would change the recommendation?
4. **Inductive bias:** Did the curated substrate introduce a lens the original LLM answer did not naturally choose?
5. **Resource rationality:** Did it add useful friction without turning the decision into endless analysis?
6. **Jaggedness control:** Did it catch an adjacent failure where the original answer sounded smart but generalized badly?

## Product Positioning

Possible positioning lines:

> Lolla is engineered inductive bias for AI-assisted reasoning.

> Lolla turns fluent AI reasoning into inspectable decision process.

> Lolla adds System 2 scaffolding around probabilistic AI.

> Lolla is a local reasoning trace layer for moments where AI reasoning may become commitment.

> Lolla does not promise the correct answer. It preserves how the reasoning was structured, challenged, updated, and later judged.

## Main Warning

The transcript also warns against overclaiming.

The "laws of thought" are not finished. Different formalisms illuminate different parts of cognition. None is the whole mind.

Therefore Lolla should not claim:

> We found the correct reasoning.

It should claim:

> We made the reasoning process more inspectable, more structured, more uncertainty-aware, and more accountable.

That is the right level of ambition.

## Bottom Line

The Griffiths conversation strengthens Lolla's thesis.

It says intelligence is hybrid, resource-limited, prior-shaped, and not reducible to one smooth answer. That is exactly why Lolla should exist.

The most important phrase for us is:

> Engineered inductive bias for AI-assisted reasoning.

That is what the deterministic graph, mental models, V60 affordances, absence records, trace ledger, and local eval history can become.

The next product step is not to claim Lolla has discovered the laws of thought. It is to build artifacts that preserve how reasoning was structured, challenged, updated, and eventually judged against outcomes.

