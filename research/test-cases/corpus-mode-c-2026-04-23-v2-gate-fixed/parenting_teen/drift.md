# Extraction drift report — corpus-v2-parenting_teen

Generated: 2026-04-23T10:28:09Z
Conversation: `/private/tmp/lolla_case_parenting_teen_conversation.txt` (19902 bytes)
Runs: 3
Run IDs: 20260423T102809Zdrift0, 20260423T102814Zdrift1, 20260423T102820Zdrift2

**Reading the metrics:**
- Free-text fields (`decision_situation`, `original_framing`, `synthesized_position`) — difflib SequenceMatcher ratio (character-level). 1.0 = identical; 0.7+ = very similar; 0.4–0.7 = material drift (paraphrase or reshape); <0.4 = shape-shift.
- List fields (`live_constraints`, `reasoning_passages`, `dropped_threads`) — Jaccard on normalized item text (strip, lowercase).
- `live_constraints_canonical_key` — Jaccard on `canonical_key` slugs with empty-string exclusion: empty/missing keys are filtered from BOTH sets before intersection so two failed extractions do not trivially match. A pair with all-empty keys on both sides is reported as `—` (undefined); the failure rate lives in `invalid_key_rate`.
- `invalid_key_rate` — share of constraints where `canonical_key` is missing or empty (the LLM failed the slug format rule). Per-run + overall. Acceptance gate target: ≤ 10%.
- `fabricated_count_per_run` — passages the extractor marked as not-a-literal-substring. Higher is worse.

## Aggregate drift

| Field | Metric | Mean | Min | Max |
|---|---|---|---|---|
| `decision_situation` | similarity | 0.628 | 0.583 | 0.665 |
| `original_framing` | similarity | 0.753 | 0.633 | 0.959 |
| `synthesized_position` | similarity | 0.367 | 0.280 | 0.448 |
| `live_constraints` | jaccard | 0.555 | 0.333 | 1.000 |
| `reasoning_passages` | jaccard | 0.345 | 0.250 | 0.500 |
| `dropped_threads` | jaccard | 0.067 | 0.000 | 0.200 |
| `live_constraints_canonical_key` | jaccard (empty-excl) | — | — | — |
> `live_constraints_canonical_key` has 3 undefined pair(s) — both runs had no valid canonical_keys. See `invalid_key_rate` below.
| `live_constraints_canonical_key_embedding` | cosine (empty-excl) | — | — | — |

**`invalid_key_rate` per run:** [1.0, 1.0, 1.0]
**`invalid_key_rate` overall:** 1.000 (12 invalid of 12 total constraints)
**Fabricated-quote counts per run:** [0, 0, 0]
**Capture health per run:** ['good', 'good', 'good']

## Pairwise detail

### `20260423T102809Zdrift0` vs `20260423T102814Zdrift1`
- **decision_situation**: similarity=0.635, lengths 159 ↔ 159
- **original_framing**: similarity=0.668, lengths 207 ↔ 218
- **synthesized_position**: similarity=0.280, lengths 383 ↔ 389
- **live_constraints**: jaccard=0.333, counts 4 ↔ 4
- **reasoning_passages**: jaccard=0.286, counts 4 ↔ 5
- **dropped_threads**: jaccard=0.200, counts 3 ↔ 3
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 4 ↔ 4
- **fabricated**: a=0, b=0

### `20260423T102809Zdrift0` vs `20260423T102820Zdrift2`
- **decision_situation**: similarity=0.665, lengths 159 ↔ 184
- **original_framing**: similarity=0.959, lengths 207 ↔ 212
- **synthesized_position**: similarity=0.448, lengths 383 ↔ 393
- **live_constraints**: jaccard=1.000, counts 4 ↔ 4
- **reasoning_passages**: jaccard=0.500, counts 4 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 4 ↔ 4
- **fabricated**: a=0, b=0

### `20260423T102814Zdrift1` vs `20260423T102820Zdrift2`
- **decision_situation**: similarity=0.583, lengths 159 ↔ 184
- **original_framing**: similarity=0.633, lengths 218 ↔ 212
- **synthesized_position**: similarity=0.373, lengths 389 ↔ 393
- **live_constraints**: jaccard=0.333, counts 4 ↔ 4
- **reasoning_passages**: jaccard=0.250, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 4 ↔ 4
- **fabricated**: a=0, b=0
