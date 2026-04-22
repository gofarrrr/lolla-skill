# Stability report — marcus-c-step1-3-validation

Generated: 2026-04-22T10:37:57Z
Runs: 3
Run IDs: 20260422T103757Zstab0, 20260422T103917Zstab1, 20260422T104033Zstab2
Prompt versions consistent across runs: True

## Per-stage stability (Jaccard)

> 1.0 is a WARNING, not a target — signals a specialist that stopped doing semantic judgment. Acceptance is a threshold band: stability moved up from baseline, no neighboring stage regressed, qualitative review confirms cards still do structural work.

| Stage | Mean | Min | Max |
|---|---|---|---|
| Pass 1 (tendencies) | 0.50 | 0.25 | 1.00 |
| Lane 2 (anchors) | 0.12 | 0.00 | 0.20 |
| Lane 3 (reframings) | 0.00 | 0.00 | 0.00 |
| Lane 4 (gap dims) | 0.60 | 0.40 | 0.80 |

## Step 6 anchor naming (per-run)

| Run | Named | Total | Rate |
|---|---|---|---|
| `20260422T103757Zstab0` | (no revised_answer) | — | — |
| `20260422T103917Zstab1` | (no revised_answer) | — | — |
| `20260422T104033Zstab2` | (no revised_answer) | — | — |

## Per-run item diff

### Pass 1 tendencies
- `20260422T103757Zstab0`: ['inconsistency-avoidance-tendency']
- `20260422T103917Zstab1`: ['contrast-misreaction-tendency', 'deprival-superreaction-tendency', 'inconsistency-avoidance-tendency', 'reward-and-punishment-superresponse-tendency']
- `20260422T104033Zstab2`: ['inconsistency-avoidance-tendency']

### Lane 2 anchors
- `20260422T103757Zstab0`: ['boundaries', 'inversion', 'signaling', 'sunk-cost-fallacy']
- `20260422T103917Zstab1`: ['endowment-effect', 'opportunity-cost', 'sunk-cost-fallacy']
- `20260422T104033Zstab2`: ['endowment-effect', 'game-theory-payoffs', 'optionality']

### Lane 3 reframings
- `20260422T103757Zstab0`: ['counterfactual-reasoning', 'first-principles-thinking']
- `20260422T103917Zstab1`: []
- `20260422T104033Zstab2`: ['decision-trees', 'trade-offs']

### Lane 4 gap dims
- `20260422T103757Zstab0`: ['information-quality', 'resource-allocation', 'stakeholder-alignment']
- `20260422T103917Zstab1`: ['existing-vs-new', 'resource-allocation', 'risk-response', 'stakeholder-alignment']
- `20260422T104033Zstab2`: ['existing-vs-new', 'information-quality', 'resource-allocation', 'risk-response', 'stakeholder-alignment']

## Cost per run (boundary-call tokens)

| Run | Calls | Prompt tok | Completion tok | Total tok |
|---|---|---|---|---|
| `20260422T103757Zstab0` | 10 | 48068 | 5681 | 53749 |
| `20260422T103917Zstab1` | 12 | 63753 | 5824 | 69577 |
| `20260422T104033Zstab2` | 10 | 48294 | 5326 | 53620 |
