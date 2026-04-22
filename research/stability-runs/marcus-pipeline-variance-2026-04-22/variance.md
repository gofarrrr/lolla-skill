# Stability report — marcus-pipeline-variance

Generated: 2026-04-22T09:54:46Z
Runs: 3
Run IDs: 20260422T095446Zstab0, 20260422T095605Zstab1, 20260422T095719Zstab2
Prompt versions consistent across runs: True

## Per-stage stability (Jaccard)

> 1.0 is a WARNING, not a target — signals a specialist that stopped doing semantic judgment. Acceptance is a threshold band: stability moved up from baseline, no neighboring stage regressed, qualitative review confirms cards still do structural work.

| Stage | Mean | Min | Max |
|---|---|---|---|
| Pass 1 (tendencies) | 1.00 | 1.00 | 1.00 |
| Lane 2 (anchors) | 0.11 | 0.00 | 0.33 |
| Lane 3 (reframings) | 0.33 | 0.00 | 1.00 |
| Lane 4 (gap dims) | 0.73 | 0.60 | 1.00 |

## Step 6 anchor naming (per-run)

| Run | Named | Total | Rate |
|---|---|---|---|
| `20260422T095446Zstab0` | (no revised_answer) | — | — |
| `20260422T095605Zstab1` | (no revised_answer) | — | — |
| `20260422T095719Zstab2` | (no revised_answer) | — | — |

## Per-run item diff

### Pass 1 tendencies
- `20260422T095446Zstab0`: ['deprival-superreaction-tendency', 'inconsistency-avoidance-tendency']
- `20260422T095605Zstab1`: ['deprival-superreaction-tendency', 'inconsistency-avoidance-tendency']
- `20260422T095719Zstab2`: ['deprival-superreaction-tendency', 'inconsistency-avoidance-tendency']

### Lane 2 anchors
- `20260422T095446Zstab0`: ['endowment-effect', 'inversion', 'opportunity-cost']
- `20260422T095605Zstab1`: ['endowment-effect', 'inversion', 'optionality', 'principal-agent-problem', 'representativeness-heuristic']
- `20260422T095719Zstab2`: ['information-asymmetry', 'sunk-cost-fallacy']

### Lane 3 reframings
- `20260422T095446Zstab0`: ['problem-framing-and-reframing', 'systems-thinking']
- `20260422T095605Zstab1`: ['problem-framing-and-reframing', 'systems-thinking']
- `20260422T095719Zstab2`: []

### Lane 4 gap dims
- `20260422T095446Zstab0`: ['existing-vs-new', 'resource-allocation', 'risk-response', 'stakeholder-alignment']
- `20260422T095605Zstab1`: ['information-quality', 'resource-allocation', 'risk-response', 'stakeholder-alignment']
- `20260422T095719Zstab2`: ['existing-vs-new', 'resource-allocation', 'risk-response', 'stakeholder-alignment']

## Cost per run (boundary-call tokens)

| Run | Calls | Prompt tok | Completion tok | Total tok |
|---|---|---|---|---|
| `20260422T095446Zstab0` | 11 | 56025 | 5064 | 61089 |
| `20260422T095605Zstab1` | 11 | 55329 | 4998 | 60327 |
| `20260422T095719Zstab2` | 10 | 54594 | 5965 | 60559 |
