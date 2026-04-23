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
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# canonical_key slug validation (PR #1 of the extraction contract roadmap)
# ---------------------------------------------------------------------------
#
# Letter-first + lowercase-only is deliberate: covers the common case cleanly.
# Slugs like "401k-vesting-risk" that start with a digit would fail and need a
# prompt iteration if a real case surfaces. The 2-4 token ceiling (i.e. 1-3
# hyphens) is where slugs stop reading like sentences and start reading like
# identifiers; beyond that we're just re-inventing the constraint text.
_CANONICAL_KEY_RE = re.compile(r"^[a-z][a-z0-9]+(-[a-z0-9]+){1,3}$")


def _validate_canonical_key(key: str) -> bool:
    """Return True if ``key`` matches the canonical_key slug rule:
    - 2-4 tokens separated by hyphens
    - lowercase ASCII letters and digits only
    - first token starts with a letter, has ≥2 characters
    - each subsequent token has ≥1 character, letters-or-digits only

    Empty strings, None, and non-str inputs return False.
    """
    if not isinstance(key, str) or not key:
        return False
    return bool(_CANONICAL_KEY_RE.match(key))


def _apply_canonical_key_validation(
    payload: dict,
    capture_warnings: list,
) -> list:
    """Walk ``payload['live_constraints']`` and enforce the canonical_key slug
    rule. Invalid keys are set to ``""``; the field is left absent when the
    LLM didn't emit it at all. If any invalid keys were found, a single
    capture_warning summarizing them is appended to ``capture_warnings``.
    Returns the list of offending key values for observability.

    Design note: we do NOT slugify the constraint text as a fallback. Fallback
    hides LLM quality and contaminates the canonical_key Jaccard signal with
    python-generated slugs. Empty-string "honest failure" is the right signal;
    the invalid_key_rate metric downstream captures the failure rate.
    """
    offenders: list = []
    for c in payload.get("live_constraints", []) or []:
        if "canonical_key" not in c:
            continue
        key = c.get("canonical_key")
        if not _validate_canonical_key(key):
            offenders.append(key)
            c["canonical_key"] = ""
    if offenders:
        preview = [k if len(str(k)) <= 40 else str(k)[:37] + "..." for k in offenders[:3]]
        capture_warnings.append(
            f"canonical_key validation: {len(offenders)} constraint(s) had "
            f"invalid slugs (set to empty); examples: {preview}"
        )
    return offenders


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


def _truncate_conversation(text: str) -> tuple[str, dict]:
    """Truncate long conversations, keeping early + late turns.

    Returns ``(text, truncation_info)`` where ``truncation_info`` is a dict
    with at minimum ``truncation_applied: bool``. When truncation fires, the
    dict also includes diagnostic fields so downstream code (run_pipeline.py,
    run_health, Step 4 chat) can surface the fact that context was dropped.
    """
    if len(text) <= MAX_CONVERSATION_CHARS:
        return text, {"truncation_applied": False}

    # Split by turn markers
    import re
    turns = re.split(r"(?=\[Turn \d+\])", text)
    turns = [t for t in turns if t.strip()]

    if len(turns) <= KEEP_FIRST_TURNS + KEEP_LAST_TURNS:
        return text, {"truncation_applied": False}

    first = turns[:KEEP_FIRST_TURNS]
    last = turns[-KEEP_LAST_TURNS:]
    omitted = len(turns) - KEEP_FIRST_TURNS - KEEP_LAST_TURNS

    truncated = (
        "".join(first)
        + f"\n[... {omitted} turns omitted for brevity ...]\n\n"
        + "".join(last)
    )
    return truncated, {
        "truncation_applied": True,
        "truncation_reason": (
            f"char_limit_exceeded (original {len(text)} chars > cap "
            f"{MAX_CONVERSATION_CHARS}); kept first {KEEP_FIRST_TURNS} + "
            f"last {KEEP_LAST_TURNS} turns, omitted {omitted} middle turns"
        ),
        "original_char_length": len(text),
        "truncated_char_length": len(truncated),
        "total_turns": len(turns),
        "kept_turns": KEEP_FIRST_TURNS + KEEP_LAST_TURNS,
        "omitted_turns": omitted,
    }


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

1. "decision_situation": the core decision as a single declarative sentence, \
≤200 characters, neutral third-person. Name the subject, the action being \
decided, and the material context. Avoid prose, emotive language, and \
speculative outcomes. Good: "Whether Marcus should receive 15% equity given \
retention risk and $9-13M exit valuation."

2. "live_constraints": Array of objects, each with:
   - "constraint": terse noun-phrase-plus-state, ≤120 characters. State the \
     what (deadline, budget, team size, dependency, regulatory requirement, \
     prior commitment, political factor) plus the current state of it. \
     Avoid prose, hedging, and multi-clause sentences. Good: "Marcus comp \
     $225k (below market $220-250k range)". Bad: "Marcus's current \
     compensation is $225K total, which is slightly below the market range \
     of $220-250K for comparable roles."
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


EXTRACTION_USER_PROMPT_RETRY = """\
CONVERSATION TRANSCRIPT:
{conversation_text}

A prior extraction attempt on this transcript returned reasoning_passages that are NOT literal substrings of the transcript above. The following passages failed validation because they were paraphrased rather than copied verbatim:

{failed_passages_block}

On this retry:
- Every entry in reasoning_passages MUST be a character-for-character verbatim copy of text that appears in the transcript above.
- Do NOT reuse any of the failed passages listed above.
- Do NOT paraphrase, smooth grammar, correct punctuation, or alter quotes.
- Return 3-8 reasoning_passages that can be found character-exactly in the transcript.

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


def _validate_conversation_capture(conversation_text: str) -> dict:
    """Check header-declared counts against actual turn markers.

    Returns a structured dict with capture_manifest (counts) and
    capture_health (grade + warnings).  The grade is:
      - "good"     — header matches body, assistant turns present
      - "degraded" — minor mismatches (<50% drop)
      - "critical" — >50% assistant turns missing or zero assistant turns
      - "unknown"  — no parseable header (can't validate)
    """
    import re

    actual_user = len(re.findall(r"\[Turn \d+\] USER:", conversation_text))
    actual_assistant = len(re.findall(r"\[Turn \d+\] ASSISTANT:", conversation_text))

    manifest: dict = {
        "actual_user_turns": actual_user,
        "actual_assistant_turns": actual_assistant,
        "char_length": len(conversation_text),
    }
    warnings: list[str] = []

    # Parse header: "CONVERSATION: {N} turns, {X} user messages, {Y} assistant responses"
    header_match = re.match(
        r"CONVERSATION:\s*(\d+)\s*turns?,\s*(\d+)\s*user\s*messages?,\s*(\d+)\s*assistant\s*responses?",
        conversation_text.strip(),
    )
    if not header_match:
        manifest["declared_turns"] = None
        manifest["declared_user"] = None
        manifest["declared_assistant"] = None
        return {
            "capture_manifest": manifest,
            "capture_health": "unknown",
            "capture_warnings": warnings,
        }

    declared_turns = int(header_match.group(1))
    declared_user = int(header_match.group(2))
    declared_assistant = int(header_match.group(3))

    manifest["declared_turns"] = declared_turns
    manifest["declared_user"] = declared_user
    manifest["declared_assistant"] = declared_assistant

    # Check mismatches
    if actual_user != declared_user:
        warnings.append(
            f"Capture mismatch: header declares {declared_user} user messages "
            f"but body contains {actual_user}"
        )
    if actual_assistant != declared_assistant:
        severity = "CRITICAL" if actual_assistant < declared_assistant * 0.5 else "minor"
        warnings.append(
            f"Capture mismatch ({severity}): header declares {declared_assistant} "
            f"assistant responses but body contains {actual_assistant}"
        )

    if actual_assistant == 0 and declared_assistant > 0:
        warnings.append(
            "CRITICAL: No assistant responses in transcript — pipeline will "
            "audit only the LLM-synthesized position, not actual reasoning"
        )

    # Grade
    if actual_assistant == 0 and declared_assistant > 0:
        grade = "critical"
    elif actual_assistant < declared_assistant * 0.5:
        grade = "critical"
    elif warnings:
        grade = "degraded"
    else:
        grade = "good"

    return {
        "capture_manifest": manifest,
        "capture_health": grade,
        "capture_warnings": warnings,
    }


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

    # Validate capture integrity on raw text (before truncation, before API call)
    capture_result = _validate_conversation_capture(conversation_text)
    capture_manifest = capture_result["capture_manifest"]
    capture_health = capture_result["capture_health"]
    capture_warnings = capture_result["capture_warnings"]

    # If capture is fundamentally broken (>50% assistant turns missing, or zero
    # assistant turns), decline the audit. An extraction on a critically
    # degraded capture produces a ghost audit — downstream lanes would treat a
    # half-captured conversation as authoritative. Better to surface the break
    # and ask the user to recapture than to ship a silent lie. We check BEFORE
    # initializing the OpenRouter client so broken captures don't cost money.
    if capture_health == "critical":
        decline = {
            "status": "capture_critical",
            "decline_reason": (
                "Conversation capture is critically degraded — more than half "
                "of the assistant turns declared in the transcript header are "
                "missing from the body, or the transcript has no assistant "
                "responses at all. An audit on this capture would be unreliable. "
                "Re-capture the conversation and retry. See capture_manifest "
                "below for the exact mismatch."
            ),
        }
        decline.update(capture_result)
        output_text = json.dumps(decline, indent=2, ensure_ascii=False)
        if args.output_file:
            Path(args.output_file).write_text(output_text, encoding="utf-8")
            print(f"Capture critical — extraction declined. Diagnostic written to {args.output_file}")
        else:
            print(output_text)
        return 0

    # Truncate if needed. If truncation fires, merge diagnostic info into
    # capture_manifest so run_pipeline.py / run_health / Step 4 chat can
    # surface that context was dropped.
    conversation_text, truncation_info = _truncate_conversation(conversation_text)
    if truncation_info.get("truncation_applied"):
        capture_result["capture_manifest"].update(truncation_info)
        capture_result["capture_warnings"].append(
            f"Conversation truncated: {truncation_info['omitted_turns']} middle "
            f"turns omitted ({truncation_info['original_char_length']} → "
            f"{truncation_info['truncated_char_length']} chars). Audit will run "
            f"on first {KEEP_FIRST_TURNS} + last {KEEP_LAST_TURNS} turns only."
        )

    # Call OpenRouter for extraction
    try:
        client = load_boundary_client_from_env("openrouter")
    except Exception as exc:
        err = {"status": "error", "error": f"Failed to initialize OpenRouter client: {exc}"}
        err.update(capture_result)
        print(json.dumps(err))
        return 1

    user_prompt = EXTRACTION_USER_PROMPT.format(conversation_text=conversation_text)

    try:
        payload = client.run_json(EXTRACTION_SYSTEM_PROMPT, user_prompt)
    except Exception as exc:
        err = {"status": "error", "error": f"OpenRouter call failed: {exc}"}
        err.update(capture_result)
        print(json.dumps(err))
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

    # Validate reasoning passages are literal substrings of the transcript.
    # If any fabricated (paraphrased, not verbatim), retry extraction ONCE with
    # an explicit correction prompt. If the retry produces fewer fabrications,
    # adopt it. Any remaining fabricated passages are dropped from the payload
    # and a capture_warning is emitted so run_pipeline.py can surface
    # `quote_fabrication` via run_health.
    def _validate_passages(pload: dict) -> tuple[list[str], list[str]]:
        items = pload.get("reasoning_passages", []) or []
        ver: list[str] = []
        fab: list[str] = []
        for p in items:
            if p and p in conversation_text:
                ver.append(p)
            else:
                fab.append(p)
        return ver, fab

    initial_passage_count = len(payload.get("reasoning_passages", []) or [])
    verified, fabricated = _validate_passages(payload)
    retry_attempted = False
    retry_succeeded = False

    if fabricated:
        retry_attempted = True
        failed_list = "\n".join(
            f"{i+1}. {json.dumps(p)}" for i, p in enumerate(fabricated)
        )
        retry_user = EXTRACTION_USER_PROMPT_RETRY.format(
            conversation_text=conversation_text,
            failed_passages_block=failed_list,
        )
        try:
            retry_payload = client.run_json(EXTRACTION_SYSTEM_PROMPT, retry_user)
        except Exception as exc:
            capture_warnings.append(f"Quote-fabrication retry failed: {exc}")
            retry_payload = None

        if (retry_payload
                and retry_payload.get("is_strategic", True)
                and retry_payload.get("decision_situation")
                and retry_payload.get("synthesized_position")):
            rv, rf = _validate_passages(retry_payload)
            if len(rf) < len(fabricated):
                # Retry improved — adopt its payload wholesale.
                payload = retry_payload
                verified, fabricated = rv, rf
                retry_succeeded = len(rf) == 0

    # Drop any fabricated passages that remain; the list contract is
    # "literal substrings only."
    if fabricated:
        payload["reasoning_passages"] = verified
        capture_warnings.append(
            f"Quote validation: {len(fabricated)} reasoning_passages dropped"
            f"{' after retry' if retry_attempted else ''} "
            f"(not literal substrings of the transcript)"
        )

    if initial_passage_count or retry_attempted:
        payload["_quote_validation"] = {
            "total": len(verified) + len(fabricated),
            "verified": len(verified),
            "fabricated": len(fabricated),
            "fabricated_passages": fabricated,
            "retry_attempted": retry_attempted,
            "retry_succeeded": retry_succeeded,
        }

    # canonical_key validation — walk live_constraints, blank any slugs that
    # fail the format rule, emit a capture_warning listing the offenders.
    # See PR #1 of the extraction contract roadmap.
    _apply_canonical_key_validation(payload, capture_warnings)

    # Extract full assistant responses from conversation for richer pipeline input
    assistant_text = _extract_assistant_responses(conversation_text)

    # Map to CritiqueRequest
    critique_request = _map_to_critique_request(payload, assistant_text=assistant_text)

    output = {
        "status": "ok",
        "extraction": payload,
        "critique_request": critique_request,
        **capture_result,
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
