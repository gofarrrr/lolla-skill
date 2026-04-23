# Extraction drift report — corpus-real_estate

Generated: 2026-04-23T10:18:27Z
Conversation: `/private/tmp/lolla_case_real_estate_conversation.txt` (6816 bytes)
Runs: 3
Run IDs: 20260423T101827Zdrift0, 20260423T101837Zdrift1, 20260423T101845Zdrift2

**Reading the metrics:**
- Free-text fields (`decision_situation`, `original_framing`, `synthesized_position`) — difflib SequenceMatcher ratio (character-level). 1.0 = identical; 0.7+ = very similar; 0.4–0.7 = material drift (paraphrase or reshape); <0.4 = shape-shift.
- List fields (`live_constraints`, `reasoning_passages`, `dropped_threads`) — Jaccard on normalized item text (strip, lowercase).
- `live_constraints_canonical_key` — Jaccard on `canonical_key` slugs with empty-string exclusion: empty/missing keys are filtered from BOTH sets before intersection so two failed extractions do not trivially match. A pair with all-empty keys on both sides is reported as `—` (undefined); the failure rate lives in `invalid_key_rate`.
- `invalid_key_rate` — share of constraints where `canonical_key` is missing or empty (the LLM failed the slug format rule). Per-run + overall. Acceptance gate target: ≤ 10%.
- `fabricated_count_per_run` — passages the extractor marked as not-a-literal-substring. Higher is worse.

## Aggregate drift

| Field | Metric | Mean | Min | Max |
|---|---|---|---|---|
| `decision_situation` | similarity | 0.859 | 0.790 | 0.986 |
| `original_framing` | similarity | 0.506 | 0.365 | 0.716 |
| `synthesized_position` | similarity | 0.421 | 0.346 | 0.519 |
| `live_constraints` | jaccard | 0.000 | 0.000 | 0.000 |
| `reasoning_passages` | jaccard | 0.524 | 0.286 | 1.000 |
| `dropped_threads` | jaccard | 0.000 | 0.000 | 0.000 |
| `live_constraints_canonical_key` | jaccard (empty-excl) | — | — | — |
> `live_constraints_canonical_key` has 3 undefined pair(s) — both runs had no valid canonical_keys. See `invalid_key_rate` below.
| `live_constraints_canonical_key_embedding` | cosine (empty-excl) | — | — | — |

**`invalid_key_rate` per run:** [1.0, 1.0, 1.0]
**`invalid_key_rate` overall:** 1.000 (14 invalid of 14 total constraints)
**Fabricated-quote counts per run:** [1, 1, 0]
**Capture health per run:** ['good', 'good', 'good']

## Pairwise detail

### `20260423T101827Zdrift0` vs `20260423T101837Zdrift1`
- **decision_situation**: similarity=0.790, lengths 178 ↔ 174
- **original_framing**: similarity=0.438, lengths 182 ↔ 197
- **synthesized_position**: similarity=0.346, lengths 353 ↔ 334
- **live_constraints**: jaccard=0.000, counts 3 ↔ 5
- **reasoning_passages**: jaccard=1.000, counts 4 ↔ 4
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 0
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 3 ↔ 5
- **fabricated**: a=1, b=1

### `20260423T101827Zdrift0` vs `20260423T101845Zdrift2`
- **decision_situation**: similarity=0.986, lengths 178 ↔ 173
- **original_framing**: similarity=0.365, lengths 182 ↔ 191
- **synthesized_position**: similarity=0.399, lengths 353 ↔ 329
- **live_constraints**: jaccard=0.000, counts 3 ↔ 6
- **reasoning_passages**: jaccard=0.286, counts 4 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 3 ↔ 6
- **fabricated**: a=1, b=0

### `20260423T101837Zdrift1` vs `20260423T101845Zdrift2`
- **decision_situation**: similarity=0.801, lengths 174 ↔ 173
- **original_framing**: similarity=0.716, lengths 197 ↔ 191
- **synthesized_position**: similarity=0.519, lengths 334 ↔ 329
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.286, counts 4 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 0 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=1, b=0
