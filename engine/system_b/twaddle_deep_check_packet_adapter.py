from __future__ import annotations

from dataclasses import dataclass

from .deep_check_packet import DeepCheckPacket
from .deep_checks import DeepCheckResult
from .subpattern_catalog import SubpatternCatalog


@dataclass(frozen=True)
class TwaddlePacketAdaptation:
    source_tendency_id: str
    source_sub_pattern: str
    mapped_subpattern_id: str
    adaptation_mode: str
    warnings: tuple[str, ...] = ()
    packet: DeepCheckPacket | None = None


class TwaddleDeepCheckPacketAdapter:
    def __init__(self, *, subpatterns: SubpatternCatalog) -> None:
        self._subpatterns = subpatterns

    @classmethod
    def load(cls, root) -> "TwaddleDeepCheckPacketAdapter":
        return cls(subpatterns=SubpatternCatalog.load(root))

    def adapt(self, result: DeepCheckResult) -> TwaddlePacketAdaptation:
        if _normalize(result.tendency_id) != "twaddle-tendency":
            return TwaddlePacketAdaptation(
                source_tendency_id=result.tendency_id,
                source_sub_pattern=result.sub_pattern,
                mapped_subpattern_id="",
                adaptation_mode="unsupported-tendency",
                warnings=("unsupported-tendency",),
                packet=None,
            )
        if not result.detected:
            return TwaddlePacketAdaptation(
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
                warnings.append("unmapped-twaddle-subpattern")

        packet = DeepCheckPacket(
            tendency_id="twaddle-tendency",
            subpattern_id=mapped_subpattern_id,
            quoted_evidence_span=result.specific_passage,
            structural_fingerprint=result.evidence,
            fingerprint_quality="mixed",
            reasoning_failure_mechanism=result.evidence,
            severity=result.severity,
            signal_tags=(),
        )
        return TwaddlePacketAdaptation(
            source_tendency_id=result.tendency_id,
            source_sub_pattern=result.sub_pattern,
            mapped_subpattern_id=mapped_subpattern_id,
            adaptation_mode=adaptation_mode,
            warnings=tuple(warnings),
            packet=packet,
        )

    def _map_subpattern(self, result: DeepCheckResult) -> str:
        if not self._subpatterns.has_tendency("twaddle-tendency"):
            return "general"
        mapped = map_twaddle_result_to_subpattern(result)
        if mapped == "general":
            return "general"
        try:
            self._subpatterns.subpattern_for("twaddle-tendency", mapped)
        except KeyError:
            return "general"
        return mapped


def map_twaddle_result_to_subpattern(result: DeepCheckResult) -> str:
    normalized_subpattern = _normalize(result.sub_pattern)
    evidence_text = " ".join(
        [
            str(result.evidence or "").strip().lower(),
            str(result.specific_passage or "").strip().lower(),
        ]
    )

    # Direct subpattern matches
    if normalized_subpattern == "procedural-noise-crowds-substance":
        return "procedural-noise-crowds-substance"
    if normalized_subpattern == "effort-spread-not-concentrated":
        return "effort-spread-not-concentrated"
    if normalized_subpattern == "jargon-masking-shallow-analysis":
        return "jargon-masking-shallow-analysis"

    # Map from antidote model route hints
    if normalized_subpattern in ("simplification", "prioritization"):
        if any(cue in evidence_text for cue in _JARGON_TOKENS):
            return "jargon-masking-shallow-analysis"
        return "procedural-noise-crowds-substance"
    if normalized_subpattern in ("occams-razor", "occams_razor"):
        return "jargon-masking-shallow-analysis"
    if normalized_subpattern in ("power-laws", "power_laws", "pareto-principle", "pareto_principle",
                                  "leverage-points", "leverage_points"):
        return "effort-spread-not-concentrated"
    if normalized_subpattern in ("lean-startup-methodology", "lean_startup_methodology",
                                  "lindy-effect", "lindy_effect", "specialization"):
        return "effort-spread-not-concentrated"

    # Evidence-based refinement
    jargon_hits = sum(1 for cue in _JARGON_TOKENS if cue in evidence_text)
    if jargon_hits >= 2:
        return "jargon-masking-shallow-analysis"

    effort_hits = sum(1 for cue in _EFFORT_SPREAD_TOKENS if cue in evidence_text)
    if effort_hits >= 2:
        return "effort-spread-not-concentrated"

    procedure_hits = sum(1 for cue in _PROCEDURAL_TOKENS if cue in evidence_text)
    if procedure_hits >= 2:
        return "procedural-noise-crowds-substance"

    return "general"


def _normalize(value: object) -> str:
    return str(value or "").strip().replace("_", "-").lower()


_PROCEDURAL_TOKENS = (
    "process detail",
    "administrative",
    "qualification",
    "scaffolding",
    "procedure",
    "bureaucra",
    "governance step",
    "approval process",
    "review cycle",
    "coordination",
    "compliance step",
)

_EFFORT_SPREAD_TOKENS = (
    "evenly",
    "spread across",
    "distributed",
    "equal attention",
    "all items",
    "comprehensive",
    "exhaustive",
    "every dimension",
    "no prioriti",
    "leverage point",
    "critical few",
)

_JARGON_TOKENS = (
    "jargon",
    "framework",
    "terminology",
    "buzzword",
    "elaborate",
    "complex language",
    "opaque",
    "incoherent",
    "substance",
    "shallow",
    "empty",
)
