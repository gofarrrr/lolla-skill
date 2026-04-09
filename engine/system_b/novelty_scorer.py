from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import TYPE_CHECKING

from .testing_harness import normalize_text

if TYPE_CHECKING:
    from .companion import CompanionCard
    from .frame_pressure import FramePressureCard
    from .pipeline import DeltaCard


_STOP_WORDS = frozenset(
    {
        "about",
        "after",
        "again",
        "against",
        "almost",
        "also",
        "because",
        "before",
        "being",
        "between",
        "could",
        "every",
        "first",
        "from",
        "have",
        "into",
        "just",
        "more",
        "only",
        "other",
        "over",
        "should",
        "than",
        "that",
        "their",
        "there",
        "these",
        "this",
        "those",
        "through",
        "under",
        "what",
        "when",
        "where",
        "which",
        "while",
        "with",
        "would",
        "your",
    }
)
_ACTION_CUES = (
    "add ",
    "audit",
    "calculate",
    "check",
    "compare",
    "define",
    "document",
    "list",
    "map",
    "measure",
    "name",
    "quantify",
    "require",
    "set ",
    "test",
    "verify",
)


@dataclass(frozen=True)
class FindingSpecificity:
    tendency_id: str
    has_specific_passage: bool
    has_non_general_sub_pattern: bool
    has_concrete_challenge: bool
    has_actionable_next_move: bool
    names_specific_model: bool
    specificity_score: float

    def to_payload(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class CompanionNovelty:
    chunk_overlap_vs_vanilla: float
    chunk_overlap_vs_delta: float
    unique_model_count: int
    unique_concepts: tuple[str, ...]
    type_diversity: int
    dominant_type_ratio: float

    def to_payload(self) -> dict[str, object]:
        return {
            "chunk_overlap_vs_vanilla": self.chunk_overlap_vs_vanilla,
            "chunk_overlap_vs_delta": self.chunk_overlap_vs_delta,
            "unique_model_count": self.unique_model_count,
            "unique_concepts": list(self.unique_concepts),
            "type_diversity": self.type_diversity,
            "dominant_type_ratio": self.dominant_type_ratio,
        }


@dataclass(frozen=True)
class FrameNovelty:
    frame_element_count: int
    unique_frame_concepts: tuple[str, ...]
    overlap_flag_count: int
    frame_novelty_ratio: float  # proportion of elements not overlapping Lane 1

    def to_payload(self) -> dict[str, object]:
        return {
            "frame_element_count": self.frame_element_count,
            "unique_frame_concepts": list(self.unique_frame_concepts),
            "overlap_flag_count": self.overlap_flag_count,
            "frame_novelty_ratio": self.frame_novelty_ratio,
        }


@dataclass(frozen=True)
class CombinedNovelty:
    total_unique_concepts: int
    lane_overlap_ratio: float

    def to_payload(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class NoveltyReport:
    passage_overlap_ratio: float
    specificity_breakdown: tuple[FindingSpecificity, ...]
    trusted_surface_ratio: float
    generic_finding_count: int
    novel_concepts: tuple[str, ...]
    companion_novelty: CompanionNovelty | None = None
    combined_novelty: CombinedNovelty | None = None
    frame_novelty: FrameNovelty | None = None

    @property
    def composite_novelty_score(self) -> float:
        """Blended score: 50% passage novelty + 30% avg specificity + 20% trusted surface.

        Passage novelty alone penalises findings that share vocabulary with the vanilla
        answer even when they add genuine structural pressure.  Blending in specificity
        and trusted-surface counters this: a high-specificity, high-trust finding that
        overlaps on tokens is still valuable.
        """
        passage_novelty = 1.0 - self.passage_overlap_ratio
        if self.specificity_breakdown:
            avg_specificity = sum(
                item.specificity_score for item in self.specificity_breakdown
            ) / len(self.specificity_breakdown)
        else:
            avg_specificity = 0.0
        return round(
            0.5 * passage_novelty
            + 0.3 * avg_specificity
            + 0.2 * self.trusted_surface_ratio,
            3,
        )

    def to_payload(self) -> dict[str, object]:
        return {
            "passage_overlap_ratio": self.passage_overlap_ratio,
            "composite_novelty_score": self.composite_novelty_score,
            "specificity_breakdown": [item.to_payload() for item in self.specificity_breakdown],
            "trusted_surface_ratio": self.trusted_surface_ratio,
            "generic_finding_count": self.generic_finding_count,
            "novel_concepts": list(self.novel_concepts),
            "companion_novelty": self.companion_novelty.to_payload() if self.companion_novelty else None,
            "combined_novelty": self.combined_novelty.to_payload() if self.combined_novelty else None,
            "frame_novelty": self.frame_novelty.to_payload() if self.frame_novelty else None,
        }


def score_novelty(
    vanilla_answer: str,
    delta_card: "DeltaCard",
    companion_card: "CompanionCard | None" = None,
    frame_pressure_card: "FramePressureCard | None" = None,
) -> NoveltyReport:
    vanilla_text = normalize_text(vanilla_answer)
    delta_text = _build_delta_text(delta_card)
    specificity = tuple(_finding_specificity(finding) for finding in delta_card.findings)
    novel_concepts = tuple(
        sorted(
            (_concept_terms(delta_text) | _model_terms(delta_card.selected_model_ids))
            - _concept_terms(vanilla_text)
        )
    )
    trusted_surface_ratio = _safe_ratio(
        sum(1 for finding in delta_card.findings if finding.is_trusted_surface),
        len(delta_card.findings),
    )
    generic_count = sum(1 for item in specificity if item.specificity_score < 0.5)
    companion_novelty: CompanionNovelty | None = None
    combined_novelty: CombinedNovelty | None = None
    if companion_card is not None:
        companion_text = _build_companion_text(companion_card)
        companion_types = _companion_type_counts(companion_card)
        delta_concepts = _concept_terms(delta_text) | _model_terms(delta_card.selected_model_ids)
        companion_concepts = _concept_terms(companion_text) | _model_terms(_companion_model_ids(companion_card))
        unique_companion_concepts = tuple(
            sorted(companion_concepts - _concept_terms(vanilla_text) - delta_concepts)
        )
        companion_novelty = CompanionNovelty(
            chunk_overlap_vs_vanilla=_overlap_ratio(companion_text, vanilla_text),
            chunk_overlap_vs_delta=_overlap_ratio(companion_text, delta_text),
            unique_model_count=len(set(_companion_model_ids(companion_card)) - set(delta_card.selected_model_ids)),
            unique_concepts=unique_companion_concepts,
            type_diversity=len(companion_types),
            dominant_type_ratio=_dominant_type_ratio(companion_types),
        )
        combined_terms = set(novel_concepts) | set(unique_companion_concepts)
        shared_terms = set(novel_concepts) & set(unique_companion_concepts)
        combined_novelty = CombinedNovelty(
            total_unique_concepts=len(combined_terms),
            lane_overlap_ratio=_safe_ratio(len(shared_terms), len(combined_terms)),
        )
    frame_novelty: FrameNovelty | None = None
    if frame_pressure_card is not None:
        frame_novelty = _build_frame_novelty(
            frame_pressure_card, vanilla_text, delta_text, delta_card,
        )
    return NoveltyReport(
        passage_overlap_ratio=_overlap_ratio(delta_text, vanilla_text),
        specificity_breakdown=specificity,
        trusted_surface_ratio=trusted_surface_ratio,
        generic_finding_count=generic_count,
        novel_concepts=novel_concepts,
        companion_novelty=companion_novelty,
        combined_novelty=combined_novelty,
        frame_novelty=frame_novelty,
    )


def _finding_specificity(finding: object) -> FindingSpecificity:
    specific_passage = normalize_text(getattr(finding, "specific_passage", ""))
    sub_pattern = normalize_text(getattr(finding, "sub_pattern", "")).replace("_", "-").lower()
    challenge_statement = normalize_text(getattr(finding, "challenge_statement", ""))
    next_move = normalize_text(getattr(finding, "next_move", ""))
    model_ids = tuple(getattr(finding, "selected_model_ids", ()) or ())
    has_specific_passage = bool(specific_passage)
    has_non_general_sub_pattern = bool(sub_pattern and sub_pattern != "general")
    has_concrete_challenge = bool(
        challenge_statement
        and (
            "?" in challenge_statement
            or "'" in challenge_statement
            or '"' in challenge_statement
            or len(_concept_terms(challenge_statement)) >= 4
        )
    )
    lower_next_move = next_move.lower()
    has_actionable_next_move = bool(next_move and any(cue in lower_next_move for cue in _ACTION_CUES))
    names_specific_model = bool(tuple(str(item).strip() for item in model_ids if str(item).strip()))
    score = round(
        (
            int(has_specific_passage)
            + int(has_non_general_sub_pattern)
            + int(has_concrete_challenge)
            + int(has_actionable_next_move)
            + int(names_specific_model)
        )
        / 5.0,
        3,
    )
    return FindingSpecificity(
        tendency_id=str(getattr(finding, "tendency_id", "")).strip(),
        has_specific_passage=has_specific_passage,
        has_non_general_sub_pattern=has_non_general_sub_pattern,
        has_concrete_challenge=has_concrete_challenge,
        has_actionable_next_move=has_actionable_next_move,
        names_specific_model=names_specific_model,
        specificity_score=score,
    )


def _build_delta_text(delta_card: "DeltaCard") -> str:
    fragments: list[str] = []
    for finding in delta_card.findings:
        fragments.extend(
            [
                getattr(finding, "tendency_name", ""),
                getattr(finding, "sub_pattern", ""),
                getattr(finding, "specific_passage", ""),
                getattr(finding, "challenge_statement", ""),
                getattr(finding, "next_move", ""),
                getattr(finding, "primary_model_id", ""),
                " ".join(getattr(finding, "selected_model_ids", ()) or ()),
            ]
        )
    return normalize_text(" ".join(fragment for fragment in fragments if normalize_text(fragment)))


def _build_companion_text(companion_card: "CompanionCard") -> str:
    fragments: list[str] = []
    for item in companion_card.detected_models:
        fragments.extend([item.model_id, item.model_name, item.evidence_quote, item.presence_explanation])
    for item in companion_card.expansions:
        fragments.extend([item.model_id, item.model_name, item.substrate_chunk, item.why_relevant, item.relation_type])
    for item in companion_card.failure_hints:
        fragments.append(item.text)
    return normalize_text(" ".join(fragment for fragment in fragments if normalize_text(fragment)))


def _companion_type_counts(companion_card: "CompanionCard") -> dict[str, int]:
    counts: dict[str, int] = {}
    if companion_card.detected_models:
        counts["detected_model"] = len(companion_card.detected_models)
    if companion_card.expansions:
        counts["expansion"] = len(companion_card.expansions)
    if companion_card.failure_hints:
        counts["failure_hint"] = len(companion_card.failure_hints)
    return counts


def _companion_model_ids(companion_card: "CompanionCard") -> tuple[str, ...]:
    model_ids = [item.model_id for item in companion_card.detected_models]
    model_ids.extend(item.model_id for item in companion_card.expansions)
    return tuple(str(item).strip() for item in model_ids if str(item).strip())


def _dominant_type_ratio(type_counts: dict[str, int]) -> float:
    total = sum(type_counts.values())
    if total <= 0:
        return 0.0
    return round(max(type_counts.values()) / total, 3)


def _model_terms(model_ids: tuple[str, ...] | list[str]) -> set[str]:
    terms: set[str] = set()
    for model_id in model_ids:
        normalized = normalize_text(model_id).replace("_", "-").lower()
        if not normalized:
            continue
        parts = [part for part in normalized.split("-") if len(part) >= 4 and part not in _STOP_WORDS]
        terms.update(parts)
        terms.add(normalized)
    return terms


def _concept_terms(text: str) -> set[str]:
    tokens = _tokenize(text)
    return {token for token in tokens if len(token) >= 5 and token not in _STOP_WORDS}


def _overlap_ratio(source_text: str, reference_text: str) -> float:
    source_tokens = _tokenize(source_text)
    if not source_tokens:
        return 0.0
    reference_tokens = _tokenize(reference_text)
    return round(len(source_tokens & reference_tokens) / len(source_tokens), 3)


def _tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9][a-z0-9_-]*", normalize_text(text).lower())
        if len(token) >= 3
    }


def _safe_ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 3)


def _build_frame_novelty(
    card: "FramePressureCard",
    vanilla_text: str,
    delta_text: str,
    delta_card: "DeltaCard",
) -> "FrameNovelty":
    """Score how much the Frame Pressure card adds beyond vanilla answer and Lane 1."""
    elements = card.frame_elements
    element_count = len(elements)
    # Collect concepts from frame element texts and patterns
    frame_terms: set[str] = set()
    for el in elements:
        frame_terms |= _concept_terms(normalize_text(el.element_text))
        frame_terms |= _concept_terms(normalize_text(el.fragility_signal))
        frame_terms.add(normalize_text(el.frame_pattern).replace("_", "-"))
    # Unique concepts: in frame but not in vanilla or delta
    vanilla_concepts = _concept_terms(vanilla_text)
    delta_concepts = _concept_terms(delta_text) | _model_terms(delta_card.selected_model_ids)
    unique_frame_concepts = tuple(sorted(frame_terms - vanilla_concepts - delta_concepts))
    # Overlap flags come directly from the card
    overlap_flag_count = len(card.overlap_flags)
    # Frame novelty ratio: elements not flagged as overlapping
    non_overlapping = sum(
        1 for el in elements if el.frame_pattern not in card.overlap_flags
    )
    frame_novelty_ratio = _safe_ratio(non_overlapping, element_count)
    return FrameNovelty(
        frame_element_count=element_count,
        unique_frame_concepts=unique_frame_concepts,
        overlap_flag_count=overlap_flag_count,
        frame_novelty_ratio=frame_novelty_ratio,
    )
