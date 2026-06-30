"""Read-only Product Delta Evidence readiness and shell generation.

This module checks existing Lolla cases for Product Delta Evidence review
readiness. It reads structured archive JSON and artifact presence only. It does
not run Lolla, call models, read raw transcript/memo/revised-answer content,
mutate archives, score advice quality, or create human labels.
"""
from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


PRODUCT_DELTA_READINESS_SCHEMA_VERSION = "lolla.product_delta_readiness_report.v0"
PRODUCT_DELTA_SEED_CASES_SCHEMA_VERSION = "lolla.product_delta_seed_cases.v0"
PROVISIONAL_REVIEW_SCHEMA_VERSION = "lolla.vanilla_vs_lolla_provisional_review.v0"

REQUIRED_RAW_ARTIFACTS = (
    "conversation.txt",
    "revised.txt",
    "memo.md",
)
REQUIRED_STRUCTURED_ARTIFACTS = (
    "evaluation.json",
    "agent_result.json",
    "reasoning_trace.json",
)
OPTIONAL_STRUCTURED_ARTIFACTS = (
    "extraction_adequacy_report.json",
)

READINESS_STATES = (
    "ready_for_codex_provisional_review",
    "thin_safe_context",
    "missing_vanilla_baseline",
    "missing_revised_answer",
    "missing_review_safe_summary",
    "degraded_run_health",
    "blocked_private_content_only",
    "missing_archive_case",
)

NON_CLAIMS = (
    "not human review",
    "not ground truth",
    "not judge calibration data",
    "not product proof",
    "not agent approval",
    "not answer-quality scoring",
    "not automatic labeling",
)


class ProductDeltaReadinessInputError(ValueError):
    """Deterministic, sanitized input error."""


def load_seed_cases(path: Path | str) -> dict[str, Any]:
    seed_path = Path(path)
    try:
        payload = json.loads(seed_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ProductDeltaReadinessInputError("case list is not valid JSON") from exc
    except OSError as exc:
        raise ProductDeltaReadinessInputError(
            f"case list could not be read:{type(exc).__name__}"
        ) from exc
    if not isinstance(payload, dict):
        raise ProductDeltaReadinessInputError("case list is not a JSON object")
    cases = payload.get("cases")
    if not isinstance(cases, list):
        raise ProductDeltaReadinessInputError("case list is missing cases array")
    return payload


def load_review_json(path: Path | str | None) -> Mapping[str, Any] | None:
    if path is None:
        return None
    review_path = Path(path)
    try:
        payload = json.loads(review_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ProductDeltaReadinessInputError("review JSON is not valid JSON") from exc
    except OSError as exc:
        raise ProductDeltaReadinessInputError(
            f"review JSON could not be read:{type(exc).__name__}"
        ) from exc
    if not isinstance(payload, dict):
        raise ProductDeltaReadinessInputError("review JSON is not a JSON object")
    return payload


def build_product_delta_readiness_report(
    *,
    seed_cases: Mapping[str, Any],
    archive_root: Path | str | None = None,
    review_json: Mapping[str, Any] | None = None,
    review_json_relpath: str | None = None,
) -> dict[str, Any]:
    """Build a deterministic readiness report and PR72-shaped shell batch."""

    archive_root_path = Path(archive_root).expanduser() if archive_root else None
    case_records: list[dict[str, Any]] = []
    shells: list[dict[str, Any]] = []
    review_index = _review_index(review_json)

    for raw_case in _case_items(seed_cases.get("cases")):
        case = _normalize_seed_case(raw_case)
        review_record = review_index.get(case["archive_relpath"])
        record = _build_case_readiness(
            case=case,
            archive_root=archive_root_path,
            review_record=review_record,
        )
        shell = _build_provisional_shell(
            case=case,
            readiness_state=record["readiness_state"],
            reviewed_artifacts=_reviewed_artifacts_for_shell(
                case=case,
                review_json_relpath=review_json_relpath,
            ),
        )
        record["provisional_review_shell_ref"] = {
            "included_in_report": True,
            "schema_version": PROVISIONAL_REVIEW_SCHEMA_VERSION,
            "semantic_fields_populated": False,
            "net_decision_read_provisional": "inconclusive",
        }
        case_records.append(record)
        shells.append(shell)

    readiness_counts = Counter(record["readiness_state"] for record in case_records)
    ready_count = readiness_counts["ready_for_codex_provisional_review"]
    thin_or_blocked = len(case_records) - ready_count
    return {
        "schema_version": PRODUCT_DELTA_READINESS_SCHEMA_VERSION,
        "review_mode": "codex_assisted_provisional",
        "case_list_schema_version": _text(seed_cases.get("schema_version")),
        "case_count": len(case_records),
        "source_artifacts": _strings(seed_cases.get("source_artifacts")),
        "custody_flags": {
            "local_only": True,
            "archive_root_supplied": archive_root_path is not None,
            "archive_root_path_included": False,
            "archive_mutated": False,
            "raw_transcript_read": False,
            "raw_memo_read": False,
            "raw_revised_answer_read": False,
            "raw_private_content_included": False,
            "structured_archive_json_read": archive_root_path is not None,
            "review_json_read": review_json is not None,
            "model_calls": 0,
            "llm_judge_used": False,
            "answer_quality_scored": False,
            "automatic_labels_created": False,
        },
        "aggregate": {
            "readiness_state_counts": {
                state: readiness_counts[state] for state in READINESS_STATES
            },
            "ready_for_codex_provisional_review": ready_count,
            "thin_or_blocked": thin_or_blocked,
            "provisional_review_shell_count": len(shells),
            "semantic_shell_fields_populated": False,
        },
        "cases": case_records,
        "provisional_review_shells": shells,
        "non_claims": [
            "This report does not test whether Lolla improved any decision.",
            "This report does not create human labels or ground truth.",
            "This report does not provide judge calibration data.",
            "This report does not score answer quality.",
            "This report does not approve agent use.",
            "PR72-shaped shells are deterministic scaffolds; semantic fields remain unfilled until Codex-assisted provisional review or later human review.",
        ],
    }


def render_product_delta_readiness_json(report: Mapping[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_product_delta_readiness_markdown(report: Mapping[str, Any]) -> str:
    aggregate = _mapping(report.get("aggregate"))
    counts = _mapping(aggregate.get("readiness_state_counts"))
    lines = [
        "# Product Delta Eval Readiness And Provisional Run v0",
        "",
        "Status: generated read-only report",
        "Review capacity mode: `codex_assisted_provisional`",
        "",
        "## Summary",
        "",
        f"- Cases checked: `{_safe_int(report.get('case_count'))}`",
        (
            "- Ready for Codex provisional review: "
            f"`{_safe_int(aggregate.get('ready_for_codex_provisional_review'))}`"
        ),
        f"- Thin or blocked: `{_safe_int(aggregate.get('thin_or_blocked'))}`",
        (
            "- PR72-shaped deterministic shells: "
            f"`{_safe_int(aggregate.get('provisional_review_shell_count'))}`"
        ),
        "- Semantic shell fields populated: `false`",
        "- Model calls: `0`",
        "- Archive mutated: `false`",
        "",
        "## What This Tests",
        "",
        "This report tests whether existing Lolla cases can be converted into",
        "conservative, schema-shaped Product Delta Evidence review shells without",
        "runtime calls or fake human judgment. It does not test whether Lolla",
        "improved any decision.",
        "",
        "The deterministic script checks artifact presence, structured JSON",
        "readiness signals, review-safe context availability, and non-claim",
        "metadata. It leaves likely-action, material-difference, useful-friction,",
        "lost-value, interpretation-adequacy, and net-decision fields unjudged.",
        "",
        "## Source Artifacts",
        "",
    ]
    source_artifacts = _strings(report.get("source_artifacts"))
    if source_artifacts:
        lines.extend(f"- `{artifact}`" for artifact in source_artifacts)
    else:
        lines.append("- None supplied.")
    lines.extend(
        [
            "",
            "## Custody Flags",
            "",
        ]
    )
    custody = _mapping(report.get("custody_flags"))
    for key in sorted(custody):
        value = custody.get(key)
        if isinstance(value, bool):
            rendered = "true" if value else "false"
        else:
            rendered = str(value)
        lines.append(f"- `{key}`: `{rendered}`")
    lines.extend(
        [
            "",
        "## Readiness Counts",
        "",
        ]
    )
    for state in READINESS_STATES:
        lines.append(f"- `{state}`: `{_safe_int(counts.get(state))}`")

    lines.extend(
        [
            "",
            "## Cases",
            "",
            "| case | readiness | blocking reasons | weakening reasons |",
            "|---|---|---|---|",
        ]
    )
    for case in _case_records(report.get("cases")):
        lines.append(
            "| "
            f"`{_text(case.get('archive_relpath'))}` | "
            f"`{_text(case.get('readiness_state'))}` | "
            f"{_format_items(case.get('blocking_reasons'))} | "
            f"{_format_items(case.get('weakening_reasons'))} |"
        )

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
        ]
    )
    for item in _strings(report.get("non_claims")):
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def write_text(path: Path | str, payload: str) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(payload, encoding="utf-8")


def _build_case_readiness(
    *,
    case: Mapping[str, Any],
    archive_root: Path | None,
    review_record: Mapping[str, Any] | None,
) -> dict[str, Any]:
    artifact_records: list[dict[str, Any]] = []
    structured_signals: dict[str, Any] = {
        "evaluation_overall": None,
        "caller_readiness": None,
        "agent_caller_action": None,
        "reasoning_trace_schema_version": None,
        "extraction_adequacy_status": None,
    }

    run_dir: Path | None = None
    if archive_root is not None:
        run_dir = archive_root / case["archive_relpath"]
        if run_dir.exists() and run_dir.is_dir():
            for artifact in REQUIRED_RAW_ARTIFACTS:
                artifact_records.append(_raw_artifact_record(run_dir, artifact))
            for artifact in REQUIRED_STRUCTURED_ARTIFACTS:
                record, payload = _structured_artifact_record(run_dir, artifact)
                artifact_records.append(record)
                _update_structured_signals(
                    signals=structured_signals,
                    artifact=artifact,
                    payload=payload,
                )
            for artifact in OPTIONAL_STRUCTURED_ARTIFACTS:
                record, payload = _structured_artifact_record(run_dir, artifact)
                artifact_records.append(record)
                _update_structured_signals(
                    signals=structured_signals,
                    artifact=artifact,
                    payload=payload,
                )

    review_context = _review_safe_context(case=case, review_record=review_record)
    readiness_state, blocking, weakening = _readiness_state(
        case=case,
        archive_root_supplied=archive_root is not None,
        run_dir_exists=run_dir is not None and run_dir.exists() and run_dir.is_dir(),
        artifacts=artifact_records,
        signals=structured_signals,
        review_context=review_context,
    )
    return {
        "case_id": case["case_id"],
        "run_id": case["run_id"],
        "archive_relpath": case["archive_relpath"],
        "readiness_state": readiness_state,
        "ready_for_codex_provisional_review": (
            readiness_state == "ready_for_codex_provisional_review"
        ),
        "ready_for_later_human_review": (
            readiness_state == "ready_for_codex_provisional_review"
        ),
        "blocking_reasons": blocking,
        "weakening_reasons": weakening,
        "artifact_presence": artifact_records,
        "structured_signals": structured_signals,
        "review_safe_context": review_context,
    }


def _build_provisional_shell(
    *,
    case: Mapping[str, Any],
    readiness_state: str,
    reviewed_artifacts: list[str],
) -> dict[str, Any]:
    first_failure = "unclear"
    if readiness_state == "degraded_run_health":
        first_failure = "artifact_custody"
    elif readiness_state != "ready_for_codex_provisional_review":
        first_failure = "review_surface"
    return {
        "schema_version": PROVISIONAL_REVIEW_SCHEMA_VERSION,
        "review_mode": "codex_assisted_provisional",
        "human_validated": False,
        "ground_truth": False,
        "judge_calibration_eligible": False,
        "reviewer_type": "codex",
        "case_id": case["case_id"],
        "archive_relpath": case["archive_relpath"],
        "reviewed_artifacts": reviewed_artifacts,
        "raw_private_content_included": False,
        "model_calls": 0,
        "archive_mutated": False,
        "vanilla_likely_next_action": _empty_likely_action(),
        "lolla_likely_next_action": _empty_likely_action(),
        "material_difference": {
            "status": "not_reviewed",
            "summary": (
                "Deterministic PR75 shell did not measure material difference; "
                "false is a shell default, not a no-delta claim."
            ),
            "changed": False,
            "uncertainty": "unclear",
        },
        "structural_delta": {
            "action_changed": False,
            "threshold_changed": False,
            "sequence_changed": False,
            "evidence_gate_added_or_changed": False,
            "stop_rule_added_or_changed": False,
            "written_term_added_or_changed": False,
            "scope_changed": False,
            "overclaim_retracted": False,
            "user_answerable_question_added": False,
            "notes": (
                "Not populated by deterministic readiness script; false values "
                "are shell defaults, not claims that no structural delta exists."
            ),
        },
        "decision_leverage": {
            "label": "unclear",
            "rationale": "Requires Codex-assisted provisional review or later human review.",
            "uncertainty": "unclear",
        },
        "friction_read": {
            "useful_friction": "not_applicable",
            "noisy_friction": "not_applicable",
            "missing_friction": "not_applicable",
            "grounded": None,
            "actionable": None,
            "proportionate": None,
            "rationale": "Not measured by deterministic readiness script.",
        },
        "lost_value": {
            "present": None,
            "categories": [],
            "rationale": "Not measured by deterministic readiness script.",
        },
        "interpretation_adequacy": {
            "label": "unclear",
            "failure_modes": [],
            "rationale": "Not measured by deterministic readiness script.",
            "would_better_interpretation_change_answer": "unclear",
        },
        "first_upstream_failure": {
            "surface": first_failure,
            "summary": (
                "Deterministic readiness state is "
                f"{readiness_state}; semantic upstream failure was not judged."
            ),
        },
        "net_decision_read_provisional": {
            "label": "inconclusive",
            "rationale": (
                "Deterministic shell generation does not decide whether Lolla "
                "helped, added noise, or changed the decision."
            ),
        },
        "codex_uncertainty_notes": [
            "Shell generated without semantic review.",
            "Likely-action and answer-quality fields require Codex-assisted provisional review or later human validation.",
        ],
        "human_followup_questions": [
            "What exact next action did the vanilla answer make likely?",
            "What exact next action did the Lolla revised answer make likely?",
            "Which action, threshold, sequence, evidence gate, stop rule, written term, scope, or user-answerable question changed?",
        ],
        "non_claims": list(NON_CLAIMS),
    }


def _empty_likely_action() -> dict[str, Any]:
    return {
        "status": "not_reviewed",
        "summary": (
            "Deterministic PR75 shell did not infer likely next action; requires "
            "Codex-assisted provisional review or later human review."
        ),
        "basis": [
            "Artifact readiness was checked without reading raw transcript, memo, or revised-answer content."
        ],
        "uncertainty": "unclear",
        "reviewer_inferred": False,
    }


def _readiness_state(
    *,
    case: Mapping[str, Any],
    archive_root_supplied: bool,
    run_dir_exists: bool,
    artifacts: Sequence[Mapping[str, Any]],
    signals: Mapping[str, Any],
    review_context: Mapping[str, Any],
) -> tuple[str, list[str], list[str]]:
    blocking: list[str] = []
    weakening: list[str] = []
    artifact_statuses = {
        _text(item.get("artifact")): _text(item.get("status")) for item in artifacts
    }
    if not archive_root_supplied:
        blocking.append("archive_root_not_supplied")
        return "thin_safe_context", blocking, weakening
    if not run_dir_exists:
        blocking.append("archive_case_missing")
        return "missing_archive_case", blocking, weakening
    if _degraded(signals=signals, review_context=review_context):
        blocking.append("degraded_or_excluded_run_health")
        return "degraded_run_health", blocking, weakening
    if artifact_statuses.get("conversation.txt") != "present":
        blocking.append("conversation_artifact_missing")
        return "missing_vanilla_baseline", blocking, weakening
    if _text(case.get("vanilla_baseline_status")) in ("", "missing", "unknown"):
        blocking.append("vanilla_baseline_status_not_supplied")
        return "missing_vanilla_baseline", blocking, weakening
    if artifact_statuses.get("revised.txt") != "present":
        blocking.append("revised_answer_missing")
        return "missing_revised_answer", blocking, weakening
    if not bool(review_context.get("review_safe_summary_available")):
        blocking.append("review_safe_summary_missing")
        return "missing_review_safe_summary", blocking, weakening

    missing_structured = [
        name
        for name in REQUIRED_STRUCTURED_ARTIFACTS
        if artifact_statuses.get(name) != "present"
    ]
    if missing_structured:
        blocking.extend(f"missing_or_malformed:{name}" for name in missing_structured)
        if all(
            artifact_statuses.get(name) == "present" for name in REQUIRED_RAW_ARTIFACTS
        ):
            return "blocked_private_content_only", blocking, weakening
        return "thin_safe_context", blocking, weakening

    if _text(signals.get("evaluation_overall")) == "warn":
        weakening.append("evaluation_overall_warn")
    if _text(signals.get("caller_readiness")) == "inspect_first":
        weakening.append("caller_readiness_inspect_first")
    if _text(review_context.get("artifact_sufficiency")) == "sufficient_with_caveat":
        weakening.append("artifact_sufficiency_caveat")
    return "ready_for_codex_provisional_review", blocking, weakening


def _degraded(
    *,
    signals: Mapping[str, Any],
    review_context: Mapping[str, Any],
) -> bool:
    if _text(signals.get("evaluation_overall")) == "fail":
        return True
    if _text(signals.get("caller_readiness")) == "do_not_use":
        return True
    caller_action = _text(signals.get("agent_caller_action"))
    if "do_not_use" in caller_action or "degraded" in caller_action:
        return True
    if _text(review_context.get("review_readiness_tier")).endswith("degraded"):
        return True
    if _text(review_context.get("review_status")) == "exclude_from_eval":
        return True
    return False


def _raw_artifact_record(run_dir: Path, artifact: str) -> dict[str, Any]:
    path = run_dir / artifact
    if not path.exists():
        status = "missing"
        byte_count = None
    elif not path.is_file():
        status = "unknown"
        byte_count = None
    else:
        status = "present"
        byte_count = path.stat().st_size
    return {
        "artifact": artifact,
        "status": status,
        "byte_count": byte_count,
        "raw_content_read": False,
    }


def _structured_artifact_record(
    run_dir: Path,
    artifact: str,
) -> tuple[dict[str, Any], Mapping[str, Any] | None]:
    path = run_dir / artifact
    base = {
        "artifact": artifact,
        "status": "missing",
        "byte_count": None,
        "schema_version": None,
        "raw_content_read": False,
    }
    if not path.exists():
        return base, None
    if not path.is_file():
        return {**base, "status": "unknown"}, None
    stat = path.stat()
    try:
        text = path.read_text(encoding="utf-8")
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {**base, "status": "malformed", "byte_count": stat.st_size}, None
    except UnicodeDecodeError:
        return {**base, "status": "malformed", "byte_count": stat.st_size}, None
    if not isinstance(payload, dict):
        return {**base, "status": "malformed", "byte_count": stat.st_size}, None
    return {
        **base,
        "status": "present",
        "byte_count": stat.st_size,
        "schema_version": _text(payload.get("schema_version")) or None,
    }, payload


def _update_structured_signals(
    *,
    signals: dict[str, Any],
    artifact: str,
    payload: Mapping[str, Any] | None,
) -> None:
    if payload is None:
        return
    if artifact == "evaluation.json":
        signals["evaluation_overall"] = _text(payload.get("overall")) or None
        signals["caller_readiness"] = _text(payload.get("caller_readiness")) or None
    elif artifact == "agent_result.json":
        signals["agent_caller_action"] = _text(payload.get("caller_action")) or None
    elif artifact == "reasoning_trace.json":
        signals["reasoning_trace_schema_version"] = (
            _text(payload.get("schema_version")) or None
        )
    elif artifact == "extraction_adequacy_report.json":
        signals["extraction_adequacy_status"] = _text(payload.get("status")) or None


def _review_safe_context(
    *,
    case: Mapping[str, Any],
    review_record: Mapping[str, Any] | None,
) -> dict[str, Any]:
    human_review = _mapping(review_record.get("human_review")) if review_record else {}
    return {
        "review_safe_summary_available": (
            _text(case.get("review_safe_summary_status")) == "available"
            or review_record is not None
        ),
        "review_safe_sources": _strings(case.get("review_safe_sources")),
        "prior_review_record_found": review_record is not None,
        "prior_review_authority": "historical_context_only",
        "review_readiness_tier": _text(review_record.get("review_readiness_tier"))
        if review_record
        else "",
        "artifact_sufficiency": _text(review_record.get("artifact_sufficiency"))
        if review_record
        else "",
        "review_status": _text(human_review.get("review_status")),
        "safe_for_agent_use_not_inferred": True,
        "actionable_delta_label_count": len(_strings(review_record.get("actionable_delta_labels")))
        if review_record
        else 0,
    }


def _review_index(review_json: Mapping[str, Any] | None) -> dict[str, Mapping[str, Any]]:
    if not review_json:
        return {}
    records = review_json.get("records")
    if not isinstance(records, list):
        records = review_json.get("cases")
    if not isinstance(records, list):
        return {}
    index: dict[str, Mapping[str, Any]] = {}
    for item in records:
        if not isinstance(item, Mapping):
            continue
        relpath = _text(item.get("archive_relpath") or item.get("archive_ref"))
        if relpath:
            index[relpath] = item
    return index


def _reviewed_artifacts_for_shell(
    *,
    case: Mapping[str, Any],
    review_json_relpath: str | None,
) -> list[str]:
    artifacts = list(dict.fromkeys(_strings(case.get("review_safe_sources"))))
    if review_json_relpath:
        artifacts.append(review_json_relpath)
    if not artifacts:
        artifacts.append("docs/evals/product-delta-seed-cases-v0.json")
    return list(dict.fromkeys(artifacts))


def _normalize_seed_case(raw_case: Mapping[str, Any]) -> dict[str, Any]:
    case_id = _text(raw_case.get("case_id"))
    run_id = _text(raw_case.get("run_id"))
    archive_relpath = _text(raw_case.get("archive_relpath"))
    if not case_id:
        raise ProductDeltaReadinessInputError("case entry is missing case_id")
    if not run_id:
        raise ProductDeltaReadinessInputError("case entry is missing run_id")
    if not archive_relpath:
        archive_relpath = f"{case_id}/{run_id}"
    if archive_relpath.startswith("/") or ".." in archive_relpath.split("/"):
        raise ProductDeltaReadinessInputError("case entry has unsafe archive_relpath")
    return {
        "case_id": case_id,
        "run_id": run_id,
        "archive_relpath": archive_relpath,
        "vanilla_baseline_status": _text(raw_case.get("vanilla_baseline_status")),
        "review_safe_summary_status": _text(raw_case.get("review_safe_summary_status")),
        "review_safe_sources": _strings(raw_case.get("review_safe_sources")),
    }


def _case_items(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _case_records(value: Any) -> list[Mapping[str, Any]]:
    return _case_items(value)


def _format_items(value: Any) -> str:
    items = _strings(value)
    if not items:
        return "None."
    return "<br>".join(f"`{item}`" for item in items)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [_text(item) for item in value if _text(item)]


def _text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    return ""


def _safe_int(value: Any) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return 0
