# Core Semantic System-Level Coverage

Corpus: `core-semantic-corpus-v0`  
Cases: 3  
Gold observations: 25

| measure | family-aligned | system-level |
| --- | ---: | ---: |
| weighted exact-span recall | 0.547 | 0.760 |
| stable observations | 13 | 19 |

Cross-family rescue opportunities: 16

## Dimensions

| dimension | family-aligned | system-level | delta |
| --- | ---: | ---: | ---: |
| `assistant_positions_and_revisions` | 0.600 | 0.600 | 0.000 |
| `constraints_and_options` | 0.800 | 0.800 | 0.000 |
| `dropped_or_under_carried_threads` | 0.000 | 0.667 | 0.667 |
| `operative_question` | 0.889 | 1.000 | 0.111 |
| `uncertainty_and_evidence_boundaries` | 0.333 | 0.333 | 0.000 |
| `user_corrections_and_pressure` | 0.111 | 1.000 | 0.889 |

Family-aligned coverage diagnoses reader placement. System-level coverage asks whether the semantic packet preserved the source observation anywhere. Neither is a quality score.
