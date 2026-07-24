from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

from engine.system_b.product_delta_graph_replication_result import NON_CLAIMS
from engine.system_b.product_delta_graph_review_envelope_v2 import (
    FUTURE_POST_REVEAL_PACKET_RELPATHS as V2_PACKET_RELPATHS,
    LANES,
    POST_REVEAL_SCHEMA_RELPATHS as V2_POST_REVEAL_SCHEMA_RELPATHS,
    REVIEW_IDS as V2_REVIEW_IDS,
    validate_json_schema_subset,
)
from engine.system_b.product_delta_graph_review_nonclaim_custody_v3 import (
    CONTRACT_RELPATH,
    EXACT_FUTURE_AUTHORIZATION,
    FIXTURE_RECEIPT_RELPATH,
    FUTURE_CONSOLIDATION_RELPATH,
    FUTURE_INTERPRETATION_RELPATHS,
    FUTURE_RESULT_RELPATH,
    LEGACY_ECHO_FIXTURE_RELPATHS,
    NONCLAIM_CUSTODY_SCHEMA_VERSION,
    PACKET_RELPATHS,
    INTERPRETATION_IDS,
    POST_REVEAL_SCHEMA_VERSION,
    RESULT_RELPATH,
    SCHEMA_RELPATHS,
    VALID_FIXTURE_RELPATHS,
    build_artifacts,
    nonclaim_statement_sha256,
    validate_checked_in_artifacts,
    validate_nonclaim_custody,
    validate_v3_post_reveal,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read_json(relpath: str) -> dict:
    return json.loads((REPO_ROOT / relpath).read_text(encoding="utf-8"))


def test_v3_schema_removes_model_authored_nonclaim_echo_only() -> None:
    artifacts = build_artifacts(repo_root=REPO_ROOT)

    for lane in LANES:
        v2_schema = _read_json(V2_POST_REVEAL_SCHEMA_RELPATHS[lane])
        v3_schema = artifacts[SCHEMA_RELPATHS[lane]]
        assert v3_schema["properties"]["schema_version"]["enum"] == [
            POST_REVEAL_SCHEMA_VERSION
        ]
        assert "nonclaims_acknowledged" not in v3_schema["properties"]
        assert "nonclaims_acknowledged" not in v3_schema["required"]
        assert set(v3_schema["properties"]) == (
            set(v2_schema["properties"]) - {"nonclaims_acknowledged"}
        )
        assert set(v3_schema["required"]) == (
            set(v2_schema["required"]) - {"nonclaims_acknowledged"}
        )
        expected_schema = copy.deepcopy(v2_schema)
        expected_schema["title"] = (
            "Lolla graph review nonclaim-custody post-reveal "
            f"v3 ({lane})"
        )
        expected_schema["properties"].pop("nonclaims_acknowledged")
        expected_schema["required"].remove("nonclaims_acknowledged")
        expected_schema["properties"]["schema_version"]["enum"] = [
            POST_REVEAL_SCHEMA_VERSION
        ]
        expected_schema["properties"]["interpretation_id"]["enum"] = [
            INTERPRETATION_IDS[lane]
        ]
        expected_schema["properties"]["source_review_id"]["enum"] = [
            V2_REVIEW_IDS[lane]
        ]
        assert v3_schema == expected_schema

        valid = artifacts[VALID_FIXTURE_RELPATHS[lane]]
        assert "nonclaims_acknowledged" not in valid
        assert validate_json_schema_subset(valid, v3_schema) == []
        assert (
            validate_v3_post_reveal(
                valid,
                packet=artifacts[PACKET_RELPATHS[lane]],
                lane=lane,
                schema=v3_schema,
            )
            == []
        )

        legacy = artifacts[LEGACY_ECHO_FIXTURE_RELPATHS[lane]]
        assert legacy["nonclaims_acknowledged"] == list(NON_CLAIMS)
        assert validate_json_schema_subset(legacy, v3_schema) == [
            "$:unexpected property nonclaims_acknowledged"
        ]


def test_packet_custody_proves_exact_input_not_internal_compliance() -> None:
    artifacts = build_artifacts(repo_root=REPO_ROOT)
    expected_ids = [f"NC-{index:02d}" for index in range(1, 11)]

    for lane in LANES:
        packet = artifacts[PACKET_RELPATHS[lane]]
        v2_packet = _read_json(V2_PACKET_RELPATHS[lane])
        assert packet["mechanical_availability"] == (
            v2_packet["mechanical_availability"]
        )
        assert packet["frozen_review"] == v2_packet["frozen_review"]
        assert packet["comparison_reveal"] == v2_packet["comparison_reveal"]
        assert packet["forbidden_behavior"] == (
            v2_packet["forbidden_behavior"]
        )
        custody = packet["nonclaim_custody"]
        assert custody["schema_version"] == NONCLAIM_CUSTODY_SCHEMA_VERSION
        assert custody["owner"] == "deterministic_input_packet"
        assert custody["statement_count"] == 10
        assert [row["nonclaim_id"] for row in custody["statements"]] == (
            expected_ids
        )
        assert [row["text"] for row in custody["statements"]] == list(
            NON_CLAIMS
        )
        assert custody["ordered_statement_sha256"] == (
            nonclaim_statement_sha256(NON_CLAIMS)
        )
        assert custody["model_response_echo_required"] is False
        assert custody["proves_internal_compliance"] is False
        assert validate_nonclaim_custody(packet) == []
        assert "non_claims" not in packet

        drifted = copy.deepcopy(packet)
        drifted["nonclaim_custody"]["statements"][0]["text"] += " drift"
        assert validate_nonclaim_custody(drifted) == [
            "nonclaim custody statements drifted",
            "nonclaim custody statement hash drifted",
        ]


def test_contract_is_provider_free_and_does_not_authorize_execution() -> None:
    artifacts = build_artifacts(repo_root=REPO_ROOT)
    contract = artifacts[CONTRACT_RELPATH]

    assert contract["status"] == (
        "provider_free_nonclaim_custody_repair_complete_"
        "semantic_execution_not_authorized"
    )
    assert contract["falsifiable_question"] == (
        "Can deterministic input-packet custody preserve the exact ten "
        "post-reveal nonclaims while the model-authored response omits every "
        "nonclaim echo field?"
    )
    assert contract["current_authorization"] == {
        "provider_free_contract_fixture_and_documentation_work": True,
        "new_codex_semantic_contexts": 0,
        "new_codex_semantic_execution_authorized": False,
        "repository_provider_api_calls": 0,
        "repository_provider_api_cost_usd": 0.0,
        "private_archive_inspection": False,
        "principal_human_fields": False,
        "historical_payload_repair_or_semantic_salvage": False,
        "graph_source_relation_traversal_policy_or_runtime_change": False,
        "answer_quality_graph_value_or_usefulness_claim": False,
    }
    assert contract["prospective_run"]["authorized_now"] is False
    assert (
        contract["prospective_run"]["exact_authorization_required"]
        == EXACT_FUTURE_AUTHORIZATION
    )
    assert contract["prospective_run"]["maximum_codex_contexts"] == 2
    assert contract["prospective_run"]["blind_review_contexts"] == 0
    assert contract["prospective_run"]["post_reveal_contexts"] == 2
    assert contract["prospective_run"]["reuse_frozen_v2_blind_reviews"] is True
    assert contract["prospective_run"]["no_retry"] is True
    assert contract["provider_calls"] == 0
    assert contract["provider_cost_usd"] == 0.0


def test_fixture_receipt_keeps_shape_and_semantics_separate() -> None:
    receipt = build_artifacts(repo_root=REPO_ROOT)[FIXTURE_RECEIPT_RELPATH]
    assert receipt["status"] == (
        "provider_free_nonclaim_input_custody_fixture_gate_passed"
    )
    assert receipt["valid_fixture_count"] == 2
    assert receipt["legacy_echo_rejection_count"] == 2
    assert receipt["input_nonclaim_custody_error_count"] == 0
    assert receipt["semantic_correctness_validated"] is False
    assert receipt["model_compliance_validated"] is False
    assert receipt["graph_value_validated"] is False
    assert receipt["provider_calls"] == 0
    assert receipt["provider_cost_usd"] == 0.0


def test_checked_in_artifacts_and_no_semantic_result_are_current() -> None:
    assert validate_checked_in_artifacts(repo_root=REPO_ROOT) == []
    assert (REPO_ROOT / RESULT_RELPATH).is_file()
    for relpath in (
        *FUTURE_INTERPRETATION_RELPATHS.values(),
        FUTURE_CONSOLIDATION_RELPATH,
        FUTURE_RESULT_RELPATH,
    ):
        assert not (REPO_ROOT / relpath).exists()


def test_cli_validates_without_starting_semantic_work() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(
                REPO_ROOT
                / "scripts/evals/"
                "build_product_delta_graph_review_nonclaim_custody_v3.py"
            ),
            "--validate-only",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "V3 nonclaim-custody artifacts are current." in result.stdout
