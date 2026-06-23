# Lolla - How It Works

Lolla is a second-pass reasoning audit for AI advice.

It starts from a simple problem: modern AI can produce advice that is fluent,
balanced, and convincing before the reasoning has earned that confidence. The
danger is not only hallucinated facts. The danger is a recommendation that
quietly inherits the user's frame, skips a reversal condition, collapses a
messy decision into a clean story, or treats an emotional signal as if it were
evidence.

Lolla slows that moment down.

It captures the conversation, extracts the decision shape, runs a structured
audit against curated reasoning knowledge, and then makes the assistant revise
its own answer in public: what survived, what it would take back, and what
actually changed.

## First Principles

Lolla is built on five principles:

1. **A good answer is not the same as good reasoning.** The answer can be
   polished while the structure is weak.
2. **The question can contain the bug.** Strategic advice often fails because
   the user's framing made one path too natural.
3. **Useful challenge needs structure.** "Think harder" is weak. "Name the
   walk-away condition before treating this as a calculated bet" is useful.
4. **Probabilistic judgment needs deterministic custody.** LLMs are good at
   reading language. They are bad at being reproducible record keepers. Lolla
   uses LLMs at the semantic edges and deterministic code for routing,
   selection, custody, hygiene, telemetry, and archive.
5. **The run should be inspectable later.** A reasoning audit that cannot be
   replayed, checked, or compared becomes another polished story.

## What It Does For You

Lolla looks for:

- assumptions the answer inherited from the user
- constraints that were mentioned but not carried into the recommendation
- missing stop rules, evidence gates, and reversal conditions
- places where "survivable" was treated as "wise"
- places where a feeling was allowed to become a decision rule
- structural dimensions the answer never entered
- internal machinery leaks or run-health issues that make the output less
  trustworthy

The best test is still simple:

> Run it on the answer you already liked.

## The Run Story

Every `/lolla` run has one visible story and one custody story.

The visible story is what the user sees:

1. Lolla reads back the decision it captured.
2. It gives the strongest case against the original answer.
3. The assistant writes an updated position.
4. It renders a memo and opens the Observatory.
5. It gives a final receipt with health, cost, memo path, and archive path.

The custody story is what makes that visible story auditable:

1. The skill creates a collision-resistant run ID such as
   `20260623T113203Z_c4df83`.
2. It writes a run-specific env file and exports `LOLLA_EXPECTED_RUN_ID`.
3. Major scripts verify that active run state and artifact paths match the
   expected run before model calls or artifact writes.
4. The conversation, extraction, pipeline result, revised answer, memo,
   private ledgers, live transcript, run events, graph survival report, and
   reasoning trace are written under the same run ID.
5. The archive groups reruns by conversation hash first, then decision
   fingerprint, so extractor paraphrase drift does not split the same case.

This is why Lolla can support research and iteration instead of only producing
a one-off answer in chat.

## The Four Audit Lanes

| Lane | Plain-language job | Product role |
| --- | --- | --- |
| Structural Pressure | Find cognitive tendencies and omitted safeguards in the reasoning. | Produces the strongest challenges, failure modes, reversal triggers, and corrective pressure. |
| Model Companion | Identify mental models the answer is already using or violating. | Adds useful lenses, premortem questions, antagonists, and failure modes. |
| Frame Pressure | Inspect the user's question for embedded assumptions. | Opens alternative frames and suppressed counterfactuals. |
| Structural Coverage | Ask what decision territory was never addressed. | Produces gap dimensions and questions only the decision-maker can answer. |

The lanes do not vote on the answer. They provide pressure. The assistant then
has to decide what to use, reject, defer, or keep private as a guardrail.

## What Changed In The Newer Machinery

Recent versions do more than run the four lanes. They preserve the reasoning
process around the lanes:

- **Run identity is collision-resistant.** Timestamp-only IDs are gone; runs
  get a short random suffix.
- **The latest-env pointer is no longer trusted inside an active run.**
  `/tmp/lolla_latest_env.sh` is a convenience pointer, not the source of truth.
- **Expected-run guards stop cross-run contamination.** Scripts compare
  `LOLLA_RUN_ID`, `LOLLA_EXPECTED_RUN_ID`, and artifact path-derived run IDs.
- **Live output is checked semantically.** The hygiene layer scans visible
  `## Updated position` blocks and degrades a run when the live transcript
  contains a mismatched position from another case.
- **Recovery events are recorded.** Restarts, pins, aborts, pointer rewrites,
  and similar operator recovery moves can be persisted in `run_events.json`.
- **Coverage is more nuanced.** A dimension can be `covered: true` while still
  carrying `coverage_quality`, such as `covered_weak_threshold`,
  `covered_missing_operational_detail`, `covered_strong`, or
  `covered_immaterial`.
- **Suppressed lenses are preserved.** `graph_survival_report.*` and
  `reasoning_trace.json` expose selected, rejected, unadjudicated, suppressed,
  and budget-suppressed model signals instead of pretending unselected means
  useless.
- **Usefulness and outcome review are first-class slots.**
  `user_usefulness_review.json` and `outcome_review.json` can be archived even
  when they are not collected yet, giving later evals somewhere clean to land.

## What You Get Back

A completed run can produce these surfaces:

- **Chat output** - readback, counterargument, revised position, final receipt.
- **Memo** - a portable Markdown decision note, focused on what changed.
- **Observatory** - a local web breakdown with the full cards, health,
  telemetry, V60/private-custody panels, graph survival, and usage.
- **Archive folder** - persistent local run directory under
  `~/.local/share/lolla/runs/<case>/<run_id>/`.
- **`reasoning_trace.json`** - local custody manifest with artifact hashes,
  run health, usage, reasoning-lens IDs, budget-suppressed lenses,
  candidate-commitment classifications, model-call telemetry, run events,
  usefulness/outcome review state, and trace adequacy.
- **Exportable dataset records** - JSONL records generated from archived
  traces by `scripts/export_reasoning_trace_dataset.py`.

## Artifact Map

Core or optional archived artifacts include:

| Artifact | Role |
| --- | --- |
| `conversation.txt` | captured source conversation |
| `extraction.json` | decision structure and capture health |
| `result.json` | full pipeline result and run health |
| `revised.txt` | assistant's updated position |
| `memo.md` / `memo_note.json` | portable decision note and memo fields |
| `gapcheck.txt` / `gapcheck_lanes.json` | default-off or optional pressure-check state |
| `v60_ledger_skeleton.json` / `v60_ledger.json` | private enrichment custody and use/reject/defer accounting |
| `pre_step6_private_table.*` | private Step 6 thinking surface and ledger |
| `live_transcript.txt` | visible chat/status surface captured for hygiene checks |
| `run_events.json` | recovery and operator-event ledger |
| `graph_survival_report.json` / `.md` | selected/suppressed/unadjudicated model-signal survival |
| `reasoning_trace.json` | local custody and eval manifest |
| `user_usefulness_review.json` | optional user usefulness rating |
| `outcome_review.json` | optional later outcome review |

Missing optional artifacts do not block archive. They are recorded as missing
so the run remains honest about what was and was not captured.

## Trust Boundaries

Lolla separates jobs:

- **Claude Code orchestrates the skill.** It captures the conversation, runs
  scripts, reads the audit output, writes the revised position, and persists
  artifacts.
- **OpenRouter-backed calls perform semantic audit work.** Extraction, triage,
  deep checks, frame extraction, model verification, structural coverage, and
  delivery-quality checks happen through calibrated boundary calls.
- **Deterministic code owns custody.** Routing, graph traversal, artifact
  writing, ledger validation, hygiene scans, pricing, archive, and trace export
  are code paths, not improvisation.

The revised answer is not treated as an oracle. It is treated as a product
surface built from a recorded audit.

## Run Health

Every run reports health. That health is not cosmetic. It tells you whether the
result is clean enough to compare or rely on:

- `healthy` - no material integrity issues found
- `partial` - usable, but at least one non-fatal layer was incomplete or
  provider behavior needs caution
- `degraded` - product, live-output, quote, fingerprint, or ledger issues
  materially weaken trust
- `critical` - capture or runtime failure makes the run unsuitable as an audit

Common issues include `vendor_boundary_reasoning_leak`, `quote_fabrication`,
`no_fingerprint`, `bullshit_index_partial`, `product_output_leak`,
`live_output_leak`, `live_output_semantic_mismatch`, `live_output_missing`,
and missing or invalid private ledgers.

## Read Next

| Document | Use it for |
| --- | --- |
| [Problem and Thesis](docs/how-it-works/problem-and-thesis.md) | Why the system exists and what problem it is trying to solve. |
| [Live Flow](docs/how-it-works/live-flow.md) | Exact `/lolla` sequence from activation to archive. |
| [Pipeline Lanes](docs/how-it-works/pipeline-lanes.md) | Lane mechanics, V60/private table, coverage quality, and run-health fields. |
| [Knowledge Substrate](docs/how-it-works/knowledge-substrate.md) | The curated model corpus, graph, embeddings, V60 artifact, and graph-survival view. |
| [Operations and Limits](docs/how-it-works/operations-and-limits.md) | What Lolla is not, known limits, env vars, edge cases, and failure states. |
| [Architecture and Evolution](docs/how-it-works/architecture-and-evolution.md) | Trust boundaries, migration history, and why the runtime has this shape. |
| [Cost and Telemetry](docs/cost-and-telemetry.md) | Per-run API calls, pricing, usage summaries, and telemetry verification. |

## Current Implementation Notes

- `SKILL.md` is the executable source of truth for the live Claude Code flow.
- The public docs explain the product and architecture; the `references/`
  directory contains operator contracts for chat voice, memo format, private
  enrichment treatment, and output hygiene.
- Archive currently copies 18 core/optional artifacts when present and
  generates `graph_survival_report.*` plus `reasoning_trace.json`.
- `scripts/export_reasoning_trace_dataset.py` scans archived traces and writes
  a JSONL corpus plus aggregate summary for eval-style review.
