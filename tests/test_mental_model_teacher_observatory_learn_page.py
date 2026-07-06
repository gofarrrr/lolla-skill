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


DOC = REPO_ROOT / "docs/product/mental-model-teacher-observatory-learn-page-v0.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/mental-model-teacher-observatory-learn-page-v0/review.json"
)
README = REPO_ROOT / "docs/product/README.md"


def _install_launch_case(monkeypatch) -> None:
    monkeypatch.setattr(
        serve_result,
        "_RESULT",
        {"usage_summary": {"run_id": "20260627T104146Z_7bfe79"}},
    )
    monkeypatch.setattr(serve_result, "_RESULT_PATH", None)
    monkeypatch.setattr(serve_result, "_CASE_ID", "lolla-audit")
    monkeypatch.setattr(serve_result, "_CASE_NAME", "Lolla Audit")


def test_server_rendered_learn_page_has_clear_narrative_order(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_teacher_learning_html("lolla-audit")

    assert "<h1>Learn</h1>" in html
    assert "Case is the anchor" in html
    assert "The Lesson" in html
    assert "Thinking move:" in html
    assert "Model Stack" in html
    assert "Practice Rep" in html
    assert "Do Not Overlearn" in html
    assert "Models" in html
    assert "Relation" in html
    assert "Map" in html
    assert "Receipts" in html
    assert "Non-Claims" in html
    assert html.index("<h2>The Lesson</h2>") < html.index("<h2>Models</h2>")
    assert html.index("<h2>Models</h2>") < html.index("<h2>Relation</h2>")
    assert html.index("<h2>Relation</h2>") < html.index("<h2>Map</h2>")
    assert html.index("<h2>Map</h2>") < html.index("<h2>Receipts</h2>")


def test_learn_page_uses_canonical_model_names_and_lesson_practice_label(
    monkeypatch,
) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_teacher_learning_html("lolla-audit")

    assert "Authority Bias" in html
    assert "Information Asymmetry" in html
    assert "First Principles Thinking" in html
    assert "Test The Authority, Not The Aura" in html
    assert "<h3>Test The Authority, Not The Aura</h3>" not in html


def test_learn_page_shows_relation_story_before_relation_taxonomy(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_teacher_learning_html("lolla-audit")

    story_index = html.index(
        "First principles thinking strips away inherited doctrine"
    )
    taxonomy_index = html.index("confidence: medium")
    assert story_index < taxonomy_index
    assert "Edges are navigation, not proof" in html
    assert "Graph is navigation" not in html


def test_learn_page_keeps_receipts_and_nonclaims_visible_but_late(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_teacher_learning_html("lolla-audit")

    assert "Source refs:" in html
    assert "Artifact refs:" in html
    assert "not_answer_correctness" in html
    assert "not_advice_correctness" in html
    assert "not_runtime_integration" in html
    assert "artifact_refs" not in html
    assert "usage_summary" not in html
    assert "audit_summary" not in html


def test_teacher_learning_route_returns_html(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    with _served_observatory() as base_url:
        with urllib.request.urlopen(f"{base_url}/teacher-learning", timeout=3) as response:
            html = response.read().decode("utf-8")

    assert response.status == 200
    assert "<title>Lolla — Learn</title>" in html
    assert "<h1>Learn</h1>" in html
    assert "Authority Bias" in html
    assert "Teacher reasoning move lives in Learn" in html


def test_root_injection_adds_learn_and_telemetry_affordances() -> None:
    rendered = serve_result._inject_telemetry_fab(b"<html><body></body></html>").decode(
        "utf-8"
    )
    rendered_again = serve_result._inject_telemetry_fab(rendered.encode("utf-8")).decode(
        "utf-8"
    )

    assert 'href="/teacher-learning"' in rendered
    assert 'class="learn-fab"' in rendered
    assert 'class="telemetry-fab"' in rendered
    assert "Case Surfaces" in rendered
    assert 'href="/teacher-learning#models"' in rendered
    assert 'href="/teacher-learning#relations"' in rendered
    assert 'href="/teacher-learning#map"' in rendered
    assert 'href="/teacher-learning#receipts"' in rendered
    assert rendered_again.count('class="learn-fab"') == 1
    assert rendered_again.count('class="telemetry-fab"') == 1


def test_learn_status_bar_uses_shared_workspace_navigation(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_teacher_learning_html("lolla-audit")

    assert 'aria-label="Observatory surfaces"' in html
    assert 'href="/">Outcome</a>' in html
    assert 'aria-current="page">Learn</a>' in html
    assert 'href="/teacher-learning#models">Models</a>' in html
    assert 'href="/teacher-learning#relations">Relations</a>' in html
    assert 'href="/teacher-learning#map">Map</a>' in html
    assert 'href="/teacher-learning#receipts">Receipts</a>' in html
    assert 'href="/audit">Audit</a>' in html


def test_learn_page_docs_review_and_readme_preserve_boundaries() -> None:
    doc = DOC.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    readme = README.read_text(encoding="utf-8")

    assert "mental-model-teacher-observatory-learn-page-v0.md" in readme
    assert review["decision_gate"] == (
        "proceed_to_compiled_observatory_learn_tab_integration"
    )
    assert review["ux_guards"]["lesson_narrative_first"] is True
    assert review["ux_guards"]["relation_story_before_taxonomy"] is True
    assert review["ux_guards"]["receipts_after_learning_sections"] is True
    assert review["product_decision"]["compiled_spa_changed"] is False
    for phrase in [
        "/teacher-learning",
        "case anchor -> thinking move -> model stack -> relation story -> practice rep",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "compiled SPA changes",
        "proceed_to_compiled_observatory_learn_tab_integration",
    ]:
        assert phrase in doc


def test_learn_page_docs_and_review_are_clean() -> None:
    text = DOC.read_text(encoding="utf-8") + REVIEW.read_text(encoding="utf-8")

    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "product_proof\": true" not in text
    assert "human_validated\": true" not in text
    assert "runtime_integration_authorized\": true" not in text


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
