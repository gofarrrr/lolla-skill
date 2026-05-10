# V60 Transaction C2 Hidden-Ledger Readout

Date: 2026-05-09
Status: dormant replay evidence only
Branch: `feat/v60-transaction-local-replay-lab`

## Question

Can v60 grouped affordance cards be injected as private audit material, with a
required transaction ledger, while keeping the user-facing answer free from
model theater and improving practical decision quality?

This was a direct follow-up to the first paid pilot, where the visible
transaction contract made Arm C look too much like a mental-model exercise. C2
tested the opposite presentation: the packet and ledger are hidden, and only the
public answer and public edges are shown to the judge.

## What Changed

The paid replay harness now supports `--c-variant hidden`.

For Arm C, the hidden variant asks the model to return:

- `private_transaction_ledger`
- `private_delta_notes`
- `user_visible_answer`
- `user_visible_edges`
- mirrored public fields: `final_answer` and `edge_findings`

The blinded judge receives only the sanitized public surface. The private
ledger, packet IDs, ledger fields, and delta notes are stripped before judging.
The validator still checks the private ledger against the deterministic packet
card IDs and affordance IDs.

Files touched for this test:

- `scripts/run_v60_transaction_paid_replay.py`
- `tests/test_v60_transaction_paid_replay.py`

## Test Setup

Replay output:

- Dry run: `data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot-c2-hidden-dry-run`
- Paid run: `data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot-c2-hidden-edge`

Configuration:

- Artifact: `data/compiled/model_affordances/affordances_v60.json`
- Config: `cap8_focused`
- Mode: `edge_audit`
- Cases: `user_has_plan`, `real_estate`, `whistleblower`, `messy_three_problems`
- Generator: `x-ai/grok-4.1-fast`
- Judge: `moonshotai/kimi-k2.6`
- Arm B: no v60 transaction packet
- Arm C2: hidden v60 grouped cards plus private ledger

Dry run confirmed:

- 4 items
- 8 cards per item
- 10 suppressed candidates per item
- hidden output contract present
- no paid calls in dry run

## Paid Results

Aggregate:

- Paid calls: 12
- Total tokens: 130,534
- Reported cost: $0.134486
- Judge winner counts: `{"B": 4}`
- Ledger validation: `{"valid": 1, "valid_after_summary_repair": 1, "invalid": 2}`

Item results:

| Item | C2 Ledger | Winner | Constructive Edge | Missing Evidence | Overburdened | Model Theater |
| --- | --- | --- | --- | --- | --- | --- |
| `user-has-plan__edge_audit` | `valid` | B | B | B | C | C |
| `real-estate__edge_audit` | `invalid` | B | B | B | C | B |
| `whistleblower__edge_audit` | `valid_after_summary_repair` | B | B | B | C | C |
| `messy-three-problems__edge_audit` | `invalid` | B | B | B | neither | neither |

Compared with C1 transaction-visible edge-audit results:

- C1 visible transaction: C won 1 of 4 edge-audit cases.
- C2 hidden transaction: C won 0 of 4 edge-audit cases.

So hidden presentation did not rescue the approach. It removed some public
machinery, but it also made the substrate easier for the model to dismiss or
collapse into no visible change.

## What Worked

The transport layer works better than the product behavior.

The system can now:

- build grouped v60 card packets from explicit nominations;
- include per-card affordance identity rather than only pooled model fields;
- keep the old flat field for compatibility;
- pass a private ledger schema to the model;
- validate private ledgers against deterministic packet IDs and affordance IDs;
- strip private transaction trace before judging;
- keep packet execution outside live `/lolla`.

The public/private boundary mostly held. Searching the public Arm C fields for
private mechanism terms such as `substrate`, `packet`, `ledger`, `affordance`,
`model_id`, and `mental model` found no public leaks.

This matters. The experiment proves that we can transport curated cognition
privately. The blocker is not "can we deliver v60 cards?" The blocker is "does
the receiving model perform the right kind of reconsideration?"

## What Failed

C2 did not create useful user-facing deltas.

The most important failure pattern:

- C2 frequently decided that the cards added no concrete delta.
- C2 often returned the vanilla synthesized position or the old full reasoning.
- C2 returned zero `edge_findings` in all four cases.
- Arm B was shorter, more decisive, and more useful in all four judged cases.

Public answer size shows the failure:

| Item | Arm B Final Answer Chars | Arm C2 Final Answer Chars | Arm C2 Edge Count |
| --- | ---: | ---: | ---: |
| `user-has-plan__edge_audit` | 352 | 567 | 0 |
| `real-estate__edge_audit` | 599 | 5,226 | 0 |
| `whistleblower__edge_audit` | 754 | 14,354 | 0 |
| `messy-three-problems__edge_audit` | 756 | 414 | 0 |

The hidden ledger protected the user from explicit model-card theater, but it
did not protect the answer from audit-pass inertia. In several cases, C2 treated
the packet as something to account for privately and then returned essentially
the original answer, sometimes with full reasoning copied back into the public
field.

## Ledger Failure Modes

Ledger compliance remains brittle with Grok in this shape.

Observed validation statuses:

- `valid`: 1
- `valid_after_summary_repair`: 1
- `invalid`: 2

Specific invalid cases:

- `real-estate`: used `wrong_object` as `grounding_check.evidence_status`
  instead of an allowed evidence status.
- `messy-three-problems`: used `silent_application` as `effect_type` instead of
  using it only as `final_answer_visibility`.

There was also semantic contradiction:

- Some ledgers marked cards as `used` with direct deltas.
- `private_delta_notes.changed` was still empty.
- The public answer often did not reflect the claimed ledger deltas.

That means shape validation is necessary but not sufficient. We need a trace
consistency check between transaction dispositions, delta notes, and public
output.

## Interpretation

This test falsifies a tempting architecture:

> Give the LLM the full grouped packet, hide the ledger from the user, and ask it
> to produce the final answer.

That is not enough.

The model can satisfy the private accounting ritual while failing the product
job. It may say "no visible delta" too cheaply, or it may claim private deltas
without actually producing a better public answer. This is exactly the problem
the handover warned about in another form: freedom of conclusion is good, but
not freedom from consideration. C2 created consideration theater in private.

The deterministic layer should not merely inject more cognition into the final
answer prompt. It needs to structure the transaction as a bounded intermediate
step.

## Architectural Read

The v60 layer should be a post-lane private critique and delta generator, not a
direct final-answer writer.

Recommended staged architecture:

1. Existing lanes nominate candidate model IDs with provenance.
2. Deterministic builder enriches nominations from explicit `affordances_v60.json`.
3. Private reconsideration pass reviews grouped cards and absences.
4. The pass returns only bounded deltas:
   - accepted public deltas;
   - deferred evidence questions;
   - rejected cards with reasons;
   - risk warnings;
   - no full rewritten answer.
5. Deterministic validator checks:
   - one transaction per card;
   - allowed enums;
   - card and affordance IDs;
   - summary counts;
   - claimed delta consistency.
6. A separate composer applies only accepted public deltas to the vanilla answer.
7. If the private pass produces no accepted delta, the system keeps the Arm B
   answer rather than forcing a substrate-shaped rewrite.

This is different from lanes. Lanes discover and nominate. The v60 transaction
layer audits and proposes deltas after nomination. The final product should see
only accepted public deltas, not the full cognitive source machinery.

## Product Read

The user should not see "we used these mental models."

The user should experience:

- a sharper answer;
- a few non-obvious edges;
- missing evidence that matters;
- confidence sizing;
- optional "why this might be wrong" when useful.

The product promise is not model usage. The product promise is better judgment
under ambiguity. This argues for packaging the feature as an invisible reasoning
audit or premium decision review, not as a visible mental-model panel.

## Monetization Read

The replay shows this should not be a default cheap chat feature yet.

Costs and latency are acceptable for premium/high-stakes moments, but not for
every turn:

- 12 calls for 4 cases;
- 130,534 total tokens;
- $0.134486 reported cost;
- noticeable latency, especially on larger C2 prompts and Kimi judge calls.

Better monetization shape:

- premium "decision audit" runs on demand;
- saved audit artifact for high-stakes decisions;
- user-facing deliverable is an edge brief, not a transcript rewrite;
- private ledger is retained for QA/evaluation, not exposed as product copy;
- future enterprise workflows can use the ledger for compliance/debugging.

## Decision

Do not promote C2 hidden-ledger injection into live `/lolla`.

Do not merge the idea as "full v60 packet goes into final answer prompt."

Keep the packet builder, card identity, sanitizer, and ledger validator. Treat
this run as evidence that the next experiment must split reconsideration from
composition.

## Next Test

Run C3 as a delta-only private audit:

- Arm C3 receives the grouped packet.
- It does not write `final_answer`.
- It returns a compact `delta_candidate_report`.
- It must choose between:
  - `accept_delta`;
  - `defer_question`;
  - `reject_card`;
  - `no_delta`.
- It cannot copy the original answer.
- A deterministic composer then produces the public answer from Arm B plus
  accepted deltas.
- If there are no accepted deltas, the public answer remains Arm B.

Promotion bar for C3:

- C must beat or tie B on at least 3 of 4 edge-audit cases.
- Public C must contain at least one grounded edge or evidence gate when the
  judge rewards C.
- Ledger validity must be `valid` or `valid_after_summary_repair` on all cases.
- No public private-mechanism leaks.
- No full-answer copy-back.

This keeps the original philosophy intact: the LLM has freedom of conclusion,
but not freedom from consideration. The deterministic system should force a
bounded audit transaction, then let only useful deltas reach the user.
