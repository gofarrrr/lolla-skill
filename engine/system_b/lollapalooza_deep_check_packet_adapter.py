from __future__ import annotations

from dataclasses import dataclass

from .deep_check_packet import DeepCheckPacket
from .deep_checks import DeepCheckResult
from .subpattern_catalog import SubpatternCatalog


@dataclass(frozen=True)
class LollapaloozaPacketAdaptation:
    source_tendency_id: str
    source_sub_pattern: str
    mapped_subpattern_id: str
    adaptation_mode: str
    warnings: tuple[str, ...] = ()
    packet: DeepCheckPacket | None = None


class LollapaloozaDeepCheckPacketAdapter:
    def __init__(self, *, subpatterns: SubpatternCatalog) -> None:
        self._subpatterns = subpatterns

    @classmethod
    def load(cls, root) -> "LollapaloozaDeepCheckPacketAdapter":
        return cls(subpatterns=SubpatternCatalog.load(root))

    def adapt(self, result: DeepCheckResult) -> LollapaloozaPacketAdaptation:
        if _normalize(result.tendency_id) != "lollapalooza-tendency":
            return LollapaloozaPacketAdaptation(
                source_tendency_id=result.tendency_id,
                source_sub_pattern=result.sub_pattern,
                mapped_subpattern_id="",
                adaptation_mode="unsupported-tendency",
                warnings=("unsupported-tendency",),
                packet=None,
            )
        if not result.detected:
            return LollapaloozaPacketAdaptation(
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
                warnings.append("unmapped-lollapalooza-subpattern")

        packet = DeepCheckPacket(
            tendency_id="lollapalooza-tendency",
            subpattern_id=mapped_subpattern_id,
            quoted_evidence_span=result.specific_passage,
            structural_fingerprint=result.evidence,
            fingerprint_quality="mixed",
            reasoning_failure_mechanism=result.evidence,
            severity=result.severity,
            signal_tags=(),
        )
        return LollapaloozaPacketAdaptation(
            source_tendency_id=result.tendency_id,
            source_sub_pattern=result.sub_pattern,
            mapped_subpattern_id=mapped_subpattern_id,
            adaptation_mode=adaptation_mode,
            warnings=tuple(warnings),
            packet=packet,
        )

    def _map_subpattern(self, result: DeepCheckResult) -> str:
        if not self._subpatterns.has_tendency("lollapalooza-tendency"):
            return "general"
        mapped = map_lollapalooza_result_to_subpattern(result)
        if mapped == "general":
            return "general"
        try:
            self._subpatterns.subpattern_for("lollapalooza-tendency", mapped)
        except KeyError:
            return "general"
        return mapped


def map_lollapalooza_result_to_subpattern(result: DeepCheckResult) -> str:
    normalized_subpattern = _normalize(result.sub_pattern)
    evidence_text = " ".join(
        [
            str(result.evidence or "").strip().lower(),
            str(result.specific_passage or "").strip().lower(),
        ]
    )

    # Direct subpattern matches
    if normalized_subpattern == "undiagnosed-tendency-compounding":
        return "undiagnosed-tendency-compounding"
    if normalized_subpattern == "cascade-effects-treated-in-isolation":
        return "cascade-effects-treated-in-isolation"
    if normalized_subpattern == "missing-structural-firebreak":
        return "missing-structural-firebreak"

    # Map from antidote model route hints
    if normalized_subpattern in ("synthesis-and-integration", "synthesis_and_integration"):
        return "undiagnosed-tendency-compounding"
    if normalized_subpattern in ("second-order-thinking", "second_order_thinking"):
        return "cascade-effects-treated-in-isolation"
    if normalized_subpattern in ("constraints", "step-back", "step_back"):
        return "missing-structural-firebreak"
    if normalized_subpattern in ("checklists",):
        # Checklists can serve multiple shapes — check evidence
        if any(cue in evidence_text for cue in _FIREBREAK_TOKENS):
            return "missing-structural-firebreak"
        if any(cue in evidence_text for cue in _CASCADE_TOKENS):
            return "cascade-effects-treated-in-isolation"
        return "undiagnosed-tendency-compounding"
    if normalized_subpattern in ("decomposition",):
        # Decomposition can serve cascade or compounding — check evidence
        if any(cue in evidence_text for cue in _CASCADE_TOKENS):
            return "cascade-effects-treated-in-isolation"
        return "undiagnosed-tendency-compounding"
    if normalized_subpattern in (
        "combinatorial-effects", "combinatorial_effects",
        "latticework-of-mental-models", "latticework_of_mental_models",
    ):
        # Core models — disambiguate by evidence
        if any(cue in evidence_text for cue in _FIREBREAK_TOKENS):
            return "missing-structural-firebreak"
        if any(cue in evidence_text for cue in _CASCADE_TOKENS):
            return "cascade-effects-treated-in-isolation"
        return "undiagnosed-tendency-compounding"

    # Evidence-based refinement for unknown route hints
    compounding_hits = sum(1 for cue in _COMPOUNDING_TOKENS if cue in evidence_text)
    if compounding_hits >= 2:
        return "undiagnosed-tendency-compounding"

    cascade_hits = sum(1 for cue in _CASCADE_TOKENS if cue in evidence_text)
    if cascade_hits >= 2:
        return "cascade-effects-treated-in-isolation"

    firebreak_hits = sum(1 for cue in _FIREBREAK_TOKENS if cue in evidence_text)
    if firebreak_hits >= 2:
        return "missing-structural-firebreak"

    return "general"


def _normalize(value: object) -> str:
    return str(value or "").strip().replace("_", "-").lower()


_COMPOUNDING_TOKENS = (
    "multiple tendencies",
    "reinforce",
    "compounding",
    "confluence",
    "acting in concert",
    "interact",
    "combination",
    "simultaneously",
    "together",
    "amplif",
    "mutual",
)

_CASCADE_TOKENS = (
    "cascade",
    "second-order",
    "third-order",
    "downstream",
    "non-linear",
    "chain reaction",
    "domino",
    "spiral",
    "escalat",
    "propagat",
)

_FIREBREAK_TOKENS = (
    "firebreak",
    "no checklist",
    "no constraint",
    "no mechanism",
    "unchecked",
    "no isolation",
    "no safeguard",
    "no structural",
    "missing process",
    "no decomposition",
    "prevent",
)
