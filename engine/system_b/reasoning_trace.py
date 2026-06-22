"""Archive-time ReasoningTrace manifest builder.

This module turns an archived Lolla run directory into a local custody
manifest. It deliberately indexes raw artifacts by path and hash rather than
duplicating conversation or memo text into the trace itself.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


REASONING_TRACE_SCHEMA_VERSION = "lolla.reasoning_trace.v0.2"
REASONING_TRACE_FILENAME = "reasoning_trace.json"

ARTIFACT_ROLES: dict[str, str] = {
    "conversation.txt": "source_conversation",
    "extraction.json": "decision_structure",
    "result.json": "pipeline_result",
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
    "live_transcript.txt": "live_product_surface",
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
    artifacts = _artifact_records(run_dir=run_dir, filenames=files_copied)
    missing_artifacts = _missing_artifact_records(files_missing)
    reasoning_lenses = _reasoning_lenses(result)
    model_calls = _model_calls(result)

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
            "raw_transcript_saved": (run_dir / "conversation.txt").exists(),
            "summary_saved": bool(extraction),
            "retention_days": None,
            "raw_text_duplicated_in_trace": False,
            "external_egress_by_trace_builder": False,
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
            "run_health": _mapping(result.get("run_health")),
            "audit_summary": _audit_summary(result),
            "pressure_check": _pressure_check(result),
            "private_custody": _private_custody(result=result, run_dir=run_dir),
            "usage": _usage_summary(result),
        },
        "artifacts": artifacts,
        "missing_artifacts": missing_artifacts,
        "reasoning_lenses": reasoning_lenses,
        "trace_adequacy": _trace_adequacy(
            run_dir=run_dir,
            extraction=extraction,
            result=result,
            reasoning_lenses=reasoning_lenses,
            model_calls=model_calls,
        ),
        "candidate_commitments": [],
        "decision_packets": [],
        "outcome_reviews": [],
        "model_calls": model_calls,
        "tool_calls": [],
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
    return {
        "capture_health": capture_health or "unknown",
        "capture_manifest": dict(capture_manifest),
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
    return {
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
    }


def _usage_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    usage = _mapping(result.get("usage_summary"))
    vendors = _mapping(usage.get("vendors"))
    vendor_calls: dict[str, int] = {}
    for vendor_name, raw_vendor in vendors.items():
        vendor = _mapping(raw_vendor)
        vendor_calls[str(vendor_name)] = _safe_int(vendor.get("calls"))
    return {
        "run_id": str(usage.get("run_id") or ""),
        "pricing_table_version": str(usage.get("pricing_table_version") or ""),
        "estimated_total_cost_usd": usage.get("estimated_total_cost_usd"),
        "cost_estimate_state": str(usage.get("cost_estimate_state") or ""),
        "vendor_calls": vendor_calls,
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
    calls: list[dict[str, Any]] = []
    for index, raw_call in enumerate(_list(audit.get("boundary_calls"))):
        call = _mapping(raw_call)
        calls.append(
            {
                "index": index,
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
    return calls


def _trace_adequacy(
    *,
    run_dir: Path,
    extraction: Mapping[str, Any],
    result: Mapping[str, Any],
    reasoning_lenses: Sequence[Mapping[str, Any]],
    model_calls: Sequence[Mapping[str, Any]],
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
            "status": "not_implemented",
            "candidate_count": 0,
        },
        "outcome_review": {
            "status": "not_started",
            "review_count": 0,
        },
    }


def _artifact_status(path: Path) -> str:
    return "present" if path.exists() and path.is_file() else "missing"


def _append_unique(values: list[Any], value: Any) -> None:
    if value and value not in values:
        values.append(value)


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
