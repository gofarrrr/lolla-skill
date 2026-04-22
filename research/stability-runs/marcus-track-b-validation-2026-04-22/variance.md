# Stability report — marcus-track-b-validation

Generated: 2026-04-22T11:15:10Z
Runs: 3
Run IDs: 20260422T111510Zstab0, 20260422T111639Zstab1, 20260422T111800Zstab2
Prompt versions consistent across runs: True

## Per-stage stability (Jaccard)

> 1.0 is a WARNING, not a target — signals a specialist that stopped doing semantic judgment. Acceptance is a threshold band: stability moved up from baseline, no neighboring stage regressed, qualitative review confirms cards still do structural work.

| Stage | Mean | Min | Max |
|---|---|---|---|
| Pass 1 (tendencies) | 0.70 | 0.60 | 0.75 |
| Lane 2 (anchors) | 0.47 | 0.40 | 0.50 |
| Lane 3 (reframings) | 0.11 | 0.00 | 0.33 |
| Lane 4 (gap dims) | 0.63 | 0.50 | 0.80 |

## Step 6 anchor naming (per-run)

| Run | Named | Total | Rate |
|---|---|---|---|
| `20260422T111510Zstab0` | (no revised_answer) | — | — |
| `20260422T111639Zstab1` | (no revised_answer) | — | — |
| `20260422T111800Zstab2` | (no revised_answer) | — | — |

## Per-run item diff

### Pass 1 tendencies
- `20260422T111510Zstab0`: ['availability-misweighing-tendency', 'contrast-misreaction-tendency', 'inconsistency-avoidance-tendency']
- `20260422T111639Zstab1`: ['availability-misweighing-tendency', 'contrast-misreaction-tendency', 'inconsistency-avoidance-tendency', 'reward-and-punishment-superresponse-tendency']
- `20260422T111800Zstab2`: ['availability-misweighing-tendency', 'contrast-misreaction-tendency', 'deprival-superreaction-tendency', 'inconsistency-avoidance-tendency']

### Lane 2 anchors
- `20260422T111510Zstab0`: ['empathy', 'inversion', 'opportunity-cost', 'power-dynamics', 'specialization']
- `20260422T111639Zstab1`: ['endowment-effect', 'inversion', 'opportunity-cost', 'power-dynamics']
- `20260422T111800Zstab2`: ['inversion', 'opportunity-cost']

### Lane 3 reframings
- `20260422T111510Zstab0`: ['decision-trees', 'first-principles-thinking']
- `20260422T111639Zstab1`: ['first-principles-thinking', 'problem-framing-and-reframing']
- `20260422T111800Zstab2`: []

### Lane 4 gap dims
- `20260422T111510Zstab0`: ['existing-vs-new', 'resource-allocation', 'risk-response', 'stakeholder-alignment']
- `20260422T111639Zstab1`: ['existing-vs-new', 'information-quality', 'resource-allocation', 'stakeholder-alignment']
- `20260422T111800Zstab2`: ['existing-vs-new', 'resource-allocation', 'risk-response', 'scope-boundary', 'stakeholder-alignment']

## Cost per run (boundary-call tokens)

| Run | Calls | Prompt tok | Completion tok | Total tok |
|---|---|---|---|---|
| `20260422T111510Zstab0` | 18 | 93949 | 7031 | 100980 |
| `20260422T111639Zstab1` | 19 | 100238 | 7222 | 107460 |
| `20260422T111800Zstab2` | 18 | 99003 | 6878 | 105881 |
