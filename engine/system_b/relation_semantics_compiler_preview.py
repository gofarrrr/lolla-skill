from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

from system_b.relation_semantics import (
    build_relation_semantics_delta_report,
    build_relation_semantics_preview,
    load_relation_semantics,
)


REVIEW_FIELD_NAME = "relation_semantics_review"
SURFACE_CONSTRAINT_MARKERS = (
    "target-id surface",
    "canonical id surface",
    "canonical target surface",
    "target surface",
)


def write_relation_semantics_compiler_preview_artifacts(
    root: Path,
    *,
    out_dir: Path,
) -> dict[str, Path]:
    root = Path(root)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    compiled_preview = build_relation_semantics_compiled_preview(root)
    diff_report = build_relation_semantics_compiler_diff_report(
        root,
        compiled_preview=compiled_preview,
    )
    summary = build_relation_semantics_compiler_preview_summary(
        compiled_preview=compiled_preview,
        diff_report=diff_report,
    )

    summary_json_path = out_dir / "summary.json"
    summary_md_path = out_dir / "summary.md"
    compiled_preview_json_path = out_dir / "relation_compiled_preview.json"
    compiled_preview_md_path = out_dir / "relation_compiled_preview.md"
    diff_json_path = out_dir / "diff_report.json"
    diff_md_path = out_dir / "diff_report.md"

    summary_json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    summary_md_path.write_text(
        render_relation_semantics_compiler_preview_summary_markdown(summary),
        encoding="utf-8",
    )
    compiled_preview_json_path.write_text(json.dumps(compiled_preview, indent=2), encoding="utf-8")
    compiled_preview_md_path.write_text(
        render_relation_semantics_compiled_preview_markdown(compiled_preview),
        encoding="utf-8",
    )
    diff_json_path.write_text(json.dumps(diff_report, indent=2), encoding="utf-8")
    diff_md_path.write_text(
        render_relation_semantics_compiler_diff_markdown(diff_report),
        encoding="utf-8",
    )

    return {
        "summary_json": summary_json_path,
        "summary_md": summary_md_path,
        "relation_compiled_preview_json": compiled_preview_json_path,
        "relation_compiled_preview_md": compiled_preview_md_path,
        "diff_report_json": diff_json_path,
        "diff_report_md": diff_md_path,
    }


def build_relation_semantics_compiled_preview(root: Path) -> dict[str, object]:
    root = Path(root)
    records = load_relation_semantics(root)
    model_ids = tuple(sorted(records))
    relation_preview = build_relation_semantics_preview(root, model_ids=model_ids)

    contested_counts_by_family = {
        family: 0 for family in sorted(relation_preview["relation_counts_by_family"])
    }
    family_counts_by_reason: dict[str, dict[str, int]] = {
        family: {} for family in sorted(relation_preview["relation_counts_by_family"])
    }
    model_relation_counts = {
        model_id: {family: 0 for family in sorted(relation_preview["relation_counts_by_family"])}
        for model_id in model_ids
    }
    model_contested_counts = {model_id: 0 for model_id in model_ids}
    relation_review_metadata: dict[str, object] = {}
    model_review_metadata: dict[str, object] = {}

    for model_id in model_ids:
        record = records[model_id]
        proxy_derived = _is_proxy_derived(record)
        target_id_surface_constrained = _is_target_id_surface_constrained(record)
        omitted_pressure = _build_omitted_source_real_pressure(record)
        model_review_metadata[model_id] = {
            "source_file": record.source_file,
            "proxy_derived": proxy_derived,
            "target_id_surface_constrained": target_id_surface_constrained,
            "omitted_source_real_pressure_count": len(omitted_pressure),
            "omitted_source_real_pressure": omitted_pressure,
            "open_questions": list(record.curation_notes.get("open_questions", []) or []),
            "deferred_higher_order_notes": {
                key: list(value) for key, value in record.deferred_higher_order_notes.items()
            },
        }

    for relation in relation_preview["relations"]:
        model_id = str(relation["model_id"])
        relation_family = str(relation["relation_family"])
        extraction_type = str(relation["extraction_type"])
        confidence = str(relation["confidence"])
        review_model = model_review_metadata[model_id]
        model_relation_counts[model_id][relation_family] += 1

        reasons: list[str] = []
        if extraction_type == "normalized":
            reasons.append("normalized_extraction")
        if confidence != "high":
            reasons.append(f"{confidence}_confidence")
        if review_model["proxy_derived"]:
            reasons.append("proxy_derived_model")
        if review_model["target_id_surface_constrained"]:
            reasons.append("target_id_surface_constraint")
        if review_model["omitted_source_real_pressure_count"]:
            reasons.append("omitted_source_real_pressure")

        contested = bool(reasons)
        if contested:
            contested_counts_by_family[relation_family] += 1
            model_contested_counts[model_id] += 1
            family_reason_counts = family_counts_by_reason[relation_family]
            for reason in reasons:
                family_reason_counts[reason] = family_reason_counts.get(reason, 0) + 1

        relation_review_metadata[str(relation["relation_id"])] = {
            "model_id": model_id,
            "relation_family": relation_family,
            "contested": contested,
            "reasons": reasons,
            "review_status": "review-visible" if contested else "source-straightforward",
            "extraction_type": extraction_type,
            "confidence": confidence,
            "proxy_derived_model": review_model["proxy_derived"],
            "target_id_surface_constrained": review_model["target_id_surface_constrained"],
            "omitted_source_real_pressure_count": review_model["omitted_source_real_pressure_count"],
        }

    for model_id in model_ids:
        total_relations = sum(model_relation_counts[model_id].values())
        normalized_count = sum(
            1
            for relation in relation_preview["relations"]
            if relation["model_id"] == model_id and relation["extraction_type"] == "normalized"
        )
        explicit_count = total_relations - normalized_count
        model_review_metadata[model_id].update(
            {
                "total_relation_count": total_relations,
                "relation_counts_by_family": model_relation_counts[model_id],
                "explicit_relation_count": explicit_count,
                "normalized_relation_count": normalized_count,
                "normalized_relation_ratio": round(normalized_count / total_relations, 4)
                if total_relations
                else 0.0,
                "contested_relation_count": model_contested_counts[model_id],
            }
        )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "preview_scope": (
            "full completed Wave 3 surface compiled into first-order relation preview artifacts; "
            "preview-only review metadata included for contested relation semantics"
        ),
        "model_ids": list(model_ids),
        "model_count": len(model_ids),
        "relation_family_contract": ["ally", "antagonist", "structured_tension"],
        "total_relation_count": relation_preview["total_relation_count"],
        "relation_counts_by_family": relation_preview["relation_counts_by_family"],
        "extraction_type_counts": relation_preview["extraction_type_counts"],
        "confidence_counts": relation_preview["confidence_counts"],
        "relation_records": relation_preview["relations"],
        REVIEW_FIELD_NAME: {
            "status": "preview_only",
            "reason": (
                "Normalized relations, medium-confidence relations, proxy-derived models, "
                "and target-id-surface constraints should stay visibly reviewable before any "
                "optional compiler-side adoption."
            ),
            "contested_relation_count": sum(contested_counts_by_family.values()),
            "contested_relation_counts_by_family": contested_counts_by_family,
            "contested_reason_counts_by_family": family_counts_by_reason,
            "proxy_derived_model_ids": sorted(
                model_id
                for model_id, payload in model_review_metadata.items()
                if payload["proxy_derived"]
            ),
            "target_id_surface_constrained_model_ids": sorted(
                model_id
                for model_id, payload in model_review_metadata.items()
                if payload["target_id_surface_constrained"]
            ),
            "omitted_source_real_pressure_model_ids": sorted(
                model_id
                for model_id, payload in model_review_metadata.items()
                if payload["omitted_source_real_pressure_count"]
            ),
            "models": model_review_metadata,
            "relations": relation_review_metadata,
        },
    }


def build_relation_semantics_compiler_diff_report(
    root: Path,
    *,
    compiled_preview: dict[str, object] | None = None,
) -> dict[str, object]:
    root = Path(root)
    compiled_preview = compiled_preview or build_relation_semantics_compiled_preview(root)
    model_ids = tuple(str(model_id) for model_id in compiled_preview["model_ids"])
    delta_report = build_relation_semantics_delta_report(root, model_ids=model_ids)
    review_payload = compiled_preview[REVIEW_FIELD_NAME]

    per_model: dict[str, object] = {}
    for model_id, payload in (delta_report.get("models", {}) or {}).items():
        model_review = review_payload["models"][model_id]
        contested_relation_families = {}
        for field_name, field_payload in (payload.get("field_deltas", {}) or {}).items():
            relation_family = field_payload["relation_family"]
            relation_count = int(field_payload["curated_item_count"])
            contested_relation_count = 0
            relation_prefix = f"{model_id}--{relation_family}--"
            for relation_id, relation_meta in (review_payload.get("relations", {}) or {}).items():
                if relation_id.startswith(relation_prefix) and relation_meta.get("contested"):
                    contested_relation_count += 1
            contested_relation_families[field_name] = {
                "relation_family": relation_family,
                "compiled_relation_count": relation_count,
                "contested_relation_count": contested_relation_count,
            }

        per_model[model_id] = {
            "source_file": payload["source_file"],
            "proxy_derived": model_review["proxy_derived"],
            "target_id_surface_constrained": model_review["target_id_surface_constrained"],
            "current_graph_counts": payload["current_graph_counts"],
            "compiled_relation_counts": payload["curated_counts"],
            "contested_relation_count": model_review["contested_relation_count"],
            "normalized_relation_ratio": model_review["normalized_relation_ratio"],
            "omitted_source_real_pressure_count": model_review["omitted_source_real_pressure_count"],
            "contested_relation_families": contested_relation_families,
            "stronger_than_current_graph": payload["stronger_than_current_graph"],
            "open_questions": model_review["open_questions"],
        }

    medium_confidence_relation_count = sum(
        1 for relation in compiled_preview["relation_records"] if relation["confidence"] == "medium"
    )
    weak_confidence_relation_count = sum(
        1 for relation in compiled_preview["relation_records"] if relation["confidence"] == "weak"
    )
    safe = (
        weak_confidence_relation_count == 0
        and delta_report["did_relation_layer_preserve_real_source_backed_content"]
        and int(delta_report["total_relation_count"]) > 0
    )
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "preview_scope": compiled_preview["preview_scope"],
        "model_count": compiled_preview["model_count"],
        "total_relation_count": compiled_preview["total_relation_count"],
        "recovered_graph_gaps": delta_report["recovered_graph_gaps"],
        "recovered_graph_gap_count": len(delta_report["recovered_graph_gaps"]),
        "explicit_relation_ratio": delta_report["explicit_relation_ratio"],
        "normalized_relation_ratio": delta_report["normalized_relation_ratio"],
        "contested_relation_count": review_payload["contested_relation_count"],
        "medium_confidence_relation_count": medium_confidence_relation_count,
        "weak_confidence_relation_count": weak_confidence_relation_count,
        "proxy_derived_model_ids": review_payload["proxy_derived_model_ids"],
        "target_id_surface_constrained_model_ids": review_payload[
            "target_id_surface_constrained_model_ids"
        ],
        "omitted_source_real_pressure_model_ids": review_payload[
            "omitted_source_real_pressure_model_ids"
        ],
        "source_first_doctrine_respected": delta_report[
            "did_relation_layer_preserve_real_source_backed_content"
        ],
        "safety_assessment": (
            "safe_for_optional_wave3_compiler_preview"
            if safe
            else "useful_but_hold_until_weak_relation_semantics_are_repaired"
        ),
        "recommendation": (
            "Wave 3 is ready for optional compiler-side adoption as a preview artifact because first-order relations are provenance-backed, weak-confidence relations are absent, and contested semantics remain visible in preview-only review metadata."
            if safe
            else "Wave 3 is useful but should stay external to compiler outputs until weak-confidence relation semantics are repaired."
        ),
        "models": per_model,
    }


def build_relation_semantics_compiler_preview_summary(
    *,
    compiled_preview: dict[str, object],
    diff_report: dict[str, object],
) -> dict[str, object]:
    review_payload = compiled_preview[REVIEW_FIELD_NAME]
    expected_model_count = len(load_relation_semantics(Path(__file__).resolve().parent.parent))
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "preview_scope": compiled_preview["preview_scope"],
        "model_count": compiled_preview["model_count"],
        "total_relation_count": compiled_preview["total_relation_count"],
        "relation_counts_by_family": compiled_preview["relation_counts_by_family"],
        "extraction_type_counts": compiled_preview["extraction_type_counts"],
        "confidence_counts": compiled_preview["confidence_counts"],
        "contested_relation_count": review_payload["contested_relation_count"],
        "proxy_derived_model_count": len(review_payload["proxy_derived_model_ids"]),
        "proxy_derived_model_ids": review_payload["proxy_derived_model_ids"],
        "target_id_surface_constrained_model_count": len(
            review_payload["target_id_surface_constrained_model_ids"]
        ),
        "target_id_surface_constrained_model_ids": review_payload[
            "target_id_surface_constrained_model_ids"
        ],
        "omitted_source_real_pressure_model_count": len(
            review_payload["omitted_source_real_pressure_model_ids"]
        ),
        "source_first_doctrine_respected": diff_report["source_first_doctrine_respected"],
        "recovered_graph_gap_count": diff_report["recovered_graph_gap_count"],
        "medium_confidence_relation_count": diff_report["medium_confidence_relation_count"],
        "weak_confidence_relation_count": diff_report["weak_confidence_relation_count"],
        "safety_assessment": diff_report["safety_assessment"],
        "recommendation": diff_report["recommendation"],
        "preview_artifact_field": REVIEW_FIELD_NAME,
        "wave3_complete_for_current_curated_surface": compiled_preview["model_count"]
        == expected_model_count,
    }


def render_relation_semantics_compiled_preview_markdown(preview: dict[str, object]) -> str:
    lines = [
        "# Wave 3 Compiler Relation Preview",
        "",
        f"- Generated at: {preview['generated_at']}",
        f"- Scope: {preview['preview_scope']}",
        f"- Model count: {preview['model_count']}",
        f"- Total relation count: {preview['total_relation_count']}",
        "",
        "## Relation Counts By Family",
        "",
    ]
    for relation_family, count in (preview.get("relation_counts_by_family", {}) or {}).items():
        lines.append(f"- {relation_family}: {count}")

    review = preview[REVIEW_FIELD_NAME]
    lines.extend(
        [
            "",
            "## Review Metadata",
            "",
            f"- Status: `{review['status']}`",
            f"- Contested relation count: {review['contested_relation_count']}",
            f"- Proxy-derived models: {', '.join(review['proxy_derived_model_ids']) or 'none'}",
            "- Target-id-surface constrained models: "
            + (", ".join(review["target_id_surface_constrained_model_ids"]) or "none"),
            "",
            "## Preview Relations",
            "",
        ]
    )
    for relation in preview.get("relation_records", []) or []:
        text = relation.get("rationale_text") or relation.get("tension_text") or ""
        lines.append(
            f"- `{relation['relation_id']}` | `{relation['model_id']}` -> `{relation['target_model_id']}` | `{relation['relation_family']}` | {text}"
        )
    return "\n".join(lines) + "\n"


def render_relation_semantics_compiler_diff_markdown(report: dict[str, object]) -> str:
    lines = [
        "# Wave 3 Compiler Preview Diff Report",
        "",
        f"- Generated at: {report['generated_at']}",
        f"- Scope: {report['preview_scope']}",
        f"- Model count: {report['model_count']}",
        f"- Total relation count: {report['total_relation_count']}",
        f"- Recovered graph gap count: {report['recovered_graph_gap_count']}",
        f"- Contested relation count: {report['contested_relation_count']}",
        f"- Medium-confidence relation count: {report['medium_confidence_relation_count']}",
        f"- Weak-confidence relation count: {report['weak_confidence_relation_count']}",
        f"- Safety assessment: `{report['safety_assessment']}`",
        f"- Recommendation: {report['recommendation']}",
        "",
    ]
    return "\n".join(lines)


def render_relation_semantics_compiler_preview_summary_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Wave 3 Compiler Preview Summary",
        "",
        f"- Generated at: {summary['generated_at']}",
        f"- Preview metadata field: `{summary['preview_artifact_field']}`",
        f"- Model count: {summary['model_count']}",
        f"- Total relation count: {summary['total_relation_count']}",
        f"- Contested relation count: {summary['contested_relation_count']}",
        f"- Proxy-derived model count: {summary['proxy_derived_model_count']}",
        "- Target-id-surface constrained model count: "
        f"{summary['target_id_surface_constrained_model_count']}",
        "- Omitted source-real pressure model count: "
        f"{summary['omitted_source_real_pressure_model_count']}",
        f"- Weak-confidence relation count: {summary['weak_confidence_relation_count']}",
        f"- Recommendation: {summary['recommendation']}",
        "",
    ]
    return "\n".join(lines)


def _is_proxy_derived(record: object) -> bool:
    text = _record_search_text(record)
    return "proxy-derived" in text or "proxy derived" in text


def _is_target_id_surface_constrained(record: object) -> bool:
    text = _record_search_text(record)
    return any(marker in text for marker in SURFACE_CONSTRAINT_MARKERS)


def _build_omitted_source_real_pressure(record: object) -> list[str]:
    pressures: list[str] = []
    seen: set[str] = set()

    for text in _record_note_texts(record):
        lowered = text.lower()
        if "source-real" not in lowered and "source real" not in lowered and "remain deferred" not in lowered:
            continue
        normalized = text.strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            pressures.append(normalized)

    for relation_family, notes in getattr(record, "deferred_higher_order_notes", {}).items():
        for note in notes:
            normalized = f"{relation_family}: {note.strip()}"
            if normalized not in seen:
                seen.add(normalized)
                pressures.append(normalized)

    return pressures


def _record_search_text(record: object) -> str:
    return " ".join(_record_note_texts(record)).lower()


def _record_note_texts(record: object) -> list[str]:
    texts: list[str] = []
    curation_notes = getattr(record, "curation_notes", {}) or {}
    for value in curation_notes.values():
        if isinstance(value, str):
            texts.append(value)
        elif isinstance(value, list):
            texts.extend(str(item) for item in value)

    deferred = getattr(record, "deferred_higher_order_notes", {}) or {}
    for notes in deferred.values():
        texts.extend(str(note) for note in notes)
    return texts
