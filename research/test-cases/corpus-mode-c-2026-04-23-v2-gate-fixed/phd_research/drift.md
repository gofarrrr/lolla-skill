# Extraction drift report — corpus-v2-phd_research

Generated: 2026-04-23T10:30:07Z
Conversation: `/private/tmp/lolla_case_phd_research_conversation.txt` (27050 bytes)
Runs: 3
Run IDs: 20260423T103007Zdrift0, 20260423T103019Zdrift1, 20260423T103028Zdrift2

**Reading the metrics:**
- Free-text fields (`decision_situation`, `original_framing`, `synthesized_position`) — difflib SequenceMatcher ratio (character-level). 1.0 = identical; 0.7+ = very similar; 0.4–0.7 = material drift (paraphrase or reshape); <0.4 = shape-shift.
- List fields (`live_constraints`, `reasoning_passages`, `dropped_threads`) — Jaccard on normalized item text (strip, lowercase).
- `live_constraints_canonical_key` — Jaccard on `canonical_key` slugs with empty-string exclusion: empty/missing keys are filtered from BOTH sets before intersection so two failed extractions do not trivially match. A pair with all-empty keys on both sides is reported as `—` (undefined); the failure rate lives in `invalid_key_rate`.
- `invalid_key_rate` — share of constraints where `canonical_key` is missing or empty (the LLM failed the slug format rule). Per-run + overall. Acceptance gate target: ≤ 10%.
- `fabricated_count_per_run` — passages the extractor marked as not-a-literal-substring. Higher is worse.

## Aggregate drift

| Field | Metric | Mean | Min | Max |
|---|---|---|---|---|
| `decision_situation` | similarity | 0.707 | 0.561 | 1.000 |
| `original_framing` | similarity | 0.449 | 0.276 | 0.643 |
| `synthesized_position` | similarity | 0.195 | 0.173 | 0.220 |
| `live_constraints` | jaccard | 0.356 | 0.125 | 0.800 |
| `reasoning_passages` | jaccard | 0.226 | 0.125 | 0.429 |
| `dropped_threads` | jaccard | 0.167 | 0.000 | 0.500 |
| `live_constraints_canonical_key` | jaccard (empty-excl) | — | — | — |
> `live_constraints_canonical_key` has 3 undefined pair(s) — both runs had no valid canonical_keys. See `invalid_key_rate` below.
| `live_constraints_canonical_key_embedding` | cosine (empty-excl) | — | — | — |

**`invalid_key_rate` per run:** [1.0, 1.0, 1.0]
**`invalid_key_rate` overall:** 1.000 (13 invalid of 13 total constraints)
**Fabricated-quote counts per run:** [0, 0, 1]
**Capture health per run:** ['good', 'good', 'good']

## Pairwise detail

### `20260423T103007Zdrift0` vs `20260423T103019Zdrift1`
- **decision_situation**: similarity=1.000, lengths 130 ↔ 130
- **original_framing**: similarity=0.643, lengths 243 ↔ 258
- **synthesized_position**: similarity=0.220, lengths 662 ↔ 640
- **live_constraints**: jaccard=0.800, counts 5 ↔ 4
- **reasoning_passages**: jaccard=0.429, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 4
- **fabricated**: a=0, b=0

### `20260423T103007Zdrift0` vs `20260423T103028Zdrift2`
- **decision_situation**: similarity=0.561, lengths 130 ↔ 184
- **original_framing**: similarity=0.276, lengths 243 ↔ 271
- **synthesized_position**: similarity=0.173, lengths 662 ↔ 572
- **live_constraints**: jaccard=0.125, counts 5 ↔ 4
- **reasoning_passages**: jaccard=0.125, counts 5 ↔ 4
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 4
- **fabricated**: a=0, b=1

### `20260423T103019Zdrift1` vs `20260423T103028Zdrift2`
- **decision_situation**: similarity=0.561, lengths 130 ↔ 184
- **original_framing**: similarity=0.427, lengths 258 ↔ 271
- **synthesized_position**: similarity=0.193, lengths 640 ↔ 572
- **live_constraints**: jaccard=0.143, counts 4 ↔ 4
- **reasoning_passages**: jaccard=0.125, counts 5 ↔ 4
- **dropped_threads**: jaccard=0.500, counts 1 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 4 ↔ 4
- **fabricated**: a=0, b=1
