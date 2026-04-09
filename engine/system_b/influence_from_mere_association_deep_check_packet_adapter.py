from __future__ import annotations

from dataclasses import dataclass

from .deep_check_packet import DeepCheckPacket
from .deep_checks import DeepCheckResult
from .subpattern_catalog import SubpatternCatalog


@dataclass(frozen=True)
class InfluenceFromMereAssociationPacketAdaptation:
    source_tendency_id: str
    source_sub_pattern: str
    mapped_subpattern_id: str
    adaptation_mode: str
    warnings: tuple[str, ...] = ()
    packet: DeepCheckPacket | None = None


class InfluenceFromMereAssociationDeepCheckPacketAdapter:
    def __init__(self, *, subpatterns: SubpatternCatalog) -> None:
        self._subpatterns = subpatterns

    @classmethod
    def load(cls, root) -> "InfluenceFromMereAssociationDeepCheckPacketAdapter":
        return cls(subpatterns=SubpatternCatalog.load(root))

    def adapt(self, result: DeepCheckResult) -> InfluenceFromMereAssociationPacketAdaptation:
        if _normalize(result.tendency_id) != "influence-from-mere-association-tendency":
            return InfluenceFromMereAssociationPacketAdaptation(
                source_tendency_id=result.tendency_id,
                source_sub_pattern=result.sub_pattern,
                mapped_subpattern_id="",
                adaptation_mode="unsupported-tendency",
                warnings=("unsupported-tendency",),
                packet=None,
            )
        if not result.detected:
            return InfluenceFromMereAssociationPacketAdaptation(
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
            if _normalize(result.sub_pattern) not in ("", "general"):
                warnings.append("unmapped-association-subpattern")

        packet = DeepCheckPacket(
            tendency_id="influence-from-mere-association-tendency",
            subpattern_id=mapped_subpattern_id,
            quoted_evidence_span=result.specific_passage,
            structural_fingerprint=result.evidence,
            fingerprint_quality="mixed",
            reasoning_failure_mechanism=result.evidence,
            severity=result.severity,
            signal_tags=(),
        )
        return InfluenceFromMereAssociationPacketAdaptation(
            source_tendency_id=result.tendency_id,
            source_sub_pattern=result.sub_pattern,
            mapped_subpattern_id=mapped_subpattern_id,
            adaptation_mode=adaptation_mode,
            warnings=tuple(warnings),
            packet=packet,
        )

    def _map_subpattern(self, result: DeepCheckResult) -> str:
        return map_influence_from_mere_association_result_to_subpattern(result)


def map_influence_from_mere_association_result_to_subpattern(result: DeepCheckResult) -> str:
    normalized = _normalize(result.sub_pattern)
    evidence_text = " ".join(
        part for part in (result.evidence, result.specific_passage) if str(part or "").strip()
    ).lower()

    if normalized == "scientific-method-evidence-testing":
        if _has_any(
            evidence_text,
            (
                "premium",
                "value realization",
                "satisfaction scores",
                "price increase",
                "justify the premium",
            ),
        ):
            return "price-quality-signal-substitution"
        if _has_any(
            evidence_text,
            (
                "proven vendor",
                "familiar environment",
                "stable and cost-effective",
                "incumbent",
            ),
        ):
            return "familiarity-equals-performance"
        return "halo-transfer-over-substance"

    if normalized == "general":
        if _has_any(
            evidence_text,
            (
                "premium",
                "satisfaction scores",
                "value realization",
                "justify the premium",
                "price hike",
            ),
        ):
            return "price-quality-signal-substitution"
        if _has_any(
            evidence_text,
            (
                "tier-1 brand",
                "tier-one market leader",
                "halo effect",
                "signaled intent",
                "game-changer",
                "charisma",
                "trusted source",
                "trusted referral",
            ),
        ):
            return "halo-transfer-over-substance"
        if _has_any(
            evidence_text,
            (
                "proven vendor",
                "familiar environment",
                "stable and cost-effective",
                "incumbent",
                "renewal",
            ),
        ):
            return "familiarity-equals-performance"
        if _has_any(
            evidence_text,
            (
                "messenger",
                "bearer of bad news",
                "bad news",
                "label contaminates",
            ),
        ):
            return "messenger-contamination"
    return "general"


def _normalize(value: object) -> str:
    return str(value or "").strip().replace("_", "-").lower()


def _has_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)
