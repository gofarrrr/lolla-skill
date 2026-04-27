# E3 — Fingerprint variance

Date: 2026-04-27
Branch: `data/lane2-experiment-e3-fingerprint-variance-2026-04-27`
Design memo: `research/lane2-producer-stability-design-2026-04-27.md`
Prior experiments: `e5-consensus-simulation.md`, `e4-broad-meta-sufficiency-rubric.md`, `e2-recall-determinism.md`, `e1-verifier-stochasticity.md`
Runs JSON: `research/stability-runs/lane2-stability-experiments-2026-04-27/e3-fingerprint-variance-runs.json`
Downstream-slate JSON: `research/stability-runs/lane2-stability-experiments-2026-04-27/e3-fingerprint-variance-downstream-slates.json`

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

**Validated count is mostly stable (7), with one outlier (run 1: 8).** Run 1's 8th move was "Provide actionable specifics for de-risking options like fractional roles" — a sub-aspect that runs 2–5 absorbed into a single broader move about fractional structure. The cap (top 8) was hit only by run 1; the other runs returned <8 to begin with.

**Reasoning-move strings vary on every run.** All 5 runs emit 5 distinct `reasoning_move` strings per ordinal slot. The semantic content is consistent (same reasoning trajectory: clarifying questions → debunk pipeline assumption → assess runway → prioritize fundamentals → multi-option generation → spouse alignment → fractional ask → conditional launch), but the LLM rephrases each move on every run.

**Evidence-quote lists vary on every run.** For each move slot present in all 5 runs, the LLM selects 2–5 distinct evidence-quote sets. Some runs return shorter, more focused quotes; others return longer, multi-sentence spans; some compress multiple quotes into one or split one quote into multiple.

**Confidence is stably "high"** for every move in every run.

### Direct stability summary

- **Semantic stability**: HIGH. The same 7 reasoning moves recur across all 5 runs (with one extra move in run 1 from a finer split).
- **Textual stability**: LOW. Free-text fields (`reasoning_move`, `evidence_rationale`) and evidence-quote selection vary every run.
- **Count stability**: NEAR-STABLE. Validated count is 7 in 4/5 runs, 8 in 1/5.

A surface-level move-id-set comparison would say "intersection 7/7, jaccard 1.0" — that is misleading because the LLM is emitting ordinal placeholders, not semantic identifiers. The substantive variance is in the free-text and evidence-quote fields, which feed downstream.

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

### Noisy-anchor robustness across slates

The two anchors E1 found verifier-stable (5/5) and E5 found rerun-recurring (CD and Checklists) appear in:

| Anchor | Slates containing (of 5) |
|---|---:|
| `cognitive-dissonance` | 4 |
| `checklists` | 4 |
| `time-tested-validation` | 4 |
| `wysiati` | (in slate intersection — all 5) |

The noisy-recurrence pattern persists through fingerprint variance. The verifier-stable failure class is robustly presented to the verifier even when the slate around them shifts. **A Path A sufficiency gate that catches CD and Checklists would catch them across fingerprint-induced slate variance.**

The H5-shaped marginal anchors are more fragile:
- `optionality` appears in 0/5 of these slates (ordinal cap effect: it ranks below 60 for all 5 fingerprints' keyword scores).
- `reasoning-mode-router` appears in 0/5 of these slates either.

Both surfaced in E1 because E1 used rerun4's specific fingerprint, which happened to push them into the top-60. The fact that fresh fingerprint runs do NOT push them in is consistent with the marginal/boundary character E1 already established for them.

## H2 verdict — supported, with structure

**H2 is supported.** The fingerprint LLM is stochastic on identical input.

Specifically:
- **Semantic content of moves is stable** (same 7 reasoning moves recur across all 5 runs).
- **Textual representation is unstable** (5 distinct `reasoning_move` phrasings per slot, 2–5 distinct evidence-quote selections per slot, 1 extra move in 1/5 runs).
- **The textual variance has downstream impact**: 5 distinct candidate slates, pairwise Jaccard mean 0.615.

H2 is **supported but bounded**, similar to H1's structure: the LLM is not chaotic; the high-level reasoning is consistent. But the surface output that downstream stages consume (evidence quotes, especially) varies enough to produce non-trivial slate divergence.

## Hypothesis state after E3

| Hypothesis | Pre-E3 status | Post-E3 status |
|---|---|---|
| H1 — verifier stochasticity | SUPPORTED with structure (E1) | unchanged |
| **H2 — fingerprint variance** | open | **SUPPORTED with structure**: semantic-stable, text-unstable, downstream Jaccard 0.615 |
| H3 — recall is deterministic | SUPPORTED (E2) | unchanged |
| H4 — broad/meta sufficiency blind spot | strongly supported (E4) + further strengthened (E1) | **further strengthened**: CD and Checklists survive fingerprint variance into 4/5 slates |
| H5 — honest hypothesis diversity | partially supported (E5), refined (E1) | unchanged. RMR and Optionality NOT in any of these 5 fresh fingerprint slates → their E1 surfacing was specific to rerun4's particular fingerprint output |

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

1. **Path A targets the verifier-stable failure class** (CD, Checklists) which survives fingerprint variance into 4/5 slates. The failure recurs across both variance sources. A sufficiency gate that catches it captures the largest single trust improvement.
2. **Path D variant for fingerprint is more invasive.** It would refactor extraction stage. Trust-axis benefit may be smaller per unit cost than Path A.
3. **Path A and Path D-fingerprint are independent**, not competing. Path A goes between verifier-acceptance and Step 6; Path D-fingerprint changes the upstream input. Both can be implemented; the question is order.
4. **The implementation memo should commit to Path A+B first**, then evaluate Path D-fingerprint as a follow-on track based on remaining failure modes after Path A+B ships.

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
- Did not score fingerprint quality against a gold reference. The semantic-stability claim is from reading the runs and noting all 5 produce the same trajectory; a gold-labeled fingerprint quality test was not part of this experiment's scope.
- Did not evaluate whether the per-run slate's intersection (30 models) is "the right 30 models." That is a recall-vocabulary question (PR #43 leak mode 1).
- Did not test fingerprint determinism under `temperature=0` or other LLM parameter settings. That is a parameter-tuning question, not a hypothesis-discrimination question.

## Status

- E3: **complete**. H2 supported with structure (semantic-stable, text-unstable, downstream Jaccard 0.615).
- All 5 pre-registered experiments closed: E1 ✓, E2 ✓, E3 ✓, E4 ✓, E5 ✓.
- §7 decision tree: **two rows fire.** Path A+B is the first lever (E1+E4). Path D-fingerprint is a contingent second track (E3).
- **Next deliverable: implementation memo** — single document committing to Path A+B as first track and Path D-fingerprint as contingent second track. The investigation phase is closed; architecture commitment is the next decision.

The measurement leads. E3 says: fingerprint produces text variance with downstream impact. Combined with E1 and E2, the smoke variance is now fully decomposed. Path A+B is the first lever; the implementation memo is next.
