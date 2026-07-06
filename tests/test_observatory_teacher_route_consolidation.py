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


DOC = REPO_ROOT / "docs/product/observatory-teacher-route-consolidation-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-teacher-route-consolidation-v0/review.json"
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
        },
    )
    monkeypatch.setattr(serve_result, "_RESULT_PATH", None)
    monkeypatch.setattr(serve_result, "_CASE_ID", "lolla-audit")
    monkeypatch.setattr(serve_result, "_CASE_NAME", "Lolla Audit")


def test_teacher_learning_route_is_compatibility_redirect(monkeypatch) -> None:
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


def test_teacher_learning_route_lands_in_workspace_when_followed(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    with _served_observatory() as base_url:
        with urllib.request.urlopen(f"{base_url}/teacher-learning", timeout=3) as response:
            html = response.read().decode("utf-8")

    assert response.status == 200
    assert response.geturl().endswith("/workspace?case_id=lolla-audit#learn")
    assert "<title>Lolla - Observatory Workspace</title>" in html
    assert "<h1>Selected Run Workspace</h1>" in html
    assert "What reasoning move can I practice?" in html
    assert "The Lesson" not in html


def test_teacher_learning_packet_api_is_preserved(monkeypatch) -> None:
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
    assert payload["missingness"]["status"] in {"complete", "partial"}


def test_injected_surface_links_use_workspace_not_teacher_learning() -> None:
    html = serve_result._inject_telemetry_fab(b"<html><body></body></html>").decode(
        "utf-8"
    )

    assert 'href="/workspace#learn"' in html
    assert 'href="/workspace#models"' in html
    assert 'href="/workspace#relations"' in html
    assert 'href="/workspace#map"' in html
    assert 'href="/workspace#receipts"' in html
    assert 'href="/teacher-learning' not in html


def test_audit_navigation_links_to_workspace_learn() -> None:
    html = serve_result._render_scaffold(
        title="Audit",
        body="<main>Audit</main>",
        current_path="/audit",
    )

    assert 'href="/workspace#learn">Learn</a>' in html
    assert 'href="/teacher-learning' not in html


def test_route_consolidation_docs_review_and_readme_capture_gate() -> None:
    doc = DOC.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    readme = README.read_text(encoding="utf-8")

    assert "Observatory Teacher Route Consolidation" in readme
    assert "observatory-teacher-route-consolidation-v0.md" in readme
    assert review["decision_gate"] == (
        "proceed_to_observatory_workspace_information_hierarchy_review"
    )
    assert review["implemented"]["teacher_learning_route_redirects_to_workspace_learn"] is True
    assert review["implemented"]["teacher_learning_packet_api_preserved"] is True
    assert review["route_contract"]["single_visible_teacher_product_path"] is True

    for phrase in [
        "`/teacher-learning` is now a compatibility entry point",
        "/workspace?case_id=<selected-case-id>#learn",
        "/api/case/<id>/teacher-learning",
        "single visible product path",
        "proceed_to_observatory_workspace_information_hierarchy_review",
    ]:
        assert phrase in doc


def test_route_consolidation_boundaries_and_nonclaims() -> None:
    doc = DOC.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    for phrase in [
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not create new Lolla runs",
        "does not wire runtime behavior",
        "does not edit `observatory/build`",
        "does not touch `SKILL.md`",
        "does not touch `scripts/skill/*`",
        "does not touch `scripts/archive_run.py`",
        "does not claim product proof",
        "does not claim human validation",
        "does not claim answer correctness",
        "does not claim advice correctness",
        "does not authorize action",
    ]:
        assert phrase in doc

    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["invokes_lolla_skill"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["boundary"]["compiled_spa_bundle_changed"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["answer_correctness"] is False
    assert review["non_claims"]["advice_correctness"] is False
    assert review["non_claims"]["action_authorized"] is False


def test_route_consolidation_docs_are_clean_of_local_paths_and_positive_claims() -> None:
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


def _free_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])
