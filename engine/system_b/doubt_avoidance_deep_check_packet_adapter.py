from __future__ import annotations

from dataclasses import dataclass

from .deep_check_packet import DeepCheckPacket
from .deep_checks import DeepCheckResult
from .subpattern_catalog import SubpatternCatalog


@dataclass(frozen=True)
class DoubtAvoidancePacketAdaptation:
    source_tendency_id: str
    source_sub_pattern: str
    mapped_subpattern_id: str
    adaptation_mode: str
    warnings: tuple[str, ...] = ()
    packet: DeepCheckPacket | None = None


class DoubtAvoidanceDeepCheckPacketAdapter:
    def __init__(self, *, subpatterns: SubpatternCatalog) -> None:
        self._subpatterns = subpatterns

    @classmethod
    def load(cls, root) -> "DoubtAvoidanceDeepCheckPacketAdapter":
        return cls(subpatterns=SubpatternCatalog.load(root))

    def adapt(self, result: DeepCheckResult) -> DoubtAvoidancePacketAdaptation:
        if _normalize(result.tendency_id) != "doubt-avoidance-tendency":
            return DoubtAvoidancePacketAdaptation(
                source_tendency_id=result.tendency_id,
                source_sub_pattern=result.sub_pattern,
                mapped_subpattern_id="",
                adaptation_mode="unsupported-tendency",
                warnings=("unsupported-tendency",),
                packet=None,
            )
        if not result.detected:
            return DoubtAvoidancePacketAdaptation(
                source_tendency_id=result.tendency_id,
                source_sub_pattern=result.sub_pattern,
                mapped_subpattern_id="",
                adaptation_mode="not-detected",
                warnings=("not-detected",),
                packet=None,
            )

        mapped_subpattern_id = self._map_subpattern(result.sub_pattern)
        warnings: list[str] = []
        adaptation_mode = "mapped-route-hint"
        if mapped_subpattern_id == "general":
            adaptation_mode = "general-fallback"
            if _normalize(result.sub_pattern) not in ("", "general"):
                warnings.append("unmapped-doubt-avoidance-subpattern")

        packet = DeepCheckPacket(
            tendency_id="doubt-avoidance-tendency",
            subpattern_id=mapped_subpattern_id,
            quoted_evidence_span=result.specific_passage,
            structural_fingerprint=result.evidence,
            fingerprint_quality="mixed",
            reasoning_failure_mechanism=result.evidence,
            severity=result.severity,
            signal_tags=(),
        )
        return DoubtAvoidancePacketAdaptation(
            source_tendency_id=result.tendency_id,
            source_sub_pattern=result.sub_pattern,
            mapped_subpattern_id=mapped_subpattern_id,
            adaptation_mode=adaptation_mode,
            warnings=tuple(warnings),
            packet=packet,
        )

    def _map_subpattern(self, source_sub_pattern: str) -> str:
        if not self._subpatterns.has_tendency("doubt-avoidance-tendency"):
            return "general"
        mapped = map_doubt_avoidance_result_to_subpattern_from_hint(source_sub_pattern)
        if mapped == "general":
            return "general"
        try:
            self._subpatterns.subpattern_for("doubt-avoidance-tendency", mapped)
        except KeyError:
            return "general"
        return mapped


def map_doubt_avoidance_result_to_subpattern(result: DeepCheckResult) -> str:
    normalized_subpattern = _normalize(result.sub_pattern)
    evidence_text = " ".join(
        [
            str(result.evidence or "").strip().lower(),
            str(result.specific_passage or "").strip().lower(),
        ]
    )

    # Direct subpattern matches
    if normalized_subpattern == "forced-closure-under-pressure":
        return "forced-closure-under-pressure"
    if normalized_subpattern == "unknowns-demoted-to-keep-motion":
        return "unknowns-demoted-to-keep-motion"
    if normalized_subpattern == "option-set-collapse":
        return "option-set-collapse"
    if normalized_subpattern == "counterargument-window-skipped":
        return "counterargument-window-skipped"

    # Map from antidote model route hints
    mapped = _LEGACY_ROUTE_HINT_MAP.get(normalized_subpattern)
    if mapped is not None and mapped != "general":
        return mapped

    # Evidence-based refinement
    closure_hits = sum(1 for cue in _CLOSURE_TOKENS if cue in evidence_text)
    if closure_hits >= 2:
        return "forced-closure-under-pressure"

    unknowns_hits = sum(1 for cue in _UNKNOWNS_TOKENS if cue in evidence_text)
    if unknowns_hits >= 2:
        return "unknowns-demoted-to-keep-motion"

    collapse_hits = sum(1 for cue in _COLLAPSE_TOKENS if cue in evidence_text)
    if collapse_hits >= 2:
        return "option-set-collapse"

    skipped_hits = sum(1 for cue in _COUNTERARG_TOKENS if cue in evidence_text)
    if skipped_hits >= 2:
        return "counterargument-window-skipped"

    return "general"


def map_doubt_avoidance_result_to_subpattern_from_hint(source_sub_pattern: str) -> str:
    normalized = _normalize(source_sub_pattern)
    return _LEGACY_ROUTE_HINT_MAP.get(normalized, "general")


def _normalize(value: object) -> str:
    return str(value or "").strip().replace("_", "-").lower()


_LEGACY_ROUTE_HINT_MAP = {
    "general": "general",
    "step-back": "forced-closure-under-pressure",
    "step_back": "forced-closure-under-pressure",
    "true-uncertainty-navigation": "unknowns-demoted-to-keep-motion",
    "true_uncertainty_navigation": "unknowns-demoted-to-keep-motion",
    "risk-vs-uncertainty": "unknowns-demoted-to-keep-motion",
    "risk_vs_uncertainty": "unknowns-demoted-to-keep-motion",
    "optionality": "option-set-collapse",
    "decision-trees": "option-set-collapse",
    "decision_trees": "option-set-collapse",
    "dialectical-reasoning": "counterargument-window-skipped",
    "dialectical_reasoning": "counterargument-window-skipped",
    "divergent-vs-convergent-thinking": "counterargument-window-skipped",
    "divergent_vs_convergent_thinking": "counterargument-window-skipped",
    "experimentation": "counterargument-window-skipped",
}

_CLOSURE_TOKENS = (
    "premature",
    "rushed",
    "forced",
    "closure",
    "decided too fast",
    "pressure to decide",
    "quick resolution",
    "uncomfortable with ambiguity",
    "escape uncertainty",
)

_UNKNOWNS_TOKENS = (
    "unknown",
    "uncertainty",
    "ambiguity",
    "unresolved",
    "swept aside",
    "ignored risk",
    "demoted",
    "momentum",
    "keep moving",
)

_COLLAPSE_TOKENS = (
    "narrowed",
    "collapsed",
    "single option",
    "only path",
    "eliminated",
    "binary",
    "either-or",
    "no alternative",
    "optionality",
)

_COUNTERARG_TOKENS = (
    "counterargument",
    "devil's advocate",
    "opposing view",
    "dissent",
    "alternative perspective",
    "skipped debate",
    "no pushback",
    "unchallenged",
    "convergent",
)
