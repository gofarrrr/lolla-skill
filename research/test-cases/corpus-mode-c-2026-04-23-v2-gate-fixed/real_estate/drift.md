# Extraction drift report — corpus-v2-real_estate

Generated: 2026-04-23T10:28:46Z
Conversation: `/private/tmp/lolla_case_real_estate_conversation.txt` (6816 bytes)
Runs: 3
Run IDs: 20260423T102846Zdrift0, 20260423T102856Zdrift1, 20260423T102901Zdrift2

**Reading the metrics:**
- Free-text fields (`decision_situation`, `original_framing`, `synthesized_position`) — difflib SequenceMatcher ratio (character-level). 1.0 = identical; 0.7+ = very similar; 0.4–0.7 = material drift (paraphrase or reshape); <0.4 = shape-shift.
- List fields (`live_constraints`, `reasoning_passages`, `dropped_threads`) — Jaccard on normalized item text (strip, lowercase).
- `live_constraints_canonical_key` — Jaccard on `canonical_key` slugs with empty-string exclusion: empty/missing keys are filtered from BOTH sets before intersection so two failed extractions do not trivially match. A pair with all-empty keys on both sides is reported as `—` (undefined); the failure rate lives in `invalid_key_rate`.
- `invalid_key_rate` — share of constraints where `canonical_key` is missing or empty (the LLM failed the slug format rule). Per-run + overall. Acceptance gate target: ≤ 10%.
- `fabricated_count_per_run` — passages the extractor marked as not-a-literal-substring. Higher is worse.

## Aggregate drift

| Field | Metric | Mean | Min | Max |
|---|---|---|---|---|
| `decision_situation` | similarity | 0.933 | 0.900 | 1.000 |
| `original_framing` | similarity | 0.746 | 0.553 | 0.929 |
| `synthesized_position` | similarity | 0.572 | 0.401 | 0.874 |
| `live_constraints` | jaccard | 0.083 | 0.000 | 0.250 |
| `reasoning_passages` | jaccard | 0.132 | 0.000 | 0.286 |
| `dropped_threads` | jaccard | 0.333 | 0.000 | 1.000 |
| `live_constraints_canonical_key` | jaccard (empty-excl) | — | — | — |
> `live_constraints_canonical_key` has 3 undefined pair(s) — both runs had no valid canonical_keys. See `invalid_key_rate` below.
| `live_constraints_canonical_key_embedding` | cosine (empty-excl) | — | — | — |

**`invalid_key_rate` per run:** [1.0, 1.0, 1.0]
**`invalid_key_rate` overall:** 1.000 (15 invalid of 15 total constraints)
**Fabricated-quote counts per run:** [0, 0, 1]
**Capture health per run:** ['good', 'good', 'good']

## Pairwise detail

### `20260423T102846Zdrift0` vs `20260423T102856Zdrift1`
- **decision_situation**: similarity=1.000, lengths 173 ↔ 173
- **original_framing**: similarity=0.553, lengths 190 ↔ 208
- **synthesized_position**: similarity=0.440, lengths 421 ↔ 325
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.000, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 0
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `20260423T102846Zdrift0` vs `20260423T102901Zdrift2`
- **decision_situation**: similarity=0.900, lengths 173 ↔ 178
- **original_framing**: similarity=0.929, lengths 190 ↔ 176
- **synthesized_position**: similarity=0.401, lengths 421 ↔ 327
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.111, counts 6 ↔ 4
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 0
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=1

### `20260423T102856Zdrift1` vs `20260423T102901Zdrift2`
- **decision_situation**: similarity=0.900, lengths 173 ↔ 178
- **original_framing**: similarity=0.755, lengths 208 ↔ 176
- **synthesized_position**: similarity=0.874, lengths 325 ↔ 327
- **live_constraints**: jaccard=0.250, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.286, counts 5 ↔ 4
- **dropped_threads**: jaccard=1.000, counts 0 ↔ 0
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=1
