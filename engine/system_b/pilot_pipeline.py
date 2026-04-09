from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .compiled_substrate import CompiledChunk, CompiledSubstrate
from .deep_check_packet import DeepCheckPacket
from .fingerprint_audit import FingerprintAudit, FingerprintAuditor
from .pressure_bundle_selector import PressureBundle, PressureBundleSelector


@dataclass(frozen=True)
class PilotTrace:
    packet: DeepCheckPacket
    selected_chunks: tuple[CompiledChunk, ...] = ()
    fingerprint_audit: FingerprintAudit | None = None


@dataclass(frozen=True)
class PilotResult:
    bundle: PressureBundle
    trace: PilotTrace


class PilotPipeline:
    def __init__(
        self,
        selector: PressureBundleSelector,
        substrate: CompiledSubstrate,
        fingerprint_auditor: FingerprintAuditor,
    ) -> None:
        self._selector = selector
        self._substrate = substrate
        self._fingerprint_auditor = fingerprint_auditor

    @classmethod
    def load(cls, root: Path) -> "PilotPipeline":
        root = Path(root)
        return cls(
            selector=PressureBundleSelector.load(root),
            substrate=CompiledSubstrate.load(root),
            fingerprint_auditor=FingerprintAuditor.load(root),
        )

    def run(self, packet: DeepCheckPacket) -> PilotResult:
        bundle = self._selector.select_from_packet(packet)
        selected_chunks = self._substrate.chunks_by_id(bundle.selected_chunk_ids)
        fingerprint_audit = self._fingerprint_auditor.audit(packet)
        return PilotResult(
            bundle=bundle,
            trace=PilotTrace(
                packet=packet,
                selected_chunks=selected_chunks,
                fingerprint_audit=fingerprint_audit,
            ),
        )
