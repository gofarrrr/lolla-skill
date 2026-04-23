# Phase 2a Lane 3 quality check — 2026-04-23

**Mode: DRY RUN** — N=1 on a subset of cases. Not an acceptance-gate run.

Measurement: 1 case(s) × 2 paths × N=1 runs. Wall time: 119.0s.

**Metrics definitions:**
- `elements`: `frame_pressure_card.frame_elements` count (0-5)
- `dropped`: `frame_pressure_card.dropped_frame_elements` count — LOWER IS BETTER
- `drop_rate`: dropped / (elements + dropped) aggregated across N runs for this path
- `reframings`: `frame_pressure_card.reframings` count (0-2)

## Aggregate across all cases

| path | total runs | elements (mean) | dropped (mean) | drop_rate | reframings (mean) |
|------|-----------|-----------------|----------------|-----------|-------------------|
| old  | 1 | 2 | 0 | 0.0 | 2 |
| new  | 1 | 2 | 0 | 0.0 | 2 |

**Aggregate drop-rate gate:** PASS (new=0.0, old=0.0, delta=+0.000; ≤ 0.05 tolerance).

## Per-case detail

### `oncologist`

| path | n | elements (mean ± sd) | dropped (mean ± sd) | drop_rate | reframings (mean) |
|------|---|----------------------|---------------------|-----------|-------------------|
| old  | 1 | 2 ± 0.0 | 0 ± 0.0 | 0.0 | 2 |
| new  | 1 | 2 ± 0.0 | 0 ± 0.0 | 0.0 | 2 |

<details><summary>per-run detail</summary>

| path | run | elements | types | dropped | drop_reasons | reframings | move_types |
|------|-----|----------|-------|---------|--------------|------------|------------|
| old | 0 | 2 | assumption:1, option_space_collapse:1 | 0 | - | 2 | constraint_relaxation:1, scope_expansion:1 |
| new | 0 | 2 | mutable_constraint:1, option_space_collapse:1 | 0 | - | 2 | constraint_relaxation:1, scope_expansion:1 |

</details>

**Per-case regression summary:** zero regressions flagged.
