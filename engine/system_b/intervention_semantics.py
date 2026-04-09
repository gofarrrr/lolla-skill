from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path


INTERVENTION_SEMANTICS_PILOT_MODEL_IDS = (
    "base-rates",
    "authority-bias",
    "information-asymmetry",
    "systems-thinking",
    "decision-trees",
    "expected-value",
    "obligations-controls-mapping",
)
ALLOWED_CHUNK_TYPES = frozenset({"failure_mode", "premortem_question", "heuristic"})
ALLOWED_EXTRACTION_TYPES = frozenset({"explicit", "normalized"})
ALLOWED_CONFIDENCE = frozenset({"high", "medium", "weak"})
REQUIRED_FIELDS = (
    "model_id",
    "source_file",
    "failure_modes",
    "premortem_questions",
    "heuristics",
)
OPTIONAL_FIELDS = ("curation_notes", "deferred_richness_notes")
ALLOWED_FIELDS = frozenset((*REQUIRED_FIELDS, *OPTIONAL_FIELDS))
ALLOWED_DEFERRED_FIELDS = frozenset({"allies", "antagonists", "structured_tensions"})


class InterventionSemanticsValidationError(ValueError):
    pass


@dataclass(frozen=True)
class InterventionSemanticItem:
    text: str
    source_quote: str
    extraction_type: str
    confidence: str
    note: str
    mitigation: str  # paired corrective action for failure_mode items; empty for other types


@dataclass(frozen=True)
class InterventionSemanticsRecord:
    model_id: str
    source_file: str
    failure_modes: tuple[InterventionSemanticItem, ...]
    premortem_questions: tuple[InterventionSemanticItem, ...]
    heuristics: tuple[InterventionSemanticItem, ...]
    curation_notes: dict[str, object]
    deferred_richness_notes: dict[str, tuple[str, ...]]
    path: Path

    @classmethod
    def from_payload(cls, payload: dict[str, object], path: Path) -> "InterventionSemanticsRecord":
        return cls(
            model_id=str(payload["model_id"]),
            source_file=str(payload["source_file"]),
            failure_modes=_items_from_payload(payload["failure_modes"]),
            premortem_questions=_items_from_payload(payload["premortem_questions"]),
            heuristics=_items_from_payload(payload["heuristics"]),
            curation_notes=dict(payload.get("curation_notes", {}) or {}),
            deferred_richness_notes={
                key: tuple(str(entry) for entry in entries)
                for key, entries in dict(payload.get("deferred_richness_notes", {}) or {}).items()
            },
            path=path,
        )


def load_intervention_semantics(
    root: Path,
    *,
    model_ids: tuple[str, ...] | None = None,
) -> dict[str, InterventionSemanticsRecord]:
    semantics_dir = Path(root) / "curation" / "intervention_semantics"
    if not semantics_dir.exists():
        raise InterventionSemanticsValidationError(
            f"Missing intervention semantics directory: {semantics_dir}"
        )

    selected_ids = set(model_ids or ())
    records: dict[str, InterventionSemanticsRecord] = {}
    for path in sorted(semantics_dir.glob("*.json")):
        if path.name == "schema.json":
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        validate_intervention_semantics_payload(payload, path=path, root=Path(root))
        record = InterventionSemanticsRecord.from_payload(payload, path)
        if selected_ids and record.model_id not in selected_ids:
            continue
        records[record.model_id] = record

    if selected_ids:
        missing = sorted(selected_ids.difference(records))
        if missing:
            raise InterventionSemanticsValidationError(
                f"Missing intervention semantics files for: {', '.join(missing)}"
            )
    return records


def validate_intervention_semantics_payload(
    payload: dict[str, object],
    *,
    path: Path,
    root: Path,
) -> None:
    if not isinstance(payload, dict):
        raise InterventionSemanticsValidationError(f"{path}: payload must be an object")

    unknown_fields = sorted(set(payload).difference(ALLOWED_FIELDS))
    if unknown_fields:
        raise InterventionSemanticsValidationError(
            f"{path}: unknown fields: {', '.join(unknown_fields)}"
        )

    missing_fields = [field for field in REQUIRED_FIELDS if field not in payload]
    if missing_fields:
        raise InterventionSemanticsValidationError(
            f"{path}: missing required fields: {', '.join(missing_fields)}"
        )

    model_id = _validate_slug(payload["model_id"], field_name="model_id", path=path)
    if path.stem != model_id:
        raise InterventionSemanticsValidationError(
            f"{path}: filename stem must match model_id '{model_id}'"
        )

    source_file = str(payload["source_file"]).strip()
    if not source_file.endswith(".md"):
        raise InterventionSemanticsValidationError(f"{path}: source_file must end with .md")
    source_path = Path(root) / "MM_CANONICAL_216" / source_file
    if not source_path.exists():
        raise InterventionSemanticsValidationError(
            f"{path}: source file does not exist: {source_path}"
        )

    wave1_path = Path(root) / "curation" / f"{model_id}.json"
    if not wave1_path.exists():
        raise InterventionSemanticsValidationError(
            f"{path}: corresponding Wave 1 curation file is missing: {wave1_path}"
        )

    for field_name in ("failure_modes", "premortem_questions", "heuristics"):
        _validate_item_list(payload[field_name], field_name=field_name, path=path)

    curation_notes = payload.get("curation_notes", {})
    if curation_notes:
        if not isinstance(curation_notes, dict):
            raise InterventionSemanticsValidationError(
                f"{path}: curation_notes must be an object"
            )
        for note_field in curation_notes:
            if note_field not in {"summary", "donor_drops", "open_questions"}:
                raise InterventionSemanticsValidationError(
                    f"{path}: unsupported curation_notes field '{note_field}'"
                )

    deferred = payload.get("deferred_richness_notes", {})
    if deferred:
        if not isinstance(deferred, dict):
            raise InterventionSemanticsValidationError(
                f"{path}: deferred_richness_notes must be an object"
            )
        unsupported = sorted(set(deferred).difference(ALLOWED_DEFERRED_FIELDS))
        if unsupported:
            raise InterventionSemanticsValidationError(
                f"{path}: unsupported deferred_richness_notes field(s): {', '.join(unsupported)}"
            )
        for key, entries in deferred.items():
            if not isinstance(entries, list):
                raise InterventionSemanticsValidationError(
                    f"{path}: deferred_richness_notes.{key} must be a list"
                )
            for index, entry in enumerate(entries):
                if not isinstance(entry, str) or len(entry.strip()) < 12:
                    raise InterventionSemanticsValidationError(
                        f"{path}: deferred_richness_notes.{key}[{index}] must be a meaningful string"
                    )


def build_intervention_semantics_chunk_preview(
    root: Path,
    *,
    model_ids: tuple[str, ...],
) -> dict[str, object]:
    records = load_intervention_semantics(root, model_ids=model_ids)
    chunks: list[dict[str, object]] = []
    counts_by_type = {chunk_type: 0 for chunk_type in sorted(ALLOWED_CHUNK_TYPES)}
    extraction_type_counts = {kind: 0 for kind in sorted(ALLOWED_EXTRACTION_TYPES)}
    confidence_counts = {confidence: 0 for confidence in sorted(ALLOWED_CONFIDENCE)}
    per_model_counts: dict[str, dict[str, int]] = {}

    for model_id in model_ids:
        record = records[model_id]
        per_model_counts[model_id] = {}
        for chunk_type, items in (
            ("failure_mode", record.failure_modes),
            ("premortem_question", record.premortem_questions),
            ("heuristic", record.heuristics),
        ):
            per_model_counts[model_id][chunk_type] = len(items)
            for index, item in enumerate(items, start=1):
                chunk = {
                    "chunk_id": _build_chunk_id(model_id, chunk_type, index),
                    "model_id": model_id,
                    "chunk_type": chunk_type,
                    "text": item.text,
                    "source_file": record.source_file,
                    "source_quote": item.source_quote,
                    "extraction_type": item.extraction_type,
                    "confidence": item.confidence,
                }
                if item.note:
                    chunk["note"] = item.note
                chunks.append(chunk)
                counts_by_type[chunk_type] += 1
                extraction_type_counts[item.extraction_type] += 1
                confidence_counts[item.confidence] += 1

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pilot_model_ids": list(model_ids),
        "total_chunk_count": len(chunks),
        "chunk_counts_by_type": counts_by_type,
        "extraction_type_counts": extraction_type_counts,
        "confidence_counts": confidence_counts,
        "per_model_counts": per_model_counts,
        "chunks": chunks,
    }


def build_intervention_semantics_delta_report(
    root: Path,
    *,
    model_ids: tuple[str, ...],
) -> dict[str, object]:
    root = Path(root)
    records = load_intervention_semantics(root, model_ids=model_ids)
    knowledge_graph = json.loads((root / "build" / "knowledge_graph.json").read_text(encoding="utf-8"))
    graph_models = knowledge_graph.get("models", {}) if isinstance(knowledge_graph, dict) else {}

    models_summary: dict[str, object] = {}
    chunk_counts_by_type = {chunk_type: 0 for chunk_type in sorted(ALLOWED_CHUNK_TYPES)}
    extraction_type_counts = {kind: 0 for kind in sorted(ALLOWED_EXTRACTION_TYPES)}
    low_confidence_chunks: list[dict[str, object]] = []
    recovered_graph_gaps: list[dict[str, object]] = []

    for model_id in model_ids:
        record = records[model_id]
        graph_model = graph_models.get(model_id, {}) if isinstance(graph_models, dict) else {}
        field_summary = {
            "failure_modes": _field_delta(
                model_id,
                "failure_mode",
                graph_model.get("failure_modes", []),
                record.failure_modes,
                low_confidence_chunks,
                recovered_graph_gaps,
            ),
            "premortem_questions": _field_delta(
                model_id,
                "premortem_question",
                graph_model.get("premortem_questions", []),
                record.premortem_questions,
                low_confidence_chunks,
                recovered_graph_gaps,
            ),
            "heuristics": _field_delta(
                model_id,
                "heuristic",
                graph_model.get("heuristics", []),
                record.heuristics,
                low_confidence_chunks,
                recovered_graph_gaps,
            ),
        }

        for field_payload in field_summary.values():
            chunk_counts_by_type[field_payload["chunk_type"]] += field_payload["curated_item_count"]
            for kind, count in field_payload["extraction_type_counts"].items():
                extraction_type_counts[kind] += count

        models_summary[model_id] = {
            "source_file": record.source_file,
            "current_graph_counts": {
                "failure_modes": len(graph_model.get("failure_modes", []) or []),
                "premortem_questions": len(graph_model.get("premortem_questions", []) or []),
                "heuristics": len(graph_model.get("heuristics", []) or []),
            },
            "curated_counts": {
                "failure_modes": len(record.failure_modes),
                "premortem_questions": len(record.premortem_questions),
                "heuristics": len(record.heuristics),
                "total_chunks": len(record.failure_modes) + len(record.premortem_questions) + len(record.heuristics),
            },
            "field_deltas": field_summary,
            "deferred_richness_notes": {
                key: list(value)
                for key, value in record.deferred_richness_notes.items()
            },
            "stronger_than_current_graph": _stronger_than_graph_reasons(field_summary),
        }

    total_chunks = sum(chunk_counts_by_type.values())
    explicit_chunks = extraction_type_counts["explicit"]
    normalized_chunks = extraction_type_counts["normalized"]
    preserve_real_content = not low_confidence_chunks and total_chunks > 0
    contract_good_enough_to_scale = preserve_real_content and all(
        models_summary[model_id]["curated_counts"]["total_chunks"] >= 5 for model_id in model_ids
    )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pilot_model_ids": list(model_ids),
        "did_deepening_layer_preserve_real_source_backed_content": preserve_real_content,
        "contract_good_enough_for_wave2_scale": contract_good_enough_to_scale,
        "total_chunk_count": total_chunks,
        "chunk_counts_by_type": chunk_counts_by_type,
        "extraction_type_counts": extraction_type_counts,
        "explicit_chunk_ratio": round(explicit_chunks / total_chunks, 4) if total_chunks else 0.0,
        "normalized_chunk_ratio": round(normalized_chunks / total_chunks, 4) if total_chunks else 0.0,
        "low_confidence_chunks": low_confidence_chunks,
        "recovered_graph_gaps": recovered_graph_gaps,
        "models": models_summary,
    }


def build_intervention_semantics_summary(
    *,
    chunk_preview: dict[str, object],
    delta_report: dict[str, object],
) -> dict[str, object]:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pilot_model_ids": chunk_preview["pilot_model_ids"],
        "total_chunk_count": chunk_preview["total_chunk_count"],
        "chunk_counts_by_type": chunk_preview["chunk_counts_by_type"],
        "extraction_type_counts": chunk_preview["extraction_type_counts"],
        "confidence_counts": chunk_preview["confidence_counts"],
        "did_deepening_layer_preserve_real_source_backed_content": delta_report[
            "did_deepening_layer_preserve_real_source_backed_content"
        ],
        "contract_good_enough_for_wave2_scale": delta_report[
            "contract_good_enough_for_wave2_scale"
        ],
        "recovered_graph_gap_count": len(delta_report["recovered_graph_gaps"]),
        "low_confidence_chunk_count": len(delta_report["low_confidence_chunks"]),
    }


def render_intervention_semantics_chunk_preview_markdown(preview: dict[str, object]) -> str:
    lines = [
        "# Intervention Semantics Chunk Preview",
        "",
        f"- Generated at: {preview['generated_at']}",
        f"- Pilot models: {', '.join(preview['pilot_model_ids'])}",
        f"- Total chunks: {preview['total_chunk_count']}",
        "",
        "## Chunk Counts By Type",
        "",
    ]
    for chunk_type, count in (preview.get("chunk_counts_by_type", {}) or {}).items():
        lines.append(f"- {chunk_type}: {count}")

    lines.extend(["", "## Preview Chunks", ""])
    for chunk in preview.get("chunks", []) or []:
        lines.append(
            f"- `{chunk['chunk_id']}` | `{chunk['model_id']}` | `{chunk['chunk_type']}` | {chunk['text']}"
        )
    return "\n".join(lines) + "\n"


def render_intervention_semantics_delta_markdown(report: dict[str, object]) -> str:
    lines = [
        "# Intervention Semantics Delta Report",
        "",
        f"- Generated at: {report['generated_at']}",
        f"- Preserve real source-backed content: {report['did_deepening_layer_preserve_real_source_backed_content']}",
        f"- Contract good enough for broader Wave 2 scaling: {report['contract_good_enough_for_wave2_scale']}",
        f"- Total chunk count: {report['total_chunk_count']}",
        f"- Recovered graph gap count: {len(report['recovered_graph_gaps'])}",
        f"- Low-confidence chunk count: {len(report['low_confidence_chunks'])}",
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
            "- Curated chunk counts: "
            f"failure_modes={payload['curated_counts']['failure_modes']}, "
            f"premortem_questions={payload['curated_counts']['premortem_questions']}, "
            f"heuristics={payload['curated_counts']['heuristics']}"
        )
        lines.append("- Stronger than current graph because: " + "; ".join(payload["stronger_than_current_graph"]))
        lines.append("")
    return "\n".join(lines) + "\n"


def render_intervention_semantics_summary_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Intervention Semantics Summary",
        "",
        f"- Generated at: {summary['generated_at']}",
        f"- Pilot models: {', '.join(summary['pilot_model_ids'])}",
        f"- Total chunk count: {summary['total_chunk_count']}",
        f"- Preserve real source-backed content: {summary['did_deepening_layer_preserve_real_source_backed_content']}",
        f"- Contract good enough for broader Wave 2 scaling: {summary['contract_good_enough_for_wave2_scale']}",
        f"- Recovered graph gap count: {summary['recovered_graph_gap_count']}",
        f"- Low-confidence chunk count: {summary['low_confidence_chunk_count']}",
        "",
    ]
    return "\n".join(lines)


def write_intervention_semantics_artifacts(
    root: Path,
    *,
    out_dir: Path,
    model_ids: tuple[str, ...] = INTERVENTION_SEMANTICS_PILOT_MODEL_IDS,
) -> dict[str, Path]:
    root = Path(root)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    chunk_preview = build_intervention_semantics_chunk_preview(root, model_ids=model_ids)
    delta_report = build_intervention_semantics_delta_report(root, model_ids=model_ids)
    summary = build_intervention_semantics_summary(
        chunk_preview=chunk_preview,
        delta_report=delta_report,
    )
    model_set_md = render_model_set_markdown(model_ids)

    chunk_preview_json_path = out_dir / "chunk_preview.json"
    chunk_preview_md_path = out_dir / "chunk_preview.md"
    delta_report_json_path = out_dir / "delta_report.json"
    delta_report_md_path = out_dir / "delta_report.md"
    summary_json_path = out_dir / "summary.json"
    summary_md_path = out_dir / "summary.md"
    model_set_md_path = out_dir / "model_set.md"

    chunk_preview_json_path.write_text(json.dumps(chunk_preview, indent=2), encoding="utf-8")
    chunk_preview_md_path.write_text(
        render_intervention_semantics_chunk_preview_markdown(chunk_preview),
        encoding="utf-8",
    )
    delta_report_json_path.write_text(json.dumps(delta_report, indent=2), encoding="utf-8")
    delta_report_md_path.write_text(
        render_intervention_semantics_delta_markdown(delta_report),
        encoding="utf-8",
    )
    summary_json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    summary_md_path.write_text(
        render_intervention_semantics_summary_markdown(summary),
        encoding="utf-8",
    )
    model_set_md_path.write_text(model_set_md, encoding="utf-8")

    return {
        "summary_json": summary_json_path,
        "summary_md": summary_md_path,
        "chunk_preview_json": chunk_preview_json_path,
        "chunk_preview_md": chunk_preview_md_path,
        "delta_report_json": delta_report_json_path,
        "delta_report_md": delta_report_md_path,
        "model_set_md": model_set_md_path,
    }


def render_model_set_markdown(model_ids: tuple[str, ...]) -> str:
    intro = (
        "This model set stays inside the already Wave 1-curated surface and focuses on models "
        "with strong raw intervention content and thin or missing current-graph failure coverage."
    )
    lines = [
        "# Wave 2 Model Set",
        "",
        intro,
        "",
    ]
    reasons = {
        "base-rates": "Strong explicit heuristics plus high-signal failure table and reference-class premortems.",
        "authority-bias": "Useful challenge-oriented mitigations and strong deference-failure content despite the persuasion-heavy raw playbook.",
        "information-asymmetry": "Unusually rich source content for hidden-variable failure modes, diligence questions, and observability heuristics.",
        "systems-thinking": "High-value leverage-oriented heuristics and architecture-misdiagnosis failure content needed for later bundle pressure.",
        "decision-trees": "Clear branch-logic heuristics plus threshold-focused premortem questions that are already close to chunk form.",
        "expected-value": "Strong risk weighting, tail-risk, and assumption-discipline content that can later fill protocol and challenge lanes.",
        "obligations-controls-mapping": "High-value control-design and handoff-discipline content with clear missing-graph upside on failure modes.",
        "conjunction-fallacy": "Rich sequential-failure content with explicit premortem questions and clear outside-view heuristics.",
        "confirmation-bias": "Strong source-backed evidence-hygiene failure modes plus useful premortem and scientific-mindset heuristics.",
        "commitment-bias": "High-value escalation and entrenchment failure content with concrete reversal-oriented questions.",
        "incentives": "Strong reward-structure failure content plus practical mitigation questions for hidden motivation problems.",
        "risk-vs-uncertainty": "Excellent uncertainty-threshold and reversibility content that is naturally chunk-ready for later pressure bundles.",
        "bottlenecks": "Constraint-diagnosis model with clear throughput failures, queue-focused premortems, and leverage heuristics.",
        "batna": "Useful fallback-discipline and negotiation-pressure content with strong walk-away and worst-case premortem signals.",
        "prioritization": "Rich leverage and anti-ocean-boiling material with concrete elimination and end-product heuristics.",
        "reasoning-mode-router": "Routing-discipline model with strong framework-bias failure content and mode-selection safeguards.",
    }
    for model_id in model_ids:
        reason = reasons.get(
            model_id,
            "Already Wave 1-curated and selected for strong raw intervention content under the frozen Wave 2 contract.",
        )
        lines.append(f"- `{model_id}`: {reason}")
    lines.append("")
    return "\n".join(lines)


def _field_delta(
    model_id: str,
    chunk_type: str,
    graph_value: object,
    curated_items: tuple[InterventionSemanticItem, ...],
    low_confidence_chunks: list[dict[str, object]],
    recovered_graph_gaps: list[dict[str, object]],
) -> dict[str, object]:
    graph_count = len(graph_value) if isinstance(graph_value, list) else 0
    extraction_type_counts = {kind: 0 for kind in sorted(ALLOWED_EXTRACTION_TYPES)}
    for index, item in enumerate(curated_items, start=1):
        extraction_type_counts[item.extraction_type] += 1
        if item.confidence == "weak":
            low_confidence_chunks.append(
                {
                    "model_id": model_id,
                    "chunk_type": chunk_type,
                    "chunk_id": _build_chunk_id(model_id, chunk_type, index),
                    "text": item.text,
                }
            )

    if graph_count == 0 and curated_items:
        recovered_graph_gaps.append(
            {
                "model_id": model_id,
                "chunk_type": chunk_type,
                "added_chunk_count": len(curated_items),
            }
        )

    return {
        "chunk_type": chunk_type,
        "current_graph_count": graph_count,
        "curated_item_count": len(curated_items),
        "chunk_ready_gain": len(curated_items),
        "recovers_missing_graph_field": graph_count == 0 and bool(curated_items),
        "extraction_type_counts": extraction_type_counts,
        "all_items_have_source_quotes": all(bool(item.source_quote) for item in curated_items),
    }


def _stronger_than_graph_reasons(field_summary: dict[str, object]) -> list[str]:
    reasons = [
        "adds stable chunk ids for future pressure-bundle selection",
        "adds source_quote, extraction_type, and confidence to every curated item",
    ]
    if any(payload["recovers_missing_graph_field"] for payload in field_summary.values()):
        reasons.append("recovers at least one field that is currently missing in build/knowledge_graph.json")
    if any(payload["current_graph_count"] > 0 and payload["curated_item_count"] > 0 for payload in field_summary.values()):
        reasons.append("deepens existing graph fields into provenance-rich chunk-ready records")
    return reasons


def _validate_slug(value: object, *, field_name: str, path: Path) -> str:
    text = str(value).strip()
    if not text:
        raise InterventionSemanticsValidationError(f"{path}: {field_name} must be non-empty")
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789-")
    if any(ch not in allowed for ch in text):
        raise InterventionSemanticsValidationError(
            f"{path}: {field_name} must contain only lowercase letters, digits, and hyphens"
        )
    return text


def _validate_item_list(value: object, *, field_name: str, path: Path) -> None:
    if not isinstance(value, list):
        raise InterventionSemanticsValidationError(f"{path}: {field_name} must be a list")
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise InterventionSemanticsValidationError(
                f"{path}: {field_name}[{index}] must be an object"
            )
        required = {"text", "source_quote", "extraction_type", "confidence"}
        missing = sorted(required.difference(item))
        if missing:
            raise InterventionSemanticsValidationError(
                f"{path}: {field_name}[{index}] missing required field(s): {', '.join(missing)}"
            )
        unknown = sorted(set(item).difference({"text", "source_quote", "extraction_type", "confidence", "note", "mitigation"}))
        if unknown:
            raise InterventionSemanticsValidationError(
                f"{path}: {field_name}[{index}] unknown field(s): {', '.join(unknown)}"
            )
        _validate_nonempty_string(item["text"], field_name=f"{field_name}[{index}].text", path=path)
        _validate_nonempty_string(
            item["source_quote"],
            field_name=f"{field_name}[{index}].source_quote",
            path=path,
        )
        extraction_type = str(item["extraction_type"]).strip()
        if extraction_type not in ALLOWED_EXTRACTION_TYPES:
            raise InterventionSemanticsValidationError(
                f"{path}: {field_name}[{index}].extraction_type must be one of {sorted(ALLOWED_EXTRACTION_TYPES)}"
            )
        confidence = str(item["confidence"]).strip()
        if confidence not in ALLOWED_CONFIDENCE:
            raise InterventionSemanticsValidationError(
                f"{path}: {field_name}[{index}].confidence must be one of {sorted(ALLOWED_CONFIDENCE)}"
            )
        note = item.get("note", "")
        if note and (not isinstance(note, str) or len(note.strip()) < 8):
            raise InterventionSemanticsValidationError(
                f"{path}: {field_name}[{index}].note must be a meaningful string when present"
            )


def _validate_nonempty_string(value: object, *, field_name: str, path: Path) -> None:
    if not isinstance(value, str) or len(value.strip()) < 3:
        raise InterventionSemanticsValidationError(
            f"{path}: {field_name} must be a non-empty string"
        )


def _build_chunk_id(model_id: str, chunk_type: str, index: int) -> str:
    return f"{model_id}--{chunk_type}--{index:02d}"


def _items_from_payload(value: object) -> tuple[InterventionSemanticItem, ...]:
    items: list[InterventionSemanticItem] = []
    for entry in list(value or []):
        item = dict(entry)
        items.append(
            InterventionSemanticItem(
                text=str(item["text"]),
                source_quote=str(item["source_quote"]),
                extraction_type=str(item["extraction_type"]),
                confidence=str(item["confidence"]),
                note=str(item.get("note", "")),
                mitigation=str(item.get("mitigation", "")),
            )
        )
    return tuple(items)
