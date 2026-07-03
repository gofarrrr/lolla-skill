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
| [Product Delta / Eval Docs Index](docs/evals/README.md) | GitHub-facing map of the offline Product Delta eval lane: what it evaluates, how to run the safe tools, what to inspect, and what not to infer. |
| [Board Product Briefs](docs/board/README.md) | Simple board/customer-facing reading packet for the current product story: what Lolla solves, what Decision Trail adds, how evals work, where the alpha is, and what remains unproven. |
| [Decision Trail Web Page Draft](docs/lolla-decision-trail-web-page-v0.md) | Customer-facing explanation of the answer-plus-process value: serious AI decisions need the revised answer, the pressure trail, the audit receipt, and explicit non-claims. |
| [Decision Work Receipt PRD](docs/conversation-understanding/decision-work-receipt-prd-v0.md) | Actionable PRD for the missing work-trail product layer: source/context inventory, conversation process map, challenge coverage, sparse receipt exporter, fixture review, and decision gate. |
| [Decision Work Receipt Schema](docs/conversation-understanding/decision-work-receipt-v0.json) | PR105's machine-readable `lolla.decision_work_receipt.v0` contract for the future work-trail receipt, without exporter code or runtime integration. |
| [Decision Work Receipt Source Inventory](docs/conversation-understanding/decision-work-receipt-source-inventory-v0.md) | PR106's read-only checked-in-safe exporter slice for source/context inventory over completed run directories, leaving process interpretation and challenge coverage sparse. |
| [Decision Work Receipt Conversation Process Map](docs/conversation-understanding/decision-work-receipt-conversation-process-map-v0.md) | PR107's read-only exporter slice for deterministic turn-count, capture, and one-shot/multi-turn process-shape metadata, while leaving semantic process events to LLM or human interpretation. |
| [Decision Work Receipt Challenge Coverage Map](docs/conversation-understanding/decision-work-receipt-challenge-coverage-map-v0.md) | PR108's read-only exporter slice for mapping which Lolla challenge surfaces and run-health caveats are visible from completed artifacts, without scoring lane quality or advice quality. |
| [Decision Work Receipt Exporter](docs/conversation-understanding/decision-work-receipt-exporter-v0.md) | PR109's read-only composed receipt exporter: source inventory, process metadata, challenge coverage, optional Decision Trail/Product Delta references, readiness labels, missingness, non-claims, and boundary flags. |
| [Decision Work Receipt Fixture Review](docs/conversation-understanding/decision-work-receipt-fixture-review-v0.md) | PR110's checked-in-safe review of the sparse receipt: useful as a work-trail shell, still too thin for the full semantic story, and risky if readiness labels are read as approval. |
| [Decision Work Receipt Decision Gate](docs/conversation-understanding/decision-work-receipt-decision-gate-v0.md) | PR111's docs-only closure gate: keep the sparse receipt as an internal/workflow wrapper and do not build a parallel Work Receipt interpretation system yet. |
| [Decision Work Receipt External Report Attachments](docs/conversation-understanding/decision-work-receipt-external-report-attachments-v0.md) | PR112's narrow read-only bridge: let the receipt CLI link externally generated Decision Trail/Product Delta reports by safe metadata, without copying report content, local paths, or semantic conclusions. |
| [Decision Work Receipt Debug Summary](docs/conversation-understanding/decision-work-receipt-debug-summary-v0.md) | Internal Markdown renderer for turning a Decision Work Receipt plus optional Decision Trail report into a maintainer-readable status/missingness packet. It is not the customer-facing decision story. |
| [Launch Public Enterprise Beta Receipt Debug Example](docs/conversation-understanding/decision-work-receipt-debug-summary-launch-public-enterprise-beta-v0.md) | A checked-in safe one-case internal example showing what the current receipt/report package can inspect and what it still cannot explain. |
| [Decision Work Brief PRD](docs/conversation-understanding/decision-work-brief-prd-v0.md) | Product-facing target and PR113-PR158 delivery plan for the missing layer: a plain-language brief explaining the decision, what Lolla pressed on, what changed, what remains unresolved, and what the audit must not claim. |
| [Decision Work Brief Schema](docs/conversation-understanding/decision-work-brief-v0.json) | PR114's machine-readable `lolla.decision_work_brief.v0` contract for the user-facing brief, with required decision-story sections, source refs, custody flags, uncertainty, human-validation state, and explicit non-claims. |
| [Decision Work Brief Schema Guide](docs/conversation-understanding/decision-work-brief-schema-v0.md) | Plain-language guide to the PR114 schema boundary: the brief tells the story, the receipt backs the story, and the schema itself adds no generator, renderer, runtime integration, semantic inference, product proof, or agent authorization. |
| [Decision Work Brief Packet Builder](docs/conversation-understanding/decision-work-brief-packet-builder-v0.md) | PR115's read-only local packet builder for preparing `lolla.decision_work_brief_packets.v0` from completed runs, with metadata-only as the default, explicit local-private include-text marking, source refs, missingness, custody flags, and no generated brief. |
| [Decision Work Brief Draft Pilot](docs/conversation-understanding/decision-work-brief-draft-pilot-v0.md) | PR116's one-case Codex-assisted provisional draft pilot, using a locally generated PR115 metadata-only packet to embed a checked-in-safe `lolla.decision_work_brief.v0` draft with source refs, uncertainty, human follow-up questions, and non-claims. |
| [Decision Work Brief Renderer](docs/conversation-understanding/decision-work-brief-renderer-v0.md) | PR117's deterministic Markdown renderer for existing `lolla.decision_work_brief.v0` JSON, patched by PR123 to use plain-language decision headings while preserving section uncertainty, source refs, custody flags, and non-claims without generating or inferring content. |
| [Decision Work Brief Rendered Example](docs/conversation-understanding/decision-work-brief-rendered-ceo-remove-founding-cofounder-v0.md) | PR117's checked-in-safe rendered Markdown example from the PR116 cofounder draft, kept under conversation-understanding rather than the board because it is still provisional. |
| [Decision Work Brief Usefulness Review](docs/conversation-understanding/decision-work-brief-usefulness-review-v0.md) | PR118's Codex-assisted delivery gate over the receipt/debug layer, structured draft, and rendered brief; it chooses `proceed_to_tiny_second_case`, not runtime integration or product readiness. |
| [Decision Work Brief Second Tiny Case Pilot](docs/conversation-understanding/decision-work-brief-second-tiny-case-pilot-v0.md) | PR119's second checked-in-safe Codex-assisted pilot on `launch-public-enterprise-beta`, comparing it to the cofounder case and choosing `proceed_to_small_pattern_review`, not runtime integration or product readiness. |
| [Decision Work Brief Rendered Launch-Beta Example](docs/conversation-understanding/decision-work-brief-rendered-launch-public-enterprise-beta-v0.md) | PR119's rendered second-case Markdown example, generated from an embedded `lolla.decision_work_brief.v0` object without checking in local-private text. |
| [Decision Work Brief Small Pattern Review](docs/conversation-understanding/decision-work-brief-small-pattern-review-v0.md) | PR120's two-case pattern review over the cofounder and launch-beta briefs; it chooses `proceed_to_third_diversity_case`, not a renderer patch or runtime integration. |
| [Decision Work Brief Third Diversity Case Pilot](docs/conversation-understanding/decision-work-brief-third-diversity-case-pilot-v0.md) | PR121A's third checked-in-safe pilot on `deploy-assisted-intake-routing`, following PR120's gate and choosing `proceed_to_three_case_pattern_review`. |
| [Decision Work Brief Rendered Intake-Routing Example](docs/conversation-understanding/decision-work-brief-rendered-deploy-assisted-intake-routing-v0.md) | PR121A's rendered third-case Markdown example, generated from an embedded `lolla.decision_work_brief.v0` object without checking in local-private text. |
| [Decision Work Brief Three-Case Pattern Review](docs/conversation-understanding/decision-work-brief-three-case-pattern-review-v0.md) | PR122's three-case pattern review over the cofounder, launch-beta, and intake-routing briefs; it finds consistent action consequence but chooses `proceed_to_plain_language_renderer_patch` because the rendered language is still too internal for a board/customer reader. |
| [Decision Work Brief Plain-Language Renderer Patch](docs/conversation-understanding/decision-work-brief-plain-language-renderer-patch-v0.md) | PR123's renderer patch that regenerates all three existing examples with plain-language decision headings and moves source refs, section uncertainty, custody flags, and non-claims into a compact Evidence and limits section. |
| [Decision Work Brief Plain-Language Re-Review](docs/conversation-understanding/decision-work-brief-plain-language-rereview-v0.md) | PR124's rereview of the PR123 examples; it finds the surface readable enough for local-private adequacy comparison and gates to `proceed_to_local_private_adequacy_check`. |
| [Decision Work Brief Local-Private Adequacy Check](docs/conversation-understanding/decision-work-brief-local-private-adequacy-check-v0.md) | PR125's one-case read-only local-private shadow review on `launch-public-enterprise-beta`; it records `adequate_but_missing_private_nuance` without checking in private text and gates to a decision review. |
| [Decision Work Brief Expansion / Runtime Attachment Decision Gate](docs/conversation-understanding/decision-work-brief-expansion-runtime-decision-gate-v0.md) | PR126's conservative gate after PR124/PR125; it selects `run_more_local_private_adequacy_checks`, not runtime integration or product readiness. |
| [Decision Work Brief Conversation Interpretation Gap Map](docs/conversation-understanding/decision-work-brief-conversation-interpretation-gap-map-v0.md) | PR127's three-case map of desired conversation fields, classifying what is clear, partial, local-private-only, LLM-interpretable, human-review-dependent, or not currently captured; it gates to a target contract rather than a runtime extractor. |
| [Decision Work Conversation Interpretation Contract](docs/conversation-understanding/decision-work-conversation-interpretation-contract-v0.md) | PR128's docs/schema/test contract for future conversation interpretation fields, ownership, source status, privacy handling, deterministic custody, non-claims, and handoff shape without changing runtime extraction. |
| [Decision Work Conversation Interpretation Contract Schema](docs/conversation-understanding/decision-work-conversation-interpretation-contract-v0.json) | Machine-readable `lolla.decision_work_conversation_interpretation_contract.v0` target contract. It defines field groups and vocabularies, not populated case data, model calls, product proof, or agent authorization. |
| [Decision Work Conversation Interpretation Contract Packet Review](docs/conversation-understanding/decision-work-conversation-interpretation-contract-packet-review-v0.md) | PR129's feasibility review of the PR128 contract against current completed-run artifacts and PR115 packet surfaces; it finds source/status carriage exists but selects `build_offline_interpretation_packet` before any LLM read or runtime extraction. |
| [Decision Work Conversation Interpretation Offline Packet](docs/conversation-understanding/decision-work-conversation-interpretation-offline-packet-v0.md) | PR130's read-only packet builder for `lolla.decision_work_conversation_interpretation_packets.v0`: a source/status dossier over completed-run artifacts and PR128 field groups for future LLM or human interpretation, with no semantic field filling, raw/private content, model calls, runtime extraction, product proof, or agent authorization. |
| [Decision Work Conversation Interpretation Tiny Offline Read](docs/conversation-understanding/decision-work-conversation-interpretation-tiny-offline-read-v0.md) | PR131's first one-case provisional read over a generated PR130 packet for launch-beta: a small PR128 field subset with source refs, uncertainty, privacy limits, non-claims, no source-packet fixture, no raw/private content, no model calls, no product proof, and no runtime integration. |
| [Decision Work Conversation Interpretation Second Tiny Offline Read](docs/conversation-understanding/decision-work-conversation-interpretation-second-tiny-offline-read-v0.md) | PR132's second one-case provisional read over a generated PR130 packet for intake routing: the same tiny field subset works across a healthcare operations/deployment decision and gates to a reusable read schema, while keeping lost value and starting direction source-limited. |
| [Decision Work Conversation Interpretation Read Schema](docs/conversation-understanding/decision-work-conversation-interpretation-read-schema-v0.md) | PR133's `lolla.decision_work_conversation_interpretation_read.v0` schema contract for future offline interpretation reads, requiring source refs, uncertainty, privacy limits, human-review flags, non-claims, and no quality-label use without adding an interpreter or runtime extraction. |
| [Decision Work Conversation Interpretation Read Comparison](docs/conversation-understanding/decision-work-conversation-interpretation-read-comparison-v0.md) | PR134's comparison gate over the PR131 and PR132 reads; it finds stable action-consequence and non-proof fields, keeps lost value/source-depth limits explicit, and selects one narrow brief-enrichment test rather than another read or runtime integration. |
| [Decision Work Brief Interpretation Enrichment Test](docs/conversation-understanding/decision-work-brief-interpretation-enrichment-test-v0.md) | PR135's one-case enrichment test: creates a separate launch-beta enriched brief from the PR131 read, using only the PR134 feed-now fields and preserving uncertainty, source limits, and non-claims. |
| [Decision Work Brief Original vs Enriched Review](docs/conversation-understanding/decision-work-brief-original-vs-enriched-review-v0.md) | PR136's comparison gate over the original and enriched launch-beta briefs; it finds the enrichment useful enough to test on a second case without treating it as product proof. |
| [Decision Work Brief Second Enrichment Test](docs/conversation-understanding/decision-work-brief-second-enrichment-test-v0.md) | PR137's second enrichment test on the intake-routing brief from the PR132 read, with the same conservative field subset and no new interpretation read. |
| [Decision Work Brief Enriched Pattern Review](docs/conversation-understanding/decision-work-brief-enriched-pattern-review-v0.md) | PR138's two-enriched-brief pattern review; it recommends a future enrichment-rules contract and explicitly does not implement PR139 or runtime integration. |
| [Decision Work Brief Enrichment Rules Contract](docs/conversation-understanding/decision-work-brief-enrichment-rules-contract-v0.md) | PR139's contract for which interpreted fields may enter the user-facing brief, which fields stay evidence-only, which concepts are forbidden, and what any offline builder must preserve. |
| [Decision Work Brief Enrichment Rules Contract JSON](docs/conversation-understanding/decision-work-brief-enrichment-rules-contract-v0.json) | Machine-readable `lolla.decision_work_brief_enrichment_rules_contract.v0` rules contract for offline enrichment. |
| [Decision Work Brief Offline Enriched Builder](docs/conversation-understanding/decision-work-brief-offline-enriched-builder-v0.md) | PR140's deterministic offline builder and CLI for creating separate enriched Markdown from an existing brief, interpretation read, and PR139 rules contract, without model calls or runtime changes. |
| [Decision Work Brief Builder-Enriched Launch Beta](docs/conversation-understanding/decision-work-brief-builder-enriched-launch-public-enterprise-beta-v0.md) | PR140's builder-generated launch-beta enriched output, separate from the hand-built enriched example. |
| [Decision Work Brief Builder-Enriched Intake Routing](docs/conversation-understanding/decision-work-brief-builder-enriched-deploy-assisted-intake-routing-v0.md) | PR140's builder-generated intake-routing enriched output, separate from the hand-built enriched example. |
| [Decision Work Brief Enriched Builder Output Review](docs/conversation-understanding/decision-work-brief-enriched-builder-output-review-v0.md) | PR141's review comparing builder-generated enriched briefs against the hand-built examples; it selects `proceed_to_builder_rule_patch` because the output is safe but still too templated. |
| [Decision Work Brief Enrichment Builder Rule Patch](docs/conversation-understanding/decision-work-brief-enrichment-builder-rule-patch-v0.md) | PR142's deterministic builder-language patch; it regenerates the two builder-enriched outputs with less repetitive wording while preserving PR139 field rules, uncertainty, source limits, and non-claims. |
| [Decision Work Brief Builder Patch Review](docs/conversation-understanding/decision-work-brief-enrichment-builder-rule-patch-review-v0.md) | PR143's review of the patched builder outputs; it selects `proceed_to_offline_system_closure_gate`, not another builder case or runtime integration. |
| [Decision Work Brief Offline System Closure Gate](docs/conversation-understanding/decision-work-brief-offline-system-closure-gate-v0.md) | PR144's closure decision over the PR114-PR143 offline surface; it selects `package_pr114_pr144` while preserving the no-runtime, no-product-proof boundary. |
| [Decision Work Brief PR114-PR144 Packaging Gate](docs/conversation-understanding/decision-work-brief-pr114-pr144-packaging-gate-v0.md) | PR145's package gate and manifest for the offline Decision Work Brief evidence surface: file groups, staging list, do-not-stage warnings, validation checklist, useful signal, unresolved risk, and explicit non-claims. |
| [Decision Work Brief Additional Local-Private Adequacy Checks](docs/conversation-understanding/decision-work-brief-additional-local-private-adequacy-checks-v0.md) | PR146's safe-conclusions-only local-private adequacy check on the cofounder and intake-routing cases; it finds no major contradiction, keeps private nuance as the main risk, and recommends a third builder case rather than runtime integration. |
| [Decision Work Brief Third Builder Case](docs/conversation-understanding/decision-work-brief-third-builder-case-v0.md) | PR147's feasibility gate for the cofounder builder case; it blocks builder output because the case lacks a PR133-shaped interpretation read and recommends creating that read first. |
| [Decision Work Conversation Interpretation Third Tiny Offline Read](docs/conversation-understanding/decision-work-conversation-interpretation-third-tiny-offline-read-v0.md) | PR147A's builder-compatible cofounder interpretation read using the formal PR133 schema; it fills the small action-consequence field subset while keeping starting direction, option status, and lost value source-limited. |
| [Decision Work Brief Third Builder Case Output](docs/conversation-understanding/decision-work-brief-third-builder-case-output-v0.md) | PR148's deterministic builder output review for the cofounder case; it creates the third builder-enriched brief, preserves uncertainty and non-claims, notes a mild template weakness, and gates to a three-builder-case pattern review. |
| [Decision Work Brief Three Builder Case Pattern Review](docs/conversation-understanding/decision-work-brief-three-builder-case-pattern-review-v0.md) | PR149's pattern review across the three builder-generated enriched briefs; it finds the builder stable enough for offline evidence review and selects `proceed_to_human_review_intake_plan`, not runtime integration. |
| [Decision Work Brief Human Review Intake Plan](docs/conversation-understanding/decision-work-brief-human-review-intake-plan-v0.md) | PR150's intake plan for future human review of the three builder-generated enriched briefs; it defines reviewer questions, stop conditions, allowed outcomes, and source-depth checks while preserving that no human validation, product proof, runtime integration, scoring, or agent authorization has occurred. |
| [Decision Work Brief Human Review Pilot Scaffold](docs/conversation-understanding/decision-work-brief-human-review-pilot-scaffold-v0.md) | PR151's runnable but blank human-review pilot scaffold for the three builder-generated enriched briefs, with reviewer instructions, a response template, stop conditions, allowed pilot outcomes, and no Codex-filled human answers. |
| [Decision Work Brief Human Review Response Template](docs/conversation-understanding/decision-work-brief-human-review-response-template-v0.json) | Machine-readable blank response template for a future human reviewer; all case answers remain `not_reviewed`, `null`, or empty until a real reviewer fills them. |
| [Decision Work Brief Human Review Pilot Readiness Gate](docs/conversation-understanding/decision-work-brief-human-review-pilot-readiness-gate-v0.md) | PR152's readiness gate: the pilot packet and blank template are ready for a real human reviewer, but no human response has been collected and runtime/customer-facing use remains blocked. |
| [Decision Work Brief Human Review Awaiting Response Gate](docs/conversation-understanding/decision-work-brief-human-review-awaiting-response-gate-v0.md) | PR153's pause gate: no real human response exists yet, so the next unblocked evidence step is a human-filled PR151 response template rather than Codex-substituted review. |
| [Decision Work Automatic Triage Contract](docs/conversation-understanding/decision-work-automatic-triage-contract-v0.md) | PR154's docs/schema/test contract for the future automatic triage layer: route attention and escalation without scoring answer quality, approving advice, proving product value, claiming human validation, or authorizing action. |
| [Decision Work Automatic Triage Contract JSON](docs/conversation-understanding/decision-work-automatic-triage-contract-v0.json) | Machine-readable `lolla.decision_work_automatic_triage_contract.v0` contract defining triage categories, fields, route values, custody flags, calibration role, and non-claims. |
| [Decision Work Automatic Triage Packet Builder](docs/conversation-understanding/decision-work-automatic-triage-packet-builder-v0.md) | PR155's deterministic offline packet builder for future triage: it gathers refs, custody flags, triage field policy, future tasks, and known limits over the three builder-enriched cases without filling semantic triage fields. |
| [Decision Work Automatic Triage Provisional Read](docs/conversation-understanding/decision-work-automatic-triage-provisional-read-v0.md) | PR156's Codex-assisted provisional read over one PR155 packet shape, routing launch-beta, intake-routing, and cofounder/governance cases toward different source-depth, domain, overtrust, agent-inspection, and runtime-blocker concerns without scoring or approving advice. |
| [Decision Work Brief Offline v1 Closure Gate](docs/conversation-understanding/decision-work-brief-offline-v1-closure-gate-v0.md) | PR157's closure gate selects `package_offline_v1`, claiming only functional offline v1 with explicit limitations: not runtime integration, not customer readiness, not human validation, not product proof, not answer-quality scoring, and not action authorization. |
| [Decision Work Brief Offline v1 Package Gate](docs/conversation-understanding/decision-work-brief-offline-v1-package-gate-v0.md) | PR158's package gate and manifest for Offline v1, referencing the PR114-PR144 base package and explicitly adding PR145-PR157 human-calibration, third-case, automatic-triage, closure, and package-gate artifacts. |
| [Decision Work Brief Runtime Attachment PRD](docs/conversation-understanding/decision-work-brief-runtime-attachment-prd-v0.md) | Planning bridge after Offline v1: decides when a future brief should run, what the user sees, what another agent sees, what blocks generation, and why the first runtime-safe slice should be a flagged post-archive attachment path rather than full automation. |
| [Decision Work Brief Runtime Attachment Contract](docs/conversation-understanding/decision-work-brief-runtime-attachment-contract-v0.md) | PR160's contract for a default-off, post-archive-only Decision Work Brief attachment path, including modes, states, blockers, receipts, handoff refs, privacy policy, custody flags, and non-claims. |
| [Decision Work Brief Runtime Sidecar Contract](docs/conversation-understanding/decision-work-brief-runtime-sidecar-v0.md) | PR161's sidecar/artifact-location contract for `decision_work/` bundle artifacts beside a completed run, with blocked/deferred/failed states and no raw/private default export. |
| [Decision Work Brief Runtime Bundle Generator](docs/conversation-understanding/decision-work-brief-runtime-bundle-generator-v0.md) | PR162's manual post-archive CLI and module for creating checked-in-safe attachment bundles from completed runs and explicitly supplied safe brief artifacts. |
| [Decision Work Brief Runtime Eligibility Gate](docs/conversation-understanding/decision-work-brief-runtime-eligibility-gate-v0.md) | PR163's deterministic blocker and routing gate, producing generated, blocked, deferred, and agent-only states from artifact status, custody flags, and explicit triage routes. |
| [Decision Work Brief Runtime Receipt](docs/conversation-understanding/decision-work-brief-runtime-receipt-v0.md) | PR164's short user receipt renderer for available, caveated, agent-only, blocked, deferred, failed-closed, and disabled attachment states. |
| [Decision Work Brief Agent Handoff](docs/conversation-understanding/decision-work-brief-agent-handoff-v0.md) | PR165's checked-in-safe agent inspection packet, carrying refs, source status, missingness, uncertainty, route outputs, privacy status, and non-claims without action authorization. |
| [Decision Work Brief Flagged Post-Archive Runtime Hook](docs/conversation-understanding/decision-work-brief-flagged-post-archive-runtime-hook-v0.md) | PR166's first runtime-attached behavior: `scripts/archive_run.py` can write a `decision_work/` sidecar only when `LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE` is explicitly enabled. |
| [Decision Work Brief Runtime Attachment Review](docs/conversation-understanding/decision-work-brief-runtime-attachment-review-v0.md) | PR167's review of PR160-PR166, covering available, blocked, caveated/agent-only, default-off, receipt, handoff, and fail-closed behavior. |
| [Decision Work Brief Runtime-Attached Internal v1 Package Gate](docs/conversation-understanding/decision-work-brief-runtime-attached-v1-package-gate-v0.md) | PR167's package gate and manifest for runtime-attached internal v1: functional behind a flag for completed clean runs, not customer readiness, product proof, human validation, answer-quality scoring, advice correctness, or action authorization. |
| [Decision Work Brief Runtime-Attached Internal v1 Follow-up Plan](docs/conversation-understanding/decision-work-brief-runtime-attached-v1-followup-plan-v0.md) | PR168's choice gate after runtime-attached internal v1; it finds the hook mechanically attached but input-supply-limited and selects `safe_brief_supply_planning` as the next PR. |
| [Decision Work Brief Runtime Safe Brief Supply Plan](docs/conversation-understanding/decision-work-brief-runtime-safe-brief-supply-plan-v0.md) | PR169's input-supply gate; it classifies which runtime attachment inputs are safe, manual, checked-in-safe only, future interpretation-dependent, or unavailable, and selects a safe supply resolver contract for PR170. |
| [Decision Work Brief Runtime Safe Supply Resolver Contract](docs/conversation-understanding/decision-work-brief-runtime-safe-supply-resolver-contract-v0.md) | PR170's contract for the future deterministic supply resolver: modes, statuses, input types, unsafe exclusions, output shape, custody flags, and PR171 implementation boundary without runtime interpretation or hook changes. |
| [Decision Work Brief Runtime Safe Supply Resolver](docs/conversation-understanding/decision-work-brief-runtime-safe-supply-resolver-v0.md) | PR171's deterministic resolver and CLI for validating safe refs, redacting local paths, excluding unsafe inputs, and emitting feedability status before the manual bundle consumes those refs. |
| [Decision Work Brief Runtime Bundle Resolver Integration](docs/conversation-understanding/decision-work-brief-runtime-bundle-resolver-integration-v0.md) | PR172's manual-bundle integration: the bundle CLI can consume `--resolver-output`, preserve resolver status in attachment status and handoff, and produce available, agent-only, deferred, queued, local-private-required, or blocked receipts without changing the runtime hook. |
| [Decision Work Brief Runtime Hook Resolver Wiring](docs/conversation-understanding/decision-work-brief-runtime-hook-resolver-wiring-v0.md) | PR173's default-off hook wiring: when `LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE` is enabled, the post-archive hook builds resolver output, passes it to the resolver-aware bundle, and writes available, agent-only, deferred, blocked, or failed-closed sidecars without model calls or default-on behavior. |
| [Decision Work Brief Runtime Hook Resolver Fixture Review](docs/conversation-understanding/decision-work-brief-runtime-hook-resolver-fixture-review-v0.md) | PR174's review-only fixture gate over the PR173 hook sidecars; it confirms flag-off, deferred, available, agent-only, blocked, privacy-blocked, and failed-closed states and selects a checked-in-safe case registry next. |
| [Decision Work Brief Runtime Checked-In Safe Case Registry](docs/conversation-understanding/decision-work-brief-runtime-checked-in-safe-case-registry-v0.md) | PR175's deterministic safe-ref registry for the three known Decision Work Brief examples; registry mode lets the resolver feed the manual bundle without manual env refs, while remaining curated-example-only and not a general live-run solution. |
| [Decision Work Brief Runtime Hook Registry Fixture Review](docs/conversation-understanding/decision-work-brief-runtime-hook-registry-fixture-review-v0.md) | PR176's review-only registry fixture pass; it confirms the three registry entries can drive generated temp hook sidecars through the resolver-aware bundle seam and selects a runtime-attached internal v1 package refresh next. |
| [Decision Work Brief Runtime-Attached Internal v1 Package Refresh](docs/conversation-understanding/decision-work-brief-runtime-attached-internal-v1-package-refresh-v0.md) | PR177's package refresh for PR160-PR176: internal default-off post-archive sidecar functionality when safe refs are supplied manually or through registry fixtures, with arbitrary-run semantic supply, customer readiness, validation, scoring, proof, and action authorization explicitly unclaimed. |
| [Decision Work Automatic Semantic Supply PRD](docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md) | PR178's planning spine after PR216 merged runtime-attached internal v1. It defines how new completed runs should enter an offline interpretation queue, produce validated interpretation/triage artifacts, feed the existing brief/enrichment/rendering path, and update the sidecar without direct runtime interpretation or product-proof claims. |
| [Decision Work Offline Interpretation Queue Contract](docs/conversation-understanding/decision-work-offline-interpretation-queue-contract-v0.md) | PR179's docs/schema/tests-only queue contract for automatic semantic supply. It defines queue item/result shapes, statuses, privacy modes, custody flags, validation requirements, and non-claims without adding a queue runner, model calls, generated reads, runtime behavior, or sidecar updates. |
| [Decision Work Offline Interpretation Queue Builder](docs/conversation-understanding/decision-work-offline-interpretation-queue-builder-v0.md) | PR180's deterministic queue item builder. It prepares checked-in-safe queue items from completed run refs and optional PR130 packet refs, preserving status and non-claims without filling semantic fields, calling models, mutating archives, or updating runtime sidecars. |
| [Decision Work Operator/Codex Interpretation Prompt Packet](docs/conversation-understanding/decision-work-operator-codex-interpretation-prompt-packet-v0.md) | PR181's prompt/input packet contract for a future operator or Codex session to fill a bounded PR133 interpretation read. It adds no generated read, generated-read intake, repo-side provider call, runtime behavior, proof claim, scoring, or action authorization. |
| [Decision Work Generated Interpretation Read Intake](docs/conversation-understanding/decision-work-generated-interpretation-read-intake-v0.md) | PR182's strict intake validator for externally supplied Decision Work interpretation reads. It validates schema compatibility, source refs, uncertainty, privacy limits, custody flags, and non-claims before any later offline brief, enrichment, triage, resolver, or sidecar path can consume the read. |
| [Decision Trail Readiness Audit](docs/conversation-understanding/decision-trail-readiness-audit-v0.md) | Internal audit of what Lolla currently captures from conversations, what is merged, what is only designed, and what is still missing before a first-class Decision Trail report. |
| [Decision Trail PR86-PR89 PRD](docs/conversation-understanding/decision-trail-pr86-pr89-prd-v0.md) | Staged implementation plan for the Decision Trail report: schema, read-only exporter, fixture review, and interpretation-gap decision gate. |
| [Decision Trail Report PRD](docs/conversation-understanding/decision-trail-report-prd-v0.md) | PR86's report contract: what the Decision Trail report is, field ownership, safe/private modes, redaction versus missingness, trace compatibility, validation, and non-claims. |
| [Decision Trail Report Schema](docs/conversation-understanding/decision-trail-report-v0.json) | Machine-readable `lolla.decision_trail_report.v0` schema for the future read-only exporter, with shared semantic section shape and custody constraints. |
| [PR86 Decision Trail Goal Prompt](docs/conversation-understanding/decision-trail-pr86-goal-prompt-v0.md) | Ready-to-paste `/goal` handoff for a fresh coder session to implement PR86 only: Decision Trail report PRD and schema, with no exporter or runtime integration. |
| [PR87 Decision Trail Goal Prompt](docs/conversation-understanding/decision-trail-pr87-goal-prompt-v0.md) | Ready-to-paste `/goal` handoff for a fresh coder session to implement PR87 only: a read-only Decision Trail exporter over completed artifacts. |
| [Decision Trail Read-Only Exporter](docs/conversation-understanding/decision-trail-readonly-exporter-v0.md) | PR87's deterministic exporter for sparse `lolla.decision_trail_report.v0` reports from completed run directories, with checked-in-safe artifact reading and explicit missingness. |
| [PR88 Decision Trail Goal Prompt](docs/conversation-understanding/decision-trail-pr88-goal-prompt-v0.md) | Ready-to-paste `/goal` handoff for a fresh coder session to implement PR88 only: fixture review of exported Decision Trail reports for usefulness, missingness, readability, and overtrust risk. |
| [Decision Trail Export Fixture Review](docs/conversation-understanding/decision-trail-export-fixture-review-v0.md) | PR88's safe-fixture-only review of exported Decision Trail reports, finding the custody/missingness shell useful but too sparse for the full Decision Trail product without later interpretation. |
| [Decision Trail Interpretation Gap Decision](docs/conversation-understanding/decision-trail-interpretation-gap-decision-v0.md) | PR89's docs-only decision gate: keep the custody shell, reject runtime/broad-IR expansion for now, and pursue narrow offline LLM specialist contracts next. |
| [PR90 Decision Trail Goal Prompt](docs/conversation-understanding/decision-trail-pr90-goal-prompt-v0.md) | Ready-to-paste `/goal` handoff for a fresh coder session to implement PR90 only: docs/schema contracts for narrow offline Decision Trail interpretation specialists. |
| [Decision Trail Specialist Contracts](docs/conversation-understanding/decision-trail-specialist-contracts-v0.md) | PR90's docs/schema contract for four narrow offline Decision Trail interpretation specialists: conversation shape, likely actions, friction/lost value, and conservative fan-in. |
| [Decision Trail Specialist Packet Builder](docs/conversation-understanding/decision-trail-specialist-packet-builder-v0.md) | PR91's read-only packet builder for shaping PR88 fixture-review context into checked-in-safe input packets for the four PR90 specialist contracts. |
| [Decision Trail Specialist Trap Set](docs/conversation-understanding/decision-trail-specialist-trap-set-v0.md) | PR92's checked-in-safe trap fixtures for testing whether future Decision Trail specialist passes resist over-inference, overtrust, lost-value blindness, and fan-in smoothing. |
| [Decision Trail Specialist Dry Run](docs/conversation-understanding/decision-trail-specialist-dry-run-v0.md) | PR93's Codex-assisted provisional dry run over PR92 traps and the tiny PR91 packet surface, checking review discipline without creating specialist outputs or product proof. |
| [Decision Trail Specialist Path Decision](docs/conversation-understanding/decision-trail-specialist-path-decision-v0.md) | PR94's docs-only decision gate selecting local-private Decision Trail packet mode as the next slice, while rejecting broader checked-in-safe batches, runtime integration, and broad IR work for now. |
| [Decision Trail Local-Private Packet Mode](docs/conversation-understanding/decision-trail-local-private-packet-mode-v0.md) | PR95's explicit local-private packet mode for operator-selected completed run directories, with output-path guards, metadata-only/include-text policies, unsafe-for-commit marking, and no specialist-output generation. |
| [Decision Trail Local-Private Packet Smoke Review](docs/conversation-understanding/decision-trail-local-private-packet-smoke-review-v0.md) | PR96's local smoke/review of PR95 packets over real completed runs and synthetic include-text guardrails, recommending only a tiny specialist-output pilot next. |
| [Decision Trail Local-Private Specialist Output Pilot](docs/conversation-understanding/decision-trail-local-private-specialist-output-pilot-v0.md) | PR97's one-case local-private specialist-output pilot, filling all four PR90 roles by checked-in summary only while keeping private packet content out of the repo. |
| [Decision Trail Specialist Output Pilot Review](docs/conversation-understanding/decision-trail-specialist-output-pilot-review-v0.md) | PR98's review/decision gate over PR97, blocking broader specialist batches until contracts and packet metadata are patched. |
| [Decision Trail Specialist Contract And Packet Patch](docs/conversation-understanding/decision-trail-specialist-contract-and-packet-patch-v0.md) | PR99's additive patch to the specialist contracts and packet metadata, adding source-scope, truncation, vanilla-overlap, severity, assistant-influence, downgrade-trigger, and retention-policy fields before any second one-case pilot. |
| [Decision Trail Second One-Case Specialist Pilot](docs/conversation-understanding/decision-trail-second-one-case-specialist-pilot-v0.md) | PR100's second local-private specialist-output pilot using the PR99 fields, finding partial usefulness because material vanilla overlap should downgrade the read before any broad batch. |
| [Decision Trail Specialist Pilot Comparison Gate](docs/conversation-understanding/decision-trail-specialist-pilot-comparison-gate-v0.md) | PR101's checked-in-summary comparison of PR97 and PR100, deciding broad batches are not ready and allowing at most one diversity-targeted third pilot. |
| [Decision Trail Third One-Case Diversity Pilot](docs/conversation-understanding/decision-trail-third-one-case-diversity-pilot-v0.md) | PR102's deployment-controls specialist-output pilot, preserving material vanilla overlap while surfacing noise-reduction and operating-load friction as the new useful signal. |
| [Decision Trail Specialist Pilot Phase Closure Gate](docs/conversation-understanding/decision-trail-specialist-pilot-phase-closure-gate-v0.md) | PR103's checked-in-summary closure gate over PR97, PR100, and PR102: close one-case pilots, block a fourth pilot and broad batch, and recommend human-review intake or pause. |
| [Decision Trail Human Review Intake Packet](docs/conversation-understanding/decision-trail-human-review-intake-packet-v0.md) | PR104's future-human-review intake packet over PR97, PR100, and PR102, with blank correction fields and an explicit pause until human review capacity returns. |
| [Evaluation Flywheel Action Plan](docs/evals/evaluation-flywheel-action-plan-v0.md) | The current action map for turning real traces into human labels, fixtures, deterministic checks, and later calibrated binary judges without drifting into generic scoring. |
| [Current System Capabilities](docs/evals/current-system-capabilities-v0.md) | A plain-language map of what the current system can do, which recorded cases show it, how the layers work together, and how it helps us avoid brittle evaluation. |
| [Product Delta Evidence And Interpretation Adequacy](docs/evals/product-delta-evidence-and-interpretation-adequacy-v0.md) | The post-PR70 product-readiness bridge: prove decision-useful deltas against actual vanilla strong-model conversations, and treat conversation interpretation quality as load-bearing. |
| [Product Delta Evidence Thesis](docs/evals/product-delta-evidence-thesis-v0.md) | PR71's docs-only thesis for the lower-claim Product Delta Evidence phase: Codex-assisted provisional review scaffolding, not human validation, product proof, scoring, judging, or agent approval. |
| [Vanilla-vs-Lolla Provisional Review Protocol](docs/evals/vanilla-vs-lolla-provisional-review-protocol-v0.md) | PR72's protocol and schema for comparing actual vanilla strong-model advice with Lolla revised answers while keeping all subjective findings provisional. |
| [Codex-Assisted Paired Review Dry Run](docs/evals/codex-assisted-paired-review-dry-run-v0.md) | PR73's eight-case paraphrase-only dry run of the provisional protocol over existing safe artifacts, including an inconclusive case and human follow-up questions. |
| [Provisional Product Delta Failure Taxonomy](docs/evals/provisional-product-delta-failure-taxonomy-v0.md) | PR74's provisional taxonomy for product-delta, interpretation, and review-process failures, explicitly not automatic labels, judge calibration data, scoring, or product proof. |
| [Product Delta Eval Readiness And Provisional Run](docs/evals/product-delta-eval-readiness-and-provisional-run-v0.md) | PR75's read-only generated report over 14 existing cases: 12 ready for Codex provisional review, one private-content-only partial, and one degraded-run block, with PR72-shaped shells and no semantic judgment. |
| [Codex-Assisted Product Delta Batch](docs/evals/codex-assisted-product-delta-batch-v0.md) | PR76's Codex-assisted provisional semantic fill over the 12 PR75-ready shells, with mixed candidate reads, lost-value notes, interpretation-adequacy caveats, and no human-validation claim. |
| [Product Delta Provisional Report](docs/evals/product-delta-provisional-report-v0.md) | PR77's state-of-evidence report over PR75 and PR76: 14 readiness cases, 12 provisional semantic reads, recurring structural deltas, lost-value risks, interpretation concerns, and explicit non-proof boundaries. |
| [Product Delta Evidence Boundary Lint](docs/evals/product-delta-evidence-boundary-lint-v0.md) | PR78's deterministic read-only lint for Product Delta artifacts: blocks metadata, field, taxonomy, privacy, and non-claim drift without judging answer quality or touching runtime. |
| [Context-Engineered Provisional Review Architecture](docs/evals/context-engineered-provisional-review-architecture-v0.md) | PR79's docs-only architecture for future bounded specialist reads: decompose LLM-assisted interpretation, preserve disagreement, pass PR78 lint, and avoid judges, scores, runtime integration, and agent approval. |
| [Product Delta Specialist Review Contracts](docs/evals/product-delta-specialist-review-contracts-v0.md) | PR80's docs/schema contracts for the bounded specialist reads named in PR79, with typed lower-claim outputs and no packet builder, review batch, fan-in execution, scoring, judging, or runtime integration. |
| [Product Delta Specialist Packet Builder](docs/evals/product-delta-specialist-packet-builder-v0.md) | PR81's read-only packet builder for creating checked-in-safe per-specialist input packets from existing Product Delta artifacts, with no specialist answers, model calls, archive mutation, scoring, judging, or runtime integration. |
| [Provisional Reviewer Trap Set](docs/evals/provisional-reviewer-trap-set-v0.md) | PR82's checked-in-safe trap fixtures for testing whether future specialist review resists thin context, length bias, caution theater, lost value, disagreement smoothing, and overclaim hardening before real specialist batches. |
| [Codex-Assisted Specialist Review Batch](docs/evals/codex-assisted-specialist-review-batch-v0.md) | PR83's first provisional specialist-review batch: trap discipline plus two checked-in-safe real cases, including one downgrade from PR76 material to partial, with no human-validation or product-proof claim. |
| [Product Delta Fan-In / Disagreement Report](docs/evals/product-delta-fan-in-disagreement-report-v0.md) | PR84's static provisional report over PR76 and PR83: preserves the one PR83 downgrade, both lost-value and interpretation-adequacy concern surfaces, trap behavior counts, and thinness limits without adding new semantic reads. |
| [Product Delta PR71-PR84 Packaging Gate](docs/evals/product-delta-pr71-pr84-packaging-gate-v0.md) | PR85's packaging gate for the Product Delta Evidence phase: manifest PR71-PR84 files, verify boundary metadata/source refs/lint coverage, and make the downgrade plus two-case thinness easy to inspect before explicit packaging. |
| [Current State Anti-Drift Handoff](docs/evals/current-state-anti-drift-handoff-v0.md) | PR45's compact fresh-session map, updated by PR70, of the PR30-PR70 eval/accountability chain, current corpus evidence, non-goals, and the next approval gates. |
| [Semantica-Inspired Accountability PRD](docs/conversation-understanding/semantica-inspired-accountability-prd-v0.md) | PR55's docs-only plan for borrowing accountability primitives such as decision records, provenance maps, conflict registers, doctor/preflight, and case graph views without building graph DB, embeddings, memory, policy, compliance, judge, or scoring products. |
| [Lolla Doctor / Preflight Plan](docs/evals/lolla-doctor-preflight-plan-v0.md) | PR56's docs-only plan for a future read-only doctor command that checks local runtime wiring, archive paths, helper scripts, provider/cost readiness, review manifests, high-stakes evidence visibility, output-path safety, and privacy without running `$lolla`, calling models, or mutating archives. |
| [Lolla Doctor Read-Only CLI](docs/evals/lolla-doctor-readonly-cli-v0.md) | PR57's implementation note for `python3 scripts/lolla_doctor.py`, a local deterministic preflight command that emits `lolla.doctor_report.v0` without running `$lolla`, calling models, reading archive payloads, mutating archives, or judging answer quality. |
| [Audit Decision Record Design](docs/conversation-understanding/audit-decision-record-v0.md) | PR58's docs/JSON design for `lolla.audit_decision_record.v0`, a paraphrase-only accountability projection over existing artifacts that maps decision deltas to PR31 labels without becoming an exporter, judge, score, memory layer, or conversation-understanding IR. |
| [Audit Decision Record Fixtures](docs/evals/audit-decision-record-fixtures-v0.md) | PR59's docs/eval-only fixture review of six paraphrase-only audit decision records, confirming the shape is useful before any exporter, runtime integration, labels, scores, or judge. |
| [Provenance Map Design](docs/conversation-understanding/provenance-map-v0.md) | PR60's docs/JSON design for `lolla.provenance_map.v0`, a local artifact-lineage map that borrows entity/activity/agent vocabulary without RDF, W3C compliance claims, graph DB, memory, runtime integration, or answer-quality scoring. |
| [Review Conflict Register Design](docs/evals/review-conflict-register-v0.md) | PR61's docs/JSON design for `lolla.review_conflict_register.v0`, a human-review-owned register of unresolved tensions that does not resolve conflicts, score severity into actions, enforce policy, or judge answer quality. |
| [Case Graph Export Design](docs/conversation-understanding/case-graph-export-v0.md) | PR62's docs/JSON design for `lolla.case_graph.v0`, a future run-local case graph export/view shape that does not implement an exporter, graph DB, memory, GraphRAG, entity resolution, runtime integration, or answer-quality scoring. |
| [Accountability View Fixtures](docs/evals/accountability-view-fixtures-v0.md) | PR63's paraphrase-only fixture pack showing audit decision record, provenance map, review conflict register, and case graph views together on three reviewed cases before any exporter or runtime feature exists. |
| [Accountability View Fixture Review](docs/evals/accountability-view-fixture-review-v0.md) | PR64's docs/eval-only review of the PR63 bundles, finding all three useful while recommending only `audit_decision_record` for a later exporter-design decision. |
| [Accountability Implementation Decision Gate](docs/evals/accountability-implementation-decision-gate-v0.md) | PR65's docs-only decision gate choosing outcome A: recommend a future read-only `audit_decision_record` exporter while holding provenance, conflict-register, and case-graph implementation. |
| [Audit Decision Record Read-Only Exporter](docs/evals/audit-decision-record-readonly-exporter-v0.md) | PR66's read-only local exporter for `lolla.audit_decision_record.v0`, built from structured/custody-safe artifacts without running `$lolla`, calling models, mutating archives, reading raw transcript/memo/revised-answer content, inferring labels, scoring advice, or changing runtime behavior. |
| [Audit Decision Record Export Smoke Review](docs/evals/audit-decision-record-export-smoke-review-v0.md) | PR67's docs/review slice over PR66 exporter outputs, finding the records useful and safe while recommending PR68 schema/exporter refinement for clearer empty PR31 bucket semantics before archive integration or automatic generation. |
| [Audit Decision Record Schema / Exporter Refinement](docs/evals/audit-decision-record-schema-exporter-refinement-v0.md) | PR68's refinement of the same `lolla.audit_decision_record.v0` exporter output, adding PR31 population policy, per-bucket statuses, nested buckets, and semantic-field empty-meaning metadata without inferring labels, scoring advice, mutating archives, or changing runtime behavior. |
| [Audit Decision Record Export Review Re-Run](docs/evals/audit-decision-record-export-review-rerun-v0.md) | PR69's docs/review rerun over refined PR68 exporter outputs, finding empty PR31 buckets and semantic empty fields clear as non-claims before PR70 closed the machinery lane. |
| [Audit / Accountability Machinery Closure Gate](docs/evals/audit-accountability-machinery-closure-gate-v0.md) | PR70's docs-only closure gate declaring the audit/accountability machinery done enough for now and shifting the next phase to Product Delta Evidence instead of more artifacts or archive integration. |
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
- Current Decision Trail state as of PR104: the runtime produces completed run
  artifacts; the offline Decision Trail lane can export sparse reports and
  build checked-in-safe or explicit local-private specialist packets; PR97
  shows one local-private include-text packet can support all four narrow
  specialist-output shapes by checked-in summary only; PR98 blocked broader use
  until contracts and packet metadata were patched; PR99 applies that patch;
  PR100 uses the patched shape on one additional case and records a
  partial-usefulness read; PR101 compares PR97 and PR100 and keeps broad
  specialist-output batches blocked; PR102 uses the one allowed
  diversity-targeted deployment-controls pilot; PR103 closes the one-case
  pilot phase and blocks a fourth pilot or broad batch; PR104 packages the
  three pilots into a future-human-review intake packet with blank correction
  fields. The next conservative move is pause until human review capacity
  returns. No Product Delta eval, Decision Trail report, specialist output, or
  fan-in is triggered automatically by `$lolla`.
- PR95 local-private packets are a source-access step, not a product verdict.
  `metadata_only` records availability, `include_text` copies capped private
  text into an unsafe-for-commit local output, and both modes still stop before
  likely-action, option, stakeholder, value, assistant-influence,
  useful/noisy-friction, lost-value, and fan-in conclusions.
- PR96 smoke-reviewed that packet path. Metadata-only packets worked over two
  real completed runs without copying raw/private content, and include-text
  worked mechanically with unsafe-for-commit marking.
- PR97 filled a tiny one-case local-private specialist-output pilot. It made
  the likely-action delta, lost-value risk, and fan-in tension more concrete
  than the sparse checked-in-safe shell, but it is still Codex-assisted,
  unvalidated, local-private, and not product proof.
- PR98 reviewed that pilot and decided the next Decision Trail step should be a
  PR99 contract/packet patch before any second one-case pilot, broad batch, or
  runtime integration.
- PR99 patched the specialist contracts and packets with source-scope,
  truncation, vanilla-overlap, lost-value severity, assistant-influence source
  status, fan-in downgrade triggers, and local-private retention policy
  metadata.
- PR100 used that patched shape on the `accept-founding-engineer-role` case.
  The strongest signal is discipline rather than positivity: `vanilla_overlap_read`
  is `material_overlap_candidate`, so the net read is partial usefulness.
  PR101 then compared PR97 and PR100 before any third pilot or broad batch.
- PR101 compared PR97 and PR100 using checked-in summaries only. It decides
  broad specialist-output batches are not ready and allows at most one
  diversity-targeted third one-case pilot before stopping, simplifying, or
  preparing human-review intake.
- PR102 used that one diversity-targeted pilot on the
  `deploy-assisted-intake-routing` case. It records a partial-usefulness read
  with a new useful signal: reduce noisy gate bloat and make admin operating
  load part of safety.
- PR103 closes the specialist-pilot phase. It compares PR97, PR100, and PR102
  by checked-in summaries only, blocks a fourth one-case pilot and broad batch,
  and recommends PR104 Human Review Intake Packet v0 or pause if human review
  capacity is unavailable.
- PR104 packages PR97, PR100, and PR102 into a future-human-review intake
  packet. It leaves all human correction fields blank, records
  `human_fields_filled: false`, and makes pause the correct next state until a
  reviewer can fill or reject the packet.
- Pressure-check agents are rested by default. If explicitly enabled, they start only after the updated position is persisted and the V60 ledger validates.
- The pre-Step-6 shadow portfolio hook is default-off and shadow-only; it records evidence but never changes visible output.
- The archive currently copies the core/optional artifact set, including live transcript, operator log, run-event log, private ledgers, memo fields, optional usefulness/outcome reviews, and optional `control_input.json` when present. It also generates `agent_result.json`, the compact agent-facing handoff; optional `control_result.json`, the control-plane wrapper; `extraction_adequacy_report.json`, the deterministic report for current extraction/provenance preservation across `conversation.txt -> extraction.json -> ConversationContext -> ConversationIR`; `evaluation.json`, the deterministic run-readiness receipt; and `reasoning_trace.json`, a local-only manifest that indexes artifacts by path/hash and adds capture-adequacy, optional control-plane references, reasoning-lens, model-call, private-custody, and trace-adequacy metadata.
- The June 24 accountability pass added run lifecycle events, operator-log separation for helper diagnostics, final-receipt Observatory liveness verification, trusted live-transcript finalization for merge-readiness checks, and graph-survival joins that preserve Lane 2 ledger uptake correctly.
- `scripts/export_reasoning_trace_dataset.py` scans archived `reasoning_trace.json` files and writes a JSONL corpus plus aggregate summary so repeated runs can be reviewed with an evals-style error-analysis workflow.
- `scripts/export_extraction_adequacy_corpus.py` scans archived runs and writes a local-only JSONL/manifest survey of extraction/provenance adequacy. It reuses existing `extraction_adequacy_report.json` files, can build legacy reports in memory without mutating archives, and does not copy raw transcript, memo, revised-answer, model-message, provider-reasoning, fabricated-passage, or control-argument text.
- `scripts/export_review_corpus.py` scans archived run folders and writes a deterministic JSONL run-envelope corpus plus manifest for human review and stability analysis. It includes blank review fields, compact custody/readiness metadata, and PR42 `risk_mode_reliance` caveats; it does not score advice quality or use an LLM judge.
- Review-corpus records include deterministic review-readiness tiers so humans and subagents can separate full modern custody runs from partial or legacy content-only archives before labeling.
- PR30 adds a local six-run human/product review seed for the complex baseline. All six answer-level reviews passed and were labeled improved, but all six remain human-owned agent-readiness `with_human_review`; `evaluation.json` is still run-readiness only, and `caller_action: use_revised_answer` is not human approval.
- PR31 adds a human-owned actionable-delta rubric. It prepares PR32 adversarial fixtures, but it is not a judge, score, automatic labeler, or runtime integration.
- PR32 adds paraphrase-only adversarial pair fixtures from the six PR30 cases. They prepare future calibration work, but they are not a judge, score, benchmark claim, automatic labeler, or runtime integration.
- PR33 adds a broader local human-review corpus batch. Twelve full-modern records count as positive answer-level eval evidence, one older partial record is `needs_followup`, and one degraded record is `exclude_from_eval`; it still does not create a judge, score, automatic labeler, or runtime integration.
- PR34 designs the first-class user-values/priorities signal. It defines boundaries, schema shape, grounding, confidence, reviewer use, and implementation gates, but does not add extraction, a report builder, runtime behavior, memory, automatic labels, or a judge.
- PR35 documents live-output hygiene policy. `live_output_health: not_checked` remains the honest default for normal runs; `clean` requires a future trusted complete transcript path, and live-output hygiene does not score answer quality or relax `caller_action`.
- PR36 documents risk-mode behavior policy. Existing `risk_mode` names remain the vocabulary; risk raises review and reliance strictness, but it does not approve actions, change runtime behavior, make Lolla a domain authority, or relax `caller_action`.
- PR37 adds a risk-mode fixture matrix. It covers `quick`, `standard`, `deep`, `high_stakes`, `stability`, and excluded/domain-review routing with expected agent-readiness and `caller_action` stances; it does not enforce behavior or add a judge.
- PR38 reviews the risk-mode fixture matrix. All original PR37 fixtures passed, one high-stakes values/priorities conflict fixture was added, and the matrix is usable as a future implementation gate without approving runtime enforcement or a judge.
- PR39 plans the risk-mode implementation path. The smallest future behavior change is high-stakes reliance/readiness tightening, starting with contract-lock tests for existing conservative behavior; it does not change runtime, prompts, `SKILL.md`, `caller_action`, or evaluation behavior.
- PR40 adds risk-mode contract-lock tests. Otherwise clean `high_stakes` stays `ask_user_first`, degraded high-stakes stays `do_not_use_run_degraded`, clean `standard` stays `use_revised_answer`, and review-corpus records preserve the risk/reliance fields; no runtime behavior changed.
- PR41 adds `risk_mode_reliance_policy` to `evaluation.json` checks for high-stakes runs. It makes reliance caveats explicit while preserving `caller_action`, standard-mode behavior, degraded-run blocking, and the human-owned agent-readiness label.
- PR42 exposes that caveat as compact `risk_mode_reliance` metadata in review-corpus records and human-review workflow docs. It does not change `caller_action`, runtime behavior, prompts, `SKILL.md`, or the human-owned agent-readiness label.
- PR43 reviews the PR42 surface with PR37/PR38 fixtures because the local real archive corpus has 80 `standard` records and zero high-stakes `risk_mode_reliance.present: true` examples. Reviewers can read `risk_mode_reliance.status: pass` as conservative reliance-policy expression without treating it as answer-quality pass, domain approval, or an automatic agent-readiness label; no workflow or taxonomy change is recommended.
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
  judging, model calls, archive mutation, or platform work.
- PR60 lands the provenance map design. It defines
  `lolla.provenance_map.v0` as a local artifact-lineage map for run and review
  custody, but it does not implement an exporter, read archives, change runtime
  behavior, claim PROV-O/W3C compliance, add graph DB, add memory, or judge
  answer quality.
- PR61 lands the review conflict register design. It defines
  `lolla.review_conflict_register.v0` as a human-review-owned surface for
  unresolved tensions, but it does not resolve conflicts, automate severity,
  enforce policy, create labels, or score answer quality.
- PR62 lands the case graph export design. It defines `lolla.case_graph.v0` as
  a future run-local graph-shaped review view, but it does not implement an
  exporter, read archives, change runtime behavior, add graph DB, add memory,
  add GraphRAG, add entity resolution, create labels, or score answer quality.
- PR63 lands the accountability view fixture pack. It bundles audit decision
  record, provenance map, review conflict register, and case graph views for
  three checked-in reviewed cases, but it remains paraphrase-only docs/JSON and
  does not implement exporters, read archives, change runtime behavior, add
  labels, or score answer quality.
- PR64 lands the accountability view fixture review. All three bundles pass as
  useful inspection evidence, `audit_decision_record` is the only view marked
  ready for later exporter design, provenance and conflict-register views need
  more fixtures, and case graph remains on hold before implementation.
- PR65 lands the accountability implementation decision gate. It chooses outcome
  A and recommends a future PR66 Audit Decision Record Read-Only Exporter v0,
  but it does not implement that exporter or start PR66.
- PR66 lands the audit decision record read-only exporter. It emits
  `lolla.audit_decision_record.v0` from structured/custody-safe run artifacts
  to an explicit external output path, refuses archive-internal output, keeps
  raw transcript/memo/revised-answer/provider/private content out, and does not
  infer labels, score advice, approve recommendations, call models, run
  `$lolla`, mutate archives, or change runtime behavior.
- PR67 reviews PR66 exporter smoke outputs from four existing reviewed archives
  and two fixture-backed temp runs. The review finds the records useful and
  raw-content-safe, but recommends PR68 schema/exporter refinement before
  archive integration or automatic generation because empty PR31 buckets are
  only partly clear as "not supplied / not inferred" non-claims.
- PR68 refines the audit decision record exporter output without changing the
  schema version. It adds PR31 population policy, per-bucket status, nested
  buckets, and semantic-field empty-meaning metadata so empty fields read as
  non-claims without adding labels, scoring, judges, archive integration,
  automatic generation, or runtime behavior.
- PR69 re-runs the exporter smoke review against refined PR68 output. Seven
  reviewed records pass, including the optional review-json-supplied bucket
  case; empty PR31 bucket clarity improves to seven `clear_non_claim`.
- PR70 closes the audit/accountability machinery phase as done enough for now.
  It does not add machinery or archive integration. It redirects the next phase
  to Product Delta Evidence: testing whether Lolla changes actual strong-model
  conversations in decision-useful ways without confusing caution, structure,
  or artifact cleanliness for truth.
- PR71-PR74 add the Codex-assisted provisional scaffold for that phase:
  thesis, protocol/schema, dry-run packet, and provisional failure taxonomy.
  These are scaffolding for later human review, not human validation, product
  proof, judge calibration data, scoring, automatic labels, or agent approval.
- PR75 turns the scaffold into a runnable read-only eval lane. It checks 14
  existing cases for Product Delta Evidence readiness and emits PR72-shaped
  shells without reading raw transcript/memo/revised-answer content, calling
  models, mutating archives, or making semantic product judgments.
- PR76 fills the 12 ready shells with Codex-assisted provisional semantic
  reads. The batch is intentionally mixed: material, partial, no-material, and
  inconclusive candidate reads all remain non-human, non-ground-truth, and
  non-product-proof.
- PR77 summarizes PR75 and PR76 as one provisional state-of-evidence package:
  the eval lane can run and carry candidate reads, but the package is still not
  human validation, product proof, judge calibration data, scoring, runtime
  integration, or agent approval.
- PR78 adds deterministic Product Delta boundary lint. It checks supplied
  Product Delta JSON/Markdown artifacts for overclaim drift, unsafe metadata,
  forbidden authority fields, taxonomy score drift, and privacy markers without
  running `$lolla`, calling models, mutating archives, or judging answer
  quality.
- PR79 defines the context-engineered provisional review architecture for the
  next eval-lane phase. It rejects a broad LLM judge, keeps future specialist
  reads downstream/offline, requires PR78 lint, and preserves disagreement,
  uncertainty, missingness, and non-claims without adding schemas, packet
  builders, model calls, runtime integration, or scoring.
- PR80 adds typed Product Delta specialist review contracts as docs/schema
  only. It defines the future conversation-interpretation, likely-action,
  structural-delta, friction/lost-value, interpretation-adequacy, overclaim,
  and conservative fan-in output shapes without creating packets, calling
  models, running review, mutating archives, or changing runtime.
- PR81 adds a read-only Product Delta specialist packet builder. It creates
  checked-in-safe per-specialist input packets for two fixture cases and a CLI
  for generating more from existing eval artifacts; it does not fill specialist
  answers, call models, mutate archives, change runtime, score advice, create
  labels, or authorize agent action.
- PR82 adds a checked-in-safe provisional reviewer trap set before any real
  specialist batch. The traps test whether future specialist review resists
  thin context, length bias, caution without leverage, repeated vanilla gates,
  lost live options, generic prudence over user ambition, assistant-influence
  blindness, disagreement smoothing, clean-artifact authority leakage, and
  hardened provisional language.
- PR83 runs the first Codex-assisted specialist-review batch. It checks all
  PR82 trap families, fills specialist reads for the two PR81 packet-fixture
  cases, downgrades one PR76 material candidate to partial, and keeps the
  output provisional, checked-in safe, linted, non-human, non-scoring,
  non-runtime, and non-authoritative.
- PR84 adds the Fan-In / Disagreement Report v0 as a static checked-in report
  over PR76 and PR83. It does not create new specialist reads; it preserves
  the one PR83 downgrade, both lost-value and interpretation-adequacy concern
  surfaces, and the remaining positive-distribution risk for later human
  review.
- PR85 adds the Product Delta PR71-PR84 Packaging Gate v0. It creates a
  package manifest and tests that the Product Delta phase is internally
  coherent, source-reference resolvable, PR78-linted, and still lower-claim.
  It does not expand evidence or add runtime behavior.
- The GitHub-facing eval index at `docs/evals/README.md` explains the
  runtime/eval split, Product Delta safe commands, what to inspect, what not
  to infer, and the current stop line without adding new evidence or runtime
  behavior.
