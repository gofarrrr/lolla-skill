"""Activation match — reasoning-shape tiebreaker for graph traversal.

Phase 3 infrastructure (Section 14 of deep-graph-enrichment-handover.md).
This module is shipped unused in Commit A — `RelationGraph.neighborhood()`
does NOT call it yet. Commit B wires it in as a near-tie tiebreaker inside
a narrow ε window; the default path stays byte-identical outside that
window.

What this module does
---------------------
Given a reasoning-shape input (produced by one of the four lanes) and a
set of candidate graph edges, compute cosine similarity between the input's
reasoning-shape prose and each edge's pre-built `activation_condition`
embedding. Return per-candidate similarity scores; the caller decides what
to do with them (tiebreak, blend, abstain).

Design invariants — do not relax without revisiting Section 14b
---------------------------------------------------------------

1. **Typed input enforcement.** `match_activation()` accepts ONLY these
   five types as reasoning input: `FingerprintPayload`, `TriggeredTendency`,
   `TendencyRef`, `FrameRoute`, `DimensionRoute`. Any other type — including
   raw `str` — raises `TypeError`. This is the structural defense against
   facts leaking into the reasoning path. The type check is at the API
   boundary, not deep inside; a caller cannot sneak a string past it.

2. **Facts/Reasoning Break.** The adapter functions below extract ONLY
   reasoning-shape prose from each type. They must NEVER touch:
       - `FingerprintMove.evidence_quotes` (verbatim conversation text)
       - `ExtractedFrameElement.evidence_quote` (frame-layer quote)
       - `DetectedDimension.coverage_evidence` (quoted answer material)
   `FrameRoute` and `DimensionRoute` are already facts-clean by structure
   (they carry pattern/dimension identifiers, not extracted prose) — the
   facts live one layer up in their detection types. A test in
   `tests/test_activation_matcher.py` asserts each adapter drops its
   facts.

3. **Graceful degradation.** Missing API key, missing embeddings.db,
   missing per-edge backfill row, or empty reasoning prose — all return
   an empty result tuple. The matcher never raises during query time
   (type validation is the sole exception; that is a programmer error).

4. **No opinionated thresholds inside.** This module does not decide what
   "close enough to win" means, or what "too noisy to trust" means. Those
   thresholds (ε, noise floor) are set at the caller from fixture data in
   Commit B. Keeping them out of the matcher keeps the matcher reusable
   across tiebreaker, ranking blend, and anti-echo phases.
"""
from __future__ import annotations

import logging
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence, Union

from .companion import FingerprintPayload
from .frame_pressure import FrameRoute
from .pipeline import TriggeredTendency
from .structural_coverage import DimensionRoute
from .tendency_catalog import TendencyRef
from .edge_activation_store import get_edge_embedding

_LOGGER = logging.getLogger("system_b.activation_matcher")

# The public type contract. Any caller passing outside this union triggers
# a TypeError. Kept as a tuple (not `typing.Union`) so `isinstance()` works
# directly on Python 3.9+.
ReasoningShapeInput = Union[
    FingerprintPayload,
    TriggeredTendency,
    TendencyRef,
    FrameRoute,
    DimensionRoute,
]
_SUPPORTED_TYPES: tuple[type, ...] = (
    FingerprintPayload,
    TriggeredTendency,
    TendencyRef,
    FrameRoute,
    DimensionRoute,
)


@dataclass(frozen=True)
class ActivationMatchResult:
    """Per-candidate similarity. Callers rank these themselves."""

    source_model_id: str
    target_model_id: str
    edge_type: str
    similarity: float  # cosine similarity in [-1.0, 1.0]


# ---------------------------------------------------------------------------
# Facts-free adapters: reasoning-shape prose extraction per input type
# ---------------------------------------------------------------------------

def _prose_from_fingerprint(fp: FingerprintPayload) -> str:
    """Extract validated reasoning moves and their rationales. Drops
    evidence_quotes (facts) entirely."""
    parts: list[str] = []
    for move in fp.validated:  # dropped/raw moves are upstream noise
        if move.reasoning_move:
            parts.append(move.reasoning_move)
        if move.evidence_rationale:
            parts.append(move.evidence_rationale)
        # INTENTIONAL: move.evidence_quotes is NOT read.
    return " ".join(p.strip() for p in parts if p.strip())


def _prose_from_triggered_tendency(t: TriggeredTendency) -> str:
    """A TriggeredTendency on its own carries only an id + source. That's
    thin but facts-free. Callers wanting richer prose for a tendency should
    pass `TendencyRef` instead."""
    return (t.tendency_id or "").replace("-", " ").replace("_", " ")


def _prose_from_tendency_ref(t: TendencyRef) -> str:
    """Display name + description. Both are curator-authored taxonomy."""
    parts = [t.display_name, t.description]
    return " ".join(p.strip() for p in parts if p and p.strip())


def _prose_from_frame_route(r: FrameRoute) -> str:
    """Frame pattern identifier only. Extracted element text (facts) lives
    on `ExtractedFrameElement`, not on `FrameRoute`."""
    return (r.frame_pattern or "").replace("_", " ").replace("-", " ")


def _prose_from_dimension_route(r: DimensionRoute) -> str:
    """Dimension identifier + human name. Detection prose (coverage_evidence,
    materiality_note) lives on `DetectedDimension`, not on `DimensionRoute`."""
    return (r.dimension_name or r.dimension_id or "").strip()


def _to_reasoning_prose(x: ReasoningShapeInput) -> str:
    if isinstance(x, FingerprintPayload):
        return _prose_from_fingerprint(x)
    if isinstance(x, TriggeredTendency):
        return _prose_from_triggered_tendency(x)
    if isinstance(x, TendencyRef):
        return _prose_from_tendency_ref(x)
    if isinstance(x, FrameRoute):
        return _prose_from_frame_route(x)
    if isinstance(x, DimensionRoute):
        return _prose_from_dimension_route(x)
    # isinstance() guard in the public API should have caught this.
    raise TypeError(
        f"activation_matcher: unsupported reasoning-shape type {type(x).__name__}"
    )


# ---------------------------------------------------------------------------
# Embedder — dependency-injectable so tests don't hit the network
# ---------------------------------------------------------------------------

Embedder = Callable[[str, str], "list[float] | None"]


def _default_embedder(text: str, api_key: str) -> list[float] | None:
    """Real embedder — calls OpenAI via embedding_retriever. Imported lazily
    so tests that only need the adapters don't pull urllib."""
    if not api_key or not text.strip():
        return None
    from .embedding_retriever import embed_query

    try:
        return embed_query(text, api_key)
    except Exception:  # pragma: no cover - defensive
        _LOGGER.debug("_default_embedder: embed_query raised", exc_info=True)
        return None


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
# Public entry point
# ---------------------------------------------------------------------------

def match_activation(
    reasoning_input: ReasoningShapeInput,
    candidate_edges: Sequence[tuple[str, str, str]],
    *,
    db_path: Path | str,
    api_key: str | None = None,
    embedder: Embedder | None = None,
) -> tuple[ActivationMatchResult, ...]:
    """Return per-candidate cosine similarity scores.

    Parameters
    ----------
    reasoning_input
        One of the five supported reasoning-shape types. A raw `str` or any
        other type raises `TypeError`. This is the structural defense
        against facts entering the reasoning path.
    candidate_edges
        Sequence of `(source_model_id, target_model_id, edge_type)` tuples
        identifying which graph edges to score. Typically the caller passes
        the top-K candidates that are near-tied in fan-adjusted affinity.
    db_path
        Path to embeddings.db where the per-edge activation_condition
        embeddings live. Built by
        `scripts/build_edge_activation_embeddings.py`.
    api_key
        OpenAI API key. If missing and no `embedder` is injected, the
        function returns an empty tuple (graceful degradation).
    embedder
        Optional override for the embedding function — used by tests to
        inject canned vectors without network calls. Signature must be
        `(text, api_key) -> list[float] | None`.

    Returns
    -------
    tuple[ActivationMatchResult, ...]
        One result per candidate edge that had a backfilled embedding.
        Edges without a backfill row are silently dropped — caller should
        infer "no signal" and abstain. Empty tuple on any degradation
        condition (missing prose, missing DB, embedding failure).

    Raises
    ------
    TypeError
        If `reasoning_input` is not one of the five supported types.
        Programmer-error contract; never caught at runtime.
    """
    if not isinstance(reasoning_input, _SUPPORTED_TYPES):
        raise TypeError(
            "match_activation: reasoning_input must be one of "
            "(FingerprintPayload, TriggeredTendency, TendencyRef, "
            "FrameRoute, DimensionRoute); got "
            f"{type(reasoning_input).__name__}"
        )

    prose = _to_reasoning_prose(reasoning_input)
    if not prose:
        return ()

    if embedder is None:
        embedder = _default_embedder
    resolved_key = api_key if api_key is not None else os.environ.get("OPENAI_API_KEY", "")

    query_vec = embedder(prose, resolved_key)
    if not query_vec:
        return ()

    results: list[ActivationMatchResult] = []
    for source, target, edge_type in candidate_edges:
        edge_vec = get_edge_embedding(
            db_path,
            source_model_id=source,
            target_model_id=target,
            edge_type=edge_type,
        )
        if edge_vec is None:
            continue  # No backfill — caller infers "no signal" for this edge
        sim = _cosine_similarity(query_vec, edge_vec)
        results.append(
            ActivationMatchResult(
                source_model_id=source,
                target_model_id=target,
                edge_type=edge_type,
                similarity=sim,
            )
        )
    return tuple(results)
