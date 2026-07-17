from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-sidecar-write-dry-run-package-gate-v0.md"
)
MANIFEST_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-sidecar-write-dry-run-package-manifest-v0.json"
)
PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md"
)
PR207_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-sidecar-write-dry-run-review-v0.md"
)
PR207_REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-sidecar-write-dry-run-review-v0/review.json"
)
ADAPTER_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-sidecar-write-dry-run-adapter-v0.md"
)
README_PATH = REPO_ROOT / "README.md"
HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"
EXPECTED_SCHEMA = "lolla.decision_work_sidecar_write_dry_run_package_manifest.v0"
FORBIDDEN_PREFIXES = (
    "scripts/skill/",
    "plans/",
    "reviews/synthetic/",
    "docs/lolla-",
    "docs/semantica-",
    "docs/thoughtbox-",
    "archive/",
    "runs/",
    "tmp/",
)
FORBIDDEN_EXACT = {"SKILL.md"}
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
    "docs/conversation-understanding/decision-work-sidecar-write-dry-run-adapter-v0.md",
    "engine/system_b/decision_work_sidecar_write_dry_run.py",
    "scripts/evals/dry_run_decision_work_sidecar_write.py",
    "tests/test_decision_work_sidecar_write_dry_run.py",
    "docs/conversation-understanding/decision-work-sidecar-write-dry-run-review-v0.md",
    "reviews/codex-assisted/decision-work-sidecar-write-dry-run-review-v0/review.json",
    "tests/test_decision_work_sidecar_write_dry_run_review.py",
    "docs/conversation-understanding/decision-work-sidecar-write-dry-run-package-gate-v0.md",
    "docs/conversation-understanding/decision-work-sidecar-write-dry-run-package-manifest-v0.json",
    "tests/test_decision_work_sidecar_write_dry_run_package_gate.py",
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
    assert metadata["included_pr_range"] == "PR206-PR208"
    assert metadata["dependency_pr_range_by_reference"] == "PR178-PR205"
    assert metadata["dry_run_v1_functional"] is True
    assert metadata["offline_only"] is True
    assert metadata["deterministic_only"] is True
    assert metadata["checked_in_safe_scope"] is True
    assert metadata["actual_sidecar_writes"] is False
    assert metadata["archive_mutation"] is False
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
    assert "plans/*" in manifest["excluded_paths"]
    assert "reviews/synthetic/*" in manifest["excluded_paths"]
    assert "docs/lolla-*" in manifest["excluded_paths"]
    assert "docs/semantica-*" in manifest["excluded_paths"]
    assert "docs/thoughtbox-*" in manifest["excluded_paths"]
    assert "tmp preview outputs" in manifest["excluded_paths"]
    for ref in files:
        assert ref not in FORBIDDEN_EXACT
        assert not any(ref.startswith(prefix) for prefix in FORBIDDEN_PREFIXES)


def test_manifest_groups_dry_run_adapter_review_and_package_files() -> None:
    manifest = _load_manifest()
    included = manifest["included_files"]

    assert "engine/system_b/decision_work_sidecar_write_dry_run.py" in (
        included["dry_run_adapter"]
    )
    assert "scripts/evals/dry_run_decision_work_sidecar_write.py" in (
        included["cli_scripts"]
    )
    assert (
        "reviews/codex-assisted/decision-work-sidecar-write-dry-run-review-v0/review.json"
        in included["review_artifacts"]
    )
    assert MANIFEST_PATH.relative_to(REPO_ROOT).as_posix() in (
        included["package_gate_files"]
    )
    assert PACKAGE_DOC.relative_to(REPO_ROOT).as_posix() in (
        included["package_gate_files"]
    )


def test_package_claim_is_dry_run_and_non_overclaiming() -> None:
    manifest = _load_manifest()
    claim = manifest["package_claim"]
    claim_text = json.dumps(claim, sort_keys=True).lower()

    assert "dry-run" in claim["claim"].lower()
    assert "offline" in claim["claim"].lower()
    assert "preview layer" in claim["claim"]
    assert "deterministic_sidecar_write_dry_run_adapter" in claim["allowed_claims"]
    assert "launch_dry_run_ready" in claim["allowed_claims"]
    assert "deploy_dry_run_packet_with_runtime_block" in claim["allowed_claims"]
    assert "not_actual_sidecar_write" in claim["claim_limits"]
    assert "not_archive_mutation" in claim["claim_limits"]
    assert "not_resolver_approval" in claim["claim_limits"]
    assert "not_runtime_wiring" in claim["claim_limits"]
    assert "customer-ready" not in claim_text
    assert "default-on" not in claim_text


def test_case_coverage_statuses_preview_safety_and_non_claims() -> None:
    manifest = _load_manifest()
    cases = manifest["case_coverage"]["sidecar_write_dry_run_cases"]
    statuses = {case["case_id"]: case["dry_run_status"] for case in cases}
    non_claims = set(manifest["non_claims"])
    preview_safety = manifest["preview_dir_safety"]

    assert statuses["launch-public-enterprise-beta"] == "dry_run_ready"
    assert statuses["deploy-assisted-intake-routing"] == (
        "dry_run_packet_with_runtime_block"
    )
    for case in cases:
        assert case["resolver_refs_approved"] is False
        assert case["actual_sidecar_write_performed"] is False
        assert case["archive_mutated"] is False
        assert case["runtime_wiring_changed"] is False
        assert case["preview_files_expected"] == 5
    assert preview_safety["preview_dir_must_be_explicit"] is True
    assert preview_safety["preview_dir_must_not_target_decision_work"] is True
    assert preview_safety["preview_dir_must_not_target_archive"] is True
    assert preview_safety["checked_in_preview_files_created"] is False
    assert "not_actual_sidecar_write" in non_claims
    assert "not_archive_mutation" in non_claims
    assert "not_runtime_wiring" in non_claims
    assert "not_resolver_approval" in non_claims
    assert "not_answer_quality_scoring" in non_claims
    assert "not_advice_correctness" in non_claims
    assert "not_agent_action_authorization" in non_claims
    assert "not_automatic_action_authorization" in non_claims


def test_package_doc_records_functionality_limits_and_next_step() -> None:
    text = PACKAGE_DOC.read_text(encoding="utf-8")

    assert "# Decision Work Sidecar Write Dry-Run Package Gate v0" in text
    assert "Narrow Dry-Run v1 Claim" in text
    assert "Functional Chain" in text
    assert "What Is Functional" in text
    assert "What Remains Missing" in text
    assert "Preview Directory Safety" in text
    assert "sidecar_write_dry_run_v1_packaged" in text
    assert "PR209 Runtime Sidecar Write Contract v0" in text
    assert "Do not implement sidecar write code" in text
    assert "actual sidecar writes" in text
    assert "archive mutation" in text
    assert "resolver approval" in text


def test_discoverability_docs_reference_pr208() -> None:
    expected = "Decision Work Sidecar Write Dry-Run Package Gate"
    for path in (
        PACKAGE_DOC,
        PR207_DOC,
        PRD_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr208_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            PACKAGE_DOC,
            MANIFEST_PATH,
            PR207_DOC,
            PR207_REVIEW,
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


def test_pr208_artifacts_contain_no_private_markers() -> None:
    paths = [
        PACKAGE_DOC,
        MANIFEST_PATH,
        PR207_DOC,
        PR207_REVIEW,
        ADAPTER_DOC,
        PRD_PATH,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ]
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for marker in PRIVATE_MARKERS:
            assert marker not in text, (path, marker)
