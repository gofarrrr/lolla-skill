from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-sidecar-automation-readiness-package-gate-v0.md"
)
MANIFEST_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-sidecar-automation-readiness-package-manifest-v0.json"
)
READINESS_PRD = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-sidecar-automation-readiness-prd-v0.md"
)
PR232_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-second-non-curated-pilot-review-v0.md"
)
PR232_REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-second-non-curated-pilot-review-v0/"
    "review.json"
)
AUTOMATIC_SUPPLY_PRD = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-automatic-semantic-supply-prd-v0.md"
)
RUNNER_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-offline-operator-runner-adapter-v0.md"
)
PR229_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-non-curated-completed-run-pilot-v0.md"
)
PR231_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-second-non-curated-completed-run-pilot-v0.md"
)
README_PATH = REPO_ROOT / "README.md"
HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"
EXPECTED_SCHEMA = (
    "lolla.decision_work_sidecar_automation_readiness_package_manifest.v0"
)
FORBIDDEN_PREFIXES = (
    "scripts/skill/",
    "plans/",
    "reviews/synthetic/",
    "docs/lolla-",
    "docs/semantica-",
    "docs/thoughtbox-",
    "archive/",
    "archives/",
    "runs/",
    "tmp/",
)
FORBIDDEN_EXACT = {"SKILL.md", "scripts/archive_run.py"}
PRIVATE_MARKERS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)
REQUIRED_FILES = {
    "docs/conversation-understanding/decision-work-sidecar-automation-readiness-prd-v0.md",
    "reviews/codex-assisted/decision-work-sidecar-automation-readiness-prd-v0/review.json",
    "tests/test_decision_work_sidecar_automation_readiness_prd.py",
    "docs/conversation-understanding/decision-work-offline-operator-runner-plan-v0.md",
    "reviews/codex-assisted/decision-work-offline-operator-runner-plan-v0/review.json",
    "tests/test_decision_work_offline_operator_runner_plan.py",
    "docs/conversation-understanding/decision-work-offline-operator-runner-adapter-v0.md",
    "engine/system_b/decision_work_offline_operator_runner.py",
    "scripts/evals/run_decision_work_offline_operator.py",
    "tests/test_decision_work_offline_operator_runner.py",
    "docs/conversation-understanding/decision-work-offline-operator-runner-fixture-review-v0.md",
    "reviews/codex-assisted/decision-work-offline-operator-runner-fixture-review-v0/review.json",
    "tests/test_decision_work_offline_operator_runner_fixture_review.py",
    "docs/conversation-understanding/decision-work-non-curated-completed-run-pilot-plan-v0.md",
    "reviews/codex-assisted/decision-work-non-curated-completed-run-pilot-plan-v0/review.json",
    "tests/test_decision_work_non_curated_completed_run_pilot_plan.py",
    "docs/conversation-understanding/decision-work-non-curated-completed-run-pilot-v0.md",
    "reviews/codex-assisted/decision-work-non-curated-completed-run-pilot-v0/review.json",
    "tests/test_decision_work_non_curated_completed_run_pilot.py",
    "docs/conversation-understanding/decision-work-non-curated-pilot-review-v0.md",
    "reviews/codex-assisted/decision-work-non-curated-pilot-review-v0/review.json",
    "tests/test_decision_work_non_curated_pilot_review.py",
    "docs/conversation-understanding/decision-work-second-non-curated-completed-run-pilot-v0.md",
    "reviews/codex-assisted/decision-work-second-non-curated-completed-run-pilot-v0/review.json",
    "tests/test_decision_work_second_non_curated_completed_run_pilot.py",
    "docs/conversation-understanding/decision-work-second-non-curated-pilot-review-v0.md",
    "reviews/codex-assisted/decision-work-second-non-curated-pilot-review-v0/review.json",
    "tests/test_decision_work_second_non_curated_pilot_review.py",
    "docs/conversation-understanding/decision-work-sidecar-automation-readiness-package-gate-v0.md",
    "docs/conversation-understanding/decision-work-sidecar-automation-readiness-package-manifest-v0.json",
    "tests/test_decision_work_sidecar_automation_readiness_package_gate.py",
}


def _load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _manifest_files(manifest: dict[str, Any]) -> list[str]:
    files: list[str] = []
    for group in manifest["included_files"].values():
        assert isinstance(group, list)
        files.extend(item for item in group if isinstance(item, str))
    return files


def test_manifest_schema_and_package_metadata() -> None:
    manifest = _load_manifest()
    metadata = manifest["package_metadata"]

    assert manifest["schema_version"] == EXPECTED_SCHEMA
    assert metadata["included_pr_range"] == "PR224-PR233"
    assert metadata["dependency_pr_range_by_reference"] == "PR178-PR223"
    assert metadata["automation_readiness_v1_packaged"] is True
    assert metadata["automation_readiness_v1_functional"] is True
    assert metadata["offline_only"] is True
    assert metadata["command_only"] is True
    assert metadata["one_shot_runner"] is True
    assert metadata["explicit_input_paths_required"] is True
    assert metadata["runner_summary_json"] is True
    assert metadata["runner_writes_sidecar"] is False
    assert metadata["actual_sidecar_write_performed"] is False
    assert metadata["archive_mutated"] is False
    assert metadata["historical_archive_mutated"] is False
    assert metadata["runtime_wiring"] is False
    assert metadata["runtime_attachment_default_on"] is False
    assert metadata["resolver_refs_approved"] is False
    assert metadata["queue_workers_or_daemons"] is False
    assert metadata["provider_model_calls"] == 0
    assert metadata["semantic_interpretation_generated"] is False
    assert metadata["arbitrary_run_semantic_generation"] is False
    assert metadata["fresh_non_curated_semantic_understanding_proof"] is False
    assert metadata["checked_in_runner_outputs_created"] is False
    assert metadata["checked_in_sidecar_outputs_created"] is False
    assert metadata["human_validated"] is False
    assert metadata["product_proof"] is False
    assert metadata["answer_quality_scored"] is False
    assert metadata["advice_correctness_claimed"] is False
    assert metadata["approval_or_certification_added"] is False
    assert metadata["agent_action_authorized"] is False
    assert metadata["automatic_action_authorized"] is False


def test_manifest_includes_required_files_and_all_exist() -> None:
    manifest = _load_manifest()
    files = set(_manifest_files(manifest))

    assert REQUIRED_FILES <= files
    for ref in sorted(files):
        assert (REPO_ROOT / ref).exists(), ref


def test_manifest_excludes_forbidden_paths() -> None:
    manifest = _load_manifest()
    files = _manifest_files(manifest)

    assert "SKILL.md" in manifest["excluded_paths"]
    assert "scripts/skill/*" in manifest["excluded_paths"]
    assert "scripts/archive_run.py" in manifest["excluded_paths"]
    assert "plans/*" in manifest["excluded_paths"]
    assert "reviews/synthetic/*" in manifest["excluded_paths"]
    assert "docs/lolla-*" in manifest["excluded_paths"]
    assert "docs/semantica-*" in manifest["excluded_paths"]
    assert "docs/thoughtbox-*" in manifest["excluded_paths"]
    assert "checked-in runner_summary.json outputs" in manifest["excluded_paths"]
    assert "checked-in dry-run outputs" in manifest["excluded_paths"]
    assert "checked-in preview files" in manifest["excluded_paths"]
    assert "checked-in decision_work sidecar outputs" in (
        manifest["excluded_paths"]
    )
    for ref in files:
        assert ref not in FORBIDDEN_EXACT
        assert not any(ref.startswith(prefix) for prefix in FORBIDDEN_PREFIXES)
        assert "runner_summary.json" not in ref
        assert "/decision_work/" not in f"/{ref}/"


def test_manifest_groups_runner_pilots_package_code_cli_and_tests() -> None:
    manifest = _load_manifest()
    included = manifest["included_files"]

    assert "engine/system_b/decision_work_offline_operator_runner.py" in (
        included["runner_adapter"]
    )
    assert "scripts/evals/run_decision_work_offline_operator.py" in (
        included["cli_scripts"]
    )
    assert (
        "reviews/codex-assisted/decision-work-second-non-curated-pilot-review-v0/review.json"
        in included["review_artifacts"]
    )
    assert MANIFEST_PATH.relative_to(REPO_ROOT).as_posix() in (
        included["package_gate_files"]
    )
    assert PACKAGE_DOC.relative_to(REPO_ROOT).as_posix() in (
        included["package_gate_files"]
    )


def test_package_claim_is_offline_runner_and_non_overclaiming() -> None:
    manifest = _load_manifest()
    claim = manifest["package_claim"]
    claim_text = json.dumps(claim, sort_keys=True).lower()

    assert "offline, command-only operator-runner layer" in claim["claim"]
    assert "stop safely on missing semantic inputs" in claim["claim"]
    assert "reach dry-run readiness" in claim["claim"]
    assert "one_shot_offline_operator_runner_exists" in claim["allowed_claims"]
    assert "missing_semantic_input_defers_visibly" in claim["allowed_claims"]
    assert (
        "existing_safe_semantic_input_reaches_dry_run_readiness"
        in claim["allowed_claims"]
    )
    assert "not_arbitrary_run_semantic_generation" in claim["claim_limits"]
    assert (
        "not_fresh_non_curated_semantic_understanding_proof"
        in claim["claim_limits"]
    )
    assert "not_runtime_hook_integration" in claim["claim_limits"]
    assert "not_resolver_approval" in claim["claim_limits"]
    assert "customer-ready" not in claim_text


def test_case_coverage_records_missing_input_and_deep_ready_signals() -> None:
    manifest = _load_manifest()
    pilots = manifest["case_coverage"]["non_curated_pilots"]
    statuses = {pilot["case_id"]: pilot["final_status"] for pilot in pilots}
    pr229 = next(
        pilot
        for pilot in pilots
        if pilot["case_id"] == "non-curated-sanitized-missing-read-fixture"
    )
    pr231 = next(
        pilot
        for pilot in pilots
        if pilot["case_id"] == "second-non-curated-existing-semantic-input-fixture"
    )

    assert statuses["non-curated-sanitized-missing-read-fixture"] == (
        "deferred_missing_semantic_read"
    )
    assert statuses["second-non-curated-existing-semantic-input-fixture"] == (
        "sidecar_ready_for_explicit_write"
    )
    assert pr229["stopped_at"] == "generated_read"
    assert pr229["generated_read_present"] is False
    assert pr229["generated_triage_present"] is False
    assert pr229["new_semantic_material_created"] is False
    assert pr231["stopped_at"] == "dry_run_complete"
    assert pr231["semantic_inputs_existing_checked_in_safe"] is True
    assert pr231["semantic_inputs_reused_from_launch_like_pair"] is True
    assert pr231["new_semantic_material_created"] is False
    assert "sidecar_write_dry_run" in pr231["completed_steps"]
    for pilot in pilots:
        assert pilot["actual_sidecar_write_performed"] is False
        assert pilot["archive_mutated"] is False
        assert pilot["historical_archive_mutated"] is False


def test_fixture_cases_preserve_launch_deploy_statuses_without_writes() -> None:
    manifest = _load_manifest()
    cases = manifest["case_coverage"]["fixture_cases"]
    statuses = {case["case_id"]: case["final_status"] for case in cases}

    assert statuses["launch-public-enterprise-beta"] == (
        "sidecar_ready_for_explicit_write"
    )
    assert statuses["deploy-assisted-intake-routing"] == (
        "sidecar_ready_blocked_state"
    )
    deploy = next(
        case for case in cases if case["case_id"] == "deploy-assisted-intake-routing"
    )
    assert deploy["runtime_block_preserved"] is True
    assert deploy["user_surface_block_preserved"] is True
    for case in cases:
        assert case["actual_sidecar_write_performed"] is False
        assert case["archive_mutated"] is False
        assert case["historical_archive_mutated"] is False
        assert case["runtime_wiring_changed"] is False
        assert case["resolver_refs_approved"] is False


def test_runner_output_contract_and_non_claims_stay_closed() -> None:
    manifest = _load_manifest()
    contract = manifest["runner_output_contract"]
    non_claims = set(manifest["non_claims"])

    assert contract["schema_version"] == (
        "lolla.decision_work_offline_operator_runner.v0"
    )
    assert contract["explicit_input_paths_only"] is True
    assert contract["auto_discover_private_archive_data"] is False
    assert contract["semantic_interpretation_generated"] is False
    assert contract["semantic_artifacts_repaired"] is False
    assert contract["write_attempted"] is False
    assert contract["actual_sidecar_write_performed"] is False
    assert contract["archive_mutated"] is False
    assert contract["runtime_wiring_changed"] is False
    assert contract["resolver_refs_approved"] is False
    assert "not_queue_worker_or_daemon" in non_claims
    assert "not_runtime_hook_integration" in non_claims
    assert "not_resolver_approval" in non_claims
    assert "not_automatic_sidecar_write" in non_claims
    assert "not_answer_quality_scoring" in non_claims
    assert "not_advice_correctness" in non_claims
    assert "not_agent_action_authorization" in non_claims
    assert manifest["decision_gate"] == "automation_readiness_v1_packaged"
    assert manifest["recommended_next_pr"] == (
        "PR234 Receipt / Blocked-State Language Review v0"
    )


def test_package_doc_records_functionality_limits_and_next_step() -> None:
    text = PACKAGE_DOC.read_text(encoding="utf-8")

    assert "# Decision Work Sidecar Automation Readiness Package Gate v0" in text
    assert "Narrow Automation Readiness v1 Claim" in text
    assert "What Is Functional" in text
    assert "What Remains Missing" in text
    assert "Pilot Evidence" in text
    assert "automation_readiness_v1_packaged" in text
    assert "PR234 Receipt / Blocked-State Language Review v0" in text
    assert "do not show arbitrary non-curated semantic automation" in text
    assert "no actual sidecar write" in text.lower()
    assert "queue worker" in text
    assert "runtime hook" in text


def test_discoverability_docs_reference_pr233() -> None:
    expected = "Decision Work Sidecar Automation Readiness Package Gate"
    for path in (
        PACKAGE_DOC,
        READINESS_PRD,
        PR232_DOC,
        AUTOMATIC_SUPPLY_PRD,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr233_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            PACKAGE_DOC,
            MANIFEST_PATH,
            READINESS_PRD,
            PR232_DOC,
            PR232_REVIEW,
            AUTOMATIC_SUPPLY_PRD,
            RUNNER_DOC,
            PR229_DOC,
            PR231_DOC,
            README_PATH,
            HOW_IT_WORKS_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0
    assert result["summary"]["info_count"] == 0


def test_pr233_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        PACKAGE_DOC,
        MANIFEST_PATH,
        READINESS_PRD,
        PR232_DOC,
        PR232_REVIEW,
        AUTOMATIC_SUPPLY_PRD,
        RUNNER_DOC,
        PR229_DOC,
        PR231_DOC,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for forbidden in PRIVATE_MARKERS:
            assert forbidden not in text, (path, forbidden)
