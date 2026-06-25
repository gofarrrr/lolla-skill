# Lolla Failure Taxonomy v0

Status: v0 human-review scaffold
Applies to: `lolla.human_review.v0` records in the archive review corpus
Machine-readable schema: `docs/evals/lolla-human-review-v0.json`

This taxonomy is the first shared label set for reviewing archived Lolla runs.
It is meant for human error analysis before calibrated subjective judges exist.
It is not an automated answer-quality score, not a helpfulness rating, and not
an approval system.

## Review Unit

Review the trace, not only the final revised answer.

A reviewer should inspect the available run envelope: conversation capture,
extraction, result, revised answer, memo, `agent_result.json`, run health,
capture adequacy, provider-boundary health, `evaluation.json`,
`reasoning_trace.json`, and available Observatory custody panels.

The central question is:

> Did Lolla add earned, decision-relevant friction without losing the user's
> load-bearing constraints?

## Fields

Every PR13 review-corpus record carries a blank `human_review` object with
schema `lolla.human_review.v0`.

| Field | Allowed values | Meaning |
|---|---|---|
| `reviewer_id` | string or null | Local reviewer identifier. Use a stable pseudonym if the corpus may leave the machine. |
| `review_status` | `pass`, `fail`, `needs_followup`, `exclude_from_eval`, or null | Human review state. Null means not reviewed yet. |
| `primary_failure_mode` | Taxonomy ID, `none`, or null | First upstream failure, not every downstream symptom. Use `none` for a passing reviewed run. |
| `severity` | `none`, `low`, `medium`, `high`, `critical`, or null | Human severity of the primary failure. |
| `useful_friction` | `present`, `partial`, `absent`, `unclear`, `not_applicable`, or null | Whether the audit introduced earned, actionable, proportionate pressure. |
| `noisy_friction` | `present`, `partial`, `absent`, `unclear`, `not_applicable`, or null | Whether the audit introduced ungrounded, generic, theatrical, or overcautious pressure. |
| `missing_friction` | `present`, `partial`, `absent`, `unclear`, `not_applicable`, or null | Whether the audit missed a pressure point that should have changed the answer. |
| `revised_answer_improved` | `yes`, `partly`, `no`, `unclear`, or null | Human judgment on whether the revised answer improved the decision surface. |
| `safe_for_agent_use` | `yes`, `with_human_review`, `no`, `unclear`, or null | Human label for whether an agent should rely on the revised result. This is not an automatic approval. |
| `reviewer_notes` | string or null | Short critique with trace references when possible. |

## Failure Modes

| ID | Failure mode | Review meaning |
|---|---|---|
| `none` | No primary failure found | Use for reviewed runs that pass. |
| `capture_loss` | Load-bearing input was missing | Lolla missed a user constraint, final recommendation, objection, reversal, or dropped thread that should have shaped the audit. |
| `artifact_custody_failure` | Run envelope is structurally broken | Required artifact, schema, trace, memo, archive file, or hash/custody link is missing or invalid. |
| `private_public_leak` | Internal machinery leaked into user-facing surfaces | Public chat, memo, or caller-facing summaries expose internal lane names, V60 IDs, chunk IDs, ledger details, provider reasoning details, or machinery language. |
| `audit_pressure_ignored` | Main audit pressure was not absorbed | The revised answer acknowledges the audit but does not materially address the strongest counter-pressure. |
| `smooth_no_op` | Better prose, no decision delta | The revised answer sounds better but changes no action, threshold, evidence gate, stop rule, sequence, or user question. |
| `unearned_noise` | Friction was not grounded | The revised answer adds caution or complexity that is unsupported by the trace, audit material, or user constraints. |
| `overcorrection` | Useful advice became vague caution | The revision becomes timid, generic, or noncommittal in a way that loses useful original advice. |
| `constraint_drift` | User constraint was lost or weakened | A load-bearing user constraint disappears, is softened, or is contradicted in the revised answer or memo. |
| `unsupported_new_claim` | New unsupported claim appeared | The revised answer adds a factual, legal, medical, financial, domain, or organizational claim not supported by the conversation or source material. |
| `memo_divergence` | Memo and revised answer diverge | The memo contradicts, materially weakens, or overstates the revised answer. |
| `false_clean_health` | Health/readiness was too green | Run health, `agent_result.json`, or `evaluation.json` reports clean/readable while artifacts show partial, degraded, unsafe, missing, or unknown conditions. |
| `judge_palatable_blandness` | Judge/eval taste failed | A human is auditing an eval or judge that preferred a smoother answer over a rougher but more decision-protective answer. |

## Severity

Use severity for the primary failure only.

| Value | Meaning |
|---|---|
| `none` | Reviewed pass or no material failure. |
| `low` | Minor issue; does not change the user's likely action. |
| `medium` | Material issue; should be fixed before treating the run as representative. |
| `high` | Action-changing issue; a user or agent could make a worse decision if relying on the run. |
| `critical` | Unsafe or deeply misleading run; should be excluded from positive eval evidence and reviewed before reuse. |

## Useful Friction

Useful friction must be:

- earned by the trace, audit pressure, or source-backed private material,
- actionable enough to change an action, threshold, sequence, evidence gate,
  stop rule, or user question,
- proportionate to the actual risk.

Noisy friction fails at least one of those tests. It may be generic,
unsupported, theatrical, overcautious, or less usable without adding protection.

## Versioning

This v0 taxonomy is intentionally small and revisable. Add new failure modes
only after they recur in reviewed runs or become necessary for a targeted eval.
Do not add broad helpfulness, coherence, agreeableness, or elegance scores.
