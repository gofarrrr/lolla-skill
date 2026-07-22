"""Current live-price verification metadata.

The rate table remains in :mod:`engine.system_b.pricing` because historical
evaluation contracts hash that file byte-for-byte. Runtime receipts import the
date here so current verification can advance without rewriting frozen proof.
"""

from __future__ import annotations


PRICES_LAST_VERIFIED = "2026-07-13"
PRICES_VERIFICATION_SCOPE = "active_openrouter_route_only"
TABLE_WIDE_LAST_VERIFIED = "2026-05-25"

# The frozen provider-boundary contract uses the 2026-07-13 active-route check
# as its freshness date. That check covered Gemini/OpenRouter only; it did not
# re-verify every OpenRouter, OpenAI, and Anthropic row. New usage summaries
# therefore disclose both the narrow scope and the older table-wide date. A
# prospective pricing-table version is required to update historical rates.
