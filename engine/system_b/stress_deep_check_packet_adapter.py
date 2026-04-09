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
        normalized = _normalize(source_sub_pattern)
        if not self._subpatterns.has_tendency("stress-influence-tendency"):
            return "general"
        mapped = _LEGACY_ROUTE_HINT_MAP.get(normalized, "general")
        if mapped == "general":
            return "general"
        try:
            self._subpatterns.subpattern_for("stress-influence-tendency", mapped)
        except KeyError:
            return "general"
        return mapped


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
}

