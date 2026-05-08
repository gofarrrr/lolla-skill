# PR 9 Batch 2 Extraction Log - 2026-05-05

**Status:** 20/20 approved models extracted. Mechanical validation complete; Marcin reviewer-eye pending.
**Protocol:** One fresh Codex worker session per model.
**Output directory:** `data/model_affordances/batch_2/`
**Packet handling:** Packets were assembled into `/tmp/pr9-batch2-packets`. No packet JSON files were committed.
**Selection source:** `research/pr9-batch2-selection-2026-05-05.md`

## Session Table

| Slice | Model | Worker | Agent id | Record | Affordances | Absences | Validation | Reviewer-eye notes |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
| Risk-response | `antifragility` | Volta | `019df6d8-663f-7953-8e5b-2172fc49e3b1` | `data/model_affordances/batch_2/antifragility.json` | 1 | 3 | passed | No blocking flags; kept to improving through bounded stress, not survival or generic risk inventory. |
| Risk-response | `black-swan-events` | Godel | `019df6d8-66aa-7130-a333-c10c361d1678` | `data/model_affordances/batch_2/black-swan-events.json` | 2 | 3 | passed | Refused standalone generic risk assessment; bounded to deep uncertainty, tail exposure, prediction limits, and post-shock learning. |
| Risk-response | `resilience` | Singer | `019df6d8-66ea-7a03-b207-4c9f968ea624` | `data/model_affordances/batch_2/resilience.json` | 1 | 3 | passed | Kept to recovery with continued function; `challenge-recovery-story` is the main reviewer judgment point. |
| Incentive alignment | `adverse-selection` | Herschel | `019df6d8-6736-7cd3-93a7-0c0098840338` | `data/model_affordances/batch_2/adverse-selection.json` | 1 | 2 | passed | Source says Adverse Selection is not explicitly defined; reviewer should decide whether confidence/status should be downgraded. |
| Risk-response | `margin-of-safety` | Ohm | `019df6d8-675c-7d32-adf4-690ff96aa67f` | `data/model_affordances/batch_2/margin-of-safety.json` | 1 | 2 | passed | Boundary with `risk-assessment` and `calculated-risk-taking` should be checked; record is buffer/safety-factor design. |
| Incentive alignment | `moral-hazard` | Carver | `019df6d9-0481-72b0-8509-0fa3bc475983` | `data/model_affordances/batch_2/moral-hazard.json` | 2 | 3 | passed | Kept `short-termism` as absence/guard rather than standalone affordance. |
| Stakeholder alignment | `six-thinking-hats` | Hooke | `019df6dc-fc3d-7cb0-b019-612043ca1e24` | `data/model_affordances/batch_2/six-thinking-hats.json` | 1 | 3 | passed | Source caveats named-model support; record is source-backed through analogous mode separation, not generic facilitation. |
| Stakeholder alignment | `social-proof` | James | `019df6dc-fd52-7f21-9d90-d3575a9b8f21` | `data/model_affordances/batch_2/social-proof.json` | 2 | 3 | passed | No blocking flags; boundary with `correlation-vs-causation`, `authority-bias`, and `psychological-safety` worth later review. |
| Stakeholder alignment | `empathy` | Locke | `019df6dc-fef5-73c1-93d0-b054c241f51d` | `data/model_affordances/batch_2/empathy.json` | 3 | 2 | passed | Only 3-affordance record; includes required differentiation note. Review possible overlap with active listening/perspective taking. |
| Stakeholder alignment | `psychological-safety` | Peirce | `019df6dd-6093-75c0-b8a3-84b0bd33c12a` | `data/model_affordances/batch_2/psychological-safety.json` | 2 | 2 | passed | Accountability material merged into correction path; reviewer may later split but this pass stayed sparse. |
| Resource allocation | `comparative-advantage` | Euclid | `019df6dd-6175-71e3-8748-bc424dbed104` | `data/model_affordances/batch_2/comparative-advantage.json` | 1 | 2 | passed | Check whether `check-specialization-boundaries` belongs in the main affordance or only misuse guards. |
| Resource allocation | `optimization-theory` | Newton | `019df6dd-f496-7d72-8660-5ef34953facd` | `data/model_affordances/batch_2/optimization-theory.json` | 2 | 3 | passed | Boundary review needed against `trade-offs`, `pareto-principle`, `prioritization`, and `theory-of-constraints`. |
| Resource allocation | `pareto-principle` | Helmholtz | `019df6e0-bd19-7c73-a638-4dde4c58902e` | `data/model_affordances/batch_2/pareto-principle.json` | 1 | 3 | passed | Check normalized "protected trial" language; activate only when skewed-return evidence changes allocation. |
| Resource allocation | `prioritization` | Wegener | `019df6e0-f5b5-7b63-9778-4e9e4cdbe162` | `data/model_affordances/batch_2/prioritization.json` | 2 | 3 | passed | Kept out of generic task-ranking; boundaries to watch with adjacent allocation and experimentation records. |
| Uncertainty type | `aleatory-epistemic-uncertainty-recognition` | Sartre | `019df6e1-280f-7760-ab07-5a9e241c1f27` | `data/model_affordances/batch_2/aleatory-epistemic-uncertainty-recognition.json` | 2 | 2 | passed | Should activate only when reducible-vs-irreducible uncertainty changes method choice, commitment size, reversibility, or monitoring. |
| Information quality | `correlation-vs-causation` | Mendel | `019df6e1-75b8-7c00-af74-1f0aedeb78fa` | `data/model_affordances/batch_2/correlation-vs-causation.json` | 2 | 2 | passed | Explicitly separated from `base-rates`; prediction-vs-causation tool routing remains a reviewer boundary. |
| Uncertainty type | `experimentation` | Harvey | `019df6e2-af56-77e2-96ba-7fd20965282d` | `data/model_affordances/batch_2/experimentation.json` | 2 | 3 | passed | Generic learning-loop, digital-twin/simulation, and standalone falsification splits recorded as absences. |
| Information quality | `law-of-large-numbers` | Mencius | `019df6e3-3fc5-7422-b7e1-bbf993176f77` | `data/model_affordances/batch_2/law-of-large-numbers.json` | 2 | 2 | passed | Explicitly separated from `base-rates`; distribution/tail checks stay guards on large-N inference. |
| Information quality | `statistical-discipline` | Einstein | `019df6e4-9487-7001-b1f4-80e8c4cb97f1` | `data/model_affordances/batch_2/statistical-discipline.json` | 2 | 2 | passed | Boundary checks requested with LLN, causation, survivorship, and aleatory/epistemic records. |
| Information quality | `survivorship-bias` | Hegel | `019df6e5-f79f-7f43-a172-27210f502797` | `data/model_affordances/batch_2/survivorship-bias.json` | 2 | 3 | passed | Explicit base-rates boundary; check whether failure-tail affordance remains survivorship-specific with adjacent risk records loaded. |

## Validation Commands

Focused PR 9 validation:

```bash
pytest tests/test_pr9_batch2_records.py tests/test_pr7_extraction_packet.py
```

Result: `10 passed`.

Each worker also ran record-level validation through `engine.system_b.model_affordance_validation.validate_model_affordance_file(..., source_roots=(Path("data/model_sources"),))`.

## Token Accounting

Token usage was not available from the Codex subagent API in this run. The durable trace available in this artifact is worker nickname, agent id, model id, output record, validation result, and reviewer flags.

## Surprises

- Batch 2 is absence-heavy: 34 affordances and 51 absence records. That is a healthy signal for a coverage-first batch, because the workers did not fill frequent Lane 4 models with generic substrate.
- Only one record produced three affordances: `empathy`. It includes the required differentiation note and should be reviewer-eye checked.
- Two affordances used `medium` confidence rather than the all-high pattern from earlier extraction. Both are in `adverse-selection`, where the source explicitly caveats named-model support.
- The information-quality records consistently recorded `base-rates` duplicates as absences rather than re-extracting denominator/reference-class anchoring.
- Source quote validation produced 0 failures.
