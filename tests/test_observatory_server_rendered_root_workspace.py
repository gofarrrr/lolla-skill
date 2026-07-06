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


DOC = REPO_ROOT / "docs/product/observatory-server-rendered-root-workspace-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-server-rendered-root-workspace-v0/review.json"
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


def test_workspace_uses_observatory_visual_system_and_surface_order(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert "<title>Lolla - Observatory Workspace</title>" in html
    assert "--bg: #060761" in html
    assert "--teal: #41FFA7" in html
    assert "JetBrains Mono" in html
    assert "Selected Run Workspace" in html
    assert "Start with what changed, then practice the reasoning" in html
    assert "Read outcome" in html
    assert "Practice lesson" in html
    assert 'href="/workspace?case_id=lolla-audit#learn"' in html
    status_bar = html.split('data-observatory-status-bar>', 1)[1].split("</nav>", 1)[0]
    assert "Advanced Audit" not in status_bar
    assert 'href="/audit">Advanced audit</a>' in html

    assert html.index("<h2>Outcome</h2>") < html.index("<h2>Learn</h2>")
    assert html.index("<h2>Learn</h2>") < html.index("<h2>Models</h2>")
    assert html.index("<h2>Models</h2>") < html.index("<h2>Relations</h2>")
    assert html.index("<h2>Relations</h2>") < html.index("<h2>Map</h2>")
    assert html.index("<h2>Map</h2>") < html.index("<h2>Receipts</h2>")


def test_workspace_model_chips_resolve_to_formatted_model_pages(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")
    detail = serve_result._render_workspace_model_detail_html(
        "authority-bias",
        "lolla-audit",
    )

    assert 'href="/models/authority-bias?case_id=lolla-audit"' in html
    assert (
        'href="/relations/authority-bias__first-principles-thinking__antagonist?case_id=lolla-audit"'
        in html
    )
    assert 'id="model-authority-bias"' in html
    assert "Authority Bias" in html
    assert "Information Asymmetry" in html
    assert "First Principles Thinking" in html
    assert "Model index" in html
    assert "What This Model Helps You See" in detail
    assert "Helps notice" in detail
    assert "Use when" in detail
    assert "Avoid when" in detail
    assert "Practice prompts" in detail
    assert "canonical_model_markdown" in detail
    assert 'href="#model-authority-bias"' not in html


def test_workspace_relation_story_comes_before_taxonomy_and_confidence(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")
    detail = serve_result._render_workspace_relation_detail_html(
        "authority-bias__first-principles-thinking__antagonist",
        "lolla-audit",
    )

    assert (
        'id="relation-authority-bias__first-principles-thinking__antagonist"'
        in html
    )
    assert "Relation story" in html
    story_index = detail.index(
        "First principles thinking strips away inherited doctrine"
    )
    taxonomy_index = detail.index("<h3>Taxonomy</h3>")
    confidence_index = detail.index("confidence: medium")

    assert story_index < taxonomy_index < confidence_index
    assert "Edges are navigation, not proof" in html
    assert "confidence is not certification" in detail


def test_product_workspace_api_route_returns_valid_adapter_payload(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    with _served_observatory() as base_url:
        with urllib.request.urlopen(
            f"{base_url}/api/case/lolla-audit/product-workspace",
            timeout=3,
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))

    assert response.status == 200
    assert payload["available"] is True
    assert payload["workspace"]["rendering_direction"] == (
        "portable_python_server_rendered_html"
    )
    assert payload["workspace"]["primary_surfaces"] == [
        "Outcome",
        "Learn",
        "Models",
        "Relations",
        "Map",
        "Receipts",
    ]
    assert payload["workspace"]["receipt_summary"]["process_brief_status"] == (
        "not_requested"
    )
    assert payload["adapter_guards"]["provider_or_model_calls"] is False
    assert payload["adapter_guards"]["runtime_behavior_changed"] is False


def test_root_route_renders_workspace_and_legacy_spa_route_remains(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    with _served_observatory() as base_url:
        with urllib.request.urlopen(f"{base_url}/", timeout=3) as response:
            root_html = response.read().decode("utf-8")
        with urllib.request.urlopen(f"{base_url}/index.html", timeout=3) as response:
            index_html = response.read().decode("utf-8")

    assert "Selected Run Workspace" in root_html
    assert "Authority Bias" in root_html
    assert "telemetry-fab" not in root_html
    assert "telemetry-fab" in index_html
    assert "lolla-selected-run-custody-panel" in index_html


def test_workspace_docs_review_and_readme_record_boundaries() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    assert "Observatory Server Rendered Root Workspace" in readme
    assert "observatory-server-rendered-root-workspace-v0.md" in readme

    for phrase in [
        "/api/case/<id>/product-workspace",
        "root / and /workspace",
        "Outcome -> Learn -> Models -> Relations -> Map -> Receipts",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not edit observatory/build",
        "proceed_to_observatory_workspace_navigation_source_of_truth",
    ]:
        assert phrase in doc

    assert review["decision_gate"] == (
        "proceed_to_observatory_workspace_navigation_source_of_truth"
    )
    assert review["implemented"]["root_workspace_route"] == "/"
    assert review["implemented"]["workspace_route"] == "/workspace"
    assert review["implemented"]["product_workspace_api"] == (
        "/api/case/<id>/product-workspace"
    )
    assert review["implemented"]["legacy_spa_route"] == "/index.html"
    assert review["ux_guards"]["outcome_first"] is True
    assert review["ux_guards"]["model_cards_are_formatted_pages"] is True
    assert review["ux_guards"]["relation_story_before_taxonomy"] is True
    assert review["boundary"]["compiled_spa_bundle_changed"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["runtime_behavior_changed"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False


def test_workspace_docs_and_review_are_clean() -> None:
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
