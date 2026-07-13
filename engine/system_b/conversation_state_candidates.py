"""Typed, provider-free conversation-state candidate contracts and source custody.

Dataclass fields are the single source of truth for local parsing and generated
provider schemas. Models decide semantic content; this module only validates
shape, controlled vocabularies, source identity, and exact excerpts.
"""
from __future__ import annotations

import hashlib
import json
import re
import types
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field, fields, is_dataclass
from typing import Any, Optional, TypeVar, Union, get_args, get_origin, get_type_hints

from .conversation_state_handoff import (
    CLAIM_MODES,
    CONTRIBUTION_ROLES,
    CONSTRAINT_STATES,
    EVIDENCE_MODES,
    OWNERSHIP,
    POSITION_STATES,
    THREAD_DISPOSITIONS,
    THREAD_ENGAGEMENTS,
)


SOURCE_CATALOG_SCHEMA = "lolla.conversation_source_catalog.v1"
POSITION_OUTPUT_SCHEMA = "lolla.position_contribution_candidates.v1"
THREAD_OUTPUT_SCHEMA = "lolla.focal_thread_candidates.v1"
CONSTRAINT_OUTPUT_SCHEMA = "lolla.atomic_constraint_candidates.v1"
EXTRACTION_STATUSES = ("supported", "unclear", "not_found")

_TURN_PATTERN = re.compile(
    r"\[Turn\s+(\d+)\]\s+(USER|ASSISTANT):\s*\n"
    r"(.*?)(?=\n\[Turn\s+\d+\]\s+(?:USER|ASSISTANT):|\Z)",
    re.DOTALL,
)
_SENTENCE_END = re.compile(r"[.!?](?:[\"”’])?(?=\s+|\Z)")


def _f(
    description: str,
    *,
    enum: Optional[Sequence[str]] = None,
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
    allow_empty: bool = False,
):
    metadata: dict[str, Any] = {
        "description": description,
        "allow_empty": allow_empty,
    }
    if enum is not None:
        metadata["enum"] = tuple(enum)
    if min_items is not None:
        metadata["min_items"] = min_items
    if max_items is not None:
        metadata["max_items"] = max_items
    return field(metadata=metadata)


@dataclass(frozen=True)
class EvidenceRef:
    span_id: str = _f("Stable source-catalog span identifier selected as evidence.")
    excerpt: str = _f("Exact contiguous substring copied from the selected span.")


@dataclass(frozen=True)
class DecisionSummaryCandidate:
    text: str = _f("Compact description of the current decision state; not advice.")
    evidence_mode: str = _f(
        "Whether the interpretation uses one exact span or multiple turns.",
        enum=sorted(EVIDENCE_MODES),
    )
    evidence: tuple[EvidenceRef, ...] = _f(
        "Source references supporting the decision-state summary.",
        min_items=1,
        max_items=4,
    )


@dataclass(frozen=True)
class ContributionCandidate:
    role: str = _f(
        "How this speaker contribution affected the position.",
        enum=sorted(CONTRIBUTION_ROLES),
    )
    evidence: EvidenceRef = _f("Exact source evidence for this contribution.")


@dataclass(frozen=True)
class PositionCandidate:
    text: str = _f("One current or materially developed position in neutral language.")
    ownership: str = _f(
        "Who materially supplied or developed the position.", enum=sorted(OWNERSHIP)
    )
    state: str = _f("Current state of the position.", enum=sorted(POSITION_STATES))
    evidence_mode: str = _f(
        "Whether the position uses one exact span or a multi-turn derivation.",
        enum=sorted(EVIDENCE_MODES),
    )
    contributions: tuple[ContributionCandidate, ...] = _f(
        "Speaker contributions that justify ownership and trajectory.",
        min_items=1,
        max_items=8,
    )


@dataclass(frozen=True)
class PositionExtraction:
    status: str = _f(
        "supported when candidates are source-supported; unclear when competing readings remain; not_found when no candidate is justified.",
        enum=EXTRACTION_STATUSES,
    )
    decision_summary: Optional[DecisionSummaryCandidate] = _f(
        "Current decision-state candidate, or null when status is not_found.",
        allow_empty=True,
    )
    positions: tuple[PositionCandidate, ...] = _f(
        "Position candidates; an empty list is valid for not_found.",
        min_items=0,
        max_items=4,
        allow_empty=True,
    )


@dataclass(frozen=True)
class ThreadResponseCandidate:
    engagement: str = _f(
        "How the response engaged the focal thread.",
        enum=sorted(THREAD_ENGAGEMENTS),
    )
    evidence: EvidenceRef = _f("Exact source evidence for this response.")


@dataclass(frozen=True)
class ThreadCandidate:
    text: str = _f("One focal substantive thread tracked across the conversation.")
    disposition: str = _f(
        "Full-trajectory disposition of the focal thread.",
        enum=sorted(THREAD_DISPOSITIONS),
    )
    introduced: EvidenceRef = _f("Source evidence where the thread was introduced.")
    responses: tuple[ThreadResponseCandidate, ...] = _f(
        "Subsequent responses to the same thread; empty only when genuinely unaddressed.",
        min_items=0,
        max_items=8,
        allow_empty=True,
    )
    latest: EvidenceRef = _f("Latest material source reference for this thread.")
    superseded_by: Optional[str] = _f(
        "Replacement thread label only when disposition is superseded; otherwise null.",
        allow_empty=True,
    )
    evidence_mode: str = _f(
        "Whether the disposition uses one exact span or multiple turns.",
        enum=sorted(EVIDENCE_MODES),
    )


@dataclass(frozen=True)
class ThreadExtraction:
    status: str = _f(
        "supported, unclear, or not_found for focal-thread extraction.",
        enum=EXTRACTION_STATUSES,
    )
    threads: tuple[ThreadCandidate, ...] = _f(
        "Focal thread candidates; empty is valid for not_found.",
        min_items=0,
        max_items=6,
        allow_empty=True,
    )


@dataclass(frozen=True)
class ConstraintCandidate:
    text: str = _f("One atomic decision condition whose removal could change the choice.")
    state: str = _f("Current state of this constraint.", enum=sorted(CONSTRAINT_STATES))
    claim_mode: str = _f(
        "Strength with which the source states this one atomic claim.",
        enum=sorted(CLAIM_MODES - {"mixed"}),
    )
    evidence_mode: str = _f(
        "Whether this atomic constraint uses one exact span or multiple turns.",
        enum=sorted(EVIDENCE_MODES),
    )
    evidence: tuple[EvidenceRef, ...] = _f(
        "Exact source references supporting this atomic constraint.",
        min_items=1,
        max_items=4,
    )


@dataclass(frozen=True)
class ConstraintExtraction:
    status: str = _f(
        "supported, unclear, or not_found for atomic-constraint extraction.",
        enum=EXTRACTION_STATUSES,
    )
    constraints: tuple[ConstraintCandidate, ...] = _f(
        "Atomic constraint candidates; empty is valid for not_found.",
        min_items=0,
        max_items=16,
        allow_empty=True,
    )


@dataclass(frozen=True)
class SourceSpan:
    span_id: str
    turn_id: str
    turn_index: int
    speaker: str
    kind: str
    char_start: int
    char_end: int
    text: str


@dataclass(frozen=True)
class SourceCatalog:
    schema_version: str
    source_path: str
    source_sha256: str
    message_count: int
    spans: tuple[SourceSpan, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def by_id(self) -> dict[str, SourceSpan]:
        return {span.span_id: span for span in self.spans}


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    path: str
    detail: str = ""

    def to_dict(self) -> dict[str, str]:
        payload = {"code": self.code, "path": self.path}
        if self.detail:
            payload["detail"] = self.detail
        return payload


_T = TypeVar("_T")


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _stable_span_id(
    *, source_sha256: str, turn_id: str, kind: str, start: int, end: int, text: str
) -> str:
    digest = _sha256_text(
        f"{source_sha256}|{turn_id}|{kind}|{start}|{end}|{text}"
    )[:16]
    return f"span-{digest}"


def _sentence_ranges(text: str) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    start = 0
    for match in _SENTENCE_END.finditer(text):
        end = match.end()
        left = start
        while left < end and text[left].isspace():
            left += 1
        right = end
        while right > left and text[right - 1].isspace():
            right -= 1
        if right > left:
            ranges.append((left, right))
        start = end
    while start < len(text) and text[start].isspace():
        start += 1
    if start < len(text):
        ranges.append((start, len(text)))
    return ranges


def build_source_catalog(*, source_text: str, source_path: str) -> SourceCatalog:
    source_sha = _sha256_text(source_text)
    spans: list[SourceSpan] = []
    seen_turns: set[tuple[int, str]] = set()
    for match in _TURN_PATTERN.finditer(source_text):
        turn_index = int(match.group(1))
        speaker = match.group(2).lower()
        key = (turn_index, speaker)
        if key in seen_turns:
            raise ValueError(f"duplicate source turn identity: {key}")
        seen_turns.add(key)
        text = match.group(3).strip()
        turn_id = f"turn-{turn_index:03d}-{speaker}"
        spans.append(
            SourceSpan(
                span_id=_stable_span_id(
                    source_sha256=source_sha,
                    turn_id=turn_id,
                    kind="turn",
                    start=0,
                    end=len(text),
                    text=text,
                ),
                turn_id=turn_id,
                turn_index=turn_index,
                speaker=speaker,
                kind="turn",
                char_start=0,
                char_end=len(text),
                text=text,
            )
        )
        for start, end in _sentence_ranges(text):
            sentence = text[start:end]
            spans.append(
                SourceSpan(
                    span_id=_stable_span_id(
                        source_sha256=source_sha,
                        turn_id=turn_id,
                        kind="sentence",
                        start=start,
                        end=end,
                        text=sentence,
                    ),
                    turn_id=turn_id,
                    turn_index=turn_index,
                    speaker=speaker,
                    kind="sentence",
                    char_start=start,
                    char_end=end,
                    text=sentence,
                )
            )
    return SourceCatalog(
        schema_version=SOURCE_CATALOG_SCHEMA,
        source_path=source_path,
        source_sha256=source_sha,
        message_count=len(seen_turns),
        spans=tuple(spans),
    )


def resolve_evidence(
    ref: EvidenceRef, *, catalog: SourceCatalog, path: str = "/evidence"
) -> tuple[Optional[SourceSpan], list[ValidationIssue]]:
    span = catalog.by_id().get(ref.span_id)
    if span is None:
        return None, [ValidationIssue("source_span_not_found", path + "/span_id")]
    if not ref.excerpt:
        return None, [ValidationIssue("source_excerpt_empty", path + "/excerpt")]
    occurrences = span.text.count(ref.excerpt)
    if occurrences == 0:
        return None, [ValidationIssue("source_excerpt_not_exact", path + "/excerpt")]
    if occurrences > 1:
        return None, [ValidationIssue("source_excerpt_not_unique_in_span", path + "/excerpt")]
    return span, []


def evidence_to_handoff(ref: EvidenceRef, *, catalog: SourceCatalog) -> dict[str, Any]:
    span, issues = resolve_evidence(ref, catalog=catalog)
    if issues or span is None:
        raise ValueError([issue.to_dict() for issue in issues])
    return {
        "speaker": span.speaker,
        "turn_index": span.turn_index,
        "quote": ref.excerpt,
    }


def _is_union(origin: object) -> bool:
    return origin in {Union, types.UnionType}


def _schema_for_type(
    annotation: Any, *, definitions: Optional[dict[str, Any]] = None
) -> dict[str, Any]:
    origin = get_origin(annotation)
    args = get_args(annotation)
    if annotation is str:
        return {"type": "string"}
    if annotation is int:
        return {"type": "integer"}
    if annotation is bool:
        return {"type": "boolean"}
    if is_dataclass(annotation):
        if definitions is None:
            return schema_for_dataclass(annotation)
        name = annotation.__name__
        if name not in definitions:
            definitions[name] = {}
            definitions[name] = _dataclass_object_schema(
                annotation, definitions=definitions
            )
        return {"$ref": f"#/$defs/{name}"}
    if origin is tuple:
        return {
            "type": "array",
            "items": _schema_for_type(args[0], definitions=definitions),
        }
    if _is_union(origin):
        variants = [
            {"type": "null"}
            if item is type(None)
            else _schema_for_type(item, definitions=definitions)
            for item in args
        ]
        return {"anyOf": variants}
    raise TypeError(f"unsupported candidate annotation: {annotation!r}")


def _dataclass_object_schema(
    cls: type[Any], *, definitions: Optional[dict[str, Any]] = None
) -> dict[str, Any]:
    hints = get_type_hints(cls)
    properties: dict[str, Any] = {}
    required: list[str] = []
    for item in fields(cls):
        spec = _schema_for_type(hints[item.name], definitions=definitions)
        metadata = dict(item.metadata)
        spec["description"] = metadata.get("description", "")
        if metadata.get("enum"):
            spec["enum"] = list(metadata["enum"])
        for source, target in (("min_items", "minItems"), ("max_items", "maxItems")):
            if source in metadata:
                spec[target] = metadata[source]
        properties[item.name] = spec
        required.append(item.name)
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        "required": required,
    }


def schema_for_dataclass(
    cls: type[Any], *, use_references: bool = False
) -> dict[str, Any]:
    if not use_references:
        return _dataclass_object_schema(cls)
    definitions: dict[str, Any] = {}
    root = _dataclass_object_schema(cls, definitions=definitions)
    if definitions:
        root["$defs"] = definitions
    return root


def _project_gemini(value: Any) -> Any:
    if isinstance(value, list):
        return [_project_gemini(item) for item in value]
    if not isinstance(value, dict):
        return value
    projected = {key: _project_gemini(item) for key, item in value.items()}
    variants = projected.get("anyOf")
    if (
        isinstance(variants, list)
        and len(variants) == 2
        and all(isinstance(item, dict) and set(item) == {"type"} for item in variants)
        and {item["type"] for item in variants} == {"string", "null"}
    ):
        projected.pop("anyOf")
        projected["type"] = ["string", "null"]
    return projected


def provider_schema(kind: str, *, provider: str) -> dict[str, Any]:
    classes = {
        "positions": PositionExtraction,
        "threads": ThreadExtraction,
        "constraints": ConstraintExtraction,
    }
    if kind not in classes:
        raise ValueError(f"unknown candidate kind: {kind}")
    schema = schema_for_dataclass(classes[kind], use_references=True)
    if provider == "openai":
        return schema
    if provider == "gemini":
        return _project_gemini(schema)
    raise ValueError(f"unsupported provider projection: {provider}")


def schema_metrics(schema: Mapping[str, Any]) -> dict[str, int]:
    def depth(value: Any) -> int:
        if isinstance(value, dict):
            return 1 + max((depth(item) for item in value.values()), default=0)
        if isinstance(value, list):
            return 1 + max((depth(item) for item in value), default=0)
        return 0

    encoded = json.dumps(schema, sort_keys=True, separators=(",", ":"))
    return {
        "bytes": len(encoded.encode("utf-8")),
        "depth": depth(schema),
        "property_nodes": encoded.count('"properties"'),
    }


def _parse_value(
    annotation: Any,
    value: Any,
    *,
    metadata: Mapping[str, Any],
    path: str,
    issues: list[ValidationIssue],
) -> Any:
    origin = get_origin(annotation)
    args = get_args(annotation)
    if _is_union(origin):
        if value is None and type(None) in args:
            return None
        non_null = [item for item in args if item is not type(None)]
        if len(non_null) == 1:
            return _parse_value(
                non_null[0], value, metadata=metadata, path=path, issues=issues
            )
    if is_dataclass(annotation):
        parsed, nested = parse_typed(annotation, value, path=path)
        issues.extend(nested)
        return parsed
    if origin is tuple:
        if not isinstance(value, list):
            issues.append(ValidationIssue("expected_array", path))
            return tuple()
        minimum = int(metadata.get("min_items", 0))
        maximum = metadata.get("max_items")
        if len(value) < minimum:
            issues.append(ValidationIssue("array_too_short", path))
        if maximum is not None and len(value) > int(maximum):
            issues.append(ValidationIssue("array_too_long", path))
        return tuple(
            _parse_value(args[0], item, metadata={}, path=f"{path}/{index}", issues=issues)
            for index, item in enumerate(value)
        )
    expected = {str: "string", int: "integer", bool: "boolean"}.get(annotation)
    valid = (
        isinstance(value, str)
        if annotation is str
        else isinstance(value, int) and not isinstance(value, bool)
        if annotation is int
        else isinstance(value, bool)
        if annotation is bool
        else False
    )
    if not valid:
        issues.append(ValidationIssue(f"expected_{expected or 'supported_type'}", path))
        return value
    if annotation is str:
        if not value and not metadata.get("allow_empty", False):
            issues.append(ValidationIssue("empty_string_forbidden", path))
        allowed = metadata.get("enum")
        if allowed and value not in allowed:
            issues.append(ValidationIssue("enum_value_invalid", path, value))
    return value


def parse_typed(
    cls: type[_T], payload: object, *, path: str = ""
) -> tuple[Optional[_T], list[ValidationIssue]]:
    issues: list[ValidationIssue] = []
    if not isinstance(payload, Mapping):
        return None, [ValidationIssue("expected_object", path or "/")]
    expected = {item.name for item in fields(cls)}
    actual = set(payload)
    for name in sorted(expected - actual):
        issues.append(ValidationIssue("required_field_missing", f"{path}/{name}"))
    for name in sorted(actual - expected):
        issues.append(ValidationIssue("additional_field_forbidden", f"{path}/{name}"))
    hints = get_type_hints(cls)
    values: dict[str, Any] = {}
    for item in fields(cls):
        if item.name not in payload:
            continue
        values[item.name] = _parse_value(
            hints[item.name],
            payload[item.name],
            metadata=item.metadata,
            path=f"{path}/{item.name}",
            issues=issues,
        )
    if expected - actual:
        return None, issues
    try:
        result = cls(**values)
    except TypeError:
        return None, issues or [ValidationIssue("typed_construction_failed", path or "/")]
    return result, issues


def validate_extraction_state(value: Any) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    status = getattr(value, "status", "")
    if isinstance(value, PositionExtraction):
        items = value.positions
        if status == "not_found" and (value.decision_summary is not None or items):
            issues.append(ValidationIssue("not_found_must_be_empty", "/"))
        if status == "supported" and (value.decision_summary is None or not items):
            issues.append(ValidationIssue("supported_requires_candidates", "/"))
    else:
        items = getattr(value, "threads", getattr(value, "constraints", ()))
        if status == "not_found" and items:
            issues.append(ValidationIssue("not_found_must_be_empty", "/"))
        if status == "supported" and not items:
            issues.append(ValidationIssue("supported_requires_candidates", "/"))
    return issues


_COMMON_MICRO_RULES = """Use the complete ordered SOURCE SPAN CATALOG as the only evidence source.
Every evidence object must select one supplied span_id and copy a character-exact contiguous excerpt from that span. Never join non-contiguous text. Review the full catalog before deciding.

Return status `supported` when at least one source-supported candidate is present, `unclear` when materially competing interpretations remain, or `not_found` when no candidate is justified. Empty candidate arrays are valid for `not_found`; do not invent an item to fill the schema.

Do not evaluate advice quality, name mental models, propose graph seeds, or decide what the user should do. Return exactly one JSON object matching the supplied schema and no wrapper."""

_MICRO_JOBS = {
    "positions": """Extract only the current decision-state summary and materially developed positions with contribution ownership.
Track who originated, developed, qualified, challenged, or accepted each position. `joint` requires material evidence from both user and assistant. Preserve late qualifications rather than treating an earlier plan as final. Do not extract threads or constraints in this call.""",
    "threads": """Extract only focal substantive threads and their full trajectories.
For each thread distinguish introduction, responses, latest material reference, and whether it is open_unaddressed, addressed_unresolved, resolved, superseded, genuinely_dropped, or unclear. Do not force a dropped thread merely because the topic is absent from the final turn. Do not extract positions or constraints in this call.""",
    "constraints": """Extract only atomic load-bearing decision constraints.
Each record must contain one claim with one source-strength mode. Split a stated condition from a possibility, preference, concern, inference, or reported statement even when they appear in the same sentence. Never use a mixed mode or merge claims to save space. Do not extract positions or threads in this call.""",
}


def _source_catalog_prompt(catalog: SourceCatalog) -> str:
    lines = [
        "SOURCE SPAN CATALOG",
        f"source_sha256={catalog.source_sha256}",
        f"message_count={catalog.message_count}",
    ]
    for span in catalog.spans:
        if span.kind != "sentence":
            continue
        lines.append(
            f"[{span.span_id}] turn={span.turn_index} speaker={span.speaker}"
        )
        lines.append(span.text)
    return "\n".join(lines)


def build_micro_contract(
    kind: str, *, catalog: SourceCatalog, provider: str
) -> dict[str, Any]:
    if kind not in _MICRO_JOBS:
        raise ValueError(f"unknown candidate kind: {kind}")
    schema = provider_schema(kind, provider=provider)
    system_prompt = _MICRO_JOBS[kind] + "\n\n" + _COMMON_MICRO_RULES
    user_prompt = (
        _source_catalog_prompt(catalog)
        + "\n\nTYPED OUTPUT SCHEMA\n"
        + json.dumps(schema, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )
    return {
        "kind": kind,
        "provider_projection": provider,
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "system_prompt_sha256": _sha256_text(system_prompt),
        "user_prompt_sha256": _sha256_text(user_prompt),
        "schema": schema,
        "schema_sha256": _sha256_text(
            json.dumps(schema, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        ),
        "schema_metrics": schema_metrics(schema),
        "provider_calls": 0,
    }


def provider_compatibility_report(*, provider: str) -> dict[str, Any]:
    allowed = {
        "$defs",
        "$ref",
        "type",
        "description",
        "enum",
        "items",
        "minItems",
        "maxItems",
        "anyOf",
        "oneOf",
        "properties",
        "additionalProperties",
        "required",
    }

    def keywords(value: Any) -> set[str]:
        found: set[str] = set()
        if not isinstance(value, dict):
            if isinstance(value, list):
                for item in value:
                    found.update(keywords(item))
            return found
        for key, item in value.items():
            if key in {"properties", "$defs"} and isinstance(item, dict):
                found.add(key)
                for child in item.values():
                    found.update(keywords(child))
            else:
                found.add(key)
                found.update(keywords(item))
        return found

    rows: list[dict[str, Any]] = []
    for kind in _MICRO_JOBS:
        schema = provider_schema(kind, provider=provider)
        used = keywords(schema)
        unsupported = sorted(used - allowed)
        metrics = schema_metrics(schema)
        rows.append(
            {
                "kind": kind,
                "schema_sha256": _sha256_text(
                    json.dumps(
                        schema,
                        sort_keys=True,
                        separators=(",", ":"),
                        ensure_ascii=False,
                    )
                ),
                "metrics": metrics,
                "keywords": sorted(used),
                "unsupported_keywords": unsupported,
                "depth_at_most_8": metrics["depth"] <= 8,
                "bytes_at_most_4096": metrics["bytes"] <= 4096,
                "compatible": not unsupported
                and metrics["depth"] <= 8
                and metrics["bytes"] <= 4096,
            }
        )
    return {
        "schema_version": "lolla.conversation_state_provider_compatibility.v1",
        "provider_projection": provider,
        "checked_against_practices_date": "2026-07-11",
        "rows": rows,
        "all_compatible": all(row["compatible"] for row in rows),
        "provider_calls": 0,
        "non_claims": [
            "schema_compatibility_is_not_provider_acceptance_proof",
            "schema_compatibility_is_not_semantic_quality",
            "no_provider_call_was_made",
        ],
    }
