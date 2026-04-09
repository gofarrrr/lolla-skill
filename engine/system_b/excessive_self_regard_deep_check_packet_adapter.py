from __future__ import annotations

from dataclasses import dataclass

from .deep_check_packet import DeepCheckPacket
from .deep_checks import DeepCheckResult
from .subpattern_catalog import SubpatternCatalog


@dataclass(frozen=True)
class ExcessiveSelfRegardPacketAdaptation:
    source_tendency_id: str
    source_sub_pattern: str
    mapped_subpattern_id: str
    adaptation_mode: str
    warnings: tuple[str, ...] = ()
    packet: DeepCheckPacket | None = None


class ExcessiveSelfRegardDeepCheckPacketAdapter:
    def __init__(self, *, subpatterns: SubpatternCatalog) -> None:
        self._subpatterns = subpatterns

    @classmethod
    def load(cls, root) -> "ExcessiveSelfRegardDeepCheckPacketAdapter":
        return cls(subpatterns=SubpatternCatalog.load(root))

    def adapt(self, result: DeepCheckResult) -> ExcessiveSelfRegardPacketAdaptation:
        if _normalize(result.tendency_id) != "excessive-self-regard-tendency":
            return ExcessiveSelfRegardPacketAdaptation(
                source_tendency_id=result.tendency_id,
                source_sub_pattern=result.sub_pattern,
                mapped_subpattern_id="",
                adaptation_mode="unsupported-tendency",
                warnings=("unsupported-tendency",),
                packet=None,
            )
        if not result.detected:
            return ExcessiveSelfRegardPacketAdaptation(
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
                warnings.append("unmapped-excessive-self-regard-subpattern")

        packet = DeepCheckPacket(
            tendency_id="excessive-self-regard-tendency",
            subpattern_id=mapped_subpattern_id,
            quoted_evidence_span=result.specific_passage,
            structural_fingerprint=result.evidence,
            fingerprint_quality="mixed",
            reasoning_failure_mechanism=result.evidence,
            severity=result.severity,
            signal_tags=(),
        )
        return ExcessiveSelfRegardPacketAdaptation(
            source_tendency_id=result.tendency_id,
            source_sub_pattern=result.sub_pattern,
            mapped_subpattern_id=mapped_subpattern_id,
            adaptation_mode=adaptation_mode,
            warnings=tuple(warnings),
            packet=packet,
        )

    def _map_subpattern(self, result: DeepCheckResult) -> str:
        return map_excessive_self_regard_result_to_subpattern(result)


def map_excessive_self_regard_result_to_subpattern(result: DeepCheckResult) -> str:
    normalized = _normalize(result.sub_pattern)
    evidence_text = " ".join(
        part for part in (result.evidence, result.specific_passage) if str(part or "").strip()
    ).lower()

    if normalized in {"circle-of-competence", "user-centered-design"}:
        return "own-offering-overrated-as-uniquely-fit"
    if normalized == "confidence-calibration":
        return "value-story-certainty-without-calibration"
    if normalized in {"peer-review-your-perspectives", "johari-window"}:
        if _has_any(
            evidence_text,
            (
                "designed the system",
                "outside critics",
                "outside review",
                "reopening the core thinking",
                "product judgment",
                "self-authored",
                "redesign",
            ),
        ):
            return "creator-judgment-insulated-from-peer-check"
        return "impression-over-record-selection"

    if normalized == "general":
        if _has_any(
            evidence_text,
            (
                "uniquely positioned",
                "perfectly aligned",
                "our platform",
                "very little technical friction",
                "user validation",
            ),
        ):
            return "own-offering-overrated-as-uniquely-fit"
        if _has_any(
            evidence_text,
            (
                "value realization",
                "justify the premium",
                "high satisfaction scores",
                "premium pricing",
                "our value enhancements",
            ),
        ):
            return "value-story-certainty-without-calibration"
        if _has_any(
            evidence_text,
            (
                "charisma",
                "trusted referral",
                "trusted source",
                "face-to-face",
                "interview",
                "game-changer",
            ),
        ):
            return "impression-over-record-selection"
        if _has_any(
            evidence_text,
            (
                "we already designed",
                "no need for outside review",
                "our plan is already right",
                "self-authored",
                "redesign",
            ),
        ):
            return "creator-judgment-insulated-from-peer-check"
    return "general"


def _normalize(value: object) -> str:
    return str(value or "").strip().replace("_", "-").lower()


def _has_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)
