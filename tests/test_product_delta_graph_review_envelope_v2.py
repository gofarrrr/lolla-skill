from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_graph_review_envelope_v2 import (
    BLIND_PACKET_RELPATH,
    CONTRACT_RELPATH,
    EXACT_AUTHORIZATION,
    FIXTURE_RECEIPT_RELPATH,
    FROZEN_INPUT_LOCKS,
    FUTURE_CONSOLIDATION_RELPATH,
    FUTURE_INTERPRETATION_RELPATHS,
    FUTURE_POST_REVEAL_PACKET_RELPATHS,
    FUTURE_RESULT_RELPATH,
    FUTURE_REVIEW_FAILURE_RELPATHS,
    FUTURE_REVIEW_RELPATHS,
    INVALID_FIXTURE_RELPATH,
    LANES,
    PACKET_RELPATHS,
    POST_REVEAL_FIXTURE_RELPATHS,
    POST_REVEAL_SCHEMA_RELPATHS,
    REVIEW_IDS,
    SCHEMA_RELPATHS,
    VALID_FIXTURE_RELPATH,
    build_artifacts,
    render_json,
    validate_checked_in_artifacts,
    validate_json_schema_subset,
    validate_v2_review,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _build() -> dict[str, dict[str, Any]]:
    return build_artifacts(repo_root=REPO_ROOT)


def test_frozen_replication_checkpoint_is_hash_locked() -> None:
    for relpath, expected in FROZEN_INPUT_LOCKS.items():
        raw = (REPO_ROOT / relpath).read_bytes()
        import hashlib

        assert len(raw) == expected["bytes"]
        assert hashlib.sha256(raw).hexdigest() == expected["sha256"]


def test_repaired_packets_preserve_semantic_material_and_remove_old_shape() -> None:
    artifacts = _build()
    source = json.loads(
        (REPO_ROOT / BLIND_PACKET_RELPATH).read_text(encoding="utf-8")
    )
    preserved_keys = (
        "authoritative_source",
        "review_order",
        "visibility",
        "qualification_cases",
        "exact_duplicate_null",
        "comparison_case_count",
        "comparison_cases",
        "standdown_cases",
        "pre_review_mechanical_availability",
        "non_claims",
    )

    for lane in LANES:
        packet = artifacts[PACKET_RELPATHS[lane]]
        assert all(packet[key] == source[key] for key in preserved_keys)
        assert packet["boundary"]["semantic_execution_authorized"] is False
        assert packet["boundary"]["new_codex_contexts_authorized"] == 0
        assert (
            packet["structured_output_contract"]["execution_flag"]
            == "--output-schema"
        )
        assert packet["review_contract"]["enum_fields"][
            "cognitive_effect"
        ]["json_type"] == "string"
        rendered = render_json(packet)
        assert '"available_pair_response_shape"' not in rendered
        assert '"response_envelope_contract"' not in rendered
        assert '"fresh_context_task_wrappers"' not in rendered


def test_schema_accepts_scalar_fixture_and_rejects_29_array_fields() -> None:
    artifacts = _build()
    valid = artifacts[VALID_FIXTURE_RELPATH]
    invalid = artifacts[INVALID_FIXTURE_RELPATH]

    assert (
        validate_json_schema_subset(valid, artifacts[SCHEMA_RELPATHS["primary"]])
        == []
    )
    errors = validate_json_schema_subset(
        invalid, artifacts[SCHEMA_RELPATHS["skeptical"]]
    )
    assert len(errors) == 29
    assert all(
        ".cognitive_effect:expected string" in error for error in errors
    )

    scalar_schema = artifacts[SCHEMA_RELPATHS["primary"]]["properties"][
        "comparison_reviews"
    ]["items"]["properties"]["atomic_moves"]["items"]["properties"][
        "cognitive_effect"
    ]
    assert scalar_schema["type"] == "string"
    assert isinstance(scalar_schema["enum"], list)


def test_v2_review_reuses_existing_product_delta_validator() -> None:
    artifacts = _build()
    blind = json.loads(
        (REPO_ROOT / BLIND_PACKET_RELPATH).read_text(encoding="utf-8")
    )
    valid = artifacts[VALID_FIXTURE_RELPATH]
    invalid = artifacts[INVALID_FIXTURE_RELPATH]

    assert validate_v2_review(
        valid,
        blind=blind,
        lane="primary",
        schema=artifacts[SCHEMA_RELPATHS["primary"]],
    ) == []
    invalid_errors = validate_v2_review(
        invalid,
        blind=blind,
        lane="skeptical",
        schema=artifacts[SCHEMA_RELPATHS["skeptical"]],
    )
    assert len(invalid_errors) == 58
    assert sum("bad cognitive effect" in error for error in invalid_errors) == 29


def test_post_reveal_schemas_are_frozen_before_any_semantic_run() -> None:
    artifacts = _build()
    for lane in LANES:
        schema = artifacts[POST_REVEAL_SCHEMA_RELPATHS[lane]]
        fixture = artifacts[POST_REVEAL_FIXTURE_RELPATHS[lane]]
        assert validate_json_schema_subset(fixture, schema) == []
        assert schema["properties"]["state"]["type"] == "string"
        assert schema["properties"]["source_review_id"]["enum"] == [
            REVIEW_IDS[lane]
        ]


def test_fixture_receipt_states_only_structural_evidence() -> None:
    receipt = _build()[FIXTURE_RECEIPT_RELPATH]

    assert receipt["status"] == (
        "provider_free_shape_repair_fixture_gate_passed"
    )
    assert receipt["valid_scalar_fixture"]["validation_error_count"] == 0
    assert receipt["valid_scalar_fixture"]["meaning_validated"] is False
    invalid = receipt["historical_invalid_array_fixture"]
    assert invalid["validation_error_count"] == 29
    assert invalid["cognitive_effect_expected_string_error_count"] == 29
    assert invalid["terminal_semantics_recovered_or_used"] is False
    assert receipt["provider_calls"] == 0
    assert receipt["provider_cost_usd"] == 0.0


def test_contract_freezes_no_generation_and_four_context_ceiling() -> None:
    contract = _build()[CONTRACT_RELPATH]
    current = contract["current_authorization"]
    proposed = contract["proposed_next_run"]

    assert current["new_codex_semantic_contexts"] == 0
    assert current["new_codex_semantic_execution_authorized"] is False
    assert proposed["authorized_now"] is False
    assert proposed["exact_authorization_required"] == EXACT_AUTHORIZATION
    assert proposed["generation_contexts"] == 0
    assert proposed["blind_review_contexts"] == 2
    assert proposed["conditional_post_reveal_contexts"] == 2
    assert proposed["maximum_codex_contexts"] == 4
    assert proposed["reuse_frozen_generation_outputs"] is True
    assert proposed["reuse_historical_blind_reviews_as_v2_results"] is False
    assert proposed["retry_fallback_healing_replacement_reformatting"] is False
    for lane in LANES:
        argv = proposed["blind_execution_envelopes"][lane][
            "argv_template"
        ]
        assert "--output-schema" in argv
        assert "--ephemeral" in argv
        assert "read-only" in argv


def test_no_unauthorized_semantic_result_exists() -> None:
    for relpath in (
        *FUTURE_REVIEW_RELPATHS.values(),
        *FUTURE_REVIEW_FAILURE_RELPATHS.values(),
        *FUTURE_POST_REVEAL_PACKET_RELPATHS.values(),
        *FUTURE_INTERPRETATION_RELPATHS.values(),
        FUTURE_CONSOLIDATION_RELPATH,
        FUTURE_RESULT_RELPATH,
    ):
        assert not (REPO_ROOT / relpath).exists()


def test_checked_in_artifacts_are_exact_builder_products() -> None:
    artifacts = _build()
    assert validate_checked_in_artifacts(repo_root=REPO_ROOT) == []
    for relpath, payload in artifacts.items():
        assert (REPO_ROOT / relpath).read_text(
            encoding="utf-8"
        ) == render_json(payload)


def test_cli_validates_without_starting_semantic_work() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/evals/build_product_delta_graph_review_envelope_v2.py",
            "--validate-only",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "provider-free artifacts are current" in result.stdout
