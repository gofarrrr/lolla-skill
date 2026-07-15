from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-runtime-sidecar-write-contract-v0.md"
)
JSON_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-runtime-sidecar-write-contract-v0.json"
)
PACKAGE_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-sidecar-write-dry-run-package-gate-v0.md"
)
PACKAGE_MANIFEST = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-sidecar-write-dry-run-package-manifest-v0.json"
)
PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md"
)
HISTORICAL_DISCOVERY_PATH = REPO_ROOT / "docs/history/decision-work-product-delta-discoverability.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"
SCHEMA_VERSION = "lolla.decision_work_runtime_sidecar_write_contract.v0"
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "contract_metadata",
    "purpose",
    "allowed_input_schemas",
    "required_preconditions",
    "write_modes",
    "sidecar_write_statuses",
    "status_policy",
    "allowed_files",
    "forbidden_content",
    "path_policy",
    "launch_handling",
    "deploy_handling",
    "audit_receipt_requirements",
    "custody_flags",
    "fail_closed_reasons",
    "non_claims",
    "decision_gate",
    "recommended_next_pr",
}
REQUIRED_STATUSES = {
    "not_requested",
    "blocked_dry_run_missing",
    "blocked_packet_not_write_eligible",
    "blocked_archive_path_unsafe",
    "blocked_runtime_mode_not_allowed",
    "blocked_privacy_risk",
    "blocked_authority_claim",
    "write_ready",
    "write_ready_blocked_state_only",
    "write_completed",
    "failed_closed",
}
REQUIRED_MODES = {
    "disabled",
    "dry_run_only",
    "explicit_operator_write",
    "future_runtime_hook_write_not_allowed_yet",
}
REQUIRED_ALLOWED_FILES = {
    "attachment_status.json",
    "user_receipt.md",
    "agent_handoff_packet.json",
    "safe_supply_summary.json",
    "sidecar_update_packet.json",
    "sidecar_write_receipt.json",
}
REQUIRED_FORBIDDEN_CONTENT = {
    "raw_conversation_text",
    "raw_revised_answer_text",
    "raw_memo_text",
    "provider_text",
    "private_ledgers",
    "local_absolute_paths_inside_checked_in_artifacts",
    "secrets",
    "credentials",
    "approval_or_certification_labels",
    "answer_quality_labels_or_scores",
    "action_authorization",
    "unchecked_provider_model_outputs",
}
REQUIRED_FALSE_FLAGS = {
    "runtime_invoked",
    "skill_invoked",
    "actual_sidecar_write_performed",
    "archive_mutated",
    "runtime_wiring_changed",
    "runtime_attachment_default_on",
    "resolver_refs_approved",
    "resolver_refs_marked_usable",
    "product_proof",
    "human_validated",
    "answer_quality_scored",
    "advice_correctness_claimed",
    "agent_action_authorized",
    "automatic_action_authorized",
}
REQUIRED_NON_CLAIMS = {
    "not_actual_sidecar_write",
    "not_archive_mutation",
    "not_runtime_wiring",
    "not_resolver_approval",
    "not_approved_resolver_refs",
    "not_resolver_refs_marked_usable",
    "not_default_on_behavior",
    "not_model_calls",
    "not_product_proof",
    "not_human_validation",
    "not_answer_quality_scoring",
    "not_advice_correctness",
    "not_lolla_improvement_proof",
    "not_agent_action_authorization",
    "not_automatic_action_authorization",
}
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


def _contract() -> dict[str, Any]:
    return json.loads(JSON_PATH.read_text(encoding="utf-8"))


def _collect_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend(_collect_strings(item))
        return result
    if isinstance(value, dict):
        result = []
        for item in value.values():
            result.extend(_collect_strings(item))
        return result
    return []


def _collect_repo_refs(value: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key.endswith("_ref") or key.endswith("_refs") or key == "ref":
                refs.update(_collect_strings(child))
            refs.update(_collect_repo_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.update(_collect_repo_refs(child))
    return {ref for ref in refs if ref.startswith(("docs/", "reviews/", "tests/"))}


def test_contract_schema_metadata_and_top_level_shape() -> None:
    contract = _contract()
    metadata = contract["contract_metadata"]

    assert contract["schema_version"] == SCHEMA_VERSION
    assert REQUIRED_TOP_LEVEL <= set(contract)
    assert metadata["contract_mode"] == "docs_schema_tests_only"
    assert metadata["source_package_ref"] == PACKAGE_DOC.relative_to(REPO_ROOT).as_posix()
    assert metadata["source_package_manifest_ref"] == (
        PACKAGE_MANIFEST.relative_to(REPO_ROOT).as_posix()
    )
    assert "sidecar_write_adapter" in metadata["not_implemented_here"]
    assert "archive_mutation" in metadata["not_implemented_here"]
    assert "runtime_hook_write" in metadata["not_implemented_here"]
    assert metadata["actual_sidecar_write_performed"] is False
    assert metadata["archive_mutated"] is False
    assert metadata["runtime_wiring_changed"] is False
    assert metadata["resolver_refs_approved"] is False
    assert contract["decision_gate"] == "proceed_to_explicit_operator_sidecar_write_adapter"
    assert contract["recommended_next_pr"] == (
        "PR210 Explicit Operator Sidecar Write Adapter v0"
    )


def test_contract_references_existing_package_and_input_schemas() -> None:
    contract = _contract()
    schemas = {item["schema_version"] for item in contract["allowed_input_schemas"]}

    assert "lolla.decision_work_resolver_candidate_sidecar_update_packet.v0" in schemas
    assert "lolla.decision_work_sidecar_write_dry_run.v0" in schemas
    for ref in _collect_repo_refs(contract):
        assert (REPO_ROOT / ref).exists(), ref


def test_required_preconditions_fail_closed() -> None:
    contract = _contract()
    preconditions = {item["name"]: item for item in contract["required_preconditions"]}

    assert preconditions["dry_run_result_exists"]["failure_status"] == (
        "blocked_dry_run_missing"
    )
    assert preconditions["dry_run_source_matches_packet"]["required"] is True
    assert preconditions["dry_run_has_no_blockers"]["required"] is True
    assert preconditions["archive_path_explicitly_supplied"]["failure_status"] == (
        "blocked_archive_path_unsafe"
    )
    assert preconditions["archive_path_passes_allowlist_safety_checks"][
        "failure_status"
    ] == "blocked_archive_path_unsafe"
    assert preconditions["write_mode_explicitly_set"]["failure_status"] == (
        "blocked_runtime_mode_not_allowed"
    )
    assert preconditions["runtime_hook_remains_default_off"]["required"] is True
    assert preconditions["privacy_markers_absent"]["failure_status"] == (
        "blocked_privacy_risk"
    )
    assert preconditions["authority_claims_absent"]["failure_status"] == (
        "blocked_authority_claim"
    )


def test_write_modes_and_statuses_are_conservative() -> None:
    contract = _contract()
    modes = {item["mode"]: item for item in contract["write_modes"]}

    assert REQUIRED_MODES <= set(modes)
    assert REQUIRED_STATUSES <= set(contract["sidecar_write_statuses"])
    assert modes["disabled"]["may_write_archive"] is False
    assert modes["dry_run_only"]["may_write_archive"] is False
    assert modes["future_runtime_hook_write_not_allowed_yet"]["may_write_archive"] is False
    assert modes["future_runtime_hook_write_not_allowed_yet"]["may_wire_runtime"] is False
    assert modes["explicit_operator_write"]["implemented_here"] is False
    assert modes["explicit_operator_write"]["may_write_archive"] == (
        "future_pr_only_after_contract"
    )
    assert contract["status_policy"]["write_completed"]["implemented_here"] is False
    assert contract["status_policy"]["write_completed"][
        "must_remain_not_resolver_approval"
    ] is True


def test_allowed_files_forbidden_content_and_path_policy() -> None:
    contract = _contract()
    path_policy = contract["path_policy"]

    assert REQUIRED_ALLOWED_FILES <= set(contract["allowed_files"])
    assert REQUIRED_FORBIDDEN_CONTENT <= set(contract["forbidden_content"])
    assert path_policy["archive_path_must_be_explicit"] is True
    assert path_policy["archive_path_must_pass_allowlist"] is True
    assert path_policy["checked_in_artifacts_must_not_include_local_absolute_paths"] is True
    assert path_policy["tmp_preview_outputs_not_valid_archive_targets"] is True
    assert path_policy["runtime_hook_paths_not_writable_by_this_contract"] is True


def test_launch_and_deploy_handling_preserve_boundaries() -> None:
    contract = _contract()
    launch = contract["launch_handling"]
    deploy = contract["deploy_handling"]

    assert launch["case_id"] == "launch-public-enterprise-beta"
    assert launch["required_dry_run_status"] == "dry_run_ready"
    assert launch["future_status_if_preconditions_pass"] == "write_ready"
    assert launch["actual_write_implemented_here"] is False
    assert launch["resolver_refs_approved"] is False
    assert launch["action_authorized"] is False
    assert deploy["case_id"] == "deploy-assisted-intake-routing"
    assert deploy["required_dry_run_status"] == "dry_run_packet_with_runtime_block"
    assert deploy["future_status_if_preconditions_pass"] == (
        "write_ready_blocked_state_only"
    )
    assert deploy["normal_available_sidecar_allowed"] is False
    assert deploy["runtime_use_status"] == "blocked"
    assert deploy["user_surface_status"] == "blocked"
    assert deploy["agent_inspection_status"] == "inspection_only"
    assert deploy["deployment_authorization"] is False
    assert deploy["legal_compliance_clinical_clearance"] is False
    assert deploy["resolver_refs_approved"] is False


def test_audit_receipt_custody_flags_and_non_claims_are_conservative() -> None:
    contract = _contract()
    receipt = contract["audit_receipt_requirements"]
    custody = contract["custody_flags"]

    assert receipt["sidecar_write_receipt_required_for_future_write"] is True
    assert "source_sidecar_update_packet_ref" in receipt["required_receipt_fields"]
    assert "source_dry_run_result_ref" in receipt["required_receipt_fields"]
    assert "candidate_refs_remain_candidate" in receipt["required_receipt_fields"]
    assert receipt["archive_mutated_can_be_true_only_after_future_explicit_write"] is True
    assert receipt["runtime_wiring_changed_must_remain_false"] is True
    assert receipt["resolver_refs_approved_must_remain_false"] is True
    for flag in REQUIRED_FALSE_FLAGS:
        assert custody[flag] is False, flag
    assert custody["model_calls"] == 0
    assert REQUIRED_NON_CLAIMS <= set(contract["non_claims"])


def test_contract_doc_records_boundary_statuses_and_next_pr() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "# Decision Work Runtime Sidecar Write Contract v0" in text
    assert "This is docs, schema, and tests only" in text
    assert "Allowed Inputs" in text
    assert "Write Modes" in text
    assert "Allowed Files" in text
    assert "Never Write" in text
    assert "Fail Closed" in text
    assert "proceed_to_explicit_operator_sidecar_write_adapter" in text
    assert "PR210 Explicit Operator Sidecar Write Adapter v0" in text
    assert "Do not implement PR210" in text


def test_discoverability_docs_reference_pr209() -> None:
    expected = "Decision Work Runtime Sidecar Write Contract"
    for path in (
        DOC_PATH,
        PACKAGE_DOC,
        PRD_PATH,
        HISTORICAL_DISCOVERY_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr209_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            JSON_PATH,
            PACKAGE_DOC,
            PACKAGE_MANIFEST,
            PRD_PATH,
            HISTORICAL_DISCOVERY_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_pr209_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        JSON_PATH,
        PACKAGE_DOC,
        PACKAGE_MANIFEST,
        PRD_PATH,
        HISTORICAL_DISCOVERY_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_STRINGS:
            assert forbidden not in text, (path, forbidden)
