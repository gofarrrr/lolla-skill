from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-generated-read-triage-generation-pilot-v0.md"
)
TRIAGE_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-generated-read-triage-generation-pilot-v0/triage.json"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-generated-read-triage-generation-pilot-v0/review.json"
)
READ_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/read.json"
)
INTAKE_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/intake.json"
)
RENDERED_BRIEF_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-generated-read-rendered-launch-public-enterprise-beta-v0.md"
)
BRIEF_SUPPLY_SCRIPT = (
    REPO_ROOT / "scripts/evals/build_decision_work_generated_read_brief_supply.py"
)
TRIAGE_SUPPLY_SCRIPT = (
    REPO_ROOT / "scripts/evals/build_decision_work_generated_read_triage_supply.py"
)
PR192_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-generated-read-triage-supply-adapter-v0.md"
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
REQUIRED_ROUTES = {
    "ordinary_caveated_offline_brief_candidate",
    "source_depth_insufficient",
    "private_context_required",
    "high_overtrust_risk",
    "runtime_attachment_blocked",
}
FORBIDDEN_ROUTES = {
    "good_answer",
    "bad_answer",
    "approved",
    "certified",
    "safe_to_act",
    "correct_advice",
    "lolla_improved_decision",
    "human_validated",
    "product_proof",
    "agent_action_authorized",
    "automatic_action_authorized",
}


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_triage_read_schema_case_routes_and_status() -> None:
    triage = _json(TRIAGE_PATH)

    assert triage["schema_version"] == "lolla.decision_work_generated_read_triage.v0"
    assert triage["source_case"]["case_id"] == "launch-public-enterprise-beta"
    assert triage["source_triage_supply_status"] == (
        "ready_for_offline_triage_generation"
    )
    assert triage["triage_status"] == "generated_provisional_checked_in_safe"
    assert set(triage["route_categories"]) == REQUIRED_ROUTES
    assert set(triage["route_categories"]).isdisjoint(FORBIDDEN_ROUTES)
    assert triage["forbidden_route_concepts_absent"] is True
    assert set(triage["route_categories_forbidden"]) == FORBIDDEN_ROUTES


def test_route_explanations_preserve_sources_uncertainty_and_quality_boundary() -> None:
    triage = _json(TRIAGE_PATH)

    assert len(triage["route_explanations"]) == len(REQUIRED_ROUTES)
    for explanation in triage["route_explanations"]:
        assert explanation["route_category"] in REQUIRED_ROUTES
        assert explanation["finding"]
        assert explanation["source_refs"]
        assert explanation["uncertainty"] in {"low", "medium", "high"}
        assert explanation["source_depth_limit"]
        assert explanation["must_not_be_used_as_quality_label"] is True
        for ref in explanation["source_refs"]:
            if ref.startswith(("docs/", "reviews/")):
                assert (REPO_ROOT / ref).exists(), ref


def test_triage_read_preserves_boundaries_and_non_claims() -> None:
    triage = _json(TRIAGE_PATH)
    custody = triage["custody_flags"]
    runtime = triage["runtime_attachment_boundary"]
    agent = triage["agent_inspection_boundary"]
    user = triage["user_surface_boundary"]

    assert triage["uncertainty"]["overall"] == "medium"
    assert triage["uncertainty"]["uncertainty_preserved"] is True
    assert triage["overtrust_risk"]["status"] == "present"
    assert triage["private_context_need"]["status"] == "required_for_stronger_claims"
    assert runtime["can_update_sidecar"] is False
    assert runtime["can_mark_resolver_refs_usable"] is False
    assert agent["agent_action_authorized"] is False
    assert user["ready_for_customer_use"] is False
    assert custody["model_calls"] == 0
    assert custody["provider_api_calls"] == 0
    assert custody["runtime_invoked"] is False
    assert custody["skill_invoked"] is False
    assert custody["archive_mutated"] is False
    assert custody["resolver_refs_marked_usable"] is False
    assert custody["runtime_sidecar_updated"] is False
    assert custody["product_proof"] is False
    assert custody["human_validated"] is False
    assert custody["answer_quality_scored"] is False
    assert custody["agent_action_authorized"] is False
    assert custody["automatic_action_authorized"] is False
    assert "triage_read_routes_attention_only" in triage["non_claims"]
    assert "triage_read_does_not_update_runtime_sidecars" in triage["non_claims"]


def test_review_json_records_pr193_gate_and_downstream_boundary() -> None:
    review = _json(REVIEW_PATH)

    assert (
        review["schema_version"]
        == "lolla.decision_work_generated_read_triage_generation_pilot_review.v0"
    )
    assert review["source_case"]["case_id"] == "launch-public-enterprise-beta"
    assert review["source_triage_supply_status"] == (
        "ready_for_offline_triage_generation"
    )
    assert review["triage_read_ref"] == (
        "reviews/codex-assisted/"
        "decision-work-generated-read-triage-generation-pilot-v0/triage.json"
    )
    assert review["triage_generation_status"] == (
        "generated_provisional_checked_in_safe"
    )
    assert set(review["route_categories_selected"]) == REQUIRED_ROUTES
    assert review["forbidden_categories_absent"] is True
    assert review["uncertainty_preserved"] is True
    assert review["privacy_limits_preserved"] is True
    assert review["non_claims_preserved"] is True
    assert review["downstream_boundary"]["can_review_triage_pilot"] is True
    assert review["downstream_boundary"]["can_attempt_second_case_after_review"] is False
    assert review["downstream_boundary"]["can_mark_resolver_refs_usable"] is False
    assert review["downstream_boundary"]["can_update_runtime_sidecar"] is False
    assert review["downstream_boundary"]["can_wire_runtime"] is False
    assert review["downstream_boundary"]["can_call_models"] is False
    assert review["downstream_boundary"]["can_authorize_agent_action"] is False
    assert review["decision_gate"] == "proceed_to_generated_read_triage_pilot_review"
    assert (
        review["recommended_next_pr"]
        == "PR194 Decision Work Generated Read Triage Pilot Review v0"
    )


def test_pr193_matches_generated_triage_supply_status(tmp_path: Path) -> None:
    brief_supply = tmp_path / "brief_supply.json"
    triage_supply = tmp_path / "triage_supply.json"

    subprocess.run(
        [
            sys.executable,
            str(BRIEF_SUPPLY_SCRIPT),
            "--read",
            str(READ_PATH),
            "--intake",
            str(INTAKE_PATH),
            "--out",
            str(brief_supply),
            "--pretty",
        ],
        check=True,
        cwd=REPO_ROOT,
    )
    subprocess.run(
        [
            sys.executable,
            str(TRIAGE_SUPPLY_SCRIPT),
            "--read",
            str(READ_PATH),
            "--intake",
            str(INTAKE_PATH),
            "--brief-supply",
            str(brief_supply),
            "--rendered-brief",
            str(RENDERED_BRIEF_PATH),
            "--out",
            str(triage_supply),
            "--pretty",
        ],
        check=True,
        cwd=REPO_ROOT,
    )

    generated_supply = _json(triage_supply)
    triage = _json(TRIAGE_PATH)
    review = _json(REVIEW_PATH)

    assert generated_supply["triage_supply_status"] == (
        triage["source_triage_supply_status"]
    )
    assert generated_supply["triage_supply_status"] == (
        review["source_triage_supply_status"]
    )
    assert generated_supply["downstream_allowed"]["can_update_sidecar"] is False
    assert generated_supply["downstream_allowed"]["can_approve_resolver_refs"] is False


def test_doc_records_scope_routes_and_gate() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "# Decision Work Generated Read Triage Generation Pilot v0" in text
    assert "lolla.decision_work_generated_read_triage.v0" in text
    assert "launch-public-enterprise-beta" in text
    assert "ordinary_caveated_offline_brief_candidate" in text
    assert "source_depth_insufficient" in text
    assert "private_context_required" in text
    assert "high_overtrust_risk" in text
    assert "runtime_attachment_blocked" in text
    assert "proceed_to_generated_read_triage_pilot_review" in text
    assert "PR194 Decision Work Generated Read Triage Pilot Review v0" in text
    assert "does not call" in text
    assert "providers or model APIs" in text


def test_discoverability_docs_reference_pr193() -> None:
    expected = "Decision Work Generated Read Triage Generation Pilot"
    for path in (
        PROGRESS_PATH,
        BOARD_README_PATH,
        PRD_PATH,
        PR192_DOC,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr193_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            TRIAGE_PATH,
            REVIEW_PATH,
            PR192_DOC,
            PRD_PATH,
            README_PATH,
            HOW_IT_WORKS_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_pr193_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        TRIAGE_PATH,
        REVIEW_PATH,
        PR192_DOC,
        PRD_PATH,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for marker in FORBIDDEN_STRINGS:
            assert marker not in text, f"{path}:{marker}"
