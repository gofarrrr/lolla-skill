# Extraction drift report — corpus-v2-multi_offer

Generated: 2026-04-23T10:29:10Z
Conversation: `/private/tmp/lolla_case_multi_offer_conversation.txt` (15787 bytes)
Runs: 3
Run IDs: 20260423T102910Zdrift0, 20260423T102916Zdrift1, 20260423T102922Zdrift2

**Reading the metrics:**
- Free-text fields (`decision_situation`, `original_framing`, `synthesized_position`) — difflib SequenceMatcher ratio (character-level). 1.0 = identical; 0.7+ = very similar; 0.4–0.7 = material drift (paraphrase or reshape); <0.4 = shape-shift.
- List fields (`live_constraints`, `reasoning_passages`, `dropped_threads`) — Jaccard on normalized item text (strip, lowercase).
- `live_constraints_canonical_key` — Jaccard on `canonical_key` slugs with empty-string exclusion: empty/missing keys are filtered from BOTH sets before intersection so two failed extractions do not trivially match. A pair with all-empty keys on both sides is reported as `—` (undefined); the failure rate lives in `invalid_key_rate`.
- `invalid_key_rate` — share of constraints where `canonical_key` is missing or empty (the LLM failed the slug format rule). Per-run + overall. Acceptance gate target: ≤ 10%.
- `fabricated_count_per_run` — passages the extractor marked as not-a-literal-substring. Higher is worse.

## Aggregate drift

| Field | Metric | Mean | Min | Max |
|---|---|---|---|---|
| `decision_situation` | similarity | 0.725 | 0.648 | 0.852 |
| `original_framing` | similarity | 0.775 | 0.695 | 0.831 |
| `synthesized_position` | similarity | 0.571 | 0.442 | 0.813 |
| `live_constraints` | jaccard | 0.296 | 0.111 | 0.667 |
| `reasoning_passages` | jaccard | 0.204 | 0.111 | 0.250 |
| `dropped_threads` | jaccard | 1.000 | 1.000 | 1.000 |
| `live_constraints_canonical_key` | jaccard (empty-excl) | — | — | — |
> `live_constraints_canonical_key` has 3 undefined pair(s) — both runs had no valid canonical_keys. See `invalid_key_rate` below.
| `live_constraints_canonical_key_embedding` | cosine (empty-excl) | — | — | — |

**`invalid_key_rate` per run:** [1.0, 1.0, 1.0]
**`invalid_key_rate` overall:** 1.000 (15 invalid of 15 total constraints)
**Fabricated-quote counts per run:** [0, 0, 0]
**Capture health per run:** ['good', 'good', 'good']

## Pairwise detail

### `20260423T102910Zdrift0` vs `20260423T102916Zdrift1`
- **decision_situation**: similarity=0.648, lengths 205 ↔ 187
- **original_framing**: similarity=0.695, lengths 246 ↔ 232
- **synthesized_position**: similarity=0.813, lengths 440 ↔ 389
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.111, counts 5 ↔ 5
- **dropped_threads**: jaccard=1.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `20260423T102910Zdrift0` vs `20260423T102922Zdrift2`
- **decision_situation**: similarity=0.852, lengths 205 ↔ 180
- **original_framing**: similarity=0.798, lengths 246 ↔ 235
- **synthesized_position**: similarity=0.442, lengths 440 ↔ 484
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.250, counts 5 ↔ 5
- **dropped_threads**: jaccard=1.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `20260423T102916Zdrift1` vs `20260423T102922Zdrift2`
- **decision_situation**: similarity=0.676, lengths 187 ↔ 180
- **original_framing**: similarity=0.831, lengths 232 ↔ 235
- **synthesized_position**: similarity=0.458, lengths 389 ↔ 484
- **live_constraints**: jaccard=0.667, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.250, counts 5 ↔ 5
- **dropped_threads**: jaccard=1.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0
