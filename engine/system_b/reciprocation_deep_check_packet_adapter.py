from __future__ import annotations

from dataclasses import dataclass

from .deep_check_packet import DeepCheckPacket
from .deep_checks import DeepCheckResult
from .subpattern_catalog import SubpatternCatalog


@dataclass(frozen=True)
class ReciprocationPacketAdaptation:
    source_tendency_id: str
    source_sub_pattern: str
    mapped_subpattern_id: str
    adaptation_mode: str
    warnings: tuple[str, ...] = ()
    packet: DeepCheckPacket | None = None


class ReciprocationDeepCheckPacketAdapter:
    def __init__(self, *, subpatterns: SubpatternCatalog) -> None:
        self._subpatterns = subpatterns

    @classmethod
    def load(cls, root) -> "ReciprocationDeepCheckPacketAdapter":
        return cls(subpatterns=SubpatternCatalog.load(root))

    def adapt(self, result: DeepCheckResult) -> ReciprocationPacketAdaptation:
        if _normalize(result.tendency_id) != "reciprocation-tendency":
            return ReciprocationPacketAdaptation(
                source_tendency_id=result.tendency_id,
                source_sub_pattern=result.sub_pattern,
                mapped_subpattern_id="",
                adaptation_mode="unsupported-tendency",
                warnings=("unsupported-tendency",),
                packet=None,
            )
        if not result.detected:
            return ReciprocationPacketAdaptation(
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
            if _normalize(result.sub_pattern) not in ("", "general", "obligations-controls-mapping", "delays"):
                warnings.append("unmapped-reciprocation-route")

        packet = DeepCheckPacket(
            tendency_id="reciprocation-tendency",
            subpattern_id=mapped_subpattern_id,
            quoted_evidence_span=result.specific_passage,
            structural_fingerprint=result.evidence,
            fingerprint_quality="mixed",
            reasoning_failure_mechanism=result.evidence,
            severity=result.severity,
            signal_tags=(),
        )
        return ReciprocationPacketAdaptation(
            source_tendency_id=result.tendency_id,
            source_sub_pattern=result.sub_pattern,
            mapped_subpattern_id=mapped_subpattern_id,
            adaptation_mode=adaptation_mode,
            warnings=tuple(warnings),
            packet=packet,
        )

    def _map_subpattern(self, result: DeepCheckResult) -> str:
        return map_reciprocation_result_to_subpattern(result)


def map_reciprocation_result_to_subpattern(result: DeepCheckResult) -> str:
    normalized = _normalize(result.sub_pattern)
    evidence_text = " ".join(
        part for part in (result.evidence, result.specific_passage) if str(part or "").strip()
    ).lower()

    if normalized in {"general", "obligations-controls-mapping", "delays"}:
        if _has_any(
            evidence_text,
            (
                "free infrastructure audit",
                "executive access",
                "vendor",
                "hospitality",
                "free advisory",
                "tier-one partner",
                "extra mile value",
                "favors from vendors",
            ),
        ):
            return "vendor-favors-treated-as-decision-debt"
        if _has_any(
            evidence_text,
            (
                "loyalty window",
                "grandfathering",
                "minimizes immediate friction",
                "extend the same courtesy back",
                "meet us halfway",
                "good-faith reset",
                "absorb the change",
                "acceptance without forcing",
            ),
        ):
            return "courtesy-back-assumed-after-concession"
        if _has_any(
            evidence_text,
            (
                "past devotion",
                "critical crises",
                "rebuilt our legacy stack",
                "outweighs raw audit data",
                "earned her a level of trust",
                "past sacrifices",
            ),
        ):
            return "past-devotion-buys-current-exemption"
    return "general"


def _normalize(value: object) -> str:
    return str(value or "").strip().replace("_", "-").lower()


def _has_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)
