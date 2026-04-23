# Extraction drift report — corpus-phd_research

Generated: 2026-04-23T10:19:33Z
Conversation: `/private/tmp/lolla_case_phd_research_conversation.txt` (27050 bytes)
Runs: 3
Run IDs: 20260423T101933Zdrift0, 20260423T101942Zdrift1, 20260423T101953Zdrift2

**Reading the metrics:**
- Free-text fields (`decision_situation`, `original_framing`, `synthesized_position`) — difflib SequenceMatcher ratio (character-level). 1.0 = identical; 0.7+ = very similar; 0.4–0.7 = material drift (paraphrase or reshape); <0.4 = shape-shift.
- List fields (`live_constraints`, `reasoning_passages`, `dropped_threads`) — Jaccard on normalized item text (strip, lowercase).
- `live_constraints_canonical_key` — Jaccard on `canonical_key` slugs with empty-string exclusion: empty/missing keys are filtered from BOTH sets before intersection so two failed extractions do not trivially match. A pair with all-empty keys on both sides is reported as `—` (undefined); the failure rate lives in `invalid_key_rate`.
- `invalid_key_rate` — share of constraints where `canonical_key` is missing or empty (the LLM failed the slug format rule). Per-run + overall. Acceptance gate target: ≤ 10%.
- `fabricated_count_per_run` — passages the extractor marked as not-a-literal-substring. Higher is worse.

## Aggregate drift

| Field | Metric | Mean | Min | Max |
|---|---|---|---|---|
| `decision_situation` | similarity | 0.991 | 0.986 | 1.000 |
| `original_framing` | similarity | 0.538 | 0.362 | 0.638 |
| `synthesized_position` | similarity | 0.264 | 0.158 | 0.438 |
| `live_constraints` | jaccard | 0.217 | 0.111 | 0.429 |
| `reasoning_passages` | jaccard | 0.443 | 0.286 | 0.667 |
| `dropped_threads` | jaccard | 0.000 | 0.000 | 0.000 |
| `live_constraints_canonical_key` | jaccard (empty-excl) | — | — | — |
> `live_constraints_canonical_key` has 3 undefined pair(s) — both runs had no valid canonical_keys. See `invalid_key_rate` below.
| `live_constraints_canonical_key_embedding` | cosine (empty-excl) | — | — | — |

**`invalid_key_rate` per run:** [1.0, 1.0, 1.0]
**`invalid_key_rate` overall:** 1.000 (15 invalid of 15 total constraints)
**Fabricated-quote counts per run:** [0, 1, 0]
**Capture health per run:** ['good', 'good', 'good']

## Pairwise detail

### `20260423T101933Zdrift0` vs `20260423T101942Zdrift1`
- **decision_situation**: similarity=1.000, lengths 213 ↔ 213
- **original_framing**: similarity=0.362, lengths 283 ↔ 253
- **synthesized_position**: similarity=0.438, lengths 653 ↔ 470
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.286, counts 5 ↔ 4
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=1

### `20260423T101933Zdrift0` vs `20260423T101953Zdrift2`
- **decision_situation**: similarity=0.986, lengths 213 ↔ 219
- **original_framing**: similarity=0.613, lengths 283 ↔ 255
- **synthesized_position**: similarity=0.158, lengths 653 ↔ 616
- **live_constraints**: jaccard=0.429, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.375, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `20260423T101942Zdrift1` vs `20260423T101953Zdrift2`
- **decision_situation**: similarity=0.986, lengths 213 ↔ 219
- **original_framing**: similarity=0.638, lengths 253 ↔ 255
- **synthesized_position**: similarity=0.195, lengths 470 ↔ 616
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.667, counts 4 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=1, b=0
