# Lolla - How It Works

Last checked against `SKILL.md` and runtime entry points: 2026-05-22.

This file is now the short map. The old monolith was over 1,000 lines, which made it a poor entry point for agents. Keep this file small and link to focused detail files instead of expanding it back into a second SKILL.md.

## Current Runtime In One Page

Lolla is a conversation-aware reasoning audit skill. It captures the current conversation, extracts decision structure, runs four external audit lanes through OpenRouter against a curated 222-model reasoning substrate, and then asks the orchestrator to reconsider its own earlier advice using the persisted pressure.

The executable source of truth is still `SKILL.md`. This document explains the architecture and flow; it should not duplicate every operator instruction.

Live `/lolla` flow:

1. Resolve the skill directory, API keys, bundled engine/data, run id, and live transcript file.
2. Capture the conversation into `/tmp/lolla_<run_id>_conversation.txt`.
3. Run `scripts/run_extract.py` to produce `/tmp/lolla_<run_id>_extraction.json`, with capture validation and quote verification.
4. Render the readback and audit promise in chat.
5. Run `scripts/run_pipeline.py --skip-revision` with the extraction and conversation files.
6. Pipeline builds `ConversationContext`, constructs `ConversationIR`, and runs four lanes: structural pressure, model companion, frame pressure, and structural coverage.
7. `run_pipeline.py` attaches the Bullshit Index, usage summary, run health, and default-on V60 private enrichment. Optional pre-Step-6 shadow portfolio remains default-off and shadow-only.
8. The orchestrator renders the strongest counterargument, then writes the updated position.
9. Step 6b persists `revised_answer` and validates the V60 consideration ledger before any pressure-check agents are launched.
10. Pressure-check agents run only after Step 6b succeeds; Step 8 persists the pressure check and auxiliary token usage.
11. Step 8c persists memo-note fields and renders the deterministic memo.
12. Step 9 finalizes V60 and live-output hygiene, opens the Observatory, and Step 10 archives the 12 core artifacts under `~/.local/share/lolla/runs/`.

## Detail Files

Read only the detail file that matches the question:

| File | Use it for |
|---|---|
| [Problem and Thesis](docs/how-it-works/problem-and-thesis.md) | Why Lolla exists; borrowed certainty, sycophancy, structural pressure, and the Munger tendency ontology. |
| [Knowledge Substrate](docs/how-it-works/knowledge-substrate.md) | The 222 mental models, tendency bindings, graph, embeddings, V60 affordance/absence artifact, and bundled data dependencies. |
| [Architecture and Evolution](docs/how-it-works/architecture-and-evolution.md) | ConversationContext -> ConversationIR -> lane packets, migration history, lane design, observability, and trust boundaries. |
| [Live Flow](docs/how-it-works/live-flow.md) | Step-by-step `/lolla` flow: capture, extraction, pipeline, reconsideration, pressure check, memo, Observatory, archive. |
| [Pipeline Lanes](docs/how-it-works/pipeline-lanes.md) | Step 3 internals: Lane 1-4 mechanics, V60 private enrichment, pre-Step-6 shadow, run health, and tiebreaker traces. |
| [Operations and Limits](docs/how-it-works/operations-and-limits.md) | Quality doctrine, environment variables, edge cases, limitations, and cost/telemetry notes. |
| [Cost and Telemetry](docs/cost-and-telemetry.md) | Canonical usage-summary and pricing reference. |

## Coverage Check From This Pass

The previous monolith broadly covered the engine, but it had stale operational details:

- It said pressure-check sub-agents start before Step 6. Current `SKILL.md` requires the updated position and V60 ledger validation to finish first; Step 7 starts only after Step 6b succeeds.
- It did not document the default-off pre-Step-6 shadow portfolio runtime hook added to `scripts/run_pipeline.py`, `scripts/archive_run.py`, and Observatory `/audit/pre-step6`.
- It still described the archive as copying 11 core files. The current archive list has 12, adding `pre_step6_shadow_portfolio.json`.
- It under-specified Step 9 finalization. Current flow finalizes V60 telemetry and live-output hygiene before opening the Observatory.
- It named the architecture current state as 2026-05-11. The detail docs now carry a 2026-05-22 check note for the runtime deltas above.

## Maintenance Rule

When the engine or skill flow changes, update this file only if the top-level map changes. Put details in one of the focused files above. If a detail file starts drifting toward monolith size again, split it and link the new file here.
