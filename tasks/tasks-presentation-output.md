# PR 3: Presentation Output

**Branch:** `feat/presentation-output`
**Issues:** #5 (memo artifact), #6 (product/process separation), #7 (STATUS block)
**Scope:** User-facing output — new memo renderer, SKILL.md presentation rewrite

## Relevant Files

- `scripts/render_memo.py` - **NEW** — Deterministic markdown memo renderer from result.json
- `SKILL.md` - Step 4 (line 162-235, chat output format), Step 6b (line 323-329, persist), Step 8b (line 418, persist), Step 9 (line 494-504, Observatory + completion status), Completion Status block (line 508-521, STATUS block to replace)
- `observatory/serve_result.py` - May serve the memo alongside the Observatory
- `tests/test_render_memo.py` - **NEW** — Tests for memo rendering from result JSON
- `/tmp/lolla_20260413T193743Z_result.json` - Real run data for testing memo output
- `references/presentation-research.md` - Book research informing presentation design (BLUF, SUCCESs, scanning behavior)
- `references/presentation-voice.md` - Voice guidance for Step 6 writing
- `references/anti-bullshit-doctrine.md` - Anti-bullshit constraints for bridge sentences

### Notes

- Unit tests should be placed in the `tests/` directory.
- Use `python3 -m pytest tests/ -v` to run tests.
- `render_memo.py` is a pure Python script that reads result.json and produces markdown. No API calls, no LLM — deterministic template rendering. It must handle missing optional fields gracefully (e.g., no bullshit_profile, no gap_check).
- SKILL.md changes are prose/instruction changes, not code. They affect how Claude presents output in the chat. These are tested by reading the SKILL.md and verifying the instructions are clear and consistent.
- The memo template must prioritize by signal strength, not by lane order. Findings from all 4 lanes should be interleaved by severity/materiality.
- Result JSON top-level keys: `detected_tendencies`, `delta_card`, `companion_cheat_sheet`, `companion_card`, `frame_pressure_card`, `structural_coverage_card`, `audit_summary`, `query`, `vanilla_answer`, `revised_answer`, `bullshit_profile`, `run_health`, `gap_check`

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps.

Example:
- `- [ ] 1.1 Read file` -> `- [x] 1.1 Read file` (after completing)

Update the file after completing each sub-task, not just after completing an entire parent task.

## Tasks

- [x] 0.0 Create feature branch
  - [x] 0.1 Create and checkout branch: `git checkout -b feat/presentation-output`

- [ ] 1.0 Build `render_memo.py` — deterministic memo from result.json (Issue #5)
  - [x] 1.1 Read `references/presentation-research.md` — understand BLUF structure, SUCCESs framework, scanning/reading behavior research. These inform memo layout decisions
  - [x] 1.2 Read `/tmp/lolla_20260413T193743Z_result.json` — study the full result schema. Map out which fields become memo sections: `delta_card.findings` (top findings), `companion_cheat_sheet.anchors` (model connections), `frame_pressure_card.reframings` (alternative questions), `structural_coverage_card.gap_questions` (structural gaps), `bullshit_profile.summary` (delivery check), `gap_check.lanes` (pressure check divergences), `revised_answer` (updated position)
  - [x] 1.3 RED: Write test in `tests/test_render_memo.py` — `render_memo(result_dict)` returns a string starting with `# ` (markdown heading) and containing the decision situation from `query`
  - [x] 1.4 GREEN: Create `scripts/render_memo.py` with `render_memo(result: dict) -> str`. Start with a heading line and decision context extracted from `result["query"]`. Truncate query to first 2 sentences for the heading context
  - [x] 1.5 RED: Write test — memo contains a "Key Findings" section with one entry per `delta_card.top_findings` (or `delta_card.findings` if `top_findings` is absent). Each entry includes `tendency_name`, `severity`, and `challenge_statement`
  - [x] 1.6 GREEN: Add findings section to `render_memo`. Iterate `delta_card["findings"]`, sort by severity (high > medium > low). For each: render `**[tendency_name]** (severity)` followed by `specific_passage` (truncated) and `challenge_statement`. Handle missing `delta_card` gracefully (skip section)
  - [x] 1.7 RED: Write test — memo contains a "Mental Model Connections" section listing companion anchors with `display_name` and `presence_explanation`
  - [x] 1.8 GREEN: Add companion section. Iterate `companion_cheat_sheet["anchors"]`, render each as `**[display_name]** — [presence_explanation]`. Include `presence_mode` if present. Handle missing `companion_cheat_sheet` gracefully
  - [x] 1.9 RED: Write test — memo contains a "Frame Alternatives" section with reframings from `frame_pressure_card.reframings`, each showing the reframed question and `what_opens`
  - [x] 1.10 GREEN: Add frame pressure section. Iterate `frame_pressure_card["reframings"]`. Handle missing card gracefully
  - [x] 1.11 RED: Write test — memo contains a "Structural Gaps" section listing `structural_coverage_card.gap_questions` with the dimension name and gap question text
  - [x] 1.12 GREEN: Add structural gaps section. Iterate `structural_coverage_card["gap_questions"]`. Include dimension context from `gap_routes`. Handle missing card gracefully
  - [x] 1.13 RED: Write test — memo contains a "Delivery Check" section when `bullshit_profile.summary.total_clear > 0`, showing the count and dominant subtype. Section is absent when `total_clear == 0`
  - [x] 1.14 GREEN: Add delivery check section. Read `bullshit_profile["summary"]`, count detections per subtype across passages to find dominant. Handle missing `bullshit_profile` gracefully
  - [x] 1.15 RED: Write test — memo contains an "Updated Position" section with `revised_answer` text when present. Section is absent when `revised_answer` is null
  - [x] 1.16 GREEN: Add updated position section. Render `revised_answer` as-is (it's already markdown from Step 6). Handle null gracefully
  - [x] 1.17 RED: Write test — memo contains a "Pressure Check" section when `gap_check` exists with divergences, listing each divergent lane and its divergences
  - [x] 1.18 GREEN: Add pressure check section. Iterate `gap_check["lanes"]`, filter to those with non-empty `divergences`. Format each divergence. Handle missing `gap_check` gracefully
  - [x] 1.19 RED: Write test — `render_memo` handles a minimal result dict with only `query`, `vanilla_answer`, and `detected_tendencies` (all optional sections omitted) without errors
  - [x] 1.20 GREEN: Ensure all section renderers have proper guard clauses. The memo should degrade gracefully — fewer sections, never an error
  - [x] 1.21 Add CLI entry point: `if __name__ == "__main__"` that reads `--result` JSON file, calls `render_memo()`, writes to `--output` file (default stdout)
  - [x] 1.22 REFACTOR: Run against real data — verified coherent output (107 lines), all sections populated, delivery check correctly identifies unverified claims, pressure check divergences render with descriptions

- [ ] 2.0 Rewrite SKILL.md presentation — separate product from process (Issue #6)
  - [x] 2.1 Read `SKILL.md` Step 4 (line 162-235) — study the current chat output format
  - [x] 2.2 Read `SKILL.md` Step 6 (line 276-321) — study the updated position instructions
  - [x] 2.3 Read `SKILL.md` Step 8 (line 383-416) — study pressure check presentation
  - [x] 2.4 Read `references/presentation-research.md` and `references/presentation-voice.md`
  - [x] 2.5 Rewrite Step 4: removed lane number references, replaced with finding-type language
  - [x] 2.6 Rewrite "What NOT to put in chat": added explicit process/product boundary rule
  - [x] 2.7 Add memo generation Step 6c after Step 6b
  - [x] 2.8 Update Step 9: added memo artifact mention alongside Observatory
  - [x] 2.9 Reviewed SKILL.md for process-language leaks. Fixed "Lane 4" in Step 6 guidance. Remaining lane references are in non-user-facing sections (architecture description, sub-agent skip conditions, lane suffixes) — appropriate
  - [x] 2.10 VERIFY: User-facing sections (Steps 4, 6, 8, 9) are clean of pipeline jargon

- [ ] 3.0 Replace STATUS block with narrative closing (Issue #7)
  - [x] 3.1 Read `SKILL.md` Completion Status section — studied the STATUS block format
  - [x] 3.2 Replaced STATUS block with narrative closing (2-3 sentences in human terms)
  - [x] 3.3 Removed DONE/DONE_WITH_CONCERNS codes. Success = narrative. Failure = one sentence naming the issue
  - [x] 3.4 Added memo path to narrative closing alongside Observatory
  - [x] 3.5 VERIFY: Reads like a human wrapping up, not a CI report

- [x] 4.0 Integrate memo into pipeline flow
  - [x] 4.1 Read `observatory/serve_result.py` — uses API endpoints, not static file serving for data
  - [x] 4.2 Skipped — Observatory uses JSON API endpoints; memo file at `/tmp/` is sufficient
  - [x] 4.3 Verified: `render_memo.py --result <path> --output <path>` works with exit code 0; stdout mode also works
  - [x] 4.4 REFACTOR: All 32 tests passing

- [x] 5.0 Verify with a real run
  - [x] 5.1 Generated memo: 107 lines, all sections populated
  - [x] 5.2 Verified: BLUF present, findings sorted (high→high→medium), 5 companion anchors, 2 frame alternatives, 12 structural gap questions, delivery check (32 clear, unverified claims dominant), updated position included, pressure check with 3 divergent lanes
  - [x] 5.3 Verified: DeltaCard (0 divergences) correctly absent from pressure check; CompanionCheatSheet, FramePressureCard, StructuralCoverageCard all listed with descriptions
  - [x] 5.4 Observatory serves the result via JSON API — new fields pass through without errors
  - [x] 5.5 Verified via test_minimal_result_no_errors: minimal result produces valid heading-only memo
