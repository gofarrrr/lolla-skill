# Core Semantic System-Level Coverage

Corpus: `core-semantic-corpus-v0`  
Cases: 12  
Gold observations: 102

| measure | family-aligned | system-level |
| --- | ---: | ---: |
| weighted exact-span recall | 0.552 | 0.716 |
| stable observations | 46 | 63 |

Cross-family rescue opportunities: 50

## Dimensions

| dimension | family-aligned | system-level | delta |
| --- | ---: | ---: | ---: |
| `assistant_positions_and_revisions` | 0.576 | 0.636 | 0.061 |
| `constraints_and_options` | 0.684 | 0.789 | 0.105 |
| `dropped_or_under_carried_threads` | 0.242 | 0.697 | 0.455 |
| `operative_question` | 0.682 | 0.773 | 0.091 |
| `uncertainty_and_evidence_boundaries` | 0.389 | 0.528 | 0.139 |
| `user_corrections_and_pressure` | 0.521 | 0.812 | 0.292 |

Family-aligned coverage diagnoses reader placement. System-level coverage asks whether the semantic packet preserved the source observation anywhere. Neither is a quality score.
