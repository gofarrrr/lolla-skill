from __future__ import annotations

import json
import socket
import sys
import threading
import urllib.request
from contextlib import closing
from http.server import HTTPServer
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

import serve_result  # noqa: E402


DOC = REPO_ROOT / "docs/product/observatory-workspace-map-interaction-slice-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-workspace-map-interaction-slice-v0/review.json"
)


def _install_launch_case(monkeypatch) -> None:
    monkeypatch.setattr(
        serve_result,
        "_RESULT",
        {
            "usage_summary": {"run_id": "20260627T104146Z_7bfe79"},
            "extraction": {
                "decision_situation": (
                    "A public enterprise beta launch is being reviewed."
                )
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
        },
    )
    monkeypatch.setattr(serve_result, "_RESULT_PATH", None)
    monkeypatch.setattr(serve_result, "_CASE_ID", "lolla-audit")
    monkeypatch.setattr(serve_result, "_CASE_NAME", "Lolla Audit")


def test_workspace_map_renders_interactive_observatory_workbench(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert 'class="graph-workbench workspace-graph-workbench"' in html
    assert "data-observatory-graph" in html
    assert 'data-graph-navigation="select"' in html
    assert 'data-default-focus="authority-bias"' in html
    assert "data-graph-search" in html
    assert "Search model, role, or id" in html
    assert "data-graph-reset" in html
    assert "Reset" in html
    assert "data-graph-filter-note" in html
    assert "Search and relation filters combine" in html
    assert "data-graph-results" in html
    assert "data-graph-selection" in html
    assert "lolla-teacher-graph-interaction" in html


def test_workspace_map_exposes_filterable_nodes_and_edges(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert html.count("data-graph-node ") == 3
    assert html.count("data-graph-edge ") == 1
    assert 'data-relation-filter="all"' in html
    assert 'data-relation-filter="antagonist"' in html
    assert 'data-relation-type="antagonist"' in html
    assert 'data-model-id="authority-bias"' in html
    assert 'data-source-id="authority-bias"' in html
    assert 'data-target-id="first-principles-thinking"' in html


def test_workspace_map_uses_durable_product_page_links(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    relation_path = (
        "/relations/authority-bias__first-principles-thinking__antagonist"
        "?case_id=lolla-audit"
    )
    assert 'href="/models/authority-bias?case_id=lolla-audit"' in html
    assert f'href="{relation_path}"' in html
    assert '<a class="graph-selection-link" data-selection-link href="/models/authority-bias?case_id=lolla-audit">' in html
    assert "Open model detail" in html
    assert "Open relation detail" in html


def test_workspace_map_script_supports_select_before_open_behavior(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert 'graphRootSelector = "[data-observatory-graph]"' in html
    assert 'root.dataset.graphNavigation === "select"' in html
    assert "if (selectOnly) event.preventDefault();" in html
    assert "No relation is visible with the current search or filter" in html
    assert "Reset filters to return to the full lesson map" in html


def test_workspace_map_keeps_graph_as_navigation_not_proof(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")
    detail = serve_result._render_workspace_relation_detail_html(
        "authority-bias__first-principles-thinking__antagonist",
        "lolla-audit",
    )

    assert "Edges are navigation, not proof" in html
    assert "confidence is not certification" in detail
    assert "not_product_proof" in html
    assert "not_answer_correctness" in html
    assert "not_advice_correctness" in html
    assert "human_validated" not in html


def test_workspace_map_route_returns_html_with_interactive_graph(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    with _served_observatory() as base_url:
        with urllib.request.urlopen(
            f"{base_url}/workspace?case_id=lolla-audit#map",
            timeout=3,
        ) as response:
            html = response.read().decode("utf-8")

    assert response.status == 200
    assert "<title>Lolla - Observatory Workspace</title>" in html
    assert "data-observatory-graph" in html
    assert "Interactive Observatory selected-run model map" in html


def test_workspace_map_docs_review_and_readme_record_boundaries() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    assert "Observatory Workspace Map Interaction Slice" in readme
    assert "observatory-workspace-map-interaction-slice-v0.md" in readme

    for phrase in [
        "interactive selected-run Map",
        "node search",
        "relation-type filters",
        "selected node or edge panel",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "proceed_to_observatory_workspace_product_flow_review",
    ]:
        assert phrase in doc

    assert review["decision_gate"] == (
        "proceed_to_observatory_workspace_product_flow_review"
    )
    assert review["implemented"]["interactive_workspace_map"] is True
    assert review["ux_guards"]["node_search"] is True
    assert review["ux_guards"]["relation_type_filters"] is True
    assert review["ux_guards"]["selected_node_edge_panel"] is True
    assert review["ux_guards"]["graph_edges_are_navigation_not_proof"] is True
    assert review["boundary"]["compiled_spa_bundle_changed"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["runtime_behavior_changed"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False


def test_workspace_map_docs_and_review_are_clean() -> None:
    text = DOC.read_text(encoding="utf-8") + REVIEW.read_text(encoding="utf-8")

    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "product_proof\": true" not in text
    assert "human_validated\": true" not in text
    assert "answer_correctness\": true" not in text
    assert "advice_correctness\": true" not in text
    assert "runtime_integration_authorized\": true" not in text
    assert "action_authorized\": true" not in text


class _served_observatory:
    def __enter__(self) -> str:
        self.httpd = HTTPServer(
            ("127.0.0.1", _free_port()),
            serve_result.ResultHandler,
        )
        host, port = self.httpd.server_address
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        return f"http://{host}:{port}"

    def __exit__(self, exc_type, exc, tb) -> None:
        self.httpd.shutdown()
        self.thread.join(timeout=2)
        self.httpd.server_close()


def _free_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])
