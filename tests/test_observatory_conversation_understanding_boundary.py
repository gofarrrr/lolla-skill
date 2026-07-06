import json
from pathlib import Path

from engine.system_b.decision_work_brief_runtime_attachment import (
    DECISION_WORK_RUNTIME_ATTACHMENT_FLAG,
    decision_work_runtime_attachment_enabled,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/product/observatory-conversation-understanding-boundary-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-conversation-understanding-boundary-v0/review.json"
)
SERVE_RESULT = REPO_ROOT / "observatory/serve_result.py"
DECISION_TRAIL_REPORT = REPO_ROOT / "engine/system_b/decision_trail_report.py"
SIDECAR_STATE = REPO_ROOT / "docs/board/decision-work-sidecar-internal-v1-current-state.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_boundary_doc_exists_and_is_indexed() -> None:
    assert DOC.exists()
    assert REVIEW.exists()

    readme = _read(README)
    assert "Observatory Conversation Understanding Boundary" in readme
    assert "observatory-conversation-understanding-boundary-v0.md" in readme


def test_boundary_doc_separates_live_extraction_from_decision_work() -> None:
    text = _read(DOC)

    for phrase in [
        "live conversation capture and compact extraction are already part of the normal run path",
        "richer Decision Work / Decision Trail conversation interpretation exists as offline, operator-driven, default-off machinery",
        "Observatory should first expose Decision Work availability, receipts, blockers, and non-claims read-only",
        "Live extraction is the compact semantic extraction that normal runs already use.",
        "The richer Decision Work path is not automatic for every skill run.",
        "When the flag is absent, the hook returns `not_requested`",
    ]:
        assert phrase in " ".join(text.split())


def test_boundary_doc_names_current_evidence_and_next_endpoint() -> None:
    text = _read(DOC)

    for phrase in [
        "scripts/skill/run_extract_step.sh",
        "scripts/run_extract.py",
        "engine/system_b/conversation_loader.py",
        "ConversationContext",
        "/audit/extraction",
        "engine/system_b/decision_trail_report.py",
        "engine/system_b/decision_work_brief_runtime_attachment.py",
        "LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE",
        "/api/case/<id>/decision-work",
        "proceed_to_observatory_decision_work_sidecar_status_adapter",
    ]:
        assert phrase in text


def test_boundary_doc_assigns_single_homes_and_avoids_duplicate_ui() -> None:
    text = _read(DOC)

    for row in [
        "| Live extraction custody | Advanced `/audit/extraction` | Receipts | Teacher lesson copy |",
        "| Rich Decision Work receipt | Receipts / Conversation Understanding | Outcome status chip | Teacher lesson body |",
        "| Teacher reasoning move | Learn | Outcome, Models, Relations | Decision Work brief |",
        "| Sidecar health and blockers | Receipts | Advanced telemetry | product certification |",
    ]:
        assert row in text


def test_boundary_doc_defines_read_only_state_model() -> None:
    text = _read(DOC)
    normalized = " ".join(text.split())

    for state in [
        "live_extraction_available",
        "decision_work_not_present",
        "decision_work_not_requested",
        "decision_work_deferred",
        "decision_work_blocked",
        "decision_work_available",
        "decision_work_failed_closed",
    ]:
        assert state in text

    for phrase in [
        "Do not use approval, certification, correctness, or readiness labels.",
        "It should read existing archive sidecars only.",
        "It should not create sidecars, run the offline operator, call providers, or invoke Lolla.",
    ]:
        assert phrase in normalized


def test_repo_state_matches_boundary_claims() -> None:
    serve_result = _read(SERVE_RESULT)
    trail_report = " ".join(_read(DECISION_TRAIL_REPORT).split())
    sidecar_state = " ".join(_read(SIDECAR_STATE).split())

    assert '("/audit/extraction", "Extraction")' in serve_result
    assert 'parts[4] == "decision-work"' not in serve_result
    assert "/api/case/<id>/decision-work" not in serve_result
    assert "Read-only Decision Trail report exporter" in trail_report
    assert "does not run Lolla" in trail_report
    assert "does not call models" in trail_report
    assert "does not mutate archives" in trail_report
    assert "No runtime hook triggers it automatically." in sidecar_state


def test_default_off_decision_work_attachment_flag_is_verified() -> None:
    assert DECISION_WORK_RUNTIME_ATTACHMENT_FLAG == "LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE"
    assert decision_work_runtime_attachment_enabled({}) is False
    assert decision_work_runtime_attachment_enabled(
        {"LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE": "1"}
    ) is True


def test_review_json_records_gate_endpoint_and_non_claims() -> None:
    data = json.loads(_read(REVIEW))

    assert data["schema"] == "lolla.observatory_conversation_understanding_boundary_review.v0"
    assert data["artifact"] == (
        "docs/product/observatory-conversation-understanding-boundary-v0.md"
    )
    assert data["decision_gate"] == (
        "proceed_to_observatory_decision_work_sidecar_status_adapter"
    )
    assert data["validated_current_state"]["live_extraction_is_runtime_path"] is True
    assert data["validated_current_state"]["observatory_extraction_route_present"] is True
    assert (
        data["validated_current_state"]["observatory_decision_work_endpoint_present_now"]
        is False
    )
    assert (
        data["validated_current_state"]["post_archive_decision_work_attachment_default_off"]
        is True
    )
    assert data["recommended_endpoint"]["path"] == "/api/case/<id>/decision-work"
    assert data["recommended_endpoint"]["mode"] == "read_only"
    assert data["recommended_endpoint"]["writes_sidecar"] is False
    assert data["recommended_endpoint"]["runs_offline_operator"] is False
    assert data["recommended_endpoint"]["calls_provider_or_model"] is False
    assert data["recommended_endpoint"]["invokes_lolla"] is False

    non_claims = data["non_claims"]
    assert non_claims["lolla_skill_invoked"] is False
    assert non_claims["provider_or_model_calls_used"] is False
    assert non_claims["runtime_behavior_changed"] is False
    assert non_claims["archive_mutated"] is False
    assert non_claims["sidecar_written"] is False
    assert non_claims["automatic_semantic_interpretation_enabled"] is False
    assert non_claims["human_validated"] is False
    assert non_claims["product_proof"] is False
    assert non_claims["answer_correctness"] is False
    assert non_claims["advice_correctness"] is False
    assert non_claims["action_authorized"] is False


def test_boundary_artifacts_have_no_local_paths_or_authority_claims() -> None:
    text = _read(DOC) + _read(REVIEW)

    for forbidden in [
        "/" + "Users/",
        "Desktop/" + "Apps",
        "product_proof\": true",
        "human_validated\": true",
        "answer_correctness\": true",
        "advice_correctness\": true",
        "action_authorized\": true",
        "runtime_behavior_changed\": true",
        "archive_mutated\": true",
        "sidecar_written\": true",
    ]:
        assert forbidden not in text
