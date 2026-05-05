# Decision Pressure Dry Surface And Coverage Priority

**Status:** Ready for implementation. Docs/research-only planning PR unless a tiny deterministic helper becomes necessary.

## Relevant Files

- `research/gate4-3case-decision-pressure-dry-surface-2026-05-05.md` - New docs-only artifact that compresses the existing 12-route Gate 4 readout into 1-3 total Decision Pressures.
- `research/affordance-batch3a-coverage-priority-2026-05-05.md` - New docs-only artifact that ranks missing v3 model coverage by Decision Pressure relevance before any Batch 3a extraction.
- `research/gate4-3case-product-readout-2026-05-05.md` - Existing deterministic 12-route Arm B/C product-readout packet.
- `research/gate4-3case-claude-code-review-2026-05-05.md` - Existing narrow external reviewer readout; useful product-shaping evidence, not formal Gate 4 evidence.
- `research/decision-pressure-surface-spec-2026-05-05.md` - Current product doctrine for Decision Pressure value modes, gates, provenance, compression, and anti-casuistry constraints.
- `.tmp/gate4_edge_probes_3case_deepseek_kimi_rerun_7742387/summary.json` - Existing 3-case calibration summary with missing coverage metadata.
- `data/compiled/model_affordances/affordances_v3.json` - Current compiled v3 affordance kernel; read-only input for coverage reasoning.
- `plans/knowledge-substrate-roadmap-2026-05-04.md` - Living roadmap; update only if PR13 materially changes next-step doctrine.
- `plans/knowledge-use-schema-2026-05-04.md` - Living schema doctrine; update only if PR13 materially changes extraction or surface-evaluation doctrine.

### Notes

- This is a docs/research-only PR. Do not run paid model calls, judges, or live `/lolla`.
- Do not modify runtime behavior, prompts, validators, or affordance records.
- Do not start broad Batch 3 extraction.
- Surface pulls extraction. Extraction does not push the product.
- If any tiny helper is needed to summarize missing coverage, prefer `jq`/existing artifacts first. Add code only if manual extraction becomes error-prone, and keep it deterministic.
- If tests are needed for a helper, use vertical TDD: one failing behavior test, minimal implementation, repeat. Do not write bulk imagined tests.

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps.

Example:
- `- [ ] 1.1 Read file` -> `- [x] 1.1 Read file` after completing.

Update the file after completing each sub-task, not just after completing an entire parent task.

## Tasks

- [x] 0.0 Create feature branch
  - [x] 0.1 Confirm the base branch contains the latest Decision Pressure doctrine, including `research/decision-pressure-surface-spec-2026-05-05.md` and `research/gate4-3case-claude-code-review-2026-05-05.md`.
  - [x] 0.2 Create and checkout a new branch for this PR, for example `feature/decision-pressure-pr13-dry-surface-coverage-priority`.
  - [x] 0.3 Run `git status --short` and note any pre-existing unrelated changes. Do not revert or clean unrelated work.

  Note: PR13 was branched as `feature/decision-pressure-pr13-dry-surface-coverage-priority`. The required doctrine/readout files are present in the working tree as pre-existing local research inputs; `git status --short` also showed pre-existing untracked `.assay/`, `.claude/`, `.tmp/`, multiple `plans/`, `research/`, `scripts/spikes/`, and unrelated `tasks/` files. These were left intact.

- [x] 1.0 Re-ground PR13 in the current Decision Pressure doctrine
  - [x] 1.1 Read `research/decision-pressure-surface-spec-2026-05-05.md` end-to-end, especially the accepted value modes, rejection modes, red-team constraints, provenance classes, global compression cap, and zero-output success mode.
  - [x] 1.2 Read `research/gate4-3case-product-readout-2026-05-05.md` to understand the 12 route pairs, Arm B/C probes, set-asides, missing coverage, and validation metadata.
  - [x] 1.3 Read `research/gate4-3case-claude-code-review-2026-05-05.md` as product-shaping reviewer evidence, not formal Gate 4 proof.
  - [x] 1.4 Read the current next-step sections in `plans/knowledge-substrate-roadmap-2026-05-04.md` and `plans/knowledge-use-schema-2026-05-04.md` so PR13 does not contradict the living doctrine.
  - [x] 1.5 Confirm the working doctrine in notes before writing artifacts: Decision Pressure is not a new lane, not a second public Pressure Check, not raw Arm B/C comparison, and not a reason to run broad Batch 3.
  - [x] 1.6 Record the current v3 corpus shape from `data/compiled/model_affordances/affordances_v3.json` for context: model record count, affordance count, and absence-record count.

  Doctrine note: Decision Pressure is a compact synthesis object that may feed existing Step 6, Step 8 Pressure Check, memo, or Observatory surfaces; it is not a fifth lane, not a second public Pressure Check, not raw Arm B/C display, and not a justification for broad Batch 3. Working corpus shape: `50` model records, `86` affordances, `83` absence records. Core line: Surface pulls extraction. Extraction does not push the product.

- [x] 2.0 Produce the 3-case Decision Pressure dry-surface artifact
  - [x] 2.1 Create `research/gate4-3case-decision-pressure-dry-surface-2026-05-05.md`.
  - [x] 2.2 Add metadata: date, status, inputs, non-goals, and the doctrine line: `Surface pulls extraction. Extraction does not push the product.`
  - [x] 2.3 Build a candidate inventory from the 12-route readout and Claude Code review. Include case ID, route ID, Arm C candidate probe, value mode, would-show-user label, coverage status, and why it might matter.
  - [x] 2.4 Apply the Coverage Gate first. Exclude or mark as Observatory-only any candidate with fake trace, missing v3 source coverage, or full-route coverage gap.
  - [x] 2.5 Apply the Action-Delta Gate. Keep only candidates that change what the user should verify, delay, test, document, monitor, dismiss, sequence, or stop.
  - [x] 2.6 Apply the Dismissal Gate. Suppress candidates that cannot be cleared by evidence, action, or user verification.
  - [x] 2.7 Apply the Bloat Gate. Suppress candidates that are merely more elaborate than Arm B or that require too much explanation to become useful.
  - [x] 2.8 Apply the global Compression Gate. Select only 1-3 total Decision Pressures across the entire 3-case sample, not one per route.
  - [x] 2.9 For each selected pressure, write the required fields: `Pressure`, `What to verify`, `Why it matters`, `Dismiss if`, `Tripwire or next action`, `Coverage`, `Provenance`, `Source route/case`, `Why this survived compression`, and `What was suppressed and why`.
  - [x] 2.10 Assign field-level provenance for each selected pressure using only `source_backed`, `case_grounded`, `llm_synthesized`, and `user_to_verify`.
  - [x] 2.11 Include an appendix with selected pressures, suppressed candidates, coverage gaps, zero-output candidates, and the recommended eventual receiving surface.
  - [x] 2.12 Explicitly evaluate tone range. If a relational/emotional candidate is selected, ensure it is humane and non-clinical; if none is selected, explain why that is a product finding rather than a case-type rule.

- [x] 3.0 Evaluate whether the compressed dry surface beats raw Arm B/C probes
  - [x] 3.1 Add a short evaluation section to the dry-surface artifact with the verdict options: `better_than_raw_probes`, `not_better_than_raw_probes`, or `inconclusive`.
  - [x] 3.2 Compare the compressed surface against reading the raw Arm B/C probe lists: does it reduce cognitive load, preserve the strongest pressure, and make the next user action clearer?
  - [x] 3.3 Check whether the selected pressures preserve coverage honesty and avoid machinery leaks.
  - [x] 3.4 Check whether any selected pressure could be generated by generic prompting alone. If yes, explain whether the added value is traceability, dismissal, tripwire, compression, or confirmation.
  - [x] 3.5 Recommend the eventual receiving surface: Observatory now, memo later, Step 8 Pressure Check later, or Step 6 later. Default to Observatory-first unless the artifact gives a reason to change.
  - [x] 3.6 Include a zero-output-success note explaining what a premium empty result would look like in this surface.

- [x] 4.0 Produce the Batch 3a coverage-priority report
  - [x] 4.1 Create `research/affordance-batch3a-coverage-priority-2026-05-05.md`.
  - [x] 4.2 Add metadata: date, status, inputs, non-goals, and the rule that coverage expansion is subordinate to the Decision Pressure surface.
  - [x] 4.3 Extract missing v3 model IDs from the 3-case calibration summary at `.tmp/gate4_edge_probes_3case_deepseek_kimi_rerun_7742387/summary.json`.
  - [x] 4.4 Locate the full 10-case Gate 4 dry-run summary or report referenced by PR11. Use existing committed or local artifacts only; do not run a paid model call.
  - [x] 4.5 Extract missing v3 model IDs from the full 10-case dry-run artifact.
  - [x] 4.6 For each missing model, record missing frequency, routes/cases affected, whether the absence creates a full-route coverage gap, and whether the missing model appeared in a product-relevant route.
  - [x] 4.7 Rank candidates by Decision Pressure relevance, not coverage statistics alone.
  - [x] 4.8 For each candidate, estimate likely high-value field yield from the source shape: `treatment_requirements`, `case_evidence_needed`, `misuse_guards`, `do_not_use_when`, dismissal logic, tripwires, stop conditions, or operational constraints.
  - [x] 4.9 For each candidate, consider whether an absence record may be the correct output instead of a runtime-useful affordance.
  - [x] 4.10 Include the starting candidate set from current evidence: `opportunity-cost`, `principal-agent-problem`, `true-uncertainty-navigation`, `probabilistic-thinking`, `falsifiability`, `batna`, `game-theory-payoffs`, `nash-equilibrium`, `prisoners-dilemma`, and `red-queen-effect`.
  - [x] 4.11 Include a clear warning against extracting models merely because they are missing.

- [x] 5.0 Decide whether targeted Batch 3a extraction is justified
  - [x] 5.1 Add a recommendation section to the coverage-priority report with one of these outcomes: `extract_0`, `extract_5`, `extract_8`, `extract_10`, `extract_12`, or `defer_extraction`.
  - [x] 5.2 For any recommended model, explain which Decision Pressure surface gap it would help close.
  - [x] 5.3 For any deferred model, explain whether it is low frequency, low Decision Pressure relevance, likely generic/theatrical, or better represented as an absence record.
  - [x] 5.4 If recommending extraction, define Batch 3a as a coverage patch, not corpus expansion.
  - [x] 5.5 If recommending extraction, state the changed extraction standard: extract Decision Pressure-ready operational constraints, not general model explanations.
  - [x] 5.6 If recommending no extraction yet, explain what evidence would make extraction worthwhile later.

- [x] 6.0 Update roadmap/schema doctrine only if the PR13 findings change the next-step recommendation
  - [x] 6.1 Decide whether PR13 confirms the existing roadmap/schema direction or changes it.
  - [x] 6.2 If confirmed, avoid unnecessary roadmap/schema churn.
  - [x] 6.3 If changed, update `plans/knowledge-substrate-roadmap-2026-05-04.md` with a brief current-state note and next-step recommendation.
  - [x] 6.4 If changed, update `plans/knowledge-use-schema-2026-05-04.md` with the same doctrine shift, especially around Decision Pressure evaluation or Batch 3a extraction.
  - [x] 6.5 Keep all roadmap/schema updates short and drift-control oriented. Do not restate the full PR13 artifacts.

  Note: PR13 changed the next-step recommendation narrowly. The existing no-broad-Batch-3 and no-runtime-promotion doctrine still stands, but the docs now allow a targeted `extract_5` Batch 3a coverage patch if extraction resumes.

- [x] 7.0 Verify docs-only constraints and prepare handoff summary
  - [x] 7.1 Run `git diff --check` on all touched files.
  - [x] 7.2 Run `git status --short` and confirm no runtime, prompt, validator, or affordance-record files were modified.
  - [x] 7.3 If a tiny deterministic helper was added, run its focused tests. If no helper was added, state that no tests were necessary because this was docs-only.
  - [x] 7.4 Review both new artifacts for banned drift: new lane framing, second public Pressure Check framing, case-type rules, broad Batch 3 framing, or fake objective certainty.
  - [x] 7.5 Prepare a concise handoff summary listing created/updated files, the dry-surface verdict, the Batch 3a recommendation, and any remaining open questions.

  Verification note: `git diff --check` is clean. Touched-file no-index whitespace checks are clean for the untracked PR13 docs. `git status --short` shows docs/task artifacts plus pre-existing untracked local files; no runtime, prompt, validator, or affordance-record files were modified. No tests were needed because no helper or runtime code was added.
