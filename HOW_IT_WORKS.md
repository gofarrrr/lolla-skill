# Lolla - How It Works

Lolla is a Claude Code and Codex skill for pressure-testing AI answers that sound convincing enough to use.

It is built for the moment after Claude gives you advice, a strategy, a recommendation, or a plan and you think: "This sounds right." Lolla slows that moment down. It asks what the answer assumed, what it skipped, what would make it fail, and what questions should have been asked before the answer sounded so sure.

The goal is not to produce a longer answer. The goal is to make the answer harder to trust blindly.

## What It Does For You

Lolla helps you catch the parts of an AI answer that polished prose can hide:

- Hidden assumptions the answer inherited from your question.
- Constraints or concerns that were mentioned but not carried into the recommendation.
- Missing failure conditions, reversal triggers, stop rules, or evidence gates.
- Weak frames where the answer accepted the wrong shape of the problem.
- Uncovered decision dimensions that only the decision-maker can answer.
- Places where the model sounded balanced but did not actually test the hard part.

Use it on answers that matter: strategy, product, hiring, investment, negotiation, architecture, career, family, health, ethics, or any decision where a fluent answer could push you toward action.

The best test is simple:

> Run it on the answer you already liked.

## What Happens In A Run

At a high level, Lolla does four things.

1. **Captures the conversation.** It takes the current agent conversation and preserves the user turns, assistant answers, and decision context.
2. **Extracts the decision structure.** It identifies the decision situation, live constraints, current recommendation, original framing, reasoning passages, and dropped threads.
3. **Runs an external reasoning audit.** The engine sends calibrated audit prompts through OpenRouter and checks the answer through four independent lanes.
4. **Forces reconsideration.** Claude then uses the audit pressure to revise its own position, persist the revised answer, record the pressure-check state, render a memo, open the Observatory, and archive the run.

The important design choice: Claude does not grade its own original answer during the audit. The detection and routing work happens through the Lolla engine and OpenRouter calls. Claude comes back in later to reconsider the answer using the persisted pressure.

## The Four Audit Lanes

Lolla does not rely on one giant "be more critical" prompt. It splits the audit into four different checks:

| Lane | Question it asks | What it gives you |
|---|---|---|
| Structural Pressure | What reasoning failure pattern is present? | A direct challenge to weak reasoning, with the specific passage and corrective pressure. |
| Model Companion | What mental models are already being used or violated? | Useful lenses, failure modes, premortem questions, and tensions from the curated substrate. |
| Frame Pressure | What did the question assume before the answer began? | Alternative ways to frame the problem. |
| Structural Coverage | What important decision territory was never addressed? | Missing dimensions and user-answerable discovery questions. |

After those four lanes, Lolla can also attach private source-backed material from the V60 affordance/absence layer. That material is not public prose. It is private pressure Claude must consider, reject, defer, or keep as a guardrail before writing the updated position.

## What You Get Back

A normal run produces:

- A short readback confirming what Lolla captured.
- The strongest case against the answer you were about to trust.
- An updated position from Claude, structured around what survived, what should be taken back or set aside, and what actually shifted.
- An intentional pressure-check state. Post-Step-6 isolated reviewers are rested by default to simplify the live skill and reduce cost; they remain available only as an explicit deeper-review mode.
- A portable memo.
- A compact `agent_result.json` contract for machine callers, including
  `caller_action`, artifact status, artifact pointers, run health, cost, and
  product-level summary fields.
- A local Observatory page with the full breakdown, traces, cards, costs, health checks, and archived artifacts.
- A local `reasoning_trace.json` custody manifest in the archived run folder, with artifact hashes, health, usage, reasoning-lens IDs, model-call telemetry, and trace-adequacy status for replay without duplicating raw transcript text.

Lolla also records run health. If capture was incomplete, embeddings were off, a private ledger was missing, a lane failed, or public prose leaked internal machinery, the run should not pretend to be clean.

## What Makes It Different

Lolla is not a prompt pack. It is a small reasoning-audit system bundled as an agent skill.

The engine combines:

- A curated substrate of 222 mental models.
- Munger-style cognitive-tendency detection.
- A graph of model relationships, allies, antagonists, and tensions.
- Deterministic routing through curated knowledge.
- LLM calls only where semantic judgment is needed.
- Traceable artifacts so findings can be inspected after the run.

The architecture principle is:

> Probabilistic judgment at the edges, curated structure in the middle.

LLMs are used to read messy natural language. The deterministic engine handles routing, graph traversal, card assembly, custody, validation, and traceability.

## The Runtime Flow

This is the live `/lolla` flow in one page:

1. Resolve skill path, API keys, bundled engine/data, run id, and live transcript file.
2. Capture the current conversation into `/tmp/lolla_<run_id>_conversation.txt`.
3. Invoke the Step 2 helper, which calls `scripts/run_extract.py` and creates `/tmp/lolla_<run_id>_extraction.json`.
4. Show a short readback and audit promise.
5. Invoke the Step 3 helper, which calls `scripts/run_pipeline.py --skip-revision` with the extraction and conversation files.
6. Build `ConversationContext`, construct `ConversationIR`, and run the four audit lanes.
7. Attach Bullshit Index, usage summary, run health, and default-on V60 private enrichment.
8. Render the strongest counterargument in chat.
9. Write the updated position.
10. Persist `revised_answer` and validate the pre-Step-6 private-table and V60 consideration ledgers.
11. Persist the default-off pressure-check state after Step 10 succeeds.
12. If the user/operator explicitly requested deeper review, run optional pressure-check agents after Step 10 and persist their comparison plus auxiliary token usage.
13. Persist memo-note fields and render the deterministic memo.
14. Finalize private ledgers and live-output hygiene, open the Observatory, archive the core/optional artifacts under `~/.local/share/lolla/runs/`, generate `agent_result.json` for the compact machine-readable handoff, and generate `reasoning_trace.json` for local custody/replay with enough metadata for local reasoning-eval corpus export.

`SKILL.md` is the executable instruction source. This page is the readable map.

## Read More

The detailed docs are split so agents and humans do not have to load one giant file.

| File | Read it for |
|---|---|
| [Pitch and Invitation](docs/lolla-pitch-and-invitation.md) | A plain-language shareable explanation of what Lolla is, why it matters for agents, who it is for, and what kind of feedback we want. |
| [Agent Result Contract](docs/lolla-agent-result-contract.md) | The shipped `lolla_agent_result.v1` archive artifact: status, `caller_action`, product summaries, artifact pointers, and current limitations. |
| [Reasoning-Audit Harness PRD](docs/lolla-reasoning-audit-harness-prd.md) | The actionable roadmap for turning Lolla into an agent-callable reasoning-audit harness with risk modes, an agent result contract, evaluation artifacts, and archive-corpus workflows. |
| [Agent Control Layers And Lolla Integration](docs/agent-control-layers-and-lolla-integration.md) | How Lolla can fit beside CrabTrap-style proxies, guardrails, approvals, sandboxes, identity scopes, and observability/eval systems without pretending to replace them. |
| [Evaluation Methodology](docs/lolla-evaluation-methodology.md) | Lolla-specific eval doctrine: error analysis first, deterministic gates before judges, calibrated binary judges, and how to avoid rewarding smoothness over useful friction. |
| [Problem and Thesis](docs/how-it-works/problem-and-thesis.md) | Why Lolla exists: borrowed certainty, sycophancy, structural pressure, and the Munger tendency ontology. |
| [Knowledge Substrate](docs/how-it-works/knowledge-substrate.md) | The 222 mental models, curation waves, graph, embeddings, V60 records, and bundled data files. |
| [Architecture and Evolution](docs/how-it-works/architecture-and-evolution.md) | `ConversationContext`, `ConversationIR`, packet builders, migration history, trust boundaries, and observability. |
| [Live Flow](docs/how-it-works/live-flow.md) | Full chronological `/lolla` flow: capture, extraction, pipeline, reconsideration, default-off pressure-check state, optional deeper review, memo, Observatory, archive. |
| [Pipeline Lanes](docs/how-it-works/pipeline-lanes.md) | Lane 1-4 mechanics, V60 private enrichment, pre-Step-6 shadow portfolio, `run_health`, and tiebreaker traces. |
| [Operations and Limits](docs/how-it-works/operations-and-limits.md) | Quality doctrine, environment variables, edge cases, limitations, and cost notes. |
| [Cost and Telemetry](docs/cost-and-telemetry.md) | Canonical usage-summary and pricing reference. |

## Current Notes

- Checked against `SKILL.md` and runtime entry points on 2026-06-24.
- Pressure-check agents are rested by default. If explicitly enabled, they start only after the updated position is persisted and the V60 ledger validates.
- The pre-Step-6 shadow portfolio hook is default-off and shadow-only; it records evidence but never changes visible output.
- The archive currently copies the core/optional artifact set, including live transcript, operator log, run-event log, private ledgers, memo fields, and optional usefulness/outcome reviews when present. It also generates `agent_result.json`, the compact agent-facing handoff, and `reasoning_trace.json`, a local-only manifest that indexes artifacts by path/hash and adds reasoning-lens, model-call, private-custody, and trace-adequacy metadata.
- The June 24 accountability pass added run lifecycle events, operator-log separation for helper diagnostics, final-receipt Observatory liveness verification, trusted live-transcript finalization for merge-readiness checks, and graph-survival joins that preserve Lane 2 ledger uptake correctly.
- `scripts/export_reasoning_trace_dataset.py` scans archived `reasoning_trace.json` files and writes a JSONL corpus plus aggregate summary so repeated runs can be reviewed with an evals-style error-analysis workflow.
