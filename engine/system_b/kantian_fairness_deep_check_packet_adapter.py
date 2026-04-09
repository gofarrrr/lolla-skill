from __future__ import annotations

from dataclasses import dataclass

from .deep_check_packet import DeepCheckPacket
from .deep_checks import DeepCheckResult
from .subpattern_catalog import SubpatternCatalog


@dataclass(frozen=True)
class KantianFairnessPacketAdaptation:
    source_tendency_id: str
    source_sub_pattern: str
    mapped_subpattern_id: str
    adaptation_mode: str
    warnings: tuple[str, ...] = ()
    packet: DeepCheckPacket | None = None


class KantianFairnessDeepCheckPacketAdapter:
    def __init__(self, *, subpatterns: SubpatternCatalog) -> None:
        self._subpatterns = subpatterns

    @classmethod
    def load(cls, root) -> "KantianFairnessDeepCheckPacketAdapter":
        return cls(subpatterns=SubpatternCatalog.load(root))

    def adapt(self, result: DeepCheckResult) -> KantianFairnessPacketAdaptation:
        if _normalize(result.tendency_id) != "kantian-fairness-tendency":
            return KantianFairnessPacketAdaptation(
                source_tendency_id=result.tendency_id,
                source_sub_pattern=result.sub_pattern,
                mapped_subpattern_id="",
                adaptation_mode="unsupported-tendency",
                warnings=("unsupported-tendency",),
                packet=None,
            )
        if not result.detected:
            return KantianFairnessPacketAdaptation(
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
            if _normalize(result.sub_pattern) not in ("", "general", "power-dynamics"):
                warnings.append("unmapped-fairness-route")

        packet = DeepCheckPacket(
            tendency_id="kantian-fairness-tendency",
            subpattern_id=mapped_subpattern_id,
            quoted_evidence_span=result.specific_passage,
            structural_fingerprint=result.evidence,
            fingerprint_quality="mixed",
            reasoning_failure_mechanism=result.evidence,
            severity=result.severity,
            signal_tags=(),
        )
        return KantianFairnessPacketAdaptation(
            source_tendency_id=result.tendency_id,
            source_sub_pattern=result.sub_pattern,
            mapped_subpattern_id=mapped_subpattern_id,
            adaptation_mode=adaptation_mode,
            warnings=tuple(warnings),
            packet=packet,
        )

    def _map_subpattern(self, result: DeepCheckResult) -> str:
        return map_kantian_fairness_result_to_subpattern(result)


def map_kantian_fairness_result_to_subpattern(result: DeepCheckResult) -> str:
    normalized = _normalize(result.sub_pattern)
    evidence_text = " ".join(
        part for part in (result.evidence, result.specific_passage) if str(part or "").strip()
    ).lower()

    if normalized in {"power-dynamics", "general"}:
        if _has_any(
            evidence_text,
            (
                "reciprocal courtesy",
                "good faith will carry this",
                "they will meet us halfway",
                "meet us halfway",
                "courtesy they desire when roles are reversed",
                "high-trust partner for years",
                "trusted ally",
                "extend the same courtesy back",
                "good-faith reset",
            ),
        ):
            return "reciprocal-courtesy-assumed-without-enforcement"
        if _has_any(
            evidence_text,
            (
                "recognize the equity in the plan",
                "fair-sharing",
                "share equally",
                "equity of the plan",
                "burden-sharing",
                "proportionally",
                "fair alignment",
            ),
        ):
            return "fair-sharing-expected-despite-leverage-asymmetry"
        if _has_any(
            evidence_text,
            (
                "fair share",
                "share equally",
                "reasonable split",
                "incumbent should absorb",
                "despite the leverage",
                "switching costs are ours",
            ),
        ):
            return "fair-sharing-expected-despite-leverage-asymmetry"
        if _has_any(
            evidence_text,
            (
                "reciprocal obligation",
                "customers will understand",
                "they should accept the burden",
                "we're being fair so they will stay",
                "concession will earn loyalty",
                "fair return",
            ),
        ):
            return "concession-reciprocity-assumed-as-self-executing"
        if _has_any(
            evidence_text,
            (
                "unfair",
                "resentment",
                "hostility",
                "reactive hostility",
                "they owe us",
            ),
        ):
            return "resentment-at-unmet-fairness-norm"
    return "general"


def _normalize(value: object) -> str:
    return str(value or "").strip().replace("_", "-").lower()


def _has_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)
