# Decision Work Brief Markdown Renderer v0

Status: PR117 deterministic renderer; PR123 plain-language patch
Date: 2026-07-01
Input schema: `lolla.decision_work_brief.v0`

## Purpose

PR117 adds a deterministic Markdown renderer for existing Decision Work Brief
JSON. PR123 patches that renderer so the main body reads as a plain-language
decision brief before the evidence appendix.

It answers a narrow implementation question:

> Can an already structured `lolla.decision_work_brief.v0` object be made
> readable without changing its meaning, hiding uncertainty, or implying product
> proof?

The renderer is not a generator. It does not fill missing semantic sections,
interpret messy conversation, call models, run Lolla, mutate archives, or judge
answer quality.

## Relationship To Earlier Slices

The Decision Work Brief lane now has these layers:

```text
PR114 schema contract
  -> PR115 local packet builder
  -> PR116 one-case provisional draft pilot
  -> PR117 Markdown renderer
```

PR117 consumes an existing brief-shaped object. For the checked-in pilots, that
object is embedded inside:

- [`review.json`](../../reviews/codex-assisted/decision-work-brief-draft-pilot-v0/review.json)
- [`review.json`](../../reviews/codex-assisted/decision-work-brief-second-tiny-case-pilot-v0/review.json)
- [`review.json`](../../reviews/codex-assisted/decision-work-brief-third-diversity-case-pilot-v0/review.json)

The renderer does not inspect raw run archives or local-private packet text.

## CLI Usage

Render a standalone brief JSON:

```bash
python3 scripts/evals/render_decision_work_brief.py \
  --brief <decision-work-brief-json> \
  --out <markdown-path>
```

Render the first embedded brief from a checked-in pilot review:

```bash
python3 scripts/evals/render_decision_work_brief.py \
  --pilot-review reviews/codex-assisted/decision-work-brief-draft-pilot-v0/review.json \
  --brief-index 0 \
  --out /tmp/decision-work-brief.md
```

The `--pilot-review` path is a convenience for the PR116, PR119, and PR121A
checked-in review shapes. It still renders only the embedded
`lolla.decision_work_brief.v0` object.

## Markdown Shape

Rendered Markdown starts with the decision story, not artifact inventory:

```text
# Decision Work Brief

opening non-claim note

## The decision
## What changed
## What this means for action
## What still might be wrong
## What this does not prove
## Evidence and limits
```

The main body answers the user-facing decision questions first. Source refs,
section uncertainty, custody flags, and non-claims are preserved in "Evidence
and limits" so a reader can see the limits without having the story interrupted
by status mechanics.

## Rendering Rules

The renderer:

- accepts only `lolla.decision_work_brief.v0`;
- requires all eight PR114 brief sections;
- renders existing section values from structured fields without changing their
  meaning;
- maps the eight schema sections into six plain-language headings;
- keeps status vocabulary out of the main body unless a section is missing,
  unclear, or requires review;
- renders source refs in compact artifact/field/status form under "Evidence and
  limits";
- renders non-claims under "Evidence and limits";
- renders custody flags including human validation, product proof,
  answer-quality scoring, agent action authorization, runtime invocation, skill
  invocation, archive mutation, model calls, source mode, raw/private content,
  and provider-text inclusion;
- renders `not_supplied`, `unclear`, `requires_human_review`, and
  `requires_llm_interpretation` plainly instead of smoothing them into prose.

The renderer does not treat empty values as absence of a problem. If a value is
missing, the Markdown says the value was not supplied and includes the section's
`empty_meaning`.

## Input Validation

The CLI returns a sanitized error when:

- JSON is malformed;
- the JSON root is not an object;
- the schema version is unsupported;
- required brief sections are missing;
- the PR116, PR119, or PR121A pilot wrapper does not contain an embedded brief
  at the requested index.

Errors avoid printing local absolute paths where the renderer can avoid them.

## Checked-In Examples

PR117 includes one checked-in-safe rendered example from the PR116 pilot:

- [Decision Work Brief Rendered Example: CEO Remove Founding Cofounder](decision-work-brief-rendered-ceo-remove-founding-cofounder-v0.md)

PR119 adds a second checked-in-safe rendered example from the second tiny case:

- [Decision Work Brief Rendered Example: Launch Public Enterprise Beta](decision-work-brief-rendered-launch-public-enterprise-beta-v0.md)

PR121A adds a third checked-in-safe rendered example from the third diversity
case:

- [Decision Work Brief Rendered Example: Deploy Assisted Intake Routing](decision-work-brief-rendered-deploy-assisted-intake-routing-v0.md)

All examples are kept under `docs/conversation-understanding/`, not the board,
because they are still provisional internal product-shape artifacts rather than
customer demos.

PR123 regenerates all three examples with the plain-language renderer patch.

## Boundary

PR117 does not:

- run `$lolla`;
- invoke the Lolla skill;
- call providers or model APIs;
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
- infer missing semantic content;
- claim product proof;
- treat clean artifacts as proof of good advice;
- implement PR118 usefulness review.

PR123 keeps those same boundaries and also does not create new case pilots or
broaden to a batch.

## Follow-On Review

PR118 has now reviewed the rendered example:

```text
PR118 Decision Work Brief Usefulness Review And Delivery Gate v0
```

See:

- [Decision Work Brief Usefulness Review v0](decision-work-brief-usefulness-review-v0.md)

PR118 asked whether the rendered brief actually answers:

```text
What did this process make me see or do differently?
```

It compared the receipt debug summary, PR116 structured brief draft, and PR117
rendered Markdown without declaring product readiness. The gate outcome is:

```text
proceed_to_tiny_second_case
```

Recommended next slice:

```text
PR119 Decision Work Brief Second Tiny Case Pilot v0
```

PR119 has now added that second case and selected:

```text
proceed_to_small_pattern_review
```

Recommended next slice:

```text
PR120 Decision Work Brief Small Pattern Review v0
```

PR120 has now selected `proceed_to_third_diversity_case`, and PR121A has added
the third checked-in-safe rendered example. PR121A selected:

```text
proceed_to_three_case_pattern_review
```

Recommended next slice:

```text
PR122 Decision Work Brief Three-Case Pattern Review v0
```

PR122 has now completed that review. It found a consistent
action-consequence signal across the cofounder, launch-beta, and intake-routing
briefs, but chose:

```text
proceed_to_plain_language_renderer_patch
```

That means the renderer's deterministic behavior remains useful, but the next
slice should make the main Markdown body sound less like schema/custody
machinery and more like a plain decision brief while preserving source status,
uncertainty, custody flags, and non-claims.

PR123 has now completed that patch:

```text
PR123 Decision Work Brief Plain-Language Renderer Patch v0
```

See:

- [Decision Work Brief Plain-Language Renderer Patch v0](decision-work-brief-plain-language-renderer-patch-v0.md)

The next recommended slice is:

```text
PR124 Plain-Language Brief Re-Review v0
```

The re-review should verify whether the regenerated examples actually read
better before moving to local-private adequacy checks, more cases, or any
runtime planning.
