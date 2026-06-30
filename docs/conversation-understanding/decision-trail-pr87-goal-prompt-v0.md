# PR87 Decision Trail Read-Only Exporter Goal Prompt v0

Use this prompt in a fresh coder session.

```text
/goal

Objective:
Implement PR87: Decision Trail Read-Only Exporter v0 for the Lolla repo.

Repository:
Use the current `lolla-skill-public-runtime` repo root.

Current stage:
PR86 is complete. It created the Decision Trail report PRD and schema:
- docs/conversation-understanding/decision-trail-report-prd-v0.md
- docs/conversation-understanding/decision-trail-report-v0.json
- tests/test_decision_trail_report_schema.py

PR87 should implement a deterministic read-only exporter against the PR86 schema.
Do not implement PR88 fixture review or PR89 decision gate.

Read first:
- PROGRESS.md
- HOW_IT_WORKS.md
- README.md
- docs/conversation-understanding/decision-trail-pr86-pr89-prd-v0.md
- docs/conversation-understanding/decision-trail-report-prd-v0.md
- docs/conversation-understanding/decision-trail-report-v0.json
- docs/conversation-understanding/decision-trail-readiness-audit-v0.md
- docs/conversation-understanding/audit-decision-record-v0.md
- docs/conversation-understanding/audit-decision-record-v0.json
- docs/evals/product-delta-evidence-boundary-lint-v0.md
- docs/evals/product-delta-pr71-pr84-packaging-gate-v0.md

Inspect code patterns before editing:
- engine/system_b/audit_decision_record.py
- scripts/build_audit_decision_record.py
- tests/test_audit_decision_record.py
- engine/system_b/product_delta_boundary_lint.py
- engine/system_b/product_delta_readiness.py
- engine/system_b/agent_result.py
- engine/system_b/evaluation.py
- engine/system_b/reasoning_trace.py if present
- scripts/run_extract.py
- engine/system_b/conversation_context.py

Also inspect:
- git status --short --branch --untracked-files=all
- git log --oneline -n 12

Important current truth:
The Lolla runtime is the producer of audit artifacts.
The Decision Trail exporter is an offline reader/reporting tool over completed artifacts.
PR87 must not invoke the runtime, run the skill, call providers, or mutate archives.

Core doctrine:
Messy interpretation belongs to LLMs or later human review.
The deterministic exporter may preserve custody, source refs, artifact health, missingness, redaction/private availability, schema status, and non-claims.
The deterministic exporter must not infer user values, live options, useful/noisy friction, lost value, stakeholder obligations, likely next action, or answer quality from messy prose.

Implement PR87 only.

Create likely files:
- engine/system_b/decision_trail_report.py
- scripts/evals/build_decision_trail_report.py
- tests/test_decision_trail_report.py
- docs/conversation-understanding/decision-trail-readonly-exporter-v0.md
- optional checked-in-safe example output only if it contains no raw/private content and passes lint

Update discoverability docs lightly:
- PROGRESS.md
- HOW_IT_WORKS.md
- README.md if appropriate
- docs/conversation-understanding/decision-trail-pr86-pr89-prd-v0.md to record PR87 completion state

Exporter behavior:
- Input: archived run directory.
- Output: lolla.decision_trail_report.v0 JSON to an explicit output path outside the run directory.
- Default mode: checked_in_safe_mode.
- Optional local_private_mode may be accepted only if implemented safely; otherwise document it as deferred.
- Validate output path is outside the run directory, copying the audit_decision_record exporter pattern.
- Read structured artifacts only by default:
  - evaluation.json
  - agent_result.json
  - reasoning_trace.json
  - extraction_adequacy_report.json when present
  - extraction.json carefully
  - result.json carefully
- Do not read raw artifacts in checked_in_safe_mode:
  - conversation.txt
  - memo.md
  - revised.txt
  - live_transcript.txt
  - operator.log
  - private ledgers
  - raw provider/model messages

Field behavior:
- Populate artifact health and custody fields deterministically.
- Populate decision_question only from existing structured extraction fields, with source refs and exporter_inferred_from_prose: false.
- Populate revised likely action only if a safe structured source exists; otherwise mark requires_llm_interpretation or not_supplied.
- Mark live options, option status, values/priorities, stakeholders, assistant influence, useful/noisy friction, and lost value as requires_llm_interpretation unless a safe structured review artifact explicitly supplies them.
- Distinguish missing from redacted/private:
  - available_but_redacted_in_safe_mode
  - available_in_private_artifact_not_exported
- Every empty semantic field must include empty_meaning.
- Every semantic field must include owner, source_status, source_refs, requires_llm_interpretation, and exporter_inferred_from_prose.
- Trace context should stay future-compatible only; no external tracing dependency.

CLI behavior:
Create a CLI similar to:

python3 scripts/evals/build_decision_trail_report.py \
  --run-dir <archive-run-dir> \
  --out /tmp/decision_trail_report.json \
  --pretty

Required CLI constraints:
- Fail if output path is inside the run directory.
- Emit sanitized errors.
- Do not mutate archives.
- Do not call models.
- Write JSON only to the requested output path.
- Support pretty JSON output.

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
- add model calls
- add a judge
- add answer-quality scoring
- add automatic labels
- add an agent-readiness field
- add graph DB, memory, embeddings, chunking, or GraphRAG
- claim product proof
- treat clean artifacts as proof of good advice

Validation:
Run focused checks appropriate for exporter code:
- python3 -m py_compile engine/system_b/decision_trail_report.py scripts/evals/build_decision_trail_report.py tests/test_decision_trail_report.py
- python3 -m pytest -q tests/test_decision_trail_report.py tests/test_decision_trail_report_schema.py tests/test_audit_decision_record.py tests/test_product_delta_boundary_lint.py
- jq . docs/conversation-understanding/decision-trail-report-v0.json
- jq . <generated temp decision trail report>
- python3 scripts/evals/lint_product_delta_evidence.py --paths <touched decision-trail docs/json/generated-safe-example-if-any>
- git diff --check
- local Markdown link check over touched Markdown
- trailing whitespace scan over touched files
- privacy/content marker scan over touched docs/json/tests/generated outputs

Tests should prove:
- schema_version is lolla.decision_trail_report.v0
- exporter reads structured artifacts only in checked_in_safe_mode
- raw artifacts are not read in checked_in_safe_mode
- output path inside run dir is rejected
- missing/malformed structured artifacts are represented as status, not crashes unless the run dir itself is invalid
- model_calls is 0
- archive_mutated is false
- runtime_invoked is false
- skill_invoked is false
- human_validated is false
- product_proof is false
- answer_quality_scored is false
- automatic_labels_created is false
- agent_action_authorized is false
- deterministic exporter does not infer messy semantic fields from prose
- redaction/private-availability statuses are available and distinct from missingness
- every empty semantic section has empty_meaning
- trace_context has no external dependency

Expected result:
PR87 should leave the repo with a conservative read-only Decision Trail exporter that can generate a sparse but honest report from existing completed artifacts.
The report may be semantically thin. That is acceptable if missingness and redaction are explicit.

Final response should include:
- files created/updated
- CLI usage
- generated temp-output path used for smoke validation
- summary of populated versus not-populated fields
- what was deliberately not changed
- validation run and results
- boundary confirmation
- recommended next PR: PR88 Decision Trail Fixture Review v0
```
