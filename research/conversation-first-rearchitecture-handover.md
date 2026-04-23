# Conversation-First Rearchitecture — Handover

**Authored:** 2026-04-23
**Status:** plan complete; execution not started
**Primary context artifact:** `research/full-system-audit-2026-04-23.md` (653-line architectural audit — read FIRST)

## Who this is for

A cold-start session or new developer picking up the lolla-skill work. If you're reading this, you may not have access to the conversation that produced it. Everything you need should be here or linked from here.

## TL;DR

The lolla pipeline has a structural bottleneck: a legacy data contract (`CritiqueRequest(query: str, vanilla_answer: str)`) that collapses rich conversation extraction into two flat strings before the 4 lanes consume them. This contract is a leftover from the System B era (pre-skill, single-shot query+answer auditing). The skill evolved into conversation-first capture and extraction, but the engine still assumes query+vanilla shape.

**The work ahead is an architectural rearchitecture to make the system conversation-first end-to-end.** Stop collapsing. Give lanes the rich structure they need. Remove the legacy shape.

## Strategic context — where we are and why

### What's shipped
- 10-case synthetic diagnostic corpus at `research/test-cases/` — conversations covering professional/personal/messy/clean variance
- 3 extraction improvements (PR #1 terse `constraint`, PR #4a `decision_situation`, PR #4b `original_framing`)
- Gate fix (PR #11 — strategic gate now includes personal decisions)
- Embedding-cosine metric infrastructure in `scripts/stability_check.py`
- Full system audit (`research/full-system-audit-2026-04-23.md`)
- **Phase 1 (PR #14, merged 2026-04-24)** — conversation-first contract scaffolding:
  - `engine/system_b/conversation_context.py` — `ConversationContext` + `Turn` + `LiveConstraint` + `DroppedThread` + `ExtractionPayload` dataclasses
  - `engine/system_b/conversation_loader.py` — `load_conversation_context(extraction_path, conversation_path)` builds the context from on-disk artifacts
  - Shim in `SystemBPipeline.run()` — accepts `CritiqueRequest | ConversationContext`; `_context_to_critique()` converts new shape to legacy one so lane code is untouched. Marked for removal in Phase 3.
  - `scripts/run_pipeline.py --new-contract` flag routes through the new path
  - `scripts/compare_outputs.py` — compares 6 meaningful fields between two result.json files (future regression tool)
  - `scripts/phase1_equivalence_check.py` — verifies shim correctness at the `CritiqueRequest` boundary
  - 41 new tests (164 total, zero regression); 10/10 corpus cases bit-identical between shim and legacy mapping
  - Evidence: `research/test-cases/phase1-equivalence-2026-04-24/shim-equivalence-report.md`
  - HOW_IT_WORKS §Step 3 has a "Conversation-first contract (Phase 1)" subsection
- **Phase 2a (PR #15, merged 2026-04-23)** — Lane 3 (Frame Pressure) migrated to `ConversationContext`. Controlled Marcus comparison shows qualitative audit-quality shift: new path grounds frame evidence in verbatim user words (`"Giving away 15% feels like giving away something I earned"`); old path grounds in extractor paraphrases. Fixed a production bug on `real_estate` (old path produced empty Lane 3 cards 2 of 3 runs). 10-case aggregate: +22% elements, drop rate 0.069 → 0.000, zero regressions. Artifacts: `research/test-cases/phase2a-marcus-controlled-comparison-2026-04-23/` and `research/test-cases/phase2a-lane3-equivalence-2026-04-23/`.

### What's paused (and why)
- PRs #1b, #2, #3, #5 — all hit prompt saturation (monolithic extraction prompt can't absorb more rules without polluting adjacent fields). Deferred pending architectural fix.
- Track A (split extraction into specialist calls per field) — proposed as the structural fix for saturation. **Deferred further pending this rearchitecture.** Reason: the bottleneck isn't "we need more extraction output"; it's "lanes discard most of what we extract." Producing more in a broken contract would be premature.

### Why we're changing direction
We spent a work cycle shipping extraction improvements, then hit a wall. Investigating, we found that the wall isn't an extraction problem — it's a contract problem. Each extraction field we tried to add (canonical_key, Position object, move_type enum) failed because prompt-saturation testing showed:

1. The monolithic extraction prompt can't absorb new rules without polluting adjacent fields.
2. EVEN IF Track A fixed saturation, the richer extraction would still be collapsed into `query + vanilla_answer` before lanes see it.
3. So: fixing extraction in the current architecture = polishing upstream data that gets thrown away downstream.

The real fix is upstream of extraction: rearchitect the lane-input contract to be conversation-first.

### What we decided (user + technical lead)
1. **Merge PR #13 as-is** (the shipped 2026-04-22/23 work is solid; stop stacking).
2. **Freeze further extraction work** until the lane contract is redesigned.
3. **Rebuild conversation-first before investing more in any upstream layer.**
4. **Track A stays deferred.** If during lane migration we find a specific lane needs structure we can't pull from current extraction, we add a Track A call for THAT field only. Per-field, on-demand, not preemptive.
5. **The 2200-line `engine/system_b/pipeline.py`** will be addressed as part of the rearchitecture, but NOT first-thing. Let lane migrations reveal which parts of pipeline.py are essential vs vestigial, then refactor.

## The plan

### Phase 0 (prerequisite) — Merge PR #13

Before any new work:
- Review PR #13 on GitHub (`https://github.com/gofarrrr/lolla-skill/pull/13`)
- Merge to main
- Delete the branch
- Main now has: terse-form extraction rules + embedding metric infra + gate fix + 10-case corpus + full audit

### Phase 1 — Holistic contract-redesign PR

**Purpose:** replace `CritiqueRequest(query, vanilla_answer)` with a richer `ConversationContext` shape, without changing any lane behavior yet. Lanes still produce identical output. New infrastructure sits alongside the legacy path.

**Task file:** `tasks/tasks-conversation-first-phase-1-contract.md`

**Scope:**
1. Define `ConversationContext` dataclass (turns + extraction + metadata)
2. Build it in `run_pipeline.py` alongside the old `CritiqueRequest`
3. Add pipeline entry-point shim: `SystemBPipeline.run()` accepts either shape, internally delegates to existing lane code
4. Outcome-measurement scaffolding: `compare_outputs.py` + golden-case protocol
5. Documentation updates (HOW_IT_WORKS.md new architecture section)

**Acceptance gate:** all existing lane outputs bit-identical on the 10-case corpus between old and new paths. No behavior change, just new infrastructure available.

**Size:** 1-2 weeks of focused work. Low-medium risk (additive, shim-based).

**Explicitly out of scope:**
- No lane prompt changes
- No LLM call changes
- No Claude orchestration changes (SKILL.md Steps 1, 4, 6-9 untouched)
- No extraction changes (6 fields stay as-is)
- No `CritiqueRequest` removal (stays during migration, marked for later deprecation)

### Phase 2 — Lane-by-lane migration (4 PRs)

Once Phase 1 lands, each lane gets its own migration PR. Recommended order:

- **PR 2a: Lane 3 (Frame Pressure)** — smallest, most self-contained. Gets access to actual first user turn instead of pre-collapsed `original_framing`. Best first migration.
- **PR 2b: Lane 4 (Structural Coverage)** — also self-contained, informative-only (doesn't affect other lanes).
- **PR 2c: Lane 1 (Structural Pressure)** — biggest, most complex. Pass 1 (6 clusters) + Pass 2 (per-tendency) both need rewiring.
- **PR 2d: Lane 2 (Companion)** — last; currently does its own extraction from vanilla_answer; may need least change or may be rebuilt entirely.

Each PR: rewrite lane prompts to use `ConversationContext`, measure old-path vs new-path on 10-case corpus, ship if new-path is ≥ old-path on whatever quality bar is agreed.

### Phase 3 — Cleanup PR

After all 4 lanes migrated:
- Remove `CritiqueRequest`
- Remove `_map_to_critique_request`
- Remove legacy shims
- Update `testing_harness.py` to emit new shape

### Phase 4 — pipeline.py restructuring

The 2200-line `engine/system_b/pipeline.py` gets addressed here. By this point, lane migrations have shown which parts are essential vs vestigial. Split into smaller modules — orchestration, triage, routing, delta assembly — roughly following the lane structure. Don't do this before Phase 3; you'd preserve structure we're removing.

## Legacy to remove

Named targets for deprecation during this rearchitecture:

| Legacy | Why it's legacy | Removal phase |
|---|---|---|
| `CritiqueRequest(query, vanilla_answer)` | System B era single-shot assumption | Phase 3 (after all lanes migrated) |
| `_map_to_critique_request` | The collapsing function itself | Phase 3 |
| `synthesized_position: str` | Single final-position assumption; should probably be position trajectory | Phase 2c (when Lane 1 migrates) |
| Step 5 placeholder | Vestige of earlier design | Phase 3 cleanup |
| Pilot bridges as config-flag code paths | Experimental code in hot path | Phase 4 (during pipeline.py split) |
| ~20 per-tendency packet adapters | Copy-paste-variant files | Phase 4 (consolidate into data-driven generic adapter) |
| 2200-line pipeline.py | Cumulative complexity | Phase 4 |

## Constraints — what NOT to do

Hard rules for anyone picking up this work:

1. **Don't stack on PR #13.** Merge it first. Start fresh from main.
2. **Don't do Track A preemptively.** Only if a specific lane migration reveals a specific missing field.
3. **Don't break the current `/lolla` skill during migration.** Shim must keep old path working. Each lane PR is independently revertible.
4. **Don't ship a lane migration without outcome measurement.** Old-path vs new-path comparison on the 10-case corpus is the gate.
5. **Don't rewrite pipeline.py before lane migrations.** You'd preserve structure we should remove.
6. **Don't treat this as cosmetic tech-debt cleanup.** It's a product-architecture change. The code is generally OK; the contract is what matters.
7. **Don't add new features during the rearchitecture.** Scope discipline matters; features land after Phase 3.

## The 2200-line pipeline.py problem

`engine/system_b/pipeline.py` is the single biggest code complexity in the system. You'll need to understand it to do Phase 1 properly. Strategy for dealing with it:

### Step 1: Map it before touching
Don't try to read it top to bottom. Map the structure:

```bash
# Get a section outline
grep -n "^class \|^def \|^    def \|# ---" engine/system_b/pipeline.py
```

The shape you'll find (from the audit):
- Top: imports (~100 lines)
- Dataclasses: `CritiqueRequest`, `PipelineConfig`, `BoundaryCallTrace`, `PromotedBundleTrace`, `TriggeredTendency`, `AuditTrace`, `DeltaFinding`, `CompoundGroup`, `DeltaCard`, `PipelineResult`, `CompanionRunResult` (~200 lines of dataclasses — the data model)
- `SystemBPipeline` class: `__init__`, `load`, `load_live`, `run` (the main orchestration)
- Many module-level helper functions at the bottom (~1000+ lines): `_run_pass1_clusters_parallel`, `_embedding_tendency_signal`, `_select_triggered_tendencies`, `_run_pass2_parallel`, `_build_lane1_relevance_scores`, `_route_deep_check_results_with_optional_tiebreaker`, `_assemble_delta_card`, `_build_compound_groups`, `_build_promoted_*_results`, `_run_companion`, `_run_frame_pressure`, `_run_structural_coverage`, various serializers

### Step 2: Identify the shim points
The new-path shim lands in `SystemBPipeline.run()`. That method is the SINGLE entry point to the whole pipeline. Adding an overload that accepts `ConversationContext` and internally builds `CritiqueRequest` (for legacy lanes) or delegates to per-lane new-path methods (once they exist) is the minimum change.

### Step 3: Don't refactor during Phase 1
Resist the urge. The file is complex but working. Phase 1 adds a new entry point + data class; it doesn't restructure the existing code. Phase 4 splits it after lane migrations tell us what the structure should be.

### Step 4: Phase 4 split strategy
When you get there, split roughly along these lines:
- `orchestration.py` — the `SystemBPipeline` class + `run()` method
- `lane1_structural_pressure.py` — Pass 1, Pass 2, routing, delta assembly
- `lane_orchestration_helpers.py` — the parallel execution + embedding promotion helpers
- `data_model.py` — dataclasses (or split further if needed)
- Telemetry/observability already in `telemetry.py`

Exact split depends on what Phase 2 revealed. Don't commit to the split upfront.

## Measurement approach

You need two measurement layers:

### Layer 1: bit-identical invariance (Phase 1 acceptance)
The 10-case corpus at `research/test-cases/case_*_conversation.txt`. Run the pipeline through both the old path and the new path; outputs must be bit-identical (or diff-equivalent if serialization differs). Tooling needed: `scripts/compare_outputs.py` — takes two result.json files, diffs meaningful fields, reports match/mismatch.

### Layer 2: output quality (Phase 2 acceptance per lane)
For each lane migration, run on the 10-case corpus:
- Compare old-path vs new-path outputs
- Human-read a sample (you or the user) and call whether quality improved
- Don't ship if outputs qualitatively worsened

This is the outcome-measurement gap the audit identified. Phase 1 builds the scaffolding; Phase 2 uses it per-lane.

### 10 cases, quick reference

From `research/test-cases/`:
- `oncologist` — medical/pharma, 9 turns, moderate complexity
- `parenting_teen` — personal/family, 12 turns, high emotion
- `startup_pivot` — business, 7 turns, clean
- `real_estate` — personal/financial, 6 turns, sparse info
- `multi_offer` — career, 15 turns, multi-thread
- `friendship_money` — personal, 10 turns, frustration escalation
- `whistleblower` — legal/ethical, 14 turns, dense
- `phd_research` — academic, 22 turns (longest)
- `user_has_plan` — career, 8 turns, user has decided
- `messy_three_problems` — multi-domain, 11 turns, topic-jumping

Plus 9 Marcus conversation captures at `/tmp/lolla_2026042*T*_conversation.txt` for continuity with prior extraction work.

## Documentation inventory

Everything a new session should read, in priority order:

### Required
1. **This handover** — `research/conversation-first-rearchitecture-handover.md`
2. **Full system audit** — `research/full-system-audit-2026-04-23.md` (especially sections 2, 3, 7, 10, 12)
3. **Phase 1 task file** — `tasks/tasks-conversation-first-phase-1-contract.md`
4. **pipeline.py structural map** — `research/pipeline-py-structural-map.md` (produced by Explore sub-agent 2026-04-23; ~500 lines, navigation guide for the 2200-line monolith, includes load-bearing vs extractable classification + shim injection points)

### Recommended
4. **Pipeline architecture overview** — `HOW_IT_WORKS.md` §Step 3 onward
5. **Skill orchestration** — `SKILL.md` (understand Claude's role vs Python pipeline)
6. **Extraction contract** — `research/extraction-contract-observations-2026-04-22.md` (the normative spec for the 6 fields)
7. **Test corpus summary** — `research/test-cases/CORPUS-SUMMARY-2026-04-23-v2.md`

### For context (not required)
8. **Prior roadmap** — `research/extraction-contract-roadmap.md` (extraction work, mostly paused now)
9. **Cycle-1 handover** — `research/llm-decomposition-handover.md` (historical context on why extraction was originally deferred)
10. **Per-PR task files** — `tasks/tasks-extraction-contract-phase-*.md` (historical, extraction work)

### Code to read
11. **`scripts/run_pipeline.py`** — entry point, ~591 lines
12. **`engine/system_b/pipeline.py`** — the beast, ~2200 lines (map it, don't try to read linearly)
13. **`scripts/run_extract.py`** — extraction (~711 lines, well-understood from prior work)
14. **`engine/system_b/companion_routing.py`** — Lane 2 main (~1050 lines)
15. **`engine/system_b/frame_pressure.py`** — Lane 3 main (~580 lines)
16. **`engine/system_b/structural_coverage.py`** — Lane 4 main
17. **`engine/system_b/prompts.py`** — Pass 1 prompts (family clusters)

## Known constraints and trade-offs

These are points that a new session should know about:

1. **The skill has two execution contexts (Claude + Python).** Any change that affects both needs coordination. `SKILL.md` is Claude's contract; scripts are Python's. Don't break either.

2. **The engine uses a knowledge graph with implicit schema** (`data/knowledge_graph.json`). 222 models + 25 tendencies + 15 dimensions. No JSON Schema. The code uses `.get(key, default)` extensively. Be careful when touching graph consumers.

3. **Embedding is optional.** If `OPENAI_API_KEY` is missing, the pipeline runs with deterministic routing only. Any change must preserve this fallback.

4. **OpenRouter is the primary LLM provider** (via `x-ai/grok-4.1-fast`). Different from Claude (which is the orchestrator). Cost: ~$0.05-0.15 per full run.

5. **The 10-case corpus is synthetic.** It's useful for regression testing but doesn't prove generalization to real conversations. The roadmap explicitly notes the "graduation to 5+ distinct real cases" gap.

6. **Tests mock the LLM.** Unit tests verify parsing + validation. Real LLM behavior variance isn't covered in the test suite. Mode C drift harness is the closest thing to an LLM-behavior regression test, and it's diagnostic only.

7. **`pipeline.py` has multiple orchestration branches** (triggered_tendencies vs not, enable_deep_checks vs not, etc.). Any change to `run()` needs to handle all paths.

8. **Pilot bridges** (authority, stress, overoptimism) are partial implementations. Don't remove them; they're referenced in tests and may ship eventually.

## Obstacles to think about

- **Scope creep.** The rearchitecture is tempting to use as "while we're in there, let's fix X" for many X. Resist. Phase 1 is contract + scaffolding. Additional fixes come later.
- **Regression invisibility.** Without outcome measurement in Phase 1, a lane migration could subtly degrade quality and nobody would notice. This is why outcome measurement is scoped into Phase 1.
- **Legacy gravity.** The pipeline was designed around `CritiqueRequest`. The temptation is to keep it "just in case." At Phase 3, actually remove it. Dead code is a cost.
- **Branch rot.** PR #13 was large and long-lived. Don't let this PR grow the same way. Ship Phase 1 in 1-2 weeks or reconsider scope.
- **The 2200-line file.** Don't start Phase 4 before Phase 3 is done. Tempting to "clean as you go"; don't.

## What the user wants at the end

Direct quote from the conversation that produced this handover:

> "At the end of the day I want a system that is conversation-first and does not have all those legacy elements that are not useful, and later on I can think about really... We want this system to be in a condition where we can measure it based on these 10 use cases. It should run Lola as a skill and we should also think about rearranging or improving the codebase so it works better."

Three end-state properties to preserve in every decision:

1. **Conversation-first end-to-end** — no `query + vanilla_answer` collapse anywhere
2. **Measurable** — 10-case corpus is the regression surface; outcome comparison is the quality bar
3. **Runs as `/lolla` skill** — the user-facing skill behavior stays intact through the migration

## Kickoff for the next session

See: `research/conversation-first-rearchitecture-kickoff.md`

Drop that prompt into the new session. It points here.

---

## Revision history

- **2026-04-23** — authored by Opus 4.7 at the end of a multi-session cycle that shipped extraction improvements, hit saturation, diagnosed the contract bottleneck, and decided to rearchitect.
