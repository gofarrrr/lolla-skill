# Review Corpus Evidence Readiness v0

Status: offline deterministic analyzer
Date: 2026-06-28
Slice: PR48

PR48 adds a read-only analyzer for review-corpus manifest JSON. It answers one
narrow question:

```text
Does this manifest actually show high-stakes reliance-present archive evidence?
```

This slice does not create conversations, run Lolla, call models, read raw
archive folders, mutate archives, change runtime behavior, change prompts,
change `SKILL.md`, add a judge, score answer quality, or populate human-review
labels.

## Tooling

The analyzer lives in:

```text
engine/system_b/review_corpus_evidence_readiness.py
scripts/analyze_review_corpus_evidence_readiness.py
tests/test_review_corpus_evidence_readiness.py
```

The CLI reads only a review-corpus manifest:

```bash
python3 scripts/analyze_review_corpus_evidence_readiness.py \
  --manifest /tmp/lolla_review_corpus_manifest.json \
  --out /tmp/lolla_review_corpus_evidence_readiness.md \
  --json-out /tmp/lolla_review_corpus_evidence_readiness.json
```

If no output paths are supplied, it prints deterministic JSON to stdout.

## Input Contract

The analyzer requires the PR44 manifest aggregate fields:

- `record_count`;
- `risk_mode_counts`;
- `risk_mode_reliance_present_counts`;
- `risk_mode_reliance_by_risk_mode_counts`;
- `risk_mode_reliance_check_status_counts`.

If those fields are missing, the analyzer returns:

```text
evidence_state: insufficient_manifest_fields
recommendation: do_not_claim_high_stakes_archive_evidence
```

That is deliberate. Older manifests do not prove absence or presence of
high-stakes evidence; they only prove the manifest is too old or too thin for
this question.

## Output Contract

The report schema is:

```text
lolla.review_corpus_evidence_readiness.v0
```

It includes compact custody-safe fields:

- manifest schema version;
- record schema version;
- total record count;
- risk-mode counts;
- reliance-present counts;
- reliance-by-risk-mode counts;
- reliance-check-status counts;
- high-stakes reliance-present count;
- missing manifest fields;
- evidence state;
- recommendation;
- caveats.

The evidence states are:

- `no_high_stakes_reliance_evidence`;
- `has_high_stakes_reliance_evidence`;
- `insufficient_manifest_fields`.

The recommendations are:

- `do_not_claim_high_stakes_archive_evidence`;
- `ready_for_high_stakes_review_batch`.

`ready_for_high_stakes_review_batch` means the manifest has high-stakes
reliance-present records to review. It does not mean the answers are good, safe,
domain-approved, or usable by an agent.

## Current Expected Local Read

The current local review-corpus manifest is expected to produce:

```json
{
  "record_count": 80,
  "risk_mode_counts": {
    "standard": 80
  },
  "risk_mode_reliance_present_counts": {
    "false": 80,
    "true": 0
  },
  "risk_mode_reliance_by_risk_mode_counts": {
    "standard|false": 80
  },
  "risk_mode_reliance_check_status_counts": {
    "unavailable": 80
  },
  "high_stakes_reliance_present_count": 0,
  "evidence_state": "no_high_stakes_reliance_evidence",
  "recommendation": "do_not_claim_high_stakes_archive_evidence"
}
```

That means the current real archive corpus still contains no high-stakes
`risk_mode_reliance.present: true` evidence.

## Custody And Privacy

The analyzer deliberately excludes:

- manifest path;
- archive root;
- local absolute archive paths;
- raw transcript text;
- raw memo text;
- raw revised-answer text;
- raw model or provider message content;
- provider reasoning details;
- private reasoning;
- secrets or credentials.

It records `model_calls: 0` and `llm_judge_used: false`.

## How This Prevents Drift

PR47 created high-stakes fixtures, but fixtures are not archive outcomes. PR44
made aggregate reliance counts visible, but people still had to inspect a
manifest correctly. PR48 turns that inspection into a small deterministic gate:

- if the manifest lacks PR44 fields, do not infer;
- if high-stakes reliance-present count is zero, do not claim evidence;
- if high-stakes reliance-present records exist, review them with humans before
  making product claims.

The analyzer is intentionally about evidence existence, not answer quality.

## Non-Goals

- no `$lolla` runs;
- no model calls;
- no archive mutation;
- no raw archive inspection;
- no runtime behavior change;
- no prompt or `SKILL.md` change;
- no caller-action change;
- no provider-boundary policy change;
- no LLM judge;
- no answer-quality score;
- no automatic human-review labels;
- no model-based risk classifier;
- no domain or crisis protocol;
- no `conversation_understanding_ir.v0`;
- no graph, embeddings, chunking, memory, or specialist runtime integration.

## Approval Gate

PR48 is the stop point before real high-stakes run work. A future PR may create
real high-stakes archive evidence only after explicit approval of the scenario
list, run count, cost ceiling, custody path, reviewer, and operator procedure
described in [High-Stakes Evidence Seed Plan v0](high-stakes-evidence-seed-plan-v0.md).
