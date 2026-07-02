"""Internal Markdown debug summary for Decision Work Receipt artifacts.

This module renders a compact maintainer packet from existing receipt/report
JSON. It does not run Lolla, call models, mutate archives, read raw/private
content, or judge answer quality. It is deliberately a renderer over known safe
fields, not a semantic interpreter over arbitrary report prose.
"""
from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any


DECISION_WORK_RECEIPT_DEBUG_SUMMARY_VERSION = "lolla.decision_work_receipt_debug_summary.v0"

DECISION_TRAIL_SECTION_LABELS = {
    "conversation_understanding_summary": "conversation understanding summary",
    "decision_question": "decision question",
    "vanilla_likely_next_action": "vanilla likely next action",
    "revised_likely_next_action": "revised likely next action",
    "option_map": "option map",
    "constraints": "constraints",
    "stakeholders": "stakeholders",
    "values_or_priorities": "values/priorities",
    "assistant_influence": "assistant influence",
    "audit_pressure_summary": "audit pressure summary",
    "structural_delta": "structural delta",
    "useful_noisy_friction": "useful/noisy friction",
    "lost_value": "lost value",
    "unresolved_questions": "unresolved questions",
}

CHALLENGE_SURFACE_LABELS = {
    "lane1_structural_pressure": "structural pressure",
    "lane2_model_companion": "model companion",
    "lane3_frame_pressure": "frame pressure",
    "lane4_structural_coverage": "structural coverage",
    "delivery_bullshit_index": "delivery bullshit-index check",
    "audit_summary_trace": "audit summary trace",
    "v60_private_enrichment": "private enrichment",
    "optional_pressure_check_state": "optional pressure-check state",
    "pre_step6_private_table": "pre-Step-6 private table",
    "graph_survival_report": "graph survival report",
}

NON_CLAIM_LABELS = {
    "clean_artifacts_do_not_imply_good_advice": "clean artifacts do not imply good advice",
    "not_agent_action_authorization": "not agent action authorization",
    "not_answer_quality_scoring": "not answer-quality scoring",
    "not_correctness_proof": "not correctness proof",
    "not_llm_judge": "not an LLM judge",
    "not_product_proof": "not product proof",
    "not_runtime_integration": "not runtime integration",
}


class DecisionWorkReceiptDebugSummaryInputError(ValueError):
    """Sanitized renderer input error."""


def load_json_object(path: Path | str) -> dict[str, Any]:
    """Load a JSON object from a path with sanitized errors."""

    input_path = Path(path).expanduser()
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DecisionWorkReceiptDebugSummaryInputError("input JSON file was not found") from exc
    except json.JSONDecodeError as exc:
        raise DecisionWorkReceiptDebugSummaryInputError("input JSON file was malformed") from exc
    except UnicodeDecodeError as exc:
        raise DecisionWorkReceiptDebugSummaryInputError("input JSON file was not valid UTF-8") from exc
    except OSError as exc:
        raise DecisionWorkReceiptDebugSummaryInputError(
            f"input JSON file could not be read:{type(exc).__name__}"
        ) from exc
    if not isinstance(payload, dict):
        raise DecisionWorkReceiptDebugSummaryInputError("input JSON root was not an object")
    return payload


def render_decision_work_receipt_debug_summary(
    *,
    receipt: Mapping[str, Any],
    decision_trail_report: Mapping[str, Any] | None = None,
) -> str:
    """Render an internal Markdown summary from safe structured fields."""

    if receipt.get("schema_version") != "lolla.decision_work_receipt.v0":
        raise DecisionWorkReceiptDebugSummaryInputError("receipt schema version was unsupported")
    if decision_trail_report is not None and decision_trail_report.get("schema_version") != "lolla.decision_trail_report.v0":
        raise DecisionWorkReceiptDebugSummaryInputError("Decision Trail schema version was unsupported")

    metadata = _mapping(receipt.get("receipt_metadata"))
    process = _mapping(receipt.get("conversation_process_map"))
    challenge = _mapping(receipt.get("challenge_coverage"))
    source_inventory = _mapping(receipt.get("source_context_inventory"))
    missingness = _mapping(receipt.get("missingness_and_redaction"))
    readiness = _mapping(receipt.get("process_evidence_readiness"))
    decision_trail_summary = _mapping(receipt.get("decision_trail_summary"))
    product_delta_summary = _mapping(receipt.get("product_delta_summary"))

    lines = [
        "# Decision Work Receipt Debug Summary",
        "",
        "This is an internal diagnostic packet generated from Lolla custody artifacts. It is not the customer-facing decision story and not a judgment that the final answer was correct or useful.",
        "",
        "## Case",
        "",
        f"- Case: `{_text(metadata.get('case_id'), 'unknown')}`",
        f"- Run: `{_text(metadata.get('run_id'), 'unknown')}`",
        f"- Receipt readiness: `{_text(readiness.get('label'), 'unknown')}`",
        f"- Receipt mode: `{_text(metadata.get('receipt_mode'), 'unknown')}`",
        "",
        "## What Happened",
        "",
    ]

    lines.extend(_process_lines(process))
    lines.extend(["", "## What Lolla Challenged", ""])
    lines.extend(_challenge_lines(challenge))
    lines.extend(["", "## What The Receipt Links", ""])
    lines.extend(_linked_report_lines(decision_trail_summary, product_delta_summary))
    lines.extend(["", "## What The Decision Trail Can Read", ""])
    lines.extend(_decision_trail_lines(decision_trail_report))
    lines.extend(["", "## What Is Still Missing Or Private", ""])
    lines.extend(_missingness_lines(source_inventory, missingness))
    lines.extend(["", "## What This Must Not Be Used For", ""])
    lines.extend(_non_claim_lines(receipt))
    lines.extend(["", "## Internal Diagnostic Read", ""])
    lines.extend(_diagnostic_read_lines(receipt, decision_trail_report))

    return "\n".join(lines).rstrip() + "\n"


def write_decision_work_receipt_debug_summary(path: Path | str, markdown: str) -> None:
    """Write the rendered Markdown to disk."""

    output_path = Path(path).expanduser()
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
    except OSError as exc:
        raise DecisionWorkReceiptDebugSummaryInputError(
            f"output could not be written:{type(exc).__name__}"
        ) from exc


def _process_lines(process: Mapping[str, Any]) -> list[str]:
    turn_count = process.get("turn_count")
    user_turns = process.get("user_turn_count")
    assistant_turns = process.get("assistant_turn_count")
    depth = _text(process.get("process_depth"), "not measured")
    count_line = _turn_count_line(
        turn_count=turn_count,
        user_turns=user_turns,
        assistant_turns=assistant_turns,
    )
    lines = [
        f"- Process shape: `{depth}`",
        count_line,
    ]
    if depth == "multi_turn_evidence":
        lines.append("- Maintainer meaning: this was not just a one-prompt answer; Lolla sees evidence of a back-and-forth conversation.")
    elif depth == "one_shot_candidate":
        lines.append("- Maintainer meaning: this may be closer to a one-prompt answer than a worked-through conversation.")
    else:
        lines.append("- Maintainer meaning: process depth is not well measured from the safe structured artifacts.")
    lines.append("- Boundary: turn count is process evidence, not proof of good thinking.")
    return lines


def _turn_count_line(
    *,
    turn_count: Any,
    user_turns: Any,
    assistant_turns: Any,
) -> str:
    if isinstance(turn_count, int) and isinstance(user_turns, int) and isinstance(assistant_turns, int):
        role_sum = user_turns + assistant_turns
        if role_sum > turn_count:
            return (
                f"- Captured turn metadata: reported total `{turn_count}`, "
                f"`{user_turns}` user, `{assistant_turns}` assistant "
                f"(role counts sum to `{role_sum}`; treat this as a metadata "
                "inconsistency, not a semantic finding)."
            )
    return (
        f"- Captured turns: `{_number_or_unknown(turn_count)}` total, "
        f"`{_number_or_unknown(user_turns)}` user, "
        f"`{_number_or_unknown(assistant_turns)}` assistant"
    )


def _challenge_lines(challenge: Mapping[str, Any]) -> list[str]:
    surfaces = _list(challenge.get("surfaces"))
    present = [
        _surface_label(_mapping(surface).get("surface_id"))
        for surface in surfaces
        if _mapping(surface).get("present") is True
    ]
    if not present:
        lines = ["- No challenge surfaces were visible from the safe structured receipt."]
    else:
        lines = ["- Visible challenge surfaces:"]
        lines.extend(f"  - {label}" for label in present)
    caveats = _string_list(challenge.get("run_health_caveats"))
    if caveats:
        lines.extend(["- Run-health caveats:"] + [f"  - `{caveat}`" for caveat in caveats])
    else:
        lines.append("- Run-health caveats: none recorded in the receipt.")
    lines.append("- Boundary: visible challenge surfaces are not proof that the challenge was sufficient.")
    return lines


def _linked_report_lines(
    decision_trail_summary: Mapping[str, Any],
    product_delta_summary: Mapping[str, Any],
) -> list[str]:
    return [
        f"- Decision Trail report: `{_text(decision_trail_summary.get('status'), 'unknown')}`",
        f"- Product Delta report: `{_text(product_delta_summary.get('status'), 'unknown')}`",
        "- Maintainer meaning: linked reports make the process easier to inspect, but do not turn the receipt into proof.",
    ]


def _decision_trail_lines(report: Mapping[str, Any] | None) -> list[str]:
    if report is None:
        return [
            "- No Decision Trail JSON was provided to this Markdown renderer.",
            "- The receipt can still describe process custody, but not the richer Decision Trail field status.",
        ]

    available: list[str] = []
    interpretation_needed: list[str] = []
    missing: list[str] = []
    for field, label in DECISION_TRAIL_SECTION_LABELS.items():
        section = _mapping(report.get(field))
        status = _text(section.get("status"), "not_supplied")
        if status in {"available_from_structured_artifact", "available_from_review_artifact"}:
            available.append(label)
        elif status == "requires_llm_interpretation":
            interpretation_needed.append(label)
        else:
            missing.append(f"{label}: `{status}`")

    lines: list[str] = []
    lines.append("- Available from structured artifacts:")
    lines.extend(_bullet_items(available))
    lines.append("- Still requiring LLM or human interpretation:")
    lines.extend(_bullet_items(interpretation_needed))
    if missing:
        lines.append("- Missing, unclear, or not supplied:")
        lines.extend(f"  - {item}" for item in missing)
    lines.append("- Boundary: this is field status, not answer-quality scoring.")
    return lines


def _missingness_lines(
    source_inventory: Mapping[str, Any],
    missingness: Mapping[str, Any],
) -> list[str]:
    counts = _mapping(source_inventory.get("source_counts"))
    missing_sources = _list(missingness.get("missing_sources"))
    redacted_private = _list(missingness.get("redacted_or_private_sources"))
    interpretation_needed = _string_list(missingness.get("interpretation_needed_fields"))
    lines = [
        f"- Safe structured sources read: `{_number_or_unknown(counts.get('read_safe_structured_fields'))}`",
        f"- Raw/redacted/private sources not exported: `{len(redacted_private)}`",
        f"- Missing sources: `{len(missing_sources)}`",
    ]
    if interpretation_needed:
        lines.append("- Fields still needing interpretation:")
        lines.extend(f"  - `{field}`" for field in interpretation_needed)
    else:
        lines.append("- Fields still needing interpretation: none listed.")
    lines.append("- Boundary: private availability is different from missing; the receipt records that distinction without exposing private content.")
    return lines


def _non_claim_lines(receipt: Mapping[str, Any]) -> list[str]:
    non_claims = _mapping(receipt.get("non_claims"))
    active = [
        label
        for key, label in NON_CLAIM_LABELS.items()
        if non_claims.get(key) is True
    ]
    if not active:
        return ["- No explicit non-claims were found; treat this summary as incomplete."]
    return [f"- {label}" for label in active]


def _diagnostic_read_lines(
    receipt: Mapping[str, Any],
    decision_trail_report: Mapping[str, Any] | None,
) -> list[str]:
    readiness = _mapping(receipt.get("process_evidence_readiness"))
    label = _text(readiness.get("label"), "unknown")
    if label == "decision_trail_review_ready":
        lead = "This case is ready for a reviewer to inspect the work trail, because the receipt has process evidence and a linked Decision Trail reference."
    elif label == "challenged_and_revised_process":
        lead = "This case shows a challenged Lolla process, but no linked Decision Trail or Product Delta report was supplied to this packet."
    else:
        lead = "This case has limited work-trail readiness from the safe structured artifacts."

    lines = [
        f"- {lead}",
        "- What this helps maintainers inspect: whether a visible process existed, which artifacts support that process, what was private or missing, and which interpretation fields remain unresolved.",
        "- What this does not give users: the actual decision consequence, what action changed, which trade-off mattered, whether Lolla improved the decision, or whether an agent should act.",
    ]
    if decision_trail_report is not None:
        lines.append("- Current product gap: the user-facing brief still needs bounded LLM or human interpretation for options, likely actions, stakeholders, useful/noisy friction, lost value, and action consequence.")
    return lines


def _surface_label(surface_id: Any) -> str:
    value = _text(surface_id, "unknown")
    return CHALLENGE_SURFACE_LABELS.get(value, value.replace("_", " "))


def _bullet_items(items: list[str]) -> list[str]:
    if not items:
        return ["  - none"]
    return [f"  - {item}" for item in items]


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    return []


def _string_list(value: Any) -> list[str]:
    return [item for item in _list(value) if isinstance(item, str)]


def _text(value: Any, fallback: str) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return fallback


def _number_or_unknown(value: Any) -> str:
    if isinstance(value, int):
        return str(value)
    return "unknown"
