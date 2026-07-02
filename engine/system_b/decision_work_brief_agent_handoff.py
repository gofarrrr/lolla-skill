"""Agent handoff packet for runtime-attached Decision Work Brief bundles."""
from __future__ import annotations

import datetime as _dt
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any


AGENT_HANDOFF_SCHEMA_VERSION = "lolla.decision_work_brief_agent_handoff.v0"
AGENT_HANDOFF_CONTRACT_SCHEMA_VERSION = "lolla.decision_work_brief_agent_handoff_contract.v0"
TRIAGE_READ_SCHEMA_VERSION = "lolla.decision_work_automatic_triage_provisional_read.v0"
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
NON_CLAIMS = (
    "not_runtime_default",
    "not_customer_readiness",
    "not_human_validation",
    "not_product_proof",
    "not_answer_quality_scoring",
    "not_advice_correctness",
    "not_lolla_improvement_proof",
    "not_agent_action_authorization",
    "not_automatic_action_authorization",
    "triage_is_routing_not_scoring",
    "handoff_is_for_inspection_not_action",
)


class DecisionWorkBriefAgentHandoffError(ValueError):
    """Sanitized handoff-generation error."""


def build_decision_work_brief_agent_handoff(
    *,
    source_run_ref: str,
    attachment_status: Mapping[str, Any],
    eligibility_result: Mapping[str, Any] | None = None,
    triage_read: Mapping[str, Any] | None = None,
    case_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build a checked-in-safe agent inspection packet."""

    generated = _mapping(attachment_status.get("generated_artifacts"))
    triage_case = _select_triage_case(triage_read=triage_read, case_id=case_id)
    eligibility = _mapping(eligibility_result)
    attachment_state = _text(attachment_status.get("attachment_state"), "deferred")
    handoff = {
        "schema_version": AGENT_HANDOFF_SCHEMA_VERSION,
        "handoff_metadata": {
            "created_at": created_at or _utc_now(),
            "builder": "engine.system_b.decision_work_brief_agent_handoff",
            "deterministic_only": True,
            "post_archive_only": True,
        },
        "source_run_ref": _safe_text(source_run_ref),
        "attachment_state": attachment_state,
        "attachment_status_ref": _safe_optional_ref(
            generated.get("attachment_status"),
        ),
        "brief_refs": {
            "decision_work_brief_json": _safe_optional_ref(
                generated.get("decision_work_brief_json"),
            ),
            "decision_work_brief_markdown": _safe_optional_ref(
                generated.get("decision_work_brief_markdown"),
            ),
        },
        "enriched_brief_refs": {
            "decision_work_brief_enriched_markdown": _safe_optional_ref(
                generated.get("decision_work_brief_enriched_markdown"),
            )
        },
        "triage_refs": {
            "automatic_triage_packet": _safe_optional_ref(
                generated.get("automatic_triage_packet"),
            ),
            "automatic_triage_read": _safe_optional_ref(
                generated.get("automatic_triage_read"),
            ),
        },
        "safe_supply_resolver": _resolver_summary(attachment_status),
        "source_status": _source_status(attachment_status, eligibility),
        "privacy_redaction_status": _privacy_redaction_status(),
        "missingness": {
            "missing_artifacts": _mapping(attachment_status.get("missing_artifacts")),
            "blocked_reasons": _string_list(attachment_status.get("blocked_reasons"))
            or _string_list(eligibility.get("hard_blockers")),
            "deferred_reasons": _string_list(attachment_status.get("deferred_reasons")),
        },
        "uncertainty": _uncertainty(triage_case),
        "route_outputs": _route_outputs(triage_case, eligibility),
        "blocked_or_deferred_state": {
            "attachment_state": attachment_state,
            "hard_blockers": _string_list(eligibility.get("hard_blockers")),
            "soft_triage_blockers": _string_list(
                eligibility.get("soft_triage_blockers")
            ),
        },
        "agent_inspection_focus": _agent_inspection_focus(triage_case, eligibility),
        "custody_flags": _custody_flags(),
        "non_claims": list(NON_CLAIMS),
    }
    _assert_private_safe(handoff)
    return handoff


def render_agent_handoff_json(handoff: Mapping[str, Any], *, pretty: bool = False) -> str:
    indent = 2 if pretty else None
    return json.dumps(handoff, indent=indent, sort_keys=True) + "\n"


def load_json_object(path: Path | str) -> dict[str, Any]:
    input_path = Path(path).expanduser()
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DecisionWorkBriefAgentHandoffError("JSON file was not found") from exc
    except json.JSONDecodeError as exc:
        raise DecisionWorkBriefAgentHandoffError("JSON file was malformed") from exc
    except UnicodeDecodeError as exc:
        raise DecisionWorkBriefAgentHandoffError("JSON file was not valid UTF-8") from exc
    if not isinstance(payload, dict):
        raise DecisionWorkBriefAgentHandoffError("JSON root was not an object")
    return payload


def _source_status(
    attachment_status: Mapping[str, Any],
    eligibility: Mapping[str, Any],
) -> dict[str, Any]:
    run_status = _mapping(
        eligibility.get("run_artifact_status")
        or attachment_status.get("run_artifact_status")
    )
    return {
        "source_refs_only": True,
        "run_artifact_status": run_status,
        "source_status_summary": "structured refs only; raw/private content omitted",
    }


def _resolver_summary(attachment_status: Mapping[str, Any]) -> dict[str, Any]:
    summary = _mapping(attachment_status.get("resolver_summary"))
    return {
        "resolver_output_ref": _safe_optional_ref(summary.get("resolver_output_ref")),
        "resolver_status": _safe_text(_text(summary.get("resolver_status"), "not_supplied")),
        "resolver_mode": _safe_text(_text(summary.get("resolver_mode"), "not_supplied")),
        "feeds_runtime_bundle": summary.get("feeds_runtime_bundle") is True,
        "resolved_inputs": _resolver_input_names(summary.get("resolved_inputs")),
        "deferred_inputs": _resolver_input_names(summary.get("deferred_inputs")),
        "blocked_inputs": _resolver_input_names(summary.get("blocked_inputs")),
        "unsafe_inputs_excluded": _string_list(summary.get("unsafe_inputs_excluded")),
        "queue_handoff": _safe_mapping(summary.get("queue_handoff")),
        "agent_action_authorized": False,
        "automatic_action_authorized": False,
    }


def _resolver_input_names(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    names: list[str] = []
    for item in value:
        if isinstance(item, Mapping):
            name = item.get("input_name")
            if isinstance(name, str) and name:
                names.append(_safe_text(name))
    return names


def _privacy_redaction_status() -> dict[str, bool]:
    return {
        "raw_conversation_text_included": False,
        "raw_revised_answer_text_included": False,
        "raw_memo_text_included": False,
        "provider_text_included": False,
        "private_ledgers_included": False,
        "local_absolute_paths_included": False,
    }


def _uncertainty(triage_case: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "uncertainty": _text(triage_case.get("uncertainty"), "not_evaluated"),
        "source_depth_read": _safe_text(
            _text(triage_case.get("source_depth_read"), "not_evaluated")
        ),
        "private_context_dependency": _safe_text(
            _text(triage_case.get("private_context_dependency"), "not_evaluated")
        ),
    }


def _route_outputs(
    triage_case: Mapping[str, Any],
    eligibility: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "user_surface_route": _text(triage_case.get("user_surface_route"), "not_evaluated"),
        "agent_inspection_route": _text(
            triage_case.get("agent_inspection_route"),
            "not_evaluated",
        ),
        "human_calibration_route": _text(
            triage_case.get("human_calibration_route"),
            "not_evaluated",
        ),
        "domain_review_route": _text(
            triage_case.get("domain_review_route"),
            "not_evaluated",
        ),
        "runtime_attachment_route": _text(
            triage_case.get("runtime_attachment_route"),
            "not_evaluated",
        ),
        "agent_inspection_only": eligibility.get("agent_inspection_only") is True,
        "agent_action_authorized": False,
        "automatic_action_authorized": False,
        "must_not_be_used_as_quality_label": True,
    }


def _agent_inspection_focus(
    triage_case: Mapping[str, Any],
    eligibility: Mapping[str, Any],
) -> list[str]:
    focus = _string_list(triage_case.get("triage_categories"))
    focus.extend(_string_list(eligibility.get("soft_triage_blockers")))
    downstream = triage_case.get("what_downstream_agent_should_inspect_first")
    if isinstance(downstream, str) and downstream:
        focus.append(_safe_text(downstream))
    return list(dict.fromkeys(focus)) or ["inspect_attachment_status_first"]


def _select_triage_case(
    *,
    triage_read: Mapping[str, Any] | None,
    case_id: str | None,
) -> Mapping[str, Any]:
    if triage_read is None:
        return {}
    if triage_read.get("schema_version") != TRIAGE_READ_SCHEMA_VERSION:
        raise DecisionWorkBriefAgentHandoffError("unsupported triage read schema")
    cases = triage_read.get("case_triage_reads")
    if not isinstance(cases, list):
        return {}
    if case_id is None and len(cases) == 1 and isinstance(cases[0], Mapping):
        return cases[0]
    for case in cases:
        if isinstance(case, Mapping) and case.get("case_id") == case_id:
            return case
    return {}


def _custody_flags() -> dict[str, Any]:
    return {
        "human_validated": False,
        "human_review_completed": False,
        "product_proof": False,
        "model_calls": 0,
        "runtime_invoked": False,
        "skill_invoked": False,
        "archive_mutated": False,
        "answer_quality_scored": False,
        "agent_action_authorized": False,
        "automatic_action_authorized": False,
        "raw_private_content_included": False,
        "provider_text_included": False,
        "local_absolute_paths_included": False,
    }


def _safe_optional_ref(value: Any) -> str | None:
    if value is None:
        return None
    ref = str(value).strip()
    if not ref:
        return None
    if Path(ref).is_absolute() or _contains_private_marker(ref):
        raise DecisionWorkBriefAgentHandoffError("handoff ref was unsafe")
    return ref


def _safe_text(value: str) -> str:
    text = " ".join(str(value).strip().split())
    if _contains_private_marker(text):
        raise DecisionWorkBriefAgentHandoffError("handoff text contains private marker")
    return text


def _contains_private_marker(text: str) -> bool:
    return any(marker in text for marker in RAW_PRIVATE_MARKERS)


def _assert_private_safe(value: Any) -> None:
    rendered = json.dumps(value, sort_keys=True)
    if _contains_private_marker(rendered):
        raise DecisionWorkBriefAgentHandoffError("handoff payload was not private safe")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _safe_mapping(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        return {}
    safe: dict[str, Any] = {}
    for key, item in value.items():
        if not isinstance(key, str):
            continue
        if isinstance(item, str):
            safe[key] = _safe_text(item)
        elif isinstance(item, bool) or item is None:
            safe[key] = item
        else:
            safe[key] = _safe_text(str(item))
    return safe


def _text(value: Any, fallback: str = "") -> str:
    return value if isinstance(value, str) and value else fallback


def _utc_now() -> str:
    return _dt.datetime.now(tz=_dt.UTC).replace(microsecond=0).isoformat().replace(
        "+00:00",
        "Z",
    )
