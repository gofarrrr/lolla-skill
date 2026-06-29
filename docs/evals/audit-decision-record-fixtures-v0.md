# Audit Decision Record Fixtures v0

Status: PR59 docs/eval-only fixture review
Date: 2026-06-29
Owner: Lolla maintainers

PR59 tests whether the PR58 audit decision record shape is understandable on
existing reviewed cases before any exporter exists.

This slice is docs/eval-only. It does not implement an exporter, run `$lolla`,
call models, mutate archives, change prompts, change `SKILL.md`, change
runtime behavior, populate labels, score answer quality, or approve high-stakes
use.

## Inputs

- [Audit Decision Record v0](../conversation-understanding/audit-decision-record-v0.md)
- [audit-decision-record-v0.json](../conversation-understanding/audit-decision-record-v0.json)
- [Actionable Delta Rubric v0](actionable-delta-rubric-v0.md)
- [Complex Baseline Human Review v0](complex-baseline-human-review-v0.md)
- [Human Review Corpus Batch v0](human-review-corpus-batch-v0.md)

Fixture JSON:

- [audit-decision-record-fixtures-v0.json](audit-decision-record-fixtures-v0.json)

Review JSON:

- [review.json](../../reviews/human/audit-decision-record-fixture-review-v0/review.json)

## Fixture Scope

The fixture pack covers six existing reviewed cases:

| fixture_id | case_id | PR31 labels exercised | expected read |
|---|---|---|---|
| `adr_fixture_v0_001_cofounder_authority_transfer` | `ceo-remove-founding-cofounder` | `action_changed`, `sequence_changed`, `stop_rule_added`, `scope_narrowed` | Authority transfer plus bounded transition rules, not warmer cofounder language. |
| `adr_fixture_v0_002_career_written_terms` | `accept-operations-role-startup` | `threshold_changed`, `evidence_gate_added`, `written_term_added`, `user_question_added`, `overclaim_retracted` | Written operating evidence and household capacity, not prestige narratives. |
| `adr_fixture_v0_003_enterprise_buyer_proof` | `launch-public-enterprise-beta` | `action_changed`, `threshold_changed`, `evidence_gate_added`, `written_term_added`, `scope_narrowed`, `overclaim_retracted` | Same-shape buyer proof, not logo-driven priority. |
| `adr_fixture_v0_004_pivot_capacity_gate` | `pivot-company-product-strategy` | `threshold_changed`, `sequence_changed`, `evidence_gate_added`, `written_term_added` | Capacity and obligations first, market proof second. |
| `adr_fixture_v0_005_clinic_operable_controls` | `deploy-assisted-intake-routing` | `action_changed`, `threshold_changed`, `evidence_gate_added`, `stop_rule_added`, `user_question_added`, `scope_narrowed` | Fewer controls that can stop the rollout, not checklist breadth. |
| `adr_fixture_v0_006_price_support_boundaries` | `implement-price-increase-three` | `action_changed`, `threshold_changed`, `evidence_gate_added`, `written_term_added`, `scope_narrowed` | Pricing separated from support operations with enforceable boundaries. |

Every fixture is paraphrase-only and uses checked-in review summaries. No raw
archive transcript, memo, revised-answer text, provider/model text, private
reasoning, credential value, or local absolute path is included.

## Review Result

The review rows exactly match the six fixture IDs.

Aggregate result:

| Field | Result |
|---|---|
| fixture count | 6 |
| review rows | 6 |
| review_status | 6 pass, 0 revise, 0 exclude |
| decision_delta_clarity | 5 clear, 1 mostly_clear, 0 unclear |
| pr31_mapping_useful | 6 yes, 0 partly, 0 no |
| conflict_preservation | 4 preserved, 2 partly_preserved, 0 flattened, 0 unclear |
| overclaim_control | 6 yes, 0 partly, 0 no |
| false_certainty_risk | 2 none, 4 low, 0 medium, 0 high |
| reviewer_can_use_without_raw_content | 6 yes, 0 partly, 0 no |
| primary_issue | 6 none |

The review says the PR58 shape is ready for a future read-only exporter design
prototype with caveats:

- keep output paraphrase-only or pointer-only;
- keep artifact references relative;
- keep custody flags false for excluded raw/private content;
- do not create human-review labels;
- do not score answer quality;
- do not treat the record as truth, domain approval, or autonomous reliance.

## What PR59 Proved

PR59 shows that reviewers can use `lolla.audit_decision_record.v0` to see:

- the audited decision;
- the original recommendation shape;
- the revised recommendation shape;
- the PR31 actionable-delta labels implicated;
- unresolved conflicts and questions;
- why a clean record is not the same thing as good advice.

The useful limit is also visible: compact records can flatten some conflict
detail. Future exporter work should preserve enough conflict text and source
references for human reviewers to challenge the projection.

## Non-Goals

PR59 does not add or approve:

- an exporter;
- runtime integration;
- `$lolla` runs;
- model calls;
- archive mutation;
- prompt changes;
- `SKILL.md` changes;
- provider-boundary policy changes;
- `caller_action` changes;
- high-stakes runs;
- answer-quality scoring;
- LLM judges;
- automatic human-review labels;
- automatic `safe_for_agent_use`;
- user memory;
- `conversation_understanding_ir.v0`;
- graph DB;
- embeddings;
- chunking;
- memory;
- policy engine;
- Semantica-style platform work.

## Stop Point

Stop after PR59.

The recommended next slice after maintainer review of PR57 through PR59 is:

```text
PR60 Provenance Map Design v0
```

PR60 should not start automatically from this fixture review. If approved, it
should remain docs/JSON design only and should not implement exporters, runtime
integration, model calls, archive mutation, prompts, `SKILL.md` changes,
automatic labels, answer-quality scoring, or platform work.
