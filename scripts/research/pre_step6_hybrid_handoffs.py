#!/usr/bin/env python3
"""Research-only validation/rendering for pre-Step-6 hybrid handoffs.

This module validates the card-first/raw-available handoff surface. It is
deliberately outside the live pipeline. It does not launch workers, select
truth, change /lolla behavior, or promote product docs.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Sequence

from pre_step6_raw_artifacts import (
    load_raw_artifact_payload,
    validate_raw_artifact_payload,
)
from pre_step6_workpacks import (
    load_json_payload,
    validate_pressure_card_payload,
)


HYBRID_HANDOFF_SCHEMA_VERSION = "pre_step6_hybrid_handoff.v1"
MAX_INSPECT_MORE_ITEMS = 2
MAX_RAW_EXCERPT_CHARS = 700
MAX_RENDER_CHARS = 3200
ALLOWED_STATUS = frozenset({"research_only"})
ALLOWED_RUNTIME_POLICY = frozenset({"runtime_dormant"})
ALLOWED_INSPECT_REASONS = frozenset(
    {"lossy", "contested", "high_stakes", "missing_nuance"}
)
HANDOFF_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "source_pressure_card",
        "inspect_more",
        "notes",
    }
)
INSPECT_MORE_FIELDS = frozenset(
    {
        "reason",
        "source_raw_handoff",
        "artifact_id",
        "raw_excerpt",
        "use_only_to_recover",
        "do_not_expand_into",
    }
)


class HybridHandoffValidationError(ValueError):
    pass


def load_handoff_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise HybridHandoffValidationError(f"{path}: payload must be an object")
    return payload


def validate_hybrid_handoff_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
) -> None:
    errors = list(
        iter_hybrid_handoff_errors(payload, path=Path(path), repo_root=repo_root)
    )
    if errors:
        raise HybridHandoffValidationError("; ".join(errors))


def validate_hybrid_handoff_file(
    path: Path,
    *,
    repo_root: Path | None = None,
) -> None:
    validate_hybrid_handoff_payload(
        load_handoff_payload(path),
        path=Path(path),
        repo_root=repo_root,
    )


def iter_hybrid_handoff_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
) -> Iterable[str]:
    required = (
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "source_pressure_card",
        "inspect_more",
    )
    yield from _unknown_fields(payload, HANDOFF_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return

    if _string(payload.get("schema_version")) != HYBRID_HANDOFF_SCHEMA_VERSION:
        yield f"{path}: schema_version must be {HYBRID_HANDOFF_SCHEMA_VERSION}"
    if _string(payload.get("status")) not in ALLOWED_STATUS:
        yield f"{path / 'status'}: status must be research_only"
    if _string(payload.get("runtime_policy")) not in ALLOWED_RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: runtime_policy must be runtime_dormant"
    case_id = _string(payload.get("case_id"))
    if not case_id.strip():
        yield f"{path / 'case_id'}: case_id must be non-empty"

    source_card = _string(payload.get("source_pressure_card"))
    if not source_card:
        yield f"{path / 'source_pressure_card'}: must be non-empty"
    elif repo_root is not None:
        card_path = repo_root / source_card
        if not card_path.exists():
            yield f"{path / 'source_pressure_card'}: source pressure card does not exist"
        else:
            card_payload = load_json_payload(card_path)
            validate_pressure_card_payload(card_payload, path=card_path)
            if not card_path.name.startswith(case_id):
                yield f"{path / 'source_pressure_card'}: source pressure card case_id mismatch"

    inspect_more = payload.get("inspect_more")
    if not isinstance(inspect_more, list):
        yield f"{path / 'inspect_more'}: inspect_more must be a list"
        return
    if len(inspect_more) > MAX_INSPECT_MORE_ITEMS:
        yield (
            f"{path / 'inspect_more'}: "
            f"inspect_more must not exceed {MAX_INSPECT_MORE_ITEMS}"
        )
    for index, item in enumerate(inspect_more):
        item_path = path / f"inspect_more[{index}]"
        if not isinstance(item, dict):
            yield f"{item_path}: inspect_more item must be an object"
            continue
        yield from _validate_inspect_more_item(
            item,
            path=item_path,
            repo_root=repo_root,
            case_id=case_id,
        )


def _validate_inspect_more_item(
    item: dict[str, object],
    *,
    path: Path,
    repo_root: Path | None,
    case_id: str,
) -> Iterable[str]:
    required = (
        "reason",
        "source_raw_handoff",
        "artifact_id",
        "raw_excerpt",
        "use_only_to_recover",
        "do_not_expand_into",
    )
    yield from _unknown_fields(item, INSPECT_MORE_FIELDS, path)
    yield from _missing_fields(item, required, path)
    if any(field not in item for field in required):
        return

    reason = _string(item.get("reason"))
    if reason not in ALLOWED_INSPECT_REASONS:
        yield f"{path / 'reason'}: unknown inspect reason '{reason}'"

    source_raw = _string(item.get("source_raw_handoff"))
    if not source_raw:
        yield f"{path / 'source_raw_handoff'}: must be non-empty"
    elif repo_root is not None:
        raw_path = repo_root / source_raw
        if not raw_path.exists():
            yield f"{path / 'source_raw_handoff'}: source raw handoff does not exist"
        else:
            raw_payload = load_raw_artifact_payload(raw_path)
            validate_raw_artifact_payload(raw_payload, path=raw_path)
            if _string(raw_payload.get("case_id")) != case_id:
                yield f"{path / 'source_raw_handoff'}: source raw handoff case_id mismatch"
            artifact_ids = {
                _string(artifact.get("artifact_id"))
                for artifact in raw_payload.get("artifacts", [])
                if isinstance(artifact, dict)
            }
            artifact_id = _string(item.get("artifact_id"))
            if artifact_id not in artifact_ids:
                yield f"{path / 'artifact_id'}: unknown artifact_id '{artifact_id}'"

    for field in ("artifact_id", "raw_excerpt", "use_only_to_recover", "do_not_expand_into"):
        value = _string(item.get(field))
        if not value.strip():
            yield f"{path / field}: must be non-empty"
    raw_excerpt = _string(item.get("raw_excerpt"))
    if len(raw_excerpt) > MAX_RAW_EXCERPT_CHARS:
        yield (
            f"{path / 'raw_excerpt'}: raw_excerpt is {len(raw_excerpt)} chars; "
            f"max is {MAX_RAW_EXCERPT_CHARS}"
        )


def render_hybrid_handoff(
    payload: dict[str, object],
    *,
    repo_root: Path,
    max_chars: int = MAX_RENDER_CHARS,
) -> str:
    validate_hybrid_handoff_payload(payload, repo_root=repo_root)
    card_path = repo_root / _string(payload.get("source_pressure_card"))
    card = load_json_payload(card_path)
    inspect_more = payload["inspect_more"]
    assert isinstance(inspect_more, list)

    lines = [
        "STEP 6 PRIVATE PRESSURE",
        "",
        "Use the card first. Do not expose this private handoff publicly.",
        "Reject any pressure that does not fit the conversation.",
        "",
        f"Case: {_string(payload.get('case_id'))}",
        "",
        "CARD",
        f"Pressure: {_string(card.get('pressure'))}",
        f"Boundary: {_string(card.get('boundary'))}",
        f"Relax if: {_string(card.get('relax_if'))}",
        f"Discard if: {_string(card.get('discard_if'))}",
        f"Risk if ignored: {_string(card.get('risk_if_ignored'))}",
        "",
        "INSPECT MORE",
    ]
    if not inspect_more:
        lines.append("None. Raw inspection is not authorized for this fixture.")
    for item in inspect_more:
        assert isinstance(item, dict)
        lines.extend(
            [
                f"Reason: {_string(item.get('reason'))}",
                f"Raw nuance: {_string(item.get('raw_excerpt'))}",
                f"Use only to recover: {_string(item.get('use_only_to_recover'))}",
                f"Do not expand into: {_string(item.get('do_not_expand_into'))}",
                "",
            ]
        )

    lines.extend(
        [
            "STEP 6 RULE",
            "Write the public answer from the conversation plus this pressure.",
            "Use the card as the default.",
            "Inspect raw only for the named nuance.",
            "Do not turn inspect-more material into extra sections.",
        ]
    )

    rendered = "\n".join(lines)
    if len(rendered) > max_chars:
        raise HybridHandoffValidationError(
            f"rendered handoff is {len(rendered)} chars; max is {max_chars}"
        )
    return rendered


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


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate or render research-only pre-Step-6 hybrid handoffs."
    )
    parser.add_argument("path", type=Path)
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args(argv)

    payload = load_handoff_payload(args.path)
    validate_hybrid_handoff_payload(payload, path=args.path, repo_root=args.repo_root)
    if args.render:
        print(render_hybrid_handoff(payload, repo_root=args.repo_root))
    else:
        print(f"valid hybrid handoff: {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
