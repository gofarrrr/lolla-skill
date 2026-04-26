# Lane 2 Path D — proxy validation report

Generated: 2026-04-26T15:15:39Z
Rows: 76 anchor-instances across 8 case-mode groups, 22 runs, 30 unique models.

Label balance (stable_anchor): 39/76 = 51.3%
Label balance (stable_accepted): 41/76 = 53.9%

## D0 verdicts

| Proxy | Verdict | Pooled AUROC | Coverage | Pos rate | Direction OK | Marcus collapse | Reason |
|---|---|---|---|---|---|---|---|
| `is_broad_overlay` | **NO_SIGNAL** | 0.4751 | 1.0 | 0.0526 | 1/8 | no | AUROC 0.48 below directional threshold (0.55) |
| `final_rank` | **WORDING_ONLY_EVIDENCE** | 0.6674 | 1.0 | — | 1/8 | YES | AUROC 0.67 (gate 0.70); direction 1/8; threshold best precision/recall 0.00/0.00; Marcus collapse: True |
| `evidence_quote_length` | **NO_SIGNAL** | 0.492 | 1.0 | — | 2/8 | no | AUROC 0.49 below directional threshold (0.55) |
| `quote_collision_count` | **NO_SIGNAL** | 0.5007 | 1.0 | — | 0/8 | no | AUROC 0.50 below directional threshold (0.55) |
| `accepted_before_cap_position` | **WORDING_ONLY_EVIDENCE** | 0.666 | 1.0 | — | 1/8 | YES | AUROC 0.67 (gate 0.70); direction 1/8; threshold best precision/recall 0.00/0.00; Marcus collapse: True |
| `recall_source` | **NO_SIGNAL** | — | 1.0 | — | — | — |  |

## Per-case AUROC (conversation-independence diagnostic)

A proxy with similar AUROCs across all case-modes is conversation-independent. Wide swings = case-coupled.

| Proxy | marcus-equity/off | marcus-equity/on | mid-level-consultant-decides/off | mid-level-consultant-decides/on | mother-deciding-address-year/off | mother-deciding-address-year/on | third-year-phd-student/off | third-year-phd-student/on |
|---|---|---|---|---|---|---|---|---|
| `is_broad_overlay` | 0.50 | 0.50 | 0.50 | 0.50 | 0.00 | 0.60 | 0.50 | 0.50 |
| `final_rank` | 0.62 | 0.08 | 0.47 | 0.38 | 0.21 | 0.20 | 0.18 | 0.15 |
| `evidence_quote_length` | 1.00 | 1.00 | 0.50 | 0.17 | 0.12 | 0.30 | 0.32 | 0.25 |
| `quote_collision_count` | 0.50 | 0.50 | 0.50 | 0.50 | 0.50 | 0.50 | 0.47 | 0.50 |
| `accepted_before_cap_position` | 0.46 | 0.58 | 0.15 | 0.33 | 0.00 | 0.20 | 0.41 | 0.33 |
| `recall_source` | — | — | — | — | — | — | — | — |

## Threshold rules per proxy

### `is_broad_overlay`

| Threshold | Direction | Precision | Recall |
|---|---|---|---|
| 0.5 | `ge` | 0.25 | 0.03 |

### `final_rank`

| Threshold | Direction | Precision | Recall |
|---|---|---|---|
| 10 | `le` | 0.75 | 0.38 |
| 20 | `le` | 0.65 | 0.72 |
| 30 | `le` | 0.61 | 0.79 |

### `evidence_quote_length`

| Threshold | Direction | Precision | Recall |
|---|---|---|---|
| 40 | `ge` | 0.51 | 1.00 |
| 80 | `ge` | 0.53 | 1.00 |
| 120 | `ge` | 0.49 | 0.82 |

### `quote_collision_count`

| Threshold | Direction | Precision | Recall |
|---|---|---|---|
| 0 | `le` | 0.51 | 0.97 |
| 1 | `le` | 0.51 | 1.00 |

### `accepted_before_cap_position`

| Threshold | Direction | Precision | Recall |
|---|---|---|---|
| 2 | `le` | 0.65 | 0.67 |
| 3 | `le` | 0.57 | 0.82 |
| 5 | `le` | 0.54 | 0.97 |

## Path D D1 routing decision

**No proxy clears D0 gates.** Wording-only Step 6 changes supported by directional evidence from: ['final_rank', 'accepted_before_cap_position'].

## Methodology

- Inputs: 8 baseline campaigns under `research/stability-runs/*-lane2-{on,off}-2026-04-26/`. Per-run details from `/tmp/lolla_*_result.json` (still present at audit time).
- Stable label threshold: appeared in ≥2 of 3 runs per case-mode.
- `is_broad_overlay` source: `engine.system_b.companion_routing._BROAD_OVERLAY_MODELS` (6 models) plus optional `model_payload.is_broad_overlay` flag (forward-compat).
- AUROC: Wilcoxon-Mann-Whitney with tie correction.
- Marcus stress: per-case Marcus AUROC must be within 0.15 of pooled AUROC, else verdict carries explicit caveat.
- No LLM calls.