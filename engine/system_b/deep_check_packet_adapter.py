from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .deep_check_packet import DeepCheckPacket
from .deep_checks import DeepCheckResult
from .subpattern_catalog import SubpatternCatalog


_OVEROPTIMISM_TENDENCY_ID = "overoptimism-tendency"
_GENERAL_SUBPATTERN_ID = "general"
_LEGACY_ROUTE_HINT_MAP = {
    "general": _GENERAL_SUBPATTERN_ID,
    "trade-offs": _GENERAL_SUBPATTERN_ID,
    "trade_offs": _GENERAL_SUBPATTERN_ID,
    "conjunction-fallacy": "conjunctive-plan-neglect",
    "conjunction_fallacy": "conjunctive-plan-neglect",
    "true-uncertainty-navigation": "single-scenario-forecasting",
    "true_uncertainty_navigation": "single-scenario-forecasting",
    "risk-vs-uncertainty": "single-scenario-forecasting",
    "risk_vs_uncertainty": "single-scenario-forecasting",
    "base-rates": "missing-denominator",
    "base_rates": "missing-denominator",
    "premortem": "missing-reversal-condition",
}


@dataclass(frozen=True)
class PacketAdaptation:
    packet: DeepCheckPacket | None
    source_tendency_id: str
    source_sub_pattern: str = ""
    mapped_subpattern_id: str = ""
    adaptation_mode: str = ""
    warnings: tuple[str, ...] = ()


class PilotDeepCheckPacketAdapter:
    def __init__(self, catalog: SubpatternCatalog) -> None:
        self._catalog = catalog

    @classmethod
    def load(cls, root: Path) -> "PilotDeepCheckPacketAdapter":
        return cls(SubpatternCatalog.load(root))

    def adapt(self, result: DeepCheckResult) -> PacketAdaptation:
        tendency_id = _normalize_id(result.tendency_id)
        source_sub_pattern = _normalize_id(result.sub_pattern)

        if not result.detected:
            return PacketAdaptation(
                packet=None,
                source_tendency_id=tendency_id,
                source_sub_pattern=source_sub_pattern,
                adaptation_mode="not-detected",
                warnings=("deep-check-not-detected",),
            )

        if tendency_id != _OVEROPTIMISM_TENDENCY_ID:
            return PacketAdaptation(
                packet=None,
                source_tendency_id=tendency_id,
                source_sub_pattern=source_sub_pattern,
                adaptation_mode="unsupported-tendency",
                warnings=("unsupported-tendency-for-pilot-adapter",),
            )

        mapped_subpattern_id, adaptation_mode, warnings = self._map_subpattern(
            tendency_id=tendency_id,
            source_sub_pattern=source_sub_pattern,
        )
        signal_tags = self._signal_tags_for(
            tendency_id=tendency_id,
            subpattern_id=mapped_subpattern_id,
        )
        packet = DeepCheckPacket(
            tendency_id=tendency_id,
            subpattern_id=mapped_subpattern_id,
            quoted_evidence_span=result.specific_passage,
            structural_fingerprint=result.evidence,
            fingerprint_quality="",
            reasoning_failure_mechanism=result.evidence,
            severity=result.severity,
            signal_tags=signal_tags,
        )
        return PacketAdaptation(
            packet=packet,
            source_tendency_id=tendency_id,
            source_sub_pattern=source_sub_pattern,
            mapped_subpattern_id=mapped_subpattern_id,
            adaptation_mode=adaptation_mode,
            warnings=warnings,
        )

    def _map_subpattern(
        self,
        *,
        tendency_id: str,
        source_sub_pattern: str,
    ) -> tuple[str, str, tuple[str, ...]]:
        warnings: list[str] = []
        if not source_sub_pattern:
            return _GENERAL_SUBPATTERN_ID, "general-fallback", ("missing-legacy-route-hint",)

        mapped_subpattern_id = _LEGACY_ROUTE_HINT_MAP.get(source_sub_pattern)
        if mapped_subpattern_id is None:
            return _GENERAL_SUBPATTERN_ID, "general-fallback", ("unmapped-legacy-route-hint",)

        if not self._has_subpattern(tendency_id=tendency_id, subpattern_id=mapped_subpattern_id):
            warnings.append("mapped-subpattern-not-compiled")
            warnings.append("fallback-to-general")
            return _GENERAL_SUBPATTERN_ID, "general-fallback", tuple(warnings)

        return mapped_subpattern_id, "mapped-route-hint", ()

    def _has_subpattern(self, *, tendency_id: str, subpattern_id: str) -> bool:
        try:
            self._catalog.subpattern_for(tendency_id, subpattern_id)
        except KeyError:
            return False
        return True

    def _signal_tags_for(
        self,
        *,
        tendency_id: str,
        subpattern_id: str,
    ) -> tuple[str, ...]:
        try:
            return self._catalog.subpattern_for(tendency_id, subpattern_id).signal_tags
        except KeyError:
            return ()


def _normalize_id(value: object) -> str:
    return str(value or "").strip().replace("_", "-").lower()
