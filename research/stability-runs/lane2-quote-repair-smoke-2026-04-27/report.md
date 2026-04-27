# Lane 2 quote-repair smoke test

Date: 2026-04-27
Branch: `feat/lane2-quote-validation-repair-2026-04-27`
Case: `user-launch-independent-fintech`

## Scope

This is a one-case smoke test for the quote-validation repair implementation. It is not the full five-case audit gate.

Inputs:

- `~/.local/share/lolla/runs/user-launch-independent-fintech/20260424T123050Z/extraction.json`
- `~/.local/share/lolla/runs/user-launch-independent-fintech/20260424T123050Z/conversation.txt`

Command shape:

```bash
python3 scripts/run_pipeline.py \
  --extraction-file ~/.local/share/lolla/runs/user-launch-independent-fintech/20260424T123050Z/extraction.json \
  --conversation-file ~/.local/share/lolla/runs/user-launch-independent-fintech/20260424T123050Z/conversation.txt \
  --skip-revision \
  --embeddings off \
  --output full \
  --output-file research/stability-runs/lane2-quote-repair-smoke-2026-04-27/<output>.json
```

`--skip-revision` avoids the Step 6 revision call. The pipeline still runs its normal Lane 2 producer path and post-pipeline Bullshit Index path.

## Runs

| Output | Code state | Result |
|---|---|---|
| `user-launch-independent-fintech.json` | initial implementation | Unusable Lane 2 sample: verifier returned malformed payload with missing `accepted` / `rejected`; 60 candidates, 0 accepted, 0 rejected. |
| `user-launch-independent-fintech-rerun2.json` | initial implementation | Interpretable sample, but no quote repairs. 6 accepted-before-cap, 3 `execution_quote_not_literal_substring` demotions remained. |
| `user-launch-independent-fintech-rerun3.json` | after whitespace-normalized literal matching + ellipsis-fragment repair | Interpretable sample with 4 quote repairs, 5 surfaced anchors, and 0 remaining quote-validation demotions. |

## Rerun 3 headline

`companion_verification_quote_repairs` contained 4 repaired accepted entries:

Note: `user-launch-independent-fintech-rerun3.json` was generated before the follow-up method-label cleanup, so its `repair_method` values are generic. Current code records ellipsis-fragment repairs as `ellipsis_literal_fragment`.

| Model | Repair type | Repaired quote |
|---|---|---|
| `wysiati` | paraphrase / omitted source prefix repaired to literal span | `On pipeline: "if you were independent, we'd consider you" is almost exactly zero in actual conversion terms...` |
| `optionality` | ellipsis-fragment repair | `Launching in 6 weeks is viable if you do three things in those 6 weeks...` |
| `reasoning-mode-router` | ellipsis-fragment repair | `Before diving into tactics, can I ask a few things to make sure we're solving the right problem.` |
| `premortem` | ellipsis-fragment repair | `If you don't have an engagement by month 5, your remaining 3 months of runway pressure-cooks you into taking whatever comes along...` |

Rerun 3 rejection summary:

- `execution_quote_not_literal_substring`: 0
- `mechanism absent`: 47
- `too generic`: 6
- `topic-adjacent`: 1
- `passage already claimed by more specific model`: 1

## Interpretation

The smoke validates the implementation path: quote repair can convert verifier-accepted-but-nonliteral evidence into literal source substrings, and the repaired entries appear in audit output.

It does **not** yet pass the product gate. The repaired anchors need reviewer classification:

- `optionality` and `premortem` look aligned with the case-1 gold clusters.
- `wysiati` may be an honest secondary read of the pipeline/base-rate correction, but needs review.
- `reasoning-mode-router` may be an honest proxy for the C1 problem-framing move, but needs review because it was not in the original gold set.

The key question before expanding is not "did repair fire?" It did. The key question is whether the repaired anchors preserve the audit's trust axis.

## Next step

Do a quick human review of the 4 repaired anchors from `user-launch-independent-fintech-rerun3.json`.

If they are acceptable, expand to the bounded five-case audit:

- Quote-gate affected: `user-launch-independent-fintech`, `marcus-equity`, `mid-level-consultant-report`
- Prior 0% demotion regression checks: `mother-deciding-address-year`, `third-year-phd-student`

If any repaired anchor is false-positive or weak-evidence, tighten repair before expanding.
