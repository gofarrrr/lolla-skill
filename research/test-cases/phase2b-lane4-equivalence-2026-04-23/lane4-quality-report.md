# Phase 2b Lane 4 quality check — 2026-04-23

Measurement: 10 case(s) × 2 paths × N=3 runs. Wall time: 2020.7s.

**Metrics definitions:**
- `qtype`: `structural_coverage_card.question_type` (4-class, per run)
- `dims total`: total dimensions detected per run (covered + gaps)
- `covered`: dimensions marked covered (the answer addressed them)
- `gaps`: dimensions marked uncovered (potentially material gaps)
- `gap_qs total`: sum of discovery questions generated across all gaps

**Note on Lane 4 signal shape:** Lane 4 has no evidence-substring validation, so there is no drop-rate metric (unlike Phase 2a's Lane 3 measurement). Quality evidence for this migration comes from per-case behavior comparison + qualitative read of whether gap_questions reference the user's actual situation particulars.

## Aggregate across all cases

| path | total runs | errored | dims (mean) | covered (mean) | gaps (mean) | gap_qs (mean) |
|------|-----------|---------|-------------|----------------|-------------|---------------|
| old | 30 | 0 | 8.77 | 4.8 | 3.97 | 10.3 |
| new | 29 | 1 | 8.45 | 4.24 | 4.21 | 11.83 |

**question_type distribution (old):** {'decision-evaluation': 27, 'action-planning': 3}

**question_type distribution (new):** {'action-planning': 9, 'decision-evaluation': 20}

**Aggregate regression summary:** zero regressions flagged across all cases.

## Per-case detail

### `friendship_money`

| path | n | qtype(s) | dims total | covered | gaps | gap_qs total |
|------|---|----------|------------|---------|------|--------------|
| old | 3 | decision-evaluation:3 | 7.67 | 4.67 | 3 | 7 |
| new | 3 | action-planning:3 | 7.67 | 3.33 | 4.33 | 13 |

<details><summary>per-run detail</summary>

| path | run | qtype | dims | covered | gaps | gap_dim_ids | gap_qs |
|------|-----|-------|------|---------|------|-------------|--------|
| old | 0 | decision-evaluation | 8 | 5 | 3 | information-quality, risk-response, stakeholder-alignment | 6 |
| old | 1 | decision-evaluation | 7 | 4 | 3 | information-quality, risk-response, stakeholder-alignment | 6 |
| old | 2 | decision-evaluation | 8 | 5 | 3 | incentive-alignment, resource-allocation, stakeholder-alignment | 9 |
| new | 0 | action-planning | 7 | 2 | 5 | commitment-reversibility, incentive-alignment, risk-response, stakeholder-alignment… | 15 |
| new | 1 | action-planning | 8 | 4 | 4 | commitment-reversibility, incentive-alignment, risk-response, stakeholder-alignment | 12 |
| new | 2 | action-planning | 8 | 4 | 4 | commitment-reversibility, risk-response, stakeholder-alignment, timing-sequencing | 12 |

</details>

### `messy_three_problems`

| path | n | qtype(s) | dims total | covered | gaps | gap_qs total |
|------|---|----------|------------|---------|------|--------------|
| old | 3 | decision-evaluation:3 | 8.33 | 4 | 4.33 | 9.67 |
| new | 3 | decision-evaluation:3 | 9 | 4 | 5 | 13.33 |

<details><summary>per-run detail</summary>

| path | run | qtype | dims | covered | gaps | gap_dim_ids | gap_qs |
|------|-----|-------|------|---------|------|-------------|--------|
| old | 0 | decision-evaluation | 8 | 4 | 4 | commitment-reversibility, incentive-alignment, resource-allocation, stakeholder-alignment | 9 |
| old | 1 | decision-evaluation | 8 | 3 | 5 | information-quality, resource-allocation, risk-response, stakeholder-alignment… | 8 |
| old | 2 | decision-evaluation | 9 | 5 | 4 | commitment-reversibility, incentive-alignment, resource-allocation, stakeholder-alignment | 12 |
| new | 0 | decision-evaluation | 10 | 5 | 5 | competitive-dynamics, incentive-alignment, information-quality, risk-response… | 10 |
| new | 1 | decision-evaluation | 9 | 4 | 5 | competitive-dynamics, incentive-alignment, risk-response, stakeholder-alignment… | 15 |
| new | 2 | decision-evaluation | 8 | 3 | 5 | competitive-dynamics, incentive-alignment, resource-allocation, stakeholder-alignment… | 15 |

</details>

### `multi_offer`

| path | n | qtype(s) | dims total | covered | gaps | gap_qs total |
|------|---|----------|------------|---------|------|--------------|
| old | 3 | decision-evaluation:3 | 8.67 | 3.67 | 5 | 15 |
| new | 3 | decision-evaluation:3 | 9 | 5 | 4 | 12 |

<details><summary>per-run detail</summary>

| path | run | qtype | dims | covered | gaps | gap_dim_ids | gap_qs |
|------|-----|-------|------|---------|------|-------------|--------|
| old | 0 | decision-evaluation | 8 | 3 | 5 | information-quality, resource-allocation, risk-response, timing-sequencing… | 15 |
| old | 1 | decision-evaluation | 8 | 3 | 5 | information-quality, resource-allocation, risk-response, timing-sequencing… | 15 |
| old | 2 | decision-evaluation | 10 | 5 | 5 | competitive-dynamics, information-quality, resource-allocation, risk-response… | 15 |
| new | 0 | decision-evaluation | 9 | 5 | 4 | competitive-dynamics, information-quality, resource-allocation, uncertainty-type | 12 |
| new | 1 | decision-evaluation | 9 | 5 | 4 | competitive-dynamics, information-quality, resource-allocation, uncertainty-type | 12 |
| new | 2 | decision-evaluation | 9 | 5 | 4 | competitive-dynamics, information-quality, resource-allocation, uncertainty-type | 12 |

</details>

### `oncologist`

| path | n | qtype(s) | dims total | covered | gaps | gap_qs total |
|------|---|----------|------------|---------|------|--------------|
| old | 3 | decision-evaluation:3 | 8 | 4 | 4 | 10.67 |
| new | 3 | decision-evaluation:3 | 8 | 3.67 | 4.33 | 13 |

<details><summary>per-run detail</summary>

| path | run | qtype | dims | covered | gaps | gap_dim_ids | gap_qs |
|------|-----|-------|------|---------|------|-------------|--------|
| old | 0 | decision-evaluation | 8 | 4 | 4 | incentive-alignment, information-quality, resource-allocation, risk-response | 8 |
| old | 1 | decision-evaluation | 8 | 4 | 4 | incentive-alignment, information-quality, resource-allocation, risk-response | 12 |
| old | 2 | decision-evaluation | 8 | 4 | 4 | incentive-alignment, information-quality, resource-allocation, risk-response | 12 |
| new | 0 | decision-evaluation | 8 | 3 | 5 | competitive-dynamics, incentive-alignment, resource-allocation, risk-response… | 15 |
| new | 1 | decision-evaluation | 8 | 4 | 4 | incentive-alignment, resource-allocation, risk-response, uncertainty-type | 12 |
| new | 2 | decision-evaluation | 8 | 4 | 4 | competitive-dynamics, incentive-alignment, resource-allocation, risk-response | 12 |

</details>

### `parenting_teen`

| path | n | qtype(s) | dims total | covered | gaps | gap_qs total |
|------|---|----------|------------|---------|------|--------------|
| old | 3 | action-planning:3 | 8.33 | 5 | 3.33 | 10 |
| new | 3 | action-planning:3 | 8.33 | 4.33 | 4 | 12 |

<details><summary>per-run detail</summary>

| path | run | qtype | dims | covered | gaps | gap_dim_ids | gap_qs |
|------|-----|-------|------|---------|------|-------------|--------|
| old | 0 | action-planning | 8 | 5 | 3 | causal-diagnosis, feedback-system-dynamics, risk-response | 9 |
| old | 1 | action-planning | 8 | 5 | 3 | causal-diagnosis, feedback-system-dynamics, risk-response | 9 |
| old | 2 | action-planning | 9 | 5 | 4 | causal-diagnosis, feedback-system-dynamics, resource-allocation, risk-response | 12 |
| new | 0 | action-planning | 8 | 4 | 4 | commitment-reversibility, competitive-dynamics, incentive-alignment, uncertainty-type | 12 |
| new | 1 | action-planning | 9 | 5 | 4 | commitment-reversibility, competitive-dynamics, incentive-alignment, uncertainty-type | 12 |
| new | 2 | action-planning | 8 | 4 | 4 | commitment-reversibility, competitive-dynamics, incentive-alignment, uncertainty-type | 12 |

</details>

### `phd_research`

| path | n | qtype(s) | dims total | covered | gaps | gap_qs total |
|------|---|----------|------------|---------|------|--------------|
| old | 3 | decision-evaluation:3 | 10.33 | 6.67 | 3.67 | 11 |
| new | 3 | decision-evaluation:3 | 9 | 5 | 4 | 10.67 |

<details><summary>per-run detail</summary>

| path | run | qtype | dims | covered | gaps | gap_dim_ids | gap_qs |
|------|-----|-------|------|---------|------|-------------|--------|
| old | 0 | decision-evaluation | 10 | 6 | 4 | information-quality, resource-allocation, risk-response, uncertainty-type | 12 |
| old | 1 | decision-evaluation | 10 | 7 | 3 | information-quality, resource-allocation, scope-boundary | 9 |
| old | 2 | decision-evaluation | 11 | 7 | 4 | information-quality, resource-allocation, scaling-dynamics, uncertainty-type | 12 |
| new | 0 | decision-evaluation | 9 | 5 | 4 | competitive-dynamics, incentive-alignment, resource-allocation, uncertainty-type | 12 |
| new | 1 | decision-evaluation | 9 | 5 | 4 | competitive-dynamics, incentive-alignment, information-quality, uncertainty-type | 12 |
| new | 2 | decision-evaluation | 9 | 5 | 4 | competitive-dynamics, incentive-alignment, resource-allocation, uncertainty-type | 8 |

</details>

### `real_estate`

| path | n | qtype(s) | dims total | covered | gaps | gap_qs total |
|------|---|----------|------------|---------|------|--------------|
| old | 3 | decision-evaluation:3 | 8.67 | 4 | 4.67 | 8 |
| new | 3 | decision-evaluation:3 | 8 | 4 | 4 | 13.33 |

<details><summary>per-run detail</summary>

| path | run | qtype | dims | covered | gaps | gap_dim_ids | gap_qs |
|------|-----|-------|------|---------|------|-------------|--------|
| old | 0 | decision-evaluation | 9 | 4 | 5 | competitive-dynamics, incentive-alignment, information-quality, stakeholder-alignment… | 12 |
| old | 1 | decision-evaluation | 8 | 3 | 5 | competitive-dynamics, information-quality, stakeholder-alignment, timing-sequencing… | 0 |
| old | 2 | decision-evaluation | 9 | 5 | 4 | commitment-reversibility, information-quality, resource-allocation, risk-response | 12 |
| new | 0 | decision-evaluation | 8 | 4 | 4 | commitment-reversibility, resource-allocation, risk-response, timing-sequencing | 12 |
| new | 1 | decision-evaluation | 8 | 4 | 4 | commitment-reversibility, risk-response, timing-sequencing, uncertainty-type | 16 |
| new | 2 | decision-evaluation | 8 | 4 | 4 | commitment-reversibility, competitive-dynamics, resource-allocation, uncertainty-type | 12 |

</details>

### `startup_pivot`

| path | n | qtype(s) | dims total | covered | gaps | gap_qs total |
|------|---|----------|------------|---------|------|--------------|
| old | 3 | decision-evaluation:3 | 10 | 7 | 3 | 9 |
| new | 2 | decision-evaluation:2 | 9 | 5 | 4 | 9.5 |

<details><summary>per-run detail</summary>

| path | run | qtype | dims | covered | gaps | gap_dim_ids | gap_qs |
|------|-----|-------|------|---------|------|-------------|--------|
| old | 0 | decision-evaluation | 10 | 7 | 3 | competitive-dynamics, resource-allocation, uncertainty-type | 9 |
| old | 1 | decision-evaluation | 10 | 7 | 3 | competitive-dynamics, resource-allocation, uncertainty-type | 9 |
| old | 2 | decision-evaluation | 10 | 7 | 3 | competitive-dynamics, resource-allocation, uncertainty-type | 9 |
| new | 0 | decision-evaluation | 9 | 5 | 4 | commitment-reversibility, information-quality, resource-allocation, stakeholder-alignment | 12 |
| new | 1 | ERR | - | - | - | - | - |
| new | 2 | decision-evaluation | 9 | 5 | 4 | commitment-reversibility, information-quality, resource-allocation, stakeholder-alignment | 7 |

</details>

### `user_has_plan`

| path | n | qtype(s) | dims total | covered | gaps | gap_qs total |
|------|---|----------|------------|---------|------|--------------|
| old | 3 | decision-evaluation:3 | 8.67 | 4.67 | 4 | 12 |
| new | 3 | action-planning:3 | 8 | 3.67 | 4.33 | 8.67 |

<details><summary>per-run detail</summary>

| path | run | qtype | dims | covered | gaps | gap_dim_ids | gap_qs |
|------|-----|-------|------|---------|------|-------------|--------|
| old | 0 | decision-evaluation | 8 | 4 | 4 | incentive-alignment, resource-allocation, risk-response, uncertainty-type | 12 |
| old | 1 | decision-evaluation | 9 | 5 | 4 | competitive-dynamics, information-quality, resource-allocation, uncertainty-type | 12 |
| old | 2 | decision-evaluation | 9 | 5 | 4 | incentive-alignment, information-quality, resource-allocation, risk-response | 12 |
| new | 0 | action-planning | 8 | 4 | 4 | behavioral-intervention, resource-allocation, risk-response, uncertainty-type | 8 |
| new | 1 | action-planning | 8 | 4 | 4 | incentive-alignment, resource-allocation, risk-response, uncertainty-type | 8 |
| new | 2 | action-planning | 8 | 3 | 5 | behavioral-intervention, incentive-alignment, resource-allocation, risk-response… | 10 |

</details>

### `whistleblower`

| path | n | qtype(s) | dims total | covered | gaps | gap_qs total |
|------|---|----------|------------|---------|------|--------------|
| old | 3 | decision-evaluation:3 | 9 | 4.33 | 4.67 | 10.67 |
| new | 3 | decision-evaluation:3 | 8.67 | 4.67 | 4 | 12 |

<details><summary>per-run detail</summary>

| path | run | qtype | dims | covered | gaps | gap_dim_ids | gap_qs |
|------|-----|-------|------|---------|------|-------------|--------|
| old | 0 | decision-evaluation | 9 | 4 | 5 | competitive-dynamics, information-quality, resource-allocation, stakeholder-alignment… | 10 |
| old | 1 | decision-evaluation | 9 | 4 | 5 | competitive-dynamics, information-quality, resource-allocation, stakeholder-alignment… | 10 |
| old | 2 | decision-evaluation | 9 | 5 | 4 | commitment-reversibility, incentive-alignment, risk-response, stakeholder-alignment | 12 |
| new | 0 | decision-evaluation | 8 | 4 | 4 | commitment-reversibility, competitive-dynamics, risk-response, stakeholder-alignment | 12 |
| new | 1 | decision-evaluation | 9 | 5 | 4 | commitment-reversibility, resource-allocation, risk-response, stakeholder-alignment | 12 |
| new | 2 | decision-evaluation | 9 | 5 | 4 | commitment-reversibility, competitive-dynamics, incentive-alignment, stakeholder-alignment | 12 |

</details>


## Errored runs (1 of 60)

| case | path | run | error |
|------|------|-----|-------|
| `startup_pivot` | new | 1 | `run_pipeline.py exit=1 on case_startup_pivot_conversation.txt (new-path). stdout: '{"status": "error", "error": "Pipeline execution failed: [Errno 54]` |
