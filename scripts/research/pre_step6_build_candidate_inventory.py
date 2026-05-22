#!/usr/bin/env python3
"""Build a research-only pre-Step-6 candidate inventory.

The inventory preserves engineered artifacts and expansion refs for later
reasoning-affordance work. It does not decide truth, usefulness, or final
advice.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable, Sequence


CANDIDATE_INVENTORY_SCHEMA_VERSION = "candidate_inventory.v1"
ALLOWED_STATUS = frozenset({"research_only"})
ALLOWED_RUNTIME_POLICY = frozenset({"runtime_dormant"})
RESULT_ORIGINS = (
    "delta_card",
    "companion_card",
    "frame_pressure_card",
    "structural_coverage_card",
    "audit_summary",
    "run_health",
)
TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "source_refs",
        "candidates",
    }
)
CANDIDATE_FIELDS = frozenset(
    {
        "candidate_id",
        "origin",
        "artifact_ref",
        "selection_basis",
        "summary",
        "source_refs",
        "expansion_ref",
    }
)
REQUIRED_CANDIDATE_FIELDS = tuple(CANDIDATE_FIELDS)
ID_RE = re.compile(r"[^a-z0-9_]+")


class CandidateInventoryValidationError(ValueError):
    pass


def build_candidate_inventory(
    *,
    case_id: str,
    result_file: Path | None = None,
    raw_handoff_files: Sequence[Path] = (),
    hybrid_handoff_files: Sequence[Path] = (),
) -> dict[str, object]:
    candidates: list[dict[str, object]] = []
    source_refs: list[str] = []

    if result_file is not None:
        result_path = Path(result_file)
        result = _load_json(result_path)
        source_refs.append(str(result_path))
        for origin in RESULT_ORIGINS:
            if origin not in result:
                continue
            artifact_ref = f"{result_path}:{origin}"
            candidates.append(
                {
                    "candidate_id": _candidate_id(case_id, origin),
                    "origin": origin,
                    "artifact_ref": artifact_ref,
                    "selection_basis": f"Existing result artifact `{origin}` surfaced by the current pipeline.",
                    "summary": _summarize(result[origin]),
                    "source_refs": [artifact_ref],
                    "expansion_ref": artifact_ref,
                }
            )

    for raw_path in raw_handoff_files:
        raw_path = Path(raw_path)
        raw = _load_json(raw_path)
        source_refs.append(str(raw_path))
        if not isinstance(raw, dict):
            continue
        artifacts = raw.get("artifacts", [])
        if not isinstance(artifacts, list):
            continue
        for index, artifact in enumerate(artifacts):
            if not isinstance(artifact, dict):
                continue
            artifact_id = _string(artifact.get("artifact_id"))
            if not artifact_id:
                continue
            artifact_ref = f"{raw_path}:artifacts[{index}]"
            source_excerpt_ids = artifact.get("source_excerpt_ids", [])
            refs = [artifact_ref]
            if isinstance(source_excerpt_ids, list):
                refs.extend(
                    f"{raw_path}:source_excerpts[{excerpt_id}]"
                    for excerpt_id in source_excerpt_ids
                    if isinstance(excerpt_id, str) and excerpt_id.strip()
                )
            candidates.append(
                {
                    "candidate_id": artifact_id,
                    "origin": "raw_artifact_handoff",
                    "artifact_ref": artifact_ref,
                    "selection_basis": _first_text(
                        artifact.get("why_provided"),
                        artifact.get("priority_hint"),
                        default="Raw artifact handoff preserved this candidate.",
                    ),
                    "summary": _first_text(
                        artifact.get("contribution"),
                        artifact.get("source_grounding"),
                        default="Raw reasoning artifact.",
                    ),
                    "source_refs": refs,
                    "expansion_ref": artifact_ref,
                }
            )

    for hybrid_path in hybrid_handoff_files:
        hybrid_path = Path(hybrid_path)
        hybrid = _load_json(hybrid_path)
        source_refs.append(str(hybrid_path))
        if not isinstance(hybrid, dict):
            continue
        inspect_more = hybrid.get("inspect_more", [])
        if isinstance(inspect_more, list):
            for index, item in enumerate(inspect_more):
                if not isinstance(item, dict):
                    continue
                artifact_id = _string(item.get("artifact_id"))
                if not artifact_id:
                    continue
                artifact_ref = f"{hybrid_path}:inspect_more[{index}]"
                candidates.append(
                    {
                        "candidate_id": _candidate_id(artifact_id, "hybrid_inspect"),
                        "origin": "hybrid_inspect_more",
                        "artifact_ref": artifact_ref,
                        "selection_basis": _first_text(
                            item.get("reason"),
                            item.get("use_only_to_recover"),
                            default="Hybrid handoff authorized raw inspection.",
                        ),
                        "summary": _first_text(
                            item.get("raw_excerpt"),
                            item.get("use_only_to_recover"),
                            default="Hybrid inspect-more receipt.",
                        ),
                        "source_refs": [
                            artifact_ref,
                            _string(item.get("source_raw_handoff")),
                        ],
                        "expansion_ref": artifact_ref,
                    }
                )
        quiet_receipts = hybrid.get("quiet_receipts", [])
        if isinstance(quiet_receipts, list):
            for index, item in enumerate(quiet_receipts):
                if not isinstance(item, dict):
                    continue
                artifact_id = _string(item.get("artifact_id"))
                if not artifact_id:
                    continue
                artifact_ref = f"{hybrid_path}:quiet_receipts[{index}]"
                candidates.append(
                    {
                        "candidate_id": _candidate_id(artifact_id, "hybrid_quiet"),
                        "origin": "hybrid_quiet_receipt",
                        "artifact_ref": artifact_ref,
                        "selection_basis": _first_text(
                            item.get("why_quiet"),
                            default="Hybrid handoff parked this as a quiet receipt.",
                        ),
                        "summary": _first_text(
                            item.get("reactivate_if"),
                            item.get("do_not_elevate_into"),
                            default="Hybrid quiet receipt.",
                        ),
                        "source_refs": [
                            artifact_ref,
                            _string(item.get("source_raw_handoff")),
                        ],
                        "expansion_ref": artifact_ref,
                    }
                )

    return {
        "schema_version": CANDIDATE_INVENTORY_SCHEMA_VERSION,
        "status": "research_only",
        "runtime_policy": "runtime_dormant",
        "case_id": case_id,
        "source_refs": source_refs,
        "candidates": candidates,
    }


def load_candidate_inventory_payload(path: Path) -> dict[str, object]:
    payload = _load_json(Path(path))
    if not isinstance(payload, dict):
        raise CandidateInventoryValidationError(f"{path}: payload must be an object")
    return payload


def validate_candidate_inventory_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_candidate_inventory_errors(payload, path=Path(path)))
    if errors:
        raise CandidateInventoryValidationError("; ".join(errors))


def validate_candidate_inventory_file(path: Path) -> None:
    validate_candidate_inventory_payload(
        load_candidate_inventory_payload(path),
        path=Path(path),
    )


def iter_candidate_inventory_errors(
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
        "source_refs",
        "candidates",
    )
    yield from _unknown_fields(payload, TOP_LEVEL_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return

    if _string(payload.get("schema_version")) != CANDIDATE_INVENTORY_SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {CANDIDATE_INVENTORY_SCHEMA_VERSION}"
    if _string(payload.get("status")) not in ALLOWED_STATUS:
        yield f"{path / 'status'}: status must be research_only"
    if _string(payload.get("runtime_policy")) not in ALLOWED_RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: runtime_policy must be runtime_dormant"
    if not _string(payload.get("case_id")).strip():
        yield f"{path / 'case_id'}: case_id must be non-empty"
    if not _non_empty_string_list(payload.get("source_refs")):
        yield f"{path / 'source_refs'}: source_refs must be a non-empty string list"

    candidates = payload.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        yield f"{path / 'candidates'}: candidates must be a non-empty list"
        return
    seen: set[str] = set()
    for index, candidate in enumerate(candidates):
        candidate_path = path / f"candidates[{index}]"
        if not isinstance(candidate, dict):
            yield f"{candidate_path}: candidate must be an object"
            continue
        yield from _validate_candidate(candidate, path=candidate_path, seen=seen)


def _validate_candidate(
    candidate: dict[str, object],
    *,
    path: Path,
    seen: set[str],
) -> Iterable[str]:
    yield from _unknown_fields(candidate, CANDIDATE_FIELDS, path)
    yield from _missing_fields(candidate, REQUIRED_CANDIDATE_FIELDS, path)
    if any(field not in candidate for field in REQUIRED_CANDIDATE_FIELDS):
        return
    candidate_id = _string(candidate.get("candidate_id"))
    if not candidate_id:
        yield f"{path / 'candidate_id'}: candidate_id must be non-empty"
    elif candidate_id in seen:
        yield f"{path / 'candidate_id'}: duplicate candidate_id"
    seen.add(candidate_id)
    for field in ("origin", "artifact_ref", "selection_basis", "summary", "expansion_ref"):
        if not _string(candidate.get(field)).strip():
            yield f"{path / field}: must be non-empty"
    if not _non_empty_string_list(candidate.get("source_refs")):
        yield f"{path / 'source_refs'}: source_refs must be a non-empty string list"


def _load_json(path: Path) -> object:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _candidate_id(case_id: str, origin: str) -> str:
    raw = f"{case_id}_{origin}".lower().replace("-", "_")
    return ID_RE.sub("_", raw).strip("_")


def _summarize(value: object) -> str:
    if isinstance(value, dict):
        keys = ", ".join(sorted(str(key) for key in value.keys())[:8])
        return f"Object with keys: {keys}."
    if isinstance(value, list):
        return f"List with {len(value)} items."
    text = str(value).strip().replace("\n", " ")
    return text[:180] if text else "Present artifact."


def _first_text(*values: object, default: str) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return default


def _unknown_fields(
    payload: dict[str, object],
    allowed: frozenset[str],
    path: Path,
) -> Iterable[str]:
    for field in sorted(set(payload) - allowed):
        yield f"{path / field}: unknown field"


def _missing_fields(
    payload: dict[str, object],
    required: Sequence[str],
    path: Path,
) -> Iterable[str]:
    for field in required:
        if field not in payload:
            yield f"{path / field}: missing required field"


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


def _non_empty_string_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and item.strip() for item in value
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--result-file", type=Path)
    parser.add_argument("--raw-handoff-file", action="append", type=Path, default=[])
    parser.add_argument("--hybrid-handoff-file", action="append", type=Path, default=[])
    parser.add_argument("--output-file", type=Path)
    args = parser.parse_args(argv)
    payload = build_candidate_inventory(
        case_id=args.case_id,
        result_file=args.result_file,
        raw_handoff_files=args.raw_handoff_file,
        hybrid_handoff_files=args.hybrid_handoff_file,
    )
    validate_candidate_inventory_payload(payload)
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.output_file:
        args.output_file.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
