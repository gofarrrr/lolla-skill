# Exhaustive candidate assessment transfer result — 2026-07-12

## Decision

The exhaustive assessment contract is mechanically successful and semantically consistent, but it should **not** become a pre-pressure gate. Every museum candidate was assessed exactly once in all three arms, and every candidate was classified `not_applicable`. Building another selector would repeat product drift: asking a probabilistic model to remove the deterministic graph's deliberately non-obvious pressure before the fresh reasoner can inspect it.

The role-record-to-mechanism bridge still requires reliability work. Conditional on a controlled mechanism reaching the graph, however, graph-returned canonical models should be preserved as bounded pressure hypotheses rather than required to win a separate applicability classification.

## Frozen result

- provider calls: 3/3 operational;
- estimated cost: `$0.00072982`;
- exact candidate coverage: passed in all arms;
- canonical and evidence custody: passed;
- unsupported activation: none;
- source/provider active-set invariance: passed trivially;
- protected `premortem` activation: failed;
- active selections: empty in source, provider, and ablation arms.

The source and provider arms independently assigned `not_applicable` to active listening, commitment bias, confirmation bias, intellectual humility, premortem, and sunk-cost fallacy. The ablation assigned `not_applicable` to all three remaining counterpressure candidates.

## What this proves

Removing the global abstention shortcut did not change the semantic outcome. The prior empty outputs were not merely an envelope convenience. Even with full operational mechanism definitions, per-candidate cards, exact coverage, and a different case, the conservative model rejected the entire deterministic recall set.

This is valuable evidence against adding more selection machinery. It does not prove that the models are useless as pressure. Applicability classification asks whether a lens is already justified by the current reasoning. Lolla's graph is meant to supply lenses precisely because they may not already look justified from inside that reasoning.

## Reassessment of the prospective target

The pre-reviewed `premortem` target was defensible as a pressure hypothesis: a pre-commitment pilot lacks a condition for reconsidering whether persistent learning defeats meaningful exit. But the canonical premortem card asks about failure-path mitigation and worst-case exposure, not specifically an exit rule. The graph edge is a recall relation, not entailment that premortem must be classified applicable.

Therefore the failed target should not be repaired into a stronger applicability prompt. The target conflated **worth exposing to a reasoner** with **already established as applicable**.

## Architectural correction

Use the hybrid boundary as originally intended:

```text
probabilistic conversation interpretation
  → controlled fact-free reasoning mechanisms
  → deterministic canonical graph recall
  → bounded pressure portfolio, all items preserved as hypotheses
  → fresh-context reasoner evaluates, applies, rejects, or parks them against the full conversation
```

Deterministic code may cap, deduplicate, preserve provenance, and organize the portfolio. It must not certify relevance. A pre-pressure LLM may summarize cards or formulate questions, but it must not silently delete graph candidates.

The fresh reasoner should receive explicit language:

- these candidates are intentionally noisy;
- graph recall is not evidence of applicability;
- inspect each candidate briefly;
- apply only what changes the reasoning;
- explicitly reject or park the rest;
- preserve those dispositions in the reasoning receipt.

This makes rejection useful evidence instead of allowing it to erase the pressure before reconsideration.

## What remains upstream

The automatic role-record-to-mechanism interpreter has not yet passed invariance. That remains the highest-risk semantic bridge. The canonical model-selection experiments should now stop; they have clarified that the graph output is a recall portfolio, not a second classification target.

## Evidence

- corpus: `research/exhaustive-candidate-assessment-transfer-corpus-2026-07-12/`
- target and contract: `docs/evals/exhaustive-candidate-assessment-transfer-target-v1.json`, `docs/evals/exhaustive-candidate-assessment-transfer-probe-contract-v1.json`
- calls: `research/exhaustive-candidate-assessment-transfer-probe-2026-07-12/`
- preceding problem-class review: `docs/conversation-understanding/canonical-candidate-abstention-problem-class-2026-07-12.md`

