# Extraction drift report — marcus-extraction-drift

Generated: 2026-04-22T13:38:22Z
Conversation: `/private/tmp/lolla_20260422T113930Z_conversation.txt` (25742 bytes)
Runs: 3
Run IDs: 20260422T133822Zdrift0, 20260422T133834Zdrift1, 20260422T133845Zdrift2

**Reading the metrics:**
- Free-text fields (`decision_situation`, `original_framing`, `synthesized_position`) — difflib SequenceMatcher ratio (character-level). 1.0 = identical; 0.7+ = very similar; 0.4–0.7 = material drift (paraphrase or reshape); <0.4 = shape-shift.
- List fields (`live_constraints`, `reasoning_passages`, `dropped_threads`) — Jaccard on normalized item text (strip, lowercase).
- `fabricated_count_per_run` — passages the extractor marked as not-a-literal-substring. Higher is worse.

## Aggregate drift

| Field | Metric | Mean | Min | Max |
|---|---|---|---|---|
| `decision_situation` | similarity | 0.256 | 0.220 | 0.301 |
| `original_framing` | similarity | 0.312 | 0.184 | 0.527 |
| `synthesized_position` | similarity | 0.277 | 0.178 | 0.355 |
| `live_constraints` | jaccard | 0.000 | 0.000 | 0.000 |
| `reasoning_passages` | jaccard | 0.389 | 0.250 | 0.667 |
| `dropped_threads` | jaccard | 0.000 | 0.000 | 0.000 |

**Fabricated-quote counts per run:** [0, 0, 0]
**Capture health per run:** ['good', 'good', 'good']

## Pairwise detail

### `20260422T133822Zdrift0` vs `20260422T133834Zdrift1`
- **decision_situation**: similarity=0.220, lengths 592 ↔ 471
- **original_framing**: similarity=0.184, lengths 445 ↔ 403
- **synthesized_position**: similarity=0.355, lengths 849 ↔ 781
- **live_constraints**: jaccard=0.000, counts 5 ↔ 4
- **reasoning_passages**: jaccard=0.250, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **fabricated**: a=0, b=0

### `20260422T133822Zdrift0` vs `20260422T133845Zdrift2`
- **decision_situation**: similarity=0.301, lengths 592 ↔ 564
- **original_framing**: similarity=0.224, lengths 445 ↔ 405
- **synthesized_position**: similarity=0.178, lengths 849 ↔ 912
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.667, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **fabricated**: a=0, b=0

### `20260422T133834Zdrift1` vs `20260422T133845Zdrift2`
- **decision_situation**: similarity=0.247, lengths 471 ↔ 564
- **original_framing**: similarity=0.527, lengths 403 ↔ 405
- **synthesized_position**: similarity=0.298, lengths 781 ↔ 912
- **live_constraints**: jaccard=0.000, counts 4 ↔ 5
- **reasoning_passages**: jaccard=0.250, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **fabricated**: a=0, b=0
