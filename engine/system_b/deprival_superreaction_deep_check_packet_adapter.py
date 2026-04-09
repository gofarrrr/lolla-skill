from __future__ import annotations

from dataclasses import dataclass

from .deep_check_packet import DeepCheckPacket
from .deep_checks import DeepCheckResult
from .subpattern_catalog import SubpatternCatalog


@dataclass(frozen=True)
class DeprivalSuperreactionPacketAdaptation:
    source_tendency_id: str
    source_sub_pattern: str
    mapped_subpattern_id: str
    adaptation_mode: str
    warnings: tuple[str, ...] = ()
    packet: DeepCheckPacket | None = None


class DeprivalSuperreactionDeepCheckPacketAdapter:
    def __init__(self, *, subpatterns: SubpatternCatalog) -> None:
        self._subpatterns = subpatterns

    @classmethod
    def load(cls, root) -> "DeprivalSuperreactionDeepCheckPacketAdapter":
        return cls(subpatterns=SubpatternCatalog.load(root))

    def adapt(self, result: DeepCheckResult) -> DeprivalSuperreactionPacketAdaptation:
        if _normalize(result.tendency_id) != "deprival-superreaction-tendency":
            return DeprivalSuperreactionPacketAdaptation(
                source_tendency_id=result.tendency_id,
                source_sub_pattern=result.sub_pattern,
                mapped_subpattern_id="",
                adaptation_mode="unsupported-tendency",
                warnings=("unsupported-tendency",),
                packet=None,
            )
        if not result.detected:
            return DeprivalSuperreactionPacketAdaptation(
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
                warnings.append("unmapped-deprival-superreaction-subpattern")

        packet = DeepCheckPacket(
            tendency_id="deprival-superreaction-tendency",
            subpattern_id=mapped_subpattern_id,
            quoted_evidence_span=result.specific_passage,
            structural_fingerprint=result.evidence,
            fingerprint_quality="mixed",
            reasoning_failure_mechanism=result.evidence,
            severity=result.severity,
            signal_tags=(),
        )
        return DeprivalSuperreactionPacketAdaptation(
            source_tendency_id=result.tendency_id,
            source_sub_pattern=result.sub_pattern,
            mapped_subpattern_id=mapped_subpattern_id,
            adaptation_mode=adaptation_mode,
            warnings=tuple(warnings),
            packet=packet,
        )

    def _map_subpattern(self, result: DeepCheckResult) -> str:
        return map_deprival_superreaction_result_to_subpattern(result)


def map_deprival_superreaction_result_to_subpattern(result: DeepCheckResult) -> str:
    normalized = _normalize(result.sub_pattern)
    evidence_text = " ".join(part for part in (result.evidence, result.specific_passage) if str(part or "").strip()).lower()

    if normalized == "endowment-effect":
        return "takeaway-pain-dampening"
    if normalized == "decision-trees":
        return "near-miss-opportunity-ratchet"
    if normalized == "expected-value":
        if _has_any(
            evidence_text,
            (
                "migration disruption",
                "business continuity",
                "switching",
                "current comfort",
                "incumbent",
                "renewal",
            ),
        ):
            return "switching-loss-overweighting"
        if _has_any(
            evidence_text,
            (
                "q1 targets",
                "quarter",
                "override security policy",
                "target loss",
                "asymmetric downside to missing",
            ),
        ):
            return "target-loss-escalation"
        if _has_any(
            evidence_text,
            (
                "rare high-leverage opportunity",
                "missing the moment",
                "window",
                "bidding war",
                "near miss",
            ),
        ):
            return "near-miss-opportunity-ratchet"
    if normalized == "general":
        if _has_any(
            evidence_text,
            (
                "quarter",
                "q1 target",
                "q1 targets",
                "net-retention target",
                "retention target",
                "target loss",
                "board explanation",
                "headline retention",
                "visible hit",
                "missing the renewal this quarter",
                "far more damaging",
            ),
        ):
            return "target-loss-escalation"
        if _has_any(
            evidence_text,
            (
                "bidding war",
                "rare high-leverage opportunity",
                "missing the moment",
                "window closes",
            ),
        ):
            return "near-miss-opportunity-ratchet"
    return "general"


def _normalize(value: object) -> str:
    return str(value or "").strip().replace("_", "-").lower()


def _has_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)
