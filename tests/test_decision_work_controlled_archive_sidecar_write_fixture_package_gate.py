from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-controlled-archive-sidecar-write-fixture-package-gate-v0.md"
)
MANIFEST_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-controlled-archive-sidecar-write-fixture-package-manifest-v0.json"
)
PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md"
)
PR215_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-controlled-archive-sidecar-write-fixture-review-v0.md"
)
PR215_REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-controlled-archive-sidecar-write-fixture-review-v0/review.json"
)
ADAPTER_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-controlled-archive-sidecar-write-fixture-adapter-v0.md"
)
PLAN_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-controlled-archive-sidecar-write-fixture-plan-v0.md"
)
README_PATH = REPO_ROOT / "README.md"
HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"
EXPECTED_SCHEMA = (
    "lolla.decision_work_controlled_archive_sidecar_write_fixture_package_manifest.v0"
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
    "docs/conversation-understanding/decision-work-controlled-archive-sidecar-write-fixture-plan-v0.md",
    "reviews/codex-assisted/decision-work-controlled-archive-sidecar-write-fixture-plan-v0/review.json",
    "tests/test_decision_work_controlled_archive_sidecar_write_fixture_plan.py",
    "docs/conversation-understanding/decision-work-controlled-archive-sidecar-write-fixture-adapter-v0.md",
    "engine/system_b/decision_work_controlled_archive_sidecar_write_fixture.py",
    "scripts/evals/write_decision_work_controlled_archive_sidecar_fixture.py",
    "tests/test_decision_work_controlled_archive_sidecar_write_fixture.py",
    "docs/conversation-understanding/decision-work-controlled-archive-sidecar-write-fixture-review-v0.md",
    "reviews/codex-assisted/decision-work-controlled-archive-sidecar-write-fixture-review-v0/review.json",
    "tests/test_decision_work_controlled_archive_sidecar_write_fixture_review.py",
    "docs/conversation-understanding/decision-work-controlled-archive-sidecar-write-fixture-package-gate-v0.md",
    "docs/conversation-understanding/decision-work-controlled-archive-sidecar-write-fixture-package-manifest-v0.json",
    "tests/test_decision_work_controlled_archive_sidecar_write_fixture_package_gate.py",
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
    assert metadata["included_pr_range"] == "PR213-PR216"
    assert metadata["dependency_pr_range_by_reference"] == "PR178-PR212"
    assert metadata["controlled_archive_sidecar_write_fixture_v1_functional"] is True
    assert metadata["synthetic_archive_fixture_only"] is True
    assert metadata["controlled_fixture_or_operator_output_only"] is True
    assert metadata["offline_only"] is True
    assert metadata["deterministic_only"] is True
    assert metadata["checked_in_safe_scope"] is True
    assert metadata["fixture_sidecar_writes"] is True
    assert metadata["real_archive_mutation"] is False
    assert metadata["historical_archive_mutation"] is False
    assert metadata["archive_hook_changed"] is False
    assert metadata["runtime_wiring"] is False
    assert metadata["resolver_refs_approved"] is False
    assert metadata["resolver_refs_marked_usable"] is False
    assert metadata["default_on_runtime_behavior"] is False
    assert metadata["direct_runtime_interpretation"] is False
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
    assert "tmp fixture outputs" in manifest["excluded_paths"]
    for ref in files:
        assert ref not in FORBIDDEN_EXACT
        assert not any(ref.startswith(prefix) for prefix in FORBIDDEN_PREFIXES)


def test_manifest_groups_plan_adapter_review_package_code_cli_and_tests() -> None:
    manifest = _load_manifest()
    included = manifest["included_files"]

    assert (
        "engine/system_b/decision_work_controlled_archive_sidecar_write_fixture.py"
        in included["code_modules"]
    )
    assert (
        "scripts/evals/write_decision_work_controlled_archive_sidecar_fixture.py"
        in included["cli_scripts"]
    )
    assert (
        "reviews/codex-assisted/decision-work-controlled-archive-sidecar-write-fixture-review-v0/review.json"
        in included["review_artifacts"]
    )
    assert MANIFEST_PATH.relative_to(REPO_ROOT).as_posix() in (
        included["package_gate_files"]
    )
    assert PACKAGE_DOC.relative_to(REPO_ROOT).as_posix() in (
        included["package_gate_files"]
    )


def test_package_claim_is_synthetic_fixture_and_non_overclaiming() -> None:
    manifest = _load_manifest()
    claim = manifest["package_claim"]
    claim_text = json.dumps(claim, sort_keys=True).lower()

    assert "synthetic archive-shaped fixture write layer" in claim["claim"]
    assert "deterministic_controlled_archive_sidecar_write_fixture_adapter" in (
        claim["allowed_claims"]
    )
    assert "launch_fixture_write_completed" in claim["allowed_claims"]
    assert "deploy_fixture_write_completed_blocked_state" in claim["allowed_claims"]
    assert "not_real_archive_mutation" in claim["claim_limits"]
    assert "not_historical_archive_mutation" in claim["claim_limits"]
    assert "not_archive_hook_integration" in claim["claim_limits"]
    assert "not_resolver_approval" in claim["claim_limits"]
    assert "default-on" not in claim_text
    assert "customer-ready" not in claim_text


def test_case_coverage_statuses_target_safety_and_non_claims() -> None:
    manifest = _load_manifest()
    cases = manifest["case_coverage"]["controlled_archive_fixture_cases"]
    statuses = {case["case_id"]: case["fixture_write_status"] for case in cases}
    non_claims = set(manifest["non_claims"])
    target_safety = manifest["target_dir_safety"]

    assert statuses["launch-public-enterprise-beta"] == "fixture_write_completed"
    assert statuses["deploy-assisted-intake-routing"] == (
        "fixture_write_completed_blocked_state"
    )
    for case in cases:
        assert case["synthetic_archive_fixture_only"] is True
        assert case["files_written_expected"] == 6
        assert case["real_archive_mutated"] is False
        assert case["historical_archive_mutated"] is False
        assert case["archive_hook_changed"] is False
        assert case["runtime_wiring_changed"] is False
        assert case["resolver_refs_approved"] is False
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
    assert target_safety["target_fixture_archive_dir_must_be_explicit"] is True
    assert target_safety["target_fixture_archive_dir_must_have_archive_shape"] is True
    assert target_safety["target_fixture_archive_dir_must_have_fixture_marker"] is True
    assert (
        target_safety["target_fixture_archive_dir_must_be_temp_or_output_only"]
        is True
    )
    assert target_safety["target_fixture_archive_dir_must_not_be_inside_repo"] is True
    assert (
        target_safety["target_fixture_archive_dir_must_not_target_real_archive"]
        is True
    )
    assert (
        target_safety[
            "target_fixture_archive_dir_must_not_target_existing_historical_archive"
        ]
        is True
    )
    assert target_safety["target_fixture_archive_dir_must_not_target_runtime"] is True
    assert target_safety["checked_in_sidecar_files_created"] is False
    assert "not_real_archive_write" in non_claims
    assert "not_historical_archive_mutation" in non_claims
    assert "not_archive_hook_integration" in non_claims
    assert "not_runtime_integration" in non_claims
    assert "not_resolver_approval" in non_claims
    assert "not_answer_quality_scoring" in non_claims
    assert "not_advice_correctness" in non_claims
    assert "not_approval_or_certification" in non_claims
    assert "not_agent_action_authorization" in non_claims
    assert "not_automatic_action_authorization" in non_claims


def test_package_doc_records_functionality_limits_and_next_step() -> None:
    text = PACKAGE_DOC.read_text(encoding="utf-8")

    assert "# Decision Work Controlled Archive Sidecar Write Fixture Package Gate v0" in text
    assert "Narrow Controlled Archive Fixture v1 Claim" in text
    assert "Functional Chain" in text
    assert "What Is Functional" in text
    assert "What Remains Missing" in text
    assert "Fixture Target Safety" in text
    assert "controlled_archive_sidecar_write_fixture_v1_packaged" in text
    assert "PR217 Real Archive Sidecar Write Plan v0" in text
    assert "Do not implement PR217" in text
    assert "real archive mutation" in text
    assert "archive-hook integration" in text
    assert "resolver approval" in text
    assert "runtime wiring" in text


def test_discoverability_docs_reference_pr216() -> None:
    expected = "Decision Work Controlled Archive Sidecar Write Fixture Package Gate"
    for path in (
        PACKAGE_DOC,
        PR215_DOC,
        PRD_PATH,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr216_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            PACKAGE_DOC,
            MANIFEST_PATH,
            PR215_DOC,
            PR215_REVIEW,
            ADAPTER_DOC,
            PLAN_DOC,
            PRD_PATH,
            README_PATH,
            HOW_IT_WORKS_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_pr216_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        PACKAGE_DOC,
        MANIFEST_PATH,
        PR215_DOC,
        PR215_REVIEW,
        ADAPTER_DOC,
        PLAN_DOC,
        PRD_PATH,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for forbidden in PRIVATE_MARKERS:
            assert forbidden not in text, (path, forbidden)
