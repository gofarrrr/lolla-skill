# User Values / Priorities Worksheet Human Pilot v0

Status: docs/local-review pilot
Date: 2026-06-28
Slice: PR53

PR53 pilots human-filled user-values/priorities worksheets on existing reviewed
records.

This slice does not run `$lolla`, call models, inspect raw archive transcripts,
mutate archives, change runtime behavior, change prompts, change `SKILL.md`,
implement extraction, populate labels automatically, score answer quality, add
a judge, change risk-mode behavior, or create high-stakes archive evidence.

Machine-readable pilot:

```text
../../reviews/human/user-values-priorities-worksheet-pilot-v0/worksheets.json
```

## What Was Piloted

The pilot fills four worksheets from existing PR30/PR33 reviewed summaries and
review JSON:

| case_id | run_id | source pattern | reason selected |
|---|---|---|---|
| `ceo-remove-founding-cofounder` | `20260627T093131Z_59d153` | cofounder authority transfer | Tests relationship preservation, fairness, authority transfer, and unresolved legitimacy conflict. |
| `accept-operations-role-startup` | `20260627T132700Z_bae7f3` | career/family written terms | Tests ambition, household capacity, spouse impact, written terms, and user-confirmed thresholds. |
| `launch-public-enterprise-beta` | `20260627T104146Z_7bfe79` | enterprise beta buyer proof | Tests credibility, buyer behavior, customer trust, proof quality, and overclaim control. |
| `deploy-assisted-intake-routing` | `20260627T130339Z_4cd3cb` | clinic controls deployment | Tests stakeholder safety, adoption, compliance, operator accountability, and conservative reliance. |

These four were chosen because they map directly to PR50 fixture patterns and
cover the central worksheet stress cases: authority, family/stakeholder
constraints, customer proof, and high-risk-like operating controls. The
consulting and pivot fixtures remain useful, but four records were enough for
this first pilot.

## How Worksheets Were Filled

The worksheets were filled by hand from existing reviewed summaries and local
human-review records:

- [Complex Baseline Human Review v0](complex-baseline-human-review-v0.md)
- [Human Review Corpus Batch v0](human-review-corpus-batch-v0.md)
- [Actionable Delta Rubric v0](actionable-delta-rubric-v0.md)
- [User Values / Priorities Worksheet Plan v0](user-values-priorities-worksheet-plan-v0.md)
- [User Values / Priorities Worksheet Fixtures v0](user-values-priorities-worksheet-fixtures-v0.md)
- [User Values / Priorities Worksheet Fixture Review v0](user-values-priorities-worksheet-fixture-review-v0.md)
- [User Values / Priorities Blank Worksheet Export v0](user-values-priorities-blank-worksheet-export-v0.md)

No raw transcript text, raw memo text, raw revised-answer text,
model/provider text, private reasoning, local absolute paths, secrets, or
credentials were copied. Notes are compact paraphrases.

The worksheets use the PR52 worksheet schema:

```text
lolla.user_values_priorities_worksheet.v0
```

Each worksheet is marked:

- `review_scope: human_review_only`;
- `source.human_filled: true`;
- `source.auto_extracted: false`;
- `source.model_calls: 0`;
- `source.llm_judge_used: false`;
- raw/private inclusion flags: `false`.

## Aggregate Results

| metric | value |
|---|---:|
| Worksheets | 4 |
| Total `values_items` | 16 |
| Total `conflicts` | 8 |
| `needs_user_confirmation` items | 16 |

Values surface sufficient for review:

| label | count |
|---|---:|
| `yes` | 4 |
| `no` | 0 |
| `unclear` | 0 |

Would change actionable-delta label:

| label | count |
|---|---:|
| `yes` | 0 |
| `no` | 4 |
| `unclear` | 0 |

Safe-for-agent-use impact:

| label | count |
|---|---:|
| `none` | 3 |
| `makes_more_conservative` | 1 |
| `unclear` | 0 |

## Findings

The worksheet added useful review structure. It made the values layer easier to
inspect without changing the underlying PR31 labels or pretending that the
system had extracted values automatically.

The worksheet preserved unresolved values and stakeholder conflicts. The four
records kept visible tensions around cooperation versus authority, ambition
versus household stability, buyer aura versus proof, and adoption versus
safety.

The worksheet exposed where user confirmation is needed. All 16 value items
retain `needs_user_confirmation: true` because the pilot used reviewed
summaries and derivations, not direct user confirmation or raw transcript
spans. That is a feature, not a failure: it prevents inferred values from
hardening into user profiles.

The worksheet connects cleanly to PR31 actionable-delta labels. It helps
explain why labels such as `stop_rule_added`, `scope_narrowed`,
`written_term_added`, `user_question_added`, `threshold_changed`, and
`evidence_gate_added` matter. It does not replace or recompute those labels.

The pilot did not show material overclaim risk as long as inferred values stay
medium or low confidence and require confirmation. The career/family worksheet
is the clearest caution case: emotional salience and family load are reviewable
signals, but the exact non-negotiable threshold remains unclear.

The worksheet affected reliance conservatism only where expected. Three
worksheets record `safe_for_agent_use_impact: none`; the clinic-control
worksheet records `makes_more_conservative` because stakeholder safety and
operable controls remain unresolved. None of the worksheets upgrades
`safe_for_agent_use` or approves agent reliance.

## Decision

Pilot status:

```text
pass
```

The four worksheets were fillable from existing reviewed summaries, added
useful review structure, preserved stakeholder obligations and unresolved
conflicts, and did not require extraction, model calls, runtime behavior, or a
judge.

Recommended next slice:

```text
PR54 User Values / Priorities Pilot Review / V0 Decision v0
```

PR54 should review the pilot result and decide whether the v0 worksheet lane is
complete enough to pause, or whether a small worksheet-shape patch is needed.
It should not add extraction, runtime integration, automatic labels, model
calls, high-stakes archive evidence, or a judge.

PR54 now completes that review:

```text
user-values-priorities-pilot-review-v0.md
../../reviews/human/user-values-priorities-pilot-review-v0/review.json
```

It marks all four pilot worksheets pass and closes the worksheet lane at v0 for
human-owned review. The lane is paused before extraction, runtime integration,
automatic labels, memory, `safe_for_agent_use` automation, high-stakes archive
evidence, or judging.

## Boundary Confirmation

- PR53 is docs/local-review only.
- Human-filled worksheets only.
- Notes are paraphrase-only.
- No `$lolla` run.
- No model calls.
- No archive mutation.
- No raw archive transcript inspection.
- No runtime files changed.
- No prompts changed.
- No `SKILL.md` changes.
- No extraction implemented.
- No judge or answer-quality score added.
- No automatic labels added.
- No risk-mode behavior change.
- No high-stakes archive evidence created.
- PR54 reviewed this pilot and paused the worksheet lane at v0.
