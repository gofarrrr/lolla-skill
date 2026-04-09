from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .deep_check_packet import DeepCheckPacket
from .deep_checks import DeepCheckResult
from .subpattern_catalog import SubpatternCatalog


@dataclass(frozen=True)
class InconsistencyAvoidancePacketAdaptation:
    source_tendency_id: str
    source_sub_pattern: str
    mapped_subpattern_id: str
    adaptation_mode: str
    warnings: tuple[str, ...] = ()
    packet: DeepCheckPacket | None = None


class InconsistencyAvoidanceDeepCheckPacketAdapter:
    def __init__(self, *, subpatterns: SubpatternCatalog) -> None:
        self._subpatterns = subpatterns

    @classmethod
    def load(cls, root) -> "InconsistencyAvoidanceDeepCheckPacketAdapter":
        return cls(subpatterns=SubpatternCatalog.load(root))

    def adapt(self, result: DeepCheckResult) -> InconsistencyAvoidancePacketAdaptation:
        if _normalize(result.tendency_id) != "inconsistency-avoidance-tendency":
            return InconsistencyAvoidancePacketAdaptation(
                source_tendency_id=result.tendency_id,
                source_sub_pattern=result.sub_pattern,
                mapped_subpattern_id="",
                adaptation_mode="unsupported-tendency",
                warnings=("unsupported-tendency",),
                packet=None,
            )
        if not result.detected:
            return InconsistencyAvoidancePacketAdaptation(
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
            if _normalize(result.sub_pattern) not in ("", "general", "step-back", "step_back"):
                warnings.append("unmapped-inconsistency-avoidance-subpattern")

        packet = DeepCheckPacket(
            tendency_id="inconsistency-avoidance-tendency",
            subpattern_id=mapped_subpattern_id,
            quoted_evidence_span=result.specific_passage,
            structural_fingerprint=result.evidence,
            fingerprint_quality="mixed",
            reasoning_failure_mechanism=result.evidence,
            severity=result.severity,
            signal_tags=(),
        )
        return InconsistencyAvoidancePacketAdaptation(
            source_tendency_id=result.tendency_id,
            source_sub_pattern=result.sub_pattern,
            mapped_subpattern_id=mapped_subpattern_id,
            adaptation_mode=adaptation_mode,
            warnings=tuple(warnings),
            packet=packet,
        )

    def _map_subpattern(self, result: DeepCheckResult) -> str:
        return map_inconsistency_avoidance_result_to_subpattern(
            result,
            has_subpattern=self._has_subpattern,
        )

    def _has_subpattern(self, subpattern_id: str) -> bool:
        try:
            self._subpatterns.subpattern_for("inconsistency-avoidance-tendency", subpattern_id)
        except KeyError:
            return False
        return True


def _normalize(value: object) -> str:
    return str(value or "").strip().replace("_", "-").lower()


def _has_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)


_LEGACY_ROUTE_HINT_MAP = {
    "general": "general",
    "iteration": "escalation-of-prior-design",
    "first-principles-thinking": "exception-to-preserve-plan",
    "first_principles_thinking": "exception-to-preserve-plan",
}


def map_inconsistency_avoidance_result_to_subpattern(
    result: DeepCheckResult,
    *,
    has_subpattern: Callable[[str], bool] | None = None,
) -> str:
    normalized = _normalize(result.sub_pattern)
    direct = _LEGACY_ROUTE_HINT_MAP.get(normalized)
    if direct and direct != "general":
        if has_subpattern is None or has_subpattern(direct):
            return direct
        return "general"

    evidence_text = " ".join(
        part for part in (result.evidence, result.specific_passage) if str(part or "").strip()
    ).lower()

    if _has_any(
        evidence_text,
        (
            "unresolved",
            "remaining terms",
            "legal terms",
            "data terms",
            "secondary",
            "already signaled",
            "already committed",
            "announcement",
            "later paperwork",
        ),
    ):
        return "commitment-before-resolution"

    if _has_any(
        evidence_text,
        (
            "familiar",
            "proven vendor",
            "existing vendor",
            "current setup",
            "status quo",
            "switching cost",
            "switching discomfort",
            "renewal",
            "renew",
            "incumbent",
            "avoid disruption",
        ),
    ):
        return "status-quo-protection"

    if _has_any(
        evidence_text,
        (
            "exception",
            "policy exception",
            "bypass",
            "waive",
            "bend the rule",
            "relax the rule",
            "fast-track approval",
        ),
    ):
        return "exception-to-preserve-plan"

    if _has_any(
        evidence_text,
        (
            "roll out",
            "full rollout",
            "full transition",
            "redesign",
            "comp plan",
            "new design",
            "scale now",
            "immediate rollout",
            "pilot later",
        ),
    ):
        return "escalation-of-prior-design"

    return "general"
