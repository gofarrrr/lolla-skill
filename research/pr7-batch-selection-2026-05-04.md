# PR 7 Batch Selection - 2026-05-04

**Status:** Step 1 selection proposal. Extraction has not started.
**Branch:** `feature/knowledge-substrate-pr7-batch-extraction-trial`
**Target:** `feature/knowledge-substrate-pr6-activation-gating`
**Canonical corpus:** `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216`
**Observed canonical source files:** 222 markdown files.
**Protocol source:** PR 7 Batch Extraction Feasibility Trial brief.

## Selection Doctrine

This PR tests whether the affordance extraction instrument scales beyond the curated 10-model pilot. The 20 models below are selected as a heterogeneous feasibility batch, not as a knowledge-base coverage claim and not as a user-facing runtime surface.

Primary rails:

- 20 unique model ids, excluding the pilot 10.
- Four primary strata with five models each.
- Source availability checked against the canonical corpus before extraction.
- No extraction begins until Marcin signs off on the list.
- The selection is allowed to be uncomfortable. Broad-overlay and thin/abstract models are included because they are where quality collapse is most likely to show up.

Pilot models excluded from this batch: `base-rates`, `confidence-calibration`, `inversion`, `optionality`, `power-dynamics`, `premortem`, `problem-framing-and-reframing`, `second-order-thinking`, `systems-thinking`, `theory-of-constraints`.

## Source Availability Summary

All 20 proposed models have canonical source markdown present in `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216`.

None of the 20 source files are currently copied into `data/model_sources/`. If this selection is approved, PR 7 extraction should copy only the approved source files into repo-local source storage with hashes recorded by the packet assembly step.

| Status | Count |
| --- | ---: |
| Proposed models | 20 |
| Canonical source present | 20 |
| Canonical source missing | 0 |
| Already present in `data/model_sources/` | 0 |
| Pilot models included | 0 |

## Proposed 20-Model Batch

Lane 4 route counts are measured from 21 archived `result.json` files, using `structural_coverage_card.gap_routes[].candidate_model_ids`. `Route count` counts candidate appearances; `run count` counts distinct archived runs where the model appeared as a Lane 4 gap-route candidate.

| Primary stratum | Model id | Source file | Words | Route count | Run count | Why selected | Expected extraction risk |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| High-confidence practical | `anchoring` | `Anchoring_rag.md` | 1954 | 0 | 0 | Common cognitive-bias model with concrete diagnostic moves. Should extract cleanly without needing broad philosophical inference. | May collapse into generic "watch the first number" advice unless requirements force operational treatment. |
| High-confidence practical | `expected-value` | `Expected_Value_rag.md` | 2281 | 0 | 0 | Quantitative decision model with clear inputs, tradeoffs, and decision-use conditions. | May become spreadsheet boilerplate rather than a treatment requirement tied to evidence quality. |
| High-confidence practical | `decomposition` | `Decomposition_rag.md` | 2260 | 0 | 0 | Operational problem-solving model; useful test of whether extraction can capture mechanism without generic "break it down" language. | May overproduce generic diagnostic questions. |
| High-confidence practical | `decision-trees` | `Decision_Trees_rag.md` | 2368 | 0 | 0 | Structured decision architecture with explicit branching and uncertainty handling. | May duplicate expected-value unless the record distinguishes branching logic from valuation. |
| High-confidence practical | `sunk-cost-fallacy` | `Sunk_Cost_Fallacy_rag.md` | 1964 | 6 | 6 | Practical, known-bias model that also appears in Lane 4 commitment-reversibility routes. | May overlap with `optionality`; extraction must preserve its distinct failure mode. |
| Broad-overlay | `complex-adaptive-systems` | `Complex_Adaptive_Systems_rag.md` | 2174 | 0 | 0 | Broad systems lens likely to tempt generic feedback-loop affordances. Good stress test for completeness theater. | High risk of vague mechanisms that sound sophisticated but do not impose treatment requirements. |
| Broad-overlay | `emergence` | `Emergence_rag.md` | 2359 | 0 | 0 | Cross-domain mechanism that can become hand-wavy if the extraction overgeneralizes. | High risk of "whole greater than parts" boilerplate. |
| Broad-overlay | `leverage-points` | `Leverage_Points_rag.md` | 2076 | 0 | 0 | Broad intervention model; relevant to many domains but easy to flatten into generic "find leverage" advice. | Must distinguish leverage-point diagnosis from ordinary prioritization. |
| Broad-overlay | `network-effects` | `Network_Effects_rag.md` | 1845 | 1 | 1 | Broad economic and social mechanism; appears once in Lane 4 timing-sequencing routes. | Risk of platform-market case categorization instead of structural mechanism extraction. |
| Broad-overlay | `multi-criteria-decision-analysis` | `Multi_Criteria_Decision_Analysis_rag.md` | 2607 | 0 | 0 | Broad procedural model with many possible criteria. Useful test of whether records avoid checklist sprawl. | May become a generic scoring rubric unless activation and misuse guards are sharp. |
| Thin/abstract | `circle-of-control` | `Circle_Of_Control_rag.md` | 730 | 0 | 0 | Shortest non-pilot source found in curation-backed corpus. Tests whether the extractor can produce absence records or appropriately sparse affordances. | High risk of inventing unsupported affordances from thin source material. |
| Thin/abstract | `lindy-effect` | `Lindy_Effect_rag.md` | 1548 | 0 | 0 | Compact, philosophical/time-tested heuristic. Tests source discipline around probabilistic heuristic use. | May overclaim empirical grounding or confuse age with quality. |
| Thin/abstract | `johari-window` | `Johari_Window_rag.md` | 1818 | 0 | 0 | Interpersonal/self-knowledge framework; odd fit for the previous pilot's mostly decision-analytic records. | Risk of therapy-flavored genericity or case-category leakage. |
| Thin/abstract | `occams-razor` | `Occams_Razor_rag.md` | 1848 | 0 | 0 | Philosophical simplicity heuristic with known misuse risks. | May produce a one-note record unless misuse guards name oversimplification clearly. |
| Thin/abstract | `flow` | `Flow_rag.md` | 1857 | 0 | 0 | Psychological-state model rather than a classic decision model. Tests whether the schema can represent non-decision mechanisms honestly. | May not produce runtime-useful affordances; absence or narrow affordance may be the correct outcome. |
| Lane-4-frequent | `calculated-risk-taking` | `Calculated_Risk_Taking_rag.md` | 2130 | 16 | 14 | Highest Lane 4 candidate count across archived runs. Included because coverage value depends on frequent route models. | Could overlap with `risk-assessment`; records must distinguish calibrated action from risk inventory. |
| Lane-4-frequent | `risk-assessment` | `Risk_Assessment_rag.md` | 2078 | 14 | 14 | One of the strict top-frequency Lane 4 models, always under risk-response in the observed archive. | May become a generic risk checklist if treatment requirements are weak. |
| Lane-4-frequent | `incentives` | `Incentives_rag.md` | 2238 | 13 | 13 | Frequent non-risk route candidate under incentive-alignment. Adds diversity beyond the risk-response cluster. | May duplicate principal-agent or moral-hazard logic unless mechanism boundaries are clear. |
| Lane-4-frequent | `trade-offs` | `Trade_Offs_rag.md` | 2101 | 12 | 10 | Frequent resource-allocation/existing-vs-new route candidate. Adds a common decision-surface model. | May become generic "name tradeoffs" advice unless evidence requirements force comparison. |
| Lane-4-frequent | `information-asymmetry` | `Information_Asymmetry_rag.md` | 2922 | 10 | 10 | Frequent incentive-alignment route candidate with rich source material and strong operational relevance. | May overlap with uncertainty/calibration models unless asymmetry of parties is preserved. |

## Lane 4 Selection Note

The strict top-five Lane 4 candidates by route count are:

| Rank | Model id | Route count | Run count | Dominant dimension |
| ---: | --- | ---: | ---: | --- |
| 1 | `calculated-risk-taking` | 16 | 14 | `risk-response` |
| 2 | `risk-assessment` | 14 | 14 | `risk-response` |
| 3 | `black-swan-events` | 14 | 14 | `risk-response` |
| 4 | `antifragility` | 14 | 14 | `risk-response` |
| 5 | `resilience` | 14 | 14 | `risk-response` |

I am not proposing the strict top-five as the Lane-4-frequent stratum because it would mostly test one route cluster. The proposed Lane 4 stratum keeps the top two risk-response models, then adds frequent models from incentive-alignment and resource-allocation. This should make the batch more diagnostic of runtime coverage.

If Marcin wants the Lane 4 slice to be strictly frequency-ranked, replace `incentives`, `trade-offs`, and `information-asymmetry` with `black-swan-events`, `antifragility`, and `resilience`.

## Alternatives For Signoff

High-confidence practical alternates: `opportunity-cost`, `hanlons-razor`, `marginal-thinking`, `expected-utility`, `checklists`.

Broad-overlay alternates: `chaos-theory`, `mental-models-of-reality`, `pattern-recognition`, `scale-economies`, `creative-destruction`.

Thin/abstract alternates: `branch-solve-merge`, `regression-to-the-mean`, `abstraction`, `specialization`, `self-control`.

Lane-4-frequent alternates: `black-swan-events`, `antifragility`, `resilience`, `social-proof`, `moral-hazard`, `adverse-selection`, `psychological-safety`, `comparative-advantage`.

## Signoff Questions

1. Approve the diversified Lane-4-frequent stratum, or switch to the strict top-five frequency list?
2. Keep `circle-of-control` as the deliberate thin-source stress test, or replace it with a less extreme abstract model?
3. Keep `sunk-cost-fallacy` in high-confidence practical even though it is also Lane-4-frequent, or move it out to make the practical stratum less archive-shaped?

## Stop Condition

Extraction must not begin until this selection is approved. The next PR 7 step after signoff is the minimal packet assembly helper, followed by one fresh extraction session per approved model.
