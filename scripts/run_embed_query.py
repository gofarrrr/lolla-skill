#!/usr/bin/env python3
"""
Semantic embedding search for Lolla skill.

Searches pre-computed embedding tables for the most relevant knowledge.

Three search modes:
  1. --mode chunks (default): Search 2,025 intervention chunks (failure modes,
     heuristics, premortems) — for companion recall augmentation.
  2. --mode tendencies: Search 25 tendency guidance vectors — for swiss cheese
     triage augmentation (catches tendencies the LLM scored below threshold).
  3. --mode models: Search 446 model signal vectors (select_when + danger_when)
     — for companion recall augmentation.

Requires OPENAI_API_KEY in environment.

Usage:
    python3 scripts/run_embed_query.py --query "Should we sign this deal?" --mode chunks --top-k 10
    python3 scripts/run_embed_query.py --query "The CEO's confidence..." --mode tendencies --threshold 0.30
    python3 scripts/run_embed_query.py --query "weighing second-order effects" --mode models --top-k 15

Output: JSON list of matches ranked by cosine similarity.
"""

import argparse
import json
import os
import sqlite3
import struct
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_DIM = 3072


def get_embedding(text: str, api_key: str) -> list[float]:
    """Get embedding from OpenAI API. Minimal implementation — no SDK dependency."""
    import urllib.request

    payload = json.dumps({"input": text, "model": EMBEDDING_MODEL}).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/embeddings",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    return data["data"][0]["embedding"]


def decode_embedding(blob: bytes) -> list[float]:
    """Decode a binary embedding blob to list of floats."""
    n = len(blob) // 4
    return list(struct.unpack(f"{n}f", blob))


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = sum(x * x for x in a) ** 0.5
    mag_b = sum(x * x for x in b) ** 0.5
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def search_chunks(query_embedding: list[float], db_path: Path, top_k: int = 10) -> list[dict]:
    """Search chunk embeddings (2,025 intervention chunks)."""
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("SELECT model_id, chunk_type, chunk_index, chunk_text, embedding FROM chunk_embeddings")
    results = []
    for model_id, chunk_type, chunk_index, chunk_text, emb_blob in cur.fetchall():
        sim = cosine_similarity(query_embedding, decode_embedding(emb_blob))
        results.append({
            "model_id": model_id,
            "chunk_type": chunk_type,
            "chunk_index": chunk_index,
            "text": chunk_text,
            "similarity": round(sim, 4),
        })
    conn.close()
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_k]


def search_tendencies(query_embedding: list[float], db_path: Path, threshold: float = 0.30) -> list[dict]:
    """Search tendency guidance vectors (25 entries). Returns hits above threshold."""
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("SELECT tendency_id, guidance_text, embedding FROM tendency_guidance")
    results = []
    for tendency_id, guidance_text, emb_blob in cur.fetchall():
        sim = cosine_similarity(query_embedding, decode_embedding(emb_blob))
        if sim >= threshold:
            results.append({
                "tendency_id": tendency_id,
                "guidance_text": guidance_text,
                "similarity": round(sim, 4),
            })
    conn.close()
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results


def search_models(query_embedding: list[float], db_path: Path, top_k: int = 15) -> list[dict]:
    """Search model signal vectors (446 entries: select_when + danger_when per model)."""
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("SELECT model_id, signal_type, signal_text, embedding FROM model_signals")
    results = []
    for model_id, signal_type, signal_text, emb_blob in cur.fetchall():
        sim = cosine_similarity(query_embedding, decode_embedding(emb_blob))
        results.append({
            "model_id": model_id,
            "signal_type": signal_type,
            "text": signal_text,
            "similarity": round(sim, 4),
        })
    conn.close()
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_k]


def main():
    parser = argparse.ArgumentParser(
        description="Semantic search against knowledge embeddings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  chunks      Search 2,025 intervention chunks (failure modes, heuristics,
              premortems). Use for companion recall augmentation.
  tendencies  Search 25 tendency guidance vectors. Use for swiss cheese triage
              augmentation — catches tendencies the LLM scored below threshold.
              Returns only hits above --threshold (default 0.30).
  models      Search 446 model signal vectors (select_when + danger_when).
              Use for companion recall augmentation alongside keyword matching.

All modes use text-embedding-3-large (3072 dimensions) to match the
pre-computed vectors in embeddings.db.
""",
    )
    parser.add_argument("--query", required=True, help="Text to embed and search against")
    parser.add_argument("--mode", choices=["chunks", "tendencies", "models"], default="chunks",
                        help="Which embedding table to search (default: chunks)")
    parser.add_argument("--top-k", type=int, default=10, help="Number of top results (chunks/models modes)")
    parser.add_argument("--threshold", type=float, default=0.30,
                        help="Minimum similarity for tendency hits (default: 0.30)")
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print(json.dumps({
            "error": "OPENAI_API_KEY not set",
            "fallback": "Use deterministic routing via run_route.py and run_companion.py instead",
        }))
        sys.exit(0)

    db_path = DATA_DIR / "embeddings.db"
    if not db_path.exists():
        print(json.dumps({"error": f"embeddings.db not found at {db_path}"}))
        sys.exit(1)

    query_embedding = get_embedding(args.query, api_key)

    if args.mode == "tendencies":
        results = search_tendencies(query_embedding, db_path, args.threshold)
    elif args.mode == "models":
        results = search_models(query_embedding, db_path, args.top_k)
    else:
        results = search_chunks(query_embedding, db_path, args.top_k)

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
