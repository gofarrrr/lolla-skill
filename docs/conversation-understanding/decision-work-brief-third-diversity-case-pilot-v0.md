# Decision Work Brief Third Diversity Case Pilot v0

Status: PR121A third diversity case pilot
Date: 2026-07-01
Schema: `lolla.decision_work_brief_third_diversity_case_pilot.v0`

## Purpose

PR121A follows the PR120 gate:

```text
proceed_to_third_diversity_case
```

It runs exactly one more checked-in-safe Decision Work Brief pilot on a third
decision type. It does not implement any other PR121 path.

The review question is:

> Does the Decision Work Brief still name a concrete action consequence in a
> healthcare operations deployment decision, without hiding uncertainty or source
> thinness?

The provisional answer is yes. The third case again names an action consequence
and preserves uncertainty. It is not product proof, human validation, answer
quality measurement, runtime integration, or evidence that Lolla improved the
decision as fact.

## Selected Case

PR121A uses:

```text
deploy-assisted-intake-routing/20260627T130339Z_4cd3cb
```

This was the preferred candidate from PR120's gate because it was available as a
completed run and differs from the first two cases:

- `ceo-remove-founding-cofounder`: founder governance and operating authority;
- `launch-public-enterprise-beta`: enterprise launch timing and buyer
  selection;
- `deploy-assisted-intake-routing`: healthcare workflow deployment under
  compliance, staff-capacity, sales, and patient-risk constraints.

No fourth case or batch was created.

## Inputs

PR121A generated local metadata-only support artifacts from the completed run:

- a Decision Trail report;
- a Decision Work Receipt;
- a Decision Work Brief packet with
  `schema_version: lolla.decision_work_brief_packets.v0`;
- a temporary standalone `lolla.decision_work_brief.v0` JSON extracted from the
  review artifact for rendering.

Only the sanitized review JSON and rendered Markdown example are checked in:

- [`review.json`](../../reviews/codex-assisted/decision-work-brief-third-diversity-case-pilot-v0/review.json)
- [Decision Work Brief Rendered Example: Deploy Assisted Intake Routing](decision-work-brief-rendered-deploy-assisted-intake-routing-v0.md)

The generated metadata-only packet and temporary support reports were not
checked in. No local-private include-text packet was used.

## Third Brief Summary

The third draft brief names the decision as whether to deploy an AI-assisted
intake routing feature in outpatient clinics next month despite operational,
compliance, sales, and staff-capacity constraints.

The provisional action consequence is:

```text
Before go-live, run a 48-hour bottleneck check, keep the pilot to one clinic
and scheduling/billing routing, require four operating gates, and predefine
pause triggers instead of treating the AI pilot as the backlog solution.
```

The useful signal is that the brief distinguishes "more safeguards" from an
operable control system. It says the decision-maker should reduce the
nine-gate burden, diagnose the actual backlog cause, and define stop conditions
that tired staff can actually run.

## What Stayed Uncertain

The third case remains source-limited:

- raw conversation, revised answer, memo, live transcript, provider text, and
  private ledgers are absent from the checked-in artifact;
- the actual clinic backlog cause is not verified here;
- admin ability to operate even four gates is not verified here;
- compliance may still require two months before even a narrowed pilot;
- the nine-gate format may have contained useful patient-trust, support, or
  measurement controls that should not be lost.

The brief keeps those risks visible.

## Comparison To Prior Cases

Across three cases, the brief shape now names concrete action consequence in
three different decision families:

- cofounder authority: move authority first, narrow transition support, and set
  stop conditions;
- enterprise launch: equalize paid/scoped private pilot offers and choose based
  on buyer behavior plus tripwire gates;
- healthcare workflow deployment: diagnose backlog cause, compress controls
  into four operating gates, and pause on credible clinician-attention misroute.

That is a useful product-shape signal. It is still only a Codex-assisted,
checked-in-safe signal.

The renderer remains adequate for internal review, but the field labels and
source refs still read as internal machinery. A three-case pattern review should
decide whether the next move is a language patch, local-private adequacy check,
human review pause, or simplification.

## Decision Gate

PR121A chooses:

```text
proceed_to_three_case_pattern_review
```

This means the next step should review all three checked-in-safe rendered briefs
before any fourth case, renderer patch, local-private adequacy check, or human
review pause.

Rejected outcomes:

- `proceed_to_renderer_language_patch`: likely needed soon, but the three-case
  pattern should be reviewed first.
- `proceed_to_local_private_adequacy_check`: important later, but PR121A did not
  implement local-private review.
- `pause_until_human_review`: human review remains necessary eventually, but the
  three-case pattern can be assessed first.
- `stop_and_simplify`: too harsh; the third brief also answers what action
  would change.

PR121A does not recommend runtime integration.

## Boundary

PR121A does not:

- run `$lolla`;
- invoke the Lolla skill;
- call providers or model APIs from repo code;
- mutate archives;
- change runtime behavior;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- add model-call code;
- add a broad judge;
- measure answer quality;
- create automatic labels;
- authorize agent action;
- claim product proof;
- add graph, memory, embedding, chunking, or GraphRAG work;
- integrate the brief into runtime;
- create a dashboard;
- broaden to a batch;
- create customer marketing copy.

## Recommended Next Slice

Recommended next slice:

```text
PR122 Decision Work Brief Three-Case Pattern Review v0
```

PR122 should review the three rendered briefs together and decide whether the
next responsible move is a renderer language patch, local-private adequacy
check, human review pause, or simplification. It should not add runtime
integration.

## Follow-On Status

PR122 has now completed that three-case review:

- [Decision Work Brief Three-Case Pattern Review v0](decision-work-brief-three-case-pattern-review-v0.md)

It found that all three rendered briefs name concrete action consequences and
preserve uncertainty/non-claims, but the current Markdown still exposes too
much schema and custody machinery in the main reading flow. PR122 therefore
chooses:

```text
proceed_to_plain_language_renderer_patch
```

The next responsible slice is PR123 Decision Work Brief Plain-Language Renderer
Patch v0, not a five-case batch or runtime integration.

## Non-Claims

PR121A is not:

- human review;
- ground truth;
- product proof;
- answer-quality measurement;
- automatic labeling;
- runtime integration;
- a broad judge;
- evidence that clean rendered briefs mean good advice;
- agent action authorization;
- general evidence from three cases.
