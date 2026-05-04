# PR 7 Batch Extraction Log - 2026-05-04

**Status:** 20/20 approved models extracted.
**Protocol:** One fresh Codex worker session per model.
**Output directory:** `data/model_affordances/batch_1/`
**Packet handling:** Workers assembled packets into `/tmp` locations only. No packet JSON files were committed.
**Reviewer-eye state:** Mechanical validation complete; Marcin reviewer-eye pending.

## Session Table

| Stratum | Model | Worker | Agent id | Record | Affordances | Absences | Validation | Reviewer-eye outcome |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
| High-confidence practical | `anchoring` | Euler | `019df4b2-9df8-78f3-aaf4-3f8edc791740` | `data/model_affordances/batch_1/anchoring.json` | 1 | 2 | passed | mechanically accepted with notes |
| High-confidence practical | `expected-value` | Anscombe | `019df4b2-9f1a-7622-9ce6-8f9237e56e5c` | `data/model_affordances/batch_1/expected-value.json` | 1 | 1 | passed | mechanically accepted with notes |
| High-confidence practical | `decomposition` | Rawls | `019df4b2-9f8d-7191-afd8-23a6dfa96ced` | `data/model_affordances/batch_1/decomposition.json` | 2 | 2 | passed | mechanically accepted with notes |
| High-confidence practical | `decision-trees` | Lovelace | `019df4b3-231f-76d3-99f6-bc0b5e78e32d` | `data/model_affordances/batch_1/decision-trees.json` | 2 | 0 | passed | mechanically accepted with notes |
| High-confidence practical | `sunk-cost-fallacy` | Jason | `019df4b3-2378-73f3-b38d-25974c44fe17` | `data/model_affordances/batch_1/sunk-cost-fallacy.json` | 1 | 0 | passed | mechanically accepted with notes |
| Broad-overlay | `complex-adaptive-systems` | Poincare | `019df4b3-2403-7931-8743-318afd6606cb` | `data/model_affordances/batch_1/complex-adaptive-systems.json` | 3 | 2 | passed | review flag: broad-overlay 3-affordance record |
| Broad-overlay | `emergence` | Lorentz | `019df4b6-8d03-7be1-a563-220707076e1e` | `data/model_affordances/batch_1/emergence.json` | 2 | 2 | passed | mechanically accepted with overlap note |
| Broad-overlay | `leverage-points` | Ptolemy | `019df4b8-0968-7c43-bc42-d0f84074a223` | `data/model_affordances/batch_1/leverage-points.json` | 3 | 1 | passed | review flag: broad-overlay 3-affordance record |
| Broad-overlay | `network-effects` | Goodall | `019df4b7-b151-7eb2-8479-4c6595b88710` | `data/model_affordances/batch_1/network-effects.json` | 2 | 2 | passed | mechanically accepted with notes |
| Broad-overlay | `multi-criteria-decision-analysis` | Dirac | `019df4b7-b1a3-7631-a5bc-e0330578eb24` | `data/model_affordances/batch_1/multi-criteria-decision-analysis.json` | 1 | 2 | passed | mechanically accepted with notes |
| Thin/abstract | `circle-of-control` | Dalton | `019df4b7-e7b9-7a02-bace-09d3b2411ed8` | `data/model_affordances/batch_1/circle-of-control.json` | 1 | 2 | passed | mechanically accepted; thin-source stress test passed |
| Thin/abstract | `lindy-effect` | Erdos | `019df4b8-8723-77e3-9a4f-f4287f10f2a2` | `data/model_affordances/batch_1/lindy-effect.json` | 1 | 0 | passed | mechanically accepted with notes |
| Thin/abstract | `johari-window` | Ampere | `019df4bb-3b66-7830-a7d3-c7bda5d0762f` | `data/model_affordances/batch_1/johari-window.json` | 1 | 2 | passed | mechanically accepted with notes |
| Thin/abstract | `occams-razor` | Franklin | `019df4bb-71bd-79e1-a0d2-e6180bc850f5` | `data/model_affordances/batch_1/occams-razor.json` | 1 | 2 | passed | mechanically accepted with notes |
| Thin/abstract | `flow` | Kant | `019df4bb-bbf5-7870-86bf-45e309890ccc` | `data/model_affordances/batch_1/flow.json` | 1 | 2 | passed | mechanically accepted with notes |
| Lane-4-frequent | `calculated-risk-taking` | Plato | `019df4bc-3267-7190-bfcc-00d4648bd75c` | `data/model_affordances/batch_1/calculated-risk-taking.json` | 1 | 2 | passed | mechanically accepted with notes |
| Lane-4-frequent | `risk-assessment` | Nash | `019df4bc-cc56-73a0-839c-51aa12108d6e` | `data/model_affordances/batch_1/risk-assessment.json` | 1 | 2 | passed | mechanically accepted with overlap note |
| Lane-4-frequent | `incentives` | Boole | `019df4bd-e2b4-7920-b1a4-2d33864d4d84` | `data/model_affordances/batch_1/incentives.json` | 2 | 1 | passed | mechanically accepted with boundary note |
| Lane-4-frequent | `trade-offs` | Planck | `019df4be-ada8-7012-b76d-2fab2133cc06` | `data/model_affordances/batch_1/trade-offs.json` | 1 | 1 | passed | mechanically accepted with genericity note |
| Lane-4-frequent | `information-asymmetry` | Banach | `019df4bf-1cf5-74f3-95eb-6aa13583f21e` | `data/model_affordances/batch_1/information-asymmetry.json` | 2 | 2 | passed | mechanically accepted with deferred exploitative-material note |

## Validation Commands

Focused batch validation:

```bash
pytest tests/test_pr7_batch_records.py tests/test_pr7_extraction_packet.py tests/test_model_affordance_pilot.py tests/test_model_affordance_compiler.py
```

Result: `24 passed`.

Each worker also ran record-level validation through `engine.system_b.model_affordance_validation.validate_model_affordance_file(..., source_roots=(Path("data/model_sources"),))`.

## Token Accounting

Token usage was not available from the Codex subagent API in this run. This is a measurement gap for future batch extraction work. The durable trace available in this artifact is worker nickname, agent id, model id, output record, and validation result.

## Surprises

- The thin/abstract stratum stayed sparse: all five records produced exactly one affordance.
- The broad-overlay stratum produced the highest affordance count and highest review burden.
- `trade-offs` did not inflate despite being the broadest Lane-4-frequent concept; it produced one affordance and one absence rejecting generic trade-off talk.
- No source quote validation failures occurred.
