from __future__ import annotations

from dataclasses import dataclass, replace
import json
from pathlib import Path
import re

from .subpattern_catalog import SourceRef


_TENDENCY_SUFFIX = "-tendency"
_DISPLAY_SUFFIX = " tendency"


@dataclass(frozen=True)
class ModelBinding:
    model_id: str
    activation_context: str = ""
    activation_context_ref: SourceRef | None = None
    blocking_quality_flags: tuple[str, ...] = ()
    advisory_quality_flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class TendencyRef:
    tendency_id: str
    display_name: str
    routing_key: str
    antidote_model_ids: tuple[str, ...]
    core_model_ids: tuple[str, ...] = ()
    related_dynamics: tuple[str, ...] = ()
    antidote_bindings: tuple[ModelBinding, ...] = ()
    core_model_bindings: tuple[ModelBinding, ...] = ()
    related_dynamic_bindings: tuple[ModelBinding, ...] = ()
    tendency_number: int = 0
    description: str = ""
    resolved_from: str = ""


class TendencyCatalog:
    def __init__(
        self,
        tendencies: dict[str, TendencyRef],
        alias_index: dict[str, str],
        warnings: tuple[str, ...] = (),
    ) -> None:
        self._tendencies = tendencies
        self._alias_index = alias_index
        self.warnings = warnings

    @classmethod
    def load(cls, root: Path) -> "TendencyCatalog":
        root = Path(root)
        graph_path = root / "build" / "knowledge_graph.json"
        graph = json.loads(graph_path.read_text(encoding="utf-8"))
        tendencies_data = graph.get("tendencies", {})
        routing_data = cls._load_routing_overlay(root)

        tendencies: dict[str, TendencyRef] = {}
        alias_index: dict[str, str] = {}
        warnings: list[str] = []

        for tendency_id, tendency in tendencies_data.items():
            display_name = str(tendency.get("display_name", tendency_id))
            routing_key = cls._find_routing_key(tendency_id, display_name, routing_data)
            tendency_ref = TendencyRef(
                tendency_id=tendency_id,
                display_name=display_name,
                routing_key=routing_key,
                antidote_model_ids=_extract_model_ids(tendency.get("antidote_models")),
                core_model_ids=_extract_model_ids(tendency.get("core_models")),
                related_dynamics=_extract_model_ids(tendency.get("related_dynamics")),
                antidote_bindings=_extract_model_bindings(tendency.get("antidote_models")),
                core_model_bindings=_extract_model_bindings(tendency.get("core_models")),
                related_dynamic_bindings=_extract_model_bindings(tendency.get("related_dynamics")),
                tendency_number=int(tendency.get("number", 0) or 0),
                description=str(tendency.get("description", "")),
            )
            tendencies[tendency_id] = tendency_ref
            for alias in _candidate_aliases(tendency_id, display_name, routing_key):
                alias_index[alias] = tendency_id
            overlay_entry = routing_data.get(routing_key)
            if isinstance(overlay_entry, dict):
                warnings.extend(_overlay_disagreements(tendency_ref, overlay_entry))

        return cls(
            tendencies=tendencies,
            alias_index=alias_index,
            warnings=tuple(warnings),
        )

    def lookup(self, key: str) -> TendencyRef:
        normalized = _normalize_alias(key)
        tendency_id = self._alias_index.get(normalized)
        if tendency_id is None:
            raise KeyError(f"Unknown tendency: {key}")
        return replace(self._tendencies[tendency_id], resolved_from=str(key))

    def all(self) -> tuple[TendencyRef, ...]:
        return tuple(
            sorted(
                self._tendencies.values(),
                key=lambda tendency: (
                    tendency.tendency_number or 10_000,
                    tendency.display_name,
                ),
            )
        )

    @staticmethod
    def _load_routing_overlay(root: Path) -> dict[str, dict]:
        candidates = (
            root / "build" / "curated" / "munger_routing_table.json",
            root / "munger_routing_table.json",
        )
        for path in candidates:
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        return {}

    @staticmethod
    def _find_routing_key(
        tendency_id: str,
        display_name: str,
        routing_data: dict[str, dict],
    ) -> str:
        target_aliases = _candidate_aliases(tendency_id, display_name, "")
        for routing_key in routing_data:
            if _normalize_alias(routing_key) in target_aliases:
                return routing_key
        return _derive_routing_key(display_name)


def _extract_model_ids(entries: object) -> tuple[str, ...]:
    if not isinstance(entries, list):
        return ()
    model_ids: list[str] = []
    for entry in entries:
        if isinstance(entry, dict):
            model_id = str(entry.get("model", "")).strip()
        else:
            model_id = str(entry).strip()
        if model_id:
            model_ids.append(model_id)
    return tuple(model_ids)


def _extract_model_bindings(entries: object) -> tuple[ModelBinding, ...]:
    if not isinstance(entries, list):
        return ()
    bindings: list[ModelBinding] = []
    for entry in entries:
        if isinstance(entry, dict):
            model_id = str(entry.get("model", "")).strip()
            activation_context = str(entry.get("activation_context", "") or "")
            source_path = str(entry.get("activation_context_source_path", "") or "").strip()
            source_quote = str(entry.get("activation_context_source_quote", "") or "").strip()
            extraction_type = str(entry.get("activation_context_extraction_type", "") or "").strip()
            confidence = str(entry.get("activation_context_confidence", "") or "").strip()
            blocking_quality_flags = _extract_string_tuple(
                entry.get("activation_context_blocking_quality_flags")
            )
            advisory_quality_flags = _extract_string_tuple(
                entry.get("activation_context_advisory_quality_flags")
            )
        else:
            model_id = str(entry).strip()
            activation_context = ""
            source_path = ""
            source_quote = ""
            extraction_type = ""
            confidence = ""
            blocking_quality_flags = ()
            advisory_quality_flags = ()
        if model_id:
            bindings.append(
                ModelBinding(
                    model_id=model_id,
                    activation_context=activation_context,
                    activation_context_ref=(
                        SourceRef(
                            path=source_path,
                            quote=source_quote,
                            extraction_type=extraction_type,
                            confidence=confidence,
                        )
                        if source_path
                        else None
                    ),
                    blocking_quality_flags=blocking_quality_flags,
                    advisory_quality_flags=advisory_quality_flags,
                )
            )
    return tuple(bindings)


def _extract_string_tuple(payload: object) -> tuple[str, ...]:
    if not isinstance(payload, (list, tuple)):
        return ()
    values: list[str] = []
    for item in payload:
        value = str(item).strip()
        if value:
            values.append(value)
    return tuple(values)


def _derive_routing_key(display_name: str) -> str:
    label = display_name.strip()
    if label.lower().endswith(_DISPLAY_SUFFIX):
        label = label[: -len(_DISPLAY_SUFFIX)]
    return "-".join(part for part in label.split() if part)


def _candidate_aliases(tendency_id: str, display_name: str, routing_key: str) -> set[str]:
    aliases = {
        _normalize_alias(tendency_id),
        _normalize_alias(display_name),
        _normalize_alias(_strip_tendency_suffix(tendency_id)),
        _normalize_alias(_strip_display_suffix(display_name)),
    }
    if routing_key:
        aliases.add(_normalize_alias(routing_key))
    return {alias for alias in aliases if alias}


def _strip_tendency_suffix(value: str) -> str:
    if value.endswith(_TENDENCY_SUFFIX):
        return value[: -len(_TENDENCY_SUFFIX)]
    return value


def _strip_display_suffix(value: str) -> str:
    if value.lower().endswith(_DISPLAY_SUFFIX):
        return value[: -len(_DISPLAY_SUFFIX)]
    return value


def _normalize_alias(value: str) -> str:
    value = _strip_display_suffix(_strip_tendency_suffix(str(value).strip().lower()))
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def _overlay_disagreements(
    tendency: TendencyRef,
    overlay_entry: dict[str, object],
) -> tuple[str, ...]:
    warnings: list[str] = []
    comparisons = (
        ("core_models", tendency.core_model_ids),
        ("related_dynamics", tendency.related_dynamics),
        ("antidote_models", tendency.antidote_model_ids),
    )
    for field_name, graph_values in comparisons:
        overlay_values = _extract_model_ids(overlay_entry.get(field_name))
        if overlay_values and tuple(overlay_values) != tuple(graph_values):
            warnings.append(
                f"Overlay disagreement for {tendency.tendency_id}: "
                f"{field_name} graph={graph_values} overlay={overlay_values}"
            )
    return tuple(warnings)
