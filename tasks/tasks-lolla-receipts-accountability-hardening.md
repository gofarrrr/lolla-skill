## Relevant Files

- `plans/lolla-receipts-accountability-hardening-plan-2026-05-11.md` - Source plan and architectural rationale for this hardening pass.
- `engine/system_b/structural_coverage.py` - Lane 4 orchestration; currently hides multiple LLM calls behind one lane function.
- `engine/system_b/pipeline.py` - Main pipeline assembly and telemetry capture; currently captures stale Lane 4 boundary metadata after the lane returns.
- `engine/system_b/boundary_tracing.py` - Boundary-call trace construction helper used by pipeline telemetry.
- `tests/test_structural_coverage_contextual.py` - Existing structural coverage behavior tests; add trace-truth regression coverage here or in a focused companion test.
- `scripts/run_extract.py` - Conversation extraction entry point; needs consistent output writing and capture criticality handling.
- `tests/test_run_extract.py` - Extraction CLI/edge-path tests for output-file writing and capture diagnostics.
- `engine/system_b/v60_enrichment.py` - V60 candidate selection, card building, ledger schema, ledger validation, and finalization.
- `scripts/finalize_v60_telemetry.py` - Finalizes V60 ledger health after runner consideration.
- `scripts/archive_run.py` - Archive path; should finalize V60 and product-output hygiene before copying artifacts.
- `tests/test_v60_enrichment_runtime.py` - Runtime tests for V60 packet construction, ledger validation, and finalization.
- `tests/test_archive_run_v60_telemetry.py` - Archive/finalization tests for V60 telemetry and run health behavior.
- `scripts/run_pipeline.py` - Run health construction, embedding state reporting, and pipeline result assembly.
- `tests/test_run_pipeline_contract_default.py` - Pipeline contract tests; extend for structured health severity behavior.
- `engine/system_b/output_hygiene.py` - New deterministic scanner for product-facing output hygiene.
- `tests/test_output_hygiene.py` - New unit tests for product-output hygiene scanning and role-specific allow/ban behavior.
- `scripts/render_memo.py` - Deterministic memo renderer; already has some product-clean stripping and should integrate with hygiene expectations.
- `tests/test_render_memo.py` - Existing memo hygiene tests; keep as renderer-specific coverage.
- `engine/system_b/embedding_retriever.py` - Embedding retrieval and RRF score source; relevant to V60 selection and Observatory score labeling.
- `observatory/serve_result.py` - Operator-facing audit view; should display corrected health, V60 selection reasons, score labels, and later comparison entry points.
- `scripts/compare_archived_runs.py` - New CLI/Markdown archived-run comparison report.
- `tests/test_compare_archived_runs.py` - New tests for comparison eligibility, health-first reporting, and output schema.
- `SKILL.md` - Live skill orchestration instructions; update after ledger skeleton and hygiene flow changes.
- `references/private-enrichment-treatment.md` - Private V60 treatment guidance for the runner.
- `references/chat-output-format.md` - User-facing chat hygiene and delivery guidance.
- `references/memo-output-format.md` - Memo output contract and banned machinery language.
- `HOW_IT_WORKS.md` - System architecture document; update after implementation changes stabilize.

### Notes

- This task list should be implemented with vertical red-green-refactor slices: one behavior test, one minimal implementation, repeat.
- Prefer tests that exercise public behavior and archived/run artifacts, not private implementation details.
- Do not run more paid live `/lolla` comparisons until receipt-truth and accountability gates are in place.
- Use `PYTHONPATH=. pytest path/to/test.py` for targeted tests. Prefer targeted tests while iterating, then run the smallest relevant regression set before committing.
- Route/disposition tests must align with the current V60 route enum unless the implementation deliberately migrates the enum:
  - `updated_position`
  - `pressure_check`
  - `private_guardrail`
  - `evidence_gate`
  - `diagnostic_question`
  - `set_aside`
  - `already_covered`
  - `irrelevant`
  - `missing_evidence`
  - `duplicate`
- Proposed route/disposition compatibility for the first strict validator pass:
  - `used`: `updated_position`, `pressure_check`, `private_guardrail`, `evidence_gate`, `diagnostic_question`
  - `rejected`: `set_aside`, `already_covered`, `irrelevant`, `missing_evidence`, `duplicate`
  - `deferred`: `set_aside`, `missing_evidence`, `evidence_gate`, `diagnostic_question`
  - `not_considered`: `already_covered`, `duplicate`, `irrelevant`
- Before implementing route/disposition validation, decide whether `set_aside` means rejected-after-consideration, deferred-for-later, or both. The compatibility table above treats it as both `rejected` and `deferred` for now.

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps.

Example:
- `- [ ] 1.1 Read file` -> `- [x] 1.1 Read file` (after completing)

Update the file after completing each sub-task, not just after completing an entire parent task.

## Tasks

- [x] 0.0 Create feature branch
  - [x] 0.1 Create and checkout a new branch, e.g. `git switch -c feature/lolla-receipts-accountability-hardening`.
  - [x] 0.2 Confirm the branch starts from the intended base and note any unrelated dirty working-tree files before editing.

- [x] 1.0 Fix Lane 4 boundary trace truth
  - [x] 1.1 RED: Add a failing test for a Lane 4 run with gap questions that expects three distinct boundary stages: `structural_coverage_classification`, `structural_coverage_detection`, and `structural_coverage_gap_questions`.
  - [x] 1.2 In the same test, make the fake boundary return distinct payload/token metadata per call so stale `last_call_metadata` reuse is observable.
  - [x] 1.3 GREEN: Add a `StructuralCoverageRun` result object or equivalent trace-returning wrapper that carries both the `StructuralCoverageCard` and immediate boundary-call traces.
  - [x] 1.4 Capture classification metadata immediately after `run_question_classification_from_packet` returns.
  - [x] 1.5 Capture dimension-detection metadata immediately after `run_dimension_detection_from_packet` returns.
  - [x] 1.6 Capture gap-question metadata immediately after `generate_gap_questions_from_packet` returns when gap routes exist.
  - [x] 1.7 Update `pipeline._run_lane4_structural_coverage` to append returned Lane 4 traces instead of reading `boundary.last_call_metadata` after the full lane returns.
  - [x] 1.8 RED: Add a no-gap Lane 4 test that expects exactly two distinct traces and no gap-question trace.
  - [x] 1.9 GREEN: Preserve or add a compatibility function for callers that only need the `StructuralCoverageCard`.
  - [x] 1.10 Verify `usage_summary` and Observatory inputs receive the corrected per-stage traces.
  - [x] 1.11 REFACTOR: Remove any leftover post-hoc Lane 4 trace capture that can still read stale `last_call_metadata`.
  - [x] 1.12 Run targeted structural coverage and pipeline contract tests.

- [x] 2.0 Fix extraction output consistency and capture criticality
  - [x] 2.1 RED: Add a test proving the `not_strategic` path writes `--output-file` and includes `capture_manifest`, `capture_health`, and `capture_warnings`.
  - [x] 2.2 GREEN: Add a centralized `_emit_result` helper in `scripts/run_extract.py` that prints JSON, writes `--output-file` when provided, and attaches capture diagnostics.
  - [x] 2.3 Migrate the `not_strategic` branch to `_emit_result`.
  - [x] 2.4 RED: Add a test proving the missing-required-field path writes `--output-file` and includes capture diagnostics.
  - [x] 2.5 GREEN: Migrate the missing-required-field branch to `_emit_result`.
  - [x] 2.6 RED: Add a test for a no-header transcript ending on a user turn; expected `capture_health` is `critical`.
  - [x] 2.7 GREEN: Update capture validation so final-user-turn criticality overrides missing-header `unknown`.
  - [x] 2.8 RED: Add a test for a no-header transcript ending on an assistant turn; expected result is non-critical but warning-bearing.
  - [x] 2.9 GREEN: Preserve non-critical behavior for recoverable no-header transcripts.
  - [x] 2.10 Migrate any remaining API-error or early-return output branches to `_emit_result` if they can currently bypass output-file writing.
  - [x] 2.11 REFACTOR: Keep successful extraction output shape backward-compatible.
  - [x] 2.12 Run targeted extraction tests.

- [x] 3.0 Harden V60 ledger accountability and reduce Step 6 structure invention
  - [x] 3.1 RED: Add a test that builds V60 enrichment and expects a deterministic ledger skeleton with exactly one transaction shell per selected chunk.
  - [x] 3.2 GREEN: Implement a ledger skeleton builder in `engine/system_b/v60_enrichment.py`.
  - [x] 3.3 Include non-runner-editable identity fields in every skeleton row: `chunk_id`, `card_id`, `model_id`, `chunk_kind`, and selection/source metadata where available.
  - [x] 3.4 Add runner-fillable fields to the skeleton: `disposition`, `route`, `strongest_plausible_application`, `why`, `visible_effect`, `private_guardrail`, and `risk_if_forced`.
  - [x] 3.5 Add absence-specific skeleton fields such as `blocked_or_guarded_claim` and `uncertainty_boundary` for `chunk_kind == "absence"`.
  - [x] 3.6 RED: Add validator tests that reject mismatched `card_id`, `model_id`, or `chunk_kind` for a known `chunk_id`.
  - [x] 3.7 GREEN: Validate each ledger transaction against the deterministic skeleton identity map.
  - [x] 3.8 RED: Add validator tests for route/disposition contradictions, using the current route enum. Include at least `used + irrelevant`, `used + missing_evidence`, `rejected + updated_position`, and `rejected + pressure_check`.
  - [x] 3.9 GREEN: Implement route/disposition compatibility validation.
  - [x] 3.10 RED: Add tests that reject `used` affordance chunks with neither `visible_effect` nor `private_guardrail`.
  - [x] 3.11 GREEN: Require `visible_effect` or explicit `private_guardrail` for `used` transactions.
  - [x] 3.12 RED: Add tests that reject `used` absence chunks without `blocked_or_guarded_claim` or `uncertainty_boundary`.
  - [x] 3.13 GREEN: Implement absence-specific blocker/guardrail validation.
  - [x] 3.14 Ensure summary counts are computed from transactions rather than trusted from runner-written freeform fields.
  - [x] 3.15 Persist the skeleton both in `result.json` and as a runner-friendly sidecar if the orchestration flow needs a file to fill.
  - [x] 3.16 Update `scripts/finalize_v60_telemetry.py` and `scripts/archive_run.py` so missing, invalid, or contradiction-bearing active V60 ledgers degrade health with specific issue codes.
  - [x] 3.17 Update `SKILL.md` and `references/private-enrichment-treatment.md` so the runner fills the skeleton instead of inventing ledger structure.
  - [x] 3.18 REFACTOR: Keep older archived result compatibility where possible, but make active current-run validation strict.
  - [x] 3.19 Run targeted V60 enrichment and archive telemetry tests.

- [x] 4.0 Introduce run health severities
  - [x] 4.1 RED: Add a run-health test proving optional embeddings-off does not make `overall` degraded when embeddings are not required.
  - [x] 4.2 GREEN: Add structured `issue_details` with `code`, `severity`, `axis`, `trust_impact`, and mode/requirement metadata while preserving legacy `issues`.
  - [x] 4.3 Compute `overall` from highest severity rather than from the mere presence of any issue.
  - [x] 4.4 RED: Add tests proving capture-critical remains `overall: critical` and active V60 invalid/missing ledger remains `overall: degraded`.
  - [x] 4.5 GREEN: Map known health issue codes to the new severity model.
  - [x] 4.6 Update Observatory health rendering to show structured issue severity without forcing operators to decode raw issue strings.
  - [x] 4.7 Run targeted health tests.

- [x] 4B.0 Add product-output hygiene gate
  - [x] 4B.1 RED: Add output-hygiene tests for clean product artifacts containing banned internal terms such as `V60`, `affordance`, `chunk`, `ledger`, and `independent review`.
  - [x] 4B.2 GREEN: Add `engine/system_b/output_hygiene.py` with role-aware deterministic scanning for `revised_answer`, clean memo, audit appendix, and Observatory/operator surfaces.
  - [x] 4B.3 Add allowlist or role logic so legitimate operator/audit surfaces can contain internal terms while clean product artifacts cannot.
  - [x] 4B.4 Wire hygiene scanning into archive/finalization so runs record `product_output_health`, `product_output_leak_count`, and leak details.
  - [x] 4B.5 Decide and implement whether clean-artifact leaks set overall health to `partial`, `degraded`, or a separate `product_output_health: unsafe` axis based on plan guidance.
  - [x] 4B.6 Update Observatory health rendering to show product-output health.
  - [x] 4B.7 REFACTOR: Reuse existing memo hygiene tests where possible instead of duplicating renderer-specific assertions in the scanner tests.
  - [x] 4B.8 Run targeted archive, memo, and output-hygiene tests.

- [x] 5.0 Improve V60 chunk and absence selection quality
  - [x] 5.1 RED: Add a V60 selection test where the first affordance is not the most relevant one and the expected selected affordance is chosen by case/lane evidence.
  - [x] 5.2 GREEN: Replace normal `_build_card` `[:1]` affordance selection with a local scoring function that considers decision situation, constraints, dropped threads, lane reason, and evidence.
  - [x] 5.3 Preserve `record_order_first` only as an explicit fallback and record when fallback is used.
  - [x] 5.4 RED: Add a test where a selected model has multiple absence records and only one matches a specific overclaim or missing-evidence risk.
  - [x] 5.5 GREEN: Add absence-specific scoring that selects absence records because of blocker/guardrail signals, not merely because the parent model was selected.
  - [x] 5.6 Add selection telemetry fields: selected chunk score, selected chunk reason, sibling alternatives considered/skipped, and absence blocker reason.
  - [x] 5.7 Update Observatory V60 audit labels to distinguish lane custody, local chunk relevance, embedding recall, hybrid rank, and absence guardrail selection.
  - [x] 5.8 Update embedding score labels so RRF/fusion scores are not presented as semantic confidence.
  - [x] 5.9 RED: Add a cap-pressure fixture proving known useful chunks are recovered without increasing `--v60-max-cards`.
  - [x] 5.10 GREEN: Add simple diversity/effect-type slotting only after local relevance and absence selection are observable.
  - [x] 5.11 Run offline replay checks on known cases before any paid live run.
  - [x] 5.12 REFACTOR: Keep the selection interface small; avoid spreading scoring heuristics across unrelated modules.

- [x] 6.0 Add first-class CLI/Markdown archived-run comparison
  - [x] 6.1 RED: Add a comparison test that loads two archived-run-like fixtures and expects the report to start with trace/product-health eligibility before answer-quality claims.
  - [x] 6.2 GREEN: Create `scripts/compare_archived_runs.py` with a small public CLI for comparing two archive paths or a case/run-id pair.
  - [x] 6.3 Emit both JSON and Markdown outputs.
  - [x] 6.4 Include final answer diff and memo diff, but place them after health, trace, hygiene, and eligibility summaries.
  - [x] 6.5 Include V60 selected cards/chunks, ledger disposition counts, capture/quote health, output-hygiene status, embedding mode, and usage/cost differences.
  - [x] 6.6 RED: Add a test proving comparison warns or refuses to call a comparison trustworthy when either run has untrusted telemetry.
  - [x] 6.7 GREEN: Implement comparison eligibility rules based on corrected health severities and product-output hygiene.
  - [x] 6.8 Map visible V60 impact into plain effect categories such as missing option, executable test, hidden assumption, evidence gate, uncertainty boundary, private guardrail, or clean no-op.
  - [x] 6.9 Add a short README/help output for the comparison CLI.
  - [x] 6.10 REFACTOR: Keep comparison logic reusable so Observatory can later consume the same schema instead of re-implementing comparison.
  - [x] 6.11 Run targeted comparison tests.

- [x] 7.0 Update docs, orchestration references, and targeted regression coverage
  - [x] 7.1 Update `HOW_IT_WORKS.md` to describe corrected Lane 4 tracing, extraction output guarantees, V60 ledger skeleton, health severities, hygiene gate, and comparison flow.
  - [x] 7.2 Update `plans/lolla-receipts-accountability-hardening-plan-2026-05-11.md` if implementation choices diverge from the draft plan.
  - [x] 7.3 Update `SKILL.md` to reflect the new Step 6 flow: fill deterministic ledger skeleton privately, then compose clean public output, then hygiene/finalization runs.
  - [x] 7.4 Update `references/private-enrichment-treatment.md` with the revised ledger skeleton contract and absence-blocker expectations.
  - [x] 7.5 Update `references/chat-output-format.md` and `references/memo-output-format.md` with the product-output hygiene gate and banned/allowed surface distinctions.
  - [x] 7.6 Add or update Observatory operator text so it explains corrected trace/health/selection signals without implying scores are semantic confidence.
  - [x] 7.7 Run the focused regression set covering structural coverage, extraction, V60 enrichment, archive/finalization, health, hygiene, render memo, and comparison.
  - [x] 7.8 Run a cheap local fixture/replay if available; do not run paid live `/lolla` unless explicitly approved after P0/P1 gates pass.
  - [x] 7.9 Review generated artifacts for product-language leakage manually once after the deterministic scanner passes.
  - [x] 7.10 Commit the completed hardening pass with a message that names the receipt/accountability changes, not just “V60 improvements.”

- [x] 8.0 Post-flight amendments from archived live run
  - [x] 8.1 RED/GREEN: Add V60 finalization idempotency coverage for invalid-to-valid ledger reruns.
  - [x] 8.2 GREEN: Clear stale missing/invalid V60 ledger issues and issue details before re-validating.
  - [x] 8.3 RED/GREEN: Add product-output hygiene idempotency coverage for unsafe-to-clean reruns.
  - [x] 8.4 GREEN: Clear stale product-output leak issues and issue details when a later clean artifact is finalized.
  - [x] 8.5 RED/GREEN: Allow normal domain language such as `sales pipeline` while still flagging internal pipeline narration.
  - [x] 8.6 GREEN: Add `--require-valid` to V60 finalization and update orchestration docs to stop on invalid ledgers before pressure checks, memo rendering, Observatory, or archive.
  - [x] 8.7 RED/GREEN: Add live-narration hygiene coverage for observed phrases such as `Beat 2`, `pressure-check agents`, `V60`, and `ledger`.
  - [x] 8.8 GREEN: Extend product-output hygiene patterns and orchestration docs so live Claude Code narration is treated as product surface.
  - [x] 8.9 RED/GREEN: Filter noisy V60 local-relevance explanation terms such as `after`, `all`, `before`, `being`, and `should`.
  - [x] 8.10 RED/GREEN: Guard against reintroducing the old instruction to launch pressure-check agents before the V60 ledger gate.
  - [x] 8.11 Run the focused post-flight regression tests.
