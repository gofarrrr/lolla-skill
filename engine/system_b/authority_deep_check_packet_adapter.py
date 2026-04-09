from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .deep_check_packet import DeepCheckPacket
from .deep_checks import DeepCheckResult
from .subpattern_catalog import SubpatternCatalog


@dataclass(frozen=True)
class AuthorityPacketAdaptation:
    source_tendency_id: str
    source_sub_pattern: str
    mapped_subpattern_id: str
    adaptation_mode: str
    warnings: tuple[str, ...] = ()
    packet: DeepCheckPacket | None = None


class AuthorityDeepCheckPacketAdapter:
    def __init__(self, *, subpatterns: SubpatternCatalog) -> None:
        self._subpatterns = subpatterns

    @classmethod
    def load(cls, root: Path) -> "AuthorityDeepCheckPacketAdapter":
        return cls(subpatterns=SubpatternCatalog.load(root))

    def adapt(self, result: DeepCheckResult) -> AuthorityPacketAdaptation:
        if _normalize(result.tendency_id) != "authority-misinfluence-tendency":
            return AuthorityPacketAdaptation(
                source_tendency_id=result.tendency_id,
                source_sub_pattern=result.sub_pattern,
                mapped_subpattern_id="",
                adaptation_mode="unsupported-tendency",
                warnings=("unsupported-tendency",),
                packet=None,
            )
        if not result.detected:
            return AuthorityPacketAdaptation(
                source_tendency_id=result.tendency_id,
                source_sub_pattern=result.sub_pattern,
                mapped_subpattern_id="",
                adaptation_mode="not-detected",
                warnings=("not-detected",),
                packet=None,
            )

        mapped_subpattern_id = self._map_subpattern(result)
        warnings: list[str] = []
        adaptation_mode = "exact-subpattern"
        if mapped_subpattern_id == "general":
            refined_subpattern_id = self._refine_general_subpattern(result)
            if refined_subpattern_id != "general":
                mapped_subpattern_id = refined_subpattern_id
                adaptation_mode = f"general-refined-to-{refined_subpattern_id}"
                warnings.append("authority-general-refined-from-evidence")
            else:
                adaptation_mode = "general-fallback"
        if mapped_subpattern_id == "general":
            adaptation_mode = "general-fallback"
            if _normalize(result.sub_pattern) not in ("", "general"):
                warnings.append("unmapped-authority-subpattern")

        packet = DeepCheckPacket(
            tendency_id="authority-misinfluence-tendency",
            subpattern_id=mapped_subpattern_id,
            quoted_evidence_span=result.specific_passage,
            structural_fingerprint=result.evidence,
            fingerprint_quality="mixed",
            reasoning_failure_mechanism=result.evidence,
            severity=result.severity,
            signal_tags=(),
        )
        return AuthorityPacketAdaptation(
            source_tendency_id=result.tendency_id,
            source_sub_pattern=result.sub_pattern,
            mapped_subpattern_id=mapped_subpattern_id,
            adaptation_mode=adaptation_mode,
            warnings=tuple(warnings),
            packet=packet,
        )

    def _map_subpattern(self, result: DeepCheckResult) -> str:
        if not self._subpatterns.has_tendency("authority-misinfluence-tendency"):
            return "general"
        mapped_subpattern_id = map_authority_result_to_subpattern(result)
        if mapped_subpattern_id == "general":
            return "general"
        try:
            self._subpatterns.subpattern_for("authority-misinfluence-tendency", mapped_subpattern_id)
        except KeyError:
            return "general"
        return mapped_subpattern_id

    def _refine_general_subpattern(self, result: DeepCheckResult) -> str:
        return map_authority_result_to_subpattern(result)


def map_authority_result_to_subpattern(result: DeepCheckResult) -> str:
    normalized_subpattern = _normalize(result.sub_pattern)
    evidence_text = " ".join(
        [
            str(result.evidence or "").strip().lower(),
            str(result.specific_passage or "").strip().lower(),
        ]
    )

    if normalized_subpattern == "authority-overrides-protocol":
        return "authority-overrides-protocol"
    if normalized_subpattern == "prestige-cue-substitution":
        return "prestige-cue-substitution"
    if normalized_subpattern == "deference-overrides-verification":
        return "deference-overrides-verification"

    protocol_authority_hits = sum(1 for cue in _PROTOCOL_AUTHORITY_TOKENS if cue in evidence_text)
    protocol_override_hits = sum(1 for cue in _PROTOCOL_OVERRIDE_TOKENS if cue in evidence_text)
    if protocol_authority_hits >= 1 and protocol_override_hits >= 1:
        return "authority-overrides-protocol"

    prestige_hits = sum(1 for cue in _PRESTIGE_CUE_TOKENS if cue in evidence_text)
    substitution_hits = sum(1 for cue in _SUBSTITUTION_TOKENS if cue in evidence_text)
    if prestige_hits >= 1 and substitution_hits >= 1:
        if any(cue in evidence_text for cue in _PROTOCOL_OVERRIDE_TOKENS):
            return "authority-overrides-protocol"
        return "prestige-cue-substitution"

    if normalized_subpattern in {
        "",
        "general",
        "dialectical-reasoning",
        "first-principles-thinking",
    } and substitution_hits >= 1:
        return "deference-overrides-verification"
    return "general"


def _normalize(value: object) -> str:
    return str(value or "").strip().replace("_", "-").lower()


_PRESTIGE_CUE_TOKENS = (
    "trusted source",
    "trusted colleague",
    "referral",
    "vetted",
    "game-changer",
    "title",
    "brand",
    "prestige",
    "credential",
    "expertise",
    "cto",
    "cio",
    "sponsor",
)

_SUBSTITUTION_TOKENS = (
    "validation",
    "proof",
    "evidence",
    "independent check",
    "independent evidence",
    "reference check",
    "skills assessment",
    "substituting for",
    "substitute for technical security evidence",
    "substitute for technical evidence",
    "personal vouching",
    "provides reasonable assurance",
    "reasonable assurance",
    "lowers hiring risk",
    "significantly lowers",
)

_PROTOCOL_AUTHORITY_TOKENS = (
    "strategic importance",
    "strategically important",
    "tier-one market leader",
    "enterprise prospect",
    "executive",
    "sponsor",
    "senior",
    "authority",
    "cto-level sponsor",
    "high-ranking executive",
    "high ranking executive",
    "personal vouching",
)

_PROTOCOL_OVERRIDE_TOKENS = (
    "bypass controls",
    "bypass standing controls",
    "override standard security policy",
    "override security policy",
    "override policy",
    "standing controls",
    "challenge rights",
    "one-time exception",
    "audit exception",
    "grant the exception",
    "normal control path",
    "policy",
    "controls",
    "security team flagged",
    "technical security evidence",
    "security posture",
    "security review",
    "protocol standards",
    "authentication protocol",
    "temporary flexibility",
)
