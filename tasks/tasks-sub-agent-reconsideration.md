# Sub-Agent Reconsideration Layer

After Step 6, spawn 4 sub-agents (one per audit lane) in parallel via the Claude Code Agent tool. Each receives ONLY the extracted decision structure + its one audit card — zero conversation history. Claude then compares their outputs to its Step 6 and surfaces only meaningful divergences. This breaks the "fox auditing the henhouse" problem where Claude both argued the position and judges whether it should shift.

## Relevant Files

- `SKILL.md` - Main orchestration file. All step definitions live here. Steps 7, 8 will be added; Step 6 timing updated; Completion Status updated.
- `scripts/run_extract.py` - Extraction script. Read-only reference for understanding the extraction JSON schema (decision_situation, live_constraints, synthesized_position, reasoning_passages, original_framing, dropped_threads).
- `observatory/serve_result.py` - Observatory server. Needs a new `/api/case/{id}` field for gap_check data and hot-reload support for the new fields.
- `observatory/build/assets/index-B8542oia.js` - Observatory frontend (pre-built Svelte). Needs a new section to render the gap check output.
- `references/output-field-guide.md` - Field definitions for pipeline output. Needs new section documenting gap_check fields in result.json.
- `references/presentation-voice.md` - Voice guidance for Step 6. Needs update acknowledging the sub-agent pressure check that follows.
- `HOW_IT_WORKS.md` - Technical architecture reference. Needs new section on the sub-agent reconsideration layer and updated trust-boundary diagram.

### Notes

- Sub-agents use the Claude Code Agent tool, NOT OpenRouter. OpenRouter is for calibrated extraction prompts against Grok. Sub-agents need cold-context judgment — that is what the Agent tool already provides.
- Opus is within the subscription — no incremental cost per sub-agent call.
- The engine (`engine/system_b/`) does NOT change. This is purely orchestration + rendering.
- Each sub-agent receives extraction fields (~800-1200 tokens) + one card's JSON (~650-3100 tokens). Total context per sub-agent: ~1,200 to ~4,200 tokens.
- The Observatory frontend is a pre-built Svelte app. Source is not in-repo — the build output at `observatory/build/` must be regenerated from the Observatory source repo after frontend changes.
- PRODUCT_VISION.md and SYSTEM_UNDERSTANDING.md live in the System B repo (`/Users/marcin/Desktop/Apps/Lolla-system-b/`), not the skill repo. Both need updating alongside the skill-repo docs.

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off by changing `- [ ]` to `- [x]`. This lets you track progress and resume work if interrupted. Tasks should be completed in order — parent tasks are checked off when all their sub-tasks are complete.

## Tasks

- [x] 0.0 Create feature branch
  - [x] 0.1 Create branch `feat/sub-agent-reconsideration` from `main`
  - [x] 0.2 Verify clean working tree before branching (`git status` shows clean)

- [x] 1.0 Document current Step 6 flow and identify insertion points
  - [x] 1.1 Read `SKILL.md` Step 6 and Step 6b sections; note exact line boundaries where Step 7 and Step 8 will be inserted (after Step 6b, before Completion Status)
  - [x] 1.2 Read `observatory/serve_result.py` `_build_case_response()` function; note how `revised_answer` is wired into the API response — the gap_check field will follow the same pattern
  - [x] 1.3 Read the extraction prompt in `scripts/run_extract.py` (lines ~120-200) to confirm the exact field names and structure sub-agents will receive: `decision_situation` (string), `live_constraints` (array of {constraint, status, evidence}), `synthesized_position` (string), `reasoning_passages` (array of verbatim strings), `original_framing` (string), `dropped_threads` (array of {thread, evidence})
  - [x] 1.4 Identify how each card's JSON is keyed in result.json: `delta_card`, `companion_cheat_sheet`, `frame_pressure_card`, `structural_coverage_card` — these are the exact keys to extract per sub-agent

- [x] 2.0 Design sub-agent prompt templates (one per lane)
  - [x] 2.1 Design the shared preamble that all 4 sub-agent prompts use. It must contain: (a) the role instruction ("You are reviewing a decision structure cold — you have no conversation history"), (b) the extraction fields pasted as structured context, (c) the instruction to identify what specifically should shift in the synthesized position given the card's findings. The preamble must explicitly state what the sub-agent does NOT have access to (raw conversation, other lanes, session history, Step 6 output).
  - [x] 2.2 Design the Lane 1 (DeltaCard) sub-agent prompt suffix. It receives `delta_card` JSON. Prompt asks: "For each tendency detection, does the specific_passage + challenge_statement warrant a concrete shift in the synthesized position? Name what should change and why. If a detection is noise given the decision_situation, say so." Output format: array of {finding_index, shift_recommended (boolean), what_should_shift (string), reasoning (string)}.
  - [x] 2.3 Design the Lane 2 (CompanionCheatSheet) sub-agent prompt suffix. It receives `companion_cheat_sheet` JSON. Prompt asks: "For each anchor's failure modes and premortem questions, does the synthesized position adequately account for them? Name any failure mode or premortem that the position ignores or underweights." Output format: array of {anchor_display_name, underweighted_items (array of {chunk_type, chunk_text, what_position_misses}), overall_assessment (string)}.
  - [x] 2.4 Design the Lane 3 (FramePressureCard) sub-agent prompt suffix. It receives `frame_pressure_card` JSON. Prompt asks: "For each frame element and reframing, does the synthesized position acknowledge the embedded assumption? Would the position change materially if the assumption were relaxed?" Output format: array of {element_index_or_reframing_index, type ("element" | "reframing"), material_shift (boolean), what_changes (string)}.
  - [x] 2.5 Design the Lane 4 (StructuralCoverageCard) sub-agent prompt suffix. It receives `structural_coverage_card` JSON. Prompt asks: "For each gap dimension, is this a genuine blind spot in the synthesized position, or is the gap acknowledged implicitly? For covered dimensions, is the coverage as strong as claimed?" Output format: array of {dimension_name, is_genuine_gap (boolean), severity ("high" | "medium" | "low"), what_position_should_add (string)}.
  - [x] 2.6 Define the empty-card skip conditions for each lane: Lane 1 skip if `delta_card.top_findings` is empty/null; Lane 2 skip if `companion_cheat_sheet.anchors` is empty/null; Lane 3 skip if `frame_pressure_card.frame_elements` is empty/null AND `frame_pressure_card.reframings` is empty/null; Lane 4 skip if `structural_coverage_card.dimensions` is empty/null or all dimensions have `covered: true`.
  - [x] 2.7 Write all 4 prompt templates as a reference section in SKILL.md (under a new "## Sub-Agent Prompt Templates" heading after the References section), so they are version-controlled and auditable. Each template should be a complete, copy-pasteable prompt with `{EXTRACTION_FIELDS}` and `{CARD_JSON}` placeholders.

- [x] 3.0 Add Step 7 to SKILL.md — spawn sub-agents
  - [x] 3.1 Add `### Step 7: Spawn Pressure-Check Sub-Agents` after Step 6b in SKILL.md. The step instructions must tell Claude to: (a) read `/tmp/lolla_{run_id}_extraction.json` to get the extraction fields, (b) read `/tmp/lolla_{run_id}_result.json` to get the 4 card JSONs, (c) check empty-card conditions per lane (from task 2.6), (d) spawn up to 4 Agent tool calls in parallel — one per non-empty lane.
  - [x] 3.2 Specify that each Agent call receives: the shared preamble (with extraction fields interpolated) + the lane-specific suffix (with card JSON interpolated). The Agent tool prompt must be fully self-contained — no file reads, no bash calls, no tool access. The sub-agent reasons over the text it receives and returns structured output.
  - [x] 3.3 Add timing guidance: Step 7 should be launched at the START of Step 6 (before Claude writes its reconsideration), so sub-agents run in parallel with Claude's Step 6 reasoning. Update the Step 6 header to note: "While you write your reconsideration below, the sub-agents from Step 7 are running in parallel." Update Step 7 to note: "These agents were launched before Step 6 began. By now their results should be available."
  - [x] 3.4 Add error handling: if an Agent call fails or times out, log the lane as `skipped_error` in the gap check output and continue with remaining lanes. Do not block Step 8 on any single lane's failure.
  - [ ] 3.5 Specify that sub-agent outputs are written to `/tmp/lolla_{run_id}_subagent_lane{N}.json` (N = 1-4) for debugging. Each file contains the raw sub-agent response.

- [x] 4.0 Add Step 8 to SKILL.md — comparison and divergence reporting
  - [x] 4.1 Add `### Step 8: Pressure-Check Comparison` after Step 7 in SKILL.md. Claude reads its Step 6 output and each sub-agent's output, then asks three specific questions per lane: (1) Did the sub-agent identify a shift I dismissed or minimized in Step 6? (2) Did the sub-agent treat a finding as material that I treated as noise? (3) Did the sub-agent connect a finding to the position in a way I didn't?
  - [x] 4.2 Define the output format for divergences. Only "yes" answers to the three questions get reported. Format per divergence: `**[Lane N — lane_name]** The isolated review [description of what the sub-agent found that Claude's Step 6 missed/minimized].` No lane-by-lane summaries — just the divergences as a flat list.
  - [x] 4.3 Define the no-divergence output: if all sub-agents aligned with Step 6 (all three questions answered "no" for every lane), output a single line: "Pressure check: isolated review aligned with assessment above."
  - [x] 4.4 Add the presentation rule: Step 8 output appears AFTER Step 6's updated position, under a `### Pressure Check` heading. It is visually separated from Step 6 — the user should see the updated position first, then the divergence report.
  - [x] 4.5 Update the pipeline description at the top of SKILL.md: change "Six steps" to "Eight steps" and add brief descriptions of Steps 7 and 8 to the pipeline overview. Also fix stale references: Step 3 says "all three lanes" and "three cards", Step 4 says "three sections", Step 6 says "three cards" — all should be "four".

- [x] 5.0 Extend result.json schema for gap check persistence
  - [x] 5.1 Add Step 8b after Step 8 in SKILL.md: persist the gap check output to result.json. New fields in result.json: `gap_check` (object with `lanes` array, each element: {lane_number, lane_name, status ("completed" | "skipped_empty" | "skipped_error"), divergences (array of {question_number (1-3), description (string)})}), `gap_check_summary` (string — the rendered text from Step 8), `gap_check_written_at` (ISO timestamp).
  - [x] 5.2 Write the persistence code block for SKILL.md (same pattern as Step 6b). Claude writes the gap check text to `/tmp/lolla_{run_id}_gapcheck.txt`, then a python3 one-liner reads it and merges it into result.json alongside the structured `gap_check` object.
  - [x] 5.3 Add `has_gap_check` boolean to result.json (analogous to `revised_answer_present`) so the Observatory can detect whether the pressure check ran.

- [x] 6.0 Update Observatory to render gap check
  - [x] 6.1 In `observatory/serve_result.py`, update `_build_case_response()` to include `gap_check`, `gap_check_summary`, and `has_gap_check` fields from the result JSON — same pattern as `revised_answer` / `revised_answer_present`.
  - [ ] 6.2 Document the expected Observatory frontend changes (these will be implemented in the Observatory source repo, not here): a new "Pressure Check" section below the "Updated Position" section, rendering `gap_check_summary` as markdown. If `has_gap_check` is false, the section should not appear. If all lanes aligned, show the single-line "aligned" message. If divergences exist, render them as a list with lane labels.
  - [ ] 6.3 Verify the Observatory hot-reload mechanism (`_reload_result_if_changed()`) will pick up the new fields automatically — it re-reads the entire JSON on mtime change, so no code change needed for hot-reload itself.

- [x] 7.0 Update Completion Status section in SKILL.md
  - [x] 7.1 Update the Completion Status template to include pressure check results: add `Pressure check: [N] divergences across [M] lanes` or `Pressure check: aligned` line after the existing status fields.
  - [x] 7.2 If any sub-agent lane was skipped (empty card or error), note it: `Pressure check: [N] divergences ([skipped lanes: Lane 2 empty, Lane 4 error])`

- [ ] 8.0 Update documentation
  - [ ] 8.1 Update `HOW_IT_WORKS.md` "Architecture" section — add a new subsection "### Sub-Agent Reconsideration Layer" after the "Conductor, Not Player" subsection. Explain: (a) the fox-henhouse problem with Step 6, (b) how sub-agents break it by reading the position cold, (c) that sub-agents use Claude via Agent tool (not OpenRouter) because this is judgment in a clean context rather than calibrated extraction, (d) the three comparison questions, (e) that only divergences are surfaced.
  - [ ] 8.2 Update `HOW_IT_WORKS.md` "Conductor, Not Player" subsection — the current text says "Claude does author the final revised position (Step 6)." Add a sentence noting that Step 6 is now followed by an independent pressure check (Steps 7-8) where isolated sub-agents with no conversation history review the same evidence and Claude surfaces only the divergences.
  - [ ] 8.3 Update `references/output-field-guide.md` — add a new `## Gap Check Fields` section documenting the `gap_check` object schema (lanes array with lane_number, lane_name, status, divergences), `gap_check_summary`, and `has_gap_check`.
  - [ ] 8.4 Update `references/presentation-voice.md` — add a paragraph in the "What You Are Doing and Why It Matters" section noting that the pressure check sub-agents exist specifically because the system's own thesis (inconsistency-avoidance, fox-henhouse) applies to Step 6 itself. Claude should be especially attentive to divergences where a sub-agent flagged something Claude dismissed — that is the exact pattern the system warns about.
  - [ ] 8.5 Update System B docs (`/Users/marcin/Desktop/Apps/Lolla-system-b/PRODUCT_VISION.md`) — add sub-agent reconsideration to the North Star flow (new step between reconsideration and final output), add to "What We Have Built" list, update Observatory section.
  - [ ] 8.6 Update System B docs (`/Users/marcin/Desktop/Apps/Lolla-system-b/SYSTEM_UNDERSTANDING.md`) — add a new section documenting the sub-agent layer's information flow, what each agent receives, and the trust-boundary expansion.

- [ ] 9.0 Testing and calibration
  - [ ] 9.1 Run a full audit on a real strategic conversation using the test conversation at `tests/conversation_for_testing.md`. Verify all 8 steps complete, sub-agents are spawned for non-empty lanes, and the gap check output appears after Step 6.
  - [ ] 9.2 Verify the empty-card skip logic: if a lane produces zero findings (e.g., no tendency detections), confirm that lane's sub-agent is not spawned and the gap check output shows `skipped_empty` for that lane.
  - [ ] 9.3 Verify result.json persistence: after a full run, read `/tmp/lolla_{run_id}_result.json` and confirm it contains `gap_check`, `gap_check_summary`, `has_gap_check`, and `gap_check_written_at` fields with correct values.
  - [ ] 9.4 Verify Observatory rendering: launch the Observatory with a result.json that contains gap check data and confirm the Pressure Check section appears below the Updated Position.
  - [ ] 9.5 Evaluate divergence quality across 3+ real conversations: do the sub-agents actually find meaningful divergences from Step 6, or do they mostly align? If they always align, the prompts may be too deferential. If they always diverge, the prompts may be too adversarial. Tune the sub-agent prompt templates based on findings.
  - [ ] 9.6 Measure latency impact: time a full run with and without Steps 7-8. Since sub-agents run in parallel with Step 6, the latency impact should be minimal (sub-agents process ~1200-4200 tokens each). If any sub-agent consistently takes longer than Step 6, investigate whether the prompt is too complex.
