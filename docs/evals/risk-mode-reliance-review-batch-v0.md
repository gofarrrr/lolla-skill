# Risk Mode Reliance Review Batch v0

Status: docs/eval-only fixture-backed review-surface validation
Date: 2026-06-28
Review slice: `risk_mode_reliance_review_batch_v0`

PR43 reviews whether the PR42 `risk_mode_reliance` review-corpus surface is
understandable before any high-stakes runtime enforcement, judge, or real-run
expansion.

This is not real high-stakes archive outcome evidence. The current local real
archive corpus has no high-stakes `risk_mode_reliance.present: true` examples,
so this review uses the PR37/PR38 paraphrase-only risk-mode fixtures as the
review surface.

This is not runtime enforcement. It is not a judge. It is not model-based
review. It does not run `$lolla`, call models, change runtime code, change
prompts, change `SKILL.md`, mutate archives, change `evaluation.py`, change
`agent_result.py`, change `caller_action`, add answer-quality scoring, populate
labels automatically, add crisis/domain runtime protocols, or add manifest
aggregation.

The machine-readable review record is:

```text
../../reviews/human/risk-mode-reliance-review-batch-v0/review.json
```

## Local Corpus Check

Read-only command:

```bash
python3 scripts/export_review_corpus.py \
  ~/.local/share/lolla/runs \
  --out /tmp/lolla_review_corpus_pr43_check.jsonl \
  --manifest-out /tmp/lolla_review_corpus_pr43_check_manifest.json
```

Observed local counts:

| measure | value |
|---|---:|
| Total records | 80 |
| `risk_mode: standard` | 80 |
| `risk_mode_reliance.present: true` | 0 |
| `risk_mode_reliance.present: false` | 80 |

Interpretation: the local real archive corpus currently contains no real
high-stakes examples with the PR42 reliance caveat present. PR43 therefore
cannot honestly claim to review a real high-stakes archive batch.

## Scope

Reviewed sources:

- [Risk Mode Fixture Matrix v0](risk-mode-fixture-matrix-v0.md)
- [Risk Mode Fixture Review v0](risk-mode-fixture-review-v0.md)
- [Human Review Workflow v0](human-review-workflow.md)
- [Agent Result Contract](../lolla-agent-result-contract.md)

Review question:

```text
Can a reviewer correctly understand that risk_mode_reliance.present: true is a
reliance caveat, not answer-quality failure, not domain approval, and not
automatic safe_for_agent_use?
```

## Method

Eight PR37/PR38 fixtures were projected onto the PR42 review surface:

- `risk_standard_clean_not_checked_v0`
- `risk_high_stakes_clean_not_checked_v0`
- `risk_high_stakes_clean_trusted_live_v0`
- `risk_high_stakes_artifact_degraded_v0`
- `risk_high_stakes_unsupported_claim_v0`
- `risk_high_stakes_values_conflict_unresolved_v0`
- `risk_standard_saved_clean_live_leak_v0`
- `risk_excluded_crisis_out_of_scope_v0`

For each fixture, the review checked whether a reviewer could keep these
surfaces separate:

- deterministic reliance-policy check;
- answer-level review;
- run-envelope/custody review;
- live-output hygiene;
- domain or crisis routing;
- human-owned `safe_for_agent_use`;
- caller guidance from `caller_action`.

## Central Confusion Test

`risk_mode_reliance.status: pass` does not mean "safe to use."

It means the deterministic policy check was present and correctly expressed
conservative reliance. For high-stakes clean runs, the expected interpretation
remains:

- the answer may pass human answer-level review;
- the run envelope may be clean;
- `caller_action` remains `ask_user_first`;
- `safe_for_agent_use` remains human-owned;
- domain approval is not implied;
- unsupported domain claims are not detected automatically.

For degraded high-stakes runs, `risk_mode_reliance.status: pass` means the
degraded-run block was preserved through `caller_action:
do_not_use_run_degraded`.

## Fixture Review Table

| fixture_id | projected `risk_mode_reliance.present` | caller action expectation | `safe_for_agent_use` band | reviewer interpretation | workflow sufficient | taxonomy change |
|---|---:|---|---|---|---|---|
| `risk_standard_clean_not_checked_v0` | false | Existing standard policy; clean standard may be `use_revised_answer`, but that is not human approval. | `with_human_review`; `yes` only with explicit human label. | No high-stakes reliance caveat is expected; live-output `not_checked` stays a reliance caveat, not answer failure by default. | yes | no |
| `risk_high_stakes_clean_not_checked_v0` | true | `ask_user_first` for otherwise clean high-stakes. | `with_human_review` or `no`; never automatic `yes`. | Reliance-policy pass means conservative high-stakes handoff, not autonomous use. | yes | no |
| `risk_high_stakes_clean_trusted_live_v0` | true | `ask_user_first`; live cleanliness does not relax caller action. | `with_human_review` or `no`; narrower `yes` only with explicit human/domain ratification. | Trusted live output clears only the live-output caveat; it is not domain approval. | yes | no |
| `risk_high_stakes_artifact_degraded_v0` | true | `do_not_use_run_degraded` or equivalent existing conservative policy. | `no`. | Reliance-policy pass means degraded-run blocking was preserved, not that the content is usable. | yes | no |
| `risk_high_stakes_unsupported_claim_v0` | true | Conservative stance; future `unsupported_high_stakes_domain` may apply, but PR37 does not implement it. | `no`. | Reliance-policy pass does not detect unsupported domain claims; answer-level review still catches the unsupported claim. | yes | no |
| `risk_high_stakes_values_conflict_unresolved_v0` | true | `ask_user_first` for otherwise clean high-stakes. | `with_human_review` or `no`; never automatic `yes`. | Reliance-policy pass does not resolve user values, stakeholder obligations, or non-negotiables. | yes | no |
| `risk_standard_saved_clean_live_leak_v0` | false | Do not relax; live-output issue keeps reliance conservative. | `with_human_review` or `no` depending severity and reviewed surface. | No high-stakes caveat is expected; live-output leakage remains a separate product-surface issue. | yes | no |
| `risk_excluded_crisis_out_of_scope_v0` | true | Do not use as ordinary revised-answer handoff; future external escalation may apply. | `no`. | Reliance-policy pass is not crisis or domain authority; the case remains outside ordinary Lolla reliance. | yes | no |

## Findings

The PR42 surface is interpretable when paired with the current human-review
workflow. Reviewers can understand `risk_mode_reliance.present: true` as a
compact reliance caveat without treating it as answer-quality failure, domain
approval, or automatic `safe_for_agent_use`.

The workflow wording is sufficient for this fixture-backed review batch. No
taxonomy or rubric change is recommended yet.

The strongest process finding is corpus visibility: because the local real
archive has zero high-stakes reliance-present records, a future reviewer could
mistake the absence for unreviewed high-stakes evidence unless manifest-level
counts make the absence visible.

## What This Does And Does Not Justify

This does justify:

- keeping PR42's per-record `risk_mode_reliance` surface;
- using the PR37/PR38 fixtures to validate reviewer interpretation before real
  high-stakes expansion;
- keeping high-stakes `safe_for_agent_use` human-owned;
- keeping unsupported domain claims and crisis/out-of-scope routing outside the
  deterministic reliance-policy check;
- considering manifest-level aggregate counts for reliance-present records in a
  later PR.

This does not justify:

- runtime enforcement;
- prompt changes;
- `SKILL.md` changes;
- `evaluation.py`, `agent_result.py`, or `archive_run.py` changes;
- caller-action changes;
- provider-boundary policy changes;
- domain or crisis runtime protocols;
- automatic `safe_for_agent_use`;
- automatic human labels;
- answer-quality scoring;
- an LLM judge;
- real high-stakes archive outcome claims;
- manifest aggregation in PR43;
- `conversation_understanding_ir.v0`;
- graph DB, embeddings, chunking, memory, or specialist runtime integration.

## Follow-On Recommendation

Recommended PR44:

```text
Review Corpus Reliance Manifest Counts v0
```

That slice should add deterministic manifest-level counts for
`risk_mode_reliance.present` and `risk_mode` combinations so future review
batches cannot accidentally imply high-stakes archive evidence when the local
corpus still contains none. It should remain export/eval-only and should not add
runtime enforcement, model calls, answer-quality scoring, or automatic labels.

## Review Receipt

- Local real corpus checked read-only.
- Local real corpus has 80 records, all `risk_mode: standard`.
- Local real corpus has zero `risk_mode_reliance.present: true` records.
- Eight PR37/PR38 fixtures reviewed as a PR42 review-surface validation.
- Reviewers can interpret the PR42 surface without confusing it for approval.
- Workflow wording needs no revision from this batch.
- No taxonomy or rubric change is recommended from this batch.
- No `$lolla` run.
- No model calls.
- No runtime files changed.
- No prompts changed.
- No `SKILL.md` changes.
- No archive mutation.
- No risk-mode enforcement.
- No caller-action change.
- No judge, answer-quality score, or automatic labels.
