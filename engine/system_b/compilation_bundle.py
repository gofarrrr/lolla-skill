from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import json
from pathlib import Path
import re
import tempfile

from .intervention_semantics import InterventionSemanticItem, load_intervention_semantics
from .operational_curation import load_operational_curation
from .relation_semantics import load_relation_semantics


@dataclass(frozen=True)
class CompilationBundle:
    root: Path
    knowledge_graph_path: Path
    relationship_graph_path: Path
    manifest_path: Path
    report_path: Path
    model_count: int
    knowledge_edge_count: int
    relationship_edge_count: int
    tendency_link_count: int


@dataclass(frozen=True)
class CompilationResult:
    bundle: CompilationBundle
    is_valid: bool
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


class KnowledgeCompiler:
    def __init__(self, root: Path) -> None:
        self._root = Path(root)

    @classmethod
    def load(cls, root: Path) -> "KnowledgeCompiler":
        return cls(root)

    def compile(self) -> CompilationResult:
        build_dir = self._root / "build"
        return self._compile_to_directory(
            output_dir=build_dir,
            use_operational_curation=True,
            include_operational_curation_review=False,
            mode_name="layer2b-canonical",
        )

    def compile_preview(
        self,
        *,
        output_dir: Path,
        use_operational_curation: bool = False,
    ) -> CompilationResult:
        mode_name = (
            "layer2b-preview"
            if use_operational_curation
            else "legacy-baseline-preview"
        )
        return self._compile_to_directory(
            output_dir=Path(output_dir),
            use_operational_curation=use_operational_curation,
            include_operational_curation_review=use_operational_curation,
            mode_name=mode_name,
        )

    def compile_intervention_semantics_preview(
        self,
        *,
        output_dir: Path,
    ) -> dict[str, Path]:
        from .intervention_semantics_compiler_preview import (
            write_intervention_semantics_compiler_preview_artifacts,
        )

        return write_intervention_semantics_compiler_preview_artifacts(
            self._root,
            out_dir=Path(output_dir),
        )

    def compile_relation_semantics_preview(
        self,
        *,
        output_dir: Path,
    ) -> dict[str, Path]:
        from .relation_semantics_compiler_preview import (
            write_relation_semantics_compiler_preview_artifacts,
        )

        return write_relation_semantics_compiler_preview_artifacts(
            self._root,
            out_dir=Path(output_dir),
        )

    def compile_higher_order_composition_preview(
        self,
        *,
        output_dir: Path,
    ) -> dict[str, Path]:
        from .higher_order_composition_compiler_preview import (
            write_higher_order_composition_compiler_preview_artifacts,
        )

        return write_higher_order_composition_compiler_preview_artifacts(
            self._root,
            out_dir=Path(output_dir),
        )

    def validate_existing_bundle(self) -> CompilationResult:
        return self._validate_bundle_directory(self._root / "build")

    def _compile_to_directory(
        self,
        *,
        output_dir: Path,
        use_operational_curation: bool,
        include_operational_curation_review: bool,
        mode_name: str,
    ) -> CompilationResult:
        output_dir.mkdir(parents=True, exist_ok=True)

        curation_metadata: dict[str, object] = _empty_curation_metadata()
        if _has_source_assets(self._root):
            kg, relationship_graph, curation_metadata = _compile_from_source_assets(
                self._root,
                use_operational_curation=use_operational_curation,
            )
        else:
            _bundle, kg, relationship_graph = self._load_bundle_source(self._root / "build")
            if use_operational_curation and (self._root / "curation").exists():
                curation_metadata = _apply_operational_curation_to_models(
                    self._root,
                    kg.get("models", {}) if isinstance(kg, dict) else {},
                )

        _apply_wave5_reframing_overlay(
            self._root,
            kg.get("models", {}) if isinstance(kg, dict) else {},
            kg if isinstance(kg, dict) else {},
        )
        _apply_prerequisite_edges_overlay(
            self._root,
            kg if isinstance(kg, dict) else {},
        )

        bundle = _bundle_from_payloads(self._root, kg, relationship_graph, build_dir=output_dir)
        _rewrite_knowledge_graph_metadata(kg, bundle)
        _rewrite_compilation_mode_metadata(
            kg,
            mode_name=mode_name,
            use_operational_curation=use_operational_curation,
            include_operational_curation_review=include_operational_curation_review,
            curation_metadata=curation_metadata,
        )
        _atomic_write_text(
            bundle.knowledge_graph_path,
            json.dumps(kg, indent=2),
        )
        _atomic_write_text(
            bundle.relationship_graph_path,
            json.dumps(relationship_graph, indent=2),
        )
        _atomic_write_text(
            bundle.report_path,
            _build_report_text(
                bundle,
                mode_name=mode_name,
                use_operational_curation=use_operational_curation,
                curation_metadata=curation_metadata,
            ),
        )
        manifest = _build_manifest_payload(
            bundle,
            mode_name=mode_name,
            use_operational_curation=use_operational_curation,
            curation_metadata=curation_metadata,
        )
        _atomic_write_text(
            bundle.manifest_path,
            json.dumps(manifest, indent=2),
        )
        return self._validate_bundle_directory(output_dir)

    def _validate_bundle_directory(self, build_dir: Path) -> CompilationResult:
        bundle, kg, relationship_graph = self._load_bundle_source(build_dir)
        report_path = bundle.report_path
        report_text = report_path.read_text(encoding="utf-8")

        errors: list[str] = []
        warnings: list[str] = []

        metadata = kg.get("metadata", {}) or {}
        if _coerce_int(metadata.get("total_models_processed")) != bundle.model_count:
            errors.append(
                f"Knowledge graph metadata drift: total_models_processed={metadata.get('total_models_processed')} actual={bundle.model_count}"
            )
        if _coerce_int(metadata.get("total_edges")) != bundle.knowledge_edge_count:
            errors.append(
                f"Knowledge graph metadata drift: total_edges={metadata.get('total_edges')} actual={bundle.knowledge_edge_count}"
            )
        if _coerce_int(metadata.get("total_tendency_links")) != bundle.tendency_link_count:
            errors.append(
                f"Knowledge graph metadata drift: total_tendency_links={metadata.get('total_tendency_links')} actual={bundle.tendency_link_count}"
            )

        report_summary = _parse_report_summary(report_text)
        if report_summary.get("total_models") not in (None, bundle.model_count):
            errors.append(
                f"Compilation report drift: total_models={report_summary.get('total_models')} actual={bundle.model_count}"
            )
        if report_summary.get("total_edges") not in (None, bundle.knowledge_edge_count):
            errors.append(
                f"Compilation report drift: total_edges={report_summary.get('total_edges')} actual={bundle.knowledge_edge_count}"
            )
        if report_summary.get("total_tendency_links") not in (None, bundle.tendency_link_count):
            errors.append(
                f"Compilation report drift: total_tendency_links={report_summary.get('total_tendency_links')} actual={bundle.tendency_link_count}"
            )

        if not isinstance(relationship_graph, list):
            errors.append("Relationship graph must be a list of relation edges")
        elif not relationship_graph:
            warnings.append("Relationship graph is present but empty")

        if bundle.manifest_path.exists():
            manifest = json.loads(bundle.manifest_path.read_text(encoding="utf-8"))
            errors.extend(_manifest_drift_errors(manifest, bundle))
        else:
            warnings.append("Compilation manifest is missing")

        return CompilationResult(
            bundle=bundle,
            is_valid=not errors,
            errors=tuple(errors),
            warnings=tuple(warnings),
        )

    def _load_bundle_source(
        self,
        build_dir: Path,
    ) -> tuple[CompilationBundle, dict[str, object], object]:
        kg_path = build_dir / "knowledge_graph.json"
        relationship_path = build_dir / "relationship_graph.json"
        manifest_path = build_dir / "compilation_manifest.json"
        report_path = build_dir / "compilation_report.md"

        kg = json.loads(kg_path.read_text(encoding="utf-8"))
        relationship_graph = json.loads(relationship_path.read_text(encoding="utf-8"))
        bundle = _bundle_from_payloads(self._root, kg, relationship_graph, build_dir=build_dir)
        bundle = CompilationBundle(
            root=bundle.root,
            knowledge_graph_path=kg_path,
            relationship_graph_path=relationship_path,
            manifest_path=manifest_path,
            report_path=report_path,
            model_count=bundle.model_count,
            knowledge_edge_count=bundle.knowledge_edge_count,
            relationship_edge_count=bundle.relationship_edge_count,
            tendency_link_count=bundle.tendency_link_count,
        )
        return bundle, kg, relationship_graph


def _has_source_assets(root: Path) -> bool:
    return (root / "MM_CANONICAL_216").exists() and (root / "munger_structural_mapping.md").exists()


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        handle.write(content)
        handle.flush()
        Path(handle.name).replace(path)


def _bundle_from_payloads(
    root: Path,
    kg: dict[str, object],
    relationship_graph: object,
    *,
    build_dir: Path | None = None,
) -> CompilationBundle:
    build_dir = build_dir or (root / "build")
    return CompilationBundle(
        root=root,
        knowledge_graph_path=build_dir / "knowledge_graph.json",
        relationship_graph_path=build_dir / "relationship_graph.json",
        manifest_path=build_dir / "compilation_manifest.json",
        report_path=build_dir / "compilation_report.md",
        model_count=len(kg.get("models", {}) or {}),
        knowledge_edge_count=len(kg.get("edges", []) or []),
        relationship_edge_count=len(relationship_graph) if isinstance(relationship_graph, list) else 0,
        tendency_link_count=_count_tendency_links(kg.get("tendencies", {}) or {}),
    )


def _compile_from_source_assets(
    root: Path,
    *,
    use_operational_curation: bool = False,
) -> tuple[dict[str, object], list[dict[str, object]], dict[str, object]]:
    corpus_dir = root / "MM_CANONICAL_216"
    models = _compile_models(corpus_dir)
    curation_metadata: dict[str, object] = dict(_empty_curation_metadata())
    if use_operational_curation and (root / "curation").exists():
        curation_metadata.update(_apply_operational_curation_to_models(root, models))
    if use_operational_curation and _intervention_semantics_dir(root).exists():
        curation_metadata.update(_apply_intervention_semantics_overlay(root, models))
    tendencies = _compile_tendencies(
        root / "munger_structural_mapping.md",
        root / "munger_routing_table.json",
        models,
    )
    edges: list[dict[str, object]] = []
    edge_seen: set[tuple[object, ...]] = set()
    _extend_tendency_knowledge_edges(edges, edge_seen, models, tendencies)

    if use_operational_curation and _relation_semantics_dir(root).exists():
        relationship_graph, rel_meta = _build_wave3_relationship_graph(root, models)
        curation_metadata.update(rel_meta)
        _extend_wave3_model_relation_knowledge_edges(edges, edge_seen, relationship_graph, models)
        model_relation_edges_source = "relation_semantics_wave3"
    else:
        # Legacy path: use_operational_curation=False. Model-level relation fields
        # (allies, antagonists, structured_tensions) were removed from _compile_model()
        # output, so this produces no relation edges. Kept for backward compatibility.
        relationship_graph = _build_relationship_graph(models)
        _extend_markdown_model_relation_knowledge_edges(edges, edge_seen, models)
        model_relation_edges_source = "markdown_model_file"

    kg = {
        "metadata": {
            "version": "1.0",
            "compiled_date": date.today().isoformat(),
            "source_file_count": len(list(corpus_dir.glob("*.md"))),
            "total_models_processed": len(models),
            "total_edges": len(edges),
            "total_tendency_links": _count_tendency_links(tendencies),
            "model_relation_edges_source": model_relation_edges_source,
        },
        "models": models,
        "tendencies": tendencies,
        "edges": edges,
    }
    return kg, relationship_graph, curation_metadata


def _apply_operational_curation_to_models(
    root: Path,
    models: dict[str, dict[str, object]],
) -> dict[str, object]:
    records = load_operational_curation(root)
    applied_model_ids: list[str] = []
    missing_model_ids: list[str] = []
    overwritten_non_empty_field_count = 0
    changed_field_count = 0
    field_review_metadata: dict[str, object] = {}
    contested_field_count = 0

    for model_id, record in records.items():
        model = models.get(model_id)
        if not isinstance(model, dict):
            missing_model_ids.append(model_id)
            continue
        applied_model_ids.append(model_id)
        model_field_metadata: dict[str, object] = {}
        overlay = {
            "select_when": list(record.select_when),
            "danger_when": list(record.avoid_when),
            "input_type": record.input_type,
            "output_type": record.output_type,
            "reasoning_types": list(record.reasoning_types),
        }
        curated_field_names = {
            "select_when": "select_when",
            "danger_when": "avoid_when",
            "input_type": "input_type",
            "output_type": "output_type",
            "reasoning_types": "reasoning_types",
        }
        for field_name, curated_value in overlay.items():
            current_value = model.get(field_name)
            if current_value == curated_value:
                overwritten_non_empty = bool(current_value)
            else:
                overwritten_non_empty = bool(current_value)
                if overwritten_non_empty:
                    overwritten_non_empty_field_count += 1
                changed_field_count += 1
                model[field_name] = curated_value

            curated_field_name = curated_field_names[field_name]
            provenance = dict(record.provenance_notes.get(curated_field_name, {}) or {})
            sources = list(provenance.get("sources", ()) or ())
            confidence = str(provenance.get("confidence", "")).strip()
            contested = "raw_markdown" not in sources or confidence != "high"
            if contested:
                contested_field_count += 1
            model_field_metadata[field_name] = {
                "curated_field": curated_field_name,
                "compiled_field": field_name,
                "sources": sources,
                "confidence": confidence,
                "note": str(provenance.get("note", "")),
                "contested": contested,
                "overwrites_non_empty_current_graph": overwritten_non_empty,
            }

        field_review_metadata[model_id] = {
            "source_file": record.source_file,
            "fields": model_field_metadata,
        }

    return {
        "applied_model_ids": sorted(applied_model_ids),
        "applied_model_count": len(applied_model_ids),
        "missing_model_ids": sorted(missing_model_ids),
        "missing_model_count": len(missing_model_ids),
        "changed_field_count": changed_field_count,
        "overwritten_non_empty_field_count": overwritten_non_empty_field_count,
        "contested_field_count": contested_field_count,
        "injected_fields": [
            "select_when",
            "danger_when",
            "input_type",
            "output_type",
            "reasoning_types",
        ],
        "field_review_metadata": field_review_metadata,
    }


def _apply_wave5_reframing_overlay(
    root: Path,
    models: dict[str, dict[str, object]],
    kg: dict[str, object],
) -> None:
    """Optional Wave 5 overlay: add reframing semantics to model objects.

    Reads ``curation/reframing_semantics/*.json`` and:
    1. Adds ``reframing_when`` and ``frame_patterns_challenged`` to model objects.
    2. Builds a ``reframing_routing`` section mapping frame patterns → model lists.

    When the directory is absent, this is a no-op (existing KG unchanged).
    """
    reframing_dir = root / "curation" / "reframing_semantics"
    if not reframing_dir.is_dir():
        return

    reframing_routing: dict[str, list[str]] = {}

    for path in sorted(reframing_dir.glob("*.json")):
        if path.name.startswith("_"):
            continue
        try:
            entry = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        model_id = entry.get("model_id", "")
        if not model_id or not entry.get("has_reframing_activation"):
            continue

        model = models.get(model_id)
        if not isinstance(model, dict):
            continue

        model["reframing_when"] = list(entry.get("reframing_when", []))
        model["frame_patterns_challenged"] = list(entry.get("frame_patterns_challenged", []))
        model["reframing_move"] = entry.get("reframing_move", "")

        for pattern in entry.get("frame_patterns_challenged", []):
            reframing_routing.setdefault(pattern, [])
            if model_id not in reframing_routing[pattern]:
                reframing_routing[pattern].append(model_id)

    if reframing_routing:
        kg["reframing_routing"] = {k: sorted(v) for k, v in sorted(reframing_routing.items())}


def _apply_prerequisite_edges_overlay(root: Path, kg: dict[str, object]) -> None:
    """Load validated prerequisite edges from curation and add to KG.

    Reads ``curation/prerequisite_semantics/*.json`` and writes a flat
    ``prerequisite_edges`` list to the KG dict.  No-op when the directory
    is absent.
    """
    prereq_dir = root / "curation" / "prerequisite_semantics"
    if not prereq_dir.is_dir():
        return

    edges: list[dict[str, str]] = []
    for path in sorted(prereq_dir.glob("*.json")):
        if path.name.startswith("_"):
            continue
        try:
            entry = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        dependent = entry.get("model_id", "")
        if not dependent:
            continue

        for prereq in entry.get("prerequisites", []):
            if prereq.get("validation_status") != "confirmed":
                continue
            edges.append({
                "dependent": dependent,
                "prerequisite": prereq["prerequisite_model_id"],
                "dependency_type": prereq.get("dependency_type", "requires"),
                "rationale": prereq.get("rationale_text", ""),
            })

    if edges:
        kg["prerequisite_edges"] = edges


def _empty_curation_metadata() -> dict[str, object]:
    return {
        "applied_model_ids": [],
        "applied_model_count": 0,
        "missing_model_ids": [],
        "missing_model_count": 0,
        "changed_field_count": 0,
        "overwritten_non_empty_field_count": 0,
        "contested_field_count": 0,
        "injected_fields": [],
        "field_review_metadata": {},
        "uses_intervention_semantics_overlay": False,
        "intervention_semantics_overlay": {},
        "uses_relation_semantics_wave3": False,
        "relation_semantics_wave3": {},
    }


def _intervention_semantics_dir(root: Path) -> Path:
    return root / "curation" / "intervention_semantics"


def _relation_semantics_dir(root: Path) -> Path:
    return root / "curation" / "relation_semantics"


def _compiled_failure_mode_item(item: InterventionSemanticItem) -> dict[str, object]:
    mode = str(item.source_quote).strip()
    if len(mode) > 120:
        text = str(item.text).strip()
        mode = text[:100] + ("..." if len(text) > 100 else "")
    return {
        "mode": mode or "Failure mode",
        "description": item.text,
        "mitigation": item.mitigation if item.mitigation else None,
        "source_quote": item.source_quote,
        "extraction_type": item.extraction_type,
        "confidence": item.confidence,
    }


def _compiled_intervention_text_item(item: InterventionSemanticItem) -> dict[str, object]:
    return {
        "description": item.text,
        "source_quote": item.source_quote,
        "extraction_type": item.extraction_type,
        "confidence": item.confidence,
    }


def _apply_intervention_semantics_overlay(
    root: Path,
    models: dict[str, dict[str, object]],
) -> dict[str, object]:
    records = load_intervention_semantics(root)
    model_keys = set(models.keys())
    applied: list[str] = []
    missing = sorted(model_keys.difference(records))
    total_fm = 0
    total_pm = 0
    total_h = 0
    for model_id, model in models.items():
        record = records.get(model_id)
        if record is None:
            continue
        applied.append(model_id)
        model["failure_modes"] = [_compiled_failure_mode_item(i) for i in record.failure_modes]
        model["premortem_questions"] = [
            _compiled_intervention_text_item(i) for i in record.premortem_questions
        ]
        model["heuristics"] = [_compiled_intervention_text_item(i) for i in record.heuristics]
        total_fm += len(record.failure_modes)
        total_pm += len(record.premortem_questions)
        total_h += len(record.heuristics)
    return {
        "uses_intervention_semantics_overlay": True,
        "intervention_semantics_overlay": {
            "applied_model_ids": sorted(applied),
            "applied_model_count": len(applied),
            "missing_model_ids": missing,
            "missing_model_count": len(missing),
            "total_failure_modes": total_fm,
            "total_premortem_questions": total_pm,
            "total_heuristics": total_h,
        },
    }


def _wave3_confidence_to_ally_affinity(confidence: str) -> float:
    return {"high": 0.9, "medium": 0.75, "weak": 0.65}.get(str(confidence).strip(), 0.72)


def _wave3_confidence_to_risk_affinity(confidence: str) -> float:
    return {"high": 0.25, "medium": 0.22, "weak": 0.2}.get(str(confidence).strip(), 0.2)


def _build_wave3_relationship_graph(
    root: Path,
    models: dict[str, dict[str, object]],
) -> tuple[list[dict[str, object]], dict[str, object]]:
    valid_ids = set(models.keys())
    records = load_relation_semantics(root, valid_model_ids=valid_ids)
    graph: list[dict[str, object]] = []
    seen: set[tuple[str, str, str]] = set()

    def append_edge(
        source_model_id: str,
        target_model_id: str,
        edge_type: str,
        *,
        source_description: str,
        source_quote: str,
        extraction_type: str,
        confidence: str,
        composition_affinity: float,
        tension_type: str = "",
    ) -> None:
        if target_model_id not in valid_ids:
            return
        key = (source_model_id, target_model_id, edge_type)
        if key in seen:
            return
        seen.add(key)
        edge: dict[str, object] = {
            "source_model_id": source_model_id,
            "target_model_id": target_model_id,
            "edge_type": edge_type,
            "source_description": source_description,
            "target_description": "",
            "is_reciprocal": False,
            "tension_depth": "moderate",
            "composition_affinity": composition_affinity,
            "source_quote": source_quote,
            "extraction_type": extraction_type,
            "confidence": confidence,
            "curated": True,
        }
        if tension_type:
            edge["tension_type"] = tension_type
        graph.append(edge)

    for model_id, record in records.items():
        if model_id not in valid_ids:
            continue
        for item in record.allies:
            append_edge(
                model_id,
                item.target_model_id,
                "ally",
                source_description=item.text,
                source_quote=item.source_quote,
                extraction_type=item.extraction_type,
                confidence=item.confidence,
                composition_affinity=_wave3_confidence_to_ally_affinity(item.confidence),
            )
        for item in record.antagonists:
            append_edge(
                model_id,
                item.target_model_id,
                "antagonist",
                source_description=item.text,
                source_quote=item.source_quote,
                extraction_type=item.extraction_type,
                confidence=item.confidence,
                composition_affinity=_wave3_confidence_to_risk_affinity(item.confidence),
            )
        for item in record.structured_tensions:
            append_edge(
                model_id,
                item.target_model_id,
                "tension",
                source_description=item.text,
                source_quote=item.source_quote,
                extraction_type=item.extraction_type,
                confidence=item.confidence,
                composition_affinity=_wave3_confidence_to_risk_affinity(item.confidence),
                tension_type=item.tension_type,
            )

    meta = {
        "uses_relation_semantics_wave3": True,
        "relation_semantics_wave3": {
            "compiled_edge_count": len(graph),
            "source_record_count": len(records),
        },
    }
    return graph, meta


def _compile_models(corpus_dir: Path) -> dict[str, dict[str, object]]:
    source_files = sorted(path for path in corpus_dir.glob("*.md") if path.is_file())
    display_names = {
        _slug_from_source_filename(path.name): _display_name_from_source_filename(path.name)
        for path in source_files
    }
    alias_index = _build_alias_index(display_names)

    models: dict[str, dict[str, object]] = {}
    for path in source_files:
        slug = _slug_from_source_filename(path.name)
        display_name = display_names[slug]
        text = path.read_text(encoding="utf-8")
        models[slug] = _parse_model_document(
            source_path=path,
            slug=slug,
            display_name=display_name,
            text=text,
            display_names=display_names,
            alias_index=alias_index,
        )
    return models


def _parse_model_document(
    source_path: Path,
    slug: str,
    display_name: str,
    text: str,
    display_names: dict[str, str],
    alias_index: dict[str, str],
) -> dict[str, object]:
    lines = text.splitlines()
    bullets = _collect_bullets_by_section(lines)

    strength_bullets = bullets.get(("application", "strengths"), [])
    weakness_bullets = bullets.get(("application", "weaknesses"), [])
    playbook_bullets = bullets.get(("playbook", None), [])
    return {
        "display_name": display_name,
        "source_file": source_path.name,
        "select_when": [_extract_bullet_body(bullet) for bullet in strength_bullets[:5]],
        "failure_modes": _extract_failure_modes(weakness_bullets),
        "premortem_questions": _extract_questions(text),
        "heuristics": [_clean_inline_markdown(bullet) for bullet in playbook_bullets[:8]],
        "danger_when": _extract_danger_when(weakness_bullets),
        "slug": slug,
        "name": display_name,
    }


def _compile_tendencies(
    mapping_path: Path,
    routing_table_path: Path,
    models: dict[str, dict[str, object]],
) -> dict[str, dict[str, object]]:
    parsed_tendencies = _parse_structural_mapping(mapping_path)
    overlay_index = _load_routing_overlay(routing_table_path)
    model_ids = set(models)
    tendencies: dict[str, dict[str, object]] = {}
    seen_overlay_keys: set[str] = set()

    for tendency in parsed_tendencies:
        overlay_key = _find_overlay_key_for_tendency(tendency["display_name"], overlay_index)
        overlay = overlay_index.get(overlay_key) if overlay_key is not None else None
        if overlay_key is not None:
            seen_overlay_keys.add(overlay_key)

        payload = {
            "number": tendency["number"],
            "display_name": tendency["display_name"],
            "description": tendency["description"],
            "core_models": _merge_binding_lists(
                tendency.get("core_models", ()),
                overlay.get("core_models", ()) if overlay else (),
                model_ids,
            ),
            "related_dynamics": _merge_binding_lists(
                tendency.get("related_dynamics", ()),
                overlay.get("related_dynamics", ()) if overlay else (),
                model_ids,
            ),
            "antidote_models": _merge_binding_lists(
                tendency.get("antidote_models", ()),
                overlay.get("antidote_models", ()) if overlay else (),
                model_ids,
            ),
        }
        tendencies[_slugify(tendency["display_name"])] = payload

    next_number = len(tendencies) + 1
    for overlay_title, overlay in overlay_index.items():
        if overlay_title in seen_overlay_keys:
            continue
        display_name = _display_name_from_overlay_title(overlay_title)
        tendencies[_slugify(display_name)] = {
            "number": next_number,
            "display_name": display_name,
            "description": "",
            "core_models": _merge_binding_lists((), overlay.get("core_models", ()), model_ids),
            "related_dynamics": _merge_binding_lists((), overlay.get("related_dynamics", ()), model_ids),
            "antidote_models": _merge_binding_lists((), overlay.get("antidote_models", ()), model_ids),
        }
        next_number += 1

    return tendencies


def _parse_structural_mapping(mapping_path: Path) -> list[dict[str, object]]:
    lines = mapping_path.read_text(encoding="utf-8").splitlines()
    tendencies: list[dict[str, object]] = []
    current: dict[str, object] | None = None

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        header_match = re.match(r"^###\s+(\d+)\.\s+(.+?)\s*$", line)
        if header_match:
            if current is not None:
                tendencies.append(current)
            current = {
                "number": int(header_match.group(1)),
                "display_name": header_match.group(2).strip(),
                "description": "",
                "core_models": [],
                "related_dynamics": [],
                "antidote_models": [],
            }
            continue

        if current is None:
            continue

        if not current["description"] and line.startswith("*") and line.endswith("*"):
            current["description"] = _clean_inline_markdown(line)
            continue

        category_match = re.match(r"^- \*\*(.+?)\*\*(?::)?\s*(.+)$", line)
        if not category_match:
            continue

        category_label = category_match.group(1).strip().rstrip(":").lower()
        body = category_match.group(2).strip()
        if category_label == "core models":
            current["core_models"] = _parse_binding_markdown(body)
        elif category_label == "related dynamics":
            current["related_dynamics"] = _parse_binding_markdown(body)
        elif category_label == "antidote / protocol models":
            current["antidote_models"] = _parse_binding_markdown(body)

    if current is not None:
        tendencies.append(current)
    return tendencies


def _load_routing_overlay(routing_table_path: Path) -> dict[str, dict[str, tuple[dict[str, object], ...]]]:
    if not routing_table_path.exists():
        return {}

    raw_overlay = json.loads(routing_table_path.read_text(encoding="utf-8"))
    overlay: dict[str, dict[str, tuple[dict[str, object], ...]]] = {}
    for title, payload in raw_overlay.items():
        overlay[_normalize_tendency_key(title)] = {
            "core_models": tuple(_binding_from_model_id(model_id) for model_id in payload.get("core_models", [])),
            "related_dynamics": tuple(
                _binding_from_model_id(model_id) for model_id in payload.get("related_dynamics", [])
            ),
            "antidote_models": tuple(
                _binding_from_model_id(model_id) for model_id in payload.get("antidote_models", [])
            ),
        }
    return overlay


def _merge_binding_lists(
    preferred: tuple[dict[str, object], ...] | list[dict[str, object]],
    fallback: tuple[dict[str, object], ...] | list[dict[str, object]],
    model_ids: set[str],
) -> list[dict[str, object]]:
    merged: list[dict[str, object]] = []
    seen_model_ids: set[str] = set()

    for binding in list(preferred) + list(fallback):
        model_id = str(binding.get("model", "")).strip()
        if not model_id or model_id not in model_ids or model_id in seen_model_ids:
            continue
        activation_context = binding.get("activation_context")
        normalized_context = str(activation_context).strip() if activation_context is not None else ""
        seen_model_ids.add(model_id)
        merged.append(
            {
                "model": model_id,
                "activation_context": normalized_context or None,
                "activation_context_source_path": (
                    str(binding.get("activation_context_source_path", "")).strip()
                    if normalized_context
                    else ""
                ),
                "activation_context_source_quote": (
                    str(binding.get("activation_context_source_quote", "")).strip()
                    if normalized_context
                    else ""
                ),
                "activation_context_extraction_type": (
                    str(binding.get("activation_context_extraction_type", "")).strip()
                    if normalized_context
                    else ""
                ),
                "activation_context_confidence": (
                    str(binding.get("activation_context_confidence", "")).strip()
                    if normalized_context
                    else ""
                ),
                "activation_context_blocking_quality_flags": _normalize_string_list(
                    binding.get("activation_context_blocking_quality_flags")
                ),
                "activation_context_advisory_quality_flags": _normalize_string_list(
                    binding.get("activation_context_advisory_quality_flags")
                ),
            }
        )

    return merged


def _normalize_string_list(payload: object) -> list[str]:
    if not isinstance(payload, (list, tuple)):
        return []
    values: list[str] = []
    for item in payload:
        value = str(item).strip()
        if value:
            values.append(value)
    return values


def _extend_tendency_knowledge_edges(
    edges: list[dict[str, object]],
    seen: set[tuple[object, ...]],
    models: dict[str, dict[str, object]],
    tendencies: dict[str, dict[str, object]],
) -> None:
    for tendency_id, tendency in tendencies.items():
        tendency_number = tendency.get("number")
        for category, edge_type in (
            ("core_models", "tendency_core"),
            ("related_dynamics", "tendency_dynamic"),
            ("antidote_models", "tendency_antidote"),
        ):
            for binding in tendency.get(category, []) or []:
                edge = {
                    "source": tendency_id,
                    "target": binding.get("model"),
                    "type": edge_type,
                    "source_origin": "munger_mapping",
                    "tendency_number": tendency_number,
                    "context": binding.get("activation_context"),
                    "in_corpus": binding.get("model") in models,
                }
                _append_unique_edge(edges, seen, edge)


def _extend_markdown_model_relation_knowledge_edges(
    edges: list[dict[str, object]],
    seen: set[tuple[object, ...]],
    models: dict[str, dict[str, object]],
) -> None:
    for source_model_id, model in models.items():
        for ally in model.get("allies", []) or []:
            edge = {
                "source": source_model_id,
                "target": ally.get("model"),
                "type": "ally",
                "source_origin": "model_file",
                "context": ally.get("relationship"),
                "in_corpus": ally.get("model") in models,
            }
            _append_unique_edge(edges, seen, edge)

        for antagonist in model.get("antagonists", []) or []:
            edge = {
                "source": source_model_id,
                "target": antagonist.get("model"),
                "type": "antagonist",
                "source_origin": "model_file",
                "context": antagonist.get("relationship"),
                "in_corpus": antagonist.get("model") in models,
            }
            _append_unique_edge(edges, seen, edge)

        for tension in model.get("structured_tensions", []) or []:
            edge = {
                "source": source_model_id,
                "target": tension.get("against"),
                "type": "structured_tension",
                "source_origin": "model_file",
                "context": tension.get("description"),
                "in_corpus": tension.get("against") in models,
            }
            _append_unique_edge(edges, seen, edge)


def _extend_wave3_model_relation_knowledge_edges(
    edges: list[dict[str, object]],
    seen: set[tuple[object, ...]],
    relationship_graph: list[dict[str, object]],
    models: dict[str, dict[str, object]],
) -> None:
    """Project Wave 3 relationship rows into knowledge_graph edge records (model↔model only)."""
    for rel in relationship_graph:
        edge_type = str(rel.get("edge_type", "")).strip().lower()
        if edge_type == "ally":
            kg_type = "ally"
        elif edge_type == "antagonist":
            kg_type = "antagonist"
        elif edge_type == "tension":
            kg_type = "structured_tension"
        else:
            continue
        source_model_id = str(rel.get("source_model_id", "")).strip()
        target_model_id = str(rel.get("target_model_id", "")).strip()
        if not source_model_id or not target_model_id:
            continue
        edge = {
            "source": source_model_id,
            "target": target_model_id,
            "type": kg_type,
            "source_origin": "relation_semantics_wave3",
            "context": rel.get("source_description", ""),
            "in_corpus": target_model_id in models,
        }
        _append_unique_edge(edges, seen, edge)


def _append_unique_edge(
    edges: list[dict[str, object]],
    seen: set[tuple[object, ...]],
    edge: dict[str, object],
) -> None:
    key = (
        edge.get("source"),
        edge.get("target"),
        edge.get("type"),
        edge.get("source_origin"),
        edge.get("context"),
        edge.get("tendency_number"),
    )
    if key in seen:
        return
    seen.add(key)
    edges.append(edge)


def _build_relationship_graph(
    models: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    graph: list[dict[str, object]] = []
    seen: set[tuple[str, str, str]] = set()
    ally_lookup = {
        (source_model_id, ally.get("model")): ally.get("relationship", "")
        for source_model_id, model in models.items()
        for ally in model.get("allies", []) or []
        if ally.get("model") in models
    }

    for source_model_id, model in models.items():
        for ally in model.get("allies", []) or []:
            target_model_id = ally.get("model")
            if target_model_id not in models:
                continue
            key = (source_model_id, target_model_id, "ally")
            if key in seen:
                continue
            seen.add(key)
            reciprocal = (target_model_id, source_model_id) in ally_lookup
            graph.append(
                {
                    "source_model_id": source_model_id,
                    "target_model_id": target_model_id,
                    "edge_type": "ally",
                    "source_description": ally.get("relationship", ""),
                    "target_description": ally_lookup.get((target_model_id, source_model_id), ""),
                    "is_reciprocal": reciprocal,
                    "tension_depth": "moderate",
                    "composition_affinity": 0.65 if reciprocal else 0.6,
                    "curated": reciprocal,
                }
            )

        for antagonist in model.get("antagonists", []) or []:
            target_model_id = antagonist.get("model")
            if target_model_id not in models:
                continue
            key = (source_model_id, target_model_id, "antagonist")
            if key in seen:
                continue
            seen.add(key)
            graph.append(
                {
                    "source_model_id": source_model_id,
                    "target_model_id": target_model_id,
                    "edge_type": "antagonist",
                    "source_description": antagonist.get("relationship", ""),
                    "target_description": "",
                    "is_reciprocal": False,
                    "tension_depth": "moderate",
                    "composition_affinity": 0.2,
                    "curated": False,
                }
            )

        for tension in model.get("structured_tensions", []) or []:
            target_model_id = tension.get("against")
            if target_model_id not in models:
                continue
            key = (source_model_id, target_model_id, "antagonist")
            if key in seen:
                continue
            seen.add(key)
            graph.append(
                {
                    "source_model_id": source_model_id,
                    "target_model_id": target_model_id,
                    "edge_type": "antagonist",
                    "source_description": tension.get("description", ""),
                    "target_description": "",
                    "is_reciprocal": False,
                    "tension_depth": "moderate",
                    "composition_affinity": 0.2,
                    "curated": False,
                }
            )

    return graph


def _collect_bullets_by_section(lines: list[str]) -> dict[tuple[str | None, str | None], list[str]]:
    bullets: dict[tuple[str | None, str | None], list[str]] = {}
    major: str | None = None
    minor: str | None = None

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        lower = line.lower().rstrip(":")
        if lower.startswith("core principles and analogies"):
            major, minor = "core", None
            continue
        if lower.startswith("the playbook in action"):
            major, minor = "playbook", None
            continue
        if lower.startswith("application context"):
            major, minor = "application", None
            continue
        if lower.startswith("the latticework"):
            major, minor = "latticework", None
            continue
        if lower.startswith("risks and mitigations"):
            major, minor = "risks", None
            continue
        if lower.startswith("strengths"):
            minor = "strengths"
            continue
        if lower.startswith("weaknesses"):
            minor = "weaknesses"
            continue
        if lower.startswith("synergistic relationships"):
            minor = "allies"
            continue
        if lower.startswith("conflicting relationships"):
            minor = "antagonists"
            continue
        if line.startswith("• "):
            bullets.setdefault((major, minor), []).append(line[2:].strip())

    return bullets


def _extract_failure_modes(weakness_bullets: list[str]) -> list[dict[str, object]]:
    modes: list[dict[str, object]] = []
    for bullet in weakness_bullets[:6]:
        label, body = _split_labeled_bullet(bullet)
        if label and "danger when" in label.lower():
            continue
        description = body or _clean_inline_markdown(bullet)
        mode = label or _sentence_prefix(description, 6)
        modes.append(
            {
                "mode": mode,
                "description": description,
                "mitigation": None,
            }
        )
    return modes


def _extract_danger_when(weakness_bullets: list[str]) -> list[str]:
    dangers: list[str] = []
    for bullet in weakness_bullets:
        label, body = _split_labeled_bullet(bullet)
        if label and "danger when" in label.lower():
            dangers.append(body or _clean_inline_markdown(bullet))
    return dangers[:4]


def _extract_questions(text: str) -> list[str]:
    questions: list[str] = []
    seen: set[str] = set()

    for match in re.finditer(r'"([^"\n]+\?)"', text):
        question = _clean_question(match.group(1))
        if question and question not in seen:
            seen.add(question)
            questions.append(question)

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("• "):
            continue
        if "?" not in line:
            continue
        question = _clean_question(_clean_inline_markdown(line[2:]))
        if question and question not in seen:
            seen.add(question)
            questions.append(question)

    return questions[:5]


def _clean_question(question: str) -> str:
    cleaned = _clean_inline_markdown(question).strip()
    cleaned = cleaned.strip('"').strip("'")
    if cleaned and not cleaned.endswith("?"):
        cleaned = f"{cleaned}?"
    return cleaned


def _extract_allies(
    source_slug: str,
    bullets: list[str],
    display_names: dict[str, str],
    alias_index: dict[str, str],
) -> list[dict[str, object]]:
    allies: list[dict[str, object]] = []
    seen: set[str] = set()
    for bullet in bullets:
        label, body = _split_labeled_bullet(bullet)
        target = _resolve_model_reference(label or bullet, display_names, alias_index)
        if target is None or target == source_slug or target in seen:
            continue
        seen.add(target)
        allies.append(
            {
                "model": target,
                "relationship": body or _clean_inline_markdown(bullet),
            }
        )
    return allies


def _extract_antagonists_and_tensions(
    source_slug: str,
    bullets: list[str],
    display_names: dict[str, str],
    alias_index: dict[str, str],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    antagonists: list[dict[str, object]] = []
    tensions: list[dict[str, object]] = []
    seen_antagonists: set[str] = set()
    seen_tensions: set[str] = set()

    for bullet in bullets:
        tension_target = _extract_tension_target(bullet, display_names, alias_index)
        if tension_target is not None and tension_target != source_slug and tension_target not in seen_tensions:
            seen_tensions.add(tension_target)
            tensions.append(
                {
                    "against": tension_target,
                    "tension_type": "conflicts",
                    "description": _clean_inline_markdown(bullet),
                }
            )
            continue

        label, body = _split_labeled_bullet(bullet)
        target = _resolve_model_reference(label or bullet, display_names, alias_index)
        if target is None or target == source_slug or target in seen_antagonists:
            continue
        seen_antagonists.add(target)
        antagonists.append(
            {
                "model": target,
                "relationship": body or _clean_inline_markdown(bullet),
            }
        )

    return antagonists, tensions


def _extract_tension_target(
    bullet: str,
    display_names: dict[str, str],
    alias_index: dict[str, str],
) -> str | None:
    match = re.search(r"\*\*[^*]+ vs ([^*]+)\*\*", bullet, re.IGNORECASE)
    if not match:
        return None
    return _resolve_model_reference(match.group(1), display_names, alias_index)


def _split_labeled_bullet(bullet: str) -> tuple[str | None, str]:
    markdown_label = re.match(r"^\*\*(.+?)\*\*:\s*(.+)$", bullet)
    if markdown_label:
        return _clean_inline_markdown(markdown_label.group(1)), _clean_inline_markdown(markdown_label.group(2))

    plain_label = re.match(r"^([^:]{3,80}):\s*(.+)$", _clean_inline_markdown(bullet))
    if plain_label:
        return plain_label.group(1).strip(), plain_label.group(2).strip()

    return None, _clean_inline_markdown(bullet)


def _extract_bullet_body(bullet: str) -> str:
    _label, body = _split_labeled_bullet(bullet)
    return body


def _resolve_model_reference(
    label: str,
    display_names: dict[str, str],
    alias_index: dict[str, str],
) -> str | None:
    variants = [label]
    variants.extend(part for part in re.split(r"/|,|\bor\b", label) if part.strip())

    for variant in variants:
        normalized = _normalize_reference(variant)
        if normalized in alias_index:
            return alias_index[normalized]

    best_slug: str | None = None
    best_score = 0.0
    for slug, display_name in display_names.items():
        score = max(_match_score(variant, slug, display_name) for variant in variants)
        if score > best_score:
            best_slug = slug
            best_score = score

    if best_score >= 0.6:
        return best_slug
    return None


def _match_score(label: str, slug: str, display_name: str) -> float:
    label_normalized = _normalize_reference(label)
    slug_normalized = _normalize_reference(slug)
    display_normalized = _normalize_reference(display_name)

    if label_normalized == slug_normalized or label_normalized == display_normalized:
        return 1.0
    if label_normalized and (
        label_normalized in slug_normalized
        or label_normalized in display_normalized
        or slug_normalized in label_normalized
        or display_normalized in label_normalized
    ):
        return 0.8

    label_tokens = set(_tokenize_reference(label))
    model_tokens = set(_tokenize_reference(display_name)) | set(_tokenize_reference(slug))
    if not label_tokens or not model_tokens:
        return 0.0
    overlap = label_tokens & model_tokens
    if not overlap:
        return 0.0
    return len(overlap) / max(len(label_tokens), len(model_tokens))


def _build_alias_index(display_names: dict[str, str]) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for slug, display_name in display_names.items():
        for variant in (
            slug,
            display_name,
            display_name.replace("&", "and"),
            display_name.replace("-", " "),
        ):
            aliases[_normalize_reference(variant)] = slug
    return aliases


def _normalize_reference(text: str) -> str:
    text = _clean_inline_markdown(text).lower()
    text = re.sub(r"\b(the|a|an|and|of|for|to)\b", " ", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text


def _tokenize_reference(text: str) -> list[str]:
    normalized = _normalize_reference(text)
    return [token for token in normalized.split("-") if token and token not in {"model", "models"}]


def _display_name_from_source_filename(filename: str) -> str:
    stem = Path(filename).stem
    if stem.endswith("_rag"):
        stem = stem[:-4]
    parts = re.split(r"[_\s]+", stem)
    return " ".join(part.capitalize() if part.islower() else part for part in parts if part)


def _slug_from_source_filename(filename: str) -> str:
    stem = Path(filename).stem
    if stem.endswith("_rag"):
        stem = stem[:-4]
    return _slugify(stem.replace("_", " "))


def _display_name_from_overlay_title(normalized_title: str) -> str:
    words = normalized_title.replace("-tendency", "").split("-")
    return " ".join(word.capitalize() for word in words if word) + " Tendency"


def _slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-")


def _normalize_tendency_key(title: str) -> str:
    normalized = _slugify(title)
    if not normalized.endswith("tendency"):
        normalized = f"{normalized}-tendency"
    return normalized


def _find_overlay_key_for_tendency(
    display_name: str,
    overlay_index: dict[str, dict[str, tuple[dict[str, object], ...]]],
) -> str | None:
    normalized = _normalize_tendency_key(display_name)
    if normalized in overlay_index:
        return normalized

    display_tokens = set(_tendency_tokens(display_name))
    best_key: str | None = None
    best_score = 0.0
    for overlay_key in overlay_index:
        overlay_tokens = set(_tendency_tokens(overlay_key))
        if not overlay_tokens:
            continue
        overlap = display_tokens & overlay_tokens
        if not overlap:
            continue
        score = len(overlap) / max(len(display_tokens), len(overlay_tokens))
        if score > best_score:
            best_key = overlay_key
            best_score = score

    if best_score >= 0.75:
        return best_key
    return None


def _tendency_tokens(value: str) -> list[str]:
    normalized = _normalize_tendency_key(value)
    return [
        token
        for token in normalized.split("-")
        if token and token != "tendency"
    ]


def _parse_binding_markdown(
    body: str,
    *,
    source_path: str = "munger_structural_mapping.md",
) -> tuple[dict[str, object], ...]:
    bindings: list[dict[str, object]] = []
    for match in re.finditer(r"`([^`]+)`(?:\s*\(([^)]*)\))?", body):
        activation_context = match.group(2).strip() if match.group(2) else None
        bindings.append(
            {
                "model": match.group(1).strip(),
                "activation_context": activation_context,
                "activation_context_source_path": source_path if activation_context else "",
                "activation_context_source_quote": activation_context or "",
                "activation_context_extraction_type": "explicit" if activation_context else "",
                "activation_context_confidence": "high" if activation_context else "",
                "activation_context_blocking_quality_flags": [],
                "activation_context_advisory_quality_flags": [],
            }
        )
    return tuple(bindings)


def _binding_from_model_id(model_id: str) -> dict[str, object]:
    return {
        "model": model_id,
        "activation_context": None,
        "activation_context_source_path": "",
        "activation_context_source_quote": "",
        "activation_context_extraction_type": "",
        "activation_context_confidence": "",
        "activation_context_blocking_quality_flags": [],
        "activation_context_advisory_quality_flags": [],
    }


def _clean_inline_markdown(text: str) -> str:
    cleaned = text.replace("**", "").replace("*", "").replace("`", "")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def _sentence_prefix(text: str, word_limit: int) -> str:
    words = _clean_inline_markdown(text).split()
    return " ".join(words[:word_limit]).rstrip(":")


def _count_tendency_links(tendencies: dict[str, dict]) -> int:
    total = 0
    for tendency in tendencies.values():
        total += len(tendency.get("core_models", []) or [])
        total += len(tendency.get("related_dynamics", []) or [])
        total += len(tendency.get("antidote_models", []) or [])
    return total


def _parse_report_summary(report_text: str) -> dict[str, int | None]:
    return {
        "total_models": _extract_report_int(report_text, r"\*\*Total Models:\*\*\s*(\d+)"),
        "total_edges": _extract_report_int(report_text, r"\*\*Total Edges:\*\*\s*(\d+)"),
        "total_tendency_links": _extract_report_int(
            report_text,
            r"\*\*Total Tendency Links:\*\*\s*(\d+)",
        ),
    }


def _extract_report_int(report_text: str, pattern: str) -> int | None:
    match = re.search(pattern, report_text)
    if not match:
        return None
    return _coerce_int(match.group(1), default=None)


def _coerce_int(value: object, default: int | None = 0) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _rewrite_knowledge_graph_metadata(
    kg: dict[str, object],
    bundle: CompilationBundle,
) -> None:
    metadata = dict(kg.get("metadata", {}) or {})
    metadata["total_models_processed"] = bundle.model_count
    metadata["total_edges"] = bundle.knowledge_edge_count
    metadata["total_tendency_links"] = bundle.tendency_link_count
    kg["metadata"] = metadata


def _rewrite_compilation_mode_metadata(
    kg: dict[str, object],
    *,
    mode_name: str,
    use_operational_curation: bool,
    include_operational_curation_review: bool,
    curation_metadata: dict[str, object],
) -> None:
    metadata = dict(kg.get("metadata", {}) or {})
    metadata["compilation_mode"] = mode_name
    metadata["uses_operational_curation"] = use_operational_curation
    if use_operational_curation:
        metadata["operational_curation"] = {
            "applied_model_count": curation_metadata.get("applied_model_count", 0),
            "changed_field_count": curation_metadata.get("changed_field_count", 0),
            "overwritten_non_empty_field_count": curation_metadata.get("overwritten_non_empty_field_count", 0),
            "contested_field_count": curation_metadata.get("contested_field_count", 0),
            "injected_fields": list(curation_metadata.get("injected_fields", ()) or ()),
        }
        uses_wave2 = bool(curation_metadata.get("uses_intervention_semantics_overlay"))
        metadata["uses_intervention_semantics_overlay"] = uses_wave2
        if uses_wave2:
            metadata["intervention_semantics_overlay"] = dict(
                curation_metadata.get("intervention_semantics_overlay", {}) or {}
            )
        else:
            metadata.pop("intervention_semantics_overlay", None)

        uses_wave3 = bool(curation_metadata.get("uses_relation_semantics_wave3"))
        metadata["uses_relation_semantics_wave3"] = uses_wave3
        if uses_wave3:
            metadata["relation_semantics_wave3"] = dict(
                curation_metadata.get("relation_semantics_wave3", {}) or {}
            )
        else:
            metadata.pop("relation_semantics_wave3", None)

        if include_operational_curation_review:
            kg["operational_curation_review"] = {
                "preview_only": True,
                "applied_model_count": curation_metadata.get("applied_model_count", 0),
                "contested_field_count": curation_metadata.get("contested_field_count", 0),
                "models": curation_metadata.get("field_review_metadata", {}),
            }
        else:
            kg.pop("operational_curation_review", None)
    else:
        metadata.pop("operational_curation", None)
        metadata.pop("uses_intervention_semantics_overlay", None)
        metadata.pop("intervention_semantics_overlay", None)
        metadata.pop("uses_relation_semantics_wave3", None)
        metadata.pop("relation_semantics_wave3", None)
        kg.pop("operational_curation_review", None)
    kg["metadata"] = metadata


def _build_report_text(
    bundle: CompilationBundle,
    *,
    mode_name: str,
    use_operational_curation: bool,
    curation_metadata: dict[str, object],
) -> str:
    lines = [
        "# Knowledge Graph Compilation Report",
        "Generated by KnowledgeCompiler",
        "",
        "## Summary",
        f"- **Compilation Mode:** {mode_name}",
        f"- **Uses Operational Curation:** {use_operational_curation}",
        f"- **Total Models:** {bundle.model_count}",
        f"- **Total Edges:** {bundle.knowledge_edge_count}",
        f"- **Total Tendency Links:** {bundle.tendency_link_count}",
        f"- **Relationship Edges:** {bundle.relationship_edge_count}",
    ]
    if use_operational_curation:
        lines.extend(
            [
                f"- **Curated Models Applied:** {curation_metadata.get('applied_model_count', 0)}",
                f"- **Curation Field Changes:** {curation_metadata.get('changed_field_count', 0)}",
                f"- **Overwritten Non-Empty Fields:** {curation_metadata.get('overwritten_non_empty_field_count', 0)}",
                f"- **Contested Curation Fields:** {curation_metadata.get('contested_field_count', 0)}",
            ]
        )
        if curation_metadata.get("uses_intervention_semantics_overlay"):
            w2 = curation_metadata.get("intervention_semantics_overlay", {}) or {}
            lines.append("- **Wave 2 Intervention Semantics:** active (replaces compiled failure_modes / premortem_questions / heuristics)")
            lines.append(f"- **Wave 2 Models Applied:** {w2.get('applied_model_count', 0)}")
            lines.append(
                f"- **Wave 2 Item Totals:** failure_modes={w2.get('total_failure_modes', 0)}, "
                f"premortem_questions={w2.get('total_premortem_questions', 0)}, "
                f"heuristics={w2.get('total_heuristics', 0)}"
            )
        if curation_metadata.get("uses_relation_semantics_wave3"):
            w3 = curation_metadata.get("relation_semantics_wave3", {}) or {}
            lines.append(
                "- **Wave 3 Relation Semantics:** active (relationship_graph.json is Wave-derived; not markdown union)"
            )
            lines.append(f"- **Wave 3 Compiled Relationship Edges:** {w3.get('compiled_edge_count', 0)}")
    return "\n".join(lines) + "\n"


def _build_manifest_payload(
    bundle: CompilationBundle,
    *,
    mode_name: str,
    use_operational_curation: bool,
    curation_metadata: dict[str, object],
) -> dict[str, object]:
    payload = {
        "schema_version": "1.0",
        "compilation_mode": mode_name,
        "uses_operational_curation": use_operational_curation,
        "artifacts": {
            "knowledge_graph": bundle.knowledge_graph_path.name,
            "relationship_graph": bundle.relationship_graph_path.name,
            "report": bundle.report_path.name,
        },
        "artifact_counts": {
            "model_count": bundle.model_count,
            "knowledge_edge_count": bundle.knowledge_edge_count,
            "relationship_edge_count": bundle.relationship_edge_count,
            "tendency_link_count": bundle.tendency_link_count,
        },
    }
    if use_operational_curation:
        payload["operational_curation"] = {
            "applied_model_count": curation_metadata.get("applied_model_count", 0),
            "changed_field_count": curation_metadata.get("changed_field_count", 0),
            "overwritten_non_empty_field_count": curation_metadata.get("overwritten_non_empty_field_count", 0),
            "contested_field_count": curation_metadata.get("contested_field_count", 0),
        }
        payload["uses_intervention_semantics_overlay"] = bool(
            curation_metadata.get("uses_intervention_semantics_overlay")
        )
        if payload["uses_intervention_semantics_overlay"]:
            payload["intervention_semantics_overlay"] = dict(
                curation_metadata.get("intervention_semantics_overlay", {}) or {}
            )
        payload["uses_relation_semantics_wave3"] = bool(curation_metadata.get("uses_relation_semantics_wave3"))
        if payload["uses_relation_semantics_wave3"]:
            payload["relation_semantics_wave3"] = dict(
                curation_metadata.get("relation_semantics_wave3", {}) or {}
            )
    return payload


def _manifest_drift_errors(
    manifest: dict[str, object],
    bundle: CompilationBundle,
) -> tuple[str, ...]:
    errors: list[str] = []
    artifacts = manifest.get("artifacts", {})
    if not isinstance(artifacts, dict):
        return ("Compilation manifest drift: artifacts block is missing or invalid",)

    expected_artifacts = {
        "knowledge_graph": bundle.knowledge_graph_path.name,
        "relationship_graph": bundle.relationship_graph_path.name,
        "report": bundle.report_path.name,
    }
    for key, expected in expected_artifacts.items():
        actual = artifacts.get(key)
        if actual != expected:
            errors.append(
                f"Compilation manifest drift: {key}={actual} actual={expected}"
            )

    counts = manifest.get("artifact_counts", {})
    if not isinstance(counts, dict):
        return tuple(errors) + ("Compilation manifest drift: artifact_counts block is missing or invalid",)

    expected_counts = {
        "model_count": bundle.model_count,
        "knowledge_edge_count": bundle.knowledge_edge_count,
        "relationship_edge_count": bundle.relationship_edge_count,
        "tendency_link_count": bundle.tendency_link_count,
    }
    for key, expected in expected_counts.items():
        actual = _coerce_int(counts.get(key), default=None)
        if actual != expected:
            errors.append(
                f"Compilation manifest drift: {key}={counts.get(key)} actual={expected}"
            )

    return tuple(errors)
