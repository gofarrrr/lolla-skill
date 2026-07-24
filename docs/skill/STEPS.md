# Lolla Pipeline: Detailed Step Procedures

This document contains detailed implementation procedures for the Lolla skill
pipeline. The high-level orchestration overview stays in `SKILL.md`.

> **Current Codex transport rule (2026-07-24):** read
> [Codex live-run transport boundary](CODEX_LIVE_RUN_BOUNDARY.md) before
> executing these semantic steps. Its exact run-handle, private-input,
> schema-owned consumer-packet, Step 6, memo, verification, and surface-health
> procedures supersede older environment-sourcing, heredoc, raw-file
> inspection, and manual-ledger command examples in this document. Those older
> examples remain temporarily for Claude Code compatibility and historical
> explanation; they are forbidden in an ordinary Codex run.

<a id="step-1-capture-conversation"></a>

## Step 1: Capture Conversation

Extract the full conversation from your context and pass it to Lolla's private
runtime capture helper. Include only user messages and your (assistant) prose
responses. Skip tool call inputs, tool results, system messages, and file
contents.

Start with a header line summarizing the conversation shape, then format each
message block. The legacy wire format calls each role block a `turn`; a
user/assistant pair shares the same display number. Counts used by the
80,000-character processing-view policy are message-block counts, not pair
counts:

```
CONVERSATION: {N} turns, {X} user messages, {Y} assistant responses

[Turn 1] USER:
{user message text}

[Turn 1] ASSISTANT:
{assistant response text}

[Turn 2] USER:
...
```

Start the helper as a runtime process, then supply the formatted transcript on
its standard input:

```bash
bash scripts/skill/capture_step.sh --run-id RUN_HANDLE
```

Wait for the helper's exact `PRIVATE_INPUT_READY` line, then use the host's
process-input channel to send the transcript and close standard input. Do not
send source bytes merely because the process has started: startup alone does
not prove terminal echo is disabled. Do not put the transcript in a command
argument. In Codex, do not use Apply Patch or another file editor for this
step: that exposes a misleading `Added ...conversation.txt` edit to the user.
The helper validates the wire format, writes the source artifact with
owner-only permissions, records `conversation_captured`, and prints only the
readiness line plus a small `CAPTURE_STATUS` receipt. When standard input is an
interactive terminal, the readiness line is emitted only after terminal echo
is disabled; the helper restores echo afterward. If it cannot disable echo, it
fails without reading the source. A host may still show that a runtime tool was
used; the transcript is neither replayed by the terminal nor presented as a
source-code edit.

**Rules:**
- Preserve the user's exact words — these contain constraints the pipeline needs
- Preserve your (assistant) reasoning passages verbatim — the companion lane needs literal substrings
- Omit tool calls and their outputs (code execution, file reads, search results)
- Omit system reminders and meta-conversation about the skill itself
- Preserve the complete available prose conversation even when it exceeds 100 turns. Do not pre-truncate the authoritative transcript.
- Long-conversation compaction belongs to a separately named processing view. `run_extract.py` may create `conversation_processing_view.txt` plus exact omission metadata, while the original `conversation.txt` remains authoritative and is archived unchanged.
- The current initial-extraction threshold is 80,000 characters, not words or provider tokens. Above it, the bounded view contains exactly the first 3 and last 15 parsed user/assistant message blocks. Later conversation-native pipeline input still loads the full authoritative transcript.
- Compatibility fields such as `authoritative_turn_count`, `total_turns`, and
  `omitted_turns` currently count those parsed message blocks. Do not reinterpret
  them as user/assistant exchange-pair counts in a new consumer.

<a id="step-2-extract-decision-structure"></a>

## Step 2: Extract Decision Structure

Invoke the Step 2 helper. Do not reconstruct the `run_extract.py` command, add `--run-id`, or guess file flags:

```bash
# Exact run state is resolved by the named helper from --run-id RUN_HANDLE.
bash scripts/skill/run_extract_step.sh --run-id RUN_HANDLE
```

The helper verifies the captured conversation, calls OpenRouter to extract the
decision situation, constraints, synthesized position, reasoning passages,
framing, and dropped threads, writes the run-scoped extraction artifact,
writes verbose diagnostics to the operator log, seals the attempt, and prints
`EXTRACTION_STATUS`.

Every extraction attempt is terminal. `ok` may proceed to the graph.
`not_strategic` and `capture_critical` stop without the graph. A provider or
operational failure also stops before the graph, records
`extraction_failed`, preserves a minimal private failure archive under
`$LOLLA_ARCHIVE_DIR/_failed-extractions/` (or the default local archive root),
and prints an exact message between `USER_FAILURE_RECEIPT_BEGIN` and
`USER_FAILURE_RECEIPT_END`. Send that message exactly. Do not retry the helper
under the same run ID: the terminal seal blocks a second paid call. A retry is
a new `$lolla` invocation with a new run ID.

The Step 1 helper rejects unparseable captures before any paid extraction call.
If the source uses `USER:` / `ASSISTANT:` without `[Turn N] USER:` /
`[Turn N] ASSISTANT:` markers, lacks a parseable `CONVERSATION:` header, or
ends without an assistant answer, start a new `$lolla` run and capture it
correctly. Do not replace source text inside an existing run.

When `conversation_processing_view.status == "partial"`, inspect
`capture_adequacy` before Step 3. The result must distinguish complete source
custody from partial initial-extraction coverage, report the exact omitted
window, and later degrade run health as
`extraction_processing_view_partial`. The legacy
`run_health.capture_truncated` boolean is a compatibility alias for that
processing-view state; it is not evidence that `conversation.txt` was cut.

Read `EXTRACTION_STATUS` or the output file's `status` field:

**If `status` is `not_strategic`:**
Present the `decline_reason` to the user and stop. Example: "This conversation is about debugging a Python error, not a strategic decision. Lolla audits strategic reasoning — try it on a conversation where you're making a recommendation or weighing tradeoffs."

**If `status` is `capture_critical`:**
The conversation capture is fundamentally broken — more than half the assistant turns are missing, no assistant responses were captured, or the captured transcript ends on a user turn without the assistant's final response. An audit on this capture would be unreliable, so the extraction declined before calling OpenRouter. Read the `decline_reason`, `capture_manifest`, and `capture_warnings` from the output file, surface a short explanation to the user, and ask them to re-run the skill so Step 1 can capture the conversation again. Do NOT proceed to Step 3. Example message: *"Lolla couldn't audit this run — the captured transcript ends on your last question, so the final assistant answer is missing. An audit would judge an incomplete conversation. Please rerun `/lolla` and I'll try to capture it cleanly this time."*

**If `status` is `ok`:** Proceed to Step 2.5.

<a id="step-25-readback-audit-promise"></a>

## Step 2.5: Readback + Audit Promise (Beat 1 — internal name)

**Before launching the pipeline (Step 3), render the readback + audit-promise content directly.** This fills the pipeline wait with a concrete product receipt: what Lolla captured and what it is about to test. Provider latency varies; do not promise a fixed duration.

First prepare the exact run's bounded readback view:

```bash
bash scripts/skill/prepare_consumer_step.sh \
  --run-id RUN_HANDLE \
  --stage readback
```

After `CONSUMER_PACKET_STATUS: readback ready`, read the owner-only
run-scoped consumer packet with the host's bounded file-read capability. Do not
print or query the extraction artifact through the shell. Codex may show its
own file-read card; do not copy the packet into narration.

**Render the content directly. Do NOT introduce it with "Beat 1," "Step 2.5," "Readback section," or any internal section label.** The user does not see the scaffolding; they read the prose. The label "Beat 1" exists in this file and in `references/chat-output-format.md` for instruction architecture only — never for rendering.

**Read `references/chat-output-format.md`** for the full specification (rule, what goes in, length targets, examples, voice contract). The voice rules apply across every section — load once and reuse for the counterargument lead, updated position, and pressure check that follow.

Length: **120–170 words** in normal mode; **70–110 words** in thin mode (when `captured_message_count <= 4` OR `extraction.reasoning_passages < 3 AND extraction.live_constraints < 3 AND extraction.dropped_threads is empty`). Hard cap: 200 words.

Always include at least one exact quote from a user turn in this readback. **On long conversations (>15 turns), the exact-quote rule still applies.** Pick one load-bearing user quote that anchors the case structure; do not replace the quote with a paraphrase of the user's framing.

The closing operational receipt is: *"Now I'm testing the part of my answer that sounded most settled: what would make it fail, what frame it accepted, and what it left uncovered. This may take several minutes; provider latency varies."*

Do not link to Observatory; the server is not running until Step 9. See `plans/voice-examples-2026-04-30.md` § Beat 1 for examples (Marcus / Mother / Short fixture), § Bad — therapy recap for the soft-recap failure mode, and § Bad — visible internal labels for the scaffolding-leak failure mode this section exists to prevent.

<a id="step-3-run-pipeline"></a>

## Step 3: Run Pipeline

**Before launching the pipeline call, present the Step 3 status receipt** — a short functional receipt (~25–35 words) that names the work in human terms:

> *"Running the audit now: pressure points, frame assumptions, mental-model tensions, and uncovered dimensions. This may take several minutes; provider latency varies."*

This is a functional receipt, not a content beat. Do not extend it with prose. Then launch:

```bash
# Exact run state is resolved by the named helper from --run-id RUN_HANDLE.
bash scripts/skill/run_pipeline_step.sh --run-id RUN_HANDLE
```

This runs the full Lolla pipeline — all four lanes — via OpenRouter. The entry point resolves the bundled engine from `SKILL_DIR`, so the caller does not need to start inside the repository or supply `PYTHONPATH`. With both `--extraction-file` and `--conversation-file`, the pipeline uses the production `ConversationContext` runtime by default: raw turns, extraction fields, and capture metadata are passed together so all four lanes audit the conversation directly. The `--skip-revision` flag skips the OpenRouter revision step because the host reasoner produces the final revised position in Step 6, using the full conversation context and the four cards. The result is stored privately in the exact run's configured runtime root.

By default this also attaches a private `v60_enrichment` block to `result.json`. That block is not user-facing and is not a fifth lane. It is source-backed consideration material selected after the lanes, with telemetry for selected chunks, skipped candidates, not-presented candidates, and embedding mode. To disable it for a run, set `LOLLA_V60_ENRICHMENT=off` before Step 3 or pass `--v60-enrichment off`.

The `--pre-step6-portfolio step6_private` mode also writes a compact, owner-only
private thinking table inside that run root, rendered from the four lanes, V60,
and any cached pre-Step-6 card deck. It adds **zero** OpenRouter calls, never
generates live cards on a cache miss, and never selects a visible answer. Its
job is only to give Step 6 a cleaner table to think on.

The helper preserves optional cache-dir/cache-ref routing, writes detail to
owner-only operator custody, prints only a compact `PIPELINE_STATUS` /
`RUN_HEALTH` / `PRE_STEP6_PRIVATE_TABLE` summary, and enforces
`LOLLA_PRE_STEP6_REQUIRE_CACHE_HIT`. This receipt is operator output, not
user-facing prose; do not append it to the live transcript. It prevents cache
misses from being mistaken for cached-card content tests. If the helper prints
`FATAL`, stop; do not continue to Step 4 or Step 6.

**If the output `status` is `error`:** Present the error to the user. Common causes: API timeout (try again), missing API key, data file issues.

<a id="step-4-counterargument-lead"></a>

## Step 4: Counterargument Lead (Beat 2 — internal name)

**Read `references/chat-output-format.md` § Beat 2** (the file should already be loaded from Step 2.5; reload if context elapsed). Also read `references/output-field-guide.md` for field definitions of the four cards.

Prepare the exact reconsideration view:

```bash
bash scripts/skill/prepare_consumer_step.sh \
  --run-id RUN_HANDLE \
  --stage reconsideration
```

After `CONSUMER_PACKET_STATUS: reconsideration ready`, read the owner-only
packet with the host's bounded file-read capability. Do not dump or query
`result.json`.

Then **render the counterargument-lead content directly. Do NOT preface it with "Now Beat 2," "Beat 2," "Now the counterargument," "the strongest counterargument from the audit," or any implementation/section label.** The content opens at *"Here's the strongest case against what I told you"* (or equivalent) — that IS the user-facing surface.

Length: **220–300 words** in normal mode; **140–220 words** in thin mode. Hard cap: 350 words.

The content leads with one verbatim quote anchored to a turn (*"In Turn N, you wrote: '...'"*), one paragraph case-against in plain language, one alternative the audit pushed onto the table, a queued-breakdown line **without an Observatory URL**, and a transition sentence to the reconsideration that follows.

Do **not** link to Observatory; the server is not running until Step 9. Do not include anchor-list, structural-gaps line, or delivery-check line — those are Observatory-only. See `plans/voice-examples-2026-04-30.md` § Beat 2 for examples and § Bad — dashboard report and § Bad — visible internal labels for the failure modes.

<a id="step-5-open-observatory"></a>

## Step 5: Open Observatory

**Do NOT offer the Observatory here.** Continue to Step 6. The Observatory should only be offered after the full cycle completes (after Step 8c), when all artifacts — cards, updated position, intentional pressure-check state, and memo fields — are persisted to the result JSON and the user can see the complete picture.

<a id="step-6-update-your-position"></a>

## Step 6: Update Your Position

**Before writing this section, read these references and the private table:**

- `references/presentation-voice.md` — voice guidance: Munger-inspired directness, concrete antidotes, earn the right to challenge, what good prose sounds like.
- `references/anti-bullshit-doctrine.md` — anti-bullshit thinking framework: five rules for honest strategic speech, RLHF patterns to avoid (paltering +57.8pp, empty rhetoric +20.9pp), the negation test.
- `references/anchor-treatment.md` — how to handle `companion_cheat_sheet.anchors[]`: the accounting invariant, three rhetorical modes (primary pressure / secondary lens / set aside), the "one primary anchor per move" rule, what good vs. bad anchor integration looks like.
- `references/private-enrichment-treatment.md` — how to privately handle lane pressure and V60 chunks: freedom of conclusion, not freedom from consideration; strongest plausible application; rejection/deferral standards; public/private split.

Use the `pre_step6_private_table` material and exact source items already carried
by the reconsideration consumer packet. Treat them as private context: a
cleaner table, not a command. The packet includes exact resolution for every
ledger-required item even when the Markdown rendering would have been capped.
Do not disposition material you were unable to inspect. Use the table to think
more clearly before writing; do not expose the table, source IDs, card IDs,
lane labels, V60 labels, or cache state in user-facing prose.

After the counterargument lead (Step 4), **reconsider your earlier advice and render the updated position directly.** This is the most important step — the updated position IS the product. The audit's findings are structural pressure from a curated knowledge substrate; your job is to absorb that pressure and produce a revised position that is better than what you said before.

**Render the content directly. Do NOT introduce it with "Beat 3," "Step 6," "Now writing the updated position," or any internal section label.** The user-facing transcript opens at the `## Updated position` heading and the `### What survived` / `### What I'd take back or set aside` / `### What actually shifted` subheadings — those ARE the section labels the user sees. No additional preamble.

**Timing note:** Post-Step-6 pressure-check sub-agents are rested by default.
First write Step 6, fill every active custody ledger, and run
`scripts/skill/finalize_step6_ledgers.sh --all`. Continue to the default-off
pressure-check persistence path only after every required ledger is `valid` or
`not_required`. If the user/operator explicitly requests the optional deeper
review mode, Step 7 may run only after this same ledger gate succeeds. This
prevents an invalid private-consideration trace from continuing into memo
rendering, Observatory, archive, or any optional pressure-check work.

The audit findings are **hints, not commands — but not disposable hints.** They come from a curated knowledge substrate that sees patterns you might miss. You are still the primary reasoning engine in this conversation: you have the full context, the user's nuances, and the back-and-forth. The audit has structural pattern detection. Use both.

**Consideration contract.** The system has already paid to select this material from structured lanes, graph relationships, source-backed affordances, absence records, and embeddings where available. You may use, reject, defer, or keep material private as a guardrail, but you must give it a serious hearing first. Before setting aside any lane pressure or V60 chunk, privately form the strongest plausible application, name the condition that would have to hold, and decide what would go wrong if it were forced. Cheap dismissal is a failure mode; grounded rejection is successful use of the system.

**How to use the audit material:**

- **Cherry-pick what genuinely matters.** Not every finding deserves equal weight. A tendency detection with high severity and a specific passage is stronger signal than a marginal detection. Read the evidence — does it ring true for THIS conversation, or is it a pattern match that doesn't quite fit? Trust your judgment.
- **Treat DeltaCard findings as challenge pressure, not corrections.** The audit says "this passage shows signs of doubt-avoidance" — it doesn't say your conclusion is wrong. Maybe you were right to be decisive. But if the finding names a specific missing check or reversal trigger, consider whether it belongs.
- **Treat CompanionCheatSheet as enrichment — and apply `anchor-treatment.md`.** Each anchor has a `display_name`. Anchors are evidence-bearing hypotheses, not canonical diagnoses; consider every anchor, disposition it privately, and surface only the decision-relevant mechanism. Public model names are optional, not proof of consideration.
- **Treat FramePressureCard as an invitation to widen the frame.** If the audit found an embedded assumption in the question, you don't have to abandon your answer — but you might want to acknowledge what changes if that assumption is relaxed.
- **Treat StructuralCoverageCard as territory you cannot address alone.** When structural coverage identifies gaps, acknowledge them as dimensions you cannot address without user input. Do NOT attempt to answer gap questions yourself. Gap questions are an invitation for the user to deepen the conversation — they ask for situation knowledge only the decision-maker has.

**Constitutional graph pressure.** If
`constitutional_graph_survival.status == "active"` in the reconsideration
packet, read every `active_pressure_items[*]` object in full. These are
deliberately noisy canonical lenses admitted before the probabilistic verifier;
graph admission is not relevance proof. For each active `pressure_id`, first
state the strongest plausible application and attempted condition, then choose
exactly one private disposition:

- `apply` when it earns a concrete test, condition, alternative, reversal rule, private guardrail, or visible shift;
- `reject` when the strongest application fails—name the failed condition and the risk of forcing it;
- `park` when evidence or timing is insufficient—name the exact reopening condition.

Do not disposition the compact reserve in this run. Reserve means inspectable capacity custody, not semantic rejection. Do not force an active item into public prose: a fully grounded rejection or park is successful consideration, and public stand-down is allowed.

**V60 private enrichment.** If the reconsideration packet contains
`v60_enrichment.status == "active"`, read it before writing the updated
position. This is the source-backed affordance / absence layer selected after
the four lanes. It is private consideration material, not user-facing content
and not a command to name mental models.

Use the V60 block like a silver platter:

- Read every `selected_cards[*].selected_affordance_cards[*]` and `selected_absence_records[*]` chunk.
- For each chunk, first form its strongest plausible application to this conversation, then decide whether it is `used`, `rejected`, `deferred`, or `not_considered`.
- A useful chunk may change visible advice, create an evidence gate, become a diagnostic question, stay private as a guardrail, or simply help you reject an overfit model.
- Absence chunks are blockers and overclaim rails. Do not turn them into positive claims.
- Do not force a chunk into §3 just because it was selected.
- Do not reject with "not relevant" or "already covered" alone. Name the failed condition, duplicate coverage, missing evidence, or risk if forced.
- Use `not_considered` only for malformed, inaccessible, or technically unusable chunks. A chunk that you read and found unhelpful is `rejected`, not `not_considered`.
- Do not mention `V60`, `affordance`, `chunk`, `packet`, `ledger`, internal IDs, or "mental model" in user-facing prose. Model names may appear only when the name genuinely clarifies the mechanism for the user; otherwise translate the mechanism into ordinary language.
- Preserve judgment: rejecting a V60 chunk with a real reason is successful use of the system.

Keep a private note while writing Step 6: which V60 chunk IDs changed the answer, which were rejected, which were deferred for missing evidence, and which were presented but not useful. Step 6b persists this as `v60_consideration_ledger`; do not render that ledger in chat.

If the pre-Step-6 private table exists, also keep a compact private note while writing Step 6: which table sections or cached cards changed the answer, stayed private as a guardrail, merely confirmed the anchor, or were rejected/deferred. Step 6b persists this as `pre_step6_private_table_ledger`; do not render that ledger in chat.

**Structure your updated position in this order:**

1. **What survived.** Start with what you'd say again unchanged. This forces you to affirm your position before modifying it, which is harder than it sounds — the temptation is to hedge everything after seeing the cards.
2. **What you'd take back or set aside.** This section covers two related moves: (a) self-corrections of your own reasoning (*"my mechanism was soft, recommendation is the same"*), and (b) audit-raised pressure you considered and chose not to adopt (*"the contrast-misreaction finding flagged my comparison, but the comparison itself is the right frame for this decision because [reason]"*). The combined heading prevents the awkward case where §2 contains an audit-rejection but the heading reads as if only self-corrections belong there. This is the hardest section to write — it requires genuine judgment, not performance.

   **§2 anti-overcorrection rule:** §2 should include at least one **audit-raised pressure you considered and did not adopt** when such a pressure exists in the audit output. Without it, Beat 3 reads as "the audit was right about everything" — pure absorption, no judgment. Self-corrections of your own reasoning ("I had soft mechanism here, recommendation is the same") are valid §2 content but do not substitute for an audit-grounded rejection when one is available.

   **Constraint:** do NOT manufacture a rejection for symmetry. If the audit produces no credible pressure to reject (empty `delta_card`, weak anchors that don't bear on a load-bearing reasoning move, no frame elements that would have changed the recommendation), say less in §2 rather than performing judgment. Fake resistance is a worse failure mode than a thin §2.
3. **What actually shifted.** Name what changed in your position and why. Keep the user-facing language practical: name the decision pressure, evidence gate, omitted option, or risk treatment. Use a model name only when it naturally helps the user understand the mechanism. Do not turn §3 into a list of internal model labels.

**§3 cap: 3–4 distinct shifts. Hard cap.** Total Beat 3 length 550–800 words; hard cap 900.

**Operational shift definition.** A shift is a change to the substantive advice the user would experience as different guidance: a different action, threshold, sequence, condition, risk treatment, or decision question. If it does not change what the user would do, delay, verify, reject, ask, or watch for, **it is not a shift.**

**Tail-addition rule.** *"One more thing,"* *"two smaller adjustments,"* *"related notes,"* *"minor caveats,"* *"final caveat"* count against the §3 cap if they change advice. If they do not change advice, they belong in §1 (with survival framing) or §2 (with set-aside framing) — not in a §3 tail-section. The cap is enforced on shifts as defined above; it cannot be evaded by re-labeling shifts as adjustments.

When the audit returns 5+ candidate shifts, your job is selection — fold related material into existing shifts (e.g., absorb a kill-criterion observation into the structural-protection rewrite rather than naming it as a separate shift) or send it to §2 if it's a precondition / set-aside. See `plans/voice-examples-2026-04-30.md` § Beat 3 for §3 excerpts demonstrating selection on Marcus (4 shifts from 7 candidates), Mother (3 shifts), and Short fixture (2 shifts on thin material). § Bad — cap evasion shows the failure mode this rule defeats.

`anchor-treatment.md` governs HOW each anchor is accounted for and, when useful, lands inside §1 / §2 / §3 (rhetorical strength matched to evidence) and what's forbidden (probability percentages, silent non-consideration, "the answer is using X" framing on weak anchors, hedging-as-style). Under the §3 cap, weak anchors are privately dispositioned or briefly set aside in §2 when the rejected argument helps the user — not promoted into §3 to prove coverage. Read it before writing.

<a id="step-6b-persist-revised-answer"></a>

## Step 6b: Persist Revised Answer and Decision Trail

Persist the updated position and all required consideration ledgers as one
private unit. Use the ordinary Codex command:

```bash
bash scripts/skill/persist_private_step.sh \
  --run-id RUN_HANDLE \
  --kind step6
```

Wait until the process prints `PRIVATE_INPUT_READY`. Then send exactly one
private JSON packet through the process-input channel and close input. The
packet shape is defined in
[`CODEX_LIVE_RUN_BOUNDARY.md`](CODEX_LIVE_RUN_BOUNDARY.md#step-6-packet).
Do not paste the packet into a shell command or visible tool argument.

The packet contains only:

- the full updated position;
- mutable judgments keyed by every exact graph pressure ID;
- mutable judgments keyed by every exact private-table source ID;
- mutable judgments keyed by every exact V60 chunk ID.

Deterministic code owns every immutable field, identity, order, and schema. It
copies those values from the current run skeletons, requires exact item
coverage, validates all active ledgers in memory, and only then replaces the
runtime artifacts. The reasoner may apply, reject, defer, or park pressure as
the governing schema permits; validation does not decide relevance.

Continue only after the compact receipt says `step6 valid` and reports each
required ledger as `valid` or `not_required`. On `invalid`, stop. The previous
valid result remains authoritative, the private payload is not printed, and a
safe failure event is recorded. Start a replacement packet from the current
skeleton; do not patch a private JSON file in the terminal.

Do not create or inspect `revised.txt`, graph ledger JSON, private-table ledger
JSON, V60 ledger JSON, or `result.json` with heredocs, inline Python, `jq`,
`sed`, Apply Patch, or an editor during the ordinary Codex flow. Those files
are internal custody artifacts, not interaction surfaces.

This step is required whenever its corresponding pressure surface is active.
Without a valid revised answer and complete active ledgers, do not run the
pressure-state helper, render the memo, open Observatory, or archive the run.

### Memo timing

Do not render the memo yet. First persist the default-off or explicitly
authorized pressure-check state in Step 8b. Step 8c prepares the memo only
after that state exists.

<a id="step-7-optional-pressure-check-sub-agents-default-off"></a>

## Step 7: Optional Pressure-Check Sub-Agents (Default Off)

**Default path: do not launch post-Step-6 pressure-check sub-agents.** The current operating choice is to simplify the live skill, reduce cost, and put more value into the pre-Step-6 thinking table. Step 7 is preserved as an explicit deeper-review mode for later use, but it is not part of the normal run.

Run Step 7 only in Claude Code, when the user/operator explicitly asks for
deeper review or sets `LOLLA_STEP7_PRESSURE_CHECK=on` for this run. The current
prompt construction, launch behavior, and telemetry depend on Claude Code's
Agent tool. In Codex, Step 7 is unsupported: do not improvise an agent substitute.
If deeper review was requested there, explain the boundary and ask whether to
continue with the default-off flow. Do not infer that a hard case, sensitive
case, or long answer automatically enables Step 7. If optional mode is not
active, skip directly to Step 8b and persist the default-off pressure-check state.

**Optional mode timing:** if Step 7 is explicitly enabled, launch it only AFTER Step 6b finalization succeeds. The V60 ledger gate comes first. If `scripts/skill/finalize_step6_ledgers.sh --v60-only` failed, repair the ledger and rerun finalization before starting any pressure-check agent.

**Read `references/sub-agent-prompts.md` only in optional mode.** It contains the full templates: shared preamble (with `{DECISION_SITUATION}`, `{LIVE_CONSTRAINTS}`, `{SYNTHESIZED_POSITION}`, `{REASONING_PASSAGES}`, `{ORIGINAL_FRAMING}`, `{DROPPED_THREADS}` placeholders) plus four lane-specific suffixes.

If optional mode is active, spawn up to 4 sub-agents via the Agent tool, one per non-empty lane. Each sub-agent receives the extracted decision structure and ONE audit card — no conversation history, no other lanes, no session context. They read the position cold and assess what should shift.

**Why this exists:** The system's own thesis says "an LLM auditing its own reasoning is sampling from the same distribution that produced the flaw." Steps 1-4 introduce provider-backed pressure before Step 6 asks the host reasoner to reconsider advice it argued for in this conversation. The optional Claude Code agents add clean-context pressure, but they use the same host model family and do not prove independent validation.

**Procedure:**

1. Read `/tmp/lolla_${LOLLA_RUN_ID}_extraction.json` for the extraction fields (decision_situation, live_constraints, synthesized_position, reasoning_passages, original_framing, dropped_threads).
2. Read `/tmp/lolla_${LOLLA_RUN_ID}_result.json` for the 4 card sections.
3. Check skip conditions — do NOT spawn for empty lanes:
   - Lane 1: skip if `delta_card.top_findings` is empty or null
   - Lane 2: skip if `companion_cheat_sheet.anchors` is empty or null
   - Lane 3: skip if `frame_pressure_card.frame_elements` is empty/null AND `frame_pressure_card.reframings` is empty/null
   - Lane 4: skip if `structural_coverage_card.dimensions` is empty/null OR all dimensions have `covered: true`
4. For each non-empty lane, spawn an Agent tool call **in the background** (`run_in_background: true`). All non-empty lanes are spawned in a single message (parallel). Build each prompt by combining the shared preamble + the appropriate lane suffix from `sub-agent-prompts.md`, with placeholders substituted.

   **Use neutral product-facing labels for the Agent tool's `description` parameter.** Claude Code's tool-use UI displays these descriptions to the user as the agents run; the user must not see "Lane N" or card names there. Use the following neutral mapping:

   | Lane | Internal name | Agent description (user-facing) |
   |------|---------------|----------------------------------|
   | Lane 1 | DeltaCard | `Fresh read - structural challenge` |
   | Lane 2 | CompanionCheatSheet | `Fresh read - reasoning tension` |
   | Lane 3 | FramePressureCard | `Fresh read - frame` |
   | Lane 4 | StructuralCoverageCard | `Fresh read - missing dimensions` |

   Do NOT use `Lane 1`, `Lane 2`, `DeltaCard`, `CompanionCheatSheet`, `FramePressureCard`, `StructuralCoverageCard`, or `sub-agent` in the Agent description. The tool-use UI is part of the felt product surface; scaffolding leaks there break the experience the same way they do in chat prose.
5. The sub-agent prompt must be fully self-contained — no file reads, no bash calls, no tool access.

**Do not stage prompts or card JSONs to `/tmp/` files first.** Build each prompt inline as the Agent tool's `prompt` parameter by reading the templates from `references/sub-agent-prompts.md` and interpolating directly into the Agent call. Disk-staging (writing `lane*_prompt.txt`, `delta.json`, `companion.json`, `frame.json`, `coverage_gaps.json`, `preamble.txt` to `/tmp/`) adds 4+ extra tool uses per run with no benefit and risks tool-budget exhaustion before sub-agents spawn.

**If a sub-agent fails or times out:** log that lane as `skipped_error` and continue. Do not block Step 8 on any single lane's failure.

**Sub-agent setup is not user-facing. Do NOT announce spawning, skipped lanes, completed lanes, partial results, or comparison summaries in chat.** Phrases like *"Spawning the four pressure-check sub-agents in parallel now"*, *"Now launching pressure-check sub-agents in parallel"*, *"lanes 2, 3, 4 — lane 1 skipped, no findings"*, *"Three of the four pressure-checks are in with strong signal"*, *"Two of three pressure-check responses are in"*, *"All four pressure checks are in"*, *"All three sub-agents completed"*, and *"Generating the memo now"* are operator narration. The user does not hear about Step 7 at all. Claude Code's tool-call surface shows the Agent calls; the orchestrator's chat prose stays silent on them.

After the counterargument lead, the next user-facing prose should be `## Updated position` unless a real error or blocker requires explanation. The reconsideration drafting, sub-agent launch, wait state, memo rendering, and internal persistence steps all run silently.

<a id="step-8-optional-pressure-check-comparison"></a>

## Step 8: Optional Pressure-Check Comparison

In the default flow, there is no Step 8 comparison because Step 7 did not run. Do not render a `### Pressure Check` section in chat. Before persisting the default-off state, silently cross-check your Step 6 against the `bullshit_profile`; if you reproduced a flagged pattern in the updated position, repair Step 6, update the persisted `revised_answer`, and then continue to Step 8b. Otherwise continue directly to Step 8b and persist the default-off pressure-check state.

Only if optional Step 7 ran, compare your Step 6 reconsideration against each sub-agent's output.

For each sub-agent that returned a result, ask yourself three specific questions:

1. **Did the sub-agent identify a shift I dismissed or minimized in Step 6?**
2. **Did the sub-agent treat a finding as material that I treated as noise?**
3. **Did the sub-agent connect a finding to the position in a way I didn't?**

Only "yes" answers get reported. Render the pressure-check directly under a `### Pressure Check` heading AFTER the updated position. **Render the content directly. Do NOT preface it with internal narration about which lanes/reviewers/sub-agents aligned or completed.** Phrases like *"Reading them honestly: the Lane 2 concerns... Lane 3's two concerns... Lane 4's three gaps..."*, *"All three pressure-check responses are in"*, *"All four pressure checks are in"*, *"Now Beat 4"*, and *"Generating the memo now"* are operator narration and never appear in chat. The user-facing surface starts at the counter-frame opening sentence below.

**Open with a counter-frame phrase.** Use one of: *"One more angle worth surfacing"*, *"A fresh read pushed on something I underweighted"*, *"Two things the position above softened or skipped"*. **Never** *"mostly aligned"*, *"all incorporated above"*, *"the rest is in the position above"*, or any variant that suppresses divergences with confident closure.

**If divergences exist:**

> ### Pressure Check
>
> One more angle worth surfacing — a fresh read pushed on [specific concern] in the position above.
>
> [Each divergence as a substantive paragraph: name the concrete alternative mechanism the sub-agent surfaced (alternative reporting channel, contractual instrument, stakeholder forum, tripwire pattern, legal-instrumental framing), explain why it was underweighted in §3, name what changes if it lands.]

**If no divergences (truly clean Step 6):**

> ### Pressure Check
>
> No additional angles surfaced beyond what the position above already addresses.

The "no divergences" close is rare and should be a deliberate judgment, not a default. If you find yourself reaching for it, run the Question-3 suppression check below first.

**Rules:**
- No lane-by-lane summaries. No machinery language. Specifically: never "my sub-agents found", "isolated review argues / notes / found", "the Lane N reading", "the pipeline flagged", "the audit card". Attribute the *argument* ("there's a case that…", "one point I may be underweighting…"), not its source. Step 7 runs behind the scenes; the user never hears about it.
- Just: "I said X. There's a case for Y that I may be underweighting."
- Be honest. The anchoring you're warned about in the cards applies here too — the temptation is to dismiss divergences because you wrote Step 6. Fight that.
- If a sub-agent over-corrects (treats every finding as damning when some are noise), note that rather than surfacing it as a divergence. Use your judgment — but lean toward surfacing rather than suppressing.

**Watch for Question-3 suppression specifically.** If your draft pressure check contains phrases like "mostly aligned", "all incorporated above", or "already covered" — re-read the sub-agent outputs for any *named alternative mechanism* (an alternative reporting channel, a different contractual instrument, a distinct stakeholder forum, a specific tripwire pattern, a particular legal-instrumental framing) that your Step 6 §3 didn't enumerate. A named alternative the sub-agent surfaced that your §3 didn't list IS a Question-3 divergence — surface it even when the underlying *concern* was addressed structurally. Confident closure that suppresses named alternatives is the failure mode this step exists to defeat.

**Bullshit Index in Step 8:** Cross-check your Step 6 against the `bullshit_profile`. Did you reproduce patterns the BI flagged in the original? See `references/anti-bullshit-doctrine.md` for the specific RLHF patterns to watch for in your own output.

**Stakeholder Assumption Check in Step 8:** If `result.json` contains `stakeholder_assumption_check`, treat it as Observatory-only validation data. Do not surface `stakeholder_assumption_check.chat_actors` or `critical_actors` in the Pressure Check, do not create a stakeholder section, and do not mention "Theory of Mind", "stakeholder assumption check", "checker", or the runtime flag in chat. The field is being evaluated against the existing Pressure Check baseline; user-facing surfacing remains disabled until production evidence shows it adds non-duplicative value.

<a id="step-8b-persist-pressure-check-state"></a>

## Step 8b: Persist Pressure-Check State

This step always writes a pressure-check state so the run is complete and observable. In the default flow it records that post-Step-6 pressure-check sub-agents were intentionally not run. This is not an error, not a skipped artifact, and not a reason to mark the run incomplete.

**Default path — Step 7 rested:**

```bash
# Exact run state is resolved by the named helper from --run-id RUN_HANDLE.
bash scripts/skill/persist_default_pressure_step.sh --run-id RUN_HANDLE
```

The helper writes the owner-only gap-check artifacts and current result fields
inside the exact runtime root: `gap_check_summary`, `gap_check`,
`has_gap_check`, `pressure_check_mode`, `gap_check_written_at`, and a
back-compatible `pressure_check_state`. Default-off runs do not create an
optional sub-agent usage artifact and do not merge Anthropic sub-agent usage.
Continue to Step 8c after the compact success receipt.

**Optional pressure-check mode only:**

Two things get persisted: the human-readable summary text AND a structured `gap_check` object with per-lane status and divergences.

**First**, build the structured object. For each of the 4 lanes, record:
- `lane_number` (1-4)
- `lane_name` ("DeltaCard", "CompanionCheatSheet", "FramePressureCard", "StructuralCoverageCard")
- `status`: "completed" if the sub-agent ran and you compared its output; "skipped_empty" if the lane was skipped due to empty card; "skipped_error" if the sub-agent failed or timed out
- `divergences`: array of objects, one per "yes" answer from the three comparison questions. Each has `question_number` (1, 2, or 3) and `description` (one sentence — what the sub-agent found that Step 6 missed or underweighted). Empty array if no divergences for that lane.

**Then**, write both the text and the structured object:

```bash
cat > /tmp/lolla_${LOLLA_RUN_ID}_gapcheck.txt << 'LOLLA_GAPCHECK_EOF'
{paste your Step 8 pressure check text here}
LOLLA_GAPCHECK_EOF

cat > /tmp/lolla_${LOLLA_RUN_ID}_gapcheck_lanes.json << 'LOLLA_LANES_EOF'
{paste the gap_check JSON object here — see format below}
LOLLA_LANES_EOF

python3 -c "
import json, datetime, pathlib
run_id = '${LOLLA_RUN_ID}'
result_path = f'/tmp/lolla_{run_id}_result.json'
gapcheck_path = f'/tmp/lolla_{run_id}_gapcheck.txt'
lanes_path = f'/tmp/lolla_{run_id}_gapcheck_lanes.json'
d = json.loads(pathlib.Path(result_path).read_text())
d['gap_check_summary'] = pathlib.Path(gapcheck_path).read_text().strip()
d['gap_check'] = json.loads(pathlib.Path(lanes_path).read_text())
d['has_gap_check'] = True
d['gap_check_written_at'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
pathlib.Path(result_path).write_text(json.dumps(d, indent=2, ensure_ascii=False))
print(f'Pressure check persisted to {result_path}')
"
```

**Format for `gap_check` JSON object:**

```json
{
  "lanes": [
    {
      "lane_number": 1,
      "lane_name": "DeltaCard",
      "status": "completed",
      "divergences": [
        {"question_number": 1, "description": "Sub-agent flagged dependency reduction as central deal condition, not a nice-to-have"}
      ]
    },
    {
      "lane_number": 2,
      "lane_name": "CompanionCheatSheet",
      "status": "completed",
      "divergences": []
    },
    {
      "lane_number": 3,
      "lane_name": "FramePressureCard",
      "status": "skipped_empty",
      "divergences": []
    },
    {
      "lane_number": 4,
      "lane_name": "StructuralCoverageCard",
      "status": "completed",
      "divergences": [
        {"question_number": 1, "description": "Equity staging after independent verification rather than front-loading with vesting"}
      ]
    }
  ]
}
```

Map each divergence to the question that triggered it: (1) shift I dismissed, (2) finding I treated as noise, (3) connection I didn't make. If a divergence spans multiple lanes or questions, pick the primary one.

**Then**, fold sub-agent token usage into `usage_summary`. Each spawned sub-agent's task notification includes a `<usage>` block with `total_tokens`. Build records **only for lanes that actually ran and produced a real `<usage>` block** — `skipped_empty` and `skipped_error` lanes already appear in `gap_check`, but they did not call Anthropic and must not be serialized as vendor call records. Otherwise `vendors.anthropic_subagents.calls` is inflated by phantom zero-token "calls" that never happened.

```bash
# Include rows ONLY for spawned, completed sub-agents. Omit any lane whose
# Step 7 status is skipped_empty or skipped_error.
cat > /tmp/lolla_${LOLLA_RUN_ID}_subagents.json << 'LOLLA_SUBAGENTS_EOF'
[
  {"lane": 1, "model": "claude-opus-4-7", "total_tokens": 39202, "duration_ms": 61008, "tool_uses": 1, "status": "completed"},
  {"lane": 2, "model": "claude-opus-4-7", "total_tokens": 36433, "duration_ms": 60605, "tool_uses": 1, "status": "completed"},
  {"lane": 3, "model": "claude-opus-4-7", "total_tokens": 32161, "duration_ms": 42133, "tool_uses": 1, "status": "completed"},
  {"lane": 4, "model": "claude-opus-4-7", "total_tokens": 33066, "duration_ms": 47550, "tool_uses": 1, "status": "completed"}
]
LOLLA_SUBAGENTS_EOF

python3 -c "
import json, sys, pathlib
sys.path.insert(0, '${SKILL_DIR}/engine')
from system_b.usage_summary import merge_subagent_calls
run_id = '${LOLLA_RUN_ID}'
result_path = f'/tmp/lolla_{run_id}_result.json'
sub_path = f'/tmp/lolla_{run_id}_subagents.json'
d = json.loads(pathlib.Path(result_path).read_text())
# Defensive filter — even if the subagents file accidentally includes
# zero-token rows, drop them before merging so phantom calls can't slip
# into vendors.anthropic_subagents.calls.
subs = [
    s for s in json.loads(pathlib.Path(sub_path).read_text())
    if int(s.get('total_tokens', 0) or 0) > 0
]
us = d.get('usage_summary') or {}
merge_subagent_calls(us, subs)
d['usage_summary'] = us
pathlib.Path(result_path).write_text(json.dumps(d, indent=2, ensure_ascii=False))
state = us.get('cost_estimate_state', 'unknown')
coverage = us.get('cost_estimate_coverage') or {}
print(f'Usage summary updated: {us[\"vendors\"][\"anthropic_subagents\"][\"calls\"]} auxiliary calls, cost estimate ({state}) \\\${us[\"estimated_total_cost_usd\"]:.4f}')
if state not in {'complete', 'not_applicable'}:
    print(f'Cost estimate warning: {coverage.get(\"calls_with_unknown_price\", 0)} calls used unpriced models; treat total as a lower bound.')
"
```

Use the exact model identity reported by the current Claude Code run for
`model`; do not infer it from an old calibration example. Optional agents
inherit the parent model. If you do not know the exact model ID with confidence,
use `"unknown"`—calls and tokens still record, and `cost_estimate_state` marks
the total as incomplete until pricing is known.

<a id="step-8c-prepare-and-render-memo"></a>

## Step 8c: Prepare and Render Memo

After Step 8b persists the pressure-check state, read
`references/memo-output-format.md` and prepare the six decision-note fields.
The memo must lead with what changed in the advice, preserve material
alternatives, remove or label unsupported precision, avoid hidden sequencing
contradictions, and keep unanswered questions priority-shaped. It may use only
already-persisted conversation evidence, the updated position, the pressure
cards, and any material authorized pressure-check divergence. Do not expose
internal lane, card, chunk, ledger, or provider machinery in the memo prose.

Submit the six fields through private input:

```bash
bash scripts/skill/persist_private_step.sh \
  --run-id RUN_HANDLE \
  --kind memo
```

Wait for `PRIVATE_INPUT_READY`, send the exact JSON object defined in
[`CODEX_LIVE_RUN_BOUNDARY.md`](CODEX_LIVE_RUN_BOUNDARY.md#memo-packet), and
close input. Do not author `memo_note.json` with a heredoc, editor, inline
Python, or Apply Patch. Continue only after `PRIVATE_PERSIST_STATUS: memo_note
ready`, then run:

```bash
bash scripts/skill/render_memo_step.sh --run-id RUN_HANDLE
```

The renderer is deterministic and makes no provider call. Its compact receipt
is `MEMO_STATUS: ready`; it does not expose the temporary memo path. The memo
is stored privately and later archived. Older archived results may still use
the legacy renderer, but that is archive compatibility, not a second ordinary
Codex authoring path.

After the helper succeeds, send the exact user-facing bridge:

> Audit complete. I am opening the full breakdown now.

Persist that prose with the private narration helper, then continue to Step 9.

<a id="step-9-open-observatory"></a>

## Step 9: Open Observatory

After the full cycle is complete (cards, updated position, pressure-check state, and memo fields all persisted), **launch the Observatory** — the primary detail surface for full card breakdowns, chunk lists, gap questions, delivery audit passages, revised answer, optional per-lane divergences, and the default-off pressure-check record.

**Always launch after Step 8c completes.** Do not wait for the user to ask:

```bash
# Exact run state is resolved by the named helper from --run-id RUN_HANDLE.
bash scripts/skill/finalize_and_archive.sh --run-id RUN_HANDLE
```

The helper finalizes the private-table ledger, V60 ledger, and live-output hygiene, starts the local Observatory server through `scripts/skill/launch_observatory.py`, archives the run, writes a final receipt to `/tmp/lolla_${LOLLA_RUN_ID}_final_receipt.txt`, appends that receipt to the live transcript, re-runs live-output hygiene, re-archives the run, writes Observatory/archive/cost details to `/tmp/lolla_${LOLLA_RUN_ID}_operator.log`, and prints `USER_RECEIPT_BEGIN` / `USER_RECEIPT_END` lines. The launcher starts `serve_result.py` in a detached local session and only returns `live` after an HTTP check succeeds. Keep these for the final receipt; do not narrate them as a separate Step 9 message.

If you have a complete captured terminal transcript for the whole live session, pass it to the same finalizer:

```bash
# Exact run state is resolved by the named helper from --run-id RUN_HANDLE.
bash scripts/skill/finalize_and_archive.sh --run-id RUN_HANDLE --trusted-transcript "/path/to/complete-live-session.txt" --require-live-output-clean
```

The trusted transcript must include the same user-visible prose the user saw. The helper appends the generated final receipt to that transcript before the second hygiene pass, syncs it into `/tmp/lolla_${LOLLA_RUN_ID}_live_transcript.txt`, and archives it as `live_transcript.txt`. Use this only for a complete capture; a manually maintained transcript without this flag remains `live_output_health: not_checked`.

**Do not produce user-facing narrative output at Step 9.** Beat 4 already closed with *"Audit complete. I'm opening the full breakdown now."* — that's the bridge to the Observatory. The artifact paths, cost, and Observatory URL are consolidated in the final functional receipt at Completion (after Step 10). A long *"The Observatory is live at … it has the full audit: all [N] findings…"* narrative at Step 9 is the close-summary anti-pattern banned in `chat-output-format.md`.

<a id="step-10-archive-run"></a>

## Step 10: Archive Run

Step 9's helper already archives the run's core artifacts into a persistent
case folder under the configured private archive root so the run survives
temporary-file cleanup and stays accessible for later review, memo re-rendering,
or stability-harness analysis. Step 10 is the silent verification point:
confirm the helper completed archive verification. Do not reconstruct or rerun
`archive_run.py` by hand unless the helper failed.

The launched browser Observatory opens on the currently served run. Its `Cases` tab also lists local archived runs from `~/.local/share/lolla/runs/` (or `$LOLLA_ARCHIVE_DIR`) and can load those archived runs into the main SPA view. The server-rendered `/audit/*` telemetry panels remain scoped to the active served run for now; use `scripts/compare_archived_runs.py` or `scripts/export_reasoning_trace_dataset.py` for historical comparison and dataset export.

The archive script:

- Finalizes V60 consideration telemetry before copying artifacts. If V60 was active and the private ledger is missing, the run is marked degraded with `v60_consideration_ledger_missing` instead of looking complete.
- Runs the product-output hygiene scanner before copying artifacts. If revised text, memo markdown, or memo-note fields leak internal terms such as V60, affordance, chunk, ledger, lane, pipeline, or independent review, `run_health.product_output_health` becomes `unsafe` and the run is degraded with `product_output_leak`.
- Runs the live-output hygiene scanner before copying artifacts. If `/tmp/lolla_${LOLLA_RUN_ID}_live_transcript.txt` exists, it is scanned as the `live_narration` product surface; detected leaks set `run_health.live_output_health` to `unsafe`, while a manually maintained no-leak transcript is `not_checked` unless a complete trusted transcript was explicitly supplied to the finalizer. If it is missing, `live_output_health` becomes `missing` without degrading archive compatibility unless the explicit `--require-live-output-clean` gate was run.
- Reads the core/optional artifacts from `/tmp/lolla_${LOLLA_RUN_ID}_*`, including the authoritative conversation, separately bounded processing view, provider budget, result, revised answer, memo, constitutional graph-survival ledger, V60/private-table ledgers, trace inputs, reviews, and control input. `result.json` carries the complete active-plus-reserve graph portfolio; `constitutional_graph_survival_ledger.json` carries Step 6 apply/reject/park custody. Missing optional artifacts are skipped gracefully, while required active ledgers fail their Step 6 finalizer before archive.
- Computes a case fingerprint from `extraction.decision_situation` (first 120 chars, normalized).
- Finds-or-creates a case folder. Matching uses **exact captured-conversation hash first**, then exact/fuzzy extractor fingerprint matching against stored fingerprints (token-set Jaccard ≥ 0.80). Identical captured reruns archive into the same case even when `decision_situation` is paraphrased differently by extraction. Matching is done against the manifest inside each case folder, not against folder names, so user renames of case folders do not break future matching. Legacy manifests without `conversation_hashes` are still matchable because archive time can compute hashes from archived `conversation.txt` files.
- Auto-names new cases with a slug derived from the first 3-4 significant words of `decision_situation` (e.g., `grant-equity-partnership-status`). Users can rename via `mv` — matching will still find the folder via manifest.
- Copies the artifacts into `{case_folder}/${LOLLA_RUN_ID}/` and updates `{case_folder}/.case-manifest.json` with the new fingerprint (added as an alias), the run_id, and metadata-only `risk_mode`.
- Enforces owner-only local custody before completion: archive/case/run directories are `0700`, and manifests plus archived files are `0600`. The setup environment also establishes `umask 077` for run-scoped temp artifacts.
- Generates `{case_folder}/${LOLLA_RUN_ID}/graph_survival_report.json` and `.md`, operator reports showing graph candidates, embedding recalls, selected cards, Step 6 uptake, suppressed/unadjudicated signals, and visible/private survival.
- Generates `{case_folder}/${LOLLA_RUN_ID}/agent_result.json`, a compact `lolla_agent_result.v2` handoff for machine callers with neutral review action, risk mode, provider-boundary summary, exact/estimated usage custody, and compact capture-adequacy status, plus `/tmp/lolla_${LOLLA_RUN_ID}_agent_result.json` as a convenience copy.
- Generates `{case_folder}/${LOLLA_RUN_ID}/control_result.json` only when `control_input.json` was supplied. This optional `lolla_control_result.v1` wrapper maps Lolla's existing `caller_action` to control-plane outcome language and preserves compact external references; it does not approve actions or replace policy, sandbox, proxy, approval, identity, or observability systems. When present, it also writes `/tmp/lolla_${LOLLA_RUN_ID}_control_result.json` as a convenience copy.
- Generates `{case_folder}/${LOLLA_RUN_ID}/evaluation.json`, a deterministic `lolla.evaluation.v0` run-readiness receipt for artifact presence, schema validity, reasoning-trace custody, product/live hygiene, provider-boundary policy, capture adequacy, and caller conservatism. It is not an advice-quality score, does not use an LLM judge, and writes `/tmp/lolla_${LOLLA_RUN_ID}_evaluation.json` as a convenience copy.
- Generates `{case_folder}/${LOLLA_RUN_ID}/reasoning_trace.json`, a local-only custody manifest with artifact paths, SHA-256 hashes, `risk_mode`, run health, capture-adequacy metadata, optional control-plane references, usage summary, pressure-check state, private-custody status, reasoning-lens IDs, model-call telemetry, and future slots for commitment candidates, decision packets, and outcome reviews. It indexes raw artifacts, including `agent_result.json`, optional `control_input.json` / `control_result.json`, and `evaluation.json`, without duplicating conversation or memo text.
- `/tmp` originals are **not** moved or deleted — Observatory and subsequent commands continue to reference them as in-flight state.

**Environment overrides (optional):**

- `$LOLLA_CASE_ID` — force a specific case folder (skips fingerprint match). Useful when a run should be grouped with an existing case despite a mismatched `decision_situation`, or when the user wants a specific folder name from the first run.
- `$LOLLA_ARCHIVE_DIR` — override the archive root (default: `~/.local/share/lolla/runs/`).
- `$LOLLA_AUDIT_MODE` — metadata-only audit mode. Accepted values are `quick`, `standard`, `deep`, `high_stakes`, and `stability`; missing or empty defaults to `standard`, and invalid explicit values fail before model calls. The normalized value is persisted as `risk_mode` but does not change prompts, cost, Step 7, replay, or high-stakes policy yet.

**Do not surface the archive path at Step 10.** The final receipt says that the
archive was saved privately without printing its location. Step 10 runs
silently from the user's perspective.

<a id="completion"></a>

## Completion

After the full cycle, send only the exact final receipt between
`USER_RECEIPT_BEGIN` and `USER_RECEIPT_END`. Do not write a second summary or
reconstruct a receipt by hand.

The receipt always states the same-context boundary: the reconsideration
happened in this conversation and was not an external check. It reports the
actual Observatory URL when one is live, says that the memo and archive were
saved privately, and reports the final estimated cost. It does not print
runtime paths, archive paths, operator logs, environment-state files, or port
fallback detail.

If run health is not healthy, the receipt begins with one plain-language
warning naming the incomplete stage or check. A partial provider result remains
partial even when other artifacts completed; no later artifact erases missing
semantic coverage. Do not call such a run clean.

A manual narration artifact can reveal leaks but cannot prove that the whole
Codex tool surface was clean. Only an explicitly supplied complete trusted
capture can support complete-surface `clean`; otherwise the receipt and archive
must preserve `not_checked` or the applicable incomplete state.

If a receipt genuinely requires an operator override, place the exact text in
the private runtime with `persist_private_step.sh --kind receipt`, then
invoke `finalize_and_archive.sh --run-id RUN_HANDLE
--private-receipt-override`. Never author the override in a visible shell
command, heredoc, edit card, or argument. The finalizer must succeed and
re-archive before that receipt is sent.
