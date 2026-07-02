"""Manual post-archive Decision Work Brief runtime bundle builder.

This module creates a checked-in-safe attachment bundle for a completed Lolla
run directory. It is deterministic and offline: it validates source artifact
presence, copies only explicitly provided safe brief/triage artifacts, writes a
status sidecar, and renders a short receipt. It does not run Lolla, call
models, mutate the input archive, infer a new Decision Work Brief, score
advice, or authorize action.
"""
from __future__ import annotations

import datetime as _dt
import json
import re
import shutil
from collections.abc import Mapping
from pathlib import Path
from typing import Any


ATTACHMENT_STATUS_SCHEMA_VERSION = (
    "lolla.decision_work_brief_runtime_attachment_status.v0"
)
ATTACHMENT_CONTRACT_SCHEMA_VERSION = (
    "lolla.decision_work_brief_runtime_attachment_contract.v0"
)
SIDECAR_CONTRACT_SCHEMA_VERSION = "lolla.decision_work_brief_runtime_sidecar.v0"
SAFE_SUPPLY_RESOLVER_SCHEMA_VERSION = (
    "lolla.decision_work_brief_runtime_safe_supply_resolver.v0"
)
DEFAULT_ATTACHMENT_CONTRACT_RELPATH = (
    "docs/conversation-understanding/"
    "decision-work-brief-runtime-attachment-contract-v0.json"
)
DEFAULT_SIDECAR_CONTRACT_RELPATH = (
    "docs/conversation-understanding/decision-work-brief-runtime-sidecar-v0.json"
)
REPO_ROOT = Path(__file__).resolve().parents[2]
SIDECAR_ROOT = "decision_work"
REQUIRED_STRUCTURED_ARTIFACTS = (
    "agent_result.json",
    "evaluation.json",
    "reasoning_trace.json",
    "extraction.json",
    "result.json",
)
REQUIRED_TEXT_ARTIFACTS = ("revised.txt",)
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
RESOLVER_INPUT_TO_BUNDLE = {
    "decision_work_brief_json_ref": {
        "kwarg": "brief_json_path",
        "artifact_id": "decision_work_brief_json",
        "filename": "decision_work_brief.json",
        "suffix": ".json",
    },
    "rendered_brief_markdown_ref": {
        "kwarg": "brief_markdown_path",
        "artifact_id": "decision_work_brief_markdown",
        "filename": "decision_work_brief.md",
        "suffix": ".md",
    },
    "enriched_brief_markdown_ref": {
        "kwarg": "enriched_brief_path",
        "artifact_id": "decision_work_brief_enriched_markdown",
        "filename": "decision_work_brief_enriched.md",
        "suffix": ".md",
    },
    "automatic_triage_packet_json_ref": {
        "kwarg": "triage_packet_path",
        "artifact_id": "automatic_triage_packet",
        "filename": "automatic_triage_packet.json",
        "suffix": ".json",
    },
    "automatic_triage_read_json_ref": {
        "kwarg": "triage_read_path",
        "artifact_id": "automatic_triage_read",
        "filename": "automatic_triage_read.json",
        "suffix": ".json",
    },
}
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
    "not_raw_private_export",
    "triage_is_routing_not_scoring",
    "clean_artifacts_do_not_imply_good_advice",
)


class DecisionWorkBriefRuntimeBundleInputError(ValueError):
    """Sanitized manual runtime-bundle input error."""


def build_decision_work_brief_runtime_bundle(
    *,
    run_dir: Path | str,
    output_dir: Path | str,
    attachment_contract_path: Path | str = DEFAULT_ATTACHMENT_CONTRACT_RELPATH,
    sidecar_contract_path: Path | str = DEFAULT_SIDECAR_CONTRACT_RELPATH,
    resolver_output_path: Path | str | None = None,
    brief_json_path: Path | str | None = None,
    brief_markdown_path: Path | str | None = None,
    enriched_brief_path: Path | str | None = None,
    triage_packet_path: Path | str | None = None,
    triage_read_path: Path | str | None = None,
    created_at: str | None = None,
    allow_archive_sidecar: bool = False,
) -> dict[str, Any]:
    """Build a manual post-archive attachment bundle outside the input archive."""

    run_path = _validated_run_dir(run_dir)
    output_path = validate_output_dir(
        output_dir=output_dir,
        run_dir=run_path,
        allow_archive_sidecar=allow_archive_sidecar,
    )
    attachment_contract = _load_json_object(attachment_contract_path)
    sidecar_contract = _load_json_object(sidecar_contract_path)
    _validate_contracts(
        attachment_contract=attachment_contract,
        sidecar_contract=sidecar_contract,
    )

    sidecar_dir = output_path / SIDECAR_ROOT
    sidecar_dir.mkdir(parents=True, exist_ok=True)

    artifact_status = _inspect_run_artifacts(run_path)
    hard_blockers = list(artifact_status["hard_blockers"])
    generated_artifacts: dict[str, str] = {}
    missing_artifacts = _initial_missing_artifacts()
    deferred_reasons: list[str] = []
    failed_closed_reasons: list[str] = []
    resolver_summary: dict[str, Any] | None = None
    resolver_source_paths: dict[str, Path] = {}

    if resolver_output_path is not None:
        resolver_result, resolver_source_paths, resolver_blockers, resolver_deferred = (
            _load_and_apply_resolver_output(
                resolver_output_path=resolver_output_path,
                sidecar_dir=sidecar_dir,
                generated_artifacts=generated_artifacts,
                missing_artifacts=missing_artifacts,
            )
        )
        resolver_summary = _resolver_summary(
            resolver_result=resolver_result,
            resolver_output_ref=generated_artifacts.get("safe_supply_resolver"),
        )
        hard_blockers.extend(resolver_blockers)
        deferred_reasons.extend(resolver_deferred)

    if not hard_blockers:
        if resolver_output_path is not None:
            brief_json_path = resolver_source_paths.get("brief_json_path")
            brief_markdown_path = resolver_source_paths.get("brief_markdown_path")
            enriched_brief_path = resolver_source_paths.get("enriched_brief_path")
            triage_packet_path = resolver_source_paths.get("triage_packet_path")
            triage_read_path = resolver_source_paths.get("triage_read_path")
        _copy_optional_artifact(
            source_path=brief_json_path,
            destination=sidecar_dir / "decision_work_brief.json",
            artifact_id="decision_work_brief_json",
            generated_artifacts=generated_artifacts,
            missing_artifacts=missing_artifacts,
            expected_suffix=".json",
        )
        _copy_optional_artifact(
            source_path=brief_markdown_path,
            destination=sidecar_dir / "decision_work_brief.md",
            artifact_id="decision_work_brief_markdown",
            generated_artifacts=generated_artifacts,
            missing_artifacts=missing_artifacts,
            expected_suffix=".md",
        )
        _copy_optional_artifact(
            source_path=enriched_brief_path,
            destination=sidecar_dir / "decision_work_brief_enriched.md",
            artifact_id="decision_work_brief_enriched_markdown",
            generated_artifacts=generated_artifacts,
            missing_artifacts=missing_artifacts,
            expected_suffix=".md",
        )
        _copy_optional_artifact(
            source_path=triage_packet_path,
            destination=sidecar_dir / "automatic_triage_packet.json",
            artifact_id="automatic_triage_packet",
            generated_artifacts=generated_artifacts,
            missing_artifacts=missing_artifacts,
            expected_suffix=".json",
        )
        _copy_optional_artifact(
            source_path=triage_read_path,
            destination=sidecar_dir / "automatic_triage_read.json",
            artifact_id="automatic_triage_read",
            generated_artifacts=generated_artifacts,
            missing_artifacts=missing_artifacts,
            expected_suffix=".json",
        )
        if "decision_work_brief_markdown" not in generated_artifacts:
            deferred_reasons.append("safe_rendered_brief_not_supplied")
        if "automatic_triage_read" not in generated_artifacts:
            deferred_reasons.append("runtime_specific_triage_read_not_supplied")

    attachment_state = _attachment_state(
        hard_blockers=hard_blockers,
        generated_artifacts=generated_artifacts,
        deferred_reasons=deferred_reasons,
        failed_closed_reasons=failed_closed_reasons,
    )
    status = _attachment_status(
        run_path=run_path,
        output_path=output_path,
        created_at=created_at,
        attachment_state=attachment_state,
        artifact_status=artifact_status,
        generated_artifacts=generated_artifacts,
        missing_artifacts=missing_artifacts,
        blocked_reasons=hard_blockers,
        deferred_reasons=deferred_reasons,
        failed_closed_reasons=failed_closed_reasons,
        attachment_contract_path=attachment_contract_path,
        sidecar_contract_path=sidecar_contract_path,
        sidecar_written_inside_archive=allow_archive_sidecar
        and output_path == run_path.resolve(strict=False),
        source_inputs={
            "resolver_output_ref": _safe_input_ref(resolver_output_path),
            "brief_json_ref": _safe_input_ref(brief_json_path),
            "brief_markdown_ref": _safe_input_ref(brief_markdown_path),
            "enriched_brief_ref": _safe_input_ref(enriched_brief_path),
            "triage_packet_ref": _safe_input_ref(triage_packet_path),
            "triage_read_ref": _safe_input_ref(triage_read_path),
        },
        resolver_summary=resolver_summary,
    )
    status_path = sidecar_dir / "attachment_status.json"
    _write_json(status_path, status)
    generated_artifacts["attachment_status"] = f"{SIDECAR_ROOT}/attachment_status.json"
    missing_artifacts.pop("attachment_status", None)

    receipt = render_runtime_bundle_receipt(status)
    receipt_path = sidecar_dir / "user_receipt.md"
    receipt_path.write_text(receipt, encoding="utf-8")
    status["generated_artifacts"]["user_receipt"] = f"{SIDECAR_ROOT}/user_receipt.md"
    status["missing_artifacts"].pop("user_receipt", None)
    _write_json(status_path, status)

    return status


def render_attachment_status_json(status: Mapping[str, Any], *, pretty: bool = False) -> str:
    """Render an attachment status object as JSON."""

    indent = 2 if pretty else None
    return json.dumps(status, indent=indent, sort_keys=True) + "\n"


def render_runtime_bundle_receipt(status: Mapping[str, Any]) -> str:
    """Render the PR162 placeholder receipt from attachment status."""

    state = _text(status.get("attachment_state"), "unknown")
    generated = _mapping(status.get("generated_artifacts"))
    blocked = _list(status.get("blocked_reasons"))
    deferred = _list(status.get("deferred_reasons"))
    full_ref = generated.get("decision_work_brief_enriched_markdown") or generated.get(
        "decision_work_brief_markdown"
    )

    if state == "generated":
        status_line = "Decision Work Brief: available"
        changed_line = "What changed: see the attached brief."
    elif state == "generated_agent_only":
        status_line = "Decision Work Brief: available for agent inspection"
        changed_line = "What changed: see the attached evidence bundle."
    elif state == "deferred":
        status_line = "Decision Work Brief: deferred"
        changed_line = f"Reason: {_join_reasons(deferred)}."
    elif state == "blocked":
        status_line = "Decision Work Brief: blocked"
        changed_line = f"Reason: {_join_reasons(blocked)}."
    else:
        status_line = "Decision Work Brief: failed closed"
        changed_line = "Reason: the attachment bundle could not be safely generated."

    lines = [
        status_line,
        "",
        changed_line,
        "",
        "Main caveat: this is an audit summary, not proof that the advice is correct.",
    ]
    if full_ref:
        lines.extend(["", f"Open full brief: `{full_ref}`"])
    evidence_ref = generated.get("attachment_status")
    if evidence_ref:
        lines.extend(["", f"Open evidence status: `{evidence_ref}`"])
    return "\n".join(lines).rstrip() + "\n"


def validate_output_dir(
    *,
    output_dir: Path | str,
    run_dir: Path | str,
    allow_archive_sidecar: bool = False,
) -> Path:
    """Validate the manual bundle output directory."""

    output = Path(output_dir).expanduser().resolve(strict=False)
    run_path = Path(run_dir).expanduser().resolve(strict=False)
    if allow_archive_sidecar and output == run_path:
        return output
    if output == run_path or run_path in output.parents:
        raise DecisionWorkBriefRuntimeBundleInputError(
            "manual bundle output must be outside the input run directory"
        )
    if output.exists() and not output.is_dir():
        raise DecisionWorkBriefRuntimeBundleInputError("output path is not a directory")
    return output


def _validated_run_dir(run_dir: Path | str) -> Path:
    run_path = Path(run_dir).expanduser()
    if not run_path.exists():
        raise DecisionWorkBriefRuntimeBundleInputError("run directory was not found")
    if not run_path.is_dir():
        raise DecisionWorkBriefRuntimeBundleInputError("run path is not a directory")
    return run_path


def _validate_contracts(
    *,
    attachment_contract: Mapping[str, Any],
    sidecar_contract: Mapping[str, Any],
) -> None:
    if attachment_contract.get("schema_version") != ATTACHMENT_CONTRACT_SCHEMA_VERSION:
        raise DecisionWorkBriefRuntimeBundleInputError(
            "runtime attachment contract schema version was unsupported"
        )
    if sidecar_contract.get("schema_version") != SIDECAR_CONTRACT_SCHEMA_VERSION:
        raise DecisionWorkBriefRuntimeBundleInputError(
            "runtime sidecar contract schema version was unsupported"
        )
    if attachment_contract.get("default_off_requirement", {}).get("required") is not True:
        raise DecisionWorkBriefRuntimeBundleInputError(
            "runtime attachment contract was not default-off"
        )
    if sidecar_contract.get("manual_output_policy", {}).get(
        "must_refuse_output_inside_input_run_by_default"
    ) is not True:
        raise DecisionWorkBriefRuntimeBundleInputError(
            "runtime sidecar contract output policy was unsafe"
        )


def _inspect_run_artifacts(run_path: Path) -> dict[str, Any]:
    artifacts: dict[str, dict[str, Any]] = {}
    hard_blockers: list[str] = []
    for artifact in REQUIRED_STRUCTURED_ARTIFACTS:
        path = run_path / artifact
        if not path.exists():
            artifacts[artifact] = {"status": "missing"}
            hard_blockers.append(f"missing_required_structured_artifact:{artifact}")
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            artifacts[artifact] = {"status": "malformed"}
            hard_blockers.append(f"malformed_json:{artifact}")
        except OSError:
            artifacts[artifact] = {"status": "unreadable"}
            hard_blockers.append(f"unreadable_required_artifact:{artifact}")
        else:
            artifacts[artifact] = {"status": "present_parseable"}

    for artifact in REQUIRED_TEXT_ARTIFACTS:
        path = run_path / artifact
        if not path.exists():
            artifacts[artifact] = {"status": "missing"}
            hard_blockers.append(f"missing_required_text_artifact:{artifact}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            artifacts[artifact] = {"status": "unreadable"}
            hard_blockers.append(f"unreadable_required_artifact:{artifact}")
            continue
        if any(marker in text for marker in RAW_PRIVATE_MARKERS):
            artifacts[artifact] = {"status": "privacy_marker_detected"}
            hard_blockers.append(f"privacy_marker_or_raw_private_export_risk:{artifact}")
        else:
            artifacts[artifact] = {"status": "present_not_exported"}

    return {
        "source_run_ref": _run_ref(run_path),
        "required_artifacts": artifacts,
        "hard_blockers": hard_blockers,
        "archive_finalized": not hard_blockers,
    }


def _copy_optional_artifact(
    *,
    source_path: Path | str | None,
    destination: Path,
    artifact_id: str,
    generated_artifacts: dict[str, str],
    missing_artifacts: dict[str, str],
    expected_suffix: str,
) -> None:
    if source_path is None:
        return
    source = Path(source_path).expanduser()
    if not source.exists() or not source.is_file():
        missing_artifacts[artifact_id] = "source_not_found"
        return
    if source.suffix != expected_suffix:
        missing_artifacts[artifact_id] = "unsupported_source_suffix"
        return
    text = source.read_text(encoding="utf-8")
    if any(marker in text for marker in RAW_PRIVATE_MARKERS):
        missing_artifacts[artifact_id] = "privacy_marker_or_raw_private_export_risk"
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    generated_artifacts[artifact_id] = f"{SIDECAR_ROOT}/{destination.name}"
    missing_artifacts.pop(artifact_id, None)


def _load_and_apply_resolver_output(
    *,
    resolver_output_path: Path | str,
    sidecar_dir: Path,
    generated_artifacts: dict[str, str],
    missing_artifacts: dict[str, str],
) -> tuple[dict[str, Any], dict[str, Path], list[str], list[str]]:
    resolver_result = _load_json_object(
        resolver_output_path,
        description="resolver output JSON",
    )
    blockers: list[str] = []
    deferred: list[str] = []
    source_paths: dict[str, Path] = {}
    if resolver_result.get("schema_version") != SAFE_SUPPLY_RESOLVER_SCHEMA_VERSION:
        resolver_result = _minimal_invalid_resolver_result(
            resolver_result=resolver_result,
            reason="resolver_schema_version_unsupported",
        )
        blockers.append("resolver:blocked_schema_invalid")
        return resolver_result, source_paths, blockers, deferred
    rendered = json.dumps(resolver_result, sort_keys=True)
    if any(marker in rendered for marker in RAW_PRIVATE_MARKERS):
        resolver_result = _minimal_invalid_resolver_result(
            resolver_result=resolver_result,
            reason="resolver_output_privacy_marker_detected",
        )
        blockers.append("resolver:blocked_privacy_risk")
        return resolver_result, source_paths, blockers, deferred

    _copy_resolver_output(
        resolver_output_path=resolver_output_path,
        sidecar_dir=sidecar_dir,
        generated_artifacts=generated_artifacts,
        missing_artifacts=missing_artifacts,
    )
    resolver_status = _text(resolver_result.get("resolver_status"), "unknown")
    feeds_runtime_bundle = resolver_result.get("feeds_runtime_bundle") is True
    if resolver_status.startswith("blocked_"):
        blockers.append(f"resolver:{resolver_status}")
    elif not feeds_runtime_bundle:
        deferred.append(f"resolver:{resolver_status}")
        reason = _text(resolver_result.get("reason_if_not_feedable"))
        if reason:
            deferred.append(f"resolver_reason:{reason}")

    if feeds_runtime_bundle:
        source_paths, path_blockers = _resolver_source_paths(
            resolver_result=resolver_result,
            resolver_output_path=resolver_output_path,
        )
        blockers.extend(path_blockers)
    return resolver_result, source_paths, blockers, deferred


def _copy_resolver_output(
    *,
    resolver_output_path: Path | str,
    sidecar_dir: Path,
    generated_artifacts: dict[str, str],
    missing_artifacts: dict[str, str],
) -> None:
    source = Path(resolver_output_path).expanduser()
    destination = sidecar_dir / "safe_supply_resolver.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    generated_artifacts["safe_supply_resolver"] = f"{SIDECAR_ROOT}/{destination.name}"
    missing_artifacts.pop("safe_supply_resolver", None)


def _resolver_source_paths(
    *,
    resolver_result: Mapping[str, Any],
    resolver_output_path: Path | str,
) -> tuple[dict[str, Path], list[str]]:
    records = _list_of_mappings(resolver_result.get("resolved_inputs"))
    resolver_dir = Path(resolver_output_path).expanduser().resolve(strict=False).parent
    source_paths: dict[str, Path] = {}
    blockers: list[str] = []
    for record in records:
        input_name = _text(record.get("input_name"))
        mapping = RESOLVER_INPUT_TO_BUNDLE.get(input_name)
        if mapping is None:
            continue
        ref = _text(record.get("input_ref"))
        if not ref:
            blockers.append(f"resolver_missing_ref:{input_name}")
            continue
        source_path, blocker = _resolver_ref_to_source(
            ref=ref,
            resolver_dir=resolver_dir,
            expected_suffix=mapping["suffix"],
        )
        if blocker:
            blockers.append(f"{blocker}:{input_name}")
            continue
        source_paths[mapping["kwarg"]] = source_path
    return source_paths, blockers


def _resolver_ref_to_source(
    *,
    ref: str,
    resolver_dir: Path,
    expected_suffix: str,
) -> tuple[Path, str | None]:
    if any(marker in ref for marker in RAW_PRIVATE_MARKERS):
        return Path(ref), "resolver_ref_privacy_marker_detected"
    candidate = Path(ref)
    if candidate.is_absolute() or ".." in candidate.parts:
        return candidate, "resolver_ref_unsafe_path"
    repo_candidate = (REPO_ROOT / candidate).resolve(strict=False)
    local_candidate = (resolver_dir / candidate).resolve(strict=False)
    if repo_candidate.exists():
        source = repo_candidate
    elif local_candidate.exists():
        source = local_candidate
    else:
        return candidate, "resolver_ref_source_not_found"
    if source.suffix != expected_suffix:
        return source, "resolver_ref_suffix_mismatch"
    return source, None


def _minimal_invalid_resolver_result(
    *,
    resolver_result: Mapping[str, Any],
    reason: str,
) -> dict[str, Any]:
    return {
        "schema_version": _text(resolver_result.get("schema_version"), "invalid"),
        "resolver_mode": _text(resolver_result.get("resolver_mode"), "unknown"),
        "resolver_status": (
            "blocked_privacy_risk"
            if "privacy" in reason
            else "blocked_schema_invalid"
        ),
        "feeds_runtime_bundle": False,
        "reason_if_not_feedable": reason,
        "resolved_inputs": [],
        "deferred_inputs": [],
        "blocked_inputs": [
            {
                "input_name": "resolver_output",
                "reason": reason,
            }
        ],
        "unsafe_inputs_excluded": [],
        "queue_handoff": {"queued": False, "queue_status": "not_queued"},
        "manual_operator_requirements": ["supply_valid_resolver_output"],
        "non_claims": list(NON_CLAIMS),
    }


def _resolver_summary(
    *,
    resolver_result: Mapping[str, Any],
    resolver_output_ref: str | None,
) -> dict[str, Any]:
    return {
        "resolver_output_ref": resolver_output_ref,
        "schema_version": _safe_text(
            _text(resolver_result.get("schema_version"), "unknown")
        ),
        "resolver_mode": _safe_text(
            _text(resolver_result.get("resolver_mode"), "unknown")
        ),
        "resolver_status": _safe_text(
            _text(resolver_result.get("resolver_status"), "unknown")
        ),
        "feeds_runtime_bundle": resolver_result.get("feeds_runtime_bundle") is True,
        "reason_if_not_feedable": _safe_optional_text(
            resolver_result.get("reason_if_not_feedable")
        ),
        "resolved_inputs": _resolver_input_summaries(
            resolver_result.get("resolved_inputs"),
            include_ref=True,
        ),
        "deferred_inputs": _resolver_input_summaries(
            resolver_result.get("deferred_inputs"),
            include_ref=False,
        ),
        "blocked_inputs": _resolver_input_summaries(
            resolver_result.get("blocked_inputs"),
            include_ref=True,
        ),
        "unsafe_inputs_excluded": [
            _safe_text(_text(item.get("input_name"), "unknown"))
            for item in _list_of_mappings(resolver_result.get("unsafe_inputs_excluded"))
        ],
        "queue_handoff": _safe_mapping(resolver_result.get("queue_handoff")),
        "manual_operator_requirements": _safe_string_list(
            resolver_result.get("manual_operator_requirements")
        ),
        "non_claims": _safe_string_list(resolver_result.get("non_claims")),
    }


def _resolver_input_summaries(value: Any, *, include_ref: bool) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for item in _list_of_mappings(value):
        summary: dict[str, Any] = {
            "input_name": _safe_text(_text(item.get("input_name"), "unknown")),
            "input_status": _safe_text(_text(item.get("input_status"), "unknown")),
            "reason": _safe_optional_text(item.get("reason")),
            "can_feed_runtime_bundle": item.get("can_feed_runtime_bundle") is True,
        }
        if include_ref:
            summary["input_ref"] = _safe_optional_ref(item.get("input_ref"))
        summaries.append(summary)
    return summaries


def _attachment_state(
    *,
    hard_blockers: list[str],
    generated_artifacts: Mapping[str, str],
    deferred_reasons: list[str],
    failed_closed_reasons: list[str],
) -> str:
    if failed_closed_reasons:
        return "failed_closed"
    if hard_blockers:
        return "blocked"
    if "decision_work_brief_markdown" in generated_artifacts or (
        "decision_work_brief_enriched_markdown" in generated_artifacts
    ):
        if "automatic_triage_read" in generated_artifacts:
            return "generated"
        return "generated_agent_only"
    if deferred_reasons:
        return "deferred"
    return "not_eligible"


def _attachment_status(
    *,
    run_path: Path,
    output_path: Path,
    created_at: str | None,
    attachment_state: str,
    artifact_status: Mapping[str, Any],
    generated_artifacts: Mapping[str, str],
    missing_artifacts: Mapping[str, str],
    blocked_reasons: list[str],
    deferred_reasons: list[str],
    failed_closed_reasons: list[str],
    attachment_contract_path: Path | str,
    sidecar_contract_path: Path | str,
    sidecar_written_inside_archive: bool,
    source_inputs: Mapping[str, str | None],
    resolver_summary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    status = {
        "schema_version": ATTACHMENT_STATUS_SCHEMA_VERSION,
        "attachment_metadata": {
            "created_at": created_at or _utc_now(),
            "builder": "engine.system_b.decision_work_brief_runtime_bundle",
            "mode": "manual_post_archive",
            "output_ref": output_path.name,
            "post_archive_only": True,
            "input_archive_mutated": False,
            "sidecar_written_inside_archive": sidecar_written_inside_archive,
            "archive_core_artifacts_mutated": False,
        },
        "source_run_ref": artifact_status["source_run_ref"],
        "attachment_mode": "manual_post_archive",
        "attachment_state": attachment_state,
        "runtime_attachment_contract_ref": _safe_input_ref(attachment_contract_path),
        "runtime_sidecar_contract_ref": _safe_input_ref(sidecar_contract_path),
        "source_inputs": dict(source_inputs),
        "run_artifact_status": artifact_status,
        "generated_artifacts": dict(generated_artifacts),
        "missing_artifacts": dict(missing_artifacts),
        "blocked_reasons": list(blocked_reasons),
        "deferred_reasons": list(deferred_reasons),
        "failed_closed_reasons": list(failed_closed_reasons),
        "custody_flags": _custody_flags(),
        "privacy_export_policy": {
            "raw_conversation_text_included": False,
            "raw_revised_answer_text_included": False,
            "raw_memo_text_included": False,
            "provider_text_included": False,
            "private_ledgers_included": False,
            "local_absolute_paths_included": False,
            "source_refs_only_by_default": True,
        },
        "non_claims": list(NON_CLAIMS),
    }
    if resolver_summary is not None:
        status["resolver_summary"] = dict(resolver_summary)
    return status


def _initial_missing_artifacts() -> dict[str, str]:
    return {
        "attachment_status": "not_written_yet",
        "safe_supply_resolver": "not_supplied",
        "decision_work_brief_json": "not_supplied",
        "decision_work_brief_markdown": "not_supplied",
        "decision_work_brief_enriched_markdown": "not_supplied",
        "automatic_triage_packet": "not_generated_in_pr162",
        "automatic_triage_read": "not_supplied",
        "agent_handoff_packet": "not_generated_until_pr165",
        "user_receipt": "not_written_yet",
    }


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
        "answer_quality_scored": False,
        "agent_action_authorized": False,
        "automatic_action_authorized": False,
        "raw_private_content_included": False,
        "provider_text_included": False,
        "local_absolute_paths_included": False,
    }


def _load_json_object(path: Path | str, *, description: str = "contract JSON file") -> dict[str, Any]:
    input_path = Path(path).expanduser()
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DecisionWorkBriefRuntimeBundleInputError(
            f"{description} was not found"
        ) from exc
    except json.JSONDecodeError as exc:
        raise DecisionWorkBriefRuntimeBundleInputError(
            f"{description} was malformed"
        ) from exc
    except UnicodeDecodeError as exc:
        raise DecisionWorkBriefRuntimeBundleInputError(
            f"{description} was not valid UTF-8"
        ) from exc
    if not isinstance(payload, dict):
        raise DecisionWorkBriefRuntimeBundleInputError(f"{description} root was not an object")
    return payload


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _safe_input_ref(path: Path | str | None) -> str | None:
    if path is None:
        return None
    candidate = Path(path).expanduser()
    try:
        resolved = candidate.resolve(strict=False)
        return str(resolved.relative_to(REPO_ROOT))
    except ValueError:
        return candidate.name


def _safe_optional_ref(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    ref = value.strip()
    if Path(ref).is_absolute() or ".." in Path(ref).parts:
        return Path(ref).name
    if any(marker in ref for marker in RAW_PRIVATE_MARKERS):
        return "private_marker_redacted"
    return ref


def _safe_mapping(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        return {}
    safe: dict[str, Any] = {}
    for key, item in value.items():
        if isinstance(key, str):
            if isinstance(item, str):
                safe[key] = _safe_text(item)
            elif isinstance(item, bool) or item is None:
                safe[key] = item
            else:
                safe[key] = _safe_text(str(item))
    return safe


def _safe_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [_safe_text(item) for item in value if isinstance(item, str)]


def _safe_optional_text(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    return _safe_text(value)


def _safe_text(value: str) -> str:
    text = " ".join(str(value).strip().split())
    if any(marker in text for marker in RAW_PRIVATE_MARKERS):
        return "private_marker_redacted"
    return text or "not_specified"


def _run_ref(run_path: Path) -> str:
    parts = [part for part in run_path.parts if part]
    if len(parts) >= 2:
        return f"{_safe_slug(parts[-2])}/{_safe_slug(parts[-1])}"
    return _safe_slug(run_path.name)


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.=-]+", "-", value).strip("-")
    return slug or "unknown"


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


def _list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _text(value: Any, fallback: str = "") -> str:
    return value if isinstance(value, str) and value else fallback


def _join_reasons(reasons: list[str]) -> str:
    if not reasons:
        return "not specified"
    return ", ".join(reasons[:3])
