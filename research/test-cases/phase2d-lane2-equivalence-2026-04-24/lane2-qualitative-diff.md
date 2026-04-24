# Phase 2d Lane 2 — qualitative diff on the one regression case

**Date:** 2026-04-24
**Companion report:** `lane2-quality-report.md` (aggregate: new 4.03 vs old 3.5 detected models, +15%)

## Purpose

Aggregate is a clean win: new path finds equal-or-more detected models on 9 of 10 cases, drop-rate stays at 0.0 on both paths, cascade into Lanes 1/3/4 is within normal variance. **One case was flagged: whistleblower.** This markdown diagnoses that single regression.

## `whistleblower` — the one flagged regression

**Flag:** `detected_models_regression: new median=3 vs old=5 (dropped ≥2)`.

### Per-run breakdown

| path | run | detected_count | models |
|---|---|---|---|
| old | 0 | 5 | information-asymmetry, understanding-motivations, checklists, intellectual-humility, auditability-traceability |
| old | 1 | 2 | scientific-method, game-theory-payoffs |
| old | 2 | 5 | principal-agent-problem, information-asymmetry, game-theory-payoffs, moral-hazard, base-rates |
| new | 0 | 3 | scientific-method, probabilistic-thinking, information-asymmetry |
| new | 1 | 5 | confidence-calibration, boundaries, authority-bias (violated!), scientific-method, intellectual-humility |
| new | 2 | 0 | (none) |

### Observation 1: both paths are inherently unstable on this case

- Old path: 5, 2, 5 detected — one run (old_1) at 2, despite median 5. Variance is real on old.
- New path: 3, 5, 0 detected — one run (new_2) at 0. Variance is real on new.

Across 3 runs, old finds 10 unique models total; new finds 7 unique. New is narrower but still substantive. The "old median 5" obscures that old_1 only found 2 — the median is not a reliable stability claim.

### Observation 2: model sets are different, both paths find relevant signal

- Old's top models on good runs: information-asymmetry, principal-agent-problem, moral-hazard, game-theory-payoffs, base-rates — relationships between senior partner, firm leadership, and the whistleblower.
- New's models on good runs: scientific-method-evidence-testing, probabilistic-thinking, confidence-calibration, authority-bias (violated), boundaries — reasoning-quality models applied to the assistant's actual reasoning.

Both are legitimate for a whistleblower scenario. Neither path is "correct" and the other "wrong" — they emphasize different classes of model. This is parallel to Phase 2c's Marcus finding (old path detected `inconsistency-avoidance`; new path detected `deprival-superreaction + contrast-misreaction` — different model sets, both grounded in the same assistant turns).

### Observation 3: the 0-detected run (new_2) is LLM variance

Looking at new_2's audit: 6 fingerprint moves validated, 60 candidates proposed at recall, 0 accepted at verification. Verification rejected every candidate as "too generic" or "topic-adjacent" — the verifier was unusually strict on that roll.

New_1 on the same case (same prompts, same input, different sampling seed) found 5 models. The failure mode is random verifier strictness, not systematic under-triggering. Same class of event as Phase 2b's 0-gap-qs anomaly (which was also 2/30 new-path runs and resolved as random variance after diagnosis).

## Not-a-false-positive check (contrast with Phase 2c)

Phase 2c had the opposite problem: 3 cases where old-path findings were confabulations. Here, neither path looks like it's confabulating — both produce evidence passages that are genuine substrings of assistant turns with plausible reasoning.

- Old's `information-asymmetry` on whistleblower cites: *"Internal reporting requires you to trust that the general counsel will take action against a senior partner who likely has the firm's political protection."* — real information asymmetry.
- New's `authority-bias (violated)` on whistleblower cites: *"Internal reporting requires you to trust that the general counsel will take action…"* — same passage, different model lens. The assistant is arguing AGAINST trusting internal authority; `authority-bias` in `violated` mode fits (the assistant names authority-bias as the failure mode the user should avoid).

These are parallel legitimate reads of the same passage from different model-library angles. Neither is wrong.

## Aggregate signal vs whistleblower regression

- 9 of 10 cases: new path ≥ old path on detected models.
- Whistleblower is 1 of 10 cases where new median is lower than old median (by 2).
- On whistleblower specifically, both paths' detected sets are legitimate; new path is narrower but still finds meaningful models.
- No zero-detected rate on old path; new path has 2/30 zero-detected runs (6.7%), both on cases where the verifier was unusually strict on one roll (whistleblower_new_2 and user_has_plan_new_0).

This is the kind of single-case noise that individual dice rolls will produce. It does not invalidate the aggregate +15% detection improvement. Parallel to 2b's multi_offer 12/8/12 pattern (one low-variance run embedded in otherwise-stable output) — acknowledged and documented, not a blocker.

## Conclusion

No false-positive diagnosis needed here (unlike 2c). The architectural change on Lane 2 is producing:
- More detected models on 9 of 10 cases
- Same fingerprint quality (drop rate 0.0 on both paths)
- Equal or stricter verification (consistent with substring validation operating on narrower audit target)
- One case (whistleblower) with run-variance noise on both paths

Ship with honest framing: aggregate is a clear win, one case has run-variance we document.
