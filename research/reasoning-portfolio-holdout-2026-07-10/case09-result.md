# Case09 holdout result

## Bottom line

Case09 is a bounded, inconclusive result with a real additive-pressure signal. The pipeline is now operationally affordable enough to study on a long conversation, and Lolla surfaced two plausible pressures that the strong transcript-only control did not fully recover. We did **not** test whether a portfolio-fed agent would use those pressures, because the downstream treatment call was not fully frozen before the control. No runtime integration is authorized.

## What worked

- Fresh extraction preserved all 44 messages and verified all six reasoning quotations with zero fabrication and no repair call.
- The pipeline stayed inside every frozen ceiling: 32 OpenRouter calls total, 19 core-pressure calls, 12 Bullshit Index calls, one extraction call, seven OpenAI embedding/query-expansion calls, no revision, no experiment retry, and an estimated total cost of $0.057738.
- The new Bullshit Index cap materially repaired the Case07 operability problem: 12 evaluations rather than 34. All 66 source passages were retained through deterministic adjacent merging into 12 evaluation passages.
- The private table was ready at 4,232 characters with 14 source items. V60 selected eight cards and produced a 16-transaction v2 ledger skeleton.
- Provider separation behaved as intended: the reasoning pipeline used OpenRouter; five embeddings and two query-expansion requests went directly to OpenAI using `OPENAI_API_KEY`. Automatic mode disables embeddings when that key is empty.

## What remained imperfect

- One of the twelve Bullshit Index evaluations returned an empty result, so run health is correctly `partial`. This was not a frozen stop condition and is carried as a limitation.
- The strong control output used bullet-delimited strings for several fields that would be cleaner as arrays. The frozen output contract required exact keys but had not declared field types. The response remained semantically reviewable, but future contracts must be typed.
- A candidate/model count did not establish novelty. The preliminary pass depended on four traced pressures with plausible consequences.

## What the strong control found without Lolla

The one-call, no-retry control independently did most of the important corrective work:

- treated Option 3 as contingent rather than inherently smart or ambitious;
- set aside invented probabilities, market claims, reviewer assumptions, and stakeholder motives;
- made actual data access, advisor support, and feasibility the decision gates;
- withdrew the fixed 18-month checkpoint;
- preserved fallback and second-faculty redundancy.

This is important evidence against an inflated Lolla claim. A strong fresh LLM rereading the complete conversation is already a powerful baseline.

## What Lolla may have added

Two trace-supported pressures remained absent or materially incomplete in the control:

1. **Two-sided regret.** The control removed the “smart versus ambitious” conclusion but never examined regret of omission and regret of action together with downside, reversibility, and option expansion. This could prevent Option 1 from being mislabeled as fear and expose which failure the user can actually absorb.
2. **Durable role and continuity design.** The control asked what collaboration would require, but did not turn it into PI-level sponsorship, responsibility and handoff ownership, minimum adjacent competence, and a plan for a postdoc or priority change. This could make collaboration durability an evidence gate rather than an assumption.

The semantic threshold for a consumer test was therefore met: two distinct traced pressures, both with plausible action or guardrail consequences.

## Why we stopped anyway

The frozen Case09 contract specified when a portfolio-consumer call would be justified, but did not freeze that call's provider/model, prompt construction, cap, and typed output schema. It also forbade changing the source, prompt, model, cap, or contract after the first call. Creating a treatment arm after reading the control would move the goalposts.

So no portfolio-consumer call was made. This is an evaluation-design failure, not a pipeline failure and not proof of product value.

## Prospective repair

The next untouched holdout should use two frozen stages:

1. Freeze and run the pipeline admission contract.
2. If admitted, build and hash-lock a paired downstream contract **before either downstream call**. Control and treatment must share the model, system prompt, neutral instruction, typed output schema, and output cap; only the treatment receives the source-traceable pressure packet.

Case09 will not be rerun. The next experiment should test whether the two types of incremental pressure visible here survive actual model consumption without forcing, bloat, or loss of good original reasoning.

## Artifacts

- `case09-contract.json`: frozen pre-call rules and budgets.
- `pipeline-gate-result.json`: passed mechanical and operability gates.
- `private-table-snapshot.json` and `v60-snapshot.json`: review-safe pipeline surfaces.
- `preliminary-novelty-review.json`: trace-based authorization for the strong control.
- `strong-control-result.json`: one-call transcript-only reconsideration.
- `control-comparison.json`: pressure-by-pressure comparison and the downstream execution stop.

These artifacts support a process claim only: Lolla can preserve a long conversation, run a bounded hybrid audit, and expose candidate pressure with inspectable traces. They do not support a better-answer or proof-of-reasoning claim.

## Verification

- 37 focused sealer, control-runner, paired-pilot, Bullshit Index, and V60 tests passed.
- The full non-network suite passed: 3,931 tests, one expected skip, and 93 subtests.
- Python compilation, JSON parsing, absolute-path/credential scans of the Case09 package, and `git diff --check` passed.
