# V60 Transaction C3 Delta-Audit Readout

Date: 2026-05-09
Status: dormant replay evidence only
Branch: `feat/v60-transaction-local-replay-lab`

## Question

Can v60 grouped affordance cards work better if the LLM is not allowed to write
the final answer?

C3 tested a different architecture from C1/C2:

- Arm B writes the strong generic edge-audit answer.
- Arm C3 receives the v60 grouped packet privately.
- Arm C3 returns only a private ledger plus a bounded
  `delta_candidate_report`.
- A deterministic composer preserves Arm B and adds only accepted public-safe
  deltas.
- The judge sees only the composed public output, not the private packet,
  ledger, or delta report.

This tests the architecture we actually want: private consideration first,
public deltas second, no full-packet final-answer injection.

## What Changed

The paid replay harness now supports:

```bash
--c-variant delta
```

The C3 contract deliberately excludes:

- `final_answer`
- `user_visible_answer`
- `mode_output`
- rewritten prose

Instead it asks for:

- `private_transaction_ledger`
- `delta_candidate_report`

The harness then:

- validates the private ledger;
- validates delta trace shape;
- saves raw C3 output as `arm_c_delta_raw.json`;
- composes public Arm C from Arm B plus accepted deltas;
- strips private trace before judging.

Implementation files:

- `scripts/run_v60_transaction_paid_replay.py`
- `tests/test_v60_transaction_paid_replay.py`

## Test Setup

Final clean C3 evidence:

- Dry run: `data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot-c3-delta-v3-dry-run`
- Paid run: `data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot-c3-delta-v3-edge`

Configuration:

- Artifact: `data/compiled/model_affordances/affordances_v60.json`
- Config: `cap8_focused`
- Mode: `edge_audit`
- Cases: `user_has_plan`, `real_estate`, `whistleblower`, `messy_three_problems`
- Generator: `x-ai/grok-4.1-fast`
- Judge: `moonshotai/kimi-k2.6`

Dry run confirmed:

- 4 items
- 8 cards per item
- 10 suppressed candidates per item
- no final-answer fields in C3 output contract
- delta validation marked `not_run_dry_run`

## Paid Result

Final C3 v3 aggregate:

- Paid calls: 12
- Total tokens: 122,700
- Reported cost: $0.136530
- Judge winners: `{"B": 1, "C": 1, "tie": 2}`
- Delta validation: `{"valid": 4}`
- Ledger validation: `{"invalid": 1, "valid_after_summary_repair": 3}`

Item results:

| Item | Ledger | Delta Report | Accepted Deltas | Winner | Constructive Edge | Evidence Discipline | Overburdened | Model Theater |
| --- | --- | --- | ---: | --- | --- | --- | --- | --- |
| `user-has-plan__edge_audit` | `invalid` | `valid` | 0 | tie | tie | tie | neither | neither |
| `real-estate__edge_audit` | `valid_after_summary_repair` | `valid` | 2 | C | C | B | neither | neither |
| `whistleblower__edge_audit` | `valid_after_summary_repair` | `valid` | 4 | B | B | tie | C | C |
| `messy-three-problems__edge_audit` | `valid_after_summary_repair` | `valid` | 2 | tie | tie | tie | B | tie |

Public mechanism leak check:

- no public leaks of `card`, `substrate`, `packet`, `ledger`,
  `affordance`, `model_id`, `mental model`, or `review machinery` in Arm C.

## Comparison To C1/C2

C1 visible transaction:

- C won 1 of 4 edge-audit cases.
- C often looked like visible model-card theater.

C2 hidden ledger:

- C won 0 of 4 edge-audit cases.
- Public/private boundary improved, but C often copied or collapsed to the old
  answer and returned zero useful edges.

C3 delta-only:

- C won 1, tied 2, lost 1.
- Public/private boundary held.
- Delta reports were valid in all four cases.
- The model no longer directly wrote the final answer.
- The best C result, `real-estate`, produced a genuine option-space expansion:
  premortem buffer stress-test plus auction optionality.

C3 is therefore the first architecture that looks directionally right, but it
still does not clear product promotion.

## What Worked

### 1. Separating Audit From Composition Helped

C3 avoided the worst C2 failure. The model did not write a huge final answer or
copy old full reasoning back into the public field. The deterministic composer
preserved Arm B and only added bounded public deltas.

This is the right architecture family.

### 2. Safe Collapse Works

`user-has-plan` had zero accepted deltas and collapsed to the baseline public
answer. The judge returned tie rather than penalizing C for forced complexity.

That is good product behavior. A substrate pass should be allowed to say:

> nothing worth adding.

### 3. C3 Can Produce Real Edges

`real-estate` was the strongest positive result. C3 added:

- a premortem stress-test around a missed $30K issue in a 1940s house;
- a post-deadline / escalation-clause optionality path in a six-offer auction.

The judge preferred C because those deltas expanded the user's decision space
beyond the original raise/walk frame.

### 4. Public Machinery Stayed Hidden

C3 did not leak the private packet/ledger/card language into public fields.
That is a meaningful improvement over C1.

### 5. Delta Shape Validation Is Useful

All four C3 `delta_candidate_report` payloads validated. That means the
accepted deltas were traceable to packet cards and did not leak private
mechanism language.

## What Failed

### 1. Ledger Compliance Is Still Not Reliable Enough

Ledger validation did not clear the promotion bar:

- 3 cases required deterministic summary repair.
- 1 case was invalid because Grok emitted invalid evidence status values and
  wrong no-effect counts.

This is a shape problem, not a product-meaning problem, but shape matters. The
ledger is the audit trail. Runtime cannot depend on ledgers that drift on enums
or summaries.

### 2. Delta Validity Is Not Delta Quality

The delta validator can catch trace and private-language failures. It cannot
decide whether a public delta is actually worth showing.

`whistleblower` demonstrates the gap. C3 returned valid deltas, but the judge
penalized C for model theater and overburdening. The additions were structurally
valid but too abstract:

- payoff maps;
- leverage maps;
- principal/agent diagnostics;
- explicit decision-tree mechanics.

Those are exactly the kinds of internal reasoning tools that should be
metabolized, not surfaced.

### 3. The Composer Needs A Quality Gate

The deterministic composer currently applies every accepted public delta. That
is too trusting. C3 needs a second gate before public composition:

- cap public deltas;
- prefer direct user moves over analytical labels;
- reject framework-shaped public copy;
- prefer evidence gates over abstract reframes;
- avoid adding deltas when Arm B already captured the edge cleanly.

### 4. The Promotion Bar Was Not Fully Met

The original C3 promotion bar was:

- C beats or ties B on at least 3 of 4 edge-audit cases;
- public C contains grounded edges/evidence gates when it wins;
- all ledgers are `valid` or `valid_after_summary_repair`;
- no private mechanism leaks;
- no full-answer copy-back.

C3 v3 met:

- C/tie on 3 of 4 cases;
- grounded edge when C won;
- no private mechanism leaks;
- no full-answer copy-back;
- valid delta reports in all cases.

C3 v3 failed:

- ledger validity on all cases;
- model-theater discipline on `whistleblower`;
- consistent public-delta usefulness.

So this is a partial pass for architecture direction, not a product pass.

## Architectural Read

C3 validates the staged direction:

1. Existing lanes nominate.
2. v60 enriches nominations.
3. Private audit considers grouped cards and absences.
4. Private audit returns bounded deltas, deferrals, rejections, and risk notes.
5. Deterministic code validates trace shape.
6. Public composer applies only surviving deltas.
7. If no delta survives, keep Arm B.

But C3 also shows that step 6 needs a stricter gate. "Accepted by the audit
LLM" is not the same as "should reach the user."

The deterministic layer probably needs a public-delta admission contract:

- max 1-2 public deltas;
- each delta must be phrased as a user move, evidence gate, or concrete risk;
- no public analytical-framework labels;
- no "map", "principal", "agent", "payoff", or similar internal-analysis
  phrasing unless the user's own case language requires it;
- no accepted delta if Arm B already has the same edge;
- public deltas must include exact case grounding or missing evidence.

This keeps the LLM free in conclusion but not free from consideration, while
also preventing the private reasoning layer from spilling into product copy.

## Product Read

C3 is the first version that resembles a product:

- the user does not see mental-model machinery;
- the answer does not balloon by default;
- no-delta collapse is possible;
- strong cases can receive a sharper edge audit.

But it should still be treated as premium/offline decision-audit tooling, not
default runtime chat.

The likely product surface is:

- a normal answer;
- then, optionally, "Edges worth checking" with 1-2 concise items;
- each item is a concrete move, caveat, or evidence gate;
- no source/card language;
- no private ledger in user UI.

The private ledger is valuable for QA, review, and future Observatory-style
diagnostics, not for user-facing explanation.

## Monetization Read

C3 cost is in the same general band as C2:

- 12 calls for 4 cases;
- 122,700 total tokens;
- $0.136530 reported cost;
- noticeable latency.

This is not a free default-path feature. It makes more sense as:

- paid decision audit;
- high-stakes edge review;
- premium "second pass";
- enterprise/internal audit artifact;
- optional workflow after a strong answer, not before every answer.

## Decision

Do not promote C3 into live `/lolla`.

Do keep and merge the dormant C3 lab machinery after branch curation:

- C3 variant;
- deterministic composer;
- delta report validator;
- tests;
- dry-run/paid replay reports.

C3 gives enough signal to continue in this direction. It does not give enough
signal to attach v60 to product runtime.

## Next Test

Run C3.5: delta-only audit plus public-delta quality gate.

Changes:

- cap public deltas at 2;
- require each accepted public delta to be one of:
  - `evidence_gate`;
  - `concrete_next_move`;
  - `risk_caveat`;
  - `option_space_expansion`;
- reject public deltas that are primarily analytical-framework descriptions;
- require `public_delta_text` to be directly user-actionable;
- require exact case quote or explicit missing evidence;
- make invalid ledger enum drift a hard failure in the run summary;
- keep no-delta collapse.

Promotion bar for C3.5:

- no invalid ledgers;
- C beats or ties B on at least 3 of 4 cases;
- C wins at least 2 of 4 or produces no user-facing regression;
- no model-theater flags for C;
- no private mechanism leaks;
- no answer copy-back;
- human review confirms deltas are not merely decorative.

The lesson is encouraging but sober: C3 is the right architecture shape, but
the public delta gate is now the bottleneck.
