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
from engine.system_b.mental_model_teacher_observatory_packet_adapter import (  # noqa: E402
    TEACHER_LEARNING_ADAPTER_SCHEMA_VERSION,
    build_teacher_learning_case_summary,
    build_teacher_learning_response,
)


DOC = REPO_ROOT / "docs/product/mental-model-teacher-observatory-packet-adapter-v0.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/mental-model-teacher-observatory-packet-adapter-v0/review.json"
)
README = REPO_ROOT / "docs/product/README.md"


def test_adapter_matches_archive_case_by_case_and_run_id() -> None:
    response = build_teacher_learning_response(
        "archive:launch-public-enterprise-beta:20260627T104146Z_7bfe79",
        {"usage_summary": {"run_id": "20260627T104146Z_7bfe79"}},
    )

    assert response["schema_version"] == TEACHER_LEARNING_ADAPTER_SCHEMA_VERSION
    assert response["available"] is True
    assert response["matched_by"] == "case_id_and_run_id"
    assert response["packet_id"] == (
        "launch-public-enterprise-beta-observatory-teacher-learning-packet"
    )
    assert response["observatory_tabs"] == [
        "Outcome",
        "Learn",
        "Models",
        "Relations",
        "Map",
        "Receipts",
    ]
    assert response["tab_payloads"]["Learn"]["lesson"]["case_id"] == (
        "launch-public-enterprise-beta"
    )
    assert response["tab_payloads"]["Models"]["models"][0]["display_name"] == (
        "Authority Bias"
    )
    assert response["tab_payloads"]["Relations"]["relations"][0]["relation_type"] == (
        "antagonist"
    )
    assert response["tab_payloads"]["Map"]["graph"]["graph_scope"] == (
        "lesson_neighborhood"
    )


def test_adapter_keeps_primary_tabs_free_of_receipt_artifacts_and_telemetry() -> None:
    response = build_teacher_learning_response(
        "archive:deploy-assisted-intake-routing:20260627T130339Z_4cd3cb",
        {"usage_summary": {"run_id": "20260627T130339Z_4cd3cb"}},
    )

    for tab in ("Outcome", "Learn", "Models", "Relations", "Map"):
        rendered = json.dumps(response["tab_payloads"][tab], sort_keys=True)
        assert "artifact_refs" not in rendered
        assert "usage_summary" not in rendered
        assert "audit_summary" not in rendered

    assert response["tab_payloads"]["Receipts"]["receipts"]["artifact_refs"]
    assert response["advanced"]["available"] is True
    assert all(
        artifact["home_tab"] == "Advanced"
        for artifact in response["advanced"]["artifact_refs"]
    )
    assert response["visibility_policy"]["raw_telemetry_in_primary_tabs"] is False
    assert response["visibility_policy"]["raw_canonical_markdown_in_primary_tabs"] is False
    assert response["product_proof"] is False
    assert response["human_validated"] is False
    assert response["runtime_integration_authorized"] is False
    assert response["provider_or_model_calls_used"] is False


def test_adapter_unavailable_response_is_stable_for_cases_without_packet(
    tmp_path: Path,
) -> None:
    response = build_teacher_learning_response(
        "archive:unknown-case:20260101T000000Z_missing",
        {"usage_summary": {"run_id": "20260101T000000Z_missing"}},
        package_dir=tmp_path,
    )

    assert response["available"] is False
    assert response["unavailable_reason"] == (
        "no_teacher_learning_packet_for_selected_case"
    )
    assert response["observatory_tabs"][1] == "Learn"
    assert response["default_tab"] == "Outcome"
    assert response["tab_payloads"] == {}
    assert response["product_proof"] is False
    assert response["human_validated"] is False
    assert response["runtime_integration_authorized"] is False


def test_case_summary_is_compact_and_omits_full_tab_payloads() -> None:
    summary = build_teacher_learning_case_summary(
        "archive:ceo-remove-founding-cofounder:20260627T093131Z_59d153",
        {"usage_summary": {"run_id": "20260627T093131Z_59d153"}},
    )

    assert summary["available"] is True
    assert summary["packet_id"] == (
        "ceo-remove-founding-cofounder-observatory-teacher-learning-packet"
    )
    assert summary["lesson_summary"]["thinking_move"]
    assert summary["model_count"] == 3
    assert summary["relation_count"] == 1
    assert "tab_payloads" not in summary


def test_observatory_case_response_includes_teacher_learning_summary(monkeypatch) -> None:
    result = {
        "usage_summary": {"run_id": "20260627T104146Z_7bfe79"},
        "extraction": {"turns": []},
    }

    response = serve_result._build_case_response(
        result,
        case_id="archive:launch-public-enterprise-beta:20260627T104146Z_7bfe79",
        result_path=None,
    )

    assert response["teacher_learning"]["available"] is True
    assert response["teacher_learning"]["lesson_summary"]["thinking_move"]
    assert response["teacher_learning"]["model_count"] == 3


def test_observatory_teacher_learning_endpoint_returns_packet(monkeypatch) -> None:
    monkeypatch.setattr(
        serve_result,
        "_RESULT",
        {"usage_summary": {"run_id": "20260627T104146Z_7bfe79"}},
    )
    monkeypatch.setattr(serve_result, "_RESULT_PATH", None)
    monkeypatch.setattr(serve_result, "_CASE_ID", "lolla-audit")

    with _served_observatory() as base_url:
        with urllib.request.urlopen(
            f"{base_url}/api/case/lolla-audit/teacher-learning",
            timeout=3,
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))

    assert payload["available"] is True
    assert payload["matched_by"] == "run_id"
    assert payload["tab_payloads"]["Learn"]["lesson"]["case_id"] == (
        "launch-public-enterprise-beta"
    )
    assert payload["advanced"]["surface"] == "Advanced"


def test_adapter_docs_review_and_readme_preserve_boundaries() -> None:
    doc = DOC.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    readme = README.read_text(encoding="utf-8")

    assert "mental-model-teacher-observatory-packet-adapter-v0.md" in readme
    assert review["decision_gate"] == "proceed_to_observatory_teacher_learn_tab_ui"
    assert review["adapter_guards"]["read_only_observatory_api"] is True
    assert review["adapter_guards"]["runtime_wiring_allowed"] is False
    assert review["adapter_guards"]["primary_tabs_own_no_receipt_artifacts"] is True
    assert review["non_claims"]["provider_or_model_calls_used"] is False
    for phrase in [
        "/api/case/<id>/teacher-learning",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not render the Learn tab UI",
        "Outcome | Learn | Models | Relations | Map | Receipts",
        "proceed_to_observatory_teacher_learn_tab_ui",
    ]:
        assert phrase in doc


def test_adapter_json_and_docs_are_clean() -> None:
    text = (
        DOC.read_text(encoding="utf-8")
        + REVIEW.read_text(encoding="utf-8")
    )
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
