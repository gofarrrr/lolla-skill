"""SQLite storage for per-edge activation_condition embeddings.

Phase 3 infrastructure (Section 14 of deep-graph-enrichment-handover.md).
Stores pre-built embeddings of each compiled edge's `activation_condition`
string, keyed by (source_model_id, target_model_id, edge_type). Read at
query time by `activation_matcher.match_activation()`; written at compile
time by `scripts/build_edge_activation_embeddings.py`.

Isolated from other embedding tables so it can be dropped / rebuilt without
touching `model_signals`, `tendency_guidance`, or `chunk_embeddings`.

Graceful degradation rule: all read helpers return None / empty on missing
DB or missing rows. They never raise. Callers treat "no backfill" the same
as "no signal" and abstain.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from .embedding_common import blob_to_vec, content_hash, vec_to_blob


TABLE_NAME = "edge_activation_conditions"

_SCHEMA_SQL = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_model_id TEXT NOT NULL,
    target_model_id TEXT NOT NULL,
    edge_type TEXT NOT NULL,
    activation_condition_text TEXT NOT NULL,
    embedding BLOB NOT NULL,
    content_hash TEXT NOT NULL,
    UNIQUE(source_model_id, target_model_id, edge_type)
)
"""


def ensure_schema(db_path: Path | str) -> None:
    """Create the table if it doesn't exist. Idempotent."""
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(_SCHEMA_SQL)
        conn.commit()


def upsert_edge_embedding(
    db_path: Path | str,
    *,
    source_model_id: str,
    target_model_id: str,
    edge_type: str,
    activation_condition_text: str,
    embedding: list[float],
) -> None:
    """Insert or replace the embedding for a single edge.

    Uses content_hash for change detection — callers can skip re-embedding
    when the activation_condition_text hasn't changed (compare to existing
    hash via `get_edge_embedding_hash`).
    """
    blob = vec_to_blob(embedding)
    chash = content_hash(activation_condition_text)
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(
            f"""
            INSERT INTO {TABLE_NAME}
                (source_model_id, target_model_id, edge_type,
                 activation_condition_text, embedding, content_hash)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(source_model_id, target_model_id, edge_type)
            DO UPDATE SET
                activation_condition_text=excluded.activation_condition_text,
                embedding=excluded.embedding,
                content_hash=excluded.content_hash
            """,
            (
                source_model_id,
                target_model_id,
                edge_type,
                activation_condition_text,
                blob,
                chash,
            ),
        )
        conn.commit()


def get_edge_embedding(
    db_path: Path | str,
    *,
    source_model_id: str,
    target_model_id: str,
    edge_type: str,
) -> list[float] | None:
    """Return the stored embedding vector, or None if missing / DB absent."""
    path = Path(db_path)
    if not path.exists():
        return None
    try:
        with sqlite3.connect(str(path)) as conn:
            row = conn.execute(
                f"""
                SELECT embedding FROM {TABLE_NAME}
                WHERE source_model_id=? AND target_model_id=? AND edge_type=?
                """,
                (source_model_id, target_model_id, edge_type),
            ).fetchone()
    except sqlite3.Error:
        return None
    if row is None:
        return None
    return blob_to_vec(row[0])


def get_edge_embedding_hash(
    db_path: Path | str,
    *,
    source_model_id: str,
    target_model_id: str,
    edge_type: str,
) -> str | None:
    """Return the stored content_hash, or None if missing. Used by the
    backfill script to decide whether to re-embed."""
    path = Path(db_path)
    if not path.exists():
        return None
    try:
        with sqlite3.connect(str(path)) as conn:
            row = conn.execute(
                f"""
                SELECT content_hash FROM {TABLE_NAME}
                WHERE source_model_id=? AND target_model_id=? AND edge_type=?
                """,
                (source_model_id, target_model_id, edge_type),
            ).fetchone()
    except sqlite3.Error:
        return None
    return row[0] if row else None


def count_edges(db_path: Path | str) -> int:
    """Number of backfilled rows. Useful for operator-level health checks."""
    path = Path(db_path)
    if not path.exists():
        return 0
    try:
        with sqlite3.connect(str(path)) as conn:
            row = conn.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()
    except sqlite3.Error:
        return 0
    return int(row[0]) if row else 0
