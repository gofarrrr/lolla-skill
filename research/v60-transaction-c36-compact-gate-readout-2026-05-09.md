# V60 Transaction C3.6 Compact-Gate Readout

Date: 2026-05-09
Status: dormant replay evidence only
Branch: `feat/v60-transaction-local-replay-lab`

## Question

Can the C3/C3.5 architecture improve user-visible output if the deterministic
composer enforces a stricter density budget?

C3.5 proved that a public gate can stop bad mental-model deltas from reaching
the user, but it also reduced product lift. C3.6 tests a narrower policy:

- at most one public addition total;
- prefer evidence gates and concrete next moves;
- drop missing `case_quote` before composition;
- drop analytical-framework language;
- drop duplicate-of-baseline public additions;
- collapse to Arm B when no useful public addition survives.

The product hypothesis is:

> v60 should not make the answer "more sophisticated"; it should add one
> sharper missing move or evidence check, or stay silent.

## What Changed

The paid replay harness now supports:

```bash
--c-variant delta_compact
```

Implementation:

- `scripts/run_v60_transaction_paid_replay.py`
- `tests/test_v60_transaction_paid_replay.py`

New C3.6 behavior:

- `delta_compact` keeps the C3 private-audit shape.
- The LLM still returns a private ledger plus `delta_candidate_report`.
- The deterministic composer applies policy `c3_6_compact`.
- The gate ranks public additions by usefulness:
  - evidence gates first;
  - concrete next moves second;
  - risk caveats third;
  - option-space expansion last.
- Only the highest-ranked surviving public addition can reach the judged
  output.
- Missing `case_quote` is a drop reason, not only a validator error.
- Stricter duplicate checks compare both the whole delta and the actual
  `public_delta_text` against the baseline output.

## Verification

Commands run:

```bash
python3 -m py_compile scripts/run_v60_transaction_paid_replay.py tests/test_v60_transaction_paid_replay.py
env PYTHONPATH=. pytest tests/test_v60_transaction_paid_replay.py -q
env PYTHONPATH=. pytest tests/test_v60_transaction_paid_replay.py tests/test_v60_transaction_replay_matrix.py tests/test_v60_transaction_replay_lab.py tests/test_card_transaction_ledger.py tests/test_reasoning_substrate_packet.py tests/test_reasoning_substrate_packet_review_render.py
```

Result:

- focused paid-replay tests: 22 passed;
- broader dormant replay/packet/ledger suite: 43 passed.

Dry run:

- Path: `data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot-c36-compact-all-dry-run`
- Cases: all 8 manifest cases, `edge_audit`
- Result: 8/8 dry-run prompt packets written.

Dry-run packet quality:

| Item | Cards | Absence Records | Weak Support | Medium Confidence |
| --- | ---: | ---: | ---: | ---: |
| `multi-offer__edge_audit` | 13 | 16 | 0 | 1 |
| `whistleblower__edge_audit` | 14 | 16 | 0 | 1 |
| `startup-pivot__edge_audit` | 11 | 16 | 0 | 0 |
| `real-estate__edge_audit` | 14 | 16 | 2 | 2 |
| `friendship-money__edge_audit` | 13 | 16 | 0 | 0 |
| `messy-three-problems__edge_audit` | 11 | 16 | 0 | 0 |
| `user-has-plan__edge_audit` | 11 | 16 | 0 | 0 |
| `phd-research__edge_audit` | 10 | 16 | 0 | 0 |

The dry run confirmed that `real-estate` is the only current paid-manifest case
with weak-support affordances in the packet. Every case carried absence rails
at the packet cap.

## Paid Replay

Path:

- `data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot-c36-compact-edge-all`

Configuration:

- Artifact: `data/compiled/model_affordances/affordances_v60.json`
- Config: `cap8_focused`
- Mode: `edge_audit`
- Cases: all 8 manifest cases
- Generator: `x-ai/grok-4.1-fast`
- Judge: `moonshotai/kimi-k2.6`
- C variant: `delta_compact`

Aggregate:

- Paid calls: 24
- Total tokens: 256,609
- Reported cost: $0.308291
- Judge winners: `{"C": 2, "tie": 6}`
- Ledger validation: `{"invalid": 1, "valid": 2, "valid_after_summary_repair": 5}`
- Raw delta validation: `{"invalid": 4, "valid": 4}`
- Public mechanism leaks: 0/8
- C overburden flags: 0/8
- C model-theater flags: 1/8

Public gate aggregate:

- Gate-enabled items: 8
- Raw accepted deltas: 8
- Public accepted deltas kept: 3
- Collapses to Arm B: 5
- Dropped public deltas: 5
- Drop reasons:
  - `not_directly_user_actionable`: 3
  - `analytical_framework_language`: 1
  - `invalid_or_missing_delta_type`: 1

Item results:

| Item | Winner | Ledger | Raw Delta | Public Kept | Raw Deltas | Dropped | Collapse |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| `multi-offer__edge_audit` | tie | `valid` | `invalid` | 0 | 1 | 1 | yes |
| `whistleblower__edge_audit` | tie | `invalid` | `valid` | 0 | 0 | 0 | yes |
| `startup-pivot__edge_audit` | tie | `valid` | `invalid` | 0 | 2 | 2 | yes |
| `real-estate__edge_audit` | C | `valid_after_summary_repair` | `invalid` | 1 | 2 | 1 | no |
| `friendship-money__edge_audit` | tie | `valid_after_summary_repair` | `invalid` | 0 | 1 | 1 | yes |
| `messy-three-problems__edge_audit` | C | `valid_after_summary_repair` | `valid` | 1 | 1 | 0 | no |
| `user-has-plan__edge_audit` | tie | `valid_after_summary_repair` | `valid` | 0 | 0 | 0 | yes |
| `phd-research__edge_audit` | tie | `valid_after_summary_repair` | `valid` | 1 | 1 | 0 | no |

Original-four comparison:

| Variant | Original Four Result |
| --- | --- |
| C3.5 | `{"B": 2, "tie": 2}` |
| C3.6 | `{"C": 2, "tie": 2}` |

This is the first replay where the original four-case set has no B wins and
two C wins.

## What Worked

### 1. The One-Delta Budget Helped

C3.6 kept only three public additions across eight cases. That is the right
density. The gate allowed C to improve when it had a concrete missing move and
collapsed when it did not.

The five collapses were productive, not failures:

- `multi-offer`: dropped a BATNA delta that was not directly user-actionable;
- `whistleblower`: proposed no public delta and tied safely;
- `startup-pivot`: dropped one framework-shaped and one non-actionable delta;
- `friendship-money`: dropped an invalid `delta_type`;
- `user-has-plan`: proposed no public delta and tied safely.

### 2. Real Estate Became The Clean Weak-Support Win

`real-estate` was the only paid-manifest case with weak-support affordances in
the packet. C3.6 kept one premortem-style stress test and dropped the weaker
optionality delta.

Kept public delta:

> Before committing, assume the $120K repair estimate balloons to $160K from a
> missed issue like a failing boiler, and walk through your exact response.

The judge preferred C because this converted generic old-house risk into a
concrete decision rehearsal. This is the shape we want: v60 did not name a
mental model; it forced a better user move.

### 3. Messy Three Problems Became A Clean Evidence-Gate Win

`messy-three-problems` kept one WYSIATI-style evidence gate:

> Before finalizing Seattle, confirm brother's willingness to step up on mom's
> care and schedule her cognitive evaluation.

The judge preferred C for making the care gap explicit and testable. This is
also the target shape: an absence rail became a concrete missing-evidence gate.

### 4. User-Has-Plan Collapsed Correctly

`user-has-plan` proposed zero deltas and tied. This remains important. A good
reasoning-substrate layer must be allowed to say:

> the baseline already handled this.

### 5. Public/Private Boundary Held

Public leak check found 0/8 leaks for:

- card;
- substrate;
- packet;
- ledger;
- affordance;
- model ID;
- mental model;
- review machinery.

This remains one of the strongest signs that the staged architecture is right.

### 6. Overburden Improved

C3.5 had overburden flags in two of four cases. C3.6 had zero overburden flags
across eight cases.

That is a product-significant result. The one-delta budget seems to reduce the
main UX failure mode.

## What Failed

### 1. Raw Delta Compliance Is Still Not Good Enough

Raw delta validation was only 4/8 valid.

Main causes:

- more than one public addition despite the compact instruction;
- analytical-framework-shaped text;
- non-actionable public text;
- invalid `delta_type`.

The deterministic gate salvaged the public output, but the private report is
not yet reliable enough for runtime auditability.

### 2. Ledger Compliance Is Still Weak

Ledger validation:

- `valid`: 2
- `valid_after_summary_repair`: 5
- `invalid`: 1

The invalid case was `whistleblower`: the model marked several transactions
`used` while giving no `final_answer_delta`, then the summary no-effect count
did not reconcile.

This is a ledger-shape problem, not a public-output problem, but it blocks
runtime promotion.

### 3. C3.6 Still Has One Theater Flag

`messy-three-problems` won, but the judge marked model theater on C because one
added edge phrase was a little too audit-shaped:

> Audit prevents overconfidence from partial story.

The useful part was the concrete evidence gate. The phrasing should be
metabolized further before product use.

### 4. Expanded Set Shows Many Ties Are Collapse Ties

Six of eight cases tied. Several ties were byte-for-byte identical after
collapse. This is safe, but it means the value story is not "always better."

The value story is narrower:

> when there is a surviving evidence gate or concrete decision rehearsal, C3.6
> can improve the answer without overburdening it.

That is good, but it is not enough for live `/lolla`.

## Architectural Read

C3.6 is the strongest architecture so far.

The staged system is now behaving more like a reasoning transport layer:

1. deterministic lanes nominate;
2. v60 enriches candidate cards and absence rails;
3. the LLM privately considers the cards;
4. the LLM proposes possible deltas;
5. deterministic code rejects bad or duplicate deltas;
6. the composer adds at most one public improvement;
7. if nothing survives, Arm C collapses to Arm B.

This is very close to the product philosophy:

> freedom of conclusion, not freedom from consideration.

The LLM is not forced to use cards. It can reject or defer them. But it also
cannot cheaply turn curated cognition into public theater.

## Product Read

C3.6 changes the product read from "maybe too much" to "possibly useful if very
sparse."

The user-visible target should be:

- one missing evidence gate;
- one concrete decision rehearsal;
- one next move that changes the user's decision quality;
- or no visible change.

The target should not be:

- a more elaborate answer;
- visible mental-model language;
- multiple clever edges;
- a full rewrite from the substrate pass.

C3.6 supports a product surface like:

> Edge check: one additional question or stress test survived review.

Not:

> We applied mental models to your problem.

## Monetization Read

C3.6 makes monetization more plausible because the value is not bulk content.

A premium feature could be framed as:

- "Blind-spot check";
- "Decision edge audit";
- "One surviving stress test";
- "Missing evidence gate."

The monetizable unit is not tokens or mental-model display. It is the rare,
high-signal intervention that prevents a bad decision:

- "What happens if the $120K repair estimate becomes $160K?"
- "Can your brother actually step up before you move?"
- "What exact observation will make you pivot back?"

The current evidence supports charging for a review layer eventually, but only
after ledger/raw compliance improves. Product trust requires auditability.

## Recommendation

Do not attach C3.6 to live `/lolla`.

Do keep C3.6 as the lead dormant transaction architecture candidate.

This run is strong enough to justify a merge of the dormant lab work after
review, but not a runtime integration. The code path remains explicit,
off-by-default, and artifact-path driven.

Before runtime consideration:

1. Fix ledger discipline for zero-delta cases:
   - if no public delta, used transactions must not claim visible effect;
   - `no_effect_count` must reconcile;
   - summary repair should not be relied on as the normal path.
2. Add post-gate public validation separately from raw delta validation.
   - raw invalid can be acceptable in replay if the public gate dropped the bad
     output;
   - product metrics should report both.
3. Tighten C3.6 public phrasing:
   - no "audit prevents" or other review-shaped public text;
   - public additions should be direct user language only.
4. Retest the same eight cases.
5. Add a case that directly nominates the known weak-support records
   `devops-and-continuous-integration` or `price-discrimination`, because the
   current manifest only tests weak support indirectly through `real-estate`.

Promotion bar for the next iteration:

- no public private-mechanism leaks;
- no overburden flags;
- no C model-theater flags;
- all ledgers `valid` or deterministically repairable with explainable summary
  repair;
- post-gate public outputs valid 8/8;
- original four stay at least `{"C": 2, "tie": 2}`;
- expanded eight stay at least C/tie 8/8 with at least two genuine C wins.

## Bottom Line

C3.6 is the best result so far.

It preserves safety, removes overburden, and produces two genuine C wins in the
original four-case set while tying everywhere else. The architecture is now
plausibly right for a dormant lab merge.

It is still not runtime-ready because raw delta and ledger compliance are not
stable enough. The next bottleneck is no longer "can v60 help?" The next
bottleneck is "can the audit trail be reliable enough to trust the help?"
