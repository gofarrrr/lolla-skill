from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from engine.system_b.decision_work_offline_interpretation_queue import (
    QUEUE_ITEM_SCHEMA_VERSION,
    DecisionWorkOfflineInterpretationQueueError,
    build_decision_work_offline_interpretation_queue_item,
    render_decision_work_offline_interpretation_queue_item_json,
    validate_output_path,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-offline-interpretation-queue-contract-v0.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-offline-interpretation-queue-builder-v0.md"
)
PR179_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-offline-interpretation-queue-contract-v0.md"
)
PR178_PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md"
)
README_PATH = REPO_ROOT / "README.md"
HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"
SCRIPT_PATH = (
    REPO_ROOT / "scripts/evals/build_decision_work_offline_interpretation_queue.py"
)

SOURCE_PACKET_SCHEMA_VERSION = (
    "lolla.decision_work_conversation_interpretation_packets.v0"
)
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "queue_metadata",
    "queue_mode",
    "source_run_ref",
    "source_packet_ref",
    "allowed_source_refs",
    "requested_interpretation_fields",
    "privacy_mode",
    "custody_flags",
    "queue_status",
    "blocked_or_deferred_reasons",
    "output_destinations",
    "validation_requirements",
    "downstream_refs",
    "known_limits",
    "semantic_fields_filled",
    "non_claims",
}
REQUIRED_FALSE_FLAGS = {
    "runtime_invoked",
    "skill_invoked",
    "archive_mutated",
    "human_validated",
    "product_proof",
    "answer_quality_scored",
    "agent_action_authorized",
    "automatic_action_authorized",
    "raw_private_content_included",
    "provider_text_included",
    "private_ledgers_included",
    "raw_transcript_included",
    "raw_revised_answer_included",
    "raw_memo_included",
    "local_absolute_paths_included",
    "semantic_fields_filled",
    "queue_runner_invoked",
}
FORBIDDEN_STRINGS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _run_dir(tmp_path: Path) -> Path:
    run_dir = tmp_path / "runs" / "launch-beta" / "20260703T000000Z"
    run_dir.mkdir(parents=True)
    return run_dir


def _source_packet(path: Path, *, schema: str = SOURCE_PACKET_SCHEMA_VERSION) -> Path:
    _write_json(
        path,
        {
            "schema_version": schema,
            "packet_metadata": {
                "case_id": "launch-beta",
                "run_id": "20260703T000000Z",
            },
            "source_inventory": [
                {
                    "input_id": "agent_result",
                    "artifact": "agent_result.json",
                    "content_included": False,
                },
                {
                    "input_id": "result",
                    "artifact": "result.json",
                    "content_included": False,
                },
            ],
            "future_interpretation_tasks": [
                {
                    "field_name": "decision_question",
                    "semantic_field_filled": False,
                }
            ],
            "custody_flags": {"model_calls": 0},
            "non_claims": ["packet_is_not_interpretation"],
        },
    )
    return path


def _assert_conservative(item: dict[str, Any]) -> None:
    assert item["schema_version"] == QUEUE_ITEM_SCHEMA_VERSION
    assert REQUIRED_TOP_LEVEL <= set(item)
    assert item["semantic_fields_filled"] is False
    assert item["custody_flags"]["model_calls"] == 0
    for field in REQUIRED_FALSE_FLAGS:
        assert item["custody_flags"][field] is False
    for requested in item["requested_interpretation_fields"]:
        assert requested["semantic_field_filled"] is False
        assert requested["value"] is None
        assert requested["interpretation_status"] == "requested_not_filled"
        assert requested["must_not_be_used_as_quality_label"] is True
    assert "queue_item_does_not_call_models" in item["non_claims"]
    assert "queue_item_does_not_authorize_agent_action" in item["non_claims"]


def test_queue_item_queues_valid_source_packet(tmp_path: Path) -> None:
    packet_path = _source_packet(tmp_path / "source_packet.json")
    item = build_decision_work_offline_interpretation_queue_item(
        run_dir=_run_dir(tmp_path),
        contract_path=CONTRACT_PATH,
        source_packet_path=packet_path,
        created_at="2026-07-03T00:00:00Z",
    )

    _assert_conservative(item)
    assert item["queue_status"] == "queued"
    assert item["source_packet_ref"]["status"] == "available"
    assert item["source_packet_ref"]["schema_version"] == SOURCE_PACKET_SCHEMA_VERSION
    assert {ref["ref"] for ref in item["allowed_source_refs"]} >= {
        "source_packet.json",
        "agent_result.json",
        "result.json",
    }
    assert item["output_destinations"]["output_status"] == "not_created"
    assert item["downstream_refs"]["downstream_outputs_created"] is False


def test_missing_source_packet_blocks_without_filling_semantics(tmp_path: Path) -> None:
    item = build_decision_work_offline_interpretation_queue_item(
        run_dir=_run_dir(tmp_path),
        contract_path=CONTRACT_PATH,
        created_at="2026-07-03T00:00:00Z",
    )

    _assert_conservative(item)
    assert item["queue_status"] == "blocked_missing_packet"
    assert item["source_packet_ref"]["status"] == "missing"
    assert "missing_source_packet" in item["blocked_or_deferred_reasons"]


def test_disabled_mode_returns_not_requested(tmp_path: Path) -> None:
    item = build_decision_work_offline_interpretation_queue_item(
        run_dir=_run_dir(tmp_path),
        contract_path=CONTRACT_PATH,
        mode="disabled",
        created_at="2026-07-03T00:00:00Z",
    )

    _assert_conservative(item)
    assert item["queue_status"] == "not_requested"
    assert item["queue_mode"] == "disabled"


def test_local_private_operator_mode_records_operator_requirement(
    tmp_path: Path,
) -> None:
    packet_path = _source_packet(tmp_path / "source_packet.json")
    item = build_decision_work_offline_interpretation_queue_item(
        run_dir=_run_dir(tmp_path),
        contract_path=CONTRACT_PATH,
        source_packet_path=packet_path,
        mode="local_private_operator",
        created_at="2026-07-03T00:00:00Z",
    )

    _assert_conservative(item)
    assert item["queue_status"] == "requires_local_private_operator"
    assert item["privacy_mode"] == "local_private_metadata_only"
    assert item["custody_flags"]["checked_in_safe"] is False


def test_local_private_operator_mode_without_packet_records_operator_requirement(
    tmp_path: Path,
) -> None:
    item = build_decision_work_offline_interpretation_queue_item(
        run_dir=_run_dir(tmp_path),
        contract_path=CONTRACT_PATH,
        mode="local_private_operator",
        created_at="2026-07-03T00:00:00Z",
    )

    _assert_conservative(item)
    assert item["queue_status"] == "requires_local_private_operator"
    assert item["source_packet_ref"]["status"] == "missing"
    assert item["privacy_mode"] == "local_private_metadata_only"
    assert item["custody_flags"]["checked_in_safe"] is False


def test_missing_validation_requirements_fail_with_sanitized_error(
    tmp_path: Path,
) -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    contract.pop("validation_requirements")
    contract_path = tmp_path / "contract.json"
    _write_json(contract_path, contract)

    with pytest.raises(
        DecisionWorkOfflineInterpretationQueueError,
        match="validation requirements",
    ):
        build_decision_work_offline_interpretation_queue_item(
            run_dir=_run_dir(tmp_path),
            contract_path=contract_path,
            created_at="2026-07-03T00:00:00Z",
        )


def test_privacy_marker_source_packet_blocks(tmp_path: Path) -> None:
    packet_path = tmp_path / "source_packet.json"
    packet_path.write_text("contains " + "api" + "_key marker", encoding="utf-8")

    item = build_decision_work_offline_interpretation_queue_item(
        run_dir=_run_dir(tmp_path),
        contract_path=CONTRACT_PATH,
        source_packet_path=packet_path,
        created_at="2026-07-03T00:00:00Z",
    )

    _assert_conservative(item)
    assert item["queue_status"] == "blocked_privacy_risk"
    assert item["source_packet_ref"]["status"] == "blocked_privacy_risk"
    rendered = render_decision_work_offline_interpretation_queue_item_json(item)
    assert "api" + "_key" not in rendered


def test_invalid_source_packet_schema_blocks(tmp_path: Path) -> None:
    packet_path = _source_packet(tmp_path / "source_packet.json", schema="wrong")
    item = build_decision_work_offline_interpretation_queue_item(
        run_dir=_run_dir(tmp_path),
        contract_path=CONTRACT_PATH,
        source_packet_path=packet_path,
        created_at="2026-07-03T00:00:00Z",
    )

    assert item["queue_status"] == "blocked_schema_invalid"
    assert item["source_packet_ref"]["status"] == "blocked_schema_invalid"


def test_output_contains_no_local_absolute_paths_or_raw_private_content(
    tmp_path: Path,
) -> None:
    packet_path = _source_packet(tmp_path / "source_packet.json")
    item = build_decision_work_offline_interpretation_queue_item(
        run_dir=_run_dir(tmp_path),
        contract_path=CONTRACT_PATH,
        source_packet_path=packet_path,
        created_at="2026-07-03T00:00:00Z",
    )
    rendered = render_decision_work_offline_interpretation_queue_item_json(item)

    assert str(tmp_path) not in rendered
    for marker in FORBIDDEN_STRINGS:
        assert marker not in rendered


def test_validate_output_path_rejects_archive_mutation(tmp_path: Path) -> None:
    run_dir = _run_dir(tmp_path)

    with pytest.raises(DecisionWorkOfflineInterpretationQueueError):
        validate_output_path(output_path=run_dir / "queue.json", run_dir=run_dir)


def test_cli_writes_queue_item_without_archive_mutation(tmp_path: Path) -> None:
    run_dir = _run_dir(tmp_path)
    packet_path = _source_packet(tmp_path / "source_packet.json")
    out_path = tmp_path / "out" / "queue_item.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--run-dir",
            str(run_dir),
            "--contract",
            str(CONTRACT_PATH.relative_to(REPO_ROOT)),
            "--source-packet",
            str(packet_path),
            "--out",
            str(out_path),
            "--pretty",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == QUEUE_ITEM_SCHEMA_VERSION
    assert payload["queue_status"] == "queued"
    assert not (run_dir / "queue_item.json").exists()


def test_front_door_docs_link_queue_builder() -> None:
    conversation_rel = "decision-work-offline-interpretation-queue-builder-v0.md"
    repo_rel = (
        "docs/conversation-understanding/"
        "decision-work-offline-interpretation-queue-builder-v0.md"
    )
    board_rel = (
        "../conversation-understanding/"
        "decision-work-offline-interpretation-queue-builder-v0.md"
    )

    assert conversation_rel in PR179_DOC_PATH.read_text(encoding="utf-8")
    assert conversation_rel in PR178_PRD_PATH.read_text(encoding="utf-8")
    assert repo_rel in README_PATH.read_text(encoding="utf-8")
    assert repo_rel in HOW_IT_WORKS_PATH.read_text(encoding="utf-8")
    assert repo_rel in PROGRESS_PATH.read_text(encoding="utf-8")
    assert board_rel in BOARD_README_PATH.read_text(encoding="utf-8")


def test_queue_builder_docs_pass_product_delta_boundary_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            PR179_DOC_PATH,
            PR178_PRD_PATH,
            README_PATH,
            HOW_IT_WORKS_PATH,
            BOARD_README_PATH,
            PROGRESS_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0
