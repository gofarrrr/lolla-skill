# Phase 2c Lane 1 quality check — 2026-04-24

Measurement: 10 case(s) × 2 paths × N=3 runs. Wall time: 3944.0s.

**Metrics definitions (Lane 1 direct):**
- `detected`: size of `detected_tendencies` set (tendencies that passed triage + routing)
- `findings`: total `delta_card.findings` count (each finding = one routed tendency)
- `top`: `delta_card.top_findings` count (tier-1 findings surfaced)
- `compounds`: `delta_card.compound_groups` count (lollapalooza-style confluence)
- `selected_models`: `delta_card.selected_model_ids` count — this is lane1's anti-echo input to Lanes 2/3/4

**Metrics definitions (downstream cascade):**
- `L2/L3/L4`: companion detected models / frame elements / structural gaps
- These change only if Lane 1's anti-echo set changes enough to shift downstream lane outputs — the cascade signal.

**Note on Lane 1 signal shape:** there is no drop-rate metric (no evidence-substring validation downstream of Pass 2). Quality evidence comes from per-case stability of detected tendencies + findings counts + downstream cascade magnitude. The 0-findings rate across all new-path runs is tracked separately below.

## Aggregate across all cases

| path | total runs | errored | detected (mean) | findings (mean) | compounds (mean) | selected_models (mean) | 0-findings count | cascade L2/L3/L4 |
|------|-----------|---------|-----------------|-----------------|------------------|------------------------|------------------|-------------------|
| old | 30 | 0 | 1.6 | 1.6 | 0 | 4.03 | 3 | 3.67 / 1.97 / 3.63 |
| new | 30 | 0 | 1 | 1 | 0 | 2.43 | 9 | 3.67 / 1.9 / 4.33 |

**Aggregate regression summary:** 3 of 10 cases regressed. Each must be diagnosed in the PR description (diagnosis-required policy).

## 0-findings anomaly tracking

- old path: 3 zero-findings runs / 30 total (10.0%)
- new path: 9 zero-findings runs / 30 total (30.0%)

## Per-case detail

### `friendship_money`

| path | n | detected | findings | top | compounds | cascade L2/L3/L4 |
|------|---|----------|----------|-----|-----------|-------------------|
| old | 3 | 2 | 2 | 1 | 0 | 3.67 / 1 / 3 |
| new | 3 | 1 | 1 | 1 | 0 | 2.67 / 2 / 4 |

<details><summary>per-run detail</summary>

| path | run | detected_ids | findings | top | compounds | L2/L3/L4 cascade |
|------|-----|--------------|----------|-----|-----------|-------------------|
| old | 0 | availability-misweighing, kantian-fairness | 2 | 1 | 0 | 3/1/3 |
| old | 1 | availability-misweighing, kantian-fairness | 2 | 1 | 0 | 4/1/3 |
| old | 2 | availability-misweighing, kantian-fairness | 2 | 1 | 0 | 4/1/3 |
| new | 0 | kantian-fairness | 1 | 1 | 0 | 2/2/4 |
| new | 1 | kantian-fairness | 1 | 1 | 0 | 3/2/4 |
| new | 2 | kantian-fairness | 1 | 1 | 0 | 3/2/4 |

</details>

### `messy_three_problems`

| path | n | detected | findings | top | compounds | cascade L2/L3/L4 |
|------|---|----------|----------|-----|-----------|-------------------|
| old | 3 | 1 | 1 | 1 | 0 | 2.67 / 2.67 / 4 |
| new | 3 | 1 | 1 | 1 | 0 | 3.33 / 2.33 / 4.67 |

<details><summary>per-run detail</summary>

| path | run | detected_ids | findings | top | compounds | L2/L3/L4 cascade |
|------|-----|--------------|----------|-----|-----------|-------------------|
| old | 0 | stress-influence | 1 | 1 | 0 | 3/3/4 |
| old | 1 | stress-influence | 1 | 1 | 0 | 3/2/4 |
| old | 2 | stress-influence | 1 | 1 | 0 | 2/3/4 |
| new | 0 | stress-influence | 1 | 1 | 0 | 3/3/5 |
| new | 1 | stress-influence | 1 | 1 | 0 | 3/2/5 |
| new | 2 | stress-influence | 1 | 1 | 0 | 4/2/4 |

</details>

### `multi_offer`

**Regression flags:**
- `NEGATIVE_CHECK_empty_delta_card: old path produced findings; new path always empty`

| path | n | detected | findings | top | compounds | cascade L2/L3/L4 |
|------|---|----------|----------|-----|-----------|-------------------|
| old | 3 | 1 | 1 | 1 | 0 | 4.67 / 2 / 3.67 |
| new | 3 | 0 | 0 | 0 | 0 | 5 / 1.33 / 4.33 |

<details><summary>per-run detail</summary>

| path | run | detected_ids | findings | top | compounds | L2/L3/L4 cascade |
|------|-----|--------------|----------|-----|-----------|-------------------|
| old | 0 | stress-influence | 1 | 1 | 0 | 4/2/4 |
| old | 1 | stress-influence | 1 | 1 | 0 | 5/2/3 |
| old | 2 | stress-influence | 1 | 1 | 0 | 5/2/4 |
| new | 0 | - | 0 | 0 | 0 | 5/1/4 |
| new | 1 | - | 0 | 0 | 0 | 5/2/4 |
| new | 2 | - | 0 | 0 | 0 | 5/1/5 |

</details>

### `oncologist`

| path | n | detected | findings | top | compounds | cascade L2/L3/L4 |
|------|---|----------|----------|-----|-----------|-------------------|
| old | 3 | 3 | 3 | 2.67 | 0 | 4 / 2.33 / 4 |
| new | 3 | 2 | 2 | 1.33 | 0 | 3.33 / 2 / 4.67 |

<details><summary>per-run detail</summary>

| path | run | detected_ids | findings | top | compounds | L2/L3/L4 cascade |
|------|-----|--------------|----------|-----|-----------|-------------------|
| old | 0 | availability-misweighing, doubt-avoidance, stress-influence | 3 | 3 | 0 | 4/3/4 |
| old | 1 | availability-misweighing, doubt-avoidance, stress-influence | 3 | 3 | 0 | 4/2/4 |
| old | 2 | availability-misweighing, doubt-avoidance, stress-influence | 3 | 2 | 0 | 4/2/4 |
| new | 0 | availability-misweighing, inconsistency-avoidance | 2 | 1 | 0 | 3/2/5 |
| new | 1 | availability-misweighing, inconsistency-avoidance | 2 | 2 | 0 | 4/2/5 |
| new | 2 | availability-misweighing, inconsistency-avoidance | 2 | 1 | 0 | 3/2/4 |

</details>

### `parenting_teen`

| path | n | detected | findings | top | compounds | cascade L2/L3/L4 |
|------|---|----------|----------|-----|-----------|-------------------|
| old | 3 | 1 | 1 | 1 | 0 | 3 / 2.67 / 3 |
| new | 3 | 1 | 1 | 1 | 0 | 4.33 / 1 / 3.67 |

<details><summary>per-run detail</summary>

| path | run | detected_ids | findings | top | compounds | L2/L3/L4 cascade |
|------|-----|--------------|----------|-----|-----------|-------------------|
| old | 0 | authority-misinfluence | 1 | 1 | 0 | 4/2/3 |
| old | 1 | authority-misinfluence | 1 | 1 | 0 | 0/3/3 |
| old | 2 | authority-misinfluence | 1 | 1 | 0 | 5/3/3 |
| new | 0 | authority-misinfluence | 1 | 1 | 0 | 3/1/3 |
| new | 1 | authority-misinfluence | 1 | 1 | 0 | 5/0/4 |
| new | 2 | authority-misinfluence | 1 | 1 | 0 | 5/2/4 |

</details>

### `phd_research`

| path | n | detected | findings | top | compounds | cascade L2/L3/L4 |
|------|---|----------|----------|-----|-----------|-------------------|
| old | 3 | 1 | 1 | 0.67 | 0 | 5 / 2 / 3.67 |
| new | 3 | 2.67 | 2.67 | 1 | 0 | 4.67 / 2 / 4.33 |

<details><summary>per-run detail</summary>

| path | run | detected_ids | findings | top | compounds | L2/L3/L4 cascade |
|------|-----|--------------|----------|-----|-----------|-------------------|
| old | 0 | availability-misweighing | 1 | 1 | 0 | 5/2/3 |
| old | 1 | availability-misweighing, curiosity | 2 | 1 | 0 | 5/2/4 |
| old | 2 | - | 0 | 0 | 0 | 5/2/4 |
| new | 0 | inconsistency-avoidance, social-proof | 2 | 1 | 0 | 5/2/4 |
| new | 1 | curiosity, inconsistency-avoidance, social-proof | 3 | 1 | 0 | 4/2/4 |
| new | 2 | curiosity, inconsistency-avoidance, social-proof | 3 | 1 | 0 | 5/2/5 |

</details>

### `real_estate`

**Regression flags:**
- `NEGATIVE_CHECK_empty_delta_card: old path produced findings; new path always empty`

| path | n | detected | findings | top | compounds | cascade L2/L3/L4 |
|------|---|----------|----------|-----|-----------|-------------------|
| old | 3 | 0.33 | 0.33 | 0.33 | 0 | 3.33 / 1 / 4 |
| new | 3 | 0 | 0 | 0 | 0 | 2.67 / 2 / 4.67 |

<details><summary>per-run detail</summary>

| path | run | detected_ids | findings | top | compounds | L2/L3/L4 cascade |
|------|-----|--------------|----------|-----|-----------|-------------------|
| old | 0 | - | 0 | 0 | 0 | 2/1/4 |
| old | 1 | - | 0 | 0 | 0 | 4/1/4 |
| old | 2 | availability-misweighing | 1 | 1 | 0 | 4/1/4 |
| new | 0 | - | 0 | 0 | 0 | 2/2/5 |
| new | 1 | - | 0 | 0 | 0 | 2/2/4 |
| new | 2 | - | 0 | 0 | 0 | 4/2/5 |

</details>

### `startup_pivot`

| path | n | detected | findings | top | compounds | cascade L2/L3/L4 |
|------|---|----------|----------|-----|-----------|-------------------|
| old | 3 | 2 | 2 | 1 | 0 | 2.67 / 2 / 3.33 |
| new | 3 | 1.33 | 1.33 | 1 | 0 | 3.33 / 2 / 4 |

<details><summary>per-run detail</summary>

| path | run | detected_ids | findings | top | compounds | L2/L3/L4 cascade |
|------|-----|--------------|----------|-----|-----------|-------------------|
| old | 0 | availability-misweighing, kantian-fairness | 2 | 1 | 0 | 4/2/4 |
| old | 1 | availability-misweighing, kantian-fairness | 2 | 1 | 0 | 3/2/3 |
| old | 2 | availability-misweighing, kantian-fairness | 2 | 1 | 0 | 1/2/3 |
| new | 0 | availability-misweighing | 1 | 1 | 0 | 3/2/4 |
| new | 1 | availability-misweighing | 1 | 1 | 0 | 4/2/4 |
| new | 2 | availability-misweighing, kantian-fairness | 2 | 1 | 0 | 3/2/4 |

</details>

### `user_has_plan`

**Regression flags:**
- `NEGATIVE_CHECK_empty_delta_card: old path produced findings; new path always empty`
- `findings_count_regression: new-path median findings=0 vs old=3 (dropped ≥2)`

| path | n | detected | findings | top | compounds | cascade L2/L3/L4 |
|------|---|----------|----------|-----|-----------|-------------------|
| old | 3 | 2.67 | 2.67 | 1.67 | 0 | 4 / 2 / 4 |
| new | 3 | 0 | 0 | 0 | 0 | 3.33 / 3 / 4 |

<details><summary>per-run detail</summary>

| path | run | detected_ids | findings | top | compounds | L2/L3/L4 cascade |
|------|-----|--------------|----------|-----|-----------|-------------------|
| old | 0 | availability-misweighing, inconsistency-avoidance, social-proof | 3 | 2 | 0 | 5/2/4 |
| old | 1 | availability-misweighing, inconsistency-avoidance | 2 | 1 | 0 | 4/2/3 |
| old | 2 | availability-misweighing, inconsistency-avoidance, social-proof | 3 | 2 | 0 | 3/2/5 |
| new | 0 | - | 0 | 0 | 0 | 3/3/4 |
| new | 1 | - | 0 | 0 | 0 | 2/3/4 |
| new | 2 | - | 0 | 0 | 0 | 5/3/4 |

</details>

### `whistleblower`

| path | n | detected | findings | top | compounds | cascade L2/L3/L4 |
|------|---|----------|----------|-----|-----------|-------------------|
| old | 3 | 2 | 2 | 1 | 0 | 3.67 / 2 / 3.67 |
| new | 3 | 1 | 1 | 1 | 0 | 4 / 1.33 / 5 |

<details><summary>per-run detail</summary>

| path | run | detected_ids | findings | top | compounds | L2/L3/L4 cascade |
|------|-----|--------------|----------|-----|-----------|-------------------|
| old | 0 | availability-misweighing, reward-and-punishment-superresponse | 2 | 1 | 0 | 4/2/4 |
| old | 1 | availability-misweighing, reward-and-punishment-superresponse | 2 | 1 | 0 | 2/2/4 |
| old | 2 | availability-misweighing, reward-and-punishment-superresponse | 2 | 1 | 0 | 5/2/3 |
| new | 0 | reward-and-punishment-superresponse | 1 | 1 | 0 | 5/1/5 |
| new | 1 | reward-and-punishment-superresponse | 1 | 1 | 0 | 4/1/5 |
| new | 2 | reward-and-punishment-superresponse | 1 | 1 | 0 | 3/2/5 |

</details>

