"""Current live-price verification metadata.

The rate table remains in :mod:`engine.system_b.pricing` because historical
evaluation contracts hash that file byte-for-byte. Runtime receipts import the
date here so current verification can advance without rewriting frozen proof.
"""

from __future__ import annotations


PRICES_LAST_VERIFIED = "2026-07-13"

# On this date OpenRouter's model and endpoint metadata still reported Gemini
# 3.1 Flash Lite at $0.25/M fresh input, $0.025/M cached input, and $1.50/M
# output for google-vertex/global. The numerical table therefore needed no
# change; only the live verification timestamp advanced.
