from __future__ import annotations

from dataclasses import dataclass

from .deep_check_packet import DeepCheckPacket
from .deep_checks import DeepCheckResult
from .subpattern_catalog import SubpatternCatalog


@dataclass(frozen=True)
class SimplePainDenialPacketAdaptation:
    source_tendency_id: str
    source_sub_pattern: str
    mapped_subpattern_id: str
    adaptation_mode: str
    warnings: tuple[str, ...] = ()
    packet: DeepCheckPacket | None = None


class SimplePainDenialDeepCheckPacketAdapter:
    def __init__(self, *, subpatterns: SubpatternCatalog) -> None:
        self._subpatterns = subpatterns

    @classmethod
    def load(cls, root) -> "SimplePainDenialDeepCheckPacketAdapter":
        return cls(subpatterns=SubpatternCatalog.load(root))

    def adapt(self, result: DeepCheckResult) -> SimplePainDenialPacketAdaptation:
        if _normalize(result.tendency_id) != "simple-pain-avoiding-psychological-denial":
            return SimplePainDenialPacketAdaptation(
                source_tendency_id=result.tendency_id,
                source_sub_pattern=result.sub_pattern,
                mapped_subpattern_id="",
                adaptation_mode="unsupported-tendency",
                warnings=("unsupported-tendency",),
                packet=None,
            )
        if not result.detected:
            return SimplePainDenialPacketAdaptation(
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
                warnings.append("unmapped-simple-pain-denial-subpattern")

        packet = DeepCheckPacket(
            tendency_id="simple-pain-avoiding-psychological-denial",
            subpattern_id=mapped_subpattern_id,
            quoted_evidence_span=result.specific_passage,
            structural_fingerprint=result.evidence,
            fingerprint_quality="mixed",
            reasoning_failure_mechanism=result.evidence,
            severity=result.severity,
            signal_tags=(),
        )
        return SimplePainDenialPacketAdaptation(
            source_tendency_id=result.tendency_id,
            source_sub_pattern=result.sub_pattern,
            mapped_subpattern_id=mapped_subpattern_id,
            adaptation_mode=adaptation_mode,
            warnings=tuple(warnings),
            packet=packet,
        )

    def _map_subpattern(self, result: DeepCheckResult) -> str:
        return map_simple_pain_denial_result_to_subpattern(result)


def map_simple_pain_denial_result_to_subpattern(result: DeepCheckResult) -> str:
        normalized = _normalize(result.sub_pattern)
        if normalized == "premortem":
            return "downside-softened-into-benign-story"
        if normalized == "falsifiability":
            return "downside-softened-into-benign-story"
        if normalized == "general":
            evidence_text = " ".join(
                part for part in (result.evidence, result.specific_passage) if str(part or "").strip()
            ).lower()
            if _has_any(
                evidence_text,
                (
                    "secondary",
                    "unfinalized",
                    "unresolved",
                    "revenue-share",
                    "data-governing",
                    "data-govern",
                    "announcement momentum",
                ),
            ):
                return "painful-reality-reframed-as-secondary"
            if _has_any(
                evidence_text,
                (
                    "temporary cleanup noise",
                    "transition noise",
                    "sorting effect",
                    "not signs of structural damage",
                    "look worse on paper",
                    "manageable sequencing issue",
                ),
            ):
                return "downside-softened-into-benign-story"
            if _has_any(
                evidence_text,
                (
                    "theoretical",
                    "policy violation",
                    "production environment",
                    "production exposure",
                    "security risk",
                    "fast-track",
                ),
            ):
                return "catastrophic-risk-normalized-as-theoretical"
        if normalized == "internal-locus-of-control":
            return "blame-shift-over-reality-contact"
        return "general"


def _normalize(value: object) -> str:
    return str(value or "").strip().replace("_", "-").lower()


def _has_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)
