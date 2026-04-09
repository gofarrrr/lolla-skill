from __future__ import annotations

from dataclasses import dataclass

from .deep_check_packet import DeepCheckPacket
from .deep_checks import DeepCheckResult
from .subpattern_catalog import SubpatternCatalog


@dataclass(frozen=True)
class ContrastMisreactionPacketAdaptation:
    source_tendency_id: str
    source_sub_pattern: str
    mapped_subpattern_id: str
    adaptation_mode: str
    warnings: tuple[str, ...] = ()
    packet: DeepCheckPacket | None = None


class ContrastMisreactionDeepCheckPacketAdapter:
    def __init__(self, *, subpatterns: SubpatternCatalog) -> None:
        self._subpatterns = subpatterns

    @classmethod
    def load(cls, root) -> "ContrastMisreactionDeepCheckPacketAdapter":
        return cls(subpatterns=SubpatternCatalog.load(root))

    def adapt(self, result: DeepCheckResult) -> ContrastMisreactionPacketAdaptation:
        if _normalize(result.tendency_id) != "contrast-misreaction-tendency":
            return ContrastMisreactionPacketAdaptation(
                source_tendency_id=result.tendency_id,
                source_sub_pattern=result.sub_pattern,
                mapped_subpattern_id="",
                adaptation_mode="unsupported-tendency",
                warnings=("unsupported-tendency",),
                packet=None,
            )
        if not result.detected:
            return ContrastMisreactionPacketAdaptation(
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
                warnings.append("unmapped-contrast-misreaction-subpattern")

        packet = DeepCheckPacket(
            tendency_id="contrast-misreaction-tendency",
            subpattern_id=mapped_subpattern_id,
            quoted_evidence_span=result.specific_passage,
            structural_fingerprint=result.evidence,
            fingerprint_quality="mixed",
            reasoning_failure_mechanism=result.evidence,
            severity=result.severity,
            signal_tags=(),
        )
        return ContrastMisreactionPacketAdaptation(
            source_tendency_id=result.tendency_id,
            source_sub_pattern=result.sub_pattern,
            mapped_subpattern_id=mapped_subpattern_id,
            adaptation_mode=adaptation_mode,
            warnings=tuple(warnings),
            packet=packet,
        )

    def _map_subpattern(self, result: DeepCheckResult) -> str:
        return map_contrast_misreaction_result_to_subpattern(result)


def map_contrast_misreaction_result_to_subpattern(result: DeepCheckResult) -> str:
    evidence_text = " ".join(
        part for part in (result.evidence, result.specific_passage) if str(part or "").strip()
    ).lower()
    if _has_any(
        evidence_text,
        (
            "familiarity",
            "migration disruption",
            "absolute cost comparison",
            "current vendor",
            "relative to disruption",
        ),
    ):
        return "incumbent-relative-offset"
    if _has_any(
        evidence_text,
        (
            "absolute security risk",
            "theoretical",
            "relative to quota pressure",
            "deal's size",
            "look small by comparison",
        ),
    ):
        return "deal-size-over-absolute-risk"
    if _has_any(
        evidence_text,
        (
            "tier-1 brand",
            "pr momentum",
            "massively positive relative",
            "brand association",
            "weak terms look acceptable",
            "brand halo",
            "momentum frame",
            "unresolved terms",
            "prestige is so overwhelmingly positive",
        ),
    ):
        return "prestige-frame-distortion"
    if _has_any(
        evidence_text,
        (
            "small leak",
            "slow drift",
            "tiny changes",
            "stepwise losses",
            "boiling frog",
            "static pricing",
            "gradual relative changes",
            "absolute hikes",
            "price sensitivity thresholds",
            "expanded significantly",
            "cumulative drift",
        ),
    ):
        return "slow-drift-under-registration-threshold"
    return "general"


def _normalize(value: object) -> str:
    return str(value or "").strip().replace("_", "-").lower()


def _has_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)
