"""Tolerant substring matching for LLM-quoted evidence.

LLMs at non-zero temperature occasionally fail character-exact substring
validation for legitimate quotes by lowercasing the first character of a
passage (e.g., transcript: "You should…"; LLM cites: "you should…"). The
content is correct but capitalization drifts when the LLM pulls a passage
from mid-sentence in the transcript into its own output where the passage
no longer sits at a sentence boundary.

This module provides narrow tolerant fallbacks: try exact match first, then
case-insensitive, then retry after removing a symmetric quote wrapper around
the whole needle. The fallbacks preserve the architectural contract that
evidence must come from the actual transcript (not paraphrase), while
eliminating common spurious rejection modes.

Shared between `scripts/run_extract.py::_validate_passages` (extraction-level
reasoning_passages validation) and `engine/system_b/frame_pressure.py::
_evidence_in_text` (Lane 3 frame-element evidence validation).
"""

from __future__ import annotations

import logging

_LOGGER = logging.getLogger("system_b.text_matching")

_QUOTE_WRAPPERS = {
    '"': '"',
    "'": "'",
    "“": "”",
    "‘": "’",
    "«": "»",
}


def find_substring_tolerant(needle: str, haystack: str) -> str | None:
    """Find ``needle`` in ``haystack`` with narrow quote-safe tolerances.

    Returns the substring from ``haystack`` with its original casing preserved
    if found either exactly or via case-insensitive match. Returns ``None``
    when neither match succeeds — this is the signal that the quote is a
    paraphrase or hallucination, not a legitimate case-folded quote.

    When the match succeeds only via a fallback, emits an INFO-level log so
    operators can measure how often LLMs case-fold or wrap quotations in
    practice.

    The helper intentionally tolerates ONLY case differences and a symmetric
    quote wrapper around the entire needle. Whitespace, punctuation, and
    word-substitution differences are all rejected — those are paraphrase or
    hallucination signatures that the substring validation is supposed to catch.
    """
    if not needle or not haystack:
        return None
    matched = _find_exact_or_casefolded(needle, haystack)
    if matched is not None:
        return matched
    stripped = _strip_symmetric_quote_wrapper(needle)
    if stripped == needle:
        return None
    matched = _find_exact_or_casefolded(stripped, haystack)
    if matched is None:
        return None
    _LOGGER.info(
        "text_matching.quote_wrapper_fallback: accepted %r (transcript: %r)",
        needle[:80], matched[:80],
    )
    return matched


def _find_exact_or_casefolded(needle: str, haystack: str) -> str | None:
    if needle in haystack:
        return needle
    idx = haystack.casefold().find(needle.casefold())
    if idx == -1:
        return None
    matched = haystack[idx:idx + len(needle)]
    _LOGGER.info(
        "text_matching.case_insensitive_fallback: accepted %r (transcript: %r)",
        needle[:80], matched[:80],
    )
    return matched


def _strip_symmetric_quote_wrapper(text: str) -> str:
    stripped = text.strip()
    if len(stripped) < 2:
        return text
    closer = _QUOTE_WRAPPERS.get(stripped[0])
    if closer and stripped[-1] == closer:
        return stripped[1:-1]
    return text
