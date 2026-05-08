## Cumulative Corpus Shape

| Batch | Models | Affordances | Absence Records |
| --- | ---: | ---: | ---: |
| Pilot | 10 | 22 | 2 |
| Batch 1 | 20 | 30 | 30 |
| Batch 2 | 20 | 34 | 51 |
| **Total (v3)** | **50** | **86** | **83** |

Absence-record density has grown with each batch: Pilot averaged 0.2 per model, Batch 1 averaged 1.5, Batch 2 averaged 2.6. This is directionally correct — the extraction contract is refusing generic field promotion rather than vacuuming up candidate material.

## Reviewer-Eye Acceptance Notes — Batch 2

These notes record the PM/reviewer judgment calls from the Batch 2 reviewer-eye pass (2026-05-05). They are not part of the mechanical compilation output.

- **`adverse-selection`** — `medium` affordance confidence accepted. Source explicitly states the named model is not present in the provided materials; the operational mechanism (hidden-type rent capture) is nonetheless source-backed with high-confidence quotes. Medium confidence is the correct signal. Do not downgrade to `weak_support` without a second review that finds the mechanism itself unsupported.
- **`empathy`** — Three-affordance record accepted. The third affordance (`empathy.substitute-perspective-taking-under-strategic-risk`) passed the structural differentiation test: it activates specifically when emotional empathy threatens strategic clarity or creates self-interest blind spots, a distinct treatment requirement from the first two affordances. Read this record first when the corpus reaches runtime evaluation.
- **`six-thinking-hats`** — Named-model caveat accepted. The affordance is source-backed through analogous role and mode separation; the named model is not explicitly present in the underlying materials. `medium` confidence on the affordance is the correct signal. If future runtime distinguishes human deliberation from AI-agent orchestration, the AI advisory-board example may deserve a separate reviewed source.
- **`pareto-principle`** — "Protected trial" normalization accepted with promotion note. The language is acceptable operational normalization of the source's 80/20 selection mechanism. When this affordance is considered for runtime promotion, the treatment requirement `retest-and-protect-future-drivers` should be reviewed to confirm the protected-trial framing holds under test.
- **`survivorship-bias`** — Failure-tail affordance accepted. The `base-rates` boundary is explicit in `do_not_use_when`. The failure-tail affordance (`survivorship-bias.restore-failure-tail-outcomes`) is survivorship-specific — it requires a selection mechanism that systematically excluded the failed cases, not generic risk assessment. Adjacent risk records verified: the boundary holds.

## Gate 3 Status

**Gate 3: cleared.**

50 models extracted across pilot, Batch 1, and Batch 2. Projected candidate-appearance coverage: **75.2%** across 21 archived Lane 4 runs (334 / 444 candidate appearances covered). Gap-route coverage: **92.0%** (80 / 87 gap-route rows).

Gate 3 cleared does not mean runtime value is proven. The gate ladder continues:

| Gate | Criterion | Status |
| --- | --- | --- |
| 1 | Instrument works (pilot calibrated) | ✅ cleared |
| 2 | Batch scales without quality collapse | ✅ cleared |
| 3 | Coverage reaches meaningful runtime slice | ✅ cleared |
| 4 | User-facing output beats baseline on archived cases | ⬜ not started |
| 5 | Stack merges to main | ⬜ blocked on Gate 4 |

No runtime consumer uses v3 records yet. Compilation to `affordances_v3.json` is the mechanical closeout of Gate 3. Gate 4 work — surfacing, baseline selection, judging archived cases — begins in the next PR.
