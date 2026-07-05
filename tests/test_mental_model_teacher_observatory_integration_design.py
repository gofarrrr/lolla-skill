import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/product/mental-model-teacher-observatory-integration-design-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/mental-model-teacher-observatory-integration-design-v0/review.json"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_design_doc_exists_and_is_indexed() -> None:
    assert DOC.exists()
    assert REVIEW.exists()
    readme = _read(README)
    assert "Mental Model Teacher Observatory Integration Design" in readme
    assert "mental-model-teacher-observatory-integration-design-v0.md" in readme


def test_design_declares_one_observatory_shell() -> None:
    text = _read(DOC)

    for phrase in [
        "Teacher should become a learner layer inside Observatory",
        "Do not ship a separate `Teacher` app beside Observatory.",
        "Do not make a second static product page",
        "Observatory is the house.",
        "Teacher is a room in the house.",
    ]:
        assert phrase in text


def test_design_defines_post_run_user_flow_and_tabs() -> None:
    text = _read(DOC)

    assert "Outcome | Learn | Models | Relations | Map | Receipts" in text
    for phrase in [
        "Flow 1: Normal Post-Run User",
        "Flow 2: Learner Mode",
        "Flow 3: Model Study",
        "Flow 4: Relation Study",
        "Flow 5: Reviewer Or Maintainer",
        "Run activation | Learning neighborhood",
    ]:
        assert phrase in text


def test_design_assigns_single_homes_to_avoid_duplicate_ui() -> None:
    text = _read(DOC)

    required_rows = [
        "| Revised answer | Outcome | Receipts, memo | Teacher lesson body |",
        (
            "| Canonical model explanation | Models | Outcome, Learn, Relations, "
            "Map | model companion chunks |"
        ),
        "| Relation explanation | Relations | Learn, Map | graph edge label only |",
        "| Graph neighborhood | Map | Outcome preview, Learn preview | separate Teacher graph app |",
        "| Source custody | Receipts | Models, Relations, Learn drawers | primary lesson copy |",
    ]
    for row in required_rows:
        assert row in text


def test_design_separates_learning_from_telemetry_and_receipts() -> None:
    text = _read(DOC)

    for phrase in [
        "The label `Telemetry` should not be the main product tab for the normal user.",
        "`/audit/*` remains advanced telemetry.",
        "It should not be renamed into Teacher.",
        "Do not make the learner decode telemetry vocabulary",
        "Receipts",
        "Advanced",
    ]:
        assert phrase in text


def test_design_proposes_selected_run_learning_packet_without_runtime_claims() -> None:
    text = _read(DOC)

    for phrase in [
        "teacher_learning_packet.v0",
        "/api/case/<id>/learning",
        "/api/case/<id>/learning/models",
        "/api/case/<id>/learning/relations",
        "/api/case/<id>/learning/graph",
        "/api/case/<id>/learning/receipts",
        "It should not call providers, run Lolla, judge answer quality, or",
        "change runtime behavior.",
    ]:
        assert phrase in text


def test_design_has_incremental_sequence_and_stop_conditions() -> None:
    text = _read(DOC)

    planned = re.findall(r"^### PR-O\d+", text, flags=re.MULTILINE)
    assert planned == [
        "### PR-O1",
        "### PR-O2",
        "### PR-O3",
        "### PR-O4",
        "### PR-O5",
        "### PR-O6",
        "### PR-O7",
    ]

    for phrase in [
        "Stop before UI changes.",
        "Stop before Observatory UI.",
        "running Lolla",
        "invoking the Lolla skill",
        "provider/model API calls",
        "changing runtime behavior",
        "claiming product proof",
        "claiming human validation",
        "claiming answer or advice correctness",
        "treating graph edges as proof",
    ]:
        assert phrase in text


def test_design_does_not_include_local_absolute_paths() -> None:
    text = _read(DOC)
    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text


def test_review_json_records_gate_and_non_claims() -> None:
    data = json.loads(_read(REVIEW))

    assert data["schema"] == (
        "lolla.mental_model_teacher_observatory_integration_design_review.v0"
    )
    assert data["artifact"] == (
        "docs/product/mental-model-teacher-observatory-integration-design-v0.md"
    )
    assert data["decision_gate"] == (
        "proceed_to_observatory_teacher_learning_packet_contract"
    )
    assert data["product_decision"]["one_shell"] == "Observatory"
    assert data["product_decision"]["teacher_position"] == (
        "selected_run_learning_mode"
    )
    assert data["product_decision"]["standalone_teacher_app"] is False
    assert data["primary_tabs"] == [
        "Outcome",
        "Learn",
        "Models",
        "Relations",
        "Map",
        "Receipts",
    ]
    assert data["single_home_rules"]["teacher_reasoning_move"] == "Learn"
    assert data["single_home_rules"]["source_custody"] == "Receipts"

    non_claims = data["non_claims"]
    assert non_claims["lolla_skill_invoked"] is False
    assert non_claims["provider_or_model_calls_used"] is False
    assert non_claims["runtime_behavior_changed"] is False
    assert non_claims["product_proof"] is False
    assert non_claims["human_validated"] is False
    assert non_claims["answer_correctness"] is False
    assert non_claims["advice_correctness"] is False
    assert non_claims["graph_edges_are_proof"] is False
