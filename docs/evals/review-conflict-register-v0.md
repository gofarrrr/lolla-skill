# Review Conflict Register v0

Status: PR61 docs/JSON design
Date: 2026-06-29
Owner: Lolla maintainers

PR61 designs `lolla.review_conflict_register.v0` as a local, human-review-owned
register of unresolved conflicts visible in a Lolla run or review projection.

The register answers:

- what values, stakeholders, obligations, assumptions, or artifact states remain
  in tension;
- which conflicts the revised answer surfaced, preserved, narrowed, or may have
  flattened;
- which conflicts need user, stakeholder, reviewer, maintainer, or domain
  review;
- which conflicts are artifact/custody conflicts rather than semantic
  conflicts.

It does not decide which side is correct, approve an action, resolve conflicts,
score answer quality, assign human-review labels, or automate severity into
policy behavior.

## Why This Matters

Good Lolla answers often improve advice by preserving tension instead of
smoothing it away. A revised answer can be better because it exposes a conflict:
relationship preservation versus authority transfer, speed versus safety,
ambition versus capacity, customer trust versus revenue, or run readiness
versus answer quality.

Without a first-class conflict register, later artifacts can look cleaner than
the decision really is. `lolla.review_conflict_register.v0` gives reviewers a
compact place to inspect unresolved tensions without pretending the machine has
resolved them.

## Schema

Schema version:

```text
lolla.review_conflict_register.v0
```

Design example:

- [review-conflict-register-v0.json](review-conflict-register-v0.json)

High-level fields:

| Field | Meaning |
|---|---|
| `schema_version` | Fixed string: `lolla.review_conflict_register.v0`. |
| `case_id` | Compact case identifier already safe for review surfaces. |
| `run_id` | Compact run identifier already safe for review surfaces. |
| `archive_relpath` | Relative archive reference only. |
| `source_refs` | Review-safe docs or artifact names supporting the register. |
| `conflicts` | Human-review-owned conflict rows. |
| `custody_flags` | Whole-register raw/private content exclusions. |
| `limitations` | Non-claims and caveats. |

## Conflict Categories

The v0 category vocabulary is:

- `user_values_conflict`
- `stakeholder_obligation_conflict`
- `live_constraint_conflict`
- `recommendation_action_conflict`
- `risk_mode_reliance_conflict`
- `artifact_health_conflict`
- `provider_boundary_conflict`
- `unresolved_user_question_conflict`
- `human_review_disagreement`
- `provenance_gap_conflict`
- `decision_record_flattening_risk`

Categories are descriptive, not commands. They do not trigger actions, scores,
approvals, or policy enforcement.

## Conflict Row Fields

Each conflict row contains:

- `conflict_id`: stable local identifier inside the register.
- `category`: one v0 category.
- `status`: `open`, `partly_resolved`, `resolved_by_human_review`, or
  `not_applicable`.
- `summary`: paraphrase-only conflict statement.
- `sides`: two or more review-safe sides of the tension.
- `review_owner`: `user`, `human_reviewer`, `domain_reviewer`, `maintainer`, or
  `unknown`.
- `decision_impact`: `blocks_action`, `changes_threshold`,
  `changes_sequence`, `requires_question`, `review_context_only`, or `unknown`.
- `related_pr31_labels`: optional PR31 actionable-delta labels implicated by
  the conflict.
- `raw_content_included`: always false in checked-in design fixtures.

## Relationship To Other Accountability Artifacts

Audit decision record:

- `lolla.audit_decision_record.v0` summarizes what changed in the decision.
- The conflict register preserves what remains unresolved or contested.
- A decision record can point to conflicts; it should not flatten them into
  certainty.

Provenance map:

- `lolla.provenance_map.v0` shows how artifacts relate.
- The conflict register can record when provenance gaps or degraded artifacts
  create review conflicts.

Doctor/preflight:

- `lolla.doctor_report.v0` reports local readiness before a run.
- The conflict register can include readiness or evidence-absence conflicts
  surfaced by preflight or manifests, but it does not run doctor or change
  doctor behavior.

Human review:

- Human reviewers own answer-level judgment and reliance labels.
- The conflict register is an input to review, not a replacement for review.

## Non-Goals

PR61 does not add or approve:

- an exporter;
- runtime integration;
- `$lolla` runs;
- model calls;
- archive mutation;
- archive reading behavior;
- prompt changes;
- `SKILL.md` changes;
- provider-boundary policy changes;
- `caller_action` changes;
- high-stakes runs;
- conflict resolution;
- automatic severity-to-action behavior;
- policy enforcement;
- domain protocol routing;
- answer-quality scoring;
- LLM judges;
- automatic human-review labels;
- automatic `safe_for_agent_use`;
- raw transcript inclusion;
- raw memo inclusion;
- raw revised-answer inclusion;
- provider/model text inclusion;
- private reasoning inclusion;
- local absolute paths in checked-in examples;
- graph DB;
- embeddings;
- chunking;
- memory;
- Semantica-style platform work.

Extra stop rule:

If a future PR61 continuation feels tempted to add code, tests, exporters,
schemas under `engine/`, CLI support, runtime integration, or archive-reading
behavior, stop and report. PR61 is only a design artifact and safe example
JSON.

## Example Read

The PR61 JSON example uses the already documented
`deploy-assisted-intake-routing` case. It preserves healthcare-adjacent
operating-control tensions in paraphrase only. It does not inspect raw archives
or approve deployment.

## PR62 Gate

Implemented next as:

```text
PR62 Case Graph Export Design v0
```

PR62 remained docs/JSON design only. It designed a run-local
case-graph view shape without implementing an exporter, graph DB, embeddings,
memory, entity resolution, runtime integration, judge, or scoring layer.

## PR63 Accountability View Fixtures

PR63 now tests review conflict registers inside combined accountability-view
bundles:

- [Accountability View Fixtures v0](accountability-view-fixtures-v0.md)
- [accountability-view-fixtures-v0.json](accountability-view-fixtures-v0.json)

Those fixtures use the conflict register to preserve unresolved tensions beside
decision, provenance, and case graph views. They do not resolve conflicts,
automate severity, enforce policy, create labels, score advice, or replace
human review.
