from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .deep_checks import DeepCheckResult
from .pilot_pipeline import PilotPipeline, PilotResult
from .stress_deep_check_packet_adapter import StressDeepCheckPacketAdapter, StressPacketAdaptation


@dataclass(frozen=True)
class StressPilotBridgeResult:
    adaptation: StressPacketAdaptation
    pilot_result: PilotResult | None = None


class StressPilotBridge:
    def __init__(
        self,
        *,
        adapter: StressDeepCheckPacketAdapter,
        pipeline: PilotPipeline,
    ) -> None:
        self._adapter = adapter
        self._pipeline = pipeline

    @classmethod
    def load(cls, root: Path) -> "StressPilotBridge":
        root = Path(root)
        return cls(
            adapter=StressDeepCheckPacketAdapter.load(root),
            pipeline=PilotPipeline.load(root),
        )

    def run(self, result: DeepCheckResult) -> StressPilotBridgeResult:
        adaptation = self._adapter.adapt(result)
        if adaptation.packet is None:
            return StressPilotBridgeResult(adaptation=adaptation, pilot_result=None)
        return StressPilotBridgeResult(
            adaptation=adaptation,
            pilot_result=self._pipeline.run(adaptation.packet),
        )

