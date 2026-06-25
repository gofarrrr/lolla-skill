# Live Flow

Detailed reference for the `/lolla` / `$lolla` skill flow from activation through archive. This should mirror SKILL.md, but SKILL.md remains the executable instruction source.

## Contents

- Step 0-2.5: activation, preamble, capture, extraction, readback
- Step 3: pipeline execution and the four audit lanes
- Step 4-8c: counterargument, updated position, private ledgers, default-off pressure-check state, optional deeper review, memo
- Step 9-10: Observatory and archive
- Cross-cutting: Bullshit Index fact registry

## Step-by-Step Flow

### Step 0: Skill Activation

The skill triggers when the orchestrator sees trigger phrases in the YAML frontmatter description:
- Explicit: "audit this", "check my reasoning", "lolla", "devil's advocate", "what am I missing", "find blind spots", "stress test", "pre-mortem", "what are we not seeing"
- Proactive: when the conversation contains strategic advice that hasn't been challenged

When triggered, the orchestrator loads the full `SKILL.md` body and runs the **preamble bash block** first.

### Step 0b: Preamble

The preamble is a bash block that runs before anything else. It checks:

1. **Skill directory location** — resolves where the skill files live (`$HOME/.codex/skills/lolla`, `.codex/skills/lolla`, `$HOME/.claude/skills/lolla`, or `.claude/skills/lolla`) and follows symlinks.
2. **API key** — `OPENROUTER_API_KEY` or `LOLLA_OPENROUTER_API_KEY` must be set. Fatal if missing.
3. **Data files** — `data/knowledge_graph.json` must exist. Fatal if missing.
4. **Pipeline engine** — the bundled engine at `engine/system_b/` must be present. Fatal if missing.
5. **Environment source** — project `.codex/lolla.env`, project `.claude/lolla.env`, then skill `.env`, then `~/.config/lolla/.env`.
6. **Run files** — generates `LOLLA_RUN_ID` and initializes `/tmp/lolla_<run_id>_live_transcript.txt` plus `/tmp/lolla_<run_id>_operator.log`.
7. **Reports config** — which OpenRouter model (default: `google/gemini-3.1-flash-lite`), whether embeddings are enabled (`OPENAI_API_KEY` present or not), whether a pre-Step-6 cached-card directory is configured, and whether V60 is enabled.

If any check says `FATAL`, Claude stops and tells the user what's missing.

After Step 3, the skill writes an operator-only pre-Step-6 private-table receipt to `/tmp/lolla_<run_id>_operator.log` before Step 6 begins. The receipt names the table status, source atom count, cached-card count, cache state, cache resolution, cache directory, compiled key, expected cache file, any operator-selected cache ref, and default-off Step 7 state. The helper prints only a compact status summary to the terminal, and the receipt is not appended to the user-facing live transcript.

### Step 1: Capture Conversation

Claude extracts the conversation from its context window into a temp file. This is purely mechanical — no judgment.

**What gets included:**
- User messages (the human's words — these contain constraints, questions, pushback)
- Assistant prose responses (Claude's reasoning — these contain the positions being audited)

**What gets excluded:**
- Tool call inputs and outputs (file reads, code execution, search results)
- System messages and reminders
- Meta-conversation about the skill itself

**Format:**
```
[Turn 1] USER:
We're considering whether to migrate to microservices...

[Turn 1] ASSISTANT:
This is a significant architectural decision. Given the context...

[Turn 2] USER:
What about the risk of...
```

**Long conversation handling:** If the conversation exceeds ~100 turns, Claude keeps the first 3 turns (contain irreplaceable constraints) and the last 15 turns (contain the current position), with an `[... N turns omitted ...]` marker.

### Step 2: Extract Decision Structure

The live skill invokes `scripts/skill/run_extract_step.sh`; the helper validates the capture, calls `scripts/run_extract.py`, writes verbose diagnostics to the operator log, and creates `/tmp/lolla_<run_id>_extraction.json`.

```bash
bash "$SKILL_DIR/scripts/skill/run_extract_step.sh"
```

The underlying extraction script reads the conversation, sends it to OpenRouter with a calibrated extraction prompt, and parses the structured response.

**First question: is this conversation strategic?** A conversation is "strategic" when the AI provides advice, recommendations, or analysis that could influence a material decision — business strategy, architecture choices, hiring, investment, product direction, vendor selection, etc. Code debugging, factual lookup, and creative writing are NOT strategic.

If not strategic → returns `{"status": "not_strategic", "decline_reason": "..."}` and Claude presents a polite decline.

If strategic → extracts 6 current compatibility fields:

| Field | What It Captures | Why the Pipeline Needs It |
|-------|-----------------|--------------------------|
| `decision_situation` | The core decision as a neutral problem statement — domain, stakeholders, what's at stake | Provides a compact compatibility summary and helps classify whether the conversation is strategic. In the target architecture this is a derived view, not the source of truth. |
| `live_constraints` | Every constraint the user stated. Each item carries a terse `constraint` string (≤120 chars, noun-phrase + state), plus `status: active / dropped / modified` and `weight: structural / situational`. | Transitional user-side issue signal. A constraint stated in turn 3 but absent from the recommendation in turn 8 is omission evidence. In the v1 IR this intent becomes `UserIssueEvent(kind="constraint")` with turn/span provenance. |
| `synthesized_position` | The LLM's latest/most developed recommendation, preserving reasoning structure | Compatibility projection of the latest assistant position. It remains useful for legacy/headless paths, but the target architecture models this as a `StanceEvent` trajectory with "latest stance" as a projection. |
| `reasoning_passages` | 3-8 VERBATIM quotes from the assistant's messages — leaps, dismissals, assertions | Evidence-eligible assistant substrings for Lane 2. If these aren't exact quotes, fingerprint verification fails. In the target architecture these become packet-local reasoning spans, and only graduate to `ReasoningSegment` if measurement justifies it. |
| `original_framing` | How the human posed the problem — what was assumed fixed, what perspectives were excluded | Bootstrap input for Lane 3 frame pressure. In the v1 IR this intent becomes `FrameAnchor` with source-span provenance. |
| `dropped_threads` | Concerns raised but never resolved — by either party | Transitional omission/open-loop signal. In the v1 IR this intent becomes `UserIssueEvent(kind="concern" \| "open_loop")` with lifecycle (`active`, `resolved`, `superseded`). |

These fields are the current extraction contract, not the source of truth. The raw transcript inside `ConversationContext` remains canonical; extracted fields are derived context and compatibility surfaces that seed the provenance-bearing IR.

**Capture validation, quote verification, and failure gates:**

Before sending the conversation to OpenRouter, the extraction script validates capture integrity against the raw (pre-truncation) text. Three signals feed downstream observability:

- `capture_manifest` — actual vs. declared turn counts (user, assistant) and character length. When the 80K-char cap or the "first 3 + last 15 turns on >100-turn conversations" rule fires, `capture_manifest.truncation_applied: true` is set and additional fields (`truncation_reason`, `original_char_length`, `truncated_char_length`, `total_turns`, `kept_turns`, `omitted_turns`) are populated so downstream layers and the chat flow know the audit ran on dropped context.
- `capture_health` — graded `good` / `degraded` / `critical` / `unknown` (no parseable header). **`capture_health: "critical"` short-circuits the run**: the extractor returns `status: "capture_critical"` with a structured `decline_reason` and the full `capture_manifest` *before* initializing the OpenRouter client, so broken captures cost nothing. A critically degraded capture (>50% assistant turns missing, zero assistant responses, or a captured transcript ending on a user turn without the assistant's final response) would produce a ghost audit on partial data; the gate prevents that silent failure from entering the pipeline.
- `_quote_validation` — after extraction, each `reasoning_passages` entry is checked against the transcript with `find_substring_tolerant(...)`. The matcher tries exact substring first, then case-insensitive match, then a narrow quote-safe fallback that removes a symmetric wrapper quote around the whole passage (`"..."`, `'...'`, smart quotes, guillemets). It still rejects paraphrase, punctuation drift, whitespace drift, and word substitutions. **If any fail, extraction retries once** with a correction prompt that lists the failed passages as examples of what NOT to do and demands character-for-character verbatim copies. If the retry produces fewer fabrications, its payload is adopted wholesale. Any fabrications that still remain after the retry are dropped from the final `reasoning_passages` list (the field contract is "literal transcript spans only"), a `capture_warning` is emitted, and `run_pipeline.py` surfaces `quote_fabrication` in `run_health`. `_quote_validation` also records `retry_attempted` and `retry_succeeded` for provenance.

These diagnostics surface in every output path — `ok`, `error`, `not_strategic`, and `capture_critical`.

**How the runtime reads these fields:**

The extraction JSON is wrapped together with the raw conversation text and capture metadata into a `ConversationContext`. From there `construct_conversation_ir(context)` builds a `ConversationIR`: each `live_constraint` becomes a `UserIssueEvent(kind="constraint")`, each `dropped_thread` becomes a `UserIssueEvent(kind="open_loop"|"concern")`, each of `original_framing` and `decision_situation` becomes a `FrameAnchor` with `DerivationProvenance` over all user turns, and `synthesized_position` is held as transitional text the runtime can read but never claims as a verbatim quote.

The default production pipeline (`SystemBPipeline.run()`) calls `construct_conversation_ir(context)` with no specialist extractors — the IR is built deterministically from the extraction fields above. `construct_conversation_ir` *also* accepts optional `stance_extractor`, `live_constraints_extractor`, and `dropped_threads_extractor` keyword arguments; when an injected specialist is provided, it replaces the corresponding paraphrased mapping with substring-validated events whose `text` is a literal substring of the named turn. This injection path is exercised today by tests, eval harnesses, and ad-hoc callers; default wiring is gated on the promotion criteria documented in [Architecture and Evolution](architecture-and-evolution.md). Either way, lanes read the IR through `Lane4Packet` (no lane sees the raw `extraction.X` paraphrases at the prompt boundary).

### Step 2.5: Readback + Audit Promise

Before launching the pipeline, Claude renders a short readback directly in chat. This is not a card summary. It tells the user what was captured, names the specific recommendation that will be stress-tested, and sets the 5-8 minute expectation for the audit run.

Required shape:

- 120-170 words in normal mode; 70-110 words in thin-material mode.
- At least one exact quote from a user turn, anchored lightly with the turn number when available.
- No internal labels (`Beat 1`, `Step 2.5`, etc.).
- No Observatory URL. The server is not running yet.

Thin-material mode is mechanical, not discretionary: the lower range applies only when the captured conversation is very short, the extraction has little constraint/reasoning material, or later audit outputs are low-signal as defined in `references/chat-output-format.md`.

This beat exists because trust is built before the long wait: the user should see that Lolla captured *their* conversation, not a generic description of the problem.

### Step 3: Run Pipeline

```bash
bash "$SKILL_DIR/scripts/skill/run_pipeline_step.sh"
```

The helper calls `scripts/run_pipeline.py` with the extraction file, conversation file, output path, `--skip-revision`, and `--pre-step6-portfolio step6_private`. The `--skip-revision` flag skips the OpenRouter revision step because Claude/Codex produces the final revised position itself in Step 6. With both `--extraction-file` and `--conversation-file`, `run_pipeline.py` wraps the raw conversation, extraction JSON, and capture metadata as `ConversationContext` by default. This script initializes the full Lolla pipeline via OpenRouter and runs all four lanes:

Immediately before launching the command, Claude sends one functional receipt, not a content section:

> Running the audit now: pressure points, frame assumptions, mental-model tensions, and uncovered dimensions. Usually 5-8 minutes.

```
                         ┌──────────────────────────────┐
                         │  ConversationContext          │
                         │  raw turns + extraction       │
                         │  + capture metadata           │
                         └──────────┬───────────────────┘
                                    │
              ┌─────────────┬───────┼───────┬─────────────┐
              ▼             ▼       ▼       ▼             ▼
       ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
       │  Lane 1  │  │  Lane 2  │  │  Lane 3  │  │  Lane 4  │
       │Structural│  │ Companion│  │  Frame   │  │ Coverage │
       │ Pressure │  │          │  │ Pressure │  │          │
       └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
            │              │              │              │
            ▼              ▼              ▼              ▼
       DeltaCard    CheatSheet    FrameCard    CoverageCard
            └──────────────┬──────────────┬──────────────┘
                           ▼
              V60 private enrichment
       explicit source-backed affordance/absence chunks
                           ▼
              pre-Step-6 private thinking table
       compact current-run table + cached cards on hit
                           ▼
                    result.json
```

#### Conversation-first contract

`SystemBPipeline.run()` accepts `ConversationContext` and only `ConversationContext`; passing anything else raises `TypeError`. The IR is constructed at entry (`conversation_ir = construct_conversation_ir(conversation_context)`) and threaded through every lane via `Lane4Packet`. There is no legacy two-string input shape, no `--legacy-contract` flag, no parallel dispatch — Phase 6 deleted all of it. See [Architecture and Evolution](architecture-and-evolution.md) for what was removed and why.

Pipeline internals are intentionally split out of this live runbook. See [Pipeline Lanes](pipeline-lanes.md) for the detailed Lane 1-4 mechanics, V60 private enrichment, pre-Step-6 shadow portfolio, `run_health`, and per-route tiebreaker observability.

High-level lane outputs:

- Lane 1 produces structural challenge findings (`delta_card`).
- Lane 2 produces model/lens anchors and curated chunks (`companion_cheat_sheet`).
- Lane 3 produces frame assumptions and reframings (`frame_pressure_card`).
- Lane 4 produces uncovered structural dimensions and user-answerable questions (`structural_coverage_card`).
- Post-lane enrichment attaches private V60 source-backed opportunities and, in the live skill, a pre-Step-6 private thinking table. The table is context-only: no live card generation, no reviewer calls, and no code-selected visible answer.

### Step 4: Counterargument Lead

Claude reads the pipeline output JSON and renders one focused counterargument lead in chat. This is not the full audit report and not a card dump. The detailed card rendering stays in the Observatory; Step 4 exists to put the strongest pressure on the table before Claude revises its answer.

**Product vs. process separation:** The chat output uses human language exclusively. Card names (`DeltaCard`, `CompanionCheatSheet`), lane numbers, pipeline stages, severity labels, JSON field names, V60/affordance/chunk/packet/ledger language, and internal section names never appear. Product words such as "audit", "pressure check", "updated position", "memo", and "Observatory" are allowed when they name a surface the user can actually see.

**Counterargument lead structure:**

1. **Run-health line, conditional.** If `run_health.overall` is not `"healthy"` and the issue affects trust in the run, open with one plain note. Material issues include `capture_degraded`, `capture_critical`, `substrate_empty`, `no_fingerprint`, `quote_fabrication`, `capture_truncated`, `lane3_all_dropped`, and `bullshit_index_partial`. Clean runs say nothing about health.

2. **One exact quote anchored to a turn.** The quote can come from the user or assistant, depending on where the case-against lives. Turn numbers are light source attribution, not headings.

3. **The strongest case against the original advice.** One plain-language argument that names the structural weakness. It should be scoped to the conversation, not padded with broad empirical claims the audit cannot support.

4. **One alternative path or question.** The alternative should be decision-useful: a different question, sequence, threshold, test, fallback, or channel. It should not be a dashboard list of every card.

5. **Queued-breakdown line without a URL.** The Observatory is still deferred. Say the remaining challenge points or uncovered dimensions are queued for the full breakdown once the reconsideration is complete; do not link to `localhost`.

6. **Transition to reconsideration.** Close with a short line that the next move is revising the answer, not merely reporting the audit.

Length target: 220-300 words in normal mode; 140-220 words in thin-material mode. The hard cap is 350 words.

After the counterargument lead, Claude continues into the reasoning + persistence arc (Steps 6-8b), records the default-off pressure-check state unless optional deeper review was explicitly requested, prepares the memo decision-note layer (Step 8c), then opens the Observatory in Step 9 and archives in Step 10. The full lifecycle is documented in `SKILL.md`; the steps below summarize each stage's product role.

### Step 5: Observatory Placeholder (deferred)

Step 5 in the SKILL flow is intentionally a no-op. The Observatory is *not* offered here — it is deferred to Step 9 so the launched view contains the complete artifact set (cards + revised answer + pressure-check state + memo). Offering Observatory mid-cycle would show an incomplete run.

### Step 6: Update Your Position (Claude reconsiders)

Before writing, Claude reads `/tmp/lolla_<run_id>_pre_step6_private_table.md` when present. This table is a compact private view of the four lanes, V60, and any cached portfolio cards. It is a cleaner thinking surface, not a command or public artifact. Claude may use, reject, defer, combine, or keep table items private, then records a compact `pre_step6_private_table_ledger` in Step 6b.

After the counterargument lead, Claude reconsiders its earlier advice. The structure is deliberate: first, what survived (what Claude would say again unchanged); then, what to take back or set aside (self-corrections and audit-raised pressures Claude considered but chose not to act on, with specific reasons); finally, what actually shifted. This three-part structure forces genuine reconsideration rather than performative hedging.

**Anchors are evidence-bearing hypotheses, not canonical diagnoses.** Lane 2 surfaces curated mental models that may explain the assistant's reasoning structure, but per-candidate verifier judgment is probabilistic — multi-run stability investigations (research/lane2-architecture-research-frozen-2026-04-26 + research/stability-runs/lane2-pathD-proxy-validation-2026-04-26) confirmed there is no single deterministic substrate fact that predicts cross-run anchor stability above usable thresholds. The product contract therefore treats each anchor as an evidence-bearing hypothesis Step 6 should weigh, not as a canonical fact Step 6 must repeat.

An **anchor-accounting invariant** constrains the reconsideration: every anchor in `companion_cheat_sheet.anchors[]` is routed privately through §1 (its pressure was already priced into the original advice), §2 (considered and set aside with a specific reason), or §3 (drove a change). No anchor is silently skipped. Public naming is no longer the proof of consideration. Claude may name a familiar model when the name genuinely helps the user, but the normal product move is to surface the mechanism, threshold, omitted option, evidence gate, or risk treatment in ordinary language. Exact anchor names remain inspectable in Observatory/audit.

The invariant is now paired with a **three-treatment vocabulary** (`SKILL.md` Step 6 *Anchor treatment*) that decouples "addressed" from "presented as canonical":
- **Primary pressure** for anchors with direct, specific evidence on a load-bearing reasoning move (stronger framing inside §1 or §3).
- **Secondary lens** for anchors with weaker, broader, or competing evidence (softer framing — *"a related lens"*, *"a possible second read"*).
- **"Set aside with a reason"** for anchors the pipeline surfaced but Step 6 reads as not load-bearing (acknowledged in §2 with explicit reason; not silently dropped).

A structural rule pairs with the vocabulary: **one primary-pressure anchor per reasoning move**. When two anchors describe the same move or evidence quote, the most specific / load-bearing anchor gets primary treatment; the others — even if their evidence is direct — become secondary lenses or are set aside with a reason. Treating two anchors as equally primary on the same move is overclaim by structure.

Claude integrates anchors into the "What survived" / "What I'd take back or set aside" / "What actually shifted" reasoning where each one earns its mention — never as a mechanical anchor-by-anchor parade — with rhetorical strength matching the evidence the anchor carries. Some will connect sharply, some won't, and both outcomes are honest. The updated position IS the product.

**V60 is private consideration material, not public content.** If `v60_enrichment.status == "active"`, Claude/Codex reads every selected affordance and absence chunk before writing the updated position. For each chunk it decides one of four dispositions: `used`, `rejected`, `deferred`, or `not_considered`. A useful chunk may visibly change the answer, become a diagnostic question, create an evidence gate, stay private as a guardrail, or help reject an overfit lens. Absence chunks are blockers and overclaim rails; they must not be converted into positive claims. The user should see the improved reasoning, not internal labels like V60, affordance, chunk, packet, or ledger.

The "What actually shifted" section is capped at 3-4 substantive shifts. A shift means a different action, threshold, sequence, condition, risk treatment, or decision question. Tail additions that merely add one more caveat are not allowed to bypass the cap; they must be folded into an existing shift or dropped.

**Timing detail:** Claude/Codex does not launch Step 7 in the default flow. Current `SKILL.md` requires Step 6 to be written, the private-table and V60 ledger skeletons to be filled, and `scripts/skill/finalize_step6_ledgers.sh` to succeed before the default-off pressure-check state, memo rendering, Observatory, archive, or optional pressure-check work can proceed.

### Step 6b: Persist Revised Answer

The Step 6 reconsideration text is written into the result JSON via a small inline Python merge that sets `revised_answer`, `revised_answer_source: "claude_step6"`, `revised_answer_present: true`, and `revised_answer_written_at`. Without this step the Observatory would render an incomplete run (four cards but no revised answer). The persisted revised answer is the first-class artifact downstream tooling reads.

When the pre-Step-6 private table is present, Step 6b writes `pre_step6_private_table_ledger` into `result.json` and `/tmp/lolla_<run_id>_pre_step6_private_table_ledger.json`. When V60 is active, Step 6b also writes a private `v60_consideration_ledger` into `result.json` and `/tmp/lolla_<run_id>_v60_ledger.json`. The V60 ledger has one transaction for every presented V60 chunk and is validated by `validate_v60_consideration_ledger(...)`. These ledgers are operator telemetry only: they tell us which selected material was used, rejected, deferred, private-only, or merely confirming, while leaving the public answer free to be natural.

Step 6b also rolls the ledger status back into `run_health` with the transaction count, disposition counts, used chunk count, and presented-but-not-used count. That makes process comparison cheap: an operator can compare two runs by candidate pool, selected chunks, skipped/not-presented candidates, ledger uptake, and final-answer delta instead of reading only the final prose.

### Memo timing: deferred until Step 8c

The final memo is **not** rendered immediately after Step 6b. The memo waits until Step 8b has persisted the pressure-check state. In the default flow that state says Step 7 was intentionally not run; in explicit deeper-review mode it contains the completed comparison.

### Step 7: Optional Pressure-Check Sub-Agents (default off)

Post-Step-6 pressure-check sub-agents are rested by default. This is now a product simplification choice: the live skill pushes value into the pre-Step-6 thinking table and avoids paying for a second post-Step-6 cognitive layer unless the user/operator explicitly asks for deeper review.

If optional mode is enabled, up to 4 Agent sub-agents (one per non-empty lane) are spawned in parallel via the Agent tool **in the background** (`run_in_background: true`), but only after Step 6b validation succeeds. Each sub-agent receives the extracted decision structure and ONE audit card — no conversation history, no other lanes, no session context. They read the position cold and assess what should shift.

**Why this exists.** The system's own thesis says "an LLM auditing its own reasoning is sampling from the same distribution that produced the flaw." Steps 1–4 honor this — Grok does the detection. But Step 6 asks Claude to reconsider advice it argued for in this conversation. Sub-agents break that loop: same model class as the orchestrator (Opus), but in a clean context that never argued the position.

**Skip conditions.** A lane's sub-agent is skipped when its card is empty:
- Lane 1: `delta_card.top_findings` empty/null
- Lane 2: `companion_cheat_sheet.anchors` empty/null
- Lane 3: both `frame_pressure_card.frame_elements` AND `reframings` empty/null
- Lane 4: `structural_coverage_card.dimensions` empty/null OR every dimension has `covered: true`

A sub-agent that times out or errors is logged as `skipped_error`; it does not block Step 8. These skip conditions apply only when optional mode is active.

### Step 8: Optional Pressure-Check Comparison

In the default flow, no comparison is rendered in chat because Step 7 did not run. Claude still silently cross-checks the updated position against the `bullshit_profile` before persisting the default-off state; if Step 6 reproduced a flagged pattern, it repairs and re-persists the revised answer before continuing. If optional Step 7 ran, Claude compares its Step 6 reconsideration against each sub-agent's output by asking three questions:

1. Did the sub-agent identify a shift I dismissed or minimized in Step 6?
2. Did the sub-agent treat a finding as material that I treated as noise?
3. Did the sub-agent connect a finding to the position in a way I didn't?

Only "yes" answers get reported, under a `### Pressure Check` heading after the Step 6 updated position. If no divergence survives, the section says so quietly. The user never hears about the sub-agent machinery — divergences are attributed to the *argument*, not its source. Claude is also expected to cross-check Step 6 against the `bullshit_profile` to confirm it didn't reproduce the patterns the BI flagged in the original.

### Step 8b: Persist Pressure-Check State

Two artifacts are persisted into `result.json`: a human-readable summary string (`gap_check_summary`), and a structured object (`gap_check`). In the default flow, `gap_check.status` is `not_run_default_off`, `reason` is `post_step6_pressure_check_default_off`, and `lanes` is empty. If optional mode ran, `gap_check` contains one entry per lane recording `lane_number`, `lane_name`, `status` (`completed` / `skipped_empty` / `skipped_error`), and a `divergences[]` array (each tagged with the question that surfaced it). The Observatory's Pressure Check view consumes the structured object; Step 8c uses the persisted pressure-check state to write the memo decision-note layer. Without this step the run is observable only as far as Step 6b.

### Step 8c: Prepare and Render Memo

Claude/Codex writes a small decision-note layer into `result.json`, then `scripts/skill/render_memo_step.sh` persists those fields and calls `scripts/render_memo.py` to render the standalone markdown memo. The memo is the portable decision artifact: what changed in the advice first; the detailed audit trace stays in Observatory unless an operator explicitly asks for a markdown appendix.

New persisted fields:

- `memo_substantive_title`
- `memo_orientation_note`
- `memo_what_changed`
- `memo_what_still_holds`
- `memo_take_back_or_set_aside`
- `memo_pressure_check`
- `memo_note_written_at`

The Python renderer remains deterministic and does not call an LLM. For new runs, it renders a product-clean memo by default:

1. **Decision note** — substantive title, orientation note, what changed, what still holds, what was taken back or set aside, and any material pressure-check divergence.
2. **Questions still unanswered** — the first three unique structural gap questions as user-answerable bullets; any remaining questions are preserved in a small additional-questions appendix.

The full deterministic audit appendix — challenge points, model connections, alternative frames, and delivery profile — is no longer included by default because it leaks machinery into the portable product artifact. Operators can explicitly render it through the memo helper with `--include-audit-appendix` when needed; Observatory remains the normal full-trace surface.

Before persisting the memo fields, Claude checks for hidden sequencing contradictions, removes or labels unverified numbers, preserves any materially different pressure-check path, and keeps the unanswered-questions section priority-shaped. The renderer can fall back to sections in `revised_answer` when individual memo fields are missing, but a complete Step 8c writes all fields explicitly.

Old archived `result.json` files without the memo fields still render in the legacy section-dump format, so existing archives remain readable.

### Step 9: Open Observatory

After the full cycle is complete (cards, updated position, pressure-check state, memo fields, and memo all persisted), the finalizer launches the Observatory through the durable launcher and verifies that the reported URL answers before the receipt is written.

```bash
: "${LOLLA_ENV_STATE:?FATAL: set LOLLA_ENV_STATE to the ENV_STATE path printed by the preamble}"
. "$LOLLA_ENV_STATE"
bash "$SKILL_DIR/scripts/skill/finalize_and_archive.sh"
```

For a merge-readiness or product-surface proof, pass a complete captured transcript and require it to scan clean:

```bash
: "${LOLLA_ENV_STATE:?FATAL: set LOLLA_ENV_STATE to the ENV_STATE path printed by the preamble}"
. "$LOLLA_ENV_STATE"
bash "$SKILL_DIR/scripts/skill/finalize_and_archive.sh" \
  --trusted-transcript "/path/to/complete-live-session.txt" \
  --require-live-output-clean
```

The helper finalizes private ledgers and live-output hygiene, starts the Observatory, verifies liveness before writing the final receipt, archives the run, appends the generated receipt to the live transcript, re-runs live-output hygiene, and re-archives so the final receipt is included. `finalize_and_archive.sh` delegates the browser server to `scripts/skill/launch_observatory.py`, which starts `observatory/serve_result.py` in a detached local session, writes `/tmp/lolla_<run_id>_observatory.pid`, records the actual URL in `/tmp/lolla_<run_id>_observatory.log`, and returns `live` only after an HTTP check succeeds. The default port is `8080`; if that port is occupied, `serve_result.py` falls forward to the next free port. The final receipt should report the actual URL and should not explain port fallback unless the user asks.

Current scope: the browser Observatory opens on the active served run, and its `Cases` tab also lists local archived runs from `~/.local/share/lolla/runs/` (or `$LOLLA_ARCHIVE_DIR`). Selecting an archived run loads that run's main product/API view and graph through the existing SPA. The selected-run custody panel shows availability and links for `agent_result.json`, `reasoning_trace.json`, `evaluation.json`, `run_events.json`, `memo.md`, and `graph_survival_report.*` using read-only local API endpoints. The `evaluation.json` preview is a deterministic run-readiness receipt, not advice-quality scoring. The server-rendered `/audit/*` telemetry panels remain scoped to the active served run for now; deeper historical comparison still lives in the archive folder and comparison/export scripts (`scripts/compare_archived_runs.py`, `scripts/export_reasoning_trace_dataset.py`). See [Observatory Archive Parity Audit](../observatory-archive-parity-audit.md) for the current local-history parity findings.

Zero dependencies (stdlib Python server + pre-built Svelte frontend). The backend API serves:

**Primary product:**
- Case focus and assistant audit target (expandable drawers)
- DeltaCard — findings with severity, passages, challenges, reversal triggers
- CompanionCheatSheet — model anchors with presence badges (EXECUTED/VIOLATED), evidence quotes, presence explanations, and typed chunks (failure modes, premortems, antagonists, heuristics, identity)
- FramePressureCard — frame elements with reframings
- StructuralCoverageCard — gap dimensions with discovery questions
- Revised answer with source provenance badge (`claude_step6`)
- Pressure Check — default-off status or optional per-lane divergences from `gap_check`

**Trust / health context:**
- Run health — overall, capture, substrate, embeddings, fingerprint status
- Pipeline inspector — tendency funnel (25 → triggered → detected → routed → DeltaCard)
- V60 private enrichment — candidate pool, selected cards/chunks, skipped/not-presented candidates, embedding recall, ledger validation, and chunk dispositions
- Delivery audit — bullshit detection with clear/unclear passage counts
- Knowledge graph — model detail views, tendency catalog browsing

**Sidebar:**
- Reasoning graph — force-directed d3 layout showing companion models, chunk references, and KG edges (ally/antagonist/tension)
- Frame pressure summary
- Structural coverage summary
- Knowledge substrate stats

**Server-rendered audit panels** (PR 3 of the 2026-04-28 visibility roadmap; portable, no SPA dependency):
- `/audit` — index of the panels below
- `/audit/extraction` — capture health, quote validation, extracted decision situation, live constraints, reasoning passages, original framing, and dropped threads
- `/audit/memo` — rendered `memo.md` decision-note artifact plus `memo_note.json` field diagnostics and source paths
- `/audit/lane1` — Pass 1 + Pass 2 funnel: 24 triage scores, threshold, triggered set with source attribution (triage / embedding / always_include), Pass 2 outcomes with `reason`, full top-25 embedding ranks (sub-threshold close-calls visible)
- `/audit/lane2` — Companion selection funnel: 60 candidates → accepted-before-cap → final cheat-sheet anchors, plus per-bucket views (rejected with reason, capped, duplicates, quote repairs, silently-omitted)
- `/audit/lane4` — All 15 catalog dimensions with detected/not-detected, covered/gap, gap routes (candidate + excluded models), gap questions
- `/audit/anti-echo` — Excluded models with lane-of-origin attribution, computed at render time by intersecting against each upstream lane's surfaced models
- `/audit/routing` — Per-tendency primary, antidotes, activation-tiebreaker traces (fired or aborted with human-readable clause)
- `/audit/treatment-audit` — optional model-treatment audit results when a separate treatment-audit run exists
- `/audit/expansions` — Companion expansions grouped by source anchor: relation type, activation condition, why relevant
- `/audit/stakeholders` — stakeholder assumption check when enabled, including actor dependencies and correction state
- `/audit/v60` — V60 private enrichment: selected source-backed affordance/absence chunks, skipped candidates, not-presented model IDs, embedding recall, and Step-6 consideration-ledger uptake
- `/audit/pre-step6` — current private-table source items, Step 6 ledger uptake, custody/cache guardrails, and legacy shadow-policy evidence when present
- `/audit/graph-survival` — selected/suppressed/answer-changing/private-guardrail graph and embedding candidate accounting
- `/audit/reasoning-trace` — artifact custody, trace adequacy, model-call telemetry, surface-divergence checks, and commitment candidates
- `/audit/events` — lifecycle timeline from `run_events.json`: extraction, pipeline, ledger finalization, memo rendering, Observatory launch, archive, and receipt
- `/usage` — per-run cost & call breakdown (existing, with cross-link to `/audit` added)

Every audit panel is server-rendered HTML and works whether or not `observatory/build/` (the Svelte SPA bundle) exists — design intent is skill portability: anyone downloading the skill can use the panels without a Node toolchain.

### Step 10: Archive Run

After launching the Observatory, the skill archives the run's core artifacts into a persistent case folder under `~/.local/share/lolla/runs/` (or `$LOLLA_ARCHIVE_DIR`) so the run survives `/tmp` cleanup and stays accessible for later review, memo re-rendering, `scripts/stability_check.py`, `scripts/compare_archived_runs.py`, or `scripts/export_reasoning_trace_dataset.py` analysis. Before copying, `scripts/archive_run.py` finalizes V60 ledger telemetry, product-output hygiene, and live-output hygiene. Archive-time live-output finalization treats `/tmp/lolla_<run_id>_live_transcript.txt` as a manual artifact by default: detected leaks are unsafe, but no-leak manual capture is `not_checked`, not proof of the full console surface. When the Step 9 finalizer receives `--trusted-transcript /path --require-live-output-clean`, it appends the final receipt to that complete capture, syncs it into `/tmp/lolla_<run_id>_live_transcript.txt`, and only then archives; the resulting `live_output_health: clean` is hash-backed against the archived transcript. It copies 19 core/optional files (`conversation.txt`, `extraction.json`, `result.json`, `revised.txt`, `memo.md`, `memo_note.json`, `gapcheck.txt`, `gapcheck_lanes.json`, `v60_ledger_skeleton.json`, `v60_ledger.json`, `pre_step6_shadow_portfolio.json`, `pre_step6_private_table.json`, `pre_step6_private_table.md`, `pre_step6_private_table_ledger.json`, `live_transcript.txt`, `operator.log`, `run_events.json`, `user_usefulness_review.json`, `outcome_review.json`) into `{archive_root}/{case_id}/{run_id}/`. Missing artifacts (e.g. on a weaker orchestrator that skipped Step 6b/8b/8c, private-table ledger persistence, V60 ledger persistence, live transcript capture, operator logging, pre-Step-6 shadow mode, usefulness review, or outcome review) are skipped gracefully. The archive also generates `agent_result.json`, a compact `lolla_agent_result.v1` handoff for machine callers; `evaluation.json`, a deterministic run-readiness receipt for artifact/schema/custody/health consistency; and `reasoning_trace.json`, a local-only custody manifest that records artifact paths, SHA-256 hashes, health, usage, reasoning-lens IDs, budget-suppressed lens summaries, candidate commitment classifications, user usefulness state, outcome review state, model-call telemetry, and trace-adequacy status without duplicating raw conversation or memo text. `/tmp` originals are not touched, except that copies of the generated agent result and evaluation receipt are written to `/tmp/lolla_<run_id>_agent_result.json` and `/tmp/lolla_<run_id>_evaluation.json` for caller convenience.

The "which case is this?" question is solved without asking the user: the archive computes a **case fingerprint** from `extraction.decision_situation` (first 120 chars, normalized — lowercased, punctuation stripped, whitespace collapsed) and matches it against fingerprints stored in `{case_folder}/.case-manifest.json`:

1. **Exact match:** the new fingerprint is already in a case's manifest → file there.
2. **Fuzzy match (token-set Jaccard ≥ 0.80):** handles extractor paraphrase drift. Same conversation re-extracted twice may produce slightly different decision_situation text; the token-set match still groups them into one case. The new fingerprint is added to the manifest as an alias so future exact-match lookups are O(1).
3. **No match:** a new case folder is created. The folder name is auto-slugged from the first 3-4 significant words of `decision_situation` (e.g., `grant-equity-partnership-status`). Users can rename freely — matching is against the in-folder manifest, not the folder name.

Escape hatches:

- `$LOLLA_CASE_ID` — force a specific folder name, skipping fingerprint match. Useful when grouping a run with an existing case despite mismatched decision_situation, or when the user wants a clean folder name from the first run.
- `$LOLLA_ARCHIVE_DIR` — override the archive root.
- The manifest is a plain JSON file editable by hand (rename the `case_id`, merge fingerprints, adjust the `runs[]` list after manual moves).

Orchestrator scratch files (`preamble.json`, `lane*.json`) are intentionally NOT archived — they are Claude-side working files regenerable from `result.json` if ever needed, and they may or may not exist depending on how the orchestrator staged Step 7 sub-agents.

### Bullshit Index — Fact Registry (cross-cutting feature)

The Bullshit Index (adapted from Hannigan et al., 2025) is not a separate step; it runs inside the pipeline (Step 3) and is consumed by Steps 4 / 6 / 8 / 8c. It evaluates the assistant audit target for four subtypes of bullshit: empty rhetoric, paltering, weasel words, and unverified claims. In normal file-based runs, that target is derived from joined assistant turns in `ConversationContext`; legacy `vanilla_answer` fields are fallback-only. To reduce false positives on unverified claims, the BI judge receives a **fact registry** — a structured summary of what the user established in conversation.

The fact registry extracts `decision_situation`, `live_constraints`, and `dropped_threads` from the extraction JSON into a compact context block (~1500 chars vs. the previous 4000-char raw conversation truncation). The `_CONTEXT_BLOCK` instructs the judge that claims referencing, restating, paraphrasing, or drawing reasonable inferences from user-stated facts are grounded — only claims introducing information the user never provided should be flagged.

This structured approach gives the judge a cleaner signal about what counts as established context, reducing over-flagging of claims that are grounded in conversational facts. Passage-level evaluator failures no longer disappear silently: successful passages still render, while the failed-call count is recorded as `bullshit_index_evaluation_failures` and surfaces through `run_health.issues[]` as `bullshit_index_partial`.

---
