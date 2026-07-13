# Case 07 Full-Surface Portfolio Diagnostic

Date: 2026-07-10  
Status: frozen pipeline contract failed; stopped before consumer call  
Experiment retries: 0  
Human review: pending

## Outcome

The run completed cleanly but failed the predeclared operability gate:

- OpenRouter calls: 51;
- frozen ceiling: 40;
- OpenAI embedding/expansion calls: 7;
- calls with known prices: 58;
- estimated total cost: $0.048731;
- run health: healthy;
- captured turns: 22 / 22;
- quote fabrication: 0;
- private table: ready, 4,794 characters, 12 source items;
- V60: active, 8 cards, 16 chunks;
- V60 ledger skeleton: `v60_skill_consideration_ledger.v2`.

Low monetary cost does not override the call-count failure. The frozen contract
required a stop before any portfolio-consumer call, so no revised answer or
private dispositions were generated and the case was not rerun.

## Why The Call Ceiling Failed

The Bullshit Index made 34 of the 51 OpenRouter calls. The rest of the pipeline
used 17 calls across the six first-pass clusters, four second-pass checks,
frame work, companion work, and structural coverage.

This is a useful architecture finding. A peripheral detector scaled with the
length and paragraph structure of the entire multi-turn assistant transcript,
while the core pressure lanes did not. The run therefore failed operability
even though provider cost and artifact health looked acceptable.

## Semantic Novelty Gate

The result also failed the planned novelty gate independently of call volume.

The private table mostly preserved or confirmed the existing assistant frame:

- optionality confirmed the short-term-rental decoupling;
- active listening confirmed the concrete boyfriend conversation;
- constraints confirmed that the apartment deadline is narrower than the life
  decision;
- cognitive-load pressure confirmed the assistant's three-decision
  organization;
- the one frame item again focused on temporal decoupling;
- coverage focused on resource allocation.

The V60 layer added regret theory, sunk-cost fallacy, calculated risk taking,
and endowment effect. These are different labels, but they did not clear the
predeclared bar for two unhandled pressures with a plausible new decision
consequence:

- the existing strong control already recovered that Seattle remained
  undecided;
- it explicitly rejected the assistant's implied preference for Seattle;
- it separated preference from boyfriend, mother-care, employer, and housing
  feasibility;
- it preserved DC attachment as underexplored;
- it softened unsupported medical and employer certainty;
- it gave the same practical next actions without deciding for the user.

Sunk-cost and endowment lenses are especially dangerous here. Eleven years in
DC, a relationship, community, and proximity to a mother who may need care are
not automatically irrational attachment to an owned option. Forcing those
lenses could discount the user's real values and nudge the answer toward
Seattle. They may be useful only as carefully bounded questions, not as
corrections.

## False-Stand-Down Read

The full transcript still contains the user's decisive self-correction: she
keeps telling herself she chose Seattle but has not. The generated private
table does not make that correction active. It also does not directly
challenge the earlier assistant's “Seattle is the root decision” frame.

That is a real attention risk, but not proof of a failed answer. Step 6 would
still receive the authoritative full conversation, and the prior strong
control recovered the correction without an overlay. Because the consumer
call was correctly blocked, this experiment cannot say whether Step 6 would
have followed the transcript or the more confirming private table.

The responsible conclusion is:

```text
raw custody survived;
the private table may still overrepresent the prior assistant frame;
no observed consumer failure or success exists for this run.
```

## Repair Made Prospectively

The Bullshit Index now caps evaluation at 12 calls. When its ordinary passage
split exceeds 12, adjacent passages are merged deterministically:

- every source passage remains present exactly once and in order;
- no relevance classifier decides what to drop;
- evaluation localization becomes coarser;
- telemetry records source passage count, evaluation passage count, the cap,
  and whether compaction occurred.

This is a bounded operability repair, not a reasoning-quality change. The
failed Case 07 experiment remains failed and will not be rerun after the code
change.

## Preserved Evidence

The checked-in research folder contains:

- the frozen contract;
- a deterministic failed-gate receipt;
- a review-safe private-table snapshot without raw table prose or absolute
  paths;
- a review-safe V60 snapshot and v2 ledger skeleton;
- this provisional review.

The raw pipeline result remains local-only and is identified by SHA-256 in the
gate receipt. It is not checked in because the generated artifact contains a
machine-specific absolute substrate path.

Local verification after the repair:

- 68 focused portfolio, V60, Bullshit Index, pipeline, graph, doctrine, and
  downstream tests passed;
- 3,925 non-network repository tests passed, with 1 expected skip and 93
  subtests;
- JSON parsing, Python compilation, privacy scans, and `git diff --check`
  passed for the new review-safe artifacts.

## Next Decision

Do not spend another call on Case 07. It already tells us three important
things:

1. full semantic overlays can distort attention;
2. the current private table can still lean toward confirming the prior
   assistant's organization;
3. peripheral detectors can dominate run operability unless explicitly
   bounded.

The next test should use an untouched holdout case after local verification of
the BI ceiling. Its contract should keep the same strong baseline and portfolio
novelty bar, but set separate ceilings for core pressure calls and peripheral
post-processing calls so one stage cannot hide inside a total.
