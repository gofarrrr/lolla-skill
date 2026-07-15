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
    / "docs/conversation-understanding/decision-work-generated-read-second-triage-pilot-v0.md"
)
TRIAGE_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-generated-read-second-triage-pilot-v0/triage.json"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-generated-read-second-triage-pilot-v0/review.json"
)
READ_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-generated-read-second-brief-rendering-pilot-v0/read.json"
)
INTAKE_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-generated-read-second-brief-rendering-pilot-v0/intake.json"
)
RENDERED_BRIEF_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-generated-read-rendered-deploy-assisted-intake-routing-v0.md"
)
BRIEF_SUPPLY_SCRIPT = (
    REPO_ROOT / "scripts/evals/build_decision_work_generated_read_brief_supply.py"
)
TRIAGE_SUPPLY_SCRIPT = (
    REPO_ROOT / "scripts/evals/build_decision_work_generated_read_triage_supply.py"
)
PR193_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-generated-read-triage-generation-pilot-v0.md"
)
PR194_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-generated-read-triage-pilot-review-v0.md"
)
PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md"
)
HISTORICAL_DISCOVERY_PATH = REPO_ROOT / "docs/history/decision-work-product-delta-discoverability.md"
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
    "source_depth_insufficient",
    "private_context_required",
    "high_overtrust_risk",
    "domain_review_recommended",
    "legal_or_compliance_review_recommended",
    "not_ready_for_user_surface",
    "agent_inspection_only",
    "runtime_attachment_blocked",
}
FORBIDDEN_ROUTES = {
    "good_answer",
    "bad_answer",
    "approved",
    "certified",
    "safe_to_act",
    "safe_to_deploy",
    "clinically_validated",
    "legally_adequate",
    "compliance_cleared",
    "correct_advice",
    "lolla_improved_decision",
    "human_validated",
    "product_proof",
    "agent_action_authorized",
    "automatic_action_authorized",
}


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_second_triage_read_schema_case_routes_and_status() -> None:
    triage = _json(TRIAGE_PATH)

    assert triage["schema_version"] == "lolla.decision_work_generated_read_triage.v0"
    assert triage["source_case"]["case_id"] == "deploy-assisted-intake-routing"
    assert triage["source_case"]["decision_family"] == (
        "healthcare_operations_or_deployment"
    )
    assert triage["source_triage_supply_status"] == (
        "ready_for_offline_triage_generation"
    )
    assert triage["triage_status"] == "generated_provisional_checked_in_safe"
    assert set(triage["route_categories"]) == REQUIRED_ROUTES
    assert "ordinary_caveated_offline_brief_candidate" not in triage[
        "route_categories"
    ]
    assert set(triage["route_categories"]).isdisjoint(FORBIDDEN_ROUTES)
    assert triage["forbidden_route_concepts_absent"] is True
    assert set(triage["route_categories_forbidden"]) == FORBIDDEN_ROUTES


def test_second_route_explanations_preserve_domain_caveats_and_quality_boundary() -> None:
    triage = _json(TRIAGE_PATH)

    assert len(triage["route_explanations"]) == len(REQUIRED_ROUTES)
    explanation_by_route = {
        explanation["route_category"]: explanation
        for explanation in triage["route_explanations"]
    }
    assert set(explanation_by_route) == REQUIRED_ROUTES
    assert "compliance" in explanation_by_route[
        "legal_or_compliance_review_recommended"
    ]["finding"]
    assert "outpatient-clinic workflow" in explanation_by_route[
        "domain_review_recommended"
    ]["finding"]
    for explanation in triage["route_explanations"]:
        assert explanation["source_refs"]
        assert explanation["uncertainty"] in {"low", "medium", "high"}
        assert explanation["source_depth_limit"]
        assert explanation["must_not_be_used_as_quality_label"] is True
        for ref in explanation["source_refs"]:
            if ref.startswith(("docs/", "reviews/")):
                assert (REPO_ROOT / ref).exists(), ref


def test_second_triage_read_preserves_domain_runtime_and_action_boundaries() -> None:
    triage = _json(TRIAGE_PATH)
    custody = triage["custody_flags"]
    runtime = triage["runtime_attachment_boundary"]
    agent = triage["agent_inspection_boundary"]
    user = triage["user_surface_boundary"]

    assert triage["uncertainty"]["overall"] == "medium"
    assert triage["uncertainty"]["uncertainty_preserved"] is True
    assert triage["overtrust_risk"]["status"] == "high_for_domain_sensitive_case"
    assert triage["domain_or_legal_review_need"]["status"] == (
        "required_before_operational_use"
    )
    assert triage["private_context_need"]["status"] == "required_for_stronger_claims"
    assert runtime["can_update_sidecar"] is False
    assert runtime["can_mark_resolver_refs_usable"] is False
    assert agent["agent_action_authorized"] is False
    assert user["can_feed_future_offline_user_surface_review"] is False
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
    assert "triage_read_is_not_legal_or_clinical_clearance" in triage["non_claims"]
    assert "triage_read_is_not_deployment_permission" in triage["non_claims"]


def test_second_review_json_records_pr195_gate_and_downstream_boundary() -> None:
    review = _json(REVIEW_PATH)

    assert (
        review["schema_version"]
        == "lolla.decision_work_generated_read_second_triage_pilot_review.v0"
    )
    assert review["source_case"]["case_id"] == "deploy-assisted-intake-routing"
    assert review["source_triage_supply_status"] == (
        "ready_for_offline_triage_generation"
    )
    assert review["triage_read_ref"] == (
        "reviews/codex-assisted/"
        "decision-work-generated-read-second-triage-pilot-v0/triage.json"
    )
    assert review["triage_generation_status"] == (
        "generated_provisional_checked_in_safe"
    )
    assert set(review["route_categories_selected"]) == REQUIRED_ROUTES
    assert review["forbidden_categories_absent"] is True
    assert review["domain_caveats_preserved"] is True
    assert review["uncertainty_preserved"] is True
    assert review["privacy_limits_preserved"] is True
    assert review["non_claims_preserved"] is True
    assert review["downstream_boundary"]["can_review_two_case_triage_pattern"] is True
    assert review["downstream_boundary"]["can_plan_resolver_supply"] is False
    assert review["downstream_boundary"]["can_mark_resolver_refs_usable"] is False
    assert review["downstream_boundary"]["can_update_runtime_sidecar"] is False
    assert review["downstream_boundary"]["can_wire_runtime"] is False
    assert review["downstream_boundary"]["can_call_models"] is False
    assert review["downstream_boundary"]["can_authorize_agent_action"] is False
    assert review["decision_gate"] == (
        "proceed_to_two_case_generated_read_triage_pattern_review"
    )
    assert (
        review["recommended_next_pr"]
        == "PR196 Two-Case Generated Read Triage Pattern Review v0"
    )


def test_pr195_matches_generated_triage_supply_status(tmp_path: Path) -> None:
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
    assert generated_supply["downstream_allowed"]["can_be_used_as_quality_label"] is (
        False
    )


def test_second_doc_records_scope_routes_domain_boundary_and_gate() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "# Decision Work Generated Read Second Triage Pilot v0" in text
    assert "lolla.decision_work_generated_read_triage.v0" in text
    assert "deploy-assisted-intake-routing" in text
    assert "domain_review_recommended" in text
    assert "legal_or_compliance_review_recommended" in text
    assert "not_ready_for_user_surface" in text
    assert "agent_inspection_only" in text
    assert "proceed_to_two_case_generated_read_triage_pattern_review" in text
    assert "PR196 Two-Case Generated Read Triage Pattern Review v0" in text
    assert "does not call" in text
    assert "providers or model APIs" in text
    assert "claim legal, compliance, clinical, or deployment clearance" in text


def test_discoverability_docs_reference_pr195() -> None:
    expected = "Decision Work Generated Read Second Triage Pilot"
    for path in (
        HISTORICAL_DISCOVERY_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
        PRD_PATH,
        PR193_DOC,
        PR194_DOC,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr195_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            TRIAGE_PATH,
            REVIEW_PATH,
            PR193_DOC,
            PR194_DOC,
            PRD_PATH,
            HISTORICAL_DISCOVERY_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_pr195_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        TRIAGE_PATH,
        REVIEW_PATH,
        PR193_DOC,
        PR194_DOC,
        PRD_PATH,
        HISTORICAL_DISCOVERY_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for marker in FORBIDDEN_STRINGS:
            assert marker not in text, f"{path}:{marker}"
