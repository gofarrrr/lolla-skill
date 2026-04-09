from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

from system_b.intervention_semantics import (
    build_intervention_semantics_chunk_preview,
    build_intervention_semantics_delta_report,
    load_intervention_semantics,
)


def write_intervention_semantics_compiler_preview_artifacts(
    root: Path,
    *,
    out_dir: Path,
) -> dict[str, Path]:
    root = Path(root)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    compiled_preview = build_intervention_semantics_compiled_preview(root)
    diff_report = build_intervention_semantics_compiler_diff_report(
        root,
        compiled_preview=compiled_preview,
    )
    summary = build_intervention_semantics_compiler_preview_summary(
        compiled_preview=compiled_preview,
        diff_report=diff_report,
    )

    summary_json_path = out_dir / "summary.json"
    summary_md_path = out_dir / "summary.md"
    compiled_preview_json_path = out_dir / "chunk_compiled_preview.json"
    compiled_preview_md_path = out_dir / "chunk_compiled_preview.md"
    diff_json_path = out_dir / "diff_report.json"
    diff_md_path = out_dir / "diff_report.md"

    summary_json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    summary_md_path.write_text(
        render_intervention_semantics_compiler_preview_summary_markdown(summary),
        encoding="utf-8",
    )
    compiled_preview_json_path.write_text(json.dumps(compiled_preview, indent=2), encoding="utf-8")
    compiled_preview_md_path.write_text(
        render_intervention_semantics_compiled_preview_markdown(compiled_preview),
        encoding="utf-8",
    )
    diff_json_path.write_text(json.dumps(diff_report, indent=2), encoding="utf-8")
    diff_md_path.write_text(
        render_intervention_semantics_compiler_diff_markdown(diff_report),
        encoding="utf-8",
    )

    return {
        "summary_json": summary_json_path,
        "summary_md": summary_md_path,
        "chunk_compiled_preview_json": compiled_preview_json_path,
        "chunk_compiled_preview_md": compiled_preview_md_path,
        "diff_report_json": diff_json_path,
        "diff_report_md": diff_md_path,
    }


def build_intervention_semantics_compiled_preview(root: Path) -> dict[str, object]:
    root = Path(root)
    records = load_intervention_semantics(root)
    model_ids = tuple(sorted(records))
    chunk_preview = build_intervention_semantics_chunk_preview(root, model_ids=model_ids)

    proxy_derived_model_ids = sorted(
        model_id
        for model_id, record in records.items()
        if _is_proxy_derived(record.curation_notes)
    )
    proxy_derived_model_set = set(proxy_derived_model_ids)

    contested_counts_by_type = {
        chunk_type: 0 for chunk_type in sorted(chunk_preview["chunk_counts_by_type"])
    }
    model_chunk_counts = {
        model_id: {chunk_type: 0 for chunk_type in sorted(chunk_preview["chunk_counts_by_type"])}
        for model_id in model_ids
    }
    model_explicit_counts = {model_id: 0 for model_id in model_ids}
    model_normalized_counts = {model_id: 0 for model_id in model_ids}
    model_contested_counts = {model_id: 0 for model_id in model_ids}
    chunk_review_metadata: dict[str, object] = {}

    for chunk in chunk_preview["chunks"]:
        model_id = str(chunk["model_id"])
        chunk_type = str(chunk["chunk_type"])
        extraction_type = str(chunk["extraction_type"])
        confidence = str(chunk["confidence"])
        model_chunk_counts[model_id][chunk_type] += 1
        if extraction_type == "explicit":
            model_explicit_counts[model_id] += 1
        else:
            model_normalized_counts[model_id] += 1

        reasons: list[str] = []
        if extraction_type == "normalized":
            reasons.append("normalized_extraction")
        if confidence != "high":
            reasons.append(f"{confidence}_confidence")
        if model_id in proxy_derived_model_set:
            reasons.append("proxy_derived_model")

        contested = bool(reasons)
        if contested:
            contested_counts_by_type[chunk_type] += 1
            model_contested_counts[model_id] += 1

        chunk_review_metadata[chunk["chunk_id"]] = {
            "model_id": model_id,
            "chunk_type": chunk_type,
            "contested": contested,
            "reasons": reasons,
            "review_status": "review-visible" if contested else "source-straightforward",
            "extraction_type": extraction_type,
            "confidence": confidence,
            "proxy_derived_model": model_id in proxy_derived_model_set,
        }

    model_review_metadata: dict[str, object] = {}
    for model_id in model_ids:
        total_chunks = sum(model_chunk_counts[model_id].values())
        normalized_chunk_count = model_normalized_counts[model_id]
        explicit_chunk_count = model_explicit_counts[model_id]
        model_review_metadata[model_id] = {
            "source_file": records[model_id].source_file,
            "proxy_derived": model_id in proxy_derived_model_set,
            "total_chunk_count": total_chunks,
            "chunk_counts_by_type": model_chunk_counts[model_id],
            "explicit_chunk_count": explicit_chunk_count,
            "normalized_chunk_count": normalized_chunk_count,
            "normalized_chunk_ratio": round(normalized_chunk_count / total_chunks, 4)
            if total_chunks
            else 0.0,
            "contested_chunk_count": model_contested_counts[model_id],
            "open_questions": list(records[model_id].curation_notes.get("open_questions", []) or []),
        }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "preview_scope": (
            "full completed Wave 2 surface compiled into chunk-oriented preview artifacts; "
            "preview-only review metadata included for contested chunk semantics"
        ),
        "model_ids": list(model_ids),
        "model_count": len(model_ids),
        "chunk_type_contract": ["failure_mode", "premortem_question", "heuristic"],
        "total_chunk_count": chunk_preview["total_chunk_count"],
        "chunk_counts_by_type": chunk_preview["chunk_counts_by_type"],
        "extraction_type_counts": chunk_preview["extraction_type_counts"],
        "confidence_counts": chunk_preview["confidence_counts"],
        "chunks": chunk_preview["chunks"],
        "intervention_semantics_review": {
            "status": "preview_only",
            "reason": (
                "Normalized and proxy-derived chunk semantics should stay visibly reviewable "
                "before any optional compiler-side adoption."
            ),
            "contested_chunk_count": sum(contested_counts_by_type.values()),
            "contested_chunk_counts_by_type": contested_counts_by_type,
            "proxy_derived_model_ids": proxy_derived_model_ids,
            "models": model_review_metadata,
            "chunks": chunk_review_metadata,
        },
    }


def build_intervention_semantics_compiler_diff_report(
    root: Path,
    *,
    compiled_preview: dict[str, object] | None = None,
) -> dict[str, object]:
    root = Path(root)
    compiled_preview = compiled_preview or build_intervention_semantics_compiled_preview(root)
    model_ids = tuple(str(model_id) for model_id in compiled_preview["model_ids"])
    delta_report = build_intervention_semantics_delta_report(root, model_ids=model_ids)
    review_payload = compiled_preview["intervention_semantics_review"]

    per_model: dict[str, object] = {}
    for model_id, payload in (delta_report.get("models", {}) or {}).items():
        model_review = review_payload["models"][model_id]
        contested_chunk_types = {}
        for field_name, field_payload in (payload.get("field_deltas", {}) or {}).items():
            chunk_type = field_payload["chunk_type"]
            chunk_count = int(field_payload["curated_item_count"])
            contested_chunk_count = 0
            chunk_prefix = f"{model_id}--{chunk_type}--"
            for chunk_id, chunk_meta in (review_payload.get("chunks", {}) or {}).items():
                if chunk_id.startswith(chunk_prefix) and chunk_meta.get("contested"):
                    contested_chunk_count += 1
            contested_chunk_types[field_name] = {
                "chunk_type": chunk_type,
                "compiled_chunk_count": chunk_count,
                "contested_chunk_count": contested_chunk_count,
            }

        per_model[model_id] = {
            "source_file": payload["source_file"],
            "proxy_derived": model_review["proxy_derived"],
            "current_graph_counts": payload["current_graph_counts"],
            "compiled_chunk_counts": payload["curated_counts"],
            "contested_chunk_count": model_review["contested_chunk_count"],
            "normalized_chunk_ratio": model_review["normalized_chunk_ratio"],
            "contested_chunk_types": contested_chunk_types,
            "stronger_than_current_graph": payload["stronger_than_current_graph"],
            "open_questions": model_review["open_questions"],
        }

    contested_chunk_count = int(review_payload["contested_chunk_count"])
    low_confidence_chunk_count = len(delta_report.get("low_confidence_chunks", []) or [])
    safe = low_confidence_chunk_count == 0 and int(delta_report["total_chunk_count"]) > 0
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "preview_scope": compiled_preview["preview_scope"],
        "model_count": compiled_preview["model_count"],
        "total_chunk_count": compiled_preview["total_chunk_count"],
        "recovered_graph_gaps": delta_report["recovered_graph_gaps"],
        "recovered_graph_gap_count": len(delta_report["recovered_graph_gaps"]),
        "explicit_chunk_ratio": delta_report["explicit_chunk_ratio"],
        "normalized_chunk_ratio": delta_report["normalized_chunk_ratio"],
        "contested_chunk_count": contested_chunk_count,
        "low_confidence_chunk_count": low_confidence_chunk_count,
        "proxy_derived_model_ids": review_payload["proxy_derived_model_ids"],
        "source_first_doctrine_respected": delta_report[
            "did_deepening_layer_preserve_real_source_backed_content"
        ],
        "safety_assessment": (
            "safe_for_optional_wave2_compiler_preview"
            if safe
            else "useful_but_hold_until_low_confidence_chunks_are_reviewed"
        ),
        "recommendation": (
            "Wave 2 is disciplined enough to become an optional compiler-side preview artifact because all current chunks are source-quoted, low-confidence chunks are absent, and contested semantics remain visibly reviewable in preview-only metadata."
            if safe
            else "Wave 2 should remain external to compiler outputs until low-confidence chunk semantics are repaired."
        ),
        "models": per_model,
    }


def build_intervention_semantics_compiler_preview_summary(
    *,
    compiled_preview: dict[str, object],
    diff_report: dict[str, object],
) -> dict[str, object]:
    review_payload = compiled_preview["intervention_semantics_review"]
    expected_model_count = len(load_intervention_semantics(Path(__file__).resolve().parent.parent))
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "preview_scope": compiled_preview["preview_scope"],
        "model_count": compiled_preview["model_count"],
        "total_chunk_count": compiled_preview["total_chunk_count"],
        "chunk_counts_by_type": compiled_preview["chunk_counts_by_type"],
        "extraction_type_counts": compiled_preview["extraction_type_counts"],
        "confidence_counts": compiled_preview["confidence_counts"],
        "contested_chunk_count": review_payload["contested_chunk_count"],
        "proxy_derived_model_count": len(review_payload["proxy_derived_model_ids"]),
        "proxy_derived_model_ids": review_payload["proxy_derived_model_ids"],
        "source_first_doctrine_respected": diff_report["source_first_doctrine_respected"],
        "recovered_graph_gap_count": diff_report["recovered_graph_gap_count"],
        "low_confidence_chunk_count": diff_report["low_confidence_chunk_count"],
        "safety_assessment": diff_report["safety_assessment"],
        "recommendation": diff_report["recommendation"],
        "preview_artifact_field": "intervention_semantics_review",
        "wave2_complete_for_current_curated_surface": compiled_preview["model_count"]
        == expected_model_count,
    }


def render_intervention_semantics_compiled_preview_markdown(preview: dict[str, object]) -> str:
    lines = [
        "# Wave 2 Compiler Chunk Preview",
        "",
        f"- Generated at: {preview['generated_at']}",
        f"- Scope: {preview['preview_scope']}",
        f"- Model count: {preview['model_count']}",
        f"- Total chunks: {preview['total_chunk_count']}",
        "",
        "## Chunk Counts By Type",
        "",
    ]
    for chunk_type, count in (preview.get("chunk_counts_by_type", {}) or {}).items():
        lines.append(f"- {chunk_type}: {count}")

    review = preview["intervention_semantics_review"]
    lines.extend(
        [
            "",
            "## Review Metadata",
            "",
            f"- Status: `{review['status']}`",
            f"- Contested chunk count: {review['contested_chunk_count']}",
            f"- Proxy-derived models: {', '.join(review['proxy_derived_model_ids']) or 'none'}",
            "",
            "## Preview Chunks",
            "",
        ]
    )
    for chunk in preview.get("chunks", []) or []:
        lines.append(
            f"- `{chunk['chunk_id']}` | `{chunk['model_id']}` | `{chunk['chunk_type']}` | {chunk['text']}"
        )
    return "\n".join(lines) + "\n"


def render_intervention_semantics_compiler_diff_markdown(report: dict[str, object]) -> str:
    lines = [
        "# Wave 2 Compiler Preview Diff Report",
        "",
        f"- Generated at: {report['generated_at']}",
        f"- Scope: {report['preview_scope']}",
        f"- Model count: {report['model_count']}",
        f"- Total chunk count: {report['total_chunk_count']}",
        f"- Recovered graph gap count: {report['recovered_graph_gap_count']}",
        f"- Contested chunk count: {report['contested_chunk_count']}",
        f"- Low-confidence chunk count: {report['low_confidence_chunk_count']}",
        f"- Source-first doctrine respected: `{report['source_first_doctrine_respected']}`",
        f"- Safety assessment: `{report['safety_assessment']}`",
        f"- Recommendation: {report['recommendation']}",
        "",
        "## Model Deltas",
        "",
    ]
    for model_id, payload in (report.get("models", {}) or {}).items():
        lines.append(f"### {model_id}")
        lines.append("")
        lines.append(
            "- Current graph counts: "
            f"failure_modes={payload['current_graph_counts']['failure_modes']}, "
            f"premortem_questions={payload['current_graph_counts']['premortem_questions']}, "
            f"heuristics={payload['current_graph_counts']['heuristics']}"
        )
        lines.append(
            "- Compiled chunk counts: "
            f"failure_modes={payload['compiled_chunk_counts']['failure_modes']}, "
            f"premortem_questions={payload['compiled_chunk_counts']['premortem_questions']}, "
            f"heuristics={payload['compiled_chunk_counts']['heuristics']}"
        )
        lines.append(f"- Proxy-derived: `{payload['proxy_derived']}`")
        lines.append(f"- Contested chunk count: {payload['contested_chunk_count']}")
        lines.append(
            "- Stronger than current graph because: "
            + "; ".join(payload["stronger_than_current_graph"])
        )
        lines.append("")
    return "\n".join(lines) + "\n"


def render_intervention_semantics_compiler_preview_summary_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Wave 2 Compiler Preview Summary",
        "",
        f"- Generated at: {summary['generated_at']}",
        f"- Scope: {summary['preview_scope']}",
        f"- Model count: {summary['model_count']}",
        f"- Total chunk count: {summary['total_chunk_count']}",
        f"- Contested chunk count: {summary['contested_chunk_count']}",
        f"- Proxy-derived model count: {summary['proxy_derived_model_count']}",
        f"- Recovered graph gap count: {summary['recovered_graph_gap_count']}",
        f"- Low-confidence chunk count: {summary['low_confidence_chunk_count']}",
        f"- Preview metadata field: `{summary['preview_artifact_field']}`",
        f"- Wave 2 complete for current curated surface: `{summary['wave2_complete_for_current_curated_surface']}`",
        f"- Safety assessment: `{summary['safety_assessment']}`",
        f"- Recommendation: {summary['recommendation']}",
        "",
    ]
    return "\n".join(lines)


def _is_proxy_derived(curation_notes: dict[str, object]) -> bool:
    haystacks = [
        str(curation_notes.get("summary", "")),
        *[str(item) for item in (curation_notes.get("open_questions", []) or [])],
    ]
    return any("proxy-derived" in haystack.lower() for haystack in haystacks)
