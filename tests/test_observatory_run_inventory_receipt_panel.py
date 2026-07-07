from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

import serve_result  # noqa: E402


DOC = REPO_ROOT / "docs/product/observatory-run-inventory-receipt-panel-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-run-inventory-receipt-panel-v0/"
    "review.json"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _json(path: Path) -> dict:
    return json.loads(_read(path))


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _install_launch_case(monkeypatch, result_path: Path | None = None) -> None:
    result = {
        "usage_summary": {"run_id": "20260627T104146Z_7bfe79"},
        "extraction": {
            "decision_situation": (
                "A public enterprise beta launch is being reviewed."
            ),
            "turns": [
                {"speaker": "user", "text": "Should we launch the beta?"},
                {"speaker": "assistant", "text": "Use a staged gate."},
            ],
        },
        "run_health": {"overall": "healthy", "issues": []},
        "revised_answer": (
            "Launch in stages after the support risk is made explicit. "
            "Keep the first cohort narrow and treat the beta as a learning gate."
        ),
        "memo_what_changed": "The answer became conditional on support readiness.",
        "delta_card": {
            "findings": [
                {
                    "challenge_statement": (
                        "What would we have to believe to accept the opposite thesis?"
                    )
                }
            ]
        },
    }
    monkeypatch.setattr(serve_result, "_RESULT", result)
    monkeypatch.setattr(serve_result, "_RESULT_PATH", result_path)
    monkeypatch.setattr(serve_result, "_CASE_ID", "lolla-audit")
    monkeypatch.setattr(serve_result, "_CASE_NAME", "Lolla Audit")
    monkeypatch.setattr(
        serve_result,
        "_RESULT_MTIME",
        result_path.stat().st_mtime if result_path else 0.0,
    )


def _write_run_archive(tmp_path: Path) -> Path:
    run_dir = tmp_path / "launch-public-enterprise-beta" / "run-1"
    result_path = run_dir / "result.json"
    _write_json(result_path, {"placeholder": True})
    for filename, body in {
        "agent_result.json": "{}",
        "conversation.txt": "User: Should we launch?\nAssistant: Use a gate.",
        "evaluation.json": "{}",
        "extraction.json": "{}",
        "graph_survival_report.json": "{}",
        "graph_survival_report.md": "# Graph Survival",
        "live_transcript.txt": "live transcript",
        "memo.md": "# Launch Gate",
        "operator.log": "operator event",
        "pre_step6_private_table.json": "{}",
        "pre_step6_private_table.md": "private table",
        "pre_step6_private_table_ledger.json": "{}",
        "reasoning_trace.json": "{}",
        "run_events.json": json.dumps({"events": []}),
        "v60_ledger.json": "{}",
    }.items():
        (run_dir / filename).write_text(body, encoding="utf-8")
    return result_path


def _inventory_panel(html: str) -> str:
    return html.split('data-run-inventory-receipt', 1)[1].split(
        '<p class="workspace-kicker">Visible non-claims</p>',
        1,
    )[0]


def _inventory_item(panel: str, label: str) -> str:
    return panel.split(f"<strong>{label}</strong>", 1)[1].split("</article>", 1)[0]


def test_receipts_surface_shows_grouped_run_inventory_without_tables(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")
    panel = _inventory_panel(html)

    assert "Run inventory receipt" in panel
    assert "Accounted for" in panel
    assert "Product path" in panel
    assert "Export or inspection" in panel
    assert "Missing or future" in panel
    assert "Show grouped inventory" in panel

    for group in [
        "First-read product path",
        "Conversation and interpretation",
        "Memory, receipts, and sidecars",
        "Technical and operator inspection",
        "Library substrate accounted for",
    ]:
        assert group in panel

    for label in [
        "Conversation transcript",
        "Conversation Understanding",
        "Agent memory Markdown",
        "Process brief sidecar",
        "Canonical model Markdown",
        "Relationship graph substrate",
        "Knowledge graph and embeddings",
    ]:
        assert label in panel

    assert "<table" not in panel
    assert "artifact_statuses" not in panel
    assert "schema_version" not in panel
    assert "/" + "Users/" not in panel
    assert "Desktop/" + "Apps" not in panel


def test_inventory_receipt_accounts_for_available_sidecars_and_not_requested_brief(
    monkeypatch,
    tmp_path: Path,
) -> None:
    result_path = _write_run_archive(tmp_path)
    _install_launch_case(monkeypatch, result_path)

    html = serve_result._render_workspace_html("lolla-audit")
    panel = _inventory_panel(html)

    for label in [
        "Conversation transcript",
        "Reasoning trace",
        "Agent result object",
        "Evaluation artifact",
        "Run events",
        "Graph survival",
        "Private tables and ledgers",
        "Operator log",
    ]:
        assert "Available" in _inventory_item(panel, label)

    assert "Downloadable" in _inventory_item(panel, "Agent memory Markdown")
    assert "Not Requested" in _inventory_item(panel, "Process brief sidecar")
    assert "Private Export" in _inventory_item(panel, "Conversation transcript")
    assert "not graph truth" in _inventory_item(panel, "Graph survival")


def test_challenge_statement_becomes_visible_strongest_pressure(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_html("lolla-audit")

    assert "What would we have to believe to accept the opposite thesis?" in html
    assert "No compact pressure summary is available" not in html


def test_inventory_receipt_docs_review_and_readme_record_boundaries() -> None:
    doc = _read(DOC)
    readme = _read(README)
    review = _json(REVIEW)

    assert "Observatory Run Inventory Receipt Panel" in readme
    assert "observatory-run-inventory-receipt-panel-v0.md" in readme

    for phrase in [
        "Run inventory receipt",
        "Accounted for",
        "Product path",
        "Export or inspection",
        "Missing or future",
        "not a table",
        "Conversation transcript",
        "Process brief sidecar",
        "Knowledge graph and embeddings",
        "challenge_statement",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not wire skill runtime behavior",
        "does not edit `observatory/build`",
        "does not claim product proof",
        "does not claim human validation",
        "proceed_to_model_detail_local_neighborhoods_or_inventory_refinement",
    ]:
        assert phrase in doc

    assert review["decision_gate"] == (
        "proceed_to_model_detail_local_neighborhoods_or_inventory_refinement"
    )
    assert review["implemented"]["run_inventory_receipt_panel"] is True
    assert review["implemented"]["inventory_rendered_as_table"] is False
    assert review["implemented"]["challenge_statement_pressure_fallback"] is True
    assert review["implemented"]["runtime_behavior_changed"] is False
    assert review["implemented"]["compiled_spa_bundle_changed"] is False
    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["invokes_lolla_skill"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False


def test_inventory_receipt_artifacts_are_clean() -> None:
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
