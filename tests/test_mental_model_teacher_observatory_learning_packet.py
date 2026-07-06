import copy
import json
import re
from pathlib import Path

import pytest

from engine.system_b.mental_model_teacher_observatory_learning_packet import (
    LEARNING_PACKET_SCHEMA_VERSION,
    PRIMARY_TABS,
    MentalModelTeacherLearningPacketError,
    load_learning_packet,
    render_learning_packet_json,
    validate_learning_packet,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/product/mental-model-teacher-observatory-learning-packet-contract-v0.md"
EXAMPLE = REPO_ROOT / "docs/product/mental-model-teacher-observatory-learning-packet-example-v0.json"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/mental-model-teacher-observatory-learning-packet-contract-v0/review.json"
)


def _example() -> dict:
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def test_contract_doc_example_review_and_readme_exist() -> None:
    assert DOC.exists()
    assert EXAMPLE.exists()
    assert REVIEW.exists()
    readme = README.read_text(encoding="utf-8")
    assert "Mental Model Teacher Observatory Learning Packet Contract" in readme
    assert "mental-model-teacher-observatory-learning-packet-contract-v0.md" in readme


def test_example_learning_packet_validates() -> None:
    packet = validate_learning_packet(_example())

    assert packet["schema_version"] == LEARNING_PACKET_SCHEMA_VERSION
    assert packet["observatory_tabs"] == list(PRIMARY_TABS)
    assert packet["default_tab"] == "Outcome"
    assert packet["lesson"]["schema_version"] == "lolla.mental_model_teacher.teacher_lesson.v0"
    assert packet["models"][0]["display_name"] == "Base Rates"
    assert packet["relations"][0]["relation_type"] == "ally"
    assert packet["graph"]["graph_scope"] == "lesson_neighborhood"
    assert packet["single_home_rules"]["teacher_reasoning_move"] == "Learn"
    assert packet["single_home_rules"]["source_custody"] == "Receipts"
    assert packet["single_home_rules"]["usage_cost_telemetry"] == "Advanced"
    assert packet["visibility_policy"]["raw_telemetry_in_primary_tabs"] is False
    assert packet["visibility_policy"]["advanced_telemetry_separate"] is True


def test_render_and_load_helpers_keep_json_shape() -> None:
    packet = validate_learning_packet(load_learning_packet(EXAMPLE))
    rendered = render_learning_packet_json(packet)
    parsed = json.loads(rendered)

    assert parsed["schema_version"] == LEARNING_PACKET_SCHEMA_VERSION
    assert parsed["packet_id"] == "contract-fixture-run-learning-packet"


def test_packet_rejects_unsupported_tabs_and_single_home_drift() -> None:
    packet = copy.deepcopy(_example())
    packet["observatory_tabs"] = ["Outcome", "Teacher", "Telemetry"]

    with pytest.raises(MentalModelTeacherLearningPacketError, match="observatory_tabs"):
        validate_learning_packet(packet)

    packet = copy.deepcopy(_example())
    packet["single_home_rules"]["canonical_model_explanation"] = "Learn"

    with pytest.raises(
        MentalModelTeacherLearningPacketError,
        match="single_home_rules.canonical_model_explanation",
    ):
        validate_learning_packet(packet)


def test_packet_rejects_primary_tab_telemetry_and_receipt_home_drift() -> None:
    packet = copy.deepcopy(_example())
    packet["visibility_policy"]["raw_telemetry_in_primary_tabs"] = True

    with pytest.raises(
        MentalModelTeacherLearningPacketError,
        match="visibility_policy.raw_telemetry_in_primary_tabs",
    ):
        validate_learning_packet(packet)

    packet = copy.deepcopy(_example())
    packet["receipts"]["artifact_refs"][0]["home_tab"] = "Learn"

    with pytest.raises(MentalModelTeacherLearningPacketError, match="home_tab"):
        validate_learning_packet(packet)


def test_packet_rejects_runtime_provider_and_proof_flags() -> None:
    packet = copy.deepcopy(_example())
    packet["runtime_integration_authorized"] = True

    with pytest.raises(
        MentalModelTeacherLearningPacketError,
        match="runtime_integration_authorized",
    ):
        validate_learning_packet(packet)

    packet = copy.deepcopy(_example())
    packet["provider_or_model_calls_used"] = True

    with pytest.raises(
        MentalModelTeacherLearningPacketError,
        match="provider_or_model_calls_used",
    ):
        validate_learning_packet(packet)

    packet = copy.deepcopy(_example())
    packet["product_proof"] = True

    with pytest.raises(MentalModelTeacherLearningPacketError, match="product_proof"):
        validate_learning_packet(packet)


def test_packet_rejects_nested_contract_violations() -> None:
    packet = copy.deepcopy(_example())
    packet["relations"][0]["confidence"] = "proof"

    with pytest.raises(MentalModelTeacherLearningPacketError, match="confidence"):
        validate_learning_packet(packet)

    packet = copy.deepcopy(_example())
    packet["graph"]["edges"][0]["affinity"] = 0.99

    with pytest.raises(MentalModelTeacherLearningPacketError, match="affinity"):
        validate_learning_packet(packet)


def test_packet_rejects_private_paths_and_score_like_keys() -> None:
    packet = copy.deepcopy(_example())
    packet["receipts"]["source_refs"][0]["path"] = "/" + "Users/example/result.json"

    with pytest.raises(MentalModelTeacherLearningPacketError, match="must be relative"):
        validate_learning_packet(packet)

    packet = copy.deepcopy(_example())
    packet["answer_quality_score"] = 1.0

    with pytest.raises(MentalModelTeacherLearningPacketError, match="forbidden packet key"):
        validate_learning_packet(packet)


def test_doc_preserves_stop_line_and_api_direction() -> None:
    text = DOC.read_text(encoding="utf-8")

    for phrase in [
        "does not build packets",
        "does not build product data",
        "Outcome | Learn | Models | Relations | Map | Receipts",
        "single-home rules",
        "raw telemetry is not shown in primary tabs",
        "Receipt artifacts must be assigned to either",
        "runtime wiring",
        "provider/model calls",
        "answer/advice correctness scoring",
        "proceed_to_observatory_teacher_learning_packet_builder",
    ]:
        assert phrase in text


def test_review_json_records_contract_gate_and_non_claims() -> None:
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    assert review["schema"] == (
        "lolla.mental_model_teacher_observatory_learning_packet_contract_review.v0"
    )
    assert review["decision_gate"] == (
        "proceed_to_observatory_teacher_learning_packet_builder"
    )
    assert review["product_decision"]["one_shell"] == "Observatory"
    assert review["product_decision"]["standalone_teacher_app"] is False
    assert review["contract_guards"]["single_home_rules_required"] is True
    assert review["contract_guards"]["receipts_home_limited_to_receipts_or_advanced"] is True
    assert review["contract_guards"]["runtime_wiring_allowed"] is False

    non_claims = review["non_claims"]
    assert non_claims["lolla_skill_invoked"] is False
    assert non_claims["provider_or_model_calls_used"] is False
    assert non_claims["runtime_behavior_changed"] is False
    assert non_claims["product_proof"] is False
    assert non_claims["human_validated"] is False
    assert non_claims["answer_correctness"] is False
    assert non_claims["advice_correctness"] is False
    assert non_claims["graph_edges_are_proof"] is False


def test_markdown_links_and_json_are_clean() -> None:
    missing = []
    for path in [README, DOC]:
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith("#") or re.match(r"^[a-z]+:", target):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).resolve().exists():
                missing.append(f"{path}: {target}")
    assert missing == []

    text = EXAMPLE.read_text(encoding="utf-8") + REVIEW.read_text(encoding="utf-8")
    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "product_proof\": true" not in text
    assert "runtime_integration_authorized\": true" not in text
