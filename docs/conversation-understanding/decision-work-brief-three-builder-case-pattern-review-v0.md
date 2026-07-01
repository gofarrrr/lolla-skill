# Decision Work Brief Three Builder Case Pattern Review v0

Status: PR149 pattern review

Date: 2026-07-01

Review schema: `lolla.decision_work_brief_three_builder_case_pattern_review.v0`

## Purpose

PR149 compares the three deterministic builder-generated enriched Decision
Work Brief examples:

- [Decision Work Brief Builder-Enriched Launch Beta](decision-work-brief-builder-enriched-launch-public-enterprise-beta-v0.md)
- [Decision Work Brief Builder-Enriched Intake Routing](decision-work-brief-builder-enriched-deploy-assisted-intake-routing-v0.md)
- [Decision Work Brief Builder-Enriched CEO Remove Founding Cofounder](decision-work-brief-builder-enriched-ceo-remove-founding-cofounder-v0.md)

The review asks whether the offline builder now preserves the useful
action-consequence signal across three different decision families without
hiding uncertainty, promoting evidence-only fields, or turning provisional
interpretation into proof.

This is a review slice only. It does not patch the builder, add a fourth case,
create a new interpretation read, or attach the brief to runtime.

## Pattern Read

All three builder outputs preserve the core useful signal: the enriched section
makes the practical action consequence easier to understand.

- Launch-beta clarifies that both prospects should compete through the same
  paid, scoped private pilot instead of treating logo size or a public page as
  proof.
- Intake-routing clarifies that the deployment should stay narrow, start with a
  backlog diagnostic, use four must-pass operating gates, and include hard
  pause triggers.
- Cofounder/governance clarifies that the CEO would align with the COO, move
  product execution authority first, narrow transition support, and precommit
  escalation triggers before the conversation.

The builder is not as smooth as hand-built prose, and the cofounder output
still exposes a mild template weakness in the opening enrichment sentence. But
the issue is reader polish, not a correctness blocker. The generated outputs
are readable enough for offline review and preserve the evidence boundary.

## Risks

The strongest unresolved risk is not builder mechanics. It is human usefulness
and source depth.

The builder relies on checked-in-safe compressed context and provisional
Codex-assisted interpretation reads. Raw conversation details, private memo
text, provider text, and private ledgers are not checked in. The cofounder case
is especially sensitive because authority-transfer language can feel like
operating advice unless the legal, equity, board, employment, relationship, and
customer-trust caveats remain visible.

Clean enriched briefs still do not prove:

- the advice is correct;
- Lolla improved the decision;
- a human validated the interpretation;
- answer quality was measured;
- an agent may act.

## Decision Gate

PR149 chooses:

```text
proceed_to_human_review_intake_plan
```

Recommended next PR:

```text
PR150 Decision Work Brief Human Review Intake Plan v0
```

The next useful evidence step is to design a small human-review intake plan for
the offline Decision Work Brief and enriched examples. Another deterministic
builder case would add less information than asking what a human reviewer must
check before any user-facing or runtime-adjacent use.

## Boundary

PR149 does not:

- run `$lolla`;
- invoke the Lolla skill;
- call provider or model APIs;
- mutate archives;
- change runtime behavior;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- create a new Lolla run;
- create a new interpretation read;
- check in local-private text;
- patch the builder;
- add answer-quality scoring;
- create automatic labels;
- authorize agent action;
- claim product proof;
- claim human validation;
- integrate the brief into runtime.
