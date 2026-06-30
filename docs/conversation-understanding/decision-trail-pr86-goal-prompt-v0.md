# PR86 Decision Trail Report Goal Prompt v0

Use this prompt in a fresh coder session.

```text
/goal

Objective:
Implement PR86: Decision Trail Report PRD And Schema v0 for the Lolla repo.

Repository:
Use the current `lolla-skill-public-runtime` repo root.

Current stage:
PR71-PR85 packaged the non-human Product Delta Evidence phase.
The next phase is Decision Trail. PR86 is schema/design only. Do not implement PR87 exporter code.

Read first:
- PROGRESS.md
- HOW_IT_WORKS.md
- README.md
- docs/lolla-decision-trail-web-page-v0.md
- docs/conversation-understanding/decision-trail-readiness-audit-v0.md
- docs/conversation-understanding/decision-trail-pr86-pr89-prd-v0.md
- docs/conversation-understanding/research-and-design-v0.md
- docs/conversation-understanding/semantic-extraction-review-pilot-v0.md
- docs/conversation-understanding/broader-specialist-evidence-gate-v0.md
- docs/conversation-understanding/specialist-runtime-design-without-integration-v0.md
- docs/evals/product-delta-pr71-pr84-packaging-gate-v0.md
- docs/evals/product-delta-evidence-boundary-lint-v0.md
- docs/evals/product-delta-specialist-review-contracts-v0.md
- docs/conversation-understanding/audit-decision-record-v0.md
- docs/conversation-understanding/audit-decision-record-v0.json

Inspect code, not only docs:
- scripts/run_extract.py
- engine/system_b/conversation_context.py
- engine/system_b/ir.py
- engine/system_b/ir_constructor.py
- engine/system_b/audit_decision_record.py
- engine/system_b/agent_result.py
- engine/system_b/product_delta_readiness.py
- engine/system_b/product_delta_boundary_lint.py
- engine/system_b/product_delta_specialist_packets.py

Also inspect:
- git status --short --branch --untracked-files=all
- git log --oneline -n 12

Important current truth:
The Lolla runtime is the producer of audit artifacts.
The Decision Trail lane is an offline reader/reporting surface over completed artifacts.
PR86 must not invoke the runtime, run the skill, or add exporter behavior.

Core doctrine:
Messy interpretation belongs to LLMs or later human review.
Deterministic code may preserve custody, status, source refs, missingness, schemas, validation, and non-claims.
Deterministic code must not infer user values, live options, useful/noisy friction, lost value, stakeholder obligations, likely next action, or answer quality from messy prose.

Implement PR86 only.

Create:
- docs/conversation-understanding/decision-trail-report-prd-v0.md
- docs/conversation-understanding/decision-trail-report-v0.json
- tests/test_decision_trail_report_schema.py if useful for schema/contract validation

Update discoverability docs lightly:
- PROGRESS.md
- HOW_IT_WORKS.md
- README.md if appropriate
- docs/conversation-understanding/decision-trail-pr86-pr89-prd-v0.md only if the PR86 completion state needs to be recorded

The PRD doc should explain:
- what the Decision Trail report is;
- what problem it solves;
- what it is not;
- how it relates to runtime, ADR, Product Delta, agent_result, evaluation, and reasoning_trace;
- field ownership;
- checked-in safe mode versus local private mode;
- redaction versus missingness;
- optional future trace compatibility without adopting external tracing dependencies;
- why deterministic code must not fill messy interpretation fields;
- expected PR87 exporter behavior at a design level only;
- validation and non-claims.

The JSON schema should define:
- schema_version: lolla.decision_trail_report.v0
- report metadata
- source_artifacts
- custody_flags
- trace_context
- report_mode
- conversation_understanding_summary
- decision_question
- vanilla_likely_next_action
- revised_likely_next_action
- option_map
- constraints
- stakeholders
- values_or_priorities
- assistant_influence
- audit_pressure_summary
- structural_delta
- useful_noisy_friction
- lost_value
- unresolved_questions
- artifact_health
- field_population_policy
- limitations
- non_claims

Every semantic section should support:
- status
- source_status
- source_refs
- value or items
- empty_meaning
- owner
- requires_llm_interpretation
- exporter_inferred_from_prose

Required status vocabulary should include:
- not_supplied
- not_measured
- not_applicable
- available_from_structured_artifact
- available_from_review_artifact
- available_but_redacted_in_safe_mode
- available_in_private_artifact_not_exported
- requires_llm_interpretation
- unavailable_missing_artifact
- unavailable_malformed_artifact
- unclear

Report modes:
- checked_in_safe_mode
- local_private_mode
- future_runtime_mode_not_implemented

Trace context:
Add optional future-compatible trace fields only. Do not depend on OpenTelemetry, OpenInference, OpenAI Agents tracing, or any external tracing package.

Suggested fields:
- trace_context.status
- trace_context.source_refs
- trace_context.external_trace_id
- trace_context.otel_genai_semconv_status
- source_artifacts[*].activity_kind
- source_artifacts[*].generated_by
- source_artifacts[*].used_by

Allowed trace statuses:
- not_used
- future_compatible
- experimental_mapping

Boundary:
Do not:
- run $lolla
- invoke the Lolla skill
- call provider/model APIs
- mutate archives
- change runtime behavior
- change prompts
- touch SKILL.md
- touch scripts/skill/*
- add exporter code
- add model calls
- add a judge
- add answer-quality scoring
- add automatic labels
- add safe_for_agent_use
- add graph DB, memory, embeddings, chunking, or GraphRAG
- claim product proof
- treat clean artifacts as proof of good advice

Validation:
Run focused checks appropriate for docs/schema:
- jq . docs/conversation-understanding/decision-trail-report-v0.json
- python3 -m py_compile tests/test_decision_trail_report_schema.py if a test file is added
- python3 -m pytest -q tests/test_decision_trail_report_schema.py if a test file is added
- python3 scripts/evals/lint_product_delta_evidence.py --paths <touched decision-trail docs/json>
- git diff --check
- local Markdown link check over touched Markdown
- trailing whitespace scan over touched files
- privacy/content marker scan over touched docs/json/tests

Expected result:
PR86 should leave the repo with a clear, reviewable Decision Trail report PRD and schema.
It should make PR87 straightforward, but it must not implement PR87.

Final response should include:
- files created/updated
- summary of the schema
- what was deliberately not changed
- validation run and results
- boundary confirmation
- recommended next PR: PR87 Decision Trail Read-Only Exporter v0
```
