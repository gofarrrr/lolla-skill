from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-offline-v1-closure-gate-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-offline-v1-closure-gate-v0/review.json"
)
TRIAGE_READ_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-automatic-triage-provisional-read-v0/read.json"
)
TRIAGE_CONTRACT_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-triage-contract-v0.json"
)
SCHEMA_VERSION = "lolla.decision_work_brief_offline_v1_closure_gate.v0"
ALLOWED_DECISION_GATES = {
    "package_offline_v1",
    "patch_triage_layer_before_v1",
    "patch_brief_surface_before_v1",
    "run_one_more_case_before_v1",
    "pause_for_human_calibration",
    "stop_and_simplify",
}
REQUIRED_FALSE_FIELDS = {
    "human_validated",
    "human_review_completed",
    "product_proof",
    "runtime_invoked",
    "skill_invoked",
    "archive_mutated",
    "answer_quality_scored",
    "agent_action_authorized",
    "automatic_action_authorized",
}
PRIVACY_MARKERS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)


def _review() -> dict[str, Any]:
    return json.loads(REVIEW_PATH.read_text(encoding="utf-8"))


def _collect_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        strings: list[str] = []
        for item in value:
            strings.extend(_collect_strings(item))
        return strings
    if isinstance(value, dict):
        strings = []
        for item in value.values():
            strings.extend(_collect_strings(item))
        return strings
    return []


def test_offline_v1_closure_schema_and_custody_are_conservative() -> None:
    review = _review()

    assert review["schema_version"] == SCHEMA_VERSION
    assert review["review_mode"] == "offline_v1_closure_readiness_review"
    assert review["model_calls"] == 0
    assert review["human_calibration_deferred"] is True
    assert review["codex_assisted_provisional"] is True
    for field in REQUIRED_FALSE_FIELDS:
        assert review[field] is False
    assert review["decision_gate"] in ALLOWED_DECISION_GATES


def test_functional_v1_claim_is_narrow_and_limitation_bound() -> None:
    claim = _review()["functional_v1_claim"]

    assert claim["offline_v1_functional"] is True
    assert claim["claim_scope"] == "offline_evidence_system_only"
    assert claim["limitations_are_required_context"] is True
    assert claim["can_prepare_automatic_triage_packets"] is True
    assert claim["can_create_codex_assisted_provisional_triage_reads"] is True
    assert claim["runtime_integrated"] is False
    assert claim["customer_ready"] is False
    assert claim["human_validated"] is False
    assert claim["product_proof"] is False
    assert claim["answer_quality_scored"] is False
    assert claim["agent_action_authorized"] is False


def test_closure_references_pr155_pr156_and_source_artifacts() -> None:
    review = _review()
    artifacts = review["source_artifacts"]

    assert artifacts["automatic_triage_contract_ref"] == str(
        TRIAGE_CONTRACT_PATH.relative_to(REPO_ROOT)
    )
    assert artifacts["automatic_triage_provisional_read_ref"] == str(
        TRIAGE_READ_PATH.relative_to(REPO_ROOT)
    )
    assert len(artifacts["builder_outputs"]) == 3
    assert len(artifacts["interpretation_reads"]) == 3
    for ref in _repo_refs(review):
        assert (REPO_ROOT / ref).exists(), ref


def test_runtime_and_customer_surface_remain_blocked() -> None:
    review = _review()

    assert review["automatic_triage_status"]["runtime_attachment_blocked_for_all_cases"] is True
    assert "no_runtime_attachment_contract" in review["runtime_blockers"]
    assert "no_human_review_response" in review["customer_surface_blockers"]
    assert "human_validated" in review["blocked_claims"]
    assert "product_proof" in review["blocked_claims"]
    assert "agent_action_authorized" in review["blocked_claims"]


def test_package_gate_only_when_pr155_and_pr156_work() -> None:
    review = _review()

    assert review["automatic_triage_status"]["contract_exists"] is True
    assert review["automatic_triage_status"]["packet_builder_exists"] is True
    assert review["automatic_triage_status"]["local_packet_generated_successfully"] is True
    assert review["automatic_triage_status"]["provisional_read_exists"] is True
    assert review["decision_gate"] == "package_offline_v1"
    assert review["recommended_next_pr"] == (
        "PR158 Decision Work Brief Offline v1 Package Gate v0"
    )


def test_non_claims_and_text_have_no_private_or_authority_leaks() -> None:
    text = REVIEW_PATH.read_text(encoding="utf-8") + "\n" + DOC_PATH.read_text(
        encoding="utf-8"
    )

    for marker in PRIVACY_MARKERS:
        assert marker not in text
    for fragment in (
        '"human_validated": true',
        '"product_proof": true',
        '"answer_quality_scored": true',
        '"agent_action_authorized": true',
        '"automatic_action_authorized": true',
        '"runtime_integrated": true',
        '"customer_ready": true',
        "safe_for_agent_use",
    ):
        assert fragment not in text
    assert "not_runtime_integration" in _review()["non_claims"]
    assert "not_customer_readiness_claim" in _review()["non_claims"]


def test_closure_docs_and_json_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths(
        [DOC_PATH, REVIEW_PATH, TRIAGE_READ_PATH, TRIAGE_CONTRACT_PATH]
    )

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }


def _repo_refs(value: Any) -> set[str]:
    return {
        item
        for item in _collect_strings(value)
        if item.startswith(("docs/", "reviews/", "engine/", "scripts/"))
    }
