from __future__ import annotations

from dataclasses import dataclass

from .deep_check_packet import DeepCheckPacket
from .deep_checks import DeepCheckResult
from .subpattern_catalog import SubpatternCatalog


@dataclass(frozen=True)
class ReasonRespectingPacketAdaptation:
    source_tendency_id: str
    source_sub_pattern: str
    mapped_subpattern_id: str
    adaptation_mode: str
    warnings: tuple[str, ...] = ()
    packet: DeepCheckPacket | None = None


class ReasonRespectingDeepCheckPacketAdapter:
    def __init__(self, *, subpatterns: SubpatternCatalog) -> None:
        self._subpatterns = subpatterns

    @classmethod
    def load(cls, root) -> "ReasonRespectingDeepCheckPacketAdapter":
        return cls(subpatterns=SubpatternCatalog.load(root))

    def adapt(self, result: DeepCheckResult) -> ReasonRespectingPacketAdaptation:
        if _normalize(result.tendency_id) != "reason-respecting-tendency":
            return ReasonRespectingPacketAdaptation(
                source_tendency_id=result.tendency_id,
                source_sub_pattern=result.sub_pattern,
                mapped_subpattern_id="",
                adaptation_mode="unsupported-tendency",
                warnings=("unsupported-tendency",),
                packet=None,
            )
        if not result.detected:
            return ReasonRespectingPacketAdaptation(
                source_tendency_id=result.tendency_id,
                source_sub_pattern=result.sub_pattern,
                mapped_subpattern_id="",
                adaptation_mode="not-detected",
                warnings=("not-detected",),
                packet=None,
            )

        mapped_subpattern_id = self._map_subpattern(result)
        warnings: list[str] = []
        adaptation_mode = "mapped-route-hint"
        if mapped_subpattern_id == "general":
            adaptation_mode = "general-fallback"
            if _normalize(result.sub_pattern) not in (
                "",
                "general",
                "chain-of-thought",
                "formal-reasoning",
                "five-whys-method",
                "first-principles-thinking",
            ):
                warnings.append("unmapped-reason-respecting-route")

        packet = DeepCheckPacket(
            tendency_id="reason-respecting-tendency",
            subpattern_id=mapped_subpattern_id,
            quoted_evidence_span=result.specific_passage,
            structural_fingerprint=result.evidence,
            fingerprint_quality="mixed",
            reasoning_failure_mechanism=result.evidence,
            severity=result.severity,
            signal_tags=(),
        )
        return ReasonRespectingPacketAdaptation(
            source_tendency_id=result.tendency_id,
            source_sub_pattern=result.sub_pattern,
            mapped_subpattern_id=mapped_subpattern_id,
            adaptation_mode=adaptation_mode,
            warnings=tuple(warnings),
            packet=packet,
        )

    def _map_subpattern(self, result: DeepCheckResult) -> str:
        return map_reason_respecting_result_to_subpattern(result)


def map_reason_respecting_result_to_subpattern(result: DeepCheckResult) -> str:
    evidence_text = " ".join(
        part for part in (result.sub_pattern, result.evidence, result.specific_passage) if str(part or "").strip()
    ).lower()

    if _has_any(
        evidence_text,
        ("narrative", "story", "coherent", "framing"),
    ):
        return "narrative-closes-the-why"
    if _has_any(
        evidence_text,
        ("correlation", "trend", "associated", "pattern"),
    ):
        return "correlation-accepted-as-cause"
    if _has_any(
        evidence_text,
        ("surface", "first", "obvious", "stated", "stop"),
    ):
        return "shallow-first-why-stops-inquiry"
    return "general"


def _normalize(value: object) -> str:
    return str(value or "").strip().replace("_", "-").lower()


def _has_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)
