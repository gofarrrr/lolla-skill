# Extraction drift report — corpus-v2-user_has_plan

Generated: 2026-04-23T10:30:38Z
Conversation: `/private/tmp/lolla_case_user_has_plan_conversation.txt` (9272 bytes)
Runs: 3
Run IDs: 20260423T103038Zdrift0, 20260423T103043Zdrift1, 20260423T103048Zdrift2

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
| `original_framing` | similarity | 1.000 | 1.000 | 1.000 |
| `synthesized_position` | similarity | 1.000 | 1.000 | 1.000 |
| `live_constraints` | jaccard | 0.359 | 0.143 | 0.600 |
| `reasoning_passages` | jaccard | 0.833 | 0.750 | 1.000 |
| `dropped_threads` | jaccard | 0.333 | 0.000 | 1.000 |
| `live_constraints_canonical_key` | jaccard (empty-excl) | — | — | — |
> `live_constraints_canonical_key` has 3 undefined pair(s) — both runs had no valid canonical_keys. See `invalid_key_rate` below.
| `live_constraints_canonical_key_embedding` | cosine (empty-excl) | — | — | — |

**`invalid_key_rate` per run:** [1.0, 1.0, 1.0]
**`invalid_key_rate` overall:** 1.000 (12 invalid of 12 total constraints)
**Fabricated-quote counts per run:** [0, 0, 0]
**Capture health per run:** ['good', 'good', 'good']

## Pairwise detail

### `20260423T103038Zdrift0` vs `20260423T103043Zdrift1`
- **decision_situation**: similarity=1.000, lengths 156 ↔ 156
- **original_framing**: similarity=1.000, lengths 207 ↔ 207
- **synthesized_position**: similarity=1.000, lengths 482 ↔ 482
- **live_constraints**: jaccard=0.143, counts 4 ↔ 4
- **reasoning_passages**: jaccard=0.750, counts 3 ↔ 4
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 4 ↔ 4
- **fabricated**: a=0, b=0

### `20260423T103038Zdrift0` vs `20260423T103048Zdrift2`
- **decision_situation**: similarity=1.000, lengths 156 ↔ 156
- **original_framing**: similarity=1.000, lengths 207 ↔ 207
- **synthesized_position**: similarity=1.000, lengths 482 ↔ 482
- **live_constraints**: jaccard=0.600, counts 4 ↔ 4
- **reasoning_passages**: jaccard=0.750, counts 3 ↔ 4
- **dropped_threads**: jaccard=1.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 4 ↔ 4
- **fabricated**: a=0, b=0

### `20260423T103043Zdrift1` vs `20260423T103048Zdrift2`
- **decision_situation**: similarity=1.000, lengths 156 ↔ 156
- **original_framing**: similarity=1.000, lengths 207 ↔ 207
- **synthesized_position**: similarity=1.000, lengths 482 ↔ 482
- **live_constraints**: jaccard=0.333, counts 4 ↔ 4
- **reasoning_passages**: jaccard=1.000, counts 4 ↔ 4
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 4 ↔ 4
- **fabricated**: a=0, b=0
