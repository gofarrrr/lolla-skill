"""Query-time embedding retriever for System B.

Loads pre-built embeddings.db and computes cosine similarity at request time.
Graceful degradation: never raises, returns empty results on failure.
"""
from __future__ import annotations

import hashlib
import json
import logging
import math
import os
import sqlite3
import urllib.request
from pathlib import Path

_LOGGER = logging.getLogger("system_b.embedding_retriever")

from .embedding_common import blob_to_vec


EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_ENDPOINT = "https://api.openai.com/v1/embeddings"


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(float(x) * float(y) for x, y in zip(a, b))
    norm_a = math.sqrt(sum(float(x) * float(x) for x in a))
    norm_b = math.sqrt(sum(float(x) * float(x) for x in b))
    if norm_a < 1e-10 or norm_b < 1e-10:
        return 0.0
    return float(dot) / (float(norm_a) * float(norm_b))


# ---------------------------------------------------------------------------
# Query embedding
# ---------------------------------------------------------------------------
def embed_query(text: str, api_key: str) -> list[float] | None:
    """Embed a single query string. Returns None on failure."""
    try:
        payload = json.dumps({
            "model": EMBEDDING_MODEL,
            "input": [text],
        }).encode("utf-8")
        req = urllib.request.Request(
            EMBEDDING_ENDPOINT,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return body["data"][0]["embedding"]
    except Exception:
        _LOGGER.warning("embed_query: API call failed", exc_info=True)
        return None


# ---------------------------------------------------------------------------
# Retriever
# ---------------------------------------------------------------------------
class EmbeddingRetriever:
    """Read-only interface over embeddings.db for query-time retrieval."""

    def __init__(self, db_path: str | Path):
        self._db_path = Path(db_path)
        self._conn: sqlite3.Connection | None = None
        self._query_cache: dict[str, list[float]] = {}

    def _connect(self) -> sqlite3.Connection | None:
        if self._conn is None:
            if not self._db_path.exists():
                return None
            self._conn = sqlite3.connect(str(self._db_path))
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def available(self) -> bool:
        """Check if embeddings.db exists and has data."""
        conn = self._connect()
        if conn is None:
            return False
        try:
            row = conn.execute("SELECT COUNT(*) FROM model_signals").fetchone()
            return row[0] > 0
        except Exception:
            _LOGGER.warning("embedding_retriever.available: query failed", exc_info=True)
            return False

    # -- Query embedding with cache ------------------------------------------

    def embed_and_cache(self, text: str, api_key: str) -> list[float] | None:
        """Embed query text, caching by content hash."""
        h = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
        if h in self._query_cache:
            return self._query_cache[h]
        vec = embed_query(text, api_key)
        if vec is not None:
            self._query_cache[h] = vec
        return vec

    # -- Model signal retrieval ----------------------------------------------

    def rank_models(
        self,
        query_vec: list[float],
        signal_types: tuple[str, ...] = ("select_when", "danger_when"),
        top_k: int = 30,
    ) -> list[dict]:
        """Rank models by cosine similarity to query vector.

        Returns list of {model_id, signal_type, score} sorted descending.
        If a model appears in both signal types, both entries are returned
        (caller decides how to merge).
        """
        conn = self._connect()
        if conn is None:
            return []
        try:
            placeholders = ",".join("?" for _ in signal_types)
            rows = conn.execute(
                f"SELECT model_id, signal_type, embedding FROM model_signals "
                f"WHERE signal_type IN ({placeholders})",
                signal_types,
            ).fetchall()
        except Exception:
            _LOGGER.warning("rank_models: query failed", exc_info=True)
            return []

        scored = []
        for row in rows:
            vec = blob_to_vec(row["embedding"])
            sim = _cosine_similarity(query_vec, vec)
            scored.append({
                "model_id": row["model_id"],
                "signal_type": row["signal_type"],
                "score": sim,
            })
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    # -- Tendency guidance retrieval -----------------------------------------

    def rank_tendencies(
        self,
        query_vec: list[float],
        top_k: int = 10,
    ) -> list[dict]:
        """Rank tendencies by cosine similarity to query vector.

        Returns list of {tendency_id, score} sorted descending.
        """
        conn = self._connect()
        if conn is None:
            return []
        try:
            rows = conn.execute(
                "SELECT tendency_id, embedding FROM tendency_guidance"
            ).fetchall()
        except Exception:
            _LOGGER.warning("rank_tendencies: query failed", exc_info=True)
            return []

        scored = []
        for row in rows:
            vec = blob_to_vec(row["embedding"])
            sim = _cosine_similarity(query_vec, vec)
            scored.append({
                "tendency_id": row["tendency_id"],
                "score": sim,
            })
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    # -- Chunk retrieval (Wave 2+3 intervention content) ----------------------

    def rank_chunks(
        self,
        query_vec: list[float],
        chunk_types: tuple[str, ...] = ("failure_mode", "heuristic", "premortem"),
        top_k: int = 50,
    ) -> list[dict]:
        """Rank intervention chunks by cosine similarity to query vector.

        Returns list of {model_id, chunk_type, chunk_index, chunk_text, score}
        sorted descending by score.
        """
        conn = self._connect()
        if conn is None:
            return []
        try:
            placeholders = ",".join("?" for _ in chunk_types)
            rows = conn.execute(
                f"SELECT model_id, chunk_type, chunk_index, chunk_text, embedding "
                f"FROM chunk_embeddings WHERE chunk_type IN ({placeholders})",
                chunk_types,
            ).fetchall()
        except Exception:
            _LOGGER.warning("rank_chunks: query failed", exc_info=True)
            return []

        scored = []
        for row in rows:
            vec = blob_to_vec(row["embedding"])
            sim = _cosine_similarity(query_vec, vec)
            scored.append({
                "model_id": row["model_id"],
                "chunk_type": row["chunk_type"],
                "chunk_index": row["chunk_index"],
                "chunk_text": row["chunk_text"],
                "score": sim,
            })
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def chunk_embeddings_available(self) -> bool:
        """Check if chunk_embeddings table has data."""
        conn = self._connect()
        if conn is None:
            return False
        try:
            row = conn.execute("SELECT COUNT(*) FROM chunk_embeddings").fetchone()
            return row[0] > 0
        except Exception:
            return False

    # -- Cleanup -------------------------------------------------------------

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def __del__(self):
        self.close()
