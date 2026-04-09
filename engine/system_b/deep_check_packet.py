from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DeepCheckPacket:
    tendency_id: str
    subpattern_id: str = "general"
    quoted_evidence_span: str = ""
    structural_fingerprint: str = ""
    fingerprint_quality: str = ""
    reasoning_failure_mechanism: str = ""
    severity: str = ""
    signal_tags: tuple[str, ...] = ()
