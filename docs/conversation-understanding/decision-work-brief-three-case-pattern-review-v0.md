# Decision Work Brief Three-Case Pattern Review v0

Status: PR122 three-case pattern review
Date: 2026-07-01
Schema: `lolla.decision_work_brief_three_case_pattern_review.v0`

## Purpose

PR122 reviews the first three checked-in-safe Decision Work Brief pilots and
decides what blocks the brief from becoming more user-facing.

The product question is:

> Across three different tiny pilots, does the Decision Work Brief consistently
> help a user understand what the Lolla process changed for action, while
> preserving uncertainty and avoiding false confidence?

The answer is: yes on action consequence, not yet on presentation. The brief
shape is useful, but the rendered language is still too field-label-heavy and
machinery-flavored for a board/customer reader.

## Cases Reviewed

PR122 reviews exactly three existing cases. It creates no fourth case.

1. `ceo-remove-founding-cofounder/20260627T093131Z_59d153`

   The brief names a governance action consequence: move product authority
   first, narrow the cofounder's transition support, and set stop conditions
   before the hard conversation.

2. `launch-public-enterprise-beta/20260627T104146Z_7bfe79`

   The brief names a go-to-market action consequence: stop defaulting to the
   largest logo or public launch, give both prospects the same paid and scoped
   private-pilot offer, and choose based on proof-producing buyer behavior.

3. `deploy-assisted-intake-routing/20260627T130339Z_4cd3cb`

   The brief names an operations action consequence: run a backlog diagnostic,
   compress nine gates into four operating gates, set hard pause triggers, and
   narrow what the pilot proves.

The durable review artifact is:

- [`review.json`](../../reviews/codex-assisted/decision-work-brief-three-case-pattern-review-v0/review.json)

## What The Three Briefs Show

The strongest useful signal is consistent action consequence.

Across three different decision families, the Decision Work Brief answers:

```text
What would I do differently now?
```

The answers are not generic caution. They are specific to the decision family:

- founder governance: authority, transition role, stop conditions;
- enterprise launch: buyer behavior, paid scope, public launch restraint;
- healthcare operations: backlog cause, operable controls, pause triggers.

That is the product value beginning to appear. The brief is useful because it
explains decision work, not because it displays internal artifacts.

## What The Three Briefs Do Not Show

The three briefs do not prove Lolla improved the decisions.

They remain:

- Codex-assisted;
- checked-in-safe;
- non-human-validated;
- source-limited;
- not answer-quality measurements;
- not agent action authorizations;
- not product proof.

The checked-in-safe context cannot verify:

- starting direction and original/revised overlap;
- user intent;
- private nuance;
- lost value or possible overcorrection;
- buyer reality;
- compliance tolerance;
- legal, governance, relationship, or patient-risk constraints.

That means the action-consequence pattern is promising, but not enough for
runtime integration or customer-facing claims.

## Main Blocker

The main blocker is now language and presentation.

The current renderer preserves source status, uncertainty, non-claims, and
custody flags, which is good. But it also exposes too much internal structure
in the main reading flow:

- backtick field labels such as `decision_story_read` and
  `action_consequence`;
- status and source-status lines before each story section;
- source refs and artifact names near the body of the decision story;
- a source/custody appendix that is necessary but still feels more like a
  maintainer artifact than a reader aid.

The brief body is close to useful. The rendered surface is not yet plain enough.

## Pattern Read

PR122 selects:

```text
useful_but_language_too_internal
```

This is different from saying the brief is not useful. The brief is useful
because it makes action consequence visible. The problem is that the current
Markdown still asks a reader to tolerate schema-shaped prose.

## Decision Gate

PR122 chooses:

```text
proceed_to_plain_language_renderer_patch
```

This means the next slice should patch the renderer before adding more cases.

Rejected outcomes:

- `proceed_to_five_case_brief_batch`: more cases would multiply examples that
  still look too internal.
- `proceed_to_local_private_adequacy_check`: important later, but the current
  checked-in examples already reveal a surface-language blocker.
- `pause_until_human_review`: reasonable eventually, but the renderer issue is
  concrete enough to fix first.
- `stop_and_simplify`: too harsh; the brief format is useful enough to repair.

PR122 does not recommend runtime integration.

## What The Renderer Patch Should Do

The next slice should make the rendered brief read like a decision brief first
and an evidence appendix second.

It should preserve:

- uncertainty;
- non-claims;
- human-validation state;
- product-proof false;
- answer-quality-scored false;
- agent-action-authorized false;
- source status;
- custody limits.

It should change the reading flow:

- start with the decision and action consequence in plain language;
- remove schema-like field labels from the main body;
- avoid status vocabulary in the main story unless a section is missing or
  requires review;
- move source refs, statuses, and custody details into a compact Evidence and
  Limits appendix;
- keep missingness and uncertainty visible without making the body feel like an
  artifact dump.

## Boundary

PR122 does not:

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
- create a fourth case.

## Recommended Next Slice

Recommended next slice:

```text
PR123 Decision Work Brief Plain-Language Renderer Patch v0
```

PR123 should patch the renderer so the main body reads as a plain-language
decision brief while preserving uncertainty, source status, custody flags, and
non-claims in a compact Evidence and Limits section.

## Follow-On Status

PR123 has now completed that renderer patch:

- [Decision Work Brief Plain-Language Renderer Patch v0](decision-work-brief-plain-language-renderer-patch-v0.md)

It regenerates the three existing rendered examples with a plain-language main
body and a compact "Evidence and limits" section. PR124 then confirms the
surface is readable enough for source-depth comparison:

- [Decision Work Brief Plain-Language Re-Review v0](decision-work-brief-plain-language-rereview-v0.md)

PR125 completes one launch-beta local-private shadow review by checked-in-safe
conclusions only:

- [Decision Work Brief Local-Private Adequacy Check v0](decision-work-brief-local-private-adequacy-check-v0.md)

PR126 selects more local-private adequacy checks rather than runtime
attachment:

- [Decision Work Brief Expansion / Runtime Attachment Decision Gate v0](decision-work-brief-expansion-runtime-decision-gate-v0.md)

The next responsible slice is:

```text
PR127 Decision Work Brief Additional Local-Private Adequacy Checks v0
```

That re-review should decide whether the regenerated examples actually read
better before moving to local-private adequacy checks, more cases, or runtime
planning.

## Non-Claims

PR122 is not:

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
