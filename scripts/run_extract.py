#!/usr/bin/env python3
"""Extract decision structure from a conversation for the Lolla pipeline.

Takes a raw conversation transcript, calls OpenRouter to extract structured
fields (decision situation, constraints, synthesized position, reasoning
passages, framing, dropped threads), and derives an explicit audit seed plus
flat query/answer compatibility fields for older downstream tooling.

Usage:
    python3 scripts/run_extract.py --conversation-file /tmp/conv.txt
    python3 scripts/run_extract.py --conversation-file /tmp/conv.txt --env-file /path/to/.env

Output: JSON to stdout with extraction fields, audit_seed, and legacy
critique_request compatibility fields.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
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

from system_b.audit_mode import AuditModeError, audit_mode_from_env  # noqa: E402
from system_b.boundary_provider import load_boundary_client_from_env  # noqa: E402
from system_b.capture_adequacy import build_capture_adequacy  # noqa: E402
from system_b.run_state import assert_expected_run_state, infer_run_id_from_lolla_path  # noqa: E402
from system_b.text_matching import find_substring_tolerant  # noqa: E402


EXTRACTION_CALL_CUSTODY_SCHEMA_VERSION = "lolla.extraction_call_custody.v0"


# ---------------------------------------------------------------------------
# Quote validation
# ---------------------------------------------------------------------------

def _validate_reasoning_passages(
    payload: dict,
    conversation_text: str,
) -> tuple[list[str], list[str]]:
    """Split extracted reasoning passages into literal transcript spans and failures.

    Verified passages are returned with the transcript's original casing and
    punctuation. The shared matcher permits only narrow quote-safe tolerances
    such as case drift or a symmetric wrapper quote around the whole passage;
    paraphrases remain failures.
    """
    items = payload.get("reasoning_passages", []) or []
    verified: list[str] = []
    fabricated: list[str] = []
    for passage in items:
        if not passage:
            fabricated.append(passage)
            continue
        matched = find_substring_tolerant(passage, conversation_text)
        if matched is None:
            fabricated.append(passage)
        else:
            verified.append(matched)
    return verified, fabricated


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


def _split_conversation_turns(text: str) -> tuple[str, list[str]]:
    """Return the transcript preamble and exact turn-marker blocks.

    The preamble (normally the ``CONVERSATION:`` header) is source metadata,
    not a conversational turn. Keeping it separate prevents bounded-view
    accounting from claiming that one more turn was retained than the model
    actually received.
    """

    markers = list(re.finditer(r"(?m)^\[Turn \d+\] (?:USER|ASSISTANT):\s*$", text))
    if not markers:
        return text, []
    preamble = text[: markers[0].start()]
    turns = [
        text[marker.start() : markers[index + 1].start()]
        if index + 1 < len(markers)
        else text[marker.start() :]
        for index, marker in enumerate(markers)
    ]
    return preamble, turns


def _truncate_conversation(text: str) -> tuple[str, dict]:
    """Truncate long conversations, keeping early + late turns.

    Returns ``(text, truncation_info)`` where ``truncation_info`` is a dict
    with at minimum ``truncation_applied: bool``. When truncation fires, the
    dict also includes diagnostic fields so downstream code (run_pipeline.py,
    run_health, Step 4 chat) can surface the fact that context was dropped.
    """
    if len(text) <= MAX_CONVERSATION_CHARS:
        return text, {"truncation_applied": False}

    preamble, turns = _split_conversation_turns(text)

    if len(turns) <= KEEP_FIRST_TURNS + KEEP_LAST_TURNS:
        return text, {"truncation_applied": False}

    first = turns[:KEEP_FIRST_TURNS]
    last = turns[-KEEP_LAST_TURNS:]
    omitted = len(turns) - KEEP_FIRST_TURNS - KEEP_LAST_TURNS

    truncated = (
        preamble
        + "".join(first)
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
        "keep_first_turns": KEEP_FIRST_TURNS,
        "keep_last_turns": KEEP_LAST_TURNS,
        "omitted_turns": omitted,
    }


def _write_conversation_processing_view(
    *,
    conversation_path: Path,
    authoritative_text: str,
    processing_text: str,
    truncation_info: dict,
) -> dict:
    """Persist the bounded extraction view without replacing source custody."""

    stem = conversation_path.stem
    base = stem[: -len("_conversation")] if stem.endswith("_conversation") else stem
    view_path = conversation_path.with_name(f"{base}_conversation_processing_view.txt")
    metadata_path = conversation_path.with_name(f"{base}_conversation_processing_view.json")
    partial = bool(truncation_info.get("truncation_applied"))
    metadata = {
        "schema_version": "lolla.conversation_processing_view.v1",
        "status": "partial" if partial else "full",
        "authoritative_artifact": "conversation.txt",
        "processing_artifact": "conversation_processing_view.txt",
        "authoritative_conversation_preserved": True,
        "processing_view_is_authoritative": False,
        "processing_strategy": "first_n_plus_last_n" if partial else "full",
        "authoritative_sha256": hashlib.sha256(
            authoritative_text.encode("utf-8")
        ).hexdigest(),
        "processing_sha256": hashlib.sha256(processing_text.encode("utf-8")).hexdigest(),
        "authoritative_char_length": len(authoritative_text),
        "processing_char_length": len(processing_text),
        "omitted_turn_count": int(truncation_info.get("omitted_turns", 0) or 0),
        "omission_metadata": dict(truncation_info) if partial else {"truncation_applied": False},
    }
    view_path.write_text(processing_text, encoding="utf-8")
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return metadata


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
design, technology tradeoffs, negotiation positioning, risk assessment, or personal \
decisions with material stakes (career, financial, family, health, relationship, \
caregiving, ethical), or similar. It is NOT strategic when it is purely technical \
execution (code debugging, syntax questions, build errors), factual lookup, creative \
writing, or casual conversation.

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

5. "original_framing": how the HUMAN posed the question IN THE FIRST USER TURN \
(mechanical anchor — NOT conversation-evolved framing). ≤200 chars, neutral \
third-person. Describe: what was assumed fixed, what alternatives were \
excluded, what lens the human brought. MUST NOT describe framing shifts \
from later turns.

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

    turn_markers = re.findall(r"\[Turn \d+\] (USER|ASSISTANT):", conversation_text)
    actual_user = sum(1 for role in turn_markers if role == "USER")
    actual_assistant = sum(1 for role in turn_markers if role == "ASSISTANT")
    last_turn_role = turn_markers[-1] if turn_markers else None

    manifest: dict = {
        "actual_user_turns": actual_user,
        "actual_assistant_turns": actual_assistant,
        "char_length": len(conversation_text),
        "last_turn_role": last_turn_role,
    }
    warnings: list[str] = []

    if last_turn_role == "USER":
        warnings.append(
            "CRITICAL: Conversation capture ends on a user turn — the final "
            "assistant response is missing, so the audit would evaluate an "
            "incomplete answer"
        )

    # Parse header: "CONVERSATION: {N} turns, {X} user messages, {Y} assistant responses"
    header_match = re.match(
        r"CONVERSATION:\s*(\d+)\s*turns?,\s*(\d+)\s*user\s*messages?,\s*(\d+)\s*assistant\s*responses?",
        conversation_text.strip(),
    )
    if not header_match:
        manifest["declared_turns"] = None
        manifest["declared_user"] = None
        manifest["declared_assistant"] = None
        warnings.append(
            "Capture warning: missing or unparseable CONVERSATION header — "
            "declared turn counts could not be checked"
        )
        return {
            "capture_manifest": manifest,
            "capture_health": "critical" if last_turn_role == "USER" else "unknown",
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
    if last_turn_role == "USER":
        grade = "critical"
    elif actual_assistant == 0 and declared_assistant > 0:
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
# Audit seed + flat query/answer compatibility mapping
# ---------------------------------------------------------------------------

def _build_case_focus(extraction: dict) -> str:
    """Build the compact decision focus used by artifact/post-processing code."""
    decision = extraction.get("decision_situation", "")

    case_focus_parts = [decision]

    constraints = extraction.get("live_constraints", [])
    if constraints:
        constraint_lines = []
        for c in constraints:
            status = c.get("status", "active")
            weight = c.get("weight", "situational")
            tag = f"{status.upper()}/{weight.upper()}" if status != "active" else status.upper()
            constraint_lines.append(f"- [{tag}] {c.get('constraint', '')}")
        case_focus_parts.append(
            "\nConstraints stated during conversation:\n" + "\n".join(constraint_lines)
        )

    framing = extraction.get("original_framing", "")
    if framing:
        case_focus_parts.append(f"\nOriginal framing: {framing}")

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
        case_focus_parts.append(
            "\nDropped threads (raised but unresolved):\n" + "\n".join(thread_lines)
        )

    return "\n".join(case_focus_parts)


def _legacy_answer_text(extraction: dict, assistant_text: str = "") -> str:
    """Build the old vanilla_answer field without changing compatibility."""

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

    return vanilla_answer


def _build_audit_seed(
    extraction: dict,
    assistant_text: str = "",
) -> dict:
    """Build the explicit post-processing seed for conversation-native runs."""
    audit_target = assistant_text.strip() or _legacy_answer_text(extraction)
    if len(audit_target) > MAX_VANILLA_ANSWER_CHARS:
        audit_target = audit_target[:MAX_VANILLA_ANSWER_CHARS]

    return {
        "case_focus": _build_case_focus(extraction),
        "audit_target_assistant_text": audit_target,
    }


def _map_to_critique_request(
    extraction: dict,
    assistant_text: str = "",
) -> dict:
    """Map extracted fields to legacy query + vanilla_answer compatibility.

    The pipeline no longer consumes this shape. It remains in the extraction
    artifact so older tools and stored captures can continue to run during the
    compatibility window.
    """
    query = _build_case_focus(extraction)
    vanilla_answer = _legacy_answer_text(extraction, assistant_text=assistant_text)

    return {"query": query, "vanilla_answer": vanilla_answer}


def _emit_result(
    payload: dict,
    *,
    output_file: str | None = None,
    capture_result: dict | None = None,
) -> None:
    """Emit extraction CLI JSON consistently across success and edge paths."""
    result = dict(payload)
    if capture_result:
        result.update(capture_result)
    output_text = json.dumps(result, indent=2, ensure_ascii=False)
    if output_file:
        Path(output_file).write_text(output_text, encoding="utf-8")
    print(output_text)


def _prepare_output_parent(output_file: str | None) -> str | None:
    """Make output persistence ready before any provider call.

    Returning an error string keeps the failure observable on stdout without
    attempting to write through the same invalid path.
    """

    if not output_file:
        return None
    path = Path(output_file)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return f"Unable to prepare output directory {path.parent}: {exc}"
    if path.exists() and path.is_dir():
        return f"Output file path is a directory: {path}"
    return None


def _call_record_payloads(client: object) -> list[dict]:
    records: list[dict] = []
    for record in getattr(client, "call_log", []) or []:
        if isinstance(record, dict):
            records.append(dict(record))
            continue
        to_dict = getattr(record, "to_dict", None)
        if callable(to_dict):
            value = to_dict()
            if isinstance(value, dict):
                records.append(value)
    return records


def _runtime_tmp_dir() -> Path:
    return Path(os.getenv("LOLLA_TMP_DIR", "/tmp")).expanduser()


def _merge_call_records(
    existing: list[dict],
    current: list[dict],
) -> list[dict]:
    """Append new call records without erasing earlier process attempts."""

    merged: list[dict] = []
    seen: set[str] = set()
    for record in [*existing, *current]:
        reservation_id = str(record.get("budget_reservation_id") or "")
        identity = (
            f"reservation:{reservation_id}"
            if reservation_id
            else "record:"
            + hashlib.sha256(
                json.dumps(
                    record,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                ).encode("utf-8")
            ).hexdigest()
        )
        if identity in seen:
            continue
        seen.add(identity)
        merged.append(record)
    return merged


def _last_call_record(client: object) -> dict:
    records = _call_record_payloads(client)
    return records[-1] if records else {}


def _provider_failure_from_record(record: dict) -> dict:
    raw_message_content = str(record.get("raw_message_content") or "")
    retry_after = record.get("retry_after_seconds")
    try:
        retry_after_value = float(retry_after) if retry_after is not None else None
    except (TypeError, ValueError):
        retry_after_value = None
    return {
        "status": str(record.get("status") or ""),
        "finish_reason": str(record.get("finish_reason") or ""),
        "provider_error_source": str(record.get("provider_error_source") or ""),
        "provider_error_type": str(record.get("provider_error_type") or ""),
        "provider_error_code": str(record.get("provider_error_code") or ""),
        "provider_error_provider_code": str(
            record.get("provider_error_provider_code") or ""
        ),
        "provider_error_message_sha256": str(
            record.get("provider_error_message_sha256") or ""
        ),
        "retry_after_seconds": retry_after_value,
        "response_id": str(record.get("response_id") or ""),
        "raw_message_content_present": bool(raw_message_content),
        "raw_message_content_chars": len(raw_message_content),
    }


def _not_attempted_call_custody(*, run_id: str, terminal_status: str) -> dict:
    return {
        "schema_version": EXTRACTION_CALL_CUSTODY_SCHEMA_VERSION,
        "run_id": run_id,
        "call_attempted": False,
        "sidecar_persisted": False,
        "call_record_persisted": False,
        "recorded_call_count": 0,
        "admissible_extraction": False,
        "terminal_status": terminal_status,
        "usage_evidence_state": "not_applicable_no_call",
        "sidecar_path": "",
        "failure_reason": "",
    }


def _persist_extraction_call_sidecar(
    client: object,
    *,
    run_id: str,
    output_file: str | None,
    terminal_status: str,
    admissible_extraction: bool,
) -> dict:
    """Atomically persist provider-call evidence and describe its custody.

    This function judges no semantic field. It records only whether a call was
    attempted, whether a corresponding record survived, and whether the caller
    has reached an admissible extraction terminal state.
    """

    active_run_id = run_id or infer_run_id_from_lolla_path(output_file)
    current_records = _call_record_payloads(client)
    non_attempt_statuses = {"not_called", "missing_api_key", "budget_blocked_preflight"}
    provider_attempted = any(
        record.get("provider_attempted") is True
        or str(record.get("status") or "") not in non_attempt_statuses
        for record in current_records
    )
    custody = {
        "schema_version": EXTRACTION_CALL_CUSTODY_SCHEMA_VERSION,
        "run_id": active_run_id,
        "call_attempted": provider_attempted,
        "sidecar_persisted": False,
        "call_record_persisted": False,
        "recorded_call_count": len(current_records),
        "admissible_extraction": bool(admissible_extraction),
        "terminal_status": terminal_status,
        "usage_evidence_state": (
            "recorded"
            if provider_attempted and current_records
            else "preflight_non_attempt_recorded"
            if current_records
            else "missing_after_attempt"
        ),
        "sidecar_path": "",
        "failure_reason": "",
    }
    if not active_run_id:
        custody["failure_reason"] = "missing_run_id"
        return custody

    from system_b.usage_summary import is_valid_run_id

    if not is_valid_run_id(active_run_id):
        custody["failure_reason"] = "invalid_run_id"
        return custody

    sidecar_path = _runtime_tmp_dir() / (
        f"lolla_{active_run_id}_extraction_calls.json"
    )
    custody["sidecar_path"] = str(sidecar_path)
    temporary_path: Path | None = None
    try:
        existing_records: list[dict] = []
        if sidecar_path.exists():
            existing_value = json.loads(sidecar_path.read_text(encoding="utf-8"))
            if isinstance(existing_value, list):
                existing_records = [
                    dict(record)
                    for record in existing_value
                    if isinstance(record, dict)
                ]
        records = _merge_call_records(existing_records, current_records)
        provider_attempted = any(
            record.get("provider_attempted") is True
            or str(record.get("status") or "") not in non_attempt_statuses
            for record in records
        )
        custody["call_attempted"] = provider_attempted
        custody["recorded_call_count"] = len(records)
        custody["usage_evidence_state"] = (
            "recorded"
            if provider_attempted and records
            else "preflight_non_attempt_recorded"
            if records
            else "missing_after_attempt"
        )
        sidecar_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=sidecar_path.parent,
            prefix=f".{sidecar_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            json.dump(records, handle, indent=2)
            handle.write("\n")
            handle.flush()
            temporary_path = Path(handle.name)
        temporary_path.replace(sidecar_path)
    except (OSError, json.JSONDecodeError) as exc:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        custody["failure_reason"] = f"sidecar_write_failed:{type(exc).__name__}"
        return custody

    custody["sidecar_persisted"] = True
    custody["call_record_persisted"] = bool(records)
    return custody


def _terminal_call_custody(
    custody: dict,
    *,
    terminal_status: str,
    admissible_extraction: bool,
) -> dict:
    finalized = dict(custody)
    finalized["terminal_status"] = terminal_status
    finalized["admissible_extraction"] = bool(admissible_extraction)
    return finalized


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

    output_path_error = _prepare_output_parent(args.output_file)
    if output_path_error:
        print(json.dumps({"status": "error", "error": output_path_error}))
        return 1

    # Load env: explicit flag -> bundled skill .env -> global config.
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

    try:
        audit_mode_from_env()
    except AuditModeError as exc:
        _emit_result(
            {"status": "error", "error": str(exc)},
            output_file=args.output_file,
        )
        return 1

    run_id_for_guard = (
        os.getenv("LOLLA_RUN_ID", "")
        or infer_run_id_from_lolla_path(args.output_file)
        or infer_run_id_from_lolla_path(args.conversation_file)
    )
    try:
        assert_expected_run_state(
            actual_run_id=run_id_for_guard,
            artifact_paths=[args.conversation_file, args.output_file],
            phase="run_extract",
        )
    except SystemExit as exc:
        print(json.dumps({"status": "error", "error": str(exc)}))
        return 1

    terminal_path = _runtime_tmp_dir() / (
        f"lolla_{run_id_for_guard}_extraction_terminal.json"
    )
    if run_id_for_guard and terminal_path.exists():
        print(
            json.dumps(
                {
                    "status": "error",
                    "error": (
                        "This extraction run is already terminal. Start a new "
                        "$lolla run instead of retrying the same run."
                    ),
                    "same_run_retry_allowed": False,
                }
            )
        )
        return 1

    # Read conversation
    conv_path = Path(args.conversation_file)
    if not conv_path.exists():
        _emit_result(
            {"status": "error", "error": f"File not found: {conv_path}"},
            output_file=args.output_file,
        )
        return 1

    authoritative_conversation_text = conv_path.read_text(encoding="utf-8")
    conversation_text = authoritative_conversation_text
    if not conversation_text.strip():
        _emit_result(
            {"status": "error", "error": "Empty conversation file"},
            output_file=args.output_file,
        )
        return 1

    # Validate capture integrity on raw text (before truncation, before API call)
    capture_result = _validate_conversation_capture(conversation_text)
    capture_manifest = capture_result["capture_manifest"]
    capture_health = capture_result["capture_health"]
    capture_warnings = capture_result["capture_warnings"]
    capture_result["capture_adequacy"] = build_capture_adequacy(
        conversation_text=conversation_text,
        run_id=run_id_for_guard,
        capture_manifest=capture_manifest,
        capture_health=capture_health,
        capture_warnings=capture_warnings,
    )

    # If capture is fundamentally broken (>50% assistant turns missing, or zero
    # assistant turns), decline the audit. An extraction on a critically
    # degraded capture produces a ghost audit — downstream lanes would treat a
    # half-captured conversation as authoritative. Better to surface the break
    # and ask the user to recapture than to ship a silent lie. We check BEFORE
    # initializing the OpenRouter client so broken captures don't cost money.
    if capture_health == "critical":
        _emit_result(
            {
                "status": "capture_critical",
                "provider_call_custody": _not_attempted_call_custody(
                    run_id=run_id_for_guard,
                    terminal_status="capture_rejected_before_provider",
                ),
                "decline_reason": (
                    "Conversation capture is critically degraded — more than half "
                    "of the assistant turns declared in the transcript header are "
                    "missing from the body, or the transcript has no assistant "
                    "responses at all, or the capture ends on a user turn without "
                    "the assistant's final response. An audit on this capture would "
                    "be unreliable. Re-capture the conversation and retry. See "
                    "capture_manifest below for the exact mismatch."
                ),
            },
            output_file=args.output_file,
            capture_result=capture_result,
        )
        return 0

    # Build a bounded extraction view when needed. The source transcript stays
    # untouched and authoritative; processing omissions are recorded on the
    # separate derivative rather than being mislabeled as capture loss.
    conversation_text, truncation_info = _truncate_conversation(conversation_text)
    processing_view = _write_conversation_processing_view(
        conversation_path=conv_path,
        authoritative_text=authoritative_conversation_text,
        processing_text=conversation_text,
        truncation_info=truncation_info,
    )
    capture_result["conversation_processing_view"] = processing_view
    if truncation_info.get("truncation_applied"):
        capture_result["capture_manifest"].update(truncation_info)
        capture_result["capture_warnings"].append(
            f"Extraction processing view is partial: {truncation_info['omitted_turns']} middle "
            f"turns omitted from the bounded extraction call "
            f"({truncation_info['original_char_length']} → "
            f"{truncation_info['truncated_char_length']} chars). The complete "
            "authoritative conversation remains preserved separately."
        )
        capture_result["capture_adequacy"] = build_capture_adequacy(
            conversation_text=authoritative_conversation_text,
            run_id=run_id_for_guard,
            capture_manifest=capture_result["capture_manifest"],
            capture_health=capture_result["capture_health"],
            capture_warnings=capture_result["capture_warnings"],
        )

    # Call OpenRouter for extraction
    try:
        client = load_boundary_client_from_env("openrouter")
    except Exception as exc:
        _emit_result(
            {
                "status": "error",
                "error": f"Failed to initialize OpenRouter client: {exc}",
                "provider_call_custody": _not_attempted_call_custody(
                    run_id=run_id_for_guard,
                    terminal_status="provider_client_initialization_failed",
                ),
            },
            output_file=args.output_file,
            capture_result=capture_result,
        )
        return 1

    user_prompt = EXTRACTION_USER_PROMPT.format(conversation_text=conversation_text)

    try:
        payload = client.run_json(
            EXTRACTION_SYSTEM_PROMPT, user_prompt, stage="extraction"
        )
    except Exception as exc:
        last_call = _last_call_record(client)
        provider_status = str(last_call.get("status") or "")
        call_custody = _persist_extraction_call_sidecar(
            client,
            run_id=run_id_for_guard,
            output_file=args.output_file,
            terminal_status=provider_status or "initial_provider_call_failed",
            admissible_extraction=False,
        )
        _emit_result(
            {
                "status": "error",
                "error": (
                    "Extraction provider call raised an unexpected "
                    f"{type(exc).__name__}."
                ),
                "provider_failure": (
                    _provider_failure_from_record(last_call)
                    if last_call
                    else {
                        "status": "initial_provider_call_failed",
                        "exception_type": type(exc).__name__,
                    }
                ),
                "provider_call_custody": call_custody,
            },
            output_file=args.output_file,
            capture_result=capture_result,
        )
        return 1

    # Persist immediately after the provider boundary returns, before semantic
    # validation can take an early exit. This is what keeps an empty or
    # schema-invalid response from masquerading as a zero-call run.
    call_custody = _persist_extraction_call_sidecar(
        client,
        run_id=run_id_for_guard,
        output_file=args.output_file,
        terminal_status="initial_call_persisted_pending_validation",
        admissible_extraction=False,
    )

    last_call = _last_call_record(client)
    provider_status = str(last_call.get("status") or "")
    if last_call and provider_status and not provider_status.startswith("ok"):
        _emit_result(
            {
                "status": "error",
                "error": (
                    "Extraction provider call did not complete: "
                    f"{provider_status}"
                ),
                "provider_failure": _provider_failure_from_record(last_call),
                "provider_call_custody": _terminal_call_custody(
                    call_custody,
                    terminal_status=provider_status,
                    admissible_extraction=False,
                ),
            },
            output_file=args.output_file,
            capture_result=capture_result,
        )
        return 1

    # Check if strategic
    if not payload.get("is_strategic", True):
        _emit_result(
            {
                "status": "not_strategic",
                "decline_reason": payload.get("decline_reason", "Not a strategic conversation"),
                "provider_call_custody": _terminal_call_custody(
                    call_custody,
                    terminal_status="not_strategic",
                    admissible_extraction=False,
                ),
            },
            output_file=args.output_file,
            capture_result=capture_result,
        )
        return 0

    # Validate required fields
    required = ["decision_situation", "synthesized_position"]
    missing = [f for f in required if not payload.get(f)]
    if missing:
        _emit_result(
            {
                "status": "error",
                "error": f"Extraction missing required fields: {missing}",
                "raw_extraction": payload,
                "provider_call_custody": _terminal_call_custody(
                    call_custody,
                    terminal_status="missing_required_fields",
                    admissible_extraction=False,
                ),
            },
            output_file=args.output_file,
            capture_result=capture_result,
        )
        return 1

    # Validate reasoning passages are literal substrings of the transcript.
    # If any fabricated (paraphrased, not verbatim), retry extraction ONCE with
    # an explicit correction prompt. If the retry produces fewer fabrications,
    # adopt it. Any remaining fabricated passages are dropped from the payload
    # and a capture_warning is emitted so run_pipeline.py can surface
    # `quote_fabrication` via run_health.
    initial_passage_count = len(payload.get("reasoning_passages", []) or [])
    verified, fabricated = _validate_reasoning_passages(payload, conversation_text)
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
            retry_payload = client.run_json(
                EXTRACTION_SYSTEM_PROMPT, retry_user, stage="extraction_retry"
            )
        except Exception as exc:
            capture_warnings.append(f"Quote-fabrication retry failed: {exc}")
            retry_payload = None
        call_custody = _persist_extraction_call_sidecar(
            client,
            run_id=run_id_for_guard,
            output_file=args.output_file,
            terminal_status="quote_repair_call_persisted_pending_validation",
            admissible_extraction=False,
        )

        if (retry_payload
                and retry_payload.get("is_strategic", True)
                and retry_payload.get("decision_situation")
                and retry_payload.get("synthesized_position")):
            rv, rf = _validate_reasoning_passages(retry_payload, conversation_text)
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

    # Persist the exact source span returned by the tolerant matcher even when
    # every passage passed. This canonicalizes harmless case/quote-delimiter
    # drift back to the transcript and makes the stored receipt byte-literal,
    # rather than merely source-grounded under the matcher.
    payload["reasoning_passages"] = verified

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

    # Emit explicit conversation-native audit seed plus legacy compatibility.
    audit_seed = _build_audit_seed(payload, assistant_text=assistant_text)
    critique_request = _map_to_critique_request(payload, assistant_text=assistant_text)

    output = {
        "status": "ok",
        "extraction": payload,
        "audit_seed": audit_seed,
        "critique_request": critique_request,
        "provider_call_custody": _terminal_call_custody(
            call_custody,
            terminal_status="admissible_extraction",
            admissible_extraction=True,
        ),
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
