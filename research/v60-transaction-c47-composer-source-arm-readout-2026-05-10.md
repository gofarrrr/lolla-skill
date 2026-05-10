# V60 C4.7 Composer Source-Arm Readout

Date: 2026-05-10

Status: cheap composer-only paid cross-check. This does not run `/lolla`, does
not rerun embeddings, and does not rerun private v60 exact-chunk consideration.

## Technical Lead Call

This was the last test I wanted before calling the dormant/shadow integration
infrastructure merge-ready for review.

It was not necessary for live runtime readiness. We are still not ready for
live `/lolla` behavior. But it was necessary to remove the biggest caveat from
C4.6: maybe lane-only opportunities would perform better if the enhanced
opportunities were hidden.

## Test Shape

C4.7 reuses paid C4.5 artifacts and filters composer opportunities to one
source arm:

- Arm: `strict_lane`
- Included only opportunities whose `source_mix` was exactly
  `["lane_preserved"]`
- Hid the embedding profile from the composer
- Did not rerun private traces
- Did not rerun full Lolla
- Ran only cases with strict lane opportunities

Harness:

`scripts/run_v60_composer_source_arm_replay.py`

Paid output:

`data/evaluations/v60_transaction_replay_lab/2026-05-10-c47-composer-source-arm-lane-only-paid/summary.json`

Safety-revalidated output:

`data/evaluations/v60_transaction_replay_lab/2026-05-10-c47-composer-source-arm-lane-only-paid/summary_revalidated_decorated_numeric_guard.json`

## Cost

- Cases run: 5
- Composer calls: 5
- Cost: `$0.004878`
- Input tokens: 23,180
- Output tokens: 927
- Total tokens: 24,107

This was deliberately cheap. It avoided the expensive C4.4 private
consideration stage.

## Results

Raw schema validation:

- 5/5 valid
- Decisions: 1 `admit_delta`, 4 `no_delta`
- Raw public deltas: 1

Safety revalidation with decorated numeric guard:

- 4/5 valid
- Safe public deltas: 0
- Unsafe public deltas: 1

The one attempted lane-only public delta was `real_estate`. It invented an
unsupported inspector-miss percentage (`20-30%`). The improved numeric guard
caught `20%` and `30%` as novel public numeric claims.

## Case Outcomes

`multi_offer`

- Strict lane opportunities: 2
- Composer decision: `no_delta`
- Reason: lane opportunities were already covered or redundant.

`whistleblower`

- Strict lane opportunities: 1
- Composer decision: `no_delta`
- Reason: game-theory payoff refinement was jargon-heavy and low marginal value.

`real_estate`

- Strict lane opportunities: 2
- Composer decision: raw `admit_delta`
- Safety result: invalid
- Reason: invented unsupported numeric percentage.

`friendship_money`

- Strict lane opportunities: 2
- Composer decision: `no_delta`
- Reason: opportunity-cost and costless-enabling points were already covered
  privately or in the answer.

`user_has_plan`

- Strict lane opportunities: 1
- Composer decision: `no_delta`
- Reason: base-rate/runway realism was already in the answer.

## Comparison Against Full Enriched C4.5

Full enriched C4.5, after decorated numeric guard:

- Cases: 8
- Composer calls: 8
- Safety-valid cases: 7/8
- Safe public deltas: 4
- Unsafe public deltas: 1

Strict lane-only C4.7:

- Cases with strict lane opportunities: 5
- Composer calls: 5
- Safety-valid cases: 4/5
- Safe public deltas: 0
- Unsafe public deltas: 1

The strict lane-only arm did not recover hidden safe value when enhanced
opportunities were removed. It mostly chose no delta, and its only attempted
public delta was unsafe.

This strengthens the C4.6 finding: the safe incremental public value in these
tests came from the v60 enrichment path, especially embedding absence and
embedding affordance recall, not from strict lane-only opportunities.

## Validator Finding

C4.7 also improved the deterministic safety layer.

The first numeric guard compared bare numbers and could miss cases where a
number appeared in one unit but was newly used in another. For example, `$20K`
in the prompt should not authorize `20%` in a public delta.

The guard now tracks decorated numeric claims separately:

- percentages such as `20%`;
- money ranges such as `$12-24K`;
- plain numbers without treating `m` from "months" as a magnitude suffix.

This is important for live-readiness later. The system needs claim-shape guards,
not only raw token guards.

## Product Interpretation

The lane system remains essential. It provides provenance, stabilizes the
candidate field, and gives the system a deterministic spine.

But strict lane-only opportunities did not produce safe visible incremental
value in this test. The value came when the lane spine was enriched by exact v60
chunks retrieved through embedding/absence/hybrid paths.

The product architecture should therefore be:

1. Keep lanes as the provenance backbone.
2. Add v60 exact chunk enrichment after nomination.
3. Use embeddings as low-trust contextual recall.
4. Reserve absence slots because absence records produced real value.
5. Keep private chunk-level consideration.
6. Feed only distilled opportunities to the composer.
7. Validate public deltas aggressively.

## Recommendation

Merge recommendation:

- Yes for dormant/shadow lab infrastructure, after normal review.
- No for live `/lolla` answer behavior.

I would treat the dormant system-bound v60 layer as merge-ready for review now.
It gives us a useful testing and shadow-evaluation instrument without promoting
v60 into runtime behavior.

Live product integration still needs:

- broader shadow replay;
- latency/cost profiling;
- stronger claim-safety checks beyond numeric novelty;
- policy work on when absence slots increase;
- a promotion gate from private opportunity to public delta.

The key product decision is no longer "is this worth testing?" It is. The next
decision is how to merge the dormant machinery cleanly without creating the
impression that v60 is already live behavior.
