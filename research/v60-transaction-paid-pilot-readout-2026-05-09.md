# V60 Transaction Paid Pilot Readout

Date: 2026-05-09
Branch: `feat/v60-transaction-local-replay-lab`
Status: paid replay evidence; do not promote into live `/lolla`

## What Ran

Clean pilot artifacts:

- `data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot-first-half/summary.json`
- `data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot-remainder/summary.json`

Smoke / operational artifacts:

- `data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot-smoke/summary.json`
- `data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot-smoke-v2/summary.json`
- `data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot/` contains a partial aborted run that exposed malformed JSON handling.

Config:

- Artifact: `data/compiled/model_affordances/affordances_v60.json`
- Packet config: `cap8_focused`
- Generator: `x-ai/grok-4.1-fast`
- Judge: `moonshotai/kimi-k2.6`
- Cases: `user_has_plan`, `real_estate`, `whistleblower`, `messy_three_problems`
- Modes: `edge_audit`, `question_gate`
- Clean pilot calls: 24
- Clean pilot reported cost: `$0.225551`
- Clean pilot tokens: 168,520 input; 60,349 output; 228,869 total

Arm definitions:

- Arm B: strong generic reconsideration prompt in the same product mode.
- Arm C: grouped v60 transaction packet plus ledger requirement in the same product mode.
- Judge comparison was blinded and did not receive the Arm C ledger.

## Headline Result

The paid pilot does not support product promotion yet.

Kimi preferred Arm B over Arm C in 7 of 8 judged items:

| Signal | Count |
| --- | ---: |
| Arm B winner | 7 |
| Arm C winner | 1 |
| Arm B constructive edge | 7 |
| Arm C constructive edge | 1 |
| Arm B missing-evidence discipline | 7 |
| Arm C missing-evidence discipline | 1 |
| C flagged as overburdened | 3 |
| C flagged for model theater | 5 |

By mode:

| Mode | Arm B wins | Arm C wins |
| --- | ---: | ---: |
| `edge_audit` | 3 | 1 |
| `question_gate` | 4 | 0 |

## Item Results

| Item | Ledger | Winner | Constructive Edge | Evidence Discipline | Overburdened | Model Theater |
| --- | --- | --- | --- | --- | --- | --- |
| `user-has-plan__edge_audit` | `valid` | C | C | C | B | B |
| `user-has-plan__question_gate` | `valid` | B | B | B | C | C |
| `real-estate__edge_audit` | `valid` | B | B | B | B | B |
| `real-estate__question_gate` | `invalid` | B | B | B | C | C |
| `whistleblower__edge_audit` | `valid` | B | B | B | neither | neither |
| `whistleblower__question_gate` | `valid_after_summary_repair` | B | B | B | C | C |
| `messy-three-problems__edge_audit` | `valid_after_summary_repair` | B | B | B | neither | C |
| `messy-three-problems__question_gate` | `invalid` | B | B | B | neither | C |

Ledger status:

| Status | Count |
| --- | ---: |
| `valid` | 4 |
| `valid_after_summary_repair` | 2 |
| `invalid` | 2 |

## What Worked

The transport layer worked.

- The runner built Arm B and Arm C packets without touching live `/lolla`.
- Explicit v60 artifact discipline held.
- `cap8_focused` stayed operationally feasible.
- All clean pilot items completed after the harness was patched to continue across provider failures.
- The model usually returned one card transaction per packet card.
- The ledger validator caught real schema failures instead of letting them pass quietly.
- The blinded judge setup worked well enough to reveal C's user-facing weakness.

The best C result was `user-has-plan__edge_audit`. C won because it preserved a useful conditional launch plan and did not invent additional speculative edges. This is an important positive signal: transaction cards can help the model decide not to add visible complexity.

## What Failed

Arm C too often turned the transaction layer into visible process.

Common judge criticisms:

- C leaked substrate/card language into user-facing output.
- C over-explained what it rejected instead of producing a sharper user answer.
- C often used the ledger as proof-of-work rather than as hidden audit trace.
- C sometimes concluded "no substantive changes" even when Arm B found a useful user-facing delta.
- C was often better at accounting than at helping.

This means our current injection prompt is still too close to "perform consideration" and not close enough to "silently metabolize consideration, then help the user."

## Ledger Findings

The ledger is useful, but not ready as-is.

Two failures were mechanically repairable summary mismatches:

- `whistleblower__question_gate`
- `messy-three-problems__edge_audit`

Two failures were substantive schema issues:

- `real-estate__question_gate`: deferred evidence status did not use an allowed deferred evidence enum, and summary counts were wrong.
- `messy-three-problems__question_gate`: effect types were invalid and summary counts were wrong.

Earlier smoke tests exposed another schema issue: Grok confused `effect_type` with `final_answer_visibility`, returning `silent_application` as an effect type. The prompt was tightened before the clean pilot.

Conclusion: keep the validator strict, but allow deterministic summary repair in the harness. Do not relax trace IDs, disposition rules, effect-type enums, or deferred evidence rules.

## Judge Caveat

The judge's `promotion_read` field is not reliable enough for go/no-go decisions. In at least one item, it conflicted with the unblinded winner/rationale. Use the unblinded winner, constructive-edge, missing-evidence, overburdened, model-theater fields, and human inspection instead.

## Product Read

This pilot argues against direct Step 6 answer integration right now.

The likely product surface is narrower:

- Use v60 first as an internal hidden audit ledger, not a visible answer writer.
- Prefer `edge_audit` over `question_gate` for the next C-arm iteration.
- Do not ask the model to explain every card in user-facing prose.
- Add a hard instruction that user-facing output must not mention cards, substrate, model IDs, or ledger logic.
- Treat "C rejects all cards and improves restraint" as a valid outcome, but only if the final user answer is still crisp.

## Architecture Read

The staged architecture is still right:

1. Existing lanes nominate.
2. v60 enriches nominations.
3. The decoder considers cards.
4. The ledger records use/reject/defer.
5. The user sees only distilled reasoning deltas.

The current failure is not selection or transport. It is decoder presentation: C is receiving the right kind of packet but not yet using it in the right product posture.

## Recommendation

Do not merge v60 into live `/lolla`.

Next implementation should be a prompt and product-shape iteration, not broader corpus work:

1. Split Arm C into two outputs: `private_transaction_ledger` and `user_visible_answer`.
2. Forbid user-visible references to cards, substrate, packet, model names, or ledger mechanics.
3. Make the ledger hidden and append-only for Observatory/memo review.
4. Add a "no visible delta" success path: if cards only confirm the answer, produce a shorter answer, not a meta-answer.
5. Retest only `edge_audit` on the same four cases before trying `question_gate` again.
6. Keep `cap8_focused`; do not widen the packet until C beats B on presentation discipline.

The lesson is sharp: v60 transport is viable, but the decoder prompt currently makes the model too aware of the machinery. The next target is not more knowledge. It is better metabolism.
