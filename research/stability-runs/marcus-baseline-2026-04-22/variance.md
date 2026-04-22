# Stability report — marcus-baseline

Generated: 2026-04-22T09:54:06Z
Runs: 4
Run IDs: 20260421T144534Z, 20260421T162225Z, 20260421T172513Z, 20260422T091837Z
Prompt versions consistent across runs: True

## Per-stage stability (Jaccard)

> 1.0 is a WARNING, not a target — signals a specialist that stopped doing semantic judgment. Acceptance is a threshold band: stability moved up from baseline, no neighboring stage regressed, qualitative review confirms cards still do structural work.

| Stage | Mean | Min | Max |
|---|---|---|---|
| Pass 1 (tendencies) | 0.50 | 0.00 | 1.00 |
| Lane 2 (anchors) | 0.06 | 0.00 | 0.33 |
| Lane 3 (reframings) | 0.17 | 0.00 | 0.33 |
| Lane 4 (gap dims) | 0.52 | 0.29 | 0.80 |

## Step 6 anchor naming (per-run)

| Run | Named | Total | Rate |
|---|---|---|---|
| `20260421T144534Z` | 0 | 1 | 0% |
| `20260421T162225Z` | 0 | 3 | 0% |
| `20260421T172513Z` | 2 | 2 | 100% |
| `20260422T091837Z` | 2 | 2 | 100% |
| **AGGREGATE** | **4** | **8** | **50%** |

## Per-run item diff

### Pass 1 tendencies
- `20260421T144534Z`: ['contrast-misreaction-tendency', 'liking-loving-tendency']
- `20260421T162225Z`: ['deprival-superreaction-tendency', 'inconsistency-avoidance-tendency']
- `20260421T172513Z`: ['deprival-superreaction-tendency', 'inconsistency-avoidance-tendency']
- `20260422T091837Z`: ['deprival-superreaction-tendency', 'inconsistency-avoidance-tendency']

### Lane 2 anchors
- `20260421T144534Z`: ['opportunity-cost']
- `20260421T162225Z`: ['endowment-effect', 'opportunity-cost', 'problem-framing-and-reframing']
- `20260421T172513Z`: ['inversion', 'premortem']
- `20260422T091837Z`: ['representativeness-heuristic', 'sunk-cost-fallacy']

### Lane 3 reframings
- `20260421T144534Z`: ['decision-trees', 'first-principles-thinking']
- `20260421T162225Z`: ['decision-trees', 'option-theory']
- `20260421T172513Z`: ['decision-trees', 'systems-thinking']
- `20260422T091837Z`: []

### Lane 4 gap dims
- `20260421T144534Z`: ['competitive-dynamics', 'information-quality', 'resource-allocation', 'risk-response', 'scope-boundary']
- `20260421T162225Z`: ['information-quality', 'resource-allocation', 'risk-response', 'stakeholder-alignment']
- `20260421T172513Z`: ['information-quality', 'resource-allocation', 'stakeholder-alignment', 'timing-sequencing']
- `20260422T091837Z`: ['existing-vs-new', 'information-quality', 'resource-allocation', 'risk-response', 'stakeholder-alignment']

## Cost per run (boundary-call tokens)

| Run | Calls | Prompt tok | Completion tok | Total tok |
|---|---|---|---|---|
| `20260421T144534Z` | 12 | 63031 | 6712 | 69743 |
| `20260421T162225Z` | 12 | 60907 | 5533 | 66440 |
| `20260421T172513Z` | 11 | 54766 | 6594 | 61360 |
| `20260422T091837Z` | 10 | 54940 | 5359 | 60299 |
