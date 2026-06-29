# PR88 Decision Trail Fixture Review Goal Prompt v0

Use this prompt in a fresh coder session.

```text
/goal

Objective:
Implement PR88: Decision Trail Fixture Review v0 for the Lolla repo.

Repository:
Use the current `lolla-skill-public-runtime` repo root.

Current stage:
PR86 is complete. It defined the Decision Trail report PRD and schema:
- docs/conversation-understanding/decision-trail-report-prd-v0.md
- docs/conversation-understanding/decision-trail-report-v0.json
- tests/test_decision_trail_report_schema.py

PR87 is complete. It implemented the read-only Decision Trail exporter:
- engine/system_b/decision_trail_report.py
- scripts/evals/build_decision_trail_report.py
- tests/test_decision_trail_report.py
- docs/conversation-understanding/decision-trail-readonly-exporter-v0.md

PR88 should review generated Decision Trail reports for usefulness, missingness,
readability, and overtrust risk.

Do not implement PR89.
Do not add new interpretation machinery.
Do not change the Lolla runtime.

Read first:
- PROGRESS.md
- HOW_IT_WORKS.md
- README.md
- docs/conversation-understanding/decision-trail-pr86-pr89-prd-v0.md
- docs/conversation-understanding/decision-trail-report-prd-v0.md
- docs/conversation-understanding/decision-trail-report-v0.json
- docs/conversation-understanding/decision-trail-readonly-exporter-v0.md
- docs/conversation-understanding/decision-trail-readiness-audit-v0.md
- docs/lolla-decision-trail-web-page-v0.md
- docs/evals/product-delta-pr71-pr84-packaging-gate-v0.md
- docs/evals/product-delta-evidence-boundary-lint-v0.md

Inspect code and existing reports before editing:
- engine/system_b/decision_trail_report.py
- scripts/evals/build_decision_trail_report.py
- tests/test_decision_trail_report.py
- tests/test_decision_trail_report_schema.py
- engine/system_b/audit_decision_record.py
- tests/test_audit_decision_record.py
- engine/system_b/product_delta_boundary_lint.py

Also inspect:
- git status --short --branch --untracked-files=all
- git log --oneline -n 12

Important current truth:
The Lolla runtime is the producer of audit artifacts.
The Decision Trail exporter is an offline reader/reporting tool over completed artifacts.
PR88 is an offline fixture/review slice over PR87 outputs.

Core doctrine:
Messy interpretation belongs to LLMs or later human review.
Deterministic code may preserve custody, source refs, artifact health,
missingness, redaction/private availability, schema status, validation, and
non-claims.
Deterministic code must not decide whether the advice is good, whether Lolla
improved the decision, or what the messy conversation "really meant."

Implement PR88 only.

Create likely files:
- docs/conversation-understanding/decision-trail-export-fixture-review-v0.md
- reviews/codex-assisted/decision-trail-fixture-review-v0/review.json
- tests/test_decision_trail_fixture_review.py
- optional checked-in-safe exported report fixtures under
  reviews/codex-assisted/decision-trail-fixture-review-v0/ only if they contain
  no raw/private content and pass lint

Update discoverability docs lightly:
- PROGRESS.md
- HOW_IT_WORKS.md
- README.md if appropriate
- docs/conversation-understanding/decision-trail-pr86-pr89-prd-v0.md to record
  PR88 completion state and point to PR89 next
- docs/conversation-understanding/decision-trail-readonly-exporter-v0.md if it
  needs a short PR88 link

Evidence mode:
PR88 should include one of two modes:

1. checked_in_safe_fixture_review
   Use generated Decision Trail reports over safe structured fixtures only.
   This is expected and acceptable if no local-private review is safe.

2. local_private_shadow_review_not_checked_in
   Optionally run a local-only shadow review over at least one real archive if
   safe and available. Do not check in raw/private content. Do not copy raw
   transcript, raw memo, raw revised answer, provider text, private ledgers, or
   local absolute paths into repo files. If this mode is not used, say so
   explicitly.

If only checked-in safe fixtures are used, PR88 must say:
- no local-private shadow review was run;
- PR89 must treat the evidence as safe-fixture-only;
- compressed safe context may make the report look thinner than a real private
  archive review would.

Fixture/report generation:
- Use the PR87 CLI to generate one or more temp Decision Trail reports.
- Output paths must stay outside the run directory.
- Prefer small, reviewable fixtures.
- Checked-in fixture reports are allowed only if they contain no raw/private
  content, no local absolute paths, and no provider/model text.
- Do not expand the case set just to make the evidence look better.

Review should answer:
- Which fields populate from existing structured artifacts?
- Which fields are missing or only status-marked?
- Which fields are available only privately or redacted in checked-in safe mode?
- Does the report help a reviewer understand how the answer moved?
- Does it make interpretation gaps visible?
- Does it show where LLM interpretation would be needed next?
- Does it create overtrust?
- Can a reviewer quickly answer:
  - what changed?
  - what evidence supports the change?
  - what is missing?
  - what must not be claimed?
  - did the report make the reviewer more careful, or merely more impressed?

Review JSON shape:
Use a conservative schema/version such as:
- schema_version: lolla.decision_trail_fixture_review.v0
- review_mode
- human_validated: false
- product_proof: false
- model_calls: 0
- archive_mutated: false
- runtime_invoked: false
- skill_invoked: false
- evidence_scope
- source_reports
- local_private_shadow_review_status
- report_reviews
- aggregate_observations
- PR89_recommendation

For each report review, include:
- report_ref
- source_run_ref
- report_mode
- field_population_summary
- populated_sections
- interpretation_needed_sections
- redacted_or_private_sections
- missing_or_malformed_artifacts
- confusing_sections
- overtrust_risk_sections
- behavioral_usefulness:
  - what_changed_answerable
  - evidence_support_answerable
  - missingness_answerable
  - non_claims_answerable
  - more_careful_or_more_impressed
- report_readability
- artifact_custody_read
- semantic_interpretation_adequacy_read
- product_delta_usefulness_read
- human_validation_read
- blockers
- human_followup_questions

Section classification vocabulary:
- clear_and_populated
- clear_but_missing
- confusing
- overclaim_risk
- requires_llm_interpretation
- requires_human_review
- not_applicable

Required review notes:
- what this report made easier to see
- what this report failed to preserve
- where checked-in safe mode is too thin
- whether missingness is legible
- whether redacted/private-available differs clearly from missing
- whether clean artifact health could accidentally make weak reasoning look
  stronger than it is

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
- add a broad judge
- add answer-quality scoring
- add automatic labels
- add agent-readiness authorization fields
- add graph DB, memory, embeddings, chunking, or GraphRAG
- infer user values, live options, likely next action, lost value, useful/noisy
  friction, stakeholder obligations, or answer quality from messy prose
- claim product proof
- treat clean artifacts as proof of good advice

Code-change rule:
PR88 is docs, safe fixtures, and review notes.
Do not change PR87 exporter code unless a blocking PR87 bug prevents review.
If such a blocker exists, stop and report it instead of silently turning PR88
into an exporter-fix PR.

Validation:
Run focused checks appropriate for review fixtures:
- python3 -m py_compile tests/test_decision_trail_fixture_review.py
- python3 -m pytest -q tests/test_decision_trail_fixture_review.py tests/test_decision_trail_report.py tests/test_decision_trail_report_schema.py tests/test_product_delta_boundary_lint.py
- jq . reviews/codex-assisted/decision-trail-fixture-review-v0/review.json
- jq . <any checked-in-safe exported report fixture>
- python3 scripts/evals/lint_product_delta_evidence.py --paths <PR88 docs/json/reports plus touched Decision Trail docs>
- git diff --check
- local Markdown link check over touched Markdown
- trailing whitespace scan over touched files
- privacy/content marker scan over touched docs/json/tests/generated outputs

Tests should prove:
- PR88 review JSON uses schema_version lolla.decision_trail_fixture_review.v0
- human_validated is false
- product_proof is false
- model_calls is 0
- archive_mutated is false
- runtime_invoked is false
- skill_invoked is false
- source report refs resolve when checked in
- checked-in reports do not contain raw/private markers
- checked-in reports do not contain local absolute paths
- classification values come from the approved PR88 vocabulary
- every report review includes behavioral usefulness fields
- every positive usefulness note has a non-human-validation caveat
- no report implies a good decision merely because artifacts are complete
- local_private_shadow_review_status is explicit
- if no local-private shadow review was run, evidence_scope is safe-fixture-only

Expected result:
PR88 should tell maintainers whether the PR87 Decision Trail report is useful,
too sparse, too confusing, or too authoritative-looking before any new
conversation-interpretation machinery is added.

Final response should include:
- files created/updated
- reports generated or reviewed
- whether local-private shadow review was run or explicitly not run
- field population summary
- strongest usefulness signal
- strongest overtrust/thinness risk
- what PR89 should decide next
- validation run and results
- boundary confirmation
- recommended next PR: PR89 Conversation Interpretation Gap Decision v0
```
