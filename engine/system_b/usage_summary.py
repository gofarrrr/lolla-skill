"""Per-run usage_summary aggregator.

Single source of truth for "what did this run cost and how many calls did
it make". Reads from four input streams and produces one canonical block:

  1. Pipeline boundary calls   — manually-recorded into ``result.audit.boundary_calls``
                                  by the lane code (pass1, pass2, frame, coverage,
                                  companion fingerprint/verification)
  2. Post-pipeline boundary calls — auto-recorded into ``client.call_log`` of the
                                    bullshit-index and revision clients (which are
                                    separate client instances from the pipeline's)
  3. Extraction boundary calls — read from the sidecar file written by run_extract.py
                                 at /tmp/lolla_<run_id>_extraction_calls.json
  4. Embedding usage records   — captured via embedding_retriever.capture_usage()

Output schema lives in :func:`build_usage_summary`. Cost estimates use the
hardcoded pricing table in :mod:`pricing`; the table version (date last
verified) is surfaced in the output so consumers can tell whether the
estimate is fresh or stale.

Design constraints:
  - Per-run isolation: every run produces its own summary. No module globals.
  - No prosthesis: numbers only appear when sourced from real telemetry.
    Unknown models report cost=null but call counts still flow through.
  - One source of truth: the ``usage_summary`` block in the result JSON.
    Observatory, memo, and the SKILL chat output all read from this; nothing
    recomputes from scratch.
"""
from __future__ import annotations

import json
import logging
import re
from collections import defaultdict
from pathlib import Path
from typing import Mapping, Sequence

from .boundary_provider import BoundaryCallRecord
from .pricing import (
    PRICES_LAST_VERIFIED,
    estimate_chat_cost_usd,
    estimate_embedding_cost_usd,
    lookup_chat_price,
    lookup_embedding_price,
)


_LOGGER = logging.getLogger("system_b.usage_summary")


# Run IDs are interpolated into /tmp paths. Restrict to the alphabet the
# SKILL preamble actually generates (timestamps, slugs, dashes/underscores)
# so a malicious or malformed value can't traverse the filesystem.
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def is_valid_run_id(run_id: str) -> bool:
    """Return True iff run_id is safe to interpolate into a sidecar path."""
    return bool(run_id) and bool(RUN_ID_PATTERN.fullmatch(run_id))


# ---------------------------------------------------------------------------
# Sidecar I/O
# ---------------------------------------------------------------------------
def load_extraction_sidecar(run_id: str) -> list[dict]:
    """Read the extraction call_log sidecar written by run_extract.py.

    Returns [] if the file is missing or unreadable. The sidecar lives at
    /tmp/lolla_<run_id>_extraction_calls.json and is one JSON list of
    BoundaryCallRecord dicts (the dict form of ``BoundaryCallRecord``).
    """
    if not is_valid_run_id(run_id):
        return []
    path = Path(f"/tmp/lolla_{run_id}_extraction_calls.json")
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [d for d in data if isinstance(d, dict)]
    except (OSError, json.JSONDecodeError):
        _LOGGER.warning("Failed to read extraction sidecar at %s", path, exc_info=True)
    return []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _record_to_dict(rec) -> dict:
    """Normalize a record to dict form regardless of source."""
    if isinstance(rec, BoundaryCallRecord):
        return rec.to_dict()
    if isinstance(rec, Mapping):
        return dict(rec)
    if hasattr(rec, "__dict__"):
        return dict(vars(rec))
    return {}


def _safe_int(value: object) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _safe_div(num: float, den: float) -> float:
    if not den:
        return 0.0
    return float(num) / float(den)


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------
def _empty_stage_totals() -> dict:
    return {
        "calls": 0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "cached_tokens": 0,
        "total_tokens": 0,
    }


def _accumulate_stage(totals: dict, rec: dict) -> None:
    totals["calls"] += 1
    totals["prompt_tokens"] += _safe_int(rec.get("prompt_tokens"))
    totals["completion_tokens"] += _safe_int(rec.get("completion_tokens"))
    totals["cached_tokens"] += _safe_int(rec.get("cached_tokens"))
    totals["total_tokens"] += _safe_int(rec.get("total_tokens"))


def _build_chat_vendor_block(
    *,
    provider_label: str,
    records: Sequence[object],
) -> dict:
    """Build the per-vendor block for a chat-LLM provider.

    Records can be a mix of BoundaryCallRecord, dicts, or anything with the
    same field shape — they're all normalized via _record_to_dict.
    """
    stage_totals: dict[str, dict] = defaultdict(_empty_stage_totals)
    overall = _empty_stage_totals()
    cost_total = 0.0
    cost_known_calls = 0
    cost_unknown_calls = 0
    models_seen: set[str] = set()
    primary_model = ""

    for raw in records:
        rec = _record_to_dict(raw)
        if not rec:
            continue
        stage = str(rec.get("stage") or "unlabeled")
        model = str(rec.get("model") or "")
        if model:
            models_seen.add(model)
            if not primary_model:
                primary_model = model

        _accumulate_stage(stage_totals[stage], rec)
        _accumulate_stage(overall, rec)

        price = lookup_chat_price(provider_label, model)
        if price is None:
            cost_unknown_calls += 1
            continue
        cost_known_calls += 1
        cost_total += estimate_chat_cost_usd(
            price=price,
            prompt_tokens=_safe_int(rec.get("prompt_tokens")),
            completion_tokens=_safe_int(rec.get("completion_tokens")),
            cached_tokens=_safe_int(rec.get("cached_tokens")),
        )

    cache_hit_rate = _safe_div(overall["cached_tokens"], overall["prompt_tokens"])

    return {
        "provider": provider_label,
        "primary_model": primary_model,
        "models_seen": sorted(models_seen),
        "calls": overall["calls"],
        "prompt_tokens": overall["prompt_tokens"],
        "completion_tokens": overall["completion_tokens"],
        "cached_tokens": overall["cached_tokens"],
        "total_tokens": overall["total_tokens"],
        "cache_hit_rate": round(cache_hit_rate, 4),
        "estimated_cost_usd": round(cost_total, 6),
        "cost_estimate_coverage": {
            "calls_with_known_price": cost_known_calls,
            "calls_with_unknown_price": cost_unknown_calls,
        },
        "stages": {
            stage: dict(totals) for stage, totals in sorted(stage_totals.items())
        },
    }


def _build_embedding_vendor_block(records: Sequence[Mapping]) -> dict:
    """Build the per-vendor block for OpenAI embeddings + query expansion."""
    overall_input = 0
    overall_output = 0
    by_model: dict[str, dict] = defaultdict(
        lambda: {"calls": 0, "input_tokens": 0, "output_tokens": 0, "estimated_cost_usd": 0.0}
    )
    cost_total = 0.0
    cost_unknown_calls = 0
    cost_known_calls = 0
    endpoints_seen: set[str] = set()

    for r in records:
        if not isinstance(r, Mapping):
            continue
        endpoint = str(r.get("endpoint", ""))
        endpoints_seen.add(endpoint)
        model = str(r.get("model", ""))
        in_tok = _safe_int(r.get("input_tokens"))
        out_tok = _safe_int(r.get("output_tokens"))
        overall_input += in_tok
        overall_output += out_tok
        by_model[model]["calls"] += 1
        by_model[model]["input_tokens"] += in_tok
        by_model[model]["output_tokens"] += out_tok

        if endpoint == "embeddings":
            price = lookup_embedding_price(model)
            if price is None:
                cost_unknown_calls += 1
                continue
            call_cost = estimate_embedding_cost_usd(price=price, tokens=in_tok)
        elif endpoint == "chat":
            chat_price = lookup_chat_price("openai", model)
            if chat_price is None:
                cost_unknown_calls += 1
                continue
            call_cost = estimate_chat_cost_usd(
                price=chat_price,
                prompt_tokens=in_tok,
                completion_tokens=out_tok,
            )
        else:
            cost_unknown_calls += 1
            continue

        cost_known_calls += 1
        cost_total += call_cost
        by_model[model]["estimated_cost_usd"] += call_cost

    return {
        "provider": "openai",
        "endpoints_seen": sorted(endpoints_seen),
        "calls": sum(m["calls"] for m in by_model.values()),
        "input_tokens": overall_input,
        "output_tokens": overall_output,
        "estimated_cost_usd": round(cost_total, 6),
        "cost_estimate_coverage": {
            "calls_with_known_price": cost_known_calls,
            "calls_with_unknown_price": cost_unknown_calls,
        },
        "by_model": {
            model: {
                "calls": v["calls"],
                "input_tokens": v["input_tokens"],
                "output_tokens": v["output_tokens"],
                "estimated_cost_usd": round(v["estimated_cost_usd"], 6),
            }
            for model, v in sorted(by_model.items())
        },
    }


def _build_subagent_vendor_block(subagent_calls: Sequence[Mapping]) -> dict:
    """Build the per-vendor block for Anthropic Step-7 sub-agent calls.

    Each subagent record: {"lane": int, "model": str, "total_tokens": int,
                           "duration_ms": int, "tool_uses": int, "status": str}

    Resolution gap: Anthropic sub-agent telemetry surfaces only total_tokens,
    not a prompt/completion split. Cost is estimated by treating the entire
    total as input tokens at the model's input price — a conservative
    over-estimate.
    """
    by_model: dict[str, dict] = defaultdict(
        lambda: {"calls": 0, "total_tokens": 0, "estimated_cost_usd": 0.0}
    )
    by_lane: dict[str, dict] = defaultdict(
        lambda: {
            "calls": 0,
            "total_tokens": 0,
            "estimated_cost_usd": 0.0,
            "model": "",
            "status": "",
            "duration_ms": 0,
        }
    )
    cost_total = 0.0
    cost_known_calls = 0
    cost_unknown_calls = 0

    for raw in subagent_calls:
        if not isinstance(raw, Mapping):
            continue
        model = str(raw.get("model", ""))
        total = _safe_int(raw.get("total_tokens"))
        # Lane labels keep the original int/string form intact, falling back to
        # "unlabeled" for older sub-agent records that pre-date the lane field.
        lane_raw = raw.get("lane")
        lane_key = str(lane_raw) if lane_raw is not None else "unlabeled"
        status = str(raw.get("status", ""))
        duration_ms = _safe_int(raw.get("duration_ms"))

        by_model[model]["calls"] += 1
        by_model[model]["total_tokens"] += total
        by_lane[lane_key]["calls"] += 1
        by_lane[lane_key]["total_tokens"] += total
        if not by_lane[lane_key]["model"]:
            by_lane[lane_key]["model"] = model
        if not by_lane[lane_key]["status"]:
            by_lane[lane_key]["status"] = status
        by_lane[lane_key]["duration_ms"] += duration_ms

        price = lookup_chat_price("anthropic", model)
        if price is None:
            cost_unknown_calls += 1
            continue
        cost_known_calls += 1
        # Conservative: charge as input. Real split unavailable from Claude
        # Code's task-notification.
        call_cost = estimate_chat_cost_usd(
            price=price,
            prompt_tokens=total,
            completion_tokens=0,
        )
        cost_total += call_cost
        by_model[model]["estimated_cost_usd"] += call_cost
        by_lane[lane_key]["estimated_cost_usd"] += call_cost

    return {
        "provider": "anthropic",
        "calls": sum(m["calls"] for m in by_model.values()),
        "total_tokens": sum(m["total_tokens"] for m in by_model.values()),
        "estimated_cost_usd": round(cost_total, 6),
        "cost_estimate_coverage": {
            "calls_with_known_price": cost_known_calls,
            "calls_with_unknown_price": cost_unknown_calls,
        },
        "estimation_method": "conservative_input_only_no_split_available",
        "by_model": {
            model: {
                "calls": v["calls"],
                "total_tokens": v["total_tokens"],
                "estimated_cost_usd": round(v["estimated_cost_usd"], 6),
            }
            for model, v in sorted(by_model.items())
        },
        # Per-lane breakdown — surfaces which Step-7 lane was the most
        # expensive without losing the model-level aggregate. Lane keys are
        # the lane numbers the SKILL Step 8b sends ("1", "2", "3", "4"); the
        # "unlabeled" bucket catches older records that pre-date the lane
        # field.
        "by_lane": {
            lane: {
                "model": v["model"],
                "status": v["status"],
                "calls": v["calls"],
                "total_tokens": v["total_tokens"],
                "duration_ms": v["duration_ms"],
                "estimated_cost_usd": round(v["estimated_cost_usd"], 6),
            }
            for lane, v in sorted(by_lane.items())
        },
    }


def merge_subagent_calls(
    usage_summary: dict,
    subagent_calls: Sequence[Mapping],
) -> dict:
    """Recompute the ``anthropic_subagents`` vendor block on an existing
    usage_summary and update the grand total.

    Used by SKILL.md Step 8b to fold in Step-7 sub-agent usage after the
    sub-agents have returned (the pipeline can't know the sub-agent results
    in advance because they fire from inside the SKILL orchestration).

    Mutates ``usage_summary`` in place and also returns it.
    """
    new_block = _build_subagent_vendor_block(subagent_calls)
    vendors = usage_summary.setdefault("vendors", {})
    vendors["anthropic_subagents"] = new_block
    grand_total = (
        vendors.get("openrouter", {}).get("estimated_cost_usd", 0.0)
        + vendors.get("openai_embeddings", {}).get("estimated_cost_usd", 0.0)
        + new_block["estimated_cost_usd"]
    )
    usage_summary["estimated_total_cost_usd"] = round(grand_total, 6)
    return usage_summary


def build_usage_summary(
    *,
    run_id: str,
    pipeline_boundary_calls: Sequence[object],
    bi_boundary_calls: Sequence[object] = (),
    revision_boundary_calls: Sequence[object] = (),
    extraction_boundary_calls: Sequence[object] = (),
    embedding_records: Sequence[Mapping] = (),
    subagent_calls: Sequence[Mapping] = (),
) -> dict:
    """Build the canonical usage_summary block for a single run.

    Each input stream is a list of records (BoundaryCallRecord, BoundaryCallTrace,
    or plain dicts with the same fields). The output is one self-describing dict
    suitable for serialization into the result JSON.
    """
    # Group all OpenRouter-bound records together so the per-vendor totals
    # match what the user pays the OpenRouter bill for.
    all_openrouter = list(pipeline_boundary_calls) \
        + list(bi_boundary_calls) \
        + list(revision_boundary_calls) \
        + list(extraction_boundary_calls)

    openrouter_block = _build_chat_vendor_block(
        provider_label="openrouter",
        records=all_openrouter,
    )

    embedding_block = _build_embedding_vendor_block(embedding_records)
    subagent_block = _build_subagent_vendor_block(subagent_calls)

    grand_total_cost = (
        openrouter_block["estimated_cost_usd"]
        + embedding_block["estimated_cost_usd"]
        + subagent_block["estimated_cost_usd"]
    )

    return {
        "run_id": run_id,
        "pricing_table_version": PRICES_LAST_VERIFIED,
        "estimated_total_cost_usd": round(grand_total_cost, 6),
        "vendors": {
            "openrouter": openrouter_block,
            "openai_embeddings": embedding_block,
            "anthropic_subagents": subagent_block,
        },
        "notes": [
            "Cost estimates use the hardcoded pricing table at "
            "engine/system_b/pricing.py. Update PRICES_LAST_VERIFIED when "
            "rates change.",
            "Anthropic sub-agent costs are conservative — only total_tokens "
            "is surfaced by Claude Code task notifications, so the full "
            "amount is billed as input tokens.",
            "Embedding costs cover OpenAI text-embedding-3-large and the "
            "gpt-4o-mini query-expansion calls made inside the pipeline.",
        ],
    }
