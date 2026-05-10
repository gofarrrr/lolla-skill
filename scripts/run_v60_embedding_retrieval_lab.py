#!/usr/bin/env python3
"""Compare lane-order v60 pickup with embedding-assisted v60 pickup.

This is a dormant lab harness. It does not call /lolla and does not promote
embedding-selected cards into runtime. It answers one diagnostic question:

    If v60 affordance and absence chunks were searched semantically, what would
    enter the packet compared with the current lane-order cap?

The script embeds the compiled v60 affordance/absence chunks, embeds each replay
case, ranks chunks by cosine similarity, and reports overlap against the current
lane-driven cap8 packet.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
ENGINE_DIR = REPO_ROOT / "engine"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from system_b.reasoning_substrate_packet import (  # noqa: E402
    build_reasoning_substrate_packet_from_files,
)
from scripts.run_v60_transaction_replay_lab import (  # noqa: E402
    DEFAULT_AFFORDANCES_PATH,
    LAB_VERSION,
    RUNTIME_POLICY,
    STATUS,
    build_case_artifact,
    extract_nominations_from_result,
    load_case_specs,
    merge_nominations,
)
from scripts.run_v60_transaction_paid_replay import DEFAULT_CASE_MANIFEST  # noqa: E402


EMBEDDING_LAB_VERSION = "v60_embedding_retrieval_lab.v1"
DEFAULT_OUTPUT_DIR = Path(
    "data/evaluations/v60_transaction_embedding_lab/2026-05-10-v60-embedding-pickup"
)
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
DEFAULT_CARD_CAP = 8
DEFAULT_MAX_NOMINATIONS = 18
DEFAULT_SNIPPET_CAP = 2
DEFAULT_TOP_CHUNKS = 18
DEFAULT_TOP_MODELS = 18
OPENAI_EMBEDDING_ENDPOINT = "https://api.openai.com/v1/embeddings"


class EmbeddingLabError(RuntimeError):
    pass


@dataclass(frozen=True)
class V60Chunk:
    chunk_id: str
    model_id: str
    chunk_kind: str
    affordance_id: str
    attempted_field: str
    status: str
    confidence: str
    text: str


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    root = REPO_ROOT
    manifest_path = _resolve(root, args.case_manifest)
    affordances_path = _resolve(root, args.affordances_path)
    output_dir = _resolve(root, args.output_dir)
    if affordances_path.name != "affordances_v60.json":
        raise EmbeddingLabError("This lab requires explicit affordances_v60.json")

    _load_dotenv(_resolve(root, args.env_file) if args.env_file else root / ".env")
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LOLLA_OPENAI_API_KEY")
    if not api_key and not args.dry_run:
        raise EmbeddingLabError("OPENAI_API_KEY is required unless --dry-run is set")

    manifest = _load_json(manifest_path)
    cases = load_case_specs(manifest, root=root)
    affordances = _load_json(affordances_path)
    chunks = build_v60_chunks(affordances)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        chunk_vectors = np.zeros((len(chunks), 1), dtype=np.float32)
        case_vectors = np.zeros((len(cases), 1), dtype=np.float32)
        usage_records: list[dict[str, Any]] = []
    else:
        chunk_vectors, chunk_usage = embed_texts(
            [chunk.text for chunk in chunks],
            api_key=api_key or "",
            model=args.embedding_model,
            batch_size=args.batch_size,
        )
        case_texts = [
            build_case_embedding_text(build_case_artifact(case, root=root))
            for case in cases
        ]
        case_vectors, case_usage = embed_texts(
            case_texts,
            api_key=api_key or "",
            model=args.embedding_model,
            batch_size=args.batch_size,
        )
        usage_records = [*chunk_usage, *case_usage]

    rows: list[dict[str, Any]] = []
    for case_index, case in enumerate(cases):
        case_artifact = build_case_artifact(case, root=root)
        packet = build_lane_packet(
            root=root,
            case=case,
            case_artifact=case_artifact,
            affordances_path=affordances_path,
            card_cap=args.card_cap,
            max_nominations=args.max_nominations,
            snippet_cap=args.snippet_cap,
        )
        row = analyze_case(
            case_id=case.case_id,
            case_stem=case.file_stem,
            packet=packet,
            chunks=chunks,
            chunk_vectors=chunk_vectors,
            case_vector=case_vectors[case_index],
            dry_run=bool(args.dry_run),
            top_chunks=args.top_chunks,
            top_models=args.top_models,
            card_cap=args.card_cap,
        )
        rows.append(row)
        _write_json(output_dir / "cases" / f"{case.file_stem}.json", row)

    summary = {
        "embedding_lab_version": EMBEDDING_LAB_VERSION,
        "lab_version": LAB_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "dry_run": bool(args.dry_run),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "case_manifest": str(manifest_path),
        "affordances_path": str(affordances_path),
        "embedding_model": "" if args.dry_run else args.embedding_model,
        "card_cap": args.card_cap,
        "max_nominations": args.max_nominations,
        "snippet_cap": args.snippet_cap,
        "chunk_count": len(chunks),
        "chunk_kind_counts": dict(Counter(chunk.chunk_kind for chunk in chunks)),
        "case_count": len(rows),
        "aggregate": aggregate_rows(rows, usage_records),
        "cases": rows,
    }
    _write_json(output_dir / "summary.json", summary)
    (output_dir / "embedding_retrieval_report.md").write_text(
        render_report(summary),
        encoding="utf-8",
    )
    print(f"wrote {output_dir / 'summary.json'}")
    print(f"wrote {output_dir / 'embedding_retrieval_report.md'}")
    return 0


def build_v60_chunks(payload: Mapping[str, Any]) -> list[V60Chunk]:
    chunks: list[V60Chunk] = []
    for affordance in (_mapping(item) for item in _list(payload.get("affordances"))):
        model_id = _text(affordance.get("model_id"))
        affordance_id = _text(affordance.get("affordance_id"))
        if not model_id or not affordance_id:
            continue
        chunks.append(
            V60Chunk(
                chunk_id=f"aff::{affordance_id}",
                model_id=model_id,
                chunk_kind="affordance",
                affordance_id=affordance_id,
                attempted_field="",
                status=_text(affordance.get("status")),
                confidence=_text(affordance.get("confidence")),
                text=affordance_embedding_text(affordance),
            )
        )

    for absence in (_mapping(item) for item in _list(payload.get("absence_records"))):
        model_id = _text(absence.get("model_id"))
        attempted_field = _text(absence.get("attempted_field"))
        if not model_id or not attempted_field:
            continue
        chunks.append(
            V60Chunk(
                chunk_id=f"abs::{model_id}::{attempted_field}",
                model_id=model_id,
                chunk_kind="absence",
                affordance_id="",
                attempted_field=attempted_field,
                status=_text(absence.get("status")),
                confidence="",
                text=absence_embedding_text(absence),
            )
        )
    return chunks


def affordance_embedding_text(affordance: Mapping[str, Any]) -> str:
    activation = _mapping(affordance.get("activation_shape"))
    review_notes = _mapping(affordance.get("review_notes"))
    source_quotes = [
        _text(item.get("source_quote"))
        for item in (_mapping(row) for row in _list(affordance.get("source_evidence"))[:2])
        if _text(item.get("source_quote"))
    ]
    requirements = []
    for row in (_mapping(item) for item in _list(affordance.get("treatment_requirements"))):
        requirements.append(
            " ".join(
                part
                for part in [
                    _text(row.get("description")),
                    " ".join(_strings(row.get("evidence_required"))),
                    " ".join(_strings(row.get("good_output_shape"))),
                ]
                if part
            )
        )
    return _compact(
        "\n".join(
            [
                f"kind: v60 reviewed affordance",
                f"model_id: {_text(affordance.get('model_id'))}",
                f"affordance_id: {_text(affordance.get('affordance_id'))}",
                f"name: {_text(affordance.get('name'))}",
                f"status: {_text(affordance.get('status'))}",
                f"confidence: {_text(affordance.get('confidence'))}",
                f"mechanism: {_text(affordance.get('mechanism'))}",
                f"use_when: {' | '.join(_strings(activation.get('use_when')))}",
                "case_evidence_needed: "
                + " | ".join(_strings(activation.get("case_evidence_needed"))),
                f"do_not_use_when: {' | '.join(_strings(activation.get('do_not_use_when')))}",
                f"treatment_requirements: {' | '.join(requirements[:3])}",
                f"diagnostic_questions: {' | '.join(_strings(affordance.get('diagnostic_questions')))}",
                f"misuse_guards: {' | '.join(_strings(affordance.get('misuse_guards')))}",
                f"source_quotes: {' | '.join(source_quotes)}",
                "dropped_material: "
                + " | ".join(_strings(review_notes.get("dropped_material"))[:2]),
            ]
        ),
        max_chars=3600,
    )


def absence_embedding_text(absence: Mapping[str, Any]) -> str:
    source_quotes = [
        _text(item.get("source_quote"))
        for item in (_mapping(row) for row in _list(absence.get("source_evidence"))[:2])
        if _text(item.get("source_quote"))
    ]
    return _compact(
        "\n".join(
            [
                "kind: v60 absence blocker",
                f"model_id: {_text(absence.get('model_id'))}",
                f"attempted_field: {_text(absence.get('attempted_field'))}",
                f"status: {_text(absence.get('status'))}",
                f"runtime_policy: {_text(absence.get('runtime_policy'))}",
                f"reason: {_text(absence.get('reason'))}",
                f"source_quotes: {' | '.join(source_quotes)}",
            ]
        ),
        max_chars=2200,
    )


def build_case_embedding_text(case_artifact: Mapping[str, Any]) -> str:
    return _compact(
        "\n\n".join(
            [
                "Retrieval goal: find v60 affordances or absence blockers worth "
                "private consideration by a reasoning model. Favor non-obvious "
                "frame changes, evidence gates, diagnostic questions, guardrails, "
                "boundary markers, and correct rejection aids. Do not optimize for "
                "public mental-model naming.",
                f"Case ID: {_text(case_artifact.get('case_id'))}",
                f"Query: {_text(case_artifact.get('query'))}",
                f"Risk notes: {' | '.join(_strings(case_artifact.get('risk_notes')))}",
                f"Conversation excerpt: {_text(case_artifact.get('conversation_excerpt'))[:10000]}",
                f"Vanilla answer: {_text(case_artifact.get('vanilla_answer'))[:6000]}",
            ]
        ),
        max_chars=18000,
    )


def build_lane_packet(
    *,
    root: Path,
    case: Any,
    case_artifact: Mapping[str, Any],
    affordances_path: Path,
    card_cap: int,
    max_nominations: int,
    snippet_cap: int,
) -> dict[str, Any]:
    nominations = (
        *case.explicit_nominations,
        *extract_nominations_from_result(
            case_artifact.get("result", {}),
            max_nominations=max_nominations,
        ),
    )
    nominations = merge_nominations(nominations)[:max_nominations]
    return build_reasoning_substrate_packet_from_files(
        root=root,
        packet_id=f"embedding-lab-{case.file_stem}",
        transaction_context={
            "case_id": case.case_id,
            "embedding_lab_version": EMBEDDING_LAB_VERSION,
            "lab_version": LAB_VERSION,
            "dry_run": False,
        },
        nominations=list(nominations),
        affordances_path=affordances_path,
        candidate_card_target_max=card_cap,
        snippet_target_max_per_card=snippet_cap,
    )


def analyze_case(
    *,
    case_id: str,
    case_stem: str,
    packet: Mapping[str, Any],
    chunks: list[V60Chunk],
    chunk_vectors: np.ndarray,
    case_vector: np.ndarray,
    dry_run: bool,
    top_chunks: int,
    top_models: int,
    card_cap: int,
) -> dict[str, Any]:
    lane_selected = [_text(card.get("model_id")) for card in _list(packet.get("candidate_cards"))]
    lane_suppressed = [
        _text(item.get("model_id")) for item in _list(packet.get("suppressed_candidates"))
    ]
    lane_full = [*lane_selected, *[mid for mid in lane_suppressed if mid not in lane_selected]]

    if dry_run:
        chunk_hits: list[dict[str, Any]] = []
        embedding_models: list[dict[str, Any]] = []
        absence_chunk_hits: list[dict[str, Any]] = []
        absence_models: list[dict[str, Any]] = []
    else:
        scores = cosine_scores(chunk_vectors, case_vector)
        chunk_hits = top_chunk_hits(chunks, scores, top_k=top_chunks)
        embedding_models = model_rank_from_chunks(chunks, scores, top_k=top_models)
        absence_chunk_hits = top_chunk_hits(
            chunks,
            scores,
            top_k=top_chunks,
            chunk_kind="absence",
        )
        absence_models = model_rank_from_chunks(
            chunks,
            scores,
            top_k=top_models,
            chunk_kind="absence",
        )

    embedding_top8 = [row["model_id"] for row in embedding_models[:card_cap]]
    absence_top8 = [row["model_id"] for row in absence_models[:card_cap]]
    hybrid_rrf = hybrid_rrf_rank(lane_full, [row["model_id"] for row in embedding_models])
    hybrid_top8 = hybrid_rrf[:card_cap]
    reserved_novelty_top8 = reserved_novelty_rank(
        lane_selected=lane_selected,
        embedding_rank=[row["model_id"] for row in embedding_models],
        card_cap=card_cap,
        lane_slots=max(4, card_cap - 3),
    )

    lane_set = set(lane_selected)
    embedding_set = set(embedding_top8)
    absence_set = set(absence_top8)
    hybrid_set = set(hybrid_top8)
    novelty_set = set(reserved_novelty_top8)

    return {
        "case_id": case_id,
        "case_stem": case_stem,
        "lane_selected_cap8": lane_selected,
        "lane_suppressed": lane_suppressed,
        "embedding_top8": embedding_top8,
        "absence_top8": absence_top8,
        "hybrid_rrf_top8": hybrid_top8,
        "reserved_novelty_top8": reserved_novelty_top8,
        "overlap": {
            "embedding_vs_lane_jaccard": jaccard(embedding_set, lane_set),
            "absence_vs_lane_jaccard": jaccard(absence_set, lane_set),
            "hybrid_vs_lane_jaccard": jaccard(hybrid_set, lane_set),
            "reserved_novelty_vs_lane_jaccard": jaccard(novelty_set, lane_set),
            "embedding_models_already_selected": sorted(embedding_set & lane_set),
            "absence_models_already_selected": sorted(absence_set & lane_set),
            "embedding_models_from_suppressed": sorted(embedding_set & set(lane_suppressed)),
            "absence_models_from_suppressed": sorted(absence_set & set(lane_suppressed)),
            "embedding_models_not_lane_nominated": sorted(
                embedding_set - set(lane_full)
            ),
            "absence_models_not_lane_nominated": sorted(absence_set - set(lane_full)),
            "hybrid_models_from_suppressed": sorted(hybrid_set & set(lane_suppressed)),
            "reserved_novelty_models_from_suppressed": sorted(
                novelty_set & set(lane_suppressed)
            ),
        },
        "top_embedding_models": embedding_models,
        "top_absence_models": absence_models,
        "top_embedding_chunks": chunk_hits,
        "top_absence_chunks": absence_chunk_hits,
        "lane_suppressed_count": len(lane_suppressed),
        "packet_coverage_summary": _mapping(packet.get("coverage_summary")),
    }


def top_chunk_hits(
    chunks: list[V60Chunk],
    scores: np.ndarray,
    *,
    top_k: int,
    chunk_kind: str = "",
) -> list[dict[str, Any]]:
    if len(scores) == 0:
        return []
    eligible = [
        index
        for index, chunk in enumerate(chunks)
        if not chunk_kind or chunk.chunk_kind == chunk_kind
    ]
    if not eligible:
        return []
    eligible_scores = scores[np.asarray(eligible, dtype=np.int64)]
    order = np.asarray(eligible, dtype=np.int64)[np.argsort(-eligible_scores)[:top_k]]
    rows = []
    for rank, index in enumerate(order, start=1):
        chunk = chunks[int(index)]
        rows.append(
            {
                "rank": rank,
                "chunk_id": chunk.chunk_id,
                "model_id": chunk.model_id,
                "chunk_kind": chunk.chunk_kind,
                "affordance_id": chunk.affordance_id,
                "attempted_field": chunk.attempted_field,
                "status": chunk.status,
                "confidence": chunk.confidence,
                "score": round(float(scores[int(index)]), 6),
                "text_preview": chunk.text[:360],
            }
        )
    return rows


def model_rank_from_chunks(
    chunks: list[V60Chunk],
    scores: np.ndarray,
    *,
    top_k: int,
    chunk_kind: str = "",
) -> list[dict[str, Any]]:
    by_model: dict[str, list[tuple[float, V60Chunk]]] = defaultdict(list)
    for score, chunk in zip(scores, chunks):
        if chunk_kind and chunk.chunk_kind != chunk_kind:
            continue
        by_model[chunk.model_id].append((float(score), chunk))

    rows = []
    for model_id, pairs in by_model.items():
        pairs.sort(key=lambda item: item[0], reverse=True)
        best_score, best_chunk = pairs[0]
        top3 = pairs[:3]
        rows.append(
            {
                "model_id": model_id,
                "score": round(best_score, 6),
                "best_chunk_kind": best_chunk.chunk_kind,
                "best_chunk_id": best_chunk.chunk_id,
                "best_affordance_id": best_chunk.affordance_id,
                "best_absence_field": best_chunk.attempted_field,
                "top_chunk_kinds": dict(Counter(chunk.chunk_kind for _, chunk in top3)),
                "top_chunk_ids": [chunk.chunk_id for _, chunk in top3],
            }
        )
    rows.sort(key=lambda item: item["score"], reverse=True)
    return rows[:top_k]


def hybrid_rrf_rank(lane_rank: list[str], embedding_rank: list[str], *, k: int = 60) -> list[str]:
    scores: dict[str, float] = {}
    for rank, model_id in enumerate(dict.fromkeys(lane_rank), start=1):
        scores[model_id] = scores.get(model_id, 0.0) + 1.0 / (k + rank)
    for rank, model_id in enumerate(dict.fromkeys(embedding_rank), start=1):
        scores[model_id] = scores.get(model_id, 0.0) + 1.0 / (k + rank)
    return [
        model_id
        for model_id, _ in sorted(
            scores.items(),
            key=lambda item: (-item[1], lane_rank.index(item[0]) if item[0] in lane_rank else 10**6),
        )
    ]


def reserved_novelty_rank(
    *,
    lane_selected: list[str],
    embedding_rank: list[str],
    card_cap: int,
    lane_slots: int,
) -> list[str]:
    selected = list(dict.fromkeys(lane_selected[:lane_slots]))
    for model_id in embedding_rank:
        if model_id not in selected:
            selected.append(model_id)
        if len(selected) >= card_cap:
            break
    return selected[:card_cap]


def cosine_scores(matrix: np.ndarray, query: np.ndarray) -> np.ndarray:
    if matrix.size == 0 or query.size == 0:
        return np.array([], dtype=np.float32)
    matrix = matrix.astype(np.float32, copy=False)
    query = query.astype(np.float32, copy=False)
    matrix_norms = np.linalg.norm(matrix, axis=1)
    query_norm = float(np.linalg.norm(query))
    if query_norm < 1e-12:
        return np.zeros((matrix.shape[0],), dtype=np.float32)
    denom = np.maximum(matrix_norms * query_norm, 1e-12)
    return np.dot(matrix, query) / denom


def embed_texts(
    texts: list[str],
    *,
    api_key: str,
    model: str,
    batch_size: int,
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    vectors: list[list[float]] = []
    usage_records: list[dict[str, Any]] = []
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        payload = json.dumps({"model": model, "input": batch}).encode("utf-8")
        req = urllib.request.Request(
            OPENAI_EMBEDDING_ENDPOINT,
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=120) as response:
            body = json.loads(response.read().decode("utf-8"))
        data = sorted(body.get("data", []), key=lambda item: int(item.get("index", 0)))
        vectors.extend(item["embedding"] for item in data)
        usage = _mapping(body.get("usage"))
        usage_records.append(
            {
                "endpoint": "embeddings",
                "model": model,
                "batch_start": start,
                "batch_size": len(batch),
                "prompt_tokens": int(usage.get("prompt_tokens", 0) or 0),
                "total_tokens": int(usage.get("total_tokens", 0) or 0),
            }
        )
    if len(vectors) != len(texts):
        raise EmbeddingLabError(f"expected {len(texts)} embeddings, got {len(vectors)}")
    return np.asarray(vectors, dtype=np.float32), usage_records


def aggregate_rows(
    rows: list[Mapping[str, Any]],
    usage_records: list[Mapping[str, Any]],
) -> dict[str, Any]:
    embedding_vs_lane = [
        float(_mapping(row.get("overlap")).get("embedding_vs_lane_jaccard", 0.0))
        for row in rows
    ]
    absence_vs_lane = [
        float(_mapping(row.get("overlap")).get("absence_vs_lane_jaccard", 0.0))
        for row in rows
    ]
    suppressed_hits = []
    absence_suppressed_hits = []
    not_nominated = []
    absence_not_nominated = []
    best_kind_counts: Counter[str] = Counter()
    for row in rows:
        overlap = _mapping(row.get("overlap"))
        suppressed_hits.extend(_list(overlap.get("embedding_models_from_suppressed")))
        absence_suppressed_hits.extend(_list(overlap.get("absence_models_from_suppressed")))
        not_nominated.extend(_list(overlap.get("embedding_models_not_lane_nominated")))
        absence_not_nominated.extend(_list(overlap.get("absence_models_not_lane_nominated")))
        for model in (_mapping(item) for item in _list(row.get("top_embedding_models"))[:8]):
            best_kind_counts[_text(model.get("best_chunk_kind"))] += 1
    return {
        "embedding_vs_lane_jaccard_mean": round(mean(embedding_vs_lane), 4),
        "embedding_vs_lane_jaccard_min": round(min(embedding_vs_lane), 4)
        if embedding_vs_lane
        else 0.0,
        "absence_vs_lane_jaccard_mean": round(mean(absence_vs_lane), 4),
        "absence_vs_lane_jaccard_min": round(min(absence_vs_lane), 4)
        if absence_vs_lane
        else 0.0,
        "embedding_suppressed_hit_count": len(suppressed_hits),
        "embedding_suppressed_hit_models": dict(Counter(_text(item) for item in suppressed_hits)),
        "absence_suppressed_hit_count": len(absence_suppressed_hits),
        "absence_suppressed_hit_models": dict(
            Counter(_text(item) for item in absence_suppressed_hits)
        ),
        "embedding_not_lane_nominated_count": len(not_nominated),
        "embedding_not_lane_nominated_models": dict(Counter(_text(item) for item in not_nominated)),
        "absence_not_lane_nominated_count": len(absence_not_nominated),
        "absence_not_lane_nominated_models": dict(
            Counter(_text(item) for item in absence_not_nominated)
        ),
        "embedding_top8_best_chunk_kind_counts": dict(best_kind_counts),
        "embedding_usage": {
            "call_count": len(usage_records),
            "prompt_tokens": sum(int(row.get("prompt_tokens", 0) or 0) for row in usage_records),
            "total_tokens": sum(int(row.get("total_tokens", 0) or 0) for row in usage_records),
        },
    }


def render_report(summary: Mapping[str, Any]) -> str:
    aggregate = _mapping(summary.get("aggregate"))
    rows = [_mapping(item) for item in _list(summary.get("cases"))]
    lines = [
        "# V60 Embedding Retrieval Lab Report",
        "",
        f"Date: {_text(summary.get('generated_at'))[:10]}",
        "Status: dormant replay evidence only",
        f"Embedding model: `{_text(summary.get('embedding_model')) or 'not run'}`",
        f"Artifact: `{Path(_text(summary.get('affordances_path'))).name}`",
        "",
        "## Aggregate",
        "",
        f"- Cases: {len(rows)}",
        f"- V60 chunks embedded: {_int(summary.get('chunk_count'))}",
        f"- Chunk kinds: `{json.dumps(_mapping(summary.get('chunk_kind_counts')), sort_keys=True)}`",
        f"- Mean embedding-vs-lane top8 Jaccard: `{aggregate.get('embedding_vs_lane_jaccard_mean')}`",
        f"- Mean absence-only-vs-lane top8 Jaccard: `{aggregate.get('absence_vs_lane_jaccard_mean')}`",
        f"- Suppressed models recovered by embedding top8: `{aggregate.get('embedding_suppressed_hit_count')}`",
        f"- Suppressed models recovered by absence-only top8: `{aggregate.get('absence_suppressed_hit_count')}`",
        f"- Models not nominated by lanes but found by embedding top8: `{aggregate.get('embedding_not_lane_nominated_count')}`",
        f"- Models not nominated by lanes but found by absence-only top8: `{aggregate.get('absence_not_lane_nominated_count')}`",
        f"- Embedding top8 best chunk kinds: `{json.dumps(_mapping(aggregate.get('embedding_top8_best_chunk_kind_counts')), sort_keys=True)}`",
        f"- Embedding usage: `{json.dumps(_mapping(aggregate.get('embedding_usage')), sort_keys=True)}`",
        "",
        "## Case Comparison",
        "",
        "| Case | Lane cap8 | Embedding top8 | Suppressed recovered | Not lane-nominated | Jaccard |",
        "| --- | --- | --- | --- | --- | ---: |",
    ]
    for row in rows:
        overlap = _mapping(row.get("overlap"))
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{_text(row.get('case_stem'))}`",
                    ", ".join(f"`{item}`" for item in _list(row.get("lane_selected_cap8"))),
                    ", ".join(f"`{item}`" for item in _list(row.get("embedding_top8"))),
                    ", ".join(
                        f"`{item}`"
                        for item in _list(overlap.get("embedding_models_from_suppressed"))
                    )
                    or "-",
                    ", ".join(
                        f"`{item}`"
                        for item in _list(overlap.get("embedding_models_not_lane_nominated"))
                    )
                    or "-",
                    str(overlap.get("embedding_vs_lane_jaccard")),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Top Chunk Samples", ""])
    for row in rows:
        lines.append(f"### `{_text(row.get('case_stem'))}`")
        for hit in (_mapping(item) for item in _list(row.get("top_embedding_chunks"))[:5]):
            label = _text(hit.get("affordance_id")) or _text(hit.get("attempted_field"))
            lines.append(
                f"- `{hit.get('rank')}` `{hit.get('model_id')}` "
                f"`{hit.get('chunk_kind')}` `{label}` score `{hit.get('score')}`"
            )
        lines.append("")
    lines.extend(["", "## Absence-Only Samples", ""])
    for row in rows:
        lines.append(f"### `{_text(row.get('case_stem'))}`")
        lines.append(
            "- absence top8: "
            + ", ".join(f"`{item}`" for item in _list(row.get("absence_top8")))
        )
        for hit in (_mapping(item) for item in _list(row.get("top_absence_chunks"))[:5]):
            lines.append(
                f"- `{hit.get('rank')}` `{hit.get('model_id')}` "
                f"`{hit.get('attempted_field')}` score `{hit.get('score')}`"
            )
        lines.append("")
    lines.extend(
        [
            "## Read",
            "",
            "This report only compares retrieval behavior. It does not prove that an",
            "embedding-selected packet improves final answers. The next evidence step is",
            "to feed one or two embedding/hybrid packets into the C4.3 private",
            "consideration router and compare usefulness, rejection, deferral, and leak",
            "rates against the lane-order packet.",
            "",
        ]
    )
    return "\n".join(lines)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-manifest", type=Path, default=DEFAULT_CASE_MANIFEST)
    parser.add_argument("--affordances-path", type=Path, default=DEFAULT_AFFORDANCES_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    parser.add_argument("--embedding-model", default=DEFAULT_EMBEDDING_MODEL)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--card-cap", type=int, default=DEFAULT_CARD_CAP)
    parser.add_argument("--max-nominations", type=int, default=DEFAULT_MAX_NOMINATIONS)
    parser.add_argument("--snippet-cap", type=int, default=DEFAULT_SNIPPET_CAP)
    parser.add_argument("--top-chunks", type=int, default=DEFAULT_TOP_CHUNKS)
    parser.add_argument("--top-models", type=int, default=DEFAULT_TOP_MODELS)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _resolve(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    return round(len(a & b) / len(a | b), 4)


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _compact(text: str, *, max_chars: int) -> str:
    text = " ".join(text.split())
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 20].rstrip() + " [truncated]"


def _strings(value: Any) -> list[str]:
    return [_text(item) for item in _list(value) if _text(item)]


def _text(value: Any) -> str:
    return str(value or "").strip()


def _int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


if __name__ == "__main__":
    raise SystemExit(main())
