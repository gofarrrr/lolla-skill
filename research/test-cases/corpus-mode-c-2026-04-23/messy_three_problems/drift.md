# Extraction drift report — corpus-messy_three_problems

Generated: 2026-04-23T10:20:19Z
Conversation: `/private/tmp/lolla_case_messy_three_problems_conversation.txt` (13239 bytes)
Runs: 3
Run IDs: 20260423T102019Zdrift0, 20260423T102028Zdrift1, 20260423T102036Zdrift2

**Reading the metrics:**
- Free-text fields (`decision_situation`, `original_framing`, `synthesized_position`) — difflib SequenceMatcher ratio (character-level). 1.0 = identical; 0.7+ = very similar; 0.4–0.7 = material drift (paraphrase or reshape); <0.4 = shape-shift.
- List fields (`live_constraints`, `reasoning_passages`, `dropped_threads`) — Jaccard on normalized item text (strip, lowercase).
- `live_constraints_canonical_key` — Jaccard on `canonical_key` slugs with empty-string exclusion: empty/missing keys are filtered from BOTH sets before intersection so two failed extractions do not trivially match. A pair with all-empty keys on both sides is reported as `—` (undefined); the failure rate lives in `invalid_key_rate`.
- `invalid_key_rate` — share of constraints where `canonical_key` is missing or empty (the LLM failed the slug format rule). Per-run + overall. Acceptance gate target: ≤ 10%.
- `fabricated_count_per_run` — passages the extractor marked as not-a-literal-substring. Higher is worse.

## Aggregate drift

| Field | Metric | Mean | Min | Max |
|---|---|---|---|---|
| `decision_situation` | similarity | 0.794 | 0.691 | 1.000 |
| `original_framing` | similarity | 0.854 | 0.793 | 0.962 |
| `synthesized_position` | similarity | 0.569 | 0.521 | 0.661 |
| `live_constraints` | jaccard | 0.048 | 0.000 | 0.143 |
| `reasoning_passages` | jaccard | 0.388 | 0.200 | 0.714 |
| `dropped_threads` | jaccard | 0.000 | 0.000 | 0.000 |
| `live_constraints_canonical_key` | jaccard (empty-excl) | — | — | — |
> `live_constraints_canonical_key` has 3 undefined pair(s) — both runs had no valid canonical_keys. See `invalid_key_rate` below.
| `live_constraints_canonical_key_embedding` | cosine (empty-excl) | — | — | — |

**`invalid_key_rate` per run:** [1.0, 1.0, 1.0]
**`invalid_key_rate` overall:** 1.000 (12 invalid of 12 total constraints)
**Fabricated-quote counts per run:** [1, 0, 1]
**Capture health per run:** ['good', 'good', 'good']

## Pairwise detail

### `20260423T102019Zdrift0` vs `20260423T102028Zdrift1`
- **decision_situation**: similarity=0.691, lengths 144 ↔ 125
- **original_framing**: similarity=0.793, lengths 184 ↔ 139
- **synthesized_position**: similarity=0.661, lengths 429 ↔ 337
- **live_constraints**: jaccard=0.000, counts 4 ↔ 4
- **reasoning_passages**: jaccard=0.714, counts 5 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 4 ↔ 4
- **fabricated**: a=1, b=0

### `20260423T102019Zdrift0` vs `20260423T102036Zdrift2`
- **decision_situation**: similarity=1.000, lengths 144 ↔ 144
- **original_framing**: similarity=0.808, lengths 184 ↔ 150
- **synthesized_position**: similarity=0.521, lengths 429 ↔ 419
- **live_constraints**: jaccard=0.000, counts 4 ↔ 4
- **reasoning_passages**: jaccard=0.250, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 4 ↔ 4
- **fabricated**: a=1, b=1

### `20260423T102028Zdrift1` vs `20260423T102036Zdrift2`
- **decision_situation**: similarity=0.691, lengths 125 ↔ 144
- **original_framing**: similarity=0.962, lengths 139 ↔ 150
- **synthesized_position**: similarity=0.524, lengths 337 ↔ 419
- **live_constraints**: jaccard=0.143, counts 4 ↔ 4
- **reasoning_passages**: jaccard=0.200, counts 7 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 4 ↔ 4
- **fabricated**: a=0, b=1
