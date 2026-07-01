# Decision Work Brief Offline Enriched Builder v0

Status: PR140 offline deterministic builder.

This builder applies the PR139 enrichment rules contract to an already-rendered
Decision Work Brief and an existing conversation interpretation read. It creates
a separate enriched Markdown file. It does not modify the original brief.

The builder is intentionally narrow. It does not interpret the conversation,
call a model, run Lolla, mutate archives, change runtime behavior, score answer
quality, authorize agent action, or claim product proof.

## Inputs

- Original rendered Decision Work Brief Markdown.
- Conversation interpretation read JSON.
- Enrichment rules contract JSON:
  `docs/conversation-understanding/decision-work-brief-enrichment-rules-contract-v0.json`

CLI shape:

```bash
python3 scripts/evals/enrich_decision_work_brief.py \
  --brief docs/conversation-understanding/decision-work-brief-rendered-launch-public-enterprise-beta-v0.md \
  --interpretation-read reviews/codex-assisted/decision-work-conversation-interpretation-tiny-offline-read-v0/read.json \
  --rules docs/conversation-understanding/decision-work-brief-enrichment-rules-contract-v0.json \
  --out /tmp/decision-work-brief-enriched-launch.md
```

## What It Does

The builder inserts or replaces exactly one section:

`## What the interpretation adds`

The section is generated from the existing interpretation read using
conservative templates. It may use only the PR139 user-facing field set:

- `decision_question`
- `likely_starting_direction`
- `revised_direction_or_action_consequence`
- `decision_thresholds`
- `evidence_gates`
- `useful_friction`
- `what_the_final_answer_does_not_prove`

The builder also adds a compact `Interpretation enrichment limits` subsection
under `Evidence and limits`. That subsection records source mode, excluded
evidence-only fields, uncertainty levels, compact source refs, and non-claims.

## What It Does Not Do

The builder does not use evidence-only fields in the main enrichment section.
Fields such as `live_options`, `abandoned_or_rejected_options`,
`noisy_friction`, and `lost_value` stay out of the main user-facing text.

The builder does not infer missing fields, decide whether the advice is good,
decide whether Lolla improved the decision, or treat useful friction as a
score. If the interpretation read marks a field as insufficient context, the
builder leaves it out of the user-facing enrichment section.

## Rejections

The CLI rejects:

- missing input files;
- unsupported interpretation read schema versions;
- unsupported enrichment rules schema versions;
- an output path equal to the input brief path;
- interpretation reads with non-conservative custody flags;
- rules contracts that allow evidence-only or forbidden fields in the
  user-facing enrichment section.

## Generated Examples

PR140 generated two checked-in-safe builder outputs, and PR142 regenerated them
after the builder-language patch:

- `docs/conversation-understanding/decision-work-brief-builder-enriched-launch-public-enterprise-beta-v0.md`
- `docs/conversation-understanding/decision-work-brief-builder-enriched-deploy-assisted-intake-routing-v0.md`

These are separate from the PR135 and PR137 hand-built enriched briefs. They
exist so PR141 can compare deterministic builder output against the hand-built
intent without overwriting either original rendered brief.

## Boundary

PR140 is offline and downstream only. It is not runtime integration, product
proof, human validation, answer-quality scoring, or agent action
authorization. Runtime invoked: no. Skill invoked: no. Model calls: 0.

## PR141 Output Review

PR141 compares the two builder-generated outputs against the earlier hand-built
enriched examples. The review finds the builder preserved the useful signal,
uncertainty, source limits, and non-claims, but the generated language is still
too repetitive and template-shaped.

Decision gate:

```text
proceed_to_builder_rule_patch
```

PR142 implements that patch and regenerates both builder outputs with less
repetitive wording while preserving the PR139 field boundary, source limits,
uncertainty, and non-claims.

## PR143-PR145 Closure

PR143 reviews the patched outputs and gates to PR144's offline-system closure
decision. PR144 selects `package_pr114_pr144`. PR145 packages the PR114-PR144
offline Decision Work Brief evidence surface with a manifest, validation
checklist, staging list, and do-not-stage warnings. None of these steps add
runtime integration, model calls, product proof, human validation, scoring, or
agent action authorization.

## PR146-PR150 Follow-Up

PR146 checks two more cases against local-private context and recommends a
third builder case. PR147 tries that cofounder builder case and blocks it
because the cofounder case has no builder-compatible interpretation read. The
builder should continue to reject unsupported schema shapes rather than convert
draft-pilot, pattern-review, or local-private adequacy review material into a
user-facing enrichment section.

PR147A then creates the missing formal-schema cofounder interpretation read.
That read is builder-compatible, but PR147A still does not create the third
builder-enriched Markdown output. Keeping the read and builder output separate
preserves the review boundary.

PR148 uses that read with the existing PR139 rules contract to create:

- `docs/conversation-understanding/decision-work-brief-builder-enriched-ceo-remove-founding-cofounder-v0.md`

The third builder output is readable enough for a pattern review and preserves
the same source-limit and non-claim boundary as the first two builder outputs.
It also exposes one remaining wording issue: the deterministic template can be
slightly visible when the interpreted decision-question value already starts
with decision-framing language.

PR149 then compares all three builder-generated enriched briefs. The review
finds the builder stable enough for offline evidence review across launch
timing, healthcare deployment controls, and founder governance. It does not
recommend another deterministic builder case before human input. The next
useful slice is a human-review intake plan, because the strongest remaining
risk is whether humans find the enriched briefs useful, bounded, and
appropriately caveated.

PR150 creates that intake plan. It names the three builder-generated enriched
briefs as review targets, defines reviewer questions and case forms, and sets
stop conditions for overtrust, source-depth gaps, private-context gaps, and
runtime attachment. It does not complete human review, claim product proof,
score answer quality, authorize agent action, or change the offline builder.
