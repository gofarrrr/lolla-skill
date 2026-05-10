# V60 C4.6 Source Ablation Readout

Date: 2026-05-10

Status: no-new-token artifact ablation. This does not run `/lolla`, does not
rerun private v60 consideration, and does not attach behavior to runtime.

## Question

How much of the useful C4.5 composer-boundary value came from strict
lane-preserved opportunities versus the v60 enrichment path that includes
embedding affordance recall, embedding absence recall, and hybrid/RRF pickup?

The goal was to avoid unnecessary token burn. This run reuses prior artifacts:

- C4.5 system-bound composer outputs;
- C4.5 numeric-guard revalidation;
- C4.4c private exact-chunk traces;
- existing embedding retrieval summary.

No new model calls were made.

## Artifact

Harness:

`scripts/run_v60_source_ablation_analysis.py`

Output:

`data/evaluations/v60_transaction_replay_lab/2026-05-10-c46-source-ablation-analysis/summary.json`

Report:

`data/evaluations/v60_transaction_replay_lab/2026-05-10-c46-source-ablation-analysis/source_ablation_report.md`

## Definitions

Strict lane-only means every source behind an opportunity is
`lane_preserved`.

Enhanced means an opportunity includes at least one of:

- `embedding_affordance_exact`;
- `embedding_absence_exact`;
- `hybrid_rrf_exact`.

Mixed lane+enhanced means lane provenance and enhanced recall both contributed
to an opportunity.

Safe public delta means the composer admitted a public-facing delta and it
survived the deterministic private-language and numeric-novelty guards.

## Results

No-new-token cost:

- New model calls: 0
- New token cost: `$0`
- Existing C4.5 composer cost reused: `$0.009722`
- Existing C4.4 private trace cost reused: `$0.032632`

Opportunity distribution:

- Cases: 8
- Composer opportunities: 22
- Strict lane-only opportunities: 8
- Enhanced opportunities: 14
- Mixed lane+enhanced opportunities: 2

Public delta outcomes:

- Safe public deltas: 4
- Strict lane safe public deltas: 0
- Enhanced safe public deltas: 4
- Unsafe public deltas caught: 1
- Lower-bound safe delta lift over strict lane-only: 4

Source counts across all opportunities:

- `lane_preserved`: 10
- `embedding_affordance_exact`: 8
- `embedding_absence_exact`: 5
- `hybrid_rrf_exact`: 1

Safe admitted deltas by source:

- `embedding_absence_exact`: 2
- `embedding_affordance_exact`: 1
- `hybrid_rrf_exact`: 1
- `lane_preserved`: 0

Unsafe admitted deltas by source:

- `lane_preserved`: 1

## Case Read

`multi_offer`

- Strict lane opportunities: 2
- Enhanced opportunities: 1
- Safe public delta: 1, from `embedding_absence_exact`
- The admitted delta pressure-tested worst-case survivability and exit
  thresholds for the startup option.

`startup_pivot`

- Strict lane opportunities: 0
- Enhanced opportunities: 2
- Safe public delta: 1, from `embedding_affordance_exact`
- The admitted delta added a hybrid option: test the pivot while minimally
  maintaining the current product.

`messy_three_problems`

- Strict lane opportunities: 0
- Enhanced opportunities: 3
- Safe public delta: 1, from `hybrid_rrf_exact`
- The admitted delta framed the short-term rental as a reversible move that
  preserves optionality while testing boyfriend and mom-care uncertainty.

`phd_research`

- Strict lane opportunities: 0
- Enhanced opportunities: 1
- Safe public delta: 1, from `embedding_absence_exact`
- The admitted delta hardened the 18-month checkpoint with learning objective,
  success threshold, and reset rule.

`real_estate`

- Strict lane opportunities: 2
- Enhanced opportunities: 1
- The composer admitted a lane-origin margin-of-safety delta, but deterministic
  validation rejected it because it invented unsupported numbers.

`whistleblower`, `friendship_money`, and `user_has_plan`

- No public delta survived or was needed.
- This is not a failure. These cases show private guardrail value and
  no-delta discipline.

## Interpretation

This ablation supports the hypothesis that the v60 enrichment path adds real
incremental value over strict lane-only composer opportunities.

The strict lanes still matter. They provided 8 pure lane opportunities and 2
mixed lane+enhanced opportunities. They remain the provenance spine.

But in the C4.5 paid composer run, every safe visible addition came from the
enhanced path. The only lane-origin visible addition was rejected as unsafe due
unsupported numeric claims.

That does not mean lanes are bad. It means lanes and v60/embedding enrichment
play different roles:

- lanes stabilize provenance and candidate structure;
- embeddings recover contextually useful opportunities the lanes do not surface
  cleanly;
- absence records create blockers, thresholds, and plan-hardening moves;
- the composer should receive distilled opportunities, not raw model labels;
- deterministic validators remain mandatory.

## Caveat

This is a no-new-token lower-bound ablation over an already-run full composer
output. It does not prove that a separately prompted lane-only composer would
make identical choices. A lane-only composer might admit some lane opportunities
if the enhanced opportunities were removed from view.

However, this artifact does answer a useful practical question:

In the paid C4.5 run we already trust enough to inspect, where did the safe
visible incremental value actually come from?

Answer: from embedding/absence/hybrid-enhanced v60 opportunities, not from
strict lane-only opportunities.

## Product Judgment

This strengthens the case for baking v60 into the existing system rather than
keeping it separate.

The product shape should not be "run v60 after Lolla." It should be:

1. Existing lanes nominate and preserve provenance.
2. Embeddings search exact v60 affordance and absence chunks.
3. Selection reserves a small number of enhanced recall slots.
4. Private chunk-level consideration filters what matters.
5. Composer sees only compact opportunities.
6. Deterministic validation blocks leaks, overfeeding, and unsupported public
   claims.

The value appears to come from the combination, not from replacing lanes.

## Next Check

The next step, if we want a stronger comparison, is a tiny composer-only paid
cross-check:

- Arm L: strict lane-only composer opportunities.
- Arm F: full C4.5 opportunities.
- Same existing Lolla answer.
- Same deterministic numeric/private-language guards.
- No full `/lolla`, no new private v60 trace.

That would cost only composer-boundary calls, not full system runs. It is not
necessary for the lower-bound finding above, but it would reduce uncertainty
about whether the composer behaves differently when enhanced opportunities are
hidden.
