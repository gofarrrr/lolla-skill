from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .compiled_substrate import CompiledChunk, CompiledSubstrate
from .deep_check_packet import DeepCheckPacket
from .pressure_router import PressureRoute, PressureRouter


@dataclass(frozen=True)
class SelectedChunkRecord:
    lane: str
    chunk_id: str
    chunk_type: str
    model_id: str
    text: str
    source_file: str = ""
    source_quote: str = ""
    extraction_type: str = ""
    confidence: str = ""
    guardrail_tags: tuple[str, ...] = ()
    blocking_quality_flags: tuple[str, ...] = ()
    advisory_quality_flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class PressureBundle:
    route: PressureRoute
    packet: DeepCheckPacket | None = None
    diagnosis_chunk_id: str = ""
    challenge_chunk_id: str = ""
    protocol_chunk_id: str = ""
    tension_chunk_id: str = ""
    selected_chunk_ids: tuple[str, ...] = ()
    selected_chunks: tuple[SelectedChunkRecord, ...] = ()


class PressureBundleSelector:
    def __init__(
        self,
        router: PressureRouter,
        substrate: CompiledSubstrate,
    ) -> None:
        self._router = router
        self._substrate = substrate

    @classmethod
    def load(cls, root: Path) -> "PressureBundleSelector":
        root = Path(root)
        return cls(
            router=PressureRouter.load(root),
            substrate=CompiledSubstrate.load(root),
        )

    def select(
        self,
        tendency_key: str,
        *,
        subpattern_id: str = "general",
        reasoning_context: Any = None,
        embeddings_db_path: Path | str | None = None,
        openai_api_key: str | None = None,
    ) -> PressureBundle:
        route = self._router.route(
            tendency_key,
            subpattern_id=subpattern_id,
            reasoning_context=reasoning_context,
            embeddings_db_path=embeddings_db_path,
            openai_api_key=openai_api_key,
        )
        return self._select_from_route(route=route, packet=None)

    def select_from_packet(
        self,
        packet: DeepCheckPacket,
        *,
        reasoning_context: Any = None,
        embeddings_db_path: Path | str | None = None,
        openai_api_key: str | None = None,
    ) -> PressureBundle:
        route = self._router.route(
            packet.tendency_id,
            subpattern_id=packet.subpattern_id,
            reasoning_context=reasoning_context,
            embeddings_db_path=embeddings_db_path,
            openai_api_key=openai_api_key,
        )
        return self._select_from_route(route=route, packet=packet)

    def _select_from_route(
        self,
        *,
        route: PressureRoute,
        packet: DeepCheckPacket | None,
    ) -> PressureBundle:
        model_priority = _dedupe_model_ids(
            (
                route.primary_model_id,
                *route.candidate_model_ids,
                *route.supporting_model_ids,
            )
        )
        chunks = _filter_chunks_for_tendency(
            self._substrate.chunks_for_models(model_priority),
            tendency_id=route.tendency_id,
        )
        tension_model_priority = _tension_model_priority(route)
        tension_chunks = _filter_chunks_for_tendency(
            self._substrate.chunks_for_models(tension_model_priority),
            tendency_id=route.tendency_id,
        )
        diagnosis = _select_chunk(
            chunks=chunks,
            model_priority=model_priority,
            subpattern_id=route.subpattern_id,
            chunk_type_priority=("diagnosis", "failure_mode", "select_when"),
        )
        challenge = _select_chunk(
            chunks=chunks,
            model_priority=model_priority,
            subpattern_id=route.subpattern_id,
            chunk_type_priority=("challenge", "premortem_question"),
            used_chunk_ids={diagnosis.chunk_id} if diagnosis else set(),
        )
        protocol = _select_chunk(
            chunks=chunks,
            model_priority=model_priority,
            subpattern_id=route.subpattern_id,
            chunk_type_priority=("protocol", "heuristic"),
            used_chunk_ids={chunk_id for chunk_id in (diagnosis.chunk_id if diagnosis else "", challenge.chunk_id if challenge else "") if chunk_id},
        )
        tension = _select_chunk(
            chunks=tension_chunks,
            model_priority=tension_model_priority,
            subpattern_id=route.subpattern_id,
            chunk_type_priority=("tension", "guardrail", "danger_when", "failure_mode"),
            used_chunk_ids={
                chunk_id
                for chunk_id in (
                    diagnosis.chunk_id if diagnosis else "",
                    challenge.chunk_id if challenge else "",
                    protocol.chunk_id if protocol else "",
                )
                if chunk_id
            },
        )
        selected_chunk_ids = tuple(
            chunk_id
            for chunk_id in (
                diagnosis.chunk_id if diagnosis else "",
                challenge.chunk_id if challenge else "",
                protocol.chunk_id if protocol else "",
                tension.chunk_id if tension else "",
            )
            if chunk_id
        )
        selected_chunks = tuple(
            record
            for record in (
                _chunk_record("diagnosis", diagnosis),
                _chunk_record("challenge", challenge),
                _chunk_record("protocol", protocol),
                _chunk_record("tension", tension),
            )
            if record is not None
        )
        return PressureBundle(
            route=route,
            packet=packet,
            diagnosis_chunk_id=diagnosis.chunk_id if diagnosis else "",
            challenge_chunk_id=challenge.chunk_id if challenge else "",
            protocol_chunk_id=protocol.chunk_id if protocol else "",
            tension_chunk_id=tension.chunk_id if tension else "",
            selected_chunk_ids=selected_chunk_ids,
            selected_chunks=selected_chunks,
        )


def _select_chunk(
    *,
    chunks: tuple[CompiledChunk, ...],
    model_priority: tuple[str, ...],
    subpattern_id: str,
    chunk_type_priority: tuple[str, ...],
    used_chunk_ids: set[str] | None = None,
) -> CompiledChunk | None:
    used_chunk_ids = used_chunk_ids or set()
    exact_candidates = _filter_chunk_candidates(
        chunks=chunks,
        model_priority=model_priority,
        subpattern_match=subpattern_id,
        chunk_type_priority=chunk_type_priority,
        used_chunk_ids=used_chunk_ids,
    )
    if exact_candidates:
        return exact_candidates[0]
    general_candidates = _filter_chunk_candidates(
        chunks=chunks,
        model_priority=model_priority,
        subpattern_match="general",
        chunk_type_priority=chunk_type_priority,
        used_chunk_ids=used_chunk_ids,
    )
    if general_candidates:
        return general_candidates[0]
    empty_candidates = _filter_chunk_candidates(
        chunks=chunks,
        model_priority=model_priority,
        subpattern_match="",
        chunk_type_priority=chunk_type_priority,
        used_chunk_ids=used_chunk_ids,
    )
    if empty_candidates:
        return empty_candidates[0]
    return None


def _filter_chunk_candidates(
    *,
    chunks: tuple[CompiledChunk, ...],
    model_priority: tuple[str, ...],
    subpattern_match: str,
    chunk_type_priority: tuple[str, ...],
    used_chunk_ids: set[str],
) -> list[CompiledChunk]:
    model_rank = {model_id: index for index, model_id in enumerate(model_priority)}
    type_rank = {chunk_type: index for index, chunk_type in enumerate(chunk_type_priority)}
    candidates: list[CompiledChunk] = []
    normalized_subpattern = _normalize_subpattern_id(subpattern_match)
    for chunk in chunks:
        if chunk.chunk_id in used_chunk_ids:
            continue
        if chunk.model_id not in model_rank:
            continue
        if chunk.chunk_type not in type_rank:
            continue
        chunk_subpatterns = {_normalize_subpattern_id(value) for value in chunk.subpattern_ids}
        if normalized_subpattern:
            if normalized_subpattern not in chunk_subpatterns:
                continue
        else:
            if chunk_subpatterns:
                continue
        candidates.append(chunk)
    return sorted(
        candidates,
        key=lambda chunk: (
            model_rank.get(chunk.model_id, 10_000),
            type_rank.get(chunk.chunk_type, 10_000),
            chunk.chunk_id,
        ),
    )


def _normalize_subpattern_id(value: str) -> str:
    return str(value or "").strip().replace("_", "-").lower()


def _filter_chunks_for_tendency(
    chunks: tuple[CompiledChunk, ...],
    *,
    tendency_id: str,
) -> tuple[CompiledChunk, ...]:
    normalized_tendency_id = str(tendency_id or "").strip()
    if not normalized_tendency_id:
        return chunks
    return tuple(
        chunk
        for chunk in chunks
        if normalized_tendency_id in chunk.tendency_ids
    )


def _dedupe_model_ids(model_ids: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    results: list[str] = []
    seen: set[str] = set()
    for model_id in model_ids:
        value = str(model_id).strip()
        if not value or value in seen:
            continue
        seen.add(value)
        results.append(value)
    return tuple(results)


def _tension_model_priority(route: PressureRoute) -> tuple[str, ...]:
    return _dedupe_model_ids(
        (
            *route.risk_model_ids,
            route.primary_model_id,
            *route.candidate_model_ids,
            *route.supporting_model_ids,
        )
    )


def _chunk_record(lane: str, chunk: CompiledChunk | None) -> SelectedChunkRecord | None:
    if chunk is None:
        return None
    return SelectedChunkRecord(
        lane=lane,
        chunk_id=chunk.chunk_id,
        chunk_type=chunk.chunk_type,
        model_id=chunk.model_id,
        text=chunk.text,
        source_file=chunk.source_file,
        source_quote=chunk.source_quote,
        extraction_type=chunk.extraction_type,
        confidence=chunk.confidence,
        guardrail_tags=chunk.guardrail_tags,
        blocking_quality_flags=chunk.blocking_quality_flags,
        advisory_quality_flags=chunk.advisory_quality_flags,
    )
