"""Tests for case-tolerant substring matching.

Fixes the quote_fabrication false-reject class observed in production runs
where the LLM copies a passage verbatim from the transcript except that it
lowercases the first character (e.g., transcript has "You should…" and the
LLM cites "you should…"). Under character-exact substring validation the
quote is rejected even though the content is legitimately in the transcript.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.text_matching import find_substring_tolerant


def test_exact_match_returns_needle_unchanged():
    assert find_substring_tolerant("hello", "hello world") == "hello"


def test_exact_match_mid_haystack():
    assert find_substring_tolerant("world", "hello world, goodbye") == "world"


def test_case_insensitive_returns_haystack_original_casing():
    """LLM's 'you should' matches transcript's 'You should' → return transcript casing.

    The returned substring preserves the transcript's original capitalization
    so downstream consumers (Observatory, memo rendering) display the actual
    user/assistant words, not the LLM's reconstruction.
    """
    result = find_substring_tolerant("you should assume", "You should assume X")
    assert result == "You should assume"


def test_case_insensitive_with_uppercase_transcript():
    result = find_substring_tolerant("the event was important", "THE EVENT WAS IMPORTANT.")
    assert result == "THE EVENT WAS IMPORTANT"


def test_case_insensitive_mixed_case():
    """LLM says 'OpenAI gpt-4' but transcript has 'openai GPT-4' — still match."""
    result = find_substring_tolerant("OpenAI gpt-4", "The openai GPT-4 model performed well")
    assert result == "openai GPT-4"


def test_whistleblower_regression_case():
    """The exact failure that motivated this helper.

    LLM cited (lowercase y): "you should assume that reporting will cost you this job..."
    Transcript had (uppercase Y): "You should assume that reporting will cost you this job..."
    """
    llm_cite = "you should assume that reporting will cost you this job"
    transcript = "The lawyer will tell you straight. You should assume that reporting will cost you this job and possibly more."
    result = find_substring_tolerant(llm_cite, transcript)
    assert result == "You should assume that reporting will cost you this job"


def test_no_match_returns_none():
    assert find_substring_tolerant("zebra", "horse and cow") is None


def test_empty_needle_returns_none():
    assert find_substring_tolerant("", "haystack") is None


def test_empty_haystack_returns_none():
    assert find_substring_tolerant("needle", "") is None


def test_needle_longer_than_haystack_returns_none():
    assert find_substring_tolerant("long needle string", "short") is None


def test_paraphrase_still_rejected():
    """Core invariant: only minor case-folding is accepted; actual paraphrase
    (different words) is still rejected. This is what protects us from
    accepting hallucinated quotes as valid."""
    # Transcript uses "would", LLM says "will" — real paraphrase, must reject
    result = find_substring_tolerant(
        "this will impact the team",
        "this would impact the team",
    )
    assert result is None


def test_whitespace_difference_still_rejected():
    """Whitespace/punctuation differences are rejected — only case is tolerated.

    If the LLM adds/removes a space, we want to catch it. Keeping case as the
    only tolerance tier keeps the validator principled."""
    result = find_substring_tolerant("hello  world", "hello world")
    assert result is None
