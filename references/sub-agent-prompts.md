# Sub-Agent Prompt Templates (Step 7)

## What this file is

The verbatim prompt templates you interpolate when spawning Step 7 pressure-check sub-agents via the Agent tool. SKILL.md tells you to load this file at Step 7. Each sub-agent receives a **shared preamble** (with extraction fields interpolated) plus a **lane-specific suffix** (with that lane's card JSON interpolated). The prompt must be fully self-contained — the sub-agent has no tool access.

## How to use this file

For each non-empty lane (Step 7 skip rules apply):

1. Extract fields from `/tmp/lolla_${LOLLA_RUN_ID}_extraction.json`:
   - `extraction.decision_situation`
   - `extraction.live_constraints`
   - `extraction.synthesized_position`
   - `extraction.reasoning_passages`
   - `extraction.original_framing`
   - `extraction.dropped_threads`
2. Build the shared preamble below, substituting those values for the placeholders.
3. Append the lane-specific suffix for that lane, with the card JSON interpolated.
4. Spawn an Agent tool call with the full prompt, `run_in_background: true`.

Spawn all non-empty lanes in a single message (parallel).

For Lane 4: strip the card JSON to only gap dimensions (`covered: false`) and their matching `gap_questions`. Drop all covered dimensions — the sub-agent doesn't need them.

---

## Shared preamble

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

---

## Lane 1 suffix — DeltaCard (Structural Pressure)

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

---

## Lane 2 suffix — CompanionCheatSheet (Mental Models Active)

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

---

## Lane 3 suffix — FramePressureCard (Question-Level Audit)

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

---

## Lane 4 suffix — StructuralCoverageCard (Gap Discovery)

**Before interpolating:** strip the card JSON to only gap dimensions (`covered: false`) and their matching `gap_questions`. Drop all covered dimensions — the sub-agent doesn't need them. This keeps the payload small and focused.

```
## Audit Findings — Structural Coverage Gaps

The following structural dimensions were identified as gaps — territory the answer didn't enter. Each includes discovery questions for the decision-maker.

{STRUCTURAL_COVERAGE_GAPS_ONLY_JSON}

## Your Assessment

For each gap: is this a genuine blind spot, or is it addressed implicitly in the position? Would filling it change the recommendation? Be direct and brief.
```
