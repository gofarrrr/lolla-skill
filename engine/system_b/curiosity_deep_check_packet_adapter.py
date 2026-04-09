from __future__ import annotations

from dataclasses import dataclass

from .deep_check_packet import DeepCheckPacket
from .deep_checks import DeepCheckResult
from .subpattern_catalog import SubpatternCatalog


@dataclass(frozen=True)
class CuriosityPacketAdaptation:
    source_tendency_id: str
    source_sub_pattern: str
    mapped_subpattern_id: str
    adaptation_mode: str
    warnings: tuple[str, ...] = ()
    packet: DeepCheckPacket | None = None


class CuriosityDeepCheckPacketAdapter:
    def __init__(self, *, subpatterns: SubpatternCatalog) -> None:
        self._subpatterns = subpatterns

    @classmethod
    def load(cls, root) -> "CuriosityDeepCheckPacketAdapter":
        return cls(subpatterns=SubpatternCatalog.load(root))

    def adapt(self, result: DeepCheckResult) -> CuriosityPacketAdaptation:
        if _normalize(result.tendency_id) != "curiosity-tendency":
            return CuriosityPacketAdaptation(
                source_tendency_id=result.tendency_id,
                source_sub_pattern=result.sub_pattern,
                mapped_subpattern_id="",
                adaptation_mode="unsupported-tendency",
                warnings=("unsupported-tendency",),
                packet=None,
            )
        if not result.detected:
            return CuriosityPacketAdaptation(
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
                warnings.append("unmapped-curiosity-subpattern")

        packet = DeepCheckPacket(
            tendency_id="curiosity-tendency",
            subpattern_id=mapped_subpattern_id,
            quoted_evidence_span=result.specific_passage,
            structural_fingerprint=result.evidence,
            fingerprint_quality="mixed",
            reasoning_failure_mechanism=result.evidence,
            severity=result.severity,
            signal_tags=(),
        )
        return CuriosityPacketAdaptation(
            source_tendency_id=result.tendency_id,
            source_sub_pattern=result.sub_pattern,
            mapped_subpattern_id=mapped_subpattern_id,
            adaptation_mode=adaptation_mode,
            warnings=tuple(warnings),
            packet=packet,
        )

    def _map_subpattern(self, result: DeepCheckResult) -> str:
        if not self._subpatterns.has_tendency("curiosity-tendency"):
            return "general"
        mapped = map_curiosity_result_to_subpattern(result)
        if mapped == "general":
            return "general"
        try:
            self._subpatterns.subpattern_for("curiosity-tendency", mapped)
        except KeyError:
            return "general"
        return mapped


def map_curiosity_result_to_subpattern(result: DeepCheckResult) -> str:
    normalized_subpattern = _normalize(result.sub_pattern)
    evidence_text = " ".join(
        [
            str(result.evidence or "").strip().lower(),
            str(result.specific_passage or "").strip().lower(),
        ]
    )

    # Direct subpattern matches from LLM route hints
    if normalized_subpattern == "shallow-first-answer-accepted":
        return "shallow-first-answer-accepted"
    if normalized_subpattern == "inquiry-suppressed-for-momentum":
        return "inquiry-suppressed-for-momentum"
    if normalized_subpattern == "missing-process-self-audit":
        return "missing-process-self-audit"

    # Map from antidote model route hints to subpatterns
    if normalized_subpattern in ("five-whys-method", "five_whys_method"):
        return "shallow-first-answer-accepted"
    if normalized_subpattern in ("first-principles-thinking", "first_principles_thinking"):
        # Could be shallow-first-answer or inquiry-suppressed — check evidence
        if any(cue in evidence_text for cue in _MOMENTUM_TOKENS):
            return "inquiry-suppressed-for-momentum"
        return "shallow-first-answer-accepted"
    if normalized_subpattern in ("scaffolding-educational", "scaffolding_educational"):
        return "inquiry-suppressed-for-momentum"
    if normalized_subpattern in ("meta-cognitive-reflection", "meta_cognitive_reflection"):
        return "missing-process-self-audit"

    # Evidence-based refinement for general or unknown route hints
    meta_hits = sum(1 for cue in _META_COGNITIVE_TOKENS if cue in evidence_text)
    if meta_hits >= 2:
        return "missing-process-self-audit"

    momentum_hits = sum(1 for cue in _MOMENTUM_TOKENS if cue in evidence_text)
    if momentum_hits >= 2:
        return "inquiry-suppressed-for-momentum"

    shallow_hits = sum(1 for cue in _SHALLOW_ANSWER_TOKENS if cue in evidence_text)
    if shallow_hits >= 2:
        return "shallow-first-answer-accepted"

    return "general"


def _normalize(value: object) -> str:
    return str(value or "").strip().replace("_", "-").lower()


_SHALLOW_ANSWER_TOKENS = (
    "first answer",
    "first explanation",
    "proximate cause",
    "surface explanation",
    "stops at",
    "accepted without",
    "without probing",
    "without questioning",
    "without asking",
    "shallow",
    "conventional frame",
    "inherited assumption",
)

_MOMENTUM_TOKENS = (
    "momentum",
    "forward progress",
    "move forward",
    "keep moving",
    "deferred",
    "unexplored",
    "unresolved question",
    "further inquiry",
    "suppress",
    "delay",
    "practical urgency",
)

_META_COGNITIVE_TOKENS = (
    "analytical frame",
    "blind spot",
    "process itself",
    "reasoning process",
    "method",
    "self-audit",
    "metacognit",
    "frame being used",
    "never questioned",
    "unexamined",
)
