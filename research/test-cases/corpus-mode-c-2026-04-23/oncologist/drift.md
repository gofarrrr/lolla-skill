# Extraction drift report — corpus-oncologist

Generated: 2026-04-23T10:17:38Z
Conversation: `/private/tmp/lolla_case_oncologist_conversation.txt` (15636 bytes)
Runs: 3
Run IDs: 20260423T101738Zdrift0, 20260423T101744Zdrift1, 20260423T101751Zdrift2

**Reading the metrics:**
- Free-text fields (`decision_situation`, `original_framing`, `synthesized_position`) — difflib SequenceMatcher ratio (character-level). 1.0 = identical; 0.7+ = very similar; 0.4–0.7 = material drift (paraphrase or reshape); <0.4 = shape-shift.
- List fields (`live_constraints`, `reasoning_passages`, `dropped_threads`) — Jaccard on normalized item text (strip, lowercase).
- `live_constraints_canonical_key` — Jaccard on `canonical_key` slugs with empty-string exclusion: empty/missing keys are filtered from BOTH sets before intersection so two failed extractions do not trivially match. A pair with all-empty keys on both sides is reported as `—` (undefined); the failure rate lives in `invalid_key_rate`.
- `invalid_key_rate` — share of constraints where `canonical_key` is missing or empty (the LLM failed the slug format rule). Per-run + overall. Acceptance gate target: ≤ 10%.
- `fabricated_count_per_run` — passages the extractor marked as not-a-literal-substring. Higher is worse.

## Aggregate drift

| Field | Metric | Mean | Min | Max |
|---|---|---|---|---|
| `decision_situation` | similarity | 0.890 | 0.825 | 0.957 |
| `original_framing` | similarity | 0.231 | 0.172 | 0.285 |
| `synthesized_position` | similarity | 0.397 | 0.095 | 1.000 |
| `live_constraints` | jaccard | 0.144 | 0.083 | 0.182 |
| `reasoning_passages` | jaccard | 0.342 | 0.222 | 0.429 |
| `dropped_threads` | jaccard | 0.000 | 0.000 | 0.000 |
| `live_constraints_canonical_key` | jaccard (empty-excl) | — | — | — |
> `live_constraints_canonical_key` has 3 undefined pair(s) — both runs had no valid canonical_keys. See `invalid_key_rate` below.
| `live_constraints_canonical_key_embedding` | cosine (empty-excl) | — | — | — |

**`invalid_key_rate` per run:** [1.0, 1.0, 1.0]
**`invalid_key_rate` overall:** 1.000 (20 invalid of 20 total constraints)
**Fabricated-quote counts per run:** [0, 0, 0]
**Capture health per run:** ['good', 'good', 'good']

## Pairwise detail

### `20260423T101738Zdrift0` vs `20260423T101744Zdrift1`
- **decision_situation**: similarity=0.825, lengths 139 ↔ 147
- **original_framing**: similarity=0.285, lengths 222 ↔ 256
- **synthesized_position**: similarity=0.095, lengths 535 ↔ 1005
- **live_constraints**: jaccard=0.167, counts 7 ↔ 7
- **reasoning_passages**: jaccard=0.429, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 0 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 7 ↔ 7
- **fabricated**: a=0, b=0

### `20260423T101738Zdrift0` vs `20260423T101751Zdrift2`
- **decision_situation**: similarity=0.957, lengths 139 ↔ 139
- **original_framing**: similarity=0.235, lengths 222 ↔ 221
- **synthesized_position**: similarity=0.095, lengths 535 ↔ 1005
- **live_constraints**: jaccard=0.083, counts 7 ↔ 6
- **reasoning_passages**: jaccard=0.222, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 0 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 7 ↔ 6
- **fabricated**: a=0, b=0

### `20260423T101744Zdrift1` vs `20260423T101751Zdrift2`
- **decision_situation**: similarity=0.888, lengths 147 ↔ 139
- **original_framing**: similarity=0.172, lengths 256 ↔ 221
- **synthesized_position**: similarity=1.000, lengths 1005 ↔ 1005
- **live_constraints**: jaccard=0.182, counts 7 ↔ 6
- **reasoning_passages**: jaccard=0.375, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 7 ↔ 6
- **fabricated**: a=0, b=0
