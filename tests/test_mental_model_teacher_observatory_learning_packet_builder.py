import json
import re
from pathlib import Path

import pytest

from engine.system_b.mental_model_teacher_observatory_learning_packet import (
    PRIMARY_TABS,
    REQUIRED_SINGLE_HOME_RULES,
    REQUIRED_VISIBILITY_POLICY,
    validate_learning_packet,
)
from engine.system_b.mental_model_teacher_observatory_learning_packet_builder import (
    CASE_IDS,
    DEFAULT_OUTPUT_DIR,
    LEARNING_PACKET_BUILDER_MANIFEST_SCHEMA_VERSION,
    MentalModelTeacherLearningPacketBuilderError,
    build_observatory_learning_packet,
    main,
    write_observatory_learning_packet_package,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = (
    REPO_ROOT
    / "docs/product/mental-model-teacher-observatory-learning-packet-builder-v0.md"
)
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/mental-model-teacher-observatory-learning-packet-builder-v0/review.json"
)
README = REPO_ROOT / "docs/product/README.md"
PACKAGE_MANIFEST = DEFAULT_OUTPUT_DIR / "manifest.json"


def test_builder_emits_valid_selected_run_learning_packet() -> None:
    packet = build_observatory_learning_packet(
        REPO_ROOT,
        case_id="launch-public-enterprise-beta",
    )
    validated = validate_learning_packet(packet)

    assert validated["packet_id"] == (
        "launch-public-enterprise-beta-observatory-teacher-learning-packet"
    )
    assert validated["run_ref"]["source"] == "archive"
    assert validated["run_ref"]["case_id"] == "launch-public-enterprise-beta"
    assert validated["observatory_tabs"] == list(PRIMARY_TABS)
    assert validated["default_tab"] == "Outcome"
    assert validated["lesson"]["case_id"] == "launch-public-enterprise-beta"
    assert len(validated["models"]) == 3
    assert len(validated["relations"]) == 1
    assert len(validated["graph"]["nodes"]) == 3
    assert len(validated["graph"]["edges"]) == 1
    assert validated["product_proof"] is False
    assert validated["human_validated"] is False
    assert validated["runtime_integration_authorized"] is False
    assert validated["provider_or_model_calls_used"] is False


def test_builder_preserves_canonical_model_identity_separate_from_lesson_label() -> None:
    packet = build_observatory_learning_packet(
        REPO_ROOT,
        case_id="launch-public-enterprise-beta",
    )
    display_names = {page["model_id"]: page["display_name"] for page in packet["models"]}
    lesson_names = {
        item["model_id"]: item.get("teaching_name")
        for item in packet["lesson"]["model_stack"]
    }

    assert display_names["authority-bias"] == "Authority Bias"
    assert lesson_names["authority-bias"] == "Test The Authority, Not The Aura"
    assert "Test The Authority, Not The Aura" not in display_names.values()
    assert "Authority Bias" not in lesson_names.values()


def test_builder_applies_single_home_and_visibility_policies() -> None:
    packet = build_observatory_learning_packet(
        REPO_ROOT,
        case_id="deploy-assisted-intake-routing",
    )

    assert packet["single_home_rules"] == dict(REQUIRED_SINGLE_HOME_RULES)
    assert packet["visibility_policy"] == dict(REQUIRED_VISIBILITY_POLICY)
    assert packet["single_home_rules"]["teacher_reasoning_move"] == "Learn"
    assert packet["single_home_rules"]["canonical_model_explanation"] == "Models"
    assert packet["single_home_rules"]["relation_explanation"] == "Relations"
    assert packet["single_home_rules"]["graph_neighborhood"] == "Map"
    assert packet["single_home_rules"]["source_custody"] == "Receipts"
    assert packet["single_home_rules"]["usage_cost_telemetry"] == "Advanced"
    assert packet["visibility_policy"]["raw_telemetry_in_primary_tabs"] is False
    assert packet["visibility_policy"]["raw_canonical_markdown_in_primary_tabs"] is False


def test_receipts_are_limited_to_receipts_or_advanced() -> None:
    packet = build_observatory_learning_packet(
        REPO_ROOT,
        case_id="ceo-remove-founding-cofounder",
    )
    artifacts = packet["receipts"]["artifact_refs"]

    assert artifacts
    assert {artifact["home_tab"] for artifact in artifacts} <= {"Receipts", "Advanced"}
    assert {artifact["exposure"] for artifact in artifacts} <= {
        "receipts",
        "advanced_only",
    }
    assert any(artifact["home_tab"] == "Advanced" for artifact in artifacts)
    assert "High-risk case" in " ".join(packet["missingness"]["notes"])


def test_three_case_package_writer_outputs_valid_packet_manifest(tmp_path: Path) -> None:
    manifest = write_observatory_learning_packet_package(
        REPO_ROOT,
        tmp_path / "learning-packets",
    )

    assert manifest["schema_version"] == LEARNING_PACKET_BUILDER_MANIFEST_SCHEMA_VERSION
    assert manifest["packet_count"] == 3
    assert manifest["decision_gate"] == "proceed_to_observatory_teacher_packet_adapter"
    assert manifest["observatory_endpoint_built"] is False
    assert manifest["observatory_ui_built"] is False
    assert manifest["runtime_integration_authorized"] is False
    assert manifest["provider_or_model_calls_used"] is False

    for entry in manifest["packets"]:
        packet_path = tmp_path / "learning-packets" / entry["path"]
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        assert validate_learning_packet(packet)["packet_id"] == entry["packet_id"]


def test_cli_writes_package_manifest(tmp_path: Path) -> None:
    output_dir = tmp_path / "packets"

    status = main(["--root", str(REPO_ROOT), "--output-dir", str(output_dir)])

    assert status == 0
    manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["packet_count"] == 3
    assert {entry["case_id"] for entry in manifest["packets"]} == set(CASE_IDS)


def test_unknown_case_is_clear_builder_error() -> None:
    with pytest.raises(MentalModelTeacherLearningPacketBuilderError, match="unsupported"):
        build_observatory_learning_packet(REPO_ROOT, case_id="not-a-case")


def test_checked_in_packet_package_validates_after_generation() -> None:
    assert PACKAGE_MANIFEST.exists()
    manifest = json.loads(PACKAGE_MANIFEST.read_text(encoding="utf-8"))
    assert manifest["schema_version"] == LEARNING_PACKET_BUILDER_MANIFEST_SCHEMA_VERSION
    assert manifest["output_dir"] == (
        "docs/product/mental-model-teacher-observatory-learning-packets-v0"
    )

    for entry in manifest["packets"]:
        packet_path = DEFAULT_OUTPUT_DIR / entry["path"]
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        validate_learning_packet(packet)


def test_builder_docs_review_and_readme_preserve_gate_and_boundaries() -> None:
    doc = DOC.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    readme = README.read_text(encoding="utf-8")

    assert "mental-model-teacher-observatory-learning-packet-builder-v0.md" in readme
    assert review["decision_gate"] == "proceed_to_observatory_teacher_packet_adapter"
    assert review["builder_guards"]["canonical_model_identity_preserved"] is True
    assert review["builder_guards"]["lesson_slogans_not_used_as_model_names"] is True
    assert review["builder_guards"]["runtime_wiring_allowed"] is False
    assert review["non_claims"]["provider_or_model_calls_used"] is False
    assert review["non_claims"]["runtime_behavior_changed"] is False
    for phrase in [
        "does not run Lolla",
        "does not alter Observatory routes",
        "Outcome | Learn | Models | Relations | Map | Receipts",
        "Mental model pages use canonical model identity",
        "remains a lesson or practice label",
        "Telemetry and review/audit artifacts are Receipts or Advanced material",
        "proceed_to_observatory_teacher_packet_adapter",
    ]:
        assert phrase in doc


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

    text = (
        DOC.read_text(encoding="utf-8")
        + REVIEW.read_text(encoding="utf-8")
        + PACKAGE_MANIFEST.read_text(encoding="utf-8")
    )
    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "product_proof\": true" not in text
    assert "human_validated\": true" not in text
    assert "runtime_integration_authorized\": true" not in text
