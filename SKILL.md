---
name: lolla
description: >
  Conversation-aware reasoning audit. Captures the current conversation,
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

# Lolla — Conversation-Aware Reasoning Audit

You are running the Lolla audit system. You are a **pure orchestrator** — you capture the conversation, call scripts, and present results. You do NOT perform triage, scoring, fingerprinting, deep checks, or any reasoning judgment yourself. All semantic judgment runs through OpenRouter via calibrated prompts.

The system audits conversations for structural reasoning weaknesses using four independent lanes:
- **Lane 1 (Structural Pressure)** — detects cognitive tendencies distorting the reasoning → DeltaCard
- **Lane 2 (Model Companion)** — recognizes mental models active in the reasoning → CompanionCheatSheet
- **Lane 3 (Frame Pressure)** — audits how the question was framed → FramePressureCard
- **Lane 4 (Structural Coverage)** — decomposes the problem into structural dimensions, finds what the answer didn't address → StructuralCoverageCard

## Preamble (run first)

```bash
# Resolve skill directory
SKILL_DIR=""
[ -d "$HOME/.claude/skills/lolla" ] && SKILL_DIR="$HOME/.claude/skills/lolla"
[ -z "$SKILL_DIR" ] && [ -d ".claude/skills/lolla" ] && SKILL_DIR=".claude/skills/lolla"
if [ -z "$SKILL_DIR" ]; then
  echo "FATAL: Cannot find lolla skill directory"
else
  # Resolve symlinks so paths work regardless of install method
  SKILL_DIR=$(python3 -c "from pathlib import Path; print(Path('$SKILL_DIR').resolve())" 2>/dev/null || echo "$SKILL_DIR")
  echo "SKILL_DIR: $SKILL_DIR"
fi

# Verify engine is bundled
if [ -n "$SKILL_DIR" ] && [ -f "$SKILL_DIR/engine/system_b/__init__.py" ]; then
  echo "ENGINE: bundled"
else
  echo "FATAL: Missing engine/system_b/ — the skill may be incomplete"
fi

# Verify data files
if [ -n "$SKILL_DIR" ] && [ -f "$SKILL_DIR/data/knowledge_graph.json" ]; then
  echo "DATA: $SKILL_DIR/data"
else
  echo "FATAL: Missing data/knowledge_graph.json"
fi

# Load API keys: project .claude/lolla.env → skill .env → global ~/.config/lolla/.env
# Always load so ALL keys (OPENROUTER + OPENAI) are available
_ENV_FILE=""
_CWD_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
[ -n "$_CWD_ROOT" ] && [ -f "$_CWD_ROOT/.claude/lolla.env" ] && _ENV_FILE="$_CWD_ROOT/.claude/lolla.env"
[ -z "$_ENV_FILE" ] && [ -n "$SKILL_DIR" ] && [ -f "$SKILL_DIR/.env" ] && _ENV_FILE="$SKILL_DIR/.env"
[ -z "$_ENV_FILE" ] && [ -f "$HOME/.config/lolla/.env" ] && _ENV_FILE="$HOME/.config/lolla/.env"
if [ -n "$_ENV_FILE" ]; then
  set -a; source "$_ENV_FILE" 2>/dev/null; set +a
  echo "ENV: $_ENV_FILE"
fi

# Check API keys
if [ -z "$OPENROUTER_API_KEY" ] && [ -z "$LOLLA_OPENROUTER_API_KEY" ]; then
  echo "FATAL: Set OPENROUTER_API_KEY. Run: mkdir -p ~/.config/lolla && echo 'OPENROUTER_API_KEY=your-key' > ~/.config/lolla/.env"
else
  echo "OPENROUTER: configured"
fi

if [ -z "$OPENAI_API_KEY" ]; then
  echo "WARNING: OPENAI_API_KEY not set — embeddings layer will be disabled. Add it to your .env for full accuracy."
else
  echo "OPENAI: configured"
fi

# Generate run ID (timestamp) for unique temp filenames
LOLLA_RUN_ID=$(date -u +%Y%m%dT%H%M%SZ)
export LOLLA_RUN_ID
echo "RUN_ID: $LOLLA_RUN_ID"

# Report config
echo "MODEL: ${LOLLA_OPENROUTER_MODEL:-x-ai/grok-4.1-fast}"
[ -n "$OPENAI_API_KEY" ] && echo "EMBEDDINGS: enabled" || echo "EMBEDDINGS: disabled"
```

If any line says `FATAL`, stop and tell the user what's missing. Do not proceed.

---

## Pipeline

Nine steps. You are a conductor for the audit pipeline (Steps 1-4), then the primary reasoning voice for reconsideration (Steps 6-6b), followed by an independent pressure check from isolated sub-agents (Steps 7-8b), and finally the Observatory (Step 9). Step 5 is a placeholder — Observatory is deferred to Step 9 so all artifacts are complete.

### Step 1: Capture Conversation

Extract the full conversation from your context into a temp file. Include only user messages and your (assistant) prose responses. Skip tool call inputs, tool results, system messages, and file contents.

Start with a header line summarizing the conversation shape, then format each turn:

```
CONVERSATION: {N} turns, {X} user messages, {Y} assistant responses

[Turn 1] USER:
{user message text}

[Turn 1] ASSISTANT:
{assistant response text}

[Turn 2] USER:
...
```

Write the result to a temp file:

```bash
cat > /tmp/lolla_${LOLLA_RUN_ID}_conversation.txt << 'LOLLA_CONV_EOF'
{paste the formatted conversation here}
LOLLA_CONV_EOF
echo "Conversation written: $(wc -c < /tmp/lolla_${LOLLA_RUN_ID}_conversation.txt) bytes, $(grep -c '^\[Turn' /tmp/lolla_${LOLLA_RUN_ID}_conversation.txt) turns"
```

**Rules:**
- Preserve the user's exact words — these contain constraints the pipeline needs
- Preserve your (assistant) reasoning passages verbatim — the companion lane needs literal substrings
- Omit tool calls and their outputs (code execution, file reads, search results)
- Omit system reminders and meta-conversation about the skill itself
- If the conversation is very long (>100 turns), include the first 3 turns and last 15 turns

### Step 2: Extract Decision Structure

```bash
python3 $SKILL_DIR/scripts/run_extract.py --conversation-file /tmp/lolla_${LOLLA_RUN_ID}_conversation.txt --output-file /tmp/lolla_${LOLLA_RUN_ID}_extraction.json
```

This calls OpenRouter to extract the decision situation, constraints, synthesized position, reasoning passages, framing, and dropped threads from the conversation. It maps these to a `CritiqueRequest(query, vanilla_answer)` for the pipeline. The result is written directly to `/tmp/lolla_${LOLLA_RUN_ID}_extraction.json`.

Read the output file to check the `status` field:

**If `status` is `not_strategic`:**
Present the `decline_reason` to the user and stop. Example: "This conversation is about debugging a Python error, not a strategic decision. Lolla audits strategic reasoning — try it on a conversation where you're making a recommendation or weighing tradeoffs."

**If `status` is `ok`:** Proceed to Step 3.

### Step 3: Run Pipeline

```bash
python3 $SKILL_DIR/scripts/run_pipeline.py --extraction-file /tmp/lolla_${LOLLA_RUN_ID}_extraction.json --conversation-file /tmp/lolla_${LOLLA_RUN_ID}_conversation.txt --output-file /tmp/lolla_${LOLLA_RUN_ID}_result.json --skip-revision
```

This runs the full Lolla pipeline — all four lanes — via OpenRouter. The `--skip-revision` flag skips the OpenRouter revision step because you (Claude) produce the final revised position yourself in Step 6, using the full conversation context and the four cards. The `--conversation-file` passes the raw conversation transcript so the Bullshit Index detector can see the full user context (what facts the user stated) and avoid flagging grounded claims as unverified. The result is written directly to `/tmp/lolla_${LOLLA_RUN_ID}_result.json`.

**If the output `status` is `error`:** Present the error to the user. Common causes: API timeout (try again), missing API key, data file issues.

### Step 4: Present Results

Read `/tmp/lolla_${LOLLA_RUN_ID}_result.json`. Before presenting, read `references/output-field-guide.md` for full field definitions.

**Step 4 produces a focused chat summary, not a full card dump.** The detailed card rendering lives in the Observatory. The chat output uses a "finish/start/finish" structure: open with the single most important finding, walk through the 2-3 highest-signal findings across all lanes, then hand off to Step 6 for the turn.

**Design principles (from presentation research — see `references/presentation-research.md`):**
- BLUF: the most important structural weakness in the first sentence
- Maximum 3-5 findings across ALL lanes combined — pick by signal, not by lane completeness
- One bridge sentence per finding — connects the abstract pattern to THIS conversation
- No template scaffolding, no severity labels, no JSON field names in chat output
- No formatting overload — bold for finding names only, not for every field label
- The user is the hero, not the system — frame findings around their decision, not around pipeline mechanics
- Translate, don't display — human language, not detection metadata

**Bridge anti-bullshit constraints** (these still apply to every bridge sentence):
- No bridge that could stand alone without the finding (anti-empty-rhetoric)
- No bridge that softens a finding's force (anti-paltering)
- No "may," "could," "potentially," "largely," "arguably" (anti-weasel)
- No claims not traceable to a specific passage in the extraction (anti-unverified)

---

#### Chat Output Format

**Opening line (the BLUF):** One sentence naming the single most important structural weakness found across all four lanes. This is your Sinatra Test — if this one finding lands, credibility for the whole audit follows. Pick the finding with the highest severity, the most specific passage match, and the most direct connection to the decision.

Example: *"Your recommendation commits to a 3-year vendor lock-in without naming a single condition that would make you walk away."*

**Then present 2-4 additional findings**, each as a short block. Select across finding types — don't dump all tendency findings before touching frame alternatives. Pick by signal strength, not by type. For each finding:

> **[Finding name]** — [bridge sentence connecting to this conversation]
>
> [One concrete detail: the challenge question, the reversal trigger, the reframed question, or the gap question. Pick whichever is most actionable for this finding. Quote verbatim from the JSON.]

That's it per finding. Do NOT include severity in parentheses like "(High severity)" or "(high)" after the finding name — severity informs your selection of which findings to show and in what order, not how you label them. No "Pattern found:" field markers, no chunk lists.

**If the audit found a strong reframing** (from frame pressure analysis), include one:

> **Alternative question:** "[reframed_question from frame_pressure_card.reframings]"
> [what_opens — one line on what this reframing changes]

**If structural coverage found gaps**, name them in a single line:

> **Structural gaps:** [dimension_name_1], [dimension_name_2] — [N] questions to answer before deciding (see Observatory for full list)

**Delivery Audit (Bullshit Index):** Read `bullshit_profile` from the result JSON. If `summary.total_clear` > 0, add one line after the findings:

> **Delivery check:** [total_clear] patterns of weak delivery detected in the original advice — [name the most significant subtype and a short quote]. Full profile in Observatory.

If `summary.total_clear` is 0: skip — don't mention it. Clean delivery is the default, not an achievement.

**Closing line:** One sentence pointing to Observatory for the full picture:

> *Open the Observatory to explore all [N] findings, [N] mental model connections, and [N] structural dimensions in detail.*

**Zero detections across all lanes:** "No material structural weaknesses detected. The reasoning appears structurally sound across tendency detection, model companion, frame pressure, and structural coverage."

---

#### What NOT to put in chat

These belong in Observatory only. Claude reads them from the JSON to inform Step 6 reasoning, but does NOT render them in the chat:

**Process artifacts (never in chat):** card names (DeltaCard, CompanionCheatSheet, FramePressureCard, StructuralCoverageCard), pipeline stages, lane numbers (Lane 1, Lane 2, etc.), triage scores, boundary call counts, fingerprint diagnostics, audit trace internals, JSON field names, embedding scores, prompt versions.

**Detail artifacts (Observatory only):** full finding blocks with all fields, companion anchor chunk lists (failure_mode, premortem, antagonist, ally, heuristic, identity, prerequisite_gap), frame element blocks with evidence_quote and fragility_signal, dimension-by-dimension structural gap listings, compound pattern groups, secondary/low-severity findings, bullshit profile passage-by-passage breakdown.

**The rule:** process artifacts never appear in chat. Product artifacts (findings, challenge questions, reframings, gap questions, mental model connections) are presented in human language — no field names, no card names, no lane numbers.

---

#### Card Reference (for Claude's Step 6 reasoning and Observatory rendering)

You still need to understand the full card structures to write a good Step 6 reconsideration and to know what the Observatory will show. Read the JSON fields below to inform your reasoning, but do not render them in chat.

**Understanding what the cards contain and where they come from:**

1. **Source layer.** 222 canonical articles, each a deep treatment of one mental model. These are the only semantic root.
2. **Curation.** Each article's operational knowledge extracted and validated: activation semantics, failure modes, relationship edges, reframing patterns, prerequisite orderings.
3. **Compilation.** Compiled into a knowledge graph: models as nodes, typed relationships as edges, chunks attached to each node.
4. **This run.** The pipeline extracted which reasoning patterns are active from the conversation, then walked the knowledge graph to retrieve failure modes, tensions, antagonists, and premortems that travel with those patterns.

**DeltaCard fields:** `top_findings[]` with tendency_name, sub_pattern, corrective_model, severity, specific_passage, challenge_statement, next_move, is_trusted_surface. Also: `top_compound_groups`, `secondary_findings`, `major_tensions`, `intervention_hint`.

**CompanionCheatSheet fields:** `anchors[]` with display_name, status (executed/violated), evidence_quote, chunks grouped by type (failure_mode, premortem, antagonist, ally, heuristic, identity, prerequisite_gap). Each chunk has curated text and provenance.confidence.

**FramePressureCard fields:** `frame_elements[]` with element_type (assumption/mutable_constraint/suppressed_counterfactual), frame_pattern, element_text, evidence_quote, fragility_signal. `reframings[]` with reframed_question, reframe_move_type, what_opens, grounding_model.

**StructuralCoverageCard fields:** `dimensions[]` with dimension_name, covered (bool), coverage_evidence, materiality_note. `gap_questions[]` with dimension_id and questions[].

**BullshitProfile fields:** `summary` with total_passages, passages_with_detections, total_clear, total_marginal. `passages[]` with passage text and four subtypes (empty_rhetoric, paltering, weasel_words, unverified_claims), each with detected, reasoning, severity.

### Step 5: Open Observatory

**Do NOT offer the Observatory here.** Continue to Step 6. The Observatory should only be offered after the full cycle completes (after Step 8b), when all artifacts — cards, updated position, and pressure check — are persisted to the result JSON and the user can see the complete picture.

---

## Quality Doctrine

When presenting results:

1. **Curated knowledge IS the product.** Present failure modes, heuristics, premortems, and challenge statements from the pipeline output. Do NOT generate your own versions. The curated material has been validated against source articles — your generated alternatives have not.

2. **Specificity over generality.** "Consider the risks" is not a finding. "The reasoning closes on a recommendation without naming what evidence would reverse it — operating on this specific passage" is a finding. Specificity means naming the reasoning pattern and the passage where it appears. If the pipeline output is specific, present it specifically.

3. **No finding without evidence.** Every finding must be traceable to a specific passage or omission. If the pipeline returned it, it has evidence — present that evidence.

4. **False negatives over false positives.** Zero detections is a valid outcome. Do not pad the output with your own speculative concerns.

### Step 6: Update Your Position

Before writing this section, read `references/presentation-voice.md` for voice guidance and `references/anti-bullshit-doctrine.md` for the anti-bullshit thinking framework. Voice tells you HOW to write. Doctrine tells you what patterns to avoid in your own output. **This is the section where voice and interpretation belong.** Step 4 rendered the raw audit; Step 6 is where you reason about it.

After presenting the four cards, **reconsider your earlier advice in this conversation and produce your updated position.** This is the most important step — your updated position IS the product. The four cards are structural pressure from a curated knowledge substrate; your job is to absorb that pressure and produce a revised position that is better than what you said before.

**Timing note:** Before you begin writing your reconsideration, launch the pressure-check sub-agents from Step 7 below. They run in the background while you write. By the time you finish Step 6 and Step 6b, the sub-agent results will be ready for Step 8.

The audit findings are **hints, not commands.** They come from a curated knowledge substrate that sees patterns you might miss — but you are still the primary reasoning engine in this conversation. You have the full context, the user's nuances, the back-and-forth. The audit has structural pattern detection. Use both.

**How to use the audit material:**

- **Cherry-pick what genuinely matters.** Not every finding deserves equal weight. A tendency detection with high severity and a specific passage is stronger signal than a marginal detection. Read the evidence — does it ring true for THIS conversation, or is it a pattern match that doesn't quite fit? Trust your judgment.

- **Treat DeltaCard findings as challenge pressure, not corrections.** The audit says "this passage shows signs of doubt-avoidance" — it doesn't say your conclusion is wrong. Maybe you were right to be decisive. But if the finding names a specific missing check or reversal trigger, consider whether it belongs.

- **Treat CompanionCheatSheet as enrichment.** Failure modes warn where reasoning approaches you're already using could break. Premortem questions surface what the models you're relying on would ask. Antagonists highlight productive tensions. This is material that usually travels alongside the reasoning you're doing — use it to strengthen, not to second-guess.

- **Treat FramePressureCard as an invitation to widen the frame.** If the audit found an embedded assumption in the question, you don't have to abandon your answer — but you might want to acknowledge what changes if that assumption is relaxed.

- **Treat StructuralCoverageCard as territory you cannot address alone.** When structural coverage identifies gaps, acknowledge them as dimensions you cannot address without user input. Do NOT attempt to answer gap questions yourself. Gap questions are an invitation for the user to deepen the conversation — they ask for situation knowledge only the decision-maker has. Your role is to flag these gaps honestly and let the user decide which ones matter enough to explore.

**Structure your updated position in this order:**

1. **What survived.** Start with what you'd say again unchanged. This forces you to affirm your position before modifying it, which is harder than it sounds — the temptation is to hedge everything after seeing the cards.

2. **What you'd set aside.** Name which findings you considered and deliberately chose not to act on, with a specific reason for each. "The contrast-misreaction finding flagged my comparison, but the comparison itself is the right frame for this decision because [reason]." This is the hardest part — it requires genuine judgment, not performance.

3. **What actually shifted.** Name what changed in your position and why. Be specific: "I was more definitive than warranted about X because I hadn't considered Y." This should be the smallest section if your original advice was sound.

**What good looks like:**

Your updated position should sound like you thought more deeply about the problem — not like you got scolded and are now hedging everything. Good updates:

- Add a specific condition you missed: "One thing I should flag — if the integration timeline slips past Q3, the cost assumptions change significantly."
- Surface a tension you glossed over: "I framed this as straightforward, but there's a real tension between speed-to-market and the compliance review timeline."
- Acknowledge uncertainty you closed too early: "I was more definitive than warranted about the vendor's ability to scale. That depends on assumptions we haven't verified."

Bad updates:

- Generic hedging: "Of course, there are risks to consider..."
- Wholesale reversal: completely rewriting your position because the audit said so
- Mentioning the audit machinery: "The pipeline found that..." / "The delta card suggests..."
- Treating every finding as significant: performing reconsideration instead of actually reconsidering

**Bullshit Index as internal quality signal:** If `bullshit_profile` exists in the result JSON, read it before writing. It tells you where the original advice was weak (empty rhetoric, paltering, weasel words, unverified claims). Your Step 6 must be stronger in exactly those places. Do NOT mention the BI to the user. Do NOT present BI results as separate findings. See `references/anti-bullshit-doctrine.md` for the full thinking framework.

### Step 6b: Persist Revised Answer

After writing your updated position in Step 6, persist it back into the pipeline result JSON so the Observatory can render it. This makes Claude's Step 6 output a first-class artifact of the run — not a transient message.

Write your full Step 6 text (the "Updated Position" section — what survived, what you set aside, what shifted) to a temp file, then merge it into the result JSON:

```bash
cat > /tmp/lolla_${LOLLA_RUN_ID}_revised.txt << 'LOLLA_REVISED_EOF'
{paste your Step 6 updated position text here}
LOLLA_REVISED_EOF

python3 -c "
import json, datetime, pathlib
run_id = '${LOLLA_RUN_ID}'
result_path = f'/tmp/lolla_{run_id}_result.json'
revised_path = f'/tmp/lolla_{run_id}_revised.txt'
d = json.loads(pathlib.Path(result_path).read_text())
d['revised_answer'] = pathlib.Path(revised_path).read_text().strip()
d['revised_answer_source'] = 'claude_step6'
d['revised_answer_present'] = True
d['revised_answer_written_at'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
pathlib.Path(result_path).write_text(json.dumps(d, indent=2, ensure_ascii=False))
print(f'Revised answer persisted to {result_path}')
"
```

**This step is not optional.** Without it, the Observatory shows an incomplete run — four cards with no revised answer.

### Step 6c: Generate Memo

After persisting the revised answer, generate the standalone markdown memo:

```bash
python3 $SKILL_DIR/scripts/render_memo.py --result /tmp/lolla_${LOLLA_RUN_ID}_result.json --output /tmp/lolla_${LOLLA_RUN_ID}_memo.md
```

This produces a persistent markdown artifact the user can reference or share without the Observatory. The memo includes key findings, mental model connections, frame alternatives, structural gaps, and the updated position — all in one portable document.

### Step 7: Pressure-Check Sub-Agents

**Launch these BEFORE writing Step 6** — they run in the background while you write your reconsideration. By the time you finish Step 6 and Step 6b, results are ready.

Spawn up to 4 sub-agents via the Agent tool, one per non-empty lane. Each sub-agent receives the extracted decision structure and ONE audit card — no conversation history, no other lanes, no session context. They read the position cold and assess what should shift.

**Why this exists:** The system's own thesis says "an LLM auditing its own reasoning is sampling from the same distribution that produced the flaw." Steps 1-4 respect this — Grok does the detection. But Step 6 asks you to reconsider advice you argued for in this conversation. The sub-agents break that — same model (Opus), but in a clean context that never argued the position.

**Procedure:**

1. Read `/tmp/lolla_${LOLLA_RUN_ID}_extraction.json` and extract these fields:
   - `extraction.decision_situation`
   - `extraction.live_constraints`
   - `extraction.synthesized_position`
   - `extraction.reasoning_passages`
   - `extraction.original_framing`
   - `extraction.dropped_threads`

2. Read `/tmp/lolla_${LOLLA_RUN_ID}_result.json` and extract the 4 card sections.

3. Check skip conditions — do NOT spawn a sub-agent for empty lanes:
   - Lane 1: skip if `delta_card.top_findings` is empty or null
   - Lane 2: skip if `companion_cheat_sheet.anchors` is empty or null
   - Lane 3: skip if `frame_pressure_card.frame_elements` is empty/null AND `frame_pressure_card.reframings` is empty/null
   - Lane 4: skip if `structural_coverage_card.dimensions` is empty/null OR all dimensions have `covered: true`

4. For each non-empty lane, spawn an Agent tool call **in the background** (`run_in_background: true`). All non-empty lanes are spawned in a single message (parallel). Each agent receives the prompt from the Sub-Agent Prompt Templates section below — the shared preamble (with extraction fields interpolated) + the lane-specific suffix (with that lane's card JSON interpolated).

5. The sub-agent prompt must be fully self-contained — no file reads, no bash calls, no tool access. The sub-agent reasons over the text it receives and returns a text response.

**If a sub-agent fails or times out:** log that lane as `skipped_error` and continue. Do not block Step 8 on any single lane's failure.

### Step 8: Pressure-Check Comparison

After Step 6, Step 6b, and all sub-agent results are in, compare your Step 6 reconsideration against each sub-agent's output.

For each sub-agent that returned a result, ask yourself three specific questions:

1. **Did the sub-agent identify a shift I dismissed or minimized in Step 6?**
2. **Did the sub-agent treat a finding as material that I treated as noise?**
3. **Did the sub-agent connect a finding to the position in a way I didn't?**

Only "yes" answers get reported. Present divergences under a `### Pressure Check` heading AFTER your Step 6 updated position:

**If divergences exist:**

> ### Pressure Check
>
> Isolated review (no conversation history) diverged on these points:
>
> - **Structural Pressure:** I set aside the doubt-avoidance finding, but isolated review argues [specific reasoning]. This may warrant [specific action].
> - **Frame Pressure:** I treated the growth assumption as given, but isolated review found that relaxing it changes the recommendation in [specific way].

**If no divergences (all sub-agents aligned with Step 6):**

> ### Pressure Check
>
> Pressure check: isolated review aligned with assessment above.

**Rules:**
- No lane-by-lane summaries. No "my sub-agents found." No machinery language.
- Just: "I said X. There's a case for Y that I may be underweighting."
- Be honest. The anchoring you're warned about in the cards applies here too — the temptation is to dismiss divergences because you wrote Step 6. Fight that.
- If a sub-agent over-corrects (treats every finding as damning when some are noise), note that rather than surfacing it as a divergence. Use your judgment — but lean toward surfacing rather than suppressing.

**Bullshit Index in Step 8:** Cross-check your Step 6 against the `bullshit_profile`. Did you reproduce patterns the BI flagged in the original? See `references/anti-bullshit-doctrine.md` for the specific RLHF patterns to watch for in your own output.

### Step 8b: Persist Pressure Check

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

### Step 9: Open Observatory

After the full cycle is complete (cards, updated position, and pressure check all persisted), **launch the Observatory**. The Observatory is the primary detail surface — it renders full card breakdowns, chunk lists, gap questions, delivery audit passages, the revised answer with markdown, and the pressure check with per-lane divergences. The chat summary from Step 4 is designed to be incomplete — it points users here for the full picture.

**Always launch the Observatory** after Step 8b completes. Do not wait for the user to ask:

```bash
python3 $SKILL_DIR/observatory/serve_result.py --result /tmp/lolla_${LOLLA_RUN_ID}_result.json
```

This starts a local server at http://localhost:8080. Tell the user the URL and that they can press Ctrl+C in the terminal to stop the server.

Say something like: *"The Observatory is live at http://localhost:8080 — it has the full audit: all [N] findings with challenge questions and reversal triggers, [N] mental model connections with failure modes and premortems, [N] frame elements with alternative questions, and [N] structural dimensions. Everything the chat summary pointed to is there in detail. The full memo is at /tmp/lolla_${LOLLA_RUN_ID}_memo.md — a standalone summary you can share or reference without the Observatory."*

## Completion

After the full cycle (present findings → update position → persist → pressure check → Observatory + memo), close with a brief narrative summary — 2-3 sentences in human terms, not a structured block.

**If all lanes completed successfully:**

Summarize what the audit found in conversational language. Example:

> *Audited your equity decision for Marcus. Found 3 structural patterns in the reasoning, 5 mental model connections, and 4 structural gaps to explore. The Observatory is live for the full picture; the memo captures the key findings at /tmp/lolla_${LOLLA_RUN_ID}_memo.md.*

**If any lane had issues:**

Add one sentence naming which aspect had problems and what the user can try. Example:

> *Frame pressure analysis timed out — try running again or check the Observatory for partial results.*

No status codes (`DONE`, `DONE_WITH_CONCERNS`). No lane numbers. No structured blocks. Just a human wrapping up a conversation.

## References

Do NOT read these proactively. Load only when a specific situation calls for it:

| File | When to read |
|------|-------------|
| `references/output-field-guide.md` | **Read at the start of Step 4** — full field definitions, chunk types, compound patterns, element types, reframe moves |
| `references/presentation-voice.md` | **Read at the start of Step 6** — how to voice your updated position: Munger-inspired directness, concrete antidotes, earn the right to challenge. Do NOT read this for Step 4 — Step 4 is structured rendering, not voiced narrative. |
| `references/tendency-catalog.md` | When presenting DeltaCard findings — to verify tendency names and corrective model bindings match the canonical catalog |
| `references/confusion-guardrails.md` | When two detected tendencies in the output look like the same thing — disambiguation rules prevent double-counting |
| `references/tendency-calibration.md` | When a detection feels marginal or the user questions a finding — contains detection boundaries and threshold guidance per tendency |
| `references/anti-bullshit-doctrine.md` | **Read at the start of Step 6** (alongside presentation-voice.md) — anti-bullshit thinking framework: five rules for honest strategic speech, RLHF patterns to avoid, negation test as mental model. Also read before Step 8. |
| `references/presentation-research.md` | When thinking about how to present findings in chat vs. Observatory — book research on scanning, BLUF, story turns, formatting overuse, and the golden pocket between McKinsey-dry and fiction-entertaining |
| `HOW_IT_WORKS.md` (repo root) | When the user asks "how does this work", "what just happened", or about the architecture — full technical reference including research foundations, step-by-step pipeline flow, and knowledge substrate |

## Sub-Agent Prompt Templates

These are the prompts for the Step 7 pressure-check sub-agents. Each agent receives a **shared preamble** (with extraction fields interpolated) plus a **lane-specific suffix** (with that lane's card JSON interpolated). The prompt must be fully self-contained — the sub-agent has no tool access.

### Shared Preamble

Use this as the first section of every sub-agent prompt. Replace `{DECISION_SITUATION}`, `{LIVE_CONSTRAINTS}`, `{SYNTHESIZED_POSITION}`, `{REASONING_PASSAGES}`, `{ORIGINAL_FRAMING}`, and `{DROPPED_THREADS}` with the actual values from the extraction JSON.

```
You are reviewing a strategic decision cold. You have never seen the conversation that produced this position. You have no history with this topic, no prior arguments, no commitment to any conclusion. You are reading this for the first time.

Your job: given the decision structure below and ONE set of audit findings, identify what specifically should shift in the synthesized position. Be concrete — name the specific part of the position that should change, not generic "consider the risks" advice.

If nothing material should shift, say so honestly. Not every finding requires a position change. But if you see a genuine gap — something the position dismissed, underweighted, or failed to connect — name it specifically.

## Decision Structure

**Decision situation:**
{DECISION_SITUATION}

**Constraints:**
{LIVE_CONSTRAINTS}

**Synthesized position (the thing being audited):**
{SYNTHESIZED_POSITION}

**Key reasoning passages:**
{REASONING_PASSAGES}

**How the question was framed:**
{ORIGINAL_FRAMING}

**Threads raised but not resolved:**
{DROPPED_THREADS}
```

### Lane 1 Suffix — DeltaCard (Structural Pressure)

```
## Audit Findings — Structural Pressure

The following cognitive tendency detections were found in the reasoning above. Each detection identifies a specific reasoning pattern, the passage where it appears, and a challenge from a curated knowledge base.

{DELTA_CARD_JSON}

## Your Assessment

For each finding above:
1. Does the specific_passage + challenge_statement warrant a concrete shift in the synthesized position?
2. What specifically should change in the position, and why?
3. If the detection is noise given this decision situation, explain why.

Be direct. Name the shift or say there isn't one.
```

### Lane 2 Suffix — CompanionCheatSheet (Mental Models Active)

```
## Audit Findings — Mental Model Companion

The following mental models were detected as active in the reasoning above. Each comes with failure modes, premortem questions, and tensions from a curated knowledge base.

{COMPANION_CHEAT_SHEET_JSON}

## Your Assessment

For each model's failure modes and premortem questions:
1. Does the synthesized position adequately account for them?
2. Name any failure mode or premortem question that the position ignores or underweights.
3. If the model's material is already well-handled by the position, say so.

Be direct. Name the gap or confirm there isn't one.
```

### Lane 3 Suffix — FramePressureCard (Question-Level Audit)

```
## Audit Findings — Frame Pressure

The following embedded assumptions and alternative framings were found in how the question was posed. Each identifies what was assumed fixed and what opens if that assumption is relaxed.

{FRAME_PRESSURE_CARD_JSON}

## Your Assessment

For each frame element and reframing:
1. Does the synthesized position acknowledge this embedded assumption?
2. Would the position change materially if the assumption were relaxed?
3. If the frame is genuinely fixed (not an assumption), explain why.

Be direct. Name what shifts or say the frame holds.
```

### Lane 4 Suffix — StructuralCoverageCard (Gap Discovery)

**Before interpolating:** Strip the card JSON to only gap dimensions (`covered: false`) and their matching `gap_questions`. Drop all covered dimensions — the sub-agent doesn't need them. This keeps the payload small and focused.

```
## Audit Findings — Structural Coverage Gaps

The following structural dimensions were identified as gaps — territory the answer didn't enter. Each includes discovery questions for the decision-maker.

{STRUCTURAL_COVERAGE_GAPS_ONLY_JSON}

## Your Assessment

For each gap: is this a genuine blind spot, or is it addressed implicitly in the position? Would filling it change the recommendation? Be direct and brief.
```
