# User Values / Priorities Worksheet Plan v0

Status: docs-only worksheet plan
Date: 2026-06-28
Slice: PR49

PR49 turns PR34's `user_values_or_priorities_signal` design into a concrete
human-review worksheet plan. It does not implement the worksheet, export blank
templates, run Lolla, call models, change runtime behavior, change prompts,
change `SKILL.md`, mutate archives, add extraction, add memory, add a judge,
score answer quality, populate labels automatically, or change
`caller_action`.

The planning question is:

```text
How should a human reviewer record user values, priorities, tradeoffs,
obligations, non-negotiables, and unresolved conflicts before Lolla has any
extractor or report builder for that surface?
```

## Why This Exists

PR30 through PR33 made Lolla's human-review flywheel more concrete. PR31 gave
reviewers a language for action-changing deltas, and PR33 showed that language
can survive a broader review-corpus batch.

PR34 then named the repeated semantic gap:

```text
user_values_or_priorities_signal
```

The current system preserves many mechanics well: artifacts, manifests, quote
and capture checks, custody, run health, `caller_action`, review-corpus records,
and aggregate readiness counts. It still does not make user values or
priorities first-class review data.

That gap matters because many good Lolla revisions are not merely more factual
or more cautious. They preserve a value, refuse a false tradeoff, name a
stakeholder obligation, narrow scope around a non-negotiable, or ask the user to
resolve a conflict the assistant cannot resolve honestly.

PR49 is the reviewability step. It makes the missing surface actionable for
humans before any extractor, exporter, runtime field, memory layer, or
`conversation_understanding_ir.v0` exists.

## What The Worksheet Is

The worksheet is a future human-owned review artifact.

It is for reviewers who are already inspecting saved artifacts from an archived
run or review-corpus record. The worksheet should help them record:

- explicit values;
- inferred priorities;
- tradeoff willingness;
- non-negotiables;
- stakeholder obligations;
- conflicts between values;
- values that are unclear or underdetermined;
- questions the user would need to answer;
- whether the revised answer honored, distorted, ignored, or over-hardened
  those values.

The worksheet should be local and review-scoped. It should point to artifacts,
turn references, span references, or reviewer derivations rather than copying
sensitive conversation text into shareable corpus material.

The human reviewer owns the semantic judgment. Deterministic checks, if added
later, can only validate boring structure: schema version, enum values, ids,
references, required fields, and absence of disallowed copied content.

## What The Worksheet Is Not

The worksheet is not:

- an LLM judge;
- an answer-quality score;
- a moral ranking system;
- domain approval;
- memory;
- user profiling;
- automatic extraction;
- automatic `safe_for_agent_use`;
- a runtime artifact;
- a prompt change;
- a `conversation_understanding_ir.v0` implementation.

It also should not decide what the user values. It records what a reviewer can
ground in the case, what remains unclear, and what should stay conservative
until a human or stakeholder resolves it.

## Proposed Worksheet Shape

This is a design shape, not production JSON and not a schema-enforced runtime
artifact.

```json
{
  "schema_version": "lolla.user_values_priorities_worksheet.v0",
  "case_id": "...",
  "run_id": "...",
  "review_scope": "human_review_only",
  "source_artifacts_reviewed": {
    "memo": true,
    "revised_answer": true,
    "agent_result": true,
    "evaluation": true,
    "review_corpus_record": true
  },
  "values_items": [
    {
      "id": "value_001",
      "kind": "explicit_value | inferred_priority | stakeholder_obligation | non_negotiable | tradeoff_willingness | unresolved_conflict",
      "status": "present | unclear | not_observed",
      "grounding": "span | turn_ref | derivation | reviewer_inference",
      "confidence": "high | medium | low",
      "review_note": "...",
      "needs_user_confirmation": true
    }
  ],
  "conflicts": [
    {
      "id": "conflict_001",
      "between": ["value_001", "value_002"],
      "status": "resolved_by_answer | preserved_for_user | flattened | unclear",
      "review_note": "..."
    }
  ],
  "answer_treatment": {
    "honored_values": [],
    "distorted_values": [],
    "ignored_values": [],
    "over_hardened_values": [],
    "open_questions_added": []
  },
  "reviewer_summary": {
    "values_surface_sufficient_for_review": "yes | no | unclear",
    "would_change_actionable_delta_label": "yes | no | unclear",
    "safe_for_agent_use_impact": "none | makes_more_conservative | unclear"
  }
}
```

The shape deliberately separates value items from answer treatment. A reviewer
can say "this value appears grounded" while still saying "the revised answer
handled it badly" or "the answer preserved the conflict instead of resolving
it." That separation prevents the worksheet from becoming a hidden approval
mechanism.

## Field Intent

`review_scope` should remain `human_review_only` for v0. Any exporter or
fixture pack should preserve that value unless a later PR explicitly changes
the contract.

`source_artifacts_reviewed` records what the reviewer inspected. It should not
imply that any one artifact is sufficient by itself. `evaluation.json` remains
run-readiness evidence, not answer wisdom.

`values_items.kind` should stay close to PR34 language:

- `explicit_value`: the user directly says what matters or what must be
  preserved.
- `inferred_priority`: the reviewer derives a decision-relevant priority from
  repeated grounded evidence.
- `stakeholder_obligation`: the decision carries a duty, dependency, or care
  burden involving another person or group.
- `non_negotiable`: the user names a boundary that should not be traded away.
- `tradeoff_willingness`: the user appears willing to give up one thing for
  another under stated conditions.
- `unresolved_conflict`: two or more grounded values or obligations pull
  against each other.

`grounding` should make the evidentiary status visible:

- `span`: the reviewer can inspect a local source span.
- `turn_ref`: the reviewer can inspect a turn reference.
- `derivation`: the item is derived from multiple signals and needs care.
- `reviewer_inference`: the reviewer is making a fragile inference that should
  normally require user confirmation.

`answer_treatment` records what the revised answer did with the values. The
important categories are asymmetric: ignored, distorted, and over-hardened
values are not balanced by a generic "nice treatment" score. The reviewer should
name concrete treatment, not award vibes.

`safe_for_agent_use_impact` is intentionally conservative. The worksheet can
make reliance more conservative or unclear; it should not upgrade agent
readiness automatically.

## Relationship To PR31 Actionable Delta

The worksheet can support PR31 labels by explaining why a delta mattered.

Examples:

- `user_question_added`: an unresolved value conflict requires a question only
  the user or stakeholder can answer.
- `scope_narrowed`: a priority or obligation makes the broader plan too risky
  or dishonest.
- `threshold_changed`: a value becomes a concrete gate or acceptance criterion.
- `evidence_gate_added`: a tradeoff should not proceed until proof exists.
- `stop_rule_added`: a non-negotiable or stakeholder obligation creates a
  pause, rollback, or refusal condition.
- `overclaim_retracted`: the revised answer stops pretending it knows the
  user's motives, values, or permission to trade something away.

The worksheet must not become a PR31 score. More value items do not mean a
better answer. A single unresolved stakeholder conflict may matter more than a
long list of weak inferred priorities.

## Relationship To Risk Mode And High Stakes

For `high_stakes` cases, unresolved user-values conflicts, stakeholder
obligations, or non-negotiables should keep reliance conservative. A clean
artifact chain can still leave the human reviewer with:

- `safe_for_agent_use: with_human_review`;
- `safe_for_agent_use: no`;
- `caller_action: ask_user_first`;
- a domain-review requirement;
- a user question that must be answered before action.

PR49 does not change risk-mode behavior, `caller_action`, review-corpus export,
evaluation logic, or high-stakes approval policy. It only designs how a future
human reviewer could record value conflicts that explain why reliance should
stay conservative.

## Human Review Workflow Fit

The worksheet should sit after the reviewer has enough artifacts to inspect the
case, not before. A reasonable future workflow is:

1. Read the review-corpus record and custody/readiness fields.
2. Inspect the saved memo, revised answer, agent result, and evaluation receipt
   as available.
3. Apply the PR31 actionable-delta rubric.
4. Fill the values/priorities worksheet only when the case has relevant values,
   obligations, tradeoffs, or conflicts.
5. Decide whether the worksheet changes the review note, actionable-delta
   label explanation, or conservative `safe_for_agent_use` stance.

This worksheet should be optional in low-signal cases. Forcing reviewers to
invent values in every run would create noise and overclaim.

## Privacy And Custody

The worksheet should be corpus-safe by default:

- no copied sensitive conversation passages in shareable records;
- no provider message text;
- no private reasoning;
- no local absolute paths in exported examples;
- no secrets, credentials, or account identifiers;
- no durable user profile outside the reviewed case.

Paraphrase-only examples are acceptable when they are clearly labeled as
fixtures or design examples. Local-only worksheets may carry source references
that let a reviewer recover evidence from the raw archive, but exported
material should not copy that source text.

## Future Validation Ideas

If this surface is implemented later, deterministic validation can check:

- schema version;
- required top-level fields;
- allowed enum values;
- stable ids;
- conflict references point to existing value ids;
- `needs_user_confirmation` is true for fragile inferences;
- source artifact flags are booleans;
- answer-treatment arrays reference known value ids if references are used;
- exported examples do not copy disallowed content.

The validator still should not decide whether a value inference is correct,
whether an answer honored it, or whether the user should act.

## Recommended PR50

Recommended next slice:

```text
PR50 User Values / Priorities Worksheet Fixture Pack v0
```

That should be docs/eval-only and paraphrase-only. It should create a small set
of filled worksheet examples from existing PR30 and PR33 review patterns without
copying raw transcripts, memo text, revised-answer text, provider text, or
private reasoning.

Fixture pack before blank exporter is the more conservative next move because
reviewers should test whether the worksheet is understandable before code
starts producing empty templates or encouraging mechanical completion. If the
fixture pack shows the shape is noisy, too burdensome, or prone to values
overclaim, the next implementation step should change the worksheet before any
exporter exists.

PR50 now adds that paraphrase-only fixture pack:

```text
user-values-priorities-worksheet-fixtures-v0.md
user-values-priorities-worksheet-fixtures-v0.json
```

The recommended next slice after PR50 is human/product fixture review, not a
blank exporter or extraction code.

## Stop Condition

PR49 stops at documentation and validation. It does not start PR50.

No implementation should follow from this note until a later PR explicitly
chooses the next slice and repeats the non-goal boundaries.

## Review Receipt

- PR49 is docs-only.
- No `$lolla` run.
- No model calls.
- No runtime files changed.
- No prompts changed.
- No `SKILL.md` changes.
- No extraction implemented.
- No blank worksheet exporter added.
- No fixture pack added.
- No report builder added.
- No memory layer added.
- No `conversation_understanding_ir.v0` added.
- No judge or answer-quality score added.
- No automatic labels added.
- No high-stakes runs started.
