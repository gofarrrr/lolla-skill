"""Provider-free, missingness-aware conversation-state fan-in.

The fan-in preserves explicit outputs from complementary semantic readers.  It
validates identities, hashes, source locators, state transitions, references,
and bounds.  It deliberately does not interpret semantic payload prose,
resolve reader disagreement, infer roles, or decide whether a record should
activate reasoning pressure.
"""
from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from itertools import combinations
from typing import Any


FAN_IN_SCHEMA = "lolla.conversation_state_fan_in.v1"
SOURCE_REGISTRY_SCHEMA = "lolla.conversation_state_source_registry.v1"
SURFACES = (
    "starting_position",
    "current_position",
    "qualification",
    "unresolved_matter",
    "reopen_condition",
    "cross_thread_relationship",
)
STATES = ("complete", "completed_zero", "partial", "failed", "missing")
FAILURE_CODES = (
    "transport_failed",
    "schema_or_custody_failed",
    "dependency_failed",
    "budget_preflight_failed",
)
PARTIAL_CODES = (
    "some_records_quarantined",
    "source_run_incomplete",
    "dependency_failed",
)
MISSING_CODES = (
    "reader_not_implemented",
    "upstream_dependency_unavailable",
    "reader_not_run",
    "artifact_unavailable",
)

MAX_READERS = 12
MAX_RECORDS_PER_READER = 8
MAX_TOTAL_RECORDS = 48
MAX_SOURCE_ALIASES = 512
MAX_SOURCE_LOCATORS_PER_RECORD = 24
MAX_RELATED_RECORD_IDS = 16
MAX_SEMANTIC_PAYLOAD_UTF8_BYTES = 32_768
MAX_TOTAL_SEMANTIC_PAYLOAD_UTF8_BYTES = 262_144
MAX_HANDOFF_PAYLOAD_UTF8_BYTES = 1_000_000


class ConversationStateFanInError(ValueError):
    """Raised when fan-in custody, state, identity, or bounds drift."""


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _value_sha256(value: Any) -> str:
    return _sha256(_canonical_json_bytes(value))


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ConversationStateFanInError(f"{label} must be an object")
    return value


def _require_exact_fields(
    value: Mapping[str, Any], fields: set[str], label: str
) -> None:
    if set(value) != fields:
        raise ConversationStateFanInError(f"{label} fields do not match contract")


def _require_string(value: Any, label: str, *, maximum: int = 500) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ConversationStateFanInError(f"{label} is invalid")
    return value


def _require_sha256(value: Any, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ConversationStateFanInError(f"{label} is not a lowercase SHA-256")
    return value


def build_source_registry(
    *,
    case_id: str,
    source_path: str,
    source_bytes: bytes,
    message_count: int,
    aliases: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build a source registry from authoritative bytes and explicit locators."""
    _require_string(case_id, "case_id", maximum=180)
    _require_string(source_path, "source_path", maximum=800)
    if not isinstance(source_bytes, bytes):
        raise ConversationStateFanInError("source_bytes must be bytes")
    if not isinstance(message_count, int) or message_count < 1:
        raise ConversationStateFanInError("message_count is invalid")
    if not isinstance(aliases, Sequence) or isinstance(aliases, (str, bytes)):
        raise ConversationStateFanInError("aliases must be an array")
    if not aliases or len(aliases) > MAX_SOURCE_ALIASES:
        raise ConversationStateFanInError("source alias count is outside bounds")

    normalized = []
    alias_ids: set[str] = set()
    span_ids: set[str] = set()
    for index, raw in enumerate(aliases, 1):
        alias = _require_mapping(raw, f"alias[{index}]")
        fields = {"alias", "span_id", "speaker", "turn_index", "text_sha256"}
        _require_exact_fields(alias, fields, f"alias[{index}]")
        alias_id = _require_string(alias["alias"], f"alias[{index}].alias", maximum=80)
        span_id = _require_string(alias["span_id"], f"alias[{index}].span_id", maximum=180)
        speaker = alias["speaker"]
        turn_index = alias["turn_index"]
        if alias_id in alias_ids or span_id in span_ids:
            raise ConversationStateFanInError("source alias or span identity is duplicated")
        if speaker not in {"user", "assistant", "tool", "system"}:
            raise ConversationStateFanInError(f"alias[{index}].speaker is invalid")
        if not isinstance(turn_index, int) or not 1 <= turn_index <= message_count:
            raise ConversationStateFanInError(f"alias[{index}].turn_index is invalid")
        text_sha256 = _require_sha256(
            alias["text_sha256"], f"alias[{index}].text_sha256"
        )
        alias_ids.add(alias_id)
        span_ids.add(span_id)
        normalized.append(
            {
                "alias": alias_id,
                "span_id": span_id,
                "speaker": speaker,
                "turn_index": turn_index,
                "text_sha256": text_sha256,
            }
        )

    body = {
        "schema_version": SOURCE_REGISTRY_SCHEMA,
        "case_id": case_id,
        "source_path": source_path,
        "source_sha256": _sha256(source_bytes),
        "source_utf8_bytes": len(source_bytes),
        "message_count": message_count,
        "aliases": sorted(normalized, key=lambda item: item["alias"]),
    }
    return {**body, "registry_sha256": _value_sha256(body)}


def _validate_source_registry(
    value: Mapping[str, Any], *, source_bytes: bytes | None = None
) -> None:
    fields = {
        "schema_version",
        "case_id",
        "source_path",
        "source_sha256",
        "source_utf8_bytes",
        "message_count",
        "aliases",
        "registry_sha256",
    }
    _require_exact_fields(value, fields, "source_registry")
    if value.get("schema_version") != SOURCE_REGISTRY_SCHEMA:
        raise ConversationStateFanInError("source registry schema is invalid")
    body = {key: copy.deepcopy(item) for key, item in value.items() if key != "registry_sha256"}
    if value.get("registry_sha256") != _value_sha256(body):
        raise ConversationStateFanInError("source registry self-hash drifted")
    _require_string(value.get("case_id"), "source_registry.case_id", maximum=180)
    _require_string(value.get("source_path"), "source_registry.source_path", maximum=800)
    _require_sha256(value.get("source_sha256"), "source_registry.source_sha256")
    if not isinstance(value.get("source_utf8_bytes"), int) or value["source_utf8_bytes"] < 1:
        raise ConversationStateFanInError("source registry byte count is invalid")
    if not isinstance(value.get("message_count"), int) or value["message_count"] < 1:
        raise ConversationStateFanInError("source registry message count is invalid")
    aliases = value.get("aliases")
    if not isinstance(aliases, list) or not aliases or len(aliases) > MAX_SOURCE_ALIASES:
        raise ConversationStateFanInError("source registry aliases are invalid")
    rebuilt = build_source_registry(
        case_id=value["case_id"],
        source_path=value["source_path"],
        source_bytes=(
            source_bytes
            if source_bytes is not None
            else b"source bytes unavailable for registry-only validation"
        ),
        message_count=value["message_count"],
        aliases=aliases,
    )
    if source_bytes is not None:
        if rebuilt["source_sha256"] != value["source_sha256"]:
            raise ConversationStateFanInError("authoritative source hash drifted")
        if rebuilt["source_utf8_bytes"] != value["source_utf8_bytes"]:
            raise ConversationStateFanInError("authoritative source byte count drifted")
    if rebuilt["aliases"] != aliases:
        raise ConversationStateFanInError("source alias registry is not canonical")


def planned_reader(
    *, reader_id: str, surface: str, producer_kind: str, producer_id: str
) -> dict[str, str]:
    if surface not in SURFACES:
        raise ConversationStateFanInError("planned reader surface is invalid")
    return {
        "reader_id": _require_string(reader_id, "reader_id", maximum=180),
        "surface": surface,
        "producer_kind": _require_string(
            producer_kind, "producer_kind", maximum=180
        ),
        "producer_id": _require_string(producer_id, "producer_id", maximum=300),
    }


def build_semantic_record(
    *,
    source_registry: Mapping[str, Any],
    record_id: str,
    surface: str,
    semantic_payload: Mapping[str, Any],
    source_aliases: Sequence[str],
    related_record_ids: Sequence[str] = (),
) -> dict[str, Any]:
    """Wrap one provider-authored semantic payload without interpreting it."""
    _validate_source_registry(source_registry)
    _require_string(record_id, "record_id", maximum=180)
    if surface not in SURFACES:
        raise ConversationStateFanInError("semantic record surface is invalid")
    payload = _require_mapping(semantic_payload, "semantic_payload")
    payload_bytes = _canonical_json_bytes(payload)
    if not payload_bytes or len(payload_bytes) > MAX_SEMANTIC_PAYLOAD_UTF8_BYTES:
        raise ConversationStateFanInError("semantic payload exceeds its byte bound")
    if (
        not isinstance(source_aliases, Sequence)
        or isinstance(source_aliases, (str, bytes))
        or not source_aliases
        or len(source_aliases) > MAX_SOURCE_LOCATORS_PER_RECORD
        or len(source_aliases) != len(set(source_aliases))
    ):
        raise ConversationStateFanInError("semantic record source aliases are invalid")
    alias_index = {item["alias"]: item for item in source_registry["aliases"]}
    unknown = set(source_aliases) - set(alias_index)
    if unknown:
        raise ConversationStateFanInError("semantic record contains unknown source aliases")
    if (
        not isinstance(related_record_ids, Sequence)
        or isinstance(related_record_ids, (str, bytes))
        or len(related_record_ids) > MAX_RELATED_RECORD_IDS
        or len(related_record_ids) != len(set(related_record_ids))
        or any(not isinstance(item, str) or not item for item in related_record_ids)
    ):
        raise ConversationStateFanInError("related record IDs are invalid")
    if surface == "cross_thread_relationship" and len(related_record_ids) < 2:
        raise ConversationStateFanInError(
            "relationship records require at least two explicit record IDs"
        )
    if surface != "cross_thread_relationship" and related_record_ids:
        raise ConversationStateFanInError(
            "only relationship records may carry related record IDs"
        )
    return {
        "record_id": record_id,
        "surface": surface,
        "semantic_payload": copy.deepcopy(dict(payload)),
        "semantic_payload_sha256": _sha256(payload_bytes),
        "source_locators": [copy.deepcopy(alias_index[item]) for item in sorted(source_aliases)],
        "related_record_ids": sorted(related_record_ids),
    }


def _artifact_descriptor(path: str, raw: bytes) -> dict[str, Any]:
    _require_string(path, "artifact.path", maximum=800)
    if not isinstance(raw, bytes):
        raise ConversationStateFanInError("artifact bytes must be bytes")
    return {"path": path, "sha256": _sha256(raw), "utf8_bytes": len(raw)}


def build_reader_result(
    *,
    reader: Mapping[str, Any],
    state: str,
    records: Sequence[Mapping[str, Any]],
    artifact_path: str | None = None,
    artifact_bytes: bytes | None = None,
    issue_code: str | None = None,
    issue_stage: str | None = None,
    safe_detail: str = "",
) -> dict[str, Any]:
    """Build one explicit tagged reader result.

    ``completed_zero`` means only that the reader completed and returned zero
    records.  It never means the underlying semantic matter is absent.
    """
    normalized_reader = planned_reader(
        reader_id=str(reader.get("reader_id", "")),
        surface=str(reader.get("surface", "")),
        producer_kind=str(reader.get("producer_kind", "")),
        producer_id=str(reader.get("producer_id", "")),
    )
    if state not in STATES:
        raise ConversationStateFanInError("reader state is invalid")
    if not isinstance(records, Sequence) or isinstance(records, (str, bytes)):
        raise ConversationStateFanInError("reader records must be an array")
    if len(records) > MAX_RECORDS_PER_READER:
        raise ConversationStateFanInError("reader record count exceeds bound")
    copied_records = [copy.deepcopy(dict(_require_mapping(item, "reader record"))) for item in records]
    if state in {"complete", "partial"} and not copied_records:
        raise ConversationStateFanInError(f"{state} reader result requires records")
    if state in {"completed_zero", "failed", "missing"} and copied_records:
        raise ConversationStateFanInError(f"{state} reader result must have zero records")
    artifact = None
    if state == "missing":
        if artifact_path is not None or artifact_bytes is not None:
            raise ConversationStateFanInError("missing reader result cannot carry an artifact")
    else:
        if artifact_path is None or artifact_bytes is None:
            raise ConversationStateFanInError("non-missing reader result requires an artifact")
        artifact = _artifact_descriptor(artifact_path, artifact_bytes)
    issue = None
    if state in {"partial", "failed", "missing"}:
        allowed_codes = (
            PARTIAL_CODES if state == "partial"
            else FAILURE_CODES if state == "failed"
            else MISSING_CODES
        )
        if issue_code not in allowed_codes:
            raise ConversationStateFanInError(f"{state} issue code is invalid")
        stage = _require_string(issue_stage, f"{state} issue stage", maximum=180)
        if not isinstance(safe_detail, str) or len(safe_detail) > 1000:
            raise ConversationStateFanInError("safe issue detail is invalid")
        issue = {
            "kind": "missingness" if state == "missing" else "failure",
            "code": issue_code,
            "stage": stage,
            "safe_detail": safe_detail,
        }
    elif issue_code is not None or issue_stage is not None or safe_detail:
        raise ConversationStateFanInError("successful reader state cannot carry an issue")
    return {
        "reader_id": normalized_reader["reader_id"],
        "surface": normalized_reader["surface"],
        "state": state,
        "producer": {
            "kind": normalized_reader["producer_kind"],
            "id": normalized_reader["producer_id"],
        },
        "artifact": artifact,
        "declared_record_count": len(copied_records),
        "records": copied_records,
        "issue": issue,
    }


def _validate_planned_readers(readers: Any) -> list[dict[str, str]]:
    if not isinstance(readers, list) or not readers or len(readers) > MAX_READERS:
        raise ConversationStateFanInError("planned reader count is outside bounds")
    normalized = []
    seen: set[str] = set()
    for index, raw in enumerate(readers, 1):
        reader = _require_mapping(raw, f"planned_reader[{index}]")
        _require_exact_fields(
            reader,
            {"reader_id", "surface", "producer_kind", "producer_id"},
            f"planned_reader[{index}]",
        )
        item = planned_reader(**dict(reader))
        if item["reader_id"] in seen:
            raise ConversationStateFanInError("planned reader ID is duplicated")
        seen.add(item["reader_id"])
        normalized.append(item)
    if {item["surface"] for item in normalized} != set(SURFACES):
        raise ConversationStateFanInError("every conversation-state surface needs a planned reader")
    if normalized != sorted(normalized, key=lambda item: item["reader_id"]):
        raise ConversationStateFanInError("planned readers are not in canonical ID order")
    return normalized


def _validate_artifact(
    artifact: Any,
    *,
    label: str,
    artifact_bytes_by_path: Mapping[str, bytes] | None,
) -> None:
    value = _require_mapping(artifact, label)
    _require_exact_fields(value, {"path", "sha256", "utf8_bytes"}, label)
    path = _require_string(value.get("path"), f"{label}.path", maximum=800)
    _require_sha256(value.get("sha256"), f"{label}.sha256")
    if not isinstance(value.get("utf8_bytes"), int) or value["utf8_bytes"] < 1:
        raise ConversationStateFanInError(f"{label}.utf8_bytes is invalid")
    if artifact_bytes_by_path is not None:
        raw = artifact_bytes_by_path.get(path)
        if raw is None:
            raise ConversationStateFanInError(f"artifact bytes unavailable for {path}")
        if _sha256(raw) != value["sha256"] or len(raw) != value["utf8_bytes"]:
            raise ConversationStateFanInError(f"artifact custody drifted for {path}")


def _validate_record(
    record: Any,
    *,
    expected_surface: str,
    alias_index: Mapping[str, Mapping[str, Any]],
    label: str,
) -> None:
    value = _require_mapping(record, label)
    fields = {
        "record_id",
        "surface",
        "semantic_payload",
        "semantic_payload_sha256",
        "source_locators",
        "related_record_ids",
    }
    _require_exact_fields(value, fields, label)
    _require_string(value.get("record_id"), f"{label}.record_id", maximum=180)
    if value.get("surface") != expected_surface:
        raise ConversationStateFanInError(f"{label}.surface does not match its reader")
    payload = _require_mapping(value.get("semantic_payload"), f"{label}.semantic_payload")
    payload_bytes = _canonical_json_bytes(payload)
    if not payload_bytes or len(payload_bytes) > MAX_SEMANTIC_PAYLOAD_UTF8_BYTES:
        raise ConversationStateFanInError(f"{label}.semantic_payload exceeds bound")
    if value.get("semantic_payload_sha256") != _sha256(payload_bytes):
        raise ConversationStateFanInError(f"{label}.semantic_payload hash drifted")
    locators = value.get("source_locators")
    if (
        not isinstance(locators, list)
        or not locators
        or len(locators) > MAX_SOURCE_LOCATORS_PER_RECORD
    ):
        raise ConversationStateFanInError(f"{label}.source_locators are invalid")
    locator_aliases = []
    for locator_index, locator in enumerate(locators, 1):
        row = _require_mapping(locator, f"{label}.source_locator[{locator_index}]")
        alias = row.get("alias")
        if alias not in alias_index or dict(row) != dict(alias_index[alias]):
            raise ConversationStateFanInError(f"{label} source locator custody drifted")
        locator_aliases.append(alias)
    if locator_aliases != sorted(locator_aliases) or len(locator_aliases) != len(set(locator_aliases)):
        raise ConversationStateFanInError(f"{label} source locators are not canonical and unique")
    related = value.get("related_record_ids")
    if (
        not isinstance(related, list)
        or len(related) > MAX_RELATED_RECORD_IDS
        or related != sorted(related)
        or len(related) != len(set(related))
        or any(not isinstance(item, str) or not item for item in related)
    ):
        raise ConversationStateFanInError(f"{label}.related_record_ids are invalid")
    if expected_surface == "cross_thread_relationship" and len(related) < 2:
        raise ConversationStateFanInError(f"{label} relationship has fewer than two endpoints")
    if expected_surface != "cross_thread_relationship" and related:
        raise ConversationStateFanInError(f"{label} non-relationship carries endpoints")


def _validate_reader_results(
    results: Any,
    *,
    readers: Sequence[Mapping[str, Any]],
    source_registry: Mapping[str, Any],
    artifact_bytes_by_path: Mapping[str, bytes] | None,
) -> list[dict[str, Any]]:
    if not isinstance(results, list) or len(results) != len(readers):
        raise ConversationStateFanInError("reader results must cover every planned reader exactly once")
    reader_index = {item["reader_id"]: item for item in readers}
    alias_index = {item["alias"]: item for item in source_registry["aliases"]}
    seen: set[str] = set()
    record_ids: set[str] = set()
    normalized = []
    for index, raw in enumerate(results, 1):
        result = _require_mapping(raw, f"reader_result[{index}]")
        fields = {
            "reader_id",
            "surface",
            "state",
            "producer",
            "artifact",
            "declared_record_count",
            "records",
            "issue",
        }
        _require_exact_fields(result, fields, f"reader_result[{index}]")
        reader_id = result.get("reader_id")
        if reader_id not in reader_index or reader_id in seen:
            raise ConversationStateFanInError("reader result identity is unknown or duplicated")
        seen.add(reader_id)
        planned = reader_index[reader_id]
        if result.get("surface") != planned["surface"]:
            raise ConversationStateFanInError("reader result surface drifted from plan")
        producer = _require_mapping(result.get("producer"), "reader result producer")
        _require_exact_fields(producer, {"kind", "id"}, "reader result producer")
        if producer != {"kind": planned["producer_kind"], "id": planned["producer_id"]}:
            raise ConversationStateFanInError("reader result producer drifted from plan")
        state = result.get("state")
        if state not in STATES:
            raise ConversationStateFanInError("reader result state is invalid")
        records = result.get("records")
        if not isinstance(records, list) or len(records) > MAX_RECORDS_PER_READER:
            raise ConversationStateFanInError("reader result records are invalid")
        if result.get("declared_record_count") != len(records):
            raise ConversationStateFanInError("declared reader record count drifted")
        if state in {"complete", "partial"} and not records:
            raise ConversationStateFanInError(f"{state} reader result requires records")
        if state in {"completed_zero", "failed", "missing"} and records:
            raise ConversationStateFanInError(f"{state} reader result must be empty")
        if state == "missing":
            if result.get("artifact") is not None:
                raise ConversationStateFanInError("missing reader result cannot carry an artifact")
        else:
            _validate_artifact(
                result.get("artifact"),
                label=f"reader_result[{index}].artifact",
                artifact_bytes_by_path=artifact_bytes_by_path,
            )
        issue = result.get("issue")
        if state in {"complete", "completed_zero"}:
            if issue is not None:
                raise ConversationStateFanInError("successful reader result cannot carry an issue")
        else:
            issue_value = _require_mapping(issue, f"reader_result[{index}].issue")
            _require_exact_fields(
                issue_value,
                {"kind", "code", "stage", "safe_detail"},
                f"reader_result[{index}].issue",
            )
            expected_kind = "missingness" if state == "missing" else "failure"
            allowed_codes = (
                MISSING_CODES if state == "missing"
                else PARTIAL_CODES if state == "partial"
                else FAILURE_CODES
            )
            if issue_value.get("kind") != expected_kind or issue_value.get("code") not in allowed_codes:
                raise ConversationStateFanInError("reader issue kind or code is invalid")
            _require_string(issue_value.get("stage"), "reader issue stage", maximum=180)
            detail = issue_value.get("safe_detail")
            if not isinstance(detail, str) or len(detail) > 1000:
                raise ConversationStateFanInError("reader safe issue detail is invalid")
        for record_index, record in enumerate(records, 1):
            _validate_record(
                record,
                expected_surface=planned["surface"],
                alias_index=alias_index,
                label=f"reader_result[{index}].record[{record_index}]",
            )
            record_id = record["record_id"]
            if record_id in record_ids:
                raise ConversationStateFanInError("semantic record ID is duplicated")
            record_ids.add(record_id)
        normalized.append(copy.deepcopy(dict(result)))
    if seen != set(reader_index):
        raise ConversationStateFanInError("reader result coverage is incomplete")
    if normalized != sorted(normalized, key=lambda item: item["reader_id"]):
        raise ConversationStateFanInError("reader results are not in canonical ID order")

    non_relationship_ids = {
        record["record_id"]
        for result in normalized
        if result["surface"] != "cross_thread_relationship"
        for record in result["records"]
    }
    for result in normalized:
        if result["surface"] == "cross_thread_relationship":
            for record in result["records"]:
                if not set(record["related_record_ids"]).issubset(non_relationship_ids):
                    raise ConversationStateFanInError("relationship endpoint is not an admitted semantic record")
    return normalized


def _pair_overlap_count(record_sets: Sequence[set[str]]) -> int:
    return sum(bool(left & right) for left, right in combinations(record_sets, 2))


def _assemble_body(
    *,
    source_registry: Mapping[str, Any],
    planned_readers: Sequence[Mapping[str, Any]],
    reader_results: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    all_records = [record for result in reader_results for record in result["records"]]
    state_counts = Counter(result["state"] for result in reader_results)
    surface_summaries = []
    for surface in SURFACES:
        selected = [result for result in reader_results if result["surface"] == surface]
        records = [record for result in selected for record in result["records"]]
        surface_summaries.append(
            {
                "surface": surface,
                "reader_ids": sorted(result["reader_id"] for result in selected),
                "state_counts": {
                    state: sum(result["state"] == state for result in selected)
                    for state in STATES
                },
                "record_ids": sorted(record["record_id"] for record in records),
                "record_count": len(records),
            }
        )
    payload_hashes = [record["semantic_payload_sha256"] for record in all_records]
    locator_sets = [
        {locator["alias"] for locator in record["source_locators"]}
        for record in all_records
    ]
    total_payload_bytes = sum(
        len(_canonical_json_bytes(record["semantic_payload"])) for record in all_records
    )
    handoff_payload = {
        "source_registry": source_registry,
        "planned_readers": planned_readers,
        "reader_results": reader_results,
        "surface_summaries": surface_summaries,
    }
    handoff_bytes = len(_canonical_json_bytes(handoff_payload))
    artifact_index = {
        (result["artifact"]["path"], result["artifact"]["sha256"]): result["artifact"]
        for result in reader_results
        if result["artifact"] is not None
    }
    within_bounds = (
        len(planned_readers) <= MAX_READERS
        and len(all_records) <= MAX_TOTAL_RECORDS
        and total_payload_bytes <= MAX_TOTAL_SEMANTIC_PAYLOAD_UTF8_BYTES
        and handoff_bytes <= MAX_HANDOFF_PAYLOAD_UTF8_BYTES
    )
    if not within_bounds:
        raise ConversationStateFanInError("assembled fan-in exceeds frozen bounds")
    if all(result["state"] in {"complete", "completed_zero"} for result in reader_results):
        status = "conversation_state_fan_in_complete"
    elif all_records:
        status = "conversation_state_fan_in_partial"
    else:
        status = "conversation_state_fan_in_unavailable"
    return {
        "schema_version": FAN_IN_SCHEMA,
        "status": status,
        "case_id": source_registry["case_id"],
        "source_registry": copy.deepcopy(dict(source_registry)),
        "planned_readers": copy.deepcopy(list(planned_readers)),
        "reader_results": copy.deepcopy(list(reader_results)),
        "surface_summaries": surface_summaries,
        "fan_in": {
            "planned_reader_count": len(planned_readers),
            "reader_state_counts": {state: state_counts[state] for state in STATES},
            "total_record_count": len(all_records),
            "total_source_locator_count": sum(len(record["source_locators"]) for record in all_records),
            "unique_source_alias_count": len(set().union(*locator_sets)) if locator_sets else 0,
            "total_semantic_payload_utf8_bytes": total_payload_bytes,
            "reader_artifact_reference_count": sum(result["artifact"] is not None for result in reader_results),
            "unique_reader_artifact_count": len(artifact_index),
            "unique_reader_artifact_utf8_bytes": sum(item["utf8_bytes"] for item in artifact_index.values()),
            "exact_semantic_payload_overlap_pair_count": sum(
                count * (count - 1) // 2 for count in Counter(payload_hashes).values()
            ),
            "source_alias_overlap_pair_count": _pair_overlap_count(locator_sets),
            "handoff_payload_utf8_bytes": handoff_bytes,
            "limits": {
                "maximum_readers": MAX_READERS,
                "maximum_records_per_reader": MAX_RECORDS_PER_READER,
                "maximum_total_records": MAX_TOTAL_RECORDS,
                "maximum_source_aliases": MAX_SOURCE_ALIASES,
                "maximum_source_locators_per_record": MAX_SOURCE_LOCATORS_PER_RECORD,
                "maximum_related_record_ids": MAX_RELATED_RECORD_IDS,
                "maximum_semantic_payload_utf8_bytes_per_record": MAX_SEMANTIC_PAYLOAD_UTF8_BYTES,
                "maximum_total_semantic_payload_utf8_bytes": MAX_TOTAL_SEMANTIC_PAYLOAD_UTF8_BYTES,
                "maximum_handoff_payload_utf8_bytes": MAX_HANDOFF_PAYLOAD_UTF8_BYTES,
            },
            "within_bounds": True,
            "interpretation": "mechanical load vector only; no direction of quality is inferred",
        },
        "boundary": {
            "provider_calls": 0,
            "runtime_or_graph_integration_performed": False,
            "provider_authored_semantic_payloads_preserved": True,
            "overlapping_reader_records_preserved": True,
            "semantic_role_inferred_by_code": False,
            "semantic_merge_or_deduplication_performed": False,
            "prose_keywords_or_chronology_used_for_meaning": False,
            "reader_or_record_array_order_used_for_meaning": False,
            "missing_reader_output_filled": False,
            "completed_zero_treated_as_semantic_absence": False,
            "relationship_meaning_inferred_by_code": False,
            "graph_pressure_or_relevance_decided": False,
            "quality_score": None,
        },
    }


def assemble_conversation_state_fan_in(
    *,
    source_registry: Mapping[str, Any],
    planned_readers: Sequence[Mapping[str, Any]],
    reader_results: Sequence[Mapping[str, Any]],
    source_bytes: bytes | None = None,
    artifact_bytes_by_path: Mapping[str, bytes] | None = None,
) -> dict[str, Any]:
    """Validate and assemble a canonical, bounded conversation-state handoff."""
    source = _require_mapping(source_registry, "source_registry")
    _validate_source_registry(source, source_bytes=source_bytes)
    readers = _validate_planned_readers(list(planned_readers))
    results = _validate_reader_results(
        list(reader_results),
        readers=readers,
        source_registry=source,
        artifact_bytes_by_path=artifact_bytes_by_path,
    )
    body = _assemble_body(
        source_registry=source,
        planned_readers=readers,
        reader_results=results,
    )
    return {**body, "result_sha256": _value_sha256(body)}


def validate_conversation_state_fan_in(
    value: Mapping[str, Any],
    *,
    source_bytes: bytes | None = None,
    artifact_bytes_by_path: Mapping[str, bytes] | None = None,
) -> dict[str, Any]:
    """Reproduce a complete fan-in value and fail closed on any drift."""
    candidate = _require_mapping(value, "fan_in")
    fields = {
        "schema_version",
        "status",
        "case_id",
        "source_registry",
        "planned_readers",
        "reader_results",
        "surface_summaries",
        "fan_in",
        "boundary",
        "result_sha256",
    }
    _require_exact_fields(candidate, fields, "fan_in")
    if candidate.get("schema_version") != FAN_IN_SCHEMA:
        raise ConversationStateFanInError("fan-in schema is invalid")
    rebuilt = assemble_conversation_state_fan_in(
        source_registry=_require_mapping(candidate.get("source_registry"), "source_registry"),
        planned_readers=candidate.get("planned_readers", []),
        reader_results=candidate.get("reader_results", []),
        source_bytes=source_bytes,
        artifact_bytes_by_path=artifact_bytes_by_path,
    )
    if dict(candidate) != rebuilt:
        raise ConversationStateFanInError("fan-in replay drifted")
    return rebuilt


def reader_result_json_schema_v1() -> dict[str, Any]:
    """Return the strict tagged-union schema documented by the contract."""
    artifact = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "minLength": 1, "maxLength": 800},
            "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            "utf8_bytes": {"type": "integer", "minimum": 1},
        },
        "required": ["path", "sha256", "utf8_bytes"],
        "additionalProperties": False,
    }
    record = {
        "type": "object",
        "properties": {
            "record_id": {"type": "string", "minLength": 1, "maxLength": 180},
            "surface": {"type": "string", "enum": list(SURFACES)},
            "semantic_payload": {"type": "object"},
            "semantic_payload_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            "source_locators": {"type": "array", "minItems": 1, "maxItems": MAX_SOURCE_LOCATORS_PER_RECORD},
            "related_record_ids": {"type": "array", "maxItems": MAX_RELATED_RECORD_IDS, "items": {"type": "string"}},
        },
        "required": [
            "record_id",
            "surface",
            "semantic_payload",
            "semantic_payload_sha256",
            "source_locators",
            "related_record_ids",
        ],
        "additionalProperties": False,
    }
    common_properties = {
        "reader_id": {"type": "string", "minLength": 1, "maxLength": 180},
        "surface": {"type": "string", "enum": list(SURFACES)},
        "producer": {
            "type": "object",
            "properties": {"kind": {"type": "string"}, "id": {"type": "string"}},
            "required": ["kind", "id"],
            "additionalProperties": False,
        },
        "declared_record_count": {"type": "integer", "minimum": 0, "maximum": MAX_RECORDS_PER_READER},
    }
    required = [
        "reader_id",
        "surface",
        "state",
        "producer",
        "artifact",
        "declared_record_count",
        "records",
        "issue",
    ]

    def variant(state: str) -> dict[str, Any]:
        properties = copy.deepcopy(common_properties)
        properties["state"] = {"const": state}
        properties["records"] = {
            "type": "array",
            "minItems": 1 if state in {"complete", "partial"} else 0,
            "maxItems": MAX_RECORDS_PER_READER if state in {"complete", "partial"} else 0,
            "items": record,
        }
        properties["artifact"] = {"type": "null"} if state == "missing" else artifact
        if state in {"complete", "completed_zero"}:
            properties["issue"] = {"type": "null"}
        else:
            properties["issue"] = {
                "type": "object",
                "properties": {
                    "kind": {"const": "missingness" if state == "missing" else "failure"},
                    "code": {
                        "type": "string",
                        "enum": list(
                            MISSING_CODES if state == "missing"
                            else PARTIAL_CODES if state == "partial"
                            else FAILURE_CODES
                        ),
                    },
                    "stage": {"type": "string", "minLength": 1, "maxLength": 180},
                    "safe_detail": {"type": "string", "maxLength": 1000},
                },
                "required": ["kind", "code", "stage", "safe_detail"],
                "additionalProperties": False,
            }
        return {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        }

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Lolla conversation-state reader result v1",
        "oneOf": [variant(state) for state in STATES],
    }
