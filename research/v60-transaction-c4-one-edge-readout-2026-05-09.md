# V60 Transaction C4 One-Edge Readout

Date: 2026-05-09
Status: dormant replay evidence only
Branch: `feat/v60-transaction-local-replay-lab`

## Plain-English Summary

C4 tested a simpler idea than C3.6:

> Do not ask the model to write the full public answer or a formal card ledger.
> Ask it to privately inspect the v60 cards and offer at most one missing edge.
> Then let deterministic code decide whether that edge is safe enough to add.

This was meant to answer one product question:

> Can v60 behave like a quiet second brain that either adds one sharp missing
> move or stays silent?

The answer from this run is mixed:

- C4 fixed ledger reliability: every generated case had a valid deterministic
  card transaction ledger.
- C4 reduced prompt/output burden versus C3.6.
- C4 preserved the public/private boundary.
- C4 did not improve user-visible answers in this replay.
- C4 made the model too comfortable saying "no useful edge," even in cases
  where C3.6 had already found useful public deltas.

So C4 should not replace C3.6 as the current lead architecture. But C4 did
prove a valuable mechanism: the ledger should be built deterministically from a
smaller model-produced trace, not written by the model as a full formal ledger.

## Why We Tested It

C3.6 was the strongest prior result:

- all 8 paid edge-audit cases completed;
- judge winners: `{"C": 2, "tie": 6}`;
- public leaks: 0/8;
- C overburden flags: 0/8;
- public accepted deltas kept: 3;
- collapses to Arm B: 5;
- ledger validation still required repair or failed in 6/8 cases.

That told us C3.6 had the right product shape but the wrong accountability
surface. The model could propose useful deltas, but asking it to also maintain
a formal card ledger was brittle.

C4 therefore tested the inverse trade:

- remove the formal ledger from the model contract;
- keep a lighter private consideration trace;
- ask for one possible public edge;
- build the ledger deterministically in code.

## What Changed

The paid replay harness now supports:

```bash
--c-variant one_edge
```

Implementation:

- `scripts/run_v60_transaction_paid_replay.py`
- `tests/test_v60_transaction_paid_replay.py`

C4 behavior:

- Arm B still writes the strong generic answer.
- Arm C receives the v60 grouped-card packet.
- Arm C returns:
  - `private_consideration_trace`, one row per candidate card;
  - `one_edge_report`, either one public candidate edge or an explicit
    no-delta reason.
- Arm C is not asked to return `private_transaction_ledger`.
- Deterministic code converts the trace and `one_edge_report` into:
  - a composed public output;
  - a private transaction ledger;
  - validation summaries.
- The public gate still rejects:
  - framework-shaped language;
  - private machinery leaks;
  - non-actionable public text;
  - missing exact case quotes;
  - duplicate baseline content.

The important architecture shift is:

> The model considers. Deterministic code accounts.

## Verification

Commands run:

```bash
python3 -m py_compile scripts/run_v60_transaction_paid_replay.py tests/test_v60_transaction_paid_replay.py
env PYTHONPATH=. pytest tests/test_v60_transaction_paid_replay.py -q
env PYTHONPATH=. pytest tests/test_v60_transaction_paid_replay.py tests/test_v60_transaction_replay_matrix.py tests/test_v60_transaction_replay_lab.py tests/test_card_transaction_ledger.py tests/test_reasoning_substrate_packet.py tests/test_reasoning_substrate_packet_review_render.py
```

Result:

- focused paid-replay tests: 26 passed;
- broader dormant replay/packet/ledger suite: 47 passed.

## Dry Run

Path:

- `data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot-c4-one-edge-all-dry-run`

Configuration:

- Artifact: `data/compiled/model_affordances/affordances_v60.json`
- Config: `cap8_focused`
- Mode: `edge_audit`
- Cases: all 8 manifest cases
- C variant: `one_edge`

Dry-run result:

- 8/8 prompt packets written.
- The C prompt contained the C4 one-edge contract.
- The C prompt removed the formal ledger schema from the model-facing contract.

Dry-run packet quality:

| Item | C Prompt Tokens | Packet Tokens | Cards | Absence Records | Weak Support | Medium Confidence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `multi-offer__edge_audit` | 14,324 | 7,183 | 13 | 16 | 0 | 1 |
| `whistleblower__edge_audit` | 15,015 | 7,276 | 14 | 16 | 0 | 1 |
| `startup-pivot__edge_audit` | 11,635 | 6,902 | 11 | 16 | 0 | 0 |
| `real-estate__edge_audit` | 10,806 | 6,664 | 14 | 16 | 2 | 2 |
| `friendship-money__edge_audit` | 11,989 | 6,708 | 13 | 16 | 0 | 0 |
| `messy-three-problems__edge_audit` | 13,171 | 6,544 | 11 | 16 | 0 | 0 |
| `user-has-plan__edge_audit` | 12,247 | 6,887 | 11 | 16 | 0 | 0 |
| `phd-research__edge_audit` | 16,434 | 6,727 | 10 | 16 | 0 | 0 |

Compared to C3.6, C4 removed about 750 prompt tokens per C-arm case by dropping
the model-facing formal ledger contract.

## Paid Replay

Primary path:

- `data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot-c4-one-edge-edge-all`

Targeted rerun path:

- `data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot-c4-one-edge-whistleblower-rerun`

The primary full run had one judge-call provider failure for
`whistleblower__edge_audit`. The C generation completed and the deterministic
ledger validated, but the judge returned empty non-JSON. I reran only that case
as a targeted check.

Primary full-run aggregate:

- Paid calls recorded: 23
- Total tokens: 216,664
- Reported cost: $0.195265
- Judge winners: `{"tie": 7}` plus one judge error
- Ledger validation: `{"valid": 8}`
- Delta validation: `{"valid": 4, "missing_one_edge_report": 3, "invalid": 1}`
- Gate-enabled items: 8
- Raw accepted deltas: 1
- Public accepted deltas kept: 0
- Collapses to Arm B: 8
- Dropped public deltas: 1
- Drop reasons: `{"analytical_framework_language": 1}`

Targeted whistleblower rerun:

- Paid calls: 3
- Total tokens: 30,503
- Reported cost: $0.031567
- Judge winner: `tie`
- Ledger validation: `valid`
- Delta validation: `missing_one_edge_report`
- Public accepted deltas kept: 0
- Collapse to Arm B: yes

## Item Results

| Item | Status | Judge | Ledger | One-Edge Report | Raw Public Edge | Public Kept | Collapse |
| --- | --- | --- | --- | --- | ---: | ---: | --- |
| `multi-offer__edge_audit` | ok | tie | valid | present, no delta | 0 | 0 | yes |
| `whistleblower__edge_audit` | judge error; rerun ok | tie on rerun | valid | missing | 0 | 0 | yes |
| `startup-pivot__edge_audit` | ok | tie | valid | present, proposed edge | 1 | 0 | yes |
| `real-estate__edge_audit` | ok | tie | valid | present, no delta | 0 | 0 | yes |
| `friendship-money__edge_audit` | ok | tie | valid | missing | 0 | 0 | yes |
| `messy-three-problems__edge_audit` | ok | tie | valid | present, no delta | 0 | 0 | yes |
| `user-has-plan__edge_audit` | ok | tie | valid | present, no delta | 0 | 0 | yes |
| `phd-research__edge_audit` | ok | tie | valid | missing | 0 | 0 | yes |

The only proposed public edge was in `startup-pivot__edge_audit`:

> Before the 14-day decision, map branches for hybrid options like building the
> workflow tool as a premium add-on to the current product to test demand
> without fully abandoning existing MRR.

The gate dropped it because it was analytical-framework shaped and not directly
actionable enough. That was the right deterministic decision.

## Comparison To C3.6

| Metric | C3.6 Compact Gate | C4 One Edge |
| --- | ---: | ---: |
| Full edge-audit cases | 8 | 8 |
| Primary paid calls | 24 | 23 recorded plus 1 judge error |
| Primary total tokens | 256,609 | 216,664 |
| Primary reported cost | $0.308291 | $0.195265 |
| Judge winners | `{"C": 2, "tie": 6}` | `{"tie": 7}` plus one judge error |
| Targeted rerun judge | n/a | `{"tie": 1}` |
| Ledger validation | `invalid`: 1, `valid`: 2, `valid_after_summary_repair`: 5 | `valid`: 8 |
| Raw accepted deltas | 8 | 1 |
| Public accepted deltas kept | 3 | 0 |
| Collapses to Arm B | 5 | 8 |
| Public leaks | 0/8 | 0/8 |
| C-specific overburden | 0/8 | 0/8 |

C4 is cleaner and cheaper. But C3.6 is still more product-useful.

## What Worked

### 1. Deterministic Ledger Construction Worked

C4 produced `valid` ledger status for all 8 primary case generations. No summary
repair was needed.

This is the strongest C4 result. It shows that the formal transaction ledger
should probably be owned by code, not by the LLM.

The LLM can still contribute:

- card-level consideration trace;
- whether a card seemed used, rejected, or deferred;
- candidate edge evidence;
- reason text.

But the system should compute the final ledger shape, counts, and visibility
classification.

### 2. Public Boundary Held

C4 leaked no checked private machinery into public composed answers:

- no card references;
- no substrate references;
- no packet references;
- no ledger references;
- no affordance IDs;
- no model IDs;
- no mental-model disclosure;
- no review machinery.

This confirms the staged composition pattern is still right. The answer can be
improved by private reasoning material without showing the machinery to the
user.

### 3. C4 Is Cheaper

C4 removed the model-facing formal ledger schema and reduced prompt pressure by
about 750 C-arm prompt tokens per dry-run case.

Primary full-run cost also fell from C3.6's $0.308291 to C4's $0.195265,
although the comparison is not perfectly apples-to-apples because the C4
primary run had one failed judge call.

### 4. The Public Gate Did Its Job

The only proposed public delta was dropped for analytical-framework language.
That is exactly the kind of product failure we want deterministic code to
catch.

C4 did not create public theater. It collapsed safely.

## What Failed

### 1. C4 Over-Suppressed The Product Edge

C4 kept zero public deltas. C3.6 kept three and got two C wins.

The important regression is not just "fewer deltas." The important regression is
that C4 said no delta in cases where C3.6 had found useful public additions:

- `real-estate__edge_audit`
- `messy-three-problems__edge_audit`

That means the one-edge prompt made the model too deferential to the baseline.
It treated "the answer is already pretty good" as enough reason to stay silent.
But our product is not trying to say whether the vanilla answer is good. It is
trying to find whether one non-obvious extra pressure point would help the user.

### 2. `one_edge_report` Compliance Was Not Reliable

The full run had:

- 4 valid reports;
- 3 missing `one_edge_report`;
- 1 invalid report.

The targeted whistleblower rerun also missed `one_edge_report`.

This tells us the C4 contract is not yet robust enough. It needs either a
stricter JSON skeleton, stronger examples, or a contract where the model must
always return a candidate slot even when the deterministic gate later rejects
it.

### 3. The Model Still Misunderstands "Useful Edge"

The startup-pivot proposed edge was directionally plausible, but it used
framework language:

- "map branches"
- "hybrid options"
- "test demand without fully abandoning existing MRR"

The substance might be salvageable, but the public text was not clean product
language. A user should get a move, not the smell of the tool that produced the
move.

### 4. No-Delta Needs To Be Harder To Claim

C4 allowed the model to say "no useful edge" too cheaply. That is not what we
want.

The right standard is not:

> Is the baseline answer already good?

The right standard is:

> After reviewing v60, what is the single strongest pressure point that the
> baseline may still be underweighting, and should deterministic code admit it
> publicly?

Those are different questions.

## First-Principles Interpretation

The system has three separate jobs:

1. Find candidate cognition.
2. Decide whether that cognition deserves private consideration.
3. Decide whether any result should reach the user.

C3.6 blended jobs 2 and 3 too much into the model contract. It got product lift,
but the private ledger was brittle.

C4 separated accountability better. It proved that code can own the ledger. But
it weakened job 1 by letting the model opt out of edge-finding too easily.

The next design should keep C4's deterministic ledger construction and restore
C3.6's pressure to find candidate deltas.

## Recommendation

Do not merge C4 as the product behavior.

Keep C3.6 as the current best dormant product architecture:

- baseline answer preserved;
- v60 considered privately;
- deterministic public gate;
- at most one public addition;
- safe collapse to Arm B.

But take this C4 lesson into the next iteration:

> The model should not write the transaction ledger. It should produce a small
> consideration trace and candidate edge material. Code should build the ledger
> and gate the public output.

## Proposed Next Iteration: C4.1 Candidate Edge

C4.1 should test:

1. Always require `one_edge_report`.
2. Split the report into two parts:
   - `best_candidate_edge`, always present;
   - `recommend_public_admission`, boolean.
3. Make no-delta a deterministic outcome, not primarily a model outcome.
4. Let the deterministic gate decide whether `best_candidate_edge` is admitted,
   rewritten, or collapsed.
5. Preserve deterministic ledger construction from C4.
6. Compare directly against C3.6 on the same 8 edge-audit cases.

The key prompt change should be:

> Do not decide whether the baseline is good. Identify the strongest plausible
> underweighted edge from the provided cards. The system will decide whether it
> is public-worthy.

That should produce better data. It separates "find the edge" from "ship the
edge." C4 accidentally let the model collapse those two decisions.

## Merge Readiness

Ready to keep as dormant lab code:

- `--c-variant one_edge`;
- deterministic one-edge ledger composer;
- one-edge validation;
- tests covering valid, collapsed, and bad-public-edge cases;
- C4 report artifacts.

Not ready for product/runtime:

- C4 one-edge prompt as-is;
- C4 no-delta policy as-is;
- any live `/lolla` injection;
- automatic promotion of v60 into runtime.

C4 gives us a better internal accounting pattern. It does not yet give us a
better user answer.
