from __future__ import annotations

from dataclasses import dataclass

from .deep_check_packet import DeepCheckPacket
from .deep_checks import DeepCheckResult
from .subpattern_catalog import SubpatternCatalog


@dataclass(frozen=True)
class SocialProofPacketAdaptation:
    source_tendency_id: str
    source_sub_pattern: str
    mapped_subpattern_id: str
    adaptation_mode: str
    warnings: tuple[str, ...] = ()
    packet: DeepCheckPacket | None = None


class SocialProofDeepCheckPacketAdapter:
    def __init__(self, *, subpatterns: SubpatternCatalog) -> None:
        self._subpatterns = subpatterns

    @classmethod
    def load(cls, root) -> "SocialProofDeepCheckPacketAdapter":
        return cls(subpatterns=SubpatternCatalog.load(root))

    def adapt(self, result: DeepCheckResult) -> SocialProofPacketAdaptation:
        if _normalize(result.tendency_id) != "social-proof-tendency":
            return SocialProofPacketAdaptation(
                source_tendency_id=result.tendency_id,
                source_sub_pattern=result.sub_pattern,
                mapped_subpattern_id="",
                adaptation_mode="unsupported-tendency",
                warnings=("unsupported-tendency",),
                packet=None,
            )
        if not result.detected:
            return SocialProofPacketAdaptation(
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
                warnings.append("unmapped-social-proof-subpattern")

        packet = DeepCheckPacket(
            tendency_id="social-proof-tendency",
            subpattern_id=mapped_subpattern_id,
            quoted_evidence_span=result.specific_passage,
            structural_fingerprint=result.evidence,
            fingerprint_quality="mixed",
            reasoning_failure_mechanism=result.evidence,
            severity=result.severity,
            signal_tags=(),
        )
        return SocialProofPacketAdaptation(
            source_tendency_id=result.tendency_id,
            source_sub_pattern=result.sub_pattern,
            mapped_subpattern_id=mapped_subpattern_id,
            adaptation_mode=adaptation_mode,
            warnings=tuple(warnings),
            packet=packet,
        )

    def _map_subpattern(self, source_sub_pattern: str) -> str:
        if not self._subpatterns.has_tendency("social-proof-tendency"):
            return "general"
        mapped = map_social_proof_result_to_subpattern_from_hint(source_sub_pattern)
        if mapped == "general":
            return "general"
        try:
            self._subpatterns.subpattern_for("social-proof-tendency", mapped)
        except KeyError:
            return "general"
        return mapped


def map_social_proof_result_to_subpattern(result: DeepCheckResult) -> str:
    normalized_subpattern = _normalize(result.sub_pattern)
    evidence_text = " ".join(
        [
            str(result.evidence or "").strip().lower(),
            str(result.specific_passage or "").strip().lower(),
        ]
    )

    # Direct subpattern matches
    if normalized_subpattern == "borrowed-consensus-as-proof":
        return "borrowed-consensus-as-proof"
    if normalized_subpattern == "stress-amplified-herd-following":
        return "stress-amplified-herd-following"
    if normalized_subpattern == "inaction-as-consensus-signal":
        return "inaction-as-consensus-signal"
    if normalized_subpattern == "contagious-normalization":
        return "contagious-normalization"

    # Map from antidote model route hints
    mapped = _LEGACY_ROUTE_HINT_MAP.get(normalized_subpattern)
    if mapped is not None and mapped != "general":
        return mapped

    # Evidence-based refinement
    consensus_hits = sum(1 for cue in _CONSENSUS_TOKENS if cue in evidence_text)
    if consensus_hits >= 2:
        return "borrowed-consensus-as-proof"

    herd_hits = sum(1 for cue in _HERD_TOKENS if cue in evidence_text)
    if herd_hits >= 2:
        return "stress-amplified-herd-following"

    inaction_hits = sum(1 for cue in _INACTION_TOKENS if cue in evidence_text)
    if inaction_hits >= 2:
        return "inaction-as-consensus-signal"

    normalization_hits = sum(1 for cue in _NORMALIZATION_TOKENS if cue in evidence_text)
    if normalization_hits >= 2:
        return "contagious-normalization"

    return "general"


def map_social_proof_result_to_subpattern_from_hint(source_sub_pattern: str) -> str:
    normalized = _normalize(source_sub_pattern)
    return _LEGACY_ROUTE_HINT_MAP.get(normalized, "general")


def _normalize(value: object) -> str:
    return str(value or "").strip().replace("_", "-").lower()


_LEGACY_ROUTE_HINT_MAP = {
    "general": "general",
    "first-principles-thinking": "general",
    "first_principles_thinking": "general",
    "peer-review-your-perspectives": "borrowed-consensus-as-proof",
    "peer_review_your_perspectives": "borrowed-consensus-as-proof",
    "step-back": "stress-amplified-herd-following",
    "step_back": "stress-amplified-herd-following",
    "six-thinking-hats": "inaction-as-consensus-signal",
    "six_thinking_hats": "inaction-as-consensus-signal",
    "brainstorming": "contagious-normalization",
}

_CONSENSUS_TOKENS = (
    "consensus",
    "everyone agrees",
    "industry standard",
    "best practice",
    "peer",
    "advisory council",
    "market adoption",
    "track record",
    "portfolio",
)

_HERD_TOKENS = (
    "herd",
    "panic",
    "rush",
    "fear of missing",
    "fomo",
    "bandwagon",
    "competitors are",
    "everyone is doing",
    "pressure to follow",
)

_INACTION_TOKENS = (
    "inaction",
    "silence",
    "no objection",
    "nobody raised",
    "absence of dissent",
    "quiet approval",
    "no one challenged",
    "default acceptance",
    "tacit",
)

_NORMALIZATION_TOKENS = (
    "normaliz",
    "accepted practice",
    "standard operating",
    "everyone does it",
    "common practice",
    "industry norm",
    "cultural",
    "contagious",
    "spread",
)
