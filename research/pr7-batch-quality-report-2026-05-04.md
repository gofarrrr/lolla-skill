# PR 7 Batch Quality Report - 2026-05-04

**Status:** Batch 1 extraction completed; reviewer-eye pending.
**Branch:** `feature/knowledge-substrate-pr7-batch-extraction-trial`
**Scope:** 20 approved non-pilot models extracted under `data/model_affordances/batch_1/`.
**Canonical source root:** `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216`
**Repo source root:** `data/model_sources`

## Headline

The batch extraction did not collapse into uniform completeness theater. The 20-model batch produced 30 affordances and 30 absence records. The distribution is uneven by design: thin/abstract models all produced exactly 1 affordance, broad-overlay models produced the widest spread and the highest review burden, and Lane-4-frequent models mostly stayed narrow.

This is encouraging feasibility evidence, not runtime-value evidence. The batch says the instrument can produce a heterogeneous corpus slice without obvious mechanical collapse. It does not prove the new affordances improve Lane 4 or any user-facing surface.

## Pilot vs Batch

| Metric | Pilot 10 | Batch 20 | Delta / note |
| --- | ---: | ---: | --- |
| Models | 10 | 20 | Batch is 2x pilot size. |
| Total affordances | 22 | 30 | Lower affordances/model in batch: 1.5 vs 2.2. |
| Total absence records | 2 | 30 | Strong increase; absence discipline is doing real work. |
| Affordance count distribution | 1: 3, 2: 3, 3: 3, 4: 1 | 1: 12, 2: 6, 3: 2 | Batch is less smooth than pilot, which is good. |
| Top-level status distribution | 10 supported | 20 supported | Status alone is not the quality signal. |
| Affordance confidence distribution | 22 high | 30 high | Confidence remains informationless; same pattern as prior substrate work. |
| Source-quote validation rejections | 0 | 0 | All batch records passed exact-quote validation. |
| Median source quote length | 130 chars | 139 chars | Comparable quote granularity. |
| Source evidence spans | 232 | 453 | More absence evidence and larger batch. |
| Cross-model identical extraction-type distributions | 0 | 3 | Mild repeat pattern; not a collapse signal by itself. |
| Empty `dropped_material` notes | 0 | 0 | Every record names material not promoted. |
| Source-file existence pre-extraction | 10/10 | 20/20 | All approved sources were present in canonical corpus. |
| Reviewer rewrite rate | n/a | 0 mechanical rewrites so far | Marcin reviewer-eye still pending. |
| Reviewer rejection rate | n/a | 0 mechanical rejections so far | Marcin reviewer-eye still pending. |
| Token cost | not logged | not logged | Codex subagent API did not expose per-worker token usage. Session IDs are logged instead. |

## Per-Stratum Quality

| Stratum | Models | Affordances | Absences | Affordance distribution | Signal |
| --- | ---: | ---: | ---: | --- | --- |
| High-confidence practical | 5 | 7 | 5 | 1: 3, 2: 2 | Pilot-like but not inflated. |
| Broad-overlay | 5 | 11 | 9 | 1: 1, 2: 2, 3: 2 | Highest richness and highest review burden. |
| Thin/abstract | 5 | 5 | 8 | 1: 5 | Strong absence/sparsity discipline. |
| Lane-4-frequent | 5 | 7 | 8 | 1: 3, 2: 2 | Narrow enough to avoid route-frequency overproduction. |

## Per-Model Summary

| Stratum | Model | Affordances | Absences | Review note |
| --- | --- | ---: | ---: | --- |
| High-confidence practical | `anchoring` | 1 | 2 | Kept to provisional-anchor correction discipline; systems-risk material left as guard/review concern. |
| High-confidence practical | `decision-trees` | 2 | 0 | Branch triggers and branch-kill audit; enriched risk table should get reviewer-eye. |
| High-confidence practical | `decomposition` | 2 | 2 | MECE/action handoff plus assumption/cut testing; learning/scaffolding not promoted. |
| High-confidence practical | `expected-value` | 1 | 1 | One weighted-payoff boundary affordance; business-case expansion treated as duplicate. |
| High-confidence practical | `sunk-cost-fallacy` | 1 | 0 | One future-value recommitment affordance; no domain split. |
| Broad-overlay | `complex-adaptive-systems` | 3 | 2 | Review flag: broad-overlay 3-affordance record. |
| Broad-overlay | `emergence` | 2 | 2 | Overlap with CAS explicitly named for later boundary review. |
| Broad-overlay | `leverage-points` | 3 | 1 | Review flag: broad-overlay 3-affordance record. |
| Broad-overlay | `multi-criteria-decision-analysis` | 1 | 2 | One auditable matrix affordance; procedural sprawl avoided. |
| Broad-overlay | `network-effects` | 2 | 2 | Threshold/adoption path split; moat inevitability not promoted. |
| Thin/abstract | `circle-of-control` | 1 | 2 | Deliberate thin-source stress test stayed sparse. |
| Thin/abstract | `flow` | 1 | 2 | Psychological-state model kept to calibrated immersion conditions. |
| Thin/abstract | `johari-window` | 1 | 2 | Feedback/disclosure loop only; personality diagnosis not promoted. |
| Thin/abstract | `lindy-effect` | 1 | 0 | Qualitative durability prior; no invented quantitative calibration. |
| Thin/abstract | `occams-razor` | 1 | 2 | Lowest-assumption pruning; prompt-concision material not promoted. |
| Lane-4-frequent | `calculated-risk-taking` | 1 | 2 | Bounded-wager contract; generic risk tools not split out. |
| Lane-4-frequent | `incentives` | 2 | 1 | Incentive mapping plus reward design; principal-agent/moral-hazard kept out. |
| Lane-4-frequent | `information-asymmetry` | 2 | 2 | Party observability and tacit-knowledge extraction; exploitative material deferred. |
| Lane-4-frequent | `risk-assessment` | 1 | 2 | Thresholded downside governance; checklist theater explicitly rejected. |
| Lane-4-frequent | `trade-offs` | 1 | 1 | Allocation-backed sacrifice only; generic "all decisions have tradeoffs" rejected. |

## Review Flags

No thin/abstract model produced 3+ affordances. This is the strongest anti-invention signal in the batch, especially because `circle-of-control` was genuinely thin at 59 lines / 5.7KB.

Two broad-overlay models produced 3 affordances and should be spot-checked cold:

- `complex-adaptive-systems`
- `leverage-points`

The broad-overlay stratum did not produce uniform 4-affordance records, but it is where the extraction instrument bends hardest. If reviewer-eye finds one or both 3-affordance records are inflated, that is not catastrophic; it is the point of this batch.

Known boundary overlaps to inspect:

- `emergence` vs `complex-adaptive-systems`
- `risk-assessment` vs `calculated-risk-taking`
- `incentives` vs principal-agent / moral-hazard models
- `trade-offs` vs expected-value / cost-benefit analysis
- `information-asymmetry` vs principal-agent observability

## What This Report Deliberately Omits

No completeness score. No promotion recommendation. No Lane 4 improvement claim. No audit re-run on archived cases. No compiled artifact regeneration. No claim that `confidence: high` is meaningful, because confidence remains uniform across the batch.

## Verdict

Batch 1 scales with caveats. The extraction instrument produced source-valid, heterogeneous records across 20 non-pilot models. The most important positive signal is not the 30 affordances; it is the 30 absence records and the sparse thin/abstract stratum. The main caveat is broad-overlay richness: `complex-adaptive-systems` and `leverage-points` need reviewer-eye before we decide whether batch quality truly holds there.
