# PR62 Targeted v24 Guard Enrichment Report

Date: 2026-05-08

## Verdict

REVISE before runtime pickup. PASS as dormant reviewed substrate.

PR62 adds eight source-backed absence records and zero positive affordances. The goal is not to make v18/v24 louder. The goal is to make future packet pickup harder to misuse by adding first-class reject/defer rails where the source already warns that a plausible use would be overclaimed.

## Contradicting Evidence First

The uncomfortable evidence is that several current cards already mention parts of these warnings in `do_not_use_when`, misuse guards, or review notes. Turning them into absence records can look like redundancy if absence is treated as another place to restate cautions.

That is why PR62 uses a stricter criterion:

> Add an absence only when it changes a future card transaction: use, reject, defer, or block overclaim.

Under that criterion, PR62 does not expand affordance counts. It promotes eight missing no-promote boundaries to first-class absence records because they are likely to matter when a decoder has to say why a nominated card should not be used.

## What Changed

Compiled artifact:

- `model_affordances_v24`
- `affordance_count`: unchanged at 268
- `absence_record_count`: 441 to 449
- `contributing_record_count`: unchanged at 222
- runtime status: dormant `draft_review_only`

Added absence records:

- `anchoring`: `audience-anchor-without-shared-schema`
- `multi-criteria-decision-analysis`: `matrix-output-without-frontline-decision-rule`
- `second-order-thinking`: `linear-blueprint-without-human-system-data`
- `optionality`: `team-option-set-after-shared-anchor`
- `systems-thinking`: `system-redesign-without-observed-behavior`
- `confidence-calibration`: `calibration-as-bias-immunity`
- `confidence-calibration`: `domain-calibration-transfer-without-domain-evidence`
- `inversion`: `externalized-failure-without-internal-cause`

## Why These Guards

The shared pattern is that each guard blocks a future decoder from treating a useful reasoning model as valid when a source-named precondition is missing.

`anchoring` now blocks expert-owned anchors that do not fit the audience's schema. The existing card handled provisional correction, but the source's curse-of-knowledge warning is a distinct handoff failure: a reference point can be true, familiar to the expert, and still unusable by the audience.

`multi-criteria-decision-analysis` now blocks matrix theater as frontline guidance. The matrix can be valid as deliberation but still fail as a user-facing operating rule when the audience needs a simple decision heuristic.

`second-order-thinking` now blocks linear blueprints for living social systems. The existing card stresses dependencies and adaptation, but the source separately warns that feelings and actor experience are implementation data, not decoration.

`optionality` now blocks fake team optionality after the first salient proposal has already anchored the group. The current affordances already require 3+ options and commitment boundaries; this guard preserves the source's independent-judgment condition.

`systems-thinking` now blocks redesign/control moves that skip observation of current system behavior. This is a broad-card danger: systems language can sound wise while imposing will on a system that has not been listened to.

`confidence-calibration` now blocks two overclaims: calibration as bias immunity, and domain transfer of calibrated confidence without domain-matched evidence. Both are structured-tension warnings in the source and both would change future rejection behavior.

`inversion` now blocks failure analysis that externalizes all causes. Inversion should force accountability for internal defaults and decisions, not only list market, competitor, or luck explanations.

## Rejected Or Deferred

No positive affordances were added.

Several tempting additions were rejected or deferred because they would duplicate existing guard text without changing downstream behavior:

- `lindy-effect`: current record already treats age as a qualitative prior, not proof, and requires discontinuity checks.
- `premortem`: current record already blocks generic worry lists without owners, mitigations, or decision changes.
- `sunk-cost-fallacy`: current record already blocks reckless abandonment by requiring future marginal value, learning value, switching cost, and upside checks.

These may be revisited only if replay traces show the decoder overpromotes them despite existing guards.

## Risk Controls

PR62 intentionally keeps the runtime boundary unchanged:

- no `/lolla` pickup;
- no packet producer default change;
- no prompt changes;
- no automatic latest-artifact behavior;
- no compiled artifact import from live runtime paths.

The new test suite asserts that v24 is exactly v23 plus the eight absence records and no new affordance IDs.

## What Would Falsify This Pass

This pass should be revised if any of the following happen:

- v24 adds a positive affordance or changes affordance IDs;
- a source quote fails exact-source validation;
- a guard merely restates existing text without changing use/reject/defer behavior;
- v24 is imported by live runtime paths;
- weak or absence records become framed as endorsed positive uses in future packet rendering.

## Next Work

Continue corpus enrichment as small dormant guard or split-candidate PRs. The next slice should inspect the remaining zero-absence or broad/meta records with the same test:

> Would this source-backed distinction change a future decoder's card transaction?

If yes, add a tightly scoped absence or mark a split candidate. If no, leave the card compressed.
