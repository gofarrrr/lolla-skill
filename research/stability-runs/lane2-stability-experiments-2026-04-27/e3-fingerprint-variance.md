# E3 — Fingerprint variance

Date: 2026-04-27
Branch: `data/lane2-experiment-e3-fingerprint-variance-2026-04-27`
Design memo: `research/lane2-producer-stability-design-2026-04-27.md`
Prior experiments: `e5-consensus-simulation.md`, `e4-broad-meta-sufficiency-rubric.md`, `e2-recall-determinism.md`, `e1-verifier-stochasticity.md`
Runs JSON: `research/stability-runs/lane2-stability-experiments-2026-04-27/e3-fingerprint-variance-runs.json`
Downstream-slate JSON: `research/stability-runs/lane2-stability-experiments-2026-04-27/e3-fingerprint-variance-downstream-slates.json`

## Correction note (2026-04-27, pre-merge)

The initial draft of this report contained two factual errors that have been corrected against the saved JSON artifacts:

1. **"`optionality` and `reasoning-mode-router` appear in 0/5 fresh-fingerprint slates" — false.** Both anchors are in **all 5** slates (Optionality at positions 3, 7, 7, 8, 10; RMR at positions 13, 14, 15, 21, 31). E1's RMR/Optionality substitution is therefore **pure verifier-side variance**, not a slate-presence artifact.
2. **"Same 7 reasoning moves recur across all 5 runs" — over-smoothed.** The high-level *trajectory* is consistent, but granularity varies across runs (run 1 splits trajectory into 8 moves; runs 3–5 introduce a "signal vs noise" theme that runs 1–2 lack). The corrected framing is "trajectory-stable, granularity-moderately-unstable, text-unstable."

Both errors originated in writing from memory rather than re-checking the JSON. Numerical claims (Jaccard 0.519/0.6151/0.7391, union 89, intersection 30, validated counts 8-7-7-7-7) were verified correct against the runs JSON. The corrected sections are: §"Direct stability summary," §"Anchor slate-presence across runs" (renamed from "Noisy-anchor robustness"), §"H2 verdict," §"Hypothesis state," §"§7 decision-tree application — Why Path A or B is still the first lever."

## Scope

Tests **H2** from the design memo:

> The fingerprint LLM is stochastic. Different runs produce different validated moves on the same source.

Two narrow questions:

1. **Direct**: Given the same source, does the fingerprint LLM produce the same validated move list every time?
2. **Downstream**: If the fingerprint output varies, does that variance propagate into a different candidate slate when fed to the (deterministic per E2) recall step?

Question 2 is the load-bearing one. E2 proved recall is deterministic given fixed fingerprint input. That leaves "fingerprint as input variance source" as the open question.

## Frozen input

- **Case**: `user-launch-independent-fintech` (same archive as E1, E2, E5)
- **Source**: archived `extraction.json` + `conversation.txt` from the 20260424T123050Z archive (16-turn packet, 8 assistant turns)
- **Knowledge graph and reasoning signals**: same files used in E2.
- **Fingerprint LLM**: production default via `OpenAICompatibleBoundaryClient` (same provider as E1).
- **Fingerprint cap**: 8 (top-k validated moves, sorted by confidence then move_id, per `companion_routing.run_fingerprint_call_from_packet`).

## Method

### Direct fingerprint stability (5 LLM calls)

```python
for run in range(1, 6):
    payload = run_fingerprint_call_from_packet(packet, client)
    record(payload.validated)
```

For each run, capture:
- `validated_count` (number of validated moves after the cap)
- per-move `move_id`, `reasoning_move` (free text), `evidence_quotes` (list), `confidence`

### Downstream slate test (zero LLM cost)

For each of the 5 fingerprint outputs, call `recall_candidates` with embeddings off and the same source / knowledge graph / reasoning signals. Record the resulting 60-candidate slate.

This isolates fingerprint variance as the only varying input. If slates differ, fingerprint variance has downstream impact even with deterministic recall (per E2).

## Results

### Direct fingerprint output

| Run | Validated count | Distinct `reasoning_move` strings | Distinct evidence-quote lists |
|---:|---:|---:|---:|
| 1 | 8 | (5 unique vs other runs) | (4–5 unique vs other runs) |
| 2 | 7 | 5 | 4 |
| 3 | 7 | 5 | 3 |
| 4 | 7 | 5 | 4 |
| 5 | 7 | 5 | 5 |

The LLM emits `move_id` as a sequential ordinal index (`"1"`, `"2"`, ...), so move-id-set comparison is meaningless across runs (the set `{"1"..."7"}` always intersects). The semantic identity of each move lives in the `reasoning_move` and `evidence_quotes` fields.

**Validated count is mostly stable (7), with one outlier (run 1: 8).** Run 1 split runway-assessment into a distinct move (#3) and split fractional-specifics into its own move (#7) — both of which other runs absorb into adjacent moves. The cap (top 8) was hit only by run 1; the other runs returned <8 to begin with.

**Reasoning-move strings vary on every run.** All 5 runs emit 5 distinct `reasoning_move` strings per ordinal slot. The high-level reasoning trajectory is consistent (clarify before tactics → challenge optimistic assumptions → prioritize fundamentals → generate multi-option tradeoffs → insist on specific spouse alignment → conditional/checkpoint commitment), but the LLM rephrases each move on every run AND chooses a different granularity (see split-vs-merge below).

**Evidence-quote lists vary on every run.** For each move slot present in all 5 runs, the LLM selects 2–5 distinct evidence-quote sets. Some runs return shorter, more focused quotes; others return longer, multi-sentence spans; some compress multiple quotes into one or split one quote into multiple.

**Confidence is stably "high"** for every move in every run.

### Direct stability summary

- **Trajectory stability**: HIGH. The same high-level reasoning trajectory recurs across all 5 runs: *clarify before tactics → challenge optimistic assumptions → prioritize fundamentals over tactics → generate multiple options with tradeoffs → insist on specific spouse alignment → conditional/checkpoint commitment.*
- **Granularity instability**: MODERATE. The trajectory is split into different numbers of moves across runs:
  - **Run 1** (8 moves) separates "runway assessment with industry timelines" (#3) from "challenge optimistic assumptions" (#2), and separates "actionable specifics for fractional roles" (#7) from "conditional checkpoint" (#8).
  - **Runs 2, 3, 4** (each 7 moves) collapse runway-assessment into challenge-assumptions and merge fractional-specifics into adjacent moves.
  - **Run 5** (7 moves) restores runway-assessment as a distinct move (#3) — like run 1 — but absorbs fractional specifics elsewhere.
  - **Runs 3, 4, 5** introduce a "signal vs noise / emotion vs evidence" theme as a distinct move; runs 1 and 2 do not.
- **Textual stability**: LOW. Free-text fields (`reasoning_move`, `evidence_rationale`) and evidence-quote selection vary every run, even where the underlying move is the same.
- **Count stability**: NEAR-STABLE. Validated count is 7 in 4/5 runs, 8 in 1/5.

A surface-level move-id-set comparison would say "intersection 7/7, jaccard 1.0" — that is misleading because the LLM is emitting ordinal placeholders, not semantic identifiers. The substantive variance is in: (1) granularity of the move split, (2) free-text phrasing, and (3) evidence-quote selection. All three feed downstream.

### Downstream slate variance

Feeding each of the 5 fingerprint outputs into `recall_candidates` (embeddings off, same source, same KG, same reasoning signals):

| Statistic | Value |
|---|---:|
| Per-run slate count | 60, 60, 60, 60, 60 (cap hit every run) |
| Distinct ordered slates | **5** (no two runs produced byte-identical slate ordering) |
| Distinct set-equivalent slates | **5** |
| Slate set union size | 89 unique model_ids |
| Slate set intersection (in all 5 slates) | 30 model_ids |
| Pairwise Jaccard min | 0.519 |
| Pairwise Jaccard mean | **0.615** |
| Pairwise Jaccard max | 0.739 |

**Fingerprint textual variance produces substantial downstream slate variance.** Five distinct fingerprint outputs produce five distinct 60-candidate slates. Half the slate (30/60) is common across all runs; the other half rotates with the fingerprint phrasing.

For comparison:
- E2 (frozen fingerprint, recall N=5): Jaccard 1.000. Recall is deterministic given fixed input.
- E3 (varying fingerprint, recall once each): Jaccard 0.615. Recall remains deterministic, but its input changes enough that the slate composition shifts substantially.

### Anchor slate-presence across runs

Slate-presence (was the anchor `model_id` in the top-60 candidate slate produced from each fresh fingerprint?) measured directly from the runs JSON. **In-slate is distinct from accepted-by-verifier**; this section covers presence only.

| Anchor | In slate (of 5) | Missing run | E1 verifier behavior |
|---|---:|---|---|
| `cognitive-dissonance` | 4/5 | run 5 | accepted 5/5 (E1 stable) |
| `checklists` | 4/5 | run 1 | accepted 5/5 (E1 stable) |
| `time-tested-validation` | 4/5 | run 2 | accepted 5/5 (E1 stable) |
| `wysiati` | 5/5 | none | accepted 5/5 (E1 stable) |
| `reasoning-mode-router` | 5/5 | none | accepted 3/5 (E1 stochastic edge) |
| `optionality` | 5/5 | none | accepted 2/5 (E1 stochastic edge) |

Two distinct patterns:

1. **Verifier-stable failure class (CD, Checklists, TTV)** is missing from exactly 1/5 fresh-fingerprint slates. Fingerprint variance hides each from the slate ~20% of the time. **A Path A sufficiency gate would catch each anchor in 80% of fresh runs and not see it in 20%.** That is a real residual for Path A's reach.
2. **E1 stochastic-edge anchors (RMR, Optionality)** are present in **all 5** fresh-fingerprint slates (RMR positions 13–31; Optionality positions 3–10). Their E1 substitution churn (RMR 3/5, Optionality 2/5 accepted) is therefore **purely verifier-side**, not slate-presence-mediated. The verifier sees both candidates on every run and chooses one to accept.

This correction strengthens E1's reading: **E1's RMR/Optionality substitution is pure verifier variance under the tested slate conditions, not a fingerprint-input artifact.**

## H2 verdict — supported, with structure

**H2 is supported.** The fingerprint LLM is stochastic on identical input.

Specifically:
- **High-level trajectory is stable** (same 6-step reasoning trajectory recurs across all 5 runs).
- **Granularity is moderately unstable** (run 1 splits trajectory into 8 moves; runs 2–5 into 7, with different absorption choices; runs 3–5 introduce a "signal vs noise" move that runs 1–2 do not).
- **Textual representation is unstable** (5 distinct `reasoning_move` phrasings per slot, 2–5 distinct evidence-quote selections per slot).
- **The variance has downstream impact**: 5 distinct candidate slates, pairwise Jaccard mean 0.615.

H2 is **supported but bounded**, similar to H1's structure: the LLM is not chaotic; the high-level reasoning is consistent. But the granularity choices and surface output that downstream stages consume vary enough to produce non-trivial slate divergence.

## Hypothesis state after E3

| Hypothesis | Pre-E3 status | Post-E3 status |
|---|---|---|
| H1 — verifier stochasticity | SUPPORTED with structure (E1) | **strengthened**: RMR/Optionality are 5/5 in fresh-fingerprint slates, so their E1 churn is pure verifier variance, not slate-presence-mediated |
| **H2 — fingerprint variance** | open | **SUPPORTED with structure**: trajectory-stable, granularity-unstable, text-unstable, downstream Jaccard 0.615 |
| H3 — recall is deterministic | SUPPORTED (E2) | unchanged |
| H4 — broad/meta sufficiency blind spot | strongly supported (E4) + further strengthened (E1) | **further strengthened**: CD, Checklists, TTV are each in 4/5 fresh-fingerprint slates (~20% per-anchor slate-rotation miss) — survives fingerprint variance the majority of runs |
| H5 — honest hypothesis diversity | partially supported (E5), refined (E1) | unchanged. RMR and Optionality remain marginal at the **verifier acceptance** layer (E1: 3/5 and 2/5 accepted), even though they are slate-stable. Their churn is verifier-side judgment diversity, not slate-input diversity |

## Smoke variance — full decomposition

The five-rerun smoke (PR #44 characterization, rerun4–7) produced 14 unique anchors. After E1, E2, and E3, the variance decomposes as:

1. **Fingerprint stage (H2)**: text-variable evidence quotes → ~Jaccard 0.615 in candidate slate composition
2. **Recall stage (H3)**: deterministic given fixed fingerprint input — does not contribute additional churn
3. **Verifier stage (H1)**: ~Jaccard 0.800 on fixed slate; stable core (5/5) + stochastic edge (RMR ↔ Optionality substitution)
4. **Step 6 stage**: not in scope of this investigation

The compound effect: fingerprint variance produces different slates (Jaccard 0.615), each of which then gets verified with ~80% Jaccard stability. Both stages are sources of churn. The 14-unique-anchor smoke result is consistent with the multiplicative effect of these two variance sources.

## §7 decision-tree application

Two §7 rows now have evidence:

> **H1 supported, H4 supported (verifier stochastic AND sufficiency rubric exists) → Path A or B.** (fired by E1+E4)

> **H2 supported (fingerprint unstable) → Path D variant — Sully decomposition starting at the fingerprint stage. Span extraction needs to be more disciplined before downstream stages can stabilize.**

The §7 tree is pre-registered. Both rows are now firing. The implementation track must address both, but order matters:

### Why Path A or B is still the first lever

1. **Path A targets the verifier-stable failure class** (CD, Checklists, TTV). Each is in 4/5 fresh-fingerprint slates (~20% per-anchor slate-rotation miss rate). For the 80% of runs where the gate sees the bad anchor, a sufficiency gate catches it. For the 20% where slate rotation hides the anchor, the gate doesn't get to act — that residual is the boundary of Path A's reach and the natural Path D-fingerprint trigger surface.
2. **Path D variant for fingerprint is more invasive.** It would refactor the extraction stage. The trust-axis benefit per unit cost is bounded by the residual after Path A+B (per-anchor slate-rotation miss rate observed at ~20% on this case).
3. **Path A and Path D-fingerprint are independent**, not competing. Path A goes between verifier-acceptance and Step 6; Path D-fingerprint changes the upstream input. Both can be implemented; the question is order.
4. **The implementation memo should commit to Path A+B first**, then evaluate Path D-fingerprint as a follow-on track based on residual noise classified as slate-rotation-mediated after Path A+B ships.

### What Path D-fingerprint would target (for the implementation memo)

If Path D-fingerprint is pursued in a second track, the candidate moves are:
- **Constrain output format**: shorter, structured `reasoning_move` (LLM tends to phrase the same move in 5 ways across 5 runs, suggesting less freedom would not lose information).
- **Canonicalize evidence quotes**: shortest substring that supports the move; deterministic post-processing.
- **Move splitting/joining policy**: run 1's 8th move was the same content as runs 2–5's 6th move with finer subdivision. A policy on minimum granularity could stabilize count.

These are not architectural commitments; they are options the implementation memo can pick from after Path A+B is in place.

## Implications

1. **Hybrid Path A + Path B remains the first lever.** E3 reinforces, not replaces, the E1+E4 recommendation.
2. **The implementation memo should be a single deliverable**, with Path A+B as the committed first track and Path D-fingerprint flagged as a contingent second track.
3. **The audit-corpus reusability protocol now has both single-run and multi-run validation requirements**: any Path A+B implementation must be tested against the audit corpus single-run AND against ≥4 fresh post-fix reruns of case 1 to verify the noisy-recurrence pattern (CD, Checklists) is now caught by the gate. Two-layer reporting per the methodology amendment.
4. **The §7 tree was a good investment.** Pre-registration means we don't have to relitigate which path to choose — the evidence picks the lever.
5. **E1 + E2 + E3 together close the producer-stability investigation phase.** No further variance-isolation experiments are needed before architecture commitment. The implementation memo is the next deliverable.

## What this experiment did NOT do

- Did not generalize to other cases. Fingerprint variance on Marcus and case 3 may have different structure. Path D-fingerprint scoping would need cross-case data before committing.
- Did not test fingerprint with `--embeddings on`. If embeddings change downstream slate sensitivity to fingerprint phrasing, the Jaccard 0.615 number would shift.
- Did not score fingerprint quality against a gold reference. The trajectory-stability claim is from reading the runs and noting all 5 produce the same high-level trajectory; a gold-labeled fingerprint quality test was not part of this experiment's scope.
- Did not evaluate whether the per-run slate's intersection (30 models) is "the right 30 models." That is a recall-vocabulary question (PR #43 leak mode 1).
- Did not test fingerprint determinism under `temperature=0` or other LLM parameter settings. That is a parameter-tuning question, not a hypothesis-discrimination question.

## Status

- E3: **complete**. H2 supported with structure (trajectory-stable, granularity-unstable, text-unstable, downstream Jaccard 0.615).
- All 5 pre-registered experiments closed: E1 ✓, E2 ✓, E3 ✓, E4 ✓, E5 ✓.
- §7 decision tree: **two rows fire.** Path A+B is the first lever (E1+E4). Path D-fingerprint is a contingent second track (E3).
- **Next deliverable: implementation memo** — single document committing to Path A+B as first track and Path D-fingerprint as contingent second track. The investigation phase is closed; architecture commitment is the next decision.

The measurement leads. E3 says: fingerprint produces text variance with downstream impact. Combined with E1 and E2, the smoke variance is now fully decomposed. Path A+B is the first lever; the implementation memo is next.
