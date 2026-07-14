from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

import pytest

from engine.system_b import conversation_state_fan_in as fan_in


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = (
    ROOT
    / "tests/fixtures/r4_conversation_state_fan_in/contract-fixture-v1.json"
)
CONTRACT_PATH = (
    ROOT / "docs/evals/lolla-r4-conversation-state-fan-in-contract-v1.json"
)


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _fixture_material() -> tuple[
    dict, list[dict], dict[str, dict], dict[str, bytes], bytes, dict
]:
    fixture = _load(FIXTURE_PATH)
    source = fixture["source"]
    source_bytes = source["text"].encode("utf-8")
    registry = fan_in.build_source_registry(
        case_id=source["case_id"],
        source_path=source["path"],
        source_bytes=source_bytes,
        message_count=source["message_count"],
        aliases=source["aliases"],
    )
    readers = fixture["planned_readers"]
    reader_index = {item["reader_id"]: item for item in readers}
    records = {}
    for spec in fixture["record_specs"]:
        reader = reader_index[spec["reader_id"]]
        records[spec["reader_id"]] = fan_in.build_semantic_record(
            source_registry=registry,
            record_id=spec["record_id"],
            surface=reader["surface"],
            semantic_payload=spec["semantic_payload"],
            source_aliases=spec["source_aliases"],
            related_record_ids=spec["related_record_ids"],
        )
    artifacts = {
        f"fixture-artifacts/{reader_id}.json": json.dumps(
            {"reader_id": reader_id}, sort_keys=True
        ).encode("utf-8")
        for reader_id in reader_index
    }
    return registry, readers, records, artifacts, source_bytes, fixture


def _reader_result(
    reader: dict,
    *,
    state: str,
    records: list[dict],
    artifacts: dict[str, bytes],
    issue_code: str | None = None,
    issue_stage: str | None = None,
    safe_detail: str = "",
) -> dict:
    path = f"fixture-artifacts/{reader['reader_id']}.json"
    return fan_in.build_reader_result(
        reader=reader,
        state=state,
        records=records,
        artifact_path=None if state == "missing" else path,
        artifact_bytes=None if state == "missing" else artifacts[path],
        issue_code=issue_code,
        issue_stage=issue_stage,
        safe_detail=safe_detail,
    )


def _complete_fan_in() -> tuple[dict, dict[str, bytes], bytes, dict]:
    registry, readers, records, artifacts, source_bytes, fixture = _fixture_material()
    results = [
        _reader_result(
            reader,
            state="complete",
            records=[records[reader["reader_id"]]],
            artifacts=artifacts,
        )
        for reader in readers
    ]
    value = fan_in.assemble_conversation_state_fan_in(
        source_registry=registry,
        planned_readers=readers,
        reader_results=results,
        source_bytes=source_bytes,
        artifact_bytes_by_path=artifacts,
    )
    return value, artifacts, source_bytes, fixture


def test_contract_constants_and_tagged_union_are_frozen() -> None:
    contract = _load(CONTRACT_PATH)
    schema = fan_in.reader_result_json_schema_v1()

    assert contract["surfaces"] == list(fan_in.SURFACES)
    assert set(contract["state_vocabulary"]) == set(fan_in.STATES)
    assert contract["machine_issue_codes"]["partial"] == list(fan_in.PARTIAL_CODES)
    assert contract["machine_issue_codes"]["failed"] == list(fan_in.FAILURE_CODES)
    assert contract["machine_issue_codes"]["missing"] == list(fan_in.MISSING_CODES)
    assert contract["reader_result_contract"]["json_schema_sha256"] == fan_in._value_sha256(schema)
    assert [variant["properties"]["state"]["const"] for variant in schema["oneOf"]] == list(fan_in.STATES)
    assert all(variant["additionalProperties"] is False for variant in schema["oneOf"])


def test_complete_fixture_preserves_complementary_overlap_and_relationships() -> None:
    value, artifacts, source_bytes, fixture = _complete_fan_in()
    expected = fixture["expected_complete"]

    assert fan_in.validate_conversation_state_fan_in(
        value,
        source_bytes=source_bytes,
        artifact_bytes_by_path=artifacts,
    ) == value
    assert value["status"] == expected["status"]
    assert value["fan_in"]["planned_reader_count"] == expected["planned_reader_count"]
    assert value["fan_in"]["total_record_count"] == expected["total_record_count"]
    assert value["fan_in"]["reader_state_counts"] == expected["reader_state_counts"]
    assert value["fan_in"]["exact_semantic_payload_overlap_pair_count"] == 1
    assert value["fan_in"]["source_alias_overlap_pair_count"] >= 1
    current = next(
        item for item in value["surface_summaries"] if item["surface"] == "current_position"
    )
    assert current["record_ids"] == ["fixture-current-a-01", "fixture-current-b-01"]
    relationship = next(
        result
        for result in value["reader_results"]
        if result["surface"] == "cross_thread_relationship"
    )["records"][0]
    assert relationship["related_record_ids"] == [
        "fixture-current-a-01",
        "fixture-reopen-01",
        "fixture-unresolved-01",
    ]
    assert value["boundary"]["semantic_merge_or_deduplication_performed"] is False
    assert value["boundary"]["quality_score"] is None


def test_all_five_states_remain_distinct_in_one_bounded_handoff() -> None:
    registry, readers, records, artifacts, source_bytes, _fixture = _fixture_material()
    results = []
    for reader in readers:
        reader_id = reader["reader_id"]
        if reader_id in {"starting-reader", "current-reader-a"}:
            result = _reader_result(
                reader,
                state="complete",
                records=[records[reader_id]],
                artifacts=artifacts,
            )
        elif reader_id == "current-reader-b":
            result = _reader_result(
                reader,
                state="partial",
                records=[records[reader_id]],
                artifacts=artifacts,
                issue_code="source_run_incomplete",
                issue_stage="system_join",
                safe_detail="The source run stopped after another reader failed.",
            )
        elif reader_id == "qualification-reader":
            result = _reader_result(
                reader, state="completed_zero", records=[], artifacts=artifacts
            )
        elif reader_id == "unresolved-reader":
            result = _reader_result(
                reader,
                state="failed",
                records=[],
                artifacts=artifacts,
                issue_code="schema_or_custody_failed",
                issue_stage="reader_custody",
            )
        else:
            result = _reader_result(
                reader,
                state="missing",
                records=[],
                artifacts=artifacts,
                issue_code="reader_not_implemented",
                issue_stage="contract_availability",
            )
        results.append(result)

    value = fan_in.assemble_conversation_state_fan_in(
        source_registry=registry,
        planned_readers=readers,
        reader_results=results,
        source_bytes=source_bytes,
        artifact_bytes_by_path=artifacts,
    )

    assert value["status"] == "conversation_state_fan_in_partial"
    assert value["fan_in"]["reader_state_counts"] == {
        "complete": 2,
        "completed_zero": 1,
        "partial": 1,
        "failed": 1,
        "missing": 2,
    }
    qualification = next(
        item for item in value["surface_summaries"] if item["surface"] == "qualification"
    )
    assert qualification["state_counts"]["completed_zero"] == 1
    assert qualification["state_counts"]["missing"] == 0
    assert value["boundary"]["completed_zero_treated_as_semantic_absence"] is False


@pytest.mark.parametrize(
    ("mutation", "error"),
    [
        ("unknown_state", "state is invalid"),
        ("unknown_issue", "issue kind or code is invalid"),
        ("payload_hash", "semantic_payload hash drifted"),
        ("source_locator", "source locator custody drifted"),
        ("relationship_endpoint", "relationship endpoint"),
        ("duplicate_record", "semantic record ID is duplicated"),
        ("reader_surface", "surface drifted from plan"),
    ],
)
def test_adversarial_semantic_and_state_drift_fails_closed(
    mutation: str, error: str
) -> None:
    value, artifacts, source_bytes, _fixture = _complete_fan_in()
    candidate = copy.deepcopy(value)
    results = candidate["reader_results"]
    if mutation == "unknown_state":
        results[0]["state"] = "empty"
    elif mutation == "unknown_issue":
        results[0]["state"] = "partial"
        results[0]["issue"] = {
            "kind": "failure",
            "code": "read_the_prose_and_guess",
            "stage": "fixture",
            "safe_detail": "",
        }
    elif mutation == "payload_hash":
        results[0]["records"][0]["semantic_payload_sha256"] = "0" * 64
    elif mutation == "source_locator":
        results[0]["records"][0]["source_locators"][0]["speaker"] = "assistant"
    elif mutation == "relationship_endpoint":
        relationship = next(
            result for result in results if result["surface"] == "cross_thread_relationship"
        )
        relationship["records"][0]["related_record_ids"][0] = "not-admitted"
        relationship["records"][0]["related_record_ids"].sort()
    elif mutation == "duplicate_record":
        results[1]["records"][0]["record_id"] = results[0]["records"][0]["record_id"]
    elif mutation == "reader_surface":
        results[0]["surface"] = "qualification"
    with pytest.raises(fan_in.ConversationStateFanInError, match=error):
        fan_in.validate_conversation_state_fan_in(
            candidate,
            source_bytes=source_bytes,
            artifact_bytes_by_path=artifacts,
        )


def test_source_and_artifact_bytes_are_verified_when_supplied() -> None:
    value, artifacts, source_bytes, _fixture = _complete_fan_in()

    with pytest.raises(fan_in.ConversationStateFanInError, match="source hash drifted"):
        fan_in.validate_conversation_state_fan_in(
            value,
            source_bytes=source_bytes + b"tamper",
            artifact_bytes_by_path=artifacts,
        )
    drifted_artifacts = dict(artifacts)
    first_path = next(iter(drifted_artifacts))
    drifted_artifacts[first_path] += b"tamper"
    with pytest.raises(fan_in.ConversationStateFanInError, match="artifact custody drifted"):
        fan_in.validate_conversation_state_fan_in(
            value,
            source_bytes=source_bytes,
            artifact_bytes_by_path=drifted_artifacts,
        )


def test_reader_and_payload_bounds_fail_before_fan_in() -> None:
    registry, readers, records, artifacts, _source_bytes, _fixture = _fixture_material()
    reader = readers[0]
    record = records[reader["reader_id"]]
    too_many = [copy.deepcopy(record) for _ in range(fan_in.MAX_RECORDS_PER_READER + 1)]

    with pytest.raises(fan_in.ConversationStateFanInError, match="record count exceeds"):
        _reader_result(
            reader,
            state="complete",
            records=too_many,
            artifacts=artifacts,
        )
    with pytest.raises(fan_in.ConversationStateFanInError, match="payload exceeds"):
        fan_in.build_semantic_record(
            source_registry=registry,
            record_id="oversized",
            surface=reader["surface"],
            semantic_payload={"prose": "x" * fan_in.MAX_SEMANTIC_PAYLOAD_UTF8_BYTES},
            source_aliases=["e003"],
        )


def test_module_has_no_network_provider_sdk_or_environment_path() -> None:
    source = Path(fan_in.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }

    assert imported.isdisjoint(
        {"anthropic", "google", "httpx", "openai", "requests", "urllib"}
    )
    assert "os.environ" not in source
