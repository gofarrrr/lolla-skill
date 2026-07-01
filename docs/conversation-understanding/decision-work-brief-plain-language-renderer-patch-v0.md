# Decision Work Brief Plain-Language Renderer Patch v0

Status: PR123 renderer readability patch
Date: 2026-07-01

## Purpose

PR123 answers the PR122 gate:

```text
proceed_to_plain_language_renderer_patch
```

The three-case pattern review found that the Decision Work Brief shape is
useful because it consistently names action consequence across three different
decision families. The blocker was presentation: the rendered Markdown still
read too much like an internal artifact inspection packet.

PR123 patches the deterministic renderer so the top of the brief reads like a
decision brief first and an evidence appendix second.

## What Changed

The renderer now uses a plain-language main flow:

- The decision
- What changed
- What this means for action
- What still might be wrong
- What this does not prove
- Evidence and limits

The renderer still consumes the same `lolla.decision_work_brief.v0` JSON
contract. It does not change the schema, fill missing sections, call models,
run Lolla, inspect archives, or infer new semantic content.

The mapping is:

- `decision` renders under "The decision";
- `starting_direction`, `what_lolla_pressed_on`, and `what_changed` render
  together under "What changed";
- `what_this_means_for_action` renders under "What this means for action";
- `what_still_might_be_wrong` renders under "What still might be wrong";
- `what_was_not_proven` renders under "What this does not prove";
- `evidence_receipt`, source refs, uncertainty, custody flags, and non-claims
  render under "Evidence and limits".

## Regenerated Examples

PR123 regenerates the three existing checked-in examples only:

- [Decision Work Brief Rendered Example: CEO Remove Founding Cofounder](decision-work-brief-rendered-ceo-remove-founding-cofounder-v0.md)
- [Decision Work Brief Rendered Example: Launch Public Enterprise Beta](decision-work-brief-rendered-launch-public-enterprise-beta-v0.md)
- [Decision Work Brief Rendered Example: Deploy Assisted Intake Routing](decision-work-brief-rendered-deploy-assisted-intake-routing-v0.md)

It does not create a fourth case.

## What The Main Body Improves

The main body now starts with the decision and the action consequence instead
of repeated section status, source status, source refs, and custody flags.

That makes the artifact easier for a busy decision-maker to scan:

- what decision was being made;
- what changed;
- what action would be different now;
- what still might be wrong;
- what was not proven.

The strongest readability improvement is that source refs and custody mechanics
no longer interrupt every story section.

## What Is Still Preserved

The "Evidence and limits" section still shows:

- human validation status;
- product-proof status;
- answer-quality scoring status;
- agent-action authorization status;
- runtime and skill invocation status;
- model-call count;
- source mode;
- private/raw content inclusion status;
- provider text inclusion status;
- section uncertainty;
- compact source references;
- explicit non-claims.

Missingness and uncertainty remain visible. If a section is missing, unclear,
or requires review, the renderer states that plainly instead of smoothing it
into confident prose.

## Remaining Risks

The strongest source-depth risk remains unchanged: checked-in-safe examples
cannot verify private nuance, original/revised overlap, user intent, lost value,
buyer reality, compliance tolerance, or relationship/legal constraints.

The strongest overclaim risk also remains: cleaner prose can feel more
validated than it is. The renderer patch makes the brief easier to read; it
does not make the interpretation human validated or product proof.

## Boundary

PR123 does not:

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
- create new case pilots;
- broaden to a batch;
- remove uncertainty, source limits, custody, or non-claims.

## Recommended Next Slice

Recommended next slice:

```text
PR124 Plain-Language Brief Re-Review v0
```

The next step should review whether the regenerated examples actually read
better for a product/board/customer reader before moving to local-private
adequacy checks or more cases.

## Follow-On Status

PR124 has now completed that rereview:

- [Decision Work Brief Plain-Language Re-Review v0](decision-work-brief-plain-language-rereview-v0.md)

It finds the patched surface readable enough for local-private adequacy
comparison and gates to PR125. PR125 then completes one launch-beta
local-private shadow review by checked-in-safe conclusions only. PR126 selects
more local-private adequacy checks next, not runtime integration.

## Non-Claims

PR123 is not:

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
