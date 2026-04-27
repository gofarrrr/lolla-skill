# E2 — Recall determinism

Date: 2026-04-27
Branch: `data/lane2-experiment-e2-recall-determinism-2026-04-27`
Design memo: `research/lane2-producer-stability-design-2026-04-27.md`
Prior experiments: `e5-consensus-simulation.md`, `e4-broad-meta-sufficiency-rubric.md`
Runs JSON: `research/stability-runs/lane2-stability-experiments-2026-04-27/e2-recall-determinism-runs.json`

## Scope

Tests **H3** from the design memo:

> Recall is deterministic; only fingerprint and verifier are stochastic.

The narrow question:

> Given the same fingerprint moves and same source, does recall return the same candidate slate every time?

This is a **zero-cost isolation test**. It is not an evaluation of anchor quality. It does not touch Step 6 or the verifier. It only tests candidate-slate determinism under the conditions used in the smoke (post-fix reruns, `--embeddings off`).

If recall is deterministic, E1 (freeze candidate slate, rerun verifier) becomes a clean test of H1. If recall is not deterministic, the architecture conversation gets more complex before any paid LLM tests are run.

## Frozen input

- **Case**: `user-launch-independent-fintech`
- **Fingerprint source**: `rerun4` (post-fix). Choice rationale: any post-fix rerun would do; rerun4 is the smallest interpretable post-fix sample. The `companion_fingerprint_validated` field gives 8 validated moves with their evidence quotes — the same data the pipeline would feed to `recall_candidates`.
- **Assistant text**: extracted from the archived `conversation.txt` Turn 1–8 ASSISTANT messages, joined with `\n\n` separator. 7108 chars, 8 turns.
- **Knowledge graph**: `data/knowledge_graph.json` — 222 models.
- **Reasoning signals**: `data/curated/reasoning_signals.json` — 217 keys.
- **Embeddings**: disabled (`embedding_retriever=None`, `embedding_api_key=""`).
- **Candidate cap**: 60.

The fingerprint payload is constructed from the validated moves persisted in rerun4's `audit_summary.companion_fingerprint_validated`. No fingerprint LLM call is made. The recall function is called purely against the frozen inputs.

## Method

```python
candidates = recall_candidates(
    assistant_text=<frozen assistant text>,
    fingerprint_payload=<frozen FingerprintPayload from rerun4>,
    knowledge_graph=<frozen 222-model graph>,
    reasoning_signals=<frozen 217-key signals>,
    max_candidates=60,
    embedding_retriever=None,
    embedding_api_key="",
)
```

Repeated N=5 times. Per-run output recorded:

- candidate slate size
- ordered list of `model_id` values
- whether the cap was hit

Cross-run comparison:

- **Set equality**: do all 5 runs return the same set of `model_id`?
- **Order equality**: do all 5 runs return the same ordered list?
- **Count equality**: same total count?

## Results

| Run | Count | First 10 model_ids |
|---:|---:|---|
| 1 | 60 | representativeness-heuristic, commitment-bias, learning-curve, principal-agent-problem, cultural-intelligence, hindsight-bias, inversion, occams-razor, intellectual-humility, wysiati |
| 2 | 60 | (identical) |
| 3 | 60 | (identical) |
| 4 | 60 | (identical) |
| 5 | 60 | (identical) |

Determinism comparison:

| Property | N=5 result |
|---|---|
| Set equality | **TRUE** — same 60 model_ids across all runs |
| Order equality | **TRUE** — identical ordered list across all runs |
| Count equality | **TRUE** — 60 candidates each run |
| Cap hit | TRUE — keyword + reasoning-signals fallback fills the 60-candidate cap; embedding path not invoked |

Full per-run candidate lists in `e2-recall-determinism-runs.json`.

## Determinism verdict

**Recall is deterministic** under the conditions used in the smoke (`--embeddings off`, fixed fingerprint, fixed source, fixed corpus). Set, order, and count are byte-identical across N=5 reruns.

This is consistent with the code structure at `engine/system_b/companion_routing.py:1017-1120`:

- The keyword path iterates `models.items()` and computes `_rank_overlap` deterministically per model.
- The sort key is `(-score, display_name, model_id)` — deterministic tie-breaking by lexicographic display name then model id.
- The reasoning-signals fallback iterates `reasoning_signals.items()` deterministically.
- The embedding path (which would introduce LLM-call stochasticity) is gated by `embedding_retriever is not None and embedding_api_key`, both of which are absent in this test.

There is no source of randomness in the keyword + reasoning-signals path under fixed inputs.

## Hypothesis update

| Hypothesis | Pre-E2 status | Post-E2 status |
|---|---|---|
| **H3** — Recall is deterministic; only fingerprint and verifier are stochastic | open | **SUPPORTED** under embeddings-off conditions |
| H1 — verifier stochasticity | open | open; E1 is now a clean test |
| H2 — fingerprint variance | open | E3 last |
| H4 — broad/meta sufficiency blind spot | strongly supported (E4) | unchanged |
| H5 — honest hypothesis diversity | partially supported (E5) | unchanged |

H3 is supported with one important scope caveat: the smoke variance was observed under `--embeddings off`. If `--embeddings on` is used, the embedding retriever path runs and could introduce its own stochasticity (cosine-similarity ranking against an embedding index, possibly with per-call API behavior). E2 does not test that case. For the variance source question on the smoke evidence, embeddings-off is the right test, and recall is cleared.

## Decision-tree implication

Per the decision rule from Marcin's E2 framing:

> If recall is deterministic: H3 supported. Recall is not the independent stochastic source under fixed fingerprint. Proceed to E1: freeze candidate slate and rerun verifier.

**That branch fires.** Recall is deterministic. The candidate slate the verifier sees on rerun4 is identical every time the recall step runs (assuming the same fingerprint feeds it). The N=5 smoke variance the audit observed must therefore come from at least one of:

- **Verifier stochasticity** (H1) — the verifier sees the same candidate list and judges differently
- **Fingerprint variance** (H2) — different fingerprint moves on different runs lead to different recall inputs and downstream candidate slates
- **Step 6 consumption variance** (different from producer-side, downstream)

The first two are addressable by E1 (freeze candidate slate, rerun verifier) and E3 (rerun fingerprint only). The Step 6 angle is not in scope of the producer-stability investigation.

E1 is now the clean test. If E1 shows the verifier accepts/rejects different models on identical input, H1 is supported. If E1 shows the verifier is stable on identical input, H1 is falsified and H2 (fingerprint variance) is the leading remaining stage.

## What this experiment did NOT do

- Did **not** test recall determinism under `--embeddings on`. The smoke runs were embeddings-off, so this is the right test for the smoke variance question; embedding-induced recall stochasticity is a separate question if embeddings are ever production-default.
- Did **not** evaluate candidate quality. The 60-candidate slate may include models that don't fit the conversation; that's a recall-vocabulary question handled elsewhere (PR #43 audit leak mode #1).
- Did **not** test recall under different fingerprint payloads. If fingerprint variance changes the input to recall (which E3 will test), recall's deterministic-given-fixed-input property still holds, but the candidate slate will differ across runs because the input differed.

## Next experiment

Per design memo §9 ordering: **E1 — freeze candidate slate, rerun verifier** (small LLM cost).

The frozen candidate slate from this experiment (60 model_ids in fixed order) becomes E1's controlled input. Run the verifier N=5 times against:

- the same source (rerun4 assistant text)
- the same fingerprint moves (rerun4 validated)
- the same candidate slate (the deterministic 60 from this experiment)

Score E1's results for verifier acceptance churn on identical input. Decision rule already pre-registered in design memo §5 + §7.

## Status

- E2: **complete**. H3 supported under embeddings-off conditions.
- E1: **next**. Cleanly interpretable now that recall is cleared as a stochastic source on this case.
- §7 decision tree: pending E1 (and E3) outcomes.
- Architecture: still open. Hybrid Path A + Path B (from E4) is the leading candidate, pending E1 to confirm verifier-side variance is the dominant non-fingerprint churn driver.

The measurement leads. E2 says: recall is deterministic. Move to E1.
