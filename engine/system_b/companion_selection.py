"""Companion cheat-sheet selection layer.

Takes a fully gathered CompanionCard + a DeltaCard (for anti-echo) and produces
a compact, bounded, provenance-tagged CompanionCheatSheet ready for PM evaluation.

Design doctrine (from plans/companion-cheat-sheet-selection-layer.md):
- Deterministic selector is primary; chunk embeddings are optional reranker
- Compactness budget enforced from day one
- Anti-echo: don't repeat what the DeltaCard already covers
- Hybrid grouping: model anchors with strongest attached chunks
- When chunk embeddings are available, candidates are reranked by semantic
  relevance to the query+answer before budget fill
"""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass

_LOGGER = logging.getLogger("system_b.companion_selection")


# ---------------------------------------------------------------------------
# Contract types
# ---------------------------------------------------------------------------

CHUNK_TYPES = frozenset({
    "identity",
    "failure_mode",
    "heuristic",
    "premortem",
    "ally",
    "antagonist",
    "prerequisite_gap",
})

SOURCE_LAYERS = frozenset({"wave1", "wave2", "wave3", "prerequisite"})


@dataclass(frozen=True)
class ChunkProvenance:
    source_layer: str  # wave1 | wave2 | wave3
    extraction_type: str  # explicit | normalized | unknown
    confidence: str  # high | medium | low | unknown
    relation_target_id: str = ""  # populated for ally/antagonist chunks

    def to_payload(self) -> dict:
        d = {
            "source_layer": self.source_layer,
            "extraction_type": self.extraction_type,
            "confidence": self.confidence,
        }
        if self.relation_target_id:
            d["relation_target_id"] = self.relation_target_id
        return d


@dataclass(frozen=True)
class CheatSheetChunk:
    """One typed, provenance-tagged chunk selected for the companion cheat sheet."""

    chunk_type: str
    source_model_id: str
    text: str
    provenance: ChunkProvenance
    affinity_rationale: str = ""
    activation_condition: str = ""

    def to_payload(self) -> dict:
        d = {
            "chunk_type": self.chunk_type,
            "source_model_id": self.source_model_id,
            "text": self.text,
            "provenance": self.provenance.to_payload(),
        }
        if self.affinity_rationale:
            d["affinity_rationale"] = self.affinity_rationale
        if self.activation_condition:
            d["activation_condition"] = self.activation_condition
        return d


@dataclass(frozen=True)
class ModelAnchor:
    """A detected model with its selected companion chunks."""

    model_id: str
    display_name: str
    chunks: tuple[CheatSheetChunk, ...]
    presence_mode: str = ""  # executed | violated
    evidence_quote: str = ""
    presence_explanation: str = ""

    def to_payload(self) -> dict:
        d = {
            "model_id": self.model_id,
            "display_name": self.display_name,
            "chunks": [c.to_payload() for c in self.chunks],
        }
        if self.presence_mode:
            d["presence_mode"] = self.presence_mode
        if self.evidence_quote:
            d["evidence_quote"] = self.evidence_quote
        if self.presence_explanation:
            d["presence_explanation"] = self.presence_explanation
        return d


@dataclass(frozen=True)
class CompanionCheatSheet:
    """The final standalone companion packet."""

    anchors: tuple[ModelAnchor, ...]
    total_chunk_count: int
    budget_max: int
    anti_echo_model_ids: frozenset[str]
    reranker_active: bool = False
    chunks_above_relevance_floor: int = 0
    mean_relevance_score: float = 0.0

    def to_payload(self) -> dict:
        d = {
            "anchors": [a.to_payload() for a in self.anchors],
            "total_chunk_count": self.total_chunk_count,
            "budget_max": self.budget_max,
            "anti_echo_model_ids": sorted(self.anti_echo_model_ids),
        }
        if self.reranker_active:
            d["reranker"] = {
                "active": True,
                "chunks_above_relevance_floor": self.chunks_above_relevance_floor,
                "mean_relevance_score": round(self.mean_relevance_score, 4),
            }
        return d


# ---------------------------------------------------------------------------
# Budget defaults
# ---------------------------------------------------------------------------

DEFAULT_BUDGET_MAX = 20
DEFAULT_PER_MODEL_CAP = 5
DEFAULT_PER_TYPE_CAP = 5


# ---------------------------------------------------------------------------
# Selector
# ---------------------------------------------------------------------------

def _confidence_rank(confidence: str) -> int:
    return {"high": 0, "medium": 1, "low": 2}.get(confidence, 3)


def _extraction_rank(extraction_type: str) -> int:
    return 0 if extraction_type == "explicit" else 1


def _chunk_sort_key(chunk: CheatSheetChunk) -> tuple[int, int, int, str]:
    """Sort chunks by type priority, confidence, extraction type, then text.

    Used as fallback when no embedding reranker is available.
    """
    type_priority = {
        "failure_mode": 0,
        "prerequisite_gap": 1,
        "premortem": 2,
        "antagonist": 3,
        "heuristic": 4,
        "ally": 5,
        "identity": 6,
    }
    return (
        type_priority.get(chunk.chunk_type, 9),
        _confidence_rank(chunk.provenance.confidence),
        _extraction_rank(chunk.provenance.extraction_type),
        chunk.text[:40],
    )


# ---------------------------------------------------------------------------
# Embedding-based chunk reranker
# ---------------------------------------------------------------------------

# Minimum relevance score to consider a chunk for reranking boost.
# Below this, the chunk falls back to the deterministic type-priority sort.
_RELEVANCE_FLOOR = 0.25

# Weight given to semantic relevance vs. type priority.
# 0.0 = pure type priority (legacy), 1.0 = pure relevance.
_RELEVANCE_WEIGHT = 0.6


def _build_chunk_relevance_scores(
    query_text: str,
    embedding_retriever,
    embedding_api_key: str,
    candidates: list[CheatSheetChunk],
) -> dict[tuple[str, str], float]:
    """Build a {(model_id, chunk_text_prefix) -> cosine_similarity} map.

    Scores the actual candidate chunks against the query embedding using
    direct cosine similarity from the chunk_embeddings DB.

    Returns empty dict on failure (graceful degradation to deterministic sort).
    """
    if embedding_retriever is None or not embedding_api_key or not candidates:
        return {}
    try:
        if not embedding_retriever.chunk_embeddings_available():
            return {}
        query_vec = embedding_retriever.embed_and_cache(query_text, embedding_api_key)
        if query_vec is None:
            return {}
        # Build candidate keys for targeted scoring
        candidate_keys = [
            (c.source_model_id, c.text[:80]) for c in candidates
        ]
        return embedding_retriever.score_candidate_chunks(query_vec, candidate_keys)
    except Exception:
        _LOGGER.warning("chunk reranker: failed, falling back to deterministic sort",
                        exc_info=True)
        return {}


def _relevance_score_for_chunk(
    chunk: CheatSheetChunk,
    scores: dict[tuple[str, str], float],
) -> float:
    """Look up the best relevance score for a chunk. Returns 0.0 if not found."""
    if not scores:
        return 0.0
    # Direct match by (model_id, text prefix)
    key = (chunk.source_model_id, chunk.text[:80])
    if key in scores:
        return scores[key]
    # Fuzzy: check all keys for this model and find best partial match
    best = 0.0
    for (mid, prefix), score in scores.items():
        if mid != chunk.source_model_id:
            continue
        # Check if the chunk text starts with the same content
        if chunk.text[:60] == prefix[:60]:
            best = max(best, score)
    return best


def _reranked_sort_key(
    chunk: CheatSheetChunk,
    scores: dict[tuple[str, str], float],
) -> tuple[float, int, int, str]:
    """Sort key that blends semantic relevance with type priority.

    Returns a tuple where lower is better (consistent with _chunk_sort_key).
    The first element is a blended score: high relevance → low sort value.
    """
    type_priority = {
        "failure_mode": 0,
        "prerequisite_gap": 1,
        "premortem": 2,
        "antagonist": 3,
        "heuristic": 4,
        "ally": 5,
        "identity": 6,
    }
    type_rank = type_priority.get(chunk.chunk_type, 9)
    relevance = _relevance_score_for_chunk(chunk, scores)

    if relevance >= _RELEVANCE_FLOOR:
        # Blend: convert relevance (0-1, higher=better) to sort key (lower=better)
        # and mix with normalized type priority (0-5 → 0-1)
        relevance_component = 1.0 - relevance  # invert: high relevance → low value
        priority_component = type_rank / 5.0
        blended = (_RELEVANCE_WEIGHT * relevance_component
                   + (1.0 - _RELEVANCE_WEIGHT) * priority_component)
    else:
        # Below floor: pure type priority, penalized to sort after relevant chunks
        blended = 1.0 + (type_rank / 5.0)

    return (
        blended,
        _confidence_rank(chunk.provenance.confidence),
        _extraction_rank(chunk.provenance.extraction_type),
        chunk.text[:40],
    )


# Chunk types that echo the DeltaCard when the same model appears in both.
# Heuristic hints restate "how to use this model" which the DeltaCard already
# covers via next_moves. Identity chunks are KEPT because the companion lane's
# identity ("you're already using this model — here's when it's dangerous")
# is different from the delta card's introduction ("you should start using this").
# Failure modes, premortems, and antagonists add genuinely different material.
_ECHO_TYPES = frozenset({"heuristic"})


def _gather_candidates(companion_card, delta_card) -> list[CheatSheetChunk]:
    """Convert CompanionCard chunks into a flat candidate list with anti-echo."""
    from .companion import CompanionCard
    from .pipeline import DeltaCard

    # Determine which model_ids are already covered by DeltaCard findings
    delta_model_ids: set[str] = set()
    if delta_card is not None and hasattr(delta_card, "findings"):
        for finding in delta_card.findings:
            if hasattr(finding, "primary_model_id") and finding.primary_model_id:
                delta_model_ids.add(finding.primary_model_id)
            if hasattr(finding, "selected_model_ids"):
                for mid in finding.selected_model_ids:
                    if mid:
                        delta_model_ids.add(mid)

    candidates: list[CheatSheetChunk] = []

    # Identity chunks (Wave 1)
    for chunk in companion_card.identity_chunks:
        # Compact identity into a single text line
        parts = []
        if chunk.select_when:
            parts.append(f"Select when: {chunk.select_when[0]}")
        if chunk.danger_when:
            parts.append(f"Danger when: {chunk.danger_when[0]}")
        if chunk.reasoning_types:
            parts.append(f"Reasoning: {', '.join(chunk.reasoning_types)}")
        text = " | ".join(parts) if parts else chunk.display_name
        candidates.append(CheatSheetChunk(
            chunk_type="identity",
            source_model_id=chunk.model_id,
            text=text,
            provenance=ChunkProvenance(
                source_layer="wave1",
                extraction_type="explicit",
                confidence="high",
            ),
        ))

    # Failure hints (Wave 2)
    for hint in companion_card.failure_hints:
        candidates.append(CheatSheetChunk(
            chunk_type="failure_mode",
            source_model_id=hint.source_model_id,
            text=hint.text,
            provenance=ChunkProvenance(
                source_layer="wave2",
                extraction_type=hint.extraction_type,
                confidence=hint.confidence,
            ),
        ))

    # Heuristic hints (Wave 2)
    for hint in companion_card.heuristic_hints:
        candidates.append(CheatSheetChunk(
            chunk_type="heuristic",
            source_model_id=hint.source_model_id,
            text=hint.text,
            provenance=ChunkProvenance(
                source_layer="wave2",
                extraction_type=hint.extraction_type,
                confidence=hint.confidence,
            ),
        ))

    # Premortem hints (Wave 2)
    for hint in companion_card.premortem_hints:
        candidates.append(CheatSheetChunk(
            chunk_type="premortem",
            source_model_id=hint.source_model_id,
            text=hint.text,
            provenance=ChunkProvenance(
                source_layer="wave2",
                extraction_type=hint.extraction_type,
                confidence=hint.confidence,
            ),
        ))

    # Relation expansions (Wave 3)
    for exp in companion_card.expansions:
        chunk_type = "antagonist" if exp.relation_type in ("antagonist", "tension") else "ally"
        candidates.append(CheatSheetChunk(
            chunk_type=chunk_type,
            source_model_id=exp.source_model_id,
            text=f"{exp.model_name}: {exp.substrate_chunk}",
            provenance=ChunkProvenance(
                source_layer="wave3",
                extraction_type="explicit",
                confidence="high",
                relation_target_id=exp.model_id,
            ),
            affinity_rationale=exp.affinity_rationale,
            activation_condition=exp.activation_condition,
        ))

    # Anti-echo: for models already in DeltaCard, drop echo types
    if delta_model_ids:
        candidates = [
            c for c in candidates
            if not (c.source_model_id in delta_model_ids and c.chunk_type in _ECHO_TYPES)
        ]

    return candidates


def _inject_prerequisite_gaps(
    candidates: list[CheatSheetChunk],
    companion_card,
    prerequisite_edges: list[dict[str, str]],
) -> list[CheatSheetChunk]:
    """Generate prerequisite_gap chunks for detected models missing prerequisites.

    For each detected model, check if any of its prerequisite models are also
    detected.  When a prerequisite is missing, generate a gap chunk attributed
    to the dependent model so the cheat-sheet can surface the gap.

    Pure, deterministic, no LLM calls.
    """
    if not prerequisite_edges:
        return candidates

    detected_ids = {dm.model_id for dm in companion_card.detected_models}
    if not detected_ids:
        return candidates

    # Build lookup: dependent_model_id → list of prerequisite edges
    deps: dict[str, list[dict[str, str]]] = {}
    for edge in prerequisite_edges:
        deps.setdefault(edge["dependent"], []).append(edge)

    gap_chunks: list[CheatSheetChunk] = []
    for model_id in sorted(detected_ids):
        for edge in deps.get(model_id, []):
            prereq_id = edge["prerequisite"]
            if prereq_id in detected_ids:
                continue  # prerequisite is present, no gap
            rationale = edge.get("rationale", "")
            dep_type = edge.get("dependency_type", "requires")
            text = (
                f"This model depends on {prereq_id} ({dep_type}), "
                f"which is not active in the answer. {rationale}"
            )
            gap_chunks.append(CheatSheetChunk(
                chunk_type="prerequisite_gap",
                source_model_id=model_id,
                text=text,
                provenance=ChunkProvenance(
                    source_layer="prerequisite",
                    extraction_type="explicit",
                    confidence=edge.get("confidence", "high"),
                ),
            ))

    if gap_chunks:
        _LOGGER.debug("prerequisite gaps: %d gaps for %d detected models",
                       len(gap_chunks), len(detected_ids))
    return candidates + gap_chunks


def _tokenize_for_dedup(text: str) -> set[str]:
    import re
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) >= 3}


def _texts_overlap(a: str, b: str) -> bool:
    """Return True if two texts share substantial content (>= 70% token overlap)."""
    tokens_a = _tokenize_for_dedup(a)
    tokens_b = _tokenize_for_dedup(b)
    if not tokens_a or not tokens_b:
        return False
    overlap = len(tokens_a & tokens_b)
    return overlap / min(len(tokens_a), len(tokens_b)) >= 0.8


def _deduplicate(candidates: list[CheatSheetChunk]) -> list[CheatSheetChunk]:
    """Remove chunks with substantially overlapping text."""
    if not candidates:
        return []
    deduped: list[CheatSheetChunk] = []
    for chunk in candidates:
        if any(_texts_overlap(chunk.text, existing.text) for existing in deduped):
            continue
        deduped.append(chunk)
    return deduped


def select_companion_cheat_sheet(
    companion_card,
    delta_card=None,
    *,
    budget_max: int = DEFAULT_BUDGET_MAX,
    per_model_cap: int = DEFAULT_PER_MODEL_CAP,
    per_type_cap: int = DEFAULT_PER_TYPE_CAP,
    query_text: str = "",
    embedding_retriever=None,
    embedding_api_key: str = "",
    prerequisite_edges: list[dict[str, str]] | None = None,
) -> CompanionCheatSheet:
    """Produce a bounded, anti-echo companion cheat sheet from gathered material.

    Args:
        companion_card: A fully gathered CompanionCard.
        delta_card: The DeltaCard from the structural pressure lane (for anti-echo).
        budget_max: Maximum total chunks in the cheat sheet.
        per_model_cap: Maximum chunks per model anchor.
        per_type_cap: Maximum chunks of any single type globally.
        query_text: Combined query+answer text for semantic reranking.
        embedding_retriever: EmbeddingRetriever with chunk_embeddings table.
        embedding_api_key: OpenAI API key for query embedding.
    """
    # Determine anti-echo model ids
    delta_model_ids: set[str] = set()
    if delta_card is not None and hasattr(delta_card, "findings"):
        for finding in delta_card.findings:
            if hasattr(finding, "primary_model_id") and finding.primary_model_id:
                delta_model_ids.add(finding.primary_model_id)
            if hasattr(finding, "selected_model_ids"):
                for mid in finding.selected_model_ids:
                    if mid:
                        delta_model_ids.add(mid)

    # Step 1: Gather and anti-echo filter
    candidates = _gather_candidates(companion_card, delta_card)

    # Step 1b: Inject prerequisite gap chunks (deterministic, no LLM)
    candidates = _inject_prerequisite_gaps(
        candidates, companion_card, prerequisite_edges or [],
    )

    # Step 2: Deduplicate
    candidates = _deduplicate(candidates)

    # Step 3: Sort by quality — use embedding reranker if available
    relevance_scores = _build_chunk_relevance_scores(
        query_text, embedding_retriever, embedding_api_key, candidates,
    ) if query_text else {}

    if relevance_scores:
        _LOGGER.debug("chunk reranker: scoring %d candidates against %d indexed chunks",
                       len(candidates), len(relevance_scores))
        candidates.sort(key=lambda c: _reranked_sort_key(c, relevance_scores))
    else:
        candidates.sort(key=_chunk_sort_key)

    # Step 4: Group by model
    by_model: dict[str, list[CheatSheetChunk]] = {}
    for chunk in candidates:
        by_model.setdefault(chunk.source_model_id, []).append(chunk)

    # Step 5: Two-pass selection (diversity first, then depth)
    type_counts: Counter[str] = Counter()
    model_counts: Counter[str] = Counter()
    selected: list[CheatSheetChunk] = []
    used: set[tuple[str, int]] = set()  # (model_id, index)
    model_ids = list(by_model.keys())

    # Pass 1 — Type diversity: guarantee one chunk of each available type.
    # Pick the best candidate for each type (first in priority-sorted order).
    # Spread across models round-robin so no single model dominates Pass 1.
    # Per-model cap is respected — if a model is full, try the next model.
    all_types_by_priority = ["failure_mode", "prerequisite_gap", "premortem", "antagonist", "heuristic", "ally", "identity"]
    for chunk_type in all_types_by_priority:
        if len(selected) >= budget_max:
            break
        # Find the first unused chunk of this type across models (round-robin order)
        for model_id in model_ids:
            if model_counts[model_id] >= per_model_cap:
                continue
            model_chunks = by_model[model_id]
            for idx, chunk in enumerate(model_chunks):
                key = (model_id, idx)
                if key in used:
                    continue
                if chunk.chunk_type != chunk_type:
                    continue
                selected.append(chunk)
                used.add(key)
                type_counts[chunk.chunk_type] += 1
                model_counts[model_id] += 1
                break
            else:
                continue
            break  # got one for this type, move to next type

    # Pass 2 — Breadth and depth: fill remaining budget with round-robin
    # across models, respecting per-model and per-type caps.
    if len(selected) < budget_max:
        max_rounds = max((len(v) for v in by_model.values()), default=0)
        for round_idx in range(max_rounds):
            for model_id in model_ids:
                if len(selected) >= budget_max:
                    break
                if model_counts[model_id] >= per_model_cap:
                    continue
                model_chunks = by_model[model_id]
                # Find the next unused, uncapped chunk for this model
                for idx, chunk in enumerate(model_chunks):
                    key = (model_id, idx)
                    if key in used:
                        continue
                    if type_counts[chunk.chunk_type] >= per_type_cap:
                        continue
                    selected.append(chunk)
                    used.add(key)
                    type_counts[chunk.chunk_type] += 1
                    model_counts[model_id] += 1
                    break
            if len(selected) >= budget_max:
                break

    # Step 6: Assemble into ModelAnchors
    # Rebuild display names + detection metadata from companion card
    display_names: dict[str, str] = {}
    detection_meta: dict[str, tuple[str, str, str]] = {}  # model_id → (presence_mode, evidence_quote, presence_explanation)
    for dm in companion_card.detected_models:
        display_names[dm.model_id] = dm.model_name
        detection_meta[dm.model_id] = (
            dm.presence_mode,
            dm.evidence_quote,
            dm.presence_explanation,
        )
    for ic in companion_card.identity_chunks:
        display_names[ic.model_id] = ic.display_name

    anchor_chunks: dict[str, list[CheatSheetChunk]] = {}
    for chunk in selected:
        anchor_chunks.setdefault(chunk.source_model_id, []).append(chunk)

    anchors = tuple(
        ModelAnchor(
            model_id=model_id,
            display_name=display_names.get(model_id, model_id),
            chunks=tuple(chunks),
            presence_mode=detection_meta.get(model_id, ("", "", ""))[0],
            evidence_quote=detection_meta.get(model_id, ("", "", ""))[1],
            presence_explanation=detection_meta.get(model_id, ("", "", ""))[2],
        )
        for model_id, chunks in anchor_chunks.items()
    )

    # Compute reranker metadata
    reranker_active = bool(relevance_scores)
    chunks_above_floor = 0
    mean_relevance = 0.0
    if reranker_active:
        all_scores = [
            _relevance_score_for_chunk(c, relevance_scores)
            for c in selected
        ]
        non_zero = [s for s in all_scores if s > 0.0]
        chunks_above_floor = sum(
            1 for s in all_scores if s >= _RELEVANCE_FLOOR
        )
        mean_relevance = sum(non_zero) / len(non_zero) if non_zero else 0.0

    return CompanionCheatSheet(
        anchors=anchors,
        total_chunk_count=len(selected),
        budget_max=budget_max,
        anti_echo_model_ids=frozenset(delta_model_ids),
        reranker_active=reranker_active,
        chunks_above_relevance_floor=chunks_above_floor,
        mean_relevance_score=mean_relevance,
    )
