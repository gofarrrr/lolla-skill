from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-triage-provisional-read-v0.md"
)
READ_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-automatic-triage-provisional-read-v0/read.json"
)
PACKET_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-triage-packet-builder-v0.md"
)
CONTRACT_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-triage-contract-v0.json"
)
SCHEMA_VERSION = "lolla.decision_work_automatic_triage_provisional_read.v0"
EXPECTED_CASES = {
    "launch-public-enterprise-beta",
    "deploy-assisted-intake-routing",
    "ceo-remove-founding-cofounder",
}
ALLOWED_DECISION_GATES = {
    "proceed_to_offline_v1_closure_gate",
    "patch_triage_contract",
    "patch_packet_builder",
    "run_more_provisional_triage_reads",
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


def _read() -> dict[str, Any]:
    return json.loads(READ_PATH.read_text(encoding="utf-8"))


def _contract() -> dict[str, Any]:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


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


def test_triage_read_schema_and_custody_are_conservative() -> None:
    read = _read()

    assert read["schema_version"] == SCHEMA_VERSION
    assert read["read_mode"] == "codex_assisted_provisional_triage"
    assert read["model_calls"] == 0
    assert read["human_calibration_deferred"] is True
    assert read["codex_assisted_provisional"] is True
    for field in REQUIRED_FALSE_FIELDS:
        assert read[field] is False
    assert read["decision_gate"] in ALLOWED_DECISION_GATES


def test_source_packet_summary_is_checked_in_safe_and_not_checked_in_fixture() -> None:
    summary = _read()["source_packet_summary"]

    assert summary["packet_schema_version"] == (
        "lolla.decision_work_automatic_triage_packets.v0"
    )
    assert summary["packet_generated_locally"] is True
    assert summary["packet_checked_in"] is False
    assert summary["packet_mode"] == "checked_in_safe"
    assert summary["semantic_triage_fields_filled_by_packet"] is False
    assert (REPO_ROOT / summary["packet_builder_ref"]).exists()
    assert (REPO_ROOT / summary["packet_cli_ref"]).exists()
    assert (REPO_ROOT / summary["triage_contract_ref"]).exists()


def test_case_triage_reads_cover_three_cases_with_contract_values() -> None:
    read = _read()
    contract = _contract()
    categories = {item["category"] for item in contract["triage_categories"]}
    route_values = set(contract["route_value_vocabulary"])

    cases = read["case_triage_reads"]
    assert {case["case_id"] for case in cases} == EXPECTED_CASES
    for case in cases:
        assert set(case["triage_categories"]) <= categories
        for route_field in (
            "user_surface_route",
            "agent_inspection_route",
            "human_calibration_route",
            "domain_review_route",
            "runtime_attachment_route",
        ):
            assert case[route_field] in route_values
        assert case["must_not_be_used_as_quality_label"] is True
        assert case["uncertainty"] in {"low", "medium", "high", "insufficient_context"}
        assert case["source_refs"]
        for ref in case["source_refs"]:
            assert (REPO_ROOT / ref).exists(), ref


def test_case_specific_routes_preserve_overtrust_and_domain_caution() -> None:
    cases = {case["case_id"]: case for case in _read()["case_triage_reads"]}

    assert cases["launch-public-enterprise-beta"]["user_surface_route"] == (
        "allowed_with_caveats"
    )
    assert cases["deploy-assisted-intake-routing"]["domain_review_route"] == (
        "requires_domain_review"
    )
    assert cases["ceo-remove-founding-cofounder"]["user_surface_route"] == "not_ready"
    assert "high_overtrust_risk" in cases["ceo-remove-founding-cofounder"][
        "triage_categories"
    ]
    assert cases["ceo-remove-founding-cofounder"]["runtime_attachment_route"] == (
        "blocked_runtime"
    )


def test_runtime_and_agent_reads_do_not_authorize_action() -> None:
    read = _read()

    assert read["runtime_attachment_read"]["route"] == "blocked_runtime"
    assert read["agent_inspection_read"]["route"] == "agent_only"
    assert "do not authorize action" in read["agent_inspection_read"][
        "rationale"
    ].lower()
    assert "blocked" in read["runtime_attachment_read"]["route"]


def test_non_claims_and_text_do_not_assert_product_proof_or_human_validation() -> None:
    rendered = READ_PATH.read_text(encoding="utf-8")

    for marker in PRIVACY_MARKERS:
        assert marker not in rendered
    forbidden_fragments = (
        '"human_validated": true',
        '"product_proof": true',
        '"answer_quality_scored": true',
        '"agent_action_authorized": true',
        '"automatic_action_authorized": true',
        '"answer_quality_score":',
        '"improvement_score":',
        "safe_for_agent_use",
    )
    for fragment in forbidden_fragments:
        assert fragment not in rendered
    assert "not_product_proof" in _read()["non_claims"]
    assert "not_human_validation" in _read()["non_claims"]


def test_all_source_refs_resolve() -> None:
    refs = {
        item
        for item in _collect_strings(_read())
        if item.startswith(("docs/", "reviews/", "engine/", "scripts/"))
    }

    for ref in refs:
        assert not ref.startswith(("SKILL.md", "scripts/skill/", "plans/"))
        assert (REPO_ROOT / ref).exists(), ref


def test_triage_read_docs_and_json_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths([DOC_PATH, READ_PATH, PACKET_DOC_PATH])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
