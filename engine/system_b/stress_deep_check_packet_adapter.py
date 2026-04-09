from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .deep_check_packet import DeepCheckPacket
from .deep_checks import DeepCheckResult
from .subpattern_catalog import SubpatternCatalog


@dataclass(frozen=True)
class StressPacketAdaptation:
    source_tendency_id: str
    source_sub_pattern: str
    mapped_subpattern_id: str
    adaptation_mode: str
    warnings: tuple[str, ...] = ()
    packet: DeepCheckPacket | None = None


class StressDeepCheckPacketAdapter:
    def __init__(self, *, subpatterns: SubpatternCatalog) -> None:
        self._subpatterns = subpatterns

    @classmethod
    def load(cls, root: Path) -> "StressDeepCheckPacketAdapter":
        return cls(subpatterns=SubpatternCatalog.load(root))

    def adapt(self, result: DeepCheckResult) -> StressPacketAdaptation:
        if _normalize(result.tendency_id) != "stress-influence-tendency":
            return StressPacketAdaptation(
                source_tendency_id=result.tendency_id,
                source_sub_pattern=result.sub_pattern,
                mapped_subpattern_id="",
                adaptation_mode="unsupported-tendency",
                warnings=("unsupported-tendency",),
                packet=None,
            )
        if not result.detected:
            return StressPacketAdaptation(
                source_tendency_id=result.tendency_id,
                source_sub_pattern=result.sub_pattern,
                mapped_subpattern_id="",
                adaptation_mode="not-detected",
                warnings=("not-detected",),
                packet=None,
            )

        mapped_subpattern_id = self._map_subpattern(result.sub_pattern)
        warnings: list[str] = []
        adaptation_mode = "mapped-route-hint"
        if mapped_subpattern_id == "general":
            adaptation_mode = "general-fallback"
            if _normalize(result.sub_pattern) not in ("", "general"):
                warnings.append("unmapped-stress-subpattern")

        packet = DeepCheckPacket(
            tendency_id="stress-influence-tendency",
            subpattern_id=mapped_subpattern_id,
            quoted_evidence_span=result.specific_passage,
            structural_fingerprint=result.evidence,
            fingerprint_quality="mixed",
            reasoning_failure_mechanism=result.evidence,
            severity=result.severity,
            signal_tags=(),
        )
        return StressPacketAdaptation(
            source_tendency_id=result.tendency_id,
            source_sub_pattern=result.sub_pattern,
            mapped_subpattern_id=mapped_subpattern_id,
            adaptation_mode=adaptation_mode,
            warnings=tuple(warnings),
            packet=packet,
        )

    def _map_subpattern(self, source_sub_pattern: str) -> str:
        if not self._subpatterns.has_tendency("stress-influence-tendency"):
            return "general"
        mapped = map_stress_result_to_subpattern_from_hint(source_sub_pattern)
        if mapped == "general":
            return "general"
        try:
            self._subpatterns.subpattern_for("stress-influence-tendency", mapped)
        except KeyError:
            return "general"
        return mapped


def map_stress_result_to_subpattern(result: DeepCheckResult) -> str:
    normalized_subpattern = _normalize(result.sub_pattern)
    evidence_text = " ".join(
        [
            str(result.evidence or "").strip().lower(),
            str(result.specific_passage or "").strip().lower(),
        ]
    )

    # Direct subpattern matches
    if normalized_subpattern == "deadline-driven-shortcutting":
        return "deadline-driven-shortcutting"
    if normalized_subpattern == "load-collapse-and-omission":
        return "load-collapse-and-omission"
    if normalized_subpattern == "feedback-threat-hijack":
        return "feedback-threat-hijack"
    if normalized_subpattern == "challenge-beyond-capacity":
        return "challenge-beyond-capacity"

    # Map from antidote model route hints
    mapped = _LEGACY_ROUTE_HINT_MAP.get(normalized_subpattern)
    if mapped is not None and mapped != "general":
        return mapped

    # Evidence-based refinement
    deadline_hits = sum(1 for cue in _DEADLINE_TOKENS if cue in evidence_text)
    if deadline_hits >= 2:
        return "deadline-driven-shortcutting"

    overload_hits = sum(1 for cue in _OVERLOAD_TOKENS if cue in evidence_text)
    if overload_hits >= 2:
        return "load-collapse-and-omission"

    feedback_hits = sum(1 for cue in _FEEDBACK_TOKENS if cue in evidence_text)
    if feedback_hits >= 2:
        return "feedback-threat-hijack"

    capacity_hits = sum(1 for cue in _CAPACITY_TOKENS if cue in evidence_text)
    if capacity_hits >= 2:
        return "challenge-beyond-capacity"

    return "general"


def map_stress_result_to_subpattern_from_hint(source_sub_pattern: str) -> str:
    normalized = _normalize(source_sub_pattern)
    return _LEGACY_ROUTE_HINT_MAP.get(normalized, "general")


def _normalize(value: object) -> str:
    return str(value or "").strip().replace("_", "-").lower()


_LEGACY_ROUTE_HINT_MAP = {
    "general": "general",
    "delays": "deadline-driven-shortcutting",
    "checklists": "general",
    "scaffolding": "general",
    "desirable-difficulties": "challenge-beyond-capacity",
    "desirable_difficulties": "challenge-beyond-capacity",
    "constructive-feedback-models": "feedback-threat-hijack",
    "constructive_feedback_models": "feedback-threat-hijack",
    "emotional-intelligence": "feedback-threat-hijack",
    "emotional_intelligence": "feedback-threat-hijack",
    "self-control": "general",
    "self_control": "general",
    "cognitive-load-theory": "load-collapse-and-omission",
    "cognitive_load_theory": "load-collapse-and-omission",
}

_DEADLINE_TOKENS = (
    "deadline",
    "time pressure",
    "quarter-end",
    "rushed",
    "shortcut",
    "expedited",
    "urgent",
    "accelerat",
    "compressed timeline",
)

_OVERLOAD_TOKENS = (
    "overload",
    "overwhelm",
    "cognitive load",
    "too many",
    "dropped",
    "omitted",
    "forgot",
    "collapsed",
    "simplif",
)

_FEEDBACK_TOKENS = (
    "feedback",
    "criticism",
    "negative review",
    "threat",
    "defensive",
    "attacked",
    "blamed",
    "performance review",
    "hijack",
)

_CAPACITY_TOKENS = (
    "beyond capacity",
    "too complex",
    "out of depth",
    "overwhelm",
    "unfamiliar",
    "stretch assignment",
    "skill gap",
    "insufficient expertise",
    "panic",
)

