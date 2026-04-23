# Extraction drift report — contract-phase1-diagnostic

Generated: 2026-04-23T07:29:24Z
Conversation: `/private/tmp/lolla_20260422T155622Z_conversation.txt` (26304 bytes)
Runs: 5
Run IDs: 20260423T072924Zdrift0, 20260423T072934Zdrift1, 20260423T072945Zdrift2, 20260423T072952Zdrift3, 20260423T073006Zdrift4

**Reading the metrics:**
- Free-text fields (`decision_situation`, `original_framing`, `synthesized_position`) — difflib SequenceMatcher ratio (character-level). 1.0 = identical; 0.7+ = very similar; 0.4–0.7 = material drift (paraphrase or reshape); <0.4 = shape-shift.
- List fields (`live_constraints`, `reasoning_passages`, `dropped_threads`) — Jaccard on normalized item text (strip, lowercase).
- `live_constraints_canonical_key` — Jaccard on `canonical_key` slugs with empty-string exclusion: empty/missing keys are filtered from BOTH sets before intersection so two failed extractions do not trivially match. A pair with all-empty keys on both sides is reported as `—` (undefined); the failure rate lives in `invalid_key_rate`.
- `invalid_key_rate` — share of constraints where `canonical_key` is missing or empty (the LLM failed the slug format rule). Per-run + overall. Acceptance gate target: ≤ 10%.
- `fabricated_count_per_run` — passages the extractor marked as not-a-literal-substring. Higher is worse.

## Aggregate drift

| Field | Metric | Mean | Min | Max |
|---|---|---|---|---|
| `decision_situation` | similarity | 0.246 | 0.083 | 0.602 |
| `original_framing` | similarity | 0.103 | 0.036 | 0.260 |
| `synthesized_position` | similarity | 0.254 | 0.105 | 0.588 |
| `live_constraints` | jaccard | 0.063 | 0.000 | 0.222 |
| `reasoning_passages` | jaccard | 0.426 | 0.222 | 1.000 |
| `dropped_threads` | jaccard | 0.150 | 0.000 | 1.000 |
| `live_constraints_canonical_key` | jaccard (empty-excl) | — | — | — |
> `live_constraints_canonical_key` has 10 undefined pair(s) — both runs had no valid canonical_keys. See `invalid_key_rate` below.

**`invalid_key_rate` per run:** [1.0, 1.0, 1.0, 1.0, 1.0]
**`invalid_key_rate` overall:** 1.000 (27 invalid of 27 total constraints)
**Fabricated-quote counts per run:** [1, 0, 0, 0, 0]
**Capture health per run:** ['good', 'good', 'good', 'good', 'good']

## Pairwise detail

### `20260423T072924Zdrift0` vs `20260423T072934Zdrift1`
- **decision_situation**: similarity=0.305, lengths 252 ↔ 483
- **original_framing**: similarity=0.210, lengths 385 ↔ 453
- **synthesized_position**: similarity=0.353, lengths 718 ↔ 788
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.571, counts 5 ↔ 6
- **dropped_threads**: jaccard=1.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=1, b=0

### `20260423T072924Zdrift0` vs `20260423T072945Zdrift2`
- **decision_situation**: similarity=0.083, lengths 252 ↔ 596
- **original_framing**: similarity=0.054, lengths 385 ↔ 437
- **synthesized_position**: similarity=0.271, lengths 718 ↔ 849
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.222, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.250, counts 2 ↔ 3
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=1, b=0

### `20260423T072924Zdrift0` vs `20260423T072952Zdrift3`
- **decision_situation**: similarity=0.387, lengths 252 ↔ 430
- **original_framing**: similarity=0.077, lengths 385 ↔ 441
- **synthesized_position**: similarity=0.274, lengths 718 ↔ 675
- **live_constraints**: jaccard=0.100, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.429, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=1, b=0

### `20260423T072924Zdrift0` vs `20260423T073006Zdrift4`
- **decision_situation**: similarity=0.119, lengths 252 ↔ 620
- **original_framing**: similarity=0.054, lengths 385 ↔ 463
- **synthesized_position**: similarity=0.250, lengths 718 ↔ 893
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.222, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=1, b=0

### `20260423T072934Zdrift1` vs `20260423T072945Zdrift2`
- **decision_situation**: similarity=0.159, lengths 483 ↔ 596
- **original_framing**: similarity=0.070, lengths 453 ↔ 437
- **synthesized_position**: similarity=0.195, lengths 788 ↔ 849
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.500, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.250, counts 2 ↔ 3
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `20260423T072934Zdrift1` vs `20260423T072952Zdrift3`
- **decision_situation**: similarity=0.254, lengths 483 ↔ 430
- **original_framing**: similarity=0.047, lengths 453 ↔ 441
- **synthesized_position**: similarity=0.154, lengths 788 ↔ 675
- **live_constraints**: jaccard=0.100, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.375, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `20260423T072934Zdrift1` vs `20260423T073006Zdrift4`
- **decision_situation**: similarity=0.279, lengths 483 ↔ 620
- **original_framing**: similarity=0.103, lengths 453 ↔ 463
- **synthesized_position**: similarity=0.105, lengths 788 ↔ 893
- **live_constraints**: jaccard=0.100, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.500, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `20260423T072945Zdrift2` vs `20260423T072952Zdrift3`
- **decision_situation**: similarity=0.142, lengths 596 ↔ 430
- **original_framing**: similarity=0.036, lengths 437 ↔ 441
- **synthesized_position**: similarity=0.150, lengths 849 ↔ 675
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.222, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `20260423T072945Zdrift2` vs `20260423T073006Zdrift4`
- **decision_situation**: similarity=0.602, lengths 596 ↔ 620
- **original_framing**: similarity=0.260, lengths 437 ↔ 463
- **synthesized_position**: similarity=0.588, lengths 849 ↔ 893
- **live_constraints**: jaccard=0.222, counts 5 ↔ 6
- **reasoning_passages**: jaccard=1.000, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `20260423T072952Zdrift3` vs `20260423T073006Zdrift4`
- **decision_situation**: similarity=0.126, lengths 430 ↔ 620
- **original_framing**: similarity=0.124, lengths 441 ↔ 463
- **synthesized_position**: similarity=0.196, lengths 675 ↔ 893
- **live_constraints**: jaccard=0.000, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.222, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0
