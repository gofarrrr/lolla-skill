# Extraction drift report — oncologist-test

Generated: 2026-04-23T09:53:09Z
Conversation: `/private/tmp/lolla_case_oncologist_conversation.txt` (15636 bytes)
Runs: 3
Run IDs: 20260423T095309Zdrift0, 20260423T095317Zdrift1, 20260423T095330Zdrift2

**Reading the metrics:**
- Free-text fields (`decision_situation`, `original_framing`, `synthesized_position`) — difflib SequenceMatcher ratio (character-level). 1.0 = identical; 0.7+ = very similar; 0.4–0.7 = material drift (paraphrase or reshape); <0.4 = shape-shift.
- List fields (`live_constraints`, `reasoning_passages`, `dropped_threads`) — Jaccard on normalized item text (strip, lowercase).
- `live_constraints_canonical_key` — Jaccard on `canonical_key` slugs with empty-string exclusion: empty/missing keys are filtered from BOTH sets before intersection so two failed extractions do not trivially match. A pair with all-empty keys on both sides is reported as `—` (undefined); the failure rate lives in `invalid_key_rate`.
- `invalid_key_rate` — share of constraints where `canonical_key` is missing or empty (the LLM failed the slug format rule). Per-run + overall. Acceptance gate target: ≤ 10%.
- `fabricated_count_per_run` — passages the extractor marked as not-a-literal-substring. Higher is worse.

## Aggregate drift

| Field | Metric | Mean | Min | Max |
|---|---|---|---|---|
| `decision_situation` | similarity | 0.883 | 0.825 | 1.000 |
| `original_framing` | similarity | 0.427 | 0.190 | 0.897 |
| `synthesized_position` | similarity | 0.403 | 0.104 | 1.000 |
| `live_constraints` | jaccard | 0.432 | 0.273 | 0.750 |
| `reasoning_passages` | jaccard | 0.386 | 0.222 | 0.714 |
| `dropped_threads` | jaccard | 0.000 | 0.000 | 0.000 |
| `live_constraints_canonical_key` | jaccard (empty-excl) | — | — | — |
> `live_constraints_canonical_key` has 3 undefined pair(s) — both runs had no valid canonical_keys. See `invalid_key_rate` below.
| `live_constraints_canonical_key_embedding` | cosine (empty-excl) | — | — | — |

**`invalid_key_rate` per run:** [1.0, 1.0, 1.0]
**`invalid_key_rate` overall:** 1.000 (21 invalid of 21 total constraints)
**Fabricated-quote counts per run:** [0, 0, 0]
**Capture health per run:** ['good', 'good', 'good']

## Pairwise detail

### `20260423T095309Zdrift0` vs `20260423T095317Zdrift1`
- **decision_situation**: similarity=0.825, lengths 139 ↔ 147
- **original_framing**: similarity=0.190, lengths 213 ↔ 230
- **synthesized_position**: similarity=0.104, lengths 551 ↔ 1005
- **live_constraints**: jaccard=0.273, counts 7 ↔ 7
- **reasoning_passages**: jaccard=0.222, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 0
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 7 ↔ 7
- **fabricated**: a=0, b=0

### `20260423T095309Zdrift0` vs `20260423T095330Zdrift2`
- **decision_situation**: similarity=0.825, lengths 139 ↔ 147
- **original_framing**: similarity=0.195, lengths 213 ↔ 227
- **synthesized_position**: similarity=0.104, lengths 551 ↔ 1005
- **live_constraints**: jaccard=0.273, counts 7 ↔ 7
- **reasoning_passages**: jaccard=0.222, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 7 ↔ 7
- **fabricated**: a=0, b=0

### `20260423T095317Zdrift1` vs `20260423T095330Zdrift2`
- **decision_situation**: similarity=1.000, lengths 147 ↔ 147
- **original_framing**: similarity=0.897, lengths 230 ↔ 227
- **synthesized_position**: similarity=1.000, lengths 1005 ↔ 1005
- **live_constraints**: jaccard=0.750, counts 7 ↔ 7
- **reasoning_passages**: jaccard=0.714, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 0 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 7 ↔ 7
- **fabricated**: a=0, b=0
