#!/usr/bin/env python3
"""Research-only payload omission gate for clean-hybrid vs card-deck answers.

This gate is a post-visibility promotion tripwire. It flags only concrete
payload categories that were present in the anchor and absent in the deck-aware
answer. It does not decide which answer is better.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Callable, Iterable, Sequence

from pre_step6_card_deck_replay_comparisons import build_replay_comparison_packet


SCHEMA_VERSION = "pre_step6_payload_omission.v1"
STATUS = "research_only"
RUNTIME_POLICY = "runtime_dormant"
EXPERIMENT_ID = "design_preamble_payload_omission_v0"
DEFAULT_OUT_DIR = Path("research/pre-step6-payload-omission-gates")
CATEGORIES = (
    "dates_or_dated_windows",
    "actor_sequence",
    "named_resources_or_channels",
    "communication_boundaries",
    "tripwires_or_gates",
    "evidence_checks",
)
ALLOWED_JUDGMENTS = frozenset(
    {"case_n_a", "deck_added_payload", "preserved", "introduced_omission"}
)
ALLOWED_GATE_RESULTS = frozenset({"preserved", "introduced_omission", "case_n_a"})
ALLOWED_GATE_ACTIONS = frozenset({"promote_eligible", "retest", "defer"})
TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "case_id",
        "anchor_ref",
        "deck_ref",
        "categories",
        "gate_result",
        "gate_action",
        "visibility_decision",
        "deterministic_limit",
        "gates",
        "notes",
    }
)
CATEGORY_FIELDS = frozenset(
    {
        "category",
        "anchor_present",
        "deck_present",
        "case_live",
        "judgment",
        "detector",
        "anchor_evidence",
        "deck_evidence",
        "missing_anchor_evidence",
    }
)
GATE_FIELDS = frozenset({"runtime_wiring_allowed", "skill_update_allowed"})


class PayloadOmissionValidationError(ValueError):
    pass


def build_payload_omission_gate(*, case_id: str, repo_root: Path) -> dict[str, object]:
    refs = _candidate_refs(case_id=case_id, repo_root=repo_root)
    anchor_answer = _load_anchor_answer(repo_root / refs["anchor_ref"])
    deck_answer = _load_deck_answer(repo_root / refs["deck_ref"])
    return build_payload_omission_payload_from_answers(
        case_id=case_id,
        anchor_ref=refs["anchor_ref"],
        deck_ref=refs["deck_ref"],
        anchor_answer=anchor_answer,
        deck_answer=deck_answer,
    )


def build_payload_omission_payload_from_answers(
    *,
    case_id: str,
    anchor_ref: str,
    deck_ref: str,
    anchor_answer: str,
    deck_answer: str,
) -> dict[str, object]:
    categories = [
        _category_record(category=category, anchor_answer=anchor_answer, deck_answer=deck_answer)
        for category in CATEGORIES
    ]
    gate_result = _gate_result(categories)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "case_id": case_id,
        "anchor_ref": anchor_ref,
        "deck_ref": deck_ref,
        "categories": categories,
        "gate_result": gate_result,
        "gate_action": _gate_action(gate_result),
        "visibility_decision": "not_decided_by_omission_gate",
        "deterministic_limit": (
            "Mechanistic detectors flag introduced omission candidates; this gate "
            "does not choose between anchor and deck answers."
        ),
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": (
            "Research-only omission gate. Anchor activates categories; only "
            "anchor-present/deck-absent rows affect the gate."
        ),
    }
    validate_payload_omission_payload(payload)
    return payload


def load_payload_omission_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise PayloadOmissionValidationError(f"{path}: payload must be an object")
    return payload


def validate_payload_omission_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_payload_omission_errors(payload, path=Path(path)))
    if errors:
        raise PayloadOmissionValidationError("; ".join(errors))


def validate_payload_omission_file(path: Path) -> None:
    validate_payload_omission_payload(load_payload_omission_payload(path), path=Path(path))


def iter_payload_omission_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be an object"
        return
    required = tuple(TOP_LEVEL_FIELDS - {"notes"})
    yield from _unknown_fields(payload, TOP_LEVEL_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return
    if _string(payload.get("schema_version")) != SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {SCHEMA_VERSION}"
    if _string(payload.get("status")) != STATUS:
        yield f"{path / 'status'}: must be {STATUS}"
    if _string(payload.get("runtime_policy")) != RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: must be {RUNTIME_POLICY}"
    if _string(payload.get("experiment_id")) != EXPERIMENT_ID:
        yield f"{path / 'experiment_id'}: must be {EXPERIMENT_ID}"
    if not _string(payload.get("case_id")).strip():
        yield f"{path / 'case_id'}: must be non-empty"
    for field in ("anchor_ref", "deck_ref"):
        if not _string(payload.get(field)).startswith("research/"):
            yield f"{path / field}: must point to research artifact"
    categories = payload.get("categories")
    if not isinstance(categories, list):
        yield f"{path / 'categories'}: must be a list"
    else:
        yield from _validate_categories(categories, path / "categories")
    gate_result = _string(payload.get("gate_result"))
    if gate_result not in ALLOWED_GATE_RESULTS:
        yield f"{path / 'gate_result'}: unsupported result"
    if _string(payload.get("gate_action")) not in ALLOWED_GATE_ACTIONS:
        yield f"{path / 'gate_action'}: unsupported action"
    if payload.get("visibility_decision") != "not_decided_by_omission_gate":
        yield f"{path / 'visibility_decision'}: omission gate must not choose visibility"
    expected = (
        "Mechanistic detectors flag introduced omission candidates; this gate "
        "does not choose between anchor and deck answers."
    )
    if payload.get("deterministic_limit") != expected:
        yield f"{path / 'deterministic_limit'}: invalid deterministic limit"
    if isinstance(categories, list):
        expected_result = _gate_result([item for item in categories if isinstance(item, dict)])
        if gate_result != expected_result:
            yield f"{path / 'gate_result'}: must match category judgments"
        expected_action = _gate_action(expected_result)
        if payload.get("gate_action") != expected_action:
            yield f"{path / 'gate_action'}: must match gate_result"
    yield from _validate_gates(payload.get("gates"), path / "gates")


def write_payload_omission_gate(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_payload_omission_payload(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{_string(payload['case_id'])}.payload-omission.v1.json"
    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return out_path


def _candidate_refs(*, case_id: str, repo_root: Path) -> dict[str, str]:
    packet = build_replay_comparison_packet(case_id=case_id, repo_root=repo_root)
    refs = packet.get("candidate_refs")
    if not isinstance(refs, dict):
        raise PayloadOmissionValidationError("candidate refs missing")
    return {
        "anchor_ref": _string(refs.get("clean_hybrid")),
        "deck_ref": _string(refs.get("card_deck_replay")),
    }


def _load_anchor_answer(path: Path) -> str:
    payload = _load_json(path)
    return _string(payload.get("answer_core"))


def _load_deck_answer(path: Path) -> str:
    payload = _load_json(path)
    output = payload.get("step6_output")
    if not isinstance(output, dict):
        return ""
    return _string(output.get("answer_core"))


def _category_record(*, category: str, anchor_answer: str, deck_answer: str) -> dict[str, object]:
    detector_name, detector = _detector(category)
    anchor_evidence = detector(anchor_answer)
    deck_evidence = detector(deck_answer)
    anchor_present = bool(anchor_evidence)
    deck_present = bool(deck_evidence)
    return {
        "category": category,
        "anchor_present": anchor_present,
        "deck_present": deck_present,
        "case_live": anchor_present,
        "judgment": _judgment(anchor_present=anchor_present, deck_present=deck_present),
        "detector": detector_name,
        "anchor_evidence": anchor_evidence,
        "deck_evidence": deck_evidence,
        "missing_anchor_evidence": _missing_evidence(anchor_evidence, deck_evidence),
    }


def _judgment(*, anchor_present: bool, deck_present: bool) -> str:
    if anchor_present and deck_present:
        return "preserved"
    if anchor_present and not deck_present:
        return "introduced_omission"
    if not anchor_present and deck_present:
        return "deck_added_payload"
    return "case_n_a"


def _gate_result(categories: Sequence[dict[str, object]]) -> str:
    judgments = {_string(item.get("judgment")) for item in categories}
    if "introduced_omission" in judgments:
        return "introduced_omission"
    if judgments <= {"case_n_a"}:
        return "case_n_a"
    return "preserved"


def _gate_action(gate_result: str) -> str:
    if gate_result == "introduced_omission":
        return "retest"
    return "promote_eligible"


def _detector(category: str) -> tuple[str, Callable[[str], list[str]]]:
    detectors: dict[str, tuple[str, Callable[[str], list[str]]]] = {
        "dates_or_dated_windows": ("regex_date_window_v0", _detect_dates_or_windows),
        "actor_sequence": ("sequence_marker_v0", _detect_actor_sequence),
        "named_resources_or_channels": ("named_resource_channel_v0", _detect_resources_or_channels),
        "communication_boundaries": ("communication_boundary_v0", _detect_communication_boundaries),
        "tripwires_or_gates": ("tripwire_gate_marker_v0", _detect_tripwires_or_gates),
        "evidence_checks": ("evidence_check_marker_v0", _detect_evidence_checks),
    }
    if category not in detectors:
        raise PayloadOmissionValidationError(f"unsupported category: {category}")
    return detectors[category]


def _detect_dates_or_windows(text: str) -> list[str]:
    return _unique_matches(
        text,
        (
            r"\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b",
            r"\b(?:today|tomorrow|tonight|right now|this week|next week|next few weeks|this month|next month)\b",
            r"\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b",
            r"\b\d+\s*(?:day|days|week|weeks|month|months|hour|hours)\b",
            r"\b\d+\s*-\s*\d+\s*(?:day|days|week|weeks|month|months|year|years)\b",
            r"\bshort(?:,|\s)+defined period\b",
            r"\bshort sprint\b",
            r"\bshort window\b",
            r"\bstop date\b",
        ),
    )


def _detect_actor_sequence(text: str) -> list[str]:
    sentences = _sentences(text)
    evidence = []
    for sentence in sentences:
        if re.search(r"\b(?:then|before|after|first|next|sequence|break this into|plan for|decide how|pulling others|team continuity)\b", sentence, re.I):
            if re.search(r"\b[A-Z][a-z]+\b", sentence) or re.search(r"\b(?:team|client|others|provider|partner|manager)\b", sentence, re.I):
                evidence.append(sentence.strip())
    return _dedupe(evidence)


def _detect_resources_or_channels(text: str) -> list[str]:
    return _unique_matches(
        text,
        (
            r"\b(?:platform|client|buyer|board|CTO|governance|revenue|team|knowledge transfer)\b",
            r"\b(?:RAINN|therapist|counsel|police|legal guidance|phone access|phone|blocking|screenshots|messages|monitored channel)\b",
            r"\b(?:advisor|committee|Silva|lab|single-cell|data|collaborator|fallback|dissertation)\b",
            r"\b(?:Marcus|Jake|Lina|Magda)\b",
        ),
    )


def _detect_communication_boundaries(text: str) -> list[str]:
    sentences = _sentences(text)
    evidence = []
    for sentence in sentences:
        if re.search(r"\b(?:say|make clear|conversation|discussion|avoid|do not|don't|cannot|keep|not vague|flat rejection|vague delay)\b", sentence, re.I):
            evidence.append(sentence.strip())
    return _dedupe(evidence)


def _detect_tripwires_or_gates(text: str) -> list[str]:
    sentences = _sentences(text)
    evidence = []
    for sentence in sentences:
        if re.search(r"\b(?:if|unless|until|before|only after|not before|gate|gates|unlock|trigger|cannot|do not|should not)\b", sentence, re.I):
            evidence.append(sentence.strip())
    return _dedupe(evidence)


def _detect_evidence_checks(text: str) -> list[str]:
    sentences = _sentences(text)
    evidence = []
    for sentence in sentences:
        if re.search(r"\b(?:evidence|test|tests|tested|prove|proof|proving|whether|verify|verified|check|demonstrated|seeing)\b", sentence, re.I):
            evidence.append(sentence.strip())
    return _dedupe(evidence)


def _unique_matches(text: str, patterns: Sequence[str]) -> list[str]:
    matches: list[str] = []
    for pattern in patterns:
        matches.extend(match.group(0) for match in re.finditer(pattern, text, re.I))
    return _dedupe(matches)


def _missing_evidence(anchor_evidence: Sequence[str], deck_evidence: Sequence[str]) -> list[str]:
    deck_lc = {_normalize(item) for item in deck_evidence}
    return [item for item in anchor_evidence if _normalize(item) not in deck_lc]


def _sentences(text: str) -> list[str]:
    normalized = " ".join(text.split())
    if not normalized:
        return []
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", normalized) if part.strip()]


def _dedupe(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = _normalize(value)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(value)
    return result


def _normalize(value: str) -> str:
    return " ".join(value.casefold().split())


def _load_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise PayloadOmissionValidationError(f"{path}: payload must be an object")
    return payload


def _validate_categories(categories: list[object], path: Path) -> Iterable[str]:
    if [item.get("category") for item in categories if isinstance(item, dict)] != list(CATEGORIES):
        yield f"{path}: categories must match protected payload category order"
    for index, item in enumerate(categories):
        item_path = path / str(index)
        if not isinstance(item, dict):
            yield f"{item_path}: must be an object"
            continue
        yield from _unknown_fields(item, CATEGORY_FIELDS, item_path)
        yield from _missing_fields(item, CATEGORY_FIELDS, item_path)
        if any(field not in item for field in CATEGORY_FIELDS):
            continue
        if _string(item.get("category")) not in CATEGORIES:
            yield f"{item_path / 'category'}: unsupported category"
        for field in ("anchor_present", "deck_present", "case_live"):
            if not isinstance(item.get(field), bool):
                yield f"{item_path / field}: must be boolean"
        if item.get("case_live") != item.get("anchor_present"):
            yield f"{item_path / 'case_live'}: must equal anchor_present"
        expected = _judgment(
            anchor_present=item.get("anchor_present") is True,
            deck_present=item.get("deck_present") is True,
        )
        if item.get("judgment") != expected:
            yield f"{item_path / 'judgment'}: must be {expected}"
        if _string(item.get("judgment")) not in ALLOWED_JUDGMENTS:
            yield f"{item_path / 'judgment'}: unsupported judgment"
        if not _string(item.get("detector")).strip():
            yield f"{item_path / 'detector'}: must be non-empty"
        for field in ("anchor_evidence", "deck_evidence", "missing_anchor_evidence"):
            if not isinstance(item.get(field), list):
                yield f"{item_path / field}: must be a list"
        if item.get("anchor_present") is True and not item.get("anchor_evidence"):
            yield f"{item_path / 'anchor_evidence'}: required when anchor_present"
        if item.get("deck_present") is True and not item.get("deck_evidence"):
            yield f"{item_path / 'deck_evidence'}: required when deck_present"


def _validate_gates(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    yield from _unknown_fields(value, GATE_FIELDS, path)
    yield from _missing_fields(value, GATE_FIELDS, path)
    if value.get("runtime_wiring_allowed") is not False:
        yield f"{path / 'runtime_wiring_allowed'}: must be false"
    if value.get("skill_update_allowed") is not False:
        yield f"{path / 'skill_update_allowed'}: must be false"


def _unknown_fields(value: dict[str, object], allowed: frozenset[str], path: Path) -> Iterable[str]:
    for field in sorted(set(value) - allowed):
        yield f"{path / field}: unknown field"


def _missing_fields(value: dict[str, object], required: Iterable[str], path: Path) -> Iterable[str]:
    for field in sorted(set(required) - set(value)):
        yield f"{path / field}: missing required field"


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="Existing payload-omission artifacts to validate")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--case-id", default="founder-grant-marcus-equity.high-clutter")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--write", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.paths:
        for path in args.paths:
            validate_payload_omission_file(path)
        return 0
    payload = build_payload_omission_gate(case_id=args.case_id, repo_root=args.repo_root)
    if args.write:
        print(write_payload_omission_gate(payload=payload, out_dir=args.out_dir))
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
