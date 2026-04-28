"""Hardcoded LLM pricing for cost estimation.

Single source of truth. Update PRICES_LAST_VERIFIED and the relevant rate
when you bump prices. Anything not listed below falls back to ``unknown``
(no cost estimate produced for that model — call counts still recorded).

Prices are USD per 1,000,000 tokens. Cached input is the price OpenRouter /
the provider charges for prompt-cache hits — typically 25-50% of fresh
input. Embedding models charge a flat rate per token (no separate cached
price).

Verification: cross-check against the provider's pricing page before
relying on these for budgeting. The pipeline will surface this date in the
``usage_summary.pricing_table_version`` field so the user can tell whether
the estimate is fresh or stale.
"""
from __future__ import annotations

from dataclasses import dataclass


PRICES_LAST_VERIFIED = "2026-04-28"


@dataclass(frozen=True)
class ChatPrice:
    """Per-million-token prices for a chat model."""

    input_usd_per_mtok: float
    cached_input_usd_per_mtok: float
    output_usd_per_mtok: float


@dataclass(frozen=True)
class EmbeddingPrice:
    """Per-million-token price for an embedding model."""

    input_usd_per_mtok: float


# OpenRouter chat models — prefix-matched (longest prefix wins).
OPENROUTER_CHAT_PRICES: dict[str, ChatPrice] = {
    "x-ai/grok-4.1-fast": ChatPrice(0.20, 0.05, 0.50),
    # add more as they get used; unknown models report cost=null, calls still counted
}

# OpenAI direct chat models — for the pipeline if it's ever used as the
# boundary provider (not embeddings). Embedding prices live below.
OPENAI_CHAT_PRICES: dict[str, ChatPrice] = {
    "gpt-4o": ChatPrice(2.50, 1.25, 10.00),
    "gpt-4o-mini": ChatPrice(0.15, 0.075, 0.60),
}

# OpenAI embedding models.
OPENAI_EMBEDDING_PRICES: dict[str, EmbeddingPrice] = {
    "text-embedding-3-large": EmbeddingPrice(0.13),
    "text-embedding-3-small": EmbeddingPrice(0.02),
}

# Anthropic models — used for Step 7 sub-agents. Sub-agent telemetry only
# exposes total_tokens, not a prompt/completion split, so cost is estimated
# by treating all tokens as input — a conservative (over-)estimate. The
# usage_summary surfaces this approximation explicitly.
ANTHROPIC_CHAT_PRICES: dict[str, ChatPrice] = {
    "claude-opus-4-7": ChatPrice(15.00, 1.50, 75.00),
    "claude-sonnet-4-6": ChatPrice(3.00, 0.30, 15.00),
    "claude-haiku-4-5-20251001": ChatPrice(1.00, 0.10, 5.00),
}


def lookup_chat_price(provider: str, model: str) -> ChatPrice | None:
    """Return the ChatPrice for (provider, model), or None if unknown.

    Provider matching is case-insensitive. Model matching is exact for
    OpenAI/Anthropic and longest-prefix for OpenRouter (where model IDs
    follow the ``"vendor/model"`` form).
    """
    p = (provider or "").strip().lower()
    m = (model or "").strip()
    if p == "openrouter":
        for key, price in sorted(
            OPENROUTER_CHAT_PRICES.items(), key=lambda kv: -len(kv[0])
        ):
            if m.startswith(key):
                return price
        return None
    if p == "openai":
        return OPENAI_CHAT_PRICES.get(m)
    if p == "anthropic":
        return ANTHROPIC_CHAT_PRICES.get(m)
    return None


def lookup_embedding_price(model: str) -> EmbeddingPrice | None:
    return OPENAI_EMBEDDING_PRICES.get((model or "").strip())


def estimate_chat_cost_usd(
    *,
    price: ChatPrice,
    prompt_tokens: int,
    completion_tokens: int,
    cached_tokens: int = 0,
) -> float:
    """Estimate cost in USD for a chat call given token counts and price.

    Cached prompt tokens are billed at ``cached_input_usd_per_mtok``; the
    remaining ``prompt_tokens - cached_tokens`` are billed at
    ``input_usd_per_mtok``.
    """
    fresh_input = max(0, prompt_tokens - cached_tokens)
    return (
        fresh_input * price.input_usd_per_mtok
        + cached_tokens * price.cached_input_usd_per_mtok
        + completion_tokens * price.output_usd_per_mtok
    ) / 1_000_000


def estimate_embedding_cost_usd(*, price: EmbeddingPrice, tokens: int) -> float:
    return tokens * price.input_usd_per_mtok / 1_000_000
