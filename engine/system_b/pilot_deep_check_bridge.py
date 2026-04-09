from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .deep_check_packet_adapter import PacketAdaptation, PilotDeepCheckPacketAdapter
from .deep_checks import DeepCheckResult
from .pilot_pipeline import PilotPipeline, PilotResult


@dataclass(frozen=True)
class PilotDeepCheckBridgeResult:
    adaptation: PacketAdaptation
    pilot_result: PilotResult | None = None


class PilotDeepCheckBridge:
    def __init__(
        self,
        adapter: PilotDeepCheckPacketAdapter,
        pipeline: PilotPipeline,
    ) -> None:
        self._adapter = adapter
        self._pipeline = pipeline

    @classmethod
    def load(cls, root: Path) -> "PilotDeepCheckBridge":
        root = Path(root)
        return cls(
            adapter=PilotDeepCheckPacketAdapter.load(root),
            pipeline=PilotPipeline.load(root),
        )

    def run(self, result: DeepCheckResult) -> PilotDeepCheckBridgeResult:
        adaptation = self._adapter.adapt(result)
        if adaptation.packet is None:
            return PilotDeepCheckBridgeResult(adaptation=adaptation, pilot_result=None)
        return PilotDeepCheckBridgeResult(
            adaptation=adaptation,
            pilot_result=self._pipeline.run(adaptation.packet),
        )
