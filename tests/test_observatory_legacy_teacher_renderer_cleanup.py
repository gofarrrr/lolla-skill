from __future__ import annotations

import json
import socket
import sys
import threading
import urllib.error
import urllib.request
from contextlib import closing
from http.server import HTTPServer
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

import serve_result  # noqa: E402


DOC = REPO_ROOT / "docs/product/observatory-legacy-teacher-renderer-cleanup-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-legacy-teacher-renderer-cleanup-v0/review.json"
)
SERVER = REPO_ROOT / "observatory/serve_result.py"


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
        },
    )
    monkeypatch.setattr(serve_result, "_RESULT_PATH", None)
    monkeypatch.setattr(serve_result, "_CASE_ID", "lolla-audit")
    monkeypatch.setattr(serve_result, "_CASE_NAME", "Lolla Audit")


def test_legacy_teacher_direct_renderer_is_removed_from_server_source() -> None:
    source = SERVER.read_text(encoding="utf-8")

    assert not hasattr(serve_result, "_render_teacher_learning_html")
    assert "def _render_teacher_learning_html" not in source
    assert "data-teacher-graph" not in source
    assert "dataset.returnHash" not in source
    assert "teacher-detail" not in source
    assert "drawer-panel" not in source
    assert "tab-btn--active" not in source


def test_teacher_learning_route_remains_compatibility_redirect(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    with _served_observatory() as base_url:
        request = urllib.request.Request(f"{base_url}/teacher-learning")
        opener = urllib.request.build_opener(_NoRedirect)
        try:
            opener.open(request, timeout=3)
        except urllib.error.HTTPError as exc:
            status = exc.code
            location = exc.headers["Location"]
        else:
            raise AssertionError("/teacher-learning should redirect")

    assert status == 302
    assert location == "/workspace?case_id=lolla-audit#learn"


def test_teacher_learning_packet_api_remains_available(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    with _served_observatory() as base_url:
        with urllib.request.urlopen(
            f"{base_url}/api/case/lolla-audit/teacher-learning",
            timeout=3,
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))

    assert response.status == 200
    assert payload["available"] is True
    assert payload["packet_summary"]["thinking_move"]
    assert payload["observatory_tabs"] == [
        "Outcome",
        "Learn",
        "Models",
        "Relations",
        "Map",
        "Receipts",
    ]


def test_workspace_is_single_visible_teacher_product_path(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")
    status_bar = html.split('data-observatory-status-bar>', 1)[1].split("</nav>", 1)[0]

    assert "What reasoning move can I practice?" in html
    assert "Test The Authority, Not The Aura" in html
    assert "data-observatory-graph" in html
    assert 'href="/models/authority-bias?case_id=lolla-audit"' in html
    assert (
        'href="/relations/authority-bias__first-principles-thinking__antagonist?case_id=lolla-audit"'
        in html
    )
    assert "Advanced Audit" not in status_bar
    assert "data-teacher-graph" not in html


def test_cleanup_docs_review_and_readme_capture_gate() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    assert "Observatory Legacy Teacher Renderer Cleanup" in readme
    assert "observatory-legacy-teacher-renderer-cleanup-v0.md" in readme
    assert review["decision_gate"] == (
        "proceed_to_observatory_workspace_accessibility_text_noise_cleanup"
    )

    for phrase in [
        "The API is data. The workspace is the visible product.",
        "The old all-in-one Teacher page is no longer a maintained renderer.",
        "/teacher-learning -> /workspace?case_id=<selected-case-id>#learn",
        "/api/case/<id>/teacher-learning",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not edit `observatory/build`",
        "Browser Check",
        "no `data-teacher-graph` or drawer panel appeared",
        "proceed_to_observatory_workspace_accessibility_text_noise_cleanup",
    ]:
        assert phrase in doc

    assert review["implemented"]["legacy_direct_teacher_renderer_removed"] is True
    assert review["implemented"]["teacher_learning_route_redirect_preserved"] is True
    assert review["implemented"]["teacher_learning_packet_api_preserved"] is True
    assert review["implemented"]["old_hash_drawer_graph_contract_removed"] is True
    assert review["browser_check"]["performed"] is True
    assert review["browser_check"]["legacy_teacher_dom_absent"] is True
    assert review["browser_check"]["observatory_graph_present"] is True
    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["invokes_lolla_skill"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["boundary"]["compiled_spa_bundle_changed"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["answer_correctness"] is False
    assert review["non_claims"]["advice_correctness"] is False
    assert review["non_claims"]["action_authorized"] is False


def test_cleanup_docs_are_clean_of_local_paths_and_positive_claims() -> None:
    text = DOC.read_text(encoding="utf-8") + REVIEW.read_text(encoding="utf-8")

    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "product_proof\": true" not in text
    assert "human_validated\": true" not in text
    assert "answer_correctness\": true" not in text
    assert "advice_correctness\": true" not in text
    assert "runtime_integration_authorized\": true" not in text
    assert "action_authorized\": true" not in text


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


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
