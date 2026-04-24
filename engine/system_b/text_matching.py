"""Tolerant substring matching for LLM-quoted evidence.

LLMs at non-zero temperature occasionally fail character-exact substring
validation for legitimate quotes by lowercasing the first character of a
passage (e.g., transcript: "You should…"; LLM cites: "you should…"). The
content is correct but capitalization drifts when the LLM pulls a passage
from mid-sentence in the transcript into its own output where the passage
no longer sits at a sentence boundary.

This module provides a tolerant fallback: try exact match first, then
case-insensitive. The case-insensitive fallback preserves the architectural
contract that evidence must come from the actual transcript (not paraphrase),
while eliminating the most common spurious rejection mode.

Shared between `scripts/run_extract.py::_validate_passages` (extraction-level
reasoning_passages validation) and `engine/system_b/frame_pressure.py::
_evidence_in_text` (Lane 3 frame-element evidence validation).
"""

from __future__ import annotations

import logging

_LOGGER = logging.getLogger("system_b.text_matching")


def find_substring_tolerant(needle: str, haystack: str) -> str | None:
    """Find ``needle`` in ``haystack``, tolerant of case differences.

    Returns the substring from ``haystack`` with its original casing preserved
    if found either exactly or via case-insensitive match. Returns ``None``
    when neither match succeeds — this is the signal that the quote is a
    paraphrase or hallucination, not a legitimate case-folded quote.

    When the match succeeds only via the case-insensitive fallback, emits an
    INFO-level log (``text_matching.case_insensitive_fallback``) so operators
    can measure how often LLMs case-fold their quotations in practice.

    The helper intentionally tolerates ONLY case differences. Whitespace,
    punctuation, and word-substitution differences are all rejected — those
    are paraphrase or hallucination signatures that the substring validation
    is supposed to catch.
    """
    if not needle or not haystack:
        return None
    if needle in haystack:
        return needle
    idx = haystack.lower().find(needle.lower())
    if idx == -1:
        return None
    matched = haystack[idx:idx + len(needle)]
    _LOGGER.info(
        "text_matching.case_insensitive_fallback: accepted %r (transcript: %r)",
        needle[:80], matched[:80],
    )
    return matched
