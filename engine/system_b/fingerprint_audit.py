from __future__ import annotations

from dataclasses import dataclass
import re
from pathlib import Path

from .deep_check_packet import DeepCheckPacket
from .structural_signal_lexicon import StructuralSignalLexicon


@dataclass(frozen=True)
class FingerprintAudit:
    assessed_quality: str
    warnings: tuple[str, ...] = ()
    expected_signal_tags: tuple[str, ...] = ()
    matched_signal_tags: tuple[str, ...] = ()
    operator_hits: tuple[str, ...] = ()
    cue_hits: tuple[str, ...] = ()
    quote_token_overlap_ratio: float = 0.0


class FingerprintAuditor:
    def __init__(self, lexicon: StructuralSignalLexicon) -> None:
        self._lexicon = lexicon

    @classmethod
    def load(cls, root: Path) -> "FingerprintAuditor":
        return cls(StructuralSignalLexicon.load(root))

    def audit(self, packet: DeepCheckPacket) -> FingerprintAudit:
        profile = self._lexicon.profile_for(packet.tendency_id, packet.subpattern_id)
        expected_signal_tags = profile.signal_tags if profile is not None else ()
        cue_phrases = profile.cue_phrases if profile is not None else ()
        fingerprint_text = packet.structural_fingerprint.strip()
        fingerprint_lower = fingerprint_text.lower()
        quote_tokens = _content_tokens(packet.quoted_evidence_span, self._lexicon.stopwords)
        fingerprint_tokens = _content_tokens(fingerprint_text, self._lexicon.stopwords)
        overlap_ratio = _overlap_ratio(quote_tokens, fingerprint_tokens)
        operator_hits = tuple(
            operator
            for operator in self._lexicon.operators
            if operator.lower() in fingerprint_lower
        )
        cue_hits = tuple(
            cue
            for cue in cue_phrases
            if cue.lower() in fingerprint_lower
        )
        matched_signal_tags = tuple(
            signal_tag
            for signal_tag in expected_signal_tags
            if signal_tag in packet.signal_tags
        )

        warnings: list[str] = []
        if overlap_ratio >= 0.6:
            warnings.append("fingerprint-overlaps-quoted-evidence")
        if not operator_hits and not cue_hits:
            warnings.append("fingerprint-lacks-structural-cues")
        if expected_signal_tags and not matched_signal_tags:
            warnings.append("packet-misses-subpattern-signals")

        assessed_quality = _assess_quality(
            overlap_ratio=overlap_ratio,
            has_structural_cues=bool(operator_hits or cue_hits),
        )
        reported_quality = _normalize_quality(packet.fingerprint_quality)
        if reported_quality and reported_quality != assessed_quality:
            warnings.append("reported-fingerprint-quality-mismatch")

        return FingerprintAudit(
            assessed_quality=assessed_quality,
            warnings=tuple(warnings),
            expected_signal_tags=expected_signal_tags,
            matched_signal_tags=matched_signal_tags,
            operator_hits=operator_hits,
            cue_hits=cue_hits,
            quote_token_overlap_ratio=round(overlap_ratio, 3),
        )


def _assess_quality(
    *,
    overlap_ratio: float,
    has_structural_cues: bool,
) -> str:
    if has_structural_cues and overlap_ratio < 0.45:
        return "structural"
    if has_structural_cues and overlap_ratio < 0.7:
        return "mixed"
    return "topical"


def _content_tokens(text: str, stopwords: tuple[str, ...]) -> set[str]:
    stopword_set = {word.lower() for word in stopwords}
    tokens: set[str] = set()
    for token in re.findall(r"[a-z0-9]+", text.lower()):
        if len(token) <= 2:
            continue
        if token in stopword_set:
            continue
        tokens.add(token)
    return tokens


def _overlap_ratio(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / float(max(len(right), 1))


def _normalize_quality(value: str) -> str:
    return str(value or "").strip().lower()
