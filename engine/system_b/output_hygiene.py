"""Deterministic scanner for product-facing Lolla output hygiene.

The scanner is deliberately role-aware. Operator surfaces may show machinery;
product surfaces should translate machinery into ordinary reasoning effects.
"""
from __future__ import annotations

import hashlib
import re
from difflib import SequenceMatcher
from typing import Any, Mapping

from .provider_boundary_health import refresh_provider_boundary_health


PRODUCT_OUTPUT_LEAK_ISSUE = "product_output_leak"
LIVE_OUTPUT_LEAK_ISSUE = "live_output_leak"
LIVE_OUTPUT_MISSING_ISSUE = "live_output_missing"
LIVE_OUTPUT_UNVERIFIED_ISSUE = "live_output_unverified"
LIVE_OUTPUT_SEMANTIC_MISMATCH_ISSUE = "live_output_semantic_mismatch"

_HEALTH_SEVERITY_RANK = {
    "info": 0,
    "optional_off": 0,
    "partial": 1,
    "degraded": 2,
    "critical": 3,
}

_BANNED_PRODUCT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("V60", re.compile(r"\bV60\b", re.IGNORECASE)),
    ("affordance", re.compile(r"\baffordances?\b", re.IGNORECASE)),
    ("chunk", re.compile(r"\bchunks?\b", re.IGNORECASE)),
    ("ledger", re.compile(r"\bledgers?\b", re.IGNORECASE)),
    ("independent review", re.compile(r"\bindependent\s+review\b", re.IGNORECASE)),
    ("isolated review", re.compile(r"\bisolated\s+review\b", re.IGNORECASE)),
    ("sub-agent", re.compile(r"\bsub[- ]?agents?\b", re.IGNORECASE)),
    ("pressure-check agents", re.compile(r"\bpressure[- ]check\s+agents?\b", re.IGNORECASE)),
    ("pressure-check readers", re.compile(r"\bpressure[- ]check\s+readers?\b", re.IGNORECASE)),
    (
        "reader status",
        re.compile(
            r"\b(?:all|both|two|three|remaining|the\s+third|third)\s+"
            r"(?:\w+\s+){0,2}readers?\s+(?:are|is)\s+in\b",
            re.IGNORECASE,
        ),
    ),
    (
        "reader wait",
        re.compile(
            r"\b(?:waiting\s+for|still\s+waiting\s+for)\s+(?:the\s+)?"
            r"(?:remaining\s+)?(?:one|two|three|third)?\s*readers?\b",
            re.IGNORECASE,
        ),
    ),
    ("Beat", re.compile(r"\bBeat\s+[1-9]\b")),
    ("Lane", re.compile(r"\bLane\s+\d+\b", re.IGNORECASE)),
    ("orchestrator", re.compile(r"\borchestrator\b", re.IGNORECASE)),
    ("Model Requirements", re.compile(r"\bModel\s+Requirements\b", re.IGNORECASE)),
    ("Now persisting", re.compile(r"\bNow\s+persisting\b", re.IGNORECASE)),
    ("rendering the memo", re.compile(r"\brendering\s+the\s+memo\b", re.IGNORECASE)),
    ("DeltaCard", re.compile(r"\bDeltaCard\b", re.IGNORECASE)),
    ("CompanionCheatSheet", re.compile(r"\bCompanionCheatSheet\b", re.IGNORECASE)),
    ("FramePressureCard", re.compile(r"\bFramePressureCard\b", re.IGNORECASE)),
    ("StructuralCoverageCard", re.compile(r"\bStructuralCoverageCard\b", re.IGNORECASE)),
    ("internal chunk id", re.compile(r"\b(?:aff|abs)::[A-Za-z0-9_.:-]+")),
    ("v60 card id", re.compile(r"\bv60-card-[A-Za-z0-9_.:-]+", re.IGNORECASE)),
    ("model_id", re.compile(r"\bmodel_id\b", re.IGNORECASE)),
)
_INTERNAL_PIPELINE_RE = re.compile(
    r"\b(?:"
    r"(?:the\s+)?pipeline\s+(?:flagged|found|returned|generated|selected|routed|produced|detected|ran|runs|stage|step|output|result|telemetry)"
    r"|the\s+pipeline\b"
    r"|(?:pre|post)-pipeline"
    r"|lolla\s+pipeline"
    r")\b",
    re.IGNORECASE,
)


def scan_output_hygiene(
    surfaces: Mapping[str, object],
    *,
    surface_roles: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Scan named output surfaces for internal language leaks.

    ``surface_roles`` defaults every surface to ``product``. Use
    ``operator`` for Observatory/audit/debug surfaces where machinery is
    expected and should not count as a product leak.
    """

    roles = dict(surface_roles or {})
    leaks: list[dict[str, Any]] = []
    scanned_surfaces: list[str] = []
    skipped_surfaces: list[str] = []

    for surface, raw_text in surfaces.items():
        role = roles.get(surface, "product")
        if role != "product":
            skipped_surfaces.append(str(surface))
            continue

        text = _text(raw_text)
        if not text:
            continue
        scanned_surfaces.append(str(surface))
        leaks.extend(_scan_product_text(surface=str(surface), text=text))

    return {
        "schema_version": "product_output_hygiene.v1",
        "status": "unsafe" if leaks else "clean",
        "leak_count": len(leaks),
        "leaks": leaks,
        "scanned_surfaces": scanned_surfaces,
        "skipped_operator_surfaces": skipped_surfaces,
    }


def finalize_product_output_hygiene(
    result_payload: Mapping[str, Any],
    product_surfaces: Mapping[str, object],
    *,
    surface_roles: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Attach product-output hygiene telemetry and run-health status."""

    result = dict(result_payload)
    scan = scan_output_hygiene(product_surfaces, surface_roles=surface_roles)
    result["product_output_hygiene"] = scan

    run_health = dict(_mapping(result.get("run_health")))
    issues = [
        issue
        for issue in _strings(run_health.get("issues"))
        if issue != PRODUCT_OUTPUT_LEAK_ISSUE
    ]
    issue_details = [
        dict(item)
        for item in _list(run_health.get("issue_details"))
        if isinstance(item, Mapping)
        and _text(item.get("code")) != PRODUCT_OUTPUT_LEAK_ISSUE
    ]

    run_health["product_output_health"] = scan["status"]
    run_health["product_output_leak_count"] = scan["leak_count"]
    run_health["product_output_leaks"] = scan["leaks"]

    if scan["status"] == "unsafe":
        _add_once(issues, PRODUCT_OUTPUT_LEAK_ISSUE)
        _add_issue_detail(
            issue_details,
            {
                "code": PRODUCT_OUTPUT_LEAK_ISSUE,
                "severity": "degraded",
                "axis": "product_output",
                "trust_impact": (
                    "A clean product-facing artifact leaked internal audit machinery, "
                    "so the run is not product-safe without editing."
                ),
                "leak_count": scan["leak_count"],
                "surfaces": sorted({leak["surface"] for leak in scan["leaks"]}),
            },
        )
        _raise_run_health_at_least(run_health, "degraded")
    elif not _text(run_health.get("overall")):
        run_health["overall"] = "healthy"
    elif "issue_details" in run_health or issue_details:
        if issue_details:
            run_health["overall"] = _overall_from_issue_details(issue_details)
        elif not issues:
            run_health["overall"] = "healthy"

    run_health["issues"] = issues
    run_health["issue_details"] = issue_details
    _refresh_derived_health_fields(run_health)
    result["run_health"] = run_health
    return result


def finalize_live_output_hygiene(
    result_payload: Mapping[str, Any],
    live_transcript: object | None,
    *,
    require_live_output_clean: bool = False,
    trusted_capture: bool = False,
) -> dict[str, Any]:
    """Attach live transcript hygiene telemetry and run-health status.

    Missing live transcripts are observable but backward-compatible by default:
    they become ``live_output_health: missing`` without changing overall health.
    A manually maintained transcript is scanned, but a clean scan only proves
    that artifact is clean; it becomes ``not_checked`` unless the caller marks
    the transcript as a complete trusted capture. In explicit gate mode, missing
    or unverified live output is a partial run-health issue. Unsafe live output
    is always degraded because the user already saw it.
    """

    result = dict(result_payload)
    text = _text(live_transcript)
    run_health = dict(_mapping(result.get("run_health")))
    issues = [
        issue
        for issue in _strings(run_health.get("issues"))
        if issue
        not in {
            LIVE_OUTPUT_LEAK_ISSUE,
            LIVE_OUTPUT_MISSING_ISSUE,
            LIVE_OUTPUT_UNVERIFIED_ISSUE,
            LIVE_OUTPUT_SEMANTIC_MISMATCH_ISSUE,
        }
    ]
    issue_details = [
        dict(item)
        for item in _list(run_health.get("issue_details"))
        if isinstance(item, Mapping)
        and _text(item.get("code"))
        not in {
            LIVE_OUTPUT_LEAK_ISSUE,
            LIVE_OUTPUT_MISSING_ISSUE,
            LIVE_OUTPUT_UNVERIFIED_ISSUE,
            LIVE_OUTPUT_SEMANTIC_MISMATCH_ISSUE,
        }
    ]

    if not text:
        scan = {
            "schema_version": "live_output_hygiene.v1",
            "status": "missing",
            "transcript_status": "missing",
            "capture_mode": "missing",
            "trusted_capture": False,
            "observed_scope": [],
            "complete_visible_surface_observed": False,
            "complete_visible_surface_leak_count": None,
            "leak_count_scope": "no_surface_observed",
            "transcript_sha256": None,
            "leak_count": 0,
            "leaks": [],
            "semantic_mismatch_count": 0,
            "semantic_mismatches": [],
            "scanned_surfaces": [],
            "skipped_operator_surfaces": [],
            "required": bool(require_live_output_clean),
        }
        run_health["live_output_health"] = "missing"
        run_health["live_output_leak_count"] = 0
        run_health["live_output_observed_surface_leak_count"] = 0
        run_health["complete_visible_surface_observed"] = False
        run_health["complete_visible_surface_leak_count"] = None
        run_health["live_output_leaks"] = []
        run_health["live_output_semantic_mismatch_count"] = 0
        run_health["live_output_semantic_mismatches"] = []
        if require_live_output_clean:
            _add_once(issues, LIVE_OUTPUT_MISSING_ISSUE)
            _add_issue_detail(
                issue_details,
                {
                    "code": LIVE_OUTPUT_MISSING_ISSUE,
                    "severity": "partial",
                    "axis": "live_output",
                    "trust_impact": (
                        "The run did not preserve a live user-visible transcript, "
                        "so live output hygiene could not be proven."
                    ),
                },
            )
            _raise_run_health_at_least(run_health, "partial")
        else:
            _refresh_overall_after_clearing_issues(run_health, issues, issue_details)
        run_health["issues"] = issues
        run_health["issue_details"] = issue_details
        _refresh_derived_health_fields(run_health)
        result["live_output_hygiene"] = scan
        result["run_health"] = run_health
        return result

    scan = dict(scan_output_hygiene({"live_narration": text}))
    scan["schema_version"] = "live_output_hygiene.v1"
    scan["required"] = bool(require_live_output_clean)
    scan["trusted_capture"] = bool(trusted_capture)
    scan["capture_mode"] = "trusted" if trusted_capture else "manual_unverified"
    scan["observed_scope"] = [
        (
            "trusted_host_visible_transcript"
            if trusted_capture
            else "curated_live_transcript_artifact"
        )
    ]
    scan["complete_visible_surface_observed"] = bool(trusted_capture)
    scan["complete_visible_surface_leak_count"] = (
        scan["leak_count"] if trusted_capture else None
    )
    scan["leak_count_scope"] = (
        "complete_visible_surface"
        if trusted_capture
        else "curated_live_transcript_artifact_only"
    )
    scan["transcript_status"] = scan["status"]
    scan["transcript_sha256"] = _sha256_text(text)
    semantic_mismatches = _scan_updated_position_semantic_mismatches(
        live_text=text,
        revised_answer=_text(result.get("revised_answer")),
    )
    scan["semantic_mismatch_count"] = len(semantic_mismatches)
    scan["semantic_mismatches"] = semantic_mismatches
    if semantic_mismatches:
        scan["status"] = "unsafe"
        scan["transcript_status"] = "unsafe"
    if scan["status"] != "unsafe" and not trusted_capture:
        scan["status"] = "not_checked"
    result["live_output_hygiene"] = scan

    run_health["live_output_health"] = scan["status"]
    run_health["live_output_leak_count"] = scan["leak_count"]
    run_health["live_output_observed_surface_leak_count"] = scan["leak_count"]
    run_health["complete_visible_surface_observed"] = bool(trusted_capture)
    run_health["complete_visible_surface_leak_count"] = (
        scan["leak_count"] if trusted_capture else None
    )
    run_health["live_output_leaks"] = scan["leaks"]
    run_health["live_output_semantic_mismatch_count"] = scan["semantic_mismatch_count"]
    run_health["live_output_semantic_mismatches"] = scan["semantic_mismatches"]

    if scan["status"] == "unsafe":
        if scan["leak_count"]:
            _add_once(issues, LIVE_OUTPUT_LEAK_ISSUE)
            _add_issue_detail(
                issue_details,
                {
                    "code": LIVE_OUTPUT_LEAK_ISSUE,
                    "severity": "degraded",
                    "axis": "live_output",
                    "trust_impact": (
                        "The live user-visible transcript leaked internal audit machinery, "
                        "so the run was not product-safe as experienced."
                    ),
                    "leak_count": scan["leak_count"],
                    "surfaces": sorted({leak["surface"] for leak in scan["leaks"]}),
                },
            )
        if scan["semantic_mismatch_count"]:
            _add_once(issues, LIVE_OUTPUT_SEMANTIC_MISMATCH_ISSUE)
            _add_issue_detail(
                issue_details,
                {
                    "code": LIVE_OUTPUT_SEMANTIC_MISMATCH_ISSUE,
                    "severity": "degraded",
                    "axis": "live_output",
                    "trust_impact": (
                        "A visible updated-position block does not match the run's "
                        "current revised answer, so the live transcript may include "
                        "cross-case or stale output."
                    ),
                    "mismatch_count": scan["semantic_mismatch_count"],
                    "surfaces": sorted(
                        {item["surface"] for item in scan["semantic_mismatches"]}
                    ),
                },
            )
        _raise_run_health_at_least(run_health, "degraded")
    elif scan["status"] == "not_checked" and require_live_output_clean:
        _add_once(issues, LIVE_OUTPUT_UNVERIFIED_ISSUE)
        _add_issue_detail(
            issue_details,
            {
                "code": LIVE_OUTPUT_UNVERIFIED_ISSUE,
                "severity": "partial",
                "axis": "live_output",
                "trust_impact": (
                    "The live transcript artifact scanned clean, but it was manually "
                    "maintained rather than a complete trusted capture, so live output "
                    "hygiene could not be proven."
                ),
            },
        )
        _raise_run_health_at_least(run_health, "partial")
    else:
        _refresh_overall_after_clearing_issues(run_health, issues, issue_details)

    run_health["issues"] = issues
    run_health["issue_details"] = issue_details
    _refresh_derived_health_fields(run_health)
    result["run_health"] = run_health
    return result


def _scan_product_text(*, surface: str, text: str) -> list[dict[str, Any]]:
    leaks: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines() or [text], start=1):
        for term, pattern in _BANNED_PRODUCT_PATTERNS:
            for match in pattern.finditer(line):
                if _is_allowed_product_match(term=term, line=line, match_text=match.group(0)):
                    continue
                leaks.append(
                    {
                        "surface": surface,
                        "term": term,
                        "line": line_number,
                        "match": _compact(match.group(0), max_chars=80),
                    }
                )
        for match in _INTERNAL_PIPELINE_RE.finditer(line):
            leaks.append(
                {
                    "surface": surface,
                    "term": "pipeline",
                    "line": line_number,
                    "match": _compact(match.group(0), max_chars=80),
                }
            )
    return leaks


_UPDATED_POSITION_RE = re.compile(
    r"(?m)^\s*(?:[•*-]\s*)?#{2,3}\s+Updated position\b.*$",
    re.IGNORECASE,
)


def _scan_updated_position_semantic_mismatches(
    *,
    live_text: str,
    revised_answer: str,
) -> list[dict[str, Any]]:
    if not live_text or not revised_answer:
        return []
    markers = list(_UPDATED_POSITION_RE.finditer(live_text))
    if not markers:
        return []
    revised_norm = _normalize_for_semantic_match(revised_answer)
    if len(revised_norm) < 80:
        return []
    mismatches: list[dict[str, Any]] = []
    for index, marker in enumerate(markers):
        end = markers[index + 1].start() if index + 1 < len(markers) else len(live_text)
        block = live_text[marker.start() : end].strip()
        block_norm = _normalize_for_semantic_match(block)
        if len(block_norm) < 80:
            continue
        similarity = SequenceMatcher(
            None,
            block_norm[:4000],
            revised_norm[:4000],
        ).ratio()
        if similarity >= 0.48:
            continue
        mismatches.append(
            {
                "surface": "live_narration",
                "kind": "updated_position_mismatch",
                "line": live_text.count("\n", 0, marker.start()) + 1,
                "similarity": round(similarity, 3),
                "match": _compact(block, max_chars=160),
                "expected_source": "result.revised_answer",
            }
        )
    return mismatches


def _normalize_for_semantic_match(value: str) -> str:
    text = re.sub(r"(?m)^\s*(?:[•*-]\s*)?#{1,6}\s*", "", str(value or "").lower())
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _is_allowed_product_match(*, term: str, line: str, match_text: str) -> bool:
    """Allow domain uses that share words with internal-hygiene terms."""
    if term != "independent review":
        return False
    lowered = line.lower()
    if not re.search(r"\bindependent\s+review\b", match_text, re.IGNORECASE):
        return False
    # The banned phrase is meant to catch hidden-review attribution such as
    # "this point survived independent review". It should not punish ordinary
    # outside diligence, e.g. equity/runway/legal/security review.
    diligence_terms = {
        "cap table",
        "counsel",
        "diligence",
        "equity",
        "financial",
        "legal",
        "runway",
        "security",
        "technical",
        "term sheet",
        "terms",
    }
    return any(token in lowered for token in diligence_terms)


def _raise_run_health_at_least(run_health: dict[str, Any], severity: str) -> None:
    current = _text(run_health.get("overall")) or "healthy"
    current_rank = _HEALTH_SEVERITY_RANK.get(current, 0)
    target_rank = _HEALTH_SEVERITY_RANK.get(severity, _HEALTH_SEVERITY_RANK["degraded"])
    if current_rank < target_rank:
        run_health["overall"] = severity


def _overall_from_issue_details(issue_details: list[dict[str, Any]]) -> str:
    highest = 0
    overall = "healthy"
    for detail in issue_details:
        severity = _text(detail.get("severity"))
        rank = _HEALTH_SEVERITY_RANK.get(severity, _HEALTH_SEVERITY_RANK["degraded"])
        if rank > highest:
            highest = rank
            overall = severity
    return "healthy" if highest == 0 else overall


def _refresh_overall_after_clearing_issues(
    run_health: dict[str, Any],
    issues: list[str],
    issue_details: list[dict[str, Any]],
) -> None:
    if not _text(run_health.get("overall")):
        run_health["overall"] = "healthy"
    elif issue_details:
        run_health["overall"] = _overall_from_issue_details(issue_details)
    elif not issues:
        run_health["overall"] = "healthy"


def _refresh_derived_health_fields(run_health: dict[str, Any]) -> None:
    details = [
        dict(item)
        for item in _list(run_health.get("issue_details"))
        if isinstance(item, Mapping)
    ]
    run_health["issue_axis_counts"] = _issue_axis_counts(details)
    run_health["partial_health_causes"] = [
        _text(item.get("code"))
        for item in details
        if _text(item.get("code")) and _text(item.get("severity")) == "partial"
    ]
    refresh_provider_boundary_health(run_health)


def _issue_axis_counts(issue_details: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for detail in issue_details:
        axis = _text(detail.get("axis"))
        if not axis:
            continue
        counts[axis] = counts.get(axis, 0) + 1
    return counts


def _add_issue_detail(issue_details: list[dict[str, Any]], detail: dict[str, Any]) -> None:
    code = _text(detail.get("code"))
    if any(_text(item.get("code")) == code for item in issue_details):
        return
    issue_details.append(detail)


def _add_once(items: list[str], value: str) -> None:
    if value and value not in items:
        items.append(value)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [_text(item) for item in value if _text(item)]


def _text(value: object) -> str:
    return str(value or "").strip()


def _compact(value: str, *, max_chars: int) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
