# PR 9 Batch 2 Selection - 2026-05-05

**Status:** Step 1 selection proposal. Marcin signoff required before extraction.
**Branch:** `feature/knowledge-substrate-pr9-batch2-lane4-coverage`
**Target:** `feature/knowledge-substrate-pr8-compile-affordances-v2`
**Canonical corpus:** `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216`
**Archived-run source:** `/Users/marcin/.local/share/lolla/runs/*/*/result.json`
**Protocol source:** PR 9 Batch 2 Lane 4 coverage planning.

## Selection Doctrine

PR 7 proved that extraction can scale from the curated 10-model pilot to a heterogeneous 20-model batch without obvious quality collapse. PR 8 compiled that work into `affordances_v2.json`: 30 model records, 52 affordances, 32 absence records, and 0 quote-validation failures.

PR 9 should not repeat the same feasibility stress test. Gate 3 asks whether the extracted corpus covers a meaningful runtime slice, especially frequent Lane 4 structural-coverage routes. The selection below is therefore Lane-4-coverage-first, not four-stratum feasibility-first.

Primary rails:

- Propose 20 unique model ids not already present in `affordances_v2.json`.
- Prefer high-frequency Lane 4 candidates from archived runs.
- Report coverage before and projected coverage after Batch 2.
- Check source availability before extraction.
- Do not start extraction until Marcin approves the list.
- Keep extraction review-heavy. The reviewer burden remains a real signal, not toil to hide.

## Method

I recomputed Lane 4 frequency from 21 archived `result.json` files. Each file was read from `structural_coverage_card.gap_routes[].candidate_model_ids`.

Metrics:

- `route_count`: number of Lane 4 gap-route rows where the model appears as a candidate.
- `run_count`: number of distinct archived runs where the model appears at least once.
- `gap-route coverage`: share of gap-route rows with at least one extracted candidate model.
- `candidate-appearance coverage`: share of all candidate model appearances covered by an extracted record.
- `run coverage`: share of archived runs with at least one gap-route row covered by an extracted candidate.

Tie break for selection is deterministic: `route_count` descending, then `run_count` descending, then `model_id` alphabetical.

## Current Extracted Set

`affordances_v2.json` currently contains 30 extracted models: the 10 pilot records plus the 20 Batch 1 records.

| Coverage metric | Current value |
| --- | ---: |
| Extracted models | 30 |
| Archived result files | 21 |
| Lane 4 gap-route rows | 87 |
| Candidate model appearances | 444 |
| Gap-route coverage | 67 / 87 = 77.0% |
| Candidate-appearance coverage | 99 / 444 = 22.3% |
| Run coverage | 21 / 21 = 100.0% |

The gap-route number is already high because many route rows contain at least one extracted candidate. The candidate-appearance number is the sharper Gate 3 pressure metric: it asks whether the route slate is mostly covered, not merely touched.

## Ranked Lane 4 Candidates

| Rank | Model id | Route count | Run count | Dominant dimension | Extracted? |
| ---: | --- | ---: | ---: | --- | --- |
| 1 | `calculated-risk-taking` | 16 | 14 | `risk-response` | yes |
| 2 | `antifragility` | 14 | 14 | `risk-response` | no |
| 3 | `black-swan-events` | 14 | 14 | `risk-response` | no |
| 4 | `resilience` | 14 | 14 | `risk-response` | no |
| 5 | `risk-assessment` | 14 | 14 | `risk-response` | yes |
| 6 | `adverse-selection` | 13 | 13 | `incentive-alignment` | no |
| 7 | `incentives` | 13 | 13 | `incentive-alignment` | yes |
| 8 | `margin-of-safety` | 13 | 13 | `risk-response` | no |
| 9 | `moral-hazard` | 13 | 13 | `incentive-alignment` | no |
| 10 | `six-thinking-hats` | 13 | 13 | `stakeholder-alignment` | no |
| 11 | `social-proof` | 13 | 13 | `stakeholder-alignment` | no |
| 12 | `empathy` | 12 | 12 | `stakeholder-alignment` | no |
| 13 | `psychological-safety` | 12 | 12 | `stakeholder-alignment` | no |
| 14 | `trade-offs` | 12 | 10 | `resource-allocation` | yes |
| 15 | `comparative-advantage` | 11 | 11 | `resource-allocation` | no |
| 16 | `optimization-theory` | 11 | 11 | `resource-allocation` | no |
| 17 | `pareto-principle` | 11 | 11 | `resource-allocation` | no |
| 18 | `prioritization` | 11 | 11 | `resource-allocation` | no |
| 19 | `aleatory-epistemic-uncertainty-recognition` | 10 | 10 | `uncertainty-type` | no |
| 20 | `confidence-calibration` | 10 | 10 | `uncertainty-type` | yes |
| 21 | `correlation-vs-causation` | 10 | 10 | `information-quality` | no |
| 22 | `experimentation` | 10 | 10 | `uncertainty-type` | no |
| 23 | `information-asymmetry` | 10 | 10 | `incentive-alignment` | yes |
| 24 | `law-of-large-numbers` | 10 | 10 | `information-quality` | no |
| 25 | `statistical-discipline` | 10 | 10 | `information-quality` | no |
| 26 | `survivorship-bias` | 10 | 10 | `information-quality` | no |
| 27 | `true-uncertainty-navigation` | 10 | 10 | `uncertainty-type` | no |
| 28 | `opportunity-cost` | 10 | 9 | `resource-allocation` | no |
| 29 | `principal-agent-problem` | 9 | 9 | `incentive-alignment` | no |
| 30 | `probabilistic-thinking` | 9 | 9 | `uncertainty-type` | no |

## Proposed Batch 2

This proposal selects the top 20 non-extracted models by the deterministic ranking above. It deliberately includes the three risk-response models held back from Batch 1: `black-swan-events`, `antifragility`, and `resilience`.

| Slice | Model id | Source file | Words | Route count | Run count | Dominant dimension | Why selected | Extraction risk |
| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| Risk-response continuation | `antifragility` | `Antifragility_rag.md` | 1843 | 14 | 14 | `risk-response` | Strict top-frequency model held back from Batch 1. Adds response-through-stress logic to the risk cluster. | May collapse into generic resilience unless the record distinguishes improvement from mere survival. |
| Risk-response continuation | `black-swan-events` | `Black_Swan_Events_rag.md` | 2113 | 14 | 14 | `risk-response` | Strict top-frequency model held back from Batch 1. Needed for rare, high-impact downside structure. | May produce generic "prepare for tail risk" affordances unless source quotes force action boundaries. |
| Risk-response continuation | `resilience` | `Resilience_rag.md` | 2193 | 14 | 14 | `risk-response` | Strict top-frequency model held back from Batch 1. Completes the high-frequency risk-response cluster. | May overlap with antifragility and margin-of-safety unless failure-recovery mechanism is crisp. |
| Incentive alignment | `adverse-selection` | `Adverse Selection_rag.md` | 2579 | 13 | 13 | `incentive-alignment` | High-frequency incentive model not covered by Batch 1. | May duplicate information-asymmetry unless the hidden-type selection mechanism stays primary. |
| Risk-response continuation | `margin-of-safety` | `Margin_Of_Safety_rag.md` | 2429 | 13 | 13 | `risk-response` | High-frequency risk model that should sharpen downside buffer logic. | May duplicate calculated-risk-taking unless buffer/safety-factor treatment is distinct. |
| Incentive alignment | `moral-hazard` | `Moral_Hazard_rag.md` | 2082 | 13 | 13 | `incentive-alignment` | High-frequency incentive model that complements adverse-selection. | May blur into principal-agent unless post-decision risk transfer is preserved. |
| Stakeholder alignment | `six-thinking-hats` | `Six_Thinking_Hats_rag.md` | 2095 | 13 | 13 | `stakeholder-alignment` | Frequent stakeholder route candidate with a concrete deliberation structure. | May become meeting-facilitation boilerplate unless each role changes decision coverage. |
| Stakeholder alignment | `social-proof` | `Social_Proof_rag.md` | 1791 | 13 | 13 | `stakeholder-alignment` | Frequent stakeholder/social-influence candidate. | May become generic conformity warning unless evidence source and crowd validity are separated. |
| Stakeholder alignment | `empathy` | `Empathy_rag.md` | 2466 | 12 | 12 | `stakeholder-alignment` | Frequent stakeholder route candidate and useful test of interpersonal source material. | May become soft advice unless it imposes specific perspective-taking evidence requirements. |
| Stakeholder alignment | `psychological-safety` | `Psychological_Safety_rag.md` | 2263 | 12 | 12 | `stakeholder-alignment` | Frequent stakeholder route candidate with likely organizational mechanism. | May become culture language unless it names speak-up risk and information suppression. |
| Resource allocation | `comparative-advantage` | `Comparative_Advantage_rag.md` | 1995 | 11 | 11 | `resource-allocation` | Frequent allocation model for who should do what or which option has relative edge. | May duplicate opportunity-cost unless relative productivity remains central. |
| Resource allocation | `optimization-theory` | `Optimization_Theory_rag.md` | 2172 | 11 | 11 | `resource-allocation` | Frequent allocation model with formal objective/constraint potential. | May become generic "optimize the objective" unless constraints and tradeoffs are explicit. |
| Resource allocation | `pareto-principle` | `Pareto_Principle_rag.md` | 2131 | 11 | 11 | `resource-allocation` | Frequent allocation model that should test focus and uneven-return logic. | May become generic prioritization unless distribution/skew evidence is required. |
| Resource allocation | `prioritization` | `Prioritization_rag.md` | 2250 | 11 | 11 | `resource-allocation` | Frequent allocation model and broad procedural stress case. | High risk of generic task-ranking affordances; third affordance must pass a differentiation test. |
| Uncertainty type | `aleatory-epistemic-uncertainty-recognition` | `Aleatory_Epistemic_Uncertainty_Recognition_rag.md` | 2796 | 10 | 10 | `uncertainty-type` | Frequent uncertainty model that can distinguish reducible uncertainty from irreducible variance. | Long, technical model; may produce multiple affordances that need clear boundary proof. |
| Information quality | `correlation-vs-causation` | `Correlation_Vs_Causation_rag.md` | 2121 | 10 | 10 | `information-quality` | Frequent information-quality model with direct diagnostic value. | May duplicate causal-inference patterns unless correlation, cause, and intervention are separated. |
| Uncertainty type | `experimentation` | `Experimentation_rag.md` | 2267 | 10 | 10 | `uncertainty-type` | Frequent uncertainty model that can turn unknowns into test design. | May overlap with lean-startup or scientific-method records unless experiment shape is operational. |
| Information quality | `law-of-large-numbers` | `Law_of_Large_Numbers_rag.md` | 2047 | 10 | 10 | `information-quality` | Frequent evidence-quality model for sample size and repeated observations. | May duplicate base-rates/statistical-discipline unless aggregation logic is distinct. |
| Information quality | `statistical-discipline` | `Statistical_Discipline_rag.md` | 2049 | 10 | 10 | `information-quality` | Frequent evidence-quality model and likely runtime-relevant audit pattern. | May become generic statistical caution unless the record names the discipline required. |
| Information quality | `survivorship-bias` | `Survivorship_Bias_rag.md` | 2065 | 10 | 10 | `information-quality` | Frequent information-quality model with clear missing-data mechanism. | May duplicate base-rates unless excluded failures and selection mechanism are explicit. |

## Projected Coverage After Batch 2

| Coverage metric | Current v2 | Proposed after Batch 2 | Delta |
| --- | ---: | ---: | ---: |
| Extracted models | 30 | 50 | +20 |
| Gap-route coverage | 67 / 87 = 77.0% | 80 / 87 = 92.0% | +15.0 pp |
| Candidate-appearance coverage | 99 / 444 = 22.3% | 334 / 444 = 75.2% | +52.9 pp |
| Run coverage | 21 / 21 = 100.0% | 21 / 21 = 100.0% | +0.0 pp |

This is the main Gate 3 reason to prefer a strict Lane-4-frequency batch: it turns the extracted corpus from touching most gap routes to covering most of the candidate slate inside those routes.

## Source Availability

All 20 proposed models have source markdown present in the canonical corpus. None of the 20 source files are currently copied into `data/model_sources/`; if approved, the next step should copy only the approved files into repo-local source storage with hashes recorded by the packet assembly step.

| Status | Count |
| --- | ---: |
| Proposed models | 20 |
| Canonical source present | 20 |
| Canonical source missing | 0 |
| Already present in `data/model_sources/` | 0 |
| Already present in `affordances_v2.json` | 0 |

## Deliberately Skipped

These are not rejected models. They are near-frontier candidates deferred by the coverage-first cutoff.

| Model id | Route count | Run count | Reason skipped |
| --- | ---: | ---: | --- |
| `true-uncertainty-navigation` | 10 | 10 | Tied with the last selected models, but alphabetical tie break put it just outside the 20. Strong alternate if Marcin wants a narrower uncertainty source than `aleatory-epistemic-uncertainty-recognition`. |
| `opportunity-cost` | 10 | 9 | High-value practical model, but lower run count than the selected 10-route candidates. Strong Batch 3 candidate. |
| `principal-agent-problem` | 9 | 9 | Deferred because `moral-hazard` and `adverse-selection` cover higher-frequency incentive-alignment routes first. |
| `probabilistic-thinking` | 9 | 9 | Deferred because uncertainty/information-quality slots were consumed by 10-run candidates. |
| Competitive-dynamics cluster | 6-7 | 6-7 | `game-theory-payoffs`, `prisoners-dilemma`, `batna`, `red-queen-effect`, and `nash-equilibrium` form a coherent future batch cluster, but frequency is lower than the Gate 3 cutoff. |
| Thin/weird controls | n/a | n/a | Intentionally not included. Batch 1 already tested thin/abstract extraction; Batch 2 optimizes runtime coverage fraction. |

## Protocol Refinements For Extraction

Carry forward the Batch 1 rails and add one sharper check:

- Broad or procedural records with a third affordance must name a specific structural differentiation test in review notes. The third affordance is not rejected by default, but it must prove it is not a generic bias guard or duplicated diagnostic question pattern.
- Source quotes remain exact-substring validated.
- New records go under `data/model_affordances/batch_2/`, not `pilot/` or `batch_1/`.
- Pilot and Batch 1 records stay byte-clean.
- No user-facing runtime code changes.
- No compilation into `affordances_v3.json` until extraction and reviewer-eye are complete.

## Signoff Questions

1. Approve the strict top-20 non-extracted Lane 4 frequency list?
2. Replace `aleatory-epistemic-uncertainty-recognition` with `true-uncertainty-navigation` if you prefer a narrower uncertainty model, accepting no material coverage loss?
3. Swap one 10-count information-quality model for `opportunity-cost` if you want a practical allocation model in Batch 2, accepting the move away from strict run-count ranking?

## Stop Condition

Extraction must not begin until Marcin signs off on the proposed 20. After signoff, the next step is source copying plus one fresh extraction session per approved model.
