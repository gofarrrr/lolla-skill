#!/usr/bin/env python3
"""Extract decision structure from a conversation for the Lolla pipeline.

Takes a raw conversation transcript, calls OpenRouter to extract structured
fields (decision situation, constraints, synthesized position, reasoning
passages, framing, dropped threads), and maps them to a CritiqueRequest.

Usage:
    python3 scripts/run_extract.py --conversation-file /tmp/conv.txt
    python3 scripts/run_extract.py --conversation-file /tmp/conv.txt --env-file /path/to/.env

Output: JSON to stdout with extraction fields and mapped CritiqueRequest.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Path resolution — find pipeline package
# ---------------------------------------------------------------------------

SKILL_ROOT = Path(__file__).resolve().parent.parent
ENGINE_DIR = SKILL_ROOT / "engine"

if (ENGINE_DIR / "system_b" / "__init__.py").exists():
    sys.path.insert(0, str(ENGINE_DIR))
elif os.environ.get("LOLLA_REPO_ROOT"):
    sys.path.insert(0, os.environ["LOLLA_REPO_ROOT"])
else:
    print(
        "ERROR: Cannot find the Lolla engine. "
        "Expected at: " + str(ENGINE_DIR / "system_b"),
        file=sys.stderr,
    )
    sys.exit(1)

from system_b.boundary_provider import load_boundary_client_from_env  # noqa: E402


# ---------------------------------------------------------------------------
# .env loader (same pattern as scripts/run_live_pipeline.py)
# ---------------------------------------------------------------------------

def _load_env_file(path: Path) -> list[str]:
    if not path.exists():
        return []
    loaded: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        if key not in os.environ:
            os.environ[key] = value
            loaded.append(key)
    return loaded


# ---------------------------------------------------------------------------
# Conversation truncation for very long conversations
# ---------------------------------------------------------------------------

MAX_CONVERSATION_CHARS = 80_000
KEEP_FIRST_TURNS = 3
KEEP_LAST_TURNS = 15


def _truncate_conversation(text: str) -> str:
    """Truncate long conversations, keeping early + late turns."""
    if len(text) <= MAX_CONVERSATION_CHARS:
        return text

    # Split by turn markers
    import re
    turns = re.split(r"(?=\[Turn \d+\])", text)
    turns = [t for t in turns if t.strip()]

    if len(turns) <= KEEP_FIRST_TURNS + KEEP_LAST_TURNS:
        return text

    first = turns[:KEEP_FIRST_TURNS]
    last = turns[-KEEP_LAST_TURNS:]
    omitted = len(turns) - KEEP_FIRST_TURNS - KEEP_LAST_TURNS

    return (
        "".join(first)
        + f"\n[... {omitted} turns omitted for brevity ...]\n\n"
        + "".join(last)
    )


# ---------------------------------------------------------------------------
# Extraction prompt
# ---------------------------------------------------------------------------

EXTRACTION_SYSTEM_PROMPT = """\
You are a conversation analyst. You extract structured decision-making elements \
from multi-turn LLM conversations.

You will receive a raw conversation transcript between a human and an AI assistant. \
Your job is to determine:
1. Whether this conversation involves a strategic decision, recommendation, or advisory situation
2. If yes, extract the key structural elements needed for a reasoning audit

A conversation is "strategic" when the AI provides advice, recommendations, or \
analysis that could influence a material decision — business strategy, architecture \
choices, hiring, investment, product direction, vendor selection, organizational \
design, technology tradeoffs, negotiation positioning, risk assessment, or similar. \
It is NOT strategic when it is purely technical execution (code debugging, syntax \
questions, build errors), factual lookup, creative writing, or casual conversation.

If the conversation is NOT strategic, respond with:
```json
{
  "is_strategic": false,
  "decline_reason": "One sentence explaining why this is not a strategic decision conversation"
}
```

If the conversation IS strategic, extract these fields:

1. "decision_situation": The core decision or question being worked through. State it \
as a neutral problem statement, not as the AI framed it. Include the domain, key \
stakeholders, and what is at stake. Be specific — "whether to adopt microservices" \
is better than "architecture decision".

2. "live_constraints": Array of objects, each with:
   - "constraint": what the user stated (deadline, budget, team size, dependency, \
     regulatory requirement, prior commitment, political factor)
   - "introduced_turn": approximate turn number where this was first mentioned
   - "status": "active" if the AI's final recommendation still addresses it, \
     "dropped" if the AI stopped referencing it, "modified" if the scope changed
   - "weight": "structural" if this constraint defines the decision context itself \
     (industry, regulatory regime, company stage, team composition — dropping it \
     changes WHAT decision is being made), or "situational" if it bounds the current \
     execution (timeline, budget, current capacity — dropping it changes HOW the \
     decision is implemented but not what the decision IS about)

3. "synthesized_position": The AI's final or most developed recommendation/analysis. \
If the conversation evolved across turns, capture the LATEST consolidated position. \
Preserve the reasoning structure — how the AI argued, not just what it concluded. \
This should be a faithful representation, not a summary.

4. "reasoning_passages": Array of 3-8 strings, each an EXACT VERBATIM substring \
copied from the AI assistant's messages. Focus on passages that show:
   - Leaps from observation to recommendation — e.g. "Given the team size, I'd \
     recommend a monolith" (jumps from one fact to an architecture choice without \
     showing the reasoning chain)
   - Tradeoff dismissals — e.g. "While there's some risk of vendor lock-in, this \
     is unlikely to matter at your scale" (acknowledges a risk then minimizes it \
     without evidence)
   - Confidence assertions about uncertain outcomes — e.g. "This approach will \
     reduce costs by approximately 40%" (precise number with no stated basis)
   - Framing moves — e.g. "The real question here is whether..." (choosing one \
     lens and implicitly excluding others)
   If the same reasoning move appears in multiple turns, select the most developed \
   version rather than including both.
   CRITICAL: Every string must be a literal substring that appears in the transcript. \
   Do NOT paraphrase, summarize, or fabricate. If you cannot find enough distinct \
   passages, return fewer rather than inventing quotes.

5. "original_framing": How the human originally posed the problem. What perspective \
was adopted? What was treated as fixed vs. open? What alternatives were implicitly \
excluded by the way the question was asked?

6. "dropped_threads": Array of objects, each with:
   - "thread": the concern, constraint, or question that was raised
   - "raised_by": "user" or "assistant"
   - "raised_turn": approximate turn number
   - "status": "never_addressed" if the AI never engaged with it, \
     "acknowledged_then_dropped" if the AI addressed it once but the final \
     recommendation ignores it, "resolved" if it was fully addressed (include \
     only unresolved ones)
   - "superseded_by": (only for "acknowledged_then_dropped") brief description \
     of what the AI focused on instead — e.g. "shifted to discussing team velocity \
     rather than data migration risk". This tells the audit what replaced the \
     dropped concern, which is stronger omission evidence than the drop alone.

Respond ONLY with valid JSON. No commentary outside the JSON object."""

EXTRACTION_USER_PROMPT = """\
CONVERSATION TRANSCRIPT:
{conversation_text}

Extract the decision-making structure from this conversation. Respond with JSON only."""


# ---------------------------------------------------------------------------
# Assistant response extraction from conversation text
# ---------------------------------------------------------------------------

MAX_VANILLA_ANSWER_CHARS = 40_000


def _extract_assistant_responses(conversation_text: str) -> str:
    """Extract all assistant responses from the formatted conversation transcript."""
    import re
    parts = re.split(r"\[Turn \d+\] (USER|ASSISTANT):", conversation_text)
    # parts alternates: preamble, role, content, role, content...
    assistant_texts = []
    for i in range(1, len(parts) - 1, 2):
        role = parts[i].strip()
        content = parts[i + 1].strip()
        if role == "ASSISTANT" and content:
            assistant_texts.append(content)
    return "\n\n---\n\n".join(assistant_texts)


# ---------------------------------------------------------------------------
# CritiqueRequest mapping
# ---------------------------------------------------------------------------

def _map_to_critique_request(
    extraction: dict,
    assistant_text: str = "",
) -> dict:
    """Map extracted fields to query + vanilla_answer for the pipeline.

    The query carries the decision structure (for Lane 1 triage and Lane 3
    frame pressure).  The vanilla_answer carries the full assistant reasoning
    (for Lane 2 companion fingerprinting/verification and Lane 1 deep checks).
    """
    decision = extraction.get("decision_situation", "")

    # Build enriched query
    query_parts = [decision]

    constraints = extraction.get("live_constraints", [])
    if constraints:
        constraint_lines = []
        for c in constraints:
            status = c.get("status", "active")
            weight = c.get("weight", "situational")
            tag = f"{status.upper()}/{weight.upper()}" if status != "active" else status.upper()
            constraint_lines.append(f"- [{tag}] {c.get('constraint', '')}")
        query_parts.append("\nConstraints stated during conversation:\n" + "\n".join(constraint_lines))

    framing = extraction.get("original_framing", "")
    if framing:
        query_parts.append(f"\nOriginal framing: {framing}")

    dropped = extraction.get("dropped_threads", [])
    if dropped:
        thread_lines = []
        for d in dropped:
            line = (
                f"- {d.get('thread', '')} (raised by {d.get('raised_by', '?')}, "
                f"status: {d.get('status', '?')})"
            )
            superseded = d.get("superseded_by", "")
            if superseded:
                line += f" → superseded by: {superseded}"
            thread_lines.append(line)
        query_parts.append(
            "\nDropped threads (raised but unresolved):\n" + "\n".join(thread_lines)
        )

    query = "\n".join(query_parts)

    # Build vanilla answer — prefer full assistant text, fall back to synthesis
    if assistant_text and len(assistant_text) > 200:
        # Use synthesized position as a preamble for focus, then full text
        synthesis = extraction.get("synthesized_position", "")
        vanilla_answer = (
            f"SYNTHESIZED POSITION:\n{synthesis}\n\n"
            f"FULL ASSISTANT REASONING:\n{assistant_text}"
        )
        # Cap at limit
        if len(vanilla_answer) > MAX_VANILLA_ANSWER_CHARS:
            vanilla_answer = vanilla_answer[:MAX_VANILLA_ANSWER_CHARS]
    else:
        # Fallback: compressed mode (no conversation text available)
        vanilla_parts = [extraction.get("synthesized_position", "")]
        passages = extraction.get("reasoning_passages", [])
        if passages:
            vanilla_parts.append("\n\nKey reasoning passages from the conversation:")
            for i, p in enumerate(passages, 1):
                vanilla_parts.append(f"\n[{i}] \"{p}\"")
        vanilla_answer = "\n".join(vanilla_parts)

    return {"query": query, "vanilla_answer": vanilla_answer}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract decision structure from a conversation"
    )
    parser.add_argument(
        "--conversation-file",
        required=True,
        help="Path to conversation transcript file",
    )
    parser.add_argument(
        "--env-file",
        help="Optional .env file path. Defaults to <repo_root>/.env",
    )
    parser.add_argument(
        "--output-file",
        help="Write output JSON to this file instead of stdout",
    )
    args = parser.parse_args()

    # Load env: explicit flag → project .claude/lolla.env → repo .env → ~/.config/lolla/.env
    if args.env_file:
        _load_env_file(Path(args.env_file))
    else:
        for candidate in [
            SKILL_ROOT / ".env",
            Path.home() / ".config" / "lolla" / ".env",
        ]:
            if candidate.exists():
                _load_env_file(candidate)
                break

    # Read conversation
    conv_path = Path(args.conversation_file)
    if not conv_path.exists():
        print(json.dumps({"status": "error", "error": f"File not found: {conv_path}"}))
        return 1

    conversation_text = conv_path.read_text(encoding="utf-8")
    if not conversation_text.strip():
        print(json.dumps({"status": "error", "error": "Empty conversation file"}))
        return 1

    # Truncate if needed
    conversation_text = _truncate_conversation(conversation_text)

    # Call OpenRouter for extraction
    try:
        client = load_boundary_client_from_env("openrouter")
    except Exception as exc:
        print(json.dumps({"status": "error", "error": f"Failed to initialize OpenRouter client: {exc}"}))
        return 1

    user_prompt = EXTRACTION_USER_PROMPT.format(conversation_text=conversation_text)

    try:
        payload = client.run_json(EXTRACTION_SYSTEM_PROMPT, user_prompt)
    except Exception as exc:
        print(json.dumps({"status": "error", "error": f"OpenRouter call failed: {exc}"}))
        return 1

    # Check if strategic
    if not payload.get("is_strategic", True):
        print(json.dumps({
            "status": "not_strategic",
            "decline_reason": payload.get("decline_reason", "Not a strategic conversation"),
        }))
        return 0

    # Validate required fields
    required = ["decision_situation", "synthesized_position"]
    missing = [f for f in required if not payload.get(f)]
    if missing:
        print(json.dumps({
            "status": "error",
            "error": f"Extraction missing required fields: {missing}",
            "raw_extraction": payload,
        }))
        return 1

    # Extract full assistant responses from conversation for richer pipeline input
    assistant_text = _extract_assistant_responses(conversation_text)

    # Map to CritiqueRequest
    critique_request = _map_to_critique_request(payload, assistant_text=assistant_text)

    output = {
        "status": "ok",
        "extraction": payload,
        "critique_request": critique_request,
    }

    output_text = json.dumps(output, indent=2, ensure_ascii=False)
    if args.output_file:
        Path(args.output_file).write_text(output_text, encoding="utf-8")
        print(f"Extraction written to {args.output_file}")
    else:
        print(output_text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
