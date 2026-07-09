# Lolla System Architecture Audit

Date: 2026-07-06 (seed) / 2026-07-09 (refresh)  
Repository: `lolla-skill-public-runtime`  
Audit mode: read-only architecture and maintainability inspection, with one documentation artifact added.

## 2026-07-09 Refresh Addendum

- Scope correction: observatory is now treated as the portable, first-surface product presentation path after skill flow, with model/relations/map/receipts as a coherent learning path and raw transcript retained as explicit private export.
- New product decision baseline: `docs/product/observatory-library-graph-scope-decision-v0.md` plus JSON and codex review record were added and should be considered authoritative for graph-scope decisions.
- Clarified ambiguity from previous snapshot:
  - The map/scope is intentionally local, visible, and progressive (`Outcome -> Learn -> Models -> Relations -> Map -> Receipts`).
  - `Download MD` is the private agent-memory export; it is not the default read layer.
  - Full-corpus graph and filtered library graph are explicitly future surfaces, not default behavior.
- Branch-level discrepancy resolved: this audit was previously captured as of an earlier branch, but current branch head is `feature/observatory-library-graph-scope-decision-v0` (ahead of origin/main), containing graph-scope accounting PRs #344-#346 and PR-P11 scope decision work.
- Tooling discrepancy resolved for this environment: Understand-Anything could not be installed/run due network/DNS limits here, so local deterministic scans and review files remain the decision baseline.
- No runtime wiring changes were introduced by this refresh; all updates are audit-map and product-scope alignment.

## 1. Executive Summary

- Overall health: the project is a functional OSS-stage skill/runtime with unusually strong custody, run-state, artifact, and provider-boundary discipline for a local tool. It is not a tidy small library; it is an accreted runtime plus review/product lab, and that shape is visible in the file graph.
- Top strength 1: the active runtime has a real contract around `ConversationContext`, provenance-bearing IR, run IDs, archive artifacts, and explicit provider usage accounting. This is a stronger center of gravity than the repo size first suggests.
- Top strength 2: provider/model/API boundaries are mostly explicit. OpenRouter calls flow through `engine/system_b/boundary_provider.py`, extraction and pipeline calls write usage traces, and archive artifacts preserve enough metadata to audit run quality.
- Top strength 3: many offline/product/review features carry explicit non-runtime and non-claim language, especially Product Delta, Teacher Observatory packet adaptation, doctor/preflight, and evaluation artifacts.
- Top strength 4: the product surface now has a clear default sequence in Observatory (`Outcome -> Learn -> Models -> Relations -> Map -> Receipts`) and explicit private-export conventions for raw transcript (`Download MD`), which reduces product ambiguity for maintainers.
- Top risk 1: the active runtime is spread across shell scripts, `/tmp/lolla_*` artifacts, environment files, a large CLI orchestrator, the core pipeline, archive finalization, and Observatory launch. The flow works, but development requires knowing several implicit path and artifact conventions at once.
- Top risk 2: `scripts/run_pipeline.py`, `engine/system_b/pipeline.py`, `scripts/archive_run.py`, and `observatory/serve_result.py` are real bottleneck files. Their size is not automatically bad, but each currently mixes enough responsibilities that future changes are easy to mis-scope.
- Top risk 3: docs, plans, review artifacts, product prototypes, generated research, and runtime code all live together. Without a maintained connectedness map, a new contributor can mistake offline plans or review artifacts for runtime behavior.
- Top risk 4: Observatory is intentionally one of the main delivery surfaces, but its role as product vs inspection surface is easy to confuse when reading older docs. The route behavior, non-claims, and private export rules need to stay synced as the quickest onboarding truth.
- The live user-facing path is: `SKILL.md` and `docs/skill/STEPS.md` orchestrate setup, capture, extraction, pipeline, private sidecars, memo/pressure state, archive, and Observatory. The most important executable path is `scripts/skill/setup.sh` -> `scripts/skill/run_extract_step.sh` -> `scripts/run_extract.py` -> `scripts/skill/run_pipeline_step.sh` -> `scripts/run_pipeline.py` -> `engine/system_b/pipeline.py` -> archive and Observatory helpers.
- The deterministic machinery is significant and worth preserving: conversation loading, canonical keys, IR construction, catalog/graph loading, V60 enrichment, pre-Step-6 private table generation, run health, archive evaluation, agent result, reasoning trace, and doctor/preflight are all concrete modules rather than vague docs.
- There are compatibility layers and stale labels, but not a large amount of confirmed dead code in the active path. Examples include the deprecated `--extraction-json`/`--new-contract` CLI surface, legacy `critique_request`, re-export compatibility from `pipeline.py`, and archived historical V60 data lineage.
- Confirmed drift: `HOW_IT_WORKS.md` currently describes pressure-check ordering differently from `SKILL.md` and `docs/skill/STEPS.md`; `scripts/run_extract.py` also references a non-existent `scripts/run_live_pipeline.py` in a comment.
- The default runtime still makes many provider calls. `README.md` documents a typical default audit at about 50-85 OpenRouter calls, and `scripts/run_pipeline.py` runs Bullshit Index analysis even when `--skip-revision` is set. This is acceptable if intentional, but it is a real cost boundary, not just local deterministic work.
- The test suite is broad and the focused safe subset passed: 139 tests passed in 4.88s. Full test execution was not run during this audit because the repository has 401 test files and some flows are provider/replay/research oriented.
- The best next work is not a rewrite. The highest-leverage next PRs are: fix docs drift, keep a maintained connectedness map, extract one or two path/sidecar/run-health helpers from large scripts, and add one no-provider integration test over the active runtime artifact chain.

## Observatory Product-Surface Truth (Refresh 2026-07-08)

This refresh adds a project-level status correction on what is currently a product surface versus inspection.

- Observatory is the active portable product presentation surface after the skill flow.
- The normal workspace sequence is `Outcome -> Learn -> Models -> Relations -> Map -> Receipts`.
- `Download MD` is the explicit private export action for full transcript material. Regular UI should not treat raw transcript text as a first-class reading layer.
- The same package content is reused across model/relational detail pages, but those pages should remain part of supporting knowledge and navigation, while Receipts remains the primary trust-and-accountability layer for optional inspection.
- Advanced Audit routes (`/audit`, `/audit/extraction`, `/usage`) are still review/diagnostic surfaces and are intentionally separated from the default user-first flow.

The project should treat this as the current truth boundary when deciding what contributors should wire next, especially around any future graph expansion.

## 2. Scope And Method

### Inspected

- User-facing skill instructions: `SKILL.md`, `docs/skill/STEPS.md`.
- Public orientation docs: `README.md`, `HOW_IT_WORKS.md`, selected product/eval/conversation-understanding docs.
- Runtime shell helpers under `scripts/skill/`.
- Main executable CLIs: `scripts/run_extract.py`, `scripts/run_pipeline.py`, `scripts/archive_run.py`, `scripts/lolla_doctor.py`.
- Core engine modules under `engine/system_b/`, especially pipeline orchestration, boundary provider, conversation context/loading, IR, usage, archive artifacts, V60, private tables, doctor/preflight, and Teacher adapter.
- Data/artifact substrate under `data/`, including compiled model affordance artifacts and curated/graph files.
- Observatory surface: `observatory/serve_result.py`, `observatory/build`, `scripts/skill/launch_observatory.py`.
- Tests by inventory and a focused no-provider test subset.
- Git state, branch, recent commits, file counts, file sizes, import graph, and likely entrypoints.

### Not Inspected Exhaustively

- The full 401-file pytest suite was not run.
- Live `$lolla`, `scripts/run_extract.py`, `scripts/run_pipeline.py`, Step 7 pressure-check agents, Product Delta replays, and research scripts were not executed because they may make provider calls, require secrets, or spend time/cost outside the audit mandate.
- The separate source repository for the compiled Observatory SPA was not available here. `observatory/serve_result.py` says the SPA build is compiled from a separate `Lolla-system-b/observatory/svelte-app` repo (`observatory/serve_result.py:7-11`).
- Most files under `research/` and generated review/product artifacts were sampled by path, naming, and references rather than read line-by-line. They are large generated/offline surfaces, not primary runtime code.

### Commands And Tests Run

- Repository orientation: `git status --short --branch`, `git log --oneline -8`, top-level `find`, `rg --files`, file counts by extension and directory, file size checks, package marker search.
- Runtime tracing: targeted `rg`, `sed`, `nl`, and static import/reference checks across `SKILL.md`, `docs/skill/STEPS.md`, shell helpers, scripts, engine modules, data loaders, archive code, and Observatory code.
- Static import-cycle check: a small AST-based script over `engine/system_b/*.py`.
- Safe syntax verification: `python3 -m py_compile` over the main runtime modules.
- Focused pytest subset: 139 tests passed in 4.88s.
- One mistaken pytest command referenced a non-existent test file and exited with pytest collection error 4; it was corrected immediately and no code was changed.

### Missing Secrets/Tools/Environment Limits

- `OPENROUTER_API_KEY`, `LOLLA_OPENROUTER_API_KEY`, `OPENAI_API_KEY`, and any live provider credentials were intentionally not used.
- The audit avoided commands that could mutate archives, call providers, or trigger expensive model runs.
- The worktree was dirty before the audit. Existing modifications and untracked files were treated as user work and left untouched.

## 3. Repository Map

### Git And Packaging State

- Branch/status observed with `git status --short --branch`: `feature/mental-model-teacher-observatory-interactive-graph-v0...origin/main`.
- Existing uncommitted work was present before the audit:
  - Modified: `docs/product/README.md`, `observatory/serve_result.py`.
  - Added/staged-looking entries in status: `docs/product/mental-model-teacher-observatory-interactive-graph-v0.md`, `reviews/codex-assisted/mental-model-teacher-observatory-interactive-graph-v0/review.json`, `tests/test_mental_model_teacher_observatory_interactive_graph.py`.
  - Many untracked docs, plans, and review artifacts under `docs/`, `plans/`, and `reviews/`.
- Recent commits show active development around Teacher/Observatory:
  - `748a614 Merge pull request #275 ... mental-model-teacher-observatory-native-learn-v0`
  - `f0457ef Add native Teacher Learn UX in Observatory`
  - `8ddf738 Add Teacher Observatory status copy v0`
  - `562aa99 Add Teacher Learn page to Observatory`
  - `606bf87 Add Teacher Observatory packet adapter`
- No root-level `pyproject.toml`, `setup.py`, `setup.cfg`, `pytest.ini`, `requirements.txt`, `Makefile`, or `package.json` was found at shallow depth. This is acceptable for a local skill/runtime, but it raises onboarding and repeatability friction.

### Top-Level Directory Purpose Map

| Path | Purpose | Runtime status |
|---|---|---|
| `SKILL.md` | User-facing skill contract and orchestration instructions. | Active runtime instruction. |
| `README.md` | Install, usage, artifact, data, cost, and project overview. | Documentation, partially runtime-relevant. |
| `HOW_IT_WORKS.md` | Narrative architecture and current flow overview. | Documentation; one confirmed step-order drift. |
| `docs/skill/` | Detailed skill step instructions. | Active runtime instruction. |
| `scripts/skill/` | Shell and launcher helpers used by skill steps. | Active runtime. |
| `scripts/run_extract.py` | Conversation extraction boundary and validation. | Active runtime plus provider boundary. |
| `scripts/run_pipeline.py` | Main pipeline CLI, usage summary, sidecar writer, result writer. | Active runtime plus provider boundary. |
| `scripts/archive_run.py` | Archive copying, finalization, generated artifacts, optional post-archive hook. | Active runtime. |
| `scripts/evals/` | Eval/product/review commands. | Mostly offline/review tooling. |
| `scripts/research/` | Research and generation utilities. | Offline/research tooling. |
| `engine/system_b/` | Main deterministic engine, provider boundary, data loaders, archive artifact builders, product adapters. | Mixed: active runtime, dormant pilots, offline tools. |
| `data/` | Knowledge graph, relation graph, embeddings, curated substrate, compiled affordances. | Active data plus historical/offline artifacts. |
| `observatory/` | Local zero-dependency review server and compiled SPA build. | Active review/product surface. |
| `tests/` | Broad test suite. | Verification. |
| `docs/product/`, `docs/evals/`, `docs/conversation-understanding/` | Product plans, eval docs, design/research notes. | Docs-only/offline unless wired by specific script. |
| `reviews/` | Review outputs and synthetic/codex-assisted review artifacts. | Review artifacts, not runtime. |
| `plans/` | PR and implementation plans. | Docs-only planning. |
| `research/` | Generated/source research artifacts. | Offline/research archive. |
| `tasks/` | Task artifacts. | Mostly planning/review support. |
| `references/` | Reference material. | Support material. |

### Size And Shape

- File counts by top-level directory are dominated by artifacts and tests: `research` about 1577 files, `data` about 1294, `tests` about 1117, `docs` about 393, `engine` about 335, `scripts` about 288, `reviews` about 269.
- Extension counts are artifact-heavy: about 2484 `.json`, 1212 `.md`, 729 `.py`, and 881 local `.pyc` files. The `__pycache__` and `.pyc` files appear ignored by git and are local workspace noise, not tracked repository content.
- Major data footprint: `data` about 325 MB, `research` about 49 MB, `tests` about 30 MB, `engine` about 7 MB, `scripts` about 6.3 MB.
- Largest active files:
  - `observatory/serve_result.py`: 6360 lines.
  - `engine/system_b/pipeline.py`: 1998 lines.
  - `scripts/run_pipeline.py`: 1503 lines.
  - `scripts/archive_run.py`: 806 lines.
  - `SKILL.md`: 293 lines.
  - `README.md`: 1266 lines.
  - `HOW_IT_WORKS.md`: 596 lines.

### Major Subsystems

- Skill orchestration: `SKILL.md`, `docs/skill/STEPS.md`, `scripts/skill/*.sh`, `scripts/skill/*.py`.
- Extraction boundary: `scripts/run_extract.py`, extraction prompts/schemas in `engine/system_b`.
- Deterministic core: `ConversationContext`, loader, IR constructor, catalogs, graphs, routing, pass runners, pipeline assembly.
- Provider boundary: OpenRouter/OpenAI-compatible boundary clients, optional Gemini CLI client, usage/pricing/run-health modules.
- Data/knowledge substrate: graph files, curated chunks, embeddings database, model affordance compilations.
- Archive and audit custody: archive run script, agent result, evaluation artifact, reasoning trace, graph survival, event/state ledgers.
- Observatory/product surface: local server, compiled SPA build, Teacher adapter, archive case APIs.
- Offline/review/eval tooling: `scripts/evals/`, product docs, review artifacts, research scripts.
- Tests: broad file coverage with a meaningful set of boundary/custody tests.

## 4. Main Execution Flow

### Step-By-Step Runtime Flow

1. The user invokes the `lolla` skill. `SKILL.md` identifies the skill as a conversation-aware reasoning audit and says the full runtime is defined in `docs/skill/STEPS.md` (`SKILL.md:32`, `SKILL.md:93`).
2. Skill setup runs `scripts/skill/setup.sh`. It resolves the skill directory, validates `engine/system_b` and `data`, loads `.env` candidates, checks audit mode, validates OpenRouter presence and OpenAI optionality, creates a run ID, writes `/tmp/lolla_${LOLLA_RUN_ID}_env.sh`, symlinks `/tmp/lolla_latest_env.sh`, and records `run_initialized` (`scripts/skill/setup.sh:3-162`).
3. Step 1 captures the exact conversation into `/tmp/lolla_${LOLLA_RUN_ID}_conversation.txt` (`docs/skill/STEPS.md:55-75`).
4. Step 2 runs `scripts/skill/run_extract_step.sh`. The wrapper sources the run env, guards the requested run ID against `LOLLA_EXPECTED_RUN_ID`, checks the expected conversation/extraction paths, validates capture, and calls `scripts/run_extract.py` (`scripts/skill/run_extract_step.sh:58-130`).
5. `scripts/run_extract.py` performs local capture validation before provider calls. It rejects critically incomplete captures without an OpenRouter call, truncates safely, calls OpenRouter for structured extraction, validates quotes and canonical keys, writes extraction JSON, and writes `/tmp/lolla_${RUN_ID}_extraction_calls.json` for cost telemetry (`scripts/run_extract.py:367-461`, `scripts/run_extract.py:658-694`, `scripts/run_extract.py:716-845`, `scripts/run_extract.py:854-885`).
6. Step 3 runs `scripts/skill/run_pipeline_step.sh`. It sources the run env, validates input path arguments, checks extraction/conversation files, and calls `scripts/run_pipeline.py` with `--skip-revision` and `--pre-step6-portfolio step6_private` (`scripts/skill/run_pipeline_step.sh:4-23`, `scripts/skill/run_pipeline_step.sh:59-120`).
7. `scripts/run_pipeline.py` validates audit mode and run state, loads extraction and `ConversationContext`, creates a temporary data-root symlink so engine code can read `root/build/...`, configures `PipelineConfig`, loads `SystemBPipeline` with OpenRouter, runs the lane pipeline, runs Bullshit Index, attaches V60 enrichment, writes pre-Step-6 private sidecars, builds usage/run-health summaries, and writes `/tmp/lolla_${RUN_ID}_result.json` (`scripts/run_pipeline.py:438-455`, `scripts/run_pipeline.py:820-981`, `scripts/run_pipeline.py:996-1499`).
8. `engine/system_b/pipeline.py` loads the data substrate and provider boundary, constructs conversation IR, runs pass 1/pass 2 pressure analysis, companion lane, frame pressure, structural coverage, and audit assembly (`engine/system_b/pipeline.py:326-365`, `engine/system_b/pipeline.py:368-607`).
9. Step 6 in the skill uses the result and private sidecars to revise the answer and persist private ledgers before pressure/memo/Observatory/archive. The docs emphasize that private support ledgers are not user-facing artifacts (`docs/skill/STEPS.md:221-327`).
10. Step 7 pressure-check agents are default-off and only run when explicitly requested (`SKILL.md:93`, `docs/skill/STEPS.md:333-384`).
11. Step 8 persists pressure-check state and writes the memo. Step 9 launches Observatory and archives the run. Step 10 verifies archive receipt silently (`docs/skill/STEPS.md:426-473`, `docs/skill/STEPS.md:561-711`).
12. `scripts/archive_run.py` copies core artifacts to `~/.local/share/lolla/runs` or `LOLLA_ARCHIVE_DIR`, computes case identity by conversation hash/fingerprint, finalizes live/product/V60 hygiene, writes manifest and generated artifacts, and optionally attaches a Decision Work brief in a failed-closed hook (`scripts/archive_run.py:1-58`, `scripts/archive_run.py:331-497`, `scripts/archive_run.py:500-516`, `scripts/archive_run.py:655-730`).
13. `scripts/skill/launch_observatory.py` starts `observatory/serve_result.py` in the background and waits for an HTTP response (`scripts/skill/launch_observatory.py:57-105`). The server exposes result, archive, usage, audit, graph, sidecar, and Teacher endpoints locally (`observatory/serve_result.py:5984-6184`).

### Mermaid Map

```mermaid
flowchart TD
  U[User invokes lolla skill] --> S[SKILL.md]
  S --> ST[docs/skill/STEPS.md]
  ST --> Setup[scripts/skill/setup.sh]
  Setup --> Env[/tmp/lolla_RUN_env.sh<br/>/tmp/lolla_latest_env.sh]
  Setup --> Conv[/tmp/lolla_RUN_conversation.txt]
  Conv --> ExtractWrap[scripts/skill/run_extract_step.sh]
  ExtractWrap --> Extract[scripts/run_extract.py]
  Extract -->|OpenRouter API| OR1[(Provider boundary)]
  Extract --> Extraction[/tmp/lolla_RUN_extraction.json<br/>extraction_calls sidecar]
  Extraction --> PipeWrap[scripts/skill/run_pipeline_step.sh]
  PipeWrap --> PipeCLI[scripts/run_pipeline.py]
  PipeCLI --> Core[engine/system_b/pipeline.py]
  Core --> Passes[Pass 1 / Pass 2 / Companion / Frame / Structural Coverage]
  Passes -->|OpenRouter API| OR2[(Provider boundary)]
  PipeCLI -->|Bullshit Index OpenRouter call(s)| BI[(Provider boundary)]
  PipeCLI -->|optional embeddings| OA[(OpenAI embeddings boundary)]
  PipeCLI --> V60[V60 enrichment and private sidecars]
  PipeCLI --> Result[/tmp/lolla_RUN_result.json]
  Result --> SkillRevise[Skill Step 6 answer revision and private ledgers]
  SkillRevise --> Memo[Memo / pressure state]
  Memo --> Observatory[scripts/skill/launch_observatory.py<br/>observatory/serve_result.py]
  Memo --> Archive[scripts/archive_run.py]
  Archive --> Artifacts[Manifest / agent_result / evaluation / reasoning_trace / graph_survival]
  Observatory --> LocalUI[Local Observatory and audit APIs]
```

### Provider/API Boundaries

- OpenRouter extraction: `scripts/run_extract.py` calls OpenRouter after local capture validation (`scripts/run_extract.py:716-739`).
- OpenRouter runtime lanes: `scripts/run_pipeline.py` calls `SystemBPipeline.load_live(provider_name="openrouter")` (`scripts/run_pipeline.py:931-936`), which loads an OpenRouter-compatible boundary client from environment (`engine/system_b/pipeline.py:354-365`).
- Bullshit Index: `scripts/run_pipeline.py` runs BI after the main pipeline even with `--skip-revision`; this is a provider boundary separate from the main lane calls (`scripts/run_pipeline.py:996-1074`).
- Optional OpenAI embeddings: `scripts/run_pipeline.py` enables embeddings when `OPENAI_API_KEY` is present (`scripts/run_pipeline.py:820-929`).
- Optional Step 7 pressure-check agents: documented as default-off in `SKILL.md` and `docs/skill/STEPS.md`, but provider/cost-bearing if explicitly enabled.
- Gemini CLI provider exists in `engine/system_b/boundary_provider.py`, but the normal live CLI path passes `provider_name="openrouter"`.

## 5. Deterministic Machinery Inventory

### Skill Run State And Shell Handoff

- Purpose: create a per-run state envelope and avoid cross-run artifact confusion.
- Entrypoints: `scripts/skill/setup.sh`, `scripts/skill/run_extract_step.sh`, `scripts/skill/run_pipeline_step.sh`.
- Inputs/outputs: environment files, `/tmp/lolla_${RUN_ID}_*` artifact paths, operator/live transcript logs.
- Artifacts written/read: `/tmp/lolla_${RUN_ID}_env.sh`, `/tmp/lolla_latest_env.sh`, live transcript, operator log, conversation/extraction/result paths.
- Tests: indirectly covered through pipeline/archive tests and run-state helper tests; shell wrappers themselves have limited direct coverage.
- Status: active runtime.
- Risk notes: the `/tmp/lolla_latest_env.sh` fallback is convenient but potentially stale if called outside the expected skill flow. The run ID guards and path validation reduce this risk.

### Capture Validation And Extraction Guard

- Purpose: reject malformed or incomplete conversation capture before paying for extraction, then produce validated structured extraction.
- Entrypoints: `scripts/skill/run_extract_step.sh`, `scripts/run_extract.py`.
- Inputs/outputs: raw transcript in `/tmp/lolla_${RUN_ID}_conversation.txt`; extraction JSON and extraction-call sidecar.
- Artifacts written/read: conversation file, extraction file, `/tmp/lolla_${RUN_ID}_extraction_calls.json`.
- Tests: extraction-related tests were not exhaustively run in the focused subset, but static compile passed.
- Status: active runtime and provider boundary.
- Risk notes: good local guards exist. The stale comment referencing `scripts/run_live_pipeline.py` is documentation drift, not runtime risk (`scripts/run_extract.py:141`).

### Conversation Context And Loader

- Purpose: create the canonical runtime conversation shape used by all lanes.
- Entrypoints: `engine/system_b/conversation_context.py`, `engine/system_b/conversation_loader.py`, `scripts/run_pipeline.py`.
- Inputs/outputs: extraction JSON plus `[Turn N]` transcript; `ConversationContext` object.
- Artifacts written/read: no persistent artifacts directly; reads extraction/conversation files.
- Tests: `tests/test_conversation_context.py`, `tests/test_conversation_loader.py`, `tests/test_pipeline_context_runtime.py` passed in the focused run.
- Status: active runtime.
- Risk notes: this is a deep module that hides useful complexity and should be preserved as the boundary for future pipeline work.

### IR Construction And Provenance

- Purpose: convert conversation context into provenance-bearing IR for lane reasoning.
- Entrypoints: `engine/system_b/ir_constructor.py`, `engine/system_b/ir.py`.
- Inputs/outputs: `ConversationContext`; conversation IR, claims, turns, evidence spans.
- Artifacts written/read: no direct files.
- Tests: `tests/test_ir.py` passed in the focused run.
- Status: active runtime for base IR. Specialist extractors are injectable and appear dormant/offline in the normal runtime path because `pipeline.run()` calls `construct_conversation_ir(conversation_context)` without specialist extractors.
- Risk notes: good deep module. The dormant specialist-extractor path should be documented as optional/offline if maintained.

### Catalogs, Graphs, Routing, And Compiled Substrate

- Purpose: provide local knowledge graph, relationship graph, tendency catalog, pressure bundle selection, routing, and embeddings-backed retrieval.
- Entrypoints: `engine/system_b/tendency_catalog.py`, `engine/system_b/relation_graph.py`, `engine/system_b/pressure_bundle_selector.py`, `engine/system_b/routing.py`, pipeline load methods.
- Inputs/outputs: graph JSON, curated chunks, embeddings database, compiled substrate.
- Artifacts written/read: `data/knowledge_graph.json`, `data/relationship_graph.json`, `data/curated/*`, `data/embeddings.db`, `data/compiled/*`.
- Tests: broad catalog/routing tests exist; not all were run.
- Status: active data substrate plus historical/offline compiled artifacts.
- Risk notes: `TendencyCatalog` checks for optional `munger_routing_table.json` overlays, but no such file was found under `data/`. This is an optional fallback path, not confirmed dead behavior.

### System B Pipeline

- Purpose: orchestrate pass 1, pass 2, companion, frame pressure, structural coverage, and final audit assembly.
- Entrypoints: `engine/system_b/pipeline.py`, `scripts/run_pipeline.py`.
- Inputs/outputs: extraction, conversation context, data root, provider boundary; pipeline result.
- Artifacts written/read: reads data substrate; persistent artifacts are written by `scripts/run_pipeline.py`.
- Tests: `tests/test_pipeline_context_runtime.py`, `tests/test_pr1_boundary_call_persistence.py`, and cost/boundary tests passed in the focused run.
- Status: active runtime.
- Risk notes: `pipeline.py` remains a central 1998-line module despite pass1/pass2 extraction. The risk is concentrated change coordination, not immediate runtime breakage.

### Pass Runners

- Purpose: run pass 1 and pass 2 lane prompts while preserving boundary metadata.
- Entrypoints: `engine/system_b/pass1_runner.py`, `engine/system_b/pass2_runner.py`.
- Inputs/outputs: selected tendencies, relation graph, evidence, boundary client.
- Artifacts written/read: provider call metadata; no direct artifact writes.
- Tests: covered indirectly by pipeline and boundary tests.
- Status: active runtime.
- Risk notes: these are useful extractions from `pipeline.py`. Compatibility re-exports and TYPE_CHECKING imports still create import-graph coupling.

### Provider Boundary, Usage, And Pricing

- Purpose: isolate OpenRouter/OpenAI-compatible calls, record request/response metadata, and estimate cost/usage.
- Entrypoints: `engine/system_b/boundary_provider.py`, `engine/system_b/usage_summary.py`, `engine/system_b/pricing.py`, `engine/system_b/provider_boundary_health.py`.
- Inputs/outputs: prompts and schemas; provider responses, usage metadata, cost summaries.
- Artifacts written/read: call logs embedded into result/usage artifacts; extraction-call sidecar.
- Tests: `tests/test_model_cost_hardening.py`, `tests/test_pr1_boundary_call_persistence.py` passed.
- Status: active runtime and provider boundary.
- Risk notes: good boundary for OSS stage. The real risk is call volume and hidden optional calls, not the absence of a boundary abstraction.

### V60 Enrichment

- Purpose: enrich runtime/product transport with compiled model affordance support without making it a final-answer selector.
- Entrypoints: `engine/system_b/v60_enrichment.py`, `scripts/run_pipeline.py`, archive finalizers.
- Inputs/outputs: result candidates plus `data/compiled/model_affordances/affordances_v60.json`.
- Artifacts written/read: `affordances_v60.json`, V60 sidecar skeleton, product/live result fields.
- Tests: `tests/test_v60_enrichment_runtime.py` passed.
- Status: active runtime/product support. Earlier `affordances_v1` through `affordances_v59` appear historical/offline.
- Risk notes: the active contract is exact V60. Historical artifacts should be labeled as lineage if kept.

### Pre-Step-6 Private Table And Shadow Portfolio

- Purpose: generate private support material for answer revision without extra LLM calls.
- Entrypoints: `engine/system_b/pre_step6_private_table.py`, `scripts/run_pipeline.py`.
- Inputs/outputs: pipeline result and candidate support records; private table and shadow portfolio sidecars.
- Artifacts written/read: `/tmp/lolla_${RUN_ID}_pre_step6_private_table.json`, shadow sidecars, result references.
- Tests: `tests/test_pre_step6_private_table.py` passed.
- Status: active runtime, private/custody support.
- Risk notes: good separation of private evidence from public answer, but sidecar path conventions should be centralized.

### Archive And Generated Artifacts

- Purpose: persist run artifacts, build case identity, write manifest and derived audit artifacts.
- Entrypoints: `scripts/archive_run.py`, `engine/system_b/agent_result.py`, `engine/system_b/evaluation.py`, `engine/system_b/reasoning_trace.py`.
- Inputs/outputs: `/tmp/lolla_${RUN_ID}_*` artifacts; archive case directory.
- Artifacts written/read: manifest, result, memo, extraction, conversation, graph survival, agent result, evaluation, reasoning trace, optional Decision Work brief.
- Tests: `tests/test_archive_run_case_identity.py`, `tests/test_agent_result.py`, `tests/test_evaluation_artifact.py`, `tests/test_reasoning_trace_archive.py` passed.
- Status: active runtime.
- Risk notes: strong custody artifacts. `scripts/archive_run.py` mixes copying, finalization, generated artifact construction, and optional hooks in one file.

### Observatory And Teacher Adapter

- Purpose: local review/product surface over live result and archive cases.
- Entrypoints: `scripts/skill/launch_observatory.py`, `observatory/serve_result.py`, `engine/system_b/mental_model_teacher_observatory_packet_adapter.py`.
- Inputs/outputs: result JSON, archive files, sidecars, compiled SPA build, local HTTP responses.
- Artifacts written/read: reads `/tmp` and archive sidecars; does not normally write provider artifacts.
- Tests: `tests/test_observatory_launcher.py`, `tests/test_mental_model_teacher_observatory_packet_adapter.py` passed. A new untracked/added interactive graph test exists in the worktree but was not run.
- Status: active review/product surface.
- Risk notes: `observatory/serve_result.py` is the largest active module and a likely development bottleneck. The Teacher adapter is intentionally read-only and carries explicit non-claims.

### Doctor / Preflight

- Purpose: read-only local preflight and artifact custody diagnostics.
- Entrypoints: `scripts/lolla_doctor.py`, `engine/system_b/lolla_doctor.py`.
- Inputs/outputs: local environment/archive/report data; optional safe output path.
- Artifacts written/read: reads environment and local paths; no model calls or archive mutation by design.
- Tests: `tests/test_lolla_doctor.py` exists but was not part of the focused test command.
- Status: offline/local support tool, not active in the normal skill flow.
- Risk notes: good candidate to surface more clearly before expensive runs.

### Eval, Product, Research, And Review Tools

- Purpose: offline evaluation, product-surface validation, generated reviews, and research workflows.
- Entrypoints: `scripts/evals/*`, `scripts/research/*`, selected `engine/system_b/decision_*` and product modules.
- Inputs/outputs: fixtures, review JSON, product docs, synthetic artifacts, optional explicit archive sidecars.
- Artifacts written/read: varies by tool; tests assert several tools do not call providers or mutate archives unless explicitly requested.
- Tests: many exist but were not exhaustively run.
- Status: offline/review/product tooling, with a small number of default-off hooks from archive.
- Risk notes: conceptually valuable but can confuse readers because the artifact volume is large and many files are not runtime-active.

## 6. Connectedness Matrix

| Component / file cluster | Status | Called by | Calls into | Writes artifacts | Reads artifacts | Evidence | Notes |
|---|---|---|---|---|---|---|---|
| `SKILL.md`, `docs/skill/STEPS.md` | Active runtime instruction | User skill invocation | `scripts/skill/*`, manual orchestration steps | None directly | Repo docs/scripts | `SKILL.md:32`, `SKILL.md:93`, `docs/skill/STEPS.md:55-75` | Source of truth for step flow. |
| `scripts/skill/setup.sh` | Active runtime | Skill preamble | `engine.system_b.run_state`, env loaders | `/tmp/lolla_${RUN_ID}_env.sh`, latest env symlink, logs | `.env` candidates, data dirs | `scripts/skill/setup.sh:3-162` | Strong run guard setup; latest fallback is convenient but implicit. |
| `scripts/skill/run_extract_step.sh` | Active runtime | Step 2 | `scripts/run_extract.py` | Extraction status/events | Run env, conversation file | `scripts/skill/run_extract_step.sh:58-193` | Rejects mismatched run/path arguments. |
| `scripts/run_extract.py` | Active runtime and provider boundary | Extract wrapper | OpenRouter; extraction validation helpers | Extraction JSON, extraction-call sidecar | Conversation file | `scripts/run_extract.py:658-845`, `scripts/run_extract.py:854-885` | Refuses critical capture before provider call. |
| `scripts/skill/run_pipeline_step.sh` | Active runtime | Step 3 | `scripts/run_pipeline.py` | Pipeline status/events | Env, extraction, conversation | `scripts/skill/run_pipeline_step.sh:59-235` | Passes `--skip-revision` and private portfolio mode. |
| `scripts/run_pipeline.py` | Active runtime and provider boundary | Pipeline wrapper; direct CLI | `SystemBPipeline`, BI, V60, private table, usage/run health | Result JSON, private sidecars, V60 skeleton, usage fields | Extraction, conversation, data substrate, extraction-call sidecar | `scripts/run_pipeline.py:820-1499` | Major god-script candidate. |
| `engine/system_b/pipeline.py` | Active core runtime | `scripts/run_pipeline.py`, tests | pass runners, catalogs, companion, frame, lane 4, audit assembly | No direct main artifact writes | Data root, provider boundary | `engine/system_b/pipeline.py:326-607` | Central orchestrator; also compatibility/re-export hub. |
| `engine/system_b/pass1_runner.py`, `pass2_runner.py` | Active runtime helpers | `pipeline.py` | boundary client, pressure logic | Provider call metadata | Tendency/evidence context | `engine/system_b/pass1_runner.py:1-6`, `engine/system_b/pass2_runner.py:1-6` | Good extractions; still coupled to pipeline types. |
| `conversation_context.py`, `conversation_loader.py`, `ir_constructor.py`, `ir.py` | Active deterministic runtime | `scripts/run_pipeline.py`, `pipeline.py` | IR/provenance constructors | None directly | Extraction/conversation | Focused tests passed | Strong boundary; preserve. |
| `boundary_provider.py`, `usage_summary.py`, `pricing.py` | Active provider/cost boundary | Extraction/pipeline/BI users | OpenRouter/OpenAI-compatible APIs; optional Gemini CLI | Call logs/usage summaries | Env keys, model pricing data | `scripts/run_pipeline.py:931-981`, focused tests passed | Default live runtime uses OpenRouter. |
| `data/knowledge_graph.json`, `relationship_graph.json`, `curated/*`, `embeddings.db` | Active data substrate | Pipeline loaders | Local graph/retrieval code | None at runtime | Local data files | `engine/system_b/pipeline.py:326-352` | Large but legitimate local substrate. |
| `data/compiled/model_affordances/affordances_v60.json` | Active V60 support | `v60_enrichment.py` | Candidate merge/enrichment | Runtime V60 fields/sidecars | V60 JSON | `engine/system_b/v60_enrichment.py:99-130` | v1-v59 are historical/offline lineage. |
| `pre_step6_private_table.py`, V60 sidecar functions | Active private/custody support | `scripts/run_pipeline.py` | Local deterministic assembly | Private table/shadow sidecars | Pipeline result | `scripts/run_pipeline.py:1163-1239` | No new model calls for private table. |
| `scripts/archive_run.py` | Active archive runtime | Skill Step 9/finalize helper | archive artifact builders, optional Decision Work hook | Archive case directory and generated artifacts | `/tmp/lolla_${RUN_ID}_*` | `scripts/archive_run.py:331-497` | Strong custody, mixed responsibilities. |
| `agent_result.py`, `evaluation.py`, `reasoning_trace.py` | Active archive artifacts | `scripts/archive_run.py` | Local deterministic artifact builders | JSON artifacts in archive | Result/memo/manifest/sidecars | `engine/system_b/agent_result.py:42-130`, `engine/system_b/evaluation.py:54-116`, `engine/system_b/reasoning_trace.py:62-170` | Conservative, no judge/quality-score claims. |
| `observatory/serve_result.py` | Active review/product surface | `launch_observatory.py`, direct CLI | archive readers, sidecar readers, Teacher adapter | HTTP responses; no provider calls | result/archive/build sidecars | `observatory/serve_result.py:1-16`, `observatory/serve_result.py:5984-6184` | Largest active file; local-only server. |
| `scripts/skill/launch_observatory.py` | Active runtime launcher | Skill Step 9 | `observatory/serve_result.py` | Background process/logs | Result file | `scripts/skill/launch_observatory.py:57-105` | Waits for local HTTP readiness. |
| `mental_model_teacher_observatory_packet_adapter.py` | Active Observatory read-only product surface | `observatory/serve_result.py` | Local package summary functions | API response only | Teacher package dir | `engine/system_b/mental_model_teacher_observatory_packet_adapter.py:1-6`, `engine/system_b/mental_model_teacher_observatory_packet_adapter.py:185-188` | Explicit non-claims; not runtime reasoning. |
| `scripts/lolla_doctor.py`, `lolla_doctor.py` | Offline/local support tool | Manual CLI | local diagnostics | Optional report only | Env/archive paths | `scripts/lolla_doctor.py:1-33`, `engine/system_b/lolla_doctor.py:57-123` | Useful preflight; not in main flow. |
| `scripts/evals/*`, `docs/evals/*` | Offline/review tooling | Manual eval commands, tests | fixtures, product/eval modules | Reports, sidecars when explicit | Fixtures/archive snapshots | Docs and test names | Not normal skill runtime. |
| `decision_work_brief_runtime_attachment.py` | Active-but-default-off hook | `scripts/archive_run.py` | Decision Work brief builder | Optional archive attachment | Archive result | `scripts/archive_run.py:500-516` | Failed-closed and non-blocking. |
| Authority/stress promoted pilot bridges | Dormant/default-off in normal runtime | `PipelineConfig` flags | `.tmp` workspaces, pilot modules | Possible `.tmp` workspaces | Pilot configs/data | `engine/system_b/pipeline.py:145-167`, `engine/system_b/pipeline.py:1419-1538` | Not exposed by normal `run_pipeline.py` config. |
| Gemini CLI provider | Dormant/local-substitutable provider | `load_boundary_client_from_env(provider_name)` if selected | `gemini` subprocess | Provider call metadata | CLI/env | `engine/system_b/boundary_provider.py` | Normal live path hardcodes OpenRouter. |
| `plans/`, `reviews/`, much of `docs/product/` | Docs-only/review artifacts | Humans/tests | None or offline tools | Markdown/JSON artifacts | Existing review data | directory inventory | Not dead merely because not runtime-active. |
| `research/`, `scripts/research/` | Offline/research | Manual research workflows | Research scripts/providers if invoked | Research outputs | Source/generated research | directory inventory | Excluded from runtime conclusions. |

## 7. Legacy, Drift, And Dead-Code Candidates

### Confirmed Legacy Or Compatibility

- `scripts/run_pipeline.py` explicitly rejects deprecated `--extraction-json` and tells callers to use `--extraction-file` (`scripts/run_pipeline.py:659-671`).
- `scripts/run_pipeline.py` accepts `--new-contract` as a deprecated no-op compatibility alias (`scripts/run_pipeline.py:724-730`).
- `scripts/run_extract.py` still writes legacy `critique_request` alongside `audit_seed` for compatibility (`scripts/run_extract.py:839-845`).
- `engine/system_b/pipeline.py` remains a compatibility/re-export hub for types and helpers that have started moving out, including boundary tracing and pass runners. This is intentional compatibility, not dead code.
- `scripts/archive_run.py` handles legacy manifests without conversation hashes, as described in its docstring and covered by archive identity tests.

### Suspected Legacy Or Dormant Elements

- `data/compiled/model_affordances/affordances_v1.json` through `affordances_v59.json` are likely historical/offline lineage. `v60_enrichment.py` requires `affordances_v60.json` for the active V60 path (`engine/system_b/v60_enrichment.py:99-130`).
- Promoted overoptimism/authority/stress pilot bridges are default-off in `PipelineConfig` and not enabled by the normal `scripts/run_pipeline.py` configuration (`engine/system_b/pipeline.py:145-167`, `scripts/run_pipeline.py:820-929`). These are dormant/default-off, not confirmed dead.
- Specialist extraction modules for constraints, dropped threads, and stance are injectable through `ir_constructor.py` but not wired into the normal runtime call path observed in `pipeline.py`. Treat as dormant/offline until a live caller is identified.
- `GeminiCliBoundaryClient` is a local-substitutable provider option but not used by the normal live CLI, which passes OpenRouter explicitly.

### Docs-Code Mismatches

- `HOW_IT_WORKS.md` says pressure-check state is persisted after Step 10 and optional pressure-check agents can run after Step 10 (`HOW_IT_WORKS.md:113-114`). `SKILL.md` and `docs/skill/STEPS.md` describe Step 7 as default-off before memo/archive and Step 8b as pressure-check state persistence before Step 9/10. The active skill docs are more specific and should be treated as current.
- `scripts/run_extract.py` contains a comment saying the `.env` loader follows the same pattern as `scripts/run_live_pipeline.py` (`scripts/run_extract.py:141`), but no `scripts/run_live_pipeline.py` file was found. This is stale commentary, not active behavior.

### Duplicate Concepts Or Schemas

- Runtime result, live result hygiene, product output, archive result, agent result, evaluation, reasoning trace, graph survival, V60 ledger, and private table sidecars are separate but adjacent schemas. Many are justified by custody boundaries, but contributors need a map to know which artifact is authoritative for which consumer.
- Run identity appears in shell env, `run_state`, usage summary validation, archive manifest, Observatory path resolution, and sidecar naming. The repeated validation is good; the repeated path construction is maintainability friction.
- Pipeline result types are partly centralized in `engine/system_b/pipeline.py` and partly consumed by downstream helper modules. This contributes to import cycles and compatibility re-exports.

### Things That Look Old But Are Still Valid

- Historical compiled affordance versions are valid lineage if they are intentionally retained as research/product history.
- Large JSON graph/data files are not dead code; they are the local substrate loaded by pipeline components.
- Review artifacts under `reviews/` and plan docs under `plans/` are not runtime-active, but they may be intentional development history.
- Product Delta and Decision Work surfaces are intentionally offline/review unless explicitly invoked. Their disconnectedness is a product-safety feature, not evidence of dead code by itself.

## 8. Architecture Risks

### Finding 1: Main Runtime CLI Mixes Too Many Responsibilities

- Severity: High.
- Evidence: `scripts/run_pipeline.py` handles CLI parsing, deprecated flag handling, audit-mode validation, run-state checks, data-root symlink construction, extraction loading, pipeline configuration, live provider loading, revision/BI execution, V60 enrichment, private sidecar writing, usage/cost summary, run-health assembly, and result serialization (`scripts/run_pipeline.py:438-455`, `scripts/run_pipeline.py:820-1499`).
- Why it matters now: future runtime features will naturally attach here, increasing the chance of accidental provider calls, sidecar mismatches, or result schema drift.
- Why it may be acceptable for OSS-stage maturity: a single CLI orchestrator is pragmatic while the runtime contract is still evolving. It has working tests around important boundaries.
- Recommended next step: extract one behavior-preserving helper at a time, starting with run-health assembly or sidecar writing. Do not rewrite the CLI.

### Finding 2: Observatory Server Is A Real Bottleneck File

- Severity: High.
- Evidence: `observatory/serve_result.py` is 6360 lines and contains local HTTP routing, SPA injection, archive case loading, sidecar discovery, API payload assembly, graph endpoints, usage views, Teacher integration, and fallback HTML (`observatory/serve_result.py:1-16`, `observatory/serve_result.py:1906-2121`, `observatory/serve_result.py:2420-2528`, `observatory/serve_result.py:5984-6360`).
- Why it matters now: current branch work is already modifying Observatory. UI/product additions will likely keep landing in the same file, making regressions hard to isolate.
- Why it may be acceptable for OSS-stage maturity: the zero-dependency server is deliberately portable, and a monofile local server is defensible for a skill runtime.
- Recommended next step: move archive/sidecar resolution and case payload building into small local modules with tests, while keeping the server entrypoint intact.

### Finding 3: `/tmp` Artifact And Env Handoff Is Powerful But Implicit

- Severity: Medium.
- Evidence: setup and wrappers write/read `/tmp/lolla_${RUN_ID}_env.sh`, `/tmp/lolla_latest_env.sh`, conversation/extraction/result files, private sidecars, and event files (`scripts/skill/setup.sh:84-162`, `scripts/skill/run_extract_step.sh:58-116`, `scripts/skill/run_pipeline_step.sh:44-120`). Observatory also searches `/tmp` sidecars for active runs (`observatory/serve_result.py:2067-2121`).
- Why it matters now: adding a new sidecar or helper requires knowing naming conventions across shell, Python CLI, archive, and Observatory.
- Why it may be acceptable for OSS-stage maturity: local files are transparent, inspectable, and testable; there are meaningful run ID guards.
- Recommended next step: create a small artifact-path registry module and use it first from Python code. Shell wrappers can adopt it later via a helper command.

### Finding 4: Active Runtime And Offline/Product Artifacts Are Hard To Distinguish

- Severity: Medium.
- Evidence: the repo contains hundreds of docs/review/product/research files next to active runtime code. README explicitly says Product Delta does not invoke the skill, call providers, or mutate archives (`README.md:171-172`), while `docs/skill/STEPS.md` defines active behavior. The connectedness boundary is distributed.
- Why it matters now: contributors may wire offline surfaces into runtime accidentally, or dismiss valid product/review artifacts as dead because they are not called by the skill.
- Why it may be acceptable for OSS-stage maturity: the project is both a runtime and a research/product lab; keeping artifacts in-repo can be useful.
- Recommended next step: maintain a simple `docs/architecture/connectedness-map.md` or generated component manifest with statuses: active runtime, offline tool, review surface, docs-only, dormant/default-off, historical.

### Finding 5: Provider Cost Boundary Is Broad

- Severity: Medium.
- Evidence: `README.md` documents a typical default audit at about 50-85 OpenRouter calls (`README.md:1140-1195`). `scripts/run_pipeline.py` runs BI calls after pipeline execution even when revision is skipped (`scripts/run_pipeline.py:996-1074`). OpenAI embeddings are enabled when `OPENAI_API_KEY` is present (`scripts/run_pipeline.py:820-929`).
- Why it matters now: users and maintainers need to know which paths are safe static checks and which paths spend provider calls.
- Why it may be acceptable for OSS-stage maturity: the docs are unusually candid about costs, and provider call logs/usage summaries exist.
- Recommended next step: make `lolla_doctor` or a preflight receipt more prominent before live runs. Consider a clearly named mode or receipt that states BI and embeddings policy before execution.

### Finding 6: Import Cycles Reflect Type And Compatibility Coupling

- Severity: Medium.
- Evidence: AST import graph over `engine/system_b/*.py` found three cycles, including a large cycle involving `pipeline`, pass runners, routing, telemetry, boundary tracing, audit assembly, and pilot modules; a smaller `companion`/`companion_routing` cycle; and an offline-looking `compilation_bundle`/`operational_curation` cycle. Some edges are `TYPE_CHECKING` or lazy imports, but the dependency shape is still real.
- Why it matters now: moving shared types or testing helpers can trigger broad import failures.
- Why it may be acceptable for OSS-stage maturity: these cycles are not currently breaking runtime, and some were created to preserve compatibility during extraction.
- Recommended next step: move shared dataclasses/protocols out of `pipeline.py` into a small type module while preserving temporary re-exports.

### Finding 7: Archive Script Mixes Persistence, Finalization, And Derived Artifact Generation

- Severity: Medium.
- Evidence: `scripts/archive_run.py` validates run state, matches/creates case identity, finalizes product/live/V60 result fields, copies core files, writes manifest, writes generated artifacts, and runs an optional Decision Work hook (`scripts/archive_run.py:331-497`, `scripts/archive_run.py:500-516`, `scripts/archive_run.py:655-730`).
- Why it matters now: archive changes can accidentally affect product/live result hygiene or generated artifact semantics.
- Why it may be acceptable for OSS-stage maturity: keeping archive policy in one script makes the current custody story inspectable.
- Recommended next step: extract generated artifact writing into a local module first. Leave archive case creation and file copying in the script until the boundary proves stable.

### Finding 8: Packaging/Test Harness Is Informal

- Severity: Low.
- Evidence: no shallow root `pyproject.toml`, `pytest.ini`, `requirements.txt`, or `Makefile` was found. Tests were run with direct `python3 -m pytest ...` commands.
- Why it matters now: new contributors may not know which tests are safe, slow, provider-backed, or research-only.
- Why it may be acceptable for OSS-stage maturity: local skill repos often start without package ceremony, and direct commands currently work.
- Recommended next step: add minimal pytest markers or a tiny `pytest.ini` once maintainers agree on safe/slow/provider test categories.

### Finding 9: Documentation Drift Is Present But Localized

- Severity: Low.
- Evidence: `HOW_IT_WORKS.md:113-114` conflicts with `SKILL.md`/`docs/skill/STEPS.md` on pressure-check step ordering. `scripts/run_extract.py:141` references a non-existent `scripts/run_live_pipeline.py`.
- Why it matters now: step-order docs are used by humans to understand what is active and when.
- Why it may be acceptable for OSS-stage maturity: the authoritative skill docs are more precise, and the drift is easy to fix.
- Recommended next step: fix these references in a small docs-only PR.

## 9. God Objects, Spaghetti Paths, And Bypass Risks

### Oversized But Understandable Files

- `observatory/serve_result.py`: real bottleneck due to routing, archive loading, sidecar resolution, payload shaping, HTML fallback, SPA injection, graph endpoints, and Teacher integration in one file.
- `engine/system_b/pipeline.py`: real central orchestrator. Some size is justified because it coordinates multiple lanes and data loaders, but type re-exports and pilot helpers make it heavier than the runtime center needs to be.
- `scripts/run_pipeline.py`: real god-script because it combines provider execution, deterministic post-processing, sidecar writing, usage/cost assembly, and result writing.
- `scripts/archive_run.py`: not as large, but it mixes persistence, finalization, generated artifacts, and optional hooks.

### Real Bypass Or Footgun Risks

- `--skip-revision` does not mean "no post-pipeline provider calls." Bullshit Index still runs in `scripts/run_pipeline.py` (`scripts/run_pipeline.py:996-1074`). This is not necessarily wrong, but the name can mislead direct CLI users.
- `/tmp/lolla_latest_env.sh` can point to the most recent run, not necessarily the intended run. Wrappers mitigate this with `LOLLA_EXPECTED_RUN_ID` and path checks, but direct shell use can still be confusing (`scripts/skill/setup.sh:129-162`).
- The pipeline creates a temporary symlink so engine code can read `root/build/...` from the real `data` directory (`scripts/run_pipeline.py:438-455`). New code may not expect this data-root convention.
- Archive finalizers mutate the result payload before archive copy to apply V60/product/live hygiene (`scripts/archive_run.py:655-730`). This is intentional, but a developer comparing pre-archive and archived results needs to know it happens.
- Observatory active-run sidecar discovery prefers `/tmp/lolla_${run_id}_*` and falls back through archive paths (`observatory/serve_result.py:2067-2121`). This is useful, but it repeats artifact naming assumptions outside the main runtime scripts.

### Not A Real Bypass Risk Based On Current Evidence

- Product Delta and many evaluation/product docs are offline by design. README explicitly says Product Delta does not invoke the skill, call providers, or mutate archives (`README.md:171-172`).
- Teacher Observatory packet adaptation is read-only and carries non-claims: no product proof, no human validation, no runtime integration authorization, and no provider/model calls (`engine/system_b/mental_model_teacher_observatory_packet_adapter.py:185-188`).
- Historical V60 affordance files are not active runtime inputs when `v60_enrichment.py` requires `affordances_v60.json`.
- Large JSON data files are not spaghetti by themselves; the active pipeline loads graph/catalog data as a local substrate.

## 10. Test And Verification Assessment

### Existing Test Strengths

- Conversation runtime contract is tested: `tests/test_conversation_context.py`, `tests/test_conversation_loader.py`, and `tests/test_pipeline_context_runtime.py` passed.
- IR and provenance have direct tests: `tests/test_ir.py` passed.
- Provider/cost hardening has tests: `tests/test_model_cost_hardening.py` passed, covering default model/cost and boundary behavior.
- Provider call persistence is tested: `tests/test_pr1_boundary_call_persistence.py` passed.
- Archive identity and generated artifact policy are tested: `tests/test_archive_run_case_identity.py`, `tests/test_agent_result.py`, `tests/test_evaluation_artifact.py`, and `tests/test_reasoning_trace_archive.py` passed.
- V60 enrichment, private pre-Step-6 table, Observatory launcher, and Teacher adapter have direct tests and passed in the focused subset.
- Many product/eval tests exist, including tests that appear to enforce no-provider/no-archive-mutation claims for offline surfaces.

### Missing Boundary Tests

- A shellless end-to-end active-flow test using fake boundary clients would be valuable: extraction fixture -> pipeline result -> private sidecars -> archive generated artifacts -> Observatory case payload.
- Shell wrapper behavior is under-tested compared with Python modules. At minimum, test run ID/path guard semantics around `run_extract_step.sh` and `run_pipeline_step.sh` in a no-provider fixture mode.
- Observatory should have focused route smoke tests for `/api/cases`, `/api/case/<id>`, sidecar endpoints, and Teacher routes, especially because `observatory/serve_result.py` is actively changing.
- `scripts/run_pipeline.py --skip-revision` should have an explicit test or doc assertion that BI still runs or is intentionally governed separately.
- Archive finalizer ordering should have tests that distinguish pre-archive result input from archived finalized result.

### Brittle/Internal Tests

- The test suite appears broad and artifact-heavy. Without full execution, the main brittleness risk is not a specific failing test but the number of tests likely coupled to JSON shapes and generated fixtures.
- Tests that import from `engine.system_b.pipeline` for types that now live elsewhere will preserve compatibility pressure and import cycles. This is acceptable short-term but should be watched.

### Suggested Test Strategy

- Keep existing unit tests around deep modules: `ConversationContext`, loader, IR, provider boundary, V60, private table, archive artifacts.
- Add one or two stronger boundary tests instead of many more shallow tests:
  - No-provider runtime artifact chain with fake boundary metadata.
  - Observatory archived-case payload smoke test.
- Add markers or naming conventions for `safe`, `provider`, `slow`, `research`, and `archive-mutating` tests before the suite grows further.
- Prefer testing public artifacts and sidecar contracts over private helper internals, especially during refactors.

### Verification Run During This Audit

- Static compile succeeded for the main runtime modules.
- Focused pytest command succeeded: 139 passed in 4.88s.
- Full test suite was not run.

## 11. Refactor Candidates

### 1. Runtime Result Assembly And Sidecar Writing

- Cluster: `scripts/run_pipeline.py`, `engine/system_b/pipeline.py`, `engine/system_b/usage_summary.py`, `engine/system_b/provider_boundary_health.py`, `engine/system_b/v60_enrichment.py`, `engine/system_b/pre_step6_private_table.py`.
- Why coupled: `scripts/run_pipeline.py` owns the result schema, run-health synthesis, usage/cost collection, V60 attachment, private sidecar writes, extraction-call sidecar merge, BI/revision metadata, and final JSON write.
- Dependency category: in-process for deterministic assembly; true-external/mock for provider call metadata; local-substitutable for embeddings and data files.
- Better boundary/module direction: extract `runtime_result_builder.py`, `run_health_builder.py`, or `sidecar_writers.py` with behavior-preserving tests. Keep `scripts/run_pipeline.py` as the CLI shell.
- Test impact: fewer tests need to exercise the whole CLI to validate result assembly. Golden artifact tests can target smaller pure functions.
- Suggested first small PR: move run-health assembly into a module that accepts already-collected provider/usage structures and returns the same dictionary. Add a golden test using an existing fixture.

### 2. Observatory Case Loading And Sidecar Resolution

- Cluster: `observatory/serve_result.py`, `scripts/archive_run.py`, `engine/system_b/mental_model_teacher_observatory_packet_adapter.py`, archive sidecar schemas.
- Why coupled: the server knows archive root rules, path traversal safety, active `/tmp` sidecars, archive sidecars, case payload shape, SPA routes, and Teacher routes.
- Dependency category: in-process and local-substitutable file/archive dependencies.
- Better boundary/module direction: extract `observatory/case_store.py` and `observatory/sidecars.py` for archive root/path/sidecar resolution, then extract API payload assembly.
- Test impact: route tests can use a tiny archive fixture instead of starting the whole server for every path.
- Suggested first small PR: move `_archive_result_path_for_case_id`, `_load_case_result`, and sidecar candidate resolution into a module with direct tests.

### 3. Run Artifact Path Registry

- Cluster: `scripts/skill/setup.sh`, `scripts/skill/run_extract_step.sh`, `scripts/skill/run_pipeline_step.sh`, `scripts/run_extract.py`, `scripts/run_pipeline.py`, `scripts/archive_run.py`, `observatory/serve_result.py`, `engine/system_b/run_state.py`.
- Why coupled: all components know pieces of the `/tmp/lolla_${RUN_ID}_...` naming scheme and expected env variables.
- Dependency category: local-substitutable filesystem convention.
- Better boundary/module direction: add a small Python module that returns canonical paths for a run ID and validates run IDs. Shell helpers can call it later through a tiny CLI if needed.
- Test impact: path convention tests become centralized; sidecar additions become safer.
- Suggested first small PR: add read-only `engine/system_b/run_artifacts.py` with no behavior changes, then migrate one Python caller.

### 4. Pipeline Shared Types And Import-Cycle Reduction

- Cluster: `engine/system_b/pipeline.py`, `audit_assembly.py`, `boundary_tracing.py`, `activation_matcher.py`, `novelty_scorer.py`, `companion_selection.py`, `telemetry.py`, pass runners, tests.
- Why coupled: downstream modules import pipeline types or compatibility exports from `pipeline.py`; pass runners use type-checking imports back to `pipeline.py`; lazy imports hide but do not remove the dependency shape.
- Dependency category: in-process.
- Better boundary/module direction: move shared dataclasses/protocols into `pipeline_types.py` or `runtime_types.py`, then preserve `pipeline.py` re-exports temporarily.
- Test impact: import graph becomes easier to reason about; fewer accidental runtime imports of the full pipeline.
- Suggested first small PR: move one low-risk shared type or protocol and update imports in modules already using `TYPE_CHECKING`.

### 5. Archive Generated Artifact Writer

- Cluster: `scripts/archive_run.py`, `agent_result.py`, `evaluation.py`, `reasoning_trace.py`, graph survival writer, Decision Work hook.
- Why coupled: archive script is responsible for both copying source artifacts and generating derived audit/custody artifacts.
- Dependency category: local-substitutable filesystem and in-process artifact builders.
- Better boundary/module direction: extract `archive_generated_artifacts.py` that receives archive paths and writes derived artifacts, leaving case creation/copying in the script.
- Test impact: generated artifact policies can be tested without invoking full archive flow.
- Suggested first small PR: move only generated artifact orchestration after the core copies, preserving output paths and failure behavior.

### 6. Offline/Product Connectedness Index

- Cluster: `docs/conversation-understanding`, `docs/evals`, `docs/product`, `scripts/evals`, `engine/system_b/decision_*`, `reviews`, `plans`.
- Why coupled: many files describe or test product/review behavior that is intentionally disconnected from runtime, but the status is not discoverable from a single place.
- Dependency category: documentation/process boundary; some local-substitutable scripts.
- Better boundary/module direction: maintain a status table with active runtime, active review surface, offline tool, docs-only, dormant/default-off, historical, and unknown.
- Test impact: low direct test impact, high contributor-orientation value.
- Suggested first small PR: docs-only connectedness map seeded from this audit.

## 12. OSS-Pragmatic Roadmap

### Next 1-2 PRs

- Fix the localized docs drift: update `HOW_IT_WORKS.md` step ordering around pressure-check state and remove/update the stale `scripts/run_live_pipeline.py` comment in `scripts/run_extract.py`.
- Add a maintained connectedness map under `docs/architecture/` or `docs/audits/` that labels active runtime, offline tooling, review surface, docs-only, dormant/default-off, historical, and unknown components.
- Extract one small helper from a bottleneck file. Best candidates are Observatory sidecar/case resolution or `scripts/run_pipeline.py` run-health assembly.
- Add one Observatory route smoke test if current branch work continues in `observatory/serve_result.py`.

### Next 1-2 Weeks

- Add a no-provider integration test that exercises the active artifact chain with fake boundary metadata.
- Split `observatory/serve_result.py` into at least one file-backed helper module for archive/case/sidecar loading.
- Split `scripts/run_pipeline.py` result assembly or sidecar writing into one or two pure modules.
- Add minimal pytest markers or documented commands for safe, slow, provider, research, and archive-mutating tests.
- Surface `scripts/lolla_doctor.py` more prominently as a preflight before live provider-cost runs.

### Later, Only If Project Grows

- Package the runtime as an installable Python package if external contributors need repeatable setup.
- Create formal ports/adapters around providers, embeddings, and archive storage only after the current local boundaries become limiting.
- Generate the connectedness matrix from a manifest if manual docs drift becomes recurring.
- Bring the Observatory SPA source/build process into this repo or document the external build provenance more formally.
- Add import-cycle checks as a soft architecture test after shared types are moved.

### Things Not Worth Doing Yet

- Full rewrite of the runtime.
- Dependency injection everywhere.
- Microservices or remote archive storage.
- Replacing the local JSON/archive model with a database.
- Enterprise observability or compliance machinery.
- Deleting historical compiled affordance files or review artifacts merely because they are not runtime-active.
- Converting every script into a package/module before a concrete development bottleneck appears.

## 13. Open Questions For Maintainers

- Should Bullshit Index be considered part of the default required audit, or should it have a separately named mode/receipt because it still calls providers when `--skip-revision` is set?
- Are the promoted authority/stress/overoptimism pilot bridges intended to become runtime features, or should they remain default-off research paths?
- Is Gemini CLI support a maintained alternative provider, or historical experimentation?
- Should V60 historical affordance versions remain in the public runtime repo as lineage, or move to a research/archive area?
- Is the Observatory SPA source intentionally external long-term, or should this repo gain a reproducible build path?
- Which archive artifact is intended to be the most stable public contract for downstream tools: `agent_result`, `evaluation`, `reasoning_trace`, manifest, or the raw result?
- Should `lolla_doctor` become a documented first step before live runs?
- What is the expected contributor workflow for tests: focused safe subset, full local suite, or CI-only full suite?
- Are Product Delta and Decision Work expected to remain offline/review surfaces, or is runtime integration planned?

## Appendix A: Commands Run

```bash
git status --short --branch
```

Summary: branch context should be rechecked from current working state before execution; this audit snapshot is not a runtime proof and is intended as an operations map rather than a live status console.

```bash
git log --oneline -8
```

Summary: recent work since this refresh remains focused on Observatory product-surface clarity, graph-scope accounting, and review/documentation alignment.

```bash
find . -maxdepth 2 -type f \( -name 'pyproject.toml' -o -name 'setup.py' -o -name 'setup.cfg' -o -name 'pytest.ini' -o -name 'requirements.txt' -o -name 'Makefile' -o -name 'package.json' \)
```

Summary: no shallow root packaging/test harness markers found.

```bash
find . -maxdepth 1 -type d -print
find . -maxdepth 2 -type f | sed 's#^\./##' | sort | head
```

Summary: identified top-level repo areas: `data`, `docs`, `engine`, `observatory`, `plans`, `references`, `research`, `reviews`, `scripts`, `tasks`, `tests`.

```bash
rg --files | awk 'BEGIN{FS="/"} NF>1{count[$1]++} NF==1{count["."]++} END{for (d in count) print count[d], d}' | sort -nr | head -40
```

Summary: largest file-count areas were `research`, `data`, `tests`, `docs`, `engine`, `scripts`, `reviews`.

```bash
rg --files | awk 'match($0,/\.([^.\/]+)$/ ,m){count[m[1]]++} END{for (e in count) print count[e], e}' | sort -nr | head -40
```

Summary: dominant extensions were `.json`, `.md`, local `.pyc`, `.py`, `.txt`.

```bash
du -sh data research tests engine scripts docs observatory reviews 2>/dev/null
```

Summary: `data` about 325 MB; `research` about 49 MB; `tests` about 30 MB; `engine` about 7 MB; `scripts` about 6.3 MB.

```bash
find engine scripts tests observatory -name '*.py' | wc -l
find tests -name 'test_*.py' | wc -l
```

Summary: about 728 Python files under core/test areas; 401 pytest files.

```bash
find . -name '*.py' -not -path './.git/*' -print0 | xargs -0 wc -l | sort -nr | head -30
```

Summary: largest active Python files include `observatory/serve_result.py`, `engine/system_b/pipeline.py`, `scripts/run_pipeline.py`, and `scripts/archive_run.py`.

```bash
rg -n "run_pipeline|run_extract|archive_run|launch_observatory|ConversationContext|SystemBPipeline|OpenRouter|OPENROUTER|OPENAI|Product Delta|Decision Work|Teacher|Observatory" SKILL.md README.md HOW_IT_WORKS.md docs scripts engine observatory tests
```

Summary: used for runtime/documentation tracing and drift checks.

```bash
rg --files | rg 'run_live_pipeline\.py$'
rg -n "run_live_pipeline" .
```

Summary: no `scripts/run_live_pipeline.py` file found; only stale reference observed in `scripts/run_extract.py`.

```bash
find data -maxdepth 3 -type f -name 'munger_routing_table.json' -print
```

Summary: no routing overlay file found; code treats it as optional fallback.

```bash
git ls-files '*__pycache__*' '*.pyc' | wc -l
rg -n "__pycache__|\*.pyc|pyc" .gitignore
```

Summary: local bytecode/cache files are ignored and not tracked.

```bash
python3 -m py_compile scripts/run_extract.py scripts/run_pipeline.py scripts/archive_run.py observatory/serve_result.py scripts/skill/launch_observatory.py engine/system_b/pipeline.py engine/system_b/conversation_context.py engine/system_b/conversation_loader.py engine/system_b/ir_constructor.py engine/system_b/boundary_provider.py engine/system_b/agent_result.py engine/system_b/evaluation.py engine/system_b/reasoning_trace.py engine/system_b/v60_enrichment.py engine/system_b/pre_step6_private_table.py engine/system_b/mental_model_teacher_observatory_packet_adapter.py
```

Summary: succeeded with no output.

```bash
python3 -m pytest -q tests/test_conversation_context.py tests/test_conversation_loader.py tests/test_ir.py tests/test_pipeline_context_runtime.py tests/test_model_cost_hardening.py tests/test_pr1_boundary_call_persistence.py tests/test_archive_run_case_identity.py tests/test_agent_result.py tests/test_evaluation_artifact.py tests/test_reasoning_trace_archive.py tests/test_v60_enrichment_runtime.py tests/test_pre_step6_private_table.py tests/test_observatory_launcher.py tests/test_mental_model_teacher_observatory_packet_adapter.py
```

Summary: `139 passed in 4.88s`.

```bash
python3 -m pytest -q tests/test_conversation_context.py tests/test_conversation_loader.py tests/test_ir.py tests/test_pipeline_context_runtime.py tests/test_model_cost_hardening.py tests/test_pr1_boundary_call_persistence.py tests/test_archive_run_case_identity.py tests/test_agent_result.py tests/test_evaluation_artifact.py tests/test_reasoning_trace.py tests/test_v60_enrichment_runtime.py tests/test_pre_step6_private_table.py tests/test_observatory_launcher.py tests/test_mental_model_teacher_observatory_packet_adapter.py
```

Summary: mistaken command; `tests/test_reasoning_trace.py` does not exist, so pytest exited with collection error 4 and no tests ran. Corrected command above used `tests/test_reasoning_trace_archive.py`.

```bash
python3 - <<'PY'
import ast
from pathlib import Path
root = Path('engine/system_b')
module_names = {p.stem for p in root.glob('*.py')}
graph = {}
for path in root.glob('*.py'):
    name = path.stem
    tree = ast.parse(path.read_text())
    deps = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.level == 1 and node.module:
            dep = node.module.split('.')[0]
            if dep in module_names:
                deps.add(dep)
    graph[name] = deps

index = 0
stack = []
indices = {}
lowlinks = {}
on_stack = set()
sccs = []

def strongconnect(v):
    global index
    indices[v] = index
    lowlinks[v] = index
    index += 1
    stack.append(v)
    on_stack.add(v)
    for w in graph[v]:
        if w not in indices:
            strongconnect(w)
            lowlinks[v] = min(lowlinks[v], lowlinks[w])
        elif w in on_stack:
            lowlinks[v] = min(lowlinks[v], indices[w])
    if lowlinks[v] == indices[v]:
        comp = []
        while True:
            w = stack.pop()
            on_stack.remove(w)
            comp.append(w)
            if w == v:
                break
        if len(comp) > 1:
            sccs.append(sorted(comp))

for node in sorted(graph):
    if node not in indices:
        strongconnect(node)
print('modules', len(graph))
print('cycles', len(sccs))
for comp in sccs:
    print(','.join(comp))
PY
```

Summary: AST import graph check over `engine/system_b/*.py`; output was `modules 170`, `cycles 3`, with cycles in `companion,companion_routing`; a large `pipeline`/routing/telemetry/pass-runner cycle; and `compilation_bundle,operational_curation`.

Targeted file reads used `sed -n`, `nl -ba`, and `rg -n` against:

- `SKILL.md`
- `docs/skill/STEPS.md`
- `README.md`
- `HOW_IT_WORKS.md`
- `scripts/skill/setup.sh`
- `scripts/skill/run_extract_step.sh`
- `scripts/skill/run_pipeline_step.sh`
- `scripts/skill/launch_observatory.py`
- `scripts/run_extract.py`
- `scripts/run_pipeline.py`
- `scripts/archive_run.py`
- `scripts/lolla_doctor.py`
- `engine/system_b/pipeline.py`
- `engine/system_b/pass1_runner.py`
- `engine/system_b/pass2_runner.py`
- `engine/system_b/conversation_context.py`
- `engine/system_b/conversation_loader.py`
- `engine/system_b/ir_constructor.py`
- `engine/system_b/boundary_provider.py`
- `engine/system_b/v60_enrichment.py`
- `engine/system_b/pre_step6_private_table.py`
- `engine/system_b/agent_result.py`
- `engine/system_b/evaluation.py`
- `engine/system_b/reasoning_trace.py`
- `engine/system_b/lolla_doctor.py`
- `engine/system_b/mental_model_teacher_observatory_packet_adapter.py`
- `observatory/serve_result.py`

## Appendix B: File/Module Index

| File / module | Purpose |
|---|---|
| `SKILL.md` | User-facing Lolla skill contract, trigger guidance, setup preamble, and high-level step rules. |
| `docs/skill/STEPS.md` | Detailed operational step flow for capture, extraction, pipeline, revision, pressure state, Observatory, and archive. |
| `README.md` | Install/setup, directory map, cost estimates, product/offline caveats, and project overview. |
| `HOW_IT_WORKS.md` | Narrative architecture overview; mostly useful but contains pressure-check step drift. |
| `scripts/skill/setup.sh` | Runtime setup, env loading, run ID creation, `/tmp` env file and log initialization. |
| `scripts/skill/run_extract_step.sh` | Guarded wrapper around extraction step. |
| `scripts/skill/run_pipeline_step.sh` | Guarded wrapper around main pipeline step. |
| `scripts/skill/launch_observatory.py` | Local Observatory process launcher with readiness check. |
| `scripts/run_extract.py` | OpenRouter extraction CLI with local capture validation, quote validation, and usage sidecar. |
| `scripts/run_pipeline.py` | Main runtime CLI orchestrating pipeline execution, BI, V60, private sidecars, usage, run health, and result write. |
| `scripts/archive_run.py` | Archive persistence, case identity, finalization, generated artifacts, and optional Decision Work hook. |
| `scripts/lolla_doctor.py` | Read-only local preflight CLI. |
| `engine/system_b/pipeline.py` | Core System B pipeline orchestration and compatibility hub. |
| `engine/system_b/pass1_runner.py` | Extracted pass 1 runner for pressure/tendency calls. |
| `engine/system_b/pass2_runner.py` | Extracted pass 2 runner for deeper pressure analysis. |
| `engine/system_b/conversation_context.py` | Canonical frozen runtime conversation contract. |
| `engine/system_b/conversation_loader.py` | Loader from extraction/transcript artifacts to `ConversationContext`. |
| `engine/system_b/ir_constructor.py` | Provenance-bearing conversation IR construction. |
| `engine/system_b/ir.py` | IR dataclasses and supporting structures. |
| `engine/system_b/boundary_provider.py` | OpenRouter/OpenAI-compatible/Gemini provider boundary clients and call metadata. |
| `engine/system_b/usage_summary.py` | Provider usage and run/cost aggregation helpers. |
| `engine/system_b/pricing.py` | Pricing/cost support for usage summaries. |
| `engine/system_b/provider_boundary_health.py` | Health/custody checks around provider boundary behavior. |
| `engine/system_b/v60_enrichment.py` | Runtime/product V60 affordance enrichment. |
| `engine/system_b/pre_step6_private_table.py` | Private support table and portfolio generation for Step 6 answer revision. |
| `engine/system_b/agent_result.py` | Conservative machine-readable agent result artifact. |
| `engine/system_b/evaluation.py` | Run-readiness evaluation artifact with no advice-quality judge claim. |
| `engine/system_b/reasoning_trace.py` | Local reasoning trace artifact describing artifact custody and support chain. |
| `engine/system_b/lolla_doctor.py` | Read-only diagnostics report builder. |
| `engine/system_b/mental_model_teacher_observatory_packet_adapter.py` | Read-only Teacher Observatory response adapter with explicit non-claims. |
| `observatory/serve_result.py` | Zero-dependency local Observatory server and API surface. |
| `observatory/build/` | Compiled SPA assets consumed by the local server. |
| `scripts/evals/` | Offline evaluation/product/review CLIs. |
| `scripts/research/` | Offline research/generation scripts. |
| `data/knowledge_graph.json` | Active knowledge graph data. |
| `data/relationship_graph.json` | Active relationship graph data. |
| `data/embeddings.db` | Optional/local embedding retrieval substrate. |
| `data/curated/` | Curated compiled chunks and reasoning signal data. |
| `data/compiled/model_affordances/affordances_v60.json` | Active V60 model affordance artifact. |
| `data/compiled/model_affordances/affordances_v1-v59.json` | Historical/offline affordance lineage. |
| `docs/product/` | Product plans and prototypes, mostly docs-only or review-surface context. |
| `docs/evals/` | Evaluation docs and offline methodology. |
| `docs/conversation-understanding/` | Conversation-understanding design/research docs. |
| `reviews/` | Review artifacts, including synthetic and codex-assisted reviews. |
| `plans/` | Implementation plans and PR slice notes. |
| `research/` | Research artifacts and generated data, not normal runtime. |
