from __future__ import annotations

from dataclasses import dataclass

from .deep_check_packet import DeepCheckPacket
from .deep_checks import DeepCheckResult
from .subpattern_catalog import SubpatternCatalog


@dataclass(frozen=True)
class EnvyJealousyPacketAdaptation:
    source_tendency_id: str
    source_sub_pattern: str
    mapped_subpattern_id: str
    adaptation_mode: str
    warnings: tuple[str, ...] = ()
    packet: DeepCheckPacket | None = None


class EnvyJealousyDeepCheckPacketAdapter:
    def __init__(self, *, subpatterns: SubpatternCatalog) -> None:
        self._subpatterns = subpatterns

    @classmethod
    def load(cls, root) -> "EnvyJealousyDeepCheckPacketAdapter":
        return cls(subpatterns=SubpatternCatalog.load(root))

    def adapt(self, result: DeepCheckResult) -> EnvyJealousyPacketAdaptation:
        if _normalize(result.tendency_id) != "envy-jealousy-tendency":
            return EnvyJealousyPacketAdaptation(
                source_tendency_id=result.tendency_id,
                source_sub_pattern=result.sub_pattern,
                mapped_subpattern_id="",
                adaptation_mode="unsupported-tendency",
                warnings=("unsupported-tendency",),
                packet=None,
            )
        if not result.detected:
            return EnvyJealousyPacketAdaptation(
                source_tendency_id=result.tendency_id,
                source_sub_pattern=result.sub_pattern,
                mapped_subpattern_id="",
                adaptation_mode="not-detected",
                warnings=("not-detected",),
                packet=None,
            )

        mapped_subpattern_id = map_envy_jealousy_result_to_subpattern(result)
        warnings: list[str] = []
        adaptation_mode = "mapped-route-hint"
        if mapped_subpattern_id == "general":
            adaptation_mode = "general-fallback"
            if _normalize(result.sub_pattern) not in ("", "general"):
                warnings.append("unmapped-envy-route")

        packet = DeepCheckPacket(
            tendency_id="envy-jealousy-tendency",
            subpattern_id=mapped_subpattern_id,
            quoted_evidence_span=result.specific_passage,
            structural_fingerprint=result.evidence,
            fingerprint_quality="mixed",
            reasoning_failure_mechanism=result.evidence,
            severity=result.severity,
            signal_tags=(),
        )
        return EnvyJealousyPacketAdaptation(
            source_tendency_id=result.tendency_id,
            source_sub_pattern=result.sub_pattern,
            mapped_subpattern_id=mapped_subpattern_id,
            adaptation_mode=adaptation_mode,
            warnings=tuple(warnings),
            packet=packet,
        )

    def _map_subpattern(self, result: DeepCheckResult) -> str:
        return map_envy_jealousy_result_to_subpattern(result)


def map_envy_jealousy_result_to_subpattern(result: DeepCheckResult) -> str:
    normalized = _normalize(result.sub_pattern)
    evidence_text = " ".join(
        part for part in (result.evidence, result.specific_passage) if str(part or "").strip()
    ).lower()

    if normalized in {"internal-locus-of-control", "internal_locus_of_control"}:
        if _has_any(
            evidence_text,
            (
                "moved first",
                "beat the neighboring unit",
                "beat the neighbor",
                "holding the line",
                "compensation discipline",
                "recruiting and prestige disadvantage",
                "prestige disadvantage",
                "escalate decisively",
                "comparison hardens",
                "relax the normal exception criteria",
                "broader retention package",
            ),
        ):
            return "rivalry-escalation-over-own-standards"
        if _has_any(
            evidence_text,
            (
                "peer's package",
                "peer package",
                "same level receiving",
                "significant bumps",
                "status imbalance",
                "departmental envy",
                "neighboring team",
                "another person's package",
                "peer's raise",
                "peer raise",
                "perceived status imbalance",
            ),
        ):
            return "peer-outcome-becomes-compensation-anchor"
        if _has_any(
            evidence_text,
            (
                "status gap",
                "comparative status",
                "visible differential",
                "resentment",
                "comparison class",
                "seen in another's possession",
            ),
        ):
            return "comparative-status-gap-treated-as-emergency"
        return "general"
    if normalized in {"game-theory-payoffs", "game_theory_payoffs"}:
        return "rivalry-escalation-over-own-standards"
    if _has_any(
        evidence_text,
        (
            "departmental envy",
            "perceived status imbalance",
            "peer's raise",
            "neighboring team received",
            "reactive pay move",
            "same level receiving",
            "another person's package has become the controlling reference point",
            "observing another's raise",
            "richer package",
        ),
    ):
        return "peer-outcome-becomes-compensation-anchor"
    return "general"


def _normalize(value: object) -> str:
    return str(value or "").strip().replace("_", "-").lower()


def _has_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)
