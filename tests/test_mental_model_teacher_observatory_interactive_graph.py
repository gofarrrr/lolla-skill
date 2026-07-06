import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

import serve_result  # noqa: E402


DOC = REPO_ROOT / "docs/product/mental-model-teacher-observatory-interactive-graph-v0.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/mental-model-teacher-observatory-interactive-graph-v0/review.json"
)
README = REPO_ROOT / "docs/product/README.md"


def _install_launch_case() -> None:
    serve_result._RESULT = {"usage_summary": {"run_id": "20260627T104146Z_7bfe79"}}
    serve_result._RESULT_PATH = None
    serve_result._CASE_ID = "lolla-audit"
    serve_result._CASE_NAME = "Lolla Audit"


def test_interactive_graph_renders_observatory_native_workbench() -> None:
    _install_launch_case()

    html = serve_result._render_teacher_learning_html("lolla-audit")

    assert 'class="graph-workbench"' in html
    assert "data-teacher-graph" in html
    assert 'data-default-focus="authority-bias"' in html
    assert "data-graph-search" in html
    assert "Search model, role, or id" in html
    assert "data-graph-results" in html
    assert "data-graph-selection" in html
    assert "map-edge-hitbox" in html
    assert "lolla-teacher-graph-interaction" in html


def test_interactive_graph_exposes_filterable_nodes_and_edges() -> None:
    _install_launch_case()

    html = serve_result._render_teacher_learning_html("lolla-audit")

    assert html.count("data-graph-node ") == 3
    assert html.count("data-graph-edge ") == 1
    assert 'data-relation-filter="all"' in html
    assert 'data-relation-filter="antagonist"' in html
    assert 'data-relation-type="antagonist"' in html
    assert 'data-model-id="authority-bias"' in html
    assert 'data-source-id="authority-bias"' in html
    assert 'data-target-id="first-principles-thinking"' in html


def test_interactive_graph_click_targets_resolve_to_existing_drawers() -> None:
    _install_launch_case()

    html = serve_result._render_teacher_learning_html("lolla-audit")

    relation_anchor = (
        "relation-authority-bias__first-principles-thinking__antagonist"
    )
    assert 'href="#model-authority-bias"' in html
    assert 'id="model-authority-bias"' in html
    assert f'href="#{relation_anchor}"' in html
    assert f'id="{relation_anchor}"' in html
    assert "Open model detail" in html
    assert "Open relation detail" in html
    assert "#map" in html
    assert "dataset.returnHash" in html


def test_interactive_graph_keeps_graph_as_navigation_not_proof() -> None:
    _install_launch_case()

    html = serve_result._render_teacher_learning_html("lolla-audit")

    assert "edges are navigation, not proof" in html
    assert "confidence is not certification" in html
    assert "artifact_refs" not in html
    assert "usage_summary" not in html
    assert "audit_summary" not in html
    assert "not_answer_correctness" in html
    assert "not_advice_correctness" in html


def test_interactive_graph_docs_review_and_readme_capture_gate_and_boundaries() -> None:
    doc = DOC.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    readme = README.read_text(encoding="utf-8")

    assert "mental-model-teacher-observatory-interactive-graph-v0.md" in readme
    assert review["decision_gate"] == "proceed_to_compiled_observatory_learn_source_port"
    assert review["ux_guards"]["offline_graph_interaction"] is True
    assert review["ux_guards"]["node_search"] is True
    assert review["ux_guards"]["relation_type_filters"] is True
    assert review["ux_guards"]["selected_node_edge_panel"] is True
    assert review["non_claims"]["graph_edges_are_proof"] is False
    for phrase in [
        "offline interactive lesson graph",
        "node search",
        "relation-type filters",
        "selected node or edge panel",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "proceed_to_compiled_observatory_learn_source_port",
    ]:
        assert phrase in doc


def test_interactive_graph_docs_and_review_are_clean() -> None:
    text = DOC.read_text(encoding="utf-8") + REVIEW.read_text(encoding="utf-8")

    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "product_proof\": true" not in text
    assert "human_validated\": true" not in text
    assert "runtime_integration_authorized\": true" not in text
