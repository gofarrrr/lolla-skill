# Core Semantic Corpus Comparison

Corpus: `core-semantic-corpus-v0-diagnostic-subset` (3 cases, three repeats per path)

## Corpus result

| measure | compact | shadow |
| --- | ---: | ---: |
| macro exact-span recall | 0.000 | 0.546 |
| weighted exact-span recall | 0.000 | 0.547 |
| stable observations | 0 / 25 | 13 / 25 |
| never recovered | 25 / 25 | 10 / 25 |
| macro span repeatability | 0.343 | 0.628 |
| macro labeled repeatability | 0.343 | 0.577 |
| lowest case recall | 0.000 | 0.500 |

Shadow wins recall on 3/3 cases, span repeatability on 3/3, and labeled repeatability on 2/3.

## Per case

| case | stratum | gold | compact recall | shadow recall | compact span J | shadow span J |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `case-02-multi-offer-career` | `career_multi_option` | 8 | 0.000 | 0.583 | 0.425 | 0.453 |
| `case-08-oncologist-career-family` | `career_family_irreversibility` | 8 | 0.000 | 0.500 | 0.179 | 0.693 |
| `case-11-user-has-consulting-plan` | `user_precommitted_plan` | 9 | 0.000 | 0.556 | 0.423 | 0.738 |

## Recovery by semantic dimension

| dimension | compact weighted recall | shadow weighted recall | compact stable | shadow stable | gold |
| --- | ---: | ---: | ---: | ---: | ---: |
| `assistant_positions_and_revisions` | 0.000 | 0.600 | 0 | 3 | 5 |
| `constraints_and_options` | 0.000 | 0.800 | 0 | 4 | 5 |
| `dropped_or_under_carried_threads` | 0.000 | 0.000 | 0 | 0 | 3 |
| `operative_question` | 0.000 | 0.889 | 0 | 5 | 6 |
| `uncertainty_and_evidence_boundaries` | 0.000 | 0.333 | 0 | 1 | 3 |
| `user_corrections_and_pressure` | 0.000 | 0.111 | 0 | 0 | 3 |

## Operational readout

- compact: 9 successful artifacts; usage tracked for 9; 15 recorded calls and 83531 tokens.
- shadow: 9 successful artifacts; usage tracked for 9; 45 recorded calls and 218992 tokens.
- Preserved failed attempts: 1.

## Limits

- gold annotations are provisional source-first research judgments
- exact-span recall does not credit ungrounded paraphrases
- three repeats are an initial stability signal, not production reliability proof
- token totals are a cost proxy; provider billing amounts are not persisted
- the short governance case has only one user and one assistant turn
