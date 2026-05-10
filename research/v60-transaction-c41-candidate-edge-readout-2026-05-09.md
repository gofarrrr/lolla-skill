# V60 Transaction C4.1 Candidate-Edge Readout

Date: 2026-05-09
Status: dormant replay evidence only
Branch: `feat/v60-transaction-local-replay-lab`

## Plain-English Summary

C4.1 tested the lesson from C4:

> The model should not decide too early that the baseline is good enough. It
> should identify the strongest plausible underweighted edge. Deterministic code
> should decide whether that edge reaches the user.

This worked directionally.

C4.1 restored candidate pressure without returning to model-written ledgers:

- C4 raw candidate edges: 1/8
- C4.1 raw candidate edges: 6/8
- C4 public kept edges: 0/8
- C4.1 public kept edges: 2/8 in the primary corrected run
- C4 ledger validation: 8/8 valid
- C4.1 ledger validation: 8/8 valid

But C4.1 is not ready for product/runtime. It exposed two next bottlenecks:

- the model still sometimes omits `one_edge_report`;
- the deterministic public gate is too crude, especially around
  `option_space_expansion` actionability.

The best conclusion is:

> C4.1 is the right architecture direction, but not yet the final admission
> policy.

## What Changed

The paid replay harness now supports:

```bash
--c-variant candidate_edge
```

Implementation:

- `scripts/run_v60_transaction_paid_replay.py`
- `tests/test_v60_transaction_paid_replay.py`

C4.1 keeps the C4 accountability model:

- the model does not write `private_transaction_ledger`;
- the model returns a lightweight `private_consideration_trace`;
- deterministic code builds the formal transaction ledger;
- deterministic code gates the public output.

C4.1 changes the model-facing report:

```json
{
  "one_edge_report": {
    "best_candidate_edge": {
      "delta_type": "evidence_gate | concrete_next_move | risk_caveat | option_space_expansion",
      "source_card_ids": ["..."],
      "affordance_ids": ["..."],
      "case_quote": "exact case substring",
      "public_delta_text": "one concise user-useful sentence",
      "why_this_changes_the_decision": "decision consequence",
      "confidence": "low | medium | high",
      "admission_risk": "why this edge may still be weak"
    },
    "recommend_public_admission": true,
    "admission_rationale": "private rationale"
  }
}
```

The important design move:

> `recommend_public_admission` is advisory. The deterministic gate owns public
> admission.

## Evaluator Fix

During the first C4.1 run, a judge selected Arm C in a case where the public
Arm B and Arm C outputs were identical after sanitization. That was pure judge
noise.

I added a deterministic tie guard:

- if the sanitized public outputs are identical;
- skip the paid judge call;
- record `deterministic_identical_output_tie`.

This is now part of the harness and covered by tests. This matters because no
substrate architecture should get credit for a C win when no public delta
exists.

## Verification

Commands run:

```bash
python3 -m py_compile scripts/run_v60_transaction_paid_replay.py tests/test_v60_transaction_paid_replay.py
env PYTHONPATH=. pytest tests/test_v60_transaction_paid_replay.py -q
env PYTHONPATH=. pytest tests/test_v60_transaction_paid_replay.py tests/test_v60_transaction_replay_matrix.py tests/test_v60_transaction_replay_lab.py tests/test_card_transaction_ledger.py tests/test_reasoning_substrate_packet.py tests/test_reasoning_substrate_packet_review_render.py
```

Result:

- focused paid-replay tests: 28 passed;
- broader dormant replay/packet/ledger suite: 49 passed.

## Dry Run

Path:

- `data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot-c41-candidate-edge-all-dry-run`

Configuration:

- Artifact: `data/compiled/model_affordances/affordances_v60.json`
- Config: `cap8_focused`
- Mode: `edge_audit`
- Cases: all 8 manifest cases
- C variant: `candidate_edge`

Dry-run result:

- 8/8 prompt packets written.
- Prompt contains `C4.1 candidate-edge transaction discipline`.
- Prompt does not ask the model to produce a formal transaction ledger.

Dry-run packet quality:

| Item | C Prompt Tokens | Packet Tokens | Cards | Absence Records | Weak Support | Medium Confidence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `multi-offer__edge_audit` | 14,379 | 7,183 | 13 | 16 | 0 | 1 |
| `whistleblower__edge_audit` | 15,069 | 7,276 | 14 | 16 | 0 | 1 |
| `startup-pivot__edge_audit` | 11,689 | 6,902 | 11 | 16 | 0 | 0 |
| `real-estate__edge_audit` | 10,860 | 6,664 | 14 | 16 | 2 | 2 |
| `friendship-money__edge_audit` | 12,043 | 6,708 | 13 | 16 | 0 | 0 |
| `messy-three-problems__edge_audit` | 13,225 | 6,544 | 11 | 16 | 0 | 0 |
| `user-has-plan__edge_audit` | 12,301 | 6,887 | 11 | 16 | 0 | 0 |
| `phd-research__edge_audit` | 16,488 | 6,727 | 10 | 16 | 0 | 0 |

C4.1 adds only about 54-55 C-arm prompt tokens per case versus C4. It remains
much lighter than the older model-written ledger variants.

## Paid Runs

Primary corrected run:

- `data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot-c41-candidate-edge-edge-all-tieguard`

Supporting runs:

- first pre-tie-guard C4.1 run:
  `data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot-c41-candidate-edge-edge-all`
- targeted `phd-research` rerun:
  `data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot-c41-candidate-edge-phd-rerun`
- targeted `whistleblower` tie-guard rerun:
  `data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot-c41-candidate-edge-whistleblower-tieguard-rerun`

The corrected run is the primary result because it includes the deterministic
identical-output tie guard.

## Primary Corrected Result

Aggregate:

- Paid calls recorded: 17
- Total tokens: 157,293
- Reported cost: $0.051309
- Judge winners: `{"C": 1, "tie": 6}` plus one judge timeout
- Ledger validation: `{"valid": 8}`
- Delta validation: `{"valid": 2, "invalid": 4, "missing_one_edge_report": 2}`
- Gate-enabled items: 8
- Raw accepted candidate edges: 6
- Public accepted edges kept: 2
- Collapses to Arm B: 6
- Dropped public deltas: 4
- Drop reasons: `{"not_directly_user_actionable": 4}`

Item results:

| Item | Status | Judge | Ledger | Candidate Report | Raw Candidate | Public Kept | Collapse | Notes |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
| `multi-offer__edge_audit` | ok | tie | valid | present | 1 | 0 | yes | dropped as not directly actionable |
| `whistleblower__edge_audit` | judge timeout | unjudged | valid | present | 1 | 1 | no | candidate admitted; judge timed out |
| `startup-pivot__edge_audit` | ok | tie | valid | present | 1 | 0 | yes | dropped as not directly actionable |
| `real-estate__edge_audit` | ok | tie | valid | present | 1 | 0 | yes | dropped as not directly actionable |
| `friendship-money__edge_audit` | ok | tie | valid | missing | 0 | 0 | yes | deterministic tie |
| `messy-three-problems__edge_audit` | ok | C | valid | present | 1 | 1 | no | clean C win |
| `user-has-plan__edge_audit` | ok | tie | valid | present | 1 | 0 | yes | model recommended false; gate dropped |
| `phd-research__edge_audit` | ok | tie | valid | missing | 0 | 0 | yes | deterministic tie |

## Clean C Win

`messy-three-problems__edge_audit` is the cleanest C4.1 success.

Kept public delta:

> Before the boyfriend talk, checklist: (1) List 3 specific logistics he'll need
> to address (job quit timeline, Seattle housing plan, family visits); (2)
> Define pass/fail (concrete dates/names vs. vagueness); (3) Schedule follow-up
> if needed.

Why it matters:

> Turns vague "have the talk" into executable steps that prevent omission
> failures and ensure real information gain for Seattle yes/no.

Judge result:

- winner: C
- constructive edge: C
- missing evidence discipline: tie
- model theater: neither
- overburdened: neither
- promotion read: promote

This is the target product shape. The user does not see "checklists" or
substrate language. They get a sharper move.

## Useful But Unjudged Candidate

`whistleblower__edge_audit` generated and admitted a public candidate edge in
the corrected full run, but the judge timed out.

Candidate:

> No documentation exists yet, so prioritize securing a timestamped personal
> record tonight before any attorney consultation to establish your witness
> credibility.

This looks product-useful, but the candidate has a problem: the supplied
`case_quote` was `[MODIFIED/SITUATIONAL] No documentation of incident yet`,
which is not an exact case substring. The current validator only checks that a
quote exists; it does not yet verify exact containment in the case text.

That is an important C4.2 requirement.

The targeted whistleblower rerun did not reproduce the candidate. It omitted
`one_edge_report` and collapsed to a deterministic tie. That tells us the
contract is still not stable enough.

## Supporting PHD Rerun

The primary corrected run omitted `one_edge_report` for `phd-research`.

A targeted rerun did produce a valid accepted edge and a C win:

- judge winner: C
- ledger validation: valid
- delta validation: valid
- public kept edge: 1

The judge liked the early-reversal checkpoint: if collaboration fails after
advisor buy-in, pivot to public datasets with a short novelty-search checkpoint
instead of locking into the single-cell path.

This is promising, but because the corrected full run did not reproduce the
report, it should be treated as stability evidence, not as the primary result.

## What Worked

### 1. Candidate Pressure Returned

C4 was too passive. It produced only one raw public candidate across eight
cases.

C4.1 produced six raw candidates in the corrected full run. That means the
prompt change did what it was meant to do: it stopped asking "is the baseline
already good?" and started asking "what is the strongest underweighted edge?"

### 2. Deterministic Ledger Construction Still Worked

C4.1 kept C4's biggest win:

- 8/8 ledgers valid in the primary corrected run;
- no summary repair needed.

This is strong evidence that ledger ownership belongs in deterministic code,
not in the model.

### 3. The Public Boundary Held

The user-facing additions did not expose cards, affordance IDs, packets,
ledgers, model IDs, or mental-model names.

The useful addition in `messy-three-problems` appears as a checklist, not as
"the checklist model says..."

### 4. Deterministic Tie Guard Removed False Wins

The first C4.1 run showed that the judge can pick a winner even when the public
outputs are identical. The new guard prevents that.

The corrected run used deterministic ties for collapsed cases. That lowered
cost and removed evaluation noise.

### 5. Cost Improved

The corrected run made only 17 recorded paid calls because identical outputs no
longer needed a paid judge.

This is architecturally important. If the system collapses to baseline, it
should not spend money asking a judge to compare identical outputs.

## What Failed

### 1. Shape Compliance Is Still Not Stable

The model still omitted `one_edge_report` in 2/8 primary corrected cases:

- `friendship-money__edge_audit`
- `phd-research__edge_audit`

The targeted whistleblower rerun also omitted `one_edge_report`.

C4.1 improved candidate pressure, but not enough to trust the shape without a
repair/retry path or stricter response constraints.

### 2. The Actionability Gate Is Too Crude

Four candidates were dropped as `not_directly_user_actionable`.

Some drops were probably correct, but at least two look like gate false
negatives:

- `multi-offer`: "Ask all three companies to extend the 7-day deadline..."
- `real-estate`: "Ask your agent if the seller might extend the deadline..."

Both are concrete user moves. They were dropped because the current
`option_space_expansion` heuristic does not understand that "ask/request/call
to create more time" can be actionable optionality.

This should be fixed carefully, not by blindly admitting everything.

### 3. Exact Case Quote Verification Is Missing

The whistleblower candidate supplied a non-exact pseudo-quote:

> `[MODIFIED/SITUATIONAL] No documentation of incident yet`

The gate admitted it because the validator only checks that `case_quote` is
non-empty. That is not enough.

C4.2 needs a containment check against the case text, or a separate
`evidence_status=inferred_from_turn` path that cannot pretend to be exact quote
support.

### 4. The Model Recommendation Is Not Yet Useful Enough

C4.1 records `recommend_public_admission`, but deterministic code does not
trust it. That is correct.

The `user-has-plan` case showed why: the model recommended false, and the gate
also dropped the candidate. That was safe.

But in future, model recommendation might be useful as a tie-breaker for
borderline candidates, not as a primary admission rule.

## Comparison

| Metric | C3.6 Compact Gate | C4 One Edge | C4.1 Candidate Edge |
| --- | ---: | ---: | ---: |
| Primary full cases | 8 | 8 | 8 |
| Judge winners | `{"C": 2, "tie": 6}` | `{"tie": 7}` plus one judge error | `{"C": 1, "tie": 6}` plus one judge timeout |
| Ledger validation | 1 invalid, 2 valid, 5 repaired | 8 valid | 8 valid |
| Raw accepted candidates | 8 | 1 | 6 |
| Public accepted kept | 3 | 0 | 2 |
| Collapses to Arm B | 5 | 8 | 6 |
| Main strength | product lift | ledger reliability | candidate pressure plus ledger reliability |
| Main weakness | model-written ledger brittle | too passive | gate/compliance not stable |

C3.6 still has the strongest clean product score. C4.1 has the better
architecture direction.

## Product Interpretation

The product promise is not "more mental models." It is:

> Here is one extra pressure point that a strong generic answer may miss.

C4.1 is closer to that promise than C4. It can produce the right kind of thing:

- an executable checklist;
- a deadline extension move;
- a documentation threshold;
- a reversal checkpoint.

But the admission layer is not mature enough. We need better validation before
we can trust the public edge.

## Recommendation

Do not merge into runtime.

Keep C4.1 as the lead dormant architecture direction:

- model produces trace plus `best_candidate_edge`;
- deterministic code builds ledger;
- deterministic code gates public output;
- deterministic tie guard prevents false C wins.

Keep C3.6 as the benchmark to beat:

- C4.1 must match or beat C3.6's product lift while keeping C4's ledger
  reliability.

## Proposed Next Iteration: C4.2 Gate And Evidence Hardening

C4.2 should not change the whole architecture. It should harden C4.1.

Required changes:

1. Enforce `one_edge_report` shape more strongly.
   - Retry or repair when missing.
   - Prefer a fixed JSON skeleton.
2. Verify `case_quote` against case text.
   - Exact quotes must be exact substrings.
   - Inferred evidence must be labeled as inferred and gated more strictly.
3. Improve actionability scoring.
   - `option_space_expansion` should accept concrete action verbs when the user
     is being asked to create or preserve an option.
   - Do not admit vague "consider options" language by default.
4. Keep deterministic tie guard.
5. Rerun the same 8 edge-audit cases.
6. Compare against C3.6 and C4.1:
   - public kept edge count;
   - C wins;
   - invalid/missing reports;
   - exact quote failures;
   - public leaks;
   - overburden/model-theater flags.

The next question is narrower now:

> Can C4.1's candidate pressure survive better quote validation and a smarter
> actionability gate without becoming noisy?

That is the right next bottleneck.
