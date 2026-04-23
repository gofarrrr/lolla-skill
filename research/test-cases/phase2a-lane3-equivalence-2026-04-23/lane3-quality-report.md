# Phase 2a Lane 3 quality check — 2026-04-23

Measurement: 5 case(s) × 2 paths × N=3 runs. Wall time: 1013.9s.

**Metrics definitions:**
- `elements`: `frame_pressure_card.frame_elements` count (0-5)
- `dropped`: `frame_pressure_card.dropped_frame_elements` count — LOWER IS BETTER
- `drop_rate`: dropped / (elements + dropped) aggregated across N runs for this path
- `reframings`: `frame_pressure_card.reframings` count (0-2)

## Aggregate across all cases

| path | total runs | elements (mean) | dropped (mean) | drop_rate | reframings (mean) |
|------|-----------|-----------------|----------------|-----------|-------------------|
| old  | 15 | 1.93 | 0 | 0.0 | 1.87 |
| new  | 15 | 2.2 | 0 | 0.0 | 2 |

**Aggregate drop-rate gate:** PASS (new=0.0, old=0.0, delta=+0.000; ≤ 0.05 tolerance).

## Per-case detail

### `friendship_money`

| path | n | elements (mean ± sd) | dropped (mean ± sd) | drop_rate | reframings (mean) |
|------|---|----------------------|---------------------|-----------|-------------------|
| old  | 3 | 2 ± 0.0 | 0 ± 0.0 | 0.0 | 2 |
| new  | 3 | 2 ± 0.0 | 0 ± 0.0 | 0.0 | 2 |

<details><summary>per-run detail</summary>

| path | run | elements | types | dropped | drop_reasons | reframings | move_types |
|------|-----|----------|-------|---------|--------------|------------|------------|
| old | 0 | 2 | assumption:1, suppressed_counterfactual:1 | 0 | - | 2 | constraint_relaxation:1, inversion:1 |
| old | 1 | 2 | assumption:1, suppressed_counterfactual:1 | 0 | - | 2 | constraint_relaxation:1, inversion:1 |
| old | 2 | 2 | assumption:1, suppressed_counterfactual:1 | 0 | - | 2 | constraint_relaxation:1, perspective_shift:1 |
| new | 0 | 2 | assumption:2 | 0 | - | 2 | constraint_relaxation:1, scope_expansion:1 |
| new | 1 | 2 | assumption:1, suppressed_counterfactual:1 | 0 | - | 2 | constraint_relaxation:1, perspective_shift:1 |
| new | 2 | 2 | assumption:2 | 0 | - | 2 | inversion:1, perspective_shift:1 |

</details>

### `messy_three_problems`

| path | n | elements (mean ± sd) | dropped (mean ± sd) | drop_rate | reframings (mean) |
|------|---|----------------------|---------------------|-----------|-------------------|
| old  | 3 | 2.67 ± 0.58 | 0 ± 0.0 | 0.0 | 2 |
| new  | 3 | 2.67 ± 0.58 | 0 ± 0.0 | 0.0 | 2 |

<details><summary>per-run detail</summary>

| path | run | elements | types | dropped | drop_reasons | reframings | move_types |
|------|-----|----------|-------|---------|--------------|------------|------------|
| old | 0 | 3 | borrowed_premise:1, option_space_collapse:1, suppressed_counterfactual:1 | 0 | - | 2 | constraint_relaxation:1, scope_expansion:1 |
| old | 1 | 3 | assumption:2, suppressed_counterfactual:1 | 0 | - | 2 | constraint_relaxation:1, inversion:1 |
| old | 2 | 2 | option_space_collapse:1, suppressed_counterfactual:1 | 0 | - | 2 | constraint_relaxation:1, perspective_shift:1 |
| new | 0 | 3 | assumption:1, mutable_constraint:2 | 0 | - | 2 | constraint_relaxation:1, perspective_shift:1 |
| new | 1 | 2 | mutable_constraint:2 | 0 | - | 2 | constraint_relaxation:1, scope_expansion:1 |
| new | 2 | 3 | assumption:1, mutable_constraint:2 | 0 | - | 2 | constraint_relaxation:1, scope_expansion:1 |

</details>

### `multi_offer`

| path | n | elements (mean ± sd) | dropped (mean ± sd) | drop_rate | reframings (mean) |
|------|---|----------------------|---------------------|-----------|-------------------|
| old  | 3 | 2 ± 0.0 | 0 ± 0.0 | 0.0 | 2 |
| new  | 3 | 1.67 ± 0.58 | 0 ± 0.0 | 0.0 | 2 |

<details><summary>per-run detail</summary>

| path | run | elements | types | dropped | drop_reasons | reframings | move_types |
|------|-----|----------|-------|---------|--------------|------------|------------|
| old | 0 | 2 | assumption:1, option_space_collapse:1 | 0 | - | 2 | constraint_relaxation:1, perspective_shift:1 |
| old | 1 | 2 | assumption:1, option_space_collapse:1 | 0 | - | 2 | constraint_relaxation:1, scope_expansion:1 |
| old | 2 | 2 | assumption:1, option_space_collapse:1 | 0 | - | 2 | constraint_relaxation:1, scope_expansion:1 |
| new | 0 | 1 | assumption:1 | 0 | - | 2 | constraint_relaxation:1, scope_expansion:1 |
| new | 1 | 2 | mutable_constraint:1, option_space_collapse:1 | 0 | - | 2 | constraint_relaxation:1, scope_expansion:1 |
| new | 2 | 2 | assumption:1, mutable_constraint:1 | 0 | - | 2 | constraint_relaxation:1, scope_expansion:1 |

</details>

### `oncologist`

| path | n | elements (mean ± sd) | dropped (mean ± sd) | drop_rate | reframings (mean) |
|------|---|----------------------|---------------------|-----------|-------------------|
| old  | 3 | 2 ± 0.0 | 0 ± 0.0 | 0.0 | 2 |
| new  | 3 | 2.67 ± 0.58 | 0 ± 0.0 | 0.0 | 2 |

<details><summary>per-run detail</summary>

| path | run | elements | types | dropped | drop_reasons | reframings | move_types |
|------|-----|----------|-------|---------|--------------|------------|------------|
| old | 0 | 2 | mutable_constraint:1, suppressed_counterfactual:1 | 0 | - | 2 | constraint_relaxation:1, perspective_shift:1 |
| old | 1 | 2 | mutable_constraint:1, suppressed_counterfactual:1 | 0 | - | 2 | constraint_relaxation:1, perspective_shift:1 |
| old | 2 | 2 | mutable_constraint:1, suppressed_counterfactual:1 | 0 | - | 2 | constraint_relaxation:1, perspective_shift:1 |
| new | 0 | 2 | mutable_constraint:1, suppressed_counterfactual:1 | 0 | - | 2 | constraint_relaxation:1, scope_expansion:1 |
| new | 1 | 3 | assumption:1, mutable_constraint:1, suppressed_counterfactual:1 | 0 | - | 2 | constraint_relaxation:1, scope_expansion:1 |
| new | 2 | 3 | assumption:1, mutable_constraint:1, suppressed_counterfactual:1 | 0 | - | 2 | constraint_relaxation:1, scope_expansion:1 |

</details>

### `parenting_teen`

| path | n | elements (mean ± sd) | dropped (mean ± sd) | drop_rate | reframings (mean) |
|------|---|----------------------|---------------------|-----------|-------------------|
| old  | 3 | 1 ± 0.0 | 0 ± 0.0 | 0.0 | 1.33 |
| new  | 3 | 2 ± 0.0 | 0 ± 0.0 | 0.0 | 2 |

<details><summary>per-run detail</summary>

| path | run | elements | types | dropped | drop_reasons | reframings | move_types |
|------|-----|----------|-------|---------|--------------|------------|------------|
| old | 0 | 1 | suppressed_counterfactual:1 | 0 | - | 2 | constraint_relaxation:1, inversion:1 |
| old | 1 | 1 | suppressed_counterfactual:1 | 0 | - | 1 | constraint_relaxation:1 |
| old | 2 | 1 | suppressed_counterfactual:1 | 0 | - | 1 | constraint_relaxation:1 |
| new | 0 | 2 | assumption:1, option_space_collapse:1 | 0 | - | 2 | constraint_relaxation:1, perspective_shift:1 |
| new | 1 | 2 | assumption:2 | 0 | - | 2 | inversion:1, perspective_shift:1 |
| new | 2 | 2 | assumption:1, mutable_constraint:1 | 0 | - | 2 | constraint_relaxation:1, inversion:1 |

</details>

**Per-case regression summary:** zero regressions flagged.
