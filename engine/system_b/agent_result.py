"""Agent-facing result contract for archived Lolla runs.

The contract is intentionally built from already-persisted product artifacts.
It does not inspect private ledgers, V60 chunk IDs, lane internals, or hidden
operator-only state. Those remain available through the archive/Observatory for
human inspection, while this file gives agents a compact handoff.
"""
from __future__ import annotations

import datetime as _dt
import json
import re
import shutil
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .audit_mode import risk_mode_from_result
from .capture_adequacy import capture_adequacy_from_artifacts
from .provider_boundary_health import build_provider_boundary_health


AGENT_RESULT_SCHEMA_VERSION = "lolla_agent_result.v1"
AGENT_RESULT_FILENAME = "agent_result.json"

CALLER_ACTIONS = frozenset(
    {
        "use_revised_answer",
        "ask_user_first",
        "rerun_deeper",
        "do_not_use_run_degraded",
        "unsupported_high_stakes_domain",
    }
)

_SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}
_QUESTION_LIMIT = 8
_SUMMARY_LIMIT = 5


def build_agent_result(
    run_dir: Path,
    *,
    run_id: str,
    case_id: str = "",
    created_at: str | None = None,
    observatory_url: str = "",
    observatory_status: str = "",
) -> dict[str, Any]:
    """Build a compact machine-readable result for an archived Lolla run."""
    run_dir = Path(run_dir)
    result = _read_json_object(run_dir / "result.json")
    extraction = _read_json_object(run_dir / "extraction.json")
    run_health = _mapping(result.get("run_health"))
    provider_boundary_health = build_provider_boundary_health(run_health)
    capture_adequacy = capture_adequacy_from_artifacts(
        extraction=extraction,
        result=result,
    )
    artifact_status = _artifact_status(run_dir=run_dir, result=result)
    risk_mode = _risk_mode(result)
    status, status_reason = _status(
        result=result,
        extraction=extraction,
        run_health=run_health,
        provider_boundary_health=provider_boundary_health,
        capture_adequacy=capture_adequacy,
        artifact_status=artifact_status,
    )
    caller_action = _caller_action(
        status=status,
        run_health=run_health,
        artifact_status=artifact_status,
        risk_mode=risk_mode,
    )
    changed_advice_summary = _changed_advice_summary(result)
    take_backs = _take_backs(result)
    human_questions = _human_questions(result)
    do_not_act_before = _do_not_act_before(
        result=result,
        caller_action=caller_action,
        artifact_status=artifact_status,
        status_reason=status_reason,
    )

    return {
        "schema_version": AGENT_RESULT_SCHEMA_VERSION,
        "created_at": created_at or _utc_now_iso(),
        "run_id": run_id,
        "case_id": case_id,
        "status": status,
        "status_reason": status_reason,
        "run_health_overall": _text(run_health.get("overall")) or "unknown",
        "product_output_health": _text(run_health.get("product_output_health")) or "unknown",
        "live_output_health": _text(run_health.get("live_output_health")) or "unknown",
        "provider_boundary_health": provider_boundary_health,
        "capture_adequacy": _capture_adequacy_compact(capture_adequacy),
        "risk_mode": risk_mode,
        "caller_action": caller_action,
        "main_counter_pressure": _main_counter_pressure(result),
        "position_changed": _position_changed(
            result=result,
            changed_advice_summary=changed_advice_summary,
            take_backs=take_backs,
        ),
        "changed_advice_summary": changed_advice_summary,
        "take_backs": take_backs,
        "human_questions": human_questions,
        "do_not_act_before": do_not_act_before,
        "artifact_status": artifact_status,
        "artifact_paths": _artifact_paths(
            run_dir=run_dir,
            observatory_url=observatory_url,
            observatory_status=observatory_status,
        ),
        "usage": _usage(result),
        "notes": _notes(
            status=status,
            caller_action=caller_action,
            contained_provider_boundary_warning_only=_contained_provider_boundary_warning_only(
                run_health=run_health,
                provider_boundary_health=provider_boundary_health,
            ),
            provider_boundary_health=provider_boundary_health,
            capture_adequacy=capture_adequacy,
        ),
    }


def write_agent_result(
    run_dir: Path,
    *,
    run_id: str,
    case_id: str = "",
    created_at: str | None = None,
    observatory_url: str = "",
    observatory_status: str = "",
    tmp_copy_path: Path | None = None,
) -> tuple[Path, dict[str, Any]]:
    """Write ``agent_result.json`` and optionally copy it to an in-flight path."""
    run_dir = Path(run_dir)
    payload = build_agent_result(
        run_dir,
        run_id=run_id,
        case_id=case_id,
        created_at=created_at,
        observatory_url=observatory_url,
        observatory_status=observatory_status,
    )
    path = run_dir / AGENT_RESULT_FILENAME
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if tmp_copy_path is not None:
        tmp_copy_path = Path(tmp_copy_path)
        tmp_copy_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, tmp_copy_path)
    return path, payload


def _status(
    *,
    result: Mapping[str, Any],
    extraction: Mapping[str, Any],
    run_health: Mapping[str, Any],
    provider_boundary_health: Mapping[str, Any],
    capture_adequacy: Mapping[str, Any],
    artifact_status: Mapping[str, str],
) -> tuple[str, str]:
    extraction_status = _text(extraction.get("status"))
    if extraction_status == "capture_critical":
        return "incomplete", "conversation capture was marked critical"
    if not result:
        return "incomplete", "result artifact is missing"

    overall = _text(run_health.get("overall")) or "unknown"
    if overall in {"critical", "degraded"}:
        return "degraded", f"run_health.overall is {overall}"

    product_health = _text(run_health.get("product_output_health"))
    if product_health == "unsafe":
        return "degraded", "product output was marked unsafe"
    live_health = _text(run_health.get("live_output_health"))
    if live_health == "unsafe":
        return "degraded", "live output was marked unsafe"
    if _text(capture_adequacy.get("status")) == "critical":
        return "degraded", "capture adequacy was marked critical"
    if overall == "partial":
        if _contained_provider_boundary_warning_only(
            run_health=run_health,
            provider_boundary_health=provider_boundary_health,
        ):
            return (
                "partial",
                "provider-boundary warning is contained; conservative policy still requires inspection",
            )
        if _text(provider_boundary_health.get("status")) == "warning_unknown_persistence":
            return "partial", "provider-boundary warning has unknown persistence status"
        return "partial", "run_health.overall is partial"

    missing_required = [
        name
        for name in ("result", "revised_answer", "memo")
        if artifact_status.get(name) != "present"
    ]
    if missing_required:
        return "incomplete", "required artifact missing: " + ", ".join(missing_required)
    return "ok", "required product artifacts are present"


def _caller_action(
    *,
    status: str,
    run_health: Mapping[str, Any],
    artifact_status: Mapping[str, str],
    risk_mode: str,
) -> str:
    if status in {"partial", "degraded", "incomplete"}:
        return "do_not_use_run_degraded"
    if risk_mode == "high_stakes":
        return "ask_user_first"
    if _text(run_health.get("product_output_health")) == "unsafe":
        return "do_not_use_run_degraded"
    if artifact_status.get("revised_answer") != "present" or artifact_status.get("memo") != "present":
        return "do_not_use_run_degraded"
    return "use_revised_answer"


def _risk_mode(result: Mapping[str, Any]) -> str:
    return risk_mode_from_result(result)


def _main_counter_pressure(result: Mapping[str, Any]) -> str:
    for key in ("main_counter_pressure", "strongest_counter_pressure", "counter_pressure"):
        value = _text(result.get(key))
        if value:
            return _compact(value)

    findings = [_mapping(item) for item in _list(_mapping(result.get("delta_card")).get("findings"))]
    findings = sorted(
        findings,
        key=lambda item: _SEVERITY_ORDER.get(_text(item.get("severity")).lower(), 99),
    )
    for finding in findings:
        value = _text(finding.get("challenge_statement")) or _text(finding.get("reversal_trigger"))
        if value:
            return _compact(value)

    for reframing in _list(_mapping(result.get("frame_pressure_card")).get("reframings")):
        item = _mapping(reframing)
        value = _text(item.get("what_opens")) or _text(item.get("reframed_question"))
        if value:
            return _compact(value)

    for question in _human_questions(result):
        if question:
            return _compact(question)
    return ""


def _changed_advice_summary(result: Mapping[str, Any]) -> list[str]:
    direct = _clean_items(result.get("changed_advice_summary"))
    if direct:
        return direct[:_SUMMARY_LIMIT]
    return _clean_items(result.get("memo_what_changed"))[:_SUMMARY_LIMIT]


def _take_backs(result: Mapping[str, Any]) -> list[str]:
    direct = _clean_items(result.get("take_backs"))
    if direct:
        return direct[:_SUMMARY_LIMIT]
    return _clean_items(result.get("memo_take_back_or_set_aside"))[:_SUMMARY_LIMIT]


def _human_questions(result: Mapping[str, Any]) -> list[str]:
    direct = _clean_items(result.get("human_questions"))
    if direct:
        return direct[:_QUESTION_LIMIT]

    questions: list[str] = []
    for gap in _list(_mapping(result.get("structural_coverage_card")).get("gap_questions")):
        item = _mapping(gap)
        for question in _list(item.get("questions")):
            _append_unique(questions, _compact(_text(question)))
        _append_unique(questions, _compact(_text(item.get("question"))))
    return questions[:_QUESTION_LIMIT]


def _do_not_act_before(
    *,
    result: Mapping[str, Any],
    caller_action: str,
    artifact_status: Mapping[str, str],
    status_reason: str,
) -> list[str]:
    direct = _clean_items(result.get("do_not_act_before"))
    if direct:
        return direct[:_SUMMARY_LIMIT]
    if caller_action == "do_not_use_run_degraded":
        reasons = [status_reason] if status_reason else []
        for name in ("result", "revised_answer", "memo"):
            if artifact_status.get(name) != "present":
                reasons.append(f"{name} artifact is missing")
        if reasons:
            return ["Inspect or rerun Lolla before relying on this audit result."]
        return ["Do not rely on this audit result until the degraded run health is resolved."]
    return _gate_like_sentences(result)[:_SUMMARY_LIMIT]


def _gate_like_sentences(result: Mapping[str, Any]) -> list[str]:
    text = "\n".join(
        _text(result.get(key))
        for key in (
            "memo_what_changed",
            "memo_orientation_note",
            "revised_answer",
        )
        if _text(result.get(key))
    )
    if not text:
        return []
    markers = (
        " before ",
        " until ",
        " unless ",
        " only after ",
        " first ",
        " gate",
        " confirm ",
        " verify ",
        " test ",
        " stop ",
    )
    gates: list[str] = []
    for sentence in _split_sentences(text):
        lower = f" {sentence.lower()} "
        if any(marker in lower for marker in markers):
            _append_unique(gates, _compact(sentence))
    return gates


def _position_changed(
    *,
    result: Mapping[str, Any],
    changed_advice_summary: Sequence[str],
    take_backs: Sequence[str],
) -> bool:
    value = result.get("position_changed")
    if isinstance(value, bool):
        return value
    if changed_advice_summary or take_backs:
        combined = " ".join([*changed_advice_summary, *take_backs]).lower()
        if "no material change" in combined or "no meaningful change" in combined:
            return False
        return True
    return False


def _artifact_status(*, run_dir: Path, result: Mapping[str, Any]) -> dict[str, str]:
    revised_present = (run_dir / "revised.txt").is_file() or bool(_text(result.get("revised_answer")))
    return {
        "conversation": _present(run_dir / "conversation.txt"),
        "extraction": _present(run_dir / "extraction.json"),
        "result": _present(run_dir / "result.json"),
        "revised_answer": "present" if revised_present else "missing",
        "memo": _present(run_dir / "memo.md"),
        "reasoning_trace": _present(run_dir / "reasoning_trace.json"),
    }


def _artifact_paths(
    *,
    run_dir: Path,
    observatory_url: str,
    observatory_status: str,
) -> dict[str, str]:
    paths = {
        "archive": str(run_dir),
        "agent_result": str(run_dir / AGENT_RESULT_FILENAME),
    }
    for key, filename in (
        ("conversation", "conversation.txt"),
        ("extraction", "extraction.json"),
        ("result", "result.json"),
        ("revised_answer", "revised.txt"),
        ("memo", "memo.md"),
        ("reasoning_trace", "reasoning_trace.json"),
    ):
        path = run_dir / filename
        if path.exists():
            paths[key] = str(path)
    if observatory_url and observatory_status == "live":
        paths["observatory_url"] = observatory_url
    return paths


def _usage(result: Mapping[str, Any]) -> dict[str, Any]:
    usage = _mapping(result.get("usage_summary"))
    return {
        "estimated_total_cost_usd": usage.get("estimated_total_cost_usd"),
        "cost_estimate_state": _text(usage.get("cost_estimate_state")) or "unknown",
        "pricing_table_version": _text(usage.get("pricing_table_version")),
    }


def _capture_adequacy_compact(capture_adequacy: Mapping[str, Any]) -> dict[str, Any]:
    if not capture_adequacy:
        return {"status": "unknown"}
    return {
        "schema_version": _text(capture_adequacy.get("schema_version")),
        "status": _text(capture_adequacy.get("status")) or "unknown",
        "capture_strategy": _text(capture_adequacy.get("capture_strategy")) or "unknown",
        "declared_turn_count": capture_adequacy.get("declared_turn_count"),
        "captured_turn_count": capture_adequacy.get("captured_turn_count"),
        "omitted_turn_count": capture_adequacy.get("omitted_turn_count"),
        "risk_flags": _clean_items(capture_adequacy.get("risk_flags")),
        "notes": _clean_items(capture_adequacy.get("notes"))[:3],
    }


def _contained_provider_boundary_warning_only(
    *,
    run_health: Mapping[str, Any],
    provider_boundary_health: Mapping[str, Any],
) -> bool:
    if _text(provider_boundary_health.get("status")) != "warning_contained":
        return False
    if _text(run_health.get("overall")) != "partial":
        return False
    if _text(run_health.get("product_output_health")) == "unsafe":
        return False
    if _text(run_health.get("live_output_health")) == "unsafe":
        return False
    issue_codes = {
        _text(item.get("code"))
        for item in _list(run_health.get("issue_details"))
        if isinstance(item, Mapping)
        and _text(item.get("severity")) in {"partial", "degraded", "critical"}
    }
    if issue_codes:
        return issue_codes == {"vendor_boundary_reasoning_leak"}
    partial_causes = set(_clean_items(run_health.get("partial_health_causes")))
    if partial_causes:
        return partial_causes == {"vendor_boundary_reasoning_leak"}
    issues = set(_clean_items(run_health.get("issues")))
    return issues == {"vendor_boundary_reasoning_leak"}


def _notes(
    *,
    status: str,
    caller_action: str,
    contained_provider_boundary_warning_only: bool,
    provider_boundary_health: Mapping[str, Any],
    capture_adequacy: Mapping[str, Any],
) -> list[str]:
    capture_status = _text(capture_adequacy.get("status"))
    if capture_status == "critical":
        return [
            "Capture adequacy is critical; rerun Lolla with a complete conversation capture before relying on this audit."
        ]
    if capture_status == "warn":
        omitted = _text(capture_adequacy.get("omitted_turn_count")) or "some"
        return [
            f"Capture adequacy is warning-level; {omitted} middle turns may be omitted, so inspect capture metadata before relying on this audit."
        ]
    if caller_action == "use_revised_answer":
        return [
            "Use the revised answer, memo, and artifact pointers together; this contract is not a safety or fact-checking guarantee."
        ]
    if (
        caller_action == "do_not_use_run_degraded"
        and status == "partial"
        and contained_provider_boundary_warning_only
        and _text(provider_boundary_health.get("status")) == "warning_contained"
    ):
        return [
            "Provider-boundary warning was contained by product/live hygiene, but this contract remains conservative until the caller explicitly accepts that policy."
        ]
    if status in {"partial", "degraded", "incomplete"}:
        return [
            "This run is not suitable for automatic agent action. Inspect the archive or rerun before relying on it."
        ]
    return []


def _clean_items(value: Any) -> list[str]:
    if isinstance(value, list):
        source = value
    else:
        source = _split_bullets_or_sentences(_text(value))
    items: list[str] = []
    for item in source:
        text = _strip_markdown_prefix(_compact(_text(item)))
        if text:
            _append_unique(items, text)
    return items


def _split_bullets_or_sentences(text: str) -> list[str]:
    if not text:
        return []
    bullet_lines = [
        _strip_markdown_prefix(line)
        for line in text.splitlines()
        if re.match(r"^\s*(?:[-*]|\d+[.)])\s+", line)
    ]
    if bullet_lines:
        return bullet_lines
    return _split_sentences(text)


def _split_sentences(text: str) -> list[str]:
    text = re.sub(r"#+\s*", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    pieces = re.split(r"(?<=[.!?])\s+", text)
    if len(pieces) == 1:
        pieces = [part.strip() for part in re.split(r"\s*;\s*", text)]
    return [part.strip() for part in pieces if part.strip()]


def _strip_markdown_prefix(text: str) -> str:
    text = re.sub(r"^\s*#+\s*", "", text)
    text = re.sub(r"^\s*(?:[-*]|\d+[.)])\s+", "", text)
    return text.strip()


def _compact(text: str, *, max_chars: int = 420) -> str:
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0].rstrip(".,;:") + "..."


def _append_unique(items: list[str], value: str) -> None:
    value = _compact(value)
    if value and value not in items:
        items.append(value)


def _present(path: Path) -> str:
    return "present" if path.exists() and path.is_file() else "missing"


def _read_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _utc_now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: Any) -> str:
    return str(value or "").strip()
