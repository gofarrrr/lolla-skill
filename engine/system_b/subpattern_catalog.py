from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class SourceRef:
    path: str
    quote: str = ""
    extraction_type: str = ""
    confidence: str = ""


@dataclass(frozen=True)
class ModelBindingRef:
    model_id: str
    role: str = ""
    activation_context: str = ""
    source_refs: tuple[SourceRef, ...] = ()
    blocking_quality_flags: tuple[str, ...] = ()
    advisory_quality_flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class SubpatternRef:
    subpattern_id: str
    display_name: str
    description: str
    detectability: str = ""
    signal_tags: tuple[str, ...] = ()
    primary_model_ids: tuple[str, ...] = ()
    supporting_model_ids: tuple[str, ...] = ()
    bindings: tuple[ModelBindingRef, ...] = ()
    source_refs: tuple[SourceRef, ...] = ()


@dataclass(frozen=True)
class TendencySubpatterns:
    tendency_id: str
    display_name: str
    subpatterns: tuple[SubpatternRef, ...]
    source_refs: tuple[SourceRef, ...] = ()


class SubpatternCatalog:
    def __init__(self, tendencies: dict[str, TendencySubpatterns]) -> None:
        self._tendencies = tendencies

    @classmethod
    def load(cls, root: Path) -> "SubpatternCatalog":
        root = Path(root)
        path = root / "build" / "curated" / "subpattern_catalog.json"
        if not path.exists():
            return cls({})
        payload = json.loads(path.read_text(encoding="utf-8"))
        tendency_payloads = payload.get("tendencies", {}) if isinstance(payload, dict) else {}
        tendencies: dict[str, TendencySubpatterns] = {}
        if not isinstance(tendency_payloads, dict):
            return cls({})
        for tendency_id, tendency_payload in tendency_payloads.items():
            if not isinstance(tendency_payload, dict):
                continue
            tendencies[tendency_id] = TendencySubpatterns(
                tendency_id=str(tendency_id),
                display_name=str(tendency_payload.get("display_name", tendency_id)),
                subpatterns=_parse_subpatterns(tendency_payload.get("subpatterns")),
                source_refs=_parse_source_refs(tendency_payload.get("source_refs")),
            )
        return cls(tendencies)

    def has_tendency(self, tendency_id: str) -> bool:
        return tendency_id in self._tendencies

    def for_tendency(self, tendency_id: str) -> TendencySubpatterns:
        if tendency_id not in self._tendencies:
            raise KeyError(f"Unknown tendency subpattern catalog: {tendency_id}")
        return self._tendencies[tendency_id]

    def subpattern_for(self, tendency_id: str, subpattern_id: str) -> SubpatternRef:
        tendency = self.for_tendency(tendency_id)
        normalized_target = _normalize_id(subpattern_id)
        for subpattern in tendency.subpatterns:
            if _normalize_id(subpattern.subpattern_id) == normalized_target:
                return subpattern
        raise KeyError(f"Unknown subpattern '{subpattern_id}' for tendency '{tendency_id}'")

    def all(self) -> tuple[TendencySubpatterns, ...]:
        return tuple(self._tendencies.values())


def _parse_subpatterns(payload: object) -> tuple[SubpatternRef, ...]:
    if not isinstance(payload, list):
        return ()
    subpatterns: list[SubpatternRef] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        subpattern_id = str(item.get("subpattern_id", "")).strip()
        if not subpattern_id:
            continue
        subpatterns.append(
            SubpatternRef(
                subpattern_id=subpattern_id,
                display_name=str(item.get("display_name", subpattern_id)),
                description=str(item.get("description", "")),
                detectability=str(item.get("detectability", "")),
                signal_tags=_parse_string_tuple(item.get("signal_tags")),
                primary_model_ids=_parse_string_tuple(item.get("primary_model_ids")),
                supporting_model_ids=_parse_string_tuple(item.get("supporting_model_ids")),
                bindings=_parse_bindings(item.get("bindings")),
                source_refs=_parse_source_refs(item.get("source_refs")),
            )
        )
    return tuple(subpatterns)


def _parse_bindings(payload: object) -> tuple[ModelBindingRef, ...]:
    if not isinstance(payload, list):
        return ()
    bindings: list[ModelBindingRef] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        model_id = str(item.get("model_id", "")).strip()
        if not model_id:
            continue
        bindings.append(
            ModelBindingRef(
                model_id=model_id,
                role=str(item.get("role", "")).strip(),
                activation_context=str(item.get("activation_context", "")).strip(),
                source_refs=_parse_source_refs(item.get("source_refs")),
                blocking_quality_flags=_parse_quality_tuple(item.get("quality", {}), "blocking_flags"),
                advisory_quality_flags=_parse_quality_tuple(item.get("quality", {}), "advisory_flags"),
            )
        )
    return tuple(bindings)


def _parse_source_refs(payload: object) -> tuple[SourceRef, ...]:
    if not isinstance(payload, list):
        return ()
    refs: list[SourceRef] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", "")).strip()
        if not path:
            continue
        refs.append(
            SourceRef(
                path=path,
                quote=str(item.get("quote", "")),
                extraction_type=str(item.get("extraction_type", "")),
                confidence=str(item.get("confidence", "")),
            )
        )
    return tuple(refs)


def _parse_string_tuple(payload: object) -> tuple[str, ...]:
    if not isinstance(payload, list):
        return ()
    values: list[str] = []
    for item in payload:
        value = str(item).strip()
        if value:
            values.append(value)
    return tuple(values)


def _normalize_id(value: object) -> str:
    return str(value or "").strip().replace("_", "-").lower()


def _parse_quality_tuple(payload: object, field: str) -> tuple[str, ...]:
    if not isinstance(payload, dict):
        return ()
    return _parse_string_tuple(payload.get(field))
