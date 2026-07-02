from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from engine.system_b.decision_work_automatic_triage_packets import (
    CASE_REFS,
    DECISION_WORK_AUTOMATIC_TRIAGE_CONTRACT_SCHEMA_VERSION,
    DECISION_WORK_AUTOMATIC_TRIAGE_PACKETS_SCHEMA_VERSION,
    NON_CLAIMS,
    DecisionWorkAutomaticTriagePacketInputError,
    build_decision_work_automatic_triage_packets,
    render_decision_work_automatic_triage_packets_json,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-triage-packet-builder-v0.md"
)
CONTRACT_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-triage-contract-v0.json"
)
SCRIPT_PATH = (
    REPO_ROOT / "scripts/evals/build_decision_work_automatic_triage_packets.py"
)
SCHEMA_VERSION = "lolla.decision_work_automatic_triage_packets.v0"
EXPECTED_CASES = {
    "launch-public-enterprise-beta",
    "deploy-assisted-intake-routing",
    "ceo-remove-founding-cofounder",
}
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "packet_metadata",
    "mode",
    "triage_contract_ref",
    "source_cases",
    "source_artifacts",
    "enriched_brief_refs",
    "original_brief_refs",
    "interpretation_read_refs",
    "source_review_refs",
    "human_calibration_refs",
    "custody_flags",
    "triage_field_groups",
    "future_triage_tasks",
    "known_limits",
    "non_claims",
}
REQUIRED_FALSE_FLAGS = {
    "human_validated",
    "human_review_completed",
    "human_response_collected",
    "product_proof",
    "runtime_invoked",
    "skill_invoked",
    "archive_mutated",
    "answer_quality_scored",
    "agent_action_authorized",
    "automatic_action_authorized",
    "semantic_triage_performed",
    "triage_fields_filled",
    "raw_private_content_included",
    "provider_text_included",
    "raw_transcript_included",
    "raw_revised_answer_included",
    "raw_memo_included",
    "private_ledger_content_included",
    "local_absolute_paths_included",
    "secrets_included",
    "automatic_labels_created",
    "broad_judge_used",
}
PRIVACY_MARKERS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)


def _packet() -> dict[str, Any]:
    return build_decision_work_automatic_triage_packets(
        created_at="2026-07-02T00:00:00Z"
    )


def _collect_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        strings: list[str] = []
        for item in value:
            strings.extend(_collect_strings(item))
        return strings
    if isinstance(value, dict):
        strings = []
        for item in value.values():
            strings.extend(_collect_strings(item))
        return strings
    return []


def _repo_refs(value: Any) -> set[str]:
    refs = {
        item
        for item in _collect_strings(value)
        if item.startswith(("docs/", "reviews/"))
    }
    return refs


def test_packet_has_expected_schema_shape_and_cases() -> None:
    packet = _packet()

    assert packet["schema_version"] == DECISION_WORK_AUTOMATIC_TRIAGE_PACKETS_SCHEMA_VERSION
    assert packet["schema_version"] == SCHEMA_VERSION
    assert REQUIRED_TOP_LEVEL <= set(packet)
    assert packet["mode"] == "checked_in_safe"
    assert packet["triage_contract_ref"] == (
        "docs/conversation-understanding/decision-work-automatic-triage-contract-v0.json"
    )
    assert packet["packet_metadata"]["semantic_triage_fields_filled"] is False
    assert {case["case_id"] for case in packet["source_cases"]} == EXPECTED_CASES
    assert [case["case_id"] for case in packet["source_cases"]] == [
        case["case_id"] for case in CASE_REFS
    ]


def test_packet_refs_resolve_and_include_expected_artifact_groups() -> None:
    packet = _packet()

    refs = _repo_refs(packet)
    assert packet["enriched_brief_refs"]
    assert packet["original_brief_refs"]
    assert packet["interpretation_read_refs"]
    assert packet["source_review_refs"]
    assert packet["human_calibration_refs"]
    for ref in refs:
        assert (REPO_ROOT / ref).exists(), ref
        assert not ref.startswith(("SKILL.md", "scripts/skill/", "plans/"))
        assert not ref.startswith("archive/")


def test_packet_custody_flags_are_conservative() -> None:
    custody = _packet()["custody_flags"]

    assert custody["checked_in_safe"] is True
    assert custody["model_calls"] == 0
    for field in REQUIRED_FALSE_FLAGS:
        assert custody[field] is False
    assert set(_packet()["non_claims"]) >= set(NON_CLAIMS)


def test_triage_field_groups_are_carried_but_not_filled() -> None:
    packet = _packet()
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    expected_groups = {field["field_group"] for field in contract["triage_fields"]}
    observed_groups = {field["field_group"] for field in packet["triage_field_groups"]}

    assert observed_groups == expected_groups
    for field in packet["triage_field_groups"]:
        assert field["current_packet_status"] == "not_evaluated"
        assert field["semantic_triage_filled"] is False
        assert field["value"] is None
        assert field["source_refs"] == []
        assert field["uncertainty"] == "not_evaluated"
        assert field["must_not_be_used_as_quality_label"] is True


def test_packet_rejects_unsupported_contract_schema(tmp_path: Path) -> None:
    bad_contract = tmp_path / "bad-contract.json"
    bad_contract.write_text(
        json.dumps(
            {
                "schema_version": "unsupported",
                "custody_flags": {"model_calls": 0},
                "triage_fields": [],
                "triage_categories": [],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(DecisionWorkAutomaticTriagePacketInputError):
        build_decision_work_automatic_triage_packets(
            triage_contract_path=Path("bad-contract.json"),
            repo_root=tmp_path,
        )


def test_rendered_packet_contains_no_private_markers_or_absolute_paths() -> None:
    rendered = render_decision_work_automatic_triage_packets_json(_packet(), pretty=True)

    for marker in PRIVACY_MARKERS:
        assert marker not in rendered
    assert DECISION_WORK_AUTOMATIC_TRIAGE_CONTRACT_SCHEMA_VERSION in CONTRACT_PATH.read_text(
        encoding="utf-8"
    )
    assert "safe_for_agent_use" not in rendered
    assert '"answer_quality_score":' not in rendered
    assert '"improvement_score":' not in rendered
    assert "approved" not in rendered.lower()
    assert "certified" not in rendered.lower()


def test_cli_generates_checked_in_safe_packet(tmp_path: Path) -> None:
    output_path = tmp_path / "decision_work_automatic_triage_packets.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--triage-contract",
            "docs/conversation-understanding/decision-work-automatic-triage-contract-v0.json",
            "--out",
            str(output_path),
            "--pretty",
        ],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    packet = json.loads(output_path.read_text(encoding="utf-8"))
    assert packet["schema_version"] == SCHEMA_VERSION
    assert packet["mode"] == "checked_in_safe"
    assert packet["custody_flags"]["model_calls"] == 0


def test_cli_rejects_output_over_contract_path() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--triage-contract",
            "docs/conversation-understanding/decision-work-automatic-triage-contract-v0.json",
            "--out",
            "docs/conversation-understanding/decision-work-automatic-triage-contract-v0.json",
        ],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 2
    assert "output path must be different" in result.stderr


def test_packet_builder_doc_and_json_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths([DOC_PATH, CONTRACT_PATH])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
