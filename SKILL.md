---
name: lolla
description: >
  Conversation-aware reasoning audit. Captures the current conversation,
  extracts decision structure, and runs the full Lolla pipeline
  (structural pressure, model companion, frame pressure) via OpenRouter
  against a curated substrate of 224 mental models. Use when asked to
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

The system audits conversations for structural reasoning weaknesses using three independent lanes:
- **Lane 1 (Structural Pressure)** — detects cognitive tendencies distorting the reasoning → DeltaCard
- **Lane 2 (Model Companion)** — recognizes mental models active in the reasoning → CompanionCheatSheet
- **Lane 3 (Frame Pressure)** — audits how the question was framed → FramePressureCard

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
if [ -z "$OPENROUTER_API_KEY" ] && [ -z "$LOLLA_OPENROUTER_API_KEY" ]; then
  _ENV_FILE=""
  _CWD_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
  [ -n "$_CWD_ROOT" ] && [ -f "$_CWD_ROOT/.claude/lolla.env" ] && _ENV_FILE="$_CWD_ROOT/.claude/lolla.env"
  [ -z "$_ENV_FILE" ] && [ -n "$SKILL_DIR" ] && [ -f "$SKILL_DIR/.env" ] && _ENV_FILE="$SKILL_DIR/.env"
  [ -z "$_ENV_FILE" ] && [ -f "$HOME/.config/lolla/.env" ] && _ENV_FILE="$HOME/.config/lolla/.env"
  if [ -n "$_ENV_FILE" ]; then
    set -a; source "$_ENV_FILE" 2>/dev/null; set +a
    echo "ENV: $_ENV_FILE"
  fi
fi

# Check API keys
if [ -z "$OPENROUTER_API_KEY" ] && [ -z "$LOLLA_OPENROUTER_API_KEY" ]; then
  echo "FATAL: Set OPENROUTER_API_KEY. Run: mkdir -p ~/.config/lolla && echo 'OPENROUTER_API_KEY=your-key' > ~/.config/lolla/.env"
else
  echo "OPENROUTER: configured"
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

Four steps. You are a conductor, not a player.

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
python3 $SKILL_DIR/scripts/run_pipeline.py --extraction-file /tmp/lolla_${LOLLA_RUN_ID}_extraction.json --output-file /tmp/lolla_${LOLLA_RUN_ID}_result.json --skip-revision
```

This runs the full Lolla pipeline — all three lanes — via OpenRouter. The `--skip-revision` flag skips the OpenRouter revision step because you (Claude) produce the final revised position yourself in Step 6, using the full conversation context and the three cards. The result is written directly to `/tmp/lolla_${LOLLA_RUN_ID}_result.json`.

**If the output `status` is `error`:** Present the error to the user. Common causes: API timeout (try again), missing API key, data file issues.

### Step 4: Present Results

Read `/tmp/lolla_${LOLLA_RUN_ID}_result.json` and present three sections. **Present the curated knowledge from the output — do not generate your own analysis.** Field names in the pipeline output may vary slightly across versions — map to the closest match rather than failing silently.

---

Before presenting, read `references/output-field-guide.md` for full field definitions, chunk types, compound patterns, and reframe move types.

---

**Understanding what the cards contain and where it comes from.**

The three cards below were not generated for this conversation. Here is how they were produced:

1. **Source layer.** 224 canonical articles, each a deep treatment of one mental model (Circle of Competence, Power Dynamics, Optionality, etc.). These are the only semantic root — everything downstream traces back to them.

2. **Curation.** Each article was read in full and its operational knowledge extracted: when to activate the model, when it's dangerous, how it fails, what questions it forces, which other models it allies or conflicts with. Each extraction was validated against the source. This produced five waves of structured curation — activation semantics, failure modes and heuristics, relationship edges, reframing patterns, and prerequisite orderings.

3. **Compilation.** The curations were compiled into a knowledge graph: models as nodes, typed relationships as edges (ally, antagonist, tension), chunks attached to each node (failure_mode, premortem, heuristic, identity).

4. **This run.** The pipeline used the conversation once — to extract which reasoning patterns are active: which mental models you used, which tendencies are present, how the question was framed. After extraction, the conversation was consumed. The deterministic system then walked the knowledge graph using those extracted patterns as keys, retrieving the failure modes, tensions, antagonists, and premortems that the curated knowledge base says travel with those models.

A chunk that sounds general — like "Is the worst case bad enough?" — is not a vague prompt. It is a validated premortem question extracted from the canonical article on that model, selected because the conversation's reasoning activated that model. It is general in form because it describes how a reasoning pattern behaves across many situations. Your task is to hold each chunk against the specific conversation and see if there is a live connection. Some will connect sharply. Some won't. Both outcomes are honest — what matters is that you look.

---

#### DeltaCard — Structural Pressure

**Before presenting, check for overlap.** If two or more findings quote the same passage (or substantially overlapping text), do NOT present them as separate findings. Merge them: present the stronger finding (higher severity, more specific challenge) and note the compound pattern — "This passage also shows signs of [other tendency]." This prevents inflating finding count with redundant detections.

For each finding in `delta_card.top_findings` (after merging overlaps):

**[tendency_name] — [sub_pattern] / [corrective model]** (Severity: [severity])

- **Pattern found:** [quote `specific_passage`]
- **Challenge:** [`challenge_statement`]
- **Reversal trigger:** [`next_move`]

Also present `major_tensions` and `intervention_hint` when present. Use `is_trusted_surface` for your own confidence weighting (don't flag to user).

If `top_compound_groups` exist, present after findings:
> **Compound pattern: [label]** — [description]
> Tendencies: [member tendencies]

If `secondary_findings` exist: use `secondary_additional_pressures_note` if summarization is active, otherwise condense (tendency + severity + one-line challenge).

Zero detections: "No structural pressures detected."

**Example:**
> **Excessive Self-Regard — Overconfidence in Proprietary Advantage / Inversion** (Severity: high)
> - **Pattern found:** "Our engineering team is significantly stronger than any competitor in this space"
> - **Challenge:** Invert the build-vs-buy calculus: if the engineering team were average, would the recommendation change?
> - **Reversal trigger:** Benchmark velocity against two comparable projects on a 90-day deliverable.

---

#### CompanionCheatSheet — Mental Models Active

For each anchor in `companion_cheat_sheet.anchors`, lead with the practical insight — what it means for THIS decision — not with model taxonomy. The model name is attribution, not the headline.

Present the most actionable chunks first: failure modes that warn where this reasoning breaks, premortem questions that surface what hasn't been asked, antagonist tensions that highlight productive disagreement. Use chunk `provenance.confidence` for your own weighting. 7 chunk types exist (failure_mode, premortem, antagonist, ally, heuristic, identity, prerequisite_gap — see field guide); present whichever are present.

Null or empty: "No mental models detected with structural evidence in this conversation."

**Example:**
> The assumption that past market experience transfers to this new channel hasn't been tested. Eight years in one market creates confidence, but the specific skills that worked there may not be what's needed here. *(Circle of Competence — executed: "We know this market deeply from 8 years of operating in it")*
> - **Where this breaks:** Circle boundaries blur when past success creates illusion of transferability
> - **Before proceeding, ask:** What specifically falls OUTSIDE your 8 years of experience?
> - **Productive tension:** Man-with-a-Hammer — the risk of applying familiar tools to unfamiliar problems

---

#### FramePressureCard — Question-Level Audit

**Lead with the most consequential element** — the one whose assumption, if wrong, would most change the conclusion. Not all frame elements carry equal weight; present the highest-impact element first and give it more space.

For each element in `frame_pressure_card.frame_elements`:

**[element_type: assumption / mutable_constraint / suppressed_counterfactual]** — [frame_pattern]
- [element_text]
- Evidence: "[evidence_quote]"
- Fragility: [fragility_signal]

**Reframings — novelty check.** Before presenting a reframing, check whether the conversation already explored that question. You have the full conversation context. If a reframing echoes something the user or you already discussed, skip it or flag it as "already explored — the conversation touched this but didn't resolve it." Only present reframings that genuinely expand the frame beyond what was discussed.

For each reframing that passes the novelty check (max 2):

> **Alternative question:** [reframed_question]
> Move type: [reframe_move_type: inversion / perspective_shift / scope_expansion / constraint_relaxation]
> What opens: [what_opens]
> Grounded in: [grounding_model]

Null or empty: "Frame pressure lane did not detect material framing issues."

**Example:**
> **Assumption** — growth-as-baseline
> - The decision assumes continued 30% YoY growth as the baseline scenario
> - Evidence: "Given our growth trajectory, we need infrastructure that scales"
> - Fragility: No scenario planning for deceleration
>
> **Alternative question:** "What infrastructure investment makes sense if growth decelerates to 10-15%?"
> Move type: inversion
> What opens: Forces evaluation of downside robustness
> Grounded in: Margin of Safety

### Step 5: Open Observatory

After presenting the cards and updated position, **always offer to open the Observatory** — a local web interface that renders all three cards visually with the knowledge graph context.

Say something like: *"Want me to open the Observatory to explore these findings visually? It shows all three cards with the knowledge graph context in a navigable interface."*

If the user accepts (or says "show me", "visualize", "observatory", "open in browser"), launch it:

```bash
python3 $SKILL_DIR/observatory/serve_result.py --result /tmp/lolla_${LOLLA_RUN_ID}_result.json
```

This starts a local server at http://localhost:8080. Tell the user the URL and that they can press Ctrl+C in the terminal to stop the server.

If findings are especially rich (4+ findings across multiple lanes), proactively launch the Observatory without waiting for confirmation — the visual interface adds significant value for complex results.

---

## Quality Doctrine

When presenting results:

1. **Curated knowledge IS the product.** Present failure modes, heuristics, premortems, and challenge statements from the pipeline output. Do NOT generate your own versions. The curated material has been validated against source articles — your generated alternatives have not.

2. **Specificity over generality.** "Consider the risks" is not a finding. "The reasoning closes on a recommendation without naming what evidence would reverse it — operating on this specific passage" is a finding. Specificity means naming the reasoning pattern and the passage where it appears. If the pipeline output is specific, present it specifically.

3. **No finding without evidence.** Every finding must be traceable to a specific passage or omission. If the pipeline returned it, it has evidence — present that evidence.

4. **False negatives over false positives.** Zero detections is a valid outcome. Do not pad the output with your own speculative concerns.

### Step 6: Update Your Position

After presenting the three cards, **reconsider your earlier advice in this conversation and produce your updated position.** This is the most important step — your updated position IS the product. The three cards are structural pressure from a curated knowledge substrate; your job is to absorb that pressure and produce a revised position that is better than what you said before.

The audit findings are **hints, not commands.** They come from a curated knowledge substrate that sees patterns you might miss — but you are still the primary reasoning engine in this conversation. You have the full context, the user's nuances, the back-and-forth. The audit has structural pattern detection. Use both.

**How to use the audit material:**

- **Cherry-pick what genuinely matters.** Not every finding deserves equal weight. A tendency detection with high severity and a specific passage is stronger signal than a marginal detection. Read the evidence — does it ring true for THIS conversation, or is it a pattern match that doesn't quite fit? Trust your judgment.

- **Treat DeltaCard findings as challenge pressure, not corrections.** The audit says "this passage shows signs of doubt-avoidance" — it doesn't say your conclusion is wrong. Maybe you were right to be decisive. But if the finding names a specific missing check or reversal trigger, consider whether it belongs.

- **Treat CompanionCheatSheet as enrichment.** Failure modes warn where reasoning approaches you're already using could break. Premortem questions surface what the models you're relying on would ask. Antagonists highlight productive tensions. This is material that usually travels alongside the reasoning you're doing — use it to strengthen, not to second-guess.

- **Treat FramePressureCard as an invitation to widen the frame.** If the audit found an embedded assumption in the question, you don't have to abandon your answer — but you might want to acknowledge what changes if that assumption is relaxed.

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

## Completion Status

After the full cycle (present cards → update position), report:

```
STATUS: DONE
Audited: [brief description of the decision situation]
Lane 1: [N] tendency detections ([list tendency names])
Lane 2: [N] companion models detected
Lane 3: [N] frame elements, [N] reframings
Position updated: [one-sentence summary of what shifted]
```

If any lane failed or returned errors, use `DONE_WITH_CONCERNS` and note which lane had issues.

## References

Do NOT read these proactively. Load only when a specific situation calls for it:

| File | When to read |
|------|-------------|
| `references/output-field-guide.md` | **Read at the start of Step 4** — full field definitions, chunk types, compound patterns, element types, reframe moves |
| `references/presentation-voice.md` | **Read at the start of Step 4** — how to voice findings: lead with the story not the label, concrete antidotes, Munger-inspired directness |
| `references/tendency-catalog.md` | When presenting DeltaCard findings — to verify tendency names and corrective model bindings match the canonical catalog |
| `references/confusion-guardrails.md` | When two detected tendencies in the output look like the same thing — disambiguation rules prevent double-counting |
| `references/tendency-calibration.md` | When a detection feels marginal or the user questions a finding — contains detection boundaries and threshold guidance per tendency |
| `HOW_IT_WORKS.md` (repo root) | When the user asks "how does this work", "what just happened", or about the architecture — full technical reference including research foundations, step-by-step pipeline flow, and knowledge substrate |
