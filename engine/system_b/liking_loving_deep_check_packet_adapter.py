from __future__ import annotations

from dataclasses import dataclass

from .deep_check_packet import DeepCheckPacket
from .deep_checks import DeepCheckResult
from .subpattern_catalog import SubpatternCatalog


@dataclass(frozen=True)
class LikingLovingPacketAdaptation:
    source_tendency_id: str
    source_sub_pattern: str
    mapped_subpattern_id: str
    adaptation_mode: str
    warnings: tuple[str, ...] = ()
    packet: DeepCheckPacket | None = None


class LikingLovingDeepCheckPacketAdapter:
    def __init__(self, *, subpatterns: SubpatternCatalog) -> None:
        self._subpatterns = subpatterns

    @classmethod
    def load(cls, root) -> "LikingLovingDeepCheckPacketAdapter":
        return cls(subpatterns=SubpatternCatalog.load(root))

    def adapt(self, result: DeepCheckResult) -> LikingLovingPacketAdaptation:
        if _normalize(result.tendency_id) != "liking-loving-tendency":
            return LikingLovingPacketAdaptation(
                source_tendency_id=result.tendency_id,
                source_sub_pattern=result.sub_pattern,
                mapped_subpattern_id="",
                adaptation_mode="unsupported-tendency",
                warnings=("unsupported-tendency",),
                packet=None,
            )
        if not result.detected:
            return LikingLovingPacketAdaptation(
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
            if _normalize(result.sub_pattern) not in ("", "general", "step-back", "step_back"):
                warnings.append("unmapped-liking-route")

        packet = DeepCheckPacket(
            tendency_id="liking-loving-tendency",
            subpattern_id=mapped_subpattern_id,
            quoted_evidence_span=result.specific_passage,
            structural_fingerprint=result.evidence,
            fingerprint_quality="mixed",
            reasoning_failure_mechanism=result.evidence,
            severity=result.severity,
            signal_tags=(),
        )
        return LikingLovingPacketAdaptation(
            source_tendency_id=result.tendency_id,
            source_sub_pattern=result.sub_pattern,
            mapped_subpattern_id=mapped_subpattern_id,
            adaptation_mode=adaptation_mode,
            warnings=tuple(warnings),
            packet=packet,
        )

    def _map_subpattern(self, result: DeepCheckResult) -> str:
        return map_liking_loving_result_to_subpattern(result)


def map_liking_loving_result_to_subpattern(result: DeepCheckResult) -> str:
    normalized = _normalize(result.sub_pattern)
    evidence_text = " ".join(
        part for part in (result.evidence, result.specific_passage) if str(part or "").strip()
    ).lower()

    if normalized in {"general", "step-back", "step_back"}:
        if _has_any(
            evidence_text,
            (
                "past devotion",
                "critical crises",
                "outweigh raw audit data",
                "outweighing objective data",
                "earn her a level of trust",
                "raw audit data",
            ),
        ):
            return "admired-insider-devotion-over-external-check"
        if _has_any(
            evidence_text,
            (
                "high-trust partner",
                "trusted ally",
                "long-term partnership",
                "perceived value of the relationship will outweigh the cost",
                "absorb the increase",
                "loyalty due to",
            ),
        ):
            return "relationship-goodwill-over-cost-reality"
        if _has_any(
            evidence_text,
            (
                "free infrastructure audit",
                "executive access",
                "tier-one partner",
                "high-touch relationship",
                "better long-term technical alignment",
                "soften the competitive tender",
            ),
        ):
            return "high-touch-affection-over-competitive-check"
        if _has_any(
            evidence_text,
            (
                "trusted source",
                "trusted referral",
                "game-changer",
                "significantly lowers the typical hiring risk",
                "already vetted his performance",
                "high-signal validation",
            ),
        ):
            return "trusted-referral-glow-over-vetting"
    return "general"


def _normalize(value: object) -> str:
    return str(value or "").strip().replace("_", "-").lower()


def _has_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)
