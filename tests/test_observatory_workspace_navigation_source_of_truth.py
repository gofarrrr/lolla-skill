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


DOC = REPO_ROOT / "docs/product/observatory-workspace-navigation-source-of-truth-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-workspace-navigation-source-of-truth-v0/review.json"
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


def test_route_helpers_keep_one_observatory_navigation_source() -> None:
    assert serve_result._observatory_workspace_href("lolla-audit", "models") == (
        "/workspace?case_id=lolla-audit#models"
    )
    assert serve_result._observatory_workspace_href("case with space", "learn") == (
        "/workspace?case_id=case%20with%20space#learn"
    )
    assert serve_result._observatory_model_href("authority-bias", "lolla-audit") == (
        "/models/authority-bias?case_id=lolla-audit"
    )
    assert serve_result._observatory_relation_href(
        "authority-bias__first-principles-thinking__antagonist",
        "lolla-audit",
    ) == (
        "/relations/authority-bias__first-principles-thinking__antagonist?case_id=lolla-audit"
    )
    assert serve_result._observatory_product_link_href(
        "/models/authority-bias",
        "lolla-audit",
    ) == "/models/authority-bias?case_id=lolla-audit"


def test_workspace_links_use_durable_model_and_relation_routes(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert 'href="/models/authority-bias?case_id=lolla-audit"' in html
    assert (
        'href="/relations/authority-bias__first-principles-thinking__antagonist?case_id=lolla-audit"'
        in html
    )
    assert 'href="#model-authority-bias"' not in html
    assert 'href="#relation-authority-bias__first-principles-thinking__antagonist"' not in html
    assert 'id="model-authority-bias"' in html
    assert 'id="relation-authority-bias__first-principles-thinking__antagonist"' in html


def test_model_detail_route_returns_formatted_selected_run_page(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    with _served_observatory() as base_url:
        with urllib.request.urlopen(
            f"{base_url}/models/authority-bias?case_id=lolla-audit",
            timeout=3,
        ) as response:
            html = response.read().decode("utf-8")

    assert response.status == 200
    assert "<title>Lolla - Authority Bias</title>" in html
    assert "<h1>Authority Bias</h1>" in html
    assert "Everything We Know" in html
    assert "Helps notice" in html
    assert "Use when" in html
    assert "Source custody" in html
    assert "All models in this run" in html
    assert 'href="/workspace?case_id=lolla-audit#models"' in html
    assert "raw canonical Markdown and curation internals stay behind" in html


def test_relation_detail_route_keeps_story_before_taxonomy(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    relation_id = "authority-bias__first-principles-thinking__antagonist"
    with _served_observatory() as base_url:
        with urllib.request.urlopen(
            f"{base_url}/relations/{relation_id}?case_id=lolla-audit",
            timeout=3,
        ) as response:
            html = response.read().decode("utf-8")

    assert response.status == 200
    assert "<title>Lolla - Authority Bias and First Principles Thinking</title>" in html
    story_index = html.index(
        "First principles thinking strips away inherited doctrine"
    )
    taxonomy_index = html.index("<h3>Taxonomy</h3>")
    confidence_index = html.index("confidence: medium")

    assert story_index < taxonomy_index < confidence_index
    assert "confidence is not certification" in html
    assert 'href="/models/authority-bias?case_id=lolla-audit"' in html
    assert 'href="/workspace?case_id=lolla-audit#relations"' in html


def test_navigation_source_of_truth_docs_review_and_readme_record_boundaries() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    assert "Observatory Workspace Navigation Source Of Truth" in readme
    assert "observatory-workspace-navigation-source-of-truth-v0.md" in readme

    for phrase in [
        "shared Observatory route helpers",
        "/models/<id>?case_id=<selected-case-id>",
        "/relations/<id>?case_id=<selected-case-id>",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not edit observatory/build",
        "proceed_to_observatory_workspace_map_interaction_slice",
    ]:
        assert phrase in doc

    assert review["decision_gate"] == (
        "proceed_to_observatory_workspace_map_interaction_slice"
    )
    assert review["implemented"]["shared_route_helpers"] is True
    assert review["implemented"]["model_route"] == "/models/<id>?case_id=<id>"
    assert review["implemented"]["relation_route"] == "/relations/<id>?case_id=<id>"
    assert review["ux_guards"]["model_clickthrough_is_durable_url"] is True
    assert review["ux_guards"]["relation_story_before_taxonomy"] is True
    assert review["boundary"]["compiled_spa_bundle_changed"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["runtime_behavior_changed"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False


def test_navigation_source_docs_and_review_are_clean() -> None:
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
