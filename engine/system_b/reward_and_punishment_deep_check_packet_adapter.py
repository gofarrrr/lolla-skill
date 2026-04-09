from __future__ import annotations

from dataclasses import dataclass

from .deep_check_packet import DeepCheckPacket
from .deep_checks import DeepCheckResult
from .subpattern_catalog import SubpatternCatalog


@dataclass(frozen=True)
class RewardAndPunishmentPacketAdaptation:
    source_tendency_id: str
    source_sub_pattern: str
    mapped_subpattern_id: str
    adaptation_mode: str
    warnings: tuple[str, ...] = ()
    packet: DeepCheckPacket | None = None


class RewardAndPunishmentDeepCheckPacketAdapter:
    def __init__(self, *, subpatterns: SubpatternCatalog) -> None:
        self._subpatterns = subpatterns

    @classmethod
    def load(cls, root) -> "RewardAndPunishmentDeepCheckPacketAdapter":
        return cls(subpatterns=SubpatternCatalog.load(root))

    def adapt(self, result: DeepCheckResult) -> RewardAndPunishmentPacketAdaptation:
        if _normalize(result.tendency_id) != "reward-and-punishment-superresponse-tendency":
            return RewardAndPunishmentPacketAdaptation(
                source_tendency_id=result.tendency_id,
                source_sub_pattern=result.sub_pattern,
                mapped_subpattern_id="",
                adaptation_mode="unsupported-tendency",
                warnings=("unsupported-tendency",),
                packet=None,
            )
        if not result.detected:
            return RewardAndPunishmentPacketAdaptation(
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
                warnings.append("unmapped-reward-route")

        packet = DeepCheckPacket(
            tendency_id="reward-and-punishment-superresponse-tendency",
            subpattern_id=mapped_subpattern_id,
            quoted_evidence_span=result.specific_passage,
            structural_fingerprint=result.evidence,
            fingerprint_quality="mixed",
            reasoning_failure_mechanism=result.evidence,
            severity=result.severity,
            signal_tags=(),
        )
        return RewardAndPunishmentPacketAdaptation(
            source_tendency_id=result.tendency_id,
            source_sub_pattern=result.sub_pattern,
            mapped_subpattern_id=mapped_subpattern_id,
            adaptation_mode=adaptation_mode,
            warnings=tuple(warnings),
            packet=packet,
        )

    def _map_subpattern(self, result: DeepCheckResult) -> str:
        return map_reward_and_punishment_result_to_subpattern(result)


def map_reward_and_punishment_result_to_subpattern(result: DeepCheckResult) -> str:
    normalized = _normalize(result.sub_pattern)
    evidence_text = " ".join(
        part for part in (result.evidence, result.specific_passage) if str(part or "").strip()
    ).lower()

    if normalized in {"systems-thinking", "general"}:
        if _has_any(
            evidence_text,
            (
                "uncapped commission",
                "tiered volume kicker",
                "accelerators",
                "front-loading the rewards",
                "compensation redesign",
                "commission-heavy",
                "aggressive commission structure",
                "70% at-risk",
                "at-risk component",
                "earnings at risk",
                "close deals fast",
                "faster deal velocity",
                "sort your sales force",
                "top performers will thrive and laggards will self-select out",
                "sales reps gaming the system",
                "high-stakes targets",
                "base salary",
                "new logo volume",
            ),
        ):
            return "compensation-design-as-behavior-engine"
        if _has_any(
            evidence_text,
            (
                "rare high-leverage opportunity",
                "market valuation",
                "news cycle",
                "appearing difficult",
                "maximize immediate visibility",
                "investor interest",
            ),
        ):
            return "reward-window-over-governance"
        if _has_any(
            evidence_text,
            (
                "first-mover advantage",
                "rapid market share acquisition",
                "bidding war",
                "moving quickly",
                "immediate expansion",
                "decisive culture",
            ),
        ):
            return "capture-speed-over-readiness"
        if _has_any(
            evidence_text,
            (
                "40% of our q1 quota",
                "valuation hit",
                "one-time audit exception",
                "missing this target",
                "immediate liquidity",
                "quota",
            ),
        ):
            return "quota-pressure-over-protocol"
    return "general"


def _normalize(value: object) -> str:
    return str(value or "").strip().replace("_", "-").lower()


def _has_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)
