"""Offline builder for Observatory Teacher learning packets.

This module translates checked-in Teacher product artifacts into the selected-run
learning packet contract used by Observatory. It does not alter Observatory,
render UI, call providers, run Lolla, create runs, or wire runtime behavior.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .mental_model_teacher_observatory_learning_packet import (
    LEARNING_PACKET_SCHEMA_VERSION,
    PRIMARY_TABS,
    REQUIRED_PACKET_NON_CLAIMS,
    REQUIRED_SINGLE_HOME_RULES,
    REQUIRED_VISIBILITY_POLICY,
    validate_learning_packet,
)
from .mental_model_teacher_pilot_page_builder import REPO_ROOT, build_pilot_page_data
from .mental_model_teacher_product_contracts import (
    RELATION_NON_CLAIMS,
    RELATION_PAGE_SCHEMA_VERSION,
    validate_mental_model_page,
    validate_relation_page,
)
from .mental_model_teacher_three_case_product_pilot import (
    CASE_IDS,
    HIGH_RISK_CASES,
    SOURCE_ROOT,
    build_lesson_graph,
    build_lesson_product,
    load_case_source,
)


DEFAULT_OUTPUT_DIR = (
    REPO_ROOT / "docs/product/mental-model-teacher-observatory-learning-packets-v0"
)
LEARNING_PACKET_BUILDER_MANIFEST_SCHEMA_VERSION = (
    "lolla.observatory_teacher.learning_packet_builder_manifest.v0"
)


class MentalModelTeacherLearningPacketBuilderError(ValueError):
    """Raised when a learning packet cannot be built safely."""


def build_observatory_learning_packet(
    root: Path | str | None = None,
    *,
    case_id: str = CASE_IDS[0],
) -> dict[str, Any]:
    """Build one selected-run Teacher learning packet from checked-in artifacts."""

    repo_root = Path(root) if root is not None else REPO_ROOT
    source_root = repo_root / "reviews/codex-assisted/mental-model-teacher-knowledge-mesh-v2"
    if case_id not in CASE_IDS:
        raise MentalModelTeacherLearningPacketBuilderError(
            f"unsupported Teacher case_id: {case_id}"
        )

    case = load_case_source(case_id, source_root)
    lesson = build_lesson_product(case)
    model_ids = _ordered_model_ids(lesson)
    model_pages = [
        validate_mental_model_page(page)
        for page in build_pilot_page_data(repo_root, model_ids=tuple(model_ids))[
            "model_pages"
        ]
    ]
    relation_page = _build_relation_page(repo_root, case)
    graph = build_lesson_graph(case, lesson)

    packet = {
        "schema_version": LEARNING_PACKET_SCHEMA_VERSION,
        "packet_id": f"{case_id}-observatory-teacher-learning-packet",
        "run_ref": _run_ref(repo_root, case),
        "observatory_tabs": list(PRIMARY_TABS),
        "default_tab": "Outcome",
        "lesson": lesson,
        "models": model_pages,
        "relations": [relation_page],
        "graph": graph,
        "receipts": _build_receipts(repo_root, case, lesson, model_pages, graph),
        "single_home_rules": dict(REQUIRED_SINGLE_HOME_RULES),
        "visibility_policy": dict(REQUIRED_VISIBILITY_POLICY),
        "missingness": _packet_missingness(case_id, lesson, model_pages, graph),
        "non_claims": sorted(REQUIRED_PACKET_NON_CLAIMS),
        "product_proof": False,
        "human_validated": False,
        "runtime_integration_authorized": False,
        "provider_or_model_calls_used": False,
    }
    return validate_learning_packet(packet)


def write_observatory_learning_packet_package(
    root: Path | str | None = None,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    *,
    case_ids: tuple[str, ...] = CASE_IDS,
) -> dict[str, Any]:
    """Write learning packets and a package manifest for the current pilot cases."""

    repo_root = Path(root) if root is not None else REPO_ROOT
    target_dir = Path(output_dir)
    packets_dir = target_dir / "packets"
    packet_entries: list[dict[str, Any]] = []

    for case_id in case_ids:
        packet = build_observatory_learning_packet(repo_root, case_id=case_id)
        packet_path = packets_dir / f"{case_id}.learning-packet.json"
        _write_json(packet_path, packet)
        packet_entries.append(
            {
                "case_id": case_id,
                "packet_id": packet["packet_id"],
                "path": _rel(packet_path, target_dir),
                "run_id": packet["run_ref"]["run_id"],
                "default_tab": packet["default_tab"],
                "model_count": len(packet["models"]),
                "relation_count": len(packet["relations"]),
                "graph_node_count": len(packet["graph"]["nodes"]),
                "graph_edge_count": len(packet["graph"]["edges"]),
                "high_risk_case": case_id in HIGH_RISK_CASES,
            }
        )

    manifest = {
        "schema_version": LEARNING_PACKET_BUILDER_MANIFEST_SCHEMA_VERSION,
        "builder": (
            "engine.system_b."
            "mental_model_teacher_observatory_learning_packet_builder"
        ),
        "source_root": _repo_rel(SOURCE_ROOT, repo_root),
        "output_dir": _safe_output_dir(target_dir, repo_root),
        "packet_schema": LEARNING_PACKET_SCHEMA_VERSION,
        "status": "observatory_teacher_learning_packets_ready_for_adapter",
        "packet_count": len(packet_entries),
        "packets": packet_entries,
        "observatory_tabs": list(PRIMARY_TABS),
        "default_tab": "Outcome",
        "single_home_rules_applied": True,
        "visibility_policy_applied": True,
        "canonical_model_pages_built": True,
        "relation_pages_built": True,
        "graph_objects_built": True,
        "observatory_endpoint_built": False,
        "observatory_ui_built": False,
        "runtime_integration_authorized": False,
        "provider_or_model_calls_used": False,
        "product_proof": False,
        "human_validated": False,
        "non_claims": {
            "product_proof": False,
            "human_validated": False,
            "answer_correctness": False,
            "advice_correctness": False,
            "runtime_integration_authorized": False,
            "graph_edges_are_proof": False,
            "embedding_similarity_is_validated_relation_semantics": False,
            "agent_or_automatic_action_authorized": False,
        },
        "missingness": {
            "status": "partial",
            "missing_fields": [
                "observatory_endpoint",
                "observatory_ui_mount",
                "selected_run_data_adapter",
                "human_review",
            ],
            "notes": [
                "This package writes contract-valid packets only.",
                "It does not mount packets in Observatory or change runtime behavior.",
            ],
        },
        "decision_gate": "proceed_to_observatory_teacher_packet_adapter",
        "stop_before": [
            "Observatory endpoints",
            "Observatory UI",
            "runtime integration",
            "provider or model calls",
            "live Lolla runs",
            "product proof claims",
            "human validation claims",
        ],
    }
    _assert_no_local_paths(manifest)
    _write_json(target_dir / "manifest.json", manifest)
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build offline Observatory Teacher learning packets.",
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--case-id",
        choices=CASE_IDS,
        help="Build a single case packet instead of the three-case package.",
    )
    args = parser.parse_args(argv)

    if args.case_id:
        packet = build_observatory_learning_packet(args.root, case_id=args.case_id)
        print(json.dumps(packet, indent=2, sort_keys=True))
        return 0

    manifest = write_observatory_learning_packet_package(
        args.root,
        args.output_dir,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _build_relation_page(root: Path, case: dict[str, Any]) -> dict[str, Any]:
    relation_doc = case["relation"]
    relation = relation_doc["relation"]
    sections = relation_doc.get("sections", {})
    relation_path = case["case_dir"] / "mental_model_teacher_relation_deep_dive.json"
    relation_type = _normalize_relation_type(str(relation["relation_type"]))
    page = {
        "schema_version": RELATION_PAGE_SCHEMA_VERSION,
        "relation_id": relation["relation_id"],
        "source_model_id": relation["source_model_id"],
        "target_model_id": relation["target_model_id"],
        "relation_type": relation_type,
        "plain_language_story": _clean(relation["teaching_value"]),
        "why_it_matters": _teaching_paragraph(
            _section_body(sections, "why_these_two_lenses_meet"),
            markers=("Teach this before the label:", "Plain teaching:"),
        ),
        "misread_risk": _teaching_paragraph(
            _section_body(sections, "when_this_pair_misleads"),
            markers=("misleads when", "This pair misleads"),
        ),
        "practice_prompt": _section_body(sections, "practice"),
        "source_quote_or_ref": f"{_repo_rel(relation_path, root)}:relation",
        "confidence": _relation_confidence(relation),
        "curation_status": _relation_curation_status(relation),
        "missingness": {
            "status": "partial",
            "missing_fields": [
                "human_review",
                "observatory_relation_page_route",
            ],
            "notes": [
                "Built from Teacher relation deep-dive source and reviewed relation graph provenance when present.",
                "Confidence is an exposure hint, not proof or certification.",
            ],
        },
        "non_claims": sorted(RELATION_NON_CLAIMS),
    }
    return validate_relation_page(page)


def _run_ref(root: Path, case: dict[str, Any]) -> dict[str, str]:
    lesson_source = case["case_dir"] / "mental_model_teacher_lesson.json"
    return {
        "run_id": case["lesson"]["run_id"],
        "case_id": case["case_id"],
        "source": "archive",
        "result_ref": _repo_rel(lesson_source, root),
    }


def _build_receipts(
    root: Path,
    case: dict[str, Any],
    lesson: dict[str, Any],
    model_pages: list[dict[str, Any]],
    graph: dict[str, Any],
) -> dict[str, Any]:
    source_refs = _unique_refs(
        list(lesson["source_refs"])
        + [ref for page in model_pages for ref in page["source_refs"]]
        + [
            {
                "source_id": artifact["artifact_id"],
                "path": artifact["path"],
                "source_type": artifact["source_type"],
            }
            for artifact in graph["source_artifacts"]
        ]
    )
    receipts = {
        "source_refs": source_refs,
        "artifact_refs": _case_artifact_refs(root, case),
        "missingness": {
            "status": "partial",
            "missing_fields": [
                "live_observatory_run_binding",
                "human_review",
                "usage_cost_telemetry_home_is_advanced_only",
            ],
            "notes": [
                "Receipts provide custody and missingness, not proof of answer or advice correctness.",
                "Advanced audit artifacts are present as advanced-only references.",
            ],
        },
        "non_claims": [
            "not_product_proof",
            "not_human_validation",
            "receipts_are_custody_not_proof",
        ],
    }
    return receipts


def _case_artifact_refs(root: Path, case: dict[str, Any]) -> list[dict[str, str]]:
    receipt_files = (
        "mental_model_teacher_lesson.json",
        "mental_model_teacher_card.md",
        "mental_model_teacher.md",
        "mental_model_teacher_model_deep_dive.json",
        "mental_model_teacher_relation_deep_dive.json",
        "mental_model_teacher_practice_lab.json",
    )
    advanced_files = (
        "case_review.json",
        "mental_model_canonical_manifest.json",
        "mental_model_teacher_anti_duplication.json",
        "mental_model_teacher_claim_grounding.json",
        "mental_model_teacher_context_trace.json",
        "mental_model_teacher_grounding_audit.json",
        "mental_model_teacher_okf_conformance.json",
        "mental_model_teacher_okf_manifest.json",
        "mental_model_teacher_read_plan.json",
        "mental_model_teacher_render_lint.json",
        "mental_model_teacher_role_map.json",
        "mental_model_teacher_sentinel_audit.json",
    )
    refs = [
        _artifact_ref(root, case, filename, "Receipts", "receipts")
        for filename in receipt_files
    ]
    refs.extend(
        _artifact_ref(root, case, filename, "Advanced", "advanced_only")
        for filename in advanced_files
        if (case["case_dir"] / filename).exists()
    )
    return refs


def _artifact_ref(
    root: Path,
    case: dict[str, Any],
    filename: str,
    home_tab: str,
    exposure: str,
) -> dict[str, str]:
    path = case["case_dir"] / filename
    artifact_type = "teacher_source" if home_tab == "Receipts" else "teacher_audit"
    return {
        "artifact_id": f"{case['case_id']}:{Path(filename).stem}",
        "artifact_type": artifact_type,
        "path": _repo_rel(path, root),
        "home_tab": home_tab,
        "exposure": exposure,
    }


def _packet_missingness(
    case_id: str,
    lesson: dict[str, Any],
    model_pages: list[dict[str, Any]],
    graph: dict[str, Any],
) -> dict[str, Any]:
    fields = {
        "selected_run_outcome_binding",
    }
    fields.update(lesson["missingness"].get("missing_fields") or [])
    fields.update(graph["missingness"].get("missing_fields") or [])
    for page in model_pages:
        fields.update(page["missingness"].get("missing_fields") or [])

    notes = [
        "Learning packet powers the Observatory Learn surface when a matching selected run is available; it remains offline review material, not runtime integration.",
        "Model pages are translated product objects, not raw canonical Markdown dumps.",
        "Telemetry and review/audit artifacts are Receipts or Advanced material, not primary learning copy.",
    ]
    if case_id in HIGH_RISK_CASES:
        notes.append(
            "High-risk case: preserve legal, HR, governance, interpersonal, answer, and advice non-claims."
        )
    return {
        "status": "partial",
        "missing_fields": sorted(fields),
        "notes": notes,
    }


def _ordered_model_ids(lesson: dict[str, Any]) -> list[str]:
    seen = set()
    result = []
    for item in lesson["model_stack"]:
        model_id = str(item["model_id"])
        if model_id not in seen:
            seen.add(model_id)
            result.append(model_id)
    return result


def _relation_confidence(relation: dict[str, Any]) -> str:
    provenance = relation.get("provenance")
    if isinstance(provenance, dict) and provenance.get("reviewed_relation_graph_edge"):
        return "medium"
    return "unknown"


def _relation_curation_status(relation: dict[str, Any]) -> str:
    provenance = relation.get("provenance")
    if isinstance(provenance, dict) and provenance.get("reviewed_relation_graph_edge"):
        return "reviewed"
    return "draft"


def _normalize_relation_type(value: str) -> str:
    if value == "structured_tension":
        return "tension"
    return value


def _section_body(sections: dict[str, Any], key: str) -> str:
    section = sections.get(key)
    if not isinstance(section, dict):
        raise MentalModelTeacherLearningPacketBuilderError(
            f"missing relation section: {key}"
        )
    return _clean(section.get("body"))


def _teaching_paragraph(body: str, *, markers: tuple[str, ...]) -> str:
    paragraphs = [item.strip() for item in body.split("\n\n") if item.strip()]
    for marker in markers:
        for paragraph in paragraphs:
            if marker.lower() in paragraph.lower():
                return _strip_teaching_prefix(paragraph)
    if paragraphs:
        return _strip_teaching_prefix(paragraphs[0])
    raise MentalModelTeacherLearningPacketBuilderError(
        "relation section had no usable body"
    )


def _strip_teaching_prefix(value: str) -> str:
    for prefix in ("Teach this before the label:", "Plain teaching:"):
        if value.startswith(prefix):
            return value.removeprefix(prefix).strip()
    return value


def _unique_refs(refs: list[dict[str, Any]]) -> list[dict[str, str]]:
    seen = set()
    result = []
    for ref in refs:
        key = (str(ref["source_id"]), str(ref["path"]), str(ref["source_type"]))
        if key in seen:
            continue
        seen.add(key)
        result.append(
            {
                "source_id": key[0],
                "path": key[1],
                "source_type": key[2],
            }
        )
    return result


def _repo_rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise MentalModelTeacherLearningPacketBuilderError(
            "path must stay inside the repository"
        ) from exc


def _safe_output_dir(path: Path, root: Path) -> str:
    try:
        return _repo_rel(path, root)
    except MentalModelTeacherLearningPacketBuilderError:
        return path.name


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.name


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _assert_no_local_paths(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _clean(value: Any) -> str:
    return str(value).replace("\r", " ").strip()


def _assert_no_local_paths(payload: Any) -> None:
    rendered = json.dumps(payload, sort_keys=True) if not isinstance(payload, str) else payload
    markers = (
        "/" + "Users/",
        "Desktop/" + "Apps",
        "\\" + "Users\\",
    )
    if any(marker in rendered for marker in markers):
        raise MentalModelTeacherLearningPacketBuilderError(
            "learning packet builder output contains a local path marker"
        )


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
