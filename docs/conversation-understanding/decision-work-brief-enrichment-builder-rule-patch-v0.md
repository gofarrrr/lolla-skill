# Decision Work Brief Enrichment Builder Rule Patch v0

Status: PR142 deterministic builder language patch.

PR141 found that the offline enriched-brief builder was safe and rule-compliant,
but still too repetitive and template-shaped compared with the hand-built
enriched examples. PR142 patches only the deterministic enrichment wording. It
does not change the PR139 rules schema, create new interpretation reads, call
models, run Lolla, mutate archives, or change runtime behavior.

## What Changed

The builder still inserts or replaces exactly one section:

```text
## What the interpretation adds
```

The patched section now organizes the same existing interpretation-read fields
around three plain-language moves:

1. What may already have been present, with visible uncertainty.
2. What becomes clearer for action.
3. What appears sharpened as a descriptive caution and what the enrichment must
   not be used to prove.

The patch removes repeated mechanical lead-ins such as:

- `The interpretation read frames...`
- `Visible decision thresholds include...`
- `Visible evidence gates include...`

It also strips the repeated `quality score` sentence from the main enrichment
section. Useful friction remains descriptive. It is not answer-quality scoring.

## What Stayed The Same

The builder still:

- accepts an original rendered brief, an interpretation read, and the PR139
  rules contract;
- writes a separate enriched Markdown output;
- leaves original rendered briefs untouched;
- preserves `What this does not prove`;
- preserves `Evidence and limits`;
- keeps evidence-only fields out of the main enrichment body;
- preserves source limits, uncertainty, custody flags, and non-claims;
- rejects unsupported schemas, unsafe custody flags, same input/output paths,
  and rules that allow evidence-only or forbidden fields in the user-facing
  section.

## Regenerated Outputs

PR142 regenerates the two PR140 builder outputs:

- `docs/conversation-understanding/decision-work-brief-builder-enriched-launch-public-enterprise-beta-v0.md`
- `docs/conversation-understanding/decision-work-brief-builder-enriched-deploy-assisted-intake-routing-v0.md`

These remain separate from the original rendered briefs and from the PR135/PR137
hand-built enriched examples.

## Boundary

PR142 is offline and deterministic. It does not decide whether the advice is
good, whether Lolla improved the decision, what the conversation really meant,
or whether an agent may act.

Runtime invoked: no. Skill invoked: no. Archive mutated: no. Model calls: 0.
Human validated: no. Product proof: no. Answer-quality scoring: no. Agent
action authorization: no.

## Next Gate

The next slice should review the patched builder output:

```text
PR143 Decision Work Brief Builder Patch Review v0
```
