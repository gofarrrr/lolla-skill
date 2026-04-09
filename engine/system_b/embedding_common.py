"""Shared helpers for embedding indexer and retriever.

Vector serialization uses float32 array format for SQLite BLOB storage.
Content hashing uses SHA256 truncated to 16 hex chars for change detection.
"""
from __future__ import annotations

import array
import hashlib


def vec_to_blob(vec: list[float]) -> bytes:
    buf = array.array("f", vec)
    return buf.tobytes()


def blob_to_vec(blob: bytes) -> list[float]:
    buf = array.array("f")
    buf.frombytes(blob)
    return list(buf)


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
