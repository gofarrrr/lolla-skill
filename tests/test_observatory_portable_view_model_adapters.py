import copy
import json
from pathlib import Path

import pytest

from engine.system_b.mental_model_teacher_observatory_packet_adapter import (
    build_teacher_learning_response,
)
from observatory.product_view_adapters import (
    OBSERVATORY_PRODUCT_VIEW_ADAPTER_SCHEMA_VERSION,
    ObservatoryProductViewAdapterError,
    build_observatory_product_view_response,
)
from observatory.product_views import (
    PORTABLE_RENDERING_DIRECTION,
    PRIMARY_SURFACES,
    WORKSPACE_SCHEMA_VERSION,
    validate_workspace,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/product/observatory-portable-view-model-adapters-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-portable-view-model-adapters-v0/review.json"
)


def _launch_result(run_id: str = "20260627T104146Z_7bfe79") -> dict:
    return {
        "usage_summary": {"run_id": run_id},
        "extraction": {
            "decision_situation": "A public enterprise beta launch is being reviewed."
        },
        "run_health": {"overall": "healthy", "issues": []},
        "revised_answer": (
            "Launch in stages after the support risk is made explicit. "
            "Keep the first cohort narrow and treat the beta as a learning gate."
        ),
        "delta_card": {
            "top_findings": [
                {
                    "description": (
                        "Authority pressure was doing too much work in the launch plan."
                    )
                }
            ]
        },
    }


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_result_path(run_dir: Path, result: dict) -> Path:
    result_path = run_dir / "result.json"
    _write_json(result_path, result)
    return result_path


def _write_decision_work_sidecar(run_dir: Path) -> None:
    sidecar = run_dir / "decision_work"
    _write_json(
        sidecar / "attachment_status.json",
        {
            "schema_version": "lolla.decision_work_brief_runtime_attachment_status.v0",
            "attachment_state": "generated",
            "generated_artifacts": {
                "attachment_status": "decision_work/attachment_status.json",
                "user_receipt": "decision_work/user_receipt.md",
            },
            "missing_artifacts": {},
            "blocked_reasons": [],
            "deferred_reasons": [],
            "custody_flags": {
                "model_calls": 0,
                "runtime_behavior_changed": False,
                "archive_mutated": False,
                "agent_action_authorized": False,
                "automatic_action_authorized": False,
            },
            "non_claims": ["not_product_proof", "not_human_validation"],
        },
    )
    (sidecar / "user_receipt.md").write_text(
        (
            "Decision Work Brief: available\n\n"
            "What changed: the launch path became narrower.\n\n"
            "Main caveat: not proof that the advice is correct.\n"
        ),
        encoding="utf-8",
    )


def test_adapter_builds_valid_workspace_from_existing_teacher_packet() -> None:
    response = build_observatory_product_view_response(
        selected_case_id="archive:launch-public-enterprise-beta:20260627T104146Z_7bfe79",
        result=_launch_result(),
    )

    assert response["schema_version"] == OBSERVATORY_PRODUCT_VIEW_ADAPTER_SCHEMA_VERSION
    assert response["available"] is True
    assert response["workspace_schema"] == WORKSPACE_SCHEMA_VERSION
    assert response["adapter_guards"]["read_only"] is True
    assert response["adapter_guards"]["provider_or_model_calls"] is False
    assert response["adapter_guards"]["runtime_behavior_changed"] is False
    assert response["adapter_guards"]["ui_rendering_added"] is False

    workspace = validate_workspace(response["workspace"])
    assert workspace["rendering_direction"] == PORTABLE_RENDERING_DIRECTION
    assert workspace["primary_surfaces"] == list(PRIMARY_SURFACES)
    assert workspace["selected_run_summary"]["health_label"] == "ok"
    assert workspace["outcome_summary"]["strongest_pressure"] == (
        "Authority pressure was doing too much work in the launch plan."
    )
    assert workspace["outcome_value"]["plain_language_answer"] == (
        "Launch in stages after the support risk is made explicit. "
        "Keep the first cohort narrow and treat the beta as a learning gate."
    )
    assert workspace["outcome_value"]["stance"] == "stage_or_gate"
    assert workspace["outcome_value"]["what_changed"] == [
        "The run made this pressure explicit: Authority pressure was doing too much work in the launch plan."
    ]
    assert workspace["outcome_value"]["recommended_next_moves"][2]["label"] == (
        "Download MD"
    )
    assert (
        workspace["outcome_value"]["recommended_next_moves"][2]["href"]
        == "/api/case/archive%3Alaunch-public-enterprise-beta%3A20260627T104146Z_7bfe79/conversation-memory.md?include_raw_conversation=1"
    )
    assert workspace["learning_packet"]["thinking_move"] == (
        "Ask what evidence remains if the authority signal is removed."
    )
    assert workspace["receipt_summary"]["process_brief_status"] == "not_requested"
    assert workspace["receipt_summary"]["conversation_understanding_status"] == (
        "available"
    )
    assert len(workspace["model_pages"]) == 3
    assert workspace["model_pages"][0]["source_refs"][0]["source_type"] == (
        "canonical_model_markdown"
    )
    assert workspace["relation_pages"][0]["relation_type"] == "antagonist"
    assert workspace["graph_neighborhood"]["edges"][0]["href"].startswith(
        "/relations/"
    )


def test_adapter_routes_models_relations_and_graph_without_raw_review_hrefs() -> None:
    workspace = build_observatory_product_view_response(
        selected_case_id="archive:launch-public-enterprise-beta:20260627T104146Z_7bfe79",
        result=_launch_result(),
    )["workspace"]

    assert all(
        link["href"].startswith("/models/")
        for link in workspace["learning_packet"]["model_links"]
    )
    assert all(
        link["href"].startswith("/relations/")
        for link in workspace["learning_packet"]["relation_links"]
    )
    assert all(
        node["href"].startswith("/models/")
        for node in workspace["graph_neighborhood"]["nodes"]
    )
    assert all(
        edge["href"].startswith("/relations/")
        for edge in workspace["graph_neighborhood"]["edges"]
    )
    rendered = json.dumps(workspace["graph_neighborhood"], sort_keys=True)
    assert "../../../../reviews" not in rendered
    assert '"affinity"' not in rendered
    assert '"rank"' not in rendered
    assert '"embedding_similarity"' not in rendered


def test_adapter_returns_unavailable_without_faking_workspace_for_missing_packet() -> None:
    response = build_observatory_product_view_response(
        selected_case_id="archive:unknown-case:20260101T000000Z_missing",
        result={"usage_summary": {"run_id": "20260101T000000Z_missing"}},
    )

    assert response["available"] is False
    assert response["workspace"] is None
    assert response["unavailable_reason"] == (
        "no_teacher_learning_packet_for_selected_case"
    )
    assert response["missingness"]["status"] == "missing"
    assert "teacher_learning_packet" in response["missingness"]["missing_fields"]
    assert response["adapter_guards"]["read_only"] is True


def test_adapter_maps_decision_work_sidecar_into_receipts_without_local_paths(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "archive/launch-public-enterprise-beta/20260627T104146Z_7bfe79"
    result = _launch_result()
    result_path = _write_result_path(run_dir, result)
    _write_decision_work_sidecar(run_dir)

    response = build_observatory_product_view_response(
        selected_case_id="archive:launch-public-enterprise-beta:20260627T104146Z_7bfe79",
        result=result,
        result_path=result_path,
    )
    workspace = validate_workspace(response["workspace"])

    receipts = workspace["receipt_summary"]
    assert receipts["process_brief_status"] == "available"
    assert receipts["conversation_understanding_status"] == "available"
    assert any(
        ref["path"] == "decision_work/user_receipt.md"
        for ref in receipts["source_refs"]
    )
    advanced = workspace["advanced_audit_index"]
    assert any(
        item["artifact_id"] == "decision-work-user_receipt"
        and item["status"] == "available"
        for item in advanced["artifact_statuses"]
    )

    rendered = json.dumps(response, sort_keys=True)
    assert str(tmp_path) not in rendered
    assert "/" + "Users/" not in rendered
    assert "Desktop/" + "Apps" not in rendered


def test_adapter_preserves_missingness_when_revised_answer_is_absent() -> None:
    result = _launch_result()
    result.pop("revised_answer")

    workspace = build_observatory_product_view_response(
        selected_case_id="archive:launch-public-enterprise-beta:20260627T104146Z_7bfe79",
        result=result,
    )["workspace"]

    assert "revised_answer" in workspace["outcome_summary"]["missingness"][
        "missing_fields"
    ]
    assert "revised_answer" in workspace["missingness"]["missing_fields"]
    assert workspace["outcome_summary"]["revised_answer_summary"] == (
        "No revised answer artifact is available for this selected run."
    )
    assert "revised_answer" in workspace["outcome_value"]["missingness"][
        "missing_fields"
    ]
    assert workspace["outcome_value"]["stance"] == "missing_revised_answer"
    assert workspace["outcome_value"]["plain_language_answer"] == (
        "No revised answer artifact is available for this selected run."
    )


def test_adapter_rejects_invalid_composed_workspace_from_unsafe_graph_label() -> None:
    teacher_response = build_teacher_learning_response(
        "archive:launch-public-enterprise-beta:20260627T104146Z_7bfe79",
        _launch_result(),
    )
    teacher_response = copy.deepcopy(teacher_response)
    teacher_response["tab_payloads"]["Map"]["graph"]["edges"][0]["label"] = (
        "proves the correct relation"
    )

    with pytest.raises(ObservatoryProductViewAdapterError, match="proof"):
        build_observatory_product_view_response(
            selected_case_id=(
                "archive:launch-public-enterprise-beta:20260627T104146Z_7bfe79"
            ),
            result=_launch_result(),
            teacher_learning_response=teacher_response,
        )


def test_adapter_docs_review_and_readme_preserve_stop_line_and_boundary() -> None:
    doc = " ".join(DOC.read_text(encoding="utf-8").split())
    readme = README.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    assert "Observatory Portable View Model Adapters" in readme
    assert "observatory-portable-view-model-adapters-v0.md" in readme

    for phrase in [
        "does not render UI",
        "does not fake a workspace",
        "root workspace rendering",
        "compiled bundle edits",
        "proceed_to_observatory_server_rendered_root_workspace",
    ]:
        assert phrase in doc

    assert review["decision_gate"] == (
        "proceed_to_observatory_server_rendered_root_workspace"
    )
    assert review["adapter_module"] == "observatory/product_view_adapters.py"
    assert review["adapter_guards"]["read_only"] is True
    assert review["adapter_guards"]["provider_or_model_calls"] is False
    assert review["adapter_guards"]["runtime_behavior_changed"] is False
    assert review["adapter_guards"]["ui_rendering_added"] is False
    assert review["boundary"]["serve_result_routes_changed"] is False
    assert review["boundary"]["compiled_js_or_css_edited"] is False
    assert review["unavailable_policy"]["workspace_faked_when_teacher_packet_missing"] is (
        False
    )
    assert review["single_home_rules"]["canonical_model_explanation"] == "Models"
    assert review["single_home_rules"]["raw_telemetry"] == "Advanced Audit"
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["graph_edges_are_proof"] is False


def test_adapter_outputs_do_not_include_local_paths_or_authority_claims() -> None:
    response = build_observatory_product_view_response(
        selected_case_id="archive:launch-public-enterprise-beta:20260627T104146Z_7bfe79",
        result=_launch_result(),
    )
    text = (
        json.dumps(response, sort_keys=True)
        + DOC.read_text(encoding="utf-8")
        + REVIEW.read_text(encoding="utf-8")
    )

    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "product_proof\": true" not in text
    assert "human_validated\": true" not in text
    assert "answer_correctness\": true" not in text
    assert "advice_correctness\": true" not in text
    assert "runtime_integration_authorized\": true" not in text
    assert "action_authorized\": true" not in text
    assert "svelte_revival_authorized\": true" not in text
