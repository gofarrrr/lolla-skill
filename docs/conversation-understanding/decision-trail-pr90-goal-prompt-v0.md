# PR90 Decision Trail Interpretation Specialist Contracts Goal Prompt v0

Use this prompt in a fresh coder session.

```text
/goal

Objective:
Implement PR90: Decision Trail Interpretation Specialist Contracts v0 for the Lolla repo.

Repository:
Use the current `lolla-skill-public-runtime` repo root.

Current stage:
PR86 through PR89 are complete.

PR86 created the Decision Trail report PRD and schema.
PR87 implemented the read-only Decision Trail exporter.
PR88 reviewed the exported report shape and found it useful as a custody and
missingness shell, but too sparse for the full Decision Trail product.
PR89 selected the next path: narrow offline LLM specialist contracts for the
missing messy interpretation fields.

PR90 should define those contracts only.

Do not build a packet builder.
Do not run specialists.
Do not call models.
Do not implement fan-in execution.
Do not integrate with the Lolla runtime.

Read first:
- PROGRESS.md
- HOW_IT_WORKS.md
- README.md
- docs/conversation-understanding/decision-trail-interpretation-gap-decision-v0.md
- docs/conversation-understanding/decision-trail-export-fixture-review-v0.md
- reviews/codex-assisted/decision-trail-fixture-review-v0/review.json
- docs/conversation-understanding/decision-trail-readonly-exporter-v0.md
- docs/conversation-understanding/decision-trail-report-prd-v0.md
- docs/conversation-understanding/decision-trail-report-v0.json
- docs/conversation-understanding/decision-trail-readiness-audit-v0.md
- docs/lolla-decision-trail-web-page-v0.md
- docs/evals/product-delta-evidence-boundary-lint-v0.md
- docs/evals/context-engineered-provisional-review-architecture-v0.md
- docs/evals/product-delta-specialist-review-contracts-v0.md
- docs/evals/product-delta-specialist-review-contracts-v0.json

Inspect code/tests patterns before editing:
- tests/test_decision_trail_report_schema.py
- tests/test_decision_trail_fixture_review.py
- tests/test_product_delta_specialist_contracts.py
- engine/system_b/product_delta_boundary_lint.py

Also inspect:
- git status --short --branch --untracked-files=all
- git log --oneline -n 12

Important current truth:
The Decision Trail shell exists and is useful for custody, source refs,
missingness, redaction/private availability, and non-claims.
It does not fill the messy product-load-bearing fields.

PR90 defines typed contracts for bounded offline LLM interpretation that may
later fill those fields under custody.

Core doctrine:
Messy interpretation belongs to bounded LLM specialist reads or later human
review.
Deterministic code preserves contracts, source refs, status, missingness,
uncertainty, disagreement, validation, and non-claims.
Deterministic code must not infer user values, live options, likely actions,
assistant influence, useful/noisy friction, lost value, or answer quality from
messy prose.

Implement PR90 only.

Create likely files:
- docs/conversation-understanding/decision-trail-specialist-contracts-v0.md
- docs/conversation-understanding/decision-trail-specialist-contracts-v0.json
- tests/test_decision_trail_specialist_contracts.py

Update discoverability docs lightly:
- PROGRESS.md
- HOW_IT_WORKS.md
- README.md if appropriate
- docs/conversation-understanding/decision-trail-interpretation-gap-decision-v0.md

Contract family:
Define a versioned contract family such as:

schema_version: lolla.decision_trail_specialist_contracts.v0

It should define future output contracts for exactly these four specialist
reads:

1. conversation_shape_reader
2. likely_action_reader
3. friction_lost_value_reader
4. conservative_fan_in_reader

Do not add more roles unless the PR89 decision doc clearly requires them.

Specialist 1: conversation_shape_reader
Purpose:
Identify the shape of the messy conversation for Decision Trail use.

It should cover:
- decision_question
- live_options
- option_status
- constraints
- stakeholders
- values_or_priorities
- assistant_influence
- dropped_threads
- unresolved_questions
- uncertainty

Specialist 2: likely_action_reader
Purpose:
Identify likely next actions before and after Lolla without claiming those
actions are good.

It should cover:
- vanilla_likely_next_action
- revised_likely_next_action
- action_delta
- threshold_delta
- sequence_delta
- evidence_gate_delta
- stop_rule_delta
- uncertainty

Specialist 3: friction_lost_value_reader
Purpose:
Separate useful friction from noisy friction and preserve lost value.

It should cover:
- useful_friction
- noisy_friction
- missing_friction
- lost_value
- value_overwrite_risk
- momentum_or_simplicity_loss
- overcaution_or_diligence_theater
- uncertainty

Specialist 4: conservative_fan_in_reader
Purpose:
Preserve disagreement and produce a conservative Decision Trail interpretation
summary without voting, scoring, or judging answer quality.

It should cover:
- areas_of_agreement
- disagreements_preserved
- high_uncertainty_fields
- fields_ready_for_report
- fields_not_ready_for_report
- human_followup_questions
- overtrust_risks
- next_review_priority

Shared contract requirements:
Every specialist output shape should include:
- specialist_role
- contract_version
- input_mode
- allowed_input_refs
- read_status
- source_refs
- source_status
- uncertainty
- evidence_strength
- fields
- limitations
- non_claims
- boundary metadata

Status/source vocabulary:
Use conservative vocabularies. Include values such as:
- not_supplied
- explicit_in_source
- inferred_from_source
- unclear
- contradicted
- requires_private_context
- available_but_redacted_in_safe_mode
- available_in_private_artifact_not_exported
- unavailable_missing_artifact
- unavailable_malformed_artifact

Input modes:
Define at least:
- checked_in_safe_mode
- local_private_mode
- future_runtime_mode_not_implemented

checked_in_safe_mode must exclude raw transcript, raw memo, raw revised answer,
provider text, private ledgers, local absolute paths, secrets, and private local
content.

local_private_mode may be defined for future use, but PR90 must not implement
it.

Boundary metadata:
Contracts should require lower-claim metadata such as:
- human_validated: false
- ground_truth: false
- judge_calibration_eligible: false
- product_proof: false
- answer_quality_scored: false
- agent_action_authorized: false
- model_calls: 0
- archive_mutated: false
- runtime_invoked: false
- skill_invoked: false
- automatic_labels_created: false
- raw_private_content_included: false for checked-in safe fixtures

Fan-in rule:
The conservative fan-in contract must not:
- vote
- average
- score
- certify
- approve
- choose a winner
- convert specialist agreement into correctness
- claim that Lolla changed decision quality

It should preserve tensions like:
- structural delta looks strong but lost value is unresolved
- likely action changed but values/priorities are unclear
- useful friction may also create momentum loss
- checked-in safe context is too thin to read assistant influence

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
- add packet builder code
- add model calls
- add specialist review outputs
- add fan-in execution
- add a broad judge
- add answer-quality scoring
- add automatic labels
- add agent-readiness authorization fields
- add graph DB, memory, embeddings, chunking, or GraphRAG
- claim product proof
- treat clean artifacts as proof of good advice

Validation:
Run focused checks appropriate for docs/schema:
- python3 -m py_compile tests/test_decision_trail_specialist_contracts.py
- python3 -m pytest -q tests/test_decision_trail_specialist_contracts.py tests/test_decision_trail_fixture_review.py tests/test_decision_trail_report_schema.py tests/test_product_delta_boundary_lint.py
- jq . docs/conversation-understanding/decision-trail-specialist-contracts-v0.json
- python3 scripts/evals/lint_product_delta_evidence.py --paths <PR90 docs/json plus touched overview docs>
- git diff --check
- local Markdown link check over touched Markdown
- trailing whitespace scan over touched files
- privacy/content marker scan over touched docs/json/tests

Tests should prove:
- schema_version is lolla.decision_trail_specialist_contracts.v0
- the four required specialist roles exist and no extra role is required
- all required boundary metadata defaults remain false or zero
- checked_in_safe_mode excludes raw/private/provider/local-absolute-path content
- local_private_mode is contract vocabulary only, not implemented behavior
- conservative_fan_in_reader forbids scoring, voting, approval, certification,
  winner selection, and correctness from agreement
- every specialist contract requires source refs, status/source status,
  uncertainty, limitations, and non-claims
- no forbidden authority field names exist
- no product-proof or human-validation claims exist

Expected result:
PR90 should leave the repo with a clear docs/schema contract for the next
Decision Trail interpretation layer.
It should prepare a future packet-builder PR, but not build it.

Final response should include:
- files created/updated
- specialist roles defined
- what PR90 deliberately did not implement
- validation run and results
- boundary confirmation
- recommended next PR: PR91 Decision Trail Specialist Packet Builder v0
```
