from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path


RELATION_SEMANTICS_PILOT_MODEL_IDS = (
    "information-asymmetry",
    "systems-thinking",
    "obligations-controls-mapping",
    "reasoning-mode-router",
    "risk-vs-uncertainty",
    "decision-trees",
    "conjunction-fallacy",
)
ALLOWED_RELATION_FAMILIES = frozenset({"ally", "antagonist", "structured_tension"})
ALLOWED_EXTRACTION_TYPES = frozenset({"explicit", "normalized"})
ALLOWED_CONFIDENCE = frozenset({"high", "medium", "weak"})
REQUIRED_FIELDS = (
    "model_id",
    "source_file",
    "allies",
    "antagonists",
    "structured_tensions",
)
OPTIONAL_FIELDS = ("curation_notes", "deferred_higher_order_notes")
ALLOWED_FIELDS = frozenset((*REQUIRED_FIELDS, *OPTIONAL_FIELDS))
ALLOWED_DEFERRED_FIELDS = frozenset({"allies", "antagonists", "structured_tensions"})


class RelationSemanticsValidationError(ValueError):
    pass


@dataclass(frozen=True)
class RelationItem:
    target_model_id: str
    text: str
    source_quote: str
    extraction_type: str
    confidence: str
    note: str
    tension_type: str


@dataclass(frozen=True)
class RelationSemanticsRecord:
    model_id: str
    source_file: str
    allies: tuple[RelationItem, ...]
    antagonists: tuple[RelationItem, ...]
    structured_tensions: tuple[RelationItem, ...]
    curation_notes: dict[str, object]
    deferred_higher_order_notes: dict[str, tuple[str, ...]]
    path: Path

    @classmethod
    def from_payload(cls, payload: dict[str, object], path: Path) -> "RelationSemanticsRecord":
        return cls(
            model_id=str(payload["model_id"]),
            source_file=str(payload["source_file"]),
            allies=_items_from_payload(payload["allies"], text_key="rationale_text"),
            antagonists=_items_from_payload(payload["antagonists"], text_key="rationale_text"),
            structured_tensions=_items_from_payload(
                payload["structured_tensions"], text_key="tension_text"
            ),
            curation_notes=dict(payload.get("curation_notes", {}) or {}),
            deferred_higher_order_notes={
                key: tuple(str(entry) for entry in entries)
                for key, entries in dict(payload.get("deferred_higher_order_notes", {}) or {}).items()
            },
            path=path,
        )


def load_relation_semantics(
    root: Path,
    *,
    model_ids: tuple[str, ...] | None = None,
    valid_model_ids: set[str] | None = None,
) -> dict[str, RelationSemanticsRecord]:
    relation_dir = Path(root) / "curation" / "relation_semantics"
    if not relation_dir.exists():
        raise RelationSemanticsValidationError(
            f"Missing relation semantics directory: {relation_dir}"
        )

    selected_ids = set(model_ids or ())
    records: dict[str, RelationSemanticsRecord] = {}
    for path in sorted(relation_dir.glob("*.json")):
        if path.name == "schema.json":
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        validate_relation_semantics_payload(
            payload,
            path=path,
            root=Path(root),
            valid_model_ids=valid_model_ids,
        )
        record = RelationSemanticsRecord.from_payload(payload, path)
        if selected_ids and record.model_id not in selected_ids:
            continue
        records[record.model_id] = record

    if selected_ids:
        missing = sorted(selected_ids.difference(records))
        if missing:
            raise RelationSemanticsValidationError(
                f"Missing relation semantics files for: {', '.join(missing)}"
            )
    return records


def validate_relation_semantics_payload(
    payload: dict[str, object],
    *,
    path: Path,
    root: Path,
    valid_model_ids: set[str] | None = None,
) -> None:
    if not isinstance(payload, dict):
        raise RelationSemanticsValidationError(f"{path}: payload must be an object")

    unknown_fields = sorted(set(payload).difference(ALLOWED_FIELDS))
    if unknown_fields:
        raise RelationSemanticsValidationError(
            f"{path}: unknown fields: {', '.join(unknown_fields)}"
        )

    missing_fields = [field for field in REQUIRED_FIELDS if field not in payload]
    if missing_fields:
        raise RelationSemanticsValidationError(
            f"{path}: missing required fields: {', '.join(missing_fields)}"
        )

    model_id = _validate_slug(payload["model_id"], field_name="model_id", path=path)
    if path.stem != model_id:
        raise RelationSemanticsValidationError(
            f"{path}: filename stem must match model_id '{model_id}'"
        )

    root = Path(root)
    source_file = str(payload["source_file"]).strip()
    if not source_file.endswith(".md"):
        raise RelationSemanticsValidationError(f"{path}: source_file must end with .md")
    source_path = root / "MM_CANONICAL_216" / source_file
    if not source_path.exists():
        raise RelationSemanticsValidationError(
            f"{path}: source file does not exist: {source_path}"
        )

    wave1_path = root / "curation" / f"{model_id}.json"
    if not wave1_path.exists():
        raise RelationSemanticsValidationError(
            f"{path}: corresponding Wave 1 curation file is missing: {wave1_path}"
        )

    if valid_model_ids is None:
        kg_path = root / "build" / "knowledge_graph.json"
        if not kg_path.exists():
            raise RelationSemanticsValidationError(
                f"{path}: knowledge graph required for relation target validation: {kg_path}"
            )
        knowledge_graph = json.loads(kg_path.read_text(encoding="utf-8"))
        valid_model_ids = set((knowledge_graph.get("models", {}) or {}).keys())

    _validate_item_list(
        payload["allies"],
        field_name="allies",
        text_key="rationale_text",
        path=path,
        valid_model_ids=valid_model_ids,
    )
    _validate_item_list(
        payload["antagonists"],
        field_name="antagonists",
        text_key="rationale_text",
        path=path,
        valid_model_ids=valid_model_ids,
    )
    _validate_item_list(
        payload["structured_tensions"],
        field_name="structured_tensions",
        text_key="tension_text",
        path=path,
        valid_model_ids=valid_model_ids,
        allow_tension_type=True,
    )

    curation_notes = payload.get("curation_notes", {})
    if curation_notes:
        if not isinstance(curation_notes, dict):
            raise RelationSemanticsValidationError(f"{path}: curation_notes must be an object")
        for note_field in curation_notes:
            if note_field not in {"summary", "donor_drops", "open_questions"}:
                raise RelationSemanticsValidationError(
                    f"{path}: unsupported curation_notes field '{note_field}'"
                )

    deferred = payload.get("deferred_higher_order_notes", {})
    if deferred:
        if not isinstance(deferred, dict):
            raise RelationSemanticsValidationError(
                f"{path}: deferred_higher_order_notes must be an object"
            )
        unsupported = sorted(set(deferred).difference(ALLOWED_DEFERRED_FIELDS))
        if unsupported:
            raise RelationSemanticsValidationError(
                f"{path}: unsupported deferred_higher_order_notes field(s): {', '.join(unsupported)}"
            )
        for key, entries in deferred.items():
            if not isinstance(entries, list):
                raise RelationSemanticsValidationError(
                    f"{path}: deferred_higher_order_notes.{key} must be a list"
                )
            for index, entry in enumerate(entries):
                if not isinstance(entry, str) or len(entry.strip()) < 12:
                    raise RelationSemanticsValidationError(
                        f"{path}: deferred_higher_order_notes.{key}[{index}] must be a meaningful string"
                    )


def build_relation_semantics_preview(
    root: Path,
    *,
    model_ids: tuple[str, ...],
) -> dict[str, object]:
    records = load_relation_semantics(root, model_ids=model_ids)
    relations: list[dict[str, object]] = []
    family_counts = {family: 0 for family in sorted(ALLOWED_RELATION_FAMILIES)}
    extraction_type_counts = {kind: 0 for kind in sorted(ALLOWED_EXTRACTION_TYPES)}
    confidence_counts = {confidence: 0 for confidence in sorted(ALLOWED_CONFIDENCE)}
    per_model_counts: dict[str, dict[str, int]] = {}

    for model_id in model_ids:
        record = records[model_id]
        per_model_counts[model_id] = {}
        for family, items in (
            ("ally", record.allies),
            ("antagonist", record.antagonists),
            ("structured_tension", record.structured_tensions),
        ):
            per_model_counts[model_id][family] = len(items)
            for index, item in enumerate(items, start=1):
                relation = {
                    "relation_id": _build_relation_id(model_id, family, item.target_model_id, index),
                    "model_id": model_id,
                    "relation_family": family,
                    "target_model_id": item.target_model_id,
                    "source_file": record.source_file,
                    "source_quote": item.source_quote,
                    "extraction_type": item.extraction_type,
                    "confidence": item.confidence,
                }
                text_field = "rationale_text" if family != "structured_tension" else "tension_text"
                relation[text_field] = item.text
                if item.note:
                    relation["note"] = item.note
                if item.tension_type:
                    relation["tension_type"] = item.tension_type
                relations.append(relation)
                family_counts[family] += 1
                extraction_type_counts[item.extraction_type] += 1
                confidence_counts[item.confidence] += 1

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pilot_model_ids": list(model_ids),
        "total_relation_count": len(relations),
        "relation_counts_by_family": family_counts,
        "extraction_type_counts": extraction_type_counts,
        "confidence_counts": confidence_counts,
        "per_model_counts": per_model_counts,
        "relations": relations,
    }


def build_relation_semantics_delta_report(
    root: Path,
    *,
    model_ids: tuple[str, ...],
) -> dict[str, object]:
    root = Path(root)
    records = load_relation_semantics(root, model_ids=model_ids)
    knowledge_graph = json.loads((root / "build" / "knowledge_graph.json").read_text(encoding="utf-8"))
    graph_models = knowledge_graph.get("models", {}) if isinstance(knowledge_graph, dict) else {}
    graph_edges = knowledge_graph.get("edges", []) if isinstance(knowledge_graph, dict) else []

    def _count_edges_for_model(mid: str, edge_type: str) -> list[dict[str, object]]:
        return [e for e in graph_edges if isinstance(e, dict) and e.get("source") == mid and e.get("type") == edge_type]

    models_summary: dict[str, object] = {}
    family_counts = {family: 0 for family in sorted(ALLOWED_RELATION_FAMILIES)}
    extraction_type_counts = {kind: 0 for kind in sorted(ALLOWED_EXTRACTION_TYPES)}
    low_confidence_relations: list[dict[str, object]] = []
    recovered_graph_gaps: list[dict[str, object]] = []

    for model_id in model_ids:
        record = records[model_id]
        graph_model = graph_models.get(model_id, {}) if isinstance(graph_models, dict) else {}
        graph_allies = _count_edges_for_model(model_id, "ally")
        graph_antagonists = _count_edges_for_model(model_id, "antagonist")
        graph_tensions = _count_edges_for_model(model_id, "structured_tension")
        field_summary = {
            "allies": _field_delta(
                model_id,
                "ally",
                graph_allies,
                record.allies,
                low_confidence_relations,
                recovered_graph_gaps,
            ),
            "antagonists": _field_delta(
                model_id,
                "antagonist",
                graph_antagonists,
                record.antagonists,
                low_confidence_relations,
                recovered_graph_gaps,
            ),
            "structured_tensions": _field_delta(
                model_id,
                "structured_tension",
                graph_tensions,
                record.structured_tensions,
                low_confidence_relations,
                recovered_graph_gaps,
            ),
        }

        for field_payload in field_summary.values():
            family_counts[field_payload["relation_family"]] += field_payload["curated_item_count"]
            for kind, count in field_payload["extraction_type_counts"].items():
                extraction_type_counts[kind] += count

        models_summary[model_id] = {
            "source_file": record.source_file,
            "current_graph_counts": {
                "allies": len(graph_allies),
                "antagonists": len(graph_antagonists),
                "structured_tensions": len(graph_tensions),
            },
            "curated_counts": {
                "allies": len(record.allies),
                "antagonists": len(record.antagonists),
                "structured_tensions": len(record.structured_tensions),
                "total_relations": len(record.allies)
                + len(record.antagonists)
                + len(record.structured_tensions),
            },
            "field_deltas": field_summary,
            "deferred_higher_order_notes": {
                key: list(value)
                for key, value in record.deferred_higher_order_notes.items()
            },
            "stronger_than_current_graph": _stronger_than_graph_reasons(field_summary),
        }

    total_relations = sum(family_counts.values())
    explicit_relations = extraction_type_counts["explicit"]
    normalized_relations = extraction_type_counts["normalized"]
    preserve_real_content = not low_confidence_relations and total_relations > 0
    contract_good_enough_to_scale = preserve_real_content and all(
        models_summary[model_id]["curated_counts"]["total_relations"] >= 2 for model_id in model_ids
    )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pilot_model_ids": list(model_ids),
        "did_relation_layer_preserve_real_source_backed_content": preserve_real_content,
        "contract_good_enough_for_wave3_scale": contract_good_enough_to_scale,
        "total_relation_count": total_relations,
        "relation_counts_by_family": family_counts,
        "extraction_type_counts": extraction_type_counts,
        "explicit_relation_ratio": round(explicit_relations / total_relations, 4) if total_relations else 0.0,
        "normalized_relation_ratio": round(normalized_relations / total_relations, 4) if total_relations else 0.0,
        "low_confidence_relations": low_confidence_relations,
        "recovered_graph_gaps": recovered_graph_gaps,
        "models": models_summary,
    }


def build_relation_semantics_summary(
    *,
    relation_preview: dict[str, object],
    delta_report: dict[str, object],
) -> dict[str, object]:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pilot_model_ids": relation_preview["pilot_model_ids"],
        "total_relation_count": relation_preview["total_relation_count"],
        "relation_counts_by_family": relation_preview["relation_counts_by_family"],
        "extraction_type_counts": relation_preview["extraction_type_counts"],
        "confidence_counts": relation_preview["confidence_counts"],
        "did_relation_layer_preserve_real_source_backed_content": delta_report[
            "did_relation_layer_preserve_real_source_backed_content"
        ],
        "contract_good_enough_for_wave3_scale": delta_report[
            "contract_good_enough_for_wave3_scale"
        ],
        "recovered_graph_gap_count": len(delta_report["recovered_graph_gaps"]),
        "low_confidence_relation_count": len(delta_report["low_confidence_relations"]),
    }


def render_relation_semantics_preview_markdown(preview: dict[str, object]) -> str:
    lines = [
        "# Relation Semantics Preview",
        "",
        f"- Generated at: {preview['generated_at']}",
        f"- Pilot models: {', '.join(preview['pilot_model_ids'])}",
        f"- Total relation records: {preview['total_relation_count']}",
        "",
        "## Relation Counts By Family",
        "",
    ]
    for family, count in (preview.get("relation_counts_by_family", {}) or {}).items():
        lines.append(f"- {family}: {count}")

    lines.extend(["", "## Preview Relations", ""])
    for relation in preview.get("relations", []) or []:
        text = relation.get("rationale_text") or relation.get("tension_text") or ""
        lines.append(
            f"- `{relation['relation_id']}` | `{relation['model_id']}` -> `{relation['target_model_id']}` | `{relation['relation_family']}` | {text}"
        )
    return "\n".join(lines) + "\n"


def render_relation_semantics_delta_markdown(report: dict[str, object]) -> str:
    lines = [
        "# Relation Semantics Delta Report",
        "",
        f"- Generated at: {report['generated_at']}",
        f"- Preserve real source-backed content: {report['did_relation_layer_preserve_real_source_backed_content']}",
        f"- Contract good enough for broader Wave 3 scaling: {report['contract_good_enough_for_wave3_scale']}",
        f"- Total relation count: {report['total_relation_count']}",
        f"- Recovered graph gap count: {len(report['recovered_graph_gaps'])}",
        f"- Low-confidence relation count: {len(report['low_confidence_relations'])}",
        "",
        "## Model Deltas",
        "",
    ]
    for model_id, payload in (report.get("models", {}) or {}).items():
        lines.append(f"### {model_id}")
        lines.append("")
        lines.append(
            "- Current graph counts: "
            f"allies={payload['current_graph_counts']['allies']}, "
            f"antagonists={payload['current_graph_counts']['antagonists']}, "
            f"structured_tensions={payload['current_graph_counts']['structured_tensions']}"
        )
        lines.append(
            "- Curated relation counts: "
            f"allies={payload['curated_counts']['allies']}, "
            f"antagonists={payload['curated_counts']['antagonists']}, "
            f"structured_tensions={payload['curated_counts']['structured_tensions']}"
        )
        lines.append("- Stronger than current graph because: " + "; ".join(payload["stronger_than_current_graph"]))
        lines.append("")
    return "\n".join(lines) + "\n"


def render_relation_semantics_summary_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Relation Semantics Summary",
        "",
        f"- Generated at: {summary['generated_at']}",
        f"- Pilot models: {', '.join(summary['pilot_model_ids'])}",
        f"- Total relation count: {summary['total_relation_count']}",
        f"- Preserve real source-backed content: {summary['did_relation_layer_preserve_real_source_backed_content']}",
        f"- Contract good enough for broader Wave 3 scaling: {summary['contract_good_enough_for_wave3_scale']}",
        f"- Recovered graph gap count: {summary['recovered_graph_gap_count']}",
        f"- Low-confidence relation count: {summary['low_confidence_relation_count']}",
        "",
    ]
    return "\n".join(lines)


def write_relation_semantics_artifacts(
    root: Path,
    *,
    out_dir: Path,
    model_ids: tuple[str, ...] = RELATION_SEMANTICS_PILOT_MODEL_IDS,
) -> dict[str, Path]:
    root = Path(root)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    relation_preview = build_relation_semantics_preview(root, model_ids=model_ids)
    delta_report = build_relation_semantics_delta_report(root, model_ids=model_ids)
    summary = build_relation_semantics_summary(
        relation_preview=relation_preview,
        delta_report=delta_report,
    )
    model_set_md = render_model_set_markdown(model_ids)

    relation_preview_json_path = out_dir / "relation_preview.json"
    relation_preview_md_path = out_dir / "relation_preview.md"
    delta_report_json_path = out_dir / "delta_report.json"
    delta_report_md_path = out_dir / "delta_report.md"
    summary_json_path = out_dir / "summary.json"
    summary_md_path = out_dir / "summary.md"
    model_set_md_path = out_dir / "model_set.md"

    relation_preview_json_path.write_text(json.dumps(relation_preview, indent=2), encoding="utf-8")
    relation_preview_md_path.write_text(
        render_relation_semantics_preview_markdown(relation_preview),
        encoding="utf-8",
    )
    delta_report_json_path.write_text(json.dumps(delta_report, indent=2), encoding="utf-8")
    delta_report_md_path.write_text(
        render_relation_semantics_delta_markdown(delta_report),
        encoding="utf-8",
    )
    summary_json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    summary_md_path.write_text(
        render_relation_semantics_summary_markdown(summary),
        encoding="utf-8",
    )
    model_set_md_path.write_text(model_set_md, encoding="utf-8")

    return {
        "summary_json": summary_json_path,
        "summary_md": summary_md_path,
        "relation_preview_json": relation_preview_json_path,
        "relation_preview_md": relation_preview_md_path,
        "delta_report_json": delta_report_json_path,
        "delta_report_md": delta_report_md_path,
        "model_set_md": model_set_md_path,
    }


def render_model_set_markdown(model_ids: tuple[str, ...]) -> str:
    intro = (
        "This pilot stays inside the already curated Wave 1 / Wave 2 surface and favors models "
        "whose raw markdown already contains relation-rich allies, antagonists, or explicit structured tensions."
    )
    reasons = {
        "information-asymmetry": "Rich ally section plus explicit tensions against principal-agent-problem and confirmation-bias.",
        "systems-thinking": "High-value ally and antagonist prose even without an explicit structured tension block.",
        "obligations-controls-mapping": "Strong ally table plus explicit structured tensions against authority-bias, status-quo-bias, and confirmation-bias.",
        "reasoning-mode-router": "One of the clearest relation-rich files, with both support models and multiple explicit structured tensions.",
        "risk-vs-uncertainty": "Strong ally and antagonist material plus an explicit structured tension against confirmation-bias.",
        "decision-trees": "Clear ally relationships and explicit tensions against chaos-theory, cognitive-biases, and confirmation-bias.",
        "conjunction-fallacy": "Useful control case with strong ally / antagonist prose but no explicit structured tension block.",
        "base-rates": "Strong ally and explicit tension sections, with a good test of disciplined omission where outside-view and System 1 concepts exceed the current canonical target-id surface.",
        "authority-bias": "Rich explicit tension section and several clean first-order antagonists, while still exposing where antidote language outruns the current canonical id surface.",
        "incentives": "Good mixed case with real ally and antagonist prose but no structured-tension block, useful for testing conservative omission discipline.",
        "expected-value": "High-value ally lattice plus multiple explicit tensions, making it one of the strongest scaling candidates after the pilot.",
        "confirmation-bias": "Strong explicit tensions and good first-order antagonist material, but with several psychologically real ally models that cannot yet be mapped cleanly.",
        "commitment-bias": "Useful bounded case with one clean ally and one clean antagonist, while surfacing the limits of the current canonical relation target surface.",
        "bottlenecks": "Strong explicit tensions and clear first-order ally material, with existing compiled relation coverage thin enough to make provenance improvements meaningful.",
        "prioritization": "Strong ally and antagonist prose with clean leverage-oriented mappings, even though its richer source material extends beyond the current id surface.",
        "adverse-selection": "Harder tail model, but the raw file still provides a strong explicit tension block plus conservative first-order ally mappings.",
        "batna": "Proxy-derived on some ally and antagonist language, but still worth preserving because its explicit tensions are clear and operationally useful.",
        "simplification": "Interpretive tail case with useful tensions and a few clean allies, good for testing whether the contract still holds under more ambiguous prose.",
        "status-quo-bias": "Deliberately sparse tail case that tests omission discipline when source richness outruns the current canonical target-id surface."
    }
    lines = [
        "# Wave 3 Pilot Model Set",
        "",
        intro,
        "",
    ]
    for model_id in model_ids:
        lines.append(f"- `{model_id}`: {reasons.get(model_id, 'Selected for the Wave 3 relation pilot.')}")
    lines.append("")
    return "\n".join(lines)


def _field_delta(
    model_id: str,
    relation_family: str,
    graph_items: list[object],
    curated_items: tuple[RelationItem, ...],
    low_confidence_relations: list[dict[str, object]],
    recovered_graph_gaps: list[dict[str, object]],
) -> dict[str, object]:
    extraction_counts = {kind: 0 for kind in sorted(ALLOWED_EXTRACTION_TYPES)}
    current_graph_count = len(graph_items or [])
    curated_count = len(curated_items)

    if current_graph_count == 0 and curated_count > 0:
        recovered_graph_gaps.append(
            {
                "model_id": model_id,
                "relation_family": relation_family,
                "current_graph_count": 0,
                "curated_item_count": curated_count,
            }
        )

    for item in curated_items:
        extraction_counts[item.extraction_type] += 1
        if item.confidence == "weak":
            low_confidence_relations.append(
                {
                    "model_id": model_id,
                    "relation_family": relation_family,
                    "target_model_id": item.target_model_id,
                    "text": item.text,
                    "source_quote": item.source_quote,
                }
            )

    return {
        "relation_family": relation_family,
        "current_graph_count": current_graph_count,
        "curated_item_count": curated_count,
        "added_count": max(curated_count - current_graph_count, 0),
        "extraction_type_counts": extraction_counts,
    }


def _stronger_than_graph_reasons(field_summary: dict[str, dict[str, object]]) -> list[str]:
    reasons: list[str] = []
    for field_name, payload in field_summary.items():
        if payload["current_graph_count"] == 0 and payload["curated_item_count"] > 0:
            reasons.append(f"{field_name} added where current graph has none")
        elif payload["curated_item_count"] > payload["current_graph_count"]:
            reasons.append(f"{field_name} broadened from {payload['current_graph_count']} to {payload['curated_item_count']}")
    if not reasons:
        reasons.append("preserves provenance and review metadata missing from current graph relations")
    return reasons


def _items_from_payload(items_payload: object, *, text_key: str) -> tuple[RelationItem, ...]:
    items = []
    for entry in list(items_payload):
        items.append(
            RelationItem(
                target_model_id=str(entry["target_model_id"]),
                text=str(entry[text_key]).strip(),
                source_quote=str(entry["source_quote"]).strip(),
                extraction_type=str(entry["extraction_type"]),
                confidence=str(entry["confidence"]),
                note=str(entry.get("note", "")).strip(),
                tension_type=str(entry.get("tension_type", "")).strip(),
            )
        )
    return tuple(items)


def _validate_item_list(
    items_payload: object,
    *,
    field_name: str,
    text_key: str,
    path: Path,
    valid_model_ids: set[str],
    allow_tension_type: bool = False,
) -> None:
    if not isinstance(items_payload, list):
        raise RelationSemanticsValidationError(f"{path}: {field_name} must be a list")

    seen_targets: set[str] = set()
    for index, entry in enumerate(items_payload):
        if not isinstance(entry, dict):
            raise RelationSemanticsValidationError(
                f"{path}: {field_name}[{index}] must be an object"
            )
        allowed = {"target_model_id", text_key, "source_quote", "extraction_type", "confidence", "note"}
        if allow_tension_type:
            allowed.add("tension_type")
        unknown_fields = sorted(set(entry).difference(allowed))
        if unknown_fields:
            raise RelationSemanticsValidationError(
                f"{path}: {field_name}[{index}] unknown fields: {', '.join(unknown_fields)}"
            )

        missing = [name for name in ("target_model_id", text_key, "source_quote", "extraction_type", "confidence") if name not in entry]
        if missing:
            raise RelationSemanticsValidationError(
                f"{path}: {field_name}[{index}] missing fields: {', '.join(missing)}"
            )

        target = _validate_slug(entry["target_model_id"], field_name=f"{field_name}[{index}].target_model_id", path=path)
        if target not in valid_model_ids:
            raise RelationSemanticsValidationError(
                f"{path}: {field_name}[{index}] target_model_id is not a known graph model: {target}"
            )
        if target in seen_targets:
            raise RelationSemanticsValidationError(
                f"{path}: {field_name}[{index}] duplicate target_model_id '{target}'"
            )
        seen_targets.add(target)

        text = str(entry[text_key]).strip()
        if len(text) < 12:
            raise RelationSemanticsValidationError(
                f"{path}: {field_name}[{index}].{text_key} must be a meaningful string"
            )
        source_quote = str(entry["source_quote"]).strip()
        if len(source_quote) < 12:
            raise RelationSemanticsValidationError(
                f"{path}: {field_name}[{index}].source_quote must be a meaningful string"
            )
        extraction_type = str(entry["extraction_type"])
        if extraction_type not in ALLOWED_EXTRACTION_TYPES:
            raise RelationSemanticsValidationError(
                f"{path}: {field_name}[{index}].extraction_type must be one of {sorted(ALLOWED_EXTRACTION_TYPES)}"
            )
        confidence = str(entry["confidence"])
        if confidence not in ALLOWED_CONFIDENCE:
            raise RelationSemanticsValidationError(
                f"{path}: {field_name}[{index}].confidence must be one of {sorted(ALLOWED_CONFIDENCE)}"
            )
        if "note" in entry and not isinstance(entry["note"], str):
            raise RelationSemanticsValidationError(
                f"{path}: {field_name}[{index}].note must be a string"
            )
        if allow_tension_type and "tension_type" in entry and not isinstance(entry["tension_type"], str):
            raise RelationSemanticsValidationError(
                f"{path}: {field_name}[{index}].tension_type must be a string"
            )


def _build_relation_id(model_id: str, family: str, target_model_id: str, index: int) -> str:
    return f"{model_id}--{family}--{index:02d}--{target_model_id}"


def _validate_slug(value: object, *, field_name: str, path: Path) -> str:
    slug = str(value).strip()
    if not slug:
        raise RelationSemanticsValidationError(f"{path}: {field_name} must not be empty")
    parts = slug.split("-")
    if any(not part or not part.replace("0", "").replace("1", "").replace("2", "").replace("3", "").replace("4", "").replace("5", "").replace("6", "").replace("7", "").replace("8", "").replace("9", "").isalnum() and not part.isalnum() for part in parts):
        # Fall through to stricter per-character check below.
        pass
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789-")
    if any(char not in allowed for char in slug):
        raise RelationSemanticsValidationError(
            f"{path}: {field_name} must be a lowercase slug"
        )
    if "--" in slug or slug.startswith("-") or slug.endswith("-"):
        raise RelationSemanticsValidationError(
            f"{path}: {field_name} must be a lowercase slug"
        )
    return slug
