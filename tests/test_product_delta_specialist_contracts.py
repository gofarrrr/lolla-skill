from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    REPO_ROOT / "docs/evals/product-delta-specialist-review-contracts-v0.json"
)
DOC_PATH = REPO_ROOT / "docs/evals/product-delta-specialist-review-contracts-v0.md"


def _schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


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


def test_schema_json_parses_and_has_expected_version() -> None:
    schema = _schema()

    assert schema["$id"] == "lolla.product_delta_specialist_review_contracts.v0"
    assert (
        schema["properties"]["schema_version"]["const"]
        == "lolla.product_delta_specialist_review_contracts.v0"
    )
    assert schema["properties"]["contract_family"]["const"] == (
        "product_delta_specialist_review"
    )


def test_required_specialist_contract_definitions_exist() -> None:
    defs = _schema()["$defs"]

    expected_defs = {
        "conversation_interpretation_read",
        "vanilla_likely_next_action_read",
        "lolla_likely_next_action_read",
        "structural_delta_read",
        "friction_lost_value_read",
        "interpretation_adequacy_read",
        "advisory_overclaim_read",
        "conservative_fan_in_read",
    }

    assert expected_defs <= set(defs)


def test_schema_avoids_forbidden_authority_fields() -> None:
    schema = _schema()
    text = SCHEMA_PATH.read_text(encoding="utf-8")
    keys = _walk_keys(schema)
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
    }

    assert not (forbidden & keys)
    for field in forbidden:
        assert f'"{field}"' not in text


def test_required_lower_claim_boundary_fields_exist() -> None:
    boundary = _schema()["$defs"]["boundary"]
    required = set(boundary["required"])
    properties = set(boundary["properties"])
    expected = {
        "human_validated",
        "ground_truth",
        "judge_calibration_eligible",
        "product_proof",
        "answer_quality_scored",
        "agent_action_authorized",
        "archive_mutated",
    }

    assert expected <= required
    assert expected <= properties
    for field in expected:
        assert boundary["properties"][field]["const"] is False


def test_net_decision_read_enum_is_provisional() -> None:
    enum = set(_schema()["$defs"]["net_decision_read_candidate"]["enum"])

    assert enum == {
        "material_improvement_candidate",
        "partial_improvement_candidate",
        "no_material_change_candidate",
        "lolla_added_noise_candidate",
        "lolla_worse_candidate",
        "inconclusive",
        "not_reviewed",
    }


def test_interpretation_adequacy_failure_fields_exist() -> None:
    properties = set(_schema()["$defs"]["interpretation_adequacy_read"]["properties"])

    assert {
        "decision_question_drift",
        "option_loss",
        "constraint_flattening",
        "stakeholder_erasure",
        "value_overwrite",
        "assistant_influence_blindness",
        "dropped_thread_blindness",
        "uncertainty_collapse",
        "risk_mode_mismatch",
    } <= properties


def test_pr78_lint_passes_new_contract_artifacts() -> None:
    report = lint_product_delta_paths([DOC_PATH, SCHEMA_PATH])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
