from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .authority_deep_check_packet_adapter import (
    AuthorityDeepCheckPacketAdapter,
    AuthorityPacketAdaptation,
)
from .deep_checks import DeepCheckResult
from .pilot_pipeline import PilotPipeline, PilotResult


@dataclass(frozen=True)
class AuthorityPilotBridgeResult:
    adaptation: AuthorityPacketAdaptation
    pilot_result: PilotResult | None = None


class AuthorityPilotBridge:
    def __init__(
        self,
        *,
        adapter: AuthorityDeepCheckPacketAdapter,
        pipeline: PilotPipeline,
    ) -> None:
        self._adapter = adapter
        self._pipeline = pipeline

    @classmethod
    def load(cls, root: Path) -> "AuthorityPilotBridge":
        root = Path(root)
        return cls(
            adapter=AuthorityDeepCheckPacketAdapter.load(root),
            pipeline=PilotPipeline.load(root),
        )

    def run(self, result: DeepCheckResult) -> AuthorityPilotBridgeResult:
        adaptation = self._adapter.adapt(result)
        if adaptation.packet is None:
            return AuthorityPilotBridgeResult(adaptation=adaptation, pilot_result=None)
        return AuthorityPilotBridgeResult(
            adaptation=adaptation,
            pilot_result=self._pipeline.run(adaptation.packet),
        )
