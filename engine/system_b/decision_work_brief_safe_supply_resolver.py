"""Safe input resolver for runtime-attached Decision Work Brief bundles.

The resolver is deterministic: it validates refs, records missingness and
blockers, and emits feedability status for the runtime bundle. It does not run
Lolla, call models, mutate archives, infer conversation meaning, score advice,
or authorize action.
"""
from __future__ import annotations

import datetime as _dt
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from engine.system_b.decision_work_brief_safe_case_registry import (
    DecisionWorkBriefSafeCaseRegistryError,
    resolver_kwargs_from_case_registry,
)


RESOLVER_SCHEMA_VERSION = "lolla.decision_work_brief_runtime_safe_supply_resolver.v0"
CONTRACT_SCHEMA_VERSION = (
    "lolla.decision_work_brief_runtime_safe_supply_resolver_contract.v0"
)
DEFAULT_CONTRACT_RELPATH = (
    "docs/conversation-understanding/"
    "decision-work-brief-runtime-safe-supply-resolver-contract-v0.json"
)
REPO_ROOT = Path(__file__).resolve().parents[2]
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
REQUIRED_STRUCTURED_ARTIFACTS = (
    "agent_result.json",
    "evaluation.json",
    "reasoning_trace.json",
    "extraction.json",
    "result.json",
)
REQUIRED_TEXT_ARTIFACTS = ("revised.txt",)
OPTIONAL_REF_FIELDS = {
    "decision_work_brief_json_ref": "brief_json_path",
    "rendered_brief_markdown_ref": "brief_markdown_path",
    "enriched_brief_markdown_ref": "enriched_brief_path",
    "interpretation_read_json_ref": "interpretation_read_path",
    "automatic_triage_packet_json_ref": "triage_packet_path",
    "automatic_triage_read_json_ref": "triage_read_path",
    "eligibility_result_ref": "eligibility_result_path",
    "attachment_status_ref": "attachment_status_path",
}
EXPECTED_SUFFIXES = {
    "decision_work_brief_json_ref": ".json",
    "rendered_brief_markdown_ref": ".md",
    "enriched_brief_markdown_ref": ".md",
    "interpretation_read_json_ref": ".json",
    "automatic_triage_packet_json_ref": ".json",
    "automatic_triage_read_json_ref": ".json",
    "eligibility_result_ref": ".json",
    "attachment_status_ref": ".json",
}
SUPPORTED_SCHEMA_VERSIONS = {
    "decision_work_brief_json_ref": {"lolla.decision_work_brief.v0"},
    "interpretation_read_json_ref": {
        "lolla.decision_work_conversation_interpretation_tiny_offline_read.v0",
        "lolla.decision_work_conversation_interpretation_second_tiny_offline_read.v0",
        "lolla.decision_work_conversation_interpretation_read.v0",
    },
    "automatic_triage_packet_json_ref": {
        "lolla.decision_work_automatic_triage_packets.v0"
    },
    "automatic_triage_read_json_ref": {
        "lolla.decision_work_automatic_triage_provisional_read.v0"
    },
    "eligibility_result_ref": {"lolla.decision_work_brief_runtime_eligibility.v0"},
    "attachment_status_ref": {
        "lolla.decision_work_brief_runtime_attachment_status.v0"
    },
}
BRIEF_INPUTS = {
    "decision_work_brief_json_ref",
    "rendered_brief_markdown_ref",
    "enriched_brief_markdown_ref",
}
SEMANTIC_INPUTS = BRIEF_INPUTS | {
    "interpretation_read_json_ref",
    "automatic_triage_read_json_ref",
}
NON_CLAIMS = (
    "not_customer_readiness",
    "not_product_proof",
    "not_human_validation",
    "not_advice_correctness",
    "not_answer_quality_scoring",
    "not_agent_action_authorization",
    "not_automatic_action_authorization",
    "not_lolla_improvement_proof",
    "not_default_on_runtime_behavior",
    "not_runtime_behavior_change",
    "not_direct_runtime_interpretation",
    "not_raw_private_export",
    "triage_is_routing_not_scoring",
    "resolver_feedability_is_not_advice_quality",
    "resolver_is_not_interpretation",
)


class DecisionWorkBriefSafeSupplyResolverError(ValueError):
    """Sanitized safe-supply resolver input error."""


def resolve_decision_work_brief_safe_supply(
    *,
    run_dir: Path | str,
    contract_path: Path | str = DEFAULT_CONTRACT_RELPATH,
    mode: str = "manual_ref_supply_only",
    case_registry_path: Path | str | None = None,
    case_key: str | None = None,
    brief_json_path: Path | str | None = None,
    brief_markdown_path: Path | str | None = None,
    enriched_brief_path: Path | str | None = None,
    interpretation_read_path: Path | str | None = None,
    triage_packet_path: Path | str | None = None,
    triage_read_path: Path | str | None = None,
    eligibility_result_path: Path | str | None = None,
    attachment_status_path: Path | str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Resolve safe refs and feedability for a runtime bundle."""

    contract = load_resolver_contract(contract_path)
    input_specs = {
        item["input_name"]: item for item in _list_of_mappings(contract["input_types"])
    }
    modes = {item["mode"]: item for item in _list_of_mappings(contract["resolver_modes"])}
    if mode not in modes:
        raise DecisionWorkBriefSafeSupplyResolverError("unsupported resolver mode")

    supplied_paths = {
        "decision_work_brief_json_ref": brief_json_path,
        "rendered_brief_markdown_ref": brief_markdown_path,
        "enriched_brief_markdown_ref": enriched_brief_path,
        "interpretation_read_json_ref": interpretation_read_path,
        "automatic_triage_packet_json_ref": triage_packet_path,
        "automatic_triage_read_json_ref": triage_read_path,
        "eligibility_result_ref": eligibility_result_path,
        "attachment_status_ref": attachment_status_path,
    }
    registry_context: dict[str, Any] | None = None
    if mode == "checked_in_safe_case_registry" and case_registry_path and case_key:
        try:
            registry_kwargs = resolver_kwargs_from_case_registry(
                case_key=case_key,
                registry_path=case_registry_path,
            )
        except DecisionWorkBriefSafeCaseRegistryError as exc:
            raise DecisionWorkBriefSafeSupplyResolverError(str(exc)) from exc
        for input_name, attr_name in OPTIONAL_REF_FIELDS.items():
            if attr_name in registry_kwargs:
                supplied_paths[input_name] = registry_kwargs[attr_name]
        registry_context = {
            "case_registry_ref": _safe_ref(case_registry_path),
            "case_key": _safe_reason(case_key),
            "registry_supplied_inputs": sorted(registry_kwargs),
        }
    run_path = Path(run_dir).expanduser()
    records: list[dict[str, Any]] = []

    if mode == "disabled":
        records = [
            _not_requested_record(input_specs[name], mode=mode)
            for name in input_specs
        ]
        return _resolver_output(
            contract=contract,
            contract_path=contract_path,
            run_path=run_path,
            mode=mode,
            status="not_requested",
            records=records,
            created_at=created_at,
            feeds_runtime_bundle=False,
            reason_if_not_feedable="resolver_disabled",
            registry_context=registry_context,
        )

    run_record = _classify_run_dir(run_path, input_specs["completed_run_dir_ref"], mode)
    records.append(run_record)
    records.append(_source_refs_record(run_path, input_specs["source_refs"], mode, run_record))

    for input_name, attr_name in OPTIONAL_REF_FIELDS.items():
        source_path = supplied_paths[input_name]
        spec = input_specs[input_name]
        if source_path is None:
            records.append(_missing_record(spec, mode=mode))
        else:
            records.append(
                _classify_supplied_ref(
                    input_name=input_name,
                    input_path=source_path,
                    spec=spec,
                    mode=mode,
                    contract=contract,
                    attr_name=attr_name,
                )
            )
    records.append(_not_requested_record(input_specs["user_receipt_ref"], mode=mode))
    records.append(_not_requested_record(input_specs["agent_handoff_ref"], mode=mode))

    status, feeds_runtime_bundle, reason = _resolver_status(
        mode=mode,
        records=records,
    )
    return _resolver_output(
        contract=contract,
        contract_path=contract_path,
        run_path=run_path,
        mode=mode,
        status=status,
        records=records,
        created_at=created_at,
        feeds_runtime_bundle=feeds_runtime_bundle,
        reason_if_not_feedable=reason,
        registry_context=registry_context,
    )


def render_resolver_json(result: Mapping[str, Any], *, pretty: bool = False) -> str:
    """Render resolver output as stable JSON."""

    indent = 2 if pretty else None
    return json.dumps(result, indent=indent, sort_keys=True) + "\n"


def write_resolver_json(
    path: Path | str,
    result: Mapping[str, Any],
    *,
    pretty: bool = False,
) -> None:
    """Write resolver output JSON."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_resolver_json(result, pretty=pretty), encoding="utf-8")


def load_resolver_contract(path: Path | str) -> dict[str, Any]:
    """Load and validate the PR170 resolver contract."""

    payload = _load_json_object(path, description="resolver contract JSON")
    if payload.get("schema_version") != CONTRACT_SCHEMA_VERSION:
        raise DecisionWorkBriefSafeSupplyResolverError(
            "resolver contract schema version was unsupported"
        )
    return payload


def _classify_run_dir(
    run_path: Path,
    spec: Mapping[str, Any],
    mode: str,
) -> dict[str, Any]:
    if mode == "future_direct_runtime_interpretation_not_allowed":
        return _record(
            spec=spec,
            input_ref=_safe_ref(run_path),
            input_status="blocked",
            can_feed_runtime_bundle=False,
            source_mode=mode,
            reason="direct_runtime_interpretation_mode_blocked",
        )
    if not run_path.exists() or not run_path.is_dir():
        return _record(
            spec=spec,
            input_ref=_safe_ref(run_path),
            input_status="blocked",
            can_feed_runtime_bundle=False,
            source_mode=mode,
            reason="completed_run_dir_not_found",
        )
    blockers = _run_artifact_blockers(run_path)
    status = "resolved" if not blockers else "blocked"
    return _record(
        spec=spec,
        input_ref=_run_ref(run_path),
        input_status=status,
        can_feed_runtime_bundle=not blockers,
        source_mode="archive_local_safe_resolver",
        reason="completed_run_dir_resolved" if not blockers else ";".join(blockers[:3]),
        extra={
            "run_artifact_status": "complete_parseable" if not blockers else "blocked",
            "hard_blockers": blockers,
        },
    )


def _source_refs_record(
    run_path: Path,
    spec: Mapping[str, Any],
    mode: str,
    run_record: Mapping[str, Any],
) -> dict[str, Any]:
    if run_record["input_status"] == "resolved":
        return _record(
            spec=spec,
            input_ref=_run_ref(run_path),
            input_status="resolved",
            can_feed_runtime_bundle=True,
            source_mode="archive_local_safe_resolver",
            reason="relative_source_refs_available",
        )
    return _record(
        spec=spec,
        input_ref=None,
        input_status="blocked",
        can_feed_runtime_bundle=False,
        source_mode=mode,
        reason="source_refs_unavailable_until_run_dir_resolves",
    )


def _classify_supplied_ref(
    *,
    input_name: str,
    input_path: Path | str,
    spec: Mapping[str, Any],
    mode: str,
    contract: Mapping[str, Any],
    attr_name: str,
) -> dict[str, Any]:
    if mode == "future_direct_runtime_interpretation_not_allowed":
        return _record(
            spec=spec,
            input_ref=None,
            input_status="blocked",
            can_feed_runtime_bundle=False,
            source_mode=mode,
            reason="direct_runtime_interpretation_mode_blocked",
            extra={"source_argument": attr_name},
        )

    if mode not in set(_string_list(spec.get("allowed_source_modes"))):
        return _record(
            spec=spec,
            input_ref=_safe_ref(input_path),
            input_status="blocked",
            can_feed_runtime_bundle=False,
            source_mode=mode,
            reason="resolver_mode_not_allowed_for_input",
            extra={"source_argument": attr_name},
        )

    source = Path(input_path).expanduser()
    if mode == "checked_in_safe_case_registry" and not _is_under_repo(source):
        return _record(
            spec=spec,
            input_ref=source.name,
            input_status="blocked",
            can_feed_runtime_bundle=False,
            source_mode=mode,
            reason="checked_in_safe_registry_requires_repo_relative_ref",
            extra={"source_argument": attr_name},
        )
    if not source.exists() or not source.is_file():
        return _record(
            spec=spec,
            input_ref=_safe_ref(source),
            input_status="blocked",
            can_feed_runtime_bundle=False,
            source_mode=mode,
            reason="supplied_ref_missing",
            extra={"source_argument": attr_name},
        )
    expected_suffix = EXPECTED_SUFFIXES[input_name]
    if source.suffix != expected_suffix:
        return _record(
            spec=spec,
            input_ref=_safe_ref(source),
            input_status="blocked",
            can_feed_runtime_bundle=False,
            source_mode=mode,
            reason="unsupported_source_suffix",
            extra={"source_argument": attr_name},
        )
    try:
        text = source.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return _record(
            spec=spec,
            input_ref=_safe_ref(source),
            input_status="blocked",
            can_feed_runtime_bundle=False,
            source_mode=mode,
            reason="supplied_ref_unreadable",
            extra={"source_argument": attr_name},
        )
    if _contains_private_marker(text):
        return _record(
            spec=spec,
            input_ref=_safe_ref(source),
            input_status="unsafe",
            can_feed_runtime_bundle=False,
            source_mode=mode,
            reason="privacy_marker_or_raw_private_export_risk",
            extra={"source_argument": attr_name},
        )
    schema_check = _schema_check(
        input_name=input_name,
        source=source,
        text=text,
        contract=contract,
    )
    if schema_check is not None:
        return _record(
            spec=spec,
            input_ref=_safe_ref(source),
            input_status="blocked",
            can_feed_runtime_bundle=False,
            source_mode=mode,
            reason=schema_check,
            extra={"source_argument": attr_name},
        )
    return _record(
        spec=spec,
        input_ref=_safe_ref(source),
        input_status="resolved",
        can_feed_runtime_bundle=True,
        source_mode=mode,
        reason="supplied_ref_resolved",
        extra={
            "source_argument": attr_name,
            "input_ref_kind": _ref_kind(source),
        },
    )


def _schema_check(
    *,
    input_name: str,
    source: Path,
    text: str,
    contract: Mapping[str, Any],
) -> str | None:
    if source.suffix != ".json":
        return None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return "json_ref_malformed"
    if not isinstance(payload, dict):
        return "json_ref_root_not_object"
    expected = SUPPORTED_SCHEMA_VERSIONS.get(input_name)
    if expected is None:
        return None
    schema = payload.get("schema_version")
    if not isinstance(schema, str):
        return "json_ref_schema_version_missing"
    if schema not in expected and schema != contract.get("schema_version"):
        return "json_ref_schema_version_unsupported"
    return None


def _missing_record(spec: Mapping[str, Any], *, mode: str) -> dict[str, Any]:
    input_name = _text(spec.get("input_name"), "unknown")
    if input_name in {"eligibility_result_ref", "attachment_status_ref"}:
        status = "missing"
        reason = "optional_status_ref_not_supplied"
    elif input_name == "automatic_triage_packet_json_ref":
        status = "missing"
        reason = "metadata_triage_packet_not_supplied"
    else:
        status = "deferred" if spec.get("requires_llm_interpretation") is True else "missing"
        reason = _text(spec.get("absence_status"), "not_supplied")
    return _record(
        spec=spec,
        input_ref=None,
        input_status=status,
        can_feed_runtime_bundle=False,
        source_mode=mode,
        reason=reason,
    )


def _not_requested_record(spec: Mapping[str, Any], *, mode: str) -> dict[str, Any]:
    return _record(
        spec=spec,
        input_ref=None,
        input_status="not_requested",
        can_feed_runtime_bundle=False,
        source_mode=mode,
        reason="not_requested_by_resolver",
    )


def _record(
    *,
    spec: Mapping[str, Any],
    input_ref: str | Path | None,
    input_status: str,
    can_feed_runtime_bundle: bool,
    source_mode: str,
    reason: str,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    record = {
        "input_name": _text(spec.get("input_name"), "unknown"),
        "input_ref": _safe_ref(input_ref),
        "input_status": input_status,
        "can_feed_runtime_bundle": can_feed_runtime_bundle,
        "can_feed_user_receipt": bool(spec.get("required_for_user_receipt")),
        "can_feed_agent_handoff": bool(spec.get("required_for_agent_handoff")),
        "source_mode": source_mode,
        "safe_default_policy": _text(spec.get("safe_default_policy"), "not specified"),
        "privacy_risk": _text(spec.get("privacy_risk"), "unknown"),
        "requires_llm_interpretation": spec.get("requires_llm_interpretation") is True,
        "requires_local_private_context": (
            source_mode == "local_private_operator_mode"
            or "local_private" in _text(spec.get("local_private_policy"), "").lower()
        ),
        "reason": _safe_reason(reason),
    }
    if extra:
        record.update(dict(extra))
    return record


def _resolver_status(
    *,
    mode: str,
    records: list[dict[str, Any]],
) -> tuple[str, bool, str | None]:
    if mode == "future_direct_runtime_interpretation_not_allowed":
        return (
            "blocked_direct_runtime_interpretation",
            False,
            "direct_runtime_interpretation_blocked_by_contract",
        )
    if mode == "offline_interpretation_queue":
        return (
            "queued_for_offline_interpretation",
            False,
            "semantic_inputs_require_offline_interpretation_queue",
        )
    if mode == "local_private_operator_mode":
        return (
            "local_private_operator_required",
            False,
            "local_private_operator_mode_cannot_feed_default_runtime_bundle",
        )

    blocked_status = _top_blocked_status(records)
    if blocked_status is not None:
        return blocked_status, False, blocked_status

    brief_resolved = any(
        record["input_name"] in BRIEF_INPUTS and record["input_status"] == "resolved"
        for record in records
    )
    triage_read_resolved = any(
        record["input_name"] == "automatic_triage_read_json_ref"
        and record["input_status"] == "resolved"
        for record in records
    )
    semantic_resolved = any(
        record["input_name"] in SEMANTIC_INPUTS
        and record["input_status"] == "resolved"
        for record in records
    )
    if brief_resolved and triage_read_resolved:
        return "resolved", True, None
    if brief_resolved:
        return "partially_resolved", True, None
    if semantic_resolved and not brief_resolved:
        return "deferred_missing_brief", False, "safe_brief_ref_not_supplied"
    return "no_safe_inputs", False, "no_safe_semantic_inputs_supplied"


def _top_blocked_status(records: list[dict[str, Any]]) -> str | None:
    reasons = [record["reason"] for record in records if record["input_status"] in {"blocked", "unsafe"}]
    if not reasons:
        return None
    if any("privacy_marker_or_raw_private_export_risk" in reason for reason in reasons):
        return "blocked_privacy_risk"
    if any("schema" in reason or "json_ref" in reason for reason in reasons):
        return "blocked_schema_invalid"
    if any("unsafe_path" in reason or "requires_repo_relative" in reason for reason in reasons):
        return "blocked_unsafe_path"
    return "blocked_untrusted_source"


def _resolver_output(
    *,
    contract: Mapping[str, Any],
    contract_path: Path | str,
    run_path: Path,
    mode: str,
    status: str,
    records: list[dict[str, Any]],
    created_at: str | None,
    feeds_runtime_bundle: bool,
    reason_if_not_feedable: str | None,
    registry_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    resolved = [record for record in records if record["input_status"] == "resolved"]
    deferred = [record for record in records if record["input_status"] in {"deferred", "missing"}]
    blocked = [
        record for record in records if record["input_status"] in {"blocked", "unsafe"}
    ]
    output = {
        "schema_version": RESOLVER_SCHEMA_VERSION,
        "contract_ref": _safe_ref(contract_path),
        "resolver_metadata": {
            "created_at": created_at or _utc_now(),
            "builder": "engine.system_b.decision_work_brief_safe_supply_resolver",
            "deterministic_only": True,
            "contract_schema_version": contract.get("schema_version"),
            "runtime_behavior_changed": False,
            "resolver_mode_supported": True,
        },
        "source_run_ref": _run_ref(run_path),
        "resolver_mode": mode,
        "resolver_status": status,
        "selected_supply_strategy": mode,
        "input_classification": records,
        "resolved_inputs": resolved,
        "deferred_inputs": deferred,
        "blocked_inputs": blocked,
        "unsafe_inputs_excluded": _unsafe_inputs_excluded(contract),
        "queue_handoff": _queue_handoff(mode=mode, status=status),
        "manual_operator_requirements": _manual_operator_requirements(records),
        "privacy_policy": dict(_mapping(contract.get("privacy_policy"))),
        "custody_flags": _custody_flags(),
        "non_claims": list(NON_CLAIMS),
        "feeds_runtime_bundle": feeds_runtime_bundle,
        "reason_if_not_feedable": reason_if_not_feedable,
    }
    if registry_context is not None:
        output["case_registry"] = dict(registry_context)
    return output


def _unsafe_inputs_excluded(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    blocked_inputs = _list_of_mappings(contract.get("blocked_inputs"))
    return [
        {
            "input_name": _text(item.get("input_name"), "unknown"),
            "excluded": item.get("must_never_auto_supply") is True,
            "reason": "blocked_by_safe_supply_resolver_contract",
        }
        for item in blocked_inputs
    ]


def _queue_handoff(*, mode: str, status: str) -> dict[str, Any]:
    queued = status == "queued_for_offline_interpretation"
    return {
        "queued": queued,
        "queue_status": status if queued else "not_queued",
        "reason": (
            "offline_interpretation_required"
            if queued
            else "queue_not_requested_by_resolver"
        ),
    }


def _manual_operator_requirements(records: list[dict[str, Any]]) -> list[str]:
    requirements: list[str] = []
    resolved_names = {
        record["input_name"] for record in records if record["input_status"] == "resolved"
    }
    if not (BRIEF_INPUTS & resolved_names):
        requirements.append("supply_safe_rendered_or_enriched_brief_ref")
    if "automatic_triage_read_json_ref" not in resolved_names:
        requirements.append("supply_safe_triage_read_ref_or_accept_agent_only")
    if "interpretation_read_json_ref" not in resolved_names:
        requirements.append("supply_safe_interpretation_read_ref_for_enrichment")
    return requirements


def _custody_flags() -> dict[str, Any]:
    return {
        "human_validated": False,
        "human_review_completed": False,
        "product_proof": False,
        "model_calls": 0,
        "runtime_invoked": False,
        "runtime_behavior_changed": False,
        "skill_invoked": False,
        "archive_mutated": False,
        "prompt_changed": False,
        "skill_files_changed": False,
        "answer_quality_scored": False,
        "agent_action_authorized": False,
        "automatic_action_authorized": False,
        "raw_private_content_included": False,
        "provider_text_included": False,
        "local_absolute_paths_included": False,
    }


def _run_artifact_blockers(run_path: Path) -> list[str]:
    blockers: list[str] = []
    for name in REQUIRED_STRUCTURED_ARTIFACTS:
        path = run_path / name
        if not path.exists():
            blockers.append(f"missing_required_structured_artifact:{name}")
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            blockers.append(f"malformed_json:{name}")
        except (OSError, UnicodeDecodeError):
            blockers.append(f"unreadable_required_artifact:{name}")
    for name in REQUIRED_TEXT_ARTIFACTS:
        path = run_path / name
        if not path.exists():
            blockers.append(f"missing_required_text_artifact:{name}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            blockers.append(f"unreadable_required_artifact:{name}")
            continue
        if _contains_private_marker(text):
            blockers.append(f"privacy_marker_or_raw_private_export_risk:{name}")
    return blockers


def _load_json_object(path: Path | str, *, description: str) -> dict[str, Any]:
    input_path = Path(path).expanduser()
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DecisionWorkBriefSafeSupplyResolverError(
            f"{description} was not found"
        ) from exc
    except json.JSONDecodeError as exc:
        raise DecisionWorkBriefSafeSupplyResolverError(
            f"{description} was malformed"
        ) from exc
    except UnicodeDecodeError as exc:
        raise DecisionWorkBriefSafeSupplyResolverError(
            f"{description} was not valid UTF-8"
        ) from exc
    if not isinstance(payload, dict):
        raise DecisionWorkBriefSafeSupplyResolverError(
            f"{description} root was not an object"
        )
    return payload


def _contains_private_marker(text: str) -> bool:
    return any(marker in text for marker in RAW_PRIVATE_MARKERS)


def _safe_ref(path: Path | str | None) -> str | None:
    if path is None:
        return None
    candidate = Path(path).expanduser()
    try:
        resolved = candidate.resolve(strict=False)
        return str(resolved.relative_to(REPO_ROOT))
    except ValueError:
        return candidate.name


def _ref_kind(path: Path) -> str:
    return "repo_relative" if _is_under_repo(path) else "local_ref_redacted"


def _is_under_repo(path: Path) -> bool:
    try:
        path.expanduser().resolve(strict=False).relative_to(REPO_ROOT)
    except ValueError:
        return False
    return True


def _run_ref(run_path: Path) -> str:
    parts = [part for part in run_path.parts if part]
    if len(parts) >= 2:
        return f"{_safe_slug(parts[-2])}/{_safe_slug(parts[-1])}"
    return _safe_slug(run_path.name)


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.=-]+", "-", value).strip("-")
    return slug or "unknown"


def _safe_reason(value: str) -> str:
    reason = _text(value, "not specified")
    if _contains_private_marker(reason):
        return "private_marker_redacted"
    return reason


def _utc_now() -> str:
    return _dt.datetime.now(tz=_dt.UTC).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list_of_mappings(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _text(value: Any, fallback: str = "") -> str:
    return value if isinstance(value, str) and value else fallback
