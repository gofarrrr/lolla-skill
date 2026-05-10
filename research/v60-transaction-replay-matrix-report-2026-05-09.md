# V60 Transaction Replay Matrix Report

Date: 2026-05-09
Branch: `feat/v60-transaction-local-replay-lab`
Status: expanded dry-run evidence only; no model calls

## What Ran

Command:

```bash
PYTHONPATH=. python3 scripts/run_v60_transaction_replay_matrix.py \
  --case-manifest research/v60-transaction-replay-case-manifest-2026-05-09.json \
  --affordances-path data/compiled/model_affordances/affordances_v60.json \
  --output-dir data/evaluations/v60_transaction_replay_lab/2026-05-09-matrix \
  --dry-run
```

Generated artifacts:

- `data/evaluations/v60_transaction_replay_lab/2026-05-09-matrix/summary.json`
- `data/evaluations/v60_transaction_replay_lab/2026-05-09-matrix/matrix_report.md`

No OpenRouter calls were made. Live `/lolla`, Step 6, Step 8, memo, and
Observatory behavior remain untouched.

## Matrix Shape

The matrix varied packet caps, packet snippet density, decoder snippet density,
and solution mode.

Configurations:

| Config | Purpose |
| --- | --- |
| `cap4_tiny` | Lower-bound stress test for extreme selectivity. |
| `cap8_focused` | First plausible product-shaped packet. |
| `cap12_default_compact` | Current research default after compact projection. |
| `cap16_wide_compact` | Wide diagnostic packet to test hidden nomination loss. |
| `cap16_wide_rich` | Upper-burden diagnostic packet with richer snippets. |

Solution modes:

| Mode | Product Meaning |
| --- | --- |
| `answer_revision` | Produce a better answer plus ledger. |
| `edge_audit` | Surface what the vanilla answer likely missed without rewriting everything. |
| `question_gate` | Separate answerable-now claims from missing-evidence blockers. |

These modes should not be collapsed. They are different products. A user buying
a decision answer, an edge audit, and an evidence gate is buying three related
but distinct experiences.

## Aggregate Results

| Config | Cap | Max Noms | Cards | Suppressed | Weak Aff. | Medium Aff. | Absences | Arm C Token Range |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `cap4_tiny` | 4 | 18 | 32 | 112 | 1 | 2 | 32 | 7.5k-12.8k |
| `cap8_focused` | 8 | 18 | 64 | 80 | 2 | 4 | 128 | 10.3k-16.0k |
| `cap12_default_compact` | 12 | 18 | 96 | 48 | 2 | 5 | 192 | 12.9k-18.9k |
| `cap16_wide_compact` | 16 | 24 | 128 | 64 | 2 | 10 | 256 | 16.0k-21.6k |
| `cap16_wide_rich` | 16 | 24 | 128 | 64 | 2 | 10 | 318 | 27.9k-35.9k |

All configurations preserve the explicit BATNA and price-discrimination probes.
That is good: explicit review probes are not being lost under cap pressure.

## What Works

The lab is now good enough to expose product-relevant tradeoffs locally:

- `cap8_focused` preserves weak-support visibility, keeps explicit probes, and
  avoids the `arm_c_more_than_3x_arm_b` flag.
- `cap12_default_compact` preserves more reasoning surface while staying below
  the 20k estimated-token threshold on all cases.
- The compact projection makes Arm C viable enough for a small paid pilot.
- The three solution modes barely change token burden; product mode should be
  chosen by user value, not cost.
- Weak-support handling is visible in the `real_estate` case across all caps.
- Absence records scale predictably with cap and snippet density.

## What Does Not Work Yet

`cap4_tiny` is too thin for broad replay. It keeps the earliest/highest-priority
cards but suppresses 14 candidates per case. It is useful only as a lower-bound
stress test.

`cap16_wide_rich` is too heavy for first paid replay. Every case exceeds the
20k estimated-token flag and every case is more than 3x Arm B. It is useful for
diagnostics, not for product-shaped evaluation.

`cap16_wide_compact` reveals hidden candidates, but it is also not a clean
product default. It increases medium-confidence visibility from 5 to 10 across
the slate, but starts tripping payload flags and still suppresses candidates
because it admits 24 nominations per case.

`cap12_default_compact` is attractive for research, but it overburdens
`user_has_plan`, the narrow-control case. That matters: if a user already has a
reasonable plan, the system should not make the experience feel artificially
deep.

## Cap Interpretation

The matrix clarifies that card cap is not a mere cost setting. It changes the
kind of cognition being tested.

`cap8_focused` keeps the first eight cards. In the slate it tends to preserve
the central pressure while avoiding broad late-arriving material. For example:

- `multi_offer`: keeps BATNA, power, sunk cost, status quo, meta-reflection,
  information asymmetry, optionality, and opportunity cost.
- `real_estate`: keeps price-discrimination, margin of safety, Nash
  equilibrium, premortem, optionality, sunk cost, lock-in, and commitment bias.
- `user_has_plan`: keeps planning fallacy, optionality, feedback loops, base
  rates, risk assessment, black swan, antifragility, and margin of safety.

`cap12_default_compact` adds more useful but heavier material:

- `multi_offer`: comparative advantage, trade-offs, Pareto, prioritization.
- `real_estate`: switching costs, path dependence, game theory, prisoners'
  dilemma.
- `user_has_plan`: calculated risk, resilience, opportunity cost, comparative
  advantage.

Those may be valuable in research. They may be too much for a first product
surface. The difference should be treated as a deliberate product decision, not
an implementation default.

## Architecture Read

The deterministic layer is behaving like a courier and validator:

- it preserves explicit v60 artifact selection;
- it merges lane and fixture nominations deterministically;
- it emits grouped affordance identities;
- it preserves absence records;
- it validates ledger traceability;
- it reports suppressed cards instead of hiding them;
- it does not decide semantic usefulness.

The next architecture requirement is cap policy. A paid replay should record
whether it is testing:

- focused product packet: `cap8_focused`;
- broader research packet: `cap12_default_compact`;
- hidden-candidate diagnostic: `cap16_wide_compact`.

Those are different tests.

## User Read

The user value question is not "how many cards did the system consider?" It is
"did the system improve the user's thinking without making the experience feel
overbuilt?"

The matrix suggests three user-facing modes worth testing separately:

- `answer_revision`: best when the user wants a better final answer now.
- `edge_audit`: best when the user has a draft or plan and wants to know what
  they are missing.
- `question_gate`: best when the evidence is thin and the right answer is not
  yet responsibly knowable.

For narrow cases, `edge_audit` or `question_gate` may be more honest than a full
answer rewrite.

## Product Read

The likely first paid pilot should not use the wide configs. My current product
recommendation is:

- default pilot config: `cap8_focused`;
- comparison config for research only: `cap12_default_compact`;
- pilot solution modes: `edge_audit` and `question_gate` before full
  `answer_revision`.

Reason: the product promise is not "we can add a lot of lenses." It is "we can
apply the right amount of source-backed pressure without theatrical depth."

## Monetization Read

This points to a clearer premium product ladder:

- basic Lolla answer: strong answer with current deterministic lanes;
- paid decision review: `edge_audit` over the user's plan or vanilla answer;
- premium evidence gate: `question_gate` with source-backed absence blockers;
- team/review tier: answer plus transaction ledger and memo traceability.

The high-value paid surface is probably not the longest answer. It is the
inspectable edge/evidence review that can tell a user:

> This is the part of your reasoning that is probably under-supported, this is
> the lens that exposed it, and this is what would have to be true before the
> stronger conclusion is justified.

## Recommendation

Do not run a broad paid replay yet.

The next paid test, if approved, should be small and explicit:

1. Use `cap8_focused` as the product-shaped config.
2. Run the four-case slate: `user_has_plan`, `real_estate`, `whistleblower`,
   `messy_three_problems`.
3. Test `edge_audit` and `question_gate` first.
4. Keep `cap12_default_compact` as a research comparison, not the default.
5. Judge against Arm B for useful decision delta, not card usage.

Promotion remains blocked until we see that the grouped substrate improves
reasoning without increasing hallucinated facts, cheap rejection, model-name
theater, or user-facing overcomplexity.
