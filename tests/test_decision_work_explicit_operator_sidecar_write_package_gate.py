from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-explicit-operator-sidecar-write-package-gate-v0.md"
)
MANIFEST_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-explicit-operator-sidecar-write-package-manifest-v0.json"
)
PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md"
)
PR211_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-explicit-operator-sidecar-write-review-v0.md"
)
PR211_REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-explicit-operator-sidecar-write-review-v0/review.json"
)
ADAPTER_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-explicit-operator-sidecar-write-adapter-v0.md"
)
README_PATH = REPO_ROOT / "README.md"
HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"
EXPECTED_SCHEMA = (
    "lolla.decision_work_explicit_operator_sidecar_write_package_manifest.v0"
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
    "docs/conversation-understanding/decision-work-explicit-operator-sidecar-write-adapter-v0.md",
    "engine/system_b/decision_work_explicit_operator_sidecar_write.py",
    "scripts/evals/write_decision_work_sidecar_explicit_operator.py",
    "tests/test_decision_work_explicit_operator_sidecar_write.py",
    "docs/conversation-understanding/decision-work-explicit-operator-sidecar-write-review-v0.md",
    "reviews/codex-assisted/decision-work-explicit-operator-sidecar-write-review-v0/review.json",
    "tests/test_decision_work_explicit_operator_sidecar_write_review.py",
    "docs/conversation-understanding/decision-work-explicit-operator-sidecar-write-package-gate-v0.md",
    "docs/conversation-understanding/decision-work-explicit-operator-sidecar-write-package-manifest-v0.json",
    "tests/test_decision_work_explicit_operator_sidecar_write_package_gate.py",
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
    assert metadata["included_pr_range"] == "PR210-PR212"
    assert metadata["dependency_pr_range_by_reference"] == "PR178-PR209"
    assert metadata["explicit_operator_sidecar_write_v1_functional"] is True
    assert metadata["controlled_fixture_or_operator_output_only"] is True
    assert metadata["offline_only"] is True
    assert metadata["deterministic_only"] is True
    assert metadata["checked_in_safe_scope"] is True
    assert metadata["fixture_sidecar_writes"] is True
    assert metadata["real_archive_mutation"] is False
    assert metadata["historical_archive_mutation"] is False
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


def test_manifest_groups_adapter_review_package_code_cli_and_tests() -> None:
    manifest = _load_manifest()
    included = manifest["included_files"]

    assert (
        "engine/system_b/decision_work_explicit_operator_sidecar_write.py"
        in included["code_modules"]
    )
    assert (
        "scripts/evals/write_decision_work_sidecar_explicit_operator.py"
        in included["cli_scripts"]
    )
    assert (
        "reviews/codex-assisted/decision-work-explicit-operator-sidecar-write-review-v0/review.json"
        in included["review_artifacts"]
    )
    assert MANIFEST_PATH.relative_to(REPO_ROOT).as_posix() in (
        included["package_gate_files"]
    )
    assert PACKAGE_DOC.relative_to(REPO_ROOT).as_posix() in (
        included["package_gate_files"]
    )


def test_package_claim_is_fixture_write_and_non_overclaiming() -> None:
    manifest = _load_manifest()
    claim = manifest["package_claim"]
    claim_text = json.dumps(claim, sort_keys=True).lower()

    assert "explicit" in claim["claim"].lower()
    assert "operator-directed" in claim["claim"].lower()
    assert "fixture/operator target directories" in claim["claim"]
    assert "deterministic_explicit_operator_sidecar_write_adapter" in (
        claim["allowed_claims"]
    )
    assert "launch_write_completed_fixture_only" in claim["allowed_claims"]
    assert "deploy_write_completed_blocked_state_fixture_only" in (
        claim["allowed_claims"]
    )
    assert "not_real_archive_mutation" in claim["claim_limits"]
    assert "not_historical_archive_mutation" in claim["claim_limits"]
    assert "not_resolver_approval" in claim["claim_limits"]
    assert "not_runtime_wiring" in claim["claim_limits"]
    assert "default-on" not in claim_text
    assert "customer-ready" not in claim_text


def test_case_coverage_statuses_target_safety_and_non_claims() -> None:
    manifest = _load_manifest()
    cases = manifest["case_coverage"]["explicit_operator_sidecar_write_cases"]
    statuses = {case["case_id"]: case["write_status"] for case in cases}
    non_claims = set(manifest["non_claims"])
    target_safety = manifest["target_dir_safety"]

    assert statuses["launch-public-enterprise-beta"] == "write_completed_fixture_only"
    assert statuses["deploy-assisted-intake-routing"] == (
        "write_completed_blocked_state_fixture_only"
    )
    for case in cases:
        assert case["fixture_only"] is True
        assert case["files_written_expected"] == 6
        assert case["real_archive_mutated"] is False
        assert case["historical_archive_mutated"] is False
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
    assert target_safety["target_sidecar_dir_must_be_explicit"] is True
    assert target_safety["target_sidecar_dir_must_be_named_decision_work"] is True
    assert target_safety["target_sidecar_dir_must_be_temp_or_output_only"] is True
    assert target_safety["target_sidecar_dir_must_not_be_inside_repo"] is True
    assert target_safety["target_sidecar_dir_must_not_target_real_archive"] is True
    assert target_safety["target_sidecar_dir_must_not_target_runtime"] is True
    assert target_safety["checked_in_sidecar_files_created"] is False
    assert "not_runtime_integration" in non_claims
    assert "not_real_archive_mutation_as_normal_behavior" in non_claims
    assert "not_resolver_approval" in non_claims
    assert "not_answer_quality_scoring" in non_claims
    assert "not_advice_correctness" in non_claims
    assert "not_approval_or_certification" in non_claims
    assert "not_agent_action_authorization" in non_claims
    assert "not_automatic_action_authorization" in non_claims


def test_package_doc_records_functionality_limits_and_next_step() -> None:
    text = PACKAGE_DOC.read_text(encoding="utf-8")

    assert "# Decision Work Explicit Operator Sidecar Write Package Gate v0" in text
    assert "Narrow Explicit Operator Write v1 Claim" in text
    assert "Functional Chain" in text
    assert "What Is Functional" in text
    assert "What Remains Missing" in text
    assert "Fixture Target Safety" in text
    assert "explicit_operator_sidecar_write_v1_packaged" in text
    assert "PR213 Controlled Archive Sidecar Write Fixture Plan v0" in text
    assert "Do not implement PR213" in text
    assert "real archive mutation" in text
    assert "resolver approval" in text
    assert "runtime wiring" in text


def test_discoverability_docs_reference_pr212() -> None:
    expected = "Decision Work Explicit Operator Sidecar Write Package Gate"
    for path in (
        PACKAGE_DOC,
        PR211_DOC,
        PRD_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr212_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            PACKAGE_DOC,
            MANIFEST_PATH,
            PR211_DOC,
            PR211_REVIEW,
            ADAPTER_DOC,
            PRD_PATH,
            README_PATH,
            HOW_IT_WORKS_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_pr212_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        PACKAGE_DOC,
        MANIFEST_PATH,
        PR211_DOC,
        PR211_REVIEW,
        ADAPTER_DOC,
        PRD_PATH,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for forbidden in PRIVATE_MARKERS:
            assert forbidden not in text, (path, forbidden)
