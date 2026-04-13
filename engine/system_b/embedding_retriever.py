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
EXPANSION_MODEL = "gpt-4o-mini"
EXPANSION_ENDPOINT = "https://api.openai.com/v1/chat/completions"


# ---------------------------------------------------------------------------
# Query expansion
# ---------------------------------------------------------------------------
def _expand_query(
    query_text: str,
    api_key: str,
    model_names: list[str],
) -> list[str]:
    """Expand a query into 2 alternative phrasings using domain vocabulary.

    Returns the variant texts (not including the original).
    Returns empty list on failure (graceful degradation).
    """
    if not api_key or not model_names:
        return []
    # Skip very short queries — not enough signal to expand
    if len(query_text.split()) < 5:
        return []
    vocab_hint = ", ".join(model_names)
    system_prompt = (
        "You expand decision queries for a mental model retrieval system. "
        "Generate 2 alternative search queries from different angles "
        "(cognitive biases vs strategic risks). Use specific model names "
        "from this list when relevant:\n"
        f"{vocab_hint}\n\n"
        "Return ONLY a JSON array of 2 strings, no markdown fences."
    )
    try:
        payload = json.dumps({
            "model": EXPANSION_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query_text},
            ],
            "max_tokens": 250,
            "temperature": 0.7,
        }).encode("utf-8")
        req = urllib.request.Request(
            EXPANSION_ENDPOINT,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        content = body["choices"][0]["message"]["content"].strip()
        # Strip markdown fences if present
        if content.startswith("```"):
            lines = content.split("\n")
            lines = [ln for ln in lines if not ln.startswith("```")]
            content = "\n".join(lines)
        variants = json.loads(content)
        if isinstance(variants, list):
            return [str(v) for v in variants if v][:2]
        return []
    except Exception:
        _LOGGER.debug("_expand_query: failed, using original query only", exc_info=True)
        return []


def _embed_batch(texts: list[str], api_key: str) -> list[list[float]] | None:
    """Embed multiple texts in a single API call. Returns None on failure."""
    if not texts:
        return []
    try:
        payload = json.dumps({
            "model": EMBEDDING_MODEL,
            "input": texts,
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
        data = sorted(body["data"], key=lambda d: d["index"])
        return [d["embedding"] for d in data]
    except Exception:
        _LOGGER.debug("_embed_batch: API call failed", exc_info=True)
        return None


def _rrf_fuse(
    rankings: list[list[dict]],
    id_key: str = "model_id",
    k: int = 60,
) -> list[dict]:
    """Reciprocal Rank Fusion across multiple ranked lists.

    Each ranking is a list of dicts with id_key and 'score'.
    Returns fused list sorted by RRF score descending.
    """
    scores: dict[str, float] = {}
    for ranking in rankings:
        # Deduplicate by id within each ranking (take best score position)
        seen: dict[str, int] = {}
        for rank_pos, hit in enumerate(ranking):
            item_id = hit[id_key]
            if item_id not in seen:
                seen[item_id] = rank_pos
        for item_id, rank_pos in seen.items():
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (k + rank_pos)
    result = [
        {id_key: item_id, "score": score}
        for item_id, score in sorted(scores.items(), key=lambda x: -x[1])
    ]
    return result


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

    # -- Query expansion + RRF ranking -------------------------------------

    def _model_names(self) -> list[str]:
        """Get sorted unique model names from model_signals table."""
        conn = self._connect()
        if conn is None:
            return []
        try:
            rows = conn.execute(
                "SELECT DISTINCT model_id FROM model_signals ORDER BY model_id"
            ).fetchall()
            return [row["model_id"] for row in rows]
        except Exception:
            return []

    def rank_models_expanded(
        self,
        query_text: str,
        api_key: str,
        signal_types: tuple[str, ...] = ("select_when", "danger_when"),
        top_k: int = 30,
    ) -> list[dict]:
        """Rank models using query expansion + RRF for better recall.

        Expands the query into 2 domain-vocabulary variants via a cheap LLM,
        embeds all 3 texts (original cached + 2 variants batched), ranks each
        against model signals, and fuses via Reciprocal Rank Fusion.

        Falls back to single-vector ranking on any failure.
        """
        # Original vector (may already be cached)
        query_vec = self.embed_and_cache(query_text, api_key)
        if query_vec is None:
            return []
        original_ranking = self.rank_models(query_vec, signal_types=signal_types, top_k=top_k)

        # Expand query
        model_names = self._model_names()
        variants = _expand_query(query_text, api_key, model_names)
        if not variants:
            return original_ranking

        # Embed variants (batch call — nearly same latency as single)
        variant_vecs = _embed_batch(variants, api_key)
        if not variant_vecs:
            return original_ranking

        # Cache variant embeddings for potential reuse by other lanes
        for text, vec in zip(variants, variant_vecs):
            h = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
            if h not in self._query_cache:
                self._query_cache[h] = vec

        # Rank with each variant
        all_rankings = [original_ranking]
        for vec in variant_vecs:
            all_rankings.append(self.rank_models(vec, signal_types=signal_types, top_k=top_k))

        # Fuse via RRF
        return _rrf_fuse(all_rankings, id_key="model_id")[:top_k]

    def rank_chunks_expanded(
        self,
        query_text: str,
        api_key: str,
        chunk_types: tuple[str, ...] = ("failure_mode", "heuristic", "premortem"),
        top_k: int = 50,
    ) -> list[dict]:
        """Rank chunks using query expansion + RRF for better recall.

        Same approach as rank_models_expanded but over chunk_embeddings.
        Falls back to single-vector ranking on any failure.
        """
        query_vec = self.embed_and_cache(query_text, api_key)
        if query_vec is None:
            return []
        original_ranking = self.rank_chunks(query_vec, chunk_types=chunk_types, top_k=top_k)

        model_names = self._model_names()
        variants = _expand_query(query_text, api_key, model_names)
        if not variants:
            return original_ranking

        variant_vecs = _embed_batch(variants, api_key)
        if not variant_vecs:
            return original_ranking

        for text, vec in zip(variants, variant_vecs):
            h = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
            if h not in self._query_cache:
                self._query_cache[h] = vec

        all_rankings = [original_ranking]
        for vec in variant_vecs:
            all_rankings.append(self.rank_chunks(vec, chunk_types=chunk_types, top_k=top_k))

        # RRF needs a unique id — combine model_id + chunk_index
        # Rebuild with composite key, then restore
        keyed_rankings: list[list[dict]] = []
        for ranking in all_rankings:
            keyed = []
            for hit in ranking:
                keyed.append({
                    **hit,
                    "_fuse_key": f"{hit['model_id']}::{hit['chunk_type']}::{hit['chunk_index']}",
                })
            keyed_rankings.append(keyed)

        fused = _rrf_fuse(keyed_rankings, id_key="_fuse_key")

        # Restore original structure from first ranking that has each key
        lookup: dict[str, dict] = {}
        for ranking in all_rankings:
            for hit in ranking:
                fk = f"{hit['model_id']}::{hit['chunk_type']}::{hit['chunk_index']}"
                if fk not in lookup:
                    lookup[fk] = hit

        result = []
        for fused_hit in fused[:top_k]:
            orig = lookup.get(fused_hit["_fuse_key"])
            if orig:
                result.append({**orig, "score": fused_hit["score"]})
        return result

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

    def score_candidate_chunks(
        self,
        query_vec: list[float],
        candidates: list[tuple[str, str]],
    ) -> dict[tuple[str, str], float]:
        """Score specific candidate chunks by cosine similarity.

        Args:
            query_vec: Pre-computed query embedding vector.
            candidates: List of (model_id, chunk_text_prefix_80) pairs to score.

        Returns:
            {(model_id, text_prefix): cosine_similarity} for candidates found
            in the DB. Missing candidates are omitted (caller treats as 0.0).
        """
        if not candidates:
            return {}
        conn = self._connect()
        if conn is None:
            return {}

        # Build lookup set for fast matching
        wanted = set(candidates)
        # Collect unique model_ids to narrow the DB query
        model_ids = list({mid for mid, _ in wanted})

        try:
            placeholders = ",".join("?" for _ in model_ids)
            rows = conn.execute(
                f"SELECT model_id, chunk_type, chunk_text, embedding "
                f"FROM chunk_embeddings WHERE model_id IN ({placeholders})",
                model_ids,
            ).fetchall()
        except Exception:
            _LOGGER.warning("score_candidate_chunks: query failed", exc_info=True)
            return {}

        scores: dict[tuple[str, str], float] = {}
        for row in rows:
            key = (row["model_id"], row["chunk_text"][:80])
            if key in wanted:
                vec = blob_to_vec(row["embedding"])
                sim = _cosine_similarity(query_vec, vec)
                scores[key] = max(scores.get(key, 0.0), sim)
        return scores

    # -- Cleanup -------------------------------------------------------------

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def __del__(self):
        self.close()
