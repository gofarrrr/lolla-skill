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
- Optional control-plane sidecars when external metadata is supplied:
  `control_input.json` preserves vendor-neutral trace/action/approval
  references, while `control_result.json` wraps the agent result for approval
  or observability systems without approving actions itself.
- A deterministic `evaluation.json` receipt for artifact/schema/custody/health
  consistency. It includes capture-adequacy checks and does not score advice
  quality.
- A metadata-first `risk_mode` recorded from `LOLLA_AUDIT_MODE` (`quick`,
  `standard`, `deep`, `high_stakes`, or `stability`). The default is
  `standard`; these modes do not yet change prompts, cost, Step 7 behavior,
  replay, or high-stakes domain policy. The agent-result contract already
  keeps clean `high_stakes` runs conservative with `caller_action:
  ask_user_first`.
- A local Observatory page with the full breakdown, traces, cards, costs, health checks, and archived artifacts.
- A local `reasoning_trace.json` custody manifest in the archived run folder, with artifact hashes, health, capture adequacy, optional control-plane references, usage, reasoning-lens IDs, model-call telemetry, and trace-adequacy status for replay without duplicating raw transcript text.

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
14. Finalize private ledgers and live-output hygiene, open the Observatory, archive the core/optional artifacts under `~/.local/share/lolla/runs/`, generate `agent_result.json` for the compact machine-readable handoff, optionally generate `control_result.json` when `control_input.json` was supplied, and generate `evaluation.json` plus `reasoning_trace.json` for local custody/replay, deterministic readiness checks, and corpus export.

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
| [Evaluation Flywheel Action Plan](docs/evals/evaluation-flywheel-action-plan-v0.md) | The current action map for turning real traces into human labels, fixtures, deterministic checks, and later calibrated binary judges without drifting into generic scoring. |
| [Current System Capabilities](docs/evals/current-system-capabilities-v0.md) | A plain-language map of what the current system can do, which recorded cases show it, how the layers work together, and how it helps us avoid brittle evaluation. |
| [Current State Anti-Drift Handoff](docs/evals/current-state-anti-drift-handoff-v0.md) | PR45's compact fresh-session map, updated by PR59, of the PR30-PR59 eval/accountability chain, current corpus evidence, non-goals, and the next approval gates. |
| [Semantica-Inspired Accountability PRD](docs/conversation-understanding/semantica-inspired-accountability-prd-v0.md) | PR55's docs-only plan for borrowing accountability primitives such as decision records, provenance maps, conflict registers, doctor/preflight, and case graph views without building graph DB, embeddings, memory, policy, compliance, judge, or scoring products. |
| [Lolla Doctor / Preflight Plan](docs/evals/lolla-doctor-preflight-plan-v0.md) | PR56's docs-only plan for a future read-only doctor command that checks local runtime wiring, archive paths, helper scripts, provider/cost readiness, review manifests, high-stakes evidence visibility, output-path safety, and privacy without running `$lolla`, calling models, or mutating archives. |
| [Lolla Doctor Read-Only CLI](docs/evals/lolla-doctor-readonly-cli-v0.md) | PR57's implementation note for `python3 scripts/lolla_doctor.py`, a local deterministic preflight command that emits `lolla.doctor_report.v0` without running `$lolla`, calling models, reading archive payloads, mutating archives, or judging answer quality. |
| [Audit Decision Record Design](docs/conversation-understanding/audit-decision-record-v0.md) | PR58's docs/JSON design for `lolla.audit_decision_record.v0`, a paraphrase-only accountability projection over existing artifacts that maps decision deltas to PR31 labels without becoming an exporter, judge, score, memory layer, or conversation-understanding IR. |
| [Audit Decision Record Fixtures](docs/evals/audit-decision-record-fixtures-v0.md) | PR59's docs/eval-only fixture review of six paraphrase-only audit decision records, confirming the shape is useful before any exporter, runtime integration, labels, scores, or judge. |
| [Complex Baseline Human Review](docs/evals/complex-baseline-human-review-v0.md) | PR30's six-run human/product review seed: useful friction, action-changing deltas, conservative reliance labels, and the PR31 rubric handoff. |
| [Actionable Delta Rubric](docs/evals/actionable-delta-rubric-v0.md) | PR31's human-owned rubric for distinguishing real Lolla improvement from smoother no-op prose before adversarial fixtures or judges. |
| [Adversarial Pair Fixtures](docs/evals/adversarial-pair-fixtures-v0.md) | PR32's seed fixtures for testing smoothness, status, checklist, balance, warmth, market-excitement, and authority-loyalty traps before any judge exists. |
| [Human Review Corpus Batch](docs/evals/human-review-corpus-batch-v0.md) | PR33's broader human/product review batch: 12 counted positives, one partial boundary record, one degraded exclusion, aggregate actionable-delta counts, and the PR34 handoff. |
| [User Values / Priorities Signal](docs/conversation-understanding/user-values-priorities-signal-v0.md) | PR34's design-only surface for representing values, priorities, tradeoffs, obligations, and non-negotiables without adding extraction, memory, runtime calls, or judging. |
| [User Values / Priorities Worksheet Plan](docs/evals/user-values-priorities-worksheet-plan-v0.md) | PR49's docs-only plan for making the PR34 values/priorities surface actionable as human review evidence before extraction, exports, memory, runtime behavior, or judging. |
| [User Values / Priorities Worksheet Fixtures](docs/evals/user-values-priorities-worksheet-fixtures-v0.md) | PR50's paraphrase-only fixture pack for testing whether the PR49 worksheet shape is understandable before export, extraction, runtime behavior, automatic labels, or judging. |
| [User Values / Priorities Worksheet Fixture Review](docs/evals/user-values-priorities-worksheet-fixture-review-v0.md) | PR51's docs/eval-only review of the PR50 fixture pack before blank worksheet/export structure, extraction, runtime behavior, automatic labels, or judging. |
| [User Values / Priorities Blank Worksheet Export](docs/evals/user-values-priorities-blank-worksheet-export-v0.md) | PR52's deterministic helper for creating blank human-owned worksheet JSON without reading archives, extracting values, changing runtime behavior, automatic labels, or judging. |
| [User Values / Priorities Worksheet Human Pilot](docs/evals/user-values-priorities-worksheet-human-pilot-v0.md) | PR53's docs/local-review pilot of human-filled worksheet JSON over existing reviewed records without raw content, extraction, runtime behavior, automatic labels, or judging. |
| [User Values / Priorities Pilot Review](docs/evals/user-values-priorities-pilot-review-v0.md) | PR54's docs/local-review decision that marks the values/priorities worksheet v0 complete for human-owned review and paused before extraction, runtime integration, automatic labels, memory, or judging. |
| [Live Output Hygiene Decision](docs/evals/live-output-hygiene-decision-v0.md) | PR35's design-only policy for `live_output_health`: keep `not_checked` honest by default, define a future trusted-transcript path to `clean`, and keep live hygiene separate from answer quality. |
| [Risk Mode Behavior Plan](docs/evals/risk-mode-behavior-plan-v0.md) | PR36's design-only policy for `quick`, `standard`, `deep`, `high_stakes`, and `stability`: risk changes review/reliance burden, not answer quality or domain authority. |
| [Risk Mode Fixture Matrix](docs/evals/risk-mode-fixture-matrix-v0.md) | PR37's paraphrase-only fixtures for testing risk-mode review/reliance expectations before runtime enforcement, caller-action changes, or judges. |
| [Risk Mode Fixture Review](docs/evals/risk-mode-fixture-review-v0.md) | PR38's human/product review of the risk-mode fixtures, including the added high-stakes values-conflict fixture and implementation-gate read. |
| [Risk Mode Implementation Plan](docs/evals/risk-mode-implementation-plan-v0.md) | PR39's docs-only plan for high-stakes reliance/readiness tightening, starting with contract-lock tests before enforcement. |
| [Risk Mode Contract Tests](tests/test_risk_mode_contract.py) | PR40's test-only contract lock for high-stakes conservatism, standard-mode regression, degraded-run dominance, fixture expectations, and review-corpus preservation. |
| [Evaluation Artifact Tests](tests/test_evaluation_artifact.py) | PR41's deterministic evaluation-artifact clarity tests for high-stakes reliance caveats without caller-action relaxation, domain approval, or answer-quality scoring. |
| [Review Corpus Evidence Readiness](docs/evals/review-corpus-evidence-readiness-v0.md) | PR48's manifest-only analyzer for deciding whether review-corpus data actually contains high-stakes reliance-present archive evidence before any real-run claim. |
| [Human Review Workflow](docs/evals/human-review-workflow.md) | The v0 human-review process and failure taxonomy for labeling exported archive-corpus records before any subjective judge is attempted. |
| [Problem and Thesis](docs/how-it-works/problem-and-thesis.md) | Why Lolla exists: borrowed certainty, sycophancy, structural pressure, and the Munger tendency ontology. |
| [Knowledge Substrate](docs/how-it-works/knowledge-substrate.md) | The 222 mental models, curation waves, graph, embeddings, V60 records, and bundled data files. |
| [Architecture and Evolution](docs/how-it-works/architecture-and-evolution.md) | `ConversationContext`, `ConversationIR`, packet builders, migration history, trust boundaries, and observability. |
| [Live Flow](docs/how-it-works/live-flow.md) | Full chronological `/lolla` flow: capture, extraction, pipeline, reconsideration, default-off pressure-check state, optional deeper review, memo, Observatory, archive. |
| [Pipeline Lanes](docs/how-it-works/pipeline-lanes.md) | Lane 1-4 mechanics, V60 private enrichment, pre-Step-6 shadow portfolio, `run_health`, and tiebreaker traces. |
| [Operations and Limits](docs/how-it-works/operations-and-limits.md) | Quality doctrine, environment variables, edge cases, limitations, and cost notes. |
| [Cost and Telemetry](docs/cost-and-telemetry.md) | Canonical usage-summary and pricing reference. |

## Current Notes

- Checked against `SKILL.md` and runtime entry points on 2026-06-25.
- Pressure-check agents are rested by default. If explicitly enabled, they start only after the updated position is persisted and the V60 ledger validates.
- The pre-Step-6 shadow portfolio hook is default-off and shadow-only; it records evidence but never changes visible output.
- The archive currently copies the core/optional artifact set, including live transcript, operator log, run-event log, private ledgers, memo fields, optional usefulness/outcome reviews, and optional `control_input.json` when present. It also generates `agent_result.json`, the compact agent-facing handoff; optional `control_result.json`, the control-plane wrapper; `extraction_adequacy_report.json`, the deterministic report for current extraction/provenance preservation across `conversation.txt -> extraction.json -> ConversationContext -> ConversationIR`; `evaluation.json`, the deterministic run-readiness receipt; and `reasoning_trace.json`, a local-only manifest that indexes artifacts by path/hash and adds capture-adequacy, optional control-plane references, reasoning-lens, model-call, private-custody, and trace-adequacy metadata.
- The June 24 accountability pass added run lifecycle events, operator-log separation for helper diagnostics, final-receipt Observatory liveness verification, trusted live-transcript finalization for merge-readiness checks, and graph-survival joins that preserve Lane 2 ledger uptake correctly.
- `scripts/export_reasoning_trace_dataset.py` scans archived `reasoning_trace.json` files and writes a JSONL corpus plus aggregate summary so repeated runs can be reviewed with an evals-style error-analysis workflow.
- `scripts/export_extraction_adequacy_corpus.py` scans archived runs and writes a local-only JSONL/manifest survey of extraction/provenance adequacy. It reuses existing `extraction_adequacy_report.json` files, can build legacy reports in memory without mutating archives, and does not copy raw transcript, memo, revised-answer, model-message, provider-reasoning, fabricated-passage, or control-argument text.
- `scripts/export_review_corpus.py` scans archived run folders and writes a deterministic JSONL run-envelope corpus plus manifest for human review and stability analysis. It includes blank review fields, compact custody/readiness metadata, and PR42 `risk_mode_reliance` caveats; it does not score advice quality or use an LLM judge.
- Review-corpus records include deterministic review-readiness tiers so humans and subagents can separate full modern custody runs from partial or legacy content-only archives before labeling.
- PR30 adds a local six-run human/product review seed for the complex baseline. All six answer-level reviews passed and were labeled improved, but all six remain `safe_for_agent_use: with_human_review`; `evaluation.json` is still run-readiness only, and `caller_action: use_revised_answer` is not human approval.
- PR31 adds a human-owned actionable-delta rubric. It prepares PR32 adversarial fixtures, but it is not a judge, score, automatic labeler, or runtime integration.
- PR32 adds paraphrase-only adversarial pair fixtures from the six PR30 cases. They prepare future calibration work, but they are not a judge, score, benchmark claim, automatic labeler, or runtime integration.
- PR33 adds a broader local human-review corpus batch. Twelve full-modern records count as positive answer-level eval evidence, one older partial record is `needs_followup`, and one degraded record is `exclude_from_eval`; it still does not create a judge, score, automatic labeler, or runtime integration.
- PR34 designs the first-class user-values/priorities signal. It defines boundaries, schema shape, grounding, confidence, reviewer use, and implementation gates, but does not add extraction, a report builder, runtime behavior, memory, automatic labels, or a judge.
- PR35 documents live-output hygiene policy. `live_output_health: not_checked` remains the honest default for normal runs; `clean` requires a future trusted complete transcript path, and live-output hygiene does not score answer quality or relax `caller_action`.
- PR36 documents risk-mode behavior policy. Existing `risk_mode` names remain the vocabulary; risk raises review and reliance strictness, but it does not approve actions, change runtime behavior, make Lolla a domain authority, or relax `caller_action`.
- PR37 adds a risk-mode fixture matrix. It covers `quick`, `standard`, `deep`, `high_stakes`, `stability`, and excluded/domain-review routing with expected `safe_for_agent_use` and `caller_action` stances; it does not enforce behavior or add a judge.
- PR38 reviews the risk-mode fixture matrix. All original PR37 fixtures passed, one high-stakes values/priorities conflict fixture was added, and the matrix is usable as a future implementation gate without approving runtime enforcement or a judge.
- PR39 plans the risk-mode implementation path. The smallest future behavior change is high-stakes reliance/readiness tightening, starting with contract-lock tests for existing conservative behavior; it does not change runtime, prompts, `SKILL.md`, `caller_action`, or evaluation behavior.
- PR40 adds risk-mode contract-lock tests. Otherwise clean `high_stakes` stays `ask_user_first`, degraded high-stakes stays `do_not_use_run_degraded`, clean `standard` stays `use_revised_answer`, and review-corpus records preserve the risk/reliance fields; no runtime behavior changed.
- PR41 adds `risk_mode_reliance_policy` to `evaluation.json` checks for high-stakes runs. It makes reliance caveats explicit while preserving `caller_action`, standard-mode behavior, degraded-run blocking, and human-owned `safe_for_agent_use`.
- PR42 exposes that caveat as compact `risk_mode_reliance` metadata in review-corpus records and human-review workflow docs. It does not change `caller_action`, runtime behavior, prompts, `SKILL.md`, or human-owned `safe_for_agent_use`.
- PR43 reviews the PR42 surface with PR37/PR38 fixtures because the local real archive corpus has 80 `standard` records and zero high-stakes `risk_mode_reliance.present: true` examples. Reviewers can read `risk_mode_reliance.status: pass` as conservative reliance-policy expression without treating it as answer-quality pass, domain approval, or automatic `safe_for_agent_use`; no workflow or taxonomy change is recommended.
- PR44 adds additive review-corpus manifest counts for `risk_mode_reliance.present`, presence by risk mode, and reliance-check status so aggregate absence/presence is visible without changing records, schema name, runtime behavior, caller action, or archive contents.
- PR45 adds the current-state anti-drift handoff. It summarizes the deterministic-harness/product boundary, the PR30-PR54 eval chain, the current 80-record all-standard corpus evidence, explicit non-goals, and the approval gates before high-stakes runs, values worksheet automation, or trusted live-output implementation.
- PR46 adds the approved high-stakes evidence seed plan. It defines scenario categories, custody, cost, privacy, and human-review gates, but does not run cases.
- PR47 adds paraphrase-only high-stakes evidence fixtures so reviewer expectations can be tested before real archive evidence exists.
- PR48 adds a read-only review-corpus evidence-readiness analyzer. It reads only manifest JSON, reports whether high-stakes reliance-present records actually exist, treats old manifests as insufficient rather than guessing, and does not read archives, call models, judge answer quality, or approve runs.
- PR49 adds a docs-only user-values/priorities worksheet plan. It makes the missing PR34 surface actionable for human review without extraction, exports, memory, runtime behavior, `conversation_understanding_ir.v0`, automatic labels, or a judge.
- PR50 adds paraphrase-only user-values/priorities worksheet fixtures. It tests whether the PR49 worksheet is understandable from PR30/PR33 review patterns without raw content, extraction, exports, runtime behavior, automatic labels, or a judge.
- PR51 reviews the user-values/priorities worksheet fixtures. All six pass as understandable human-review examples, so the next conservative slice is blank worksheet/export structure, not extraction, runtime behavior, automatic labels, or a judge.
- PR52 adds a deterministic blank user-values/priorities worksheet helper. It creates empty `lolla.user_values_priorities_worksheet.v0` JSON for human review without reading archives, extracting values, populating labels, changing runtime behavior, or adding a judge.
- PR53 pilots human-filled user-values/priorities worksheets on existing reviewed records. It stores four paraphrase-only local-review worksheets, keeps all raw/private inclusion flags false, and recommends a PR54 pilot review / v0 decision before any extraction, runtime behavior, automatic labels, or judge.
- PR54 reviews the PR53 pilot and closes the worksheet lane at v0 for human-owned review. It marks all four pilot worksheets pass, preserves the need for user confirmation, and pauses before extraction, runtime integration, automatic labels, memory, or judging.
- PR55 lands the Semantica-inspired accountability PRD. It is docs-only: it
  records the selective borrowing rule and the PR56-PR65 accountability queue,
  but it does not add doctor/preflight, decision records, provenance maps,
  conflict registers, case graph exports, runtime behavior, graph DBs,
  embeddings, memory, policy engines, automatic labels, answer-quality scoring,
  or judges.
- PR56 lands the Lolla Doctor / Preflight plan. It is docs-only: it defines the
  future read-only doctor check groups, pass/warn/fail semantics, and
  `lolla.doctor_report.v0` draft shape, but it does not add a CLI, run
  `$lolla`, call models, mutate archives, change prompts, change `SKILL.md`,
  or change runtime behavior.
- PR57 lands the read-only Lolla doctor CLI. It implements
  `python3 scripts/lolla_doctor.py` and `lolla.doctor_report.v0` for local
  preflight checks, but it does not run `$lolla`, call models, mutate archives,
  change prompts, change `SKILL.md`, approve high-stakes use, or judge answer
  quality.
- PR58 lands the audit decision record design. It defines
  `lolla.audit_decision_record.v0` as a paraphrase-only local accountability
  projection over existing artifacts and PR31 labels, but it does not implement
  an exporter, run `$lolla`, call models, mutate archives, change prompts,
  change `SKILL.md`, approve high-stakes use, score answer quality, or create a
  conversation-understanding IR.
- PR59 lands audit decision record fixtures and a human-owned fixture review.
  Six paraphrase-only records pass review as understandable and PR31-mappable,
  with caveats about preserving conflict detail before any future exporter.
  PR59 does not implement an exporter, runtime integration, labels, scoring,
  judging, model calls, archive mutation, or platform work. Stop after PR59;
  PR60 should start only after maintainer review.
