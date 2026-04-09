from __future__ import annotations

from dataclasses import dataclass

from .deep_check_packet import DeepCheckPacket
from .deep_checks import DeepCheckResult
from .subpattern_catalog import SubpatternCatalog


@dataclass(frozen=True)
class UseItOrLoseItPacketAdaptation:
    source_tendency_id: str
    source_sub_pattern: str
    mapped_subpattern_id: str
    adaptation_mode: str
    warnings: tuple[str, ...] = ()
    packet: DeepCheckPacket | None = None


class UseItOrLoseItDeepCheckPacketAdapter:
    def __init__(self, *, subpatterns: SubpatternCatalog) -> None:
        self._subpatterns = subpatterns

    @classmethod
    def load(cls, root) -> "UseItOrLoseItDeepCheckPacketAdapter":
        return cls(subpatterns=SubpatternCatalog.load(root))

    def adapt(self, result: DeepCheckResult) -> UseItOrLoseItPacketAdaptation:
        if _normalize(result.tendency_id) != "use-it-or-lose-it-tendency":
            return UseItOrLoseItPacketAdaptation(
                source_tendency_id=result.tendency_id,
                source_sub_pattern=result.sub_pattern,
                mapped_subpattern_id="",
                adaptation_mode="unsupported-tendency",
                warnings=("unsupported-tendency",),
                packet=None,
            )
        if not result.detected:
            return UseItOrLoseItPacketAdaptation(
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
                warnings.append("unmapped-use-it-or-lose-it-subpattern")

        packet = DeepCheckPacket(
            tendency_id="use-it-or-lose-it-tendency",
            subpattern_id=mapped_subpattern_id,
            quoted_evidence_span=result.specific_passage,
            structural_fingerprint=result.evidence,
            fingerprint_quality="mixed",
            reasoning_failure_mechanism=result.evidence,
            severity=result.severity,
            signal_tags=(),
        )
        return UseItOrLoseItPacketAdaptation(
            source_tendency_id=result.tendency_id,
            source_sub_pattern=result.sub_pattern,
            mapped_subpattern_id=mapped_subpattern_id,
            adaptation_mode=adaptation_mode,
            warnings=tuple(warnings),
            packet=packet,
        )

    def _map_subpattern(self, result: DeepCheckResult) -> str:
        if not self._subpatterns.has_tendency("use-it-or-lose-it-tendency"):
            return "general"
        mapped = map_use_it_or_lose_it_result_to_subpattern(result)
        if mapped == "general":
            return "general"
        try:
            self._subpatterns.subpattern_for("use-it-or-lose-it-tendency", mapped)
        except KeyError:
            return "general"
        return mapped


def map_use_it_or_lose_it_result_to_subpattern(result: DeepCheckResult) -> str:
    normalized_subpattern = _normalize(result.sub_pattern)
    evidence_text = " ".join(
        [
            str(result.evidence or "").strip().lower(),
            str(result.specific_passage or "").strip().lower(),
        ]
    )

    # Direct subpattern matches
    if normalized_subpattern == "stale-methodology-unquestioned":
        return "stale-methodology-unquestioned"
    if normalized_subpattern == "lapsed-process-from-neglect":
        return "lapsed-process-from-neglect"
    if normalized_subpattern == "degraded-pattern-recognition":
        return "degraded-pattern-recognition"

    # Map from antidote model route hints
    if normalized_subpattern in ("varied-practice-interleaving", "varied_practice_interleaving"):
        return "stale-methodology-unquestioned"
    if normalized_subpattern in ("habit-formation", "habit_formation"):
        return "lapsed-process-from-neglect"
    if normalized_subpattern in ("perceptual-learning", "perceptual_learning"):
        return "degraded-pattern-recognition"
    if normalized_subpattern in ("deliberate-practice", "deliberate_practice"):
        # Could be any shape — check evidence
        if any(cue in evidence_text for cue in _PATTERN_RECOGNITION_TOKENS):
            return "degraded-pattern-recognition"
        if any(cue in evidence_text for cue in _PROCESS_LAPSE_TOKENS):
            return "lapsed-process-from-neglect"
        return "stale-methodology-unquestioned"
    if normalized_subpattern in ("persistence-grit", "persistence_grit"):
        return "general"

    # Evidence-based refinement
    pattern_hits = sum(1 for cue in _PATTERN_RECOGNITION_TOKENS if cue in evidence_text)
    if pattern_hits >= 2:
        return "degraded-pattern-recognition"

    process_hits = sum(1 for cue in _PROCESS_LAPSE_TOKENS if cue in evidence_text)
    if process_hits >= 2:
        return "lapsed-process-from-neglect"

    stale_hits = sum(1 for cue in _STALE_METHOD_TOKENS if cue in evidence_text)
    if stale_hits >= 2:
        return "stale-methodology-unquestioned"

    return "general"


def _normalize(value: object) -> str:
    return str(value or "").strip().replace("_", "-").lower()


_STALE_METHOD_TOKENS = (
    "stale",
    "outdated",
    "once-strong",
    "old approach",
    "familiar framework",
    "comfortable routine",
    "habitual",
    "unchallenged",
    "without pressure-test",
    "not rotated",
    "narrow",
)

_PROCESS_LAPSE_TOKENS = (
    "lapsed",
    "abandoned",
    "never systematized",
    "no routine",
    "no habit",
    "fell into disuse",
    "stopped doing",
    "used to",
    "once had",
    "atrophied",
    "neglect",
)

_PATTERN_RECOGNITION_TOKENS = (
    "pattern recognition",
    "intuition",
    "instinct",
    "subtle cue",
    "situational",
    "exposure",
    "lost the ability",
    "no longer recogni",
    "degraded",
    "missed signal",
)
