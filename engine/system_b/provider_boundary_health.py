"""Provider-boundary health metadata for Lolla run artifacts.

This module classifies provider-boundary violations separately from product
and live-output contamination. It does not decide caller policy; PR7A only
makes the trust impact inspectable.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any


PROVIDER_BOUNDARY_HEALTH_SCHEMA_VERSION = "lolla.provider_boundary_health.v0.1"
PROVIDER_BOUNDARY_REASONING_LEAK_ISSUE = "vendor_boundary_reasoning_leak"
PROVIDER_BOUNDARY_REASONING_LEAK_REASON = (
    "vendor_returned_reasoning_details_despite_disabled"
)


def build_provider_boundary_health(run_health: Mapping[str, Any]) -> dict[str, Any]:
    """Return structured provider-boundary health from existing run health.

    Raw provider reasoning fields are not copied into this metadata. The
    boundary client records presence/count metadata; product and live-output
    hygiene remain independent axes.
    """

    run_health = _mapping(run_health)
    detected = _boundary_issue_detected(run_health)
    affected_call_count = _boundary_count(run_health)
    product_output_health = _text(run_health.get("product_output_health")) or "unknown"
    live_output_health = _text(run_health.get("live_output_health")) or "unknown"
    product_contamination = product_output_health == "unsafe"
    live_contamination = live_output_health == "unsafe"

    if not detected:
        status = "clean"
        reason = "no_provider_boundary_issue"
        archive_custody_status = "not_applicable"
    elif product_contamination or live_contamination:
        status = "confirmed_contamination"
        reason = "provider_boundary_warning_with_output_contamination"
        archive_custody_status = "not_checked_for_raw_reasoning_details"
    elif product_output_health == "unknown":
        status = "warning_unknown_persistence"
        reason = PROVIDER_BOUNDARY_REASONING_LEAK_REASON
        archive_custody_status = "not_checked"
    else:
        status = "warning_contained"
        reason = PROVIDER_BOUNDARY_REASONING_LEAK_REASON
        archive_custody_status = "not_detected"

    return {
        "schema_version": PROVIDER_BOUNDARY_HEALTH_SCHEMA_VERSION,
        "status": status,
        "reason": reason,
        "issue_code": PROVIDER_BOUNDARY_REASONING_LEAK_ISSUE if detected else "",
        "affected_call_count": affected_call_count,
        "affected_models": _boundary_strings(
            run_health,
            "boundary_reasoning_leak_models",
            "models",
        ),
        "affected_stages": _boundary_strings(
            run_health,
            "boundary_reasoning_leak_stages",
            "stages",
        ),
        "reasoning_disabled": True if detected else None,
        "reasoning_details_returned": bool(detected),
        "product_output_health": product_output_health,
        "product_contamination_detected": product_contamination,
        "live_output_health": live_output_health,
        "live_output_contamination_detected": live_contamination,
        "archive_custody_contamination_status": archive_custody_status,
        "raw_reasoning_details_persisted": False,
        "raw_reasoning_details_persistence_basis": (
            "boundary_call_metadata_presence_flags_only" if detected else "not_applicable"
        ),
    }


def refresh_provider_boundary_health(run_health: dict[str, Any]) -> dict[str, Any]:
    """Attach/replace provider-boundary health on a mutable run_health dict."""

    run_health["provider_boundary_health"] = build_provider_boundary_health(run_health)
    return run_health


def _boundary_issue_detected(run_health: Mapping[str, Any]) -> bool:
    if bool(run_health.get("boundary_reasoning_leak_detected")):
        return True
    if _boundary_count(run_health) > 0:
        return True
    return PROVIDER_BOUNDARY_REASONING_LEAK_ISSUE in _strings(run_health.get("issues"))


def _boundary_count(run_health: Mapping[str, Any]) -> int:
    direct = _safe_int(run_health.get("boundary_reasoning_leak_count"))
    if direct:
        return direct
    detail = _boundary_issue_detail(run_health)
    return _safe_int(detail.get("leak_count"))


def _boundary_strings(
    run_health: Mapping[str, Any],
    direct_key: str,
    detail_key: str,
) -> list[str]:
    direct = _strings(run_health.get(direct_key))
    if direct:
        return direct
    detail = _boundary_issue_detail(run_health)
    return _strings(detail.get(detail_key))


def _boundary_issue_detail(run_health: Mapping[str, Any]) -> Mapping[str, Any]:
    for item in _list(run_health.get("issue_details")):
        if not isinstance(item, Mapping):
            continue
        if _text(item.get("code")) == PROVIDER_BOUNDARY_REASONING_LEAK_ISSUE:
            return item
    return {}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [text for item in value if (text := _text(item))]


def _text(value: Any) -> str:
    return str(value or "").strip()


def _safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0
