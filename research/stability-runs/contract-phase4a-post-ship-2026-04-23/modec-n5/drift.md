# Extraction drift report — contract-phase4a-post-ship

Generated: 2026-04-23T09:06:17Z
Conversation: `/private/tmp/lolla_20260422T155622Z_conversation.txt` (26304 bytes)
Runs: 5
Run IDs: 20260423T090617Zdrift0, 20260423T090627Zdrift1, 20260423T090637Zdrift2, 20260423T090643Zdrift3, 20260423T090649Zdrift4

**Reading the metrics:**
- Free-text fields (`decision_situation`, `original_framing`, `synthesized_position`) — difflib SequenceMatcher ratio (character-level). 1.0 = identical; 0.7+ = very similar; 0.4–0.7 = material drift (paraphrase or reshape); <0.4 = shape-shift.
- List fields (`live_constraints`, `reasoning_passages`, `dropped_threads`) — Jaccard on normalized item text (strip, lowercase).
- `live_constraints_canonical_key` — Jaccard on `canonical_key` slugs with empty-string exclusion: empty/missing keys are filtered from BOTH sets before intersection so two failed extractions do not trivially match. A pair with all-empty keys on both sides is reported as `—` (undefined); the failure rate lives in `invalid_key_rate`.
- `invalid_key_rate` — share of constraints where `canonical_key` is missing or empty (the LLM failed the slug format rule). Per-run + overall. Acceptance gate target: ≤ 10%.
- `fabricated_count_per_run` — passages the extractor marked as not-a-literal-substring. Higher is worse.

## Aggregate drift

| Field | Metric | Mean | Min | Max |
|---|---|---|---|---|
| `decision_situation` | similarity | 0.899 | 0.859 | 1.000 |
| `original_framing` | similarity | 0.290 | 0.183 | 0.374 |
| `synthesized_position` | similarity | 0.311 | 0.172 | 0.513 |
| `live_constraints` | jaccard | 0.396 | 0.200 | 1.000 |
| `reasoning_passages` | jaccard | 0.493 | 0.250 | 0.833 |
| `dropped_threads` | jaccard | 0.175 | 0.000 | 1.000 |
| `live_constraints_canonical_key` | jaccard (empty-excl) | — | — | — |
> `live_constraints_canonical_key` has 10 undefined pair(s) — both runs had no valid canonical_keys. See `invalid_key_rate` below.
| `live_constraints_canonical_key_embedding` | cosine (empty-excl) | — | — | — |

**`invalid_key_rate` per run:** [1.0, 1.0, 1.0, 1.0, 1.0]
**`invalid_key_rate` overall:** 1.000 (29 invalid of 29 total constraints)
**Fabricated-quote counts per run:** [0, 0, 0, 0, 0]
**Capture health per run:** ['good', 'good', 'good', 'good', 'good']

## Pairwise detail

### `20260423T090617Zdrift0` vs `20260423T090627Zdrift1`
- **decision_situation**: similarity=1.000, lengths 138 ↔ 138
- **original_framing**: similarity=0.340, lengths 204 ↔ 208
- **synthesized_position**: similarity=0.289, lengths 576 ↔ 481
- **live_constraints**: jaccard=1.000, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.333, counts 7 ↔ 5
- **dropped_threads**: jaccard=1.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `20260423T090617Zdrift0` vs `20260423T090637Zdrift2`
- **decision_situation**: similarity=0.859, lengths 138 ↔ 160
- **original_framing**: similarity=0.226, lengths 204 ↔ 362
- **synthesized_position**: similarity=0.247, lengths 576 ↔ 664
- **live_constraints**: jaccard=0.333, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.500, counts 7 ↔ 5
- **dropped_threads**: jaccard=0.250, counts 2 ↔ 3
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `20260423T090617Zdrift0` vs `20260423T090643Zdrift3`
- **decision_situation**: similarity=0.859, lengths 138 ↔ 160
- **original_framing**: similarity=0.374, lengths 204 ↔ 325
- **synthesized_position**: similarity=0.188, lengths 576 ↔ 744
- **live_constraints**: jaccard=0.200, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.333, counts 7 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `20260423T090617Zdrift0` vs `20260423T090649Zdrift4`
- **decision_situation**: similarity=0.905, lengths 138 ↔ 158
- **original_framing**: similarity=0.240, lengths 204 ↔ 296
- **synthesized_position**: similarity=0.399, lengths 576 ↔ 692
- **live_constraints**: jaccard=0.222, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.444, counts 7 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `20260423T090627Zdrift1` vs `20260423T090637Zdrift2`
- **decision_situation**: similarity=0.859, lengths 138 ↔ 160
- **original_framing**: similarity=0.372, lengths 208 ↔ 362
- **synthesized_position**: similarity=0.311, lengths 481 ↔ 664
- **live_constraints**: jaccard=0.333, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.429, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.250, counts 2 ↔ 3
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `20260423T090627Zdrift1` vs `20260423T090643Zdrift3`
- **decision_situation**: similarity=0.859, lengths 138 ↔ 160
- **original_framing**: similarity=0.255, lengths 208 ↔ 325
- **synthesized_position**: similarity=0.266, lengths 481 ↔ 744
- **live_constraints**: jaccard=0.200, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.250, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `20260423T090627Zdrift1` vs `20260423T090649Zdrift4`
- **decision_situation**: similarity=0.905, lengths 138 ↔ 158
- **original_framing**: similarity=0.325, lengths 208 ↔ 296
- **synthesized_position**: similarity=0.305, lengths 481 ↔ 692
- **live_constraints**: jaccard=0.222, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.571, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `20260423T090637Zdrift2` vs `20260423T090643Zdrift3`
- **decision_situation**: similarity=1.000, lengths 160 ↔ 160
- **original_framing**: similarity=0.183, lengths 362 ↔ 325
- **synthesized_position**: similarity=0.172, lengths 664 ↔ 744
- **live_constraints**: jaccard=0.500, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.667, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 3
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `20260423T090637Zdrift2` vs `20260423T090649Zdrift4`
- **decision_situation**: similarity=0.874, lengths 160 ↔ 158
- **original_framing**: similarity=0.316, lengths 362 ↔ 296
- **synthesized_position**: similarity=0.416, lengths 664 ↔ 692
- **live_constraints**: jaccard=0.571, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.833, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `20260423T090643Zdrift3` vs `20260423T090649Zdrift4`
- **decision_situation**: similarity=0.874, lengths 160 ↔ 158
- **original_framing**: similarity=0.267, lengths 325 ↔ 296
- **synthesized_position**: similarity=0.513, lengths 744 ↔ 692
- **live_constraints**: jaccard=0.375, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.571, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.250, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0
