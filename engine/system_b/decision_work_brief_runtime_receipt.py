"""Short user receipt renderer for runtime-attached Decision Work Briefs."""
from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


SUPPORTED_ATTACHMENT_STATES = (
    "generated",
    "generated_with_caveats",
    "generated_agent_only",
    "blocked",
    "deferred",
    "failed_closed",
    "not_requested",
    "not_eligible",
    "disabled",
)
RAW_PRIVATE_MARKERS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)
DEFAULT_ACTION_LINE = "See the Decision Work Brief."
DEFAULT_CAVEAT = "this is an audit summary, not proof that the advice is correct"


class DecisionWorkBriefRuntimeReceiptError(ValueError):
    """Sanitized receipt-rendering error."""


def render_decision_work_brief_runtime_receipt(
    *,
    attachment_state: str,
    action_consequence: str | None = None,
    full_brief_ref: str | None = None,
    evidence_ref: str | None = None,
    reasons: Sequence[str] | None = None,
    caveat: str | None = None,
) -> str:
    """Render a compact, non-overclaiming Decision Work Brief receipt."""

    state = _normalize_state(attachment_state)
    status_line = _status_line(state)
    changed_line = _changed_or_reason_line(
        state=state,
        action_consequence=action_consequence,
        reasons=reasons,
    )
    caveat_line = f"Main caveat: {_safe_text(caveat or DEFAULT_CAVEAT)}."
    lines = [status_line, "", changed_line, "", caveat_line]

    if state in {"generated", "generated_with_caveats", "generated_agent_only"}:
        if full_brief_ref:
            lines.extend(["", f"Open full brief: `{_safe_ref(full_brief_ref)}`"])
        if evidence_ref:
            lines.extend(["", f"Open evidence bundle: `{_safe_ref(evidence_ref)}`"])
    elif evidence_ref:
        lines.extend(["", f"Open evidence status: `{_safe_ref(evidence_ref)}`"])

    return "\n".join(lines).rstrip() + "\n"


def render_receipt_from_status(
    status: Mapping[str, Any],
    *,
    action_consequence: str | None = None,
) -> str:
    """Render receipt text from an attachment status or eligibility object."""

    generated = _mapping(status.get("generated_artifacts"))
    state = _text(status.get("attachment_state"), "deferred")
    full_ref = (
        generated.get("decision_work_brief_enriched_markdown")
        or generated.get("decision_work_brief_markdown")
        or generated.get("full_brief_ref")
    )
    evidence_ref = (
        generated.get("attachment_status")
        or generated.get("evidence_bundle_ref")
        or status.get("status_ref")
    )
    reasons = (
        _string_list(status.get("blocked_reasons"))
        or _string_list(status.get("hard_blockers"))
        or _string_list(status.get("deferred_reasons"))
        or _string_list(status.get("soft_triage_blockers"))
    )
    if state == "generated" and _string_list(status.get("soft_triage_blockers")):
        state = "generated_with_caveats"
    return render_decision_work_brief_runtime_receipt(
        attachment_state=state,
        action_consequence=action_consequence,
        full_brief_ref=_text(full_ref),
        evidence_ref=_text(evidence_ref),
        reasons=reasons,
    )


def load_status_json(path: Path | str) -> dict[str, Any]:
    """Load a receipt source JSON object."""

    input_path = Path(path).expanduser()
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DecisionWorkBriefRuntimeReceiptError("status JSON file was not found") from exc
    except json.JSONDecodeError as exc:
        raise DecisionWorkBriefRuntimeReceiptError("status JSON file was malformed") from exc
    except UnicodeDecodeError as exc:
        raise DecisionWorkBriefRuntimeReceiptError(
            "status JSON file was not valid UTF-8"
        ) from exc
    if not isinstance(payload, dict):
        raise DecisionWorkBriefRuntimeReceiptError("status JSON root was not an object")
    return payload


def _status_line(state: str) -> str:
    return {
        "generated": "Decision Work Brief: available",
        "generated_with_caveats": "Decision Work Brief: available with caveats",
        "generated_agent_only": "Decision Work Brief: available for agent inspection",
        "blocked": "Decision Work Brief: blocked",
        "deferred": "Decision Work Brief: deferred",
        "failed_closed": "Decision Work Brief: failed closed",
        "not_requested": "Decision Work Brief: not requested",
        "not_eligible": "Decision Work Brief: not eligible",
        "disabled": "Decision Work Brief: not requested",
    }[state]


def _changed_or_reason_line(
    *,
    state: str,
    action_consequence: str | None,
    reasons: Sequence[str] | None,
) -> str:
    if state in {"generated", "generated_with_caveats", "generated_agent_only"}:
        prefix = "What changed"
        if state == "generated_agent_only":
            prefix = "Agent route"
        return f"{prefix}: {_safe_text(action_consequence or DEFAULT_ACTION_LINE)}"
    if state == "not_requested" or state == "disabled":
        return "Reason: runtime attachment is disabled by default."
    return f"Reason: {_safe_text(_join_reasons(reasons or []))}."


def _normalize_state(state: str) -> str:
    if state not in SUPPORTED_ATTACHMENT_STATES:
        raise DecisionWorkBriefRuntimeReceiptError("unsupported attachment state")
    return "not_requested" if state == "disabled" else state


def _safe_text(value: str) -> str:
    text = " ".join(str(value).strip().split())
    if not text:
        return "not specified"
    if any(marker in text for marker in RAW_PRIVATE_MARKERS):
        raise DecisionWorkBriefRuntimeReceiptError("receipt text contains private marker")
    return text


def _safe_ref(value: str) -> str:
    ref = str(value).strip()
    if not ref:
        raise DecisionWorkBriefRuntimeReceiptError("receipt ref was empty")
    if Path(ref).is_absolute() or any(marker in ref for marker in RAW_PRIVATE_MARKERS):
        raise DecisionWorkBriefRuntimeReceiptError("receipt ref was unsafe")
    return ref


def _join_reasons(reasons: Sequence[str]) -> str:
    safe = [_safe_text(reason) for reason in reasons if str(reason).strip()]
    return ", ".join(safe[:3]) if safe else "not specified"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _text(value: Any, fallback: str = "") -> str:
    return value if isinstance(value, str) and value else fallback
