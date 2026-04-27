# E1 — Verifier stochasticity

Date: 2026-04-27
Branch: `data/lane2-experiment-e1-verifier-stochasticity-2026-04-27`
Design memo: `research/lane2-producer-stability-design-2026-04-27.md`
Prior experiments: `e5-consensus-simulation.md`, `e4-broad-meta-sufficiency-rubric.md`, `e2-recall-determinism.md`
Runs JSON: `research/stability-runs/lane2-stability-experiments-2026-04-27/e1-verifier-stochasticity-runs.json`

## Scope

Tests **H1** from the design memo:

> The verifier is stochastic on identical input.

The narrow question:

> Given the same source, same fingerprint moves, and the same 60-candidate slate, does the verifier accept the same models every time?

This is the first paid LLM experiment in the §9 ordering. E2 cleared recall as a stochastic source under embeddings-off. The verifier is now isolatable: any acceptance churn observed here is verifier-side, not recall-side or fingerprint-side.

## Frozen input

- **Case**: `user-launch-independent-fintech` (post-fix archive)
- **Fingerprint**: rerun4 `companion_fingerprint_validated` — 8 validated moves with evidence quotes. Same payload as E2.
- **Assistant text**: rerun4 conversation Turns 1–8 ASSISTANT messages, joined with `\n\n`. 7108 chars.
- **Candidate slate**: deterministic 60-model list from E2. First five model_ids: `representativeness-heuristic, commitment-bias, learning-curve, principal-agent-problem, cultural-intelligence`. Identical across all 5 runs by E2's verdict.
- **Knowledge graph**: `data/knowledge_graph.json` (222 models).
- **Embeddings**: off.
- **Verifier model**: production default via `OpenAICompatibleBoundaryClient` against the same provider/key the audit pipeline uses.

The frozen slate is byte-identical across runs. Only the verifier LLM call varies.

## Method

```python
for run in range(1, 6):
    result = run_verification_call_from_packet(packet, candidates)
    record(result.accepted_ids, result.rejected_ids, result.repaired_ids)
```

Per-run output:
- count of accepted models
- ordered list of accepted `model_id`
- ordered list of rejected `model_id`
- count and list of `model_id` whose evidence quote was repaired during this run

Cross-run comparison:
- **Set equality**: do all 5 runs accept the same set of `model_id`?
- **Count stability**: same total accept count?
- **Pairwise Jaccard** of accept sets across the 10 unordered pairs.
- **Per-anchor surfacing rate** (fraction of runs in which each surfaced anchor was accepted).

## Results

### Per-run accepted sets

| Run | Accept count | Accepted `model_id` (sorted) | Quote repairs |
|---:|---:|---|---|
| 1 | 5 | checklists, cognitive-dissonance, **reasoning-mode-router**, time-tested-validation, wysiati | TTV |
| 2 | 5 | checklists, cognitive-dissonance, **reasoning-mode-router**, time-tested-validation, wysiati | optionality (rejected post-repair), TTV |
| 3 | 5 | checklists, cognitive-dissonance, **optionality**, time-tested-validation, wysiati | TTV |
| 4 | 5 | checklists, cognitive-dissonance, **optionality**, time-tested-validation, wysiati | none |
| 5 | 5 | checklists, cognitive-dissonance, **reasoning-mode-router**, time-tested-validation, wysiati | none |

Bolded entries are the run-varying anchors. Counts are stable at 5 in every run; **membership is not**.

### Per-anchor surfacing rate

| `model_id` | Runs accepted (of 5) | Surfacing rate |
|---|---:|---:|
| `checklists` | 5 | 1.00 |
| `cognitive-dissonance` | 5 | 1.00 |
| `time-tested-validation` | 5 | 1.00 |
| `wysiati` | 5 | 1.00 |
| `reasoning-mode-router` | 3 | 0.60 |
| `optionality` | 2 | 0.40 |

Six unique surfaced anchors across N=5. Four are stable (5/5). Two are stochastic (3/5 and 2/5). RMR and Optionality are mutually exclusive across these runs — no run accepted both. The 5-anchor count is preserved by RMR ↔ Optionality substitution.

### Pairwise Jaccard

| Statistic | Value |
|---|---:|
| min | 0.667 |
| mean | 0.800 |
| max | 1.000 |

The minimum 0.667 corresponds to RMR-runs vs Optionality-runs (4 shared / 6 union). Three pairs are identical (1.00) — runs 1↔2, runs 3↔4, run 1↔5 / 2↔5.

### Quote repair behavior

Time-tested-validation's evidence quote was repaired in runs 1, 2, 3 and accepted directly without repair in runs 4, 5. **TTV is 5/5 accepted regardless of whether the quote needed repair.** This is verifier-side variance in *how* it processes the evidence, not in *whether* it accepts the model.

Optionality's quote was repaired in run 2 and rejected post-repair in that run; accepted directly without repair in runs 3, 4. RMR was accepted in runs 1, 2, 5, none of which required RMR-specific quote repair — RMR's verifier acceptance is a direct judgment call, not a quote-repair-mediated path.

This contradicts a comfortable reading from the smoke characterization (where 7/7 noisy anchors entered Step 6 via direct literal verifier acceptance, not quote repair). E1 confirms: even on identical input, the verifier judges some borderline anchors differently across runs without any quote-repair mediation.

## H1 verdict — supported, with structure

**H1 is supported.** The verifier is stochastic on identical input.

Specifically:
- **4/6 unique anchors are stable** across all 5 runs (mean Jaccard 0.800, min 0.667).
- **2/6 unique anchors are stochastic** (RMR 3/5, Optionality 2/5). They never co-occur in this sample, suggesting the verifier is choosing between them on judgment calls about adjacent models.
- The accept count is exactly 5 in every run.
- Variance is concentrated at the *boundary* of acceptance, not throughout the slate. The same broad core is accepted every run; the marginal slot moves.

This is **H1 supported but bounded**. The verifier is not chaotic. It has a stable core and a stochastic edge.

## H4 — strongly strengthened

E4's anchor sufficiency audit classified `cognitive-dissonance` and `checklists` as gate-buildable broad/meta anchors that the verifier was over-accepting on the smoke evidence. **E1 confirms they are not random failures.** They are accepted in 5 of 5 verifier runs on this case. The verifier is reliably and stably wrong on this class of anchors on this conversation, exactly as H4 predicts.

This is the **load-bearing finding for architecture**:

| Anchor | E5 (post-fix N=4 reruns) | E1 (verifier N=5 same input) | Pattern |
|---|---|---|---|
| cognitive-dissonance | 2/4 | 5/5 | recurs across reruns AND stable across verifier judgments on identical input → verifier-stable failure |
| checklists | 2/4 | 5/5 | same pattern |
| reasoning-mode-router | 0/4 (not in post-fix smoke surfacing) | 3/5 | newly-visible; verifier accepts as judgment call without quote repair |
| optionality | 1/4 | 2/5 | rare-acceptable diversity (H5-shaped) |
| time-tested-validation | 1/4 | 5/5 | verifier-stable accept, sufficiency-borderline (E4 medium confidence) |

The pattern: **verifier-stable acceptances include both clearly-acceptable anchors (wysiati, broadly defensible per source-first gold) and the noisy-adjacent failures (CD, Checklists) E4 identified as gate-buildable.** Path A's sufficiency gate would catch the failure class without endangering the legitimate acceptances.

## H5 — partial, refined

The stochastic edge (RMR ↔ Optionality) is shaped like H5: different runs surface different defensible-or-borderline reads of the same source. But the stable failures are NOT honest hypothesis diversity — they are stable verifier mistakes. H5 covers the marginal slot, not the body of the acceptance set.

E1 sharpens E5's H5-partial reading: H5 is real for **rare anchors**, not for the overall variance. The dominant variance source is **stable verifier failure on broad/meta anchors (H4) plus marginal stochastic substitution at the boundary (H1)**. H5 is product-relevant for the boundary anchors only.

## Hypothesis state after E1

| Hypothesis | Pre-E1 status | Post-E1 status |
|---|---|---|
| **H1 — verifier stochasticity** | open | **SUPPORTED** with structure: stable core + stochastic edge. Mean Jaccard 0.800. |
| H2 — fingerprint variance | open; tested last by E3 | open. E1 isolated verifier-only variance; E3 still tests whether fingerprint adds churn on top. |
| H3 — recall is deterministic | SUPPORTED (E2) | unchanged |
| H4 — broad/meta sufficiency blind spot | strongly supported (E4) | **further strengthened**: CD and Checklists 5/5 stable on identical input → verifier-stable failures, not random. |
| H5 — honest hypothesis diversity | partially supported (E5) | refined: H5 lives at the boundary (RMR ↔ Optionality), not in the stable body. |

## §7 decision-tree application

The §7 row that fires:

> **H1 supported, H4 supported (verifier stochastic AND sufficiency rubric exists) → Path A or B. Both are local fixes. Pick based on engineering cost and Path B's prior-attempt history.**

E1 + E4 together fire this row. Path C (consensus) was already ruled out by E5. Path D (Sully decomposition) remains premature: the evidence still points to a specific upstream problem at the verifier/sufficiency layer, not a fundamental decomposition failure.

The Path A vs Path B discrimination from E4 stands: hybrid (A for the 5/9 gate-buildable anchors including CD and Checklists; B for the 3/9 prompt-only anchors). E1 reinforces the priority of Path A specifically — the 5/5-stable broad/meta failures are the cleanest target for a deterministic sufficiency check and the loudest cost in the current acceptance set.

## E3 — still worth running, scope reduced

E1 used a FROZEN fingerprint payload (rerun4's validated moves). The 2/6 stochastic anchors observed are **purely verifier-judgment variance, not fingerprint variance bleeding through.** E3 still has work:

- E3 tests whether running the fingerprint LLM call N=5 times on the same source produces stable validated-move output, or whether fingerprint moves themselves vary run-to-run.
- If fingerprint is stable: the smoke-rerun variance (rerun4–7 produced 14 unique anchors) traces almost entirely to the verifier (E1 effect) and not to upstream churn.
- If fingerprint is unstable: the smoke variance is partly fingerprint-mediated (different validated moves → different recall keyword fields → different candidate slates → different verifier inputs).

E3's outcome doesn't change the §7 decision tree's first lever recommendation (Path A or B from E1+E4), but it determines whether the fingerprint stage needs its own treatment in the implementation track.

## Implications

1. **Hybrid Path A + Path B is the leading architecture for the next deliverable.** E1 + E4 fire the §7 "H1 + H4 supported" branch.
2. **Path A applies first to the 5/5-stable broad/meta failures.** The deterministic sufficiency gate has its strongest target in Cognitive Dissonance and Checklists. These are the anchors that recur stably across both rerun-level (E5) and verifier-judgment-level (E1) variance.
3. **Path B applies to the prompt-only anchors from E4.** Verifier-prompt restructuring covers the gate-resistant cases.
4. **Time-tested-validation is the next stress-test case.** It's 5/5-stable but E4 classified it as medium-confidence sufficiency. If a Path A gate accidentally rejects TTV under the rubric tightening for CD/Checklists, that's a regression. The rubric must distinguish.
5. **The marginal RMR ↔ Optionality slot is product-relevant.** Architectures that suppress the boundary anchor in pursuit of single-canonical stability would lose H5's contribution. Whatever Path A+B implementation is chosen, the marginal slot should be allowed to remain a marginal slot, not be forced into hard determinism.
6. **Reasoning-mode-router surfacing without quote repair is a live concern.** PR #44 closed the trust-breach via quote repair. E1 shows RMR can still be accepted via direct verifier judgment in 3/5 runs. This is a Path A or B target, not a quote-repair gap.

## Pre-registered scope of E1 not exceeded

Per design memo §5: E1 measures verifier acceptance churn given identical input. It does not:
- score quality of accepted anchors against a gold label (covered by audit synthesis and the source-first gold table)
- propose or test an architectural fix (next deliverable, separate memo)
- run on more than one case (case 1 was the smoke source; future Path A+B implementation work should validate against additional cases per the audit infrastructure protocol)

## What this experiment did NOT do

- Did not test cross-conversation generalization. RMR's reappearance and the CD/Checklists stability are case-1-specific until tested on Marcus, case 3, and case 7.
- Did not test how Step 6 consumes the verifier's accept set. Verifier 5/5 stability for CD does not mean Step 6 will surface CD; the audit found Step 6 sometimes drops verifier-accepted anchors.
- Did not test whether `temperature` settings or other LLM parameters could reduce the boundary stochasticity. That is a parameter-tuning question, not a hypothesis-discrimination question.
- Did not run on `--embeddings on`. If embeddings change the candidate slate, E1's verifier read against this specific slate doesn't generalize. E2's embeddings-off scope carries into E1 by design.

## Status

- E1: **complete**. H1 supported (mean Jaccard 0.800, stable core + stochastic edge). H4 strongly strengthened.
- E3 (fingerprint variance): **next**, per design memo §9 ordering. Last paid LLM experiment in the investigation.
- §7 decision tree: **Path A or B branch fires**. Hybrid implementation track is the leading next deliverable.
- Architecture: still not committed. The implementation memo will be written after E3 closes the upstream variance question.

The measurement leads. E1 says: verifier is stochastic but bounded; the stable failures are exactly the anchors E4 said a sufficiency gate could catch. Path A + B is the lever. E3 next.
