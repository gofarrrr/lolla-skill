from __future__ import annotations

from dataclasses import dataclass

from .deep_check_packet import DeepCheckPacket
from .deep_checks import DeepCheckResult
from .subpattern_catalog import SubpatternCatalog


@dataclass(frozen=True)
class DislikingHatingPacketAdaptation:
    source_tendency_id: str
    source_sub_pattern: str
    mapped_subpattern_id: str
    adaptation_mode: str
    warnings: tuple[str, ...] = ()
    packet: DeepCheckPacket | None = None


class DislikingHatingDeepCheckPacketAdapter:
    def __init__(self, *, subpatterns: SubpatternCatalog) -> None:
        self._subpatterns = subpatterns

    @classmethod
    def load(cls, root) -> "DislikingHatingDeepCheckPacketAdapter":
        return cls(subpatterns=SubpatternCatalog.load(root))

    def adapt(self, result: DeepCheckResult) -> DislikingHatingPacketAdaptation:
        if _normalize(result.tendency_id) != "disliking-hating-tendency":
            return DislikingHatingPacketAdaptation(
                source_tendency_id=result.tendency_id,
                source_sub_pattern=result.sub_pattern,
                mapped_subpattern_id="",
                adaptation_mode="unsupported-tendency",
                warnings=("unsupported-tendency",),
                packet=None,
            )
        if not result.detected:
            return DislikingHatingPacketAdaptation(
                source_tendency_id=result.tendency_id,
                source_sub_pattern=result.sub_pattern,
                mapped_subpattern_id="",
                adaptation_mode="not-detected",
                warnings=("not-detected",),
                packet=None,
            )

        mapped_subpattern_id = map_disliking_hating_result_to_subpattern(result)
        warnings: list[str] = []
        adaptation_mode = "mapped-route-hint"
        if mapped_subpattern_id == "general":
            adaptation_mode = "general-fallback"
            if _normalize(result.sub_pattern) not in ("", "general"):
                warnings.append("unmapped-disliking-route")

        packet = DeepCheckPacket(
            tendency_id="disliking-hating-tendency",
            subpattern_id=mapped_subpattern_id,
            quoted_evidence_span=result.specific_passage,
            structural_fingerprint=result.evidence,
            fingerprint_quality="mixed",
            reasoning_failure_mechanism=result.evidence,
            severity=result.severity,
            signal_tags=(),
        )
        return DislikingHatingPacketAdaptation(
            source_tendency_id=result.tendency_id,
            source_sub_pattern=result.sub_pattern,
            mapped_subpattern_id=mapped_subpattern_id,
            adaptation_mode=adaptation_mode,
            warnings=tuple(warnings),
            packet=packet,
        )

    def _map_subpattern(self, result: DeepCheckResult) -> str:
        return map_disliking_hating_result_to_subpattern(result)


def map_disliking_hating_result_to_subpattern(result: DeepCheckResult) -> str:
    normalized = _normalize(result.sub_pattern)
    evidence_text = " ".join(
        part for part in (result.evidence, result.specific_passage) if str(part or "").strip()
    ).lower()

    if _has_any(
        evidence_text,
        (
            "bad news",
            "messenger",
            "bearer of bad news",
            "unwelcome information",
            "painful to hear",
            "replace the messenger",
            "remove them from the review cadence",
            "contain the negativity",
            "dragging every conversation back into bad news",
            "silence the bottleneck of negativity",
        ),
    ):
        return "messenger-punished-for-bad-news"
    if _has_any(
        evidence_text,
        (
            "even if the proposal is technically sound",
            "technically sound",
            "because it came from",
            "came from someone people can actually support",
            "hand credibility to someone",
            "disliked presenter",
            "associated with that person",
            "veto this option now",
            "the bigger risk is not the design itself",
        ),
    ):
        return "disliked-presenter-vetoes-valid-option"
    if normalized in {"hanlons-razor", "hanlons_razor"}:
        return "hostile-motive-overread-driving-switch"
    if normalized in {"multi-criteria-decision-analysis", "multi_criteria_decision_analysis"}:
        return "disliked-presenter-vetoes-valid-option"
    if normalized in {"non-violent-communication", "non_violent_communication", "game-theory-payoffs", "game_theory_payoffs", "nash-equilibrium", "nash_equilibrium"}:
        return "reciprocal-spite-over-joint-outcome"
    if normalized in {"active-listening", "active_listening", "constructive-feedback-models", "constructive_feedback_models"}:
        return "messenger-punished-for-bad-news"
    if _has_any(
        evidence_text,
        (
            "toxic dynamic",
            "adversarial vendor",
            "breakdown in communication",
            "difficult and unpleasant",
            "switching to",
            "malicious",
            "evil intent",
            "lost confidence in the vendor",
            "lost confidence",
            "dismissive attitude",
            "interpersonal friction",
            "vendor virtues",
            "objective verification",
            "bypass objective verification",
            "terminate the relationship",
            "unsalvageable",
            "ongoing conflict",
        ),
    ):
        return "hostile-motive-overread-driving-switch"
    return "general"


def _normalize(value: object) -> str:
    return str(value or "").strip().replace("_", "-").lower()


def _has_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)
