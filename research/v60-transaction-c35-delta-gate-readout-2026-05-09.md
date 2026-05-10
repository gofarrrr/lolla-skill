# V60 Transaction C3.5 Public-Delta Gate Readout

Date: 2026-05-09
Status: dormant replay evidence only
Branch: `feat/v60-transaction-local-replay-lab`

## Question

Does the C3 architecture become safer if a deterministic public gate decides
which LLM-proposed v60 deltas may reach the user?

C3 was the first architecture that looked directionally right:

- Arm B writes the strong generic edge-audit answer.
- Arm C privately reviews grouped v60 affordance cards.
- Arm C returns a private ledger plus a bounded `delta_candidate_report`.
- Deterministic code preserves Arm B and adds only accepted public deltas.

C3 still failed on public-delta quality in the whistleblower case. The LLM
produced structurally valid deltas, but they surfaced too much analytical
machinery: payoff maps, leverage maps, decision-tree language, and similar
model-theater residue.

C3.5 tests whether we can keep the good part of C3 while refusing those weak
public deltas before composition.

## What Changed

The paid replay harness now supports:

```bash
--c-variant delta_gated
```

C3.5 keeps the C3 private-audit shape but adds a public admission gate:

- at most two public accepted deltas;
- each accepted delta must declare `delta_type`;
- allowed public delta types are `evidence_gate`, `concrete_next_move`,
  `risk_caveat`, and `option_space_expansion`;
- public text must be directly useful to the user;
- public text must not expose analytical-framework language such as payoff
  maps, game trees, principal/agent diagnostics, leverage maps, branch
  diagrams, or incentive-alignment labels;
- public text must not mention cards, substrate, packets, ledgers, affordance
  IDs, model IDs, mental-model names, or review machinery;
- if no public delta survives, Arm C collapses back to Arm B.

Implementation files:

- `scripts/run_v60_transaction_paid_replay.py`
- `tests/test_v60_transaction_paid_replay.py`

The important product stance is unchanged: the LLM may propose candidate
reasoning deltas, but deterministic code owns public admission.

## Test Setup

Artifacts:

- Dry run: `data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot-c35-delta-gated-dry-run`
- Paid run: `data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot-c35-delta-gated-edge`

Configuration:

- Affordance artifact: `data/compiled/model_affordances/affordances_v60.json`
- Config: `cap8_focused`
- Mode: `edge_audit`
- Cases: `user_has_plan`, `real_estate`, `whistleblower`,
  `messy_three_problems`
- Generator: `x-ai/grok-4.1-fast`
- Judge: `moonshotai/kimi-k2.6`
- C variant: `delta_gated`

Commands run:

```bash
python3 -m py_compile scripts/run_v60_transaction_paid_replay.py
env PYTHONPATH=. pytest tests/test_v60_transaction_paid_replay.py
env PYTHONPATH=. pytest tests/test_v60_transaction_paid_replay.py tests/test_v60_transaction_replay_matrix.py tests/test_v60_transaction_replay_lab.py tests/test_card_transaction_ledger.py tests/test_reasoning_substrate_packet.py tests/test_reasoning_substrate_packet_review_render.py
python3 scripts/run_v60_transaction_paid_replay.py --case-manifest research/v60-transaction-replay-case-manifest-2026-05-09.json --affordances-path data/compiled/model_affordances/affordances_v60.json --output-dir data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot-c35-delta-gated-dry-run --cases user_has_plan real_estate whistleblower messy_three_problems --modes edge_audit --c-variant delta_gated --dry-run
python3 scripts/run_v60_transaction_paid_replay.py --case-manifest research/v60-transaction-replay-case-manifest-2026-05-09.json --affordances-path data/compiled/model_affordances/affordances_v60.json --output-dir data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot-c35-delta-gated-edge --cases user_has_plan real_estate whistleblower messy_three_problems --modes edge_audit --c-variant delta_gated
```

Local verification:

- focused replay tests: 19 passed;
- broader dormant packet/ledger regression suite: 40 passed;
- dry run: 4/4 items wrote expected prompt packets;
- paid run: 4/4 items completed.

## Paid Result

Aggregate:

- Paid calls: 12
- Total tokens: 123,119
- Reported cost: $0.141239
- Judge winners: `{"B": 2, "tie": 2}`
- Ledger validation: `{"valid": 1, "valid_after_summary_repair": 3}`
- Raw delta validation: `{"valid": 1, "invalid": 3}`
- Public mechanism leaks: 0/4

Item results:

| Item | Ledger | Raw Delta | Public Deltas Kept | Raw Deltas | Dropped | Winner | Theater |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| `user-has-plan__edge_audit` | `valid` | `valid` | 0 | 0 | 0 | tie | neither |
| `real-estate__edge_audit` | `valid_after_summary_repair` | `invalid` | 1 | 2 | 1 | B | C |
| `whistleblower__edge_audit` | `valid_after_summary_repair` | `invalid` | 0 | 3 | 3 | tie | neither |
| `messy-three-problems__edge_audit` | `valid_after_summary_repair` | `invalid` | 2 | 2 | 0 | B | neither |

Public gate outcomes:

| Item | Gate Behavior |
| --- | --- |
| `user-has-plan__edge_audit` | Safe collapse to Arm B. The model found no useful v60 delta. |
| `real-estate__edge_audit` | Kept one premortem-style repair-buffer caveat; dropped one optionality delta as not directly user-actionable. |
| `whistleblower__edge_audit` | Dropped all three proposed deltas: two analytical-framework shaped, one not directly user-actionable. Safe collapse to Arm B. |
| `messy-three-problems__edge_audit` | Kept two concrete moves: ask Seattle for a short extension, and run a 3-step evidence checklist. |

## Comparison To C3

C3 final clean run:

- Judge winners: `{"B": 2, "C": 1, "tie": 1}`
- Delta validation: `{"valid": 4}`
- Ledger validation: `{"valid": 1, "valid_after_summary_repair": 3}`
- Public leaks: 0/4
- Main failure: structurally valid but poor public deltas in whistleblower.

C3.5:

- Judge winners: `{"B": 2, "tie": 2}`
- Raw delta validation: `{"valid": 1, "invalid": 3}`
- Ledger validation: `{"valid": 1, "valid_after_summary_repair": 3}`
- Public leaks: 0/4
- Main improvement: whistleblower no longer loses to model theater because the
  gate suppresses all three bad deltas.
- Main regression: real-estate loses its prior C win, and the stricter delta
  contract reveals that Grok does not reliably produce public-ready deltas.

So C3.5 trades upside for safety. That is a useful discovery, but not yet a
merge signal for product use.

## What Worked

### 1. The Public/Private Boundary Held

Across all four paid cases, the composed Arm C public output leaked none of the
private machinery terms checked by the harness:

- card;
- substrate;
- packet;
- ledger;
- affordance;
- model ID;
- mental model;
- review machinery.

This matters because the product should not tell the user, "we used a reasoning
substrate card." It should simply produce better decision pressure.

### 2. Safe Collapse Is Real

Two cases collapsed to the baseline public output:

- `user-has-plan`, because no useful delta was proposed;
- `whistleblower`, because all proposed public deltas were too abstract or not
  actionable enough.

This is the right failure mode. If v60 only creates private consideration but
no public improvement, the system should keep the strong vanilla answer.

### 3. The Gate Caught The Known C3 Failure

Whistleblower was the important stress test. C3 had allowed public deltas that
were valid by trace but bad by product quality. C3.5 dropped:

- decision-tree branch language;
- sunk-cost framing that did not produce a concrete move;
- game-theory payoff mapping language.

That is exactly the class of failure the gate was designed to stop.

### 4. Good Deltas Can Still Pass

The gate did not suppress everything. It kept:

- a real-estate premortem caveat around repair-overrun exposure;
- a Seattle-decision extension ask;
- a Seattle-decision evidence checklist.

These are shaped like product-useful additions: moves, checks, and caveats,
not labels.

## What Failed

### 1. Raw Delta Compliance Is Not Stable Enough

Only 1 of 4 raw `delta_candidate_report` payloads passed strict C3.5
validation.

Failures:

- `real-estate`: one accepted delta was not directly user-actionable.
- `whistleblower`: two deltas were analytical-framework shaped; two were not
  directly user-actionable by the stricter gate.
- `messy-three-problems`: one grounded public delta lacked `case_quote`.

The deterministic gate can salvage the public output, but the private contract
is still too loose for a runtime-quality audit trail.

### 2. Product Lift Did Not Beat Baseline

C3.5 did not produce a C win:

- B wins: 2
- C wins: 0
- ties: 2

That is not enough for product promotion. Safety improved, but the additional
reasoning layer did not yet reliably improve the user-visible decision output.

### 3. The Judge Still Saw C As Overburdened In Two Cases

Even after the gate:

- `real-estate`: judge marked C as overburdened and model-theater-prone.
- `messy-three-problems`: judge marked C as overburdened.

The issue is not private leakage; it is composition density. Adding even one or
two deltas can still make an already-strong Arm B answer feel overstuffed.

### 4. Ledger Shape Still Needs Repair

Three of four ledgers required deterministic summary repair. This is the same
pattern as C3 and means we still should not treat the ledger as a runtime-grade
artifact. It is good enough for replay analysis, not good enough for product
attachment.

## Example: How C3.5 Worked In Practice

For `whistleblower`, v60 nominated grouped cards including decision-tree,
sunk-cost, and game-theory/payoff affordances. The private LLM proposed three
public deltas:

- outline internal/external/wait paths with triggers and odds;
- set aside eight years at the firm and family commitments as sunk;
- map general counsel's likely moves and payoffs.

C3 would likely have surfaced some of that. C3.5 refused all of it:

- the first looked like branch/decision-tree machinery;
- the second was too abstract and not directly user-actionable;
- the third exposed payoff-map language.

The composer then collapsed Arm C back to Arm B. The judge returned tie rather
than B winning on theater. That is the best C3.5 evidence: it can prevent a
bad mental-model injection from becoming public advice.

For `messy-three-problems`, two deltas passed:

- ask Seattle for a two-week extension today;
- run a three-step checklist covering boyfriend move specifics, mom care, and
  short-term housing.

Those are the shape we want, even though the judge still preferred B overall.
The useful knowledge was metabolized into action rather than displayed as a
model name.

## Architectural Read

C3.5 strengthens the core architecture:

1. Deterministic lanes nominate candidates.
2. v60 enriches those nominations into grouped cards and absence rails.
3. The LLM receives private consideration material, not final authority.
4. The LLM returns a private ledger and proposed bounded deltas.
5. Deterministic validators check trace and shape.
6. A deterministic public gate decides whether any proposed delta is allowed
   into user-facing output.
7. If nothing survives, the system keeps the baseline answer.

This is the right direction because it treats the LLM as a probabilistic
reasoning surface and the deterministic layer as the product's epistemic
transport system. The LLM can notice, connect, and propose. The deterministic
system decides what is admissible, traceable, bounded, and user-safe.

But C3.5 also shows the current form is too brittle:

- prompt-only discipline is insufficient;
- public-delta admission cannot rely on the model's self-classification;
- better composition is needed so accepted deltas do not overburden already
  good answers;
- raw ledger quality still needs schema repair or a stricter generation path.

## Product Read

C3.5 is promising as a safety layer, not as a value layer yet.

From the user's perspective, the target experience should be:

> "The answer found one sharper move or one missing check I would not have
> naturally considered."

C3.5 sometimes does that, but it does not do it reliably enough. It is very
good at refusing bad additions. It is weaker at selecting additions that beat a
high-quality baseline.

That means the next product question is not:

> Can v60 change the output?

It is:

> Can v60 change the output only when the addition is clearer, shorter, and
> more decision-useful than the baseline?

## Monetization Read

C3.5 points toward a product feature, but not a standalone product promise yet.

Possible future product framing:

- "Decision edge check": runs privately and returns only the few missing checks
  that survived evidence and actionability gates.
- "Second-order reasoning audit": shows the user where the original answer may
  be overconfident, under-evidenced, or trapped in a narrow frame.
- "Premium decision review": useful for high-stakes personal, career, legal,
  finance, and founder decisions where one missed constraint matters.

But the monetizable feature is not "mental models added to your answer." That
would invite theater. The monetizable feature is:

> fewer blind spots, fewer false certainties, and better next questions.

C3.5 proves part of the safety story. It does not yet prove enough user-visible
lift to price as a premium layer.

## Recommendation

Do not merge C3.5 into the main product path.

Do keep C3.5 in the dormant replay lab as the current safest transaction
architecture candidate.

Before merge or runtime consideration, do the next iteration:

1. Re-run with the new replay-summary instrumentation so raw model compliance
   and post-gate public composition metrics are visible in the paid summary.
2. Add a second composition gate that rejects additions when Arm B already
   contains the same move in clearer form.
3. Add a density budget: max one added delta unless the baseline is missing an
   evidence gate.
4. Prefer `evidence_gate` and `concrete_next_move` over `risk_caveat` and
   `option_space_expansion`.
5. Turn missing `case_quote` into an automatic drop, not only a validation
   error.
6. Re-run the same four edge-audit cases, then add at least one absence-heavy
   case and one weak-support case.

Promotion bar for the next run:

- no private public leaks;
- all post-gate public outputs valid;
- raw delta compliance at least 3/4 or deterministic repair explains every
  invalid item;
- C wins or ties B on at least 3/4 cases;
- no C overburden flags;
- every public delta is either a concrete next move, an evidence gate, or a
  short risk caveat that changes a user decision.

## Bottom Line

C3.5 proves that a deterministic public gate can stop mental-model theater from
reaching the user. That is a real architectural win.

It does not yet prove that v60 reliably improves the final product output. The
next problem is not safety alone; it is selective usefulness under a strict
density budget.

Keep iterating in the dormant lab. Do not attach this to live `/lolla` yet.
