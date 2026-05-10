# V60 Transaction C4.2 Hardened Edge Readout

Date: 2026-05-09
Status: dormant replay evidence only
Branch: `feat/v60-transaction-local-replay-lab`

## Plain-English Summary

C4.2 tested whether C4.1's architecture can become more useful as an addition
to the existing answer without drifting into noisy mental-model decoration.

The product question was:

> Can v60 add one grounded, decision-useful edge on top of a strong baseline
> answer, while staying silent when the edge is weak, unsupported, or redundant?

The answer is:

> Directionally yes, but not safely enough for runtime.

C4.2 improved on C4.1:

- raw candidate edges increased from 6/8 to 7/8;
- public kept edges increased from 2/8 to 3/8;
- missing `one_edge_report` decreased from 2/8 to 1/8;
- ledger validation stayed 8/8 valid;
- judge C wins increased from 1 to 2.

But C4.2 also introduced one B win. That matters more than the extra C win.

The useful interpretation is:

> The reasoning-substrate layer can create real additive value, but public
> admission still needs stronger domain sensitivity and overclaim control before
> product/runtime use.

## What Changed

The paid replay harness now supports:

```bash
--c-variant candidate_edge_hardened
```

Implementation:

- `scripts/run_v60_transaction_paid_replay.py`
- `tests/test_v60_transaction_paid_replay.py`

C4.2 keeps the C4.1 architecture:

- model produces `private_consideration_trace`;
- model produces `one_edge_report.best_candidate_edge`;
- model does not write the formal transaction ledger;
- deterministic code builds the ledger;
- deterministic code gates public admission;
- deterministic identical-output tie guard remains.

C4.2 hardens:

- prompt discipline around exact case quotes;
- model contract by adding `evidence_status` to `best_candidate_edge`;
- deterministic quote containment checks for hardened candidate edges;
- deterministic actionability checks for concrete option-preserving moves.

The goal was not to make v60 speak more. The goal was to make v60 speak only
when it has a better grounded move.

## Verification

Commands run:

```bash
python3 -m py_compile scripts/run_v60_transaction_paid_replay.py tests/test_v60_transaction_paid_replay.py
env PYTHONPATH=. pytest tests/test_v60_transaction_paid_replay.py -q
env PYTHONPATH=. pytest tests/test_v60_transaction_paid_replay.py tests/test_v60_transaction_replay_matrix.py tests/test_v60_transaction_replay_lab.py tests/test_card_transaction_ledger.py tests/test_reasoning_substrate_packet.py tests/test_reasoning_substrate_packet_review_render.py
```

Result:

- focused paid-replay tests: 30 passed;
- broader dormant replay/packet/ledger suite: 51 passed.

## Dry Run

Path:

- `data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot-c42-hardened-edge-all-dry-run`

Configuration:

- Artifact: `data/compiled/model_affordances/affordances_v60.json`
- Config: `cap8_focused`
- Mode: `edge_audit`
- Cases: all 8 manifest cases
- C variant: `candidate_edge_hardened`

Dry-run packet quality:

| Item | C Prompt Tokens | Packet Tokens | Cards | Absence Records | Weak Support | Medium Confidence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `multi-offer__edge_audit` | 14,491 | 7,183 | 13 | 16 | 0 | 1 |
| `whistleblower__edge_audit` | 15,182 | 7,276 | 14 | 16 | 0 | 1 |
| `startup-pivot__edge_audit` | 11,802 | 6,902 | 11 | 16 | 0 | 0 |
| `real-estate__edge_audit` | 10,973 | 6,664 | 14 | 16 | 2 | 2 |
| `friendship-money__edge_audit` | 12,156 | 6,708 | 13 | 16 | 0 | 0 |
| `messy-three-problems__edge_audit` | 13,338 | 6,544 | 11 | 16 | 0 | 0 |
| `user-has-plan__edge_audit` | 12,414 | 6,887 | 11 | 16 | 0 | 0 |
| `phd-research__edge_audit` | 16,601 | 6,727 | 10 | 16 | 0 | 0 |

C4.2 adds roughly 112-113 C-arm prompt tokens per case over C4.1. That is an
acceptable review-lab cost because the extra tokens are doing evidence and
admission discipline work.

## Paid Replay

Path:

- `data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot-c42-hardened-edge-edge-all`

Aggregate:

- Paid calls recorded: 19
- Total tokens: 183,148
- Reported cost: $0.132814
- Judge winners: `{"B": 1, "C": 2, "tie": 5}`
- Ledger validation: `{"valid": 8}`
- Delta validation: `{"valid": 3, "invalid": 4, "missing_one_edge_report": 1}`
- Gate-enabled items: 8
- Raw accepted candidate edges: 7
- Public accepted edges kept: 3
- Collapses to Arm B: 5
- Dropped public deltas: 4
- Drop reasons:
  - `not_directly_user_actionable`: 3
  - `case_quote_not_exact`: 1

Item results:

| Item | Winner | Ledger | Candidate Report | Raw Candidate | Public Kept | Collapse | Notes |
| --- | --- | --- | --- | ---: | ---: | --- | --- |
| `multi-offer__edge_audit` | tie | valid | present | 1 | 0 | yes | quote rejected as not exact |
| `whistleblower__edge_audit` | B | valid | present | 1 | 1 | no | harmful overclaim admission |
| `startup-pivot__edge_audit` | C | valid | present | 1 | 1 | no | clean option-expansion win |
| `real-estate__edge_audit` | tie | valid | missing | 0 | 0 | yes | shape failure |
| `friendship-money__edge_audit` | C | valid | present | 1 | 1 | no | clean sunk-cost reframe win |
| `messy-three-problems__edge_audit` | tie | valid | present | 1 | 0 | yes | false drop: actionability heuristic too narrow |
| `user-has-plan__edge_audit` | tie | valid | present | 1 | 0 | yes | safe collapse |
| `phd-research__edge_audit` | tie | valid | present | 1 | 0 | yes | false drop: evidence-gate heuristic too narrow |

## Clean Additive Wins

### Startup Pivot

C4.2 added a hybrid option that the baseline missed:

> Map three options side-by-side: full pivot, sales push on current 22 customers,
> or hybrid building workflow tool as feature add-on, with estimated MRR impact
> and probability for each.

Judge result:

- winner: C
- constructive edge: C
- missing evidence discipline: tie
- model theater: neither
- overburdened: neither
- promotion read: promote

Why this matters:

The baseline treated the decision as pivot versus no pivot. C4.2 surfaced a
third path that preserves current MRR while testing the workflow-tool signal.
This is exactly the intended product value: v60 adds a non-obvious but
decision-relevant option, without naming mental models.

### Friendship Money

C4.2 added a sunk-cost isolation move:

> Explicitly set aside the prior $5K as already lost before deciding on new
> help, asking if you'd start lending today based only on forward value.

Judge result:

- winner: C
- constructive edge: C
- missing evidence discipline: tie
- model theater: neither
- overburdened: neither
- promotion read: promote

Why this matters:

The answer already had a good boundary script. C4.2 added the pressure point
that makes the boundary emotionally executable: do not let the unpaid $5K buy
another $10K mistake.

This is a strong example of the system acting as an addition, not a replacement.

## Harmful Admission

### Whistleblower

C4.2 admitted:

> Document the incident details tonight in a timestamped personal email before
> contacting attorneys, as regulators prioritize witnesses with contemporaneous
> records.

Judge result:

- winner: B
- constructive edge: B
- missing evidence discipline: B
- model theater: C
- overburdened: C

Why it lost:

The baseline already said to document the incident tonight. C4.2 reframed that
as a stronger gating action and added an ungrounded claim about regulator
prioritization. In a legal-ish, high-stakes case, that is not a harmless
addition. It nudges sequencing and authority without enough support.

This is an important product lesson:

> High-stakes domains need stricter public admission than normal decision cases.

The substrate should be allowed to help, but the gate needs domain-sensitive
overclaim control.

## Useful Drops And False Drops

### Good Drop: Multi-Offer

The candidate quote was:

> If wife is a hard or soft no, I take A

That exact phrase was not in the case evidence. C4.2 rejected it as
`case_quote_not_exact`.

This is good. The candidate was also mostly a duplicate of the baseline BATNA
logic. No public value was lost.

### False Drop: Messy Three Problems

C4.2 proposed:

> Before accepting Seattle, confirm boyfriend's specific relocation timeline
> and costs by asking: "If I accept, what's your quit date, job search plan, and
> our joint housing steps?"

This should probably have been admitted. It is a concrete, useful move.

It was dropped because the actionability heuristic for `concrete_next_move`
does not currently treat `confirm` as a concrete action verb.

### False Drop: PHD Research

C4.2 proposed:

> If no single-cell lab agrees to share data after pitching both options at your
> institution, abandon option 3 immediately and pivot to modified option 1.

This also looks like a useful evidence gate. It was dropped because the current
evidence-gate actionability heuristic does not understand reversal gates like
"if no X, abandon Y."

These false drops are not philosophical failures. They are admission-policy
bugs.

## Comparison

| Metric | C3.6 Compact Gate | C4 One Edge | C4.1 Candidate Edge | C4.2 Hardened Edge |
| --- | ---: | ---: | ---: | ---: |
| Full edge-audit cases | 8 | 8 | 8 | 8 |
| Judge winners | `{"C": 2, "tie": 6}` | `{"tie": 7}` plus one judge error | `{"C": 1, "tie": 6}` plus one judge timeout | `{"B": 1, "C": 2, "tie": 5}` |
| Ledger validation | 1 invalid, 2 valid, 5 repaired | 8 valid | 8 valid | 8 valid |
| Raw accepted candidates | 8 | 1 | 6 | 7 |
| Public accepted kept | 3 | 0 | 2 | 3 |
| Collapses to Arm B | 5 | 8 | 6 | 5 |
| Main strength | clean product wins | ledger reliability | candidate pressure + ledger reliability | richer candidate production + evidence gate |
| Main weakness | model-written ledger brittle | too passive | gate/compliance not stable | one harmful admission |

C4.2 matched C3.6's C-win count, but C3.6 had no B wins. C4.2 therefore is not
better yet. The B win is the deciding safety signal.

## Product Interpretation

C4.2 helps answer the core product question:

> Is this system useful as an addition to a strong answer?

Yes, when it does one of these:

- adds a missing option that changes the decision frame;
- turns a vague emotional/social decision into an executable test;
- isolates a hidden bias or pressure that makes the recommendation easier to
  act on;
- creates a hard evidence gate for a tempting but under-supported path.

No, when it does one of these:

- repeats the baseline in more authoritative language;
- strengthens a claim in a legal/financial/high-stakes setting without source
  support;
- adds a public edge only because a card was considered;
- uses evidence labels without real evidence custody.

That is the product shape:

> v60 should not make the answer more intellectual. It should make one next move
> sharper, safer, or more testable.

## Monetization/Product Angle

The most defensible future product surface is not "we use mental models."

The defensible product surface is a second-pass decision-pressure layer:

- baseline answer remains intact;
- private substrate review looks for one non-obvious pressure point;
- user sees only the admitted move/check/caveat;
- product can report, internally or in a pro view, why no edge was admitted.

This could become a premium "Decision Edge" or "Second-Pass Pressure Test"
feature, but only after admission reliability improves. The value is not in
showing the model inventory. The value is in helping the user notice the thing a
high-quality generic answer still underweighted.

## Recommendation

Do not merge into runtime.

Keep C4.2 as useful evidence and continue the dormant lab.

Current best judgment:

- C3.6 remains the cleanest product benchmark.
- C4.2 is the best architecture direction so far.
- The next bottleneck is not packet grouping or ledger construction.
- The next bottleneck is public admission policy.

## Proposed Next Iteration: C4.3 Domain-Sensitive Admission

C4.3 should keep C4.2's architecture and harden admission:

1. Add high-stakes domain sensitivity.
   - Legal/medical/financial/employment-risk cases should require stronger
     evidence and avoid authority claims.
2. Expand actionability carefully.
   - Admit `confirm`, `verify`, and reversal-gate patterns when they are
     concrete.
   - Still reject vague "consider options" language.
3. Add overclaim detection.
   - Drop public text that says regulators, courts, employers, markets, or
     counterparties "will" behave a certain way without evidence.
4. Add duplicate-strengthening detection.
   - If the baseline already says "document tonight," do not admit another edge
     that merely makes it sound more official.
5. Keep exact quote checks.
6. Rerun the same 8 cases.

The sharper question is now:

> Can the system keep the startup/friendship wins, recover the messy/PHD false
> drops, and prevent the whistleblower harmful admission?

That is the right next test before any merge conversation.
