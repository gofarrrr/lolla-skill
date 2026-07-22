import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = (
    REPO_ROOT
    / "docs/product/mental-model-teacher-observatory-ownership-portability-boundary-v0.md"
)
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/mental-model-teacher-observatory-ownership-portability-boundary-v0/review.json"
)
README = REPO_ROOT / "docs/product/README.md"
INTERACTIVE_GRAPH_DOC = (
    REPO_ROOT / "docs/product/mental-model-teacher-observatory-interactive-graph-v0.md"
)


def test_boundary_doc_records_current_observatory_owner() -> None:
    doc = DOC.read_text(encoding="utf-8")
    normalized = " ".join(doc.split())

    for phrase in [
        "Decision gate: `keep_teacher_learn_server_rendered_until_source_owner_verified`",
        "do not port Teacher Learn into a compiled",
        "current Observatory owner is the portable local Python server",
        "observatory/serve_result.py",
        "observatory/build/",
        "Legacy bundle authoring source",
        "no root `package.json`",
        "no local `vite.config.*`",
        "no local `svelte.config.*`",
        "finalize_and_archive.sh -> scripts/skill/launch_observatory.py -> observatory/serve_result.py",
        "Teacher Learn should become a first-class learning mode inside Observatory",
        "Telemetry should remain a separate explanation mode",
        "raw `audit_summary`",
        "raw `usage_summary`",
        "proceed_to_teacher_learn_information_architecture_revision",
    ]:
        assert phrase in normalized


def test_repo_shape_matches_boundary_doc_claim() -> None:
    assert (REPO_ROOT / "observatory/serve_result.py").is_file()
    assert (REPO_ROOT / "observatory/build/index.html").is_file()

    frontend_source_markers = [
        REPO_ROOT / "package.json",
        REPO_ROOT / "observatory/package.json",
        REPO_ROOT / "observatory/svelte-app/package.json",
        REPO_ROOT / "vite.config.js",
        REPO_ROOT / "vite.config.ts",
        REPO_ROOT / "svelte.config.js",
        REPO_ROOT / "svelte.config.ts",
        REPO_ROOT / "observatory/vite.config.js",
        REPO_ROOT / "observatory/vite.config.ts",
        REPO_ROOT / "observatory/svelte.config.js",
        REPO_ROOT / "observatory/svelte.config.ts",
    ]

    assert all(not marker.exists() for marker in frontend_source_markers)


def test_review_receipt_records_no_source_port_or_runtime_change() -> None:
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    assert (
        review["decision_gate"]
        == "keep_teacher_learn_server_rendered_until_source_owner_verified"
    )
    assert (
        review["recommended_next_gate"]
        == "proceed_to_teacher_learn_information_architecture_revision"
    )
    assert review["ownership_decision"]["current_owner"] == "observatory/serve_result.py"
    assert review["ownership_decision"]["compiled_bundle_is_source_of_truth"] is False
    assert review["ownership_decision"]["external_svelte_source_verified"] is False
    assert review["ownership_decision"]["source_port_authorized_by_this_slice"] is False
    assert review["ownership_decision"]["runtime_wiring_allowed"] is False
    assert review["evidence"]["local_frontend_source_tree_present"] is False
    assert review["information_flow_decision"]["teacher_learn_is_product_learning_mode"] is True
    assert review["information_flow_decision"]["telemetry_is_separate_explanation_mode"] is True
    assert review["information_flow_decision"]["duplicate_teacher_app_allowed"] is False
    assert review["non_claims"]["runtime_behavior_changed"] is False
    assert review["non_claims"]["compiled_spa_changed"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["answer_correctness"] is False
    assert review["non_claims"]["advice_correctness"] is False
    assert review["non_claims"]["action_authorized"] is False


def test_readme_and_previous_graph_doc_point_to_boundary_correction() -> None:
    readme = README.read_text(encoding="utf-8")
    graph_doc = INTERACTIVE_GRAPH_DOC.read_text(encoding="utf-8")

    assert "mental-model-teacher-observatory-ownership-portability-boundary-v0.md" in readme
    assert "Current ownership note" in graph_doc
    assert "superseded by" in graph_doc
    assert "source-owner verification question" in graph_doc
    assert "not the default next implementation path" in graph_doc


def test_boundary_docs_and_review_are_clean() -> None:
    text = (
        DOC.read_text(encoding="utf-8")
        + REVIEW.read_text(encoding="utf-8")
        + INTERACTIVE_GRAPH_DOC.read_text(encoding="utf-8")
    )

    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "product_proof\": true" not in text
    assert "human_validated\": true" not in text
    assert "answer_correctness\": true" not in text
    assert "advice_correctness\": true" not in text
    assert "action_authorized\": true" not in text
    assert "runtime_integration_authorized\": true" not in text
