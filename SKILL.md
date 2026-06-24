---
name: lolla
description: >
  Conversation-aware reasoning audit for Codex and Claude Code. Captures the current conversation,
  extracts decision structure, and runs the full Lolla pipeline
  (structural pressure, model companion, frame pressure) via OpenRouter
  against a curated substrate of 222 mental models. Use when asked to
  "audit this", "check my reasoning", "find blind spots", "stress test",
  "what am I missing", "challenge this", "devil's advocate", "lolla",
  "what are we not seeing", or "pre-mortem". Also use proactively when
  the conversation contains strategic advice that hasn't been challenged.
  Do NOT use for coding tasks, simple Q&A, or non-strategic topics.
allowed-tools: "Bash(python3:*)"
metadata:
  author: Lolla
  version: 1.0.0
  requires: OPENROUTER_API_KEY (required), OPENAI_API_KEY (optional for embeddings)
---

<!--
Protected during Track 1 refactor:
- frontmatter above
- pure-orchestrator identity statement
- four-lane system summary
- Model Requirements

Behavioral changes to these sections require a separate, explicit PR.
-->

# Lolla — Conversation-Aware Reasoning Audit

You are running the Lolla audit system. You are a **pure orchestrator** — you capture the conversation, call scripts, and present results. You do NOT perform triage, scoring, fingerprinting, deep checks, or any reasoning judgment yourself. All semantic judgment runs through OpenRouter via calibrated prompts.

The system audits conversations for structural reasoning weaknesses using four independent lanes:
- **Lane 1 (Structural Pressure)** — detects cognitive tendencies distorting the reasoning → DeltaCard
- **Lane 2 (Model Companion)** — recognizes mental models active in the reasoning → CompanionCheatSheet
- **Lane 3 (Frame Pressure)** — audits how the question was framed → FramePressureCard
- **Lane 4 (Structural Coverage)** — decomposes the problem into structural dimensions, finds what the answer didn't address → StructuralCoverageCard

## Model Requirements

Calibrated on Claude Opus 4.7. Cross-model validation (2026-04-22) yielded three tiers:

- **Opus 4.7** — recommended. Full doctrine compliance (anchor accounting, machinery-leak avoidance, full pipeline cycle executed).
- **Sonnet 4.6** — acceptable. Completes the full default pipeline cycle with artifact persistence; modest phrasing regressions (public anchor naming may be over-explicit; occasional machinery-term leaks like "sub-agents" or "the audit changes").
- **Haiku 4.5** — below floor. Skips Steps 6b / 8b / 8c (no revised_answer persistence, no intentional pressure-check state, no final memo render) while generating plausible-looking output for the steps that didn't run. Do not use.

The skill cannot detect the orchestrator model mechanically (`$CLAUDE_MODEL` is not exposed). Self-identify before Step 1:

- **Opus 4.7 or later** — proceed normally.
- **Sonnet 4.6 or later** — proceed normally, with reduced narration and strict live-output hygiene.
- **Haiku (any version)** — STOP. Tell the user, verbatim: *"This skill requires Opus or Sonnet to run reliably. Haiku has been observed to skip critical artifact-persistence steps while generating plausible-looking output for the steps that didn't run. Please re-run on Opus or Sonnet."*
- **Cannot identify with confidence** — proceed without a model caveat in chat. Let the structured run-health checks and archived artifacts expose missing work instead of narrating model uncertainty to the user.

Only refuse when highly confident the orchestrator is Haiku. Don't false-refuse on uncertainty — the user should be able to proceed and investigate.

## Codex Compatibility

This skill was originally authored for Claude Code and now also supports Codex skill installation. In Codex, invoke it explicitly with `$lolla` or ask to use the Lolla skill; in Claude Code, `/lolla` remains the expected command. When instructions say "Claude" or "Claude Code", treat the current agent as the orchestrator. When instructions say "Bash", use the available shell tool for the same command.

## Preamble (run first)

```bash
# Locate the external setup script, then let it perform full initialization.
_LOLLA_SETUP_DIR=""
[ -d "$HOME/.codex/skills/lolla" ] && _LOLLA_SETUP_DIR="$HOME/.codex/skills/lolla"
[ -z "$_LOLLA_SETUP_DIR" ] && [ -d ".codex/skills/lolla" ] && _LOLLA_SETUP_DIR=".codex/skills/lolla"
[ -z "$_LOLLA_SETUP_DIR" ] && [ -d "$HOME/.claude/skills/lolla" ] && _LOLLA_SETUP_DIR="$HOME/.claude/skills/lolla"
[ -z "$_LOLLA_SETUP_DIR" ] && [ -d ".claude/skills/lolla" ] && _LOLLA_SETUP_DIR=".claude/skills/lolla"
if [ -z "$_LOLLA_SETUP_DIR" ] || [ ! -f "$_LOLLA_SETUP_DIR/scripts/skill/setup.sh" ]; then
  echo "FATAL: Cannot find lolla setup script"
else
  bash "$_LOLLA_SETUP_DIR/scripts/skill/setup.sh"
fi
```

This sets up the skill directory, run ID, live transcript, operator log,
environment variables, cache configuration, run-event logging, and runtime
state. It prints an `ENV_STATE:` path such as
`/tmp/lolla_${LOLLA_RUN_ID}_env.sh`; later shell calls should source that
run-specific file. `/tmp/lolla_latest_env.sh` is only a discoverability fallback
before the active run is pinned. Guarded helpers keep
`LOLLA_EXPECTED_RUN_ID` set and abort if stale state points at a different run.
See `scripts/skill/setup.sh` for the full setup procedure.

If any line says `FATAL`, stop and tell the user what's missing. Do not proceed.

---

## Pipeline

Ten steps. You are a conductor for the audit pipeline (Steps 1-4), then the primary reasoning voice for reconsideration (Steps 6-6b). Post-Step-6 pressure-check sub-agents are **rested by default**: the normal flow records an intentional default-off pressure-check state, then writes the memo decision-note layer (Step 8c), Observatory, and archive (Steps 9-10). Step 7 remains available only as an explicit deeper-review mode when the user/operator asks for it. Step 5 is a placeholder — Observatory is deferred to Step 9 so all artifacts are complete.

### Operating Invariants

`SKILL.md` is the conductor surface. The detailed procedures live in
`docs/skill/STEPS.md`; when a step needs an exact command, JSON shape, word
limit, or failure branch, open that linked section and follow it rather than
improvising from memory.

When a linked step names a helper script, invoke the helper. Do not reconstruct
multi-argument commands from prose or memory. The helper carries the current
mechanical contract; your job is to invoke it, inspect its receipt, and stop on
its fatal errors.

Every new Bash tool call starts in a fresh shell. Source the run-specific
`$LOLLA_ENV_STATE` file before invoking helper scripts, and keep
`LOLLA_EXPECTED_RUN_ID` aligned with `LOLLA_RUN_ID`. If a new shell did not
inherit variables, set `LOLLA_ENV_STATE` to the exact `ENV_STATE:` path printed
by setup, then source it. Treat `/tmp/lolla_latest_env.sh` as a discoverability
fallback only, not the active source of truth for a running audit.

The refactor is structural only. It does not activate curated atom retrieval,
shadow private-table rendering, automatic graduation, production case-class
routing, or any research-only cleaning architecture. The live runtime still
uses the existing `--pre-step6-portfolio step6_private` path from Step 3.

Code and scripts may make accountable, source-visible custody decisions:
capture, normalize, run the lanes, render private tables, persist ledgers,
validate hygiene, compute costs, launch Observatory, and archive artifacts.
They must not make hidden final-quality or answer-selection decisions. Step 6
remains the cognitive synthesis point.

Run the steps in order. Do not skip Step 6b ledger finalization, Step 8b
pressure-check-state persistence, Step 8c memo fields, Step 9 finalizers, or
Step 10 archive. Plausible-looking chat output is not a complete run unless the
artifacts and validation gates exist.

Keep live narration small. The product surface is the readback, the
counterargument lead, the updated position, any optional pressure-check
divergence, and the final functional receipt. Setup, ledger repair, memo
rendering, Observatory launch, and archive work are operator actions, not chat
content.

A completed run leaves a durable artifact chain:

- captured conversation
- extraction JSON
- pipeline result JSON
- revised answer
- pre-Step-6 private-table ledger when required
- V60 consideration ledger when required
- pressure-check state, even when default-off
- memo note fields and rendered memo
- live transcript hygiene state
- operator log
- run-event log
- Observatory server
- archived case folder with graph-survival report, agent result, and reasoning trace

If one of these is missing, treat the run as incomplete or degraded, not as a
clean success.

Archive case identity uses the exact captured-conversation hash first, then
manifest fingerprint matching. Case manifests retain `conversation_hashes` so
reruns of the same captured conversation do not split into new case folders.

### Live Product Surface Rule

Treat every visible Claude Code narration line during a `/lolla` run as product
surface, even if it is not archived. The persisted hygiene gate protects
`revised.txt`, memo artifacts, and result health; it does not protect the live
terminal transcript unless you preserve the transcript artifact. Therefore the
live run must use reduced narration and maintain a live transcript:

- Do not announce internal beat names, step names, lane names, agent launches,
  waiting states, ledger repair/debugging, telemetry finalization, or archive
  internals.
- Do not write phrases such as *"Beat 2"*, *"launching pressure-check agents"*,
  *"sub-agents are in"*, *"debugging the V60 ledger"*, or *"the pipeline
  flagged"* in any user-visible narration.
- If progress must be visible, state only the user-facing work product:
  *"I have the counterargument; I’m folding it into the revised answer now."*
  If the next action is internal, stay silent unless there is a real blocker.
- Before sending a visible progress line, mentally apply the product-output
  hygiene rule: if the line would fail as `live_narration`, do not send it.
- Append every user-visible Claude Code prose line, status receipt, content
  beat, and final functional receipt exactly as sent to
  `/tmp/lolla_${LOLLA_RUN_ID}_live_transcript.txt`, separated by blank lines.
  In short: append every user-visible prose/status/content message before the
  run is archived.
  Do not append raw bash output, JSON, Observatory pages, or operator-only
  artifacts. This file is archived as `live_transcript.txt` and scanned as the
  `live_narration` product surface.
- Put verbose helper output, provider warnings, raw JSON inspections, validation
  receipts, and exploratory diagnostics in
  `/tmp/lolla_${LOLLA_RUN_ID}_operator.log` instead of chat prose or the live
  transcript. The operator log is archived as `operator.log`.
- A manually maintained transcript is not proof that the full Claude Code
  console was captured. The hygiene finalizer records a manual transcript with
  no detected leaks as `live_output_health: not_checked`, not `clean`. It only
  records `clean` when a complete captured transcript is supplied with
  `--trusted-transcript`.
- Before archive, live-output health must be recorded through
  `scripts/finalize_live_output_hygiene.py`. The Step 9 finalizer does this
  automatically. For merge-readiness proof, invoke the finalizer with
  `--trusted-transcript /path/to/complete-live-session.txt
  --require-live-output-clean`; it syncs that trusted capture into the archived
  `live_transcript.txt` artifact before archive. If it fails on text the user
  already saw, do not rewrite the transcript to make the run look clean; the
  live surface is unsafe and the run should be treated as degraded or rerun.
  Only correct the transcript when it contains a draft or operator note that was
  never sent.

### Step 1: Capture Conversation

Capture the current conversation to `/tmp/lolla_${LOLLA_RUN_ID}_conversation.txt`, preserving user words and assistant prose while omitting tool calls, tool results, system messages, and file contents. See [Step 1 in STEPS.md](docs/skill/STEPS.md#step-1-capture-conversation) for the exact transcript format and write command.

### Step 2: Extract Decision Structure

Invoke `scripts/skill/run_extract_step.sh`; do not reconstruct the `run_extract.py` command yourself. Then branch on `EXTRACTION_STATUS`: decline for `not_strategic`, stop cleanly for `capture_critical`, and continue for `ok`. See [Step 2 in STEPS.md](docs/skill/STEPS.md#step-2-extract-decision-structure) for the helper and status handling.

### Step 2.5: Readback + Audit Promise (Beat 1 — internal name)

Render the user-facing readback and audit promise directly before launching the pipeline. Load `references/chat-output-format.md`, include one load-bearing user quote, avoid internal labels, and do not link to Observatory. See [Step 2.5 in STEPS.md](docs/skill/STEPS.md#step-25-readback-audit-promise) for length targets, thin-mode rules, and examples.

### Step 3: Run Pipeline

Run the four-lane pipeline through `scripts/skill/run_pipeline_step.sh`; do not reconstruct the `run_pipeline.py` command yourself. The helper preserves cache-dir/cache-ref routing, writes the operator-only pre-Step-6 receipt to the operator log, and enforces `LOLLA_PRE_STEP6_REQUIRE_CACHE_HIT`. See [Step 3 in STEPS.md](docs/skill/STEPS.md#step-3-run-pipeline) for the status receipt, V60/private-table notes, and stop conditions.

### Step 4: Counterargument Lead (Beat 2 — internal name)

Read the result JSON plus the chat/output field references, then render the counterargument lead directly without internal labels or Observatory links. See [Step 4 in STEPS.md](docs/skill/STEPS.md#step-4-counterargument-lead) for length targets, required quote anchoring, and failure modes.

### Step 5: Open Observatory

Do not offer or open the Observatory here. Continue to Step 6; Observatory is deferred until the full cycle completes. See [Step 5 in STEPS.md](docs/skill/STEPS.md#step-5-open-observatory) for the exact timing rule.

---

### Step 6: Update Your Position

Read the Step 6 references and the pre-Step-6 private table, then render the updated position directly under `## Updated position` with no internal labels. Treat audit and V60 material as private consideration pressure, keep the §1/§2/§3 structure, and preserve the hard §3 shift cap. See [Step 6 in STEPS.md](docs/skill/STEPS.md#step-6-update-your-position) for the full procedure, reference list, V60 consideration rules, and private-table handling.

### Step 6b: Persist Revised Answer

Persist the updated position with `scripts/skill/persist_revised_answer.py`, then complete and finalize both private custody ledgers with `scripts/skill/finalize_step6_ledgers.sh` before any pressure-check, memo, Observatory, or archive work continues. The pre-Step-6 private-table ledger allows `used`, `rejected`, `deferred`, `private_guardrail`, and `confirming_support`; the V60 ledger separately allows `not_considered` for technically unusable chunks. See [Step 6b in STEPS.md](docs/skill/STEPS.md#step-6b-persist-revised-answer) for the write-file shapes, skeleton-copying rules, validation gates, and repair loops.

### Memo Timing: Do Not Render Yet

Do not generate the final memo immediately after Step 6b. Persist the Step 8b pressure-check state first, then prepare and render the memo in Step 8c. Memo generation is silent until the final receipt. See [Step 6b in STEPS.md](docs/skill/STEPS.md#step-6b-persist-revised-answer) for the full timing rule.

### Step 7: Optional Pressure-Check Sub-Agents (Default Off)

Default path: do not launch post-Step-6 pressure-check sub-agents. Run them only when the user/operator explicitly asks for deeper review or sets `LOLLA_STEP7_PRESSURE_CHECK=on`, and only after Step 6b finalization succeeds. See [Step 7 in STEPS.md](docs/skill/STEPS.md#step-7-optional-pressure-check-sub-agents-default-off) for optional-mode prompt construction, skip conditions, and product-surface rules.

### Step 8: Optional Pressure-Check Comparison

In default flow, no Step 8 comparison renders because Step 7 did not run. Silently cross-check Step 6 against `bullshit_profile`, repair only if you reproduced a flagged pattern, then continue to Step 8b. In optional mode, compare returned pressure-check outputs against Step 6 and surface only material divergences. See [Step 8 in STEPS.md](docs/skill/STEPS.md#step-8-optional-pressure-check-comparison) for the divergence questions and no-machinery language rules.

### Step 8b: Persist Pressure-Check State

Always write a structured pressure-check state. In default flow, invoke `scripts/skill/persist_default_off_pressure_check.py` rather than reconstructing the JSON write. In optional mode, persist the pressure-check text, per-lane divergences, and real sub-agent usage records only for completed calls. See [Step 8b in STEPS.md](docs/skill/STEPS.md#step-8b-persist-pressure-check-state) for the helper and optional-mode JSON shape.

### Step 8c: Prepare and Render Memo

After Step 8b, write the memo decision-note fields to `/tmp/lolla_${LOLLA_RUN_ID}_memo_note.json`, then invoke `scripts/skill/render_memo_step.sh` to persist them and render `/tmp/lolla_${LOLLA_RUN_ID}_memo.md`. Keep memo content product-clean and source it only from already-persisted Step 6, Step 8, and audit-card material. See [Step 8c in STEPS.md](docs/skill/STEPS.md#step-8c-prepare-and-render-memo) for the field list, quality checks, and helper contract.

### Step 9: Open Observatory

After the full cycle artifacts are persisted, invoke `scripts/skill/finalize_and_archive.sh` to validate private ledgers, finalize live-output hygiene, launch Observatory, and archive the run. Do not narrate Step 9 in chat; consolidate the URL in the final functional receipt. See [Step 9 in STEPS.md](docs/skill/STEPS.md#step-9-open-observatory) for the helper contract.

### Step 10: Archive Run

The Step 9 helper already archives once. Step 10 is the silent archive verification point; do not call `archive_run.py` by hand unless the helper failed. See [Step 10 in STEPS.md](docs/skill/STEPS.md#step-10-archive-run) for the artifact list, `graph_survival_report.*`, `reasoning_trace.json`, case matching, and environment overrides.

## Completion

Close with the final functional receipt: Observatory URL, memo path, cost, and archive location, plus one plain warning sentence when run health is not clean. Prefer the receipt printed between `USER_RECEIPT_BEGIN` and `USER_RECEIPT_END` by `scripts/skill/finalize_and_archive.sh`; the helper already appends and re-archives it. Only use `--receipt-file ... --skip-observatory` when overriding that generated receipt. See [Completion in STEPS.md](docs/skill/STEPS.md#completion) for the receipt templates and degraded-run handling.

## References

Do NOT read these proactively. Load only when a specific situation calls for it:

| File | When to read |
|------|-------------|
| `references/output-field-guide.md` | **Read at the start of Step 4** — full field definitions, chunk types, compound patterns, element types, reframe moves |
| `references/chat-output-format.md` | **Read at the start of Step 4** — render specification: run-health surface, BLUF, finding blocks, anchors line, alternative-question line, structural-gaps line, delivery-check line, run-cost line, closing line, "what NOT to put in chat" |
| `references/presentation-voice.md` | **Read at the start of Step 6** — how to voice your updated position: Munger-inspired directness, concrete antidotes, earn the right to challenge |
| `references/anti-bullshit-doctrine.md` | **Read at the start of Step 6** — anti-bullshit thinking framework: five rules for honest strategic speech, RLHF patterns to avoid, negation test as mental model. Also cross-check before Step 8. |
| `references/anchor-treatment.md` | **Read at the start of Step 6** — how to handle `companion_cheat_sheet.anchors[]`: accounting invariant, three rhetorical modes (primary pressure / secondary lens / set aside), one-primary-per-move rule, what good vs. bad anchor integration looks like |
| `references/private-enrichment-treatment.md` | **Read at the start of Step 6** — consideration standard for lane pressure and V60 chunks: strongest plausible application, rejection/deferral standard, public/private split |
| `references/sub-agent-prompts.md` | **Read only when optional Step 7 is explicitly enabled** — shared preamble + four lane-specific suffixes for pressure-check sub-agents |
| `references/memo-output-format.md` | **Read at Step 8c** — decision-note memo contract: title, orientation note, compressed sections, pressure-check inclusion, banned memo language |
| `references/tendency-catalog.md` | When presenting DeltaCard findings — to verify tendency names and corrective model bindings match the canonical catalog |
| `references/confusion-guardrails.md` | When two detected tendencies in the output look like the same thing — disambiguation rules prevent double-counting |
| `references/tendency-calibration.md` | When a detection feels marginal or the user questions a finding — contains detection boundaries and threshold guidance per tendency |
| `references/presentation-research.md` | When thinking about how to present findings in chat vs. Observatory — book research on scanning, BLUF, story turns, formatting overuse |
| `HOW_IT_WORKS.md` (repo root) | When the user asks "how does this work", "what just happened", or about the architecture — full technical reference including research foundations, step-by-step pipeline flow, and knowledge substrate |
| `docs/cost-and-telemetry.md` | When the user asks about cost, call counts, prompt caching, or what's measured per run — single canonical doc covering the `usage_summary` block, vendor tracking, pricing table, and how to add a new vendor or stage |
