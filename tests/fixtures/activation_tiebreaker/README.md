# Activation-match tiebreaker fixtures (Phase 3 Commit B, step 4 starter)

**Status: same-session authorship — pending second-reader review per §14e.**

These fixtures exercise `RelationGraph.neighborhood(reasoning_context=...)`
end-to-end against the real graph + real backfilled embeddings (frozen probe
vectors so tests stay offline and deterministic).

## What these fixtures claim (and what they don't)

They test **mechanical faithfulness**: when reasoning-shape prose paraphrases
curator activation_condition A, the matcher's cosine prefers edge A; when it
paraphrases B, cosine prefers edge B. This is a structural property of
cosine similarity against curator-authored text, **not** a judgment that
model A or B is the "correct" antidote for any real-world reasoning context.

The "correct antidote" judgment is a semantic claim and is still doctrine-gated.
A blind-authored fixture set (author does not see candidate ACs when writing
probes) is what earns that claim — see `research/deep-graph-enrichment-handover.md`
§14e.

## File layout

- `frozen_probes.json` — reasoning-shape probes with pre-computed
  text-embedding-3-large vectors (3072-dim). Committed so tests don't hit
  the API.
- `scenarios/*.json` — one fixture per scenario. Each names a seed, a
  probe (by key in frozen_probes), and the expected supporting-model order.

## How to add a fixture

1. Pick a real seed from `data/relationship_graph.json` whose ally/compound
   neighbors have a genuine near-tie (δ < 0.01 in fan-adjusted affinity) OR
   a clear non-tie — whichever the fixture is meant to assert.
2. Author the probe text in reasoning-shape register (facts-free). If the
   intent is to align with a specific curator AC, loosely paraphrase that
   AC without reusing exact words.
3. Compute the probe vector once via `scripts/run_embed_query.py` or inline,
   add it to `frozen_probes.json`.
4. Write the scenario JSON declaring `expected_supporting_model_ids`.
5. Run `pytest tests/test_activation_tiebreaker_realdata.py`.

## Second-reader review checklist

When a non-author reviews these:

- [ ] Does the probe text paraphrase the curator AC, or does it contain
      curator phrasing lifted verbatim? (Latter = self-fulfilling, reject.)
- [ ] Is the probe in reasoning-shape register, not facts register? (Should
      not reference specific domains, names, numbers.)
- [ ] Does the expected outcome follow from cosine between probe and AC, or
      does it require outside knowledge of what the "right" model is? (The
      former is fair; the latter is a semantic claim that needs blind
      authoring.)
