# Phase 2d Lane 2 quality check — 2026-04-24

Measurement: 10 case(s) × 2 paths × N=3 runs. Wall time: 4683.3s.

**Lane 2 direct metrics:**
- `fp_valid` / `fp_dropped`: fingerprint moves that passed/failed substring validation against the audit target (flattened `vanilla_answer` on old, joined assistant turns on new).
- `drop_rate`: `fp_dropped / (fp_valid + fp_dropped)`. Analog to Lane 3's drop rate. A drop here means the LLM cited evidence from CONTEXT (user turns or extractor summaries), which is rejected under the new contract.
- `detected`: verified candidate models accepted into `companion_card.detected_models`.
- `rejected`: candidates rejected at verification.

**Cascade L1/L3/L4:** Lane 2 does not feed Lanes 1/3/4 anti-echo — cascade numbers should be unchanged vs. old path. Any cascade drift signals noise from Lane 1's anti-echo shift rippling differently, not a Lane-2-induced change.

## Aggregate across all cases

| path | total | errored | fp_valid | fp_dropped | drop_rate | detected | rejected | 0-detected | L1/L3/L4 |
|------|-------|---------|----------|------------|-----------|----------|----------|------------|----------|
| old | 30 | 0 | 6.67 | 0 | 0.0 | 3.5 | 56.03 | 0 | 1.77 / 1.63 / 4.2 |
| new | 30 | 0 | 6.9 | 0 | 0.0 | 4.03 | 51.97 | 2 | 1.03 / 1.83 / 4.13 |

**Aggregate regression summary:** 1 of 10 cases regressed. Diagnose in PR.

## Per-case detail

### `friendship_money`

| path | n | fp_valid | fp_dropped | drop_rate | detected | rejected | cascade L1/L3/L4 |
|------|---|----------|------------|-----------|----------|----------|-------------------|
| old | 3 | 6 | 0 | 0.0 | 2 | 58 | 2 / 2 / 4 |
| new | 3 | 6.33 | 0 | 0.0 | 3.67 | 56.33 | 1 / 2 / 4 |

<details><summary>per-run detail</summary>

| path | run | fp_raw | fp_valid | fp_drop | drop_rate | detected | rejected | L1/L3/L4 |
|------|-----|--------|----------|---------|-----------|----------|----------|----------|
| old | 0 | 6 | 6 | 0 | 0.00 | 1 | 59 | 2/2/4 |
| old | 1 | 6 | 6 | 0 | 0.00 | 3 | 57 | 2/2/4 |
| old | 2 | 6 | 6 | 0 | 0.00 | 2 | 58 | 2/2/4 |
| new | 0 | 6 | 6 | 0 | 0.00 | 5 | 55 | 1/2/4 |
| new | 1 | 6 | 6 | 0 | 0.00 | 3 | 57 | 1/2/4 |
| new | 2 | 7 | 7 | 0 | 0.00 | 3 | 57 | 1/2/4 |

</details>

### `messy_three_problems`

| path | n | fp_valid | fp_dropped | drop_rate | detected | rejected | cascade L1/L3/L4 |
|------|---|----------|------------|-----------|----------|----------|-------------------|
| old | 3 | 6.67 | 0 | 0.0 | 4 | 56 | 1 / 2 / 4.33 |
| new | 3 | 7 | 0 | 0.0 | 4.67 | 55 | 1 / 2 / 4.67 |

<details><summary>per-run detail</summary>

| path | run | fp_raw | fp_valid | fp_drop | drop_rate | detected | rejected | L1/L3/L4 |
|------|-----|--------|----------|---------|-----------|----------|----------|----------|
| old | 0 | 6 | 6 | 0 | 0.00 | 4 | 56 | 1/2/4 |
| old | 1 | 7 | 7 | 0 | 0.00 | 4 | 56 | 1/2/5 |
| old | 2 | 7 | 7 | 0 | 0.00 | 4 | 56 | 1/2/4 |
| new | 0 | 7 | 7 | 0 | 0.00 | 5 | 54 | 1/2/5 |
| new | 1 | 7 | 7 | 0 | 0.00 | 5 | 55 | 1/2/5 |
| new | 2 | 7 | 7 | 0 | 0.00 | 4 | 56 | 1/2/4 |

</details>

### `multi_offer`

| path | n | fp_valid | fp_dropped | drop_rate | detected | rejected | cascade L1/L3/L4 |
|------|---|----------|------------|-----------|----------|----------|-------------------|
| old | 3 | 7 | 0 | 0.0 | 3.67 | 56 | 2.33 / 2 / 5 |
| new | 3 | 7 | 0 | 0.0 | 5 | 54.67 | 0 / 0.67 / 4 |

<details><summary>per-run detail</summary>

| path | run | fp_raw | fp_valid | fp_drop | drop_rate | detected | rejected | L1/L3/L4 |
|------|-----|--------|----------|---------|-----------|----------|----------|----------|
| old | 0 | 7 | 7 | 0 | 0.00 | 5 | 55 | 3/2/5 |
| old | 1 | 7 | 7 | 0 | 0.00 | 2 | 58 | 2/2/5 |
| old | 2 | 7 | 7 | 0 | 0.00 | 4 | 55 | 2/2/5 |
| new | 0 | 7 | 7 | 0 | 0.00 | 5 | 55 | 0/1/5 |
| new | 1 | 7 | 7 | 0 | 0.00 | 5 | 55 | 0/0/4 |
| new | 2 | 7 | 7 | 0 | 0.00 | 5 | 54 | 0/1/3 |

</details>

### `oncologist`

| path | n | fp_valid | fp_dropped | drop_rate | detected | rejected | cascade L1/L3/L4 |
|------|---|----------|------------|-----------|----------|----------|-------------------|
| old | 3 | 7 | 0 | 0.0 | 3.67 | 56 | 2 / 2.33 / 4 |
| new | 3 | 7 | 0 | 0.0 | 4 | 56 | 2.33 / 2.33 / 4.67 |

<details><summary>per-run detail</summary>

| path | run | fp_raw | fp_valid | fp_drop | drop_rate | detected | rejected | L1/L3/L4 |
|------|-----|--------|----------|---------|-----------|----------|----------|----------|
| old | 0 | 7 | 7 | 0 | 0.00 | 4 | 55 | 2/3/4 |
| old | 1 | 7 | 7 | 0 | 0.00 | 3 | 57 | 2/2/4 |
| old | 2 | 7 | 7 | 0 | 0.00 | 4 | 56 | 2/2/4 |
| new | 0 | 7 | 7 | 0 | 0.00 | 5 | 55 | 2/2/5 |
| new | 1 | 7 | 7 | 0 | 0.00 | 3 | 57 | 2/3/5 |
| new | 2 | 7 | 7 | 0 | 0.00 | 4 | 56 | 3/2/4 |

</details>

### `parenting_teen`

| path | n | fp_valid | fp_dropped | drop_rate | detected | rejected | cascade L1/L3/L4 |
|------|---|----------|------------|-----------|----------|----------|-------------------|
| old | 3 | 7.33 | 0 | 0.0 | 4.67 | 52.67 | 1.67 / 0.33 / 3.67 |
| new | 3 | 7 | 0 | 0.0 | 5 | 52.67 | 0.67 / 0.67 / 3.67 |

<details><summary>per-run detail</summary>

| path | run | fp_raw | fp_valid | fp_drop | drop_rate | detected | rejected | L1/L3/L4 |
|------|-----|--------|----------|---------|-----------|----------|----------|----------|
| old | 0 | 7 | 7 | 0 | 0.00 | 5 | 51 | 1/0/3 |
| old | 1 | 8 | 8 | 0 | 0.00 | 5 | 51 | 2/1/4 |
| old | 2 | 7 | 7 | 0 | 0.00 | 4 | 56 | 2/0/4 |
| new | 0 | 7 | 7 | 0 | 0.00 | 5 | 51 | 0/1/4 |
| new | 1 | 7 | 7 | 0 | 0.00 | 5 | 53 | 1/0/4 |
| new | 2 | 7 | 7 | 0 | 0.00 | 5 | 54 | 1/1/3 |

</details>

### `phd_research`

| path | n | fp_valid | fp_dropped | drop_rate | detected | rejected | cascade L1/L3/L4 |
|------|---|----------|------------|-----------|----------|----------|-------------------|
| old | 3 | 6.33 | 0 | 0.0 | 3.67 | 55.67 | 1.67 / 2 / 4.33 |
| new | 3 | 7.33 | 0 | 0.0 | 4.33 | 54.33 | 2.33 / 1.67 / 4.67 |

<details><summary>per-run detail</summary>

| path | run | fp_raw | fp_valid | fp_drop | drop_rate | detected | rejected | L1/L3/L4 |
|------|-----|--------|----------|---------|-----------|----------|----------|----------|
| old | 0 | 7 | 7 | 0 | 0.00 | 5 | 53 | 2/2/4 |
| old | 1 | 6 | 6 | 0 | 0.00 | 4 | 56 | 1/2/4 |
| old | 2 | 6 | 6 | 0 | 0.00 | 2 | 58 | 2/2/5 |
| new | 0 | 8 | 8 | 0 | 0.00 | 4 | 55 | 2/2/5 |
| new | 1 | 7 | 7 | 0 | 0.00 | 4 | 53 | 3/1/5 |
| new | 2 | 7 | 7 | 0 | 0.00 | 5 | 55 | 2/2/4 |

</details>

### `real_estate`

| path | n | fp_valid | fp_dropped | drop_rate | detected | rejected | cascade L1/L3/L4 |
|------|---|----------|------------|-----------|----------|----------|-------------------|
| old | 3 | 6.67 | 0 | 0.0 | 2 | 58 | 0.33 / 1 / 5 |
| new | 3 | 7 | 0 | 0.0 | 3.33 | 56.67 | 0 / 2 / 4.33 |

<details><summary>per-run detail</summary>

| path | run | fp_raw | fp_valid | fp_drop | drop_rate | detected | rejected | L1/L3/L4 |
|------|-----|--------|----------|---------|-----------|----------|----------|----------|
| old | 0 | 7 | 7 | 0 | 0.00 | 2 | 58 | 1/1/5 |
| old | 1 | 6 | 6 | 0 | 0.00 | 3 | 57 | 0/1/5 |
| old | 2 | 7 | 7 | 0 | 0.00 | 1 | 59 | 0/1/5 |
| new | 0 | 7 | 7 | 0 | 0.00 | 3 | 57 | 0/2/5 |
| new | 1 | 7 | 7 | 0 | 0.00 | 4 | 56 | 0/2/4 |
| new | 2 | 7 | 7 | 0 | 0.00 | 3 | 57 | 0/2/4 |

</details>

### `startup_pivot`

| path | n | fp_valid | fp_dropped | drop_rate | detected | rejected | cascade L1/L3/L4 |
|------|---|----------|------------|-----------|----------|----------|-------------------|
| old | 3 | 7 | 0 | 0.0 | 4 | 55.67 | 2.67 / 1.33 / 3.67 |
| new | 3 | 6.67 | 0 | 0.0 | 4.67 | 40.67 | 1.67 / 2 / 3.33 |

<details><summary>per-run detail</summary>

| path | run | fp_raw | fp_valid | fp_drop | drop_rate | detected | rejected | L1/L3/L4 |
|------|-----|--------|----------|---------|-----------|----------|----------|----------|
| old | 0 | 7 | 7 | 0 | 0.00 | 5 | 55 | 2/1/4 |
| old | 1 | 7 | 7 | 0 | 0.00 | 5 | 54 | 3/1/4 |
| old | 2 | 7 | 7 | 0 | 0.00 | 2 | 58 | 3/2/3 |
| new | 0 | 7 | 7 | 0 | 0.00 | 5 | 54 | 2/2/4 |
| new | 1 | 6 | 6 | 0 | 0.00 | 4 | 55 | 2/2/2 |
| new | 2 | 7 | 7 | 0 | 0.00 | 5 | 13 | 1/2/4 |

</details>

### `user_has_plan`

| path | n | fp_valid | fp_dropped | drop_rate | detected | rejected | cascade L1/L3/L4 |
|------|---|----------|------------|-----------|----------|----------|-------------------|
| old | 3 | 6 | 0 | 0.0 | 3.33 | 56.67 | 2 / 2 / 3.33 |
| new | 3 | 7 | 0 | 0.0 | 3 | 36 | 0.33 / 3 / 4 |

<details><summary>per-run detail</summary>

| path | run | fp_raw | fp_valid | fp_drop | drop_rate | detected | rejected | L1/L3/L4 |
|------|-----|--------|----------|---------|-----------|----------|----------|----------|
| old | 0 | 6 | 6 | 0 | 0.00 | 2 | 58 | 2/2/3 |
| old | 1 | 6 | 6 | 0 | 0.00 | 3 | 57 | 2/2/4 |
| old | 2 | 6 | 6 | 0 | 0.00 | 5 | 55 | 2/2/3 |
| new | 0 | 7 | 7 | 0 | 0.00 | 0 | 0 | 0/3/4 |
| new | 1 | 7 | 7 | 0 | 0.00 | 4 | 55 | 1/3/4 |
| new | 2 | 7 | 7 | 0 | 0.00 | 5 | 53 | 0/3/4 |

</details>

### `whistleblower`

**Regression flags:**
- `detected_models_regression: new median=3 vs old=5 (dropped ≥2)`

| path | n | fp_valid | fp_dropped | drop_rate | detected | rejected | cascade L1/L3/L4 |
|------|---|----------|------------|-----------|----------|----------|-------------------|
| old | 3 | 6.67 | 0 | 0.0 | 4 | 55.67 | 2 / 1.33 / 4.67 |
| new | 3 | 6.67 | 0 | 0.0 | 2.67 | 57.33 | 1 / 2 / 4 |

<details><summary>per-run detail</summary>

| path | run | fp_raw | fp_valid | fp_drop | drop_rate | detected | rejected | L1/L3/L4 |
|------|-----|--------|----------|---------|-----------|----------|----------|----------|
| old | 0 | 7 | 7 | 0 | 0.00 | 5 | 55 | 2/0/4 |
| old | 1 | 6 | 6 | 0 | 0.00 | 2 | 58 | 2/2/5 |
| old | 2 | 7 | 7 | 0 | 0.00 | 5 | 54 | 2/2/5 |
| new | 0 | 7 | 7 | 0 | 0.00 | 3 | 57 | 1/2/4 |
| new | 1 | 7 | 7 | 0 | 0.00 | 5 | 55 | 1/2/4 |
| new | 2 | 6 | 6 | 0 | 0.00 | 0 | 60 | 1/2/4 |

</details>

