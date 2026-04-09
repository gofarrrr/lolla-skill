from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class CompiledChunk:
    chunk_id: str
    model_id: str
    chunk_type: str
    text: str
    source_file: str = ""
    source_quote: str = ""
    extraction_type: str = ""
    confidence: str = ""
    tendency_ids: tuple[str, ...] = ()
    subpattern_ids: tuple[str, ...] = ()
    guardrail_tags: tuple[str, ...] = ()
    blocking_quality_flags: tuple[str, ...] = ()
    advisory_quality_flags: tuple[str, ...] = ()


class CompiledSubstrate:
    def __init__(self, chunks: tuple[CompiledChunk, ...]) -> None:
        self._chunks = chunks

    @classmethod
    def load(cls, root: Path) -> "CompiledSubstrate":
        root = Path(root)
        path = root / "build" / "curated" / "compiled_chunks.json"
        if not path.exists():
            return cls(())
        payload = json.loads(path.read_text(encoding="utf-8"))
        raw_chunks = payload.get("chunks", []) if isinstance(payload, dict) else []
        if not isinstance(raw_chunks, list):
            return cls(())
        chunks: list[CompiledChunk] = []
        for item in raw_chunks:
            if not isinstance(item, dict):
                continue
            chunk_id = str(item.get("chunk_id", "")).strip()
            model_id = str(item.get("model_id", "")).strip()
            chunk_type = str(item.get("chunk_type", "")).strip()
            text = str(item.get("text", "")).strip()
            if not chunk_id or not model_id or not chunk_type or not text:
                continue
            chunks.append(
                CompiledChunk(
                    chunk_id=chunk_id,
                    model_id=model_id,
                    chunk_type=chunk_type,
                    text=text,
                    source_file=str(item.get("source_file", "")),
                    source_quote=str(item.get("source_quote", "")),
                    extraction_type=str(item.get("extraction_type", "")),
                    confidence=str(item.get("confidence", "")),
                    tendency_ids=_parse_string_tuple(item.get("tendency_ids")),
                    subpattern_ids=_parse_string_tuple(item.get("subpattern_ids")),
                    guardrail_tags=_parse_string_tuple(item.get("guardrail_tags")),
                    blocking_quality_flags=_parse_quality_tuple(item.get("quality", {}), "blocking_flags"),
                    advisory_quality_flags=_parse_quality_tuple(item.get("quality", {}), "advisory_flags"),
                )
            )
        return cls(tuple(chunks))

    def all_chunks(self) -> tuple[CompiledChunk, ...]:
        return self._chunks

    def chunks_for_models(self, model_ids: tuple[str, ...] | list[str]) -> tuple[CompiledChunk, ...]:
        model_id_set = {str(model_id).strip() for model_id in model_ids if str(model_id).strip()}
        if not model_id_set:
            return ()
        return tuple(chunk for chunk in self._chunks if chunk.model_id in model_id_set)

    def chunk_by_id(self, chunk_id: str) -> CompiledChunk | None:
        target = str(chunk_id).strip()
        if not target:
            return None
        for chunk in self._chunks:
            if chunk.chunk_id == target:
                return chunk
        return None

    def chunks_by_id(self, chunk_ids: tuple[str, ...] | list[str]) -> tuple[CompiledChunk, ...]:
        selected: list[CompiledChunk] = []
        for chunk_id in chunk_ids:
            chunk = self.chunk_by_id(str(chunk_id))
            if chunk is not None:
                selected.append(chunk)
        return tuple(selected)


def _parse_string_tuple(payload: object) -> tuple[str, ...]:
    if not isinstance(payload, list):
        return ()
    values: list[str] = []
    for item in payload:
        value = str(item).strip()
        if value:
            values.append(value)
    return tuple(values)


def _parse_quality_tuple(payload: object, field: str) -> tuple[str, ...]:
    if not isinstance(payload, dict):
        return ()
    return _parse_string_tuple(payload.get(field))
