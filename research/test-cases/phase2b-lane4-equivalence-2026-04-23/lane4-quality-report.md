# Phase 2b Lane 4 quality check — 2026-04-23

**Mode: DRY RUN** — N=1 on a subset of cases. Not an acceptance-gate run.

Measurement: 1 case(s) × 2 paths × N=1 runs. Wall time: 127.8s.

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
| old | 1 | 0 | 8 | 4 | 4 | 8 |
| new | 1 | 0 | 8 | 4 | 4 | 12 |

**question_type distribution (old):** {'decision-evaluation': 1}

**question_type distribution (new):** {'decision-evaluation': 1}

**Aggregate regression summary:** zero regressions flagged across all cases.

## Per-case detail

### `oncologist`

| path | n | qtype(s) | dims total | covered | gaps | gap_qs total |
|------|---|----------|------------|---------|------|--------------|
| old | 1 | decision-evaluation:1 | 8 | 4 | 4 | 8 |
| new | 1 | decision-evaluation:1 | 8 | 4 | 4 | 12 |

<details><summary>per-run detail</summary>

| path | run | qtype | dims | covered | gaps | gap_dim_ids | gap_qs |
|------|-----|-------|------|---------|------|-------------|--------|
| old | 0 | decision-evaluation | 8 | 4 | 4 | incentive-alignment, information-quality, resource-allocation, risk-response | 8 |
| new | 0 | decision-evaluation | 8 | 4 | 4 | information-quality, resource-allocation, risk-response, scope-boundary | 12 |

</details>

