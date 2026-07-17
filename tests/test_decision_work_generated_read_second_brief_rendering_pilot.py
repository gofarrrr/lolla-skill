from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from engine.system_b.decision_work_generated_interpretation_read_intake import (
    validate_generated_interpretation_read,
)
from engine.system_b.decision_work_generated_read_brief_supply import (
    SUPPLY_SCHEMA_VERSION,
    build_generated_read_brief_supply,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-generated-read-second-brief-rendering-pilot-v0.md"
)
RENDERED_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-generated-read-rendered-deploy-assisted-intake-routing-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-generated-read-second-brief-rendering-pilot-v0/review.json"
)
READ_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-generated-read-second-brief-rendering-pilot-v0/read.json"
)
INTAKE_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-generated-read-second-brief-rendering-pilot-v0/intake.json"
)
PROMPT_PACKET_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-operator-codex-interpretation-prompt-packet-v0.json"
)
SUPPLY_SCRIPT = (
    REPO_ROOT / "scripts/evals/build_decision_work_generated_read_brief_supply.py"
)
RENDER_SCRIPT = REPO_ROOT / "scripts/evals/render_decision_work_generated_read_brief.py"
PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-automatic-semantic-supply-prd-v0.md"
)
PR187_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-generated-read-brief-rendering-pilot-v0.md"
)
PR188_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-generated-read-brief-vs-existing-brief-review-v0.md"
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


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_second_pilot_read_and_intake_are_accepted() -> None:
    read = _json(READ_PATH)
    intake = _json(INTAKE_PATH)

    assert read["schema_version"] == "lolla.decision_work_conversation_interpretation_read.v0"
    assert read["selected_case"]["case_id"] == "deploy-assisted-intake-routing"
    assert read["selected_case"]["decision_family"] == (
        "healthcare_operations_or_deployment"
    )
    assert {field["field_name"] for field in read["interpreted_fields"]} == {
        "decision_question",
        "revised_direction_or_action_consequence",
        "evidence_gates",
        "what_the_final_answer_does_not_prove",
    }
    for field in read["interpreted_fields"]:
        assert field["source_refs"], field["field_name"]
        assert field["uncertainty"] in {"low", "medium", "high"}
        assert field["privacy_limit"]
        assert field["human_review_required"] is True
        assert field["must_not_be_used_as_quality_label"] is True
        for source_ref in field["source_refs"]:
            artifact = source_ref["artifact"]
            assert not artifact.startswith("/")
            assert (REPO_ROOT / artifact).exists(), artifact

    expected = validate_generated_interpretation_read(
        read_path=READ_PATH,
        prompt_packet_path=PROMPT_PACKET_PATH,
        created_at="2026-07-03T00:00:00Z",
    )
    assert intake == expected
    assert intake["intake_status"] == "accepted"
    assert intake["accepted_for_downstream"] is True
    assert intake["downstream_allowed"]["can_update_sidecar"] is False


def test_second_pilot_supply_is_ready_and_renderer_output_matches(tmp_path: Path) -> None:
    supply = build_generated_read_brief_supply(
        read_path=READ_PATH,
        intake_path=INTAKE_PATH,
        created_at="2026-07-03T00:00:00Z",
    )
    assert supply["schema_version"] == SUPPLY_SCHEMA_VERSION
    assert supply["supply_status"] == "ready_for_offline_brief_rendering"
    assert supply["downstream_allowed"]["can_render_offline_brief"] is True
    assert supply["downstream_allowed"]["can_update_sidecar"] is False

    supply_path = tmp_path / "supply.json"
    rendered_path = tmp_path / "rendered.md"
    subprocess.run(
        [
            sys.executable,
            str(SUPPLY_SCRIPT),
            "--read",
            str(READ_PATH),
            "--intake",
            str(INTAKE_PATH),
            "--out",
            str(supply_path),
            "--pretty",
        ],
        check=True,
        cwd=REPO_ROOT,
    )
    subprocess.run(
        [
            sys.executable,
            str(RENDER_SCRIPT),
            "--supply",
            str(supply_path),
            "--case-id",
            "deploy-assisted-intake-routing",
            "--out",
            str(rendered_path),
        ],
        check=True,
        cwd=REPO_ROOT,
    )
    assert rendered_path.read_text(encoding="utf-8") == RENDERED_PATH.read_text(
        encoding="utf-8"
    )


def test_rendered_second_brief_preserves_domain_caveats_and_boundaries() -> None:
    markdown = RENDERED_PATH.read_text(encoding="utf-8")

    assert "deploy-assisted-intake-routing" in markdown
    assert "outpatient clinics" in markdown
    assert "compliance" in markdown
    assert "clinical compliance" in markdown
    assert "do not prove the routing feature should deploy" in markdown
    assert "Human review is still required" in markdown
    assert "Runtime sidecar update allowed: no" in markdown
    assert "Agent action authorization: no" in markdown
    assert "Product proof: no" in markdown
    assert "Answer-quality scoring: no" in markdown
    assert "Source references" in markdown
    assert "legal or clinical compliance is satisfied" in markdown
    assert "approval" not in markdown.lower()
    assert "certification" not in markdown.lower()


def test_review_json_records_second_pilot_gate_and_non_claims() -> None:
    review = _json(REVIEW_PATH)

    assert (
        review["schema_version"]
        == "lolla.decision_work_generated_read_second_brief_rendering_pilot.v0"
    )
    assert review["source_case"]["case_id"] == "deploy-assisted-intake-routing"
    assert review["source_supply_status"] == "ready_for_offline_brief_rendering"
    assert review["rendering_status"] == "rendered_from_generated_read_supply"
    assert review["domain_compliance_caveats_preserved"] is True
    assert review["decision_gate"] == (
        "proceed_to_two_case_generated_read_brief_pattern_review"
    )
    assert (
        review["recommended_next_pr"]
        == "PR190 Two-Case Generated Read Brief Pattern Review v0"
    )
    assert review["custody_flags"]["model_calls"] == 0
    assert review["custody_flags"]["skill_invoked"] is False
    assert review["custody_flags"]["triage_generated"] is False
    assert review["custody_flags"]["runtime_sidecar_updated"] is False
    assert review["custody_flags"]["product_proof"] is False
    assert review["custody_flags"]["human_validated"] is False
    assert review["custody_flags"]["answer_quality_scored"] is False
    assert review["custody_flags"]["agent_action_authorized"] is False
    assert review["downstream_boundary"]["can_compare_two_case_pattern"] is True
    assert review["downstream_boundary"]["can_generate_triage"] is False
    assert review["downstream_boundary"]["can_update_runtime_sidecar"] is False


def test_second_pilot_docs_and_discoverability_are_linked() -> None:
    expected = "Decision Work Generated Read Second Brief Rendering Pilot"
    for path in (
        DOC_PATH,
        PRD_PATH,
        PR187_DOC,
        PR188_DOC,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)
    assert "proceed_to_two_case_generated_read_brief_pattern_review" in (
        DOC_PATH.read_text(encoding="utf-8")
    )


def test_second_pilot_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            RENDERED_PATH,
            REVIEW_PATH,
            READ_PATH,
            INTAKE_PATH,
            PRD_PATH,
            PR187_DOC,
            PR188_DOC,
            README_PATH,
            HOW_IT_WORKS_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_second_pilot_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        RENDERED_PATH,
        REVIEW_PATH,
        READ_PATH,
        INTAKE_PATH,
        PRD_PATH,
        PR188_DOC,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for marker in FORBIDDEN_STRINGS:
            assert marker not in text, f"{path}:{marker}"
