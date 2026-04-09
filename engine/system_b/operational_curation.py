from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path


ALLOWED_REASONING_TYPES = frozenset(
    {
        "abductive",
        "analogical",
        "causal",
        "counterfactual",
        "deductive",
        "diagnostic",
        "metacognitive",
        "probabilistic",
        "systems",
    }
)
ALLOWED_PROVENANCE_SOURCES = frozenset(
    {
        "raw_markdown",
        "donor_draft",
        "reviewed_normalization",
    }
)
ALLOWED_CONFIDENCE = frozenset({"high", "medium", "weak"})
ALLOWED_COMPOUND_SOURCE_BASIS = frozenset({"raw_supported", "reviewed_normalization"})
REQUIRED_FIELDS = (
    "model_id",
    "source_file",
    "select_when",
    "avoid_when",
    "input_type",
    "output_type",
    "reasoning_types",
)
OPTIONAL_FIELDS = ("compound_contracts", "curation_notes", "provenance_notes")
ALLOWED_FIELDS = frozenset((*REQUIRED_FIELDS, *OPTIONAL_FIELDS))
PROVENANCE_REQUIRED_FIELDS = (
    "select_when",
    "avoid_when",
    "input_type",
    "output_type",
    "reasoning_types",
)


class OperationalCurationValidationError(ValueError):
    pass


@dataclass(frozen=True)
class OperationalCurationRecord:
    model_id: str
    source_file: str
    select_when: tuple[str, ...]
    avoid_when: tuple[str, ...]
    input_type: str
    output_type: str
    reasoning_types: tuple[str, ...]
    compound_contracts: tuple[dict[str, object], ...]
    curation_notes: dict[str, object]
    provenance_notes: dict[str, dict[str, object]]
    path: Path

    @classmethod
    def from_payload(cls, payload: dict[str, object], path: Path) -> "OperationalCurationRecord":
        return cls(
            model_id=str(payload["model_id"]),
            source_file=str(payload["source_file"]),
            select_when=tuple(str(item) for item in payload["select_when"]),
            avoid_when=tuple(str(item) for item in payload["avoid_when"]),
            input_type=str(payload["input_type"]),
            output_type=str(payload["output_type"]),
            reasoning_types=tuple(str(item) for item in payload["reasoning_types"]),
            compound_contracts=tuple(payload.get("compound_contracts", ()) or ()),
            curation_notes=dict(payload.get("curation_notes", {}) or {}),
            provenance_notes=dict(payload.get("provenance_notes", {}) or {}),
            path=path,
        )


def load_operational_curation(root: Path, model_ids: tuple[str, ...] | None = None) -> dict[str, OperationalCurationRecord]:
    curation_dir = Path(root) / "curation"
    if not curation_dir.exists():
        raise OperationalCurationValidationError(f"Missing curation directory: {curation_dir}")

    selected_ids = set(model_ids or ())
    records: dict[str, OperationalCurationRecord] = {}
    for path in sorted(curation_dir.glob("*.json")):
        if path.name == "schema.json":
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        validate_operational_curation_payload(payload, path=path, root=Path(root))
        record = OperationalCurationRecord.from_payload(payload, path)
        if selected_ids and record.model_id not in selected_ids:
            continue
        records[record.model_id] = record
    if selected_ids:
        missing = sorted(selected_ids.difference(records))
        if missing:
            raise OperationalCurationValidationError(
                f"Missing curated model files for: {', '.join(missing)}"
            )
    return records


def validate_operational_curation_payload(
    payload: dict[str, object],
    *,
    path: Path,
    root: Path,
) -> None:
    if not isinstance(payload, dict):
        raise OperationalCurationValidationError(f"{path}: payload must be an object")

    unknown_fields = sorted(set(payload).difference(ALLOWED_FIELDS))
    if unknown_fields:
        raise OperationalCurationValidationError(
            f"{path}: unknown fields: {', '.join(unknown_fields)}"
        )

    missing_fields = [field for field in REQUIRED_FIELDS if field not in payload]
    if missing_fields:
        raise OperationalCurationValidationError(
            f"{path}: missing required fields: {', '.join(missing_fields)}"
        )

    model_id = _validate_slug(payload["model_id"], field_name="model_id", path=path)
    if path.stem != model_id:
        raise OperationalCurationValidationError(
            f"{path}: filename stem must match model_id '{model_id}'"
        )

    source_file = str(payload["source_file"]).strip()
    if not source_file.endswith(".md"):
        raise OperationalCurationValidationError(f"{path}: source_file must end with .md")
    source_path = root / "MM_CANONICAL_216" / source_file
    if not source_path.exists():
        raise OperationalCurationValidationError(
            f"{path}: source file does not exist: {source_path}"
        )

    _validate_string_list(payload["select_when"], field_name="select_when", path=path)
    _validate_string_list(payload["avoid_when"], field_name="avoid_when", path=path)
    _validate_nonempty_string(payload["input_type"], field_name="input_type", path=path)
    _validate_nonempty_string(payload["output_type"], field_name="output_type", path=path)

    reasoning_types = payload["reasoning_types"]
    if not isinstance(reasoning_types, list) or not reasoning_types:
        raise OperationalCurationValidationError(f"{path}: reasoning_types must be a non-empty list")
    seen_reasoning_types: set[str] = set()
    for entry in reasoning_types:
        reasoning_type = str(entry).strip()
        if reasoning_type not in ALLOWED_REASONING_TYPES:
            raise OperationalCurationValidationError(
                f"{path}: unsupported reasoning_type '{reasoning_type}'"
            )
        if reasoning_type in seen_reasoning_types:
            raise OperationalCurationValidationError(
                f"{path}: duplicate reasoning_type '{reasoning_type}'"
            )
        seen_reasoning_types.add(reasoning_type)

    compound_contracts = payload.get("compound_contracts", ())
    if compound_contracts:
        if not isinstance(compound_contracts, list):
            raise OperationalCurationValidationError(
                f"{path}: compound_contracts must be a list"
            )
        for index, contract in enumerate(compound_contracts):
            _validate_compound_contract(contract, path=path, index=index)

    curation_notes = payload.get("curation_notes", {})
    if curation_notes:
        if not isinstance(curation_notes, dict):
            raise OperationalCurationValidationError(
                f"{path}: curation_notes must be an object"
            )
        for allowed_note_field in curation_notes:
            if allowed_note_field not in {"summary", "donor_drops", "open_questions"}:
                raise OperationalCurationValidationError(
                    f"{path}: unsupported curation_notes field '{allowed_note_field}'"
                )

    provenance_notes = payload.get("provenance_notes", {})
    if provenance_notes:
        if not isinstance(provenance_notes, dict):
            raise OperationalCurationValidationError(
                f"{path}: provenance_notes must be an object"
            )
        for field_name in PROVENANCE_REQUIRED_FIELDS:
            if field_name not in provenance_notes:
                raise OperationalCurationValidationError(
                    f"{path}: provenance_notes missing required field '{field_name}'"
                )
        for field_name, note in provenance_notes.items():
            if field_name not in (*PROVENANCE_REQUIRED_FIELDS, "compound_contracts"):
                raise OperationalCurationValidationError(
                    f"{path}: unsupported provenance_notes key '{field_name}'"
                )
            _validate_provenance_note(note, path=path, field_name=field_name)


def build_operational_curation_audit(
    root: Path,
    *,
    model_ids: tuple[str, ...],
) -> dict[str, object]:
    root = Path(root)
    records = load_operational_curation(root, model_ids=model_ids)
    knowledge_graph, comparison_graph_source = load_operational_curation_comparison_graph(root)
    graph_models = knowledge_graph.get("models", {}) if isinstance(knowledge_graph, dict) else {}
    graph_edges = knowledge_graph.get("edges", []) if isinstance(knowledge_graph, dict) else []

    models_summary: dict[str, object] = {}
    provenance_source_counts = {source: 0 for source in sorted(ALLOWED_PROVENANCE_SOURCES)}
    weak_confidence_fields: list[dict[str, object]] = []
    unresolved_items: list[dict[str, object]] = []

    for model_id in model_ids:
        record = records[model_id]
        graph_model = graph_models.get(model_id, {}) if isinstance(graph_models, dict) else {}
        graph_select_when = tuple(str(item) for item in graph_model.get("select_when", ()) or ())
        graph_danger_when = tuple(str(item) for item in graph_model.get("danger_when", ()) or ())
        graph_reasoning_types = tuple(str(item) for item in graph_model.get("reasoning_types", ()) or ())

        provenance_by_field: dict[str, object] = {}
        for field_name, note in record.provenance_notes.items():
            sources = tuple(note.get("sources", ()))
            confidence = str(note.get("confidence", "")).strip()
            provenance_by_field[field_name] = {
                "sources": list(sources),
                "confidence": confidence,
                "note": str(note.get("note", "")),
            }
            for source in sources:
                provenance_source_counts[source] += 1
            if confidence == "weak":
                weak_confidence_fields.append(
                    {
                        "model_id": model_id,
                        "field": field_name,
                        "note": str(note.get("note", "")),
                    }
                )

        improvement_over_current_graph = _build_improvement_summary(
            record=record,
            graph_model=graph_model if isinstance(graph_model, dict) else {},
        )
        model_unresolved = _collect_unresolved_items(record)
        for item in model_unresolved:
            unresolved_items.append({"model_id": model_id, "note": item})

        models_summary[model_id] = {
            "source_file": record.source_file,
            "curated_counts": {
                "select_when": len(record.select_when),
                "avoid_when": len(record.avoid_when),
                "reasoning_types": len(record.reasoning_types),
                "compound_contracts": len(record.compound_contracts),
            },
            "current_graph_counts": {
                "select_when": len(graph_select_when),
                "danger_when": len(graph_danger_when),
                "reasoning_types": len(graph_reasoning_types),
                "allies": sum(1 for e in graph_edges if isinstance(e, dict) and e.get("source") == model_id and e.get("type") == "ally"),
                "antagonists": sum(1 for e in graph_edges if isinstance(e, dict) and e.get("source") == model_id and e.get("type") == "antagonist"),
            },
            "input_output_comparison": {
                "curated_input_type": record.input_type,
                "curated_output_type": record.output_type,
                "graph_has_input_type": bool(graph_model.get("input_type")) if isinstance(graph_model, dict) else False,
                "graph_has_output_type": bool(graph_model.get("output_type")) if isinstance(graph_model, dict) else False,
            },
            "provenance_by_field": provenance_by_field,
            "improvement_over_current_graph": improvement_over_current_graph,
            "unresolved_items": model_unresolved,
        }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "curation_root": str(root / "curation"),
        "schema_path": str(root / "curation" / "schema.json"),
        "all_files_valid": True,
        "validated_model_count": len(records),
        "validated_model_ids": list(model_ids),
        "comparison_graph_source": comparison_graph_source,
        "provenance_source_counts": provenance_source_counts,
        "weak_confidence_fields": weak_confidence_fields,
        "unresolved_items": unresolved_items,
        "models": models_summary,
    }


def load_operational_curation_comparison_graph(
    root: Path,
) -> tuple[dict[str, object], str]:
    root = Path(root)
    build_graph = json.loads((root / "build" / "knowledge_graph.json").read_text(encoding="utf-8"))
    metadata = build_graph.get("metadata", {}) if isinstance(build_graph, dict) else {}
    if metadata.get("uses_operational_curation"):
        from .compilation_bundle import KnowledgeCompiler

        legacy_dir = root / ".tmp" / "operational_curation_legacy_baseline"
        compiler = KnowledgeCompiler.load(root)
        compiler.compile_preview(
            output_dir=legacy_dir,
            use_operational_curation=False,
        )
        legacy_graph = json.loads((legacy_dir / "knowledge_graph.json").read_text(encoding="utf-8"))
        return legacy_graph, "legacy-baseline-preview"
    return build_graph, "current-build"


def render_operational_curation_audit_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Operational Curation Audit",
        "",
        f"- Generated at: {summary['generated_at']}",
        f"- Validated model count: {summary['validated_model_count']}",
        f"- All files valid: {summary['all_files_valid']}",
        "",
        "## Provenance Mix",
        "",
    ]
    for source, count in (summary.get("provenance_source_counts", {}) or {}).items():
        lines.append(f"- {source}: {count}")

    weak_confidence_fields = summary.get("weak_confidence_fields", []) or []
    lines.extend(["", "## Model Review", ""])
    for model_id, payload in (summary.get("models", {}) or {}).items():
        lines.append(f"### {model_id}")
        lines.append("")
        lines.append(f"- Source file: `{payload['source_file']}`")
        curated_counts = payload.get("curated_counts", {}) or {}
        lines.append(
            "- Curated counts: "
            f"select_when={curated_counts.get('select_when', 0)}, "
            f"avoid_when={curated_counts.get('avoid_when', 0)}, "
            f"reasoning_types={curated_counts.get('reasoning_types', 0)}, "
            f"compound_contracts={curated_counts.get('compound_contracts', 0)}"
        )
        graph_counts = payload.get("current_graph_counts", {}) or {}
        lines.append(
            "- Current graph counts: "
            f"select_when={graph_counts.get('select_when', 0)}, "
            f"danger_when={graph_counts.get('danger_when', 0)}, "
            f"reasoning_types={graph_counts.get('reasoning_types', 0)}, "
            f"allies={graph_counts.get('allies', 0)}, "
            f"antagonists={graph_counts.get('antagonists', 0)}"
        )
        lines.append("- Improvement over current graph:")
        for item in payload.get("improvement_over_current_graph", ()) or ():
            lines.append(f"  - {item}")
        unresolved = payload.get("unresolved_items", ()) or ()
        if unresolved:
            lines.append("- Unresolved items:")
            for item in unresolved:
                lines.append(f"  - {item}")
        lines.append("")

    lines.append("## Weak-Confidence Fields")
    lines.append("")
    if weak_confidence_fields:
        for item in weak_confidence_fields:
            lines.append(
                f"- {item['model_id']}::{item['field']} - {item['note']}"
            )
    else:
        lines.append("- None")
    lines.append("")
    return "\n".join(lines)


def _build_improvement_summary(
    *,
    record: OperationalCurationRecord,
    graph_model: dict[str, object],
) -> list[str]:
    improvements: list[str] = []
    graph_select_when = tuple(str(item) for item in graph_model.get("select_when", ()) or ())
    if len(record.select_when) > len(graph_select_when):
        improvements.append(
            f"Adds {len(record.select_when)} reviewed select_when triggers where the current graph has {len(graph_select_when)}."
        )
    graph_danger_when = tuple(str(item) for item in graph_model.get("danger_when", ()) or ())
    if len(record.avoid_when) > len(graph_danger_when):
        improvements.append(
            f"Adds {len(record.avoid_when)} reviewed avoid_when conditions against {len(graph_danger_when)} current graph danger_when entries."
        )
    if not graph_model.get("input_type"):
        improvements.append("Introduces an explicit input_type that the current graph does not carry.")
    if not graph_model.get("output_type"):
        improvements.append("Introduces an explicit output_type that the current graph does not carry.")
    if not graph_model.get("reasoning_types"):
        improvements.append("Introduces explicit reasoning_types that the current graph does not carry.")
    if not improvements:
        improvements.append("No field-count gain over the current graph; value is mainly in reviewed provenance and normalization.")
    return improvements


def _collect_unresolved_items(record: OperationalCurationRecord) -> list[str]:
    unresolved = list(record.curation_notes.get("open_questions", ()) or ())
    for field_name, note in record.provenance_notes.items():
        if note.get("confidence") == "weak":
            unresolved.append(f"Weak-confidence field {field_name}: {note.get('note', '')}")
    return [str(item) for item in unresolved if str(item).strip()]


def _validate_compound_contract(contract: object, *, path: Path, index: int) -> None:
    if not isinstance(contract, dict):
        raise OperationalCurationValidationError(
            f"{path}: compound_contracts[{index}] must be an object"
        )
    for field_name in ("target_model_id", "context_trigger", "rationale", "source_basis"):
        if field_name not in contract:
            raise OperationalCurationValidationError(
                f"{path}: compound_contracts[{index}] missing '{field_name}'"
            )
    _validate_slug(contract["target_model_id"], field_name=f"compound_contracts[{index}].target_model_id", path=path)
    _validate_nonempty_string(contract["context_trigger"], field_name=f"compound_contracts[{index}].context_trigger", path=path)
    _validate_nonempty_string(contract["rationale"], field_name=f"compound_contracts[{index}].rationale", path=path)
    source_basis = str(contract["source_basis"]).strip()
    if source_basis not in ALLOWED_COMPOUND_SOURCE_BASIS:
        raise OperationalCurationValidationError(
            f"{path}: compound_contracts[{index}].source_basis must be one of {sorted(ALLOWED_COMPOUND_SOURCE_BASIS)}"
        )


def _validate_provenance_note(note: object, *, path: Path, field_name: str) -> None:
    if not isinstance(note, dict):
        raise OperationalCurationValidationError(
            f"{path}: provenance_notes.{field_name} must be an object"
        )
    for required in ("sources", "confidence", "note"):
        if required not in note:
            raise OperationalCurationValidationError(
                f"{path}: provenance_notes.{field_name} missing '{required}'"
            )
    sources = note["sources"]
    if not isinstance(sources, list) or not sources:
        raise OperationalCurationValidationError(
            f"{path}: provenance_notes.{field_name}.sources must be a non-empty list"
        )
    seen_sources: set[str] = set()
    for source in sources:
        source_name = str(source).strip()
        if source_name not in ALLOWED_PROVENANCE_SOURCES:
            raise OperationalCurationValidationError(
                f"{path}: provenance_notes.{field_name}.sources contains unsupported source '{source_name}'"
            )
        if source_name in seen_sources:
            raise OperationalCurationValidationError(
                f"{path}: provenance_notes.{field_name}.sources contains duplicate source '{source_name}'"
            )
        seen_sources.add(source_name)
    confidence = str(note["confidence"]).strip()
    if confidence not in ALLOWED_CONFIDENCE:
        raise OperationalCurationValidationError(
            f"{path}: provenance_notes.{field_name}.confidence must be one of {sorted(ALLOWED_CONFIDENCE)}"
        )
    _validate_nonempty_string(note["note"], field_name=f"provenance_notes.{field_name}.note", path=path)


def _validate_slug(value: object, *, field_name: str, path: Path) -> str:
    slug = str(value).strip()
    if not slug or any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789-" for ch in slug):
        raise OperationalCurationValidationError(
            f"{path}: {field_name} must be a lowercase slug"
        )
    return slug


def _validate_nonempty_string(value: object, *, field_name: str, path: Path) -> None:
    if not str(value).strip():
        raise OperationalCurationValidationError(f"{path}: {field_name} must be a non-empty string")


def _validate_string_list(value: object, *, field_name: str, path: Path) -> None:
    if not isinstance(value, list) or not value:
        raise OperationalCurationValidationError(f"{path}: {field_name} must be a non-empty list")
    seen: set[str] = set()
    for item in value:
        text = str(item).strip()
        if len(text) < 8:
            raise OperationalCurationValidationError(
                f"{path}: {field_name} entries must be meaningful strings"
            )
        if text in seen:
            raise OperationalCurationValidationError(
                f"{path}: {field_name} contains duplicate entry '{text}'"
            )
        seen.add(text)
