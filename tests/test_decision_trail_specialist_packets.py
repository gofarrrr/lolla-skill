from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from engine.system_b.decision_trail_specialist_packets import (
    DECISION_TRAIL_SPECIALIST_PACKETS_SCHEMA_VERSION,
    SPECIALIST_ROLES,
    DecisionTrailSpecialistPacketInputError,
    build_decision_trail_specialist_packets,
    load_json_object,
    render_decision_trail_specialist_packets_json,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-trail-fixture-review-v0/review.json"
)
CONTRACT_SCHEMA = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-trail-specialist-contracts-v0.json"
)
CONTRACT_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-trail-specialist-contracts-v0.md"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-trail-specialist-packet-builder-v0.md"
)
PACKET_FIXTURE = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-trail-specialist-packets-v0/packets.json"
)


def _build_packets(
    *,
    limit: int | None = 2,
    report_ids: list[str] | None = None,
) -> dict[str, Any]:
    return build_decision_trail_specialist_packets(
        fixture_review=load_json_object(FIXTURE_REVIEW),
        contract_schema=load_json_object(CONTRACT_SCHEMA),
        fixture_review_relpath=(
            "reviews/codex-assisted/decision-trail-fixture-review-v0/review.json"
        ),
        contract_schema_relpath=(
            "docs/conversation-understanding/decision-trail-specialist-contracts-v0.json"
        ),
        limit=limit,
        report_ids=report_ids,
    )


def _walk_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(str(key))
            keys.update(_walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(_walk_keys(child))
    return keys


def test_packet_builder_generates_checked_in_safe_packets() -> None:
    packets = _build_packets(limit=2)

    assert packets["schema_version"] == DECISION_TRAIL_SPECIALIST_PACKETS_SCHEMA_VERSION
    assert packets["generated_by"] == "decision_trail_specialist_packets"
    assert packets["mode"] == "checked_in_safe_mode"
    assert packets["report_count"] == 2
    assert len(packets["reports"]) == 2
    assert packets["packet_policy"]["specialist_reads_filled"] is False
    assert packets["packet_policy"]["fan_in_executed"] is False


def test_boundary_metadata_is_conservative() -> None:
    boundary = _build_packets(limit=1)["boundary"]

    assert boundary["human_validated"] is False
    assert boundary["ground_truth"] is False
    assert boundary["judge_calibration_eligible"] is False
    assert boundary["product_proof"] is False
    assert boundary["answer_quality_scored"] is False
    assert boundary["agent_action_authorized"] is False
    assert boundary["model_calls"] == 0
    assert boundary["archive_mutated"] is False
    assert boundary["runtime_invoked"] is False
    assert boundary["skill_invoked"] is False


def test_each_report_gets_all_pr90_specialist_packets() -> None:
    packets = _build_packets(limit=2)

    for report in packets["reports"]:
        assert set(report["packets"]) == set(SPECIALIST_ROLES)
        for role, packet in report["packets"].items():
            assert packet["specialist_role"] == role
            assert packet["expected_output_contract"]["filled_by_packet_builder"] is False
            assert packet["expected_output_contract"][
                "must_be_filled_by_future_specialist"
            ] is True
            assert packet["expected_output_contract"]["candidate_only"] is True
            assert packet["expected_output_contract"]["pr99_patch_fields"]
            assert "source_refs" in packet
            assert packet["known_limits"]
            assert packet["context"]["source_scope_summary"][
                "specialists_must_cite_scope_status"
            ] is True
            assert packet["context"]["truncation_summary"]["artifact_records_truncated"] == 0
            assert packet["context"]["local_private_retention_policy"][
                "local_include_text_output_retention_status"
            ] == "not_created_by_checked_in_safe_mode"


def test_pr99_patch_fields_are_role_specific() -> None:
    packets = _build_packets(limit=1)
    role_packets = packets["reports"][0]["packets"]

    assert {
        "assistant_influence_source_status",
        "source_scope_and_truncation_impact",
    } <= set(
        role_packets["conversation_shape_reader"]["expected_output_contract"][
            "pr99_patch_fields"
        ]
    )
    assert {
        "vanilla_overlap_read",
        "source_scope_and_truncation_impact",
    } <= set(
        role_packets["likely_action_reader"]["expected_output_contract"][
            "pr99_patch_fields"
        ]
    )
    assert {
        "lost_value_severity_read",
        "severity_source_status",
        "source_scope_and_truncation_impact",
    } <= set(
        role_packets["friction_lost_value_reader"]["expected_output_contract"][
            "pr99_patch_fields"
        ]
    )
    assert {
        "downgrade_triggers",
        "not_ready_reason",
        "source_scope_and_truncation_impact",
    } <= set(
        role_packets["conservative_fan_in_reader"]["expected_output_contract"][
            "pr99_patch_fields"
        ]
    )


def test_packets_preserve_pr88_thinness_and_report_non_checkin_status() -> None:
    packets = _build_packets(limit=2)

    for report in packets["reports"]:
        assert "source_report_not_checked_in" in report["missing_or_thin_context"]
        assert "local_private_shadow_review:not_run" in report["missing_or_thin_context"]
        assert report["available_context"]["source_report_checked_in"] is False
        assert report["available_context"]["source_report_available_in_repo"] is False
        for packet in report["packets"].values():
            assert "generated Decision Trail report JSON is not checked in" in " ".join(
                packet["known_limits"]
            )


def test_packets_do_not_fill_specialist_result_fields() -> None:
    rendered = render_decision_trail_specialist_packets_json(_build_packets(limit=2))

    forbidden_result_phrases = (
        '"completed_candidate"',
        '"areas_of_agreement":',
        '"vanilla_likely_next_action":',
        '"useful_friction":',
        '"lost_value":',
    )
    for phrase in forbidden_result_phrases:
        assert phrase not in rendered


def test_no_forbidden_authority_field_names_in_packet_output() -> None:
    packets = _build_packets(limit=2)
    keys = _walk_keys(packets)
    forbidden = {
        "safe_for_agent_use",
        "quality_score",
        "answer_quality_score",
        "improvement_score",
        "judge_score",
        "winner",
        "approved",
        "certified",
        "pass_fail",
        "score",
        "rating",
    }

    assert not (forbidden & keys)
    assert '"safe_for_agent_use"' not in render_decision_trail_specialist_packets_json(
        packets
    )


def test_local_private_mode_requires_local_run_dir() -> None:
    with pytest.raises(
        DecisionTrailSpecialistPacketInputError,
        match="local_private_mode requires at least one local run directory",
    ):
        build_decision_trail_specialist_packets(
            fixture_review=load_json_object(FIXTURE_REVIEW),
            contract_schema=load_json_object(CONTRACT_SCHEMA),
            fixture_review_relpath=(
                "reviews/codex-assisted/decision-trail-fixture-review-v0/review.json"
            ),
            mode="local_private_mode",
        )


def test_cli_writes_json_and_supports_report_filter(tmp_path: Path) -> None:
    out = tmp_path / "packets.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/evals/build_decision_trail_specialist_packets.py",
            "--fixture-review",
            str(FIXTURE_REVIEW),
            "--contract-schema",
            str(CONTRACT_SCHEMA),
            "--report-id",
            "structured_fixture_report",
            "--out",
            str(out),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["schema_version"] == DECISION_TRAIL_SPECIALIST_PACKETS_SCHEMA_VERSION
    assert payload["report_count"] == 1
    assert payload["reports"][0]["report_id"] == "structured_fixture_report"


def test_generated_packet_json_has_no_privacy_markers() -> None:
    rendered = render_decision_trail_specialist_packets_json(_build_packets(limit=2))

    for marker in (
        "/User" + "s/",
        "SEC" + "RET",
        "raw_message_" + "content",
        "fabricated_" + "passages",
        "FULL ASSISTANT " + "REASONING",
        "client_" + "secret",
        "api_" + "key",
        "pass" + "word",
    ):
        assert marker not in rendered


def test_pr78_lint_passes_generated_packets_and_docs(tmp_path: Path) -> None:
    out = tmp_path / "packets.json"
    out.write_text(
        render_decision_trail_specialist_packets_json(_build_packets(limit=2)),
        encoding="utf-8",
    )

    report = lint_product_delta_paths([out, DOC_PATH, CONTRACT_DOC, CONTRACT_SCHEMA])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }


def test_checked_in_fixture_is_small_and_safe() -> None:
    fixture = json.loads(PACKET_FIXTURE.read_text(encoding="utf-8"))

    assert fixture["schema_version"] == DECISION_TRAIL_SPECIALIST_PACKETS_SCHEMA_VERSION
    assert fixture["report_count"] == 2
    assert len(fixture["reports"]) == 2
    assert fixture["packet_policy"]["specialist_reads_filled"] is False
    assert fixture["packet_policy"]["fan_in_executed"] is False
    assert fixture["packet_policy"]["source_scope_policy"][
        "source_scope_summary_required"
    ] is True
    assert set(fixture["reports"][0]["packets"]) == set(SPECIALIST_ROLES)
    assert fixture["reports"][0]["available_context"]["source_scope_summary"]
    rendered = json.dumps(fixture, sort_keys=True)
    assert "/User" + "s/" not in rendered
    assert "raw_message_" + "content" not in rendered
