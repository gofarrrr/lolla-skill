from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from engine.system_b.decision_work_generated_read_brief_supply import (
    SUPPLY_SCHEMA_VERSION,
    build_generated_read_brief_supply,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-generated-read-brief-supply-adapter-v0.md"
)
SCRIPT_PATH = (
    REPO_ROOT
    / "scripts/evals/build_decision_work_generated_read_brief_supply.py"
)
READ_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/read.json"
)
INTAKE_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/intake.json"
)
PR185_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-generated-read-to-brief-supply-plan-v0.md"
)
PR185_REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-generated-read-to-brief-supply-plan-v0/review.json"
)
PR184_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-operator-codex-generated-read-pilot-v0.md"
)
PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md"
)
README_PATH = REPO_ROOT / "README.md"
HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"

FORBIDDEN_STRINGS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)


def _read_payload() -> dict[str, Any]:
    return json.loads(READ_PATH.read_text())


def _intake_payload() -> dict[str, Any]:
    return json.loads(INTAKE_PATH.read_text())


def _write_json(tmp_path: Path, name: str, payload: dict[str, Any]) -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _supply_for_payloads(
    tmp_path: Path,
    read: dict[str, Any],
    intake: dict[str, Any],
) -> dict[str, Any]:
    read_path = _write_json(tmp_path, "read.json", read)
    intake["source_read_ref"] = read_path.name
    intake_path = _write_json(tmp_path, "intake.json", intake)
    return build_generated_read_brief_supply(
        read_path=read_path,
        intake_path=intake_path,
        created_at="2026-07-03T00:00:00Z",
    )


def test_pr184_read_and_intake_produce_ready_supply() -> None:
    result = build_generated_read_brief_supply(
        read_path=READ_PATH,
        intake_path=INTAKE_PATH,
        created_at="2026-07-03T00:00:00Z",
    )

    assert result["schema_version"] == SUPPLY_SCHEMA_VERSION
    assert result["supply_status"] == "ready_for_offline_brief_rendering"
    assert result["blocker_reasons"] == []
    assert {item["field_name"] for item in result["allowed_brief_feed"]} == {
        "decision_question",
        "revised_direction_or_action_consequence",
        "evidence_gates",
        "what_the_final_answer_does_not_prove",
    }
    assert result["missing_required_fields"] == []
    assert result["source_ref_summary"]["status"] == "passed"
    assert result["uncertainty_summary"]["status"] == "passed"
    assert result["privacy_summary"]["status"] == "passed"
    assert result["downstream_allowed"]["can_render_offline_brief"] is True
    assert result["downstream_allowed"]["can_update_sidecar"] is False
    assert result["downstream_allowed"]["can_authorize_agent_action"] is False
    assert result["downstream_allowed"]["can_be_used_as_quality_label"] is False


def test_rejected_intake_is_blocked(tmp_path: Path) -> None:
    read = _read_payload()
    intake = _intake_payload()
    intake["intake_status"] = "rejected_quality_label"
    intake["accepted_for_downstream"] = False
    intake["downstream_allowed"]["can_feed_brief"] = False

    result = _supply_for_payloads(tmp_path, read, intake)

    assert result["supply_status"] == "blocked_intake_not_accepted"
    assert result["allowed_brief_feed"] == []
    assert result["downstream_allowed"]["can_render_offline_brief"] is False
    assert result["downstream_allowed"]["can_update_sidecar"] is False


def test_missing_required_field_defers(tmp_path: Path) -> None:
    read = _read_payload()
    read["interpreted_fields"] = [
        field
        for field in read["interpreted_fields"]
        if field["field_name"] != "decision_question"
    ]

    result = _supply_for_payloads(tmp_path, read, _intake_payload())

    assert result["supply_status"] == "deferred_missing_required_fields"
    assert result["missing_required_fields"] == ["decision_question"]
    assert result["downstream_allowed"]["can_render_offline_brief"] is False


def test_missing_source_refs_are_blocked(tmp_path: Path) -> None:
    read = _read_payload()
    read["interpreted_fields"][0]["source_refs"] = []

    result = _supply_for_payloads(tmp_path, read, _intake_payload())

    assert result["supply_status"] == "blocked_missing_source_refs"
    assert "missing_source_refs" in result["blocker_reasons"]
    assert result["source_ref_summary"]["missing_source_ref_fields"] == [
        "decision_question"
    ]


def test_missing_uncertainty_is_blocked(tmp_path: Path) -> None:
    read = _read_payload()
    del read["interpreted_fields"][0]["uncertainty"]

    result = _supply_for_payloads(tmp_path, read, _intake_payload())

    assert result["supply_status"] == "blocked_missing_uncertainty"
    assert "missing_uncertainty" in result["blocker_reasons"]
    assert result["uncertainty_summary"]["missing_uncertainty_fields"] == [
        "decision_question"
    ]


def test_privacy_markers_and_local_paths_are_blocked(tmp_path: Path) -> None:
    read = _read_payload()
    read["interpreted_fields"][0]["source_refs"][0]["artifact"] = (
        "/" + "Users" + "/example/private/archive/result.json"
    )
    result = _supply_for_payloads(tmp_path, read, _intake_payload())
    assert result["supply_status"] == "blocked_privacy_risk"
    assert result["privacy_summary"]["local_absolute_path_detected"] is True

    read = _read_payload()
    read["read_metadata"]["notes"].append("SEC" + "RET")
    result = _supply_for_payloads(tmp_path, read, _intake_payload())
    assert result["supply_status"] == "blocked_privacy_risk"
    assert result["privacy_summary"]["privacy_marker_detected"] is True


def test_authority_proof_scoring_and_action_claims_are_blocked(tmp_path: Path) -> None:
    for flag in (
        "product_proof",
        "human_validated",
        "answer_quality_scored",
        "agent_action_authorized",
        "automatic_action_authorized",
    ):
        read = _read_payload()
        read["custody_flags"][flag] = True
        result = _supply_for_payloads(tmp_path, read, _intake_payload())
        assert result["supply_status"] == "blocked_authority_claim", flag
        assert f"{flag}_claimed" in result["blocker_reasons"]


def test_cli_writes_valid_supply_json(tmp_path: Path) -> None:
    out = tmp_path / "supply.json"
    subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--read",
            str(READ_PATH),
            "--intake",
            str(INTAKE_PATH),
            "--out",
            str(out),
            "--pretty",
        ],
        check=True,
        cwd=REPO_ROOT,
    )

    payload = json.loads(out.read_text())
    assert payload["schema_version"] == SUPPLY_SCHEMA_VERSION
    assert payload["supply_status"] == "ready_for_offline_brief_rendering"
    assert payload["downstream_allowed"]["can_update_sidecar"] is False


def test_source_read_is_not_modified() -> None:
    before = READ_PATH.read_text()
    build_generated_read_brief_supply(
        read_path=READ_PATH,
        intake_path=INTAKE_PATH,
        created_at="2026-07-03T00:00:00Z",
    )
    assert READ_PATH.read_text() == before


def test_doc_records_statuses_cli_and_decision_gate() -> None:
    text = DOC_PATH.read_text()

    assert "# Decision Work Generated Read Brief Supply Adapter v0" in text
    assert "lolla.decision_work_generated_read_brief_supply.v0" in text
    assert "ready_for_offline_brief_rendering" in text
    assert "blocked_intake_not_accepted" in text
    assert "blocked_missing_source_refs" in text
    assert "blocked_missing_uncertainty" in text
    assert "blocked_privacy_risk" in text
    assert "blocked_authority_claim" in text
    assert "proceed_to_generated_read_brief_rendering_pilot" in text
    assert "PR187 Decision Work Generated Read Brief Rendering Pilot v0" in text
    assert "does not add" in text
    assert "new semantic interpretation" in text
    assert "can_update_sidecar" in text
    assert "can_authorize_agent_action" in text


def test_discoverability_docs_reference_pr186() -> None:
    expected = "Decision Work Generated Read Brief Supply Adapter"
    for path in (
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
        PRD_PATH,
        PR185_DOC,
    ):
        assert expected in path.read_text(), str(path)


def test_pr186_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            PR185_DOC,
            PR185_REVIEW,
            PR184_DOC,
            READ_PATH,
            INTAKE_PATH,
            PRD_PATH,
            README_PATH,
            HOW_IT_WORKS_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_pr186_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        SCRIPT_PATH,
        REPO_ROOT / "engine/system_b/decision_work_generated_read_brief_supply.py",
        PR185_DOC,
        PR185_REVIEW,
        PR184_DOC,
        READ_PATH,
        INTAKE_PATH,
        PRD_PATH,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text()
        for marker in FORBIDDEN_STRINGS:
            assert marker not in text, f"{path}:{marker}"
