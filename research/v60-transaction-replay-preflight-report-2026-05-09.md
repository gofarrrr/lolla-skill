# V60 Transaction Replay Lab Preflight Report

Date: 2026-05-09
Branch: `feat/v60-transaction-local-replay-lab`
Status: dry-run evidence only; no model calls

## What Ran

Command:

```bash
PYTHONPATH=. python3 scripts/run_v60_transaction_replay_lab.py \
  --case-manifest research/v60-transaction-replay-case-manifest-2026-05-09.json \
  --affordances-path data/compiled/model_affordances/affordances_v60.json \
  --output-dir data/evaluations/v60_transaction_replay_lab/2026-05-09-preflight \
  --dry-run
```

Generated artifacts:

- `data/evaluations/v60_transaction_replay_lab/2026-05-09-preflight/summary.json`
- `data/evaluations/v60_transaction_replay_lab/2026-05-09-preflight/preflight_report.md`
- per-case case artifacts
- per-case grouped v60 packets
- per-case Arm A/B/C prompt packets
- per-case dry-run ledger templates

No OpenRouter calls were made. Live `/lolla`, Step 6, Step 8, memo, and
Observatory behavior remain untouched.

Expanded matrix follow-up:

- `data/evaluations/v60_transaction_replay_lab/2026-05-09-matrix/summary.json`
- `data/evaluations/v60_transaction_replay_lab/2026-05-09-matrix/matrix_report.md`
- `research/v60-transaction-replay-matrix-report-2026-05-09.md`

## Case Slate

| Case | Main role in lab |
| --- | --- |
| `multi_offer` | negotiation, career, family constraints, BATNA probe |
| `whistleblower` | legal/ethical risk, power asymmetry, evidence threshold |
| `startup_pivot` | weak evidence, thin-signal overconfidence |
| `real_estate` | sparse personal finance, weak-support price-discrimination probe |
| `friendship_money` | personal strategic-gate edge, relationship pressure |
| `messy_three_problems` | multi-thread instability and separation stress |
| `user_has_plan` | narrow-control case; avoid needless complexity |
| `phd_research` | long professional uncertainty and broad-card pressure |

## Preflight Counts

| Case | Cards | Suppressed | Reviewed | Weak/conflicting | Medium aff. | Weak aff. | Absence records |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `multi_offer` | 12 | 6 | 12 | 0 | 1 | 0 | 24 |
| `whistleblower` | 12 | 6 | 12 | 0 | 1 | 0 | 24 |
| `startup_pivot` | 12 | 6 | 12 | 0 | 1 | 0 | 24 |
| `real_estate` | 12 | 6 | 11 | 1 | 2 | 2 | 24 |
| `friendship_money` | 12 | 6 | 12 | 0 | 0 | 0 | 24 |
| `messy_three_problems` | 12 | 6 | 12 | 0 | 0 | 0 | 24 |
| `user_has_plan` | 12 | 6 | 12 | 0 | 0 | 0 | 24 |
| `phd_research` | 12 | 6 | 12 | 0 | 0 | 0 | 24 |

## Token Pressure

The generated preflight now estimates serialized prompt packet size. This is a
rough character-based estimate, not provider billing truth, but it is enough to
show whether the next run would be testing reasoning lift or payload bulk.

| Case | Stored packet est. | Arm C view est. | Arm B est. | Arm C est. |
| --- | ---: | ---: | ---: | ---: |
| `multi_offer` | 41,563 | 10,366 | 6,503 | 16,942 |
| `whistleblower` | 43,329 | 9,866 | 7,101 | 17,039 |
| `startup_pivot` | 37,769 | 9,427 | 4,094 | 13,594 |
| `real_estate` | 40,264 | 9,267 | 3,504 | 12,843 |
| `friendship_money` | 41,195 | 9,535 | 4,642 | 14,249 |
| `messy_three_problems` | 36,714 | 9,131 | 5,988 | 15,192 |
| `user_has_plan` | 38,291 | 10,111 | 4,721 | 14,904 |
| `phd_research` | 38,264 | 9,656 | 9,068 | 18,797 |

The initial dry run exposed two blockers: card cap pressure and compression
pressure. The compact decoder-facing packet projection materially reduces the
second blocker. Arm C is no longer 42k-50k estimated tokens; it is now roughly
12.8k-18.8k, while the rich stored packet remains available for audit. The
remaining blocker before interpreting paid output as evidence is cap policy:
every case still reaches 12 cards and suppresses six candidates.

## Architecture Read

The dry run proves the first architectural layer is viable:

- explicit `affordances_v60.json` selection works;
- grouped `reviewed_affordance_cards` are emitted;
- the review-only Markdown renderer now prefers grouped affordance cards when
  present;
- Arm C uses a compact decoder-facing packet view while preserving the full
  packet for audit and ledger validation;
- treatment requirements remain traceable to affordance IDs;
- absence records are present on every card;
- ledger templates validate shape and trace IDs;
- old flat `reviewed_affordance_fields` remains for compatibility;
- live runtime paths are not touched.

The dry run also exposes the next architecture problem: all eight cases hit the
12-card cap with six suppressed candidates. That means any paid replay would be
testing a cap policy as much as a card policy. Before promotion, the lab needs a
clear rule for whether lane precedence, explicit probes, source support, broad
card caps, or packet diversity controls should decide which cards survive.

The compact projection lowers payload risk enough for a small pilot, but it does
not solve selection risk. The first paid replay should be treated as a
cap-policy stress run unless the nomination/cap rule is made explicit first.

## User Read

The user-facing value being tested is not "more analysis." It is whether the
answer becomes sharper in ways a user can feel:

- fewer unsupported claims;
- clearer missing evidence;
- more useful questions;
- better confidence sizing;
- more explicit trade-offs;
- better refusal to force a tempting frame.

The `user_has_plan` and `real_estate` cases are especially important. If Arm C
only makes them longer, the system is failing. A good outcome can reject or
defer most cards and produce a shorter answer.

## Product Read

The first product question is whether grouped v60 cards beat a strong generic
reconsideration prompt. The second product question is stability: can the same
case produce a similar class of useful deltas across reruns, or does the card
ledger churn?

The dry-run result says the next paid run should be small:

- one narrow control;
- one weak/absence-heavy case;
- one high-stakes power/evidence case;
- one messy-context case.

Run these first before spending on the full eight-case slate.

## Monetization Read

If this works, the monetizable unit is not "we used mental models." It is:

- source-backed decision review;
- evidence-threshold audit;
- hidden-edge discovery;
- inspectable reasoning ledger;
- team memo traceability;
- premium review mode for high-stakes decisions.

The buyer is not paying for a longer answer. They are paying for a system that
can say: "Here is what the original reasoning missed, here is why we did or did
not use each source-backed lens, and here is what changed."

Cost control matters. The preflight already shows why:

- every case hit the cap;
- every full packet includes 24 absence records at snippet cap 2;
- compact Arm C remains roughly 12.8k-18.8k estimated tokens before answer
  generation;
- a full N=3, eight-case, two-arm replay would multiply quickly.

Use Grok 4.1 Fast as the cautious generator and Kimi K2.6 as the cautious judge
candidate only after dry-run artifacts are approved. Avoid DeepSeek for the
first controlled replay because prior local evidence showed slow calls and
validation failures.

## Recommendation

Do not run the full paid eight-case replay yet.

Run a four-case paid pilot after one more local pass on cap policy:

1. `user_has_plan` as narrow/no-extra-complexity control.
2. `real_estate` as weak-support/absence probe.
3. `whistleblower` as high-stakes evidence/power case.
4. `messy_three_problems` as context-separation stress.

Promotion remains blocked until Arm C beats Arm B on decision usefulness without
increasing hallucinated facts, cheap rejection, or model-name theater.
