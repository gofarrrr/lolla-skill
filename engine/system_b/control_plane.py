"""Control-plane contract helpers for optional external Lolla callers.

The control-plane layer is metadata only. It preserves trace/action/approval
references supplied by an external agent framework without making Lolla a
policy engine, sandbox, proxy, or action approver.
"""
from __future__ import annotations

import datetime as _dt
import json
import shutil
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


CONTROL_INPUT_SCHEMA_VERSION = "lolla_control_input.v1"
CONTROL_RESULT_SCHEMA_VERSION = "lolla_control_result.v1"
CONTROL_INPUT_FILENAME = "control_input.json"
CONTROL_RESULT_FILENAME = "control_result.json"

CONTROL_MODES = frozenset(
    {
        "pre_final_answer",
        "pre_action_reasoning_gate",
        "post_run_review",
        "regression_eval",
    }
)

APPROVAL_OUTCOME_BY_CALLER_ACTION = {
    "use_revised_answer": "proceed_with_external_policy",
    "ask_user_first": "require_human_approval",
    "rerun_deeper": "rerun_deeper",
    "do_not_use_run_degraded": "block_reasoning_incomplete",
    "unsupported_high_stakes_domain": "block_unsupported_stakes",
}


def control_input_summary(run_dir: Path) -> dict[str, Any]:
    """Return compact external control metadata for public artifacts.

    The raw ``control_input.json`` is preserved as an archive artifact when
    supplied. This summary intentionally avoids copying proposed-action
    argument values into agent-facing/custody summaries.
    """

    payload = _read_json_object(Path(run_dir) / CONTROL_INPUT_FILENAME)
    if not payload:
        return {}

    conversation = _mapping(payload.get("conversation"))
    agent = _mapping(payload.get("agent"))
    proposed_action = _mapping(payload.get("proposed_action"))
    control_context = _mapping(payload.get("control_context"))
    schema_version = _text(payload.get("schema_version"))
    mode = _mode(payload)

    summary: dict[str, Any] = {
        "schema_version": schema_version or "unknown",
        "expected_schema_version": CONTROL_INPUT_SCHEMA_VERSION,
        "status": "valid" if schema_version == CONTROL_INPUT_SCHEMA_VERSION else "invalid_schema",
        "control_mode": mode,
        "lolla_enforces_actions": False,
    }
    _add_if_present(
        summary,
        "external_trace_id",
        _text(payload.get("external_trace_id")) or _text(conversation.get("trace_id")),
    )
    spans = _strings(payload.get("external_span_ids")) or _strings(conversation.get("span_ids"))
    if spans:
        summary["external_span_ids"] = spans
    _add_if_present(
        summary,
        "agent_run_id",
        _text(payload.get("agent_run_id"))
        or _text(agent.get("run_id"))
        or _text(conversation.get("session_id")),
    )
    _add_if_present(
        summary,
        "agent_framework",
        _text(payload.get("agent_framework")) or _text(agent.get("framework")),
    )
    action_summary = _proposed_action_summary(proposed_action)
    if action_summary:
        summary["proposed_action"] = action_summary
    tool_call_ids = (
        _strings(payload.get("tool_call_ids"))
        or _strings(control_context.get("tool_call_ids"))
        or _strings(proposed_action.get("tool_call_ids"))
    )
    if tool_call_ids:
        summary["tool_call_ids"] = tool_call_ids
    for field in (
        "approval_id",
        "policy_engine",
        "policy_decision",
        "sandbox_id",
        "credential_scope",
    ):
        _add_if_present(
            summary,
            field,
            _text(payload.get(field)) or _text(control_context.get(field)),
        )
    return summary


def build_control_result(
    run_dir: Path,
    *,
    run_id: str,
    case_id: str = "",
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build ``lolla_control_result.v1`` around the existing agent result.

    Returns an empty dict when no ``control_input.json`` was supplied.
    """

    run_dir = Path(run_dir)
    control_input = control_input_summary(run_dir)
    if not control_input:
        return {}
    agent_result = _read_json_object(run_dir / "agent_result.json")
    caller_action = _text(agent_result.get("caller_action"))
    return {
        "schema_version": CONTROL_RESULT_SCHEMA_VERSION,
        "created_at": created_at or _utc_now_iso(),
        "run_id": run_id,
        "case_id": case_id,
        "control_mode": control_input.get("control_mode") or "pre_final_answer",
        "status": _text(agent_result.get("status")) or "unknown",
        "status_reason": _text(agent_result.get("status_reason")),
        "risk_mode": _text(agent_result.get("risk_mode")) or "standard",
        "caller_action": caller_action,
        "approval_outcome": APPROVAL_OUTCOME_BY_CALLER_ACTION.get(
            caller_action,
            "inspect_manually",
        ),
        "reasoning_risk": _text(agent_result.get("main_counter_pressure"))
        or _text(agent_result.get("status_reason")),
        "do_not_act_before": _strings(agent_result.get("do_not_act_before")),
        "human_approval_context": _human_approval_context(
            caller_action=caller_action,
            agent_result=agent_result,
            control_input=control_input,
        ),
        "control_input": control_input,
        "artifact_paths": _mapping(agent_result.get("artifact_paths")),
        "boundary": {
            "lolla_approves_actions": False,
            "lolla_replaces_policy_engine": False,
            "lolla_replaces_sandbox": False,
            "lolla_replaces_identity_scope": False,
        },
    }


def write_control_result(
    run_dir: Path,
    *,
    run_id: str,
    case_id: str = "",
    created_at: str | None = None,
    tmp_copy_path: Path | None = None,
) -> tuple[Path | None, dict[str, Any]]:
    """Write ``control_result.json`` when control input was supplied."""

    payload = build_control_result(
        run_dir,
        run_id=run_id,
        case_id=case_id,
        created_at=created_at,
    )
    if not payload:
        return None, {}
    path = Path(run_dir) / CONTROL_RESULT_FILENAME
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if tmp_copy_path is not None:
        tmp_copy_path = Path(tmp_copy_path)
        tmp_copy_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, tmp_copy_path)
    return path, payload


def _mode(payload: Mapping[str, Any]) -> str:
    mode = _text(payload.get("control_mode")) or _text(payload.get("mode"))
    return mode if mode in CONTROL_MODES else "pre_final_answer"


def _proposed_action_summary(action: Mapping[str, Any]) -> dict[str, Any]:
    if not action:
        return {}
    arguments = _mapping(action.get("arguments"))
    summary: dict[str, Any] = {}
    for field in ("tool_name", "action_type", "risk_class"):
        _add_if_present(summary, field, _text(action.get(field)))
    if arguments:
        summary["has_arguments"] = True
        summary["argument_keys"] = sorted(str(key) for key in arguments.keys())
    return summary


def _human_approval_context(
    *,
    caller_action: str,
    agent_result: Mapping[str, Any],
    control_input: Mapping[str, Any],
) -> dict[str, Any]:
    action = _mapping(control_input.get("proposed_action"))
    action_name = _text(action.get("tool_name")) or _text(action.get("action_type")) or "the proposed action"
    if caller_action == "use_revised_answer":
        summary = (
            "Lolla did not identify a run-health reason to block use; external "
            "policy, approval, sandbox, and credential checks still apply."
        )
        rejection = ""
    elif caller_action == "ask_user_first":
        summary = f"Ask the user before proceeding with {action_name}."
        rejection = "Do not proceed until the user explicitly approves the action."
    elif caller_action == "rerun_deeper":
        summary = "Rerun Lolla in a deeper mode before proceeding."
        rejection = "Do not proceed from this audit result; rerun deeper first."
    elif caller_action == "unsupported_high_stakes_domain":
        summary = "Do not proceed automatically; the domain is outside Lolla's supported action boundary."
        rejection = "Escalate to an appropriate human/domain expert before acting."
    else:
        summary = "Do not proceed from this audit result because Lolla marked the run degraded or incomplete."
        rejection = "Do not act on this run; inspect artifacts or rerun Lolla first."
    return {
        "summary": summary,
        "suggested_rejection_message": rejection,
        "human_questions": _strings(agent_result.get("human_questions")),
    }


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _strings(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [text for item in value if (text := _text(item))]


def _text(value: Any) -> str:
    return str(value or "").strip()


def _add_if_present(payload: dict[str, Any], key: str, value: str) -> None:
    if value:
        payload[key] = value


def _utc_now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
