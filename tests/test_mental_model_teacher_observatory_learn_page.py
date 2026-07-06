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


def test_workspace_learn_surface_has_clear_narrative_order(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert "<h2>Learn</h2>" in html
    assert "What reasoning move can I practice?" in html
    assert "Thinking move" in html
    assert "Lesson steps and boundaries" in html
    assert "Model links" in html
    assert "Relation links" in html
    assert "Do not overlearn" in html
    assert "Models" in html
    assert "Relations" in html
    assert "Map" in html
    assert "Receipts" in html
    assert html.index("<h2>Learn</h2>") < html.index("<h2>Models</h2>")
    assert html.index("<h2>Models</h2>") < html.index("<h2>Relations</h2>")
    assert html.index("<h2>Relations</h2>") < html.index("<h2>Map</h2>")
    assert html.index("<h2>Map</h2>") < html.index("<h2>Receipts</h2>")


def test_learn_page_uses_canonical_model_names_and_lesson_practice_label(
    monkeypatch,
) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert "Authority Bias" in html
    assert "Information Asymmetry" in html
    assert "First Principles Thinking" in html
    assert "Test The Authority, Not The Aura" in html
    assert html.index("Test The Authority, Not The Aura") < html.index("<h2>Models</h2>")
    assert 'id="model-test-the-authority-not-the-aura"' not in html


def test_learn_page_shows_relation_story_before_relation_taxonomy(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")
    detail = serve_result._render_workspace_relation_detail_html(
        "authority-bias__first-principles-thinking__antagonist",
        "lolla-audit",
    )

    story_index = detail.index(
        "First principles thinking strips away inherited doctrine"
    )
    taxonomy_index = detail.index("confidence: medium")
    assert story_index < taxonomy_index
    assert "Edges are navigation, not proof" in html
    assert "Graph is navigation" not in html


def test_learn_page_keeps_receipts_and_nonclaims_visible_but_late(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert "Source and missingness details" in html
    assert "Technical inspection" in html
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
    assert response.geturl().endswith("/workspace?case_id=lolla-audit#learn")
    assert "<title>Lolla - Observatory Workspace</title>" in html
    assert "<h1>Run Learning Workspace</h1>" in html
    assert "Authority Bias" in html
    assert "What reasoning move can I practice?" in html


def test_root_injection_adds_learn_and_telemetry_affordances() -> None:
    rendered = serve_result._inject_telemetry_fab(b"<html><body></body></html>").decode(
        "utf-8"
    )
    rendered_again = serve_result._inject_telemetry_fab(rendered.encode("utf-8")).decode(
        "utf-8"
    )

    assert 'href="/workspace#learn"' in rendered
    assert 'class="learn-fab"' in rendered
    assert 'class="telemetry-fab"' in rendered
    assert "Case Surfaces" in rendered
    assert 'href="/workspace#models"' in rendered
    assert 'href="/workspace#relations"' in rendered
    assert 'href="/workspace#map"' in rendered
    assert 'href="/workspace#receipts"' in rendered
    assert 'href="/teacher-learning' not in rendered
    assert rendered_again.count('class="learn-fab"') == 1
    assert rendered_again.count('class="telemetry-fab"') == 1


def test_workspace_learn_status_bar_uses_shared_workspace_navigation(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert 'aria-label="Observatory workspace"' in html
    assert (
        'data-observatory-surface-link="outcome" '
        'href="/workspace?case_id=lolla-audit#outcome">Outcome</a>'
    ) in html
    assert (
        'data-observatory-surface-link="learn" '
        'href="/workspace?case_id=lolla-audit#learn">Learn</a>'
    ) in html
    assert (
        'data-observatory-surface-link="models" '
        'href="/workspace?case_id=lolla-audit#models">Models</a>'
    ) in html
    assert (
        'data-observatory-surface-link="relations" '
        'href="/workspace?case_id=lolla-audit#relations">Relations</a>'
    ) in html
    assert (
        'data-observatory-surface-link="map" '
        'href="/workspace?case_id=lolla-audit#map">Map</a>'
    ) in html
    assert (
        'data-observatory-surface-link="receipts" '
        'href="/workspace?case_id=lolla-audit#receipts">Receipts</a>'
    ) in html
    status_bar = html.split('data-observatory-status-bar>', 1)[1].split("</nav>", 1)[0]
    assert "Advanced Audit" not in status_bar
    assert 'href="/models/authority-bias?case_id=lolla-audit"' in html


def test_legacy_teacher_learning_direct_renderer_is_removed() -> None:
    assert not hasattr(serve_result, "_render_teacher_learning_html")


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
