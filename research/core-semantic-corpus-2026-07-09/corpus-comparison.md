# Core Semantic Corpus Comparison

Corpus: `core-semantic-corpus-v0` (12 cases, three repeats per path)

## Corpus result

| measure | compact | shadow |
| --- | ---: | ---: |
| macro exact-span recall | 0.076 | 0.528 |
| weighted exact-span recall | 0.065 | 0.542 |
| stable observations | 6 / 102 | 49 / 102 |
| never recovered | 94 / 102 | 41 / 102 |
| macro span repeatability | 0.376 | 0.642 |
| macro labeled repeatability | 0.376 | 0.628 |
| lowest case recall | 0.000 | 0.208 |

Shadow wins recall on 12/12 cases, span repeatability on 11/12, and labeled repeatability on 11/12.

## Per case

| case | stratum | gold | compact recall | shadow recall | compact span J | shadow span J |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `case-01-enterprise-logo-beta` | `business_evidence_gate` | 15 | 0.000 | 0.778 | 0.460 | 0.865 |
| `case-02-multi-offer-career` | `career_multi_option` | 8 | 0.000 | 0.208 | 0.425 | 0.402 |
| `case-03-startup-pivot` | `business_pivot_evidence` | 8 | 0.125 | 0.583 | 0.547 | 0.601 |
| `case-04-whistleblower` | `ethical_institutional_risk` | 7 | 0.286 | 0.714 | 0.386 | 0.580 |
| `case-05-parenting-teen` | `family_safety` | 8 | 0.125 | 0.625 | 0.174 | 0.391 |
| `case-06-friendship-money` | `relationship_financial` | 8 | 0.000 | 0.500 | 0.316 | 0.451 |
| `case-07-messy-linked-decisions` | `multi_problem_dependency` | 8 | 0.083 | 0.708 | 0.597 | 0.646 |
| `case-08-oncologist-career-family` | `career_family_irreversibility` | 8 | 0.000 | 0.500 | 0.179 | 0.751 |
| `case-09-phd-dissertation` | `research_optionality` | 9 | 0.000 | 0.444 | 0.431 | 0.818 |
| `case-10-real-estate-bid` | `financial_deadline` | 8 | 0.125 | 0.500 | 0.209 | 0.667 |
| `case-11-user-has-consulting-plan` | `user_precommitted_plan` | 9 | 0.000 | 0.333 | 0.423 | 0.952 |
| `case-12-lolla-project-governance` | `short_governance_boundary` | 6 | 0.167 | 0.444 | 0.358 | 0.576 |

## Recovery by semantic dimension

| dimension | compact weighted recall | shadow weighted recall | compact stable | shadow stable | gold |
| --- | ---: | ---: | ---: | ---: | ---: |
| `assistant_positions_and_revisions` | 0.303 | 0.545 | 6 | 12 | 22 |
| `constraints_and_options` | 0.000 | 0.614 | 0 | 11 | 19 |
| `dropped_or_under_carried_threads` | 0.000 | 0.273 | 0 | 2 | 11 |
| `operative_question` | 0.000 | 0.697 | 0 | 13 | 22 |
| `uncertainty_and_evidence_boundaries` | 0.000 | 0.472 | 0 | 4 | 12 |
| `user_corrections_and_pressure` | 0.000 | 0.479 | 0 | 7 | 16 |

## Operational readout

- compact: 36 successful artifacts; usage tracked for 33; 52 recorded calls and 261801 tokens.
- shadow: 36 successful artifacts; usage tracked for 36; 144 recorded calls and 631439 tokens.
- Preserved failed attempts: 1.

## Limits

- gold annotations are provisional source-first research judgments
- exact-span recall does not credit ungrounded paraphrases
- three repeats are an initial stability signal, not production reliability proof
- token totals are a cost proxy; provider billing amounts are not persisted
- the short governance case has only one user and one assistant turn
