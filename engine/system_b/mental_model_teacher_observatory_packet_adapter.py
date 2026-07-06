"""Read-only Observatory adapter for Teacher learning packets.

The adapter maps a selected Observatory case to a checked-in Teacher learning
packet and returns tab-ready payloads. It does not render UI, call providers,
create Lolla runs, mutate archives, or wire Lolla runtime behavior.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .mental_model_teacher_observatory_learning_packet import (
    LEARNING_PACKET_SCHEMA_VERSION,
    PRIMARY_TABS,
    REQUIRED_PACKET_NON_CLAIMS,
    validate_learning_packet,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PACKET_PACKAGE_DIR = (
    REPO_ROOT / "docs/product/mental-model-teacher-observatory-learning-packets-v0"
)
TEACHER_LEARNING_ADAPTER_SCHEMA_VERSION = (
    "lolla.observatory_teacher.learning_packet_adapter.v0"
)
ADVANCED_SURFACE = "Advanced"


class MentalModelTeacherObservatoryPacketAdapterError(ValueError):
    """Raised when the checked-in Teacher packet package is malformed."""


def build_teacher_learning_response(
    selected_case_id: str,
    result: dict[str, Any] | None = None,
    result_path: Path | None = None,
    *,
    package_dir: Path | str = DEFAULT_PACKET_PACKAGE_DIR,
) -> dict[str, Any]:
    """Return an Observatory-safe Teacher learning response for one case."""

    package_path = Path(package_dir)
    context = _selected_case_context(selected_case_id, result, result_path)
    packet, packet_path, matched_by = _find_packet(package_path, context)
    if packet is None:
        return _unavailable_response(
            context,
            unavailable_reason="no_teacher_learning_packet_for_selected_case",
        )
    return _available_response(
        context=context,
        packet=packet,
        packet_path=packet_path,
        matched_by=matched_by,
    )


def build_teacher_learning_case_summary(
    selected_case_id: str,
    result: dict[str, Any] | None = None,
    result_path: Path | None = None,
    *,
    package_dir: Path | str = DEFAULT_PACKET_PACKAGE_DIR,
) -> dict[str, Any]:
    """Return a compact availability summary for the selected case payload."""

    response = build_teacher_learning_response(
        selected_case_id,
        result,
        result_path,
        package_dir=package_dir,
    )
    if not response["available"]:
        return {
            "available": False,
            "unavailable_reason": response["unavailable_reason"],
            "observatory_tabs": response["observatory_tabs"],
            "default_tab": response["default_tab"],
        }
    return {
        "available": True,
        "packet_id": response["packet_id"],
        "run_ref": response["run_ref"],
        "observatory_tabs": response["observatory_tabs"],
        "default_tab": response["default_tab"],
        "lesson_summary": response["tab_payloads"]["Outcome"]["lesson_summary"],
        "model_count": response["packet_summary"]["model_count"],
        "relation_count": response["packet_summary"]["relation_count"],
        "graph_node_count": response["packet_summary"]["graph_node_count"],
        "graph_edge_count": response["packet_summary"]["graph_edge_count"],
    }


def _available_response(
    *,
    context: dict[str, str],
    packet: dict[str, Any],
    packet_path: Path,
    matched_by: str,
) -> dict[str, Any]:
    lesson = packet["lesson"]
    models = packet["models"]
    relations = packet["relations"]
    graph = packet["graph"]
    receipts = packet["receipts"]
    advanced_artifacts = [
        artifact
        for artifact in receipts["artifact_refs"]
        if artifact["home_tab"] == ADVANCED_SURFACE
    ]
    summary = {
        "case_id": packet["run_ref"]["case_id"],
        "run_id": packet["run_ref"]["run_id"],
        "thinking_move": lesson["thinking_move"],
        "model_count": len(models),
        "relation_count": len(relations),
        "graph_node_count": len(graph["nodes"]),
        "graph_edge_count": len(graph["edges"]),
        "human_review_status": lesson["human_review_status"],
    }
    response = {
        "schema_version": TEACHER_LEARNING_ADAPTER_SCHEMA_VERSION,
        "available": True,
        "packet_id": packet["packet_id"],
        "packet_schema": packet["schema_version"],
        "packet_ref": _repo_rel(packet_path),
        "requested_case_id": context["selected_case_id"],
        "selected_run_id": context["selected_run_id"],
        "matched_by": matched_by,
        "run_ref": packet["run_ref"],
        "observatory_tabs": packet["observatory_tabs"],
        "default_tab": packet["default_tab"],
        "packet_summary": summary,
        "tab_payloads": {
            "Outcome": {
                "teacher_learning_available": True,
                "lesson_summary": {
                    "case_anchor": lesson["case_anchor"],
                    "thinking_move": lesson["thinking_move"],
                    "model_ids": [item["model_id"] for item in lesson["model_stack"]],
                    "relation_ids": [
                        relation["relation_id"] for relation in relations
                    ],
                    "practice_prompt": lesson["practice_rep"]["prompt"],
                },
                "single_home_note": (
                    "Outcome owns revised answer and structural pressure; "
                    "Teacher reasoning move lives in Learn."
                ),
            },
            "Learn": {
                "lesson": lesson,
            },
            "Models": {
                "models": models,
            },
            "Relations": {
                "relations": relations,
            },
            "Map": {
                "graph": graph,
            },
            "Receipts": {
                "receipts": receipts,
                "missingness": packet["missingness"],
                "non_claims": packet["non_claims"],
            },
        },
        "advanced": {
            "available": bool(advanced_artifacts),
            "surface": ADVANCED_SURFACE,
            "artifact_refs": advanced_artifacts,
            "note": (
                "Advanced artifacts are reachable for inspection but are not "
                "primary learning-tab copy."
            ),
        },
        "single_home_rules": packet["single_home_rules"],
        "visibility_policy": packet["visibility_policy"],
        "missingness": packet["missingness"],
        "non_claims": packet["non_claims"],
        "product_proof": False,
        "human_validated": False,
        "runtime_integration_authorized": False,
        "provider_or_model_calls_used": False,
    }
    _assert_primary_tabs_are_clean(response)
    _assert_no_local_paths(response)
    return response


def _unavailable_response(
    context: dict[str, str],
    *,
    unavailable_reason: str,
) -> dict[str, Any]:
    response = {
        "schema_version": TEACHER_LEARNING_ADAPTER_SCHEMA_VERSION,
        "available": False,
        "requested_case_id": context["selected_case_id"],
        "selected_run_id": context["selected_run_id"],
        "unavailable_reason": unavailable_reason,
        "observatory_tabs": list(PRIMARY_TABS),
        "default_tab": "Outcome",
        "tab_payloads": {},
        "advanced": {
            "available": False,
            "surface": ADVANCED_SURFACE,
            "artifact_refs": [],
        },
        "missingness": {
            "status": "missing",
            "missing_fields": ["teacher_learning_packet"],
            "notes": [
                "No checked-in Teacher learning packet matched the selected Observatory case."
            ],
        },
        "non_claims": sorted(REQUIRED_PACKET_NON_CLAIMS),
        "product_proof": False,
        "human_validated": False,
        "runtime_integration_authorized": False,
        "provider_or_model_calls_used": False,
    }
    _assert_no_local_paths(response)
    return response


def _find_packet(
    package_dir: Path,
    context: dict[str, str],
) -> tuple[dict[str, Any] | None, Path, str]:
    manifest_path = package_dir / "manifest.json"
    if not manifest_path.is_file():
        return None, manifest_path, ""
    manifest = _load_json_object(manifest_path)
    entries = manifest.get("packets")
    if not isinstance(entries, list):
        raise MentalModelTeacherObservatoryPacketAdapterError(
            "Teacher learning packet manifest packets must be a list"
        )

    selected_case = context["selected_case_slug"]
    selected_run_id = context["selected_run_id"]
    fallback: tuple[dict[str, Any], Path, str] | None = None
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            continue
        packet_path = (package_dir / entry["path"]).resolve()
        _assert_inside(package_dir.resolve(), packet_path)
        packet = validate_learning_packet(_load_json_object(packet_path))
        run_ref = packet["run_ref"]
        case_matches = bool(selected_case and run_ref["case_id"] == selected_case)
        run_matches = bool(selected_run_id and run_ref["run_id"] == selected_run_id)
        if case_matches and run_matches:
            return packet, packet_path, "case_id_and_run_id"
        if run_matches:
            fallback = (packet, packet_path, "run_id")
        elif case_matches and fallback is None:
            fallback = (packet, packet_path, "case_id")

    if fallback is not None:
        return fallback
    return None, manifest_path, ""


def _selected_case_context(
    selected_case_id: str,
    result: dict[str, Any] | None,
    result_path: Path | None,
) -> dict[str, str]:
    archive_case_slug, archive_run_id = _parse_archive_case_id(selected_case_id)
    run_id = _run_id_from_result(result) or archive_run_id
    if not run_id and result_path is not None:
        run_id = result_path.parent.name
    selected_case_slug = archive_case_slug or selected_case_id
    return {
        "selected_case_id": selected_case_id,
        "selected_case_slug": selected_case_slug,
        "selected_run_id": run_id,
    }


def _parse_archive_case_id(case_id: str) -> tuple[str, str]:
    if not case_id.startswith("archive:"):
        return "", ""
    parts = case_id.split(":", 2)
    if len(parts) != 3:
        return "", ""
    return parts[1], parts[2]


def _run_id_from_result(result: dict[str, Any] | None) -> str:
    if not isinstance(result, dict):
        return ""
    usage = result.get("usage_summary")
    if isinstance(usage, dict) and usage.get("run_id"):
        return str(usage["run_id"])
    run_id = result.get("run_id")
    if isinstance(run_id, str):
        return run_id
    return ""


def _load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MentalModelTeacherObservatoryPacketAdapterError(
            f"Teacher learning packet JSON is malformed: {_repo_rel(path)}"
        ) from exc
    except OSError as exc:
        raise MentalModelTeacherObservatoryPacketAdapterError(
            f"Teacher learning packet JSON could not be read: {_repo_rel(path)}"
        ) from exc
    if not isinstance(payload, dict):
        raise MentalModelTeacherObservatoryPacketAdapterError(
            f"Teacher learning packet JSON root must be an object: {_repo_rel(path)}"
        )
    return payload


def _assert_primary_tabs_are_clean(response: dict[str, Any]) -> None:
    tab_payloads = response["tab_payloads"]
    for tab_name in ("Outcome", "Learn", "Models", "Relations", "Map"):
        rendered = json.dumps(tab_payloads.get(tab_name, {}), sort_keys=True)
        if "artifact_refs" in rendered:
            raise MentalModelTeacherObservatoryPacketAdapterError(
                f"{tab_name} must not own receipt artifact_refs"
            )
        if "usage_summary" in rendered or "audit_summary" in rendered:
            raise MentalModelTeacherObservatoryPacketAdapterError(
                f"{tab_name} must not expose raw telemetry"
            )


def _assert_inside(root: Path, path: Path) -> None:
    if root != path and root not in path.parents:
        raise MentalModelTeacherObservatoryPacketAdapterError(
            "Teacher learning packet path escaped package directory"
        )


def _repo_rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.name


def _assert_no_local_paths(payload: Any) -> None:
    rendered = json.dumps(payload, sort_keys=True) if not isinstance(payload, str) else payload
    markers = (
        "/" + "Users/",
        "Desktop/" + "Apps",
        "\\" + "Users\\",
    )
    if any(marker in rendered for marker in markers):
        raise MentalModelTeacherObservatoryPacketAdapterError(
            "Teacher learning adapter response contains a local path marker"
        )


__all__ = [
    "DEFAULT_PACKET_PACKAGE_DIR",
    "LEARNING_PACKET_SCHEMA_VERSION",
    "TEACHER_LEARNING_ADAPTER_SCHEMA_VERSION",
    "MentalModelTeacherObservatoryPacketAdapterError",
    "build_teacher_learning_case_summary",
    "build_teacher_learning_response",
]
