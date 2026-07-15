from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-real-archive-sidecar-write-package-gate-v0.md"
)
MANIFEST_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-real-archive-sidecar-write-package-manifest-v0.json"
)
PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md"
)
INTERNAL_V1_PRD = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-sidecar-internal-v1-completion-prd-v0.md"
)
PR220_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-real-archive-sidecar-write-review-v0.md"
)
PR220_REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-real-archive-sidecar-write-review-v0/"
    "review.json"
)
ADAPTER_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-real-archive-sidecar-write-adapter-v0.md"
)
PLAN_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-real-archive-sidecar-write-plan-v0.md"
)
HISTORICAL_DISCOVERY_PATH = REPO_ROOT / "docs/history/decision-work-product-delta-discoverability.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"
EXPECTED_SCHEMA = "lolla.decision_work_real_archive_sidecar_write_package_manifest.v0"
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
    "docs/conversation-understanding/decision-work-real-archive-sidecar-write-plan-v0.md",
    "reviews/codex-assisted/decision-work-real-archive-sidecar-write-plan-v0/review.json",
    "tests/test_decision_work_real_archive_sidecar_write_plan.py",
    "docs/conversation-understanding/decision-work-real-archive-sidecar-write-adapter-v0.md",
    "engine/system_b/decision_work_real_archive_sidecar_write.py",
    "scripts/evals/write_decision_work_real_archive_sidecar.py",
    "tests/test_decision_work_real_archive_sidecar_write.py",
    "docs/conversation-understanding/decision-work-real-archive-sidecar-write-review-v0.md",
    "reviews/codex-assisted/decision-work-real-archive-sidecar-write-review-v0/review.json",
    "tests/test_decision_work_real_archive_sidecar_write_review.py",
    "docs/conversation-understanding/decision-work-real-archive-sidecar-write-package-gate-v0.md",
    "docs/conversation-understanding/decision-work-real-archive-sidecar-write-package-manifest-v0.json",
    "tests/test_decision_work_real_archive_sidecar_write_package_gate.py",
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
    assert metadata["included_pr_range"] == "PR218-PR221"
    assert metadata["dependency_pr_range_by_reference"] == "PR178-PR217"
    assert metadata["real_archive_sidecar_write_v1_functional"] is True
    assert metadata["command_only"] is True
    assert metadata["operator_confirmation_required"] is True
    assert metadata["no_overwrite_v1"] is True
    assert metadata["validated_against_synthetic_completed_run_archive_dirs"] is True
    assert metadata["offline_only"] is True
    assert metadata["deterministic_only"] is True
    assert metadata["runtime_wiring"] is False
    assert metadata["archive_hook_changed"] is False
    assert metadata["runtime_attachment_default_on"] is False
    assert metadata["resolver_refs_approved"] is False
    assert metadata["resolver_refs_marked_usable"] is False
    assert metadata["queue_workers_or_daemons"] is False
    assert metadata["provider_model_calls"] == 0
    assert metadata["human_validated"] is False
    assert metadata["product_proof"] is False
    assert metadata["answer_quality_scored"] is False
    assert metadata["advice_correctness_claimed"] is False
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
    for ref in files:
        assert ref not in FORBIDDEN_EXACT
        assert not any(ref.startswith(prefix) for prefix in FORBIDDEN_PREFIXES)


def test_manifest_groups_plan_adapter_review_package_code_cli_and_tests() -> None:
    manifest = _load_manifest()
    included = manifest["included_files"]

    assert (
        "engine/system_b/decision_work_real_archive_sidecar_write.py"
        in included["code_modules"]
    )
    assert (
        "scripts/evals/write_decision_work_real_archive_sidecar.py"
        in included["cli_scripts"]
    )
    assert (
        "reviews/codex-assisted/decision-work-real-archive-sidecar-write-review-v0/review.json"
        in included["review_artifacts"]
    )
    assert MANIFEST_PATH.relative_to(REPO_ROOT).as_posix() in (
        included["package_gate_files"]
    )
    assert PACKAGE_DOC.relative_to(REPO_ROOT).as_posix() in (
        included["package_gate_files"]
    )


def test_package_claim_is_command_only_and_non_overclaiming() -> None:
    manifest = _load_manifest()
    claim = manifest["package_claim"]
    claim_text = json.dumps(claim, sort_keys=True).lower()

    assert "command-only, explicit-operator" in claim["claim"]
    assert "no-overwrite sidecar write layer" in claim["claim"]
    assert "deterministic_command_only_real_archive_sidecar_write_adapter" in (
        claim["allowed_claims"]
    )
    assert "launch_real_archive_sidecar_write_completed" in claim["allowed_claims"]
    assert (
        "deploy_real_archive_sidecar_write_completed_blocked_state"
        in claim["allowed_claims"]
    )
    assert "not_runtime_wiring" in claim["claim_limits"]
    assert "not_archive_hook_integration" in claim["claim_limits"]
    assert "not_resolver_approval" in claim["claim_limits"]
    assert "customer-ready" not in claim_text
    assert "approved" not in claim_text


def test_case_coverage_statuses_target_safety_and_non_claims() -> None:
    manifest = _load_manifest()
    cases = manifest["case_coverage"]["real_archive_sidecar_write_cases"]
    statuses = {case["case_id"]: case["real_archive_write_status"] for case in cases}
    non_claims = set(manifest["non_claims"])
    target_safety = manifest["target_dir_safety"]

    assert statuses["launch-public-enterprise-beta"] == (
        "real_archive_sidecar_write_completed"
    )
    assert statuses["deploy-assisted-intake-routing"] == (
        "real_archive_sidecar_write_completed_blocked_state"
    )
    for case in cases:
        assert case["validation_target"] == "synthetic_completed_run_archive_dir"
        assert case["files_written_expected"] == 6
        assert case["actual_sidecar_write_performed"] is True
        assert case["real_archive_mutated_for_supplied_archive_dir"] is True
        assert case["historical_archive_mutated_for_supplied_archive_dir"] is True
        assert case["real_historical_archive_paths_touched"] is False
        assert case["archive_hook_changed"] is False
        assert case["runtime_wiring_changed"] is False
        assert case["resolver_refs_approved"] is False
        assert case["resolver_refs_marked_usable"] is False
        assert case["product_proof"] is False
        assert case["human_validated"] is False
        assert case["answer_quality_scored"] is False
        assert case["agent_action_authorized"] is False
        assert case["automatic_action_authorized"] is False
    deploy = next(
        case for case in cases if case["case_id"] == "deploy-assisted-intake-routing"
    )
    assert deploy["runtime_block_preserved"] is True
    assert deploy["user_surface_block_preserved"] is True
    assert target_safety["target_archive_dir_must_be_explicit"] is True
    assert target_safety["target_archive_dir_must_have_completed_run_markers"] is True
    assert target_safety["operator_confirmation_flag_required"] is True
    assert target_safety["dry_run_must_match_packet"] is True
    assert target_safety["existing_decision_work_sidecar_rejected_v1"] is True
    assert target_safety["generated_sidecar_files_checked_in"] is False
    assert "not_runtime_wiring" in non_claims
    assert "not_archive_hook_integration" in non_claims
    assert "not_resolver_approval" in non_claims
    assert "not_answer_quality_scoring" in non_claims
    assert manifest["decision_gate"] == "real_archive_sidecar_write_v1_packaged"
    assert manifest["recommended_next_pr"] == "PR222 Internal Demo / Operator Runbook v0"


def test_package_doc_and_discoverability_references() -> None:
    expected = "Decision Work Real Archive Sidecar Write Package Gate"
    for path in (
        PACKAGE_DOC,
        PR220_DOC,
        INTERNAL_V1_PRD,
        PRD_PATH,
        HISTORICAL_DISCOVERY_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr221_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            PACKAGE_DOC,
            MANIFEST_PATH,
            PR220_DOC,
            PR220_REVIEW,
            ADAPTER_DOC,
            PLAN_DOC,
            INTERNAL_V1_PRD,
            PRD_PATH,
            HISTORICAL_DISCOVERY_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0
    assert result["summary"]["info_count"] == 0


def test_manifest_and_docs_contain_no_forbidden_markers() -> None:
    for path in (
        PACKAGE_DOC,
        MANIFEST_PATH,
        PR220_DOC,
        PR220_REVIEW,
        ADAPTER_DOC,
        PLAN_DOC,
        INTERNAL_V1_PRD,
        PRD_PATH,
        HISTORICAL_DISCOVERY_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for forbidden in PRIVATE_MARKERS:
            assert forbidden not in text, (path, forbidden)
