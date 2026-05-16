#!/usr/bin/env python3
"""Research-only validation/rendering for pre-Step-6 raw reasoning artifacts.

This module is deliberately outside the live pipeline. It validates a small
raw artifact handoff and renders the private pressure block a Step-6-style
consumer would see. It does not select truth, launch workers, build bundles, or
change /lolla runtime behavior.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Iterable, Sequence


RAW_HANDOFF_SCHEMA_VERSION = "pre_step6_raw_artifact_handoff.v1"
ANSWER_CORE_SCHEMA_VERSION = "pre_step6_raw_answer_core.v1"
ANSWER_COMPARISON_SCHEMA_VERSION = "pre_step6_answer_comparison.v1"
ARTIFACT_SCHEMA_VERSION = "reasoning_artifact.v1"
MAX_ARTIFACTS = 5
MAX_SOURCE_EXCERPTS = 4
MAX_RENDER_CHARS = 4000
MAX_ANSWER_CORE_CHARS = 2500

ALLOWED_STATUS = frozenset({"research_only"})
ALLOWED_RUNTIME_POLICY = frozenset({"runtime_dormant"})
ALLOWED_PRIORITY_HINTS = frozenset({"high", "medium", "low", "quiet", "discard"})
ALLOWED_WORKER_ADMISSION_DECISIONS = frozenset(
    {"decline_worker", "no_worker_needed", "not_evaluated", "admit_worker"}
)
ALLOWED_CRITERION_WINNERS = frozenset({"control", "raw", "tie"})
ALLOWED_AGGREGATE_DECISIONS = frozenset({"control_wins", "raw_wins", "tie_stop"})
TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "source_artifacts",
        "source_excerpts",
        "artifacts",
        "worker_admission",
        "notes",
    }
)
SOURCE_EXCERPT_FIELDS = frozenset({"excerpt_id", "text"})
ARTIFACT_FIELDS = frozenset(
    {
        "schema_version",
        "artifact_id",
        "worker_type",
        "why_provided",
        "source_grounding",
        "contribution",
        "hard_boundary",
        "relaxation_condition",
        "discard_condition",
        "relation_to_answer",
        "source_excerpt_ids",
        "duplicate_of",
        "conflicts_with",
        "priority_hint",
        "risk_if_forced",
        "risk_if_ignored",
        "public_render_hint",
    }
)
REQUIRED_ARTIFACT_FIELDS = (
    "schema_version",
    "artifact_id",
    "why_provided",
    "source_grounding",
    "contribution",
    "hard_boundary",
    "relaxation_condition",
    "discard_condition",
    "priority_hint",
    "risk_if_forced",
    "risk_if_ignored",
)
WORKER_ADMISSION_FIELDS = frozenset(
    {"decision", "reason", "unnecessary_if", "admit_only_if"}
)
ANSWER_CORE_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "source_handoff",
        "source_handoff_render_sha256",
        "answer_core",
        "expected_inclusions",
        "expected_exclusions",
        "comparison_to_control",
        "notes",
    }
)
COMPARISON_FIELDS = frozenset(
    {"preserved_from_control", "changed_from_raw_handoff", "kept_private_or_discarded"}
)
ANSWER_COMPARISON_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "control_answer_core",
        "raw_answer_core_ref",
        "criteria",
        "tie_break_rule",
        "aggregate_decision",
        "notes",
    }
)
CRITERION_FIELDS = frozenset(
    {
        "criterion_id",
        "question",
        "winner",
        "control_evidence",
        "raw_evidence",
        "rationale",
    }
)
FORBIDDEN_PUBLIC_TERMS = (
    "artifact",
    "bundle",
    "worker",
    "workpack",
    "lane",
    "v60",
    "chunk",
    "ledger",
    "schema",
    "priority_hint",
    "hard_boundary",
    "discard_condition",
)
ARTIFACT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


class RawArtifactValidationError(ValueError):
    pass


def load_raw_artifact_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RawArtifactValidationError(f"{path}: payload must be an object")
    return payload


def validate_raw_artifact_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_raw_artifact_errors(payload, path=Path(path)))
    if errors:
        raise RawArtifactValidationError("; ".join(errors))


def validate_raw_artifact_file(path: Path) -> None:
    validate_raw_artifact_payload(load_raw_artifact_payload(path), path=Path(path))


def load_answer_core_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RawArtifactValidationError(f"{path}: payload must be an object")
    return payload


def validate_answer_core_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
) -> None:
    errors = list(
        iter_answer_core_errors(payload, path=Path(path), repo_root=repo_root)
    )
    if errors:
        raise RawArtifactValidationError("; ".join(errors))


def validate_answer_core_file(path: Path, *, repo_root: Path | None = None) -> None:
    validate_answer_core_payload(
        load_answer_core_payload(path),
        path=Path(path),
        repo_root=repo_root,
    )


def load_answer_comparison_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RawArtifactValidationError(f"{path}: payload must be an object")
    return payload


def validate_answer_comparison_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
) -> None:
    errors = list(
        iter_answer_comparison_errors(payload, path=Path(path), repo_root=repo_root)
    )
    if errors:
        raise RawArtifactValidationError("; ".join(errors))


def validate_answer_comparison_file(
    path: Path,
    *,
    repo_root: Path | None = None,
) -> None:
    validate_answer_comparison_payload(
        load_answer_comparison_payload(path),
        path=Path(path),
        repo_root=repo_root,
    )


def iter_raw_artifact_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be an object"
        return

    required = (
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "source_artifacts",
        "source_excerpts",
        "artifacts",
        "worker_admission",
    )
    yield from _unknown_fields(payload, TOP_LEVEL_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return

    if _string(payload.get("schema_version")) != RAW_HANDOFF_SCHEMA_VERSION:
        yield f"{path}: schema_version must be {RAW_HANDOFF_SCHEMA_VERSION}"
    if _string(payload.get("status")) not in ALLOWED_STATUS:
        yield f"{path}: status must be research_only"
    if _string(payload.get("runtime_policy")) not in ALLOWED_RUNTIME_POLICY:
        yield f"{path}: runtime_policy must be runtime_dormant"
    if not _string(payload.get("case_id")).strip():
        yield f"{path / 'case_id'}: case_id must be a non-empty string"

    yield from _validate_string_list(
        payload.get("source_artifacts"),
        path=path / "source_artifacts",
        required_non_empty=True,
    )

    excerpt_ids = set()
    source_excerpts = payload.get("source_excerpts")
    if not isinstance(source_excerpts, list):
        yield f"{path / 'source_excerpts'}: source_excerpts must be a list"
        source_excerpts = []
    elif len(source_excerpts) > MAX_SOURCE_EXCERPTS:
        yield (
            f"{path / 'source_excerpts'}: "
            f"source_excerpts must not exceed {MAX_SOURCE_EXCERPTS}"
        )
    for index, excerpt in enumerate(source_excerpts):
        item_path = path / f"source_excerpts[{index}]"
        if not isinstance(excerpt, dict):
            yield f"{item_path}: source excerpt must be an object"
            continue
        yield from _validate_source_excerpt(excerpt, path=item_path)
        excerpt_id = _string(excerpt.get("excerpt_id"))
        if excerpt_id in excerpt_ids:
            yield f"{item_path}: duplicate excerpt_id '{excerpt_id}'"
        if excerpt_id:
            excerpt_ids.add(excerpt_id)

    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, list):
        yield f"{path / 'artifacts'}: artifacts must be a list"
        artifacts = []
    elif len(artifacts) > MAX_ARTIFACTS:
        yield f"{path / 'artifacts'}: artifacts must not exceed {MAX_ARTIFACTS}"
    elif not artifacts:
        yield f"{path / 'artifacts'}: artifacts must not be empty"

    artifact_ids: set[str] = set()
    for index, artifact in enumerate(artifacts):
        item_path = path / f"artifacts[{index}]"
        if not isinstance(artifact, dict):
            yield f"{item_path}: artifact must be an object"
            continue
        artifact_id = _string(artifact.get("artifact_id"))
        if artifact_id in artifact_ids:
            yield f"{item_path}: duplicate artifact_id '{artifact_id}'"
        if artifact_id:
            artifact_ids.add(artifact_id)
        yield from _validate_artifact(
            artifact,
            path=item_path,
            known_source_excerpt_ids=excerpt_ids,
        )

    yield from _validate_worker_admission(
        payload.get("worker_admission"),
        path=path / "worker_admission",
    )


def iter_answer_core_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be an object"
        return

    required = (
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "source_handoff",
        "answer_core",
        "expected_inclusions",
        "expected_exclusions",
        "comparison_to_control",
    )
    yield from _unknown_fields(payload, ANSWER_CORE_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return

    if _string(payload.get("schema_version")) != ANSWER_CORE_SCHEMA_VERSION:
        yield f"{path}: schema_version must be {ANSWER_CORE_SCHEMA_VERSION}"
    if _string(payload.get("status")) not in ALLOWED_STATUS:
        yield f"{path}: status must be research_only"
    if _string(payload.get("runtime_policy")) not in ALLOWED_RUNTIME_POLICY:
        yield f"{path}: runtime_policy must be runtime_dormant"
    if not _string(payload.get("case_id")).strip():
        yield f"{path / 'case_id'}: case_id must be a non-empty string"

    source_handoff = _string(payload.get("source_handoff"))
    if not source_handoff:
        yield f"{path / 'source_handoff'}: source_handoff must be a non-empty string"
    elif repo_root is not None:
        handoff_path = repo_root / source_handoff
        if not handoff_path.exists():
            yield f"{path / 'source_handoff'}: source_handoff does not exist"
        else:
            handoff_payload = load_raw_artifact_payload(handoff_path)
            validate_raw_artifact_payload(handoff_payload, path=handoff_path)
            if _string(handoff_payload.get("case_id")) != _string(payload.get("case_id")):
                yield f"{path / 'source_handoff'}: source handoff case_id mismatch"
            rendered = render_raw_artifact_handoff(handoff_payload)
            expected_sha = _string(payload.get("source_handoff_render_sha256"))
            actual_sha = hashlib.sha256(rendered.encode("utf-8")).hexdigest()
            if expected_sha and expected_sha != actual_sha:
                yield f"{path / 'source_handoff_render_sha256'}: sha256 mismatch"

    answer_core = _string(payload.get("answer_core"))
    if not answer_core.strip():
        yield f"{path / 'answer_core'}: answer_core must be a non-empty string"
    elif len(answer_core) > MAX_ANSWER_CORE_CHARS:
        yield (
            f"{path / 'answer_core'}: "
            f"answer_core must not exceed {MAX_ANSWER_CORE_CHARS} chars"
        )
    try:
        validate_public_answer_hygiene(answer_core)
    except RawArtifactValidationError as exc:
        yield f"{path / 'answer_core'}: {exc}"

    yield from _validate_string_list(
        payload.get("expected_inclusions"),
        path=path / "expected_inclusions",
        required_non_empty=True,
    )
    if isinstance(payload.get("expected_inclusions"), list):
        lower_answer = answer_core.lower()
        for index, expected in enumerate(payload["expected_inclusions"]):
            if isinstance(expected, str) and expected.lower() not in lower_answer:
                yield (
                    f"{path / 'expected_inclusions' / str(index)}: "
                    "expected inclusion missing from answer_core"
                )

    yield from _validate_string_list(
        payload.get("expected_exclusions"),
        path=path / "expected_exclusions",
        required_non_empty=False,
    )
    if isinstance(payload.get("expected_exclusions"), list):
        lower_answer = answer_core.lower()
        for index, forbidden in enumerate(payload["expected_exclusions"]):
            if isinstance(forbidden, str) and forbidden.lower() in lower_answer:
                yield (
                    f"{path / 'expected_exclusions' / str(index)}: "
                    "expected exclusion appears in answer_core"
                )

    yield from _validate_comparison_to_control(
        payload.get("comparison_to_control"),
        path=path / "comparison_to_control",
    )


def iter_answer_comparison_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be an object"
        return

    required = (
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "control_answer_core",
        "raw_answer_core_ref",
        "criteria",
        "tie_break_rule",
        "aggregate_decision",
    )
    yield from _unknown_fields(payload, ANSWER_COMPARISON_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return

    if _string(payload.get("schema_version")) != ANSWER_COMPARISON_SCHEMA_VERSION:
        yield f"{path}: schema_version must be {ANSWER_COMPARISON_SCHEMA_VERSION}"
    if _string(payload.get("status")) not in ALLOWED_STATUS:
        yield f"{path}: status must be research_only"
    if _string(payload.get("runtime_policy")) not in ALLOWED_RUNTIME_POLICY:
        yield f"{path}: runtime_policy must be runtime_dormant"
    if not _string(payload.get("case_id")).strip():
        yield f"{path / 'case_id'}: case_id must be a non-empty string"

    control_answer = _string(payload.get("control_answer_core"))
    if not control_answer.strip():
        yield f"{path / 'control_answer_core'}: control_answer_core must be non-empty"
    elif len(control_answer) > MAX_ANSWER_CORE_CHARS:
        yield (
            f"{path / 'control_answer_core'}: "
            f"control_answer_core must not exceed {MAX_ANSWER_CORE_CHARS} chars"
        )
    try:
        validate_public_answer_hygiene(control_answer)
    except RawArtifactValidationError as exc:
        yield f"{path / 'control_answer_core'}: {exc}"

    raw_answer_core_ref = _string(payload.get("raw_answer_core_ref"))
    if not raw_answer_core_ref:
        yield f"{path / 'raw_answer_core_ref'}: raw_answer_core_ref must be non-empty"
    elif repo_root is not None:
        raw_path = repo_root / raw_answer_core_ref
        if not raw_path.exists():
            yield f"{path / 'raw_answer_core_ref'}: raw_answer_core_ref does not exist"
        else:
            raw_payload = load_answer_core_payload(raw_path)
            validate_answer_core_payload(raw_payload, path=raw_path, repo_root=repo_root)
            if _string(raw_payload.get("case_id")) != _string(payload.get("case_id")):
                yield f"{path / 'raw_answer_core_ref'}: raw answer case_id mismatch"

    if _string(payload.get("tie_break_rule")) != "raw_tie_with_control_stops":
        yield f"{path / 'tie_break_rule'}: tie_break_rule must be raw_tie_with_control_stops"

    criteria = payload.get("criteria")
    if not isinstance(criteria, list):
        yield f"{path / 'criteria'}: criteria must be a list"
        criteria = []
    elif not criteria:
        yield f"{path / 'criteria'}: criteria must not be empty"
    elif len(criteria) > 8:
        yield f"{path / 'criteria'}: criteria must not exceed 8"
    for index, criterion in enumerate(criteria):
        item_path = path / f"criteria[{index}]"
        if not isinstance(criterion, dict):
            yield f"{item_path}: criterion must be an object"
            continue
        yield from _validate_criterion(criterion, path=item_path)

    decision = _string(payload.get("aggregate_decision"))
    if decision not in ALLOWED_AGGREGATE_DECISIONS:
        yield f"{path / 'aggregate_decision'}: unknown aggregate_decision '{decision}'"
    else:
        expected = score_answer_comparison(payload)["aggregate_decision"]
        if decision != expected:
            yield (
                f"{path / 'aggregate_decision'}: aggregate_decision must be "
                f"{expected} from criterion winners"
            )


def score_answer_comparison(payload: dict[str, object]) -> dict[str, object]:
    criteria = payload.get("criteria")
    raw = control = tie = 0
    if isinstance(criteria, list):
        for criterion in criteria:
            if not isinstance(criterion, dict):
                continue
            winner = _string(criterion.get("winner"))
            if winner == "raw":
                raw += 1
            elif winner == "control":
                control += 1
            elif winner == "tie":
                tie += 1
    if raw > control:
        aggregate = "raw_wins"
    elif control > raw:
        aggregate = "control_wins"
    else:
        aggregate = "tie_stop"
    return {
        "raw": raw,
        "control": control,
        "tie": tie,
        "aggregate_decision": aggregate,
    }


def render_raw_artifact_handoff(
    payload: dict[str, object],
    *,
    max_chars: int = MAX_RENDER_CHARS,
) -> str:
    validate_raw_artifact_payload(payload)
    artifacts = payload["artifacts"]
    assert isinstance(artifacts, list)

    lines = [
        "RAW REASONING PRESSURE",
        "",
        "Use these as private pressure, not public sections.",
        "Reject any item that is unsupported, duplicate, or misfit.",
        "Ties go to the simpler answer.",
        "",
        f"Case: {_string(payload.get('case_id'))}",
    ]
    for artifact in artifacts:
        assert isinstance(artifact, dict)
        lines.extend(
            [
                "",
                f"Artifact: {_string(artifact.get('artifact_id'))}",
                f"Grounding: {_string(artifact.get('source_grounding'))}",
                f"Boundary: {_string(artifact.get('hard_boundary'))}",
                f"Relax if: {_string(artifact.get('relaxation_condition'))}",
                f"Discard if: {_string(artifact.get('discard_condition'))}",
                f"Contribution: {_string(artifact.get('contribution'))}",
                f"Force risk: {_string(artifact.get('risk_if_forced'))}",
                f"Ignore risk: {_string(artifact.get('risk_if_ignored'))}",
                f"Priority hint: {_string(artifact.get('priority_hint'))}",
            ]
        )

    rendered = "\n".join(lines)
    if len(rendered) > max_chars:
        raise RawArtifactValidationError(
            f"rendered handoff is {len(rendered)} chars; max is {max_chars}"
        )
    return rendered


def iter_public_machinery_terms(text: str) -> Iterable[str]:
    for term in FORBIDDEN_PUBLIC_TERMS:
        pattern = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(term)}(?![A-Za-z0-9_])", re.I)
        if pattern.search(text):
            yield term


def validate_public_answer_hygiene(text: str) -> None:
    terms = sorted(set(iter_public_machinery_terms(text)))
    if terms:
        joined = ", ".join(terms)
        raise RawArtifactValidationError(
            f"public answer leaks private machinery term(s): {joined}"
        )


def _validate_source_excerpt(
    excerpt: dict[str, object],
    *,
    path: Path,
) -> Iterable[str]:
    yield from _unknown_fields(excerpt, SOURCE_EXCERPT_FIELDS, path)
    yield from _missing_fields(excerpt, ("excerpt_id", "text"), path)
    excerpt_id = _string(excerpt.get("excerpt_id"))
    if not excerpt_id:
        yield f"{path / 'excerpt_id'}: excerpt_id must be a non-empty string"
    elif not ARTIFACT_ID_RE.match(excerpt_id):
        yield f"{path / 'excerpt_id'}: excerpt_id must be a lowercase id"
    if not _string(excerpt.get("text")).strip():
        yield f"{path / 'text'}: text must be a non-empty string"


def _validate_artifact(
    artifact: dict[str, object],
    *,
    path: Path,
    known_source_excerpt_ids: set[str],
) -> Iterable[str]:
    yield from _unknown_fields(artifact, ARTIFACT_FIELDS, path)
    yield from _missing_fields(artifact, REQUIRED_ARTIFACT_FIELDS, path)
    if any(field not in artifact for field in REQUIRED_ARTIFACT_FIELDS):
        return

    if _string(artifact.get("schema_version")) != ARTIFACT_SCHEMA_VERSION:
        yield f"{path}: schema_version must be {ARTIFACT_SCHEMA_VERSION}"
    artifact_id = _string(artifact.get("artifact_id"))
    if not ARTIFACT_ID_RE.match(artifact_id):
        yield f"{path / 'artifact_id'}: artifact_id must be a lowercase id"

    for field in REQUIRED_ARTIFACT_FIELDS:
        if field in {"schema_version", "artifact_id", "priority_hint"}:
            continue
        value = _string(artifact.get(field)).strip()
        if not value:
            yield f"{path / field}: {field} must be a non-empty string"

    priority = _string(artifact.get("priority_hint"))
    if priority not in ALLOWED_PRIORITY_HINTS:
        yield f"{path / 'priority_hint'}: unknown priority_hint '{priority}'"

    for field in ("duplicate_of", "conflicts_with", "source_excerpt_ids"):
        if field not in artifact:
            continue
        yield from _validate_string_list(
            artifact.get(field),
            path=path / field,
            required_non_empty=False,
        )

    source_excerpt_ids = artifact.get("source_excerpt_ids")
    if isinstance(source_excerpt_ids, list):
        for excerpt_id in source_excerpt_ids:
            if isinstance(excerpt_id, str) and excerpt_id not in known_source_excerpt_ids:
                yield (
                    f"{path / 'source_excerpt_ids'}: "
                    f"unknown source_excerpt_id '{excerpt_id}'"
                )


def _validate_worker_admission(
    worker_admission: object,
    *,
    path: Path,
) -> Iterable[str]:
    if not isinstance(worker_admission, dict):
        yield f"{path}: worker_admission must be an object"
        return
    yield from _unknown_fields(worker_admission, WORKER_ADMISSION_FIELDS, path)
    yield from _missing_fields(worker_admission, ("decision", "reason"), path)
    decision = _string(worker_admission.get("decision"))
    if decision not in ALLOWED_WORKER_ADMISSION_DECISIONS:
        yield f"{path / 'decision'}: unknown worker admission decision '{decision}'"
    if not _string(worker_admission.get("reason")).strip():
        yield f"{path / 'reason'}: reason must be a non-empty string"
    for field in ("unnecessary_if", "admit_only_if"):
        if field in worker_admission:
            yield from _validate_string_list(
                worker_admission.get(field),
                path=path / field,
                required_non_empty=False,
            )


def _validate_comparison_to_control(
    comparison: object,
    *,
    path: Path,
) -> Iterable[str]:
    if not isinstance(comparison, dict):
        yield f"{path}: comparison_to_control must be an object"
        return
    yield from _unknown_fields(comparison, COMPARISON_FIELDS, path)
    yield from _missing_fields(
        comparison,
        ("preserved_from_control", "changed_from_raw_handoff", "kept_private_or_discarded"),
        path,
    )
    for field in COMPARISON_FIELDS:
        if field in comparison:
            yield from _validate_string_list(
                comparison.get(field),
                path=path / field,
                required_non_empty=True,
            )


def _validate_criterion(
    criterion: dict[str, object],
    *,
    path: Path,
) -> Iterable[str]:
    required = (
        "criterion_id",
        "question",
        "winner",
        "control_evidence",
        "raw_evidence",
        "rationale",
    )
    yield from _unknown_fields(criterion, CRITERION_FIELDS, path)
    yield from _missing_fields(criterion, required, path)
    if any(field not in criterion for field in required):
        return
    criterion_id = _string(criterion.get("criterion_id"))
    if not ARTIFACT_ID_RE.match(criterion_id):
        yield f"{path / 'criterion_id'}: criterion_id must be a lowercase id"
    winner = _string(criterion.get("winner"))
    if winner not in ALLOWED_CRITERION_WINNERS:
        yield f"{path / 'winner'}: unknown winner '{winner}'"
    for field in ("question", "control_evidence", "raw_evidence", "rationale"):
        if not _string(criterion.get(field)).strip():
            yield f"{path / field}: {field} must be a non-empty string"


def _missing_fields(
    payload: dict[str, object],
    required: Sequence[str],
    path: Path,
) -> Iterable[str]:
    for field in required:
        if field not in payload:
            yield f"{path}: missing required field '{field}'"


def _unknown_fields(
    payload: dict[str, object],
    allowed: frozenset[str],
    path: Path,
) -> Iterable[str]:
    for field in sorted(set(payload) - allowed):
        yield f"{path}: unknown field '{field}'"


def _validate_string_list(
    value: object,
    *,
    path: Path,
    required_non_empty: bool,
) -> Iterable[str]:
    if not isinstance(value, list):
        yield f"{path}: must be a list"
        return
    if required_non_empty and not value:
        yield f"{path}: must not be empty"
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            yield f"{path / str(index)}: item must be a non-empty string"


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate or render research-only raw artifact fixtures."
    )
    parser.add_argument("path", type=Path)
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--answer-core", action="store_true")
    parser.add_argument("--comparison", action="store_true")
    parser.add_argument("--repo-root", type=Path)
    args = parser.parse_args(argv)

    if args.comparison:
        payload = load_answer_comparison_payload(args.path)
        validate_answer_comparison_payload(payload, path=args.path, repo_root=args.repo_root)
        score = score_answer_comparison(payload)
        print(
            f"valid comparison: {args.path} "
            f"raw={score['raw']} control={score['control']} tie={score['tie']} "
            f"decision={score['aggregate_decision']}"
        )
        return 0

    if args.answer_core:
        validate_answer_core_file(args.path, repo_root=args.repo_root)
        print(f"valid answer core: {args.path}")
        return 0

    payload = load_raw_artifact_payload(args.path)
    validate_raw_artifact_payload(payload, path=args.path)
    if args.render:
        print(render_raw_artifact_handoff(payload))
    else:
        print(f"valid: {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
