# Bevelin Safe Local Substrate Experiment

## Relevant Files

- `tasks/tasks-bevelin-safe-local-substrate-experiment.md` - This implementation task list; update checkboxes as work completes.
- `HOW_IT_WORKS.md` - Ground truth for how Lolla uses LLMs, embeddings, deterministic custody, V60, Step 6, run health, and archive comparison.
- `research/seeking-wisdom-existing-system-enrichment-plan-2026-05-11.md` - Step 1 framing: Bevelin should enrich the existing system, not become a new lane or lexical layer.
- `research/seeking-wisdom-step2-actionable-handover-2026-05-11.md` - Step 2 handover: candidate knowledge units, gates, costs, and quality-first call discipline.
- `/Users/marcin/Desktop/ksiazki pdf/outbox/processing/Peter Bevelin - Seeking Wisdom.md` - Read-only source text for Bevelin candidate source anchors.
- `/Users/marcin/Desktop/Apps/Lolla-system-b/munger_structural_mapping.md` - Read-only System B lineage for Munger tendency-to-model mappings.
- `/Users/marcin/Desktop/Apps/Lolla-system-b/The_Psychology_of_Human_Misjudgment.md` - Read-only System B lineage for Munger's original tendency descriptions and antidotes.
- `research/bevelin-safe-local-baseline-2026-05-12.md` - Baseline contract note with branch, commit SHA, artifact hashes, and no-default-runtime-change rule.
- `research/seeking-wisdom-source-packet-2026-05-12.md` - Source packet with Bevelin line anchors, candidate-unit map, owners, expected effects, and duplicate checks.
- `research/spikes/bevelin-safe-local-substrate-experiment/tiny_cases/*.txt` - New tiny ASCII/plain-text cases for one-pressure-at-a-time local probes.
- `research/spikes/bevelin-safe-local-substrate-experiment/tiny_case_manifest.json` - New manifest that maps each tiny case to the single Bevelin unit and expected product operator under test.
- `research/v60-embedding-balanced-4211-case-manifest-2026-05-10.json` - Existing 8-case replay manifest for broader local replay after tiny probes.
- `data/compiled/model_affordances/affordances_v60.json` - Current default V60 artifact; baseline/read-only for this experiment unless promotion is explicitly approved later.
- `data/curated/subpattern_catalog.json` - Current Lane 1 subpattern catalog; baseline/read-only for first-wave testing unless V60 evidence shows a subpattern change is necessary.
- `data/model_affordances/bevelin_candidate/*.json` - New candidate V60 source-backed records or record variants, kept outside default runtime paths.
- `data/compiled/model_affordances/bevelin_candidate/affordances_v60.json` - New compiled candidate V60 artifact, used only through explicit `--affordances-path`.
- `data/compiled/model_affordances/bevelin_candidate/quality_report_v60.md` - New compiler quality report for the candidate artifact.
- `scripts/compile_model_affordances.py` - Existing compiler for creating candidate artifacts and quality reports.
- `scripts/run_v60_transaction_replay_lab.py` - Existing dry replay harness for checking candidate packet selection without paid calls.
- `scripts/run_v60_chunk_exact_private_replay.py` - Existing focused private-trace replay harness for judging selected chunks before public writing.
- `scripts/run_v60_system_bound_enrichment_replay.py` - Existing focused composer replay harness for checking whether private pressure can become clean product prose.
- `scripts/run_v60_transaction_paid_replay.py` - Existing full A/B replay harness for baseline-vs-candidate comparison after cheaper gates pass.
- `scripts/compare_archived_runs.py` - Existing archived-run comparison tool for live repeated runs.
- `scripts/run_bevelin_tiny_probe.py` - Optional new local-only probe adapter if existing replay scripts cannot test tiny cases clearly.
- `tests/test_bevelin_tiny_probe.py` - Optional behavior tests for `scripts/run_bevelin_tiny_probe.py`, if that adapter is created.
- `tests/test_bevelin_candidate_records.py` - New behavior/schema tests proving candidate records are source-backed, scoped, compiled to a non-default artifact, and not promoted into default runtime.
- `tests/test_model_affordance_schema.py` - Existing schema validation tests for model affordance records.
- `tests/test_model_affordance_compiler.py` - Existing compiler tests for model affordance artifacts.
- `tests/test_v60_transaction_replay_lab.py` - Existing dry replay tests.
- `tests/test_v60_chunk_exact_private_replay.py` - Existing private-trace replay tests.
- `tests/test_v60_system_bound_enrichment_replay.py` - Existing system-bound composer replay tests.
- `tests/test_v60_transaction_paid_replay.py` - Existing full replay tests.
- `research/bevelin-safe-local-experiment-readout-2026-05-12.md` - Final readout with selected chunks, duplicate controls, dry-run evidence, and promote/revise/reject decision.

### Notes

- Safe-local-first: do not overwrite `data/compiled/model_affordances/affordances_v60.json`, do not edit default runtime paths, and do not add a new lane before evidence supports promotion.
- Use explicit paths for every candidate run, especially `--affordances-path data/compiled/model_affordances/bevelin_candidate/affordances_v60.json`.
- Quality-first call discipline: prefer small isolated calls or replay surfaces when the work is cognitively meaningful. Do not stuff detection, selection, usefulness judgment, rewriting, privacy hygiene, and ledger validity into one overloaded prompt.
- Use tiny ASCII/plain-text cases before broad end-to-end runs. Each tiny case should test one Bevelin pressure only.
- Use TDD/tracer bullets only where executable behavior is added or changed. Documentation, source packets, and readouts do not need tests unless a generated artifact or validator depends on them.
- When tests are required, use one behavior test at a time through public interfaces, then the smallest implementation needed to pass it.
- Keep evidence as first-class output: cost, token counts, selected chunks, rejected/deferred chunks, product deltas, leakage checks, and run-health status.

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps.

Example:
- `- [ ] 1.1 Read file` -> `- [x] 1.1 Read file` (after completing)

Update the file after completing each sub-task, not just after completing an entire parent task.

## Tasks

- [x] 0.0 Create feature branch
  - [x] 0.1 Create and checkout a new feature branch, for example `git switch -c feature/bevelin-safe-local-substrate-experiment`.
  - [x] 0.2 Confirm the intended base branch or commit for implementation work, preferably after the planning PR has landed or from the current approved planning branch if continuing locally.
  - [x] 0.3 Check `git status --short` and note unrelated untracked files so they are not accidentally staged.
  - [x] 0.4 Confirm the branch name, base SHA, and working-tree state in the task or baseline note.

- [x] 1.0 Lock the local experiment contract and baseline
  - [x] 1.1 Read `HOW_IT_WORKS.md` sections covering Lane 1, embeddings, V60 private enrichment, Step 6, run health, archives, and costs.
  - [x] 1.2 Read the Step 1 and Step 2 Bevelin planning docs to preserve the "enrich existing system, do not multiply architecture" constraint.
  - [x] 1.3 Read the relevant System B and Bevelin source files enough to understand the source lineage and first-wave candidate units.
  - [x] 1.4 Create `research/bevelin-safe-local-baseline-2026-05-12.md` with branch, commit SHA, default artifact paths, and artifact hashes or checksums.
  - [x] 1.5 Record the baseline status of `affordances_v60.json`, `subpattern_catalog.json`, `data/embeddings.db`, and the 8-case replay manifest.
  - [x] 1.6 Write the non-negotiable local safety contract: no default artifact overwrite, no live `/lolla` runtime wiring, no new lane, no broad prompt stuffing, no product Bevelin label.
  - [x] 1.7 Define the first-wave candidate scope as four units: absolute yardstick, role-reversal system fairness, postmortem/learning trace, and disconfirmation/prosecutor test as a control.
  - [x] 1.8 Define stop/go gates before implementation starts, including "duplicate current V60", "selected but irrelevant", "product bloat", "machinery leak", and "no adjacent-case confirmation".

- [x] 2.0 Build the Bevelin source packet and candidate-unit map
  - [x] 2.1 Create `research/seeking-wisdom-source-packet-2026-05-12.md`.
  - [x] 2.2 For each first-wave unit, capture exact Bevelin line anchors, short paraphrases, and only tiny quotes where useful.
  - [x] 2.3 Add the matching System B/Munger lineage anchors when they explain why the unit belongs in Lane 1 or V60.
  - [x] 2.4 For each unit, name the current owner models, tendencies, and subpatterns, or explicitly mark "no clean owner".
  - [x] 2.5 For each unit, classify the intended injection type: duplicate, sharpen existing, new affordance/absence candidate, subpattern candidate, or reject/defer.
  - [x] 2.6 Inspect current V60 records for the likely owner models and record whether each Bevelin pressure is already represented.
  - [x] 2.7 Inspect current Lane 1 subpatterns for the likely tendency homes and record whether each pressure needs a subpattern change or can stay in V60 first.
  - [x] 2.8 Add a misuse guard for each unit, especially generic skepticism, moralizing fairness, diary-like postmortems, and psychologizing state-of-mind claims.
  - [x] 2.9 Decide the smallest first candidate set to author. Prefer V60 record sharpening before adding new ontology.
  - [x] 2.10 Update the source packet with a clear "candidate, defer, reject" decision table.

- [x] 3.0 Design the minimal quality-first test surfaces and tiny ASCII cases
  - [x] 3.1 Create `research/spikes/bevelin-safe-local-substrate-experiment/tiny_cases/`.
  - [x] 3.2 Write one tiny ASCII/plain-text case for absolute yardstick pressure.
  - [x] 3.3 Write one tiny ASCII/plain-text case for role-reversal system fairness pressure.
  - [x] 3.4 Write one tiny ASCII/plain-text case for postmortem/learning trace pressure.
  - [x] 3.5 Write one tiny ASCII/plain-text case for disconfirmation/prosecutor-test control pressure.
  - [x] 3.6 Create `research/spikes/bevelin-safe-local-substrate-experiment/tiny_case_manifest.json` mapping each case to exactly one candidate unit, expected product operator, and reject condition.
  - [x] 3.7 Decide whether existing replay scripts can inspect these tiny cases clearly enough without new code.
  - [x] 3.8 Not needed: existing replay scripts can load the tiny manifest and emit focused packets.
  - [x] 3.9 Not needed: no `scripts/run_bevelin_tiny_probe.py` adapter was created.
  - [x] 3.10 Not needed: candidate explicit-path and default-artifact safety are covered by compiler and candidate-record tests.
  - [x] 3.11 Not needed: no tiny probe adapter exists.

- [x] 4.0 Add candidate substrate artifacts behind explicit local paths
  - [x] 4.1 Decide the exact candidate record IDs and owner model IDs from the source packet.
  - [x] 4.2 RED: add a behavior/schema test in `tests/test_bevelin_candidate_records.py` proving the candidate record directory contains only the approved first-wave candidate records.
  - [x] 4.3 GREEN: create the minimum candidate JSON records under `data/model_affordances/bevelin_candidate/` needed to pass the approved-scope test.
  - [x] 4.4 RED: add a test proving every candidate record validates against the existing affordance schema and uses source-backed evidence.
  - [x] 4.5 GREEN: fill only the required source-backed fields, source evidence, diagnostic questions, treatment requirements, and absence records needed to pass validation.
  - [x] 4.6 RED: add a test proving candidate records compile into `data/compiled/model_affordances/bevelin_candidate/affordances_v60.json` and do not overwrite or modify `affordances_v60.json`.
  - [x] 4.7 GREEN: compile the candidate artifact and quality report using explicit output filenames.
  - [x] 4.8 RED/GREEN: add or update a test proving the live default runtime still points at the existing `affordances_v60.json` unless an explicit candidate path is supplied.
  - [x] 4.9 Run candidate record tests plus existing schema/compiler tests.
  - [x] 4.10 If V60 cannot safely express one first-wave unit, document the reason and defer any subpattern-catalog edit to a later evidence-backed slice.

- [x] 5.0 Run gated local evaluation and collect evidence
  - [x] 5.1 Run dry replay with `scripts/run_v60_transaction_replay_lab.py` and the explicit candidate `--affordances-path`.
  - [x] 5.2 Compare dry replay packets against baseline: selected cards, selected chunks, skipped candidates, not-presented candidates, and displaced baseline chunks.
  - [x] 5.3 Stop and revise candidate records if candidate chunks never enter packets, enter for the wrong reason, or displace stronger baseline chunks without a clear justification.
  - [x] 5.4 Stopped by dry-replay gate: no private-trace replay was run because candidate chunks did not naturally enter the 8-case packets.
  - [x] 5.5 Stopped by dry-replay gate: no private-trace dispositions exist.
  - [x] 5.6 Gate failed for continuation: tiny forced probes worked, but the candidate chunks entered zero of eight normal broad-case packets.
  - [x] 5.7 Stopped by dry-replay gate: no system-bound composer replay was run.
  - [x] 5.8 Stopped by dry-replay gate: no product-prose leakage check was needed beyond explicit no-promotion decision.
  - [x] 5.9 Stopped by dry-replay gate: no full A/B paid replay was run.
  - [x] 5.10 Capture dry-run evidence; paid-call costs, LLM token counts, and product deltas are not applicable because the dry-replay gate stopped the experiment.
  - [x] 5.11 Stopped by dry-replay gate: no live repeated local skill run was run.
  - [x] 5.12 Stopped by dry-replay gate: no live archives were produced to compare.
  - [x] 5.13 Create or update `research/bevelin-safe-local-experiment-readout-2026-05-12.md` with the full evidence table.

- [x] 6.0 Decide promote, revise, or reject based on observed edge
  - [x] 6.1 Review the readout against the predeclared gates instead of judging from one interesting case.
  - [x] 6.2 Mark each first-wave unit as promote, revise, reject, or keep as source-only research.
  - [x] 6.3 Promote only narrow records that produced better evidence gates, thresholds, role-reversal checks, or learning traces without product bloat or leakage.
  - [x] 6.4 If evidence is mixed, write the smallest next revision hypothesis instead of widening scope.
  - [x] 6.5 If evidence is weak, leave the candidate artifact non-default and document why it should not burden runtime.
  - [x] 6.6 Run the relevant test suite for changed executable code and artifact validators.
  - [x] 6.7 Run `git diff --check`.
  - [x] 6.8 Confirm `git status --short` and distinguish intended experiment files from unrelated pre-existing untracked files.
  - [x] 6.9 Prepare the PR summary with scope, changed files, tests, costs, evidence, and promote/revise/reject decisions.
  - [x] 6.10 If no edge is found, close with a rollback/no-promotion note rather than forcing the substrate change.
