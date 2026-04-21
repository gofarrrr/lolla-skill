#!/usr/bin/env python3
"""Backfill per-edge `activation_condition` embeddings into embeddings.db.

Phase 3 infrastructure (Section 14 of deep-graph-enrichment-handover.md).
Reads `data/relationship_graph.json`, finds every edge with a non-empty
`activation_condition` string, embeds it via OpenAI `text-embedding-3-large`,
and stores the vector in the `edge_activation_conditions` table.

Current graph state: 867 of 1,358 edges (ally + antagonist) carry an
activation_condition. Tension edges (491) carry only `source_description`
and are intentionally skipped — see Section 14f Phase 2 block (REV-6) for
why the tension re-read was rejected.

Idempotent: re-running only re-embeds edges whose text has changed
(detected via content_hash). Estimated cost: ~$2 for a fresh full run.

Usage
-----
    OPENAI_API_KEY=sk-... python scripts/build_edge_activation_embeddings.py

Options via env vars:
    LOLLA_GRAPH_PATH      override graph JSON path
    LOLLA_EMBEDDINGS_DB   override embeddings.db path
    LOLLA_DRY_RUN=1       print counts only, no API calls, no writes

Exit codes: 0 ok, 1 config error (missing key / files), 2 embed failure.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.edge_activation_store import (  # noqa: E402
    count_edges,
    ensure_schema,
    get_edge_embedding_hash,
    upsert_edge_embedding,
)
from engine.system_b.embedding_common import content_hash  # noqa: E402
from engine.system_b.embedding_retriever import _embed_batch  # noqa: E402


DEFAULT_GRAPH_PATH = Path("data/relationship_graph.json")
DEFAULT_DB_PATH = Path("data/embeddings.db")
BATCH_SIZE = 50
THROTTLE_SECONDS = 0.1  # between batches


def _load_edges(graph_path: Path) -> list[dict]:
    with graph_path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        edges = data.get("edges", [])
        return edges if isinstance(edges, list) else []
    return []


def _edge_triples_to_backfill(edges: list[dict]) -> list[tuple[str, str, str, str]]:
    """Return (source_model_id, target_model_id, edge_type, activation_condition_text)
    for each edge with a non-empty activation_condition."""
    out: list[tuple[str, str, str, str]] = []
    for e in edges:
        ac = (e.get("activation_condition") or "").strip()
        if not ac:
            continue
        src = str(e.get("source_model_id", "")).strip()
        tgt = str(e.get("target_model_id", "")).strip()
        etype = str(e.get("edge_type") or e.get("relation_type") or "").strip().lower()
        if not src or not tgt or not etype:
            continue
        out.append((src, tgt, etype, ac))
    return out


def _chunks(seq: list, size: int):
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def main() -> int:
    graph_path = Path(os.environ.get("LOLLA_GRAPH_PATH", DEFAULT_GRAPH_PATH))
    db_path = Path(os.environ.get("LOLLA_EMBEDDINGS_DB", DEFAULT_DB_PATH))
    dry_run = os.environ.get("LOLLA_DRY_RUN", "") == "1"

    if not graph_path.exists():
        print(f"ERROR: graph file not found: {graph_path}", file=sys.stderr)
        return 1
    if not db_path.exists():
        print(f"ERROR: embeddings.db not found: {db_path}", file=sys.stderr)
        return 1

    edges = _load_edges(graph_path)
    targets = _edge_triples_to_backfill(edges)
    print(f"Loaded {len(edges)} edges; {len(targets)} carry activation_condition.")

    ensure_schema(db_path)
    prior_rows = count_edges(db_path)
    print(f"Existing backfilled rows: {prior_rows}")

    to_embed: list[tuple[str, str, str, str]] = []
    for src, tgt, etype, text in targets:
        existing_hash = get_edge_embedding_hash(
            db_path,
            source_model_id=src,
            target_model_id=tgt,
            edge_type=etype,
        )
        if existing_hash == content_hash(text):
            continue  # unchanged
        to_embed.append((src, tgt, etype, text))

    print(f"Need to embed: {len(to_embed)} (new or changed)")

    if dry_run:
        print("DRY RUN — no API calls, no writes.")
        return 0

    if not to_embed:
        print("Nothing to do. All edges are up to date.")
        return 0

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set.", file=sys.stderr)
        return 1

    written = 0
    failed = 0
    for batch in _chunks(to_embed, BATCH_SIZE):
        texts = [text for _, _, _, text in batch]
        vectors = _embed_batch(texts, api_key)
        if vectors is None or len(vectors) != len(batch):
            print(
                f"WARN: batch embed failed for {len(batch)} items, skipping",
                file=sys.stderr,
            )
            failed += len(batch)
            continue
        for (src, tgt, etype, text), vec in zip(batch, vectors):
            upsert_edge_embedding(
                db_path,
                source_model_id=src,
                target_model_id=tgt,
                edge_type=etype,
                activation_condition_text=text,
                embedding=vec,
            )
            written += 1
        time.sleep(THROTTLE_SECONDS)

    print(f"Wrote {written} embeddings; {failed} failed.")
    print(f"Total backfilled rows now: {count_edges(db_path)}")
    return 2 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
