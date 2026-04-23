# Extraction drift report — corpus-whistleblower

Generated: 2026-04-23T10:19:06Z
Conversation: `/private/tmp/lolla_case_whistleblower_conversation.txt` (17309 bytes)
Runs: 3
Run IDs: 20260423T101906Zdrift0, 20260423T101913Zdrift1, 20260423T101924Zdrift2

**Reading the metrics:**
- Free-text fields (`decision_situation`, `original_framing`, `synthesized_position`) — difflib SequenceMatcher ratio (character-level). 1.0 = identical; 0.7+ = very similar; 0.4–0.7 = material drift (paraphrase or reshape); <0.4 = shape-shift.
- List fields (`live_constraints`, `reasoning_passages`, `dropped_threads`) — Jaccard on normalized item text (strip, lowercase).
- `live_constraints_canonical_key` — Jaccard on `canonical_key` slugs with empty-string exclusion: empty/missing keys are filtered from BOTH sets before intersection so two failed extractions do not trivially match. A pair with all-empty keys on both sides is reported as `—` (undefined); the failure rate lives in `invalid_key_rate`.
- `invalid_key_rate` — share of constraints where `canonical_key` is missing or empty (the LLM failed the slug format rule). Per-run + overall. Acceptance gate target: ≤ 10%.
- `fabricated_count_per_run` — passages the extractor marked as not-a-literal-substring. Higher is worse.

## Aggregate drift

| Field | Metric | Mean | Min | Max |
|---|---|---|---|---|
| `decision_situation` | similarity | 1.000 | 1.000 | 1.000 |
| `original_framing` | similarity | 0.316 | 0.038 | 0.858 |
| `synthesized_position` | similarity | 0.271 | 0.202 | 0.376 |
| `live_constraints` | jaccard | 0.429 | 0.429 | 0.429 |
| `reasoning_passages` | jaccard | 0.528 | 0.333 | 0.750 |
| `dropped_threads` | jaccard | 0.000 | 0.000 | 0.000 |
| `live_constraints_canonical_key` | jaccard (empty-excl) | — | — | — |
> `live_constraints_canonical_key` has 3 undefined pair(s) — both runs had no valid canonical_keys. See `invalid_key_rate` below.
| `live_constraints_canonical_key_embedding` | cosine (empty-excl) | — | — | — |

**`invalid_key_rate` per run:** [1.0, 1.0, 1.0]
**`invalid_key_rate` overall:** 1.000 (15 invalid of 15 total constraints)
**Fabricated-quote counts per run:** [0, 1, 2]
**Capture health per run:** ['good', 'good', 'good']

## Pairwise detail

### `20260423T101906Zdrift0` vs `20260423T101913Zdrift1`
- **decision_situation**: similarity=1.000, lengths 182 ↔ 182
- **original_framing**: similarity=0.858, lengths 183 ↔ 232
- **synthesized_position**: similarity=0.202, lengths 579 ↔ 550
- **live_constraints**: jaccard=0.429, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.500, counts 5 ↔ 4
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=1

### `20260423T101906Zdrift0` vs `20260423T101924Zdrift2`
- **decision_situation**: similarity=1.000, lengths 182 ↔ 182
- **original_framing**: similarity=0.038, lengths 183 ↔ 241
- **synthesized_position**: similarity=0.234, lengths 579 ↔ 557
- **live_constraints**: jaccard=0.429, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.333, counts 5 ↔ 3
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=2

### `20260423T101913Zdrift1` vs `20260423T101924Zdrift2`
- **decision_situation**: similarity=1.000, lengths 182 ↔ 182
- **original_framing**: similarity=0.051, lengths 232 ↔ 241
- **synthesized_position**: similarity=0.376, lengths 550 ↔ 557
- **live_constraints**: jaccard=0.429, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.750, counts 4 ↔ 3
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=1, b=2
