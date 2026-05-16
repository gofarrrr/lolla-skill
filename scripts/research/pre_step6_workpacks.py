#!/usr/bin/env python3
"""Research-only validation/rendering for pre-Step-6 worker workpacks.

This module is deliberately outside the live pipeline. It validates the
admission-first worker shape and renders the prompt a bounded native subagent
would receive. It does not launch workers, select truth, build bundles, or
change /lolla runtime behavior.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable, Sequence


ADMISSION_SCHEMA_VERSION = "pre_step6_worker_admission.v1"
WORKPACK_SCHEMA_VERSION = "reasoning_workpack.v1"
ARTIFACT_SCHEMA_VERSION = "reasoning_artifact.v1"
PRESSURE_CARD_SCHEMA_VERSION = "pre_step6_pressure_card.v1"
MAX_LOCAL_ARTIFACTS = 5
MAX_SOURCE_EXCERPTS = 4
MAX_PROMPT_CHARS = 7000
MAX_WORKER_OUTPUT_CHARS = 1500
MAX_WORKER_OUTPUT_LIST_ITEMS = 3
MAX_WORKER_OUTPUT_LIST_ITEM_CHARS = 180
MAX_PRESSURE_CARD_CHARS = 900
ALLOWED_STATUS = frozenset({"research_only"})
ALLOWED_RUNTIME_POLICY = frozenset({"runtime_dormant"})
ALLOWED_WORKER_TYPES = frozenset({"boundary/evidence-gate"})
ALLOWED_ADMISSION_DECISIONS = frozenset({"admit_worker", "decline_worker"})
ADMISSION_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "worker_type",
        "candidate_worker_question",
        "decision",
        "reason",
        "expected_artifact_contribution",
        "unnecessary_if",
        "kill_condition",
        "source_excerpts",
        "notes",
    }
)
WORKPACK_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "workpack_id",
        "case_id",
        "worker_type",
        "admission_ref",
        "admission_gate",
        "shared_situation_brief",
        "worker_question",
        "local_artifacts",
        "source_excerpts",
        "forbidden_moves",
        "output_contract",
        "notes",
    }
)
ADMISSION_GATE_FIELDS = frozenset(
    {
        "decision",
        "reason",
        "unnecessary_if",
        "kill_condition",
        "expected_artifact_contribution",
    }
)
SHARED_BRIEF_FIELDS = frozenset(
    {
        "user_question",
        "decision_situation",
        "live_constraints",
        "resolution_target",
        "available_artifacts",
        "why_launched",
        "useful_output",
        "noise",
    }
)
LOCAL_ARTIFACT_FIELDS = frozenset({"artifact_id", "text"})
SOURCE_EXCERPT_FIELDS = frozenset({"excerpt_id", "text"})
OUTPUT_CONTRACT_FIELDS = frozenset(
    {"schema_version", "max_chars", "required_fields"}
)
WORKER_OUTPUT_FIELDS = frozenset(
    {"schema_version", *(
        "why_provided",
        "source_grounding",
        "contribution",
        "hard_boundary",
        "relaxation_condition",
        "discard_condition",
        "relation_to_bundle",
        "priority_hint",
        "risk_if_forced",
        "risk_if_ignored",
    )}
)
PRESSURE_CARD_FIELDS = frozenset(
    {
        "schema_version",
        "pressure",
        "boundary",
        "relax_if",
        "discard_if",
        "risk_if_ignored",
    }
)
REQUIRED_REASONING_ARTIFACT_FIELDS = (
    "why_provided",
    "source_grounding",
    "contribution",
    "hard_boundary",
    "relaxation_condition",
    "discard_condition",
    "relation_to_bundle",
    "priority_hint",
    "risk_if_forced",
    "risk_if_ignored",
)
LIST_OK_WORKER_OUTPUT_FIELDS = frozenset({"source_grounding", "contribution"})
ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


class WorkpackValidationError(ValueError):
    pass


def load_json_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise WorkpackValidationError(f"{path}: payload must be an object")
    return payload


def validate_admission_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_admission_errors(payload, path=Path(path)))
    if errors:
        raise WorkpackValidationError("; ".join(errors))


def validate_workpack_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
) -> None:
    errors = list(
        iter_workpack_errors(payload, path=Path(path), repo_root=repo_root)
    )
    if errors:
        raise WorkpackValidationError("; ".join(errors))


def validate_worker_output_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_worker_output_errors(payload, path=Path(path)))
    if errors:
        raise WorkpackValidationError("; ".join(errors))


def validate_pressure_card_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_pressure_card_errors(payload, path=Path(path)))
    if errors:
        raise WorkpackValidationError("; ".join(errors))


def validate_admission_file(path: Path) -> None:
    validate_admission_payload(load_json_payload(path), path=Path(path))


def validate_workpack_file(path: Path, *, repo_root: Path | None = None) -> None:
    validate_workpack_payload(
        load_json_payload(path),
        path=Path(path),
        repo_root=repo_root,
    )


def validate_worker_output_file(path: Path) -> None:
    validate_worker_output_payload(load_json_payload(path), path=Path(path))


def validate_pressure_card_file(path: Path) -> None:
    validate_pressure_card_payload(load_json_payload(path), path=Path(path))


def iter_admission_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    required = (
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "worker_type",
        "candidate_worker_question",
        "decision",
        "reason",
        "expected_artifact_contribution",
        "unnecessary_if",
        "kill_condition",
        "source_excerpts",
    )
    yield from _unknown_fields(payload, ADMISSION_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return

    if _string(payload.get("schema_version")) != ADMISSION_SCHEMA_VERSION:
        yield f"{path}: schema_version must be {ADMISSION_SCHEMA_VERSION}"
    yield from _validate_common_policy(payload, path=path)
    yield from _validate_worker_type(payload.get("worker_type"), path=path / "worker_type")
    if not _string(payload.get("candidate_worker_question")).strip():
        yield f"{path / 'candidate_worker_question'}: must be non-empty"
    decision = _string(payload.get("decision"))
    if decision not in ALLOWED_ADMISSION_DECISIONS:
        yield f"{path / 'decision'}: unknown decision '{decision}'"
    if not _string(payload.get("reason")).strip():
        yield f"{path / 'reason'}: must be non-empty"
    if decision == "admit_worker":
        if _string(payload.get("expected_artifact_contribution")).strip() == "none":
            yield f"{path / 'expected_artifact_contribution'}: admitted worker needs expected contribution"
    if decision == "decline_worker":
        if _string(payload.get("expected_artifact_contribution")).strip() != "none":
            yield f"{path / 'expected_artifact_contribution'}: declined worker must use none"
    for field in ("unnecessary_if", "kill_condition"):
        if not _string(payload.get(field)).strip():
            yield f"{path / field}: must be non-empty"
    yield from _validate_source_excerpts(
        payload.get("source_excerpts"),
        path=path / "source_excerpts",
    )


def iter_workpack_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
) -> Iterable[str]:
    required = (
        "schema_version",
        "status",
        "runtime_policy",
        "workpack_id",
        "case_id",
        "worker_type",
        "admission_ref",
        "admission_gate",
        "shared_situation_brief",
        "worker_question",
        "local_artifacts",
        "source_excerpts",
        "forbidden_moves",
        "output_contract",
    )
    yield from _unknown_fields(payload, WORKPACK_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return

    if _string(payload.get("schema_version")) != WORKPACK_SCHEMA_VERSION:
        yield f"{path}: schema_version must be {WORKPACK_SCHEMA_VERSION}"
    yield from _validate_common_policy(payload, path=path)
    workpack_id = _string(payload.get("workpack_id"))
    if not ID_RE.match(workpack_id):
        yield f"{path / 'workpack_id'}: must be a lowercase id"
    yield from _validate_worker_type(payload.get("worker_type"), path=path / "worker_type")

    admission_ref = _string(payload.get("admission_ref"))
    if not admission_ref:
        yield f"{path / 'admission_ref'}: must be non-empty"
    elif repo_root is not None:
        admission_path = repo_root / admission_ref
        if not admission_path.exists():
            yield f"{path / 'admission_ref'}: admission_ref does not exist"
        else:
            admission_payload = load_json_payload(admission_path)
            validate_admission_payload(admission_payload, path=admission_path)
            if _string(admission_payload.get("case_id")) != _string(payload.get("case_id")):
                yield f"{path / 'admission_ref'}: admission case_id mismatch"
            if _string(admission_payload.get("decision")) != "admit_worker":
                yield f"{path / 'admission_ref'}: workpacks require admitted admission_ref"

    yield from _validate_admission_gate(
        payload.get("admission_gate"),
        path=path / "admission_gate",
    )
    yield from _validate_shared_brief(
        payload.get("shared_situation_brief"),
        path=path / "shared_situation_brief",
    )
    if not _string(payload.get("worker_question")).strip():
        yield f"{path / 'worker_question'}: must be non-empty"
    yield from _validate_local_artifacts(
        payload.get("local_artifacts"),
        path=path / "local_artifacts",
    )
    yield from _validate_source_excerpts(
        payload.get("source_excerpts"),
        path=path / "source_excerpts",
    )
    yield from _validate_string_list(
        payload.get("forbidden_moves"),
        path=path / "forbidden_moves",
        required_non_empty=True,
    )
    yield from _validate_output_contract(
        payload.get("output_contract"),
        path=path / "output_contract",
    )


def iter_worker_output_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    required = ("schema_version", *REQUIRED_REASONING_ARTIFACT_FIELDS)
    yield from _unknown_fields(payload, WORKER_OUTPUT_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return

    if _string(payload.get("schema_version")) != ARTIFACT_SCHEMA_VERSION:
        yield f"{path}: schema_version must be {ARTIFACT_SCHEMA_VERSION}"
    serialized_len = len(json.dumps(payload, ensure_ascii=False))
    if serialized_len > MAX_WORKER_OUTPUT_CHARS:
        yield (
            f"{path}: worker output is {serialized_len} chars; "
            f"max is {MAX_WORKER_OUTPUT_CHARS}"
        )
    for field in REQUIRED_REASONING_ARTIFACT_FIELDS:
        value = payload.get(field)
        if field in LIST_OK_WORKER_OUTPUT_FIELDS:
            if _non_empty_string_or_string_list(value):
                continue
            yield f"{path / field}: must be a non-empty string or non-empty string list"
            continue
        if not isinstance(value, str) or not value.strip():
            yield f"{path / field}: must be a non-empty string"


def iter_pressure_card_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    required = (
        "schema_version",
        "pressure",
        "boundary",
        "relax_if",
        "discard_if",
        "risk_if_ignored",
    )
    yield from _unknown_fields(payload, PRESSURE_CARD_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return

    if _string(payload.get("schema_version")) != PRESSURE_CARD_SCHEMA_VERSION:
        yield f"{path}: schema_version must be {PRESSURE_CARD_SCHEMA_VERSION}"
    serialized_len = len(json.dumps(payload, ensure_ascii=False))
    if serialized_len > MAX_PRESSURE_CARD_CHARS:
        yield (
            f"{path}: pressure card is {serialized_len} chars; "
            f"max is {MAX_PRESSURE_CARD_CHARS}"
        )
    for field in required:
        if field == "schema_version":
            continue
        if not _string(payload.get(field)).strip():
            yield f"{path / field}: must be a non-empty string"


def render_worker_prompt(
    payload: dict[str, object],
    *,
    max_chars: int = MAX_PROMPT_CHARS,
) -> str:
    validate_workpack_payload(payload)
    brief = payload["shared_situation_brief"]
    admission = payload["admission_gate"]
    local_artifacts = payload["local_artifacts"]
    source_excerpts = payload["source_excerpts"]
    forbidden_moves = payload["forbidden_moves"]
    output_contract = payload["output_contract"]
    assert isinstance(brief, dict)
    assert isinstance(admission, dict)
    assert isinstance(local_artifacts, list)
    assert isinstance(source_excerpts, list)
    assert isinstance(forbidden_moves, list)
    assert isinstance(output_contract, dict)

    lines = [
        "You are a research-only bounded pre-Step-6 worker.",
        "Do not edit files.",
        "Do not write final answer prose. Step 6 is the final reasoner.",
        "Return exactly one JSON object and nothing else.",
        "Do not use Markdown fences or prose outside the JSON object.",
        "",
        "SHARED SITUATION BRIEF",
        f"User question: {_string(brief.get('user_question'))}",
        f"Decision situation: {_string(brief.get('decision_situation'))}",
        f"Live constraints: {_string(brief.get('live_constraints'))}",
        f"Resolution target: {_string(brief.get('resolution_target'))}",
        f"Available artifacts: {_string(brief.get('available_artifacts'))}",
        f"Why launched: {_string(brief.get('why_launched'))}",
        f"Useful output: {_string(brief.get('useful_output'))}",
        f"Noise: {_string(brief.get('noise'))}",
        "",
        "ADMISSION RECORD",
        f"Decision: {_string(admission.get('decision'))}",
        f"Reason: {_string(admission.get('reason'))}",
        f"Unnecessary if: {_string(admission.get('unnecessary_if'))}",
        f"Kill condition: {_string(admission.get('kill_condition'))}",
        "",
        f"WORKER QUESTION: {_string(payload.get('worker_question'))}",
        "",
        "LOCAL ARTIFACTS",
    ]
    for artifact in local_artifacts:
        assert isinstance(artifact, dict)
        lines.append(f"- {_string(artifact.get('artifact_id'))}: {_string(artifact.get('text'))}")
    lines.extend(["", "SOURCE EXCERPTS"])
    for excerpt in source_excerpts:
        assert isinstance(excerpt, dict)
        lines.append(f"- {_string(excerpt.get('excerpt_id'))}: {_string(excerpt.get('text'))}")
    lines.extend(["", "FORBIDDEN MOVES"])
    for move in forbidden_moves:
        lines.append(f"- {_string(move)}")
    lines.extend(
        [
            "",
        "OUTPUT CONTRACT",
        f"schema_version must be: {_string(output_contract.get('schema_version'))}",
        f"max serialized JSON chars: {output_contract.get('max_chars')}",
        "JSON keys must be exactly:",
        "- schema_version",
        ]
    )
    required_fields = output_contract.get("required_fields")
    assert isinstance(required_fields, list)
    for field in required_fields:
        lines.append(f"- {_string(field)}")
    lines.extend(
        [
            "Compact JSON skeleton:",
            "{",
            '  "schema_version": "reasoning_artifact.v1",',
            '  "why_provided": "<=120 chars",',
            '  "source_grounding": ["<=180 chars each, max 3"],',
            '  "contribution": ["<=180 chars each, max 3"],',
            '  "hard_boundary": "<=240 chars",',
            '  "relaxation_condition": "<=160 chars",',
            '  "discard_condition": "<=160 chars",',
            '  "relation_to_bundle": "<=140 chars",',
            '  "priority_hint": "high|medium|low|quiet|discard",',
            '  "risk_if_forced": "<=140 chars",',
            '  "risk_if_ignored": "<=140 chars"',
            "}",
            "Value rules:",
            "- use compact strings for most fields",
            "- source_grounding and contribution may be short string arrays",
            f"- arrays must have at most {MAX_WORKER_OUTPUT_LIST_ITEMS} items",
            f"- array items must be at most {MAX_WORKER_OUTPUT_LIST_ITEM_CHARS} chars",
            "- no nested objects",
        ]
    )

    rendered = "\n".join(lines)
    if len(rendered) > max_chars:
        raise WorkpackValidationError(
            f"rendered prompt is {len(rendered)} chars; max is {max_chars}"
        )
    return rendered


def _validate_common_policy(
    payload: dict[str, object],
    *,
    path: Path,
) -> Iterable[str]:
    if _string(payload.get("status")) not in ALLOWED_STATUS:
        yield f"{path / 'status'}: status must be research_only"
    if _string(payload.get("runtime_policy")) not in ALLOWED_RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: runtime_policy must be runtime_dormant"
    if not _string(payload.get("case_id")).strip():
        yield f"{path / 'case_id'}: case_id must be non-empty"


def _validate_worker_type(value: object, *, path: Path) -> Iterable[str]:
    worker_type = _string(value)
    if worker_type not in ALLOWED_WORKER_TYPES:
        yield f"{path}: unknown worker_type '{worker_type}'"


def _validate_admission_gate(gate: object, *, path: Path) -> Iterable[str]:
    if not isinstance(gate, dict):
        yield f"{path}: admission_gate must be an object"
        return
    required = (
        "decision",
        "reason",
        "unnecessary_if",
        "kill_condition",
        "expected_artifact_contribution",
    )
    yield from _unknown_fields(gate, ADMISSION_GATE_FIELDS, path)
    yield from _missing_fields(gate, required, path)
    if any(field not in gate for field in required):
        return
    if _string(gate.get("decision")) != "admit_worker":
        yield f"{path / 'decision'}: workpack admission_gate must be admit_worker"
    for field in ("reason", "unnecessary_if", "kill_condition", "expected_artifact_contribution"):
        if not _string(gate.get(field)).strip():
            yield f"{path / field}: must be non-empty"


def _validate_shared_brief(brief: object, *, path: Path) -> Iterable[str]:
    if not isinstance(brief, dict):
        yield f"{path}: shared_situation_brief must be an object"
        return
    yield from _unknown_fields(brief, SHARED_BRIEF_FIELDS, path)
    yield from _missing_fields(brief, tuple(SHARED_BRIEF_FIELDS), path)
    for field in SHARED_BRIEF_FIELDS:
        if field in brief and not _string(brief.get(field)).strip():
            yield f"{path / field}: must be non-empty"


def _validate_local_artifacts(value: object, *, path: Path) -> Iterable[str]:
    if not isinstance(value, list):
        yield f"{path}: local_artifacts must be a list"
        return
    if not value:
        yield f"{path}: local_artifacts must not be empty"
    if len(value) > MAX_LOCAL_ARTIFACTS:
        yield f"{path}: local_artifacts must not exceed {MAX_LOCAL_ARTIFACTS}"
    seen: set[str] = set()
    for index, artifact in enumerate(value):
        item_path = path / f"local_artifacts[{index}]"
        if not isinstance(artifact, dict):
            yield f"{item_path}: local artifact must be an object"
            continue
        yield from _unknown_fields(artifact, LOCAL_ARTIFACT_FIELDS, item_path)
        yield from _missing_fields(artifact, ("artifact_id", "text"), item_path)
        artifact_id = _string(artifact.get("artifact_id"))
        if not ID_RE.match(artifact_id):
            yield f"{item_path / 'artifact_id'}: must be a lowercase id"
        if artifact_id in seen:
            yield f"{item_path / 'artifact_id'}: duplicate id '{artifact_id}'"
        seen.add(artifact_id)
        if not _string(artifact.get("text")).strip():
            yield f"{item_path / 'text'}: must be non-empty"


def _validate_source_excerpts(value: object, *, path: Path) -> Iterable[str]:
    if not isinstance(value, list):
        yield f"{path}: source_excerpts must be a list"
        return
    if not value:
        yield f"{path}: source_excerpts must not be empty"
    if len(value) > MAX_SOURCE_EXCERPTS:
        yield f"{path}: source_excerpts must not exceed {MAX_SOURCE_EXCERPTS}"
    seen: set[str] = set()
    for index, excerpt in enumerate(value):
        item_path = path / f"source_excerpts[{index}]"
        if not isinstance(excerpt, dict):
            yield f"{item_path}: source excerpt must be an object"
            continue
        yield from _unknown_fields(excerpt, SOURCE_EXCERPT_FIELDS, item_path)
        yield from _missing_fields(excerpt, ("excerpt_id", "text"), item_path)
        excerpt_id = _string(excerpt.get("excerpt_id"))
        if not ID_RE.match(excerpt_id):
            yield f"{item_path / 'excerpt_id'}: must be a lowercase id"
        if excerpt_id in seen:
            yield f"{item_path / 'excerpt_id'}: duplicate id '{excerpt_id}'"
        seen.add(excerpt_id)
        if not _string(excerpt.get("text")).strip():
            yield f"{item_path / 'text'}: must be non-empty"


def _validate_output_contract(contract: object, *, path: Path) -> Iterable[str]:
    if not isinstance(contract, dict):
        yield f"{path}: output_contract must be an object"
        return
    yield from _unknown_fields(contract, OUTPUT_CONTRACT_FIELDS, path)
    yield from _missing_fields(
        contract,
        ("schema_version", "max_chars", "required_fields"),
        path,
    )
    if any(field not in contract for field in ("schema_version", "max_chars", "required_fields")):
        return
    if _string(contract.get("schema_version")) != ARTIFACT_SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {ARTIFACT_SCHEMA_VERSION}"
    max_chars = contract.get("max_chars")
    if not isinstance(max_chars, int):
        yield f"{path / 'max_chars'}: must be an integer"
    elif max_chars > MAX_WORKER_OUTPUT_CHARS:
        yield f"{path / 'max_chars'}: must not exceed {MAX_WORKER_OUTPUT_CHARS}"
    required_fields = contract.get("required_fields")
    yield from _validate_string_list(
        required_fields,
        path=path / "required_fields",
        required_non_empty=True,
    )
    if isinstance(required_fields, list):
        missing = [
            field for field in REQUIRED_REASONING_ARTIFACT_FIELDS if field not in required_fields
        ]
        if missing:
            joined = ", ".join(missing)
            yield f"{path / 'required_fields'}: missing required artifact fields: {joined}"


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


def _non_empty_string_or_string_list(value: object) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list) and value:
        if len(value) > MAX_WORKER_OUTPUT_LIST_ITEMS:
            return False
        return all(
            isinstance(item, str)
            and item.strip()
            and len(item) <= MAX_WORKER_OUTPUT_LIST_ITEM_CHARS
            for item in value
        )
    return False


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate or render research-only pre-Step-6 workpacks."
    )
    parser.add_argument("path", type=Path)
    parser.add_argument("--admission", action="store_true")
    parser.add_argument("--worker-output", action="store_true")
    parser.add_argument("--pressure-card", action="store_true")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--repo-root", type=Path)
    args = parser.parse_args(argv)

    payload = load_json_payload(args.path)
    if args.admission:
        validate_admission_payload(payload, path=args.path)
        print(f"valid admission: {args.path}")
        return 0
    if args.worker_output:
        validate_worker_output_payload(payload, path=args.path)
        print(f"valid worker output: {args.path}")
        return 0
    if args.pressure_card:
        validate_pressure_card_payload(payload, path=args.path)
        print(f"valid pressure card: {args.path}")
        return 0

    validate_workpack_payload(payload, path=args.path, repo_root=args.repo_root)
    if args.render:
        print(render_worker_prompt(payload))
    else:
        print(f"valid workpack: {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
