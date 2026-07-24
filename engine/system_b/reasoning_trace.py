"""Archive-time ReasoningTrace manifest builder.

This module turns an archived Lolla run directory into a local custody
manifest. It deliberately indexes raw artifacts by path and hash rather than
duplicating conversation or memo text into the trace itself.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .audit_mode import risk_mode_from_result
from .capture_adequacy import capture_adequacy_from_artifacts
from .source_coverage import build_source_coverage
from .control_plane import control_input_summary
from .provider_boundary_health import build_provider_boundary_health


REASONING_TRACE_SCHEMA_VERSION = "lolla.reasoning_trace.v0.2"
REASONING_TRACE_FILENAME = "reasoning_trace.json"

ARTIFACT_ROLES: dict[str, str] = {
    "conversation.txt": "source_conversation",
    "conversation_processing_view.txt": "bounded_conversation_processing_view",
    "conversation_processing_view.json": "bounded_conversation_processing_view_metadata",
    "extraction.json": "decision_structure",
    "provider_budget.json": "provider_budget_ledger",
    "result.json": "pipeline_result",
    "constitutional_graph_survival_ledger.json": "constitutional_graph_disposition_ledger",
    "revised.txt": "reconsidered_position",
    "memo.md": "decision_memo",
    "memo_note.json": "decision_memo_fields",
    "gapcheck.txt": "pressure_check_summary",
    "gapcheck_lanes.json": "pressure_check_state",
    "v60_ledger_skeleton.json": "private_enrichment_ledger_skeleton",
    "v60_ledger.json": "private_enrichment_ledger",
    "pre_step6_shadow_portfolio.json": "shadow_portfolio_trace",
    "pre_step6_private_table.json": "private_reasoning_table",
    "pre_step6_private_table.md": "private_reasoning_table_markdown",
    "pre_step6_private_table_ledger.json": "private_reasoning_table_ledger",
    "graph_survival_report.json": "graph_survival_report",
    "graph_survival_report.md": "graph_survival_report_markdown",
    "agent_result.json": "agent_facing_result",
    "control_input.json": "control_plane_input",
    "control_result.json": "control_plane_result",
    "extraction_adequacy_report.json": "extraction_adequacy_report",
    "evaluation.json": "deterministic_evaluation",
    "live_transcript.txt": "live_product_surface",
    "operator.log": "operator_log",
    "run_events.json": "run_event_ledger",
    "user_usefulness_review.json": "user_usefulness_review",
    "outcome_review.json": "outcome_review",
}

CONTENT_TYPES = {
    ".json": "application/json",
    ".md": "text/markdown",
    ".txt": "text/plain",
}


def build_reasoning_trace(
    run_dir: Path,
    *,
    run_id: str,
    case_id: str,
    fingerprint: str,
    how_matched: str,
    files_copied: Sequence[str],
    files_missing: Sequence[str],
    manifest: Mapping[str, Any],
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build a JSON-safe ReasoningTrace payload for an archived run."""
    run_dir = Path(run_dir)
    extraction = _read_json_object(run_dir / "extraction.json")
    result = _read_json_object(run_dir / "result.json")
    run_health = dict(_mapping(result.get("run_health")))
    if run_health:
        run_health["provider_boundary_health"] = build_provider_boundary_health(run_health)
    artifacts = _artifact_records(run_dir=run_dir, filenames=files_copied)
    missing_artifacts = _missing_artifact_records(files_missing)
    reasoning_lenses = _reasoning_lenses(result)
    graph_survival = _graph_survival(run_dir)
    budget_suppressed_lenses = _budget_suppressed_lenses(run_dir)
    model_calls = _model_calls(result)
    control_plane = control_input_summary(run_dir)
    candidate_commitments = _candidate_commitments(
        run_dir=run_dir,
        run_id=run_id,
        result=result,
    )
    surface_divergence = _surface_divergence(run_dir=run_dir, result=result)
    run_events = _run_events(run_dir)
    user_usefulness_review = _user_usefulness_review(run_dir)
    outcome_reviews = _outcome_reviews(run_dir)
    outcome_review_state = _outcome_review_state(outcome_reviews=outcome_reviews, run_dir=run_dir)

    trace: dict[str, Any] = {
        "schema_version": REASONING_TRACE_SCHEMA_VERSION,
        "trace_id": f"trace_{run_id}",
        "created_at": created_at or _utc_now_iso(),
        "source": {
            "adapter": "lolla_skill",
            "capture_hook": "archive_run",
            "storage_mode": "local_archive",
            "project_root": None,
        },
        "participants": _participants(extraction=extraction, result=result),
        "privacy": {
            "mode": "local_only",
            "mode_scope": "archive_storage_only",
            "provider_egress_covered_by_mode": False,
            "interface_visibility_covered_by_mode": False,
            "raw_transcript_saved": (run_dir / "conversation.txt").exists(),
            "summary_saved": bool(extraction),
            "retention_days": None,
            "raw_text_duplicated_in_trace": False,
            "selected_commitment_snippets_saved": bool(candidate_commitments),
            "external_egress_by_trace_builder": False,
            "non_claim": (
                "local_only_describes_archive_storage_not_the_provider_or_host_ui"
            ),
        },
        "case": {
            "case_id": case_id,
            "run_id": run_id,
            "decision_situation": _decision_situation(extraction),
            "fingerprint": fingerprint,
            "how_matched": how_matched,
            "run_count": _safe_int(manifest.get("run_count")),
            "case_manifest_ref": "../.case-manifest.json",
        },
        "content_hashes": {
            "conversation_sha256": _sha256_uri_or_none(run_dir / "conversation.txt"),
            "result_sha256": _sha256_uri_or_none(run_dir / "result.json"),
            "artifact_index_sha256": _object_sha256_uri(artifacts),
        },
        "capture": _capture_summary(extraction=extraction, result=result),
        "process": {
            "risk_mode": risk_mode_from_result(result),
            "run_health": run_health,
            "audit_summary": _audit_summary(result),
            "pressure_check": _pressure_check(result),
            "private_custody": _private_custody(result=result, run_dir=run_dir),
            "graph_survival": graph_survival,
            "run_events": run_events,
            "usage": _usage_summary(result),
            **({"control_plane": control_plane} if control_plane else {}),
        },
        "artifacts": artifacts,
        "missing_artifacts": missing_artifacts,
        "reasoning_lenses": reasoning_lenses,
        "budget_suppressed_lenses": budget_suppressed_lenses,
        "top_budget_suppressed_lenses": list(
            _list(graph_survival.get("top_budget_suppressed_lenses"))
        ),
        "surface_divergence": surface_divergence,
        "trace_adequacy": _trace_adequacy(
            run_dir=run_dir,
            extraction=extraction,
            result=result,
            reasoning_lenses=reasoning_lenses,
            model_calls=model_calls,
            candidate_commitments=candidate_commitments,
            outcome_reviews=outcome_reviews,
        ),
        "candidate_commitments": candidate_commitments,
        "decision_packets": [],
        "user_usefulness_review": user_usefulness_review,
        "outcome_review_state": outcome_review_state,
        "outcome_reviews": outcome_reviews,
        "model_calls": model_calls,
        "tool_calls": [],
        "tool_call_coverage": {
            "status": "not_observed",
            "scope": "repository_run_events_only",
            "complete_host_tool_stream_captured": False,
            "non_claim": "empty_tool_calls_does_not_prove_no_host_tool_calls",
        },
    }
    return trace


def write_reasoning_trace(
    run_dir: Path,
    *,
    run_id: str,
    case_id: str,
    fingerprint: str,
    how_matched: str,
    files_copied: Sequence[str],
    files_missing: Sequence[str],
    manifest: Mapping[str, Any],
    created_at: str | None = None,
) -> tuple[Path, dict[str, Any]]:
    """Write ``reasoning_trace.json`` into ``run_dir`` and return path/payload."""
    payload = build_reasoning_trace(
        run_dir,
        run_id=run_id,
        case_id=case_id,
        fingerprint=fingerprint,
        how_matched=how_matched,
        files_copied=files_copied,
        files_missing=files_missing,
        manifest=manifest,
        created_at=created_at,
    )
    path = Path(run_dir) / REASONING_TRACE_FILENAME
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path, payload


def _artifact_records(*, run_dir: Path, filenames: Sequence[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for filename in filenames:
        path = run_dir / filename
        if not path.exists() or not path.is_file():
            continue
        stat = path.stat()
        records.append(
            {
                "path": filename,
                "role": _artifact_role(filename),
                "sha256": _sha256_uri(path),
                "bytes": stat.st_size,
                "content_type": CONTENT_TYPES.get(path.suffix.lower(), "application/octet-stream"),
            }
        )
    return records


def _missing_artifact_records(filenames: Sequence[str]) -> list[dict[str, str]]:
    return [
        {
            "path": filename,
            "role": _artifact_role(filename),
        }
        for filename in filenames
    ]


def _artifact_role(filename: str) -> str:
    return ARTIFACT_ROLES.get(filename, "archived_artifact")


def _read_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _sha256_uri(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def _sha256_uri_or_none(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    return _sha256_uri(path)


def _object_sha256_uri(value: Any) -> str:
    canonical = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(canonical).hexdigest()}"


def _utc_now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _participants(*, extraction: Mapping[str, Any], result: Mapping[str, Any]) -> list[str]:
    speakers: list[str] = []
    seen: set[str] = set()
    for payload in (extraction, result):
        turns = _turns(payload)
        for turn in turns:
            speaker = str(_mapping(turn).get("speaker") or "").strip()
            if speaker and speaker not in seen:
                seen.add(speaker)
                speakers.append(speaker)
    return speakers


def _turns(payload: Mapping[str, Any]) -> list[Any]:
    extraction = _mapping(payload.get("extraction"))
    turns = extraction.get("turns")
    return turns if isinstance(turns, list) else []


def _decision_situation(extraction_payload: Mapping[str, Any]) -> str:
    extraction = _mapping(extraction_payload.get("extraction"))
    return str(extraction.get("decision_situation") or "").strip()


def _capture_summary(
    *,
    extraction: Mapping[str, Any],
    result: Mapping[str, Any],
) -> dict[str, Any]:
    capture_manifest = _mapping(extraction.get("capture_manifest"))
    capture_health = str(extraction.get("capture_health") or "").strip()
    if not capture_health:
        capture_health = str(_mapping(result.get("run_health")).get("capture") or "").strip()
    capture_adequacy = capture_adequacy_from_artifacts(
        extraction=extraction,
        result=result,
    )
    return {
        "capture_health": capture_health or "unknown",
        "capture_manifest": dict(capture_manifest),
        "capture_adequacy": capture_adequacy,
        "source_coverage": build_source_coverage(
            processing_view=_mapping(extraction.get("conversation_processing_view")),
            capture_adequacy=capture_adequacy,
        ),
        "decision_structure": _decision_structure_summary(extraction),
    }


def _decision_structure_summary(extraction_payload: Mapping[str, Any]) -> dict[str, Any]:
    extraction = _mapping(extraction_payload.get("extraction"))
    return {
        "live_constraint_count": len(_list(extraction.get("live_constraints"))),
        "reasoning_passage_count": len(_list(extraction.get("reasoning_passages"))),
        "dropped_thread_count": len(_list(extraction.get("dropped_threads"))),
        "original_framing_present": bool(str(extraction.get("original_framing") or "").strip()),
        "synthesized_position_present": bool(
            str(extraction.get("synthesized_position") or "").strip()
        ),
    }


def _audit_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    audit = _mapping(result.get("audit_summary"))
    deep_results = [_mapping(item) for item in _list(audit.get("deep_check_results"))]
    route_trace = _mapping(audit.get("route_trace"))
    triggered = [str(item) for item in _list(audit.get("triggered_tendencies")) if str(item)]
    detected = [
        str(item.get("tendency_id") or "")
        for item in deep_results
        if item.get("detected") and str(item.get("tendency_id") or "")
    ]
    return {
        "triggered_tendency_ids": triggered,
        "triggered_tendency_count": len(triggered),
        "deep_check_count": len(deep_results),
        "detected_tendency_ids": detected,
        "detected_tendency_count": len(detected),
        "routing_decision_count": len(_list(audit.get("routing_decisions"))),
        "boundary_call_count": _safe_int(audit.get("boundary_call_count")),
        "warning_count": len(_list(audit.get("warnings"))),
        "route_trace_schema_version": str(route_trace.get("schema_version") or ""),
        "route_trace_summary": dict(_mapping(route_trace.get("summary"))),
    }


def _pressure_check(result: Mapping[str, Any]) -> dict[str, Any]:
    gap_check = _mapping(result.get("gap_check"))
    return {
        "has_gap_check": bool(result.get("has_gap_check")),
        "mode": str(result.get("pressure_check_mode") or ""),
        "status": str(gap_check.get("status") or ""),
        "reason": str(gap_check.get("reason") or ""),
        "lane_count": len(_list(gap_check.get("lanes"))),
        "summary_present": bool(str(result.get("gap_check_summary") or "").strip()),
    }


def _private_custody(*, result: Mapping[str, Any], run_dir: Path) -> dict[str, Any]:
    run_health = _mapping(result.get("run_health"))
    private_table = _mapping(result.get("pre_step6_private_table"))
    v60 = _mapping(result.get("v60_enrichment"))
    v60_validation = _mapping(result.get("v60_consideration_validation"))
    graph_survival = _mapping(result.get("constitutional_graph_survival"))
    graph_validation = _mapping(
        result.get("constitutional_graph_survival_ledger_validation")
    )
    return {
        "constitutional_graph_survival_status": str(
            graph_survival.get("status") or ""
        ),
        "constitutional_graph_survival_ledger_status": str(
            graph_validation.get("status")
            or run_health.get("constitutional_graph_survival_ledger")
            or ""
        ),
        "constitutional_graph_survival_ledger_file_present": (
            run_dir / "constitutional_graph_survival_ledger.json"
        ).exists(),
        "v60_enrichment_status": str(v60.get("status") or ""),
        "v60_consideration_ledger_status": str(
            v60_validation.get("status") or run_health.get("v60_consideration_ledger") or ""
        ),
        "v60_ledger_file_present": (run_dir / "v60_ledger.json").exists(),
        "pre_step6_private_table_status": str(private_table.get("status") or ""),
        "pre_step6_private_table_ledger_file_present": (
            run_dir / "pre_step6_private_table_ledger.json"
        ).exists(),
        "pre_step6_shadow_portfolio_file_present": (
            run_dir / "pre_step6_shadow_portfolio.json"
        ).exists(),
        "graph_survival_report_file_present": (
            run_dir / "graph_survival_report.json"
        ).exists(),
    }


def _graph_survival(run_dir: Path) -> dict[str, Any]:
    try:
        from engine.system_b.graph_survival_report import graph_survival_summary_for_trace
    except Exception:
        return {"status": "unavailable", "artifact_path": ""}
    return graph_survival_summary_for_trace(run_dir)


def _budget_suppressed_lenses(run_dir: Path) -> list[dict[str, Any]]:
    try:
        from engine.system_b.graph_survival_report import budget_suppressed_lenses_for_trace
    except Exception:
        return []
    return budget_suppressed_lenses_for_trace(run_dir, limit=None)


def _usage_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    usage = _mapping(result.get("usage_summary"))
    vendors = _mapping(usage.get("vendors"))
    vendor_calls: dict[str, int] = {}
    for vendor_name, raw_vendor in vendors.items():
        vendor = _mapping(raw_vendor)
        vendor_calls[str(vendor_name)] = _safe_int(vendor.get("calls"))
    total_vendor_calls = sum(vendor_calls.values())
    return {
        "run_id": str(usage.get("run_id") or ""),
        "pricing_table_version": str(usage.get("pricing_table_version") or ""),
        "estimated_total_cost_usd": usage.get("estimated_total_cost_usd"),
        "provider_reported_total_cost_usd": usage.get(
            "provider_reported_total_cost_usd"
        ),
        "cost_estimate_state": str(usage.get("cost_estimate_state") or ""),
        "vendor_calls": vendor_calls,
        "total_vendor_call_count": total_vendor_calls,
    }


def _reasoning_lenses(result: Mapping[str, Any]) -> list[dict[str, Any]]:
    lenses: dict[str, dict[str, Any]] = {}
    audit = _mapping(result.get("audit_summary"))
    route_trace = _mapping(audit.get("route_trace"))

    if _mapping(route_trace.get("lanes")):
        _add_route_trace_lenses(lenses, route_trace)
    else:
        _add_fallback_lenses(lenses, result)

    _add_companion_anchor_details(lenses, result)
    _add_companion_verification_lenses(lenses, audit)
    _add_private_enrichment_lenses(lenses, result)

    return [_finalize_lens(row) for row in lenses.values()]


def _add_route_trace_lenses(
    lenses: dict[str, dict[str, Any]],
    route_trace: Mapping[str, Any],
) -> None:
    lanes = _mapping(route_trace.get("lanes"))
    for lane_id, raw_lane in lanes.items():
        lane = _mapping(raw_lane)
        if lane_id == "lane2":
            for model_id in _list(lane.get("selected_model_ids")):
                _add_lens(
                    lenses,
                    model_id,
                    lane="lane2",
                    role="companion_anchor",
                    selected=True,
                    surfaced=True,
                    source_ref="result.json#/audit_summary/route_trace/lanes/lane2/selected_model_ids",
                )
            for index, rejected in enumerate(_list(lane.get("rejected_candidates"))):
                item = _mapping(rejected)
                _add_lens(
                    lenses,
                    item.get("model_id"),
                    lane="lane2",
                    role="rejected_candidate",
                    selected=False,
                    rejection_reason=_text(item.get("rejection_reason")),
                    source_ref=(
                        "result.json#/audit_summary/route_trace/lanes/"
                        f"lane2/rejected_candidates/{index}"
                    ),
                )
            continue

        for route_index, raw_route in enumerate(_list(lane.get("routes"))):
            route = _mapping(raw_route)
            route_ref = (
                "result.json#/audit_summary/route_trace/lanes/"
                f"{lane_id}/routes/{route_index}"
            )
            if lane_id == "lane1":
                _add_lens(
                    lenses,
                    route.get("primary_model_id"),
                    lane="lane1",
                    role="primary_antidote",
                    selected=True,
                    surfaced=True,
                    source_ref=f"{route_ref}/primary_model_id",
                )
                for model_id in _list(route.get("supporting_model_ids")):
                    _add_lens(
                        lenses,
                        model_id,
                        lane="lane1",
                        role="supporting_antidote",
                        selected=True,
                        surfaced=True,
                        source_ref=f"{route_ref}/supporting_model_ids",
                    )
                for model_id in _list(route.get("risk_model_ids")):
                    _add_lens(
                        lenses,
                        model_id,
                        lane="lane1",
                        role="risk_model",
                        selected=True,
                        surfaced=True,
                        source_ref=f"{route_ref}/risk_model_ids",
                    )
            for model_id in _list(route.get("selected_model_ids")):
                _add_lens(
                    lenses,
                    model_id,
                    lane=str(lane_id),
                    role=_selected_lens_role(str(lane_id)),
                    selected=True,
                    surfaced=True,
                    source_ref=f"{route_ref}/selected_model_ids",
                )
            for rejected_index, rejected in enumerate(_list(route.get("rejected_candidates"))):
                item = _mapping(rejected)
                _add_lens(
                    lenses,
                    item.get("model_id"),
                    lane=str(lane_id),
                    role="rejected_candidate",
                    selected=False,
                    rejection_reason=_text(item.get("rejection_reason")),
                    source_ref=f"{route_ref}/rejected_candidates/{rejected_index}",
                )

    anti_echo = _mapping(route_trace.get("anti_echo"))
    for index, exclusion in enumerate(_list(anti_echo.get("exclusions"))):
        item = _mapping(exclusion)
        excluded_from = _text(item.get("excluded_from")) or "unknown"
        _add_lens(
            lenses,
            item.get("model_id"),
            lane=excluded_from,
            role="anti_echo_excluded",
            selected=False,
            rejection_reason=_text(item.get("reason")) or "anti_echo_excluded",
            source_ref=f"result.json#/audit_summary/route_trace/anti_echo/exclusions/{index}",
        )


def _add_fallback_lenses(lenses: dict[str, dict[str, Any]], result: Mapping[str, Any]) -> None:
    delta = _mapping(result.get("delta_card"))
    for index, finding in enumerate(_list(delta.get("findings"))):
        item = _mapping(finding)
        for model_id in _list(item.get("selected_model_ids")):
            _add_lens(
                lenses,
                model_id,
                lane="lane1",
                role="lane1_selected",
                selected=True,
                surfaced=True,
                source_ref=f"result.json#/delta_card/findings/{index}/selected_model_ids",
            )

    companion = _mapping(result.get("companion_cheat_sheet"))
    for index, anchor in enumerate(_list(companion.get("anchors"))):
        item = _mapping(anchor)
        _add_lens(
            lenses,
            item.get("model_id"),
            lane="lane2",
            role="companion_anchor",
            selected=True,
            surfaced=True,
            source_ref=f"result.json#/companion_cheat_sheet/anchors/{index}",
        )

    frame = _mapping(result.get("frame_pressure_card"))
    for index, reframing in enumerate(_list(frame.get("reframings"))):
        item = _mapping(reframing)
        _add_lens(
            lenses,
            item.get("grounding_model"),
            lane="lane3",
            role="frame_reframing",
            selected=True,
            surfaced=True,
            source_ref=f"result.json#/frame_pressure_card/reframings/{index}/grounding_model",
        )

    coverage = _mapping(result.get("structural_coverage_card"))
    for index, route in enumerate(_list(coverage.get("gap_routes"))):
        item = _mapping(route)
        for model_id in _list(item.get("candidate_model_ids")):
            _add_lens(
                lenses,
                model_id,
                lane="lane4",
                role="structural_gap_candidate",
                selected=True,
                surfaced=True,
                source_ref=f"result.json#/structural_coverage_card/gap_routes/{index}",
            )


def _add_companion_anchor_details(
    lenses: dict[str, dict[str, Any]],
    result: Mapping[str, Any],
) -> None:
    companion = _mapping(result.get("companion_cheat_sheet"))
    for index, anchor in enumerate(_list(companion.get("anchors"))):
        item = _mapping(anchor)
        details = {
            "display_name": _text(item.get("display_name")),
            "chunk_count": len(_list(item.get("chunks"))),
            "presence_mode": _text(item.get("presence_mode")),
            "has_evidence_quote": bool(_text(item.get("evidence_quote"))),
            "has_presence_explanation": bool(_text(item.get("presence_explanation"))),
        }
        _add_lens(
            lenses,
            item.get("model_id"),
            lane="lane2",
            role="companion_anchor",
            selected=True,
            surfaced=True,
            source_ref=f"result.json#/companion_cheat_sheet/anchors/{index}",
            details=details,
        )


def _add_companion_verification_lenses(
    lenses: dict[str, dict[str, Any]],
    audit: Mapping[str, Any],
) -> None:
    for index, item in enumerate(_list(audit.get("companion_verification_accepted_before_cap"))):
        accepted = _mapping(item)
        _add_lens(
            lenses,
            accepted.get("model_id"),
            lane="lane2",
            role="companion_verified",
            selected=True,
            surfaced=False,
            source_ref=(
                "result.json#/audit_summary/"
                f"companion_verification_accepted_before_cap/{index}"
            ),
            details={"presence_mode": _text(accepted.get("presence_mode"))},
        )

    for field, default_reason in (
        ("companion_rejected_models", "verifier_rejected"),
        ("companion_verification_capped_models", "capped_at_top_5"),
        ("companion_verification_duplicate_accepts", "duplicate_accept_dedupe"),
        ("companion_verification_silently_omitted", "not_in_verifier_response"),
    ):
        for index, item in enumerate(_list(audit.get(field))):
            row = _mapping(item)
            _add_lens(
                lenses,
                row.get("model_id"),
                lane="lane2",
                role="companion_not_surfaced",
                selected=False,
                rejection_reason=(
                    _text(row.get("rejection_reason"))
                    or _text(row.get("drop_reason"))
                    or default_reason
                ),
                source_ref=f"result.json#/audit_summary/{field}/{index}",
            )


def _add_private_enrichment_lenses(
    lenses: dict[str, dict[str, Any]],
    result: Mapping[str, Any],
) -> None:
    enrichment = _mapping(result.get("v60_enrichment"))
    telemetry = _mapping(enrichment.get("telemetry"))
    for model_id in _list(telemetry.get("selected_model_ids")):
        _add_lens(
            lenses,
            model_id,
            lane="private_enrichment",
            role="private_enrichment_selected",
            selected=True,
            surfaced=False,
            source_ref="result.json#/v60_enrichment/telemetry/selected_model_ids",
            details={
                "private_enrichment_status": _text(enrichment.get("status")),
                "selected_chunk_count": _safe_int(telemetry.get("selected_chunk_count")),
            },
        )


def _add_lens(
    lenses: dict[str, dict[str, Any]],
    lens_id: Any,
    *,
    lane: str,
    role: str,
    selected: bool,
    source_ref: str,
    surfaced: bool = False,
    rejection_reason: str = "",
    details: Mapping[str, Any] | None = None,
) -> None:
    model_id = _text(lens_id)
    if not model_id:
        return
    row = lenses.setdefault(
        model_id,
        {
            "lens_id": model_id,
            "lens_type": "mental_model",
            "source_lanes": [],
            "roles": [],
            "selected": False,
            "surfaced": False,
            "disposition": "candidate",
            "rejection_reasons": [],
            "source_refs": [],
            "evidence": {},
            "usage": {
                "used_in_revised_answer": "unknown",
                "changed_recommendation": "unknown",
                "human_marked_useful": None,
                "outcome_signal": "unknown",
            },
        },
    )
    _append_unique(row["source_lanes"], lane)
    _append_unique(row["roles"], role)
    _append_unique(row["source_refs"], source_ref)
    row["selected"] = bool(row["selected"] or selected)
    row["surfaced"] = bool(row["surfaced"] or surfaced)
    if rejection_reason:
        _append_unique(row["rejection_reasons"], rejection_reason)
    if details:
        evidence = row["evidence"]
        for key, value in details.items():
            if value not in (None, "", [], {}):
                evidence[key] = value


def _finalize_lens(row: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(row)
    if payload.get("selected") and payload.get("rejection_reasons"):
        payload["disposition"] = "mixed_selected"
    elif payload.get("selected"):
        payload["disposition"] = "selected"
    elif payload.get("rejection_reasons"):
        payload["disposition"] = "rejected"
    else:
        payload["disposition"] = "candidate"
    payload["source_lanes"] = sorted(_list(payload.get("source_lanes")))
    payload["roles"] = sorted(_list(payload.get("roles")))
    payload["rejection_reasons"] = sorted(_list(payload.get("rejection_reasons")))
    payload["source_refs"] = sorted(_list(payload.get("source_refs")))
    return payload


def _selected_lens_role(lane_id: str) -> str:
    return {
        "lane1": "lane1_selected",
        "lane2": "companion_anchor",
        "lane3": "frame_reframing",
        "lane4": "structural_gap_candidate",
    }.get(lane_id, "selected")


def _model_calls(result: Mapping[str, Any]) -> list[dict[str, Any]]:
    audit = _mapping(result.get("audit_summary"))
    boundary_stage_counts: dict[str, int] = {}
    calls: list[dict[str, Any]] = []
    for index, raw_call in enumerate(_list(audit.get("boundary_calls"))):
        call = _mapping(raw_call)
        stage = _text(call.get("stage"))
        if stage:
            boundary_stage_counts[stage] = boundary_stage_counts.get(stage, 0) + 1
        calls.append(
            {
                "index": index,
                "record_type": "boundary_call",
                "call_count": 1,
                "stage": _text(call.get("stage")),
                "tendency_id": _text(call.get("tendency_id")),
                "provider_name": _text(call.get("provider_name")),
                "requested_model": _text(call.get("requested_model")),
                "served_model": _text(call.get("served_model")),
                "model": _text(call.get("model")),
                "model_attribution_status": _text(call.get("model_attribution_status")),
                "status": _text(call.get("status")),
                "finish_reason": _text(call.get("finish_reason")),
                "temperature": call.get("temperature"),
                "prompt_tokens": _safe_int(call.get("prompt_tokens")),
                "completion_tokens": _safe_int(call.get("completion_tokens")),
                "total_tokens": _safe_int(call.get("total_tokens")),
                "cached_tokens": _safe_int(call.get("cached_tokens")),
                "cache_write_tokens": _safe_int(call.get("cache_write_tokens")),
                "reasoning_tokens": _safe_int(call.get("reasoning_tokens")),
                "reasoning_disabled": bool(call.get("reasoning_disabled")),
                "reasoning_details_present": bool(call.get("reasoning_details_present")),
                "raw_message_content_present": bool(_text(call.get("raw_message_content"))),
            }
        )
    _append_usage_summary_model_calls(
        calls,
        result=result,
        boundary_stage_counts=boundary_stage_counts,
    )
    return calls


def _append_usage_summary_model_calls(
    calls: list[dict[str, Any]],
    *,
    result: Mapping[str, Any],
    boundary_stage_counts: Mapping[str, int],
) -> None:
    """Add sanitized aggregate call records for calls not present in boundary_calls."""
    usage = _mapping(result.get("usage_summary"))
    vendors = _mapping(usage.get("vendors"))
    represented_by_vendor: dict[str, int] = {}
    for call in calls:
        provider = _text(call.get("provider_name")) or "unknown"
        represented_by_vendor[provider] = represented_by_vendor.get(provider, 0) + _safe_int(
            call.get("call_count") or 1
        )

    openrouter = _mapping(vendors.get("openrouter"))
    openrouter_stage_extra = 0
    for stage_name, raw_stage in _mapping(openrouter.get("stages")).items():
        stage = _mapping(raw_stage)
        stage_call_count = _safe_int(stage.get("calls"))
        represented = _safe_int(boundary_stage_counts.get(str(stage_name)))
        extra_count = max(stage_call_count - represented, 0)
        if extra_count <= 0:
            continue
        openrouter_stage_extra += extra_count
        calls.append(
            _aggregate_model_call(
                index=len(calls),
                record_type="usage_stage_summary",
                provider_name="openrouter",
                stage=str(stage_name),
                call_count=extra_count,
                requested_model=_first_string(openrouter.get("requested_models_seen")),
                served_model=_first_string(openrouter.get("models_seen")),
                model=_text(openrouter.get("primary_model"))
                or _first_string(openrouter.get("models_seen")),
                prompt_tokens=_scaled_count(stage.get("prompt_tokens"), extra_count, stage_call_count),
                completion_tokens=_scaled_count(
                    stage.get("completion_tokens"),
                    extra_count,
                    stage_call_count,
                ),
                total_tokens=_scaled_count(stage.get("total_tokens"), extra_count, stage_call_count),
                cached_tokens=_scaled_count(stage.get("cached_tokens"), extra_count, stage_call_count),
            )
        )
    if openrouter_stage_extra:
        represented_by_vendor["openrouter"] = represented_by_vendor.get("openrouter", 0) + openrouter_stage_extra

    _append_openai_usage_model_calls(calls, vendors, represented_by_vendor)
    _append_anthropic_usage_model_calls(calls, vendors, represented_by_vendor)

    for vendor_name, raw_vendor in vendors.items():
        vendor = _mapping(raw_vendor)
        vendor_call_count = _safe_int(vendor.get("calls"))
        represented = represented_by_vendor.get(str(vendor_name), 0)
        extra_count = max(vendor_call_count - represented, 0)
        if extra_count <= 0:
            continue
        calls.append(
            _aggregate_model_call(
                index=len(calls),
                record_type="vendor_usage_summary",
                provider_name=str(vendor_name),
                stage="usage_summary",
                call_count=extra_count,
                model=_text(vendor.get("primary_model")) or _first_string(vendor.get("models_seen")),
            )
        )


def _append_openai_usage_model_calls(
    calls: list[dict[str, Any]],
    vendors: Mapping[str, Any],
    represented_by_vendor: dict[str, int],
) -> None:
    vendor = _mapping(vendors.get("openai_embeddings"))
    by_model = _mapping(vendor.get("by_model"))
    for model_name, raw_model in by_model.items():
        model = _mapping(raw_model)
        call_count = _safe_int(model.get("calls"))
        if call_count <= 0:
            continue
        represented_by_vendor["openai_embeddings"] = (
            represented_by_vendor.get("openai_embeddings", 0) + call_count
        )
        calls.append(
            _aggregate_model_call(
                index=len(calls),
                record_type="vendor_model_summary",
                provider_name="openai_embeddings",
                stage="openai_model_usage",
                call_count=call_count,
                model=str(model_name),
                prompt_tokens=_safe_int(model.get("input_tokens")),
                completion_tokens=_safe_int(model.get("output_tokens")),
                total_tokens=(
                    _safe_int(model.get("input_tokens")) + _safe_int(model.get("output_tokens"))
                ),
            )
        )


def _append_anthropic_usage_model_calls(
    calls: list[dict[str, Any]],
    vendors: Mapping[str, Any],
    represented_by_vendor: dict[str, int],
) -> None:
    vendor = _mapping(vendors.get("anthropic_subagents"))
    by_model = _mapping(vendor.get("by_model"))
    for model_name, raw_model in by_model.items():
        model = _mapping(raw_model)
        call_count = _safe_int(model.get("calls"))
        if call_count <= 0:
            continue
        represented_by_vendor["anthropic_subagents"] = (
            represented_by_vendor.get("anthropic_subagents", 0) + call_count
        )
        calls.append(
            _aggregate_model_call(
                index=len(calls),
                record_type="vendor_model_summary",
                provider_name="anthropic_subagents",
                stage="anthropic_subagent_usage",
                call_count=call_count,
                model=str(model_name),
                total_tokens=_safe_int(model.get("total_tokens")),
            )
        )


def _aggregate_model_call(
    *,
    index: int,
    record_type: str,
    provider_name: str,
    stage: str,
    call_count: int,
    requested_model: str = "",
    served_model: str = "",
    model: str = "",
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    total_tokens: int = 0,
    cached_tokens: int = 0,
) -> dict[str, Any]:
    return {
        "index": index,
        "record_type": record_type,
        "call_count": call_count,
        "stage": stage,
        "tendency_id": "",
        "provider_name": provider_name,
        "requested_model": requested_model,
        "served_model": served_model,
        "model": model,
        "model_attribution_status": "aggregate",
        "status": "summarized",
        "finish_reason": "",
        "temperature": None,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "cached_tokens": cached_tokens,
        "cache_write_tokens": 0,
        "reasoning_tokens": 0,
        "reasoning_disabled": False,
        "reasoning_details_present": False,
        "raw_message_content_present": False,
    }


def _surface_divergence(*, run_dir: Path, result: Mapping[str, Any]) -> dict[str, Any]:
    revised_path = run_dir / "revised.txt"
    live_path = run_dir / "live_transcript.txt"
    revised_text = _read_text(revised_path)
    live_text = _read_text(live_path)
    result_revised_answer = _text(result.get("revised_answer"))
    revised_present = bool(revised_text.strip())
    live_present = bool(live_text.strip())
    result_present = bool(result_revised_answer)
    revised_matches_result = (
        _normalize_surface_text(revised_text) == _normalize_surface_text(result_revised_answer)
        if revised_present and result_present
        else None
    )
    revised_found_in_live = (
        _normalize_surface_text(revised_text) in _normalize_surface_text(live_text)
        if revised_present and live_present
        else None
    )
    if not revised_present or not live_present:
        status = "not_checkable"
    elif revised_found_in_live:
        status = "matched"
    else:
        status = "diverged"
    return {
        "schema_version": "lolla.surface_divergence.v0.1",
        "status": status,
        "comparison_scope": (
            "persisted_revised_artifact_vs_curated_live_transcript_artifact"
        ),
        "complete_visible_surface_compared": False,
        "non_claim": (
            "matched_does_not_prove_the_complete_host_visible_surface_matched"
        ),
        "revised_artifact_present": revised_present,
        "live_transcript_present": live_present,
        "result_revised_answer_present": result_present,
        "revised_artifact_matches_result": revised_matches_result,
        "revised_artifact_found_in_live_transcript": revised_found_in_live,
        "revised_sha256": _sha256_uri_or_none(revised_path),
        "live_transcript_sha256": _sha256_uri_or_none(live_path),
        "source_refs": {
            "revised": "revised.txt" if revised_present else "",
            "live_transcript": "live_transcript.txt" if live_present else "",
            "result_revised_answer": "result.json#/revised_answer" if result_present else "",
        },
    }


def _run_events(run_dir: Path) -> dict[str, Any]:
    try:
        from .run_events import load_run_events

        return load_run_events(run_dir)
    except Exception:
        return {
            "schema_version": "lolla.run_events.v0.1",
            "status": "unreadable",
            "event_count": 0,
            "artifact_path": (
                "run_events.json" if (Path(run_dir) / "run_events.json").exists() else ""
            ),
            "events": [],
        }


def _candidate_commitments(
    *,
    run_dir: Path,
    run_id: str,
    result: Mapping[str, Any],
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    revised_text = _read_text(run_dir / "revised.txt")
    for turn in _conversation_turns(run_dir / "conversation.txt"):
        source_surface = "conversation"
        source_ref = f"conversation.txt#turn{turn['turn_index']}.{turn['role'].lower()}"
        source_actor = turn["role"].lower()
        for span_index, span in enumerate(_commitment_spans(turn["text"])):
            candidate = _commitment_candidate_from_span(
                span,
                run_id=run_id,
                source_surface=source_surface,
                source_ref=f"{source_ref}.span{span_index + 1}",
                source_actor=source_actor,
                revised_text=revised_text,
                result=result,
            )
            if candidate:
                candidates.append(candidate)

    for paragraph_index, paragraph in enumerate(_paragraphs(revised_text)):
        for span_index, span in enumerate(_commitment_spans(paragraph)):
            candidate = _commitment_candidate_from_span(
                span,
                run_id=run_id,
                source_surface="revised_answer",
                source_ref=f"revised.txt#paragraph{paragraph_index + 1}.span{span_index + 1}",
                source_actor="assistant",
                revised_text=revised_text,
                result=result,
            )
            if candidate:
                candidates.append(candidate)

    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for candidate in sorted(
        candidates,
        key=lambda item: (
            -float(item["confidence"]),
            str(item["source_surface"]),
            str(item["source_ref"]),
        ),
    ):
        key = _normalize_candidate_text(str(candidate["claim"]))
        if key in seen:
            continue
        seen.add(key)
        candidate["candidate_id"] = f"commitment_{run_id}_{len(deduped) + 1:03d}"
        deduped.append(candidate)
        if len(deduped) >= 12:
            break
    return deduped


def _commitment_candidate_from_span(
    span: str,
    *,
    run_id: str,
    source_surface: str,
    source_ref: str,
    source_actor: str,
    revised_text: str,
    result: Mapping[str, Any],
) -> dict[str, Any] | None:
    claim = _bounded_text(span, limit=650)
    if len(claim) < 24:
        return None
    if _is_non_action_commitment_span(claim):
        return None
    kind, confidence, reason = _classify_commitment_span(claim)
    if not kind:
        return None
    if source_actor == "user" and kind != "plan" and not _looks_like_user_commitment(claim):
        return None
    actionability = "high" if confidence >= 0.8 else "medium"
    audit_effect, corrected_to = _audit_effect_for_candidate(
        claim=claim,
        source_surface=source_surface,
        revised_text=revised_text,
    )
    classification = _commitment_classification(
        claim=claim,
        kind=kind,
        source_actor=source_actor,
        source_surface=source_surface,
        audit_effect=audit_effect,
    )
    return {
        "schema_version": "lolla.commitment_candidate.v0.1",
        "candidate_id": f"commitment_{run_id}_pending",
        "kind": kind,
        "source_surface": source_surface,
        "source_ref": source_ref,
        "source_actor": source_actor,
        "actor_type": classification["actor_type"],
        "commitment_source": (
            "human_plan" if source_actor == "user" else "ai_recommendation"
        ),
        "claim": claim,
        "claim_sha256": _object_sha256_uri(claim),
        "actionability": actionability,
        "impact": classification["impact"],
        "reversibility": classification["reversibility"],
        "evidence_status": classification["evidence_status"],
        "correction_status": classification["correction_status"],
        "semantic_flags": classification["semantic_flags"],
        "classification": classification,
        "confidence": round(confidence, 2),
        "reason": reason,
        "audit_effect": audit_effect,
        "corrected_to": corrected_to,
        "escalation_recommended": kind in {"recommendation", "plan", "gate", "reversal_trigger"},
        "decision_packet_ready": False,
        "decision_packet_blockers": _decision_packet_blockers(result),
    }


def _classify_commitment_span(span: str) -> tuple[str, float, str]:
    lower = span.lower()
    if lower.startswith("generate more options") or lower.startswith('"generate more options"'):
        return "meta_constraint", 0.62, "Contains a bounded meta-constraint, not a direct action."
    if "my revised recommendation is" in lower or "revised recommendation is" in lower:
        return "recommendation", 0.94, "Contains an explicit revised recommendation."
    if re.search(r"\b(if|when)\b.+\b(take|accept|choose|decline|reject)\b", lower):
        return "recommendation", 0.9, "Contains conditional action advice."
    if re.search(r"\b(take|accept|choose|decline|reject)\s+[a-z0-9]\b", lower):
        return "recommendation", 0.88, "Contains direct option-selection advice."
    if "do not stay" in lower or "don't stay" in lower:
        return "recommendation", 0.87, "Contains direct stay/leave advice."
    if re.search(r"\b(plan:|tomorrow|this week|decision in \d|i'm going to|i will)\b", lower):
        return "plan", 0.84, "Contains a concrete user plan with timing."
    if lower.startswith("only ") and " after " in lower:
        return "gate", 0.83, "Defines an evidence gate before action."
    if "only if" in lower or "hard gates" in lower or "gates clear" in lower:
        return "gate", 0.82, "Defines a gate before action."
    if "stop-loss" in lower or "reversal trigger" in lower or "revisit" in lower:
        return "reversal_trigger", 0.8, "Defines a future reversal or review condition."
    if re.search(r"\b(should|must|have to|ask for|talk to|inspect|get time with)\b", lower):
        return "recommendation", 0.68, "Contains action-oriented advice."
    return "", 0.0, ""


def _is_non_action_commitment_span(span: str) -> bool:
    lower = span.lower().strip()
    return (
        lower.startswith("i would take back")
        or lower.startswith("i would also delete")
        or lower.startswith("one pressure i would set aside")
        or lower.startswith("so it's not really")
        or lower.startswith("i'm not asking you")
        or "if i'm working 70 hours" in lower
        or "if i take a startup gig" in lower
    )


def _looks_like_user_commitment(span: str) -> bool:
    lower = span.lower()
    return bool(
        re.search(
            r"\b(plan:|i take|i will|i'm going to|decision in \d|tomorrow|this week)\b",
            lower,
        )
    )


def _audit_effect_for_candidate(
    *,
    claim: str,
    source_surface: str,
    revised_text: str,
) -> tuple[str, str]:
    lower_claim = claim.lower()
    lower_revised = revised_text.lower()
    if source_surface == "revised_answer":
        return "post_audit_commitment", ""
    if (
        "wife conversation goes well" in lower_claim
        and "take b" in lower_claim
        and _revised_answer_corrects_spouse_gate(lower_revised)
    ):
        return (
            "corrected",
            (
                "A spouse yes clears one gate; B still requires company-quality, "
                "operating-hours, equity-quality, household-resilience, and stop-loss gates."
            ),
        )
    if (
        "thank you" in lower_claim
        and "proxy" in lower_claim
        and "delete the pseudo-readiness test" in lower_revised
    ):
        return (
            "corrected",
            "The revised answer rejects gratitude as readiness evidence.",
        )
    return "observed", ""


def _revised_answer_corrects_spouse_gate(lower_revised: str) -> bool:
    return any(
        phrase in lower_revised
        for phrase in (
            "clears one gate",
            "necessary, but not sufficient",
            "necessary but not sufficient",
            "not sufficient",
            "too compressed",
            "wife support is real and b passes",
            "spouse support is real and b passes",
        )
    )


def _commitment_classification(
    *,
    claim: str,
    kind: str,
    source_actor: str,
    source_surface: str,
    audit_effect: str,
) -> dict[str, Any]:
    lower = claim.lower()
    semantic_flags = _commitment_semantic_flags(lower)
    return {
        "schema_version": "lolla.commitment_classification.v0.1",
        "actor": source_actor,
        "actor_type": _actor_type(source_actor),
        "kind": kind,
        "source_surface": source_surface,
        "impact": _commitment_impact(lower, kind),
        "reversibility": _commitment_reversibility(lower, kind),
        "evidence_status": _commitment_evidence_status(lower, kind),
        "correction_status": _commitment_correction_status(
            audit_effect=audit_effect,
            source_surface=source_surface,
        ),
        "semantic_flags": semantic_flags,
    }


def _actor_type(source_actor: str) -> str:
    if source_actor == "user":
        return "human"
    if source_actor == "assistant":
        return "ai_assistant"
    return "unknown"


def _commitment_impact(lower_claim: str, kind: str) -> str:
    high_terms = (
        "take b",
        "take a",
        "accept",
        "decline",
        "reject",
        "startup",
        "faang",
        "wife",
        "spouse",
        "marriage",
        "salary",
        "equity",
        "runway",
        "cap table",
        "walk-away",
        "walk away",
    )
    if any(term in lower_claim for term in high_terms):
        return "high"
    if kind in {"recommendation", "plan", "gate", "reversal_trigger"}:
        return "medium"
    return "low"


def _commitment_reversibility(lower_claim: str, kind: str) -> str:
    if any(term in lower_claim for term in ("walk-away", "walk away", "stop-loss", "revisit", "review")):
        return "bounded_reversible"
    if any(term in lower_claim for term in ("only if", "gate", "before signing", "threshold")):
        return "bounded_reversible"
    if any(term in lower_claim for term in ("accept", "sign", "take b", "take a", "decline", "reject")):
        return "costly_reversible"
    if kind == "meta_constraint":
        return "not_applicable"
    return "unknown"


def _commitment_evidence_status(lower_claim: str, kind: str) -> str:
    if any(
        term in lower_claim
        for term in (
            "evidence",
            "diligence",
            "inspect",
            "talk to",
            "ask for",
            "threshold",
            "runway",
            "cap table",
            "employees",
            "ceo",
            "customer",
        )
    ):
        return "evidence_attached_or_requested"
    if kind in {"gate", "reversal_trigger"}:
        return "evidence_required"
    if kind in {"recommendation", "plan"}:
        return "evidence_missing"
    return "not_applicable"


def _commitment_correction_status(*, audit_effect: str, source_surface: str) -> str:
    if source_surface == "revised_answer":
        return "post_audit"
    if audit_effect == "corrected":
        return "corrected"
    return "observed_uncorrected_or_carried_forward"


def _commitment_semantic_flags(lower_claim: str) -> list[str]:
    flags: list[str] = []
    checks = (
        ("conditional_action", r"\b(if|when|only if)\b"),
        ("spouse_or_household", r"\b(wife|spouse|marriage|household|family)\b"),
        ("option_selection", r"\b(take|accept|choose|decline|reject)\s+[abc]\b"),
        ("evidence_gate", r"\b(gate|threshold|evidence|diligence|before signing)\b"),
        ("reversal_or_review", r"\b(stop-loss|reversal|revisit|review|walk-away|walk away)\b"),
        ("startup_quality", r"\b(runway|cap table|equity|ceo|employees|workload)\b"),
    )
    for flag, pattern in checks:
        if re.search(pattern, lower_claim):
            flags.append(flag)
    return flags


def _decision_packet_blockers(result: Mapping[str, Any]) -> list[str]:
    blockers = ["human has not confirmed intent", "outcome has not been reviewed"]
    run_health = _mapping(result.get("run_health"))
    if _text(run_health.get("overall")) in {"degraded", "critical"}:
        blockers.append(f"run health is {_text(run_health.get('overall'))}")
    return blockers


def _conversation_turns(path: Path) -> list[dict[str, Any]]:
    text = _read_text(path)
    if not text:
        return []
    pattern = re.compile(
        r"^\[Turn (?P<turn>\d+)\] (?P<role>USER|ASSISTANT):\n"
        r"(?P<text>.*?)(?=^\[Turn \d+\] (?:USER|ASSISTANT):\n|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    turns: list[dict[str, Any]] = []
    for match in pattern.finditer(text):
        turns.append(
            {
                "turn_index": int(match.group("turn")),
                "role": match.group("role"),
                "text": match.group("text").strip(),
            }
        )
    return turns


def _commitment_spans(text: str) -> list[str]:
    spans: list[str] = []
    for paragraph in _paragraphs(text):
        if _is_high_value_commitment_span(paragraph):
            spans.append(paragraph)
            continue
        for sentence in re.split(r"(?<=[.!?])\s+", paragraph):
            sentence = sentence.strip()
            if sentence:
                spans.append(sentence)
    return spans


def _is_high_value_commitment_span(text: str) -> bool:
    lower = text.lower()
    return (
        "my revised recommendation is" in lower
        or lower.startswith("right. ok. plan:")
        or ("if the wife conversation goes well" in lower and "take b" in lower)
    )


def _paragraphs(text: str) -> list[str]:
    return [paragraph.strip() for paragraph in re.split(r"\n\s*\n", text or "") if paragraph.strip()]


def _user_usefulness_review(run_dir: Path) -> dict[str, Any]:
    path = run_dir / "user_usefulness_review.json"
    if not path.exists():
        return {
            "schema_version": "lolla.user_usefulness_review.v0.1",
            "status": "not_collected",
            "artifact_path": "",
            "rating": None,
            "helped_change_view": None,
            "would_reuse": None,
        }
    payload = _read_json_object(path)
    if not payload:
        return {
            "schema_version": "lolla.user_usefulness_review.v0.1",
            "status": "invalid",
            "artifact_path": "user_usefulness_review.json",
            "rating": None,
            "helped_change_view": None,
            "would_reuse": None,
        }
    return {
        "schema_version": _text(payload.get("schema_version"))
        or "lolla.user_usefulness_review.v0.1",
        "status": _text(payload.get("status")) or "collected",
        "artifact_path": "user_usefulness_review.json",
        "rating": payload.get("rating"),
        "helped_change_view": payload.get("helped_change_view"),
        "would_reuse": payload.get("would_reuse"),
        "most_useful_component": _text(payload.get("most_useful_component")),
        "least_useful_component": _text(payload.get("least_useful_component")),
        "reviewed_at": _text(payload.get("reviewed_at")),
    }


def _outcome_reviews(run_dir: Path) -> list[dict[str, Any]]:
    path = run_dir / "outcome_review.json"
    if not path.exists():
        return []
    payload = _read_json_object(path)
    raw_reviews = payload.get("reviews") if isinstance(payload.get("reviews"), list) else None
    if raw_reviews is None:
        raw_reviews = [payload] if payload else []
    reviews: list[dict[str, Any]] = []
    for index, raw_review in enumerate(raw_reviews):
        review = _mapping(raw_review)
        if not review:
            continue
        reviews.append(
            {
                "schema_version": _text(review.get("schema_version"))
                or "lolla.outcome_review.v0.1",
                "review_id": _text(review.get("review_id")) or f"outcome_review_{index + 1:03d}",
                "status": _text(review.get("status")) or "collected",
                "artifact_path": "outcome_review.json",
                "reviewed_at": _text(review.get("reviewed_at")),
                "outcome_status": _text(review.get("outcome_status")),
                "decision_taken": _text(review.get("decision_taken")),
                "surprise_count": _safe_int(review.get("surprise_count")),
                "suppressed_lens_relevance": _text(review.get("suppressed_lens_relevance")),
                "usefulness_rating": review.get("usefulness_rating"),
            }
        )
    return reviews


def _outcome_review_state(*, outcome_reviews: Sequence[Mapping[str, Any]], run_dir: Path) -> dict[str, Any]:
    path = run_dir / "outcome_review.json"
    return {
        "schema_version": "lolla.outcome_review_state.v0.1",
        "status": "available" if outcome_reviews else "not_started",
        "review_count": len(outcome_reviews),
        "artifact_path": "outcome_review.json" if path.exists() else "",
    }


def _trace_adequacy(
    *,
    run_dir: Path,
    extraction: Mapping[str, Any],
    result: Mapping[str, Any],
    reasoning_lenses: Sequence[Mapping[str, Any]],
    model_calls: Sequence[Mapping[str, Any]],
    candidate_commitments: Sequence[Mapping[str, Any]],
    outcome_reviews: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    run_health = _mapping(result.get("run_health"))
    capture = _capture_summary(extraction=extraction, result=result)
    capture_health = _text(capture.get("capture_health")) or "unknown"
    overall_health = _text(run_health.get("overall")) or "unknown"
    live_output_health = _text(run_health.get("live_output_health")) or "unknown"
    product_output_health = _text(run_health.get("product_output_health")) or "unknown"
    core = {
        "source_conversation": _artifact_status(run_dir / "conversation.txt"),
        "decision_structure": _artifact_status(run_dir / "extraction.json"),
        "pipeline_result": _artifact_status(run_dir / "result.json"),
        "revised_answer": _artifact_status(run_dir / "revised.txt"),
        "decision_memo": _artifact_status(run_dir / "memo.md"),
        "reasoning_lenses": "present" if reasoning_lenses else "missing",
        "model_call_telemetry": "present" if model_calls else "missing",
    }
    missing_context: list[str] = []
    for label, status in core.items():
        if status == "missing" and label in {
            "source_conversation",
            "decision_structure",
            "pipeline_result",
        }:
            missing_context.append(f"{label} artifact is missing")
    if capture_health in {"critical", "degraded", "unknown"}:
        missing_context.append(f"capture_health is {capture_health}")
    if overall_health in {"critical", "degraded"}:
        missing_context.append(f"run_health.overall is {overall_health}")
    if product_output_health == "unsafe":
        missing_context.append("product output hygiene is unsafe")
    if live_output_health in {"unsafe", "not_checked"}:
        missing_context.append(f"live_output_health is {live_output_health}")
    if not reasoning_lenses:
        missing_context.append("no reasoning lens route data was extracted")

    core_missing = any(
        core[key] == "missing"
        for key in ("source_conversation", "decision_structure", "pipeline_result")
    )
    if core_missing or capture_health == "critical":
        status = "insufficient"
    elif missing_context:
        status = "thin"
    else:
        status = "sufficient"

    return {
        "schema_version": "lolla.trace_adequacy.v0.1",
        "status": status,
        "future_review_ready": status == "sufficient",
        "error_analysis_ready": not core_missing and capture_health != "critical",
        "coverage": core,
        "missing_context": missing_context,
        "commitment_detection": {
            "status": "heuristic_v0",
            "candidate_count": len(candidate_commitments),
            "escalation_recommended_count": sum(
                1 for item in candidate_commitments if item.get("escalation_recommended")
            ),
        },
        "outcome_review": {
            "status": "available" if outcome_reviews else "not_started",
            "review_count": len(outcome_reviews),
        },
    }


def _artifact_status(path: Path) -> str:
    return "present" if path.exists() and path.is_file() else "missing"


def _append_unique(values: list[Any], value: Any) -> None:
    if value and value not in values:
        values.append(value)


def _read_text(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _normalize_surface_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _normalize_candidate_text(value: str) -> str:
    return re.sub(r"\W+", " ", (value or "").lower()).strip()


def _bounded_text(value: str, *, limit: int) -> str:
    value = _normalize_surface_text(value)
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"


def _first_string(value: Any) -> str:
    values = _list(value)
    for item in values:
        text = _text(item)
        if text:
            return text
    return ""


def _scaled_count(value: Any, numerator: int, denominator: int) -> int:
    raw = _safe_int(value)
    if raw <= 0 or numerator <= 0 or denominator <= 0:
        return 0
    if numerator == denominator:
        return raw
    return round(raw * (numerator / denominator))


def _text(value: Any) -> str:
    return str(value or "").strip()


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0
