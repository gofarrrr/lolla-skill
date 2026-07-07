from __future__ import annotations

import json
import re
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


DOC = REPO_ROOT / "docs/product/observatory-agent-memory-markdown-download-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-agent-memory-markdown-download-v0/"
    "review.json"
)
RAW_MARKER = "RAW CONVERSATION MARKER FOR PRIVATE AGENT EXPORT"
PRIVATE_MARKER = "PRIVATE LEDGER MARKER MUST NOT APPEAR"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_run(run_dir: Path) -> Path:
    run_dir.mkdir(parents=True)
    _write_json(
        run_dir / "reasoning_trace.json",
        {
            "schema_version": "lolla.reasoning_trace.v0.2",
            "case": {
                "case_id": "lolla-audit",
                "run_id": "run-1",
                "decision_situation": "Whether to launch after mixed evidence.",
            },
            "capture": {
                "capture_adequacy": {
                    "status": "good",
                    "capture_strategy": "full_conversation",
                },
                "decision_structure": {
                    "live_constraint_count": 1,
                    "reasoning_passage_count": 2,
                    "dropped_thread_count": 1,
                },
            },
            "reasoning_lenses": [
                {
                    "model_id": "inversion",
                    "lane": "lane3",
                    "role": "frame_pressure",
                    "selected": True,
                    "surfaced": True,
                    "disposition": "selected",
                }
            ],
        },
    )
    _write_json(
        run_dir / "agent_result.json",
        {
            "schema_version": "lolla_agent_result.v1",
            "case_id": "lolla-audit",
            "run_id": "run-1",
            "status": "ok",
            "position_changed": True,
            "main_counter_pressure": "The launch gate was under-specified.",
            "changed_advice_summary": ["Add a launch gate."],
            "human_questions": ["Who owns the gate?"],
        },
    )
    _write_json(
        run_dir / "evaluation.json",
        {
            "schema_version": "lolla.evaluation.v0",
            "case_id": "lolla-audit",
            "run_id": "run-1",
            "overall": "pass",
        },
    )
    _write_json(
        run_dir / "extraction.json",
        {
            "extraction": {
                "decision_situation": "Whether to launch after mixed evidence.",
                "original_framing": "The beta looked ready.",
                "synthesized_position": "Launch only if a narrow gate passes.",
                "live_constraints": [{"text": "Do not overfit one signal."}],
                "dropped_threads": [{"text": "Pricing risk was not resolved."}],
                "assumptions": [{"text": "The team can still delay."}],
            }
        },
    )
    _write_json(
        run_dir / "result.json",
        {
            "usage_summary": {"run_id": "run-1"},
            "extraction": {
                "decision_situation": "Whether to launch after mixed evidence."
            },
            "revised_answer": "Launch only if the gate passes.",
            "memo_what_changed": "The recommendation became conditional.",
            "memo_what_still_holds": "The enterprise signal still matters.",
            "memo_take_back_or_set_aside": "Do not treat one signal as proof.",
            "run_health": {"overall": "healthy"},
        },
    )
    _write_json(
        run_dir / "memo_note.json",
        {"memo_substantive_title": "Launch Gate"},
    )
    _write_json(
        run_dir / "graph_survival_report.json",
        {
            "summary": {
                "lane_candidate_count": 2,
                "embedding_hit_count": 1,
                "selected_card_count": 1,
                "suppressed_signal_count": 1,
            },
            "candidate_survival": [
                {"model_id": "inversion", "survival_state": "selected"}
            ],
            "suppressed_signals": [
                {"model_id": "base-rates", "reason": "budget"}
            ],
        },
    )
    _write_json(
        run_dir / "run_events.json",
        {"events": [{"event_type": "archive_completed"}]},
    )
    (run_dir / "conversation.txt").write_text(
        f"User: Should we launch?\nAssistant: Maybe.\n{RAW_MARKER}",
        encoding="utf-8",
    )
    (run_dir / "memo.md").write_text("# Launch Gate\n\nUse a gate.", encoding="utf-8")
    (run_dir / "revised.txt").write_text(
        "Launch only if the gate passes.",
        encoding="utf-8",
    )
    (run_dir / "pre_step6_private_table.md").write_text(
        PRIVATE_MARKER,
        encoding="utf-8",
    )
    return run_dir / "result.json"


def _with_server(result_path: Path, callback):
    old_result = serve_result._RESULT
    old_result_path = serve_result._RESULT_PATH
    old_case_id = serve_result._CASE_ID
    old_mtime = serve_result._RESULT_MTIME

    serve_result._RESULT = json.loads(result_path.read_text(encoding="utf-8"))
    serve_result._RESULT_PATH = result_path
    serve_result._CASE_ID = "lolla-audit"
    serve_result._RESULT_MTIME = result_path.stat().st_mtime

    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    server = HTTPServer(("127.0.0.1", port), serve_result.ResultHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        return callback(port)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
        serve_result._RESULT = old_result
        serve_result._RESULT_PATH = old_result_path
        serve_result._CASE_ID = old_case_id
        serve_result._RESULT_MTIME = old_mtime


def test_main_workspace_contains_agent_memory_download_action() -> None:
    html = serve_result._render_workspace_hero(
        {
            "case_id": "lolla-audit",
            "run_id": "run-1",
            "health_label": "ok",
        },
        {
            "rendering_direction": "portable_python_server_rendered_html",
            "primary_surfaces": ["Outcome", "Learn", "Models", "Relations", "Map", "Receipts"],
            "advanced_surface": "Advanced Audit",
        },
    )

    assert "Start here" in html
    assert "data-agent-memory-export-card" in html
    assert "Download a complete run memory for your agent" in html
    assert "full 1:1 conversation transcript" in html
    assert ">Download MD</a>" in html
    assert "data-agent-memory-download-action" in html
    assert "data-agent-memory-download-toast" in html
    assert "workspace-chip-with-toast--right" in html
    assert "generated synthesis to verify" in html
    assert "Give it to a future agent" in html
    assert (
        'download href="/api/case/lolla-audit/conversation-memory.md?include_raw_conversation=1"'
        in html
    )
    assert html.index("Use map") < html.index("Download MD")
    assert html.index("Download MD") < html.index("Check receipts")
    assert (
        ".workspace-chip-with-toast:hover .workspace-chip-toast"
        in serve_result._WORKSPACE_CSS
    )
    assert (
        ".workspace-chip-with-toast:focus-within .workspace-chip-toast"
        in serve_result._WORKSPACE_CSS
    )
    assert (
        ".workspace-chip-with-toast--right .workspace-chip-toast"
        in serve_result._WORKSPACE_CSS
    )


def test_receipts_repeats_agent_memory_download_with_custody_context() -> None:
    html = serve_result._render_workspace_receipts(
        {
            "learning_packet_status": "available",
            "conversation_understanding_status": "available",
            "process_brief_status": "not_requested",
            "visible_non_claims": ["Not product proof"],
        },
        {"advanced_links": [], "artifact_statuses": []},
        {"missingness": {}, "non_claims": []},
        "lolla-audit",
    )

    assert "Agent memory export" in html
    assert ">Download MD</a>" in html
    assert "data-agent-memory-download-toast" in html
    assert 'download href="/api/case/lolla-audit/conversation-memory.md?include_raw_conversation=1"' in html
    assert "private Markdown file for your agent" in html
    assert "future agent" in html


def test_agent_memory_download_route_returns_self_explaining_markdown(
    tmp_path: Path,
) -> None:
    result_path = _write_run(tmp_path / "archive" / "lolla-audit" / "run-1")

    def _fetch(port: int) -> tuple[dict, str]:
        request = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/case/lolla-audit/"
            "conversation-memory.md?include_raw_conversation=1"
        )
        with urllib.request.urlopen(request, timeout=3) as response:
            headers = dict(response.headers.items())
            body = response.read().decode("utf-8")
        return headers, body

    headers, markdown = _with_server(result_path, _fetch)

    assert headers["Content-Type"] == "text/markdown; charset=utf-8"
    assert "attachment;" in headers["Content-Disposition"]
    assert "lolla-audit-run-1-conversation-memory.md" in headers[
        "Content-Disposition"
    ]

    for heading in [
        "# Conversation Memory",
        "## Cold Reader Orientation",
        "## Claim Verification Checklist",
        "## What This File Is",
        "## What This File Is Not",
        "## How This File Was Produced",
        "## Source Artifact Map",
        "## Interpretation Legend",
        "## Conversation Interpretation",
        "## Selected Models",
        "## Suppressed Or Unadjudicated Signals",
        "## Open Questions",
        "## Agent Instructions For Future Use",
        "## Appendix: Source Excerpts",
        "### Full 1:1 Conversation Transcript",
    ]:
        assert heading in markdown

    assert RAW_MARKER in markdown
    assert "hypotheses to verify, not ground truth" in markdown
    assert "Do not treat this orientation as the answer." in markdown
    assert "Use this as a checking index, not as a conclusion." in markdown
    assert "Claim / item to verify" in markdown
    assert "Source locator" in markdown
    assert "Still verify before relying" in markdown
    assert "[Transcript](#cm-source-full-transcript)" in markdown
    assert "[Run Health And Readiness](#cm-section-run-health-and-readiness)" in markdown
    assert '<a id="cm-source-full-transcript"></a>' in markdown
    assert "- Generated synthesis:" not in markdown
    assert "full archived `conversation.txt` transcript" in markdown
    assert PRIVATE_MARKER not in markdown
    assert "not_advice_correctness" in markdown
    assert "not_answer_correctness" in markdown
    assert "not_action_authorization" in markdown
    assert "Raw conversation included: `true`" in markdown


def test_agent_memory_download_helper_writes_outside_archive(tmp_path: Path) -> None:
    result_path = _write_run(tmp_path / "archive" / "lolla-audit" / "run-1")

    markdown, filename = serve_result._build_agent_memory_markdown_download(
        "lolla-audit",
        result_path,
        is_current=True,
        include_raw_conversation=True,
    )

    assert filename == "lolla-audit-run-1-conversation-memory.md"
    assert "# Conversation Memory" in markdown
    assert RAW_MARKER in markdown
    assert not (result_path.parent / "conversation_memory.md").exists()
    assert not (result_path.parent / "conversation_memory_packet.json").exists()


def test_agent_memory_doc_review_and_readme_are_clean() -> None:
    assert DOC.exists()
    assert REVIEW.exists()
    readme = _read(README)
    doc = _read(DOC)
    review = json.loads(_read(REVIEW))

    assert "Observatory Agent Memory Markdown Download" in readme
    assert "observatory-agent-memory-markdown-download-v0.md" in readme

    for phrase in [
        "Download MD",
        "hover or keyboard focus",
        "main workspace",
        "/api/case/<id>/conversation-memory.md",
        "explicit private local export",
        "not the default product UI",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not wire skill runtime behavior",
        "does not mutate archives",
        "does not edit `observatory/build`",
        "does not claim product proof",
        "does not claim human validation",
    ]:
        assert phrase in doc

    assert review["decision_gate"] == "proceed_to_presentation_visibility_revision"
    assert review["implemented"]["main_workspace_download_button"] is True
    assert review["implemented"]["receipts_download_button"] is True
    assert review["implemented"]["markdown_download_route"] is True
    assert review["implemented"]["offline_bundle_builder"] is True
    assert review["implemented"]["runtime_behavior_changed"] is False
    assert review["implemented"]["compiled_spa_bundle_changed"] is False
    assert review["privacy"]["raw_conversation_default_public_safe"] is False
    assert review["privacy"]["private_operator_bodies_copied"] is False


def test_agent_memory_links_and_private_markers_are_clean() -> None:
    missing = []
    for path in [DOC, README]:
        text = _read(path)
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith("#") or re.match(r"^[a-z]+:", target):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).resolve().exists():
                missing.append(f"{path}: {target}")

    combined = _read(DOC) + _read(REVIEW)
    assert missing == []
    assert "/" + "Users/" not in combined
    assert "Desktop/" + "Apps" not in combined
    assert "product_proof\": true" not in combined
    assert "human_validated\": true" not in combined
    assert "answer_correctness\": true" not in combined
    assert "advice_correctness\": true" not in combined
    assert "runtime_integration_authorized\": true" not in combined
    assert "action_authorized\": true" not in combined
