"""Deterministic boundary lint for Product Delta Evidence artifacts.

The lint is an offline eval-lane guardrail. It reads only the target files it is
given, validates evidence-boundary metadata and common overclaim patterns, and
does not run Lolla, call models, mutate archives, or judge answer quality.
"""
from __future__ import annotations

import json
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PRODUCT_DELTA_BOUNDARY_LINT_SCHEMA_VERSION = (
    "lolla.product_delta_boundary_lint.v0"
)
PROVISIONAL_REVIEW_SCHEMA_VERSION = "lolla.vanilla_vs_lolla_provisional_review.v0"
PROVISIONAL_TAXONOMY_SCHEMA_VERSION = (
    "lolla.provisional_product_delta_failure_taxonomy.v0"
)

PR72_REQUIRED_FIELDS = (
    "schema_version",
    "review_mode",
    "human_validated",
    "ground_truth",
    "judge_calibration_eligible",
    "reviewer_type",
    "case_id",
    "reviewed_artifacts",
    "raw_private_content_included",
    "model_calls",
    "archive_mutated",
    "vanilla_likely_next_action",
    "lolla_likely_next_action",
    "material_difference",
    "structural_delta",
    "decision_leverage",
    "friction_read",
    "lost_value",
    "interpretation_adequacy",
    "first_upstream_failure",
    "net_decision_read_provisional",
    "codex_uncertainty_notes",
    "human_followup_questions",
    "non_claims",
)

FALSE_METADATA_FIELDS = (
    "human_validated",
    "ground_truth",
    "judge_calibration_eligible",
    "archive_mutated",
    "raw_private_content_included",
)
ZERO_METADATA_FIELDS = ("model_calls",)
FALSE_IF_PRESENT_FIELDS = (
    "automatic_labels",
    "automatic_labels_created",
    "answer_quality_scored",
    "llm_judge_used",
)
FORBIDDEN_FIELD_NAMES = {
    "safe_for_agent_use",
    "approved",
    "approval",
    "approval_status",
    "certified",
    "passed",
    "pass",
    "pass_fail",
    "score",
    "quality_score",
    "answer_quality_score",
    "improvement_score",
    "decision_quality_score",
    "confidence_score",
    "judge_score",
    "rating",
    "winner",
    "llm_judge_winner",
}
FORBIDDEN_FIELD_SUFFIXES = ("_score",)
ALLOWED_SCORE_FIELD_NAMES = {"not_a_score"}
POSITIVE_NET_READS = {
    "material_improvement_candidate",
    "partial_improvement_candidate",
}
NON_CLAIM_FRAGMENTS = (
    "not human review",
    "not ground truth",
    "not judge calibration",
    "not product proof",
    "not agent approval",
    "not answer-quality",
    "not automatic label",
)
PRIVACY_MARKERS = (
    "/Users/",
    "SECRET",
    "raw_message_content",
    "fabricated_passages",
    "FULL ASSISTANT REASONING",
    "client_secret",
    "api_key",
    "password",
)
SEVERITIES = ("blocking_error", "warning", "info")


class ProductDeltaBoundaryLintInputError(ValueError):
    """Deterministic, sanitized input error."""


@dataclass(frozen=True)
class BoundaryFinding:
    severity: str
    code: str
    path: str
    message: str
    json_pointer: str | None = None
    line: int | None = None
    suggested_fix: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "severity": self.severity,
            "code": self.code,
            "path": self.path,
            "message": self.message,
        }
        if self.json_pointer is not None:
            payload["json_pointer"] = self.json_pointer
        if self.line is not None:
            payload["line"] = self.line
        if self.suggested_fix is not None:
            payload["suggested_fix"] = self.suggested_fix
        return payload


def lint_product_delta_paths(paths: Sequence[Path | str]) -> dict[str, Any]:
    """Lint one or more Product Delta Evidence artifacts."""

    if not paths:
        raise ProductDeltaBoundaryLintInputError("at least one path is required")

    findings: list[BoundaryFinding] = []
    checked_paths: list[str] = []
    for raw_path in paths:
        path = Path(raw_path)
        display_path = _display_path(path)
        checked_paths.append(display_path)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise ProductDeltaBoundaryLintInputError(
                f"artifact could not be read:{type(exc).__name__}"
            ) from exc
        _lint_privacy_markers(
            text=text,
            display_path=display_path,
            findings=findings,
        )
        if path.suffix.lower() == ".json":
            try:
                payload = json.loads(text)
            except json.JSONDecodeError as exc:
                raise ProductDeltaBoundaryLintInputError(
                    "artifact JSON is not valid JSON"
                ) from exc
            _lint_json_payload(
                payload=payload,
                display_path=display_path,
                findings=findings,
            )
        elif path.suffix.lower() in {".md", ".markdown"}:
            _lint_markdown(
                text=text,
                display_path=display_path,
                findings=findings,
            )
        else:
            findings.append(
                BoundaryFinding(
                    severity="info",
                    code="unchecked_extension",
                    path=display_path,
                    message=(
                        "Path was scanned for privacy markers but has no JSON or "
                        "Markdown structural lint."
                    ),
                    suggested_fix=(
                        "Pass Product Delta JSON or Markdown artifacts for full lint."
                    ),
                )
            )

    finding_dicts = [finding.to_dict() for finding in findings]
    summary = {
        "blocking_error_count": _count_severity(findings, "blocking_error"),
        "warning_count": _count_severity(findings, "warning"),
        "info_count": _count_severity(findings, "info"),
    }
    return {
        "schema_version": PRODUCT_DELTA_BOUNDARY_LINT_SCHEMA_VERSION,
        "checked_paths": checked_paths,
        "summary": summary,
        "findings": finding_dicts,
        "boundary": {
            "model_calls": 0,
            "archive_mutated": False,
            "runtime_invoked": False,
            "skill_invoked": False,
            "human_validated": False,
            "product_proof": False,
        },
    }


def render_boundary_lint_json(report: Mapping[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_boundary_lint_text(report: Mapping[str, Any]) -> str:
    summary = _as_mapping(report.get("summary"))
    lines = [
        "Product Delta Evidence Boundary Lint",
        "",
        "Summary:",
        f"- blocking_error: {_safe_int(summary.get('blocking_error_count'))}",
        f"- warning: {_safe_int(summary.get('warning_count'))}",
        f"- info: {_safe_int(summary.get('info_count'))}",
        "",
        "Checked paths:",
    ]
    checked_paths = report.get("checked_paths")
    if isinstance(checked_paths, list) and checked_paths:
        lines.extend(f"- {item}" for item in checked_paths)
    else:
        lines.append("- none")
    findings = report.get("findings")
    if isinstance(findings, list) and findings:
        lines.extend(["", "Findings:"])
        for finding in findings:
            if not isinstance(finding, Mapping):
                continue
            location = _text(finding.get("path"))
            pointer = _text(finding.get("json_pointer"))
            line = finding.get("line")
            if pointer:
                location = f"{location}{pointer}"
            elif isinstance(line, int):
                location = f"{location}:{line}"
            lines.append(
                "- "
                f"{_text(finding.get('severity'))} "
                f"{_text(finding.get('code'))} "
                f"{location}: {_text(finding.get('message'))}"
            )
    else:
        lines.extend(["", "Findings: none"])
    return "\n".join(lines) + "\n"


def write_text(path: Path | str, payload: str) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(payload, encoding="utf-8")


def _lint_json_payload(
    *,
    payload: Any,
    display_path: str,
    findings: list[BoundaryFinding],
) -> None:
    if not isinstance(payload, Mapping):
        findings.append(
            BoundaryFinding(
                severity="blocking_error",
                code="json_root_not_object",
                path=display_path,
                message="Product Delta JSON artifacts must be JSON objects.",
            )
        )
        return
    _walk_json(value=payload, path=(), display_path=display_path, findings=findings)
    _lint_schema_contract(
        payload=payload,
        display_path=display_path,
        findings=findings,
    )
    _lint_taxonomy(
        payload=payload,
        display_path=display_path,
        findings=findings,
    )
    _lint_review_cases(
        value=payload,
        path=(),
        display_path=display_path,
        findings=findings,
    )


def _walk_json(
    *,
    value: Any,
    path: tuple[str, ...],
    display_path: str,
    findings: list[BoundaryFinding],
) -> None:
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key)
            child_path = (*path, key)
            normalized = _normalize_field_name(key)
            _lint_field_name(
                field_name=normalized,
                display_name=key,
                path=child_path,
                display_path=display_path,
                findings=findings,
            )
            _lint_boundary_value(
                field_name=normalized,
                value=child,
                path=child_path,
                display_path=display_path,
                findings=findings,
            )
            _walk_json(
                value=child,
                path=child_path,
                display_path=display_path,
                findings=findings,
            )
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _walk_json(
                value=child,
                path=(*path, str(index)),
                display_path=display_path,
                findings=findings,
            )


def _lint_field_name(
    *,
    field_name: str,
    display_name: str,
    path: tuple[str, ...],
    display_path: str,
    findings: list[BoundaryFinding],
) -> None:
    if field_name in ALLOWED_SCORE_FIELD_NAMES:
        return
    if field_name == "safe_for_agent_use":
        findings.append(
            BoundaryFinding(
                severity="blocking_error",
                code="forbidden_safe_for_agent_use_field",
                path=display_path,
                json_pointer=_json_pointer(path),
                message="Product Delta provisional artifacts must not infer safe_for_agent_use.",
                suggested_fix="Remove the field or move any future value into human-owned review.",
            )
        )
        return
    if field_name in FORBIDDEN_FIELD_NAMES or any(
        field_name.endswith(suffix) for suffix in FORBIDDEN_FIELD_SUFFIXES
    ):
        findings.append(
            BoundaryFinding(
                severity="blocking_error",
                code="forbidden_authority_field",
                path=display_path,
                json_pointer=_json_pointer(path),
                message=(
                    f"Field `{display_name}` implies scoring, approval, or an "
                    "automatic verdict."
                ),
                suggested_fix="Use provisional/candidate review fields without scores or approval semantics.",
            )
        )


def _lint_boundary_value(
    *,
    field_name: str,
    value: Any,
    path: tuple[str, ...],
    display_path: str,
    findings: list[BoundaryFinding],
) -> None:
    if _inside_json_schema_properties(path):
        return
    if field_name in FALSE_METADATA_FIELDS and value is not False:
        findings.append(
            BoundaryFinding(
                severity="blocking_error",
                code=f"{field_name}_must_be_false",
                path=display_path,
                json_pointer=_json_pointer(path),
                message=f"`{field_name}` must be false for provisional Product Delta artifacts.",
                suggested_fix=f"Set `{field_name}` to false or remove the artifact from provisional eval output.",
            )
        )
    if field_name in ZERO_METADATA_FIELDS and value != 0:
        findings.append(
            BoundaryFinding(
                severity="blocking_error",
                code=f"{field_name}_must_be_zero",
                path=display_path,
                json_pointer=_json_pointer(path),
                message=f"`{field_name}` must be 0 for checked-in provisional eval artifacts.",
                suggested_fix=f"Set `{field_name}` to 0 or document the artifact outside this linted lane.",
            )
        )
    if field_name in FALSE_IF_PRESENT_FIELDS and value is not False:
        findings.append(
            BoundaryFinding(
                severity="blocking_error",
                code=f"{field_name}_must_be_false",
                path=display_path,
                json_pointer=_json_pointer(path),
                message=f"`{field_name}` must be false when present in Product Delta eval artifacts.",
                suggested_fix=f"Keep `{field_name}` false; do not create automatic labels, scores, or judges.",
            )
        )


def _lint_schema_contract(
    *,
    payload: Mapping[str, Any],
    display_path: str,
    findings: list[BoundaryFinding],
) -> None:
    properties = payload.get("properties")
    if not isinstance(properties, Mapping):
        return
    schema_const = _schema_const(properties.get("schema_version"))
    if schema_const != PROVISIONAL_REVIEW_SCHEMA_VERSION:
        return
    required = payload.get("required")
    if not isinstance(required, list):
        findings.append(
            BoundaryFinding(
                severity="blocking_error",
                code="schema_missing_required_array",
                path=display_path,
                message="PR72 review schema must define required fields.",
            )
        )
        return
    for field in PR72_REQUIRED_FIELDS:
        if field not in required:
            findings.append(
                BoundaryFinding(
                    severity="blocking_error",
                    code="schema_missing_required_boundary_field",
                    path=display_path,
                    json_pointer="/required",
                    message=f"PR72 review schema must require `{field}`.",
                )
            )
    _lint_schema_const_false(
        properties=properties,
        field_names=FALSE_METADATA_FIELDS,
        display_path=display_path,
        findings=findings,
    )
    _lint_schema_const_zero(
        properties=properties,
        field_names=ZERO_METADATA_FIELDS,
        display_path=display_path,
        findings=findings,
    )


def _lint_schema_const_false(
    *,
    properties: Mapping[str, Any],
    field_names: Iterable[str],
    display_path: str,
    findings: list[BoundaryFinding],
) -> None:
    for field_name in field_names:
        spec = properties.get(field_name)
        if not isinstance(spec, Mapping) or spec.get("const") is not False:
            findings.append(
                BoundaryFinding(
                    severity="blocking_error",
                    code="schema_boundary_const_missing",
                    path=display_path,
                    json_pointer=f"/properties/{field_name}",
                    message=f"Schema must constrain `{field_name}` to false.",
                )
            )


def _lint_schema_const_zero(
    *,
    properties: Mapping[str, Any],
    field_names: Iterable[str],
    display_path: str,
    findings: list[BoundaryFinding],
) -> None:
    for field_name in field_names:
        spec = properties.get(field_name)
        if not isinstance(spec, Mapping) or spec.get("const") != 0:
            findings.append(
                BoundaryFinding(
                    severity="blocking_error",
                    code="schema_boundary_const_missing",
                    path=display_path,
                    json_pointer=f"/properties/{field_name}",
                    message=f"Schema must constrain `{field_name}` to 0.",
                )
            )


def _lint_taxonomy(
    *,
    payload: Mapping[str, Any],
    display_path: str,
    findings: list[BoundaryFinding],
) -> None:
    if _text(payload.get("schema_version")) != PROVISIONAL_TAXONOMY_SCHEMA_VERSION:
        return
    if payload.get("not_a_score") is not True:
        findings.append(
            BoundaryFinding(
                severity="blocking_error",
                code="taxonomy_not_a_score_missing",
                path=display_path,
                json_pointer="/not_a_score",
                message="Product Delta failure taxonomy must preserve `not_a_score: true`.",
                suggested_fix="Set top-level `not_a_score` to true.",
            )
        )
    entries = payload.get("entries")
    if not isinstance(entries, list):
        findings.append(
            BoundaryFinding(
                severity="blocking_error",
                code="taxonomy_entries_missing",
                path=display_path,
                json_pointer="/entries",
                message="Product Delta failure taxonomy must contain entries.",
            )
        )
        return
    for index, entry in enumerate(entries):
        if not isinstance(entry, Mapping):
            findings.append(
                BoundaryFinding(
                    severity="blocking_error",
                    code="taxonomy_entry_not_object",
                    path=display_path,
                    json_pointer=f"/entries/{index}",
                    message="Taxonomy entries must be JSON objects.",
                )
            )
            continue
        if entry.get("not_a_score") is not True:
            findings.append(
                BoundaryFinding(
                    severity="blocking_error",
                    code="taxonomy_entry_not_a_score_missing",
                    path=display_path,
                    json_pointer=f"/entries/{index}/not_a_score",
                    message="Every taxonomy entry must preserve `not_a_score: true`.",
                    suggested_fix="Set entry `not_a_score` to true.",
                )
            )
        if entry.get("current_status") != "provisional_until_human_review":
            findings.append(
                BoundaryFinding(
                    severity="blocking_error",
                    code="taxonomy_entry_status_not_provisional",
                    path=display_path,
                    json_pointer=f"/entries/{index}/current_status",
                    message=(
                        "Every taxonomy entry must remain "
                        "`provisional_until_human_review`."
                    ),
                    suggested_fix="Set entry `current_status` to `provisional_until_human_review`.",
                )
            )


def _lint_review_cases(
    *,
    value: Any,
    path: tuple[str, ...],
    display_path: str,
    findings: list[BoundaryFinding],
) -> None:
    if isinstance(value, Mapping):
        if _looks_like_review_case(value):
            _lint_review_case(
                case=value,
                path=path,
                display_path=display_path,
                findings=findings,
            )
        for raw_key, child in value.items():
            _lint_review_cases(
                value=child,
                path=(*path, str(raw_key)),
                display_path=display_path,
                findings=findings,
            )
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _lint_review_cases(
                value=child,
                path=(*path, str(index)),
                display_path=display_path,
                findings=findings,
            )


def _lint_review_case(
    *,
    case: Mapping[str, Any],
    path: tuple[str, ...],
    display_path: str,
    findings: list[BoundaryFinding],
) -> None:
    for field in PR72_REQUIRED_FIELDS:
        if field not in case:
            findings.append(
                BoundaryFinding(
                    severity="blocking_error",
                    code="review_case_missing_required_field",
                    path=display_path,
                    json_pointer=_json_pointer((*path, field)),
                    message=f"PR72-shaped review case is missing `{field}`.",
                )
            )
    if "archive_relpath" not in case and "case_relpath" not in case:
        findings.append(
            BoundaryFinding(
                severity="blocking_error",
                code="review_case_missing_relative_case_path",
                path=display_path,
                json_pointer=_json_pointer(path),
                message="Review case must include `archive_relpath` or `case_relpath`.",
            )
        )
    _lint_case_non_claims(
        case=case,
        path=path,
        display_path=display_path,
        findings=findings,
    )
    _lint_case_sections(
        case=case,
        path=path,
        display_path=display_path,
        findings=findings,
    )


def _lint_case_non_claims(
    *,
    case: Mapping[str, Any],
    path: tuple[str, ...],
    display_path: str,
    findings: list[BoundaryFinding],
) -> None:
    non_claims = case.get("non_claims")
    if not isinstance(non_claims, list):
        return
    joined = " ".join(_text(item).lower() for item in non_claims)
    for fragment in NON_CLAIM_FRAGMENTS:
        if fragment not in joined:
            findings.append(
                BoundaryFinding(
                    severity="blocking_error",
                    code="review_case_missing_non_claim",
                    path=display_path,
                    json_pointer=_json_pointer((*path, "non_claims")),
                    message=f"Review case non-claims must include `{fragment}`.",
                )
            )


def _lint_case_sections(
    *,
    case: Mapping[str, Any],
    path: tuple[str, ...],
    display_path: str,
    findings: list[BoundaryFinding],
) -> None:
    for section_name in (
        "vanilla_likely_next_action",
        "lolla_likely_next_action",
        "material_difference",
        "decision_leverage",
    ):
        section = case.get(section_name)
        if isinstance(section, Mapping) and "uncertainty" not in section:
            findings.append(
                BoundaryFinding(
                    severity="blocking_error",
                    code="subjective_section_missing_uncertainty",
                    path=display_path,
                    json_pointer=_json_pointer((*path, section_name)),
                    message=f"`{section_name}` must include uncertainty.",
                )
            )
    net = case.get("net_decision_read_provisional")
    label = _text(net.get("label")) if isinstance(net, Mapping) else ""
    if label in POSITIVE_NET_READS:
        lost_value = case.get("lost_value")
        if not isinstance(lost_value, Mapping) or "present" not in lost_value:
            findings.append(
                BoundaryFinding(
                    severity="blocking_error",
                    code="positive_candidate_missing_lost_value",
                    path=display_path,
                    json_pointer=_json_pointer((*path, "lost_value")),
                    message="Positive candidate reads must still record lost-value status.",
                    suggested_fix="Populate `lost_value` or downgrade the candidate read.",
                )
            )
        followups = case.get("human_followup_questions")
        if not isinstance(followups, list) or not followups:
            findings.append(
                BoundaryFinding(
                    severity="blocking_error",
                    code="positive_candidate_missing_human_followup",
                    path=display_path,
                    json_pointer=_json_pointer((*path, "human_followup_questions")),
                    message="Positive candidate reads must include human follow-up questions.",
                    suggested_fix="Add human follow-up questions or downgrade the candidate read.",
                )
            )
        notes = case.get("codex_uncertainty_notes")
        if not isinstance(notes, list) or not notes:
            findings.append(
                BoundaryFinding(
                    severity="blocking_error",
                    code="positive_candidate_missing_uncertainty_notes",
                    path=display_path,
                    json_pointer=_json_pointer((*path, "codex_uncertainty_notes")),
                    message="Positive candidate reads must include Codex uncertainty notes.",
                    suggested_fix="Add uncertainty notes or downgrade the candidate read.",
                )
            )


def _lint_markdown(
    *,
    text: str,
    display_path: str,
    findings: list[BoundaryFinding],
) -> None:
    lines = text.splitlines()
    for index, line in enumerate(lines, 1):
        context = _line_context(lines, index - 1)
        lowered_context = context.lower()
        lowered_line = line.lower()
        if _safe_negated_context(lowered_context):
            continue
        if re.search(r"\blolla\s+(proved|proves|validated|validates)\b", lowered_line):
            findings.append(
                BoundaryFinding(
                    severity="warning",
                    code="markdown_possible_product_proof_claim",
                    path=display_path,
                    line=index,
                    message="Markdown may imply Lolla proved or validated product value.",
                    suggested_fix="Use provisional/candidate language or add an explicit non-claim.",
                )
            )
        if re.search(r"\bcodex\s+(proved|proves|validated|validates)\b", lowered_line):
            findings.append(
                BoundaryFinding(
                    severity="warning",
                    code="markdown_possible_codex_validation_claim",
                    path=display_path,
                    line=index,
                    message="Markdown may imply Codex validated a result.",
                    suggested_fix="Say Codex-assisted reads are provisional, not validation.",
                )
            )
        if re.search(r"\blolla\s+improves?\b", lowered_line):
            findings.append(
                BoundaryFinding(
                    severity="warning",
                    code="markdown_possible_improvement_claim",
                    path=display_path,
                    line=index,
                    message="Markdown says Lolla improves without nearby provisional or non-claim language.",
                    suggested_fix="Use candidate/provisional language or state that improvement is unproven.",
                )
            )
    lowered_text = text.lower()
    if _has_candidate_distribution(lowered_text) and not any(
        phrase in lowered_text
        for phrase in (
            "agreement bias",
            "selection bias",
            "corpus bias",
            "safe-summary compression",
        )
    ):
        findings.append(
            BoundaryFinding(
                severity="warning",
                code="positive_distribution_missing_bias_caveat",
                path=display_path,
                message=(
                    "Report-like Markdown contains positive candidate distribution "
                    "without an agreement/selection-bias caveat."
                ),
                suggested_fix="Add a caveat that positive provisional distributions may reflect selection or Codex bias.",
            )
        )
    if _is_product_delta_report(display_path) and not (
        "falsif" in lowered_text or "what would make" in lowered_text
    ):
        findings.append(
            BoundaryFinding(
                severity="warning",
                code="report_missing_falsification_language",
                path=display_path,
                message="Product Delta report lacks falsification language.",
                suggested_fix="Add what would make the candidate reads wrong.",
            )
        )


def _has_candidate_distribution(text: str) -> bool:
    return (
        "| provisional read | count |" in text
        or "distribution of candidate reads" in text
    )


def _is_product_delta_report(display_path: str) -> bool:
    name = Path(display_path).name
    return name == "product-delta-provisional-report-v0.md"


def _lint_privacy_markers(
    *,
    text: str,
    display_path: str,
    findings: list[BoundaryFinding],
) -> None:
    for marker in PRIVACY_MARKERS:
        if marker not in text:
            continue
        line = text[: text.find(marker)].count("\n") + 1
        findings.append(
            BoundaryFinding(
                severity="blocking_error",
                code="privacy_marker_detected",
                path=display_path,
                line=line,
                message=f"Artifact contains privacy/content marker `{marker}`.",
                suggested_fix="Remove raw/private markers from checked-in Product Delta artifacts.",
            )
        )


def _line_context(lines: Sequence[str], index: int) -> str:
    start = max(0, index - 8)
    end = min(len(lines), index + 3)
    return " ".join(lines[start:end])


def _safe_negated_context(text: str) -> bool:
    safe_terms = (
        "not",
        "does not",
        "do not",
        "cannot",
        "can't",
        "without",
        "unproven",
        "not prove",
        "not proof",
        "non-claim",
        "provisional",
        "candidate",
        "hypothesis",
        "whether",
        "if ",
        "later human",
    )
    return any(term in text for term in safe_terms)


def _schema_const(spec: Any) -> Any:
    if isinstance(spec, Mapping):
        return spec.get("const")
    return None


def _looks_like_review_case(value: Mapping[str, Any]) -> bool:
    return (
        _text(value.get("schema_version")) == PROVISIONAL_REVIEW_SCHEMA_VERSION
        and (
            "review_mode" in value
            or "vanilla_likely_next_action" in value
            or "lolla_likely_next_action" in value
        )
    )


def _inside_json_schema_properties(path: Sequence[str]) -> bool:
    return len(path) >= 2 and path[-2] == "properties"


def _normalize_field_name(value: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", value.strip().lower()).strip("_")


def _json_pointer(path: Sequence[str]) -> str:
    if not path:
        return ""
    return "/" + "/".join(part.replace("~", "~0").replace("/", "~1") for part in path)


def _count_severity(findings: Sequence[BoundaryFinding], severity: str) -> int:
    return sum(1 for finding in findings if finding.severity == severity)


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.name


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _safe_int(value: Any) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    return 0


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)
